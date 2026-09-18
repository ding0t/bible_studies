"""Tests for evidence.py.

`claims:` already proved that a recorded query beats a remembered answer. Evidence widens that
from "SQL returning one number" to any registered tool call, which is what most of a study
actually rests on -- a quotation's wording, a gloss, a root number, whether a cross-reference is
really there.

The property these tests defend hardest is the separation of **wrong** from **untested**. If an
unmounted volume reported every ESV entry as FAIL, a routine local condition would produce a
screenful of red, and a verification tool people have learned to ignore is worse than none,
because it looks like cover.
"""
import pytest

import evidence as ev
import study_notes_query as snq

HAS_STUDY_NOTES = snq.availability()["available"]
needs_study_notes = pytest.mark.skipif(not HAS_STUDY_NOTES, reason="study-notes.db not mounted")


# --- path resolution -------------------------------------------------------

@pytest.mark.parametrize("value,path,expected", [
    ({"text": "hello"}, "text", "hello"),
    ([{"text": "hi"}], "0.text", "hi"),
    ({"rows": [{"lemma": "λόγος"}]}, "rows.0.lemma", "λόγος"),
    ({"text": "hello"}, None, {"text": "hello"}),
])
def test_resolve_path(value, path, expected):
    assert ev.resolve_path(value, path) == expected


def test_unresolvable_path_returns_none_rather_than_raising():
    """A path that stopped resolving is the drift being reported; it must surface as a failed
    assertion showing the real shape, not as a crash that hides every other entry."""
    assert ev.resolve_path({"text": "x"}, "rows.4.lemma") is None
    assert ev.resolve_path([], "0.text") is None


# --- assertions ------------------------------------------------------------

def test_expect_contains_passes_and_fails():
    entry = {"expect_contains": "Sir", "path": "0.text"}
    assert ev.evaluate(entry, [{"text": "They said, Sir, give us"}])[0] == ev.PASS
    status, detail = ev.evaluate(entry, [{"text": "They said, Lord, give us"}])
    assert status == ev.FAIL
    assert "Lord" in detail, "the failure must show what the source actually says"


def test_expect_absent_catches_a_reappearance():
    entry = {"expect_absent": "Lord"}
    assert ev.evaluate(entry, [{"text": "Sir, give us"}])[0] == ev.PASS
    assert ev.evaluate(entry, [{"text": "Lord, give us"}])[0] == ev.FAIL


def test_expect_count_is_exact():
    assert ev.evaluate({"expect_count": 3}, [1, 2, 3])[0] == ev.PASS
    status, detail = ev.evaluate({"expect_count": 3}, [1, 2])
    assert status == ev.FAIL and "got 2" in detail


def test_expect_min_allows_growth():
    """A corpus can gain rows; an exhaustiveness claim should not break on that alone."""
    assert ev.evaluate({"expect_min": 2}, [1, 2, 3])[0] == ev.PASS
    assert ev.evaluate({"expect_min": 5}, [1, 2])[0] == ev.FAIL


def test_expect_equals_compares_exactly():
    assert ev.evaluate({"expect_equals": 9, "path": "n"}, {"n": 9})[0] == ev.PASS
    assert ev.evaluate({"expect_equals": 9, "path": "n"}, {"n": 10})[0] == ev.FAIL


def test_entry_with_no_assertion_is_malformed():
    status, detail = ev.evaluate({"what": "nothing asserted"}, [1])
    assert status == ev.MALFORMED
    assert "expect_contains" in detail


def test_entry_with_two_assertions_is_malformed():
    """Two assertions in one entry hide which one failed."""
    status, detail = ev.evaluate({"expect_count": 1, "expect_contains": "x"}, [1])
    assert status == ev.MALFORMED
    assert "separate entries" in detail


def test_uncountable_target_fails_clearly():
    status, detail = ev.evaluate({"expect_count": 1, "path": "n"}, {"n": 5})
    assert status == ev.FAIL
    assert "countable" in detail


# --- replay ----------------------------------------------------------------

def test_check_entries_runs_real_lookups():
    records = ev.check_entries([
        {"id": "gram", "what": "γραμματεύς in Matthew",
         "tool": "bible_word", "args": {"lemma": "γραμματεύς", "book": "Matt"},
         "expect_count": 22},
    ])
    assert len(records) == 1
    assert records[0]["status"] == ev.PASS, records[0]["detail"]


def test_drifted_expectation_is_reported_with_the_real_value():
    records = ev.check_entries([
        {"id": "gram", "tool": "bible_word",
         "args": {"lemma": "γραμματεύς", "book": "Matt"}, "expect_count": 19},
    ])
    assert records[0]["status"] == ev.FAIL
    assert "got 22" in records[0]["detail"]


def test_unknown_tool_is_malformed_not_failed():
    records = ev.check_entries([{"id": "x", "tool": "nope", "args": {}, "expect_count": 1}])
    assert records[0]["status"] == ev.MALFORMED


def test_bad_args_is_malformed():
    records = ev.check_entries([{"id": "x", "tool": "bible_word", "args": "not a dict",
                                 "expect_count": 1}])
    assert records[0]["status"] == ev.MALFORMED


# --- the distinction the design turns on -----------------------------------

def test_unreachable_source_is_unverified_not_failed(monkeypatch):
    """An unmounted volume means the evidence could not be tested -- a different fact from the
    evidence being wrong, and it must read differently or the report becomes noise."""
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/definitely-not-mounted")
    records = ev.check_entries([
        {"id": "esv", "tool": "study_verse",
         "args": {"book": "John", "chapter": 6, "verse": 34, "work_id": "esv-study-bible"},
         "expect_contains": "Sir"},
        {"id": "open", "tool": "bible_word",
         "args": {"lemma": "γραμματεύς", "book": "Matt"}, "expect_count": 22},
    ])
    by_id = {r["id"]: r for r in records}
    assert by_id["esv"]["status"] == ev.UNVERIFIED
    assert "not mounted" in by_id["esv"]["detail"]
    assert by_id["open"]["status"] == ev.PASS, "an absent source must not stop the others"


def test_unverified_is_not_counted_as_a_failure(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/definitely-not-mounted")
    records = ev.check_entries([
        {"id": "esv", "tool": "study_verse",
         "args": {"book": "John", "chapter": 6, "verse": 34}, "expect_contains": "Sir"},
    ])
    counts = ev.summarise(records)
    assert counts.get(ev.FAIL, 0) == 0
    assert counts.get(ev.UNVERIFIED) == 1


# --- drafting --------------------------------------------------------------

def test_draft_produces_replayable_entries():
    """The adoption half: an entry for a call just made should cost nothing to record."""
    draft = ev.draft_entries([
        {"id": "ezra", "tool": "bible_verse",
         "args": {"book": "Ezra", "chapter": 7, "verse": 6, "translation": "WEB"}},
    ])
    entry = draft["evidence"][0]
    assert entry["tool"] == "bible_verse"
    assert entry.get("expect_contains")
    # and the draft must itself replay clean
    records = ev.check_entries([entry])
    assert records[0]["status"] == ev.PASS, records[0]["detail"]


def test_draft_marks_entries_it_could_not_run(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/definitely-not-mounted")
    draft = ev.draft_entries([
        {"id": "esv", "tool": "study_verse", "args": {"book": "John", "chapter": 6, "verse": 34}},
    ])
    assert "_skipped" in draft["evidence"][0]


# --- the committed block ---------------------------------------------------

def test_the_scribe_studys_evidence_still_holds():
    """A real committed block, replayed. Guards the shape as well as the facts."""
    path = ev.STATE_DIR / "scribe-trained-for-the-kingdom.yml"
    entries, parse_error = ev.load_evidence(path)
    assert parse_error is None
    assert entries, "the scribe study should carry an evidence block"
    records = ev.check_entries(entries)
    bad = [r for r in records if r["status"] in (ev.FAIL, ev.MALFORMED)]
    assert not bad, bad


def test_load_evidence_reports_a_bad_file_without_raising(tmp_path):
    path = tmp_path / "broken.yml"
    path.write_text("evidence: [unclosed\n", encoding="utf-8")
    entries, parse_error = ev.load_evidence(path)
    assert entries == [] and parse_error


def test_load_evidence_rejects_a_non_list(tmp_path):
    path = tmp_path / "wrong.yml"
    path.write_text("evidence: just a string\n", encoding="utf-8")
    entries, parse_error = ev.load_evidence(path)
    assert parse_error == "`evidence` is not a list"
