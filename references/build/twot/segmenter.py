"""Core TWOT segmentation logic, extracted so it can be run against different
OCR sources and the results combined per-entry (see combine_sources.py) --
whole-page swaps between DPI sources cause collateral damage to *other*
entries sharing that page (confirmed empirically: a targeted 600dpi re-OCR
fixed 51 of 315 suspect entries but broke enough others that net verified
count dropped). Combining at the entry level, picking whichever source scored
better for each individual TWOT root, avoids that collateral damage entirely.
"""
import bisect
import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

CANDIDATE_RE = re.compile(r"(?:^|\s)(\d{1,4})\s*\S{0,20}?\s*\(([^)]{1,20})\)", re.MULTILINE)
INITIALS_CANDIDATE_RE = re.compile(r"\b([A-Z]\.\s?[A-Z]\.\s?[A-Z]?\.?)\b")
INITIALS_FREQ_THRESHOLD = 15
STOPWORDS = {"the", "a", "an", "of", "to", "in", "on", "and", "or", "is", "be", "it",
             "with", "as", "by", "for", "from", "not", "also", "see", "no"}

AUTHORITATIVE_INITIALS = {
    "JEH", "CDI", "WCK", "ESK", "JPL", "GHL", "TEM", "AAM", "EAM", "JNO", "RDP", "JBP",
    "CR", "JBS", "CS", "EBS", "RLA", "RHA", "RBA", "GLA", "HJA", "AB", "GLC", "GGC",
    "WBC", "LJC", "RDC", "CLF", "PRG", "LG", "VPH", "RLH", "DJW", "LW", "HW", "LJW",
    "EY", "RFY", "JES", "HGS", "GVG", "BKW", "CPW", "WW", "MRW", "MCF",
}

CONFIDENCE_RANK = {"verified": 3, "unverified": 2, "suspect": 1, "not-found": 0}

BIBLIOGRAPHY_RE = re.compile(r"[Bb]ibliography\s*:")

# TWOT's dictionary body is interleaved with a separate alphabetical
# cross-reference index -- short stubs like "'abôy). See no. 3d." that point
# an alphabetically-placed word spelling to the root entry that actually
# discusses it. These aren't derivatives or content of whichever real entry
# they happen to land inside during segmentation; they're noise from a
# different structural layer of the book and get stripped out of main_text.
# (confirmed via direct page inspection: 1,507 occurrences total, clustered
# right after a contributor's initials/Bibliography -- which is also why
# using initials-adjacency as a *boundary* signal doesn't outperform the
# existing transliteration/gloss anchor logic: it just as often lands on one
# of these stubs as on the next real entry.)
SEE_NO_RE = re.compile(r"See nos?\.?\s*\d{1,4}[a-z]?(?:\s*,\s*(?:\d{1,4})?[a-z]?)*\.?", re.IGNORECASE)


def strip_index_stubs(text: str | None) -> str | None:
    if not text:
        return text
    stripped = SEE_NO_RE.sub("", text)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped or None


# A word split across a line-wrap in the justified column layout prints as
# "signifi- ca-" ... "tion" once flattened to plain text (a hyphen, then
# whatever whitespace joined the two source lines) -- e.g. root 3's own
# discussion has "...only with a negative partiCle... G. J. Botterweck
# concludes that the primary emphasis... on the main behavioral patterns
# and actions in which the inten- tion is manifested", where "inten- tion"
# should read "intention". Heuristic, not dictionary-verified: a lowercase
# letter immediately followed by a hyphen at end of line, then whitespace,
# then a lowercase letter, is treated as a wrapped word and rejoined
# directly (hyphen and whitespace both dropped). This occasionally
# mis-joins a genuine compound word that happens to wrap at its own
# hyphen (e.g. a hypothetical "self- control" would become "selfcontrol"
# instead of "self-control") -- accepted, since plain word-wrap is far
# more common in this dense justified text than a compound hyphen landing
# exactly at a line break, and leaving EVERY wrap unjoined (the previous
# behavior) was a much more consistently visible defect. Applied to
# already-assembled text (main_text etc.), not to full_text during
# extraction -- deliberately independent of extract_positioned_lines()'s
# own line-offset bookkeeping, which downstream position-matching (
# find_derivative_anchors, CANDIDATE_RE scanning, etc.) depends on staying
# one-line-per-offset; rewriting text length there would break it silently.
WRAP_HYPHEN_RE = re.compile(r"([a-z])-\s+([a-z])")


def dehyphenate(text: str | None) -> str | None:
    if not text:
        return text
    return WRAP_HYPHEN_RE.sub(r"\1\2", text)


def truncate_at_first_signoff(text: str | None) -> str | None:
    """A captured span running past its own end swallowed at least one
    subsequent entry whose own boundary wasn't found -- the gap-filling
    behavior common to every segmentation strategy here (each finds an
    entry's end by locating wherever the NEXT successfully-found entry
    begins, so a missing neighbor lets the span run on). split_entry_text()
    only separates fields WITHIN an already-bounded span; it can't detect
    the span itself is too wide.

    Truncates at the FIRST confirmed-initials occurrence found anywhere, not
    only ones following a second 'Bibliography:' marker -- an earlier version
    required two Bibliography markers, on the assumption every swallowed
    entry has its own, but a short stub entry with no bibliography or
    signature of its own (confirmed on entry 5: a single sentence, nothing
    else) slips through that gate and stays swallowed. A confirmed
    contributor's initials appearing anywhere means SOME entry just ended
    there; for a normally-bounded entry this is simply its own trailing
    signature, so truncating there is a no-op (nothing follows it anyway)."""
    if not text:
        return text
    for m in INITIALS_CANDIDATE_RE.finditer(text):
        norm = re.sub(r"[\s.]", "", m.group(1))
        if norm in AUTHORITATIVE_INITIALS:
            return text[:m.end()]
    return text


def split_entry_text(text: str | None) -> tuple[str | None, str | None, str | None]:
    """Split a captured entry's raw text into (main_text, bibliography,
    contributor_initials), using the same two markers already used as
    end-of-entry boundary signals during segmentation -- 'Bibliography:' and
    the confirmed-initials roster -- but now to split the INSIDE of an
    already-bounded entry rather than to find where it ends."""
    if not text:
        return None, None, None

    text = dehyphenate(text)
    text = strip_index_stubs(text)
    if not text:
        return None, None, None

    m = BIBLIOGRAPHY_RE.search(text)
    if m:
        main_text = text[:m.start()].strip() or None
        remainder = text[m.start():].strip()
    else:
        main_text = text
        remainder = ""

    contributor_initials = None
    # look for a confirmed-initials match at/near the end of whichever chunk
    # we have (remainder if there's a bibliography, else main_text itself --
    # short entries with no bibliography can still end in a bare signature)
    search_in = remainder if remainder else (main_text or "")
    last_match = None
    for im in INITIALS_CANDIDATE_RE.finditer(search_in):
        norm = re.sub(r"[\s.]", "", im.group(1))
        if norm in AUTHORITATIVE_INITIALS:
            last_match = (im, norm)
    if last_match and last_match[0].end() >= len(search_in) - 5:  # must be trailing, not mid-text
        im, norm = last_match
        contributor_initials = norm
        if remainder:
            remainder = remainder[:im.start()].strip()
        else:
            main_text = search_in[:im.start()].strip() or None

    bibliography = remainder or None
    return main_text, bibliography, contributor_initials


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())


def normalize_hebrew(s: str) -> str:
    """Keep only Hebrew consonant letters (\\u05d0-\\u05ea) -- drops niqqud
    (vowel points), cantillation marks, and any Latin/punctuation noise. An
    independent signal from normalize()/transliteration matching: OCR
    quality on the Hebrew glyphs and on the English transliteration in the
    same entry are two different recognition problems, so one being garbled
    doesn't imply the other is (confirmed on root 9: 'eben' xlit and 'אבה'
    Hebrew both OCR cleanly for the SAME entry, but that won't always hold --
    checking both catches cases neither alone would)."""
    return "".join(c for c in s if "א" <= c <= "ת")


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


def load_expectations(twot_map: dict) -> tuple[list[str], dict, dict, dict]:
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
    return main_numbers, seq_index, expected_xlit, expected_gloss


def load_expected_lemma(twot_map: dict) -> dict[str, str]:
    """{root: normalized Hebrew consonants of the ROOT's OWN lemma} (not
    aggregated across sub-entries, which have their own different Hebrew
    words) -- an independent-of-transliteration signal for confirming a
    candidate's identity, since Hebrew-glyph OCR quality and English-
    transliteration OCR quality are different recognition problems on the
    same source image."""
    expected_lemma: dict[str, str] = {}
    for k, entries in twot_map.items():
        m = re.match(r"^(\d+)$", k)
        if m and entries[0].get("lemma"):
            expected_lemma[m.group(1)] = normalize_hebrew(entries[0]["lemma"])
    return expected_lemma


def load_derivative_sequences(twot_map: dict) -> dict[str, list[str]]:
    """{root: [normalized xlit, ...]} in alphabetical sub-entry order (3a,
    3b, 3c, 3d...) -- the book's own 'Derivative'/'Derivatives' lists follow
    this exact order, and matching the WHOLE sequence against known xlits is
    a far stronger anchor than any single number+paren match, since OCR
    reads English transliterations far more reliably than it reads the
    number+letter+Hebrew that precedes each one (confirmed by direct
    comparison: root 3's list OCRs as '38 (ebyon)... 30 (abiyond)... 36
    (reed, papyrus)... 36 (oh!)' -- the leading number+letter is scrambled
    nearly every time, but 'ebyon'/'abiyond' match 3a/3b's real xlits
    cleanly)."""
    by_root: dict[str, list[tuple[str, dict]]] = {}
    for k, entries in twot_map.items():
        m = re.match(r"^(\d+)([a-z]*)$", k)
        root, suffix = m.group(1), m.group(2)
        if suffix:
            by_root.setdefault(root, []).append((suffix, entries[0]))
    return {
        root: [normalize(e["xlit"]) for _, e in sorted(items) if e.get("xlit")]
        for root, items in by_root.items()
    }


PAREN_RE = re.compile(r"\(([^)]{2,30})\)")
# Two distinct list-introduction patterns: roots with independent standalone
# meaning get an explicit "Derivative(s)" heading before their sub-entry
# list; roots that only exist grammatically as the common root of their
# derivatives (no meaning of their own) skip straight from "Assumed root of
# the following." to the numbered list with no "Derivatives" heading at all
# (confirmed on entry 1 directly: root 1 has 2 derivatives but was invisible
# to a Derivative(s)-only matcher because the book never prints that word for
# it -- 455 "Assumed root of the following" occurrences in the book, a
# pattern too common to skip).
DERIV_KEYWORD_RE = re.compile(r"Derivatives?\b|Assumed root of the following\.?")
DERIV_WINDOW = 700
DERIV_MIN_AVG_SCORE = 0.5

# Pages a candidate root's own known page (from a verified/embedded-only
# page header, see combine_sources.py) may plausibly differ from a keyword
# occurrence's actual page before that candidate is rejected outright.
PAGE_PLAUSIBILITY_TOLERANCE = 20


def find_derivative_anchors(full_text: str, deriv_seqs: dict[str, list[str]],
                             verbose: bool = True,
                             page_for_offset=None,
                             expected_page_by_root: dict[str, int] | None = None) -> dict[str, int]:
    """Scan every list-introduction occurrence ('Derivative(s)' or 'Assumed
    root of the following'), extract the parenthetical transliterations
    immediately following it, and align that extracted sequence against
    every candidate root's known derivative-xlit sequence (roots with >=2
    derivatives only -- a single-item sequence isn't distinctive enough to
    disambiguate reliably). Returns {root: keyword_end_position} for
    whichever root scored best at each keyword occurrence, keeping only the
    highest-scoring occurrence per root if it appears (or is coincidentally
    matched) more than once.

    If `page_for_offset` and `expected_page_by_root` are also given, a
    candidate root is rejected at a given occurrence when it has a KNOWN
    expected page (from a page header) implausibly far
    (> PAGE_PLAUSIBILITY_TOLERANCE) from that occurrence's actual page --
    confirmed necessary directly: root 420's own (unrelated, short)
    expected sequence ['dehi', 'midheh'] scores 0.533 against root 1's own
    REAL trigger's parens ['eh', 'ahfh', ...], beating root 1's own score of
    0.375 outright, even though root 420 goes on to score ~1.0 against its
    OWN real trigger elsewhere in the book. Helps when the colliding
    candidate (root 420 here) has a known page to rule it out by.

    Tried and reverted a "global-best" two-pass restructuring meant to catch
    this more generally (a root should only win an occurrence if that
    occurrence is ALSO that root's own best-scoring occurrence anywhere in
    the book, so a root with a genuinely better occurrence elsewhere
    wouldn't be allowed to steal a weaker root's only real one) -- it does
    fix the root-1-vs-420 case, but confirmed directly to make things worse
    overall (anchor coverage dropped 690->650 on a full-book run): a root
    with a weak/short expected sequence can ALSO score higher at some
    OTHER unrelated position than at its own true (low-scoring) occurrence,
    so "always take a root's single global-best score" just relocates the
    same short-sequence collision problem rather than solving it, and with
    a demonstrated net-negative effect on other roots. Reverted rather than
    ship an unvalidated regression to a function this heavily shared;
    root 1 itself remains a known, narrow, unresolved case (see
    combine_sources.py's docstring / memory notes) -- structurally the
    first entry of a Hebrew-letter section, with no page header of its own
    to lean on, and a 2-item derivative sequence too short (<5 chars each)
    to reliably self-disambiguate against unrelated text elsewhere."""
    multi_root_seqs = {root: seq for root, seq in deriv_seqs.items() if len(seq) >= 2}
    best_per_root: dict[str, tuple[float, int]] = {}
    for m in DERIV_KEYWORD_RE.finditer(full_text):
        window = full_text[m.end():m.end() + DERIV_WINDOW]
        # A derivative's own gloss can carry an inline Scripture citation
        # BETWEEN list items, not just trailing after the whole list -- e.g.
        # root 2: "2a ('öbed) destruction (Num 24:20, 24 only). 2b ('aheda)
        # lost thing...". Naively taking "the next len(seq) parens" then
        # shifts every subsequent item out of alignment against seq (2b's
        # real xlit compared against seq[2] instead of seq[1], etc.),
        # confirmed directly: root 2's real occurrence scored only 0.438 --
        # under DERIV_MIN_AVG_SCORE -- because of exactly this misalignment,
        # even though its FIRST item ('öbed) matched perfectly on its own.
        # A real transliteration never contains a digit (Hebrew
        # romanization is letters/apostrophes/diacritics only); a citation
        # always does (chapter:verse) -- filtering on the RAW paren content
        # before normalize() strips digits away is what makes this a safe,
        # cheap distinguisher.
        parens = [normalize(pm.group(1)) for pm in PAREN_RE.finditer(window) if not re.search(r"\d", pm.group(1))]
        if not parens:
            continue
        occurrence_page = page_for_offset(m.end()) if page_for_offset else None
        best = (0.0, None)
        for root, seq in multi_root_seqs.items():
            # only reject on UNDER-coverage (not enough parens to even try
            # the full expected sequence) -- extra trailing parens beyond
            # len(seq) are normal (they're discussion-prose citations after
            # a short derivative list, e.g. root 1's 2-item list followed by
            # "(Isa 24:4)"-style references within the scan window) and
            # don't penalize the score, since only the first len(seq) are
            # ever compared.
            if len(parens) < len(seq):
                continue
            if (expected_page_by_root is not None and occurrence_page is not None
                    and root in expected_page_by_root
                    and abs(expected_page_by_root[root] - occurrence_page) > PAGE_PLAUSIBILITY_TOLERANCE):
                continue
            n = len(seq)
            avg = sum(SequenceMatcher(None, seq[j], parens[j]).ratio() for j in range(n)) / n
            if avg > best[0]:
                best = (avg, root)
        score, root = best
        if root and score >= DERIV_MIN_AVG_SCORE:
            if root not in best_per_root or score > best_per_root[root][0]:
                best_per_root[root] = (score, m.end())
    result = {root: pos for root, (score, pos) in best_per_root.items()}
    if verbose:
        print(f"derivative-list anchors: {len(result)}/{len(multi_root_seqs)} "
              f"multi-derivative roots confirmed via list matching")
    return result


DERIV_BACKWARD_WINDOW = 1500
PAGE_HEADER_ZONE = 60  # chars from a page's own text-chunk start


def make_page_start_offsets(page_offsets: list[tuple[int, int]]) -> list[int]:
    """Sorted list of char offsets where each page's own OCR text begins --
    used to detect when a candidate match falls in a page's running-header
    zone rather than real body content."""
    return sorted(off for off, _ in page_offsets)


def near_page_start(pos: int, page_starts: list[int], zone: int = PAGE_HEADER_ZONE) -> bool:
    """True if `pos` falls within the first `zone` chars of whichever page
    contains it -- i.e. plausibly a running header, not body text. TWOT
    prints a running head ('N hebrew (xlit)') at the physical top of every
    page showing which entry the page covers; Tesseract has no concept of
    header vs. body regions and merges it straight into the text stream.
    Confirmed directly on entry 3: page 24 opens with '3 אבה (aba)' followed
    immediately by the tail of entry 2's still-unfinished sentence from the
    previous page, not by entry 3's real content -- entry 3 actually starts
    much further down the same page, right after entry 2's own closing
    signature. A header match scores just as well against CANDIDATE_RE as a
    real opening (same literal pattern), so position -- not content -- is
    what distinguishes them."""
    i = bisect.bisect_right(page_starts, pos) - 1
    if i < 0:
        return False
    return pos - page_starts[i] < zone


HEBREW_CONTEXT_WINDOW = 50


def hebrew_nearby_score(pos: int, full_text: str, expected_lemma: str, window: int = HEBREW_CONTEXT_WINDOW) -> float:
    """How well the Hebrew consonants near `pos` match a root's known lemma
    -- substring containment scores a clean 1.0 (the common case: the exact
    word appears somewhere in the surrounding noise), fuzzy ratio as a
    fallback for partial OCR damage. A window rather than an exact position
    because bidi reordering means the Hebrew word isn't reliably immediately
    before or after the number+paren match -- it can land on either side."""
    if not expected_lemma:
        return 0.0
    context = normalize_hebrew(full_text[max(0, pos - window):pos + window])
    if not context:
        return 0.0
    if expected_lemma in context:
        return 1.0
    return SequenceMatcher(None, expected_lemma, context).ratio()


def segment_derivative_anchored(ocr_dir: Path, twot_map: dict, main_numbers: list, seq_index: dict,
                                 expected_xlit: dict, expected_gloss: dict, verbose: bool = True) -> dict:
    """A root's own opening line ('N (hebrew) (xlit) definition...') is
    often the weakest, most collision-prone signal in the book (short
    transliterations especially -- see segment_blockwalk's docstring). Its
    Derivative(s) list, when it has one, is the strongest: matching a whole
    ordered sequence of sub-entry transliterations essentially can't happen
    by chance. This anchors on the derivative list first via
    find_derivative_anchors(), then searches backward from there for the
    root's own opening candidate -- accepting a much lower individual score
    than segment()/segment_blockwalk() would alone, since the derivative
    match already independently confirms which root this is. Running-header
    lookalikes (see near_page_start) are excluded from that backward search
    entirely, not just deprioritized -- a header can score a perfect 1.0
    against the real xlit precisely because it prints the same text, so
    scoring alone can't break the tie. Candidate scoring also checks the
    known Hebrew lemma nearby (see hebrew_nearby_score) alongside the
    transliteration -- independent OCR problems on the same source image, so
    checking both catches entries where one is clean but the other isn't."""
    full_text, page_offsets = load_pages(ocr_dir)
    page_for_offset = make_page_for_offset(page_offsets)
    page_starts = make_page_start_offsets(page_offsets)

    deriv_seqs = load_derivative_sequences(twot_map)
    deriv_anchors = find_derivative_anchors(full_text, deriv_seqs, verbose)
    expected_lemma = load_expected_lemma(twot_map)

    found: dict[str, int] = {}
    boundary_text: dict[str, str] = {}
    for root, deriv_pos in deriv_anchors.items():
        if root not in expected_xlit:
            continue
        lo = max(0, deriv_pos - DERIV_BACKWARD_WINDOW)
        window = full_text[lo:deriv_pos]
        best_pos, best_score = None, 0.0
        for m in CANDIDATE_RE.finditer(window):
            num, paren = m.group(1), m.group(2)
            if num != root:
                continue
            abs_pos = lo + m.start(1)
            if near_page_start(abs_pos, page_starts):
                continue
            cand_norm = normalize(paren)
            xlit_score = max(
                (SequenceMatcher(None, cand_norm, exp).ratio() for exp in expected_xlit[root]), default=0,
            ) if len(cand_norm) >= 2 else 0.0
            heb_score = hebrew_nearby_score(abs_pos, full_text, expected_lemma.get(root, ""))
            score = max(xlit_score, heb_score)
            if score <= 0:
                continue
            if score >= best_score:
                best_score, best_pos = score, abs_pos
        start = best_pos if best_pos is not None else max(0, deriv_pos - 200)
        found[root] = start
        boundary_text[root] = full_text[start:start + 80].replace("\n", " ")
    if verbose:
        backward_hits = sum(1 for r in found if found[r] != max(0, deriv_anchors[r] - 200))
        print(f"derivative-anchored: {len(found)} roots "
              f"({backward_hits} with a confirmed own-opening match, "
              f"{len(found) - backward_hits} using a fallback offset before the list)")

    result = build_boundary_result(full_text, page_for_offset, main_numbers, expected_gloss, found)
    for root in result:
        result[root]["boundary_text"] = boundary_text.get(root)
    return result


def find_confirmed_initials(full_text: str, verbose: bool = True) -> set[str]:
    """Only the book's own 44-name Contributors roster counts as confirmed --
    a frequency-based fallback was tried and dropped: it added exactly two
    extra codes ('EJ', 'EA'), and both turned out to be repeated bibliography
    citations of prolific authors (e.g. 'E. J. Young') rather than real
    contributor signatures, confirmed via direct page inspection. Bibliography
    citations recur often enough across the book to cross any frequency bar
    that also has to stay low enough to catch a genuine contributor."""
    if verbose:
        counts = Counter()
        for m in INITIALS_CANDIDATE_RE.finditer(full_text):
            norm = re.sub(r"[\s.]", "", m.group(1))
            if 2 <= len(norm) <= 3:
                counts[norm] += 1
        print(f"confirmed contributor initials: {len(AUTHORITATIVE_INITIALS)} "
              f"from the book's own Contributors list (frequency fallback disabled)")
    return set(AUTHORITATIVE_INITIALS)


BIDI_MARKS_RE = re.compile(r"[‎‏]")  # LRM/RLM -- Tesseract's heb+eng
# model inserts these at every Hebrew/English script boundary as a bidi
# rendering hint. They carry no informational content and litter every
# entry's raw text (visibly, if you inspect it directly); stripped once here
# so every downstream consumer (segment(), segment_blockwalk(),
# segment_derivative_anchored(), and the review export) gets clean text
# without needing its own strip, and so offsets stay consistent throughout
# (stripped before length is measured, not after).


def load_pages(ocr_dir: Path) -> tuple[str, list[tuple[int, int]]]:
    page_files = sorted(ocr_dir.glob("page-*.txt"))
    full_text_parts, page_offsets = [], []
    offset = 0
    for pf in page_files:
        page_num = int(pf.stem.split("-")[1])
        text = BIDI_MARKS_RE.sub("", pf.read_text(encoding="utf-8"))
        page_offsets.append((offset, page_num))
        full_text_parts.append(text)
        offset += len(text) + 1
    return "\n".join(full_text_parts), page_offsets


def make_page_for_offset(page_offsets: list[tuple[int, int]]):
    def page_for_offset(char_offset: int) -> int:
        page_num = page_offsets[0][1]
        for start, pnum in page_offsets:
            if start > char_offset:
                break
            page_num = pnum
        return page_num
    return page_for_offset


def build_boundary_result(full_text: str, page_for_offset, main_numbers: list,
                           expected_gloss: dict, found: dict) -> dict:
    """Shared by segment() and segment_blockwalk() -- turns
    {number: start_offset} into the {number: {text, confidence, pages}} shape,
    scoring confidence by whether the captured text contains one of the
    root's known gloss words."""
    boundaries = sorted(found.items(), key=lambda kv: kv[1])
    texts_pages = {}
    for i, (num, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(full_text)
        raw = full_text[start:end]
        raw = re.sub(r"^\s*\d{1,4}\b", "", raw, count=1)
        text = re.sub(r"\s+", " ", raw).strip()
        pages = sorted({page_for_offset(start), page_for_offset(max(start, end - 1))})
        texts_pages[num] = (text, pages)

    result = {}
    for num in main_numbers:
        if num in texts_pages:
            text, pages = texts_pages[num]
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
        result[num] = {"text": text, "confidence": confidence, "pages": pages}
    return result


BLOCKWALK_MAX_WIDEN = 6
# A flat low floor isn't enough on its own -- short expected transliterations
# (e.g. "bb", "eb") coincidentally score high against unrelated words via
# SequenceMatcher regardless of the floor's value (confirmed empirically:
# "abbir" vs "abib" scores 0.67), so loose_threshold()'s existing
# length-aware scaling is reused here instead of a constant. Without ANY
# floor, small root numbers (1, 2, 3...) false-positive whenever OCR splits a
# stray space inside a larger multi-digit number (e.g. "1 38" read from a
# garbled "138"), since a bare leading digit + nearby paren alone satisfies
# CANDIDATE_RE -- the block-boundary constraint doesn't catch that either.


def segment_blockwalk(ocr_dir: Path, twot_map: dict, main_numbers: list, seq_index: dict,
                       expected_xlit: dict, expected_gloss: dict, verbose: bool = True) -> dict:
    """Alternative segmentation strategy: instead of scoring every candidate
    globally by transliteration match (segment()'s approach), treat confirmed
    contributor-initials occurrences as hard block boundaries an entry can
    never be matched across. Within the narrow window up to the next
    unclaimed boundary, the first line-start number+paren match for the
    expected root wins outright -- no transliteration floor needed, because
    the block structure itself is doing the disambiguation. Higher precision,
    lower recall than segment(): meant to be combined with it (and the other
    OCR sources) in combine_sources.py, not used alone.

    This was tried as a strict greedy left-to-right walk first and failed
    badly (545/3057) -- one missed/garbled number let the search jump
    arbitrarily far forward into someone else's block. The fix is the
    ceiling: a candidate for root N may never be searched for past the
    BLOCKWALK_MAX_WIDEN-th unclaimed initials checkpoint ahead of where root
    N-1 was found, matching the observation that a genuine entry never gets
    "resequenced" out of its own initials-delimited block."""
    full_text, page_offsets = load_pages(ocr_dir)
    page_for_offset = make_page_for_offset(page_offsets)

    bib_match = BIBLIOGRAPHY_RE.search(full_text)
    body_start = max(0, bib_match.start() - 5000) if bib_match else 0

    confirmed_initials = find_confirmed_initials(full_text, verbose)
    checkpoints = sorted(
        m.end() for m in INITIALS_CANDIDATE_RE.finditer(full_text)
        if re.sub(r"[\s.]", "", m.group(1)) in confirmed_initials and m.start() > body_start
    )

    candidates: dict[str, list[int]] = {}
    for m in CANDIDATE_RE.finditer(full_text):
        num, paren = m.group(1), m.group(2)
        if num not in expected_xlit or m.start(1) < body_start:
            continue
        cand_norm = normalize(paren)
        if len(cand_norm) < 2:
            continue
        # threshold by the length of whichever expected variant actually won
        # the comparison, not the shortest variant overall -- entry 1 has
        # xlit variants {"bb", "eb", "abib"}; "abbir" scores 0.67 against
        # "abib" (len 4, needs >=0.7) but would wrongly pass a threshold
        # keyed to "bb"'s length (len 2, needs only >=0.65 under loose_
        # threshold, and even strict_threshold(2)=0.85 being applied to the
        # wrong variant either over- or under-shoots depending which variant
        # is shortest).
        best_score, best_exp = max(
            ((SequenceMatcher(None, cand_norm, exp).ratio(), exp) for exp in expected_xlit[num]),
            default=(0, ""),
        )
        if best_score < loose_threshold(len(best_exp)):
            continue
        candidates.setdefault(num, []).append(m.start(1))

    found: dict[str, int] = {}
    search_from = body_start
    ckpt_idx = 0
    for num in main_numbers:
        chosen = None
        for widen in range(BLOCKWALK_MAX_WIDEN + 1):
            idx = ckpt_idx + widen
            ceiling = checkpoints[idx] if idx < len(checkpoints) else len(full_text)
            in_window = [pos for pos in candidates.get(num, []) if search_from <= pos <= ceiling]
            if in_window:
                chosen = min(in_window)
                break
            if idx >= len(checkpoints):
                break
        if chosen is not None:
            found[num] = chosen
            search_from = chosen + 1
            while ckpt_idx < len(checkpoints) and checkpoints[ckpt_idx] < search_from:
                ckpt_idx += 1
    if verbose:
        print(f"blockwalk: {len(found)}/{len(main_numbers)}")

    return build_boundary_result(full_text, page_for_offset, main_numbers, expected_gloss, found)


def segment(ocr_dir: Path, twot_map: dict, main_numbers: list, seq_index: dict,
            expected_xlit: dict, expected_gloss: dict, verbose: bool = True) -> dict:
    """Returns {twot_number: {"text": str|None, "confidence": str, "pages": [int]}}
    for every main root in main_numbers -- always a complete dict, 'not-found'
    entries included, so results from different sources can be compared 1:1."""
    full_text, page_offsets = load_pages(ocr_dir)
    page_for_offset = make_page_for_offset(page_offsets)

    confirmed_initials = find_confirmed_initials(full_text, verbose)
    initials_end_positions = sorted(
        m.end() for m in INITIALS_CANDIDATE_RE.finditer(full_text)
        if re.sub(r"[\s.]", "", m.group(1)) in confirmed_initials
    )
    bibliography_positions = sorted(m.start() for m in re.finditer(r"[Bb]ibliography\s*:", full_text))

    def initials_shortly_before(pos: int, window: int = 200) -> bool:
        lo = pos - window
        i = bisect.bisect_left(initials_end_positions, lo)
        return i < len(initials_end_positions) and initials_end_positions[i] < pos

    def bibliography_shortly_before(pos: int, window: int = 400) -> bool:
        lo = pos - window
        i = bisect.bisect_left(bibliography_positions, lo)
        return i < len(bibliography_positions) and bibliography_positions[i] < pos

    strong_end_positions = sorted(p for p in initials_end_positions if bibliography_shortly_before(p))
    if verbose:
        print(f"{len(bibliography_positions)} Bibliography markers, "
              f"{len(strong_end_positions)} high-precision end markers")

    candidates: dict[str, list[tuple[float, bool, bool, bool, int]]] = {}
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

    def qualifies(score, gloss_hit, sig_hit, bib_hit, thresh) -> bool:
        bonus = (0.15 if gloss_hit else 0) + (0.15 if sig_hit else 0) + (0.1 if bib_hit else 0)
        return score + bonus >= thresh

    def pick_best(qualifying, prefer_early=False) -> int:
        if not prefer_early:
            return max(qualifying, key=lambda sp: sp[0])[1]
        by_position = sorted(qualifying, key=lambda sp: sp[1])
        best = by_position[0]
        for score, pos in by_position[1:]:
            if score > best[0] + 0.15:
                best = (score, pos)
        return best[1]

    anchors: dict[str, int] = {}
    for num, cands in candidates.items():
        thresh = strict_threshold(min((len(x) for x in expected_xlit[num]), default=4))
        qualifying = [(score, pos) for score, hit, sig, bib, pos in cands if qualifies(score, hit, sig, bib, thresh)]
        if qualifying:
            anchors[num] = pick_best(qualifying)
    if verbose:
        print(f"pass 1: {len(anchors)}/{len(main_numbers)}")

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
    if verbose:
        print(f"pass 2: {len(filled)}/{len(main_numbers)}")

    anchor_seq = sorted(((seq_index[n], pos) for n, pos in filled.items()))
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
            continue
        # N missing items need exactly N split points: marker[0] is anchor_a's
        # OWN end-of-entry signature (so missing[0] starts right after it),
        # marker[1] is missing[0]'s own signature (so missing[1] starts right
        # after IT), and so on -- missing[-1] ends at pos_b (anchor_b's own
        # start), already known and not part of markers_in_gap.
        #
        # A prior version prepended pos_a to markers_in_gap here, which
        # shifted every assignment one marker early: missing[0] got pos_a
        # itself (anchor_a's own START, not its end), giving it a
        # zero-length span and handing anchor_a's ENTIRE content to
        # missing[0] instead. Confirmed directly: with anchor_a=root 4 and
        # missing=[root 5], the single found marker (J.B.P., root 4's real
        # closing signature) was being discarded in favor of pos_a, so root
        # 5 was assigned root 4's whole "father" discussion verbatim.
        for j, num in enumerate(missing):
            filled[num] = markers_in_gap[j]
    if verbose:
        print(f"pass 3: {len(filled)}/{len(main_numbers)}")

    # pass 4: a gap with exactly ONE missing number is unambiguous by
    # construction -- whatever's in there IS that entry, whether or not its
    # own leading digit ever recognized (confirmed directly: root 5's "5"
    # never appears anywhere in the OCR text at all, not misread as a wrong
    # character but never tokenized -- likely clipped by a column/line
    # boundary right after the dense "See no." index-stub cluster that
    # precedes it). Unlike pass 3, no marker-count match is needed since
    # there's nothing to disambiguate with only one candidate. Still try to
    # localize the split precisely (search the gap for the PRECEDING entry's
    # own Bibliography+signature, same signal truncate_at_first_signoff uses
    # downstream) rather than just handing the whole gap to the missing
    # number, which would swallow the preceding entry's real tail.
    anchor_seq = sorted(((seq_index[n], pos) for n, pos in filled.items()))
    for i in range(len(anchor_seq) - 1):
        idx_a, pos_a = anchor_seq[i]
        idx_b, pos_b = anchor_seq[i + 1]
        if idx_b - idx_a != 2:
            continue  # exactly one missing number between two filled anchors
        num = main_numbers[idx_a + 1]
        gap = full_text[pos_a:pos_b]
        bib_match = BIBLIOGRAPHY_RE.search(gap)
        split_at = None
        if bib_match:
            for m in INITIALS_CANDIDATE_RE.finditer(gap, bib_match.start()):
                if re.sub(r"[\s.]", "", m.group(1)) in AUTHORITATIVE_INITIALS:
                    split_at = pos_a + m.end()
                    break
        if split_at is None:
            # no signature found to localize the preceding entry's own end --
            # guessing would risk stealing anchor_a's whole span (assigning
            # pos_a itself would zero it out entirely), so leave not-found
            # rather than fabricate a boundary with nothing to anchor it.
            continue
        filled[num] = split_at
    if verbose:
        print(f"pass 4: {len(filled)}/{len(main_numbers)}")

    return build_boundary_result(full_text, page_for_offset, main_numbers, expected_gloss, filled)
