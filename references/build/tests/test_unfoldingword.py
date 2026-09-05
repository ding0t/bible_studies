"""The unfoldingWord sources, and the two lookups that are the reason for taking them.

ULT's alignment is the only link in this database between an English word and the original it
renders, and UHG is the only thing here that says what a *form* does rather than what a word means.
Both are new enough that a silent regression would not be noticed by any existing test.
"""
import sqlite3
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


def test_all_four_sources_ingested(conn):
    works = {r["work_id"]: r for r in conn.execute(
        "SELECT work_id, license_tier, license FROM works WHERE work_id LIKE 'uw-%'")}
    assert set(works) == {"uw-uhb", "uw-ugnt", "uw-ult", "uw-uhg"}
    # all four are CC BY-SA, which is open for this project's purposes but is NOT plain CC BY --
    # see references/README.md before publishing a derived dataset built on them
    for work in works.values():
        assert work["license_tier"] == "open"
        assert "BY-SA" in work["license"]


def test_alignment_covers_both_testaments(conn):
    """A regression here would most likely be a parser that silently stopped at one testament."""
    ot = conn.execute("SELECT COUNT(*) FROM word_alignment WHERE book='Gen'").fetchone()[0]
    nt = conn.execute("SELECT COUNT(*) FROM word_alignment WHERE book='John'").fetchone()[0]
    assert ot > 1000 and nt > 1000


def test_interlinear_reports_the_many_to_many_relation(conn):
    """Genesis 1:1's "the heavens" renders both אֵת and הַשָּׁמַיִם.

    Pinned because the obvious "tidy-up" is to collapse rows sharing an English phrase, which would
    throw away the object marker and quietly assert a one-to-one mapping the Hebrew does not have.
    """
    result = query.lookup_interlinear(conn, "Gen", 1, 1)
    heavens = [r for r in result["rows"] if r["english"] == "the heavens"]
    assert len(heavens) == 2
    # asserted on Strong's rather than the lemma: the Hebrew carries vowel points, and a literal in
    # this file can differ from the database by Unicode normalisation alone while looking identical
    assert {r["strong"] for r in heavens} == {"H0853", "d:H8064"}


def test_interlinear_resolves_against_ugnt_not_sblgnt(conn):
    """The Greek side is UGNT, and at John 1:34 the two texts genuinely differ.

    SBLGNT reads ἐκλεκτός, UGNT υἱός. Anything that "fixed" the alignment by pointing it at SBLGNT
    would break here, which is the point -- a study quoting this verse needs to know which text it
    is standing on.
    """
    ugnt = conn.execute(
        "SELECT text FROM verses WHERE work_id='uw-ugnt' AND book='John' AND chapter=1 AND verse=34"
    ).fetchone()[0]
    sblgnt = conn.execute(
        "SELECT text FROM verses WHERE work_id='sblgnt' AND book='John' AND chapter=1 AND verse=34"
    ).fetchone()[0]
    assert "υἱ" in ugnt.lower()          # UGNT capitalises it, Υἱὸς
    assert "ἐκλεκτ" in sblgnt
    assert ugnt != sblgnt


def test_grammar_finds_a_form_not_a_word(conn):
    rows = query.lookup_grammar(conn, "gentilic")
    assert rows and any("gentilic" in str(r["slug"]) for r in rows)
    assert "ethnic" in str(rows[0]["body"]).lower()


def test_grammar_body_has_its_sphinx_directives_stripped(conn):
    """The articles are prose once the roles are removed; leaving them in makes every quotation
    from this source unusable without hand-editing."""
    rows = query.lookup_grammar(conn, "adjective", full=True)
    body = str(rows[0]["body"])
    assert ":ref:`" not in body
    assert ":github_url:" not in body
