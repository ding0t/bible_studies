"""Verse-text integrity checks for out/bible-text.db.

Guards the class of bug where an ingest reconstructs a verse from word-level markup and loses the
word separators. SBLGNT's XML has no explicit separator -- <suffix> carries trailing punctuation
and sits empty between plain words -- so joining <w>/<suffix> naively produced run-together text
("Ἐνἀρχῇἦνὁλόγος") in every one of its 7939 verses. It read as a display quirk but it silently
broke any string-level work against the Greek NT, which is exactly what OT-quotation matching
needs.

The strongest available oracle is the publisher's own plain-text edition shipped alongside the XML
in the same submodule, so the check is a direct comparison against it rather than a heuristic.
"""
import sqlite3
from pathlib import Path

import pytest

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"
SBLGNT_TEXT_DIR = (
    Path(__file__).parent.parent.parent
    / "open-data" / "sblgnt" / "data" / "sblgnt" / "text"
)


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(DB_PATH)
    yield connection
    connection.close()


def _published_text() -> dict[tuple[str, int, int], str]:
    """(book_code, chapter, verse) -> verse text, from data/sblgnt/text/*.txt."""
    published = {}
    for path in sorted(SBLGNT_TEXT_DIR.glob("*.txt")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if "\t" not in line:
                continue  # the book-title line
            ref, text = line.split("\t", 1)
            chapter, verse = ref.rsplit(" ", 1)[1].split(":")
            published[(path.stem, int(chapter), int(verse))] = text.strip()
    return published


def test_sblgnt_matches_publisher_text_edition(conn):
    if not SBLGNT_TEXT_DIR.exists():
        pytest.skip("sblgnt submodule not checked out")
    published = _published_text()
    assert len(published) == 7939, f"expected 7939 published verses, got {len(published)}"

    rows = conn.execute(
        "SELECT book, chapter, verse, text FROM verses WHERE work_id='sblgnt'"
    ).fetchall()
    assert len(rows) == len(published)

    mismatched = [
        f"{book} {chapter}:{verse}"
        for book, chapter, verse, text in rows
        if published.get((book, chapter, verse)) != text
    ]
    assert not mismatched, f"{len(mismatched)} verses differ from the SBLGNT text edition: {mismatched[:5]}"


@pytest.mark.parametrize("work_id", ["sblgnt", "ebible-grc-tisch", "scrollmapper-Byz", "ebible-grcbrent"])
def test_multi_word_verses_have_word_separators(conn, work_id):
    """A whole Greek work rendered without spaces is the run-together signature; a handful of
    genuinely single-word verses is not, so this fails on the ratio rather than on any one verse."""
    rows = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND length(text) > 40", (work_id,)
    ).fetchall()
    assert rows, f"no verses found for {work_id}"
    spaceless = sum(1 for (text,) in rows if " " not in text)
    assert spaceless == 0, f"{work_id}: {spaceless}/{len(rows)} long verses have no spaces"


def test_one_row_per_reference_per_work(conn):
    """(work_id, book, chapter, verse) must identify at most one row. A unique index enforces this
    now, but it was merely assumed for a long time and was not true: upstream scrollmapper ships
    each verse several times over (ASV: 217714 rows for 31102 references) with the copies differing
    in whitespace, so DISTINCT on the raw text kept two or three rows for 28674 references across
    38 works -- and lookup_verse's fetchone() returned whichever SQLite reached first.
    """
    duplicated = conn.execute(
        "SELECT work_id, book, chapter, verse, COUNT(*) n FROM verses "
        "GROUP BY work_id, book, chapter, verse HAVING n > 1 LIMIT 5"
    ).fetchall()
    assert not duplicated


def test_deduplication_keeps_the_copy_with_word_separators_intact(conn):
    """Where copies disagree beyond whitespace it is because one lost its word separators, so the
    wordiest copy is the intact one. ASV 1 Corinthians 2:9 had three copies, two of them damaged."""
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id='scrollmapper-ASV' AND book='1Cor' "
        "AND chapter=2 AND verse=9"
    ).fetchone()[0]
    assert "And which entered" in text, text


def test_psalm_119_is_not_inflated_by_its_acrostic_headings(conn):
    """The KJV carried 198 verses here against the true 176: the 22 Hebrew letter headings shared
    verse numbers with the verses they head, and both rows survived."""
    assert conn.execute(
        "SELECT COUNT(*) FROM verses WHERE work_id='scrollmapper-KJV' AND book='Ps' AND chapter=119"
    ).fetchone()[0] == 176


@pytest.mark.parametrize("work_id", ["ebible-eng-web", "ebible-grcbrent", "ebible-heb", "ebible-grc-tisch"])
def test_no_bibleorgsys_style_markers_leak_into_verse_text(conn, work_id):
    """getVerseText represents formatting with uncommon Unicode symbols and offers no flag to
    suppress them, so they reached 47% of WEB verses and 24% of the Brenton LXX until stripped at
    ingest. Greek ano teleia and Hebrew sof pasuq are real punctuation and must survive."""
    leaked = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE work_id=? AND (text LIKE '%¶%' OR text LIKE '%¦%' "
        "OR text LIKE '%§%' OR text LIKE '%₁%' OR text LIKE '%₂%')", (work_id,)
    ).fetchone()[0]
    assert leaked == 0


def test_real_punctuation_survives_marker_stripping(conn):
    greek = conn.execute("SELECT COUNT(*) FROM verses WHERE work_id='ebible-grcbrent' AND text LIKE '%·%'").fetchone()[0]
    hebrew = conn.execute("SELECT COUNT(*) FROM verses WHERE work_id='morphhb-wlc' AND text LIKE '%׃%'").fetchone()[0]
    assert greek > 1000 and hebrew > 10000


def test_two_independent_hebrew_new_testaments_are_genuinely_different(conn):
    """Delitzsch (1877) and Salkinson-Ginsburg (1885/86) are separate 19th-century translations of
    the Greek into Hebrew, and holding both is only worth anything if they differ. They do:
    Salkinson confined himself to vocabulary attested in the Tanakh and pointed his text, where
    Delitzsch wrote unpointed in a more Mishnaic register.

    Neither is a witness to a Hebrew original -- see references/README.md. This also guards against
    the pair silently collapsing into one text, which is exactly what ebible-heb and
    scrollmapper-HebModern turned out to be (31101 of 31102 verses identical).
    """
    pairs = conn.execute(
        "SELECT a.book, a.chapter, a.verse, a.text, b.text FROM verses a JOIN verses b "
        "ON a.book=b.book AND a.chapter=b.chapter AND a.verse=b.verse "
        "WHERE a.work_id='ebible-hebsg' AND b.work_id='ebible-heb'"
    ).fetchall()
    assert len(pairs) > 7000, "expected the two to overlap across the whole New Testament"
    identical = sum(1 for *_, a, b in pairs if a == b)
    assert identical == 0, f"{identical} verses identical -- are these really two translations?"


def test_salkinson_is_pointed_and_delitzsch_is_not(conn):
    """The visible difference, and a cheap check that the niqqud survived ingest intact."""
    niqqud = "ְ"  # sheva, the commonest vowel point
    sg = conn.execute("SELECT text FROM verses WHERE work_id='ebible-hebsg' AND book='John' "
                      "AND chapter=1 AND verse=1").fetchone()[0]
    de = conn.execute("SELECT text FROM verses WHERE work_id='ebible-heb' AND book='John' "
                      "AND chapter=1 AND verse=1").fetchone()[0]
    assert niqqud in sg and niqqud not in de
