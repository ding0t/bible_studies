"""Run segmentation against every OCR source we've produced, then combine
per-entry -- whichever source gives the best confidence tier for a given
TWOT root wins. Comparing at the entry level (rather than picking one whole
source, or swapping whole pages) takes each source's wins without its
collateral damage; confirmed empirically at each step: 400dpi alone (1509
verified) < entry-combined 400dpi+600dpi-targeted (1681) < column-aware
400dpi alone, which fixes the root-cause right/left column reading-order bug
(1801) < this N-way combine of all of them together.
"""
import bisect
import json
import sqlite3
from datetime import date
from pathlib import Path

from twot.derivative_structure import (
    extract_page_headers, extract_positioned_lines, segment_derivative_anchored_positioned,
    structure_derivatives,
)
from twot.segmenter import (
    CANDIDATE_RE, CONFIDENCE_RANK, PAREN_RE, load_expectations, load_pages, normalize, segment,
    segment_blockwalk, segment_derivative_anchored, split_entry_text, truncate_at_first_signoff,
)

BUILD_DIR = Path(__file__).resolve().parent
LOCAL_ONLY = Path("/Volumes/media/bible/local-only-build")
SOURCES = {
    "colsplit": LOCAL_ONLY / "twot-ocr-pages-colsplit",   # column-aware, fixes the reading-order bug -- best single source
    "400dpi": LOCAL_ONLY / "twot-ocr-pages-400dpi",
    "merged600": LOCAL_ONLY / "twot-ocr-pages-merged",     # 400dpi + targeted 600dpi override
}
DB_PATH = LOCAL_ONLY / "lexicon-restricted.db"
TWOT_MAP_PATH = BUILD_DIR / "twot_strongs_map.json"
SCHEMA_PATH = BUILD_DIR / "schema.sql"
SRC_PDF_PATH = "/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf"

# preference order among equally-ranked results. "pdftext-derivatives" goes
# first: same derivative-list-anchored approach as "colsplit-derivatives",
# but sourced from the PDF's own embedded text layer instead of Tesseract --
# confirmed directly to resolve failures Tesseract can't recover from at all
# (a dropped digit on root 3's own opening; genuine reading-order corruption,
# not just noise, in root 2's own Derivative-list text), so where it applies
# it's more trustworthy than any OCR source. "colsplit-derivatives" is next:
# matching a whole ordered Derivative-list sequence against known sub-entry
# transliterations essentially can't happen by chance, making it the most
# structurally trustworthy OCR source where it applies at all (roots with
# >=2 derivatives). "colsplit-blockwalk" (initials as hard block boundaries,
# no transliteration floor) is placed last -- it trades recall for precision
# and carries a known short-transliteration collision risk (see
# segment_blockwalk's docstring), so it should only win when nothing else
# found anything.
SOURCE_PRIORITY = ["pdftext-derivatives", "colsplit-derivatives", "colsplit", "400dpi",
                    "merged600", "colsplit-blockwalk"]


HEADER_OCR_ZONE = 80  # chars from a page's own OCR text start to look for a header candidate


def read_ocr_header_candidates(ocr_dir: Path) -> dict[int, str]:
    """Best-effort OCR reading of each page's own running head, for
    cross-validating extract_page_headers()'s embedded-text-layer reading.
    Only catches headers printed on the left/even-page side reliably --
    colsplit's OCR text concatenates left-column-then-right-column per page
    with no column-boundary marker preserved, so a right-side header (which
    prints AFTER the whole left column's body text) can't be isolated from
    flat text the same way. A page with no near-page-start candidate simply
    has no ocr_reading here -- expected for roughly half the book's pages
    (the odd-numbered, right-header ones), not a bug -- see
    build_page_headers()'s 'embedded-only' confidence tier for how that's
    handled downstream."""
    full_text, page_offsets = load_pages(ocr_dir)
    result: dict[int, str] = {}
    for start, page in page_offsets:
        window = full_text[start:start + HEADER_OCR_ZONE].strip()
        m = CANDIDATE_RE.match(window)
        if m:
            result[page] = m.group(1)
    return result


def build_page_headers(embedded_by_page: dict[int, dict], ocr_by_page: dict[int, str]) -> dict[int, dict]:
    """{page: {"header_root", "embedded_reading", "ocr_reading", "confidence"}}
    ready for page_headers table insertion. 'verified' when the embedded and
    OCR readings agree, 'suspect' when both exist but disagree (embedded
    wins regardless -- see extract_page_headers()'s docstring for why it's
    the more reliable source of the two), 'embedded-only' when OCR had
    nothing to compare against (see read_ocr_header_candidates)."""
    result = {}
    for page, embedded in embedded_by_page.items():
        ocr_root = ocr_by_page.get(page)
        if ocr_root is None:
            confidence = "embedded-only"
        elif ocr_root == embedded["root"]:
            confidence = "verified"
        else:
            confidence = "suspect"
        result[page] = {"header_root": embedded["root"], "embedded_reading": embedded["raw"],
                         "ocr_reading": ocr_root, "confidence": confidence}
    return result


def enforce_header_consistency(combined: dict, main_numbers: list, page_headers: dict[int, dict],
                                verbose: bool = True) -> list:
    """Cross-checks each root's own winning start page against page_headers
    -- the page whose running head first names that root (see schema.sql's
    page_headers comment for the "highest root starting on this page"
    convention this relies on). A root whose real entry spans several pages
    (e.g. root 93, 'ēl "god, God" -- a major theological entry) gets the
    SAME header on every one of those pages, not just its first -- so OCR
    independently confirming ANY page within that consecutive run is
    accepted as confirming the whole run, and the run's OWN earliest page is
    what gets compared against (not the earliest page that happens to carry
    'verified' confidence on its own). Confirmed necessary directly: root
    93's header reads '93' on pages 60-63, but OCR only independently
    confirmed page 63 -- taking "first verified page" alone would have
    computed an expected start of 63 and wrongly demoted root 93's own
    correct page-60 result. Still deliberately conservative in the sense
    that matters here (a lone, isolated 'verified' page with no
    'embedded-only' run backing it up behaves exactly as before) -- the cost
    of a false demotion (losing a correct entry) is worse than the cost of
    missing a real mismatch (which other checks may still catch)."""
    pages_sorted = sorted(page_headers)
    runs: list[tuple[str, int, bool]] = []  # (root, run_start_page, any_verified_in_run)
    i = 0
    while i < len(pages_sorted):
        page = pages_sorted[i]
        root = page_headers[page]["header_root"]
        run_start = page
        any_verified = page_headers[page]["confidence"] == "verified"
        j = i + 1
        while (j < len(pages_sorted) and pages_sorted[j] == pages_sorted[j - 1] + 1
               and page_headers[pages_sorted[j]]["header_root"] == root):
            any_verified = any_verified or page_headers[pages_sorted[j]]["confidence"] == "verified"
            j += 1
        runs.append((root, run_start, any_verified))
        i = j

    expected_start_page: dict[str, int] = {}
    for root, start, verified in runs:
        if verified and root not in expected_start_page:
            expected_start_page[root] = start

    demoted_nums = []
    for num in main_numbers:
        entry = combined[num]
        if entry["confidence"] == "not-found" or not entry["pages"]:
            continue
        expected = expected_start_page.get(num)
        if expected is None or min(entry["pages"]) == expected:
            continue
        combined[num] = {"text": None, "confidence": "not-found", "pages": [],
                          "source": entry["source"] + "-demoted(header-mismatch)"}
        demoted_nums.append(num)
    if verbose:
        print(f"page-header cross-check: demoted {len(demoted_nums)} entries whose start page "
              f"contradicted a verified page-header reading")
    return demoted_nums


def enforce_page_monotonicity(combined: dict, main_numbers: list, verbose: bool = True) -> int:
    """TWOT entries appear in strict page order through the book -- if entry
    N's page comes earlier than an entry preceding it in the numbering, at
    least one of them is misattributed (confirmed empirically: entry 1
    landed on pages 26-27 via a bad blockwalk match while entry 3 correctly
    sits on pages 24-25, an isolated regression rather than a real
    reordering). Finds the longest non-decreasing subsequence of page
    numbers across every non-'not-found' entry and demotes everything
    outside it back to not-found, rather than guessing which side of any
    single regression is the bad one -- an isolated outlier will always fall
    outside the longest consistent run, whichever direction it jumped."""
    indexed = [num for num in main_numbers if combined[num]["confidence"] != "not-found"]
    pages = [min(combined[num]["pages"]) if combined[num]["pages"] else 0 for num in indexed]

    tails_val: list[int] = []
    chain_end_idx: list[int] = []
    predecessor = [-1] * len(indexed)
    for j, p in enumerate(pages):
        pos = bisect.bisect_right(tails_val, p)
        if pos > 0:
            predecessor[j] = chain_end_idx[pos - 1]
        if pos == len(tails_val):
            tails_val.append(p)
            chain_end_idx.append(j)
        else:
            tails_val[pos] = p
            chain_end_idx[pos] = j

    keep = set()
    k = chain_end_idx[-1] if chain_end_idx else -1
    while k != -1:
        keep.add(k)
        k = predecessor[k]

    demoted_nums = []
    for j, num in enumerate(indexed):
        if j not in keep:
            combined[num] = {"text": None, "confidence": "not-found", "pages": [],
                              "source": combined[num]["source"] + "-demoted(page-order)"}
            demoted_nums.append(num)
    if verbose:
        print(f"page-monotonicity check: demoted {len(demoted_nums)} entries whose page "
              f"order contradicted their neighbors in the TWOT sequence")
    return demoted_nums


def flag_neighbors_of_demoted(combined: dict, main_numbers: list, demoted_nums: list,
                               verbose: bool = True) -> int:
    """A demoted entry leaves a hole in the sequence -- and segmentation
    finds each entry's END by locating the NEXT found entry's start, so
    whichever entry immediately precedes a demoted one may have silently
    over-captured the demoted entry's real content as if it were its own
    (confirmed directly: entry 1's text, once correctly bounded on the page
    level, still ran on past its own Bibliography/initials straight into
    entry 2's real discussion, because entry 2 -- the entry that should have
    closed entry 1 off -- got demoted for landing on a coincidental
    Aramaic-section match, leaving entry 1's span to expand into the gap).
    This doesn't re-cut the overrun text (that needs a real re-segmentation,
    not a post-hoc fix), but downgrades a wrongly-confident 'verified' tag on
    the preceding entry to 'suspect' so review isn't misled by it."""
    seq_index = {n: i for i, n in enumerate(main_numbers)}
    flagged = 0
    for num in demoted_nums:
        idx = seq_index[num]
        for j in range(idx - 1, -1, -1):
            prev_num = main_numbers[j]
            if combined[prev_num]["confidence"] != "not-found":
                if combined[prev_num]["confidence"] == "verified":
                    combined[prev_num]["confidence"] = "suspect"
                    flagged += 1
                break
    if verbose:
        print(f"downgraded {flagged} entries immediately preceding a demoted entry "
              f"(verified -> suspect: their text may have over-captured the gap)")
    return flagged


DUPLICATE_PREFIX_LEN = 60
# How close to the start of a captured prefix its own parenthetical (xlit
# or gloss) must appear to count as "looks like a real entry opening" --
# see flag_swallowed_neighbors's docstring.
ENTRY_OPENING_PAREN_LOOKAHEAD = 25


def flag_duplicate_starts(combined: dict, main_numbers: list, verbose: bool = True) -> int:
    """The page-monotonicity check catches an entry landing on the WRONG
    page; it can't catch two DIFFERENT entries claiming the SAME page and
    the SAME text, which is a distinct failure mode -- confirmed directly:
    root 5 has zero derivatives (nothing for the derivative-anchored source
    to grab), so it fell back to segment()'s plain per-number search, which
    misfired and captured root 4's entire 'father' discussion wholesale
    (root 4 was independently, correctly found by the derivative-anchored
    source at the same position) -- same page range, so monotonicity never
    flags it. Any entry whose captured text starts with (near-)the same
    normalized prefix as another entry's is almost certainly this same bug,
    not a coincidence -- demote whichever one has the lower-priority source,
    since the higher-priority one is more likely correct."""
    seen: dict[str, str] = {}  # normalized prefix -> num that claimed it first
    demoted_nums = []
    for num in main_numbers:
        entry = combined[num]
        if entry["confidence"] == "not-found" or not entry["text"]:
            continue
        prefix = normalize(entry["text"][:DUPLICATE_PREFIX_LEN * 2])[:DUPLICATE_PREFIX_LEN]
        if len(prefix) < DUPLICATE_PREFIX_LEN // 2:
            continue
        if prefix in seen:
            other_num = seen[prefix]
            other_rank = SOURCE_PRIORITY.index(combined[other_num]["source"].split("-demoted")[0])
            this_rank = SOURCE_PRIORITY.index(entry["source"].split("-demoted")[0])
            loser = num if this_rank >= other_rank else other_num
            if combined[loser]["confidence"] != "not-found":
                combined[loser] = {"text": None, "confidence": "not-found", "pages": [],
                                    "source": combined[loser]["source"] + "-demoted(duplicate-text)"}
                demoted_nums.append(loser)
            if loser == other_num:
                seen[prefix] = num
        else:
            seen[prefix] = num
    if verbose:
        print(f"duplicate-text check: demoted {len(demoted_nums)} entries whose captured text "
              f"opening matched another entry's -- same content claimed twice")
    return demoted_nums


def flag_swallowed_neighbors(combined: dict, main_numbers: list, verbose: bool = True) -> int:
    """flag_duplicate_starts catches two entries claiming the same START;
    this catches the opposite shape -- one entry's TAIL containing a
    DIFFERENT entry's whole start. Confirmed directly: entry 8 has no
    signature of its own (a short stub, same shape as entry 5), so its span
    ran on through all of entry 9's ~5000-char discussion before hitting a
    confirmed signature at all -- but that signature was entry 9's OWN
    (R.L.A.), not entry 8's, so truncate_at_first_signoff had nothing wrong
    to stop at. Entry 9 was independently, correctly found too, so this is
    directly detectable: if entry N's text literally contains another known
    entry's opening somewhere past its own start, N swallowed it -- truncate
    N right before that point.

    A candidate's own prefix is only trusted as "another entry's whole
    start" if it actually LOOKS like one -- a parenthetical (the entry's own
    Hebrew xlit or gloss) appearing near its own beginning -- confirmed
    necessary directly: root 1's own boundary search sometimes lands wrong
    (a separate, still-open issue -- see find_derivative_anchors's
    docstring), giving it a "prefix" like "t the word refers to the
    destruction of the grave..." that isn't root 1's opening at all, just
    prose that happens to ALSO legitimately appear within root 2's own
    correct, much longer discussion (since it's genuinely part of root 2's
    text, not swallowed from anywhere). Without this check, root 2's correct
    text gets wrongly truncated right before that shared substring, on the
    mistaken theory that root 2 must have swallowed root 1 -- when actually
    root 1's own boundary is what's wrong, and root 2 did nothing wrong at
    all.

    Checks for a NEARBY parenthetical specifically, not CANDIDATE_RE's
    stricter "leading digit" shape -- confirmed necessary directly: this
    initially used CANDIDATE_RE.match(prefix), which broke the exact
    original motivating case above the fold (entry 8 swallowing entry 9's
    whole ~5000-char discussion) -- entry 9's own genuine winning text has
    its leading root-number digit ALREADY stripped by an earlier processing
    step (build_boundary_result's own leading-number strip, used by
    segment()/segment_blockwalk()), so its real prefix is
    "אבה (eben) stone. Derivative 9a..." -- no leading digit, so
    CANDIDATE_RE.match() failed at position 0 even though this is obviously
    a genuine entry opening. A parenthetical near the start catches both
    shapes (digit-led or not) while still rejecting root 1's prose-only,
    parenthetical-free bogus prefix."""
    prefixes = {}
    for num in main_numbers:
        entry = combined[num]
        if entry["confidence"] == "not-found" or not entry["text"]:
            continue
        prefix = entry["text"][:DUPLICATE_PREFIX_LEN]
        paren_match = PAREN_RE.search(prefix)
        looks_like_opening = paren_match is not None and paren_match.start() < ENTRY_OPENING_PAREN_LOOKAHEAD
        if len(prefix) >= DUPLICATE_PREFIX_LEN // 2 and looks_like_opening:
            prefixes[num] = prefix

    truncated = 0
    for num in main_numbers:
        entry = combined[num]
        if entry["confidence"] == "not-found" or not entry["text"]:
            continue
        text = entry["text"]
        best_cut = None
        for other_num, other_prefix in prefixes.items():
            if other_num == num:
                continue
            idx = text.find(other_prefix, 1)  # skip a match at position 0 (that's flag_duplicate_starts' job)
            if idx > 0 and (best_cut is None or idx < best_cut):
                best_cut = idx
        if best_cut is not None:
            combined[num]["text"] = text[:best_cut].strip() or None
            truncated += 1
    if verbose:
        print(f"swallowed-neighbor check: truncated {truncated} entries whose text "
              f"contained another entry's start past their own")
    return truncated


def main() -> None:
    assert "bible_studies" not in str(DB_PATH), "must stay outside the git repo"

    twot_map: dict = json.loads(TWOT_MAP_PATH.read_text())
    main_numbers, seq_index, expected_xlit, expected_gloss = load_expectations(twot_map)
    print(f"{len(main_numbers)} known main TWOT roots\n")

    results = {}
    for name, ocr_dir in SOURCES.items():
        print(f"=== segmenting: {name} ({ocr_dir.name}) ===")
        results[name] = segment(ocr_dir, twot_map, main_numbers, seq_index, expected_xlit, expected_gloss)
        print()

    print("=== segmenting: colsplit-blockwalk (twot-ocr-pages-colsplit) ===")
    results["colsplit-blockwalk"] = segment_blockwalk(
        SOURCES["colsplit"], twot_map, main_numbers, seq_index, expected_xlit, expected_gloss
    )
    print()

    print("=== segmenting: colsplit-derivatives (twot-ocr-pages-colsplit) ===")
    results["colsplit-derivatives"] = segment_derivative_anchored(
        SOURCES["colsplit"], twot_map, main_numbers, seq_index, expected_xlit, expected_gloss
    )
    print()

    print("=== extracting PDF embedded text layer (shared by pdftext-derivatives, "
          "structure_derivatives, page headers) ===")
    lines = extract_positioned_lines()
    print(f"positioned-text extraction: {len(lines)} lines across the PDF")
    print()

    print("=== reading page headers (embedded text layer + OCR cross-check) ===")
    embedded_headers = extract_page_headers(lines)
    ocr_headers = read_ocr_header_candidates(SOURCES["colsplit"])
    page_headers = build_page_headers(embedded_headers, ocr_headers)
    header_conf_tally = {}
    for v in page_headers.values():
        header_conf_tally[v["confidence"]] = header_conf_tally.get(v["confidence"], 0) + 1
    print(f"page headers: {len(page_headers)} pages read, confidence breakdown: {header_conf_tally}")
    # reverse lookup: root -> first page whose header names it (see
    # page_headers table comment for the "highest root starting on this
    # page" convention). Two tiers, deliberately different strictness for
    # two different risk profiles: the RESCUE pass below only GUIDES a
    # search that still has to independently clear HEADER_RESCUE_MIN_SCORE
    # on its own verified-data signals, so a wrong header here just fails to
    # rescue anything -- safe to trust 'embedded-only' pages too (confirmed
    # necessary: OCR only independently confirms roughly half of headers, so
    # restricting to 'verified' alone left root 1's own page -- 21 -- with no
    # entry at all, and its rescue never even attempted). enforce_header_
    # consistency's DEMOTION check further down is the opposite risk profile
    # (a wrong header there actively discards a possibly-correct entry), so
    # it stays restricted to 'verified' only, computed separately there.
    expected_page_by_root: dict[str, int] = {}
    for page in sorted(page_headers):
        h = page_headers[page]
        if h["confidence"] in ("verified", "embedded-only") and h["header_root"] not in expected_page_by_root:
            expected_page_by_root[h["header_root"]] = page
    print()

    print("=== segmenting: pdftext-derivatives (PDF embedded text layer, header-guided rescue) ===")
    results["pdftext-derivatives"] = segment_derivative_anchored_positioned(
        twot_map, main_numbers, expected_xlit, expected_gloss, lines, expected_page_by_root
    )
    print()

    print(f"=== combining per-entry (best confidence tier wins, ties -> {' > '.join(SOURCE_PRIORITY)}) ===")
    combined = {}
    source_used = {name: 0 for name in SOURCE_PRIORITY}
    for num in main_numbers:
        candidates = [(name, results[name][num]) for name in SOURCE_PRIORITY]
        best_name, best_entry = max(
            candidates, key=lambda nc: CONFIDENCE_RANK[nc[1]["confidence"]]
        )
        combined[num] = {**best_entry, "source": best_name}
        source_used[best_name] += 1

    print(f"source wins: {source_used}")
    tally = {}
    for v in combined.values():
        tally[v["confidence"]] = tally.get(v["confidence"], 0) + 1
    print(f"combined confidence breakdown (pre-monotonicity-check): {tally}")

    demoted_nums = enforce_page_monotonicity(combined, main_numbers)
    header_demoted_nums = enforce_header_consistency(combined, main_numbers, page_headers)
    dup_demoted_nums = flag_duplicate_starts(combined, main_numbers)
    flag_swallowed_neighbors(combined, main_numbers)
    flag_neighbors_of_demoted(combined, main_numbers, demoted_nums + header_demoted_nums + dup_demoted_nums)
    tally = {}
    for v in combined.values():
        tally[v["confidence"]] = tally.get(v["confidence"], 0) + 1
    print(f"combined confidence breakdown (final): {tally}")

    print("=== structuring derivative discussion paragraphs (embedded PDF text layer) ===")
    derivative_structure, heading_by_root = structure_derivatives(twot_map, lines, expected_page_by_root)
    print()

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.execute(
        "INSERT INTO works (work_id, title, publisher, year, source_path, ingested_at, "
        "license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?)",
        ("twot", "Theological Wordbook of the Old Testament", "Moody Press", 1980,
         SRC_PDF_PATH, date.today().isoformat(),
         "Copyright 1980 by the Moody Bible Institute", "quotation-only",
         "Harris, Archer & Waltke, eds., Theological Wordbook of the Old Testament, Moody Press, 1980"),
    )
    derivative_count = 0
    for num in main_numbers:
        sub_entries = {k: v for k, v in twot_map.items() if k == num or (k.startswith(num) and k[len(num):].isalpha())}
        strongs_ids = sorted({e["strongs_id"] for sub in sub_entries.values() for e in sub if e["strongs_id"]})
        bdb_ids = sorted({e["bdb_id"] for sub in sub_entries.values() for e in sub if e["bdb_id"]})
        base = sub_entries.get(num, [{}])[0]
        entry = combined[num]
        truncated_text = truncate_at_first_signoff(entry["text"])
        main_text, bibliography, contributor_initials = split_entry_text(truncated_text)

        conn.execute(
            "INSERT INTO entries (work_id, key, lemma, transliteration, strongs_ids, bdb_id, "
            "short_gloss, main_text, bibliography, contributor_initials, source_pages, "
            "extraction_source, boundary_text, text_confidence, derivative_heading) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("twot", num, base.get("lemma"), base.get("xlit"),
             json.dumps(strongs_ids), json.dumps(bdb_ids), base.get("gloss"),
             main_text, bibliography, contributor_initials,
             json.dumps(entry["pages"]), entry["source"], entry.get("boundary_text"), entry["confidence"],
             heading_by_root.get(num)),
        )

        # derivatives: 100% populated from verified data regardless of whether
        # the parent's main_text was ever found -- no OCR dependency at all
        for sub_key, sub_list in sorted(sub_entries.items()):
            if sub_key == num:
                continue  # the root itself, not a derivative
            sub_strongs = sorted({e["strongs_id"] for e in sub_list if e["strongs_id"]})
            sub_bdb = sorted({e["bdb_id"] for e in sub_list if e["bdb_id"]})
            sub_base = sub_list[0]
            deriv_text = derivative_structure.get(sub_key, {})
            conn.execute(
                "INSERT INTO derivatives (work_id, parent_key, key, lemma, transliteration, "
                "strongs_ids, bdb_id, gloss, main_text, source_pages) VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("twot", num, sub_key, sub_base.get("lemma"), sub_base.get("xlit"),
                 json.dumps(sub_strongs), json.dumps(sub_bdb), sub_base.get("gloss"),
                 deriv_text.get("main_text"),
                 json.dumps(deriv_text["source_pages"]) if "source_pages" in deriv_text else None),
            )
            derivative_count += 1

    for page, h in sorted(page_headers.items()):
        conn.execute(
            "INSERT INTO page_headers (page, header_root, embedded_reading, ocr_reading, confidence) "
            "VALUES (?,?,?,?,?)",
            (page, h["header_root"], h["embedded_reading"], h["ocr_reading"], h["confidence"]),
        )

    conn.commit()
    conn.close()
    print(f"loaded {len(combined)} entries + {derivative_count} derivatives + "
          f"{len(page_headers)} page headers into {DB_PATH}")


if __name__ == "__main__":
    main()
