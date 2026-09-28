import pytest

import strongs_suggest as ss

pytestmark = pytest.mark.skipif(not ss.DB_PATH.exists(), reason="bible-text.db not built")


@pytest.fixture(scope="module")
def index():
    import sqlite3

    return ss.load_index(sqlite3.connect(ss.DB_PATH))


def test_untagged_glosses_are_reported_by_how_they_resolve(tmp_path, index):
    page = tmp_path / "study.md"
    page.write_text(
        "---\ntitle: t\n---\n"
        "The deposit is ἀρραβών (*arrabōn*, G728), and ἀρραβὼν (*arrabōn*) again.\n"
        "The verb is κατέχω (*katechō*), and ὁ κατέχων (*ho katechōn*) is a phrase.\n"
        "He stood, עָמַד (*amad*).\n"
        'Levi is <span dir="rtl">לֵוִי</span> *Lewi*, "attached".\n'
        "The count, οἰκονομία (9), is not a gloss.\n",
        encoding="utf-8",
    )
    report = ss.scan(page, *index)
    assert [(run, [sid for sid, _ in ids]) for _, run, _, ids in report["suggest"]] == [("κατέχω", ["G2722"])]
    assert "H5975" in [sid for sid, _ in report["ambiguous"][0][3]]
    assert [run for _, run, _ in report["phrase"]] == ["ὁ κατέχων"]
    assert [run for _, run, _ in report["unbracketed"]] == ["לֵוִי"]


def test_bare_words_are_reported_unless_tagged_quoted_or_glossed(tmp_path, index):
    page = tmp_path / "study.md"
    page.write_text(
        "---\ntitle: t\n---\n"
        "The deposit is ἀρραβών (*arrabōn*, G728), and the ἀρραβὼν comes back bare.\n"
        "The New Testament never uses δαιμονίζομαι of a Christian.\n"
        "Luke quotes λόγος καὶ δύναμις inline, a phrase.\n"
        "> ἐν ἀρχῇ ἦν ὁ λόγος\n"
        "Paul was διαπονηθείς (*diaponētheis*, from διαπονέω, G1278).\n"
        'The <span data-strongs="G1142">δαίμων</span> is tagged, so a later δαίμων is too.\n',
        encoding="utf-8",
    )
    bare = ss.scan(page, *index, site={"δαιμονιζομαι": {"G1139"}})["bare"]
    assert [(word, source, [sid for sid, _ in ids]) for _, word, source, ids in bare] == [
        ("δαιμονίζομαι", "site", ["G1139"])
    ]


def test_a_word_opening_its_own_gloss_tags_its_later_mentions(tmp_path, index):
    page = tmp_path / "study.md"
    page.write_text(
        "---\ntitle: t\n---\n"
        "It **remains** (μένω, *menō*, G3306), and later μένω comes back bare.\n"
        'A <span lang="grc" data-strongs="G406">Ἀνδρέας</span> row, then Ἀνδρέας again.\n',
        encoding="utf-8",
    )
    assert ss.scan(page, *index)["bare"] == []
