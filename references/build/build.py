"""Build bible-text.db from the open-data/ submodules.

Master build artifact -- gitignored, fully regenerable from the submodules.
Contains ALL license tiers (open / restricted-nc / unknown) with heritage
metadata per work; tier filtering happens at export time (see export.py),
not here.
"""
import collections
import csv
import difflib
import json
import math
import re
import sqlite3
import subprocess
import sys
import unicodedata
import urllib.request
import zipfile
from datetime import date, timezone
from pathlib import Path
from xml.etree import ElementTree

import yaml

from book_map import BOS_CODE_TO_USFM, MACULA_USFM_TO_OSIS, NUM_TO_OSIS, SCROLLMAPPER_NAME_TO_OSIS
import quotations
import versification
from versification import scheme_for_work

REPO_ROOT = Path(__file__).resolve().parents[2]
OPEN_DATA = REPO_ROOT / "references" / "open-data"
RESTRICTED_DATA = REPO_ROOT / "references" / "restricted-data"
BUILD_DIR = Path(__file__).resolve().parent
OUT_DIR = BUILD_DIR / "out"
DB_PATH = OUT_DIR / "bible-text.db"
CACHE_DIR = BUILD_DIR / "cache"
TODAY = date.today().isoformat()

with open(BUILD_DIR / "license_map.yml") as f:
    LICENSE_MAP = yaml.safe_load(f)


def submodule_commit_at(rel_path: str) -> str:
    """Pinned commit of a submodule, by its path from the repo root. Sources live under two trees
    -- open-data/ and restricted-data/ -- and the tree a source sits in is the license boundary."""
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "submodule", "status", rel_path],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip().lstrip("-+U ").split()[0]


def submodule_commit(name: str) -> str:
    return submodule_commit_at(f"references/open-data/{name}")


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
            # Upstream stores each verse many times over (ASV: 217714 rows for 31102 references)
            # and the copies differ in whitespace, so DISTINCT on the raw text collapses only the
            # byte-identical ones. Normalize the whitespace, then where copies still disagree keep
            # the one with the most words: the disagreements are lost word separators
            # ("andperfect" for "and perfect"), so the wordiest copy is the intact one. Verified
            # across the 763 ASV references where normalizing alone wasn't enough.
            best: dict[tuple[str, int, int], str] = {}
            unmapped_books = set()
            for name, chapter, verse, text in rows:
                osis = SCROLLMAPPER_NAME_TO_OSIS.get(name)
                if osis is None:
                    unmapped_books.add(name)
                    continue
                normalized = re.sub(r"\s+", " ", text).strip()
                key = (osis, chapter, verse)
                current = best.get(key)
                if current is None or (len(normalized.split()), len(normalized)) > (len(current.split()), len(current)):
                    best[key] = normalized
            verse_rows = [(work_id, osis, chapter, verse, text)
                          for (osis, chapter, verse), text in best.items()]
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


# The WEB's own footnote cross-references, as its translators marked them in the USFM. Tiny beside
# openbible -- a few hundred against 830,000 -- and not a general-purpose chain reference: they sit
# almost entirely on New Testament quotations of the Old, which is exactly where the derived links
# are measured. That makes them worth having despite the size. They are a genuinely independent
# witness, which openbible-via-scrollmapper is not: that file's own header reads
# "#www.openbible.info CC-BY", so checking the derived links against it twice would be checking
# them against one list twice.
#
# BibleOrgSys drops notes during ingest_ebible (cleanText), so these have to be read from the raw
# USFM rather than recovered from the verses table.
_WEB_XREF = re.compile(r"\\x\s.*?\\xo\s*(\d+):(\d+).*?\\xt\s*(.+?)\\x\*", re.S)
_WEB_TARGET = re.compile(r"^(?:((?:[1-4]\s)?[A-Za-z][A-Za-z ]*?)\s+)?(\d+):([\d,\s\u2013-]+)$")


def _parse_web_targets(raw: str) -> list[tuple[str, int, int, int]]:
    """One \\xt payload -> (book, chapter, verse_start, verse_end) rows.

    Handles the four shapes the WEB actually uses: a plain reference, a verse range, a comma list
    of verses in one chapter, and several references separated by ';' where a later one may omit
    the book and continue the previous. A cross-chapter range ("2 Kings 6:31-7:20", em-dash in the
    source) keeps its opening verse -- the schema addresses one chapter, and the anchor is the
    reference a reader follows.
    """
    out: list[tuple[str, int, int, int]] = []
    last_book: str | None = None
    for part in raw.split(";"):
        part = " ".join(part.split())
        part = re.sub(r"^(?:See|see|cf\.?)\s+", "", part)
        part = re.sub(r"\s*\(?LXX\)?$", "", part)
        part = part.split("\u2014")[0].strip()
        if not part:
            continue
        match = _WEB_TARGET.match(part)
        if not match:
            continue
        book = match.group(1) or last_book
        if book is None:
            continue
        last_book = book
        chapter = int(match.group(2))
        for chunk in match.group(3).split(","):
            chunk = chunk.strip()
            if re.fullmatch(r"\d+", chunk):
                out.append((book, chapter, int(chunk), int(chunk)))
            elif re.fullmatch(r"\d+\s*[-\u2013]\s*\d+", chunk):
                start, end = re.split(r"[-\u2013]", chunk)
                out.append((book, chapter, int(start), int(end)))
    return out


def ingest_web_crossrefs(conn: sqlite3.Connection) -> None:
    work_id = "web-crossrefs"
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, None, "World English Bible Cross References", "eng", "ebible-eng-web",
         "https://ebible.org/find/details.php?id=eng-web", None, TODAY, "Public Domain", "open",
         "World English Bible, ebible.org"),
    )
    rows, skipped = [], collections.Counter()
    for path in sorted((CACHE_DIR / "eng-web").glob("*.usfm")):
        text = path.read_text(encoding="utf-8", errors="replace")
        id_match = re.search(r"\\id\s+(\S+)", text)
        if id_match is None:
            continue
        from_book = MACULA_USFM_TO_OSIS.get(id_match.group(1))
        if from_book is None:            # front matter, and the deuterocanonical books
            skipped[id_match.group(1)] += 1
            continue
        for chapter, verse, payload in _WEB_XREF.findall(text):
            for book, to_chapter, start, end in _parse_web_targets(payload):
                osis = SCROLLMAPPER_NAME_TO_OSIS.get(book)
                if osis is None:            # deuterocanonical targets (Wisdom), out of scope here
                    skipped[book] += 1
                    continue
                rows.append((work_id, from_book, int(chapter), int(verse),
                             osis, to_chapter, start, end, None))
    conn.executemany(
        "INSERT INTO cross_references (work_id, from_book, from_chapter, from_verse, "
        "to_book, to_chapter, to_verse_start, to_verse_end, votes) VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    print(f"web cross_references: loaded {len(rows)} rows"
          + (f" (skipped: {dict(skipped)})" if skipped else ""))


# unfoldingWord's USFM marks every word with lemma, Strong's and morphology, and ULT additionally
# wraps its English in \zaln-s frames naming the original word being rendered. Four repos, three
# shapes: UHB/UGNT are tagged originals, ULT is a tagged translation carrying alignment, UHG is
# reStructuredText prose.
_UW_WORD = re.compile(r'\\w\s+([^|\\]+)\|([^\\]*)\\w\*')
_UW_ZALN_OPEN = re.compile(r'\\zaln-s\s*\|([^\\]*?)\\\*')
_UW_ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def _uw_books(repo: Path):
    """(osis_book, usfm_text) for each book file, in canonical order."""
    for path in sorted(repo.glob("*.usfm")):
        match = re.search(r"\\id\s+(\S+)", path.read_text(encoding="utf-8", errors="replace")[:400])
        if match is None:
            continue
        osis = MACULA_USFM_TO_OSIS.get(match.group(1))
        if osis is not None:
            yield osis, path.read_text(encoding="utf-8", errors="replace")


def _uw_verses(usfm: str):
    r"""(chapter, verse, body) for each verse. USFM puts \c before its verses, so split on it."""
    for chunk in re.split(r"\\c\s+(\d+)", usfm)[1:]:
        if chunk.strip().isdigit() and len(chunk.strip()) < 4:
            chapter = int(chunk.strip())
            continue
        for m in re.finditer(r"\\v\s+(\d+)(.*?)(?=\\v\s+\d+|\Z)", chunk, re.S):
            yield chapter, int(m.group(1)), m.group(2)


# A footnote is \f, an optional caller (+), then marker-tagged content, closed by \f*. The content
# markers (\ft free text, \fq a quotation of the translated text, \fqa an alternative rendering)
# read as continuous prose once stripped, so they are dropped rather than preserved -- "\fq your
# cloak \ft or perhaps \fqa your clothes \ft (Hebrew Qere)" becomes exactly the sentence a reader
# wants. Original-language words inside a note carry the same \w markup as the running text and are
# reduced to the word itself; keeping their lemma/Strong's attributes would bury a one-word Qere
# reading in eighty characters of tagging.
_UW_FOOTNOTE = re.compile(r"\\f\s+\+?\s*(.*?)\\f\*", re.S)
_UW_FOOTNOTE_WORD = re.compile(r"\\\+?w\s+([^|\\]+)\|[^\\]*\\\+?w\*")
_UW_FOOTNOTE_MARKER = re.compile(r"\\[+a-z]+\*?")


def _alt_ref_row(work_id: str, book: str, chapter: int, verse: int,
                 alt: tuple[int | None, int]) -> tuple:
    r"""One versification_map row, resolving the chapter when \va did not state it.

    A bare \va gives the verse only, so the chapter comes from the scheme map -- which is exactly
    the part that is sometimes wrong (English Jonah 1:17 is Hebrew 2:1; align() leaves it at 1:17).
    The label set here is provisional -- _resolve_alt_chapters() then checks the chapter against the
    WLC text and upgrades it to 'verse+verified' or downgrades it to 'verse+unverified', so a caller
    is never left trusting an unchecked chapter as much as a stated one.
    """
    alt_chapter, alt_verse = alt
    if alt_chapter is not None:
        return (work_id, book, chapter, verse, "masoretic", alt_chapter, alt_verse, "explicit")
    ref = versification.align(book, chapter, max(verse, 1), "english", "masoretic")
    resolved_chapter = ref[1] if ref is not None else chapter
    return (work_id, book, chapter, verse, "masoretic", resolved_chapter, alt_verse, "verse+provisional")


def _hebrew_letters(text: str) -> str:
    """Consonants only -- vowels, cantillation, maqqef and morpheme separators all dropped.

    The two editions disagree about where a word divides (WLC writes a maqqef, UHB a word joiner),
    so any comparison that keeps word boundaries reports differences that are not there.
    """
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^\u05d0-\u05ea]", "", stripped)


def _resolve_alt_chapters(conn: sqlite3.Connection, work_id: str, rows: list) -> list:
    r"""Fix the chapter on every `verse+scheme` row by checking which one the WLC actually agrees with.

    \va states the verse but often not the chapter, and the scheme map is exactly what is unreliable
    at a chapter boundary -- it leaves English Jonah 1:17 at Hebrew 1:17 when the answer is 2:1, and
    English Job 41:2 at 41:26 when it is 40:26. Both are recoverable without guessing: morphhb-wlc is
    already ingested, so the candidate chapters can be tested against the text itself and the one
    that matches kept -- marked 'verse+verified'. A row that matches nothing keeps its inferred
    chapter and is marked 'verse+unverified' so a caller knows not to lean on it.
    """
    wlc = {}
    for book, chap, vs, text in conn.execute(
            "SELECT book, chapter, verse, text FROM verses WHERE work_id='morphhb-wlc'"):
        wlc[(book, chap, vs)] = _hebrew_letters(text)
    source_text = {}
    for book, chap, vs, text in conn.execute(
            "SELECT book, chapter, verse, text FROM verses WHERE work_id=?", (work_id,)):
        source_text[(book, chap, vs)] = _hebrew_letters(text)

    resolved = []
    for row in rows:
        wid, book, chapter, verse, scheme, alt_chapter, alt_verse, origin = row
        if origin == "explicit":
            resolved.append(row)
            continue
        mine = source_text.get((book, chapter, verse))
        if not mine:
            resolved.append(row)
            continue
        best, best_ratio = None, 0.0
        for candidate in (alt_chapter, chapter, chapter - 1, chapter + 1):
            theirs = wlc.get((book, candidate, alt_verse))
            if not theirs:
                continue
            ratio = difflib.SequenceMatcher(None, mine, theirs).ratio()
            if ratio > best_ratio:
                best, best_ratio = candidate, ratio
        if best is not None and best_ratio >= 0.9:
            resolved.append((wid, book, chapter, verse, scheme, best, alt_verse, "verse+verified"))
        else:
            resolved.append((wid, book, chapter, verse, scheme, alt_chapter, alt_verse,
                             "verse+unverified"))
    return resolved


def _uw_superscriptions(usfm: str):
    r"""(chapter, body) for each \d superscription block -- the psalm titles.

    UHB numbers verses the ULT's way, so where Hebrew counts a superscription as verse 1 and English
    does not, the title cannot be a \v at all: it sits in a \d block before the first verse, with its
    Hebrew number preserved alongside in \va. 64 psalms are built that way, and _uw_verses -- which
    splits on \v -- cannot see any of them. Their footnotes are Qere readings on names in the titles
    (Jeduthun at Psalms 39 and 77), so they are attributed to verse 1, the nearest reference an
    English-numbered reader can look up.
    """
    for chunk in re.split(r"\\c\s+(\d+)", usfm)[1:]:
        if chunk.strip().isdigit() and len(chunk.strip()) < 4:
            chapter = int(chunk.strip())
            continue
        head = re.split(r"\\v\s+\d+", chunk, maxsplit=1)[0]
        for m in re.finditer(r"\\d\b(.*?)(?=\\[cpqsm]\w*\s*\n|\Z)", head, re.S):
            yield chapter, m.group(1)


_UW_VA = re.compile(r"\\va\s+([0-9]+(?::[0-9]+)?)\s*\\va\*")


def _uw_alt_verse(body: str):
    r"""The Hebrew verse number this verse carries in \va, as (chapter_or_None, verse).

    UHB is numbered the ULT's way and records the Masoretic number alongside. It is inconsistent
    about the chapter: 131 markers give it outright ("32:1"), but Daniel 5:31 and Jonah 1:17 record
    a bare "1" where the Hebrew chapter also rolls over. So the chapter is returned only when the
    source actually stated it, and the caller falls back to the scheme map otherwise.
    """
    m = _UW_VA.search(body)
    if m is None:
        return None
    raw = m.group(1)
    if ":" in raw:
        chapter, verse = raw.split(":", 1)
        return int(chapter), int(verse)
    return None, int(raw)


def _uw_footnotes(body: str):
    r"""(note_type, text) for each footnote in one verse body.

    UHB spends 930 of its 949 notes on a single job: it prints the Ketiv in the text and records the
    Qere here, flagged by a bare `Q`. That is the Masoretes' own "the consonants say X, read Y" --
    the reason UHB and morphhb-wlc disagree in 340 verses -- so it gets its own note_type rather
    than being filed under 'translator' with genuine translator prose. The one-letter flags are
    expanded because `Q` alone is opaque next to the reading it introduces.
    """
    for raw in _UW_FOOTNOTE.findall(body):
        text = _UW_FOOTNOTE_WORD.sub(r"\1", raw)
        text = _UW_FOOTNOTE_MARKER.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        note_type = "translator"
        if text == "Q" or text.startswith("Q "):
            note_type, text = "qere", "Qere: " + text[1:].strip()
        elif text == "K" or text.startswith("K "):
            note_type, text = "ketiv", "Ketiv: " + text[1:].strip()
        yield note_type, text


def ingest_unfoldingword_text(conn: sqlite3.Connection, repo_name: str, work_id: str, title: str,
                              language: str, url_slug: str) -> None:
    """UHB and UGNT: the tagged original-language texts, stored as verse text.

    Their per-word lemma/Strong's/morphology is deliberately NOT loaded into `morphology`. That
    table is filled from MACULA off the same WLC and SBLGNT, and a second opinion keyed to the same
    columns would silently double every count a word study makes. What these two are here for is
    the text itself -- UGNT is a witness this database otherwise lacks, and both are what ULT's
    alignment resolves against.
    """
    repo = OPEN_DATA / repo_name
    if not repo.is_dir():
        print(f"{work_id}: {repo} missing -- skipped")
        return
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (work_id, None, title, language, repo_name,
         f"https://git.door43.org/unfoldingWord/{url_slug}", submodule_commit(repo_name), TODAY,
         "Creative Commons: BY-SA 4.0", "open",
         f"unfoldingWord, https://www.unfoldingword.org/{url_slug.split('_')[-1]}"),
    )
    rows, note_rows, map_rows = [], [], []
    for osis, usfm in _uw_books(repo):
        for chapter, verse, body in _uw_verses(usfm):
            words = [w for w, _ in _UW_WORD.findall(body)]
            if words:
                rows.append((work_id, osis, chapter, verse, " ".join(words)))
            for note_type, text in _uw_footnotes(body):
                note_rows.append((work_id, osis, chapter, verse, note_type, text))
            alt = _uw_alt_verse(body)
            if alt is not None:
                map_rows.append(_alt_ref_row(work_id, osis, chapter, verse, alt))
        # A psalm title that is Hebrew verse 1 cannot be a \v in an English-numbered text, so 64 of
        # them sit in a \d block that _uw_verses cannot see -- their text was absent from `verses`
        # entirely. Stored as verse 0: it is the only number that cannot collide with a real verse,
        # and it keeps the title attached to its psalm instead of merged into verse 1, which would
        # silently fuse two Hebrew verses into one row.
        for chapter, head in _uw_superscriptions(usfm):
            words = [w for w, _ in _UW_WORD.findall(head)]
            if words:
                rows.append((work_id, osis, chapter, 0, " ".join(words)))
            for note_type, text in _uw_footnotes(head):
                note_rows.append((work_id, osis, chapter, 0, note_type, text))
            alt = _uw_alt_verse(head)
            if alt is not None:
                map_rows.append(_alt_ref_row(work_id, osis, chapter, 0, alt))
    conn.executemany("INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", rows)
    conn.executemany(
        "INSERT INTO notes (work_id, book, chapter, verse, note_type, text) VALUES (?,?,?,?,?,?)",
        note_rows)
    conn.executemany(
        "INSERT INTO versification_map (work_id, book, chapter, verse, alt_scheme, alt_chapter, "
        "alt_verse, source) VALUES (?,?,?,?,?,?,?,?)", _resolve_alt_chapters(conn, work_id, map_rows))
    conn.commit()
    print(f"{work_id}: {len(rows)} verses, {len(note_rows)} notes, "
          f"{len(map_rows)} versification rows")


def ingest_ult(conn: sqlite3.Connection) -> None:
    r"""ULT: the English text, and the alignment that is the reason for taking it.

    Parsed with a stack because \zaln frames nest -- Genesis 1:1 opens one for אֵת and another for
    הַשָּׁמַיִם before closing both around "the heavens". Every open frame collects the English words
    that appear while it is open, so a nested pair produces two rows sharing that English. See the
    schema comment on word_alignment for why that is the honest shape rather than a defect.
    """
    repo = OPEN_DATA / "uw-ult"
    if not repo.is_dir():
        print("uw-ult: missing -- skipped")
        return
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("uw-ult", "ULT", "unfoldingWord Literal Text", "eng", "uw-ult",
         "https://git.door43.org/unfoldingWord/en_ult", submodule_commit("uw-ult"), TODAY,
         "Creative Commons: BY-SA 4.0", "open", "unfoldingWord, https://www.unfoldingword.org/ult"),
    )
    verse_rows, align_rows, note_rows = [], [], []
    for osis, usfm in _uw_books(repo):
        for chapter, verse, body in _uw_verses(usfm):
            for note_type, text in _uw_footnotes(body):
                note_rows.append(("uw-ult", osis, chapter, verse, note_type, text))
            english_all, stack = [], []
            for token in re.finditer(r"\\zaln-s\s*\|([^\\]*?)\\\*|\\zaln-e\\\*|\\w\s+([^|\\]+)\|([^\\]*)\\w\*", body):
                if token.group(1) is not None:
                    stack.append((dict(_UW_ATTR.findall(token.group(1))), []))
                elif token.group(2) is not None:
                    english_all.append(token.group(2))
                    for _, collected in stack:
                        collected.append(token.group(2))
                elif stack:
                    attrs, collected = stack.pop()
                    if collected and attrs.get("x-content"):
                        align_rows.append((
                            "uw-ult", osis, chapter, verse, " ".join(collected),
                            attrs["x-content"], attrs.get("x-lemma"), attrs.get("x-strong"),
                            attrs.get("x-morph"),
                            int(attrs["x-occurrence"]) if attrs.get("x-occurrence", "").isdigit() else None,
                        ))
            if english_all:
                verse_rows.append(("uw-ult", osis, chapter, verse, " ".join(english_all)))
        for chapter, head in _uw_superscriptions(usfm):
            for note_type, text in _uw_footnotes(head):
                note_rows.append(("uw-ult", osis, chapter, 1, note_type, f"{text} (on the superscription)"))
    conn.executemany("INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows)
    conn.executemany(
        "INSERT INTO word_alignment (work_id, book, chapter, verse, english, content, lemma, "
        "strong, morph, occurrence) VALUES (?,?,?,?,?,?,?,?,?,?)", align_rows)
    conn.executemany(
        "INSERT INTO notes (work_id, book, chapter, verse, note_type, text) VALUES (?,?,?,?,?,?)",
        note_rows)
    conn.commit()
    print(f"uw-ult: {len(verse_rows)} verses, {len(align_rows)} alignment rows, "
          f"{len(note_rows)} notes")


def ingest_uhg(conn: sqlite3.Connection) -> None:
    """UHG: the Hebrew reference grammar, one row per article.

    Sphinx directives, cross-reference roles and include lines are stripped to leave prose --
    `:ref:`masculine<gender_masculine>`` becomes "masculine". The articles are the point, not the
    HTML build, so nothing here tries to resolve the includes.
    """
    content_dir = OPEN_DATA / "uw-uhg" / "content"
    if not content_dir.is_dir():
        print("uw-uhg: missing -- skipped")
        return
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("uw-uhg", None, "unfoldingWord Hebrew Grammar", "eng", "uw-uhg",
         "https://git.door43.org/unfoldingWord/en_uhg", submodule_commit("uw-uhg"), TODAY,
         "Creative Commons: BY-SA 4.0", "open", "unfoldingWord, https://www.unfoldingword.org/uhg"),
    )
    rows = []
    for path in sorted(content_dir.glob("*.rst")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        lines = [l for l in raw.splitlines()
                 if not l.startswith((":github_url:", ".. _", ".. include::", ".. toctree::"))]
        title = ""
        for i, line in enumerate(lines[:-1]):
            if line.strip() and set(lines[i + 1].strip()) in ({"="}, {"-"}) and lines[i + 1].strip():
                title = line.strip()
                break
        body = re.sub(r":ref:`([^<`]+)<[^>]+>`", r"\1", "\n".join(lines))
        body = re.sub(r":\w+:`([^`]+)`", r"\1", body)
        rows.append(("uw-uhg", path.stem, title or path.stem, body.strip()))
    conn.executemany(
        "INSERT INTO grammar_articles (work_id, slug, title, body) VALUES (?,?,?,?)", rows)
    conn.commit()
    print(f"uw-uhg: {len(rows)} grammar articles")


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
        current_ref, parts, after_prefix = None, [], False

        def flush():
            if current_ref and parts:
                verse_rows.append((*current_ref, "".join(parts).strip()))

        # SBLGNT's XML carries no explicit word separator: <suffix> holds trailing punctuation
        # and is empty between plain words, while an apparatus siglum sits in a <prefix> bound to
        # the word after it. So the space goes before each word (or its prefix) whenever the
        # preceding suffix didn't already supply one. Reconstructing it any other way runs the
        # words together -- this reproduces data/sblgnt/text/*.txt exactly for all 7939 verses.
        for elem in tree.getroot().iter():
            if elem.tag == "verse-number":
                flush()
                ref = elem.get("id")  # e.g. "John 1:1"
                _, cv = ref.rsplit(" ", 1)
                c, v = cv.split(":")
                current_ref = (work_id, book_code, int(c), int(v))
                parts, after_prefix = [], False
            elif current_ref is None:
                continue
            elif elem.tag in ("w", "prefix"):
                if not after_prefix and parts and not parts[-1][-1:].isspace():
                    parts.append(" ")
                parts.append((elem.text or "").lstrip() if elem.tag == "prefix" else (elem.text or ""))
                after_prefix = elem.tag == "prefix"
            elif elem.tag == "suffix":
                if elem.text:
                    parts.append(elem.text)
                after_prefix = False
        flush()

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows,
    )
    conn.commit()
    print(f"sblgnt: {len(verse_rows)} verses")


def macula_node_id(raw: str | None) -> str | None:
    """Normalize one MACULA xml:id to digits only.

    The corpus prefix ('n' for the Greek NT, 'o' for the Hebrew OT) is present on every xml:id but
    only on *Greek* pointers -- Hebrew subjref/participantref drop it. Stripping it on both sides is
    what lets a pointer join find anything; joined raw, every Hebrew coreference lookup returns zero
    rows and looks like missing data rather than a key mismatch.
    """
    if not raw:
        return None
    match = re.fullmatch(r"[a-z]?(\d+)", raw.strip())
    return match.group(1) if match else None


def macula_node_refs(raw: str | None) -> str | None:
    """Normalize a coreference pointer, which may name SEVERAL nodes, to a space-separated list.

    subjref/referent/participantref are multi-valued whenever the reference is compound -- a plural
    subject ('Paul and Timothy'), or a pronoun gathering up more than one antecedent. About 3.5k
    Greek and 15k Hebrew rows are like this, so treating the field as a single id silently discards
    every compound reference in the corpus and leaves exactly the plural subjects an exegete is most
    likely to be asking about.
    """
    if not raw:
        return None
    ids = [node for node in (macula_node_id(tok) for tok in raw.split()) if node]
    return " ".join(ids) or None


MORPH_COLUMNS = (
    "work_id, book, chapter, verse, word_position, surface_form, strongs_id, morph_code, "
    "cantillation_level, lemma, gloss, domain_code, node_id, word_class, syntactic_role, "
    "sub_type, state, frame, subject_ref, referent"
)
MORPH_PLACEHOLDERS = ",".join("?" * 20)


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
                macula_node_id(row["xml:id"]), row["class"] or None, row["role"] or None,
                row["type"] or None, None, row["frame"] or None,
                macula_node_refs(row["subjref"]), macula_node_refs(row["referent"]),
            ))

    conn.executemany(
        f"INSERT INTO morphology ({MORPH_COLUMNS}) VALUES ({MORPH_PLACEHOLDERS})", morph_rows,
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
                macula_node_id(row["xml:id"]), row["class"] or None, None,
                row["type"] or None, row["state"] or None, row["frame"] or None,
                macula_node_refs(row["subjref"]), macula_node_refs(row["participantref"]),
            ))

    conn.executemany(
        f"INSERT INTO morphology ({MORPH_COLUMNS}) VALUES ({MORPH_PLACEHOLDERS})", morph_rows,
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


# BibleOrgSys's getVerseText documents that it "uses uncommon Unicode symbols to represent
# various formatted styles", and there is no flag to suppress them: cleanText already drops the
# notes but keeps these. Left in, they reached 47% of WEB verses and 24% of the Brenton LXX --
# "|A Psalm by David.|(1)Yahweh is my shepherd" -- polluting anything that quotes or tokenizes the
# text. Replaced with a space rather than deleted, since they sit between words.
# Deliberately NOT stripped: middle dot (Greek ano teleia, real punctuation) and Hebrew sof pasuq.
_BOS_STYLE_MARKERS = re.compile(r"[\u00b6\u00a6\u00a7\u2080-\u2089]+")


def _strip_bos_style_markers(text: str) -> str:
    return re.sub(r"\s+", " ", _BOS_STYLE_MARKERS.sub(" ", text)).strip()


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

    # The Brenton LXX follows the Greek canon's own shape, which hides three protocanonical books
    # from a plain USFM-code lookup. Daniel ships as Greek Daniel (BibleOrgSys code DNG) rather
    # than DAN -- that's Theodotion, the form the New Testament generally quotes -- Esther ships as
    # Greek Esther (ESG), and Nehemiah has no file of its own at all, being the back half of
    # 2 Esdras inside EZR at chapters 11-23. All three were being dropped as "deuterocanonical",
    # which is what made this edition look as though it lacked them.
    #
    # Greek Esther costs nothing to align, because its six additions are carried on *lettered*
    # sub-verses (1:1b-1s, 3:13a-g, 4:17a-x, 5:1a-2b, 8:12a-u, 10:3a-k) exactly so the numeric
    # verses keep the Masoretic numbering. The verse loop below is integer-only, so the additions
    # are skipped and what lands is the shared narrative -- eight of its ten chapters then match
    # the WLC verse-for-verse. Storing the additions would need a schema change (verses.verse is
    # INTEGER); see references/README.md before making one.
    #
    # The one place that costs something is Esther 1:1. Addition A's opening carries a plain
    # numeric 1 (the rest of it is 1b-1r), so it would land on Esth 1:1 and collide there with
    # every other work, where that address is "in the days of Ahasuerus". The Greek of the
    # Masoretic 1:1 is on the lettered 1:1s, which the integer loop can't reach. Dropping the
    # collision just finishes the exclusion of Addition A that skipping the lettered verses
    # already starts: LXX Esther then begins at 1:2, and nothing is filed under a reference that
    # means something else.
    lxx_aliases = {"DNG": "Dan", "ESG": "Esth"} if ebible_id == "grcbrent" else {}
    skip_esther_addition_a = ebible_id == "grcbrent"
    split_2_esdras = ebible_id == "grcbrent"

    verse_rows = []
    for bos_code in bible.getBookList():
        usfm_code = BOS_CODE_TO_USFM.get(bos_code, bos_code)
        osis_book = MACULA_USFM_TO_OSIS.get(usfm_code) or lxx_aliases.get(usfm_code)
        if osis_book is None:
            continue  # front matter, glossary, deuterocanonical -- out of scope
        book_obj = bible.books[bos_code]
        for c in range(1, book_obj.getNumChapters() + 1):
            for v in range(1, book_obj.getNumVerses(c) + 1):
                try:
                    verse_text = bible.getVerseText(SimpleVerseKey(bos_code, c, v))
                except KeyError:
                    continue  # versification gaps -- expected for LXX/deuterocanonical editions
                if not verse_text:
                    continue
                verse_text = _strip_bos_style_markers(verse_text)
                if not verse_text:
                    continue
                book, chapter = osis_book, c
                if split_2_esdras and osis_book == "Ezra" and c > 10:
                    book, chapter = "Neh", c - 10
                if skip_esther_addition_a and book == "Esth" and (chapter, v) == (1, 1):
                    continue
                verse_rows.append((work_id, book, chapter, v, verse_text))

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows,
    )
    conn.commit()
    print(f"ebible-{ebible_id}: {len(verse_rows)} verses")


def set_versification(conn: sqlite3.Connection) -> None:
    """Stamp each work with the scheme its (book, chapter, verse) references belong to.

    Done as one pass at the end rather than threaded through eight separate works INSERTs, so the
    classification lives in one readable place -- versification.scheme_for_work -- instead of
    being scattered across every ingest function.
    """
    rows = conn.execute("SELECT work_id FROM works").fetchall()
    conn.executemany(
        "UPDATE works SET versification=? WHERE work_id=?",
        [(scheme_for_work(work_id), work_id) for (work_id,) in rows],
    )
    conn.commit()
    counts = dict(conn.execute("SELECT versification, COUNT(*) FROM works GROUP BY versification"))
    print(f"versification: {counts}")



# Abegg's book codes are OSIS apart from these two, which between them carry a third of the
# biblical words in the corpus. Anything else that isn't already an OSIS code is a scroll
# designation used where the editors could not assign a canonical book -- unidentified fragments,
# skipped rather than guessed at.
DSS_BOOK_ALIASES = {"Is": "Isa", "Ex": "Exod"}


def ingest_dss(conn: sqlite3.Connection) -> None:
    """Biblical Dead Sea Scrolls from ETCBC's Text-Fabric edition of Martin Abegg's data.

    One work per scroll, because a scroll IS a witness: Isaiah 53:5 is attested by both 1Qisaa and
    1Q8 and they do not read alike (1Qisaa's fuller orthography has WHW>H where 1Q8 has WHW>), so
    collapsing them would destroy the only thing this corpus is for. 265 scrolls carry biblical
    references, giving ~13.4k scroll/book/chapter/verse rows.

    verses.text keeps the `full` transcription, brackets and all, because 31.8% of the biblical
    words carry an editorial mark -- [ ] for reconstruction, # and ? for damaged or uncertain
    letters. A scroll reading that differs from the Masoretic while sitting inside brackets is an
    editor's reconstruction, not manuscript evidence, and stripping that distinction would make
    the corpus quietly misleading for exactly the textual-critical work it exists to support.
    morphology.surface_form carries the clean `glyph` form for tokenizing and lemma queries.

    Licensed CC BY-NC 4.0 (stated in the data's own feature metadata, not just the repo README),
    so every row lands in the restricted-nc tier -- cite it, don't reproduce it wholesale.
    """
    from tf.fabric import Fabric

    tf_dir = RESTRICTED_DATA / "dss" / "tf" / "2.0"
    if not tf_dir.is_dir():
        print("dss: submodule not checked out, skipping")
        return
    commit = submodule_commit_at("references/restricted-data/dss")
    api = Fabric(locations=str(tf_dir), silent="deep").loadAll(silent="deep")
    F, L = api.F, api.L

    osis_codes = set(NUM_TO_OSIS.values())
    grouped: dict[tuple[str, str, int, int], list[int]] = {}
    for w in F.otype.s("word"):
        book, chapter, verse = F.book.v(w), F.chapter.v(w), F.verse.v(w)
        if not (book and chapter and verse):
            continue
        book = DSS_BOOK_ALIASES.get(book, book)
        if book not in osis_codes:
            continue  # a scroll designation, not a canonical book
        scroll_nodes = L.u(w, otype="scroll")
        if not scroll_nodes:
            continue
        try:
            key = (F.scroll.v(scroll_nodes[0]), book, int(chapter), int(verse))
        except ValueError:
            continue  # a non-numeric chapter/verse label
        grouped.setdefault(key, []).append(w)

    scrolls = sorted({k[0] for k in grouped})
    conn.executemany(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [(f"dss-{s}", s, f"Dead Sea Scrolls: {s}", "hbo", "dss",
          "https://github.com/ding0t/dss", commit, TODAY,
          "Creative Commons: BY-NC 4.0", "restricted-nc",
          "Martin G. Abegg Jr., James E. Bowley and Edward M. Cook; Text-Fabric conversion by "
          "Jarod Jacobs, Martijn Naaijer and Dirk Roorda",
          "One work per scroll -- each is a separate manuscript witness and they disagree. Verse "
          "text is the `full` transcription including editorial marks: [ ] reconstruction, # and ? "
          "damaged or uncertain. Check those before resting an argument on a variant reading.")
         for s in scrolls],
    )

    verse_rows, morph_rows = [], []
    for (scroll, book, chapter, verse), words in grouped.items():
        work_id = f"dss-{scroll}"
        text = "".join((F.full.v(w) or "") + (F.after.v(w) or "") for w in words).strip()
        if text:
            verse_rows.append((work_id, book, chapter, verse, text))
        for position, w in enumerate(words, start=1):
            # rec/unc sit on SIGN nodes, one level below the word -- a word is only evidence when
            # none of its letters is a modern editor's reconstruction or a doubtful reading
            extant = 0 if any(F.rec.v(s) or F.unc.v(s) for s in L.d(w, otype="sign")) else 1
            morph_rows.append((work_id, book, chapter, verse, position,
                               F.glyph.v(w), F.lex.v(w), F.sp.v(w), extant))

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)", verse_rows)
    conn.executemany(
        "INSERT INTO morphology (work_id, book, chapter, verse, word_position, surface_form, "
        "lemma, word_class, extant) VALUES (?,?,?,?,?,?,?,?,?)", morph_rows)
    conn.commit()
    whole = sum(1 for r in morph_rows if r[8])
    print(f"dss: {len(scrolls)} scrolls, {len(verse_rows)} verses, {len(morph_rows)} words, "
          f"{whole} fully extant ({100*whole//len(morph_rows)}%)")



def chapter_lengths(conn: sqlite3.Connection, work_id: str, book: str, chapter: int) -> int:
    return conn.execute("SELECT COUNT(*) FROM verses WHERE work_id=? AND book=? AND chapter=?",
                        (work_id, book, chapter)).fetchone()[0]



# The Open Scriptures lemma files use their own book codes; only this one needs mapping, and the
# choice matters: Theodotion's Daniel is the form the church received and the one Brenton carries.
LXX_LEMMA_BOOKS = {"DanTh": "Dan"}


def ingest_lxx_lemmas(conn: sqlite3.Connection) -> None:
    """Lemmatise the Septuagint from the Open Scriptures Septuagint Project's lemma files.

    The gap this closes: we had the Septuagint's text but not its lemmas, which blocked every
    lemma-level question about the Old Testament in the language the New Testament authors read it
    in. CCAT's morphological database is restrictively licensed and is why our own GreekResources
    fork ships without it -- but these lemma files are a separate work, CC BY 4.0, carrying only a
    key and a lemma per word and none of CCAT's text. They were sitting in open-data/ unused.

    Stored as morphology rather than verses: there is no surface form here, and the word ORDER is
    CCAT/Rahlfs's, not Brenton's. Those two editions agree on word count in only 73% of verses and
    on position in 47%, so word_position indexes this source's own sequence and must not be joined
    positionally to `ebible-grcbrent`. Verse-level lemma SETS are what this is for.
    """
    lemma_dir = OPEN_DATA / "greek-resources" / "LxxLemmas"
    if not lemma_dir.is_dir():
        print("lxx-lemmas: greek-resources submodule not checked out, skipping")
        return
    conn.execute(
        "INSERT INTO works (work_id, translation_code, title, language, source_id, source_repo_url, "
        "source_commit, ingested_at, license, license_tier, attribution, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("lxx-lemmas", None, "Septuagint lemmas (Open Scriptures Septuagint Project)", "grc",
         "greek-resources", "https://github.com/ding0t/GreekResources",
         submodule_commit("greek-resources"), TODAY,
         "Creative Commons: BY 4.0", "open", "Open Scriptures Septuagint Project",
         "Lemmas only -- no surface form, no morphology code, none of CCAT's restricted text. Word "
         "order follows CCAT/Rahlfs, NOT Brenton: do not join positionally to ebible-grcbrent. "
         "Covers the deuterocanon too, so allusions to Wisdom and Sirach are visible here."),
    )
    # The same fork carries a Greek Word List indexing New Testament AND Septuagint vocabulary,
    # which covers 100% of the lemmas here and carries a Strong's number for 93% of the tokens.
    # Worth taking: the Septuagint had no Strong's tagging at all, so a concordance could not follow
    # a Greek word across the testaments -- and the Septuagint is the Old Testament as the New
    # Testament's authors read it.
    word_list = {}
    gwl_path = OPEN_DATA / "greek-resources" / "GreekWordList.js"
    if gwl_path.is_file():
        match = re.search(r"\{.*\}", gwl_path.read_text(encoding="utf-8-sig"), re.DOTALL)
        if match:
            for key, entry in json.loads(match.group(0)).items():
                normalised = quotations.normalise_greek(key)
                if normalised:
                    word_list[normalised[0]] = entry

    rows = []
    for path in sorted(lemma_dir.glob("*.js")):
        book = LXX_LEMMA_BOOKS.get(path.stem, path.stem)
        for ref, words in json.loads(path.read_text(encoding="utf-8")).items():
            parts = ref.split(".")
            if len(parts) != 3:
                continue
            try:
                chapter, verse = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            for position, word in enumerate(words, start=1):
                normalised = quotations.normalise_greek(word.get("key") or "")
                if normalised:
                    entry = word_list.get(normalised[0], {})
                    strongs = entry.get("strong")
                    rows.append(("lxx-lemmas", book, chapter, verse, position, normalised[0],
                                 word.get("lemma"),
                                 str(strongs).lstrip("GH") if strongs else None,
                                 entry.get("pos")))
    conn.executemany(
        "INSERT INTO morphology (work_id, book, chapter, verse, word_position, lemma, gloss, "
        "strongs_id, word_class) VALUES (?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    books = len({r[1] for r in rows})
    tagged = sum(1 for r in rows if r[7])
    print(f"lxx-lemmas: {books} books, {len(rows)} lemmatised words, "
          f"{tagged} with a Strong's number ({100*tagged//len(rows)}%)")



def derive_dss_variants(conn: sqlite3.Connection) -> None:
    """Where a scroll reads something the Masoretic does not.

    Compared at LEMMA level, and that choice is the whole difference between signal and noise. On
    surface forms 99% of comparable verses "differ" -- 1QIsaa's fuller spelling and the scrolls'
    habit of writing a prefix as its own word swamp everything. At lemma level both vanish and the
    figure falls to 28%, leaving readings: Isaiah 2:20's moles, where the scroll has one word where
    the Masoretic has two.

    Only fully-extant scroll words count. 46% of signs in this corpus are a modern editor's
    reconstruction, so a differing word that isn't extant is a hole in the leather, not a variant.
    But how much of the SURROUNDING verse survives is recorded rather than filtered on: an earlier
    cut at five surviving words discarded Deuteronomy 32:8 in 4Q37, the best-known variant here,
    where only four survive and "sons of God" is among them, whole.

    One direction only: a lemma the scroll has and the Masoretic lacks is a reading; a lemma the
    Masoretic has and the scroll lacks is almost always damage, and recording it would manufacture
    omissions out of gaps.
    """
    masoretic: dict[tuple, set[str]] = {}
    for book, chapter, verse, lemma in conn.execute(
            "SELECT book, chapter, verse, lemma FROM morphology WHERE work_id='macula-hebrew-wlc' "
            "AND lemma IS NOT NULL AND lemma != ''"):
        key = quotations.normalise_hebrew(lemma)
        if key:
            masoretic.setdefault((book, chapter, verse), set()).add(key[0])

    scrolls: dict[tuple, list[str]] = {}
    for work_id, book, chapter, verse, lemma in conn.execute(
            "SELECT work_id, book, chapter, verse, lemma FROM morphology "
            "WHERE work_id LIKE 'dss-%' AND extant = 1 AND lemma IS NOT NULL AND lemma != ''"):
        key = quotations.normalise_hebrew(lemma)
        # single-letter lemmas are the article, the conjunction and the prepositions -- artefacts of
        # how each source tokenizes a prefix, never a variant reading
        if key and len(key[0]) > 1:
            scrolls.setdefault((work_id, book, chapter, verse), []).append(key[0])

    rows = []
    for (work_id, book, chapter, verse), lemmas in sorted(scrolls.items()):
        if len(lemmas) < 2:
            continue        # nothing to compare against; see the schema note on why this is 2
        against = masoretic.get((book, chapter, verse))
        if not against:
            continue
        for lemma in sorted(set(lemmas) - against):
            rows.append((work_id, book, chapter, verse, lemma, len(lemmas)))
    conn.executemany(
        "INSERT INTO dss_variants (work_id, book, chapter, verse, lemma, extant_words) "
        "VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    verses = len({(r[1], r[2], r[3]) for r in rows})
    print(f"dss variants: {len(rows)} readings across {verses} verses, "
          f"{len({r[0] for r in rows})} scrolls")


def derive_scripture_links(conn: sqlite3.Connection) -> None:
    """Compute the three typed link classes. Runs last -- it reads `verses` for four works and
    `cross_references` for corroboration.

    Corroboration is a second opinion from a source with no connection to the method: openbible's
    cross-references are crowd-assembled and English-scheme, so where they name the same passage,
    two unrelated lines of evidence agree. Recorded per row rather than used as a filter -- a strong
    verbatim run that openbible does NOT carry is a link a cross-reference list missed, which is the
    point of deriving these at all.
    """
    fetch = "SELECT book, chapter, verse, text FROM verses WHERE work_id=? ORDER BY book, chapter, verse"
    nt_books = {r[0] for r in conn.execute(
        "SELECT DISTINCT book FROM verses WHERE work_id='sblgnt'")}
    rows: list[tuple] = []

    def english_ref(book, chapter, verse, scheme, source_work):
        aligned = versification.align(book, chapter, verse, scheme, "english")
        if aligned is None:
            return None
        # the chapter comes from the scheme, the verse has to be measured -- otherwise Hebrews
        # 10:5's source records as English Psalm 40:7 when the verse it quotes is 40:6
        offset = versification.superscription_offset(
            chapter_lengths(conn, source_work, book, chapter),
            chapter_lengths(conn, "ebible-eng-web", aligned[0], aligned[1]))
        shifted = aligned[2] - offset
        # A title shift that lands below verse 1 was never a title: the two chapters differ for
        # some other reason, and shifting the front is the wrong correction. Hosea is now mapped
        # explicitly above, but the guard stays -- it is what turned that bug into a visible
        # impossible reference (English Hosea 2:-1) rather than a plausible wrong one.
        if shifted < 1:
            return (aligned[0], aligned[1], aligned[2])
        return (aligned[0], aligned[1], shifted)

    def record(link_type, from_work, to_work, pair, to_scheme):
        fb, fc, fv = pair["from"]
        tb, tc, tv = pair["to"]
        english = english_ref(tb, tc, tv, to_scheme, to_work)
        corroborated = 0
        if english is not None:
            corroborated = 1 if conn.execute(
                "SELECT 1 FROM cross_references WHERE from_book=? AND from_chapter=? AND from_verse=? "
                "AND to_book=? AND to_chapter=? AND ABS(to_verse_start - ?) <= 2 LIMIT 1",
                (fb, fc, fv, english[0], english[1], english[2])).fetchone() else 0
        rows.append((link_type, from_work, fb, fc, fv, to_work, tb, tc, tv, pair["shared_ngrams"],
                     pair["containment"], pair["longest_run"], pair["alignment"],
                     pair["idf_overlap"], corroborated,
                     english[1] if english else None, english[2] if english else None))

    # 1. the Greek class -- the New Testament quoting the Septuagint, in one language
    lxx_tokens, lxx_index = quotations.build_index(conn.execute(fetch, ("ebible-grcbrent",)).fetchall())
    for pair in quotations.find_quotations(conn.execute(fetch, ("sblgnt",)).fetchall(),
                                            lxx_tokens, lxx_index):
        record("quotation-greek", "sblgnt", "ebible-grcbrent", pair, "lxx")

    # 2. inner-biblical -- the Hebrew Old Testament quoting itself. Trigrams, because Hebrew packs
    # more into a word than Greek does; a higher shared-gram floor to compensate.
    wlc = [r for r in conn.execute(fetch, ("morphhb-wlc",)).fetchall() if r[0] not in nt_books]
    heb_tokens, heb_index = quotations.build_index(wlc, quotations.normalise_hebrew, n=3)

    def same_context(source, target):
        """A verse resembling its own neighbours is continuous prose, not a citation."""
        return source[0] == target[0] and abs(source[1] - target[1]) <= 1

    seen: set[tuple] = set()
    for pair in quotations.find_quotations(wlc, heb_tokens, heb_index, quotations.normalise_hebrew,
                                            n=3, min_shared=4, exclude=same_context):
        if pair["alignment"] < quotations.QUOTATION_ALIGNMENT:
            continue
        key = tuple(sorted([pair["from"], pair["to"]]))   # the relation is symmetric; store it once
        if key in seen:
            continue
        seen.add(key)
        record("inner-biblical", "morphhb-wlc", "morphhb-wlc", pair, "masoretic")

    # 3. the Hebrew New Testament -- candidates only, see the schema comment
    hebrew_nt = [r for r in conn.execute(fetch, ("ebible-heb",)).fetchall() if r[0] in nt_books]
    for pair in quotations.find_quotations(hebrew_nt, heb_tokens, heb_index,
                                            quotations.normalise_hebrew, n=3, min_shared=3):
        if pair["alignment"] >= quotations.QUOTATION_ALIGNMENT:
            record("quotation-hebrew", "ebible-heb", "morphhb-wlc", pair, "masoretic")

    # 4. rare-lemma allusion -- the Septuagint against the Greek New Testament, both lemmatised.
    # Same language and a shared lemma inventory (96% of NT tokens have a lemma the LXX also uses),
    # so this needs no bridge: where two passages share several lemmas that are rare across the
    # whole corpus, that is evidence even with no shared phrasing. It reaches what quotation
    # matching cannot -- Revelation 21:20's jewels against Ezekiel 28:13, and, because the lemma
    # files cover the deuterocanon, Paul at the Areopagus against Wisdom 13:10.
    lemma_verses: dict[tuple, set[str]] = {}
    for work, table_rows in (("lxx-lemmas", conn.execute(
            "SELECT book, chapter, verse, lemma FROM morphology WHERE work_id='lxx-lemmas'")),
            ("macula-greek-sblgnt", conn.execute(
            "SELECT book, chapter, verse, lemma FROM morphology WHERE work_id='macula-greek-sblgnt' "
            "AND lemma IS NOT NULL AND lemma != ''"))):
        for book, chapter, verse, lemma in table_rows:
            normalised = quotations.normalise_greek(lemma or "")
            if normalised:
                lemma_verses.setdefault((work, book, chapter, verse), set()).add(normalised[0])

    frequency: collections.Counter = collections.Counter()
    for lemmas in lemma_verses.values():
        frequency.update(lemmas)
    vocabulary = len(frequency)
    rare_index: dict[str, list] = {}
    for (work, book, chapter, verse), lemmas in lemma_verses.items():
        if work != "lxx-lemmas":
            continue
        for lemma in lemmas:
            if frequency[lemma] <= quotations.RARE_LEMMA_VERSES:
                rare_index.setdefault(lemma, []).append((book, chapter, verse))

    for (work, book, chapter, verse), lemmas in sorted(lemma_verses.items()):
        if work != "macula-greek-sblgnt":
            continue
        rare = {l for l in lemmas if frequency[l] <= quotations.RARE_LEMMA_VERSES}
        if len(rare) < 2:
            continue
        hits: collections.Counter = collections.Counter()
        for lemma in rare:
            for target in rare_index.get(lemma, ()):
                hits[target] += 1
        for target, count in sorted(hits.items()):
            if count < 2:
                continue
            shared = rare & lemma_verses[("lxx-lemmas", *target)]
            weight = sum(math.log(vocabulary / frequency[l]) for l in shared)
            if weight < quotations.ALLUSION_WEIGHT:
                continue
            record("allusion-lemma", "macula-greek-sblgnt", "lxx-lemmas",
                   {"from": (book, chapter, verse), "to": target, "shared_ngrams": len(shared),
                    "containment": round(len(shared) / len(rare), 4), "longest_run": 0,
                    "alignment": 0, "idf_overlap": round(weight, 3)}, "lxx")

    conn.executemany(
        "INSERT INTO scripture_links (link_type, from_work, from_book, from_chapter, from_verse, "
        "to_work, to_book, to_chapter, to_verse, shared_ngrams, containment, longest_run, "
        "alignment, idf_overlap, corroborated, to_english_chapter, to_english_verse) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows)
    conn.commit()
    for link_type, in conn.execute("SELECT DISTINCT link_type FROM scripture_links"):
        # allusion is scored on rarity, not alignment -- reporting it against the wrong measure
        # would say "0 strong" about a class where every stored row already cleared its threshold
        column, floor = (("idf_overlap", quotations.ALLUSION_WEIGHT)
                         if link_type == "allusion-lemma"
                         else ("alignment", quotations.QUOTATION_ALIGNMENT))
        total, strong, agreed = conn.execute(
            f"SELECT COUNT(*), SUM({column} >= ?), SUM({column} >= ? AND corroborated) "
            "FROM scripture_links WHERE link_type=?", (floor, floor, link_type)).fetchone()
        print(f"links {link_type:18} {total:6} pairs, {strong or 0:5} at {column}>={floor} "
              f"({agreed or 0} corroborated)")


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
    ingest_web_crossrefs(conn)   # after ingest_ebible: reads the USFM that call caches
    ingest_ebible(conn, "grcbrent", "Brenton-LXX", "Brenton Septuagint (Greek)", "grc")
    ingest_ebible(conn, "grc-tisch", "Tischendorf", "Tischendorf 8th ed. Greek New Testament", "grc")
    ingest_ebible(conn, "heb", "Delitzsch", "Delitzsch Hebrew Bible (OT+NT)", "heb")
    # A second, independent Hebrew rendering of the Greek NT. Salkinson (1885) and Ginsburg's
    # revision (1886) confined themselves to vocabulary attested in the Tanakh, where Delitzsch
    # wrote a more Mishnaic register -- so the pair shows two different answers to the same
    # question, which is the whole reason for holding both. Like Delitzsch it is a 19th-century
    # translation FROM the Greek, not a witness to any Hebrew original.
    ingest_ebible(conn, "hebsg", "Salkinson", "Salkinson-Ginsburg Hebrew New Testament", "heb")
    ingest_unfoldingword_text(conn, "uw-uhb", "uw-uhb", "unfoldingWord Hebrew Bible", "hbo", "hbo_uhb")
    ingest_unfoldingword_text(conn, "uw-ugnt", "uw-ugnt", "unfoldingWord Greek New Testament", "grc", "el-x-koine_ugnt")
    ingest_ult(conn)
    ingest_uhg(conn)
    ingest_dss(conn)
    ingest_lxx_lemmas(conn)
    set_versification(conn)
    derive_scripture_links(conn)
    derive_dss_variants(conn)
    conn.close()
    print(f"\nBuild complete: {DB_PATH}")


if __name__ == "__main__":
    main()
