"""Render every page of the TWOT PDF and OCR it with Tesseract (heb+eng).
Writes one .txt file per page to OUT_DIR, incrementally, so progress survives
an interruption -- skips pages whose output file already exists, so this is
safe to re-run. Parallelized across CPU cores; each worker renders its own
page (pymupdf) then shells out to tesseract (no benefit to sharing a process
pool across both steps, and tesseract itself is single-threaded per call).
"""
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import pymupdf

SRC_PDF = Path("/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf")
# 400 DPI confirmed to genuinely improve header-line recognition over 300 DPI
# (verified on known-suspect pages); 600 DPI tested too but sometimes
# regressed on the same pages, so 400 is the sweet spot, not "higher is better".
OUT_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-400dpi")
DPI = 400
WORKERS = 8


def ocr_page(page_num: int) -> None:
    out_txt = OUT_DIR / f"page-{page_num:04d}.txt"
    if out_txt.exists():
        return
    doc = pymupdf.open(SRC_PDF)
    page = doc[page_num]
    pix = page.get_pixmap(dpi=DPI)
    png_path = OUT_DIR / f"_tmp-{page_num:04d}.png"
    pix.save(png_path)
    doc.close()

    result = subprocess.run(
        ["tesseract", str(png_path), "stdout", "-l", "heb+eng"],
        capture_output=True,  # bytes, not text=True -- tesseract's stderr can contain
    )                          # non-UTF8 bytes that would crash text-mode decoding
    out_txt.write_text(result.stdout.decode("utf-8", errors="replace"), encoding="utf-8")
    png_path.unlink()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(SRC_PDF)
    total = doc.page_count
    doc.close()
    print(f"OCRing {total} pages with {WORKERS} workers...", flush=True)

    with Pool(WORKERS) as pool:
        done = 0
        for _ in pool.imap_unordered(ocr_page, range(total)):
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{total}", flush=True)

    print("OCR complete.")


if __name__ == "__main__":
    main()
