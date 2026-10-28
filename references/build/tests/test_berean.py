"""The Berean Literal Bible and the Berean Interlinear (the BSB translation tables).

The interlinear shares word_alignment with the ULT, so the regression most worth catching is the
two bleeding into each other: a ULT lookup returning Berean rows would look like more evidence
for a rendering while being the same verse counted twice.
"""
import json
from pathlib import Path

import pytest

import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    c = query.connect()
    yield c
    c.close()


def test_literal_bible_covers_both_testaments(conn):
    books = conn.execute(
        "SELECT COUNT(DISTINCT book) FROM verses WHERE work_id='berean-blb'").fetchone()[0]
    assert books == 66
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id='berean-blb' AND book='Gen' AND chapter=1 AND verse=2"
    ).fetchone()[0]
    assert "[was]" in text  # supplied words keep the BLB's brackets


def test_bsb_interlinear_links_daily_to_epiousios(conn):
    result = query.lookup_interlinear(conn, "Matt", 6, 11, interlinear="bsb")
    assert result["text"].startswith("Give us this day our daily bread")
    assert {"english": "daily", "content": "ἐπιούσιον", "strong": "G1967"}.items() <= next(
        r for r in result["rows"] if r["english"] == "daily").items()


def test_bsb_interlinear_runs_in_hebrew_order(conn):
    """The file runs in English order; Genesis 1:1 reads בָּרָא before אֱלֹהִים only if re-sorted."""
    rows = query.lookup_interlinear(conn, "Gen", 1, 1, interlinear="bsb")["rows"]
    assert [r["strong"] for r in rows[:3]] == ["H7225", "H1254", "H430"]


def test_interlinears_do_not_mix(conn):
    ult = query.lookup_interlinear(conn, "Matt", 6, 11)["rows"]
    bsb = query.lookup_interlinear(conn, "Matt", 6, 11, interlinear="bsb")["rows"]
    assert ult and bsb
    assert all(r["lemma"] for r in ult)       # ULT rows carry a lemma
    assert not any(r["lemma"] for r in bsb)   # Berean rows never do


def test_scrollmapper_titles_lose_their_markdown_heading(conn):
    title = conn.execute("SELECT title FROM works WHERE work_id='scrollmapper-ASV'").fetchone()[0]
    assert not title.startswith("#")


def test_bsb_comes_from_its_publisher_with_list_verses_intact(conn):
    """scrollmapper's copy pushed every list line into the following verse; 1 Chronicles 1:29 lost
    Nebaioth to 1:30. Pinned so a source swap back cannot pass unnoticed."""
    works = {r[0] for r in conn.execute("SELECT work_id FROM works WHERE translation_code='BSB'")}
    assert works == {"berean-bsb"}
    text = conn.execute("SELECT text FROM verses WHERE work_id='berean-bsb' AND book='1Chr' "
                        "AND chapter=1 AND verse=29").fetchone()[0]
    assert "Nebaioth" in text


def test_msb_carries_the_doxology_and_names_who_omits_it(conn):
    verse = query.lookup_verse(conn, "Matt", 6, 13, translation="MSB")
    assert verse["text"].endswith("For Yours is the kingdom and the power and the glory forever. Amen.’")
    assert any(n["work_id"] == "berean-msb" and n["text"].startswith("CT does not include")
               for n in verse["notes"])


def test_section_finds_the_lords_prayer_and_its_parallel(conn):
    r = query.lookup_section(conn, "Matt", 6, 9, 13)
    assert ("The Lord’s Prayer", 5, 15) in {(s["text"], s["verse"], s["end_verse"]) for s in r["sections"]}
    assert "Luke 11:1-4" in {p["reference"] for p in r["parallels"]}
    back = query.lookup_section(conn, "Luke", 11, 2)
    assert ("Matt", 6, 5) in {(p["book"], p["chapter"], p["verse"]) for p in back["parallel_to"]}


def test_names_are_individuals_not_spellings(conn):
    zechariahs = query.lookup_names(conn, "Zechariah")["individuals"]
    assert len(zechariahs) > 20
    aaron = query.lookup_names(conn, "Aaron")["individuals"][0]
    assert aaron["parents"].startswith("Amram@")
    named = query.lookup_names(conn, book="Exod", chapter=4, verse=14)["individuals"]
    assert any(p["name_id"].startswith("Aaron@") for p in named)


def test_a_disputed_site_reports_its_alternatives(conn):
    emmaus = query.lookup_names(conn, "Emmaus")["individuals"][0]["location"]
    assert emmaus["score"] < 500 and len(json.loads(emmaus["alternatives"])) >= 3
