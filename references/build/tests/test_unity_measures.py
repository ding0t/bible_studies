"""The dating and parsing rules the unity measures rest on, run against the real tables."""
import pytest

from unity_measures import (author_of, date_range, load_authorship, normalise_greek, parse_refs,
                            chronology_years)


@pytest.fixture(scope="module")
def books():
    return load_authorship()


def test_every_book_has_a_date_and_a_writer(books):
    assert len(books) == 66
    for b in books.values():
        lo, hi = b["date"]
        assert lo <= hi, b["id"]
        assert b["author_key"], b["id"]


def test_critical_isaiah_is_dated_by_chapter(books):
    isa = books["Isa"]
    assert date_range(isa, "critical", 7) == (-740, -700)
    assert date_range(isa, "critical", 53) == (-560, -540)
    assert date_range(isa, "critical", 60) == (-500, -400)
    assert author_of(isa, "critical", 53) == "second-isaiah"
    assert author_of(isa, "traditional", 53) == "isaiah"


def test_critical_falls_back_to_traditional_only_where_no_source_differs(books):
    assert date_range(books["Dan"], "critical") == (-167, -164)
    assert date_range(books["Amos"], "critical") == date_range(books["Amos"], "traditional")
    # a bare lower bound is used as a point, never widened to an unsourced range
    assert date_range(books["Matt"], "critical") == (70, 70)


def test_references_continue_the_previous_book():
    assert parse_refs("Isaiah 44:28; 45:1") == [("Isa", 44, 28), ("Isa", 45, 1)]
    assert parse_refs("Jeremiah 51:11, 28") == [("Jer", 51, 11), ("Jer", 51, 28)]
    assert parse_refs("Exodus 12:46; Psalm 34:20") == [("Exod", 12, 46), ("Ps", 34, 20)]
    assert parse_refs("Matthew 26:15; 27:3-10 (Matthew names Jeremiah)") == [
        ("Matt", 26, 15), ("Matt", 27, 3)]


def test_greek_lemmas_compare_across_editions():
    # MACULA prints accented lemmas, the LXX lemma file unaccented with medial sigma
    assert normalise_greek("ὄφις") == normalise_greek("οφισ") == "οφισ"


def test_every_prophecy_event_is_in_the_chronology():
    import tomllib
    from unity_measures import PROPHECY
    years = chronology_years()
    with open(PROPHECY, "rb") as f:
        for p in tomllib.load(f)["prophecy"]:
            assert p.get("event") in years or "year" in p, p["id"]
