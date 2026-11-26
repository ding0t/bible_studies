"""What the reference page computes for each prophecy of Christ, written for the site's build.

Writes docs/data/prophecies-of-christ.json from docs/data/prophecies-of-christ.toml. The build has
no Bible databases, so what needs one is worked out here: which Qumran scrolls hold the prophecy's
Hebrew. The rest (when it was written, on both dating schemes, and when it came to pass) is put
here too, so the page and its charts read one set of numbers. hooks/prophecies.py renders it and
utils/build_jesus_graphics.py draws from it. Re-run after changing the ledger, the authorship table
or the chronology; utils/check_prophecies.py fails while the file is stale:

    uv run python export_prophecies.py
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tomllib
from collections import defaultdict
from pathlib import Path

from unity_measures import (
    AUTHORSHIP, CHRIST_PROPHECY, CHRONOLOGY, DB, GREAT_ISAIAH_SCROLL, QUMRAN, QUMRAN_FALLS, ROOT,
    chronology_years, date_range, load_authorship, parse_refs,
)

OUT = ROOT / "docs" / "data" / "prophecies-of-christ.json"
# The inputs whose change makes the file stale; check_prophecies.py hashes the same three.
INPUTS = (CHRIST_PROPHECY, AUTHORSHIP, CHRONOLOGY)


def inputs_hash() -> str:
    digest = hashlib.sha256()
    for path in INPUTS:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def has_critical_date(book: dict, chapter: int) -> bool:
    if any(lo <= chapter <= hi for lo, hi in (part["chapters"] for part in book.get("critical_parts", []))):
        return True
    return "critical" in book or "critical_after" in book


def crucifixion_year() -> int:
    """passion_sequence events carry days, not years: they fall in the crucifixion's year."""
    return chronology_years()["anchor_41"]


def qumran_index(conn: sqlite3.Connection) -> dict[tuple[str, int, int], set[str]]:
    index = defaultdict(set)
    for work, b, c, v in conn.execute("SELECT DISTINCT work_id, book, chapter, verse FROM morphology "
                                      "WHERE work_id LIKE 'dss-%'"):
        if QUMRAN.match(work):
            index[(b, c, v)].add(work.removeprefix("dss-"))
    return index


def entry_row(e: dict, books: dict, years: dict[str, int], passion: set[str], scrolls_at) -> dict:
    refs = parse_refs(e["prophecy"])
    hebrew = parse_refs(e.get("masoretic", e["prophecy"]))
    # The latest year the earliest of its texts could have been written: the end of its range.
    written = {s: min(date_range(books[b], s, c)[1] for b, c, _ in refs) for s in ("traditional", "critical")}
    if "written" in e:
        written["traditional"] = e["written"]
    # date_range falls back to the traditional date where the authorship table records no critical
    # one (the Psalms, Zechariah), which would read as the critics agreeing. Keep a critical date
    # only where every text's book has one of its own.
    existed_by = None
    if not all(has_critical_date(books[b], c) for b, c, _ in refs):
        written["critical"] = None
        # The bracket instead: the latest year any dating allows, fixed by a witness that names
        # the book (Sirach 49 for Jeremiah, Ezekiel and the Twelve). Only where every text has one.
        if all("existed_by" in books[b] for b, _, _ in refs):
            existed_by = min(books[b]["existed_by"] for b, _, _ in refs)
    event = e.get("event")
    fulfilled = (crucifixion_year() if event in passion else years.get(event)) if event else e.get("year")
    scrolls = sorted(set().union(*(scrolls_at.get(r, set()) for r in hebrew)))
    dated = fulfilled is not None
    return {
        "id": e["id"],
        "prophecy": e["prophecy"],
        "written_traditional": written["traditional"],
        "written_critical": written["critical"],
        "fulfilled": fulfilled,
        "years_ahead_traditional": fulfilled - written["traditional"] if dated else None,
        "years_ahead_critical": fulfilled - written["critical"] if dated and written["critical"] is not None else None,
        "existed_by": existed_by,
        "years_ahead_at_least": fulfilled - existed_by if dated and existed_by is not None else None,
        "qumran": scrolls,
        # A manuscript you can hold, older than the event: the Great Isaiah Scroll (about 125 BC),
        # or any Qumran copy of a prophecy fulfilled after the site fell. A Qumran copy of one
        # fulfilled in Jesus' lifetime counts only by its own palaeographic date, which this file
        # does not yet carry (prophecy-and-jesus.yml, open).
        "manuscript_before": dated and (("1Qisaa" in scrolls and fulfilled > GREAT_ISAIAH_SCROLL)
                                        or (bool(scrolls) and fulfilled > QUMRAN_FALLS)),
    }


def main() -> int:
    books = load_authorship()
    years = chronology_years()
    passion = {e["id"] for e in json.loads(CHRONOLOGY.read_text(encoding="utf-8"))["passion_sequence"]["events"]}
    with open(CHRIST_PROPHECY, "rb") as f:
        entries = tomllib.load(f)["prophecy"]
    conn = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
    scrolls_at = qumran_index(conn)
    result = {
        "inputs_sha256": inputs_hash(),
        "note": "Written by references/build/export_prophecies.py; do not edit by hand.",
        "prophecies": [entry_row(e, books, years, passion, scrolls_at) for e in entries],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(entries)} prophecies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
