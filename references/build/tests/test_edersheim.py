"""Edersheim's Appendix IX, indexed by Old Testament reference (a file on the media volume)."""
import pytest

import edersheim
import source_catalog


@pytest.fixture(scope="module", autouse=True)
def appendix():
    path = source_catalog.profile_location("edersheim")
    if path is None or not path.is_file():
        pytest.skip(f"Edersheim not on the media volume ({path})")


def test_a_passage_is_found_under_its_own_reference():
    about = edersheim.lookup_edersheim("Mic", 5, 2)["about"]
    assert any("Micah v. 2, is admittedly Messianic" in p["text"] for p in about)


def test_a_verse_paragraph_continues_the_chapter_before_it():
    """'Verse 13 is applied in the Targum expressly to the Messiah' follows a paragraph that names
    Ps. cxxi. 1 only as the place Yalkut quotes Isaiah 52:7. The Psalm must not take over."""
    about = edersheim.lookup_edersheim("Isa", 52, 13)["about"]
    assert any(p["text"].startswith("Verse 13 is applied in the Targum expressly") for p in about)


def test_a_chapter_wide_paragraph_answers_for_each_verse():
    about = edersheim.lookup_edersheim("Ps", 110, 1)["about"]
    assert any(p["text"].startswith("Ps. cx. is throughout applied to the Messiah") for p in about)


def test_the_apocrypha_comparisons_are_not_entries():
    """'Ecclus. xlviii. 10, 11. See the comments on Is. lii. 7' is a comparison, not Isaiah's entry."""
    about = edersheim.lookup_edersheim("Isa", 52, 7)["about"]
    assert not any(p["text"].startswith("Ecclus.") for p in about)
