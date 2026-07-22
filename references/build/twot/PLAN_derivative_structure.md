# Plan: structured per-derivative discussion text (position-aware extraction)

Status: **not started** — scoped in a planning conversation, deferred to a future session.
Picks up after the entry-level segmentation work in `segmenter.py`/`combine_sources.py`
(derivative-list anchoring, page-monotonicity, duplicate/swallowed-neighbor checks,
bidi-mark stripping — all already implemented and working as of this plan's writing).

## Motivation

The `derivatives` table currently carries `lemma`/`transliteration`/`gloss` per
sub-entry (e.g. `4a`, `4b`), 100% populated from `twot_strongs_map.json` — never
OCR-dependent, always reliable. What it does NOT carry is each derivative's own
**dedicated discussion paragraph** — TWOT often gives a distinct sub-entry
(like `4a`) a full paragraph of its own later in the entry (e.g. "*'ebyon.* One
in the state of wanting, a needy or poor person..."), separate from the root's
general discussion and separate from the one-line list-gloss. That paragraph
currently just sits undifferentiated inside the parent entry's `main_text`.

The user's idea: TWOT's own typography marks the derivatives LIST block with a
visually distinct indentation level, different from both the trigger phrase
("Derivatives" / "Assumed root of the following.") and normal body-paragraph
text. If that's a reliable signal, we can parse the list *structurally*
instead of just pattern-matching plain text, and then link each list item to
its own discussion paragraph later in the entry.

## Established parsing findings (from the entry-segmentation session)

Everything below was learned empirically while building `segmenter.py`/
`combine_sources.py` and is directly relevant to this feature too — a fresh
session shouldn't have to rediscover any of it.

### Segmenting on author (contributor initials)

- `AUTHORITATIVE_INITIALS` (in `segmenter.py`) is a hardcoded 46-name list
  sourced directly from the book's own printed Contributors section — the
  only reliable ground truth for "this is a real contributor signature."
- A frequency-based fallback was tried (any 2-3 letter dotted-initials
  pattern appearing >=15 times anywhere) and **removed**: it added exactly
  two false positives, `EJ` and `EA`, which turned out to be repeated
  bibliography citations of a prolific cited author ("E. J. Young"), not
  contributor signatures. Bibliography citations recur often enough across
  the book to cross any frequency bar low enough to also catch a genuine
  contributor. Lesson: don't trust frequency alone to disambiguate
  signature-shaped text from citation-shaped text.
- A contributor signature always appears on its own line, right-aligned, at
  the very end of an entry — confirmed by direct PDF visual inspection (page
  25). Our own whitespace-flattening (`\s+` → ` ` during extraction) erases
  that visual isolation, which is why a signature can look "mid-paragraph"
  in already-extracted text — that's a display artifact of extraction, not a
  real formatting anomaly in the source.
- Bare confirmed-initials occurrences (not gated behind proximity to
  "Bibliography:") are far more numerous (1,270 in the colsplit OCR text)
  than the "near a Bibliography marker" high-precision subset (~450-470) —
  the bare occurrences alone are still a strong, usable end-of-entry signal.
- Using initials as a hard BLOCK BOUNDARY (an entry's search may never cross
  past the next unclaimed initials checkpoint) was tried as a primary
  strategy on its own and initially failed badly (545/3057) from having no
  ceiling on how far a search could drift; fixed with a max-widen cap. Even
  fixed, it underperforms xlit-anchoring + gap-recovery as a *primary*
  method — it's most valuable as an *additional* combine-source
  (`colsplit-blockwalk`), not the main strategy.
- **The most important fix**: `truncate_at_first_signoff()`. An entry's
  captured span can run past its own true end into subsequent entries whose
  own boundary was never independently found (a "hole" in the sequence,
  since every strategy here finds an entry's END by locating wherever the
  NEXT successfully-found entry begins). The fix is to truncate at the FIRST
  confirmed-initials occurrence found ANYWHERE in the captured text — not
  gated behind requiring a second "Bibliography:" marker, because some
  swallowed entries have no bibliography or signature of their own at all
  (confirmed on entry 5: a single sentence, nothing else). This is a no-op
  for a normally-bounded entry (its own signature is the first and only one
  found) and correctly trims an over-captured span otherwise.
- A related but distinct failure mode: if the swallowed content itself
  contains a LONG intervening entry with its own valid signature before the
  true stopping point, `truncate_at_first_signoff` stops too late — at that
  intervening entry's signature, not at the real boundary. Caught instead by
  `flag_swallowed_neighbors()` in `combine_sources.py`: if entry N's text
  literally contains another independently-found entry M's own opening text
  as a substring, N swallowed M — truncate N right before that point. This
  turned out to be extremely widespread (500+ entries affected in one run).

### Structure of an entry start

- The canonical opening pattern is `[number] [Hebrew word] ([transliteration])
  [definition...]`, matched by `CANDIDATE_RE = r"(?:^|\s)(\d{1,4})\s*\S{0,20}?\s*\(([^)]{1,20})\)"`.
  But the literal order in OCR'd text is unreliable — bidi (right-to-left/
  left-to-right) rendering can put the Hebrew word before OR after the
  `(xlit)` parenthetical, and the leading number can be dropped by OCR
  entirely (confirmed on entry 5: its "5" was never tokenized at all, not
  misread as a wrong character).
- Two distinct conventions introduce the material after an entry's own
  opening line:
  - **"Derivatives" / "Derivative"** (both singular and plural occur) — used
    when the root has independent meaning of its own; printed as its own
    heading before the numbered sub-entry list.
  - **"Assumed root of the following."** — used when the root has NO
    independent meaning (purely a grammatical construct inferred from its
    derivatives); skips straight from this phrase to the numbered list, no
    separate "Derivatives" heading at all. 455 occurrences in the book — too
    common to treat as an edge case.
- Derivative list items print in strict alphabetical-suffix order (3a, 3b,
  3c, 3d...), and that order is 100% reliable — it comes from
  `twot_strongs_map.json` (itself derived from Strong's/BDB data), never
  from OCR — even when the item's own printed ref-number+Hebrew is garbled
  beyond recognition. The English transliteration in parens after each list
  item OCRs far more reliably than the Hebrew/number preceding it, so
  matching a list item by transliteration-in-sequence-order is a much
  stronger anchor than trying to read its ref number.
- The whole numbered list, when present, is a far more reliable identifying
  signal for "which root is this" than the root's own single opening
  number+xlit match — matching 2+ words in the correct sequence essentially
  can't happen by coincidence, whereas isolated short transliterations (2-3
  letters) frequently do coincidentally match unrelated words (confirmed:
  root 1's xlit "bb" scored 0.667 similarity against "abbir", an unrelated
  word from a different entry entirely).
- **Running headers**: the book prints the entry currently being discussed at
  the physical TOP of every page (e.g. "3 אבה (aba)") as a navigation aid.
  Tesseract has no concept of header-vs-body regions and merges this
  straight into the body text stream, where it can look exactly like a real
  entry start (identical N+Hebrew+(xlit) shape) and score just as well —
  even a perfect 1.0 — against the real transliteration, since it prints the
  identical text. What follows a header in the OCR stream is typically the
  *continuation of an unfinished sentence from the previous page*, not new
  content. The reliable detection signal is positional, not content-based:
  a header sits within the first ~60 characters of its own page's OCR text
  chunk (`near_page_start()`) — real entries essentially never start there.
- **Separate structural layer — the cross-reference index**: short stub
  lines like "אבוי ('ābôy). See no. 3d." are interleaved through the whole
  dictionary body, pointing an alphabetically-placed word spelling to
  wherever it's actually discussed. 1,507 occurrences total. These are NOT
  derivatives or content of whichever entry they happen to land inside
  during segmentation — a different structural layer entirely — and are
  stripped via `strip_index_stubs()` (matches "See no."/"See nos." plus a
  trailing number-letter list).
- **Bidi control characters**: U+200E (LRM) and U+200F (RLM) are inserted by
  Tesseract's heb+eng model at every Hebrew/English script boundary. They
  carry zero informational content but ARE non-whitespace characters — they
  were silently breaking `CANDIDATE_RE`'s number-to-parenthesis proximity
  match throughout the entire document (the lazy `\S{0,20}?` middle group
  would get consumed by these invisible marks). Stripping them at load time
  (`load_pages()`) was the single biggest accuracy lever pulled all
  session — verified entries jumped from 2,252 to 2,546 in one fix. If phase
  1 of this plan reads the embedded text layer directly, check whether it
  has the same characters before assuming this fix is still needed there.
- The Hebrew lemma itself (not just the transliteration) is a valid,
  independent confirmation signal — Hebrew-glyph OCR quality and
  English-transliteration OCR quality are different recognition problems on
  the same source image, so one can be garbled while the other is clean.
  `normalize_hebrew()` (keeps only `א`-`ת`, drops niqqud/
  cantillation) + `hebrew_nearby_score()` check a window around a candidate
  position for the expected lemma as a supplement to xlit-only matching.

### Page-number logic for entries

- TWOT entries appear in strict, monotonic page order through the book —
  entry N can never legitimately be sourced from an earlier page than any
  entry preceding it in the numbering. A free, powerful, purely structural
  check, independent of OCR quality.
- Implemented as `enforce_page_monotonicity()`: computes the longest
  non-decreasing subsequence of page numbers across all found entries
  (O(n log n), patience-sorting/bisect) and demotes anything OUTSIDE that
  subsequence back to not-found. This correctly identifies the true outlier
  regardless of which direction it jumped (confirmed: entry 1's bad match
  jumped forward to pages 26-27 while entries 3/4/5... stayed consistent —
  removing entry 1, not entry 3, is what restores the longer consistent run).
- This check **cannot** catch same-page duplicate-content claims (two
  entries both correctly page-attributed but claiming overlapping/identical
  text) — that needed a separate check, `flag_duplicate_starts()` (same
  normalized opening claimed twice) plus `flag_swallowed_neighbors()`
  (one entry's tail contains another's start).
- A demoted entry leaves a hole in the sequence, and whichever entry
  immediately precedes it may have silently over-captured into that hole.
  `flag_neighbors_of_demoted()` downgrades verified→suspect for the entry
  immediately before any demotion (from either the page-order check or the
  duplicate-text check), since its text is now known-uncertain even though
  its own boundary was never independently flagged.
- Page numbers are stored 0-indexed internally (matching pymupdf/PDF page
  indexing) but shown 1-indexed in the human-facing export (`p.{p+1}`).
- `source_pages` on an entry is the set of PDF pages touched by its captured
  character-offset span (start page and end page), which can be 1 or 2 pages
  for entries crossing a page boundary.

## Key discovery: the PDF has an embedded text layer with position data

`/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf`
is a scanned book, but **it already has an embedded text layer** — confirmed via:

```python
import pymupdf
doc = pymupdf.open(PDF_PATH)
page = doc[25]  # 0-indexed
text = page.get_text("text")       # plain text, has content
d = page.get_text("dict")          # structured: blocks -> lines -> spans, each with bbox
```

This is a **different OCR pass** than our own Tesseract pipeline (`ocr_twot_columns.py`),
with different error patterns. Confirmed directly: it correctly read entry 5's
leading digit ("5 *'!!;~ ( 'abak)"), which our Tesseract pipeline dropped
entirely (see `segmenter.py`'s `hebrew_nearby_score`/pass-4 docstrings for that
saga — the "5" was never tokenized by Tesseract at all, not misread).

Two follow-on implications, not yet acted on:
1. This embedded layer could be a **6th combine-source** for entry-level
   `main_text` too (alongside colsplit/400dpi/merged600/colsplit-blockwalk/
   colsplit-derivatives in `combine_sources.py`), independent of this
   derivative-structuring feature. Worth evaluating separately — different
   scope, same discovery.
2. It gives us **position data** (`bbox` on every line/span), which plain
   Tesseract text output does not have at all. This is what makes
   indentation-based parsing possible.

## Confirmed structural facts (empirically verified, one sample page — page 24, 0-indexed)

```
x0=115.2  'Assumed root of the following. '
x0=55.7   "4a t:tc ('ab) father, forefather. "
x0=55.7   '4b '
```

- The list-introduction trigger line ("Derivatives" / "Assumed root of the
  following.") sits at its own x0 (~115 on this page, left column).
- Derivative list items sit at a **distinctly smaller x0** (~55.7) than both
  the trigger line and normal body-paragraph text (~48 was the body-paragraph
  indent seen on the same page, so list items are actually LESS indented than
  body text — a hanging-indent convention, number in the margin).
- Two-column layout is visible in the position data too: left column x0 in
  the ~55-115 range, right column x0 in the ~313-322 range on the pages
  sampled. This roughly matches (but is a different measurement space than)
  the pixel-based column-gutter detection already used for the Tesseract
  pipeline in `column_detect.py`.
- Hebrew glyphs still garble in this embedded layer too ("t:tc" for a Hebrew
  word) — this is NOT a magic clean source, just a differently-flawed one.

**Not yet validated**: whether x0≈55.7 for list items and the ~48/~115
reference points are STABLE across the whole book, or vary by page/section
(front matter vs. body, single- vs. two-column stretches, font-size changes
for longer entries, etc.). Only one page was sampled before deferring. This
needs empirical validation across a real sample (10-20 pages spanning
different sections) before being trusted as a hard parsing rule — same
iterative-empirical approach used for every other heuristic in this project
(see `segmenter.py` docstrings throughout for the pattern: hypothesize,
measure against real pages, adjust).

## Proposed phases

**Phase 1 — position-aware page extraction.** New extraction pass using
`page.get_text("dict")` directly (no OCR, no Tesseract) across the dictionary
body's page range. Output: per-line `(text, x0, y0, page_num)`, analogous to
`load_pages()` in `segmenter.py` but carrying position instead of just a flat
offset. Likely fast (parsing, not image recognition).

**Phase 2 — derivative-list block detection.** For each root with >=1
derivative (reuse `load_derivative_sequences()` from `segmenter.py` to know
which roots qualify), find the "Derivatives"/"Assumed root of the following"
trigger line (reuse `DERIV_KEYWORD_RE`), then classify subsequent lines by
x0: consistent list-indent x0 = list item, reversion to body-paragraph x0 (or
a blank-line/paragraph-break signal) = end of list.

**Phase 3 — per-item structured extraction.** For each detected list-block
line: extract the parenthetical transliteration, match against the
derivative's *known* xlit from `twot_map` in list order (reuse the same
SequenceMatcher-based approach `find_derivative_anchors()` already uses for
the whole-sequence match) — position-in-list is authoritative, so a garbled
or missing ref-number digit (like entry 5's) doesn't block correct
attribution.

**Phase 4 — link to discussion paragraphs.** Within the entry's own
already-correctly-bounded `main_text` (the entry-level segmentation pipeline
already handles this — see the whole chain of fixes in `segmenter.py`/
`combine_sources.py`: derivative-anchoring, page-monotonicity,
`flag_duplicate_starts`, `flag_swallowed_neighbors`, `truncate_at_first_signoff`),
search for paragraph-start patterns (short italicized transliteration + period
at a paragraph boundary — needs its own position-based paragraph-boundary
detection, likely using y-coordinate jumps combined with x0 reverting to the
paragraph-start indent). Match each candidate paragraph to a derivative by
xlit similarity, same technique as elsewhere in this project.

## Schema change needed

Add to `derivatives` in `schema.sql`:
```sql
main_text TEXT,        -- the derivative's own dedicated discussion paragraph,
                         -- OCR-derived, NULLABLE -- most derivatives are
                         -- list-only and never get their own paragraph, so
                         -- null here is a correct, expected outcome, not a gap
source_pages TEXT       -- optional, mirrors entries.source_pages, for provenance
```

## Known risks / open questions for the next session

1. **Partial coverage by design.** Not every derivative gets its own
   discussion paragraph in the book — many are list-only (just the one-line
   gloss). `main_text` will be null often; that's correct.
2. **Indent-value stability unvalidated.** Only one page sampled. Must check
   a real spread of pages before trusting x0 thresholds as a hard rule.
3. **Column mapping between the embedded-text position space and the
   existing Tesseract-pixel column-detection space** (`column_detect.py`) is
   not yet reconciled — they're different coordinate systems (PDF points vs.
   rendered pixels at a chosen DPI) and don't need to be reconciled unless
   this phase-1 extraction is later combined with the Tesseract-based
   `colsplit` pipeline directly.
4. **Whether to also use the embedded layer as a 6th combine-source for
   entry-level `main_text`** (separate question from derivative structuring,
   noted above) is undecided — would need its own quality evaluation against
   the existing 5 sources before wiring into `combine_sources.py`'s
   `SOURCE_PRIORITY`.
5. **Paragraph-boundary detection for phase 4** is the least-scoped part of
   this plan — "italicized transliteration + period at a paragraph start" is
   a hypothesis, not yet checked against real position/font data (pymupdf's
   `dict` mode also exposes font/flags per span, e.g. italic, which hasn't
   been explored yet but is very likely the right signal to check first).

## Relevant existing code (for orientation in a fresh session)

All build/pipeline code lives under, and this plan file itself sits in:
```
/Users/dave/code/gh_ding0t/bible_studies/references/build/twot/
```
That directory is git-tracked (it's code, not copyrighted book content).
Everything below is a file in that directory unless a full path is given.

- **`segmenter.py`** (`.../twot/segmenter.py`) — all segmentation logic:
  `load_derivative_sequences()`, `find_derivative_anchors()`,
  `segment_derivative_anchored()`, `truncate_at_first_signoff()`,
  `strip_index_stubs()`, bidi-mark stripping in `load_pages()`. This whole
  file's docstrings are written narratively with the empirical reasoning
  behind each decision — worth reading in full before touching it.
- **`combine_sources.py`** (`.../twot/combine_sources.py`) — multi-source
  combination, `enforce_page_monotonicity()`, `flag_duplicate_starts()`,
  `flag_swallowed_neighbors()`, `flag_neighbors_of_demoted()` — the
  safety-net passes that catch segmentation errors after the fact. Run via
  `uv run python -m twot.combine_sources` from the `references/build/`
  directory (must use `-m twot.<module>`, not a direct path — the package's
  own absolute imports break otherwise).
- **`schema.sql`** (`.../twot/schema.sql`) — `lexicon-restricted.db` schema
  (entries + derivatives + works).
- **`export_for_review.py`** (`.../twot/export_for_review.py`) — generates
  the human-review Markdown at
  `/Volumes/media/bible/reference/Theological Wordbook of the Old Testament -- extracted text (for review).md`
  (never committed — copyrighted, quotation-only tier, lives outside the
  repo). Run via `uv run python -m twot.export_for_review`.
- **`build_twot_map.py`** (`.../twot/build_twot_map.py`) — builds
  `twot_strongs_map.json` (`.../twot/twot_strongs_map.json`) from
  `hebrew-lexicon/LexicalIndex.xml` — the authoritative, non-OCR source for
  every root/derivative's key, lemma, transliteration, Strong's/BDB ids, and
  short gloss. 6,925 entries.
- **`column_detect.py`** / **`ocr_twot_columns.py`** (`.../twot/`) — the
  existing Tesseract-based, pixel-space column-aware OCR pipeline (produces
  the `colsplit` source). Output OCR text lives at
  `/Volumes/media/bible/local-only-build/twot-ocr-pages-colsplit/page-NNNN.txt`
  (also `twot-ocr-pages-400dpi/` and `twot-ocr-pages-merged/` for the other
  two Tesseract sources combine_sources.py reads).
- **Source PDF**: `/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf`
  (Moody Press, 1980, copyright — never committed, this is what Phase 1's
  `page.get_text("dict")` would read directly).
- **Database**: `/Volumes/media/bible/local-only-build/lexicon-restricted.db`
  — also never committed, rebuilt from scratch each time
  `combine_sources.py` runs (`DB_PATH.unlink()` at the top of `main()`).

## Current state as of this plan (context, not part of the plan itself)

Last full rebuild: 2,541 verified / 222 suspect / 260 not-found / 34 unverified
out of 3,057 main roots. Multiple structural bugs found and fixed this
session (off-by-one in gap-recovery pass 3, page-header false positives,
frequency-based false-positive contributor initials, bidi-mark interference
with candidate regex matching, entry-swallowing-neighbor cases) — see git
history / session transcript for the full list if deeper context is needed.


