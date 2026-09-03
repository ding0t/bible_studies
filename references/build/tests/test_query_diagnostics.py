"""lookup_verse/lookup_passage empty-result diagnostics.

An empty result (verses: [] / text: None) looks the same whether the caller typo'd the book
code, asked a translation for a book it doesn't cover, or gave a bad chapter/verse -- see
_empty_result_reason in query.py. These pin the three cases apart so a future edit can't quietly
collapse them back into one indistinguishable "nothing found".
"""
from pathlib import Path

import pytest

import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = query.connect()
    yield connection
    connection.close()


def test_unrecognized_book_code_warns(conn):
    result = query.lookup_verse(conn, "2Kng", 4, 42)
    assert result["text"] is None
    assert "recognized OSIS book code" in result["warning"]


def test_valid_book_not_covered_by_translation_warns(conn):
    # ebible-grc-tisch is a Greek NT text -- Genesis is a real OSIS book it simply doesn't have.
    result = query.lookup_passage(conn, "Gen", 1, 1, 3, translation="ebible-grc-tisch")
    assert result["verses"] == []
    assert "has no verses for Gen at all" in result["warning"]


def test_bad_verse_in_covered_book_warns(conn):
    result = query.lookup_verse(conn, "Jude", 1, 999)
    assert result["text"] is None
    assert "exists in" in result["warning"]
    assert "not at the chapter/verse given" in result["warning"]


def test_found_verse_has_no_warning(conn):
    result = query.lookup_verse(conn, "2Kgs", 4, 42)
    assert result["text"] is not None
    assert "warning" not in result


def test_translation_codes_resolve_to_works_that_exist(conn):
    """Resolution used to build 'scrollmapper-{code}' by convention. Five codes live under a
    different prefix -- WEB, SBLGNT, Brenton-LXX, Tischendorf, Delitzsch -- so asking for them by
    name hit a work_id that does not exist and came back empty. WEB is this repo's default English
    text, so the most ordinary lookup there is was silently returning nothing."""
    for code, expected in [("WEB", "ebible-eng-web"), ("SBLGNT", "sblgnt"),
                           ("Brenton-LXX", "ebible-grcbrent"), ("KJV", "scrollmapper-KJV")]:
        assert query._resolve_work_id(conn, code) == expected
        assert conn.execute("SELECT 1 FROM works WHERE work_id=?", (expected,)).fetchone()


def test_default_english_lookup_returns_text(conn):
    assert query.lookup_verse(conn, "Joel", 2, 28, "WEB")["text"]


def test_a_prefixed_strongs_number_does_not_mix_the_testaments(conn):
    """Strong's numbers are stored bare, so G1242 and H1242 are one string in the table -- diatheke
    and boqer, 'covenant' and 'morning'. Without a language filter a Greek word study silently
    collects Hebrew hits. The collision predates the Septuagint tagging; adding 566k Strong's-tagged
    Greek rows is what made it loud enough to notice."""
    greek = {r["work_id"] for r in query.lookup_concordance(conn, "G1242")}
    hebrew = {r["work_id"] for r in query.lookup_concordance(conn, "H1285")}
    assert greek and hebrew
    assert not (greek & hebrew), "a prefixed lookup reached into the other language"
    assert "lxx-lemmas" in greek, "the Septuagint should answer a Greek concordance"
    # unprefixed stays unfiltered -- the caller did not say which numbering they meant
    assert {r["work_id"] for r in query.lookup_concordance(conn, "1242")} > greek


def test_septuagint_is_reachable_by_strongs_number(conn):
    """The Septuagint had no Strong's tagging at all, so a word could not be followed across the
    testaments -- and the Septuagint is the Old Testament as the New Testament's authors read it."""
    rows = query.lookup_concordance(conn, "G1242")
    assert sum(1 for r in rows if r["work_id"] == "lxx-lemmas") > 100
