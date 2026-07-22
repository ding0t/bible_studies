"""Segment the OCR'd TWOT pages into individual entries and load them into
lexicon-restricted.db.

Iteration 4. What changed each time:

- v1 (bare number + strict monotonic order): 65/3057 roots. TWOT has ~3057
  main roots spanning 1-2700+, so nearly any 1-4 digit number in the OCR
  text (a verse citation, a footnote marker) coincidentally IS a valid id,
  and a garbled number that ALSO happens to coincidentally be a valid-but-
  wrong id poisons a strict sequence tracker for everything between.

- v2 (require a fuzzy transliteration match nearby, keep the LAST match per
  number): 1857/3057 roots, but ~5-20% wrongly attributed. Short
  transliterations (2-3 letters) pass a 0.5 fuzzy-match threshold by pure
  chance too often, and "keep the last occurrence" let a late false positive
  silently overwrite a correct earlier match.

- v3: length-aware thresholds, best-score-wins, two-pass with positional
  sanity (a looser-threshold candidate must fall between its nearest
  confirmed neighbors), and gloss corroboration as a second independent
  signal. 1696/3057, 85% of those independently verified.

- v4 (this version): TWOT entries are each signed with contributor initials
  (confirmed empirically: ~32 distinct 2-3 letter dotted-initial patterns
  repeat 15-2500+ times each across the corpus, e.g. "V.P.H", "R.L.A" --
  everything below that frequency is OCR noise on the same regex shape).
  This is an END-of-entry marker, independent of the start-of-entry
  number/transliteration signal used so far. Two uses:
    1. A confirmed initials-marker shortly before a candidate boosts
       confidence, admitted at a lower transliteration threshold (same
       mechanism as the existing gloss-hit bonus).
    2. NEW pass 3: for a gap between two confirmed entries where we know
       EXACTLY how many roots should exist (from the complete TWOT root
       list) -- if the gap contains exactly that many initials-markers, the
       markers themselves delimit the missing entries positionally, with no
       need to successfully read any of their numbers at all. Exact-count
       match only; a mismatched count is left alone rather than guessed at.
"""
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
OCR_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-400dpi")
DB_PATH = Path("/Volumes/media/bible/local-only-build/lexicon-restricted.db")
TWOT_MAP_PATH = BUILD_DIR / "twot_strongs_map.json"
SCHEMA_PATH = BUILD_DIR / "schema.sql"
SRC_PDF_PATH = "/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf"

CANDIDATE_RE = re.compile(r"(?:^|\s)(\d{1,4})\s*\S{0,20}?\s*\(([^)]{1,20})\)", re.MULTILINE)
INITIALS_CANDIDATE_RE = re.compile(r"\b([A-Z]\.\s?[A-Z]\.\s?[A-Z]?\.?)\b")
INITIALS_FREQ_THRESHOLD = 15  # empirical break point: rank ~32 drops from 15 to 11 --
                                # used as a fallback for anyone missed below, not the primary source
STOPWORDS = {"the", "a", "an", "of", "to", "in", "on", "and", "or", "is", "be", "it",
             "with", "as", "by", "for", "from", "not", "also", "see", "no"}

# Transcribed directly from the book's own CONTRIBUTORS section (OCR pages
# 8-9), which lists every contributor's initials next to their name -- e.g.
# "GOLDBERG, Louis ... L.G." This is authoritative, not statistical inference,
# so it catches contributors who wrote too few entries to clear the frequency
# threshold above (12 of these 44 weren't in the frequency-derived list at all).
AUTHORITATIVE_INITIALS = {
    "JEH", "CDI", "WCK", "ESK", "JPL", "GHL", "TEM", "AAM", "EAM", "JNO", "RDP", "JBP",
    "CR", "JBS", "CS", "EBS", "RLA", "RHA", "RBA", "GLA", "HJA", "AB", "GLC", "GGC",
    "WBC", "LJC", "RDC", "CLF", "PRG", "LG", "VPH", "RLH", "DJW", "LW", "HW", "LJW",
    "EY", "RFY", "JES", "HGS", "GVG", "BKW", "CPW", "WW", "MRW", "MCF",
}


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())


def strict_threshold(length: int) -> float:
    if length <= 3:
        return 0.85
    if length <= 5:
        return 0.7
    return 0.6


def loose_threshold(length: int) -> float:
    if length <= 3:
        return 0.65
    if length <= 5:
        return 0.55
    return 0.45


def gloss_words(gloss_text: str | None) -> set[str]:
    words = re.findall(r"[A-Za-z]+", gloss_text or "")
    return {normalize(w) for w in words if len(normalize(w)) >= 3 and normalize(w) not in STOPWORDS}


def find_confirmed_initials(full_text: str) -> set[str]:
    counts = Counter()
    for m in INITIALS_CANDIDATE_RE.finditer(full_text):
        norm = re.sub(r"[\s.]", "", m.group(1))
        if 2 <= len(norm) <= 3:
            counts[norm] += 1
    # authoritative list (from the book's own Contributors section) is trusted
    # at any frequency >=1 -- it's not statistical inference, it's a known-real
    # roster. Frequency threshold is a fallback for anyone missed in transcription.
    from_book = AUTHORITATIVE_INITIALS & counts.keys()
    from_frequency = {k for k, v in counts.items() if v >= INITIALS_FREQ_THRESHOLD}
    confirmed = from_book | from_frequency
    print(f"confirmed contributor initials: {len(from_book)} from the book's own Contributors list, "
          f"+{len(from_frequency - from_book)} more via frequency = {len(confirmed)} total")
    missing_from_corpus = AUTHORITATIVE_INITIALS - counts.keys()
    if missing_from_corpus:
        print(f"  (authoritative names never matched in OCR text at all: {sorted(missing_from_corpus)})")
    return confirmed


def main() -> None:
    assert "bible_studies" not in str(DB_PATH), "must stay outside the git repo"

    twot_map: dict[str, list[dict]] = json.loads(TWOT_MAP_PATH.read_text())
    main_numbers = sorted({re.match(r"^(\d+)", k).group(1) for k in twot_map}, key=int)
    seq_index = {n: i for i, n in enumerate(main_numbers)}

    expected_xlit: dict[str, set[str]] = {}
    expected_gloss: dict[str, set[str]] = {}
    for k, entries in twot_map.items():
        num = re.match(r"^(\d+)", k).group(1)
        for e in entries:
            if e.get("xlit"):
                expected_xlit.setdefault(num, set()).add(normalize(e["xlit"]))
            if e.get("gloss"):
                expected_gloss.setdefault(num, set()).update(gloss_words(e["gloss"]))

    print(f"{len(main_numbers)} known main TWOT roots")

    page_files = sorted(OCR_DIR.glob("page-*.txt"))
    full_text_parts, page_offsets = [], []
    offset = 0
    for pf in page_files:
        page_num = int(pf.stem.split("-")[1])
        text = pf.read_text(encoding="utf-8")
        page_offsets.append((offset, page_num))
        full_text_parts.append(text)
        offset += len(text) + 1
    full_text = "\n".join(full_text_parts)

    def page_for_offset(char_offset: int) -> int:
        page_num = page_offsets[0][1]
        for start, pnum in page_offsets:
            if start > char_offset:
                break
            page_num = pnum
        return page_num

    confirmed_initials = find_confirmed_initials(full_text)
    initials_end_positions = sorted(
        m.end() for m in INITIALS_CANDIDATE_RE.finditer(full_text)
        if re.sub(r"[\s.]", "", m.group(1)) in confirmed_initials
    )
    bibliography_positions = sorted(m.start() for m in re.finditer(r"[Bb]ibliography\s*:", full_text))
    print(f"{len(bibliography_positions)} 'Bibliography:' markers found")

    import bisect

    def initials_shortly_before(pos: int, window: int = 200) -> bool:
        lo = pos - window
        i = bisect.bisect_left(initials_end_positions, lo)
        return i < len(initials_end_positions) and initials_end_positions[i] < pos

    def bibliography_shortly_before(pos: int, window: int = 400) -> bool:
        lo = pos - window
        i = bisect.bisect_left(bibliography_positions, lo)
        return i < len(bibliography_positions) and bibliography_positions[i] < pos

    # the strongest end-of-entry signal: a Bibliography marker immediately
    # followed by a confirmed initials signature -- Bibliography: ... L.J.C.
    # This is much higher precision than bare initials alone (an author's own
    # initials cited *within* a bibliography citation, e.g. "Harris, R. L.,
    # ...", can otherwise look like a signature; requiring Bibliography
    # shortly before rules most of those out).
    strong_end_positions = sorted(
        p for p in initials_end_positions if bibliography_shortly_before(p)
    )
    print(f"{len(strong_end_positions)} high-precision end markers (Bibliography + initials combined)")

    # gather every candidate with its score, grouped by number
    candidates: dict[str, list[tuple[float, bool, bool, bool, int]]] = {}
    # -> [(translit_score, gloss_hit, sig_hit, bib_hit, pos)]
    for m in CANDIDATE_RE.finditer(full_text):
        num, paren = m.group(1), m.group(2)
        if num not in expected_xlit:
            continue
        cand_norm = normalize(paren)
        if len(cand_norm) < 2:
            continue
        translit_score = max(
            (SequenceMatcher(None, cand_norm, exp).ratio() for exp in expected_xlit[num]), default=0,
        )
        window = full_text[m.end():m.end() + 80]
        window_words = {normalize(w) for w in re.findall(r"[A-Za-z]+", window)}
        gloss_hit = bool(expected_gloss.get(num, set()) & window_words)
        sig_hit = initials_shortly_before(m.start(1))
        bib_hit = bibliography_shortly_before(m.start(1))
        candidates.setdefault(num, []).append((translit_score, gloss_hit, sig_hit, bib_hit, m.start(1)))

    def qualifies(score: float, gloss_hit: bool, sig_hit: bool, bib_hit: bool, thresh: float) -> bool:
        bonus = (0.15 if gloss_hit else 0) + (0.15 if sig_hit else 0) + (0.1 if bib_hit else 0)
        return score + bonus >= thresh

    def pick_best(qualifying: list[tuple[float, int]], prefer_early: bool = False) -> int:
        """Best-score wins by default. With prefer_early, chronologically
        earlier candidates win unless a later one scores meaningfully higher
        (>0.15) -- models 'the first plausible match right after a known-good
        predecessor is usually the real one', not just 'whatever scores best
        anywhere in the gap'."""
        if not prefer_early:
            return max(qualifying, key=lambda sp: sp[0])[1]
        by_position = sorted(qualifying, key=lambda sp: sp[1])
        best = by_position[0]
        for score, pos in by_position[1:]:
            if score > best[0] + 0.15:
                best = (score, pos)
        return best[1]

    # pass 1: high-confidence anchors, best score wins
    anchors: dict[str, int] = {}
    for num, cands in candidates.items():
        thresh = strict_threshold(min((len(x) for x in expected_xlit[num]), default=4))
        qualifying = [(score, pos) for score, hit, sig, bib, pos in cands if qualifies(score, hit, sig, bib, thresh)]
        if qualifying:
            anchors[num] = pick_best(qualifying)

    print(f"pass 1 (high-confidence anchors): {len(anchors)}/{len(main_numbers)}")

    # pass 2: fill gaps with a looser threshold, constrained to fall between
    # the nearest confirmed neighbors' positions in the sequence. Ties prefer
    # the earliest qualifying candidate after the previous confirmed entry.
    anchor_seq = sorted(((seq_index[n], pos) for n, pos in anchors.items()))
    filled = dict(anchors)
    for num, cands in candidates.items():
        if num in filled:
            continue
        idx = seq_index[num]
        prev_pos = max((pos for i, pos in anchor_seq if i < idx), default=0)
        next_pos = min((pos for i, pos in anchor_seq if i > idx), default=len(full_text))
        if prev_pos >= next_pos:
            continue
        thresh = loose_threshold(min((len(x) for x in expected_xlit[num]), default=4))
        qualifying = [
            (score, pos) for score, hit, sig, bib, pos in cands
            if qualifies(score, hit, sig, bib, thresh) and prev_pos <= pos <= next_pos
        ]
        if qualifying:
            filled[num] = pick_best(qualifying, prefer_early=True)

    print(f"pass 2 (+ positionally-constrained recovery): {len(filled)}/{len(main_numbers)}")

    # pass 3: gap-count recovery. For each gap between confirmed entries where
    # we know exactly K roots are missing, if the gap contains exactly K
    # end-of-entry markers, those markers delimit the K missing entries
    # positionally -- no need to read any of their numbers at all. Try the
    # high-precision Bibliography+initials marker set first; only fall back
    # to bare initials (noisier -- can catch a cited author's own initials
    # inside someone else's bibliography) if the strong set doesn't line up.
    anchor_seq = sorted(((seq_index[n], pos) for n, pos in filled.items()))
    recovered_via_gap = 0
    for i in range(len(anchor_seq) - 1):
        idx_a, pos_a = anchor_seq[i]
        idx_b, pos_b = anchor_seq[i + 1]
        missing = [main_numbers[j] for j in range(idx_a + 1, idx_b)]
        if not missing:
            continue
        strong_in_gap = [p for p in strong_end_positions if pos_a < p < pos_b]
        markers_in_gap = strong_in_gap if len(strong_in_gap) == len(missing) else \
            [p for p in initials_end_positions if pos_a < p < pos_b]
        if len(markers_in_gap) != len(missing):
            continue  # count mismatch -- don't guess
        boundary_points = [pos_a] + markers_in_gap
        for j, num in enumerate(missing):
            filled[num] = boundary_points[j]
            recovered_via_gap += 1

    print(f"pass 3 (+ exact-count gap recovery via end-of-entry markers): "
          f"{recovered_via_gap} recovered, {len(filled)}/{len(main_numbers)} total")

    boundaries = sorted(filled.items(), key=lambda kv: kv[1])
    entries = []
    for i, (num, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(full_text)
        raw = full_text[start:end]
        raw = re.sub(r"^\s*\d{1,4}\b", "", raw, count=1)
        text = re.sub(r"\s+", " ", raw).strip()
        pages = sorted({page_for_offset(start), page_for_offset(max(start, end - 1))})
        entries.append((num, text, pages))

    lengths = sorted(len(e[1]) for e in entries)
    median_len = lengths[len(lengths) // 2] if lengths else 0
    long_entries = [e for e in entries if len(e[1]) > median_len * 5]
    print(f"median entry length: {median_len} chars; {len(long_entries)} unusually long (>5x median)")

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
    found = {num: (text, pages) for num, text, pages in entries}

    for num in main_numbers:
        sub_entries = {k: v for k, v in twot_map.items() if re.match(rf"^{num}[a-z]?$", k)}
        strongs_ids = sorted({e["strongs_id"] for sub in sub_entries.values() for e in sub if e["strongs_id"]})
        bdb_ids = sorted({e["bdb_id"] for sub in sub_entries.values() for e in sub if e["bdb_id"]})
        base = sub_entries.get(num, [{}])[0]

        if num in found:
            text, pages = found[num]
            expected_words = expected_gloss.get(num, set())
            if not text:
                confidence = "not-found"
            elif not expected_words:
                confidence = "unverified"
            else:
                text_words = {normalize(w) for w in re.findall(r"[A-Za-z]+", text)}
                confidence = "verified" if expected_words & text_words else "suspect"
        else:
            text, pages, confidence = None, [], "not-found"

        conn.execute(
            "INSERT INTO entries (work_id, key, lemma, transliteration, strongs_ids, bdb_id, "
            "short_gloss, text, source_pages, text_confidence) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("twot", num, base.get("lemma"), base.get("xlit"),
             json.dumps(strongs_ids), json.dumps(bdb_ids), base.get("gloss"), text, json.dumps(pages),
             confidence),
        )
    conn.commit()
    conn.close()
    print(f"loaded {len(entries)} entries into {DB_PATH}")


if __name__ == "__main__":
    main()
