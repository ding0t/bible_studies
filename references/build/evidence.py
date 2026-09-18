#!/usr/bin/env python3
"""Replayable evidence: a study's lookups recorded as assertions, re-run on demand.

The problem this finishes solving
---------------------------------
verify_claims.py already proved the idea: a number written into prose drifts from the query that
produced it, so the query gets recorded in the state file with its expected answer and re-run.
Every Critical finding this repo has produced came from that same place -- a fact queried once,
written down, and never checked again.

But `claims:` only accepts **SQL returning a single number**, which is a narrow slice of what a
study actually rests on. A quotation's wording, a lexicon gloss, a TWOT root number, whether a
cross-reference exists -- none of them reduce to one integer, so none of them were checkable, and
only 9 of 43 state files ever grew a `claims:` block. Writing SQL by hand for each is work; that
is why adoption stalled.

`evidence:` records a **tool call** instead -- the same call the agent already made while
researching -- with what the answer should contain:

    evidence:
      - id: john-6-34-esv
        what: the ESV reads "Sir", not "Lord"
        tool: study_verse
        args: {book: John, chapter: 6, verse: 34, work_id: esv-study-bible}
        expect_contains: "Sir, give us this bread always"
        checked: 2026-09-18

Nothing here is a new capability: `tool` is any name in research_batch.REGISTRY, so replaying a
study's evidence is one batch, over shared connections, under one deadline.

Unavailable is not failed
-------------------------
The distinction this whole line of work turns on. If the external volume is not mounted, every
piece of ESV evidence is **unverified**, not **failed**. Reporting those as failures would make an
unmounted drive produce a screenful of red, which teaches a reader to ignore the tool -- and a
verification tool nobody reads is worse than none, because it looks like cover.

This module is read-only. It never writes `checked:` back into a state file: the dates are
authored when the evidence is recorded, and a verifier that edits its own inputs cannot be trusted
to report on them.
"""
from __future__ import annotations

import json
import pathlib

import research_batch

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
STATE_DIR = REPO_ROOT / "references" / "study-state"

ASSERTIONS = ("expect_contains", "expect_absent", "expect_equals", "expect_count", "expect_min")

# Result statuses, in report order. 'unverified' is deliberately not a failure -- see the docstring.
PASS, FAIL, UNVERIFIED, MALFORMED = "ok", "FAIL", "unverified", "malformed"


def resolve_path(value, path: str | None):
    """Walk a dotted path into a result. '0.text' -> value[0]['text'].

    Integer-looking segments index lists, everything else keys dicts. A miss returns None rather
    than raising: a path that no longer resolves is itself the drift being reported, and it should
    show up as a failed assertion with the actual shape, not as a crash.
    """
    if not path:
        return value
    current = value
    for segment in str(path).split("."):
        if current is None:
            return None
        try:
            if isinstance(current, (list, tuple)):
                current = current[int(segment)]
            elif isinstance(current, dict):
                current = current.get(segment)
            else:
                return None
        except (ValueError, IndexError, KeyError, TypeError):
            return None
    return current


def _haystack(value) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def evaluate(entry: dict, result) -> tuple[str, str]:
    """(status, detail) for one evidence entry against the value its tool returned."""
    used = [k for k in ASSERTIONS if k in entry]
    if not used:
        return MALFORMED, f"no assertion; expected one of {', '.join(ASSERTIONS)}"
    if len(used) > 1:
        return MALFORMED, f"more than one assertion ({', '.join(used)}); split into separate entries"

    kind = used[0]
    expected = entry[kind]
    target = resolve_path(result, entry.get("path"))

    if kind == "expect_contains":
        text = _haystack(target)
        if str(expected) in text:
            return PASS, f"found {expected!r}"
        return FAIL, f"{expected!r} not present; got {text[:160]!r}"

    if kind == "expect_absent":
        text = _haystack(target)
        if str(expected) not in text:
            return PASS, f"{expected!r} absent, as recorded"
        return FAIL, f"{expected!r} IS present -- the claim that it is absent no longer holds"

    if kind == "expect_equals":
        if target == expected:
            return PASS, f"{target!r}"
        return FAIL, f"expected {expected!r}, got {target!r}"

    if kind in ("expect_count", "expect_min"):
        try:
            count = len(target)
        except TypeError:
            return FAIL, f"expected something countable at path {entry.get('path')!r}, got {target!r}"
        if kind == "expect_count":
            if count == expected:
                return PASS, f"{count}"
            return FAIL, f"expected {expected}, got {count}"
        if count >= expected:
            return PASS, f"{count} (at least {expected})"
        return FAIL, f"expected at least {expected}, got {count}"

    return MALFORMED, f"unhandled assertion {kind!r}"  # unreachable; kept so a new kind fails loudly


def load_evidence(path: pathlib.Path) -> tuple[list[dict], str | None]:
    """(entries, parse_error). A malformed state file is reported, never fatal."""
    import yaml
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return [], str(e).split("\n")[0]
    entries = data.get("evidence") or []
    if not isinstance(entries, list):
        return [], "`evidence` is not a list"
    return entries, None


def check_entries(entries: list[dict], budget_seconds: float = 60.0) -> list[dict]:
    """Replay evidence entries in one batch and evaluate each.

    Returns one record per entry: {id, what, status, detail, tool}.
    """
    requests, index = [], {}
    records: list[dict] = []
    for position, entry in enumerate(entries):
        eid = str(entry.get("id") or f"e{position}")
        tool = entry.get("tool")
        if tool not in research_batch.REGISTRY:
            records.append({"id": eid, "what": entry.get("what", ""), "tool": tool,
                            "status": MALFORMED,
                            "detail": f"unknown tool {tool!r}"})
            continue
        if not isinstance(entry.get("args"), dict):
            records.append({"id": eid, "what": entry.get("what", ""), "tool": tool,
                            "status": MALFORMED, "detail": "args must be a mapping"})
            continue
        rid = f"{position}:{eid}"
        requests.append({"id": rid, "tool": tool, "args": entry["args"]})
        index[rid] = (eid, entry)

    if requests:
        batch = research_batch.run_batch(requests, budget_seconds=budget_seconds)
        for rid, (eid, entry) in index.items():
            outcome = batch["results"].get(rid, {})
            status = outcome.get("status")
            base = {"id": eid, "what": entry.get("what", ""), "tool": entry.get("tool")}
            if status == "ok":
                verdict, detail = evaluate(entry, outcome["result"])
                records.append(base | {"status": verdict, "detail": detail})
            elif status in ("unavailable", "timed_out", "skipped"):
                # Not a failure: the evidence could not be tested, which is a different fact from
                # the evidence being wrong, and must read differently.
                records.append(base | {
                    "status": UNVERIFIED,
                    "detail": f"{status}: {outcome.get('reason') or outcome.get('error', '')}",
                })
            else:
                records.append(base | {"status": FAIL,
                                       "detail": f"lookup failed: {outcome.get('error', 'unknown')}"})

    order = {r["id"]: i for i, r in enumerate(records)}
    return sorted(records, key=lambda r: order[r["id"]])


def draft_entries(requests: list[dict], budget_seconds: float = 30.0) -> dict:
    """Run lookups and return them as evidence entries ready to paste into a state file.

    This is the adoption half. `claims:` reached 9 of 43 state files because writing SQL by hand
    for each number is work nobody does twice; an evidence entry for a call the agent has just
    made should cost nothing. Each drafted entry carries a conservative `expect_contains` drawn
    from the actual answer, for the author to tighten or replace.
    """
    batch = research_batch.run_batch(requests, budget_seconds=budget_seconds)
    drafted = []
    for request in requests:
        rid = str(request.get("id"))
        outcome = batch["results"].get(rid, {})
        entry = {"id": rid, "what": "", "tool": request.get("tool"), "args": request.get("args")}
        if outcome.get("status") != "ok":
            entry["_skipped"] = outcome.get("reason") or outcome.get("error") or outcome.get("status")
            drafted.append(entry)
            continue
        result = outcome["result"]
        if isinstance(result, list):
            entry["expect_min"] = len(result)
        else:
            text = resolve_path(result, "text") or resolve_path(result, "verses.0.text")
            if isinstance(text, str) and text.strip():
                entry["path"] = "text" if resolve_path(result, "text") else "verses.0.text"
                entry["expect_contains"] = text.strip()[:80]
            else:
                entry["expect_contains"] = ""
        drafted.append(entry)
    return {"evidence": drafted, "summary": batch["summary"]}


def summarise(records: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    return counts
