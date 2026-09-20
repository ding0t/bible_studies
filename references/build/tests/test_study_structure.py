"""Tests for study_structure.py -- the measurements behind the read-bible-study skill.

The one that matters most is prose_identity. It is the check the whole readability pass rests on:
if it wrongly reports clean, a prose edit ships inside a "structure only" commit and nobody
re-verifies the study. So it is tested in both directions -- it must pass a real restructure that
changed no sentence, and it must fail an edit that changed one.
"""
import subprocess

import pytest

import study_structure as ss

SCRIBE = "docs/content/scripture/scribe-trained-for-the-kingdom.md"
# The commit that restructured the scribe study; its parent is the pre-restructure draft.
RESTRUCTURE = "c8bad96f"


def _text_at(ref: str, path: str = SCRIBE) -> str:
    return subprocess.run(["git", "-C", str(ss.REPO_ROOT), "show", f"{ref}:{path}"],
                          capture_output=True, text=True, check=True).stdout


# --- what counts as prose --------------------------------------------------

def test_tables_lists_quotes_and_code_are_not_prose():
    """Must match validate-content.js Check 21 exactly, or the tool and the check disagree about
    what a 600-word section is."""
    lines = [
        "Real prose here.",
        "| a | b |", "|---|---|",
        "> a block quote",
        "- a list item", "1. a numbered item",
        "```", "code = 1", "```",
        "More real prose.",
    ]
    assert ss._prose_lines(lines) == ["Real prose here.", "More real prose."]


def test_frontmatter_is_not_prose():
    body = ss._strip_frontmatter("---\ntitle: x\ndraft: true\n---\n\nThe body.\n")
    assert "title" not in body
    assert "The body." in body


# --- outline ---------------------------------------------------------------

def test_outline_measures_sections():
    out = ss.outline(SCRIBE)
    assert out["summary"]["sections"] > 0
    assert out["summary"]["median_words"] > 0
    for s in out["sections"]:
        assert s["verdict"] in {"ok", "long", "wall"}


def test_verdicts_follow_the_thresholds():
    out = ss.outline(SCRIBE)
    for s in out["sections"]:
        if s["words"] > ss.WARN_AT:
            assert s["verdict"] == "wall"
        elif s["words"] > ss.TARGET_MAX:
            assert s["verdict"] == "long"
        else:
            assert s["verdict"] == "ok"


def test_the_restructured_scribe_study_has_no_walls():
    """The pass that motivated all of this should leave nothing over 600 words."""
    assert ss.outline(SCRIBE)["summary"]["walls"] == 0


def test_missing_file_raises_rather_than_returning_empty():
    with pytest.raises(FileNotFoundError):
        ss.outline("docs/content/does-not-exist.md")


# --- prose identity: the check the pass rests on ---------------------------

def test_a_real_restructure_reports_no_sentence_changed():
    """Compared ref-to-ref (RESTRUCTURE against its own parent), not disk-to-ref: this test used
    to read the file's current working-tree content as the "after" side, which put a later,
    unrelated prose edit (commit d7d49da, restandardizing Key Takeaways) on the wrong side of the
    comparison and made a genuinely clean historical restructure look dirty. RESTRUCTURE's own
    snapshot can't drift out from under this test the way the working tree can."""
    result = ss._prose_diff(_text_at(f"{RESTRUCTURE}^"), _text_at(RESTRUCTURE))
    assert result["clean"] is True, result
    assert result["removed"] == []
    assert result["added_unexpected"] == []
    assert result["added_allowed"], "the one-line summary should show as a permitted addition"


def test_provenance_edits_do_not_register_as_prose_changes():
    """date_modified is rewritten by refresh_frontmatter_provenance.py on every run.

    The first draft of this tool compared frontmatter and reported that rewrite as a DELETED
    sentence -- the one finding it treats as always a defect. A verifier that cries wolf on a
    routine edit is a verifier people stop reading.
    """
    result = ss.prose_identity(SCRIBE, f"{RESTRUCTURE}^")
    joined = " ".join(result["removed"] + result["added_allowed"] + result["added_unexpected"])
    assert "date_modified" not in joined


def test_unchanged_file_is_clean_against_head():
    result = ss.prose_identity(SCRIBE, "HEAD")
    assert result["clean"] is True
    assert result["added_allowed"] == [] and result["added_unexpected"] == []


def test_a_changed_sentence_is_caught(tmp_path, monkeypatch):
    """The direction that matters: it must NOT report clean when prose changed."""
    target = ss.CONTENT_DIR / "scripture" / "_prose_identity_probe.md"
    original = (ss.REPO_ROOT / SCRIBE).read_text(encoding="utf-8")
    try:
        target.write_text(original, encoding="utf-8")
        # baseline: the probe does not exist at HEAD, so compare the real file to itself instead
        clean = ss.prose_identity(SCRIBE, "HEAD")
        assert clean["clean"] is True

        edited = original.replace("They say yes.", "They said yes, eventually.", 1)
        assert edited != original, "fixture sentence not found -- update the test"
        (ss.REPO_ROOT / SCRIBE).write_text(edited, encoding="utf-8")
        dirty = ss.prose_identity(SCRIBE, "HEAD")
        assert dirty["clean"] is False
        assert dirty["removed"], "the replaced sentence should show as removed"
        assert "PROSE CHANGED" in dirty["verdict"]
        assert dirty["note"] and "always a defect" in dirty["note"]
    finally:
        (ss.REPO_ROOT / SCRIBE).write_text(original, encoding="utf-8")
        target.unlink(missing_ok=True)


def test_unknown_ref_reports_an_error_not_a_crash():
    result = ss.prose_identity(SCRIBE, "no-such-ref-xyz")
    assert "error" in result


# --- corpus survey ---------------------------------------------------------

def test_survey_ranks_worst_first_and_lives_before_drafts(tmp_path, monkeypatch):
    """Synthetic fixture files, not the live corpus's current wall count -- asserting against that
    is not a stable invariant to test against. It hit zero the day this test's original
    `assert rows` broke, when a corpus-wide read-bible-study sweep fixed every remaining wall; the
    corpus reaching a clean state is success, not a reason this test should fail.
    """
    monkeypatch.setattr(ss, "CONTENT_DIR", tmp_path)
    long_section = "word " * 700
    (tmp_path / "probe_live.md").write_text(
        f"---\ndraft: false\n---\n\n## Section\n\n{long_section}\n", encoding="utf-8")
    (tmp_path / "probe_draft.md").write_text(
        f"---\ndraft: true\n---\n\n## Section\n\n{long_section}\n", encoding="utf-8")

    out = ss.survey(limit=50, include_drafts=True)
    rows = out["ranked"]
    names = [r["file"] for r in rows]
    assert "probe_live.md" in names and "probe_draft.md" in names
    assert names.index("probe_live.md") < names.index("probe_draft.md"), \
        "a live page a reader meets now outranks a draft"
    live_words = [r["worst_words"] for r in rows if not r["draft"]]
    assert live_words == sorted(live_words, reverse=True)


def test_survey_only_lists_files_that_need_a_pass():
    for row in ss.survey(limit=50)["ranked"]:
        assert row["worst_words"] > ss.WARN_AT


def test_survey_skips_generated_commentary_pages():
    files = {r["file"] for r in ss.survey(limit=200)["ranked"]}
    assert not any(f.startswith("commentaries/") for f in files)
