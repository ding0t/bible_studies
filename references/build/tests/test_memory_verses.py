"""The memory-card exporter's reading of STEPBible's tagged texts, against the real files."""
import pytest

import export_memory_verses as mv


def words_for(ref: str) -> list[dict]:
    r = mv.parse_ref(ref)
    book = mv.OSIS_TO_STEP[r["osis"]]
    rows = mv.tagged_rows(mv.tagged_file(r["num"], book), book, r["chapter"], range(r["start"], r["end"] + 1))
    if r["num"] >= mv.FIRST_NT_BOOK:
        return mv.greek_words(rows)
    return mv.hebrew_words(rows, r["osis"] in mv.POETIC_BOOKS)


def test_genesis_1_1_reads_seven_pointed_words_without_cantillation():
    words = words_for("Genesis 1:1")
    assert [w["w"] for w in words] == ["בְּרֵאשִׁית", "בָּרָא", "אֱלֹהִים", "אֵת", "הַשָּׁמַיִם", "וְאֵת", "הָאָרֶץ"]
    assert words[0]["t"] == ["be", "re", "shit"] and words[0]["s"] == 2


def test_a_capitalised_name_does_not_take_the_stress():
    assert mv.hebrew_syllables("'E.lo.Him") == (["'e", "lo", "him"], 2)


def test_a_prepositive_accent_in_the_poetic_books_marks_no_stress():
    assert mv.hebrew_syllables("Be./li.b/i", poetic=True) == (["be", "li", "bi"], None)
    assert mv.hebrew_syllables("'A.retz", poetic=False) == (["'a", "retz"], 0)


def test_qere_is_read_where_the_ketiv_differs():
    # Genesis 9:21 'his tent': Leningrad writes it ending in he, the scribes read vav.
    assert any(w["w"].endswith("וֹ") and w["g"] == "tent his" for w in words_for("Genesis 9:21"))


def test_greek_takes_only_the_nestle_aland_words():
    words = words_for("John 3:16")
    assert len(words) == 25
    assert words[0] == {"w": "οὕτως", "t": ["houtōs"], "s": None, "g": "Thus"}


def test_a_range_spans_its_verses():
    assert len(words_for("Proverbs 3:5-6")) == 15


def test_an_unknown_book_is_refused():
    with pytest.raises(ValueError):
        mv.parse_ref("Hezekiah 1:1")
