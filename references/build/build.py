"""Build bible-text.db from the open-data/ submodules.

Master build artifact -- gitignored, fully regenerable from the submodules.
Contains ALL license tiers (open / restricted-nc / unknown) with heritage
metadata per work; tier filtering happens at export time (see export.py),
not here.
"""
import csv
import html
import re
import sqlite3
import subprocess
import sys
import urllib.request
import zipfile
from datetime import date, timezone
from pathlib import Path
from xml.etree import ElementTree

import yaml

from book_map import MACULA_USFM_TO_OSIS, NUM_TO_OSIS, SCROLLMAPPER_NAME_TO_OSIS

REPO_ROOT = Path(__file__).resolve().parents[2]
OPEN_DATA = REPO_ROOT / "references" / "open-data"
BUILD_DIR = Path(__file__).resolve().parent
OUT_DIR = BUILD_DIR / "out"
DB_PATH = OUT_DIR / "bible-text.db"
CACHE_DIR = BUILD_DIR / "cache"
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
         "the noun it attaches to) -- word_position counts rows, not surface words. Spot-checked (Ps "
         "23:1): on some pronominal-suffix splits the `gloss` column is misassigned across the two "
         "morpheme rows even though `lemma`/`strong` are correct on each (verified against our own "
         "Strong's dictionary) -- e.g. the row for רֹעִי glossed 'shepherd' correctly carries strong "
         "H7473, but the gloss text itself sits on the wrong row of the pair. Not observed on simple "
         "article/preposition splits (spot-checked Gen 1:5) -- looks isolated to certain suffix "
         "constructions, not systemic, but don't trust `gloss` blindly on split rows without a check."),
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


def ingest_ebible(
    conn: sqlite3.Connection, ebible_id: str, translation_code: str, title: str, language: str,
    license_str: str = "Public Domain", license_tier: str = "open",
) -> None:
    """Fetches a USFM translation from eBible.org into a gitignored build cache and ingests it.

    eBible.org is a plain file host, not a git repo -- there's nothing to fork/submodule the way
    every other source in this file works. Rather than vendoring raw USFM into this repo (one
    translation per source would sprawl fast -- WEB today, several Greek/Hebrew texts are candidates
    next), the zip is fetched on demand into CACHE_DIR and re-ingested on every build. Re-run this
    function (or just build.py) to pick up any upstream edition update; nothing here is pinned.
    """
    from BibleOrgSys import BibleOrgSysGlobals
    from BibleOrgSys.Formats.USFMBible import USFMBible
    from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey

    BibleOrgSysGlobals.preloadCommonData()

    usfm_dir = CACHE_DIR / ebible_id
    if not any(usfm_dir.glob("*.usfm")):
        usfm_dir.mkdir(parents=True, exist_ok=True)
        zip_path = usfm_dir / f"{ebible_id}_usfm.zip"
        request = urllib.request.Request(
            f"https://eBible.org/Scriptures/{ebible_id}_usfm.zip",
            headers={"User-Agent": "Mozilla/5.0 (compatible; bible_studies build script)"},
        )
        with urllib.request.urlopen(request) as response, open(zip_path, "wb") as f:
            f.write(response.read())
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(usfm_dir)
        # This edition tags words with USFM 3.0 word-level attributes (\w word|strong="G1234"\w*),
        # and NT books additionally double-tag some words with a non-standard \ww run carrying
        # the same attribute. The installed BibleOrgSys doesn't strip either correctly here (it
        # handles OT \w|attr fine but not NT), leaking "word|strong=\"G1234\"" into verse text.
        # We already get precise Strong's tagging from macula-greek/macula-hebrew/sblgnt, so this
        # is pure redundancy -- strip the \ww run entirely, then strip any surviving |attribute.
        for usfm_file in usfm_dir.glob("*.usfm"):
            text = usfm_file.read_text(encoding="utf-8")
            cleaned = re.sub(r"\\ww\s.*?\\ww\*", "", text, flags=re.DOTALL)
            cleaned = re.sub(r"\|[^\\]*", "", cleaned)
            if cleaned != text:
                usfm_file.write_text(cleaned, encoding="utf-8")

    edition_date = None
    id_lines = (usfm_dir.glob("*GEN*.usfm") if ebible_id.startswith("eng") else usfm_dir.glob("*.usfm"))
    for usfm_file in id_lines:
        match = re.search(r"^\\id\s+\S+.*?(\d{4}-\d{2}-\d{2})", usfm_file.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            edition_date = match.group(1)
        break

    work_id = f"ebible-{ebible_id}"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, translation_code, title, language, "ebible.org",
         f"https://ebible.org/find/show.php?id={ebible_id}", edition_date, TODAY,
         license_str, license_tier, "eBible.org",
         f"Not a submodule -- fetched from https://eBible.org/Scriptures/{ebible_id}_usfm.zip into "
         "references/build/cache/ (gitignored) and re-ingested on every build, not pinned to a "
         "specific upstream git revision (eBible.org isn't git-hosted). source_commit above holds the "
         "USFM edition date self-reported in the \\id line, the closest thing to a version marker this "
         "source has. Confirm license per-id before adding another eBible.org source -- not all listed "
         "translations are public domain. LXX/deuterocanonical editions may use different "
         "chapter/verse numbering than the Masoretic/English versification in some books (Psalms, "
         "Daniel, Esther) -- don't assume (book,chapter,verse) lines up 1:1 against other works "
         "without checking for that specific book."),
    )

    bible = USFMBible(str(usfm_dir))
    bible.load()

    verse_rows = []
    for bos_code in bible.getBookList():
        osis_book = MACULA_USFM_TO_OSIS.get(bos_code)
        if osis_book is None:
            continue  # front matter, glossary, deuterocanonical -- out of scope
        book_obj = bible.books[bos_code]
        for c in range(1, book_obj.getNumChapters() + 1):
            for v in range(1, book_obj.getNumVerses(c) + 1):
                try:
                    verse_text = bible.getVerseText(SimpleVerseKey(bos_code, c, v))
                except KeyError:
                    continue  # versification gaps -- expected for LXX/deuterocanonical editions
                if verse_text:
                    verse_rows.append((work_id, osis_book, c, v, verse_text))

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows,
    )
    conn.commit()
    print(f"ebible-{ebible_id}: {len(verse_rows)} verses")


def ingest_cultural_backgrounds(conn: sqlite3.Connection, edition: str = "niv") -> None:
    """Ingests the NIV/NKJV Cultural Backgrounds Study Bible's verse-by-verse notes.

    Personal-use, machine-local source only -- never distributed, never committed to this
    repo (see references/README.md). The epub isn't git-hosted or fetchable, so unlike
    ingest_ebible() there's no download step: this just parses whatever's already unzipped
    at MEDIA_ROOT below. Skips silently (prints a note, doesn't fail the build) if that path
    isn't present -- this source only exists on the one machine that owns the epub, and the
    rest of the build must stay runnable without it.

    license_tier is 'quotation-only', per schema.sql's own documented (if previously unused)
    tier -- this data must never appear in any export/build step that isn't explicitly
    scoped to stay local. There is currently no export.py in this pipeline to enforce that
    automatically; until one exists, tier-filtering here is a manual discipline, not a
    guarantee.
    """
    media_root = Path("/Volumes/media/bible/local-only-build/unzipped") / f"{edition}-cultural-backgrounds-study-bible" / "OEBPS"
    if not media_root.is_dir():
        print(f"cultural-backgrounds-{edition}: source not found at {media_root}, skipping (expected on machines without the media volume)")
        return

    commit = None  # not git-hosted; nothing to pin
    work_id = f"cultural-backgrounds-{edition}"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, edition.upper(), f"{edition.upper()} Cultural Backgrounds Study Bible", "eng",
         "cultural-backgrounds-study-bible", None, commit, TODAY,
         "Copyrighted, all rights reserved (Zondervan)", "quotation-only",
         "Zondervan, ed. John H. Walton & Craig S. Keener",
         f"Personal-use extraction from a purchased epub at {media_root} -- not git-hosted, not "
         "redistributable. Never export/output this work_id's notes into anything that leaves this "
         "machine. Quote briefly with attribution in a study file; never reproduce a note in full."),
    )

    note_pattern = re.compile(r'<p class="com" id="(com\d+)">(.*?)</p>', re.DOTALL)
    tag_pattern = re.compile(r"<[^>]+>")
    note_rows = []
    seen_ids = set()
    for xhtml_file in sorted(media_root.glob("*.xhtml")):
        text = xhtml_file.read_text(encoding="utf-8")
        for anchor_id, raw_note in note_pattern.findall(text):
            if anchor_id in seen_ids:
                continue
            seen_ids.add(anchor_id)
            digits = anchor_id.removeprefix("com")
            book_num, chapter, verse = int(digits[:2]), int(digits[2:5]), int(digits[5:8])
            osis_book = NUM_TO_OSIS.get(book_num)
            if osis_book is None:
                continue
            clean_text = html.unescape(tag_pattern.sub("", raw_note)).strip()
            note_rows.append((work_id, osis_book, chapter, verse, "cultural-background", clean_text))

    conn.executemany(
        "INSERT INTO notes (work_id, book, chapter, verse, note_type, text) VALUES (?,?,?,?,?,?)",
        note_rows,
    )
    conn.commit()
    print(f"cultural-backgrounds-{edition}: {len(note_rows)} notes")


def main() -> None:
    conn = init_db()
    ingest_scrollmapper(conn)
    ingest_scrollmapper_crossrefs(conn)
    ingest_morphhb(conn)
    ingest_sblgnt(conn)
    ingest_macula_greek(conn)
    ingest_macula_hebrew(conn)
    ingest_hebrew_literary_units(conn)
    ingest_ebible(conn, "eng-web", "WEB", "World English Bible", "eng")
    ingest_ebible(conn, "grcbrent", "Brenton-LXX", "Brenton Septuagint (Greek)", "grc")
    ingest_ebible(conn, "grc-tisch", "Tischendorf", "Tischendorf 8th ed. Greek New Testament", "grc")
    ingest_ebible(conn, "heb", "Delitzsch", "Delitzsch Hebrew Bible (OT+NT)", "heb")
    ingest_cultural_backgrounds(conn)
    conn.close()
    print(f"\nBuild complete: {DB_PATH}")


if __name__ == "__main__":
    main()
