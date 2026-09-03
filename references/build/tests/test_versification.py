"""Cross-scheme reference alignment.

(book, chapter, verse) means different things in different works, and getting it wrong is silent:
before versification.py existed, lookup_verse('Joel', 3, 1, 'WEB') returned the English text of
Joel 3:1 with the Hebrew morphology of Joel 3:1 attached -- and Hebrew Joel 3:1 is English Joel
2:28, the verse Acts 2 quotes. Two different verses, presented as one, with no warning.

The rules in versification.py were each derived from this database rather than from a reference
table, so these tests check them back against it.
"""
import sqlite3
import unicodedata
from pathlib import Path

import pytest

import query
import versification
from versification import align

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"
WLC, WEB, LXX = "morphhb-wlc", "ebible-eng-web", "ebible-grcbrent"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = query.connect()
    yield connection
    connection.close()


def chapter_lengths(conn, work_id, book):
    return dict(conn.execute(
        "SELECT chapter, COUNT(*) FROM verses WHERE work_id=? AND book=? GROUP BY chapter",
        (work_id, book),
    ).fetchall())


def test_every_work_declares_a_scheme(conn):
    bad = conn.execute(
        "SELECT work_id FROM works WHERE versification IS NULL OR versification NOT IN (?,?,?)",
        versification.SCHEMES,
    ).fetchall()
    assert not [r["work_id"] for r in bad]


@pytest.mark.parametrize("book,chapter,verse,scheme_a,scheme_b,expected", [
    # the English tradition is the outlier in Joel and Malachi -- the LXX keeps the Hebrew division
    ("Joel", 3, 1, "masoretic", "english", ("Joel", 2, 28)),
    ("Joel", 4, 1, "masoretic", "english", ("Joel", 3, 1)),
    ("Joel", 3, 1, "lxx", "english", ("Joel", 2, 28)),
    ("Joel", 3, 1, "masoretic", "lxx", ("Joel", 3, 1)),
    ("Mal", 3, 19, "masoretic", "english", ("Mal", 4, 1)),
    ("Mal", 3, 19, "lxx", "english", ("Mal", 4, 1)),
    # Daniel: here it is the Masoretic that is the outlier; english and lxx agree
    ("Dan", 3, 31, "masoretic", "english", ("Dan", 4, 1)),
    ("Dan", 4, 1, "masoretic", "english", ("Dan", 4, 4)),
    # Psalms: the lxx renumbers nearly the whole psalter
    ("Ps", 23, 1, "english", "lxx", ("Ps", 22, 1)),
    ("Ps", 9, 22, "lxx", "english", ("Ps", 10, 1)),
    ("Ps", 113, 9, "lxx", "english", ("Ps", 115, 1)),
    ("Ps", 147, 1, "lxx", "english", ("Ps", 147, 12)),
    ("Ps", 150, 1, "lxx", "english", ("Ps", 150, 1)),
    ("Gen", 1, 1, "lxx", "masoretic", ("Gen", 1, 1)),
])
def test_known_alignments(book, chapter, verse, scheme_a, scheme_b, expected):
    assert align(book, chapter, verse, scheme_a, scheme_b) == expected


@pytest.mark.parametrize("book,chapter,verse,scheme", [
    ("Ps", 151, 1, "lxx"),      # supernumerary psalm
    ("Prov", 24, 40, "lxx"),    # the Agur material relocated into LXX Proverbs 24's tail
    ("Jer", 30, 1, "lxx"),      # oracles reordered within the chapter
])
def test_passages_with_no_english_counterpart(book, chapter, verse, scheme):
    assert align(book, chapter, verse, scheme, "english") is None


@pytest.mark.parametrize("book,chapter,verse", [
    ("Joel", 3, 1), ("Joel", 4, 21), ("Mal", 3, 24), ("Dan", 4, 34), ("Gen", 1, 1),
])
def test_alignment_round_trips(book, chapter, verse):
    english = align(book, chapter, verse, "masoretic", "english")
    assert align(*english, "english", "masoretic") == (book, chapter, verse)


@pytest.mark.parametrize("book,scheme,work_id", [
    ("Joel", "masoretic", WLC), ("Joel", "lxx", LXX), ("Mal", "masoretic", WLC), ("Mal", "lxx", LXX),
    ("Jer", "lxx", LXX), ("Dan", "masoretic", WLC),
    # Psalms is deliberately absent: its chapter mapping is right, but the superscription counted
    # as verse 1 in Hebrew and Greek is not modelled, so a verse can legitimately overrun the
    # English chapter by one or two. That limitation gets its own test below.
])
def test_rules_agree_with_what_the_works_actually_contain(conn, book, scheme, work_id):
    """A rule that maps into an English chapter which is too short to hold the verse is wrong.
    This catches a mis-typed delta, which the hand-written cases above cannot."""
    english = chapter_lengths(conn, WEB, book)
    for chapter, length in chapter_lengths(conn, work_id, book).items():
        for verse in (1, length):
            mapped = align(book, chapter, verse, scheme, "english")
            if mapped is None:
                continue
            _, e_chapter, e_verse = mapped
            assert e_chapter in english, f"{book} {chapter}:{verse} -> missing English chapter {e_chapter}"
            assert 1 <= e_verse <= english[e_chapter], (
                f"{book} {chapter}:{verse} -> {e_chapter}:{e_verse}, but English {book} "
                f"{e_chapter} has {english[e_chapter]} verses")


def test_lookup_verse_attaches_morphology_from_the_aligned_reference(conn):
    """The original bug, pinned. English Joel 3:1 must not carry Hebrew Joel 3:1's morphology."""
    english = query.lookup_verse(conn, "Joel", 3, 1, "WEB")
    assert english["versification"] == "english"
    assert english["aligned_references"]["masoretic"] == "Joel 4:1"
    glosses = " ".join(str(m["gloss"]) for m in english["morphology"])
    assert "pour.out" not in glosses, "picked up Hebrew Joel 3:1, which is English Joel 2:28"

    # and the verse that genuinely is the Hebrew's Joel 3:1
    acts_quote = query.lookup_verse(conn, "Joel", 2, 28, "WEB")
    assert "pour.out" in " ".join(str(m["gloss"]) for m in acts_quote["morphology"])


def test_lookup_verse_reports_no_alignment_when_none_is_needed(conn):
    assert "aligned_references" not in query.lookup_verse(conn, "Gen", 1, 1, "WEB")


def test_crossref_lookup_aligns_the_query_reference(conn):
    """The cross-reference data is numbered in the english scheme. Hebrew Joel 3:1 is the verse
    Peter quotes at Pentecost, so aligned it must reach Acts 2; taken at face value it returns the
    links for english Joel 3:1, a different verse entirely."""
    aligned = query.lookup_crossref(conn, "Joel", 3, 1, from_scheme="masoretic", limit=5)
    assert any(r["to_book"] == "Acts" and r["to_chapter"] == 2 for r in aligned)

    unaligned = query.lookup_crossref(conn, "Joel", 3, 1, limit=5)
    assert not any(r["to_book"] == "Acts" for r in unaligned)


def test_crossref_returns_nothing_for_a_verse_the_english_scheme_lacks(conn):
    assert query.lookup_crossref(conn, "Ps", 151, 1, from_scheme="lxx") == []


@pytest.mark.parametrize("chapter,verse", [
    (3, 11), (11, 31), (24, 12), (24, 34), (25, 21), (29, 1), (31, 10),
])
def test_lxx_proverbs_keeps_the_hebrew_numbering(chapter, verse):
    """Brenton preserves the Hebrew verse numbers and omits what the LXX lacks -- chapter 20 runs
    to verse 30 with 14-22 absent, chapter 31 opens at verse 10 -- so a shorter chapter here is
    not a renumbered one. Six NT quotations confirm it independently."""
    assert align("Prov", chapter, verse, "lxx", "english") == ("Prov", chapter, verse)


def test_lxx_proverbs_relocated_agur_material_is_unmapped():
    """Chapter 24 runs to verse 62, its tail carrying what English prints as chapter 30."""
    assert align("Prov", 24, 35, "lxx", "english") is None
    assert align("Prov", 24, 62, "lxx", "english") is None


def test_english_proverbs_thirty_has_no_lxx_counterpart():
    """There is no LXX Proverbs 30 at all. Without an explicit absence the reverse lookup would
    fall through and hand back a reference to a chapter that does not exist."""
    assert align("Prov", 30, 1, "english", "lxx") is None
    assert align("Prov", 31, 10, "english", "lxx") == ("Prov", 31, 10)


@pytest.mark.parametrize("lxx_chapter,verse,english_chapter", [
    (38, 32, 31), (38, 33, 31), (38, 34, 31),   # Hebrews 8:9-11 anchor this block
    (1, 1, 1), (24, 1, 24),                      # the unshifted opening block
    (33, 1, 26), (51, 1, 44),                    # the -7 block's edges
])
def test_lxx_jeremiah_mapped_blocks(lxx_chapter, verse, english_chapter):
    assert align("Jer", lxx_chapter, verse, "lxx", "english") == ("Jer", english_chapter, verse)


def test_lxx_psalms_chapter_mapping_is_right_but_verse_level_is_not_modelled(conn):
    """The documented limit: chapters map, verses may not. Hebrew and Greek count a psalm's
    superscription as verse 1 and most English editions do not, and that is a per-digitisation
    choice rather than a scheme property, so it is not encoded. Callers comparing psalm verse
    numbers across schemes have to check."""
    lxx = chapter_lengths(conn, LXX, "Ps")
    english = chapter_lengths(conn, WEB, "Ps")
    overruns = [n for n in range(1, 151)
                if (m := align("Ps", n, lxx.get(n, 1), "lxx", "english"))
                and m[2] > english.get(m[1], 0)]
    assert overruns, "expected the superscription offset to still be visible"
    assert all(lxx[n] - english[align("Ps", n, 1, "lxx", "english")[1]] <= 2 for n in overruns)


def test_hebrews_new_covenant_quotation_resolves(conn):
    """The concrete payoff: Hebrews 8 quotes the new covenant passage, which the LXX numbers as
    Jeremiah 38 and every English Bible as Jeremiah 31."""
    _, chapter, verse = align("Jer", 38, 31, "lxx", "english")
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id='ebible-eng-web' AND book='Jer' AND chapter=? AND verse=?",
        (chapter, verse)).fetchone()[0]
    assert "new covenant" in text.lower()


# LXX Jeremiah's relocated oracles, each chapter identified by the nation it is against -- Greek
# and English proper nouns agreeing, then verse deltas confirmed by verse-by-verse name matching.
@pytest.mark.parametrize("lxx_chapter,english_chapter,nation", [
    (26, 46, "Egypt"), (27, 50, "Babylon"), (28, 51, "Babylon"),
    (29, 47, "the Philistines"), (31, 48, "Moab"),
])
def test_lxx_jeremiah_oracle_chapters(lxx_chapter, english_chapter, nation):
    assert align("Jer", lxx_chapter, 1, "lxx", "english") == ("Jer", english_chapter, 1)


@pytest.mark.parametrize("lxx_ref,english_ref", [
    ((25, 1), (25, 1)), ((25, 14), (49, 34)), ((25, 19), (49, 39)),   # the Elam oracle
    ((32, 15), (25, 15)), ((32, 38), (25, 38)),                        # the cup of wrath
    ((52, 1), (52, 1)),
])
def test_lxx_jeremiah_split_chapters(lxx_ref, english_ref):
    assert align("Jer", *lxx_ref, "lxx", "english") == ("Jer", *english_ref)


@pytest.mark.parametrize("chapter,verse", [(30, 1), (30, 20), (25, 20)])
def test_lxx_jeremiah_genuinely_unmappable_parts(chapter, verse):
    """Chapter 30's sub-oracles are reordered inside the chapter, so no delta holds; 25:20 is a
    displaced Elam superscription whose English slot 49:34 is already occupied."""
    assert align("Jer", chapter, verse, "lxx", "english") is None


def test_lxx_jeremiah_content_matches_where_mapped(conn):
    """Spot-check that a mapped reference actually lands on the same text in both works, using a
    proper noun that survives translation."""
    for lxx_ch, lxx_v, name_gk, name_en in [(26, 2, "αιγυπτ", "Egypt"), (31, 1, "μωαβ", "Moab")]:
        greek = conn.execute(
            "SELECT text FROM verses WHERE work_id=? AND book='Jer' AND chapter=? AND verse=?",
            (LXX, lxx_ch, lxx_v)).fetchone()[0]
        _, e_ch, e_v = align("Jer", lxx_ch, lxx_v, "lxx", "english")
        english = conn.execute(
            "SELECT text FROM verses WHERE work_id=? AND book='Jer' AND chapter=? AND verse=?",
            (WEB, e_ch, e_v)).fetchone()[0]
        flat = "".join(ch for ch in unicodedata.normalize("NFD", greek)
                       if not unicodedata.combining(ch)).lower()
        assert name_gk in flat and name_en in english


@pytest.mark.parametrize("mt_ref,english_ref", [
    ((6, 1), (5, 31)),      # "Darius the Mede received the kingdom" closes English chapter 5
    ((6, 2), (6, 1)), ((6, 29), (6, 28)),
])
def test_masoretic_daniel_five_six_boundary(mt_ref, english_ref):
    """The Daniel chapter break moves twice, not once. 3/4 was known; 5/6 shifts the same way."""
    assert align("Dan", *mt_ref, "masoretic", "english") == ("Dan", *english_ref)


@pytest.mark.parametrize("lxx_ref,english_ref", [
    ((51, 1), (44, 1)), ((51, 30), (44, 30)),   # the body stays in English chapter 44
    ((51, 31), (45, 1)), ((51, 35), (45, 5)),   # the word to Baruch becomes English chapter 45
])
def test_lxx_jeremiah_fiftyone_splits(lxx_ref, english_ref):
    assert align("Jer", *lxx_ref, "lxx", "english") == ("Jer", *english_ref)


@pytest.mark.parametrize("scheme", ["masoretic", "lxx"])
def test_daniel_five_six_boundary_applies_to_both_original_language_schemes(scheme):
    """Daniel divides differently in each direction, so neither "the LXX follows the Hebrew" nor
    "the LXX follows the English" is safe. At 3/4 the LXX sides with English; at 5/6 it sides with
    the Hebrew -- LXX Daniel 6:1 is verbatim English 5:31."""
    assert align("Dan", 6, 1, scheme, "english") == ("Dan", 5, 31)
    assert align("Dan", 6, 2, scheme, "english") == ("Dan", 6, 1)


# --- verse-level alignment between two named works -------------------------------------------
# versification.align handles the chapter, which belongs to the scheme. The verse offset does not:
# Hebrew and Greek count a psalm's superscription as verse 1 and most English editions don't, and
# which a given edition does is a per-digitisation choice (scrollmapper-KJV counts them and differs
# from ebible-eng-web in 116 psalms). So lookup_parallel measures it between the two works named.

@pytest.mark.parametrize("en_ref,lxx_ref,quoted_by", [
    ((40, 6), (39, 7), "Hebrews 10:5"),      # "a body you have prepared for me"
    ((40, 7), (39, 8), "Hebrews 10:7"),
    ((45, 6), (44, 7), "Hebrews 1:8"),
    ((102, 25), (101, 26), "Hebrews 1:10"),
    ((22, 22), (21, 23), "Hebrews 2:12"),
    ((69, 22), (68, 23), "Romans 11:9"),
    ((110, 1), (109, 1), "Matthew 22:44"),   # no superscription -- offset 0
    ((118, 22), (117, 22), "Matthew 21:42"),
])
def test_english_psalm_resolves_to_the_lxx_verse_the_nt_quotes(conn, en_ref, lxx_ref, quoted_by):
    result = query.lookup_parallel(conn, "Ps", *en_ref, source="WEB", target="Brenton-LXX")
    assert result["target"] == f"Ps {lxx_ref[0]}:{lxx_ref[1]}", f"({quoted_by})"
    assert result["text"], "aligned to a verse that has no text"


def test_hebrews_ten_five_finds_the_body_reading(conn):
    """The case that exposed the gap. English Psalm 40:6 reads 'you have opened my ears'; the LXX
    verse Hebrews quotes reads 'a body you prepared for me'. Landing one verse early returns
    neither."""
    lxx = query.lookup_parallel(conn, "Ps", 40, 6, source="WEB", target="Brenton-LXX")
    assert "σῶμα" in lxx["text"]
    mt = query.lookup_parallel(conn, "Ps", 40, 6, source="WEB", target="WLC")
    assert "אָ֭זְנַיִם" in mt["text"] or "אזנים" in "".join(
        ch for ch in unicodedata.normalize("NFD", mt["text"]) if not unicodedata.combining(ch))


def test_parallel_does_not_shift_when_the_gap_is_too_large_to_be_a_superscription(conn):
    """A one- or two-verse gap is the title. A larger one means the target omits verses somewhere
    else, and a front-shift would be the wrong correction -- so none is applied."""
    result = query.lookup_parallel(conn, "Prov", 20, 1, source="WEB", target="Brenton-LXX")
    assert "verse_offset" not in result


def test_parallel_reports_when_the_target_has_no_counterpart(conn):
    result = query.lookup_parallel(conn, "Prov", 30, 1, source="WEB", target="Brenton-LXX")
    assert "warning" in result and result.get("target") is None
