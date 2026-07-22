"""Re-OCR at 600 DPI only the pages associated with current 'suspect'
entries -- targeted, not a full-book re-run. 600 DPI regressed on some pages
in earlier testing, so this is explicitly an experiment to see whether it
helps on THIS specific problem set, not a blanket upgrade.
"""
import json
import subprocess
import sqlite3
from multiprocessing import Pool
from pathlib import Path

import pymupdf

SRC_PDF = Path("/Volumes/media/bible/reference/Theological Wordbook of the Old Testament.pdf")
DB_PATH = Path("/Volumes/media/bible/local-only-build/lexicon-restricted.db")
OUT_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-600dpi-targeted")
DPI = 600
WORKERS = 8


def get_target_pages() -> list[int]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT source_pages FROM entries WHERE text_confidence='suspect'").fetchall()
    pages = set()
    for (raw,) in rows:
        pages.update(json.loads(raw))
    return sorted(pages)


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
        capture_output=True,
    )
    out_txt.write_text(result.stdout.decode("utf-8", errors="replace"), encoding="utf-8")
    png_path.unlink()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = get_target_pages()
    print(f"OCRing {len(pages)} targeted pages at {DPI} DPI with {WORKERS} workers...", flush=True)
    with Pool(WORKERS) as pool:
        for i, _ in enumerate(pool.imap_unordered(ocr_page, pages)):
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(pages)}", flush=True)
    print("Targeted OCR complete.")


if __name__ == "__main__":
    main()
