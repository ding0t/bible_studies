"""Tests for cross_study_claims.sibling_studies -- finding what other studies say about a chapter.

Run over a small synthetic corpus, since the question is whether a study is *found*, and the
failures are silent: a study the lookup misses is one a new study re-argues or contradicts.
"""
import cross_study_claims as csc


def page(fm: str, body: str) -> str:
    return f"---\ntitle: \"T\"\n{fm}\n---\n\n{body}\n"


CORPUS = [
    ("a/primary.md", page('primary_passage: "Psalm 23:1-4"\nbible_references: ["John 10:11"]',
                          "The shepherd of Psalm 23 leads.")),
    ("a/cited.md", page('primary_passage: "John 10:1-18"\nbible_references: ["Psalms 23:1"]',
                        "Nothing here.")),
    ("a/prose.md", page('primary_passage: "Ezekiel 34"', "Ezekiel echoes Psalm 23 directly.")),
    ("a/epistle.md", page('primary_passage: "1 John 3:1-3"', "1 John 3 is about adoption.")),
    ("a/draft.md", page('draft: true\nprimary_passage: "Psalm 23"', "Draft.")),
]


def test_singular_and_plural_psalm_are_one_chapter():
    found = {s["slug"]: s for s in csc.sibling_studies("Psalms", 23, corpus=CORPUS)}
    assert found["a/primary.md"]["role"] == "primary"
    assert found["a/cited.md"]["role"] == "cited"


def test_prose_only_mention_is_reported():
    """Older studies left bible_references empty; the prose is the only signal they give."""
    found = {s["slug"]: s for s in csc.sibling_studies("Ps", 23, corpus=CORPUS)}
    assert found["a/prose.md"]["role"] == "prose"
    assert found["a/prose.md"]["refs"] == []


def test_primary_studies_come_first_and_drafts_are_flagged():
    found = csc.sibling_studies("Psalm", 23, corpus=CORPUS)
    assert [s["role"] for s in found] == ["primary", "primary", "cited", "prose"]
    assert next(s for s in found if s["slug"] == "a/draft.md")["draft"] is True


def test_john_does_not_match_inside_1_john():
    assert [s["slug"] for s in csc.sibling_studies("John", 3, corpus=CORPUS)] == []
    assert [s["slug"] for s in csc.sibling_studies("1 John", 3, corpus=CORPUS)] == ["a/epistle.md"]


def test_exclude_leaves_out_the_study_being_written():
    slugs = [s["slug"] for s in csc.sibling_studies("Psalm", 23, exclude="a/primary.md",
                                                     corpus=CORPUS)]
    assert "a/primary.md" not in slugs
