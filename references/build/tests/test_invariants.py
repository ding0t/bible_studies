"""Invariants that hold for any successful build, whatever the sources happen to contain.

Written after the `notes` table was found empty in every build since it was created. It was not a
subtle bug: the table existed, the schema documented it, `lookup_verse` and `lookup_passage` both
queried it, and `query.py passage --notes` was a flag that returned nothing for every passage in
every work. Nothing failed, because nothing asserted that a declared table should hold anything.

These tests are deliberately shallow. They do not check that the data is *right* -- the other suites
do that -- only that each declared structure is populated and each advertised code path can return
something. That is the class of defect that hides for months.
"""
import sqlite3
from pathlib import Path

import pytest

import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"

# A table may be legitimately empty only with a reason recorded here. An empty table with no entry
# is a failure, which is the whole point.
MAY_BE_EMPTY: dict[str, str] = {}


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    c = query.connect()
    yield c
    c.close()


def test_every_declared_table_has_rows(conn):
    """A table in the schema that no ingest ever writes to is a silent hole."""
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    assert tables, "no tables at all -- the build did not run"
    empty = [t for t in tables
             if t not in MAY_BE_EMPTY
             and conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == 0]
    assert not empty, (
        f"declared but empty: {empty}. Either an ingest is missing, or the table is legitimately "
        f"empty and belongs in MAY_BE_EMPTY with the reason.")


def test_notes_reach_a_verse_lookup(conn):
    """The specific path that was dead: notes exist AND a lookup can surface them."""
    assert conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0] > 0
    found = conn.execute(
        "SELECT book, chapter, verse FROM notes ORDER BY book, chapter, verse LIMIT 1").fetchone()
    result = query.lookup_verse(conn, found["book"], found["chapter"], found["verse"],
                                translation="ebible-eng-web")
    assert result["notes"], "notes table is populated but lookup_verse returns none for a verse that has one"


def test_passage_notes_flag_can_return_something(conn):
    """`--notes` returned nothing for every input for the life of the flag."""
    row = conn.execute("SELECT book, chapter, verse FROM notes LIMIT 1").fetchone()
    result = query.lookup_passage(conn, row["book"], row["chapter"], max(row["verse"], 1),
                                  row["verse"] + 2, translation="ebible-eng-web",
                                  include_notes=True)
    assert result.get("notes"), "include_notes produced nothing for a passage known to contain a note"


def test_every_ingested_work_has_content_somewhere(conn):
    """A work row with no content in any table is an ingest that silently did nothing.

    The content tables are discovered from the schema rather than listed here. Listing them by hand
    is how the first cut of this test reported hebrew-vocab-tools-pericopes as an orphan: its rows
    are in `literary_units`, which the hand-written list had left out. A test that needs editing
    every time a table is added will eventually be edited wrongly.
    """
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    carriers = [t for t in tables
                if t != "works"
                and any(c[1] == "work_id" for c in conn.execute(f"PRAGMA table_info({t})"))]
    assert carriers, "no table carries a work_id -- the schema is not what this test assumes"
    populated = set()
    for t in carriers:
        populated |= {r[0] for r in conn.execute(f"SELECT DISTINCT work_id FROM {t}")}
    registered = {r[0] for r in conn.execute("SELECT work_id FROM works")}
    orphans = sorted(registered - populated)
    assert not orphans, (
        f"works registered but carrying no content in any of {carriers}: {orphans}")


def test_every_study_state_file_parses():
    """A research trail no tool can read is a research trail that will quietly rot.

    Three of thirty-nine state files were unparseable YAML when this was written -- an unterminated
    flow mapping, a top-level key indented two spaces, and list items whose text contained ": ".
    None of it was visible to anyone until a tool tried to read them all at once.
    """
    import yaml
    state_dir = Path(__file__).parent.parent.parent / "study-state"
    if not state_dir.is_dir():
        pytest.skip("no study-state directory")
    broken = []
    for path in sorted(state_dir.glob("*.yml")):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            broken.append(f"{path.name}: {getattr(e, 'problem', e)}")
    assert not broken, "unparseable state files:\n  " + "\n  ".join(broken)
