#!/usr/bin/env python3
"""Run many reference lookups in one call, over shared connections, with a deadline.

Why this exists
---------------
A single exegesis step is a dozen lookups: the verse in three translations, the interlinear, the
cross-references, the variants, the TWOT roots, the study notes. Issued one MCP call at a time
that is a dozen round trips, and -- worse -- a dozen `connect()` calls. On the SMB-mounted
study-notes.db, opening the connection is a large share of the cost of a fast indexed query, so
the per-call overhead dominates the actual work.

This module runs the same lookups against **one connection per database per batch**, and returns
results keyed by the caller's own ids.

Three properties matter more than the speed
-------------------------------------------
1. **Partial success is a first-class outcome.** One unreachable source must never fail the
   batch. The failure this repo has already lived through is an agent treating an unavailable
   source as a reason to fall back on recalled verse text; a batch that fails whole would create
   exactly that pressure. Every request carries its own `status`.

2. **A deadline that can actually interrupt.** `budget_seconds` is enforced with a SQLite progress
   handler, so a query that is genuinely slow is abandoned and reported as `timed_out` rather than
   hanging the call. "Slow" must be distinguishable from "broken" -- conflating them is what
   produced a three-times-repeated claim that a healthy NAS was hung.

3. **No second implementation.** Every entry in REGISTRY points at a `lookup_*` function in
   query.py, study_notes_query.py or twot_lookup.py -- the same functions the CLI and the
   individual MCP tools call. A batch result and a single-tool result for the same request are the
   same code path, so they cannot disagree.

Deliberately not in the registry
--------------------------------
`study_gaps` -- it takes a study file path rather than a passage, is run once per review rather
than per verse, and its orchestration currently lives in mcp_server.py. Batching it would buy
nothing and would mean either moving that logic or duplicating it. Recorded here rather than left
as an unexplained gap, per this repo's rule that an exemption carries its justification.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field

import query
import study_notes_query
import twot_lookup

DEFAULT_BUDGET_SECONDS = 30.0
MAX_REQUESTS = 100

# How often SQLite runs the progress handler, in VM instructions. Low enough that a long scan is
# interrupted promptly, high enough that the callback is not a measurable cost on fast queries.
_PROGRESS_INTERVAL = 2000


@dataclass(frozen=True)
class Spec:
    """One dispatchable lookup: which library function, and which database it needs."""
    fn: object
    source: str  # 'bible-text' | 'study-notes' | 'none'


REGISTRY: dict[str, Spec] = {
    # bible-text.db
    "bible_word": Spec(query.lookup_word_annotated, "bible-text"),
    "bible_concordance": Spec(query.lookup_concordance, "bible-text"),
    "bible_domain": Spec(query.lookup_domain, "bible-text"),
    "bible_verse": Spec(query.lookup_verse, "bible-text"),
    "bible_syntax": Spec(query.lookup_syntax, "bible-text"),
    "bible_passage": Spec(query.lookup_passage, "bible-text"),
    "bible_crossref": Spec(query.lookup_crossref, "bible-text"),
    "bible_parallel": Spec(query.lookup_parallel, "bible-text"),
    "bible_links": Spec(query.lookup_links, "bible-text"),
    "bible_interlinear": Spec(query.lookup_interlinear, "bible-text"),
    "bible_grammar": Spec(query.lookup_grammar, "bible-text"),
    "bible_variants": Spec(query.lookup_variants, "bible-text"),
    "bible_trace": Spec(query.lookup_trace, "bible-text"),
    "bible_align": Spec(query.lookup_alignment, "bible-text"),
    "bible_works": Spec(query.list_works, "bible-text"),
    # study-notes.db (quotation-only; records arrive tier-stamped)
    "study_verse": Spec(study_notes_query.lookup_verse, "study-notes"),
    "study_note": Spec(study_notes_query.lookup_note, "study-notes"),
    "study_intro": Spec(study_notes_query.lookup_intro, "study-notes"),
    "study_article": Spec(study_notes_query.lookup_article, "study-notes"),
    "study_works": Spec(study_notes_query.list_works, "study-notes"),
    # TWOT root map -- a JSON file, no connection
    "twot_root": Spec(twot_lookup.lookup_root, "none"),
    "twot_strongs": Spec(twot_lookup.lookup_strongs, "none"),
    "twot_lemma": Spec(twot_lookup.lookup_lemma, "none"),
}


class _Deadline:
    """Wall-clock budget for a whole batch."""

    def __init__(self, budget_seconds: float):
        self.budget = max(0.0, float(budget_seconds))
        self.started = time.monotonic()

    @property
    def remaining(self) -> float:
        return self.budget - (time.monotonic() - self.started)

    @property
    def expired(self) -> bool:
        return self.remaining <= 0


@dataclass
class _Connections:
    """One connection per database, opened on first use and reused for the whole batch.

    Reuse is the point: opening the connection costs a meaningful fraction of an indexed query
    (more so back when study-notes.db was NAS-mounted over SMB than now it's on local disk), so a
    dozen lookups that each connect pay that dozen times.
    """
    deadline: _Deadline
    _open: dict = field(default_factory=dict)
    _failed: dict = field(default_factory=dict)

    def get(self, source: str):
        """(conn, unavailable_dict). Exactly one is not None; 'none' yields (None, None)."""
        if source == "none":
            return None, None
        if source in self._failed:
            return None, self._failed[source]
        if source in self._open:
            return self._open[source], None
        try:
            conn = query.connect() if source == "bible-text" else study_notes_query.connect()
        except study_notes_query.SourceUnavailable as e:
            self._failed[source] = e.as_dict()
            return None, self._failed[source]
        except FileNotFoundError as e:
            self._failed[source] = {
                "available": False,
                "reason": str(e),
                "remedy": "Build it: `uv run python build.py` from references/build.",
            }
            return None, self._failed[source]
        conn.set_progress_handler(lambda: 1 if self.deadline.expired else 0, _PROGRESS_INTERVAL)
        self._open[source] = conn
        return conn, None

    def close(self):
        for conn in self._open.values():
            conn.set_progress_handler(None, 0)
            conn.close()
        self._open.clear()


def _dedupe_key(tool: str, args: dict) -> str:
    return json.dumps([tool, args], sort_keys=True, default=str)


def run_batch(requests: list[dict], budget_seconds: float = DEFAULT_BUDGET_SECONDS) -> dict:
    """Run typed lookups over shared connections.

    Each request is {"id": str, "tool": str, "args": dict}. Returns
    {"results": {id: {...}}, "summary": {...}}, where each result carries a `status` of
    ok | error | unavailable | timed_out | skipped, and `ok` results carry `result`.

    Identical (tool, args) pairs are executed once and the answer shared, so a batch assembled by
    unioning several passages' needs does not pay twice for the overlap.
    """
    if not isinstance(requests, list):
        return {"error": "requests must be a list of {id, tool, args} objects"}
    if len(requests) > MAX_REQUESTS:
        return {"error": f"{len(requests)} requests exceeds the {MAX_REQUESTS} limit"}

    deadline = _Deadline(budget_seconds)
    conns = _Connections(deadline)
    results: dict[str, dict] = {}
    seen: dict[str, str] = {}  # dedupe key -> id that actually ran it

    try:
        for index, request in enumerate(requests):
            rid = str(request.get("id") or f"r{index}")
            tool = request.get("tool")
            args = request.get("args") or {}

            if rid in results:
                results[rid] = {"status": "error", "error": f"duplicate request id {rid!r}"}
                continue
            if tool not in REGISTRY:
                results[rid] = {"status": "error",
                                "error": f"unknown tool {tool!r}",
                                "known_tools": sorted(REGISTRY)}
                continue
            if not isinstance(args, dict):
                results[rid] = {"status": "error", "error": "args must be an object"}
                continue

            key = _dedupe_key(tool, args)
            if key in seen:
                source_id = seen[key]
                results[rid] = dict(results[source_id]) | {"deduped_from": source_id}
                continue

            if deadline.expired:
                results[rid] = {"status": "skipped",
                                "error": f"batch budget of {deadline.budget}s exhausted before "
                                         f"this request ran"}
                continue

            spec = REGISTRY[tool]
            conn, unavailable = conns.get(spec.source)
            if unavailable is not None:
                results[rid] = {"status": "unavailable", "tool": tool, "source": spec.source,
                                **unavailable}
                continue

            started = time.monotonic()
            try:
                value = spec.fn(conn, **args) if conn is not None else spec.fn(**args)
            except sqlite3.OperationalError as e:
                # The progress handler aborts with "interrupted" when the budget runs out.
                timed_out = "interrupt" in str(e).lower()
                results[rid] = {
                    "status": "timed_out" if timed_out else "error",
                    "tool": tool,
                    "error": (f"exceeded the batch budget of {deadline.budget}s"
                              if timed_out else str(e)),
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                }
            except (ValueError, TypeError, KeyError) as e:
                # A caller-shaped mistake: bad arguments, an unindexed query study_notes_query
                # refuses, an unknown work id. Reported against the one request, never fatal.
                results[rid] = {"status": "error", "tool": tool, "error": str(e),
                                "elapsed_seconds": round(time.monotonic() - started, 3)}
            except study_notes_query.SourceUnavailable as e:
                results[rid] = {"status": "unavailable", "tool": tool, **e.as_dict()}
            else:
                results[rid] = {"status": "ok", "tool": tool, "result": value,
                                "elapsed_seconds": round(time.monotonic() - started, 3)}
                seen[key] = rid
    finally:
        conns.close()

    counts: dict[str, int] = {}
    for record in results.values():
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    return {
        "results": results,
        "summary": {
            "requested": len(requests),
            "executed": len(seen),
            "deduped": sum(1 for r in results.values() if "deduped_from" in r),
            "by_status": counts,
            "elapsed_seconds": round(deadline.budget - deadline.remaining, 3),
            "budget_seconds": deadline.budget,
        },
    }


def known_tools() -> dict[str, str]:
    """Tool name -> which database it reads. For error messages and documentation."""
    return {name: spec.source for name, spec in sorted(REGISTRY.items())}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("json_file", nargs="?",
                        help="file holding {\"requests\": [...], \"budget_seconds\": N}; "
                             "omit to list the dispatchable tools")
    parser.add_argument("--budget", type=float, default=DEFAULT_BUDGET_SECONDS)
    args = parser.parse_args()

    if not args.json_file:
        for name, source in known_tools().items():
            print(f"  {name:22} {source}")
        raise SystemExit(0)

    with open(args.json_file, encoding="utf-8") as f:
        payload = json.load(f)
    out = run_batch(payload.get("requests", payload), payload.get("budget_seconds", args.budget))
    print(json.dumps(out, indent=2, default=str))
