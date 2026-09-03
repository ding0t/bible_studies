"""Book-coverage completeness checks for out/bible-text.db.

Catches the class of bug where a translation source silently drops books it should have --
e.g. ingest_ebible() mis-mapping BibleOrgSys's internal book codes against MACULA_USFM_TO_OSIS
caused the WEB, Delitzsch Hebrew, Tischendorf, and Brenton LXX ingests to each silently lose a
chunk of their books (WEB: 44/66) with no error, no warning, just quietly-wrong query results.

This is not a general validity check on every source -- several are intentionally partial (NT-only
Greek texts, OT-only Masoretic texts, historically-incomplete translations like Tyndale/Noyes/OEB,
the Samaritan Pentateuch, the LXX's deuterocanonical gap). Those are named in PARTIAL_COVERAGE
below with the exact book set actually expected, so a new gap in a full-Bible source still fails
loudly instead of blending into the list of "known" partial ones.
"""
import sqlite3
from pathlib import Path

import pytest

from book_map import NUM_TO_OSIS

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"

OT_BOOKS = {NUM_TO_OSIS[i] for i in range(1, 40)}
NT_BOOKS = {NUM_TO_OSIS[i] for i in range(40, 67)}
ALL_BOOKS = OT_BOOKS | NT_BOOKS

# work_id -> exact book set expected, for sources that are legitimately not full-Bible.
# Anything not listed here is expected to have all 66 books. Verified against the actual
# ingested data, not guessed -- if a source's true scope changes upstream, update the set here
# with the same care (query the db, don't just widen the set to make the test pass).
PARTIAL_COVERAGE = {
    # Greek NT texts -- no OT by design
    "sblgnt": NT_BOOKS,
    "ebible-grc-tisch": NT_BOOKS,
    "ebible-hebsg": NT_BOOKS,   # Salkinson-Ginsburg is a New Testament only
    "scrollmapper-Anderson": NT_BOOKS,
    "scrollmapper-Byz": NT_BOOKS,
    "scrollmapper-Haweis": NT_BOOKS,
    "scrollmapper-StatResGNT": NT_BOOKS,
    "scrollmapper-TR": NT_BOOKS,
    "scrollmapper-Twenty": NT_BOOKS,
    # Hebrew/Masoretic OT texts -- no NT by design
    "morphhb-wlc": OT_BOOKS,
    "scrollmapper-WLC": OT_BOOKS,
    "scrollmapper-JPS": OT_BOOKS,
    "scrollmapper-MapM": OT_BOOKS,
    # Samaritan Pentateuch -- Torah only by design
    "scrollmapper-SP": {"Gen", "Exod", "Lev", "Num", "Deut"},
    # Tyndale died before finishing the OT -- Genesis plus the NT (minus a handful of NT books
    # not published before his execution) is genuinely all there is.
    "scrollmapper-Tyndale": {"Gen", "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "Heb", "Rev"},
    # Noyes only translated the OT poetic/wisdom/prophetic books, not the Torah or histories.
    "scrollmapper-Noyes": {
        "Job", "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel",
        "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    } | NT_BOOKS,
    # Open English Bible is a still-in-progress public-domain project -- Psalms plus the NT is
    # the current published scope, not a bug.
    "scrollmapper-OEB": {"Ps"} | NT_BOOKS,
    "scrollmapper-OEBcth": {"Ps"} | NT_BOOKS,
    # Brenton's LXX edition's deuterocanonical/GA books (Tobit, Judith, Wisdom, Sirach, Baruch,
    # 1-4 Maccabees, Greek Esther/Daniel additions) use book codes MACULA_USFM_TO_OSIS
    # deliberately doesn't map (see ingest_ebible in build.py) -- Nehemiah is folded into 2 Esdras
    # under LXX numbering rather than standing alone, so it's absent here too.
    "ebible-grcbrent": OT_BOOKS,
}


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(DB_PATH)
    yield connection
    connection.close()


def test_full_bible_sources_have_all_66_books(conn):
    rows = conn.execute("SELECT work_id, GROUP_CONCAT(DISTINCT book) FROM verses GROUP BY work_id").fetchall()
    failures = []
    for work_id, books_csv in rows:
        if work_id.startswith("dss-"):
            continue  # a scroll covers whatever survived; see test_dss.py for what IS asserted
        books = set(books_csv.split(","))
        expected = PARTIAL_COVERAGE.get(work_id, ALL_BOOKS)
        missing = expected - books
        extra = books - expected
        if missing:
            failures.append(f"{work_id}: missing {sorted(missing)}")
        if extra:
            failures.append(f"{work_id}: unexpected extra books {sorted(extra)} -- narrow its PARTIAL_COVERAGE entry")
    assert not failures, "\n".join(failures)


def test_no_unrecognized_book_codes(conn):
    rows = conn.execute("SELECT DISTINCT book FROM verses").fetchall()
    unknown = {book for (book,) in rows if book not in ALL_BOOKS}
    assert not unknown, f"unrecognized OSIS book codes in verses table: {sorted(unknown)}"
