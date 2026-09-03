"""Brenton LXX book-mapping checks for out/bible-text.db.

The Greek canon's shape hides two protocanonical books from a plain USFM-code lookup, and both
were silently dropped for a while as "deuterocanonical", making the edition look as though it
lacked them:

  * Daniel ships as Greek Daniel (BibleOrgSys code DNG), not DAN. That text is Theodotion --
    identifiable at 1:3 by Ασφανεζ, where the Old Greek reads Αβιεσδρι -- which is the form the
    New Testament generally quotes, so it's the one worth having.
  * Nehemiah has no file at all: it is the back half of 2 Esdras, inside EZR at chapters 11-23.
    Ingesting EZR as-is therefore produced a 23-chapter "Ezra" and no Nehemiah.

These pin the mapping and the versification facts that depend on it. Greek Esther is deliberately
NOT mapped onto Esth -- see PARTIAL_COVERAGE in test_completeness.py.
"""
import sqlite3
import unicodedata
from pathlib import Path

import pytest

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"
LXX = "ebible-grcbrent"
WLC = "morphhb-wlc"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(DB_PATH)
    yield connection
    connection.close()


def chapter_lengths(conn, work_id, book):
    return dict(conn.execute(
        "SELECT chapter, COUNT(*) FROM verses WHERE work_id=? AND book=? GROUP BY chapter",
        (work_id, book),
    ).fetchall())


def test_greek_daniel_is_present_and_complete(conn):
    chapters = chapter_lengths(conn, LXX, "Dan")
    assert sorted(chapters) == list(range(1, 13))


def test_greek_daniel_is_theodotion_not_old_greek(conn):
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book='Dan' AND chapter=1 AND verse=3", (LXX,)
    ).fetchone()[0]
    assert "Ἀσφανὲζ" in text, "expected Theodotion's Ασφανεζ at Daniel 1:3"


def test_ezra_nehemiah_split_out_of_2_esdras(conn):
    assert sorted(chapter_lengths(conn, LXX, "Ezra")) == list(range(1, 11))
    assert sorted(chapter_lengths(conn, LXX, "Neh")) == list(range(1, 14))
    # 2 Esdras 11:1 is Nehemiah 1:1 -- the incipit naming Nehemiah is the check that the
    # split landed on the right chapter rather than merely producing 13 chapters.
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book='Neh' AND chapter=1 AND verse=1", (LXX,)
    ).fetchone()[0]
    assert "Νεεμία" in text


@pytest.mark.parametrize("chapter", [1, 2, 5, 6, 7, 8, 9, 10, 11, 12])
def test_daniel_versification_matches_masoretic_outside_chapters_three_and_four(conn, chapter):
    """Ten of Daniel's twelve chapters line up verse-for-verse with the WLC, which is what makes
    cross-work lookup safe there -- Daniel 9:24-27, the Seventy Weeks, in particular."""
    lxx, wlc = chapter_lengths(conn, LXX, "Dan"), chapter_lengths(conn, WLC, "Dan")
    assert lxx[chapter] == wlc[chapter]


def test_daniel_three_and_four_do_not_align_with_the_masoretic(conn):
    """The two exceptions, and they are one problem seen from both sides. Theodotion inserts the
    Prayer of Azariah and the Song of the Three after 3:23 (95 verses against the WLC's 33), and
    the chapter break then falls three verses later than the Masoretic one: Greek Daniel 4:1-3 is
    WLC Daniel 3:31-33, so Greek 4:n is WLC 4:n-3 from there on. Neither chapter may be compared
    verse-for-verse against a Masoretic work.
    """
    lxx, wlc = chapter_lengths(conn, LXX, "Dan"), chapter_lengths(conn, WLC, "Dan")
    assert lxx[3] > wlc[3] + 50
    assert lxx[4] == wlc[4] + 3

    # the shared incipit that fixes the offset: "Nebuchadnezzar the king, to all peoples".
    # Compared on consonants only -- the WLC carries niqqud and cantillation, so a literal
    # match against pointed text is brittle for no benefit here.
    greek = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book='Dan' AND chapter=4 AND verse=1", (LXX,)
    ).fetchone()[0]
    hebrew = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book='Dan' AND chapter=3 AND verse=31", (WLC,)
    ).fetchone()[0]
    consonants = "".join(c for c in hebrew if not unicodedata.combining(c))
    assert "Ναβουχοδονόσορ" in greek
    assert "נבוכדנצר" in consonants


ESTHER_ALIGNED_CHAPTERS = [1, 2, 3, 5, 6, 7, 8, 10]


@pytest.mark.parametrize("chapter", ESTHER_ALIGNED_CHAPTERS)
def test_greek_esther_keeps_masoretic_verse_numbering(conn, chapter):
    """Greek Esther's six additions ride on *lettered* sub-verses (1:1b-1s, 3:13a-g, 4:17a-x,
    5:1a-2b, 8:12a-u, 10:3a-k) precisely so the numeric verses keep the Hebrew numbering. Only the
    numeric ones are ingested, so eight of the ten chapters match the WLC exactly."""
    lxx, wlc = chapter_lengths(conn, LXX, "Esth"), chapter_lengths(conn, WLC, "Esth")
    expected = wlc[chapter] - (1 if chapter == 1 else 0)  # chapter 1 loses Addition A's verse 1
    assert lxx[chapter] == expected


def test_greek_esther_chapters_four_and_nine_are_shorter(conn):
    """The two real divergences: the Greek abbreviates. Small, but don't assume a 1:1 match."""
    lxx, wlc = chapter_lengths(conn, LXX, "Esth"), chapter_lengths(conn, WLC, "Esth")
    assert (lxx[4], wlc[4]) == (16, 17)
    assert (lxx[9], wlc[9]) == (30, 32)


def test_esther_addition_a_does_not_squat_on_chapter_one_verse_one(conn):
    """Addition A's opening carries a plain numeric 1, so ingesting it would put Mordecai's dream
    at Esth 1:1 -- an address that everywhere else reads "in the days of Ahasuerus". The Greek of
    the Masoretic 1:1 is on the lettered 1:1s, out of the integer loop's reach, so the chapter
    starts at verse 2 rather than carrying something false at verse 1."""
    verses = [r[0] for r in conn.execute(
        "SELECT verse FROM verses WHERE work_id=? AND book='Esth' AND chapter=1 ORDER BY verse",
        (LXX,),
    )]
    assert verses == list(range(2, 23))
