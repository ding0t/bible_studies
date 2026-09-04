"""The two cross-reference witnesses, and the WEB footnote parser that produces the second one.

`corroborated` on a derived link means "some list independently names this pair". It is only worth
anything if the lists are actually independent, which is why the scrollmapper file is NOT a second
witness: its own header reads "#www.openbible.info CC-BY", so it and openbible-crossrefs are one
source counted twice. The WEB's translator footnotes are a real second opinion, and small enough
that a parsing regression would be easy to miss without these.
"""
import sqlite3
from pathlib import Path

import pytest

from build import _parse_web_targets

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


# Every shape the WEB actually uses, taken from the USFM rather than invented.
@pytest.mark.parametrize("payload,expected", [
    ("Deuteronomy 8:3", [("Deuteronomy", 8, 3, 3)]),
    ("Isaiah 40:3-5", [("Isaiah", 40, 3, 5)]),
    ("Exodus 13:2,12", [("Exodus", 13, 2, 2), ("Exodus", 13, 12, 12)]),
    ("2 Kings 23:21; 2 Chronicles 35:1",
     [("2 Kings", 23, 21, 21), ("2 Chronicles", 35, 1, 1)]),
    # a later segment may drop the book and continue the previous one
    ("Isaiah 8:14; 28:16", [("Isaiah", 8, 14, 14), ("Isaiah", 28, 16, 16)]),
    # annotations the parser has to strip rather than choke on
    ("Deuteronomy 32:43 LXX", [("Deuteronomy", 32, 43, 43)]),
    ("See Isaiah 53:4", [("Isaiah", 53, 4, 4)]),
    # cross-chapter range keeps its anchor -- the schema addresses one chapter
    ("2 Kings 6:31—7:20", [("2 Kings", 6, 31, 31)]),
])
def test_web_target_shapes(payload, expected):
    assert _parse_web_targets(payload) == expected


def test_both_witnesses_present(conn):
    counts = {r["work_id"]: r["n"] for r in conn.execute(
        "SELECT work_id, COUNT(*) n FROM cross_references GROUP BY work_id")}
    assert counts.get("openbible-crossrefs", 0) > 800_000
    # small by design: these are quotation footnotes, not a chain reference
    assert 300 < counts.get("web-crossrefs", 0) < 1_000


def test_web_crossrefs_sit_on_new_testament_quotations(conn):
    """The WEB's footnotes earn their place by covering exactly where the derived links are scored."""
    nt = conn.execute(
        "SELECT COUNT(*) FROM cross_references WHERE work_id='web-crossrefs' "
        "AND from_book IN ('Matt','Mark','Luke','John','Acts','Rom','1Cor','2Cor','Gal','Eph',"
        "'Phil','Col','1Thess','2Thess','1Tim','2Tim','Titus','Phlm','Heb','Jas','1Pet','2Pet',"
        "'1John','2John','3John','Jude','Rev')").fetchone()[0]
    total = conn.execute(
        "SELECT COUNT(*) FROM cross_references WHERE work_id='web-crossrefs'").fetchone()[0]
    assert nt / total > 0.8


def test_matthew_11_10_conflation_is_missed_by_both_lists(conn):
    """Both witnesses carry the Malachi half of Matthew's conflated quotation and neither the Exodus
    half, which the derived link finds on nine verbatim Greek words. If a list ever gains it this
    test should fail and the claim on how-we-cross-reference.md be revisited."""
    for work in ("openbible-crossrefs", "web-crossrefs"):
        rows = {(r["to_book"], r["to_chapter"]) for r in conn.execute(
            "SELECT to_book, to_chapter FROM cross_references "
            "WHERE work_id=? AND from_book='Matt' AND from_chapter=11 AND from_verse=10", (work,))}
        assert ("Mal", 3) in rows
        assert ("Exod", 23) not in rows
