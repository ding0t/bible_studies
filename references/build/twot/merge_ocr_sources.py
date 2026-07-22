"""Build a merged OCR page directory: 400 DPI as the baseline for every page,
overridden by the 600 DPI targeted re-OCR wherever that exists (i.e. only the
pages tied to currently-suspect entries). Symlinks where possible to avoid
duplicating ~1GB of page text unnecessarily.
"""
from pathlib import Path

BASE_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-400dpi")
OVERRIDE_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-600dpi-targeted")
MERGED_DIR = Path("/Volumes/media/bible/local-only-build/twot-ocr-pages-merged")


def main() -> None:
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    override_names = {p.name for p in OVERRIDE_DIR.glob("page-*.txt")}

    linked, overridden = 0, 0
    for src in sorted(BASE_DIR.glob("page-*.txt")):
        dest = MERGED_DIR / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        if src.name in override_names:
            dest.write_text((OVERRIDE_DIR / src.name).read_text(encoding="utf-8"), encoding="utf-8")
            overridden += 1
        else:
            dest.symlink_to(src)
            linked += 1

    print(f"merged directory: {linked} pages linked from 400dpi baseline, "
          f"{overridden} pages overridden with 600dpi targeted OCR")


if __name__ == "__main__":
    main()
