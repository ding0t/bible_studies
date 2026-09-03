"""Biblical Dead Sea Scrolls (ETCBC/Abegg, CC BY-NC 4.0).

Fragmentary by nature, so the completeness test skips them: a scroll covers whatever survived.
What can be asserted is the shape of the corpus and the two things that make it worth holding --
that each scroll is kept as its own witness, and that reconstruction is still visible in the text.
"""
import sqlite3
import unicodedata
from pathlib import Path

import pytest

from book_map import NUM_TO_OSIS

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"
OT_BOOKS = {NUM_TO_OSIS[i] for i in range(1, 40)}


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


def consonants(text):
    """Vowel points off, and morpheme separators with them -- the WLC divides with '/' and the
    scrolls with the geresh, so a bare substring search misses כארי inside כ/ארי."""
    stripped = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    return stripped.replace("/", "").replace("\u05f3", "")


def test_corpus_is_present_and_restricted(conn):
    works = conn.execute(
        "SELECT work_id, license_tier, versification FROM works WHERE work_id LIKE 'dss-%'"
    ).fetchall()
    assert len(works) > 200
    # CC BY-NC: usable here, but never in the 'open' tier and never reproduced wholesale
    assert {w["license_tier"] for w in works} == {"restricted-nc"}
    # the editors assigned references against the Hebrew Bible, not an English one
    assert {w["versification"] for w in works} == {"masoretic"}


def test_only_canonical_books_were_admitted(conn):
    """Abegg uses a scroll designation in the book field where no canonical book could be assigned.
    Those are unidentified fragments and are skipped rather than guessed at."""
    books = {r["book"] for r in conn.execute("SELECT DISTINCT book FROM verses WHERE work_id LIKE 'dss-%'")}
    assert books <= OT_BOOKS
    assert len(books) == 36


def test_esther_nehemiah_and_chronicles_are_absent(conn):
    """Esther is famously unattested at Qumran. Asserted so that a future ingest change which
    silently invents coverage for it fails here rather than in a study."""
    books = {r["book"] for r in conn.execute("SELECT DISTINCT book FROM verses WHERE work_id LIKE 'dss-%'")}
    assert OT_BOOKS - books == {"Esth", "Neh", "1Chr"}


def test_each_scroll_is_kept_as_its_own_witness(conn):
    """Isaiah 53:5 survives in two scrolls and they do not read alike -- 1Qisaa has the fuller
    orthography. Collapsing the scrolls into one work would destroy the only thing this corpus is
    for, and the unique index would have silently dropped one of them."""
    rows = conn.execute(
        "SELECT work_id, text FROM verses WHERE work_id LIKE 'dss-%' AND book='Isa' "
        "AND chapter=53 AND verse=5"
    ).fetchall()
    assert len(rows) >= 2
    assert len({r["text"] for r in rows}) == len(rows), "witnesses collapsed to identical text"


def test_reconstruction_markers_survive_into_the_verse_text(conn):
    """31.8% of biblical words carry an editorial mark. A scroll reading that differs from the
    Masoretic while sitting inside brackets is an editor's reconstruction, not evidence, so the
    marks have to reach the reader."""
    marked = conn.execute(
        "SELECT COUNT(*) n FROM verses WHERE work_id LIKE 'dss-%' AND (text LIKE '%[%' OR text LIKE '%#%')"
    ).fetchone()["n"]
    assert marked > 1000


def test_deuteronomy_32_8_reads_sons_of_god(conn):
    """The reading the Septuagint and the New Testament follow, against the Masoretic 'sons of
    Israel'. 4Q37 is the scroll usually cited; before this corpus was ingested the claim could not
    be checked here at all."""
    row = conn.execute(
        "SELECT text FROM verses WHERE work_id='dss-4Q37' AND book='Deut' AND chapter=32 AND verse=8"
    ).fetchone()
    assert row and "אלוהים" in consonants(row["text"])
    mt = conn.execute(
        "SELECT text FROM verses WHERE work_id='morphhb-wlc' AND book='Deut' AND chapter=32 AND verse=8"
    ).fetchone()
    assert "ישראל" in consonants(mt["text"])


def test_psalm_22_reads_karu_not_kaari(conn):
    """One letter, waw against yod: the Nahal Hever psalms scroll has כארו where the Masoretic has
    כארי. The whole 'pierced' / 'like a lion' question turns on it."""
    row = conn.execute(
        "SELECT text FROM verses WHERE work_id='dss-5/6hev1b' AND book='Ps' AND chapter=22 AND verse=17"
    ).fetchone()
    assert row and "כארו" in consonants(row["text"])
    mt = conn.execute(
        "SELECT text FROM verses WHERE work_id='morphhb-wlc' AND book='Ps' AND chapter=22 AND verse=17"
    ).fetchone()
    assert "כארי" in consonants(mt["text"])
