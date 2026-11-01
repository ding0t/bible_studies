"""Build study-notes.db from the study-Bible EPUBs.

Every source registered in study_notes/sources.py is license_tier='quotation-only'
-- commercial study Bible products. Everything this script produces (the
unzipped EPUB cache, extracted images, the resulting database) is written
OUTSIDE this git repository, on the same local media volume the source EPUBs
already live on. Never point LOCAL_ONLY_ROOT at a path inside bible_studies/.
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sqlite3

from study_notes.epub_utils import unzip_epub
from study_notes.extractors import REGISTRY
from study_notes.sources import SOURCES
from study_notes.writer import write_work

import media_root
from book_map import STEP_ABBREV_TO_OSIS

LOCAL_ONLY_ROOT = media_root.local_only_build()
UNZIP_CACHE = LOCAL_ONLY_ROOT / "unzipped"
IMAGES_ROOT = LOCAL_ONLY_ROOT / "images"
DB_PATH = LOCAL_ONLY_ROOT / "study-notes.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "study_notes" / "schema.sql"
TODAY = date.today().isoformat()
TTESV_PATH = next((Path(__file__).resolve().parents[1] / "open-data" / "stepbible-data" /
                   "Tagged-Bibles").glob("TTESV*.txt"), None)


def init_db() -> sqlite3.Connection:
    LOCAL_ONLY_ROOT.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def write_esv_tags(conn: sqlite3.Connection) -> None:
    """STEP's TTESV word tags for the ESV, beside the ESV text they index.

    The tags are open data (CC BY-NC) and live in the repo, but they are useless without the ESV
    words, which may not be committed -- so they are joined here, where the ESV already is.
    Lines read "$Gen 1:2<TAB>04+05=<08414><TAB>11=<00914>+<00996>": the ESV word positions, then
    the Strong's numbers they render. Their positions count words in the ESV 2011/2016 text.
    Psalm titles are verse 0 in TTESV and absent from the ESV verses here, so they are skipped.
    """
    if TTESV_PATH is None:
        print("SKIP esv tags: TTESV not found under references/open-data/stepbible-data")
        return
    conn.execute("DELETE FROM esv_tags")
    conn.execute("DELETE FROM works WHERE work_id='step-ttesv'")
    conn.execute(
        "INSERT INTO works (work_id, title, publisher, year, source_id, source_path, ingested_at, "
        "license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?)",
        ("step-ttesv", "TTESV: Tyndale Translation tags for the ESV", "Tyndale House, Cambridge",
         None, "stepbible-data", str(TTESV_PATH.relative_to(TTESV_PATH.parents[3])), TODAY,
         "CC BY-NC 4.0", "restricted-nc", "Tyndale House, Cambridge, and STEP Bible (www.STEPBible.org)"))
    books = {**STEP_ABBREV_TO_OSIS, "Ezek": "Ezek", "Joel": "Joel", "Song": "Song"}
    rows = []
    for line in TTESV_PATH.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("$"):
            continue
        head, *cells = line.rstrip("\t").split("\t")
        abbrev, _, place = head[1:].partition(" ")
        chapter, verse = (int(x) for x in place.split(":"))
        if verse == 0 or abbrev not in books:
            continue
        for cell in cells:
            positions, _, strongs = cell.partition("=")
            if not strongs:
                continue
            numbers = [int(p) for p in positions.split("+")]
            # Hebrew is five digits and Greek four, with no prefix; a name built from two words
            # (Yahweh-nissi) is "<03068+05251>". Written the way bible-text.db writes them.
            rows.append(("step-ttesv", books[abbrev], chapter, verse, min(numbers), max(numbers),
                         "+".join(("H" if len(n) >= 5 else "G") + str(int(n))
                                  for n in re.findall(r"\d+", strongs))))
    conn.executemany(
        "INSERT INTO esv_tags (work_id, book, chapter, verse, word_start, word_end, strongs) "
        "VALUES (?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"step-ttesv: {len(rows)} ESV word tags")


def main() -> None:
    assert "bible_studies" not in str(LOCAL_ONLY_ROOT), \
        "LOCAL_ONLY_ROOT must never resolve inside the git repo -- refusing to run"

    if "--esv-tags" in sys.argv:  # add the tags to the existing database, no EPUB rebuild
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(re.search(r"CREATE TABLE esv_tags.*?;\s*CREATE INDEX idx_esv_tags_ref[^;]*;",
                                     SCHEMA_PATH.read_text(), re.S)[0]
                           .replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                           .replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS"))
        write_esv_tags(conn)
        conn.close()
        return

    conn = init_db()
    for config in SOURCES:
        if not config.epub_path.exists():
            print(f"SKIP {config.work_id}: epub not found at {config.epub_path}")
            continue

        print(f"=== {config.work_id} ===")
        extractor_cls = REGISTRY[config.extractor]
        # Most sources are EPUBs that must be unzipped first; a single-file source (a Jet/Access
        # module, say) declares needs_unzip = False and is handed its own path instead.
        source_root = (unzip_epub(config.epub_path, UNZIP_CACHE / config.work_id)
                       if extractor_cls.needs_unzip else config.epub_path)
        extractor = extractor_cls(config, source_root, IMAGES_ROOT / config.work_id)
        result = extractor.extract()

        print(f"  verses={len(result.verses)} notes={len(result.notes)} "
              f"introductions={len(result.introductions)} "
              f"topical_articles={len(result.topical_articles)} images={len(result.images)}")

        write_work(conn, config, result, TODAY)

    write_esv_tags(conn)
    conn.close()
    print(f"\nBuild complete: {DB_PATH}")


if __name__ == "__main__":
    main()
