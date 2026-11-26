"""The years and copies the prophecies-of-Christ reference page shows, run against the real ledger."""
import json
import sqlite3
import tomllib

import pytest

import export_prophecies as ep
from unity_measures import DB, load_authorship, chronology_years


@pytest.fixture(scope="module")
def rows():
    if not DB.exists():
        pytest.skip(f"{DB} not built -- run `uv run python build.py` first")
    with open(ep.CHRIST_PROPHECY, "rb") as f:
        entries = {e["id"]: e for e in tomllib.load(f)["prophecy"]}
    passion = {e["id"] for e in json.loads(ep.CHRONOLOGY.read_text(encoding="utf-8"))["passion_sequence"]["events"]}
    conn = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
    scrolls = ep.qumran_index(conn)
    books, years = load_authorship(), chronology_years()
    lengths = ep.chapter_length_lookup(conn)
    return {i: ep.entry_row(e, books, years, passion, scrolls, lengths) for i, e in entries.items()}


def test_a_copy_at_qumran_is_not_older_than_an_event_in_jesus_lifetime(rows):
    """Zechariah 12:10 is in 4Q80, but Qumran's copies run to AD 68 and the spear was AD 33: only
    the Great Isaiah Scroll (about 125 BC) is a manuscript dated before His lifetime."""
    pierced = rows["pierced-one"]
    assert pierced["qumran"] and pierced["fulfilled"] == 33
    assert not pierced["manuscript_before"]
    servant = rows["suffering-servant"]
    assert "1Qisaa" in servant["qumran"] and servant["manuscript_before"]


def test_critical_isaiah_dates_the_servant_by_its_chapter(rows):
    servant = rows["suffering-servant"]
    assert servant["written_critical"] == -540 and servant["years_ahead_critical"] == 573


def test_no_critical_date_is_claimed_where_the_table_records_none(rows):
    """The authorship table gives the Psalms no critical date; showing the traditional one under the
    critics' name would make them agree with it."""
    assert rows["hands-and-feet"]["written_critical"] is None
    assert rows["hands-and-feet"]["years_ahead_critical"] is None
    assert rows["hands-and-feet"]["existed_by"] is None  # the Psalms have no bracket yet


def test_zechariah_is_bracketed_by_sirach(rows):
    """Zechariah 9-14 has no critical date in the table, but Sirach 49:10 names the Twelve and its
    translator wrote after 132 BC: on any dating the prophecy existed by then."""
    pierced = rows["pierced-one"]
    assert pierced["written_critical"] is None
    assert pierced["existed_by"] == -132 and pierced["years_ahead_at_least"] == 165


def test_an_undated_prophecy_claims_nothing(rows):
    future = [r for r in rows.values() if r["fulfilled"] is None]
    assert future and not any(r["manuscript_before"] for r in future)
    assert all(r["years_ahead_traditional"] is None for r in future)


def test_the_committed_file_is_this_ledgers(rows):
    """check_prophecies.py fails on a stale file by its hash; this checks the hash means what it says."""
    written = json.loads(ep.OUT.read_text(encoding="utf-8"))
    assert written["inputs_sha256"] == ep.inputs_hash()
    assert {r["id"]: r for r in written["prophecies"]} == rows


def lengths(book, chapter):
    return {("Mark", 14): 72, ("Mark", 15): 47, ("Heb", 7): 28}.get((book, chapter), 0)


def test_references_expand_to_the_verses_the_popup_reads():
    """A bare verse continues its chapter, a bare chapter:verse its book, a range may cross a
    chapter, and commentary after '(' or a source that is not Scripture gives nothing."""
    assert ep.verse_keys("Isaiah 53:5, 9, 12", lengths) == ["Isa 53:5", "Isa 53:9", "Isa 53:12"]
    assert ep.verse_keys("Psalm 69:25; 109:8", lengths) == ["Ps 69:25", "Ps 109:8"]
    assert ep.verse_keys("Isaiah 53:12b", lengths) == ["Isa 53:12"]
    crossing = ep.verse_keys("Mark 14:70-15:2", lengths)
    assert crossing == ["Mark 14:70", "Mark 14:71", "Mark 14:72", "Mark 15:1", "Mark 15:2"]
    assert ep.verse_keys("Josephus, Jewish War 6-7 (the trampling begun)", lengths) == []
    assert ep.verse_keys("Colossians 1:6, 23 (begun)", lengths) == ["Col 1:6", "Col 1:23"]
