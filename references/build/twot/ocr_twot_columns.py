"""Render every page of the TWOT PDF and OCR it column-aware: two-column
pages are cropped into left/right halves and OCR'd separately, left column
first then right -- fixing a confirmed systemic bug where Tesseract's
auto column-order detection reads the RIGHT column before the LEFT column
on this book's layout, corrupting the text's actual reading order (verified
visually against the source PDF on multiple pages). Single-column pages
(front matter) are OCR'd whole, unsplit, using column_detect.py's gutter
detection rather than a fixed split -- splitting a single-column page in
half would corrupt it by interleaving half-lines from both fabricated
"columns".
"""
import subprocess
from multiprocessing import Pool
from pathlib import Path

import pymupdf

from twot.column_detect import detect_column_split

SRC_PDF = Path("/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf")
OUT_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-colsplit")
DPI = 400
WORKERS = 8


def ocr_image_bytes(png_path: Path) -> str:
    result = subprocess.run(
        ["tesseract", str(png_path), "stdout", "-l", "heb+eng"],
        capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="replace")


def ocr_page(page_num: int) -> None:
    out_txt = OUT_DIR / f"page-{page_num:04d}.txt"
    if out_txt.exists():
        return

    doc = pymupdf.open(SRC_PDF)
    page = doc[page_num]

    # detect columns at a cheap resolution, apply the split (proportionally)
    # to the actual high-DPI render used for OCR
    probe_pix = page.get_pixmap(dpi=200)
    split_at_probe_dpi = detect_column_split(probe_pix)

    png_path = OUT_DIR / f"_tmp-{page_num:04d}.png"

    if split_at_probe_dpi is None:
        full_pix = page.get_pixmap(dpi=DPI)
        full_pix.save(png_path)
        text = ocr_image_bytes(png_path)
        png_path.unlink()
    else:
        # clip is in page-point coordinates, not pixels -- convert the
        # detected pixel split (from the 200dpi probe render) to points
        split_frac = split_at_probe_dpi / probe_pix.width
        pr = page.rect
        split_x_pts = pr.x0 + pr.width * split_frac

        left_clip = pymupdf.Rect(pr.x0, pr.y0, split_x_pts, pr.y1)
        right_clip = pymupdf.Rect(split_x_pts, pr.y0, pr.x1, pr.y1)

        left_pix = page.get_pixmap(dpi=DPI, clip=left_clip)
        right_pix = page.get_pixmap(dpi=DPI, clip=right_clip)

        left_png = OUT_DIR / f"_tmp-{page_num:04d}-L.png"
        right_png = OUT_DIR / f"_tmp-{page_num:04d}-R.png"
        left_pix.save(left_png)
        right_pix.save(right_png)

        left_text = ocr_image_bytes(left_png)
        right_text = ocr_image_bytes(right_png)
        text = left_text + "\n\n" + right_text

        left_png.unlink()
        right_png.unlink()

    doc.close()
    out_txt.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(SRC_PDF)
    total = doc.page_count
    doc.close()
    print(f"Column-aware OCRing {total} pages with {WORKERS} workers...", flush=True)

    with Pool(WORKERS) as pool:
        done = 0
        for _ in pool.imap_unordered(ocr_page, range(total)):
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{total}", flush=True)

    print("OCR complete.")


if __name__ == "__main__":
    main()
