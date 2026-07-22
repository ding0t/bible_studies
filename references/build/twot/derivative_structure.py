"""Position-aware extraction from the PDF's embedded text layer, used to
structure each root's Derivative(s)/"Assumed root of the following" list and
link each list item to its own dedicated discussion paragraph later in the
entry (see PLAN_derivative_structure.md for the empirical background this
was designed against, and this module's own docstrings for corrections made
to that plan once measured directly against the PDF).

This is a SEPARATE extraction pass from segmenter.py's OCR-based pipeline --
it reads pymupdf's `get_text("dict")` output directly (no Tesseract), which
carries per-line position (`bbox`) and per-span font flags (incl. italic),
neither of which plain OCR text has. Confirmed empirically that this embedded
layer has NO bidi control marks (unlike the Tesseract heb+eng model's
output), so no bidi-stripping is needed here.

Scope note: only roots with >=2 derivatives get list-block + paragraph
linking, because find_derivative_anchors() (reused from segmenter.py) only
scores sequences of that length -- a single-item list isn't distinctive
enough to anchor reliably by itself. Single-derivative roots simply keep
main_text=NULL for their one derivative, same as before this feature existed.
"""
import bisect
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import pymupdf

from twot.segmenter import (
    CANDIDATE_RE, DERIV_BACKWARD_WINDOW, DERIV_KEYWORD_RE,
    SEE_NO_RE, build_boundary_result, dehyphenate, find_derivative_anchors,
    hebrew_nearby_score, load_derivative_sequences, load_expected_lemma, make_page_for_offset,
    make_page_start_offsets, near_page_start, normalize,
)

PDF_PATH = Path("/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf")

# Confirmed empirically across a book-wide page sample (front, mid, back of
# the dictionary body): left-column line x0 clusters in ~40-130, right-column
# BODY text never starts before ~240 -- confirmed by sampling every span with
# x0 in [200, 240) across pages 20-120 (709 samples): every single one is
# either a genuine left-column artifact (a short last-word fragment of a
# justified line -- "the", "of the" -- or a right-aligned contributor
# sign-off like "L.J.C.") or a bare page-footer number, never real
# right-column prose. A single threshold at RIGHT_COL_BODY_MIN_X0
# classifies all of it as col=0.
#
# TWOT right-aligns a contributor sign-off (e.g. "L.J.C.") at the end of an
# entry's Bibliography, WITHIN whichever column that entry's text is in --
# confirmed directly by rendering the actual page: root 1 (a short, LEFT-
# column entry ending "...Smick, E. B., 'Calendar,' in WBE." then, right-
# aligned on its own line, "L.J.C.") sits just before root 2's own opening,
# also left column. Because it's SHORT and right-aligned, its own x0 (207.2)
# lands well past a narrower gutter despite visually belonging to the LEFT
# column. Left uncorrected, this gets column-misclassified as col=1 and its
# y0 places it, once sorted into reading order, in the MIDDLE of whatever
# unrelated right-column text happens to share that vertical position on the
# page (confirmed: root 2's own independently-continuing right-column
# discussion on that same page) -- reading as "...Smick, E. B., in
# Bibliography). L.J.C. Psalms 49 and 73 are frequently cited..."
# mid-paragraph. Since it IS a confirmed contributor's initials, this
# corrupts segmenter.py's truncate_at_first_signoff() into cutting the
# unrelated entry short deep inside its own legitimate text (same mechanism,
# mirrored: root 2's own real sign-off "R.L.H." similarly lands inside root
# 3's discussion on the following page).
#
# An ordinary (non-sign-off) fragment in this same band causes the same
# reading-order corruption, just without the sign-off-specific truncation
# side effect -- confirmed directly: root 22's own entry ran straight through
# root 23's opening ("23 [Hebrew] ('gr) II. Assumed root of the following.")
# and swallowed all of root 23 and its derivatives, because the trailing
# word "the" (x0=220.3, the tail of the LEFT column's "...\"Apis,\" the"
# line) got column-misclassified as col=1 and sorted in just above root 23's
# real opening, shrinking the gap find_entry_openings() measures from a
# genuine ~18pt down to ~4.8pt -- under ENTRY_OPENING_MIN_GAP, so root 23's
# boundary was never detected at all.
#
# Earlier attempt (WRONG, reverted): dropping any fragment with x0 in this
# band outright deleted these marks entirely -- since sign-offs are genuine
# data, not noise, that lost real data (root 2's own contributor became
# unrecoverable). A later attempt reclassified ONLY sign-off-shaped
# fragments, which fixed the sign-off case but left ordinary wrapped words
# like "the"/"of the" misclassified (the root 22/23 failure above). The
# correct fix is the general one: this x0 band is never genuine right-column
# body text, full stop, so everything in it reclassifies to col=0 uniformly.
RIGHT_COL_BODY_MIN_X0 = 240.0


ITALIC_FLAG = 2  # pymupdf span["flags"] bit for italic

# pymupdf's dict-mode line clustering sometimes fragments a single visual
# line into multiple "line" objects right at a font/style boundary (confirmed
# directly: derivative 4a's own discussion-paragraph start -- the exact kind
# of line this module depends on -- prints on the page as one baseline,
# "'ab. Father, forefather. This primitive noun...", but pymupdf returns it
# as THREE separate line dicts at y0=614.3/614.4/615.2, split exactly where
# the italic "Father, forefather." run begins and ends). A book-wide
# gap-distribution sample (same column, consecutive y0s) is cleanly bimodal:
# same-line fragments cluster under 2pt apart, real line-to-line spacing has
# a median of ~9.4pt -- so a 3pt threshold safely separates the two without
# merging genuinely distinct lines.
LINE_MERGE_Y_TOLERANCE = 3.0


@dataclass
class PositionedLine:
    page: int
    y0: float
    x0: float
    col: int  # 0 = left column, 1 = right column
    runs: list[tuple[str, bool]] = field(default_factory=list)  # (text, italic), reading order

    @property
    def text(self) -> str:
        return " ".join(t for t, _ in self.runs)


def _raw_dict_lines(page) -> list[tuple[float, float, int, str, bool]]:
    """(x0, y0, col, text, italic) for every non-empty SPAN on a page (not
    yet grouped into lines) -- spans, not pymupdf's own "line" dicts, are the
    right unit here specifically because a single visual line can carry
    spans of different styles (plain transliteration then italic gloss),
    and pymupdf's own line-vs-line split is exactly what's unreliable at
    those boundaries (see LINE_MERGE_Y_TOLERANCE)."""
    raw = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue
                x0, y0 = span["bbox"][0], span["bbox"][1]
                italic = bool(span["flags"] & ITALIC_FLAG)
                col = 0 if x0 < RIGHT_COL_BODY_MIN_X0 else 1
                raw.append((x0, y0, col, text, italic))
    return raw


def _merge_line_fragments(raw: list[tuple[float, float, int, str, bool]],
                           page_num: int) -> list[PositionedLine]:
    """Groups same-column spans whose y0 falls within LINE_MERGE_Y_TOLERANCE
    of the group's running y0 into one logical PositionedLine, ordered
    left-to-right by x0, preserving each span's own italic flag as a
    separate run -- this is what lets find_paragraph_starts() see "plain
    transliteration, then italic gloss" as adjacent runs on the same line
    even though pymupdf reported them as different line dicts."""
    by_col: dict[int, list[tuple[float, float, str, bool]]] = {0: [], 1: []}
    for x0, y0, col, text, italic in raw:
        by_col[col].append((y0, x0, text, italic))

    merged: list[PositionedLine] = []
    for col, frags in by_col.items():
        frags.sort()  # by y0, then x0
        group: list[tuple[float, float, str, bool]] = []
        prev_y0 = None
        for y0, x0, text, italic in frags:
            if prev_y0 is not None and y0 - prev_y0 > LINE_MERGE_Y_TOLERANCE:
                merged.append(_flush_group(group, page_num, col))
                group = []
            group.append((y0, x0, text, italic))
            prev_y0 = y0
        if group:
            merged.append(_flush_group(group, page_num, col))
    return merged


def _flush_group(group: list[tuple[float, float, str, bool]], page_num: int, col: int) -> PositionedLine:
    group.sort(key=lambda g: g[1])  # left-to-right by x0
    y0 = min(g[0] for g in group)
    x0 = group[0][1]
    runs = [(g[2], g[3]) for g in group]
    return PositionedLine(page_num, y0, x0, col, runs)


def extract_positioned_lines(pdf_path: Path = PDF_PATH,
                              first_page: int = 0, last_page: int | None = None) -> list[PositionedLine]:
    """All non-empty text lines across the given PDF page range, in reading
    order (left column top-to-bottom, then right column top-to-bottom, per
    page) -- the same reading-order fix behind the Tesseract `colsplit`
    source, but done directly in PDF-point space using the embedded text
    layer's own column geometry rather than a pixel-space gutter detector.
    Same-visual-line span fragments are merged first (see
    _merge_line_fragments)."""
    doc = pymupdf.open(pdf_path)
    end = last_page if last_page is not None else doc.page_count
    lines: list[PositionedLine] = []
    for page_num in range(first_page, end):
        raw = _raw_dict_lines(doc[page_num])
        page_lines = _merge_line_fragments(raw, page_num)
        page_lines.sort(key=lambda l: (l.col, l.y0))
        lines.extend(page_lines)
    doc.close()
    return lines


def build_full_text(lines: list[PositionedLine]) -> tuple[str, list[int]]:
    """Returns (full_text, line_start_offsets): line_start_offsets[i] is the
    char offset in full_text where lines[i]'s own text begins, so a regex
    match position found in full_text (by the segmenter.py helpers this
    module reuses, e.g. find_derivative_anchors/CANDIDATE_RE) can be mapped
    back to its source PositionedLine via line_for_offset()."""
    parts, offsets = [], []
    pos = 0
    for line in lines:
        offsets.append(pos)
        parts.append(line.text)
        pos += len(line.text) + 1  # +1 for the joining space below
    return " ".join(parts), offsets


def line_for_offset(offset: int, line_start_offsets: list[int]) -> int:
    i = bisect.bisect_right(line_start_offsets, offset) - 1
    return max(0, min(i, len(line_start_offsets) - 1))


def build_page_offsets(lines: list[PositionedLine], line_start_offsets: list[int]) -> list[tuple[int, int]]:
    """Same shape as segmenter.py's load_pages() page_offsets
    ([(char_offset, page_num), ...], page_num 0-indexed matching pymupdf) --
    lets this module reuse make_page_for_offset()/make_page_start_offsets()
    unmodified."""
    page_offsets = []
    seen = set()
    for line, off in zip(lines, line_start_offsets):
        if line.page not in seen:
            page_offsets.append((off, line.page))
            seen.add(line.page)
    return page_offsets


# --- Page-header extraction ---------------------------------------------
#
# TWOT prints exactly one running head per page, in the outer top margin --
# well above the body text (confirmed directly: body starts around y0=65,
# the header sits at y0=25-43) and near the page's outer edge (left margin
# on even pages, right on odd -- standard verso/recto convention, confirmed
# across a random 12-page sample spanning the whole book). It names the
# HIGHEST root number that begins on that page (a "last headword" guide-word
# convention, not "current entry as of page top") -- confirmed against 5
# consecutive pages (p.24-28): each header matched the root that starts
# somewhere on that specific page, including cases where that root doesn't
# start until deep in the page (root 4 starts near the bottom of the left
# column on p.25, yet the header at the very top already says "4") and cases
# where several intervening roots (6,7,8) get no header of their own because
# they neither start nor are the last to start on any single page. This
# makes it an anchor signal independent of body-text matching -- useful
# specifically because body-text matching is what's failing when OCR drops
# characters (see combine_sources.py's page-header cross-check).
#
# A header can split into two PositionedLines at a font-boundary (plain root
# number+Hebrew, then italic transliteration) the same way body text does --
# confirmed on p.97 ('176 ,,w~' at y0=25.6, '(ashshur)' at y0=42.6, a 17pt
# gap far past LINE_MERGE_Y_TOLERANCE) -- so headers are read directly from
# already-extracted PositionedLines (not re-merged) and concatenated by
# page+y0 order here instead.
HEADER_Y0_MAX = 55.0


def extract_page_headers(lines: list[PositionedLine]) -> dict[int, dict]:
    """{page: {"root": root_number_str, "raw": raw_header_text}} for every
    page whose running head could be parsed -- a page with no header
    (confirmed to happen: front matter, section-break pages) or unparsable
    header text is simply omitted. `raw` is kept alongside `root` (not just
    the parsed number) so a reviewer can spot-check the actual matched
    evidence directly, same reasoning as entries.boundary_text."""
    by_page: dict[int, list[PositionedLine]] = {}
    for line in lines:
        if line.y0 < HEADER_Y0_MAX:
            by_page.setdefault(line.page, []).append(line)

    result: dict[int, dict] = {}
    for page, frags in by_page.items():
        frags.sort(key=lambda l: l.y0)
        text = " ".join(l.text for l in frags).strip()
        m = CANDIDATE_RE.match(text)
        if m:
            result[page] = {"root": m.group(1), "raw": text}
    return result


# --- List-block detection ----------------------------------------------
#
# Earlier design (removed): scanned forward for ANY line matching a plain-
# transliteration+italic-gloss pattern ("'ab. Father, forefather...")
# anywhere in a multi-thousand-char window after the trigger, on the theory
# that this marked a derivative's own dedicated discussion paragraph. Wrong:
# confirmed directly against the PDF (root 4, p.24) that this same pattern
# is ALSO how TWOT opens its MAIN BODY discussion -- restating the entry's
# key transliteration+gloss is a standard dictionary convention, not
# something specific to a derivative. The scan was walking straight through
# the list block and attributing the main body's own opening to whichever
# derivative happened to be last in the list -- e.g. 3a/4a's captured text
# was really the start of ROOT 3/4's own discussion, not a paragraph
# dedicated to that one derivative.
#
# Real structure (confirmed via per-line y0 gaps, both columns): the
# Derivatives/Assumed-root trigger begins a tightly-spaced LIST BLOCK --
# each item's own marker line ("3a ... needy person.", "4a ... father,
# forefather.") sometimes followed by a short attached note on the next
# line or two ("ASV, RSV similar, except that..." for 4a) -- then a
# distinctly larger vertical gap into the main body's own opening paragraph.
# Root 3: within-list gaps 8.6-12.4pt, block-end gap 14.4pt. Root 4:
# within-list gaps 5.7-9.6pt, block-end gap 19.5pt. Different magnitudes per
# root (font-size/leading differences), but always the largest gap in the
# sequence -- so a relative threshold (BLOCK_END_GAP_MULTIPLIER over that
# root's own within-block median), not one fixed absolute cutoff.
#
# This also means each derivative's OWN keys/expected xlit (already known
# from twot_map -- no fuzzy matching needed) can bound attribution directly:
# a derivative's captured text is everything between ITS OWN list marker and
# the NEXT derivative's marker (or, for a root's last derivative, the
# block-end gap) -- exactly the boundary the user described by hand
# ("4b text even is on the fourth line after 4a, then a blank line, then
# the main body starts").

LIST_ITEM_RE = re.compile(r"^(\d+[a-z])\b")

# TWOT's embedded text layer sometimes encodes the numeral "1" as a
# lowercase "l" -- a font glyph collision, confirmed directly on root 1's
# own derivatives, which print as "la"/"lb" instead of "1a"/"1b" in the
# extracted text (the same underlying issue that garbles root 1's own
# opening digit elsewhere in this module). LIST_ITEM_RE requires a real
# digit, so root 1's items would otherwise never match. Rather than loosen
# the pattern book-wide -- which would risk matching unrelated words
# starting with "l" -- this fallback only applies when the key being
# searched for is itself a direct derivative of root 1 (e.g. "1a", "1b").
LIST_ITEM_MISREAD_RE = re.compile(r"^l([a-z])\b")


def _matches_list_item_key(text: str, key: str) -> bool:
    m = LIST_ITEM_RE.match(text)
    if m and m.group(1) == key:
        return True
    if len(key) == 2 and key[0] == "1":
        m2 = LIST_ITEM_MISREAD_RE.match(text)
        if m2 and "1" + m2.group(1) == key:
            return True
    return False

# How far past the trigger (or the previously-found item) to look for each
# derivative's own list marker -- generous for a list block (which is a
# handful of short lines), not for a whole entry's discussion.
LIST_ITEM_SEARCH_WINDOW = 80

# A block-end (or item-end) gap must exceed this multiple of the list
# block's own running-median line-to-line gap to count as a paragraph break
# rather than a normal short-note wrap. See module comment above for the
# two data points (1.41x and ~3.0x) this was picked to safely separate.
BLOCK_END_GAP_MULTIPLIER = 1.35
BOOK_WIDE_MEDIAN_LINE_GAP = 9.4  # fallback when a block has too few internal gaps to measure its own

# Safety cap on how far past the last list item to look for the block-end
# gap, and the minimum length (chars) a captured snippet needs to be worth
# keeping -- guards against e.g. 3d's wrapped "(etymology dubious.)" tail
# ("ous.)") being stored as if it were a real standalone note.
MAX_TAIL_LINES = 8
MIN_SNIPPET_CHARS = 15


def find_list_items(lines: list[PositionedLine], trigger_li: int,
                     ordered_keys: list[str]) -> dict[str, int]:
    """{derivative_key: line_idx} for each of ordered_keys (a root's
    derivatives in order, e.g. ['3a','3b','3c','3d']) whose own list-item
    marker line was located scanning forward from the trigger line. Keys
    are matched in STRICT sequence -- each search starts right after the
    previous match -- so a stray "3a"-shaped substring elsewhere can't be
    matched out of order. A key not found within LIST_ITEM_SEARCH_WINDOW
    lines of where its search started is simply omitted (matches the
    existing "not confidently located" semantics used elsewhere here)."""
    found: dict[str, int] = {}
    search_from = trigger_li
    for key in ordered_keys:
        limit = min(search_from + LIST_ITEM_SEARCH_WINDOW, len(lines))
        match_idx = None
        for i in range(search_from, limit):
            if _matches_list_item_key(lines[i].text.strip(), key):
                match_idx = i
                break
        if match_idx is None:
            continue
        found[key] = match_idx
        search_from = match_idx + 1
    return found


def _running_median_gap(lines: list[PositionedLine], lo_li: int, hi_li: int) -> float:
    """Median line-to-line y0 gap between lo_li and hi_li (inclusive),
    within the same page/column only -- the list block's own normal
    spacing, used as the baseline BLOCK_END_GAP_MULTIPLIER scales from."""
    gaps = []
    for i in range(lo_li + 1, hi_li + 1):
        if (lines[i].page, lines[i].col) == (lines[i - 1].page, lines[i - 1].col):
            gaps.append(lines[i].y0 - lines[i - 1].y0)
    if not gaps:
        return BOOK_WIDE_MEDIAN_LINE_GAP
    gaps.sort()
    return gaps[len(gaps) // 2]


def _block_end_index(lines: list[PositionedLine], trigger_li: int, last_item_li: int) -> int:
    """Index one past the last line still belonging to the list block's
    final item -- walks forward from last_item_li while the gap to the
    previous line stays within BLOCK_END_GAP_MULTIPLIER of the block's own
    running-median gap, stopping at the first larger gap (paragraph break
    into the main body), a page/column break (spacing isn't comparable
    across one), or MAX_TAIL_LINES, whichever comes first."""
    baseline = _running_median_gap(lines, trigger_li, last_item_li)
    threshold = baseline * BLOCK_END_GAP_MULTIPLIER
    end = last_item_li + 1
    for i in range(last_item_li + 1, min(last_item_li + 1 + MAX_TAIL_LINES, len(lines))):
        if (lines[i].page, lines[i].col) != (lines[i - 1].page, lines[i - 1].col):
            break
        if lines[i].y0 - lines[i - 1].y0 > threshold:
            break
        end = i + 1
    return end


def _derivative_keys_by_root(twot_map: dict) -> dict[str, list[str]]:
    """{root: [derivative_key, ...]} in letter-suffix order (3a, 3b, 3c...)
    -- find_list_items depends on this order to search for each key in
    strict sequence."""
    by_root: dict[str, list[str]] = {}
    for key in twot_map:
        m = re.match(r"^(\d+)([a-z]+)$", key)
        if m:
            by_root.setdefault(m.group(1), []).append(key)
    for keys in by_root.values():
        keys.sort()
    return by_root


def _is_running_header(lines: list[PositionedLine], i: int) -> bool:
    """True if lines[i] is the first line of a new page/column AND looks
    like an entry-opening (CANDIDATE_RE-shaped). TWOT prints a running head
    ('N hebrew (xlit)') at the physical top of every column as a navigation
    aid -- confirmed directly: root 4's own entry span crosses from its
    left-column discussion straight into a right-column header ('4 M:IN
    ('bh)') before the real continuation ('abab (cf. "Papa,"...)') resumes,
    and that header line was leaking into derivative 4a's captured
    main_text verbatim before this filter existed. Same failure mode
    near_page_start() guards against in segmenter.py, checked here at
    line-granularity instead of by character offset since this module
    already has each line's own page/column."""
    if i == 0:
        return False
    prev = lines[i - 1]
    cur = lines[i]
    if (cur.page, cur.col) == (prev.page, prev.col):
        return False
    return bool(CANDIDATE_RE.match(cur.text))


def find_discussion_paragraphs(lines: list[PositionedLine], line_offsets: list[int],
                                deriv_anchors: dict[str, int],
                                by_root_keys: dict[str, list[str]]) -> dict[str, dict]:
    """{derivative_key: {"main_text": str, "source_pages": [int, ...]}} --
    for each anchored root, locates its list block (find_list_items +
    _block_end_index) and attributes to each found derivative the VERBATIM
    TWOT text of its OWN list-item line PLUS anything attached beyond it, up
    to the next derivative's marker (or, for the root's last derivative, the
    block-end gap). Includes the marker line itself deliberately -- unlike
    derivatives.lemma/transliteration/gloss (from verified hebrew-lexicon
    data, reliable but necessarily terse), this is TWOT's own printed
    phrasing for that specific derivative, which can carry detail the
    verified data doesn't (e.g. a fuller gloss, an inline citation, a usage
    note) -- confirmed worth keeping even for the common "list-only, no
    attached note" case, not just the minority with a longer discussion.
    Skips any running-header line in between (see _is_running_header).
    Snippets under MIN_SNIPPET_CHARS are dropped (guards against a
    genuinely missing/misdetected marker line producing something too
    thin to be useful, though including the marker line itself means most
    located derivatives clear this easily now)."""
    result: dict[str, dict] = {}
    for root, trigger_end in deriv_anchors.items():
        keys = by_root_keys.get(root, [])
        if not keys:
            continue
        trigger_li = line_for_offset(trigger_end, line_offsets)
        items = find_list_items(lines, trigger_li, keys)
        if not items:
            continue
        item_positions = sorted(items.items(), key=lambda kv: kv[1])
        last_key, last_li = item_positions[-1]
        block_end_li = _block_end_index(lines, trigger_li, last_li)
        for idx, (key, start_li) in enumerate(item_positions):
            end_li = item_positions[idx + 1][1] if idx + 1 < len(item_positions) else block_end_li
            item_lines = [l for j, l in enumerate(lines[start_li:end_li], start=start_li)
                          if not _is_running_header(lines, j)]
            text = dehyphenate(re.sub(r"\s+", " ", " ".join(l.text for l in item_lines)).strip())
            if len(text) < MIN_SNIPPET_CHARS:
                continue
            pages = sorted({l.page for l in item_lines})
            result[key] = {"main_text": text, "source_pages": pages}
    return result


# TWOT uses two distinct, semantically different headings before a root's
# numbered sub-entry list (see segmenter.py's DERIV_KEYWORD_RE docstring,
# which already distinguishes them for matching purposes but discards which
# one matched): "Derivatives"/"Derivative" means the root HAS independent
# meaning of its own, and the discussion that follows the list is generally
# about the root itself, with sub-entries occasionally getting their own
# separate paragraph later (e.g. root 3 'āba "be willing", whose own
# discussion is distinct from 3a 'ebyon's). "Assumed root of the following."
# means the root has NO independent meaning -- it's a grammatical
# abstraction purely inferred from its derivatives -- so the discussion that
# follows is naturally ABOUT one of the derivatives directly (e.g. root 4,
# whose entire discussion is about 4a 'ab "father"; root 4 itself has no
# separate meaning to discuss). Surfaced per root (not persisted per
# derivative) since it describes the ROOT's own construction, not any one
# sub-entry.
ASSUMED_ROOT_TAIL_RE = re.compile(r"Assumed root of the following\.?\s*$")
DERIVATIVES_TAIL_RE = re.compile(r"Derivatives?\s*$")
HEADING_LOOKBACK = 40


def classify_heading(full_text: str, trigger_end: int) -> str:
    """'assumed-root' | 'derivatives' | 'unknown' for the list-introduction
    heading immediately preceding `trigger_end` (a find_derivative_anchors
    keyword-match end position)."""
    window = full_text[max(0, trigger_end - HEADING_LOOKBACK):trigger_end]
    if ASSUMED_ROOT_TAIL_RE.search(window):
        return "assumed-root"
    if DERIVATIVES_TAIL_RE.search(window):
        return "derivatives"
    return "unknown"


def structure_derivatives(twot_map: dict, lines: list[PositionedLine],
                           expected_page_by_root: dict[str, int] | None = None,
                           verbose: bool = True) -> tuple[dict[str, dict], dict[str, str]]:
    """Top-level entry point: ({derivative_key: {"main_text", "source_pages"}},
    {root: heading_type}) -- the first for every derivative whose own
    attached short note could be located within its root's list block, the
    second for every root whose Derivative(s) list was located at all (see
    classify_heading). Called from combine_sources.py after the OCR-based
    entry pipeline runs -- this pass is entirely independent of it (reads
    the PDF's embedded text layer directly) and never touches entries.*.
    Takes `lines` (extract_positioned_lines()'s own ~4-5 minute output)
    rather than computing it internally, since combine_sources.py also needs
    it for segment_derivative_anchored_positioned() and extract_page_headers()
    -- extracting the whole PDF's positioned text three times over would
    triple a cost that's already the single most expensive step in the
    build. `expected_page_by_root`, if given, feeds find_derivative_anchors's
    page-plausibility check (see its own docstring) -- without it, a root
    with a short/weak expected derivative sequence can have its OWN correct
    trigger occurrence stolen by an unrelated root's sequence scoring even
    higher against the same parens (confirmed on root 1 vs. root 420)."""
    deriv_seqs = load_derivative_sequences(twot_map)
    full_text, line_offsets = build_full_text(lines)
    page_offsets = build_page_offsets(lines, line_offsets)
    page_for_offset = make_page_for_offset(page_offsets)

    deriv_anchors = find_derivative_anchors(full_text, deriv_seqs, verbose, page_for_offset, expected_page_by_root)

    # Same fix as segment_derivative_anchored_positioned's own -- see its
    # docstring for the full reasoning. This function has its own
    # INDEPENDENT find_derivative_anchors call, so it needs the same
    # override applied separately (confirmed necessary directly: without
    # it here, derivatives 1a/1b stayed empty even after the entry-level
    # fix landed, since THIS function's own deriv_anchors['1'] was still
    # whatever false positive it happened to land on).
    bare_root_numbers = sorted((k for k in twot_map if re.match(r"^\d+$", k)), key=int)
    if bare_root_numbers and bare_root_numbers[0] in deriv_seqs:
        first_trigger = DERIV_KEYWORD_RE.search(full_text)
        if first_trigger:
            deriv_anchors[bare_root_numbers[0]] = first_trigger.end()

    heading_by_root = {root: classify_heading(full_text, pos) for root, pos in deriv_anchors.items()}

    by_root_keys = _derivative_keys_by_root(twot_map)

    result = find_discussion_paragraphs(lines, line_offsets, deriv_anchors, by_root_keys)
    if verbose:
        total_derivatives = sum(len(v) for v in by_root_keys.values())
        heading_tally = {}
        for h in heading_by_root.values():
            heading_tally[h] = heading_tally.get(h, 0) + 1
        print(f"list-block note linking: {len(result)}/{total_derivatives} derivatives "
              f"({len(deriv_anchors)} roots anchored, headings: {heading_tally})")
    return result, heading_by_root


# Deliberately below what DERIV_MIN_AVG_SCORE/strict_threshold() would ever
# accept globally -- the header has ALREADY confirmed the page
# independently (that's the whole point of the rescue), so a candidate here
# only needs to look PLAUSIBLE, not out-score every unrelated occurrence of
# similar text elsewhere in the whole book. Confirmed necessary directly:
# root 1's real occurrence ('eb'/'abib' -- both under 5 chars) scores only
# 0.375 against its own genuinely-matching text, because expected sequences
# that short just don't carry much discriminating power on their own, and
# some OTHER root's unrelated list coincidentally scores higher against the
# same short sequence hundreds of pages away (this is the general
# short-sequence collision problem segment_blockwalk's own docstring already
# names -- the header sidesteps it by page constraint rather than needing a
# better score to win a global contest it was never going to win cleanly).
HEADER_RESCUE_MIN_SCORE = 0.3
HEADER_RESCUE_PAGE_TOLERANCE = 1
HEADER_RESCUE_GLOSS_BONUS = 0.15


def _rescue_via_header(root: str, expected_page: int, full_text: str, page_offsets: list[tuple[int, int]],
                        page_starts: list[int], expected_xlit_root: set, expected_lemma_root: str,
                        expected_gloss_root: set) -> int | None:
    """Best CANDIDATE_RE match for `root`'s own opening within
    [expected_page - tolerance, expected_page + tolerance], scored by the
    max of xlit similarity and nearby-Hebrew similarity (either signal
    alone can be independently OCR/text-layer-damaged -- see
    hebrew_nearby_score's docstring) plus a bonus if any of the root's own
    expected gloss words appears nearby. Returns the winning absolute
    offset, or None if nothing clears HEADER_RESCUE_MIN_SCORE -- the header
    confirms the PAGE, but a candidate still has to look at least plausible
    to avoid capturing pure noise on a crowded page."""
    lo_page, hi_page = expected_page - HEADER_RESCUE_PAGE_TOLERANCE, expected_page + HEADER_RESCUE_PAGE_TOLERANCE
    starts_on_or_after_lo = [off for off, p in page_offsets if p >= lo_page]
    starts_after_hi = [off for off, p in page_offsets if p > hi_page]
    lo = min(starts_on_or_after_lo) if starts_on_or_after_lo else 0
    hi = min(starts_after_hi) if starts_after_hi else len(full_text)
    if hi <= lo:
        return None

    best_pos, best_score = None, 0.0
    for m in CANDIDATE_RE.finditer(full_text[lo:hi]):
        if m.group(1) != root:
            continue
        abs_pos = lo + m.start(1)
        if near_page_start(abs_pos, page_starts):
            continue
        cand_norm = normalize(m.group(2))
        xlit_score = max(
            (SequenceMatcher(None, cand_norm, exp).ratio() for exp in expected_xlit_root), default=0,
        ) if len(cand_norm) >= 2 else 0.0
        heb_score = hebrew_nearby_score(abs_pos, full_text, expected_lemma_root)
        nearby = normalize(full_text[abs_pos:abs_pos + 200])
        gloss_bonus = HEADER_RESCUE_GLOSS_BONUS if any(w in nearby for w in expected_gloss_root) else 0.0
        score = max(xlit_score, heb_score) + gloss_bonus
        if score > best_score:
            best_score, best_pos = score, abs_pos
    return best_pos if best_score >= HEADER_RESCUE_MIN_SCORE else None


# A genuine entry opening sits at an anomalously large vertical gap from
# the previous line (compared to ~9.4pt normal in-paragraph spacing) --
# confirmed directly against real position data for roots 8-13 (p.26-27):
# every real opening had a preceding gap of 12.0-36.3pt, while every false
# candidate (an ordinary continuation line, or a bare page-footer number
# like "7"/"8"/"9" printed at a page's bottom margin that happens to BE a
# valid root number by coincidence) had either a normal ~9.4pt gap or no
# parenthetical on the same line at all (CANDIDATE_RE alone already rejects
# the bare footer numbers; the gap check is what rejects a running-header
# lookalike like "9 ('eben)" printed at the page's outer margin, which
# CANDIDATE_RE matches fine but which sits only ~4pt below the previous
# line since it's the very FIRST thing on the page).
ENTRY_OPENING_MIN_GAP = 12.0


def find_entry_openings(lines: list[PositionedLine], main_numbers: set[str]) -> dict[str, int]:
    """{root: line_idx} for every KNOWN root number (from main_numbers)
    whose own line, in the embedded PDF text layer, both (a) starts with
    that EXACT bare number in CANDIDATE_RE's "N ... (parenthetical)" shape,
    and (b) is preceded by an anomalously large gap from the previous line
    in the same column (see ENTRY_OPENING_MIN_GAP) -- confirmed this two-
    signal combination is what actually distinguishes a genuine entry
    opening from the various false positives a bare digit match alone would
    catch (see ENTRY_OPENING_MIN_GAP's own comment). Position-based and
    fully independent of transliteration/gloss scoring, so it works even
    for a short "stub" entry (no derivatives, no distinguishing xlit text)
    that the scoring-based backward search has no other way to find at
    all -- confirmed necessary directly: entries 11/12/13 are exactly this
    shape, and entry 10's OWN scored span had been running straight through
    all three (no independent signal existed to stop it) before this.

    A line that's the FIRST on a fresh page/column has no previous line in
    that column to measure a gap against -- treated as passing the gap
    check UNLESS it also falls in the page header's own zone (y0 <
    HEADER_Y0_MAX), since a running header is exactly this shape too
    (fresh column top, CANDIDATE_RE-matching "N (xlit)" text) but printed
    in the page's outer margin specifically -- confirmed directly: root
    25's own header ("25 ciN ('dm)" at y0=41.9, column-first) would
    otherwise have been mistaken for root 25's real opening, which actually
    starts 8 lines later at y0=64.8 with its own proper large gap.

    A line containing a "See no. X" index-stub reference (see
    segmenter.py's SEE_NO_RE) is rejected outright, regardless of the other
    two signals -- confirmed necessary directly: an index-stub line's own
    leading Hebrew letter can misread as a digit in this text layer just
    like a real root's own leading digit sometimes garbles the other way
    (see _nearest_preceding_large_gap_line's docstring), and a fresh
    alphabetical block of stubs starting at a page/section boundary can
    genuinely clear the gap check too -- "1i~M ('iim6n). See no. 1161." (an
    unrelated index stub on p.69) was matched as root 1's own opening this
    way before this filter existed. A genuine entry opening is never
    immediately followed by "See no." -- that phrase is specifically the
    index-stub's own structure, pointing AWAY from itself to a different
    root, never appearing in a root's own discussion of itself."""
    result: dict[str, int] = {}
    prev: PositionedLine | None = None
    for i, line in enumerate(lines):
        text = line.text.strip()
        m = CANDIDATE_RE.match(text)
        same_col = prev is not None and (line.page, line.col) == (prev.page, prev.col)
        gap = (line.y0 - prev.y0) if same_col else None
        passes_gap = (gap is not None and gap >= ENTRY_OPENING_MIN_GAP) or (gap is None and line.y0 >= HEADER_Y0_MAX)
        if m and m.group(1) in main_numbers and passes_gap and not SEE_NO_RE.search(text):
            if m.group(1) not in result:
                result[m.group(1)] = i
        prev = line
    return result


# How far back (in lines) to look for a large-gap fallback boundary when no
# CANDIDATE_RE-shaped backward-search candidate was found at all.
NEAREST_GAP_LOOKBACK = 60


def _nearest_preceding_large_gap_line(lines: list[PositionedLine], from_li: int) -> int | None:
    """Line index of the CLOSEST line AT OR before `from_li` (within
    NEAREST_GAP_LOOKBACK lines) that has a large gap from its own previous
    line -- the same "new entry/paragraph" signal find_entry_openings()
    uses, but WITHOUT requiring a CANDIDATE_RE match. A fallback for a root
    whose own leading digit isn't cleanly readable at all in this text
    layer -- confirmed necessary directly: root 1's own opening line, "1
    [Hebrew] ('bb). Assumed root of the following.", extracts as literally
    '::H' with no recognizable digit anywhere in it (a source-data
    limitation specific to this one glyph sequence, not a bug in any
    matching logic -- every OTHER root's leading digit reads cleanly). Its
    line still clears ENTRY_OPENING_MIN_GAP from the index-stub line before
    it (12.7pt gap, confirmed directly), so this still finds the right
    position even though find_entry_openings() itself can't (that function
    requires the CANDIDATE_RE match this line doesn't have).

    Checks `from_li` ITSELF first, not just lines strictly before it --
    confirmed necessary directly: for an "Assumed root of the following"
    entry this short, the root's own opening and the trigger phrase sit on
    the SAME merged line (root 1's whole "1 [Hebrew] ('bb). Assumed root of
    the following." is one PositionedLine), so `from_li` (computed from the
    trigger's own offset) already points at the line with the gap that
    matters -- searching only from `from_li - 1` backward skipped checking
    it entirely and fell through to an unrelated earlier line instead
    (confirmed: landed on a stray "XVII" bibliography-citation fragment)."""
    for i in range(from_li, max(-1, from_li - NEAREST_GAP_LOOKBACK), -1):
        line = lines[i]
        if i == 0:
            continue
        prev = lines[i - 1]
        if (line.page, line.col) != (prev.page, prev.col):
            continue
        if line.y0 - prev.y0 >= ENTRY_OPENING_MIN_GAP:
            return i
    return None


def segment_derivative_anchored_positioned(twot_map: dict, main_numbers: list, expected_xlit: dict,
                                            expected_gloss: dict, lines: list[PositionedLine],
                                            expected_page_by_root: dict[str, int] | None = None,
                                            verbose: bool = True) -> dict:
    """Entry-level counterpart to segmenter.py's segment_derivative_anchored()
    -- same approach (anchor on the Derivative(s) list, search backward for
    the root's own opening candidate), same shared matching functions, but
    sourced from the PDF's own embedded text layer instead of Tesseract OCR.
    Confirmed directly to resolve two failures Tesseract couldn't: root 3's
    real opening drops its leading "3" in every OCR source (this layer has
    it intact, since it was never run through Tesseract), and root 2's own
    Derivative-list text is genuinely reading-order-corrupted in the OCR
    (whole fragments printed out of sequence) in a way this layer isn't.
    Takes `lines` rather than calling extract_positioned_lines() itself --
    see structure_derivatives()'s docstring for why.

    Three mechanisms, tried in order of decreasing structural reliability;
    each root is resolved by the first one that finds it, and later ones
    only run for roots still unresolved. FIRST, find_entry_openings() --
    position-based (a large vertical gap + a CANDIDATE_RE-shaped line at
    the column's own left-flush margin), fully independent of
    transliteration/gloss scoring, so it works even for a short "stub" root
    with 0-1 derivatives and no distinguishing xlit text at all. Confirmed
    directly this is what a scoring-only approach structurally can't do:
    entries 11/12/13 (no derivatives, no contributor of their own) have no
    other signal, and entry 10's OWN scored span had been running straight
    through all three with nothing to stop it. SECOND, the "Derivatives"-
    anchored backward search (only applies to roots with >=2 derivatives).
    THIRD, if `expected_page_by_root` is given (page-header readings, see
    combine_sources.py): find_derivative_anchors's own page-plausibility
    check feeds into the second mechanism (a root with a short/weak expected
    sequence can have its OWN correct trigger occurrence stolen by an
    unrelated root's sequence scoring even higher against the same parens --
    confirmed: root 420 vs. root 1), and a rescue pass runs after it for any
    root whose position (if any) still lands on a different page than the
    header confirms, re-searching within that page using ALL available
    verified-data signals together (xlit, Hebrew lemma, gloss words) rather
    than requiring a Derivative-list match at all -- see
    _rescue_via_header()."""
    deriv_seqs = load_derivative_sequences(twot_map)
    expected_lemma = load_expected_lemma(twot_map)

    full_text, line_offsets = build_full_text(lines)
    page_offsets = build_page_offsets(lines, line_offsets)
    page_for_offset = make_page_for_offset(page_offsets)
    page_starts = make_page_start_offsets(page_offsets)

    found: dict[str, int] = {}
    boundary_text: dict[str, str] = {}
    entry_openings = find_entry_openings(lines, set(main_numbers))
    for root, line_idx in entry_openings.items():
        start = line_offsets[line_idx]
        found[root] = start
        boundary_text[root] = full_text[start:start + 80].replace("\n", " ")
    if verbose:
        print(f"position-based entry openings: {len(found)}/{len(main_numbers)} roots "
              f"(large-gap + left-flush digit match, independent of derivative-list scoring)")

    deriv_anchors = find_derivative_anchors(full_text, deriv_seqs, verbose, page_for_offset, expected_page_by_root)

    # The very FIRST "Derivatives"/"Assumed root of the following"
    # occurrence in the whole book structurally MUST belong to the first
    # root (main_numbers[0]) -- TWOT's entries are strictly sequential, so
    # nothing else can precede it. Overridden directly rather than trusting
    # find_derivative_anchors's own scoring for this one root: confirmed
    # repeatedly that root 1's own expected sequence is too short (both
    # items under 5 chars) to reliably win the GLOBAL scoring contest --
    # it's lost to different unrelated, coincidentally higher-scoring
    # occurrences elsewhere in the book across multiple rebuilds (root 420
    # at one point, an unrelated index-stub-heavy page at another). No
    # score-based fix (page-plausibility, gap-based fallback, etc.) can
    # rescue a signal this weak, but the POSITION is structurally
    # guaranteed regardless of what it scores.
    #
    # find_entry_openings() can ALSO be fooled the same way, for the same
    # underlying reason (root 1's own signal is weak, and this text layer
    # has a handful of index-stub lines whose leading Hebrew letter misreads
    # as a digit) -- confirmed directly across several rebuilds, each fixing
    # one specific false-positive line only for a DIFFERENT one to surface
    # elsewhere in the ~1100-page book (p.69, then p.400, chasing individual
    # garbling variants is a losing game). Since this override is
    # deterministic and already verified correct, it takes priority: pop
    # root 1 out of `found` first if entry_openings put something (wrong)
    # there, so the backward-search/gap-fallback logic below -- which
    # starts from THIS verified-correct trigger position -- gets to run
    # instead of being skipped as "already found".
    if main_numbers and main_numbers[0] in deriv_seqs:
        first_trigger = DERIV_KEYWORD_RE.search(full_text)
        if first_trigger:
            deriv_anchors[main_numbers[0]] = first_trigger.end()
            found.pop(main_numbers[0], None)
            boundary_text.pop(main_numbers[0], None)

    for root, deriv_pos in deriv_anchors.items():
        if root not in expected_xlit or root in found:
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
        if best_pos is not None:
            start = best_pos
        else:
            # no CANDIDATE_RE-shaped candidate at all in the backward window --
            # fall back to the nearest preceding large-gap line (see
            # _nearest_preceding_large_gap_line's own docstring for why a
            # blind character-offset guess isn't used here anymore)
            gap_li = _nearest_preceding_large_gap_line(lines, line_for_offset(deriv_pos, line_offsets))
            start = line_offsets[gap_li] if gap_li is not None else max(0, deriv_pos - 200)
        found[root] = start
        boundary_text[root] = full_text[start:start + 80].replace("\n", " ")

    if verbose:
        backward_found = {r: p for r, p in found.items() if r in deriv_anchors}
        backward_hits = sum(1 for r, p in backward_found.items() if p != max(0, deriv_anchors[r] - 200))
        print(f"pdftext-derivative-anchored: {len(found)} roots total "
              f"({len(entry_openings)} via position, {len(backward_found)} via derivative-list backward search: "
              f"{backward_hits} confirmed own-opening, {len(backward_found) - backward_hits} fallback offset)")

    if expected_page_by_root:
        rescued = 0
        for root in main_numbers:
            if root not in expected_xlit or root not in expected_page_by_root or root in entry_openings:
                continue  # entry_openings is the most structurally reliable signal -- never overwritten
            expected_page = expected_page_by_root[root]
            if root in found and page_for_offset(found[root]) == expected_page:
                continue
            rescue_pos = _rescue_via_header(
                root, expected_page, full_text, page_offsets, page_starts,
                expected_xlit[root], expected_lemma.get(root, ""), expected_gloss.get(root, set()),
            )
            if rescue_pos is not None:
                found[root] = rescue_pos
                boundary_text[root] = full_text[rescue_pos:rescue_pos + 80].replace("\n", " ")
                rescued += 1
        if verbose:
            print(f"header-guided rescue: fixed {rescued} roots whose page was missing or "
                  f"disagreed with a verified header")

    result = build_boundary_result(full_text, page_for_offset, main_numbers, expected_gloss, found)
    for root in result:
        result[root]["boundary_text"] = boundary_text.get(root)
    return result
