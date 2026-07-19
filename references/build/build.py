"""Build bible-text.db from the open-data/ submodules.

Master build artifact -- gitignored, fully regenerable from the submodules.
Contains ALL license tiers (open / restricted-nc / unknown) with heritage
metadata per work; tier filtering happens at export time (see export.py),
not here.
"""
import csv
import sqlite3
import subprocess
import sys
from datetime import date, timezone
from pathlib import Path
from xml.etree import ElementTree

import yaml

from book_map import MACULA_USFM_TO_OSIS, SCROLLMAPPER_NAME_TO_OSIS

REPO_ROOT = Path(__file__).resolve().parents[2]
OPEN_DATA = REPO_ROOT / "references" / "open-data"
BUILD_DIR = Path(__file__).resolve().parent
OUT_DIR = BUILD_DIR / "out"
DB_PATH = OUT_DIR / "bible-text.db"
TODAY = date.today().isoformat()

with open(BUILD_DIR / "license_map.yml") as f:
    LICENSE_MAP = yaml.safe_load(f)


def submodule_commit(name: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "submodule", "status", f"references/open-data/{name}"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip().lstrip("-+U ").split()[0]


def classify_license(license_str: str | None) -> str:
    if not license_str:
        return "unknown"
    return LICENSE_MAP.get(license_str, "unknown")


def init_db() -> sqlite3.Connection:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript((BUILD_DIR / "schema.sql").read_text())
    return conn


def scrollmapper_scope() -> dict[str, str]:
    """translation_code -> language_code, restricted to English + original languages
    (Hebrew, Greek) per the current scope. Latin Vulgate and everything else in
    scrollmapper's 60+ other languages is available but deliberately excluded here --
    add to this dict (or extend the glob) if that scope ever changes."""
    source_dir = OPEN_DATA / "scrollmapper-bible-databases" / "sources"
    scope: dict[str, str] = {}
    for lang in ("en", "grc", "he", "hbo"):
        lang_dir = source_dir / lang
        if not lang_dir.is_dir():
            continue
        for entry in lang_dir.iterdir():
            if entry.is_dir():
                scope[entry.name] = lang
    return scope


def ingest_scrollmapper(conn: sqlite3.Connection) -> None:
    source_dir = OPEN_DATA / "scrollmapper-bible-databases"
    sqlite_dir = source_dir / "formats" / "sqlite"
    commit = submodule_commit("scrollmapper-bible-databases")
    fork_url = "https://github.com/ding0t/bible_databases"
    scope = scrollmapper_scope()

    skipped, loaded = [], []
    tier_counts: dict[str, int] = {}

    for db_file in sorted(sqlite_dir.glob("*.db")):
        code = db_file.stem
        if code not in scope:
            continue  # out of scope: not English or an original-language text
        language = scope[code]
        try:
            src = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
            tables = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "translations" not in tables or f"{code}_verses" not in tables:
                skipped.append((code, "missing expected tables (empty/broken db)"))
                src.close()
                continue

            row = src.execute("SELECT translation, title, license FROM translations").fetchone()
            if row is None:
                skipped.append((code, "no translations row"))
                src.close()
                continue
            _, title, license_str = row
            tier = classify_license(license_str)

            work_id = f"scrollmapper-{code}"
            conn.execute(
                "INSERT INTO works (work_id, translation_code, title, language, source_id, "
                "source_repo_url, source_commit, ingested_at, license, license_tier, attribution) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (work_id, code, title, language, "scrollmapper-bible-databases", fork_url, commit,
                 TODAY, license_str, tier, "scrollmapper/bible_databases"),
            )

            rows = src.execute(
                f"SELECT DISTINCT b.name, v.chapter, v.verse, TRIM(v.text) "
                f"FROM {code}_verses v JOIN {code}_books b ON v.book_id = b.id "
                f"WHERE TRIM(v.text) != ''"
            ).fetchall()
            verse_rows = []
            unmapped_books = set()
            for name, chapter, verse, text in rows:
                osis = SCROLLMAPPER_NAME_TO_OSIS.get(name)
                if osis is None:
                    unmapped_books.add(name)
                    continue
                verse_rows.append((work_id, osis, chapter, verse, text))
            conn.executemany(
                "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)",
                verse_rows,
            )
            if unmapped_books:
                skipped.append((code, f"unmapped books (likely deuterocanonical, skipped): {sorted(unmapped_books)}"))

            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            loaded.append((code, tier, len(verse_rows)))
            src.close()
        except sqlite3.Error as e:
            skipped.append((code, f"sqlite error: {e}"))

    conn.commit()
    full_skips = [(c, r) for c, r in skipped if "unmapped books" not in r]
    partial = [(c, r) for c, r in skipped if "unmapped books" in r]
    print(f"scrollmapper: loaded {len(loaded)} translations, {len(full_skips)} fully skipped, "
          f"{len(partial)} loaded-with-unmapped-extra-books (deuterocanonical/apocrypha, out of scope this pass)")
    print(f"  tier counts: {tier_counts}")
    for code, reason in full_skips:
        print(f"  SKIPPED {code}: {reason}")


def ingest_scrollmapper_crossrefs(conn: sqlite3.Connection) -> None:
    extras_dir = OPEN_DATA / "scrollmapper-bible-databases" / "formats" / "sqlite" / "extras"
    commit = submodule_commit("scrollmapper-bible-databases")
    work_id = "openbible-crossrefs"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, None, "OpenBible.info Cross References", None, "scrollmapper-bible-databases",
         "https://github.com/ding0t/bible_databases", commit, TODAY, "CC-BY", "open",
         "openbible.info, https://www.openbible.info/labs/cross-references/"),
    )
    total = 0
    for shard in sorted(extras_dir.glob("cross_references_*.db")):
        src = sqlite3.connect(f"file:{shard}?mode=ro", uri=True)
        rows = src.execute(
            "SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse_start, to_verse_end, votes "
            "FROM cross_references"
        ).fetchall()
        mapped = []
        for from_book, fc, fv, to_book, tc, tvs, tve, votes in rows:
            fb, tb = SCROLLMAPPER_NAME_TO_OSIS.get(from_book), SCROLLMAPPER_NAME_TO_OSIS.get(to_book)
            if fb is None or tb is None:
                continue
            mapped.append((work_id, fb, fc, fv, tb, tc, tvs, tve, votes))
        conn.executemany(
            "INSERT INTO cross_references (work_id, from_book, from_chapter, from_verse, "
            "to_book, to_chapter, to_verse_start, to_verse_end, votes) VALUES (?,?,?,?,?,?,?,?,?)",
            mapped,
        )
        total += len(mapped)
        src.close()
    conn.commit()
    print(f"cross_references: loaded {total} rows")


def ingest_morphhb(conn: sqlite3.Connection) -> None:
    from BibleOrgSys import BibleOrgSysGlobals
    from BibleOrgSys.OriginalLanguages.HebrewWLCBible import OSISHebrewWLCBible
    from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey

    BibleOrgSysGlobals.preloadCommonData()

    wlc_dir = OPEN_DATA / "morphhb" / "wlc"
    commit = submodule_commit("morphhb")
    work_id = "morphhb-wlc"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, "WLC", "Westminster Leningrad Codex", "heb", "morphhb",
         "https://github.com/ding0t/morphhb", commit, TODAY, "Public Domain (text); CC BY 4.0 (tagging)",
         "open", "Open Scriptures Hebrew Bible", "WLC text is public domain; morphological tagging is CC BY 4.0"),
    )

    verse_rows, morph_rows = [], []
    for xml_file in sorted(wlc_dir.glob("*.xml")):
        if xml_file.stem == "VerseMap":
            continue
        osis_book_code = xml_file.stem  # our canonical code, matches scrollmapper/sblgnt convention
        wlc = OSISHebrewWLCBible(str(xml_file))
        wlc.load()
        bos_book_code = list(wlc.books.keys())[0]  # BibleOrgSys's OWN internal BBB scheme -- lookups only, never stored
        book_obj = wlc.books[bos_book_code]

        for c in range(1, book_obj.getNumChapters() + 1):
            for v in range(1, book_obj.getNumVerses(c) + 1):
                key = SimpleVerseKey(bos_book_code, c, v)
                verse_text = wlc.getVerseText(key)
                if verse_text:
                    verse_rows.append((work_id, osis_book_code, c, v, verse_text))

                word_pos = 0
                for entry in wlc.getVerseDataList(key) or []:
                    if entry.getMarker() not in ("v~", "p~"):
                        continue
                    for wd in wlc.getVerseDictList(entry, key):
                        word_pos += 1
                        morph_rows.append((
                            work_id, osis_book_code, c, v, word_pos,
                            wd.get("word"), wd.get("strong"), wd.get("morph"),
                            wd.get("cantillationLevel"),
                        ))
        print(f"  morphhb {osis_book_code} (internal {bos_book_code}): {book_obj.getNumChapters()} chapters loaded")

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows,
    )
    conn.executemany(
        "INSERT INTO morphology (work_id, book, chapter, verse, word_position, surface_form, "
        "strongs_id, morph_code, cantillation_level) VALUES (?,?,?,?,?,?,?,?,?)", morph_rows,
    )
    conn.commit()
    print(f"morphhb: {len(verse_rows)} verses, {len(morph_rows)} morphology rows")


def ingest_sblgnt(conn: sqlite3.Connection) -> None:
    xml_dir = OPEN_DATA / "sblgnt" / "data" / "sblgnt" / "xml"
    commit = submodule_commit("sblgnt")
    work_id = "sblgnt"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, "SBLGNT", "SBL Greek New Testament", "grc", "sblgnt",
         "https://github.com/ding0t/SBLGNT", commit, TODAY, "CC BY 4.0", "open",
         "SBL & Logos Bible Software"),
    )

    verse_rows = []
    for xml_file in sorted(xml_dir.glob("*.xml")):
        if xml_file.stem == "sblgnt":  # combined file, skip -- using per-book files instead
            continue
        book_code = xml_file.stem
        tree = ElementTree.parse(xml_file)
        current_ref, words = None, []
        for elem in tree.getroot().iter():
            if elem.tag == "verse-number":
                if current_ref and words:
                    verse_rows.append((*current_ref, "".join(words).strip()))
                ref = elem.get("id")  # e.g. "John 1:1"
                _, cv = ref.rsplit(" ", 1)
                c, v = cv.split(":")
                current_ref = (work_id, book_code, int(c), int(v))
                words = []
            elif elem.tag == "w" and current_ref:
                words.append(elem.text or "")
            elif elem.tag == "suffix" and current_ref:
                words.append(elem.text or "")
        if current_ref and words:
            verse_rows.append((*current_ref, "".join(words).strip()))

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows,
    )
    conn.commit()
    print(f"sblgnt: {len(verse_rows)} verses")


def ingest_macula_greek(conn: sqlite3.Connection) -> None:
    tsv_path = OPEN_DATA / "macula-greek" / "SBLGNT" / "tsv" / "macula-greek-SBLGNT.tsv"
    commit = submodule_commit("macula-greek")
    work_id = "macula-greek-sblgnt"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, "SBLGNT", "MACULA Greek Linguistic Datasets (SBLGNT)", "grc", "macula-greek",
         "https://github.com/ding0t/macula-greek", commit, TODAY, "CC BY 4.0", "open",
         "MACULA Greek Linguistic Datasets © Biblica, Inc.",
         "Louw-Nida domain data (domain/ln columns) is UBS MARBLE project data 'used with permission' "
         "to Clear-Bible specifically per their LICENSE.md -- not itself a separate blanket CC grant, "
         "cite carefully. strongs_id is occasionally a '+'-joined compound (one word, multiple Strong's "
         "numbers) -- lookups on a single number need to account for that, not just '='."),
    )

    morph_rows = []
    last_key, word_pos = None, 0
    with open(tsv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            verse_ref, _ = row["ref"].split("!")
            book_usfm, cv = verse_ref.split(" ")
            chapter, verse = cv.split(":")
            book = MACULA_USFM_TO_OSIS[book_usfm]
            key = (book, chapter, verse)
            word_pos = word_pos + 1 if key == last_key else 1
            last_key = key
            morph_rows.append((
                work_id, book, int(chapter), int(verse), word_pos,
                row["text"] or None, row["strong"] or None, row["morph"] or None, None,
                row["lemma"] or None, row["gloss"] or None, row["ln"] or row["domain"] or None,
            ))

    conn.executemany(
        "INSERT INTO morphology (work_id, book, chapter, verse, word_position, surface_form, "
        "strongs_id, morph_code, cantillation_level, lemma, gloss, domain_code) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", morph_rows,
    )
    conn.commit()
    print(f"macula-greek: {len(morph_rows)} morphology rows")


def ingest_macula_hebrew(conn: sqlite3.Connection) -> None:
    tsv_path = OPEN_DATA / "macula-hebrew" / "WLC" / "tsv" / "macula-hebrew.tsv"
    commit = submodule_commit("macula-hebrew")
    work_id = "macula-hebrew-wlc"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, "WLC", "MACULA Hebrew Linguistic Datasets (WLC)", "heb", "macula-hebrew",
         "https://github.com/ding0t/macula-hebrew", commit, TODAY, "CC BY 4.0", "open",
         "MACULA Hebrew Linguistic Datasets © Biblica, Inc.",
         "domain_code is the `lexdomain` column (falling back to `contextualdomain`), from the Semantic "
         "Dictionary of Biblical Hebrew (SDBH). The raw TSV also carries `coredomain` and a separate "
         "`sdbh` sense-ID column, neither loaded here. Hebrew words are frequently split into multiple "
         "morpheme rows sharing one surface word (e.g. a prefixed preposition gets its own row before "
         "the noun it attaches to) -- word_position counts rows, not surface words."),
    )

    morph_rows = []
    last_key, word_pos = None, 0
    with open(tsv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            verse_ref, _ = row["ref"].split("!")
            book_usfm, cv = verse_ref.split(" ")
            chapter, verse = cv.split(":")
            book = MACULA_USFM_TO_OSIS[book_usfm]
            key = (book, chapter, verse)
            word_pos = word_pos + 1 if key == last_key else 1
            last_key = key
            morph_rows.append((
                work_id, book, int(chapter), int(verse), word_pos,
                row["text"] or None, row["strongnumberx"] or None, row["morph"] or None, None,
                row["lemma"] or None, row["gloss"] or None, row["lexdomain"] or row["contextualdomain"] or None,
            ))

    conn.executemany(
        "INSERT INTO morphology (work_id, book, chapter, verse, word_position, surface_form, "
        "strongs_id, morph_code, cantillation_level, lemma, gloss, domain_code) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", morph_rows,
    )
    conn.commit()
    print(f"macula-hebrew: {len(morph_rows)} morphology rows")


def ingest_hebrew_literary_units(conn: sqlite3.Connection) -> None:
    map_path = OPEN_DATA / "hebrew-vocab-tools" / "pericope_verse_map.txt"
    commit = submodule_commit("hebrew-vocab-tools")
    work_id = "hebrew-vocab-tools-pericopes"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, None, "WLC Pericope Divisions (samekh/pe markers)", "heb", "hebrew-vocab-tools",
         "https://github.com/ding0t/hebrew-vocab-tools", commit, TODAY, "CC BY 4.0", "open",
         "fhardison/hebrew-vocab-tools, derived from the OSHB WLC (see morphhb above)",
         "Paragraph-level units (paragraphs.txt) are token-index ranges, not verse refs, and aren't "
         "ingested here -- would need cross-referencing against the tool's own tokens.txt to resolve "
         "to verses. Only pericope-level units (already verse-ref-keyed) are loaded."),
    )

    def parse_ref(ref: str) -> tuple[str, int, int]:
        book, chapter, verse = ref.rsplit(".", 2)
        return book, int(chapter), int(verse)

    unit_rows = []
    with open(map_path, encoding="utf-8") as f:
        for line in f:
            _, start_ref, end_ref = line.split()
            start_book, start_chapter, start_verse = parse_ref(start_ref)
            _, end_chapter, end_verse = parse_ref(end_ref)
            unit_rows.append((work_id, start_book, "pericope", start_chapter, start_verse, end_chapter, end_verse))

    conn.executemany(
        "INSERT INTO literary_units (work_id, book, unit_type, start_chapter, start_verse, "
        "end_chapter, end_verse) VALUES (?,?,?,?,?,?,?)", unit_rows,
    )
    conn.commit()
    print(f"hebrew-vocab-tools: {len(unit_rows)} pericope units")


def main() -> None:
    conn = init_db()
    ingest_scrollmapper(conn)
    ingest_scrollmapper_crossrefs(conn)
    ingest_morphhb(conn)
    ingest_sblgnt(conn)
    ingest_macula_greek(conn)
    ingest_macula_hebrew(conn)
    ingest_hebrew_literary_units(conn)
    conn.close()
    print(f"\nBuild complete: {DB_PATH}")


if __name__ == "__main__":
    main()
