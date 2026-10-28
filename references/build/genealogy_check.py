"""Compare this site's genealogy with STEP's TIPNR, an independent record of the same families.

The timeline's family tree (docs/data/genealogy/*.json) was assembled by hand. TIPNR records every
individual in Scripture with parents, spouses and children, built by Tyndale House from the text.
Where the two disagree, one of them is wrong or the text is ambiguous; either way the site should
know. This reports, it never edits.

Each person is matched to a TIPNR individual by name and then by shared verses, because names
repeat (29 Zechariahs). A person who matches none, or several equally, is reported as unmatched
rather than guessed. Links are compared through the matches: the site's parent is right when its
own match is among TIPNR's parents for this person. TIPNR marks some links as looser than they
look -- (a) an ancestor, not a parent; (?) a judgment on an ambiguous text -- and those are
reported as such, since a family tree that skips generations (Luke 3, Matthew 1) can be right to.

Usage:  uv run python genealogy_check.py            # disagreements only
        uv run python genealogy_check.py --all      # every comparison
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

from book_map import NUM_TO_OSIS
from commentary_index import parse_reference, split_compound

DB_PATH = Path(__file__).resolve().parent / "out" / "bible-text.db"
GENEALOGY_DIR = Path(__file__).resolve().parents[2] / "docs" / "data" / "genealogy"


def site_people() -> dict[str, dict]:
    people = {}
    for path in sorted(GENEALOGY_DIR.glob("*.json")):
        if path.name == "index.json":
            continue
        for person in json.loads(path.read_text(encoding="utf-8"))["people"]:
            people[person["id"]] = person
    return people


def verses_of(person: dict) -> tuple[set[tuple[str, int, int]], set[tuple[str, int]]]:
    """The person's bible_references as verses, and as chapters for a chapter-only reference
    ("2 Chronicles 13"), which the kings mostly carry. 'LXX'-suffixed ones contribute nothing."""
    verses, chapters = set(), set()
    for raw in person.get("bible_references", []):
        for ref in split_compound(raw):
            parsed = parse_reference(ref)
            if parsed is None:
                continue
            book = NUM_TO_OSIS[parsed[0]]
            if ":" not in parsed[2]:
                chapters.add((book, parsed[1]))
                continue
            first, _, last = parsed[2].split(":", 1)[1].partition("-")
            if first.isdigit() and (not last or last.isdigit()):
                verses |= {(book, parsed[1], v) for v in range(int(first), int(last or first) + 1)}
    return verses, chapters


def _overlap(conn: sqlite3.Connection, name_id: str, verses: set, chapters: set) -> tuple[int, int]:
    refs = {tuple(r) for r in conn.execute(
        "SELECT book, chapter, verse FROM name_references WHERE name_id=?", (name_id,))}
    return len(verses & refs), sum(1 for b, c, _ in refs if (b, c) in chapters)


def match(conn: sqlite3.Connection, person: dict) -> tuple[str | None, str]:
    """By name, then by shared verses. The fallback catches a person TIPNR files under another
    name -- the patriarch Jacob is 'Israel@Gen.25.26-Rev', Arphaxad the ESV's 'Arpachshad' -- which
    a name-only match gets wrong by landing on a different individual of the same name."""
    name = re.sub(r"\s*\(.*\)$", "", person["name"]).strip()
    verses, chapters = verses_of(person)
    candidates = [r[0] for r in conn.execute(
        "SELECT name_id FROM proper_names WHERE name=? COLLATE NOCASE AND kind LIKE 'person%'",
        (name,))]
    scored = sorted(((_overlap(conn, c, verses, chapters), c) for c in candidates), reverse=True)
    if scored and scored[0][0] > (0, 0):
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            return None, f"{scored[0][1]} and {scored[1][1]} share equally many verses"
        return scored[0][1], f"by name, {scored[0][0][0]} shared verses"
    # Nobody of that name shares a verse: who do this person's verses name most often?
    if verses:
        placeholders = ",".join("(?,?,?)" for _ in verses)
        rows = conn.execute(
            "SELECT r.name_id, COUNT(*) AS n FROM name_references r JOIN proper_names p "
            "ON p.name_id = r.name_id WHERE p.kind LIKE 'person%' AND (r.book, r.chapter, r.verse) "
            f"IN (VALUES {placeholders}) GROUP BY r.name_id ORDER BY n DESC LIMIT 2",
            [x for v in sorted(verses) for x in v]).fetchall()
        if rows and rows[0][1] >= max(2, len(verses) // 2) and (len(rows) == 1 or rows[0][1] > rows[1][1]):
            return rows[0][0], f"by verses ({rows[0][1]} of {len(verses)}); TIPNR names them differently"
    if len(candidates) == 1:
        # TIPNR lists only verses that use the name: Eve is named at Genesis 3:20 and 4:1, not
        # in the Genesis 2-3 narrative a site entry cites, so a lone candidate stands unconfirmed.
        return candidates[0], "only individual of that name, no shared verse"
    if not candidates:
        return None, f"no TIPNR person named {name!r} and the verses name nobody consistently"
    return None, f"{len(candidates)} individuals named {name!r}, none sharing a verse"


def links(value: str | None) -> dict[str, str]:
    """'Amram@Exo.6.18-1Ch, Mahol@1Ki.4.31(a)' -> {name_id: marker}."""
    out = {}
    for part in (value or "").split(","):
        part = part.strip()
        if part:
            marker = re.search(r"\(([a-z?])\)$", part)
            out[re.sub(r"\([a-z?]\)$", "", part)] = marker[1] if marker else ""
    return out


def compare(conn: sqlite3.Connection, show_all: bool) -> int:
    conn.row_factory = sqlite3.Row
    people = site_people()
    matched = {pid: match(conn, p) for pid, p in people.items()}
    problems = 0
    unmatched = [(pid, why) for pid, (tid, why) in matched.items() if tid is None]
    for pid, person in people.items():
        tid = matched[pid][0]
        if tid is None:
            continue
        row = conn.execute("SELECT * FROM proper_names WHERE name_id=?", (tid,)).fetchone()
        lines = []
        for field, site_ids in (("parents", [person.get("parent_id")]),
                                ("partners", [person.get("spouse_id")]),
                                ("offspring", person.get("children") or [])):
            theirs = links(row[field])
            for site_id in filter(None, site_ids):
                other = matched.get(site_id, (None, "not in the site's genealogy"))[0]
                if other is None:
                    lines.append(f"  ?  {field}: {site_id} has no TIPNR match, cannot compare")
                elif other not in theirs:
                    lines.append(f"  x  {field}: site has {site_id} ({other}); TIPNR has "
                                 f"{', '.join(theirs) or 'none'}")
                    problems += 1
                elif theirs[other]:
                    lines.append(f"  ~  {field}: {site_id} agrees, but TIPNR marks it "
                                 f"({theirs[other]})")
                elif show_all:
                    lines.append(f"  ok {field}: {site_id}")
        if lines:
            print(f"{pid}  ->  {tid}  ({matched[pid][1]})")
            print("\n".join(lines))
    print(f"\n{len(people)} people; {len(people) - len(unmatched)} matched to TIPNR; "
          f"{problems} link(s) disagree")
    if unmatched:
        print("unmatched (add verse references to the person, or check the name):")
        for pid, why in unmatched:
            print(f"  {pid}: {why}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="show agreeing links too")
    args = parser.parse_args()
    if not DB_PATH.exists():
        print(f"{DB_PATH} not built -- run build.py", file=sys.stderr)
        return 2
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    compare(conn, args.all)
    return 0


if __name__ == "__main__":
    sys.exit(main())
