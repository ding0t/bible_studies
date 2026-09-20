"""Tests for research_batch.py.

The three properties under test are the ones the module exists for, and each corresponds to a real
failure this repo has already had:

- **partial success** -- an unreachable source must not fail the batch, because a failed batch is
  the pressure that pushes an agent toward recalled verse text.
- **an interruptible deadline** -- "slow" must be reportable as slow. A 60-100s scan read as a hung
  volume three times in one session before this existed.
- **no second implementation** -- a batch result and a single-tool result for the same request must
  be the same code path, so they cannot drift.
"""
import sqlite3
import time

import pytest

import query
import research_batch as rb
import study_notes_query as snq

HAS_STUDY_NOTES = snq.availability()["available"]
needs_study_notes = pytest.mark.skipif(
    not HAS_STUDY_NOTES, reason="study-notes.db not mounted"
)


# --- no second implementation ----------------------------------------------

def test_every_registry_entry_is_a_library_function():
    """Nothing in the registry may be defined in research_batch itself.

    The registry is a dispatch table over query.py / study_notes_query.py / twot_lookup.py. A
    callable defined here would be a second implementation of a lookup, which is precisely what
    the CLI/MCP split is built to prevent.
    """
    for name, spec in rb.REGISTRY.items():
        module = getattr(spec.fn, "__module__", "")
        assert module in {"query", "study_notes_query", "twot_lookup"}, \
            f"{name} dispatches to {module}, not a library module"


def test_batch_and_direct_call_agree():
    conn = query.connect()
    try:
        direct = query.lookup_verse(conn, "John", 6, 34)
    finally:
        conn.close()
    batched = rb.run_batch(
        [{"id": "v", "tool": "bible_verse", "args": {"book": "John", "chapter": 6, "verse": 34}}]
    )["results"]["v"]
    assert batched["status"] == "ok"
    assert batched["result"] == direct


def test_word_lookup_keeps_its_sanity_warning():
    """bible_word's lemma warning used to live in mcp_server, where a batch could not see it.

    It now lives in query.lookup_word_annotated, so both paths carry it. Without this the batch
    would silently return the bare count that once had a study reporting one occurrence of a word
    the text uses ten times.
    """
    out = rb.run_batch(
        [{"id": "w", "tool": "bible_word", "args": {"lemma": "δεῖ", "book": "John"}}]
    )["results"]["w"]
    assert out["status"] == "ok"
    assert "warning" in out["result"][0]


# --- partial success -------------------------------------------------------

def test_unavailable_source_does_not_fail_the_batch(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/definitely-not-mounted")
    out = rb.run_batch([
        {"id": "web", "tool": "bible_verse", "args": {"book": "John", "chapter": 6, "verse": 34}},
        {"id": "esv", "tool": "study_verse", "args": {"book": "John", "chapter": 6, "verse": 34}},
        {"id": "twot", "tool": "twot_strongs", "args": {"strongs_id": "H1"}},
    ])
    assert out["results"]["web"]["status"] == "ok"
    assert out["results"]["twot"]["status"] == "ok"
    assert out["results"]["esv"]["status"] == "unavailable"
    assert out["results"]["esv"]["remedy"], "an unavailable result must say how to fix it"


def test_a_bad_request_is_isolated():
    out = rb.run_batch([
        {"id": "good", "tool": "bible_verse", "args": {"book": "John", "chapter": 6, "verse": 34}},
        {"id": "bad", "tool": "bible_verse", "args": {"nonsense": True}},
    ])
    assert out["results"]["good"]["status"] == "ok"
    assert out["results"]["bad"]["status"] == "error"


def test_unknown_tool_reports_the_known_ones():
    out = rb.run_batch([{"id": "x", "tool": "no_such_tool", "args": {}}])["results"]["x"]
    assert out["status"] == "error"
    assert "bible_verse" in out["known_tools"]


def test_duplicate_ids_are_rejected_not_silently_overwritten():
    out = rb.run_batch([
        {"id": "same", "tool": "twot_strongs", "args": {"strongs_id": "H1"}},
        {"id": "same", "tool": "twot_strongs", "args": {"strongs_id": "H2"}},
    ])
    assert out["results"]["same"]["status"] == "error"
    assert "duplicate" in out["results"]["same"]["error"]


@needs_study_notes
def test_unindexed_request_is_refused_per_request():
    """study_notes_query's scan guard must survive batching -- it is the whole point of it."""
    out = rb.run_batch([
        {"id": "ok", "tool": "study_verse",
         "args": {"book": "John", "chapter": 6, "verse": 34}},
        {"id": "scan", "tool": "study_note", "args": {"book": "John", "chapter": None}},
    ])
    assert out["results"]["ok"]["status"] == "ok"
    assert out["results"]["scan"]["status"] == "error"
    assert "chapter is required" in out["results"]["scan"]["error"]


# --- the deadline ----------------------------------------------------------

def _sleep_step(_):
    time.sleep(0.005)
    return 1


def _burn_time(conn: sqlite3.Connection) -> int:
    """A registered lookup that exists only for the test below: 3000 rows, each carrying a 5ms
    Python-function sleep, so it is reliably slow regardless of disk speed or hardware.

    Used in place of a real production query because leaning on one's incidental slowness is
    exactly what broke this test once already -- study_works(with_counts=True) was ~90s over SMB
    and dropped well under any reasonable budget once study-notes.db moved to local disk.
    """
    conn.create_function("slow_step", 1, _sleep_step)
    return conn.execute(
        "WITH RECURSIVE cnt(x) AS (VALUES(0) UNION ALL SELECT x+1 FROM cnt WHERE x<3000) "
        "SELECT COUNT(*) FROM cnt WHERE slow_step(x)=1"
    ).fetchone()[0]


def test_slow_query_is_interrupted_and_reported_as_timed_out(monkeypatch):
    """A genuinely slow query must come back as timed_out well inside its natural completion time,
    or "slow" and "broken" stay indistinguishable -- the confusion this module was built to end
    (a 60-100s scan read as a hung volume three times in one session before it did).
    """
    monkeypatch.setitem(rb.REGISTRY, "_burn_time", rb.Spec(_burn_time, "bible-text"))
    started = time.monotonic()
    out = rb.run_batch(
        [{"id": "slow", "tool": "_burn_time", "args": {}}],
        budget_seconds=0.05,
    )
    elapsed = time.monotonic() - started
    assert out["results"]["slow"]["status"] == "timed_out"
    assert elapsed < 30, f"budget not enforced: took {elapsed:.1f}s"
    assert "budget" in out["results"]["slow"]["error"]


def test_requests_after_the_budget_are_skipped_not_run():
    out = rb.run_batch(
        [{"id": "a", "tool": "twot_strongs", "args": {"strongs_id": "H1"}}],
        budget_seconds=0,
    )
    assert out["results"]["a"]["status"] == "skipped"


# --- dedupe and accounting -------------------------------------------------

def test_identical_requests_execute_once():
    args = {"book": "John", "chapter": 6, "verse": 34}
    out = rb.run_batch([
        {"id": "first", "tool": "bible_verse", "args": args},
        {"id": "second", "tool": "bible_verse", "args": dict(args)},
    ])
    assert out["results"]["second"]["deduped_from"] == "first"
    assert out["results"]["second"]["result"] == out["results"]["first"]["result"]
    assert out["summary"]["executed"] == 1
    assert out["summary"]["deduped"] == 1


def test_summary_counts_every_request():
    out = rb.run_batch([
        {"id": "a", "tool": "twot_strongs", "args": {"strongs_id": "H1"}},
        {"id": "b", "tool": "no_such_tool", "args": {}},
    ])
    assert out["summary"]["requested"] == 2
    assert sum(out["summary"]["by_status"].values()) == 2


def test_oversized_batch_is_refused():
    out = rb.run_batch([{"id": str(i), "tool": "twot_strongs", "args": {"strongs_id": "H1"}}
                        for i in range(rb.MAX_REQUESTS + 1)])
    assert "error" in out


def test_non_list_requests_is_refused():
    assert "error" in rb.run_batch({"id": "x"})


def test_known_tools_covers_the_registry():
    assert set(rb.known_tools()) == set(rb.REGISTRY)
    assert set(rb.known_tools().values()) <= {"bible-text", "study-notes", "none"}
