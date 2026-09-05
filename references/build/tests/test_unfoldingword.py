"""The unfoldingWord sources, and the two lookups that are the reason for taking them.

ULT's alignment is the only link in this database between an English word and the original it
renders, and UHG is the only thing here that says what a *form* does rather than what a word means.
Both are new enough that a silent regression would not be noticed by any existing test.
"""
import difflib
import re
import sqlite3
import unicodedata
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


def test_footnotes_ingested_for_all_three_texts(conn):
    """The notes table sat empty for the whole life of this database before these were wired in,
    which made `query.py passage --notes` a flag that silently returned nothing for every passage
    in every work. Counts are pinned exactly against a raw grep of the USFM: 949 + 22 + 326."""
    counts = dict(conn.execute(
        "SELECT work_id, COUNT(*) FROM notes GROUP BY work_id"))
    assert counts == {"uw-uhb": 949, "uw-ugnt": 22, "uw-ult": 326}


def test_uhb_notes_are_overwhelmingly_qere_readings(conn):
    """UHB prints the Ketiv and records the Qere in a footnote flagged by a bare `Q`. That is the
    mechanism behind the ~340 verses where uw-uhb and morphhb-wlc genuinely differ, so the Qere
    notes get their own note_type rather than being filed under translator prose."""
    by_type = dict(conn.execute(
        "SELECT note_type, COUNT(*) FROM notes WHERE work_id='uw-uhb' GROUP BY note_type"))
    assert by_type["qere"] == 930
    assert by_type["ketiv"] == 1
    assert all(t.startswith("Qere: ") for (t,) in conn.execute(
        "SELECT text FROM notes WHERE note_type='qere'"))


def test_footnote_markup_is_stripped_to_readable_prose(conn):
    r"""A note must not leak USFM. The Ruth 2:1 pair is the reference case: ULT records the
    translators' fork and UHB the Qere behind it, and both have to come back as prose rather than
    as \fq/\ft markers wrapped around eighty characters of lemma and Strong's tagging."""
    texts = [r["text"] for r in conn.execute(
        "SELECT text FROM notes WHERE book='Ruth' AND chapter=2 AND verse=1 ORDER BY work_id")]
    assert texts == [
        "Qere: מוֹדַ֣ע",
        "a relative of her husband or perhaps an acquaintance of her husband (Hebrew Ketiv)",
    ]
    for (text,) in conn.execute("SELECT text FROM notes"):
        assert "\\" not in text and 'lemma="' not in text


def test_superscription_footnotes_are_not_lost(conn):
    r"""64 psalms carry their title in a \d block rather than a \v, because UHB numbers verses the
    English way and those titles are Hebrew verse 1. _uw_verses splits on \v and cannot see them,
    so two Qere readings on Jeduthun's name went missing until _uw_superscriptions was added."""
    rows = {(r["chapter"], r["text"]) for r in conn.execute(
        "SELECT chapter, text FROM notes WHERE work_id='uw-uhb' AND book='Ps' AND verse=0")}
    assert {c for c, _ in rows} == {39, 77}
    # compared on the consonantal skeleton: the two spellings differ in pointing and one carries a
    # prefixed lamed, so a pointed substring match would pass on one psalm and fail on the other
    bare = lambda t: "".join(
        ch for ch in unicodedata.normalize("NFD", t) if not unicodedata.combining(ch))
    assert all("ידות" in bare(t) for _, t in rows)


def test_notes_reach_the_verse_and_passage_lookups(conn):
    """Both lookups query `notes` by versification scheme, and both returned nothing for years.
    Guard the wiring, not just the table."""
    verse = query.lookup_verse(conn, "Gen", 8, 17, translation="ebible-eng-web")
    assert any(n["text"].startswith("Qere: ") for n in verse["notes"])
    passage = query.lookup_passage(
        conn, "Ruth", 2, 1, 3, translation="ebible-eng-web", include_notes=True)
    assert {n["work_id"] for n in passage["notes"]} == {"uw-uhb", "uw-ult"}


def test_psalm_superscriptions_are_ingested_as_verse_zero(conn):
    r"""64 psalm titles sit in a \d block rather than a \v, because UHB numbers verses the English
    way and those titles are Hebrew verse 1. Their text was absent from `verses` entirely until
    _uw_superscriptions was added. Verse 0 is used because it cannot collide with a real verse, and
    because merging the title into verse 1 would fuse two Hebrew verses into one row."""
    count, = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE work_id='uw-uhb' AND verse=0").fetchone()
    assert count == 64
    # the title must equal what the WLC carries as its verse 1
    uhb, = conn.execute(
        "SELECT text FROM verses WHERE work_id='uw-uhb' AND book='Ps' AND chapter=39 AND verse=0"
    ).fetchone()
    wlc, = conn.execute(
        "SELECT text FROM verses WHERE work_id='morphhb-wlc' AND book='Ps' AND chapter=39 AND verse=1"
    ).fetchone()
    letters = lambda t: re.sub(
        r"[^א-ת]", "",
        "".join(c for c in unicodedata.normalize("NFD", t) if not unicodedata.combining(c)))
    assert letters(uhb) == letters(wlc)


def test_versification_map_beats_the_scheme_map(conn):
    r"""UHB records its Hebrew verse number in \va. That is stated evidence where
    versification.align() is an inference from verse counts, and the two disagree exactly where the
    inference breaks: at a chapter boundary. These two are the reference cases -- align() returns
    both references unchanged, which is wrong in both."""
    for book, chapter, verse, want_chapter, want_verse in [
        ("Jonah", 1, 17, 2, 1),      # align() leaves this at Jonah 1:17
        ("Job", 41, 2, 40, 26),      # align() leaves this at Job 41:2
        ("Gen", 31, 55, 32, 1),      # \va states the chapter outright here
    ]:
        row = conn.execute(
            "SELECT alt_chapter, alt_verse FROM versification_map "
            "WHERE work_id='uw-uhb' AND book=? AND chapter=? AND verse=?",
            (book, chapter, verse)).fetchone()
        assert row is not None, f"{book} {chapter}:{verse} missing from versification_map"
        assert (row["alt_chapter"], row["alt_verse"]) == (want_chapter, want_verse)


def test_versification_map_agrees_with_the_wlc_text(conn):
    """The map is only worth having if it lands on the verse the WLC actually carries. Compared on
    consonants alone, since the two editions divide words differently (maqqef vs word joiner) and a
    boundary-sensitive comparison reports differences that are not there. The residue is Ketiv/Qere
    -- the right verse, a different reading -- which is the point of the notes table."""
    letters = lambda t: re.sub(
        r"[^א-ת]", "",
        "".join(c for c in unicodedata.normalize("NFD", t) if not unicodedata.combining(c)))
    wlc = {(b, c, v): letters(t) for b, c, v, t in conn.execute(
        "SELECT book, chapter, verse, text FROM verses WHERE work_id='morphhb-wlc'")}
    uhb = {(b, c, v): letters(t) for b, c, v, t in conn.execute(
        "SELECT book, chapter, verse, text FROM verses WHERE work_id='uw-uhb'")}
    exact = near = 0
    for r in conn.execute("SELECT * FROM versification_map WHERE work_id='uw-uhb'"):
        mine = uhb.get((r["book"], r["chapter"], r["verse"]))
        theirs = wlc.get((r["book"], r["alt_chapter"], r["alt_verse"]))
        if mine is None or theirs is None:
            continue
        if mine == theirs:
            exact += 1
        elif difflib.SequenceMatcher(None, mine, theirs).ratio() >= 0.9:
            near += 1
    total, = conn.execute(
        "SELECT COUNT(*) FROM versification_map WHERE work_id='uw-uhb'").fetchone()
    assert exact >= 1820, f"only {exact} map rows land on identical WLC text"
    assert (exact + near) / total >= 0.99


def test_unverified_map_rows_are_labelled(conn):
    r"""A bare \va gives the verse but not the chapter, so the chapter is checked against the WLC
    text rather than trusted. Rows that match nothing keep their inferred chapter and must say so --
    silently presenting a guess as a stated fact is the failure this column exists to prevent."""
    sources = dict(conn.execute(
        "SELECT source, COUNT(*) FROM versification_map GROUP BY source"))
    assert set(sources) <= {"explicit", "verse+verified", "verse+unverified"}
    assert sources["explicit"] == 130
    assert sources.get("verse+unverified", 0) < 20
    # the great majority must be verified against the WLC, not left as a bare inference
    assert sources["verse+verified"] > 1800
