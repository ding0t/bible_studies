"""Detect whether a rendered page is two-column, and if so, find the x-pixel
split point -- by looking for a vertical whitespace gutter in the middle
third of the page. Front matter (intro, contributors, suggestions-for-use)
is single-column prose; the dictionary body is two-column; treating both the
same (fixed 50% split, or no split) breaks one or the other.
"""
import numpy as np
import pymupdf


def detect_column_split(pix: pymupdf.Pixmap) -> int | None:
    """Returns the x-pixel column boundary, or None if the page looks single-column."""
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    gray = arr[:, :, :3].mean(axis=2)
    is_dark = gray < 200

    body_lo, body_hi = int(pix.height * 0.08), int(pix.height * 0.92)
    mid_lo, mid_hi = int(pix.width * 0.35), int(pix.width * 0.65)
    strip = is_dark[body_lo:body_hi, mid_lo:mid_hi]
    if strip.shape[0] == 0:
        return None

    col_dark_counts = strip.sum(axis=0)
    noise_threshold = strip.shape[0] * 0.01
    whitespace_cols = np.where(col_dark_counts <= noise_threshold)[0]

    if len(whitespace_cols) < 5:
        return None  # no real gutter -- single column

    # find the widest contiguous run of whitespace columns (the actual gutter,
    # as opposed to scattered incidental gaps between characters)
    runs = []
    run_start = whitespace_cols[0]
    prev = whitespace_cols[0]
    for c in whitespace_cols[1:]:
        if c != prev + 1:
            runs.append((run_start, prev))
            run_start = c
        prev = c
    runs.append((run_start, prev))
    widest = max(runs, key=lambda r: r[1] - r[0])
    if widest[1] - widest[0] < 3:
        return None  # widest gap still too narrow to be a real gutter

    split_col = mid_lo + (widest[0] + widest[1]) // 2
    return split_col
