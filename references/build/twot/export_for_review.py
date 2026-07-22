"""Export lexicon-restricted.db's TWOT entries as a single readable Markdown
file, next to the source PDF, for manual review. Never committed -- this is
just as copyrighted (Moody Press, 1980) as the OCR text it's built from, and
lives in the same local-only location as the source itself.

For 'not-found' entries, page numbers alone ("page unknown") aren't enough to
actually go find them -- so instead: consecutive not-found roots are grouped
into runs, each run's page range is estimated from its nearest CONFIRMED
neighbors on either side (we don't know exactly where the missing entries
start/end, but we know they're somewhere between two known-good anchors),
and the raw OCR text for that page range is included once per run -- a
starting point for manual transcription, not just a page pointer.

Segment boundaries are surfaced two ways:
- Found entries show which extraction source/strategy won (colsplit vs
  400dpi vs merged600 vs colsplit-blockwalk) and the main_text/bibliography/
  contributor_initials split explicitly, since the split itself can be wrong
  even when the overall entry boundary is right.
- Not-found runs' raw OCR dumps get inline annotations at every position the
  segmenter considered (and rejected or left unscored) as a candidate start
  for one of the expected entries in that run, or as a contributor-initials
  end marker -- so a human reviewer can see where the algorithm *almost*
  broke, not just a blob of undifferentiated text.
"""
import json
import re
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

from twot.segmenter import (
    CANDIDATE_RE, INITIALS_CANDIDATE_RE, load_expectations, normalize,
    find_confirmed_initials,
)

BUILD_DIR = Path(__file__).resolve().parent
DB_PATH = Path("/Volumes/media/bible/local-only-build/lexicon-restricted.db")
GAP_TEXT_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-colsplit")
TWOT_MAP_PATH = BUILD_DIR / "twot_strongs_map.json"
OUT_PATH = Path("/Volumes/media/bible/reference/Theological Wordbook of the Old Testament -- extracted text (for review).md")
SRC_PDF_NAME = "Theological Wordbook of the Old Testament.pdf"

CONFIDENCE_LABEL = {
    "verified": "VERIFIED",
    "suspect": "SUSPECT -- please check against the page(s) listed",
    "unverified": "UNVERIFIED -- no gloss available to cross-check against",
}

SOURCE_LABEL = {
    "colsplit": "colsplit (column-aware OCR, transliteration-anchored)",
    "400dpi": "400dpi (whole-page OCR, transliteration-anchored)",
    "merged600": "merged600 (targeted 600dpi override)",
    "colsplit-blockwalk": "colsplit-blockwalk (NEW: initials-boundary segmentation -- "
                           "no transliteration floor within a signed block; spot-check recommended)",
}


def load_page_text() -> tuple[str, list[tuple[int, int]]]:
    """Same page-concatenation logic as segmenter.py, exposed here so gap
    text can be extracted for the not-found runs."""
    page_files = sorted(GAP_TEXT_DIR.glob("page-*.txt"))
    parts, offsets = [], []
    offset = 0
    for pf in page_files:
        page_num = int(pf.stem.split("-")[1])
        text = pf.read_text(encoding="utf-8")
        offsets.append((offset, page_num))
        parts.append(text)
        offset += len(text) + 1
    return "\n".join(parts), offsets


def raw_span_for_pages(offsets: list[tuple[int, int]], full_text_len: int,
                        page_lo: int, page_hi: int) -> tuple[int, int]:
    starts = {pnum: off for off, pnum in offsets}
    sorted_pages = sorted(starts)
    chunk_starts = [starts[p] for p in sorted_pages if page_lo <= p <= page_hi]
    if not chunk_starts:
        return 0, 0
    lo = min(chunk_starts)
    later = [off for off, pnum in offsets if pnum > page_hi]
    hi = min(later) if later else full_text_len
    return lo, hi


def annotate_gap_text(full_text: str, lo: int, hi: int, expected_xlit: dict,
                       confirmed_initials: set) -> str:
    """Inject inline markers at every candidate-start and initials-end
    position found within [lo, hi), so a not-found run's raw dump shows where
    the segmenter looked (and what it found/rejected), not just plain text."""
    chunk = full_text[lo:hi]
    markers: list[tuple[int, str]] = []

    for m in CANDIDATE_RE.finditer(chunk):
        num, paren = m.group(1), m.group(2)
        if num not in expected_xlit:
            continue
        cand_norm = normalize(paren)
        if len(cand_norm) < 2:
            continue
        score = max(
            (SequenceMatcher(None, cand_norm, exp).ratio() for exp in expected_xlit[num]), default=0,
        )
        markers.append((m.start(1), f"[candidate: entry {num} ({paren!r}) translit-score={score:.2f}]"))

    for m in INITIALS_CANDIDATE_RE.finditer(chunk):
        norm = re.sub(r"[\s.]", "", m.group(1))
        if norm in confirmed_initials:
            markers.append((m.end(), f"[contributor sign-off: {norm}]"))

    markers.sort(key=lambda t: t[0], reverse=True)
    for pos, label in markers:
        chunk = chunk[:pos] + f"\n\n>>> {label} <<<\n\n" + chunk[pos:]
    return chunk


def main() -> None:
    assert "bible_studies" not in str(OUT_PATH), "must stay outside the git repo"

    twot_map: dict = json.loads(TWOT_MAP_PATH.read_text())
    _, _, expected_xlit, _ = load_expectations(twot_map)

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key, lemma, transliteration, strongs_ids, bdb_id, short_gloss, "
        "main_text, bibliography, contributor_initials, source_pages, "
        "extraction_source, boundary_text, text_confidence, derivative_heading "
        "FROM entries ORDER BY CAST(key AS INTEGER)"
    ).fetchall()
    deriv_rows = conn.execute(
        "SELECT parent_key, key, lemma, transliteration, gloss, main_text, source_pages "
        "FROM derivatives ORDER BY parent_key, key"
    ).fetchall()
    conn.close()

    by_key = {r[0]: r for r in rows}
    ordered_keys = [r[0] for r in rows]  # already sorted by numeric key

    derivs_by_parent: dict[str, list] = {}
    for d in deriv_rows:
        derivs_by_parent.setdefault(d[0], []).append(d)

    tally = {}
    for row in rows:
        tally[row[12]] = tally.get(row[12], 0) + 1

    print("loading column-aware OCR text for gap annotation...")
    full_text, offsets = load_page_text()
    confirmed_initials = find_confirmed_initials(full_text, verbose=False)

    lines = [
        "# Theological Wordbook of the Old Testament -- Extracted Text (for review)",
        "",
        f"Source: `{SRC_PDF_NAME}` (Moody Press, 1980, copyright -- kept local, never committed)",
        "Extracted via OCR (Tesseract, heb+eng, column-aware left/right split at 400 DPI, "
        "combined with earlier whole-page 400/600 DPI passes, plus a newer initials-boundary "
        "segmentation pass) + automated entry segmentation. Hebrew lemma, transliteration, "
        "Strong's, and BDB numbers below are NOT from OCR -- they're sourced from the verified "
        "`hebrew-lexicon` data and are reliable regardless of the discussion text's confidence flag.",
        "",
        f"**{len(rows)} main roots total** -- "
        + ", ".join(f"{tally.get(k, 0)} {k}" for k in ["verified", "suspect", "not-found", "unverified"]),
        "",
        "Sorted by TWOT number order (matches the book itself). Each found entry shows which "
        "**extraction source** won it -- `colsplit-blockwalk` is a newly added strategy "
        "(initials mark hard block boundaries an entry can never be matched across) and is "
        "flagged for extra scrutiny since it trades a transliteration check for boundary "
        "structure. The **main text / bibliography / contributor** split is shown explicitly "
        "so you can catch a wrong internal split even when the overall entry boundary is right. "
        "**Not-found entries are grouped into runs** with an estimated page range and the raw "
        "OCR text for that range annotated with `>>> candidate <<<` and `>>> contributor "
        "sign-off <<<` markers -- every position the segmenter looked at and either accepted, "
        "scored too low, or used as an end-of-entry signal, not just a plain OCR blob.",
        "",
        "Where an entry has derivatives, its **Derivatives** list is shown BEFORE the discussion "
        "text -- matching the book's own printed order. Each derivative's lemma/transliteration/"
        "gloss is from verified data (not OCR, always reliable); a derivative's own short "
        "discussion snippet, when one was found, is a SEPARATE extraction pass from the entry "
        "text below it -- it reads the PDF's embedded text layer directly (position + font data, "
        "not Tesseract OCR), locating a `transliteration. *Italicized gloss.*` line and capping "
        "what it captures to a few sentences (most derivatives that get their own paragraph at "
        "all stop naturally within that; see `derivative_structure.py`). A derivative with no "
        "snippet shown is either genuinely list-only in the book, or its paragraph wasn't "
        "located -- the fuller discussion, if one exists, is normally still present in the "
        "entry's own text below.",
        "",
        "To correct a boundary, insert a marker on its own line where the real entry should "
        "start: `<<<N>>>` (N = the TWOT number). Reorder text first if the OCR column order is "
        "wrong.",
        "",
        "---",
        "",
    ]

    i = 0
    while i < len(ordered_keys):
        key = ordered_keys[i]
        row = by_key[key]
        confidence = row[12]

        if confidence != "not-found":
            (_, lemma, xlit, strongs_json, bdb_id, gloss, main_text, bibliography,
             contributor_initials, pages_json, extraction_source, boundary_text, _,
             derivative_heading) = row
            strongs_ids = json.loads(strongs_json) if strongs_json else []
            pages = json.loads(pages_json) if pages_json else []
            page_str = ", ".join(f"p.{p + 1}" for p in pages) if pages else "page unknown"
            strongs_str = ", ".join(strongs_ids) if strongs_ids else "--"
            source_label = SOURCE_LABEL.get(extraction_source, extraction_source or "?")

            lines.append(f"## {key}  —  {lemma or '?'}  ({xlit or '?'})")
            lines.append(
                f"**Strong's:** {strongs_str}  |  **BDB:** {bdb_id or '--'}  |  "
                f"**Gloss:** {gloss or '--'}  |  **Source:** {page_str}  |  "
                f"**Status:** {CONFIDENCE_LABEL[confidence]}"
            )
            lines.append(f"**Extraction:** {source_label}")
            if boundary_text:
                lines.append(f"**Boundary evidence:** `{boundary_text.strip()}`")
            lines.append("")

            derivs = derivs_by_parent.get(key, [])
            if derivs:
                heading_label = {
                    "assumed-root": f"**Assumed root of the following** ({len(derivs)} -- "
                                     "root has no independent meaning of its own):",
                    "derivatives": f"**Derivative{'s' if len(derivs) != 1 else ''} ({len(derivs)}):**",
                }.get(derivative_heading, f"**Derivatives ({len(derivs)}, heading not located):**")
                lines.append(heading_label)
                lines.append("")
                for d in derivs:
                    _, dkey, dlemma, dxlit, dgloss, dmain, dpages_json = d
                    dpages = json.loads(dpages_json) if dpages_json else []
                    dpage_str = ", ".join(f"p.{p + 1}" for p in dpages) if dpages else None
                    lines.append(f"- **{dkey}** — {dlemma or '?'} ({dxlit or '?'}) — {dgloss or '--'}")
                    if dmain:
                        lines.append(f"  > {dmain}" + (f"  ({dpage_str})" if dpage_str else ""))
                lines.append("")
            lines.append("**Main text:**")
            lines.append(main_text if main_text else "*(none)*")
            lines.append("")
            lines.append("**Bibliography:** " + (bibliography if bibliography else "*(none)*"))
            lines.append("**Contributor:** " + (contributor_initials if contributor_initials else "*(none -- check for a missed split)*"))
            lines.append("")
            lines.append("---")
            lines.append("")
            i += 1
            continue

        # gather the consecutive not-found run
        run = []
        while i < len(ordered_keys) and by_key[ordered_keys[i]][12] == "not-found":
            run.append(ordered_keys[i])
            i += 1

        # nearest found neighbors before/after this run, for the page estimate
        before_pages = None
        for j in range(ordered_keys.index(run[0]) - 1, -1, -1):
            r = by_key[ordered_keys[j]]
            if r[12] != "not-found" and r[9]:
                before_pages = json.loads(r[9])
                break
        after_pages = None
        for j in range(ordered_keys.index(run[-1]) + 1, len(ordered_keys)):
            r = by_key[ordered_keys[j]]
            if r[12] != "not-found" and r[9]:
                after_pages = json.loads(r[9])
                break

        page_lo = max(before_pages) if before_pages else 0
        page_hi = min(after_pages) if after_pages else page_lo + 1

        lines.append(f"## {run[0]}–{run[-1]}  —  {len(run)} entries not automatically found")
        lines.append(f"**Estimated location:** pages {page_lo + 1}–{page_hi + 1} "
                      f"(between confirmed neighbors before/after this run)")
        lines.append("")
        lines.append("Expected entries in this range:")
        for k in run:
            r = by_key[k]
            strongs_ids = json.loads(r[3]) if r[3] else []
            lines.append(f"- **{k}** — {r[1] or '?'} ({r[2] or '?'}) — "
                          f"Strong's: {', '.join(strongs_ids) or '--'} — gloss: {r[5] or '--'}")
        lines.append("")
        lines.append("Raw OCR text for pages "
                      f"{page_lo + 1}–{page_hi + 1}, annotated with every candidate/sign-off "
                      "position the segmenter considered (uncorrected, unsegmented otherwise):")
        lines.append("")
        lines.append("```")
        lo, hi = raw_span_for_pages(offsets, len(full_text), page_lo, page_hi)
        lines.append(annotate_gap_text(full_text, lo, hi, expected_xlit, confirmed_initials))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(rows)} entries to {OUT_PATH}")
    print(f"file size: {OUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
