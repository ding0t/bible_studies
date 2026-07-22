"""Build study-notes.db from the study-Bible EPUBs.

Every source registered in study_notes/sources.py is license_tier='quotation-only'
-- commercial study Bible products. Everything this script produces (the
unzipped EPUB cache, extracted images, the resulting database) is written
OUTSIDE this git repository, on the same local media volume the source EPUBs
already live on. Never point LOCAL_ONLY_ROOT at a path inside bible_studies/.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sqlite3

from study_notes.epub_utils import unzip_epub
from study_notes.extractors import REGISTRY
from study_notes.sources import SOURCES
from study_notes.writer import write_work

LOCAL_ONLY_ROOT = Path("/Volumes/media/bible/local-only-build")
UNZIP_CACHE = LOCAL_ONLY_ROOT / "unzipped"
IMAGES_ROOT = LOCAL_ONLY_ROOT / "images"
DB_PATH = LOCAL_ONLY_ROOT / "study-notes.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "study_notes" / "schema.sql"
TODAY = date.today().isoformat()


def init_db() -> sqlite3.Connection:
    LOCAL_ONLY_ROOT.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def main() -> None:
    assert "bible_studies" not in str(LOCAL_ONLY_ROOT), \
        "LOCAL_ONLY_ROOT must never resolve inside the git repo -- refusing to run"

    conn = init_db()
    for config in SOURCES:
        if not config.epub_path.exists():
            print(f"SKIP {config.work_id}: epub not found at {config.epub_path}")
            continue

        print(f"=== {config.work_id} ===")
        unzipped = unzip_epub(config.epub_path, UNZIP_CACHE / config.work_id)
        extractor_cls = REGISTRY[config.extractor]
        extractor = extractor_cls(config, unzipped, IMAGES_ROOT / config.work_id)
        result = extractor.extract()

        print(f"  verses={len(result.verses)} notes={len(result.notes)} "
              f"introductions={len(result.introductions)} "
              f"topical_articles={len(result.topical_articles)} images={len(result.images)}")

        write_work(conn, config, result, TODAY)

    conn.close()
    print(f"\nBuild complete: {DB_PATH}")


if __name__ == "__main__":
    main()
