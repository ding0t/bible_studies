"""Compare this site's dates with STEP Bible's chronology, an independent dating of the same events.

STEP's chronology app (j_chronology.json, fetched at build.py's STEP_APP_COMMIT) dates 354 events
under twelve schemes: the Hebrew, Greek (LXX) or Samaritan numbers of Genesis, crossed with 400 or
200 years in Egypt and a 15th- or 13th-century Exodus, plus Ussher. This site works to one line --
the Masoretic numbers, Terah 130 at Abram's birth (Acts 7:4), 430 years from the promise to the
Exodus (Galatians 3:17) and the Exodus in 1446 BC -- which is STEP's Hebrew_200_15.

**The two AMs are not the same year.** Both count from creation, but this site puts AM 0 at
3959 BC, Ussher at 4004 BC, and STEP's own timeline axis at 4174 BC. So a date is never carried
from one epoch to another: before Abram's call STEP dates in AM, and the check compares AM with AM
(the same Genesis arithmetic on both sides); after it STEP dates in BC/AD, and the check compares
calendar years, converting this site's AM by this site's own epoch (chronology.json `epochs`) and
STEP's by nothing at all. Ussher's column is never compared.

Events are matched by the verses they cite. A match is STEP's reading of the same verses, not
proof that the two describe the same moment, so each row prints both labels for a reader to judge.
Reports, never edits.

Usage:  uv run python step_chronology_check.py          # disagreements only
        uv run python step_chronology_check.py --all    # every comparison
"""
import argparse
import json
import re
import sys
from pathlib import Path

from book_map import NUM_TO_OSIS, STEP_ABBREV_TO_OSIS
from build import fetch_step_app
from commentary_index import parse_reference, split_compound
from genealogy_check import site_people

REPO = Path(__file__).resolve().parents[2]
CHRONOLOGY = REPO / "docs" / "data" / "chronology.json"
GENERATED = REPO / "docs" / "data" / "genealogy" / "generated" / "mt.json"
SCHEME = "dt_Hebrew_200_15"
CLOSE = 5   # years: inside this the two agree as closely as a regnal-year reconstruction can

_STEP_REF = re.compile(r"(?:([1-3]?[A-Z][a-z]{1,4})\.)?(\d+)(?:\.(\d+))?(?:-(\d+)(?:\.(\d+))?)?")


def step_date(text: str) -> tuple[str, int] | None:
    """('AM', 1656), ('cal', -1446) or ('cal', 33) from "AM 1656", "1446 BC", "33 AD"."""
    match = re.match(r"\s*(AM\s*(\d+)|(\d+)\s*BC|(\d+)\s*AD)", text or "")
    if not match:
        return None
    if match[2]:
        return "AM", int(match[2])
    return ("cal", -int(match[3])) if match[3] else ("cal", int(match[4]))


def step_verses(refs: str) -> set[tuple[str, int, int]]:
    """Verses named by "Gen.4.25-26; 5.3-7" or "2Ki.15.1-7; 2Ch.26.1-23"; a chapter alone
    ("Gen.6-9", "Jon.*") stands for its first 200 verses, enough to overlap any cited verse."""
    verses, book = set(), None
    for part in refs.replace("*", "1-1").split(";"):
        match = _STEP_REF.fullmatch(part.strip())
        if not match:
            continue
        named, chapter, verse, to, to_verse = match.groups()
        if named:
            book = STEP_ABBREV_TO_OSIS.get(named)
        if not book:
            continue
        first = int(chapter)
        if verse is None:
            for c in range(first, int(to or first) + 1):
                verses.update((book, c, v) for v in range(1, 200))
        elif to_verse is not None:
            verses.update((book, c, v) for c in range(first, int(to) + 1) for v in range(1, 200)
                          if (c, v) >= (first, int(verse)) and (c, v) <= (int(to), int(to_verse)))
        else:
            verses.update((book, first, v) for v in range(int(verse), int(to or verse) + 1))
    return verses


def site_verses(refs: str | None) -> set[tuple[str, int, int]]:
    verses = set()
    for ref in split_compound(refs or ""):
        parsed = parse_reference(ref)
        if not parsed:
            continue
        book_num, chapter, display = parsed
        book = NUM_TO_OSIS[book_num]
        span = display.split(":", 1)[1] if ":" in display else "1-199"
        first, _, last = span.partition("-")
        verses.update((book, chapter, v) for v in range(int(first), int(last or first) + 1))
    return verses


def step_events() -> list[dict]:
    events = []
    for entry in fetch_step_app("J_AppsJson/J_Chronology/j_chronology")["ChronologyEntries"]:
        date = step_date(entry.get(SCHEME, ""))
        if not date or not entry.get("bibleRefs"):
            continue
        label = re.sub(r"<[^>]+>|▼", "", entry["desc"]).strip()
        events.append({"label": label, "date": date, "verses": step_verses(entry["bibleRefs"]),
                       "refs": entry["bibleRefs"]})
    return events


def site_events() -> list[dict]:
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    epoch = next(e["am0_gregorian"] for e in data["epochs"] if e["id"] == "genealogy")
    events = []
    for marker in data["genesis_markers"]:
        events.append({"label": marker["label"], "date": ("AM", marker["am_year"]),
                       "verses": site_verses(marker["scripture"]), "from": "genesis_markers"})
    # Not `artifacts`: an inscription's date is when it was made, and the verses it cites are
    # the events it bears on, often centuries apart.
    for key in ("anchor_table", "anchors", "milestones"):
        for item in data[key]:
            if item.get("gregorian_year") is None:
                continue
            events.append({"label": item["label"], "date": ("cal", item["gregorian_year"]),
                           "verses": site_verses(item.get("scripture") or item.get("refs")),
                           "from": key})
    # Genesis 5 and 11 births, as the site's own generator dates them. STEP writes a birth as
    # "Seth, lives 912 yrs"; the site's verse is the one giving the father's age at it.
    names = {pid: re.sub(r"\s*\(.*\)$", "", p["name"]) for pid, p in site_people().items()}
    for person_id, person in json.loads(GENERATED.read_text(encoding="utf-8"))["people"].items():
        if person.get("zadok_year_born") is not None:
            name = names.get(person_id, person_id)
            events.append({"label": f"{name} born", "date": ("AM", person["zadok_year_born"]),
                           "name": name, "verses": set(), "from": "genealogy (mt)"})
    for event in events:
        if event["date"][0] == "AM":  # AM 0 is 3959 BC; AM 3959 is AD 1, there being no year 0
            year = epoch + event["date"][1]
            event["calendar"] = ("cal", year + 1 if year >= 0 else year)
    return events


_SMALL = {"the", "and", "of", "to", "in", "on", "at", "by", "for", "from", "his", "her", "with",
          "after", "into", "year", "years", "lives", "king", "over", "born", "dies"}


def words(label: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", label.lower()) if len(w) > 2 and w not in _SMALL}


def match(event: dict, step: list[dict]) -> dict | None:
    """STEP's event citing the same verses and either sharing a word of its label or containing
    every verse the site cites. Verses alone are not enough: STEP's "Abraham, lives 175 yrs" cites
    Genesis 11:26-50:13, so it overlaps every event in the patriarchs' lives, and Daniel 10-12 is
    both a vision of 535 BC and the events of 167."""
    named = re.fullmatch(r"(\w+) born", event["label"])
    if "name" in event or named:
        name = (event.get("name") or named[1]).lower()
        return next((s for s in step
                     if re.match(rf"{name}\b,? (lives|born)", s["label"].lower())), None)
    if not event["verses"]:
        return None
    # A birth on STEP's side ("Haran born", "Isaac, lives 180 yrs") is only ever a birth.
    births = re.compile(r"^[\w' ]+( born\b|, lives)")
    # STEP dates a prophecy when it was given; the site dates the events it foretells. Daniel 11
    # is STEP's 535 BC vision and the site's 167 BC desecration, so the two never match.
    foretold = re.compile(r"vision|prophec|dream", re.I)
    scored = [(len(words(event["label"]) & words(s["label"])),
               len(event["verses"] & s["verses"]) / len(event["verses"]), i)
              for i, s in enumerate(step) if comparable(event, s) and event["verses"] & s["verses"]
              and ("born" in event["label"] or not births.match(s["label"]))]
    # Sharing a word, or citing nothing STEP's entry does not: the event sits inside STEP's range
    # -- unless that range is a prophecy and the labels have nothing in common.
    scored = [x for x in scored
              if x[0] or (x[1] == 1 and not foretold.search(step[x[2]]["label"]))]
    return step[max(scored)[2]] if scored else None


def comparable(event: dict, step: dict) -> tuple[str, int] | None:
    """This site's date in STEP's terms: as it stands when both are AM or both calendar years,
    converted by this site's epoch when STEP has moved to BC. STEP's AM is never converted."""
    if event["date"][0] == step["date"][0]:
        return event["date"]
    return event.get("calendar") if step["date"][0] == "cal" else None


def show(date: tuple[str, int]) -> str:
    kind, year = date
    return f"AM {year}" if kind == "AM" else f"{-year} BC" if year < 0 else f"AD {year}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--all", action="store_true", help="print agreements too")
    args = parser.parse_args()
    step = step_events()
    rows, unmatched = [], []
    for event in site_events():
        found = match(event, step)
        if not found:
            unmatched.append(event)
            continue
        ours = comparable(event, found)
        if not ours:
            unmatched.append(event)
            continue
        rows.append((abs(ours[1] - found["date"][1]), event, found, ours))
    rows.sort(key=lambda r: -r[0])
    agree = sum(1 for d, *_ in rows if d == 0)
    close = sum(1 for d, *_ in rows if 0 < d <= CLOSE)
    print(f"{len(rows)} of this site's dated events matched one of STEP's {len(step)} "
          f"({SCHEME}): {agree} agree, {close} within {CLOSE} years, "
          f"{len(rows) - agree - close} further apart; {len(unmatched)} unmatched.\n")
    for diff, event, found, ours in rows:
        if diff == 0 and not args.all:
            continue
        converted = f" (= {show(event['date'])})" if ours != event["date"] else ""
        print(f"{diff:>4} yr  site {show(ours):>9} {event['label']}{converted} [{event['from']}]\n"
              f"          STEP {show(found['date']):>9} {found['label']} ({found['refs']})")
    if args.all and unmatched:
        print("\nunmatched: " + "; ".join(e["label"] for e in unmatched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
