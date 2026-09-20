"""Tests for study_notes_query.py.

Two of these are regression tests for real incidents rather than hypotheticals:

- `test_john_6_34_esv_reads_sir` pins the quotation that a study once got wrong by drafting from
  memory ("Lord, give us this bread" for "Sir, give us this bread always"). This is the lookup the
  whole module exists to make cheap.
- The `EXPLAIN QUERY PLAN` tests pin the scan guard. On 2026-09-18 an agent hand-rolled survey
  queries against this database over SMB, waited 64-97s, and concluded the volume was hung. A
  comment saying "use the index" would not have prevented that; an assertion does.

The database lives on an external volume, so every test skips (never fails) when it is not
mounted -- an unmounted drive is a routine local condition, not a broken build.
"""
import pytest

import study_notes_query as snq

pytestmark = pytest.mark.skipif(
    not snq.availability()["available"],
    reason=f"study-notes.db unavailable: {snq.availability().get('reason')}",
)


@pytest.fixture(scope="module")
def conn():
    c = snq.connect()
    yield c
    c.close()


# --- the regression that motivated the module ------------------------------

def test_john_6_34_esv_reads_sir(conn):
    rows = snq.lookup_verse(conn, "John", 6, 34, work_id="esv-study-bible")
    assert len(rows) == 1
    assert "Sir, give us this bread always" in rows[0]["text"]
    assert "Lord, give us this bread" not in rows[0]["text"]


# --- P2: the wrong query is unrepresentable --------------------------------

@pytest.mark.parametrize("table,sql,params", [
    ("verses", "SELECT text FROM verses WHERE book=? AND chapter=? AND verse=?", ("John", 6, 34)),
    ("notes", "SELECT text FROM notes WHERE book=? AND chapter=?", ("John", 6)),
    ("notes", "SELECT text FROM notes WHERE book=? AND chapter=? AND verse_start<=? AND verse_end>=?",
     ("John", 6, 10, 10)),
])
def test_query_plans_use_an_index(conn, table, sql, params):
    """Every shape this module issues against a large table must SEARCH, never SCAN.

    A SCAN here was 60-100s back when this was NAS-mounted over SMB and read to an agent as a
    hung volume; still a needless full scan of a large table now it's local.
    """
    plan = " ".join(r["detail"] for r in conn.execute("EXPLAIN QUERY PLAN " + sql, params))
    assert "SEARCH" in plan, f"{table}: expected an indexed SEARCH, got: {plan}"
    assert f"SCAN {table}" not in plan, f"{table}: full scan in plan: {plan}"


def test_missing_book_is_refused(conn):
    with pytest.raises(ValueError, match="book is required"):
        snq.lookup_note(conn, "", 6)


def test_missing_chapter_is_refused(conn):
    with pytest.raises(ValueError, match="chapter is required"):
        snq.lookup_note(conn, "John", None)


def test_non_osis_book_is_refused(conn):
    with pytest.raises(ValueError, match="OSIS book code"):
        snq.lookup_verse(conn, "Jn", 6, 34)


def test_list_works_does_not_scan_by_default(conn):
    """The default path must stay on the 11-row works table.

    This function's first draft counted notes and verses per work unconditionally and hung the
    module's own smoke test, so the guard is asserted rather than assumed.
    """
    plan = " ".join(
        r["detail"] for r in conn.execute(
            "EXPLAIN QUERY PLAN SELECT work_id, title, publisher, year, license_tier, attribution "
            "FROM works ORDER BY work_id"
        )
    )
    assert "notes" not in plan and "verses" not in plan
    works = snq.list_works(conn)
    assert works and "notes" not in works[0]


# --- P3: every record carries its own licence ------------------------------

def test_every_record_is_tier_stamped(conn):
    records = (
        snq.lookup_verse(conn, "John", 6, 34)
        + snq.lookup_note(conn, "John", 6, 10)
        + snq.lookup_intro(conn, "Matt")
        + snq.lookup_article(conn, "Passover")
    )
    assert records
    for r in records:
        assert r["tier"] == "quotation-only"
        assert r["quote_allowance"]
        assert r["attribution"], f"no attribution on {r.get('work_id')}"


# --- truncation is always declared -----------------------------------------

def test_truncation_marks_itself(conn):
    long_one = snq.lookup_intro(conn, "Matt", work_id="esv-study-bible", max_chars=200)
    assert long_one
    rec = long_one[0]
    assert rec["truncated"] is True
    assert rec["full_length"] > 200
    assert len(rec["text"]) <= 201 + 1  # cap + ellipsis, after rstrip


def test_untruncated_reports_full_length(conn):
    rows = snq.lookup_note(conn, "John", 6, 10, work_id="esv-study-bible", max_chars=None)
    assert rows
    for r in rows:
        assert r["truncated"] is False
        assert r["full_length"] == len(r["text"])


def test_verse_text_is_never_truncated(conn):
    """Verifying a quotation against a clipped verse is worse than not verifying it."""
    rows = snq.lookup_verse(conn, "John", 6, 34)
    assert rows
    for r in rows:
        assert "truncated" not in r


# --- notes spanning several verses -----------------------------------------

def test_span_notes_are_returned_for_a_covered_verse(conn):
    rows = snq.lookup_note(conn, "John", 6, 10, work_id="esv-study-bible")
    spans = {(r["verse_start"], r["verse_end"]) for r in rows}
    assert (1, 15) in spans, "the 6:1-15 span note should cover v10"
    assert (10, 11) in spans


def test_empty_result_is_a_real_answer(conn):
    """The ESV has no note on John 6:34 -- that is data, not unavailability."""
    assert snq.lookup_note(conn, "John", 6, 34, work_id="esv-study-bible") == []
    assert snq.lookup_note(conn, "John", 6, 34) != []


# --- P4: degrade loudly and specifically -----------------------------------

def test_availability_reports_a_remedy_when_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", str(tmp_path / "nope"))
    status = snq.availability()
    assert status["available"] is False
    assert "not mounted" in status["reason"]
    assert "BIBLE_MEDIA_ROOT" in status["remedy"]


def test_connect_raises_structured_error_when_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", str(tmp_path / "nope"))
    with pytest.raises(snq.SourceUnavailable) as e:
        snq.connect()
    assert e.value.as_dict()["available"] is False
    assert e.value.remedy
