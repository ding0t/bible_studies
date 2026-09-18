#!/usr/bin/env python3
"""Re-run the countable claims a study records, and report where prose and database disagree.

Why this exists. Every Critical finding this repo has produced came from the same place: a number
that was queried once, written into prose, and never checked again. `three-days-and-three-nights.md`
said "on the third day" occurs eight times; it occurs nine, and the miss propagated to six sentences
before a review caught it. The query had been run. The number in the file had drifted from it, and
nothing connected the two.

So the fix is to give the number a source of truth outside the prose. A study's state file records
its claims as SQL with an expected answer, and this re-runs them:

    claims:
      - id: third-day-count
        what: '"on the third day" in resurrection contexts'
        sql: |
          SELECT COUNT(*) FROM verses WHERE work_id='sblgnt'
            AND (text LIKE '%τρίτῃ ἡμέρᾳ%' OR text LIKE '%ἡμέρᾳ τῇ τρίτῃ%')
        expect: 10
        note: nine after excluding John 2:1, the Cana wedding

Only single-value queries are supported, deliberately. A claim that cannot be reduced to one number
is a claim this tool should not pretend to check.
"""
import argparse
import pathlib
import sqlite3
import sys

import yaml

import evidence as evidence_lib
import query

STATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "study-state"


def load_claims(path: pathlib.Path) -> tuple[list[dict], str | None]:
    """(claims, parse_error). A malformed state file is reported, never fatal.

    Three of the thirty-nine state files were unparseable YAML when this was written, which is its
    own defect -- a research trail no tool can read is a research trail that will quietly rot -- but
    it must not stop the other thirty-six being checked.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return [], str(e).split("\n")[0]
    claims = data.get("claims") or []
    if not isinstance(claims, list):
        return [], "`claims` is not a list"
    return claims, None


def check(conn: sqlite3.Connection, claim: dict) -> tuple[bool, str]:
    sql = (claim.get("sql") or "").strip()
    if not sql:
        return False, "no sql"
    if not sql.lower().lstrip().startswith("select"):
        return False, "sql must be a SELECT"
    try:
        row = conn.execute(sql).fetchone()
    except sqlite3.Error as e:
        return False, f"query failed: {e}"
    if row is None or len(row) != 1:
        return False, "query must return exactly one value"
    got, expect = row[0], claim.get("expect")
    if got != expect:
        return False, f"expected {expect!r}, database says {got!r}"
    return True, f"{got!r}"


def report_evidence(paths, budget: float) -> tuple[int, int, int, list[tuple[str, str]]]:
    """Replay each state file's `evidence:` block. Returns (checked, failed, unverified, unreadable).

    `unverified` is counted and reported separately from `failed` and does NOT fail the run: an
    unmounted volume means the evidence could not be tested, which is a different fact from the
    evidence being wrong. Conflating them would turn a routine local condition into a screenful of
    red and teach a reader to stop looking.
    """
    checked = failed = unverified = 0
    unreadable: list[tuple[str, str]] = []
    for path in paths:
        entries, parse_error = evidence_lib.load_evidence(path)
        if parse_error:
            unreadable.append((path.stem, parse_error))
            continue
        if not entries:
            continue
        records = evidence_lib.check_entries(entries, budget_seconds=budget)
        print(f"\n{path.stem}  (evidence)")
        for record in records:
            checked += 1
            if record["status"] == evidence_lib.FAIL:
                failed += 1
            elif record["status"] in (evidence_lib.UNVERIFIED, evidence_lib.MALFORMED):
                unverified += 1
            label = {evidence_lib.PASS: "ok  ", evidence_lib.FAIL: "FAIL",
                     evidence_lib.UNVERIFIED: "----", evidence_lib.MALFORMED: "????"}[record["status"]]
            print(f"  {label} {record['id']:24} {record['what']}\n       {record['detail']}")
    return checked, failed, unverified, unreadable


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug", nargs="?", help="study slug; omit to check every state file")
    ap.add_argument("--evidence", action="store_true",
                    help="also replay each study's `evidence:` block (tool calls with expected "
                         "answers), not just its SQL `claims:`")
    ap.add_argument("--only-evidence", action="store_true",
                    help="replay `evidence:` blocks and skip the SQL claims entirely")
    ap.add_argument("--budget", type=float, default=60.0,
                    help="wall-clock seconds per state file's evidence replay (default 60)")
    args = ap.parse_args()

    paths = ([STATE_DIR / f"{args.slug}.yml"] if args.slug
             else sorted(STATE_DIR.glob("*.yml")))
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"no such state file: {missing[0]}")

    if args.only_evidence:
        e_checked, e_failed, e_unverified, e_unreadable = report_evidence(paths, args.budget)
        print(f"\n{e_checked} evidence entry(ies); {e_failed} failing, {e_unverified} unverified")
        if not e_checked:
            print("No study records evidence yet. Add an `evidence:` block to a state file "
                  "(see references/build/evidence.py for the shape).")
        for stem, err in e_unreadable:
            print(f"  {stem}: {err}")
        sys.exit(1 if (e_failed or e_unreadable) else 0)

    conn = query.connect()
    checked = failed = files_with_claims = 0
    unreadable: list[tuple[str, str]] = []
    try:
        for path in paths:
            claims, parse_error = load_claims(path)
            if parse_error:
                unreadable.append((path.stem, parse_error))
                continue
            if not claims:
                continue
            files_with_claims += 1
            print(f"\n{path.stem}")
            for claim in claims:
                ok, detail = check(conn, claim)
                checked += 1
                if not ok:
                    failed += 1
                print(f"  {'ok  ' if ok else 'FAIL'} {claim.get('id','(unnamed)'):24} "
                      f"{claim.get('what','')}\n       {detail}")
    finally:
        conn.close()

    if unreadable:
        print("\nstate files that could not be parsed at all:")
        for stem, err in unreadable:
            print(f"  {stem}: {err}")
    e_checked = e_failed = e_unverified = 0
    if args.evidence:
        e_checked, e_failed, e_unverified, e_unreadable = report_evidence(paths, args.budget)
        unreadable += [x for x in e_unreadable if x not in unreadable]

    print(f"\n{checked} claim(s) across {files_with_claims} study(ies); {failed} failing"
          + (f"; {len(unreadable)} state file(s) unreadable" if unreadable else ""))
    if args.evidence:
        print(f"{e_checked} evidence entry(ies); {e_failed} failing, {e_unverified} unverified"
              + (" (unverified means could not be tested -- an absent source, not a wrong claim)"
                 if e_unverified else ""))
    if not checked and not e_checked:
        print("No study records claims or evidence yet. Add a `claims:` or `evidence:` block to a "
              "state file.")
    sys.exit(1 if (failed or e_failed or unreadable) else 0)


if __name__ == "__main__":
    main()
