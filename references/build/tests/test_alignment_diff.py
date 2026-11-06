"""The ULT-against-Berean comparison. The synthetic cases pin the logic; the real-data cases pin
that it finds what a reader would want it to."""

import pytest

import alignment_diff as ad
import alignment_ranking
import query
from query import DB_PATH


def row(english, content, occurrence=1):
    return {"english": english, "content": content, "occurrence": occurrence}


def test_a_word_rendered_with_no_shared_content_word_is_a_difference():
    result = ad.compare([[row("and empty", "וָבֹהוּ")]], [[row("and void", "וָבֹהוּ")]],
                        [["וָבֹהוּ"]], [["וָבֹהוּ"]], [2])
    assert [(d["ult"], d["bsb"], d["verse"]) for d in result["differences"]] == [("and empty", "and void", 2)]


def test_inflections_of_one_word_agree():
    result = ad.compare([[row("being justified", "δικαιούμενοι")]], [[row("[and are] justify", "δικαιούμενοι")]],
                        [["δικαιούμενοι"]], [["δικαιούμενοι"]], [3])
    assert result["agreed"] == 1 and not result["differences"]


def test_english_hung_on_an_article_is_not_a_textual_difference():
    """The ULT's nested frames put 'God' on the article τὸν; the Berean has no English there. Both
    base texts have the word, so it is an alignment artefact and must not be reported."""
    result = ad.compare([[row("God", "τὸν"), row("God", "Θεόν")]], [[row("God", "Θεόν")]],
                        [["τὸν", "Θεόν"]], [["τὸν", "Θεόν"]], [1])
    assert not result["differences"] and not result["text_differs"]


def test_a_word_only_one_base_text_has_is_reported_as_that():
    result = ad.compare([[]], [[row("A Psalm", "מִזְמוֹר")]], [[]], [["מִזְמוֹר"]], [1])
    assert [(d["kind"], d["original"]) for d in result["text_differs"]] == [("Berean only", "מִזְמוֹר")]


def test_a_word_moved_across_a_verse_boundary_cancels_over_the_range():
    one_verse = ad.compare([[], [row("forbearance", "ἀνοχῇ")]], [[row("forbearance", "ἀνοχῇ")], []],
                           [[], ["ἀνοχῇ"]], [["ἀνοχῇ"], []], [25, 26])
    assert not one_verse["text_differs"] and one_verse["agreed"] == 1


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    c = query.connect()
    yield c
    c.close()


def test_romans_3_25_propitiation_is_flagged(conn):
    r = query.lookup_alignment_diff(conn, "Rom", 3, 21, 26)
    flagged = {d["original"]: d for d in r["differences"]}
    assert "ἱλαστήριον" in flagged
    assert "propitiation" in flagged["ἱλαστήριον"]["ult"] and "atoning" in flagged["ἱλαστήριον"]["bsb"]
    assert not r["text_differs"]


def test_psalm_51_title_is_a_base_text_difference(conn):
    r = query.lookup_alignment_diff(conn, "Ps", 51, 1)
    assert any(d["kind"] == "Berean only" and "Bathsheba" in d["english"] for d in r["text_differs"])


def test_the_result_is_the_same_every_time(conn):
    assert query.lookup_alignment_diff(conn, "John", 1, 1, 5) == query.lookup_alignment_diff(conn, "John", 1, 1, 5)


def test_ranking_orders_by_how_often_a_word_differs_and_drops_rare_words():
    tally = [("H2617", False, "covenant faithfulness", "loving devotion")] * 9 + [("H2617", True, "x", "x")]
    tally += [("H776", False, "land", "earth")] * 3 + [("H776", True, "x", "x")] * 7
    tally += [("H1", False, "father", "dad")] * 2
    ranked = alignment_ranking.rank(tally, minimum=5)
    assert [r["strong"] for r in ranked] == ["H2617", "H776"]
    assert ranked[0]["ult"].most_common(1) == [("covenant faithfulness", 9)]


def test_a_study_is_told_about_a_tagged_word_the_translations_disagree_on(tmp_path):
    from collections import Counter
    page = tmp_path / "study.md"
    page.write_text("---\ntitle: t\n---\nHis חֶסֶד (*chesed*, H2617) and the אֶרֶץ (*erets*, H776).\n", encoding="utf-8")
    rows = [{"strong": "H2617", "n": 10, "differ": 9, "ult": Counter({"covenant faithfulness": 9}),
             "bsb": Counter({"loving devotion": 9})},
            {"strong": "H776", "n": 10, "differ": 2, "ult": Counter({"land": 2}), "bsb": Counter({"earth": 2})}]
    found = alignment_ranking.study_words(page, rows, {})
    assert len(found) == 1 and found[0].startswith("H2617") and "no recorded decision" in found[0]
    decided = alignment_ranking.study_words(page, rows, {"H2617": {"kind": "interpretive", "follow": "steadfast love",
                                                                   "why": "ESV", "status": "proposed"}})
    assert "site follows 'steadfast love'" in decided[0]

