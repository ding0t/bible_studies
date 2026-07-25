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
