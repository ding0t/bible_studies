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
    return {i: ep.entry_row(e, books, years, passion, scrolls) for i, e in entries.items()}


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
