"""STEP Bible's reference lists: the notation parser, and the lists reaching a passage lookup.

step_list_refs reads four notations in one file set ("Gen.1:1-27", the harmony's "1.1-17" under a
gospel column, "Josh.19:28,21:30" carrying the book across a comma, Philemon's bare "1-3"), and a
range read wrongly would put a harmony event on the wrong verses with nothing to show for it.
"""
from pathlib import Path

import pytest

import query
from build import step_list_refs

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"
LAST = {"Gen": {1: 31}, "Josh": {19: 51, 21: 45}, "1Chr": {6: 81}, "Exod": {4: 31},
        "1Sam": {27: 12}, "Matt": {26: 75, 27: 66}, "Phlm": {1: 25}, "Dan": {10: 21},
        "Luke": {24: 53}, "Acts": {1: 26}}


@pytest.mark.parametrize("text, book, expected", [
    ("Gen.1:1-27", None, [("Gen", 1, 1, 1, 27)]),
    ("1.1-17", "Matt", [("Matt", 1, 1, 1, 17)]),
    ("26.1-27.2", "Matt", [("Matt", 26, 1, 27, 2)]),
    ("Josh.19:28,21:30;1Chr.6:74", None,
     [("Josh", 19, 28, 19, 28), ("Josh", 21, 30, 21, 30), ("1Chr", 6, 74, 6, 74)]),
    ("Exod.4:3-4,30", None, [("Exod", 4, 3, 4, 4), ("Exod", 4, 30, 4, 30)]),
    ("1Sam.27", None, [("1Sam", 27, 1, 27, 12)]),
    ("1-3", "Phlm", [("Phlm", 1, 1, 1, 3)]),
    ("Dan.10:8 ff", None, [("Dan", 10, 8, 10, 8)]),
    ("24.50-53; Act.1.3-11", "Luke", [("Luke", 24, 50, 24, 53), ("Acts", 1, 3, 1, 11)]),
    ("2Chr.11:5-13-17", None, []),  # STEP's own typo: reported by the build, never guessed at
])
def test_step_list_refs(text, book, expected):
    assert step_list_refs(text, book, LAST) == expected


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    c = query.connect()
    yield c
    c.close()


def test_harmony_returns_every_account(conn):
    entries = query.lookup_lists(conn, book="Matt", chapter=26, verse=26)["entries"]
    supper = next(e for e in entries if e["list"] == "gospel-harmony")
    assert {r["reference"].split()[0] for r in supper["ranges"]} == {"Matt", "Mark", "Luke", "John"}


def test_harmony_reaches_bible_section(conn):
    """The pairs sit in parallel_passages, so bible_section lists John's Last Supper for Mark's."""
    parallels = query.lookup_section(conn, "Mark", 14, 22)["parallels"]
    assert any(p["work_id"] == "step-lists" and p["to_book"] == "John" for p in parallels)


def test_divine_name_at_genesis_16_13(conn):
    entries = query.lookup_lists(conn, list_id="divine-names", book="Gen", chapter=16, verse=13)["entries"]
    assert any("Ro'i" in (e.get("detail") or "") for e in entries)
