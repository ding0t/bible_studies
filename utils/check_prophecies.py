#!/usr/bin/env python3
"""Check docs/data/prophecies-of-christ.toml against its own schema and the data it points into.

Why this exists: the file is built over many sessions, and a half-finished entry, a mistyped
category or a chronology id that was renamed would otherwise reach the reference page and the
prophecy validator unnoticed. The schema is documented at the top of the TOML file; this checks it.

Errors (exit non-zero):

1. **Identity.** Every id is kebab-case and unique, and no id is also in fulfilled-prophecy.toml.
2. **Vocabulary.** research, tier, category, status, use kind and text, control, recognition,
   form, speaker, specific and offices take only the documented values.
3. **References.** `prophecy` names an Old Testament book, each `uses` ref a New Testament book,
   and each carries chapter:verse.
4. **Pointers.** `event` is a dated id in chronology.json (or a passion_sequence id, dated by the
   crucifixion); `future_event` is a future_sequence id.
5. **Tier and use agree.** A tier 1 entry has a fulfilment, split or type use; a tier 3 entry has
   none of those. Status "partly" or "future" names a future_event once drafted; a split use on
   a drafted entry needs a `split` block.
6. **Drafted means filled in.** A drafted or verified entry has predicts, specific, control and
   recognition, and a `text` on every fulfilment, split and application use; a verified one has
   recognition other than "unassessed". Recognition "read-after" carries a witness dated after
   the New Testament (a Targum, a midrash), or the label has nothing under it.
7. **Validator entries are dated.** An entry with `standing` has an `event` or a `year`.
8. **The New Testament table** (`[[nt_prophecy]]`): ids unique across both tables; speaker,
   recorded and the shared vocabulary as documented; `prophecy` a New Testament reference; `see`
   an id that exists in either file; a `fulfilment` unless the status is "future".

9. **The computed file is current.** docs/data/prophecies-of-christ.json, which the reference page
   renders, was written from this ledger, the authorship table and the chronology as they are now
   (references/build/export_prophecies.py records their hash). A stale file would put old counts on
   the page with no error anywhere.

Prints a progress summary (entries by research level, tier and category). Run from the repo root:
python3 utils/check_prophecies.py
"""

import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "references" / "build"))
from book_map import REFERENCE_NAME_TO_NUM  # noqa: E402

DATA = ROOT / "docs" / "data"
CHRIST = DATA / "prophecies-of-christ.toml"
OTHER = DATA / "fulfilled-prophecy.toml"
CHRONOLOGY = DATA / "chronology.json"
AUTHORSHIP = DATA / "book-authorship.toml"
COMPUTED = DATA / "prophecies-of-christ.json"

VOCAB = {
    "research": {"candidate", "drafted", "verified"},
    "tier": {1, 2, 3},
    "category": {"nature", "lineage", "birth", "childhood", "forerunner", "ministry", "passion",
                 "resurrection", "redemption", "office", "future"},
    "status": {"fulfilled", "partly", "future"},
    "control": {"divine", "opponents", "unwitting", "followers", "chosen", "unfulfilled"},
    "recognition": {"known-before", "partly", "read-after", "veiled", "unassessed"},
    "form": {"prediction", "type"},
    "speaker": {"messiah"},
    "standing": {"stated", "contested-reading", "contested-reckoning", "record-after"},
}
LIST_VOCAB = {
    "specific": {"name", "place", "number", "time", "manner", "sequence", "lineage", "person"},
    "offices": {"prophet", "priest", "king"},
}
USE_KINDS = {"fulfilment", "split", "type", "application", "imagery", "allusion"}
CLOSING_KINDS = {"fulfilment", "split", "type"}
QUOTING_KINDS = {"fulfilment", "split", "application"}
USE_TEXTS = {"mt", "lxx", "both", "neither", "none"}
DRAFTED_REQUIRED = ("predicts", "specific", "control", "recognition")
OT_BOOKS = set(list(REFERENCE_NAME_TO_NUM)[:39]) | {"Psalm", "Song of Songs"}
BOOK = re.compile(r"^((?:[1-3] )?[A-Z][a-z]+(?: of [A-Z][a-z]+)?) \d+:\d+")
ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def book_of(ref: str) -> str | None:
    m = BOOK.match(ref.strip())
    return m.group(1) if m and m.group(1) in REFERENCE_NAME_TO_NUM else None


def chronology_ids() -> tuple[set[str], set[str]]:
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    dated = {e["id"] for key in ("anchors", "anchor_table", "milestones", "life_events") for e in data[key]
             if e.get("gregorian_year", e.get("gregorian")) is not None}
    dated |= {e["id"] for e in data["passion_sequence"]["events"]}
    future = {e["id"] for e in data["future_sequence"]["events"]}
    return dated, future


def check(entries: list[dict], other_ids: set[str], dated: set[str], future: set[str]) -> list[str]:
    errors = []
    seen = set()
    for e in entries:
        pid = e.get("id", "?")

        def err(msg: str) -> None:
            errors.append(f"{pid}: {msg}")

        if not ID.match(pid):
            err("id is not kebab-case")
        if pid in seen:
            err("duplicate id")
        if pid in other_ids:
            err("id is also in fulfilled-prophecy.toml")
        seen.add(pid)

        for field in ("research", "tier", "category", "prophecy", "uses", "status"):
            if field not in e:
                err(f"missing {field}")
        for field, allowed in VOCAB.items():
            if field in e and e[field] not in allowed:
                err(f"{field} {e[field]!r} is not one of {sorted(allowed, key=str)}")
        for field, allowed in LIST_VOCAB.items():
            for value in e.get(field, []):
                if value not in allowed:
                    err(f"{field} value {value!r} is not one of {sorted(allowed)}")

        first = e.get("prophecy", "").split(";")[0]
        if book_of(first) not in OT_BOOKS:
            err(f"prophecy {e.get('prophecy')!r} does not start with an Old Testament book and chapter:verse")
        kinds = set()
        for use in e.get("uses", []):
            kinds.add(use.get("kind"))
            if use.get("kind") not in USE_KINDS:
                err(f"use {use.get('ref')!r} has kind {use.get('kind')!r}")
            if "text" in use and use["text"] not in USE_TEXTS:
                err(f"use {use.get('ref')!r} has text {use['text']!r}")
            if (e.get("research") in ("drafted", "verified") and use.get("kind") in QUOTING_KINDS
                    and "text" not in use):
                err(f"use {use.get('ref')!r} ({use['kind']}) needs a text once drafted")
            book = book_of(use.get("ref", ""))
            if book is None or book in OT_BOOKS:
                err(f"use ref {use.get('ref')!r} is not a New Testament book and chapter:verse")

        if "event" in e and e["event"] not in dated:
            err(f"event {e['event']!r} is not a dated chronology.json id")
        if "future_event" in e and e["future_event"] not in future:
            err(f"future_event {e['future_event']!r} is not in future_sequence")

        if e.get("tier") == 1 and not kinds & CLOSING_KINDS:
            err("tier 1 needs a fulfilment, split or type use")
        if e.get("tier") == 3 and kinds & CLOSING_KINDS:
            err(f"tier 3 carries {sorted(kinds & CLOSING_KINDS)} uses; it is tier 1 or 2")

        if e.get("research") in ("drafted", "verified"):
            missing = [f for f in DRAFTED_REQUIRED if f not in e]
            if missing:
                err(f"research {e['research']!r} but missing {', '.join(missing)}")
            if e.get("status") in ("partly", "future") and "future_event" not in e:
                err(f"status {e['status']!r} needs a future_event")
            if "split" in kinds and "split" not in e:
                err("a split use needs a split block")
        if e.get("research") == "verified" and e.get("recognition") == "unassessed":
            err("verified with recognition still unassessed")
        if e.get("recognition") == "read-after" and not any(
                isinstance(w.get("year"), int) and w["year"] > NT_WRITTEN_BY
                for w in e.get("recognition_evidence", [])):
            err(f"recognition 'read-after' needs a recognition_evidence witness dated after AD {NT_WRITTEN_BY}")
        if "standing" in e and "event" not in e and "year" not in e:
            err("a validator entry (standing) needs an event or a year")
    return errors


# 'read-after' means a Jewish reading of the Messiah made after the church's own: every Targum and
# midrash is later than the New Testament's last book.
NT_WRITTEN_BY = 100

NT_VOCAB = {"speaker": {"jesus", "angel", "apostle", "revelation"},
            "recorded": {"before", "after", "contested"}}


def check_nt(entries: list[dict], known_ids: set[str], dated: set[str], future: set[str]) -> list[str]:
    errors = []
    seen = set()
    for e in entries:
        pid = e.get("id", "?")

        def err(msg: str) -> None:
            errors.append(f"nt_prophecy {pid}: {msg}")

        if not ID.match(pid) or pid in seen or pid in known_ids:
            err("id is not kebab-case, or is already used")
        seen.add(pid)
        for field in ("research", "speaker", "category", "prophecy", "predicts", "status", "recorded"):
            if field not in e:
                err(f"missing {field}")
        for field, allowed in {**{k: VOCAB[k] for k in ("research", "category", "status", "control")},
                               **NT_VOCAB}.items():
            if field in e and e[field] not in allowed:
                err(f"{field} {e[field]!r} is not one of {sorted(allowed)}")
        for value in e.get("specific", []):
            if value not in LIST_VOCAB["specific"]:
                err(f"specific value {value!r} is not one of {sorted(LIST_VOCAB['specific'])}")
        book = book_of(e.get("prophecy", "").split(";")[0])
        if book is None or book in OT_BOOKS:
            err(f"prophecy {e.get('prophecy')!r} is not a New Testament book and chapter:verse")
        if e.get("status") != "future" and "fulfilment" not in e:
            err("a fulfilled or partly fulfilled prophecy needs a fulfilment")
        if "see" in e and e["see"] not in known_ids:
            err(f"see {e['see']!r} is not an id in either prophecy file")
        if "event" in e and e["event"] not in dated:
            err(f"event {e['event']!r} is not a dated chronology.json id")
        if "future_event" in e and e["future_event"] not in future:
            err(f"future_event {e['future_event']!r} is not in future_sequence")
    return errors


def check_computed() -> list[str]:
    """The same three inputs, in the same order, as export_prophecies.inputs_hash()."""
    digest = hashlib.sha256()
    for path in (CHRIST, AUTHORSHIP, CHRONOLOGY):
        digest.update(path.read_bytes())
    if not COMPUTED.exists():
        return [f"{COMPUTED.name} is missing: run `uv run python export_prophecies.py` in references/build"]
    if json.loads(COMPUTED.read_text(encoding="utf-8")).get("inputs_sha256") != digest.hexdigest():
        return [f"{COMPUTED.name} is stale: run `uv run python export_prophecies.py` in references/build"]
    return []


def main() -> int:
    data = tomllib.loads(CHRIST.read_text(encoding="utf-8"))
    entries, nt_entries = data["prophecy"], data.get("nt_prophecy", [])
    other_ids = {e["id"] for e in tomllib.loads(OTHER.read_text(encoding="utf-8"))["prophecy"]}
    dated, future = chronology_ids()
    errors = check(entries, other_ids, dated, future)
    errors += check_nt(nt_entries, other_ids | {e["id"] for e in entries}, dated, future)
    errors += check_computed()
    for line in errors:
        print(f"ERROR prophecies-of-christ.toml {line}")
    research = Counter(e.get("research") for e in entries)
    tiers = Counter(e.get("tier") for e in entries)
    print(f"check_prophecies: {len(entries)} entries "
          f"({', '.join(f'{n} {k}' for k, n in sorted(research.items()))}; "
          f"tier {', '.join(f'{k}: {n}' for k, n in sorted(tiers.items()))}), "
          f"{len(nt_entries)} New Testament; {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
