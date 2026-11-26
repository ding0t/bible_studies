"""The Targums (Sefaria export; Aramaic public domain, English Public Domain or CC0 only).

A Targum is a witness to how the synagogue read a verse, so what matters is that the verse it
renders is the verse it is filed under, and that nothing of uncertain licence came in with it.
"""
import sqlite3
import unicodedata
from pathlib import Path

import pytest

import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


MESSIAH = "משיחא"   # consonants: the pointed text orders its marks differently from a typed word


def consonants(text):
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def _text(conn, work_id, book, chapter, verse):
    row = conn.execute("SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                       (work_id, book, chapter, verse)).fetchone()
    return consonants(row["text"]) if row else None


def test_only_open_files_were_admitted(conn):
    works = conn.execute("SELECT work_id, license, license_tier, versification FROM works "
                         "WHERE work_id LIKE 'targum-%'").fetchall()
    assert len(works) >= 8
    assert {w["license_tier"] for w in works} == {"open"}
    for w in works:
        assert set(w["license"].split(" + ")) <= {"Public Domain", "CC0"}, w["work_id"]


def test_targums_follow_the_hebrew_numbering(conn):
    """Micah's Bethlehem verse is Hebrew 5:1 (English 5:2), and the Targum has the Messiah there.
    Filed in English numbering it would sit one verse off, with no error."""
    assert {w["versification"] for w in conn.execute(
        "SELECT versification FROM works WHERE work_id LIKE 'targum-%'")} == {"masoretic"}
    assert MESSIAH in _text(conn, "targum-jonathan", "Mic", 5, 1)
    assert "בית לחם" in _text(conn, "targum-jonathan", "Mic", 5, 1)


def test_a_psalm_title_counts_as_a_verse(conn):
    """Psalm 22 has 32 verses in Hebrew and 31 in English; the Targum has the Hebrew's 32."""
    n = conn.execute("SELECT MAX(verse) m FROM verses WHERE work_id='targum-writings' AND book='Ps' "
                     "AND chapter=22").fetchone()["m"]
    assert n == 32


def test_the_lookup_reports_the_english_verse_a_targum_verse_renders(conn):
    """bible_verse reads a reference in the work's own numbering, as it does the WLC's, and says
    which English verse that is: the Targum's Micah 5:1 is English 5:2."""
    result = query.lookup_verse(conn, "Mic", 5, 1, "targum-jonathan")
    assert MESSIAH in consonants(result["text"])
    assert result["aligned_references"]["english"] == "Mic 5:2"


def test_isaiah_52_13_names_the_messiah_in_both_languages(conn):
    assert MESSIAH in _text(conn, "targum-jonathan", "Isa", 52, 13)
    assert "my servant the messiah" in _text(conn, "targum-jonathan-en", "Isa", 52, 13)


def test_footnotes_are_stripped(conn):
    """Sefaria's footnote markup goes; Etheridge's own <mymr'> (the Aramaic word, transliterated in
    angle brackets) is his text and stays."""
    leaked = conn.execute("SELECT COUNT(*) n FROM verses WHERE work_id LIKE 'targum-%' "
                          "AND (text LIKE '%<sup%' OR text LIKE '%<i %' OR text LIKE '%</%' "
                          "OR text LIKE '%footnote%')").fetchone()["n"]
    assert leaked == 0
