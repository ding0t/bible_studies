"""Emit the full words of every song in the Songbook to docs/data/songbook-words.json.

The song list is docs/data/songbook.toml; hooks/songbook.py folds each song's words into its card.
Committed rather than generated in CI, like export_memory_verses.py: bible-text.db is not reachable
from the deploy workflow.

The words are the site's reading translation (references/sources.toml [reading_translation]), which
is public domain, so a song can be printed whole; the JSON records which translation it used. A song
whose words are not in Scripture's text carries its own `words` in the TOML instead (the Morning Hymn, translated for the page
from the Greek) and is skipped here.

Usage: uv run python export_songbook.py
"""
import json
import re
import tomllib
from pathlib import Path

import book_map
import query
import source_catalog

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "data" / "songbook.toml"
OUT = REPO / "docs" / "data" / "songbook-words.json"
READING = source_catalog.reading_translation()

# "Exodus 15:1-18", "Luke 2:14", or across chapters, "Psalms 113:1-118:29".
_REF = re.compile(r"^(?P<book>.+?)\s+(?P<c1>\d+):(?P<v1>\d+)(?:-(?:(?P<c2>\d+):)?(?P<v2>\d+))?$")


def chapters(conn, ref: str) -> list[dict]:
    m = _REF.match(ref.strip())
    if not m:
        raise ValueError(f"cannot read reference {ref!r}")
    num = book_map.REFERENCE_NAME_TO_NUM.get(m["book"].title())
    if num is None:
        raise ValueError(f"unknown book in {ref!r}")
    osis = book_map.NUM_TO_OSIS[num]
    c1, v1 = int(m["c1"]), int(m["v1"])
    c2, v2 = int(m["c2"] or c1), int(m["v2"] or v1)
    out = []
    for chapter in range(c1, c2 + 1):
        first = v1 if chapter == c1 else 1
        last = v2 if chapter == c2 else 999
        rows = conn.execute(
            "SELECT verse, text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse BETWEEN ? AND ? "
            "ORDER BY verse", (READING["work_id"], osis, chapter, first, last)).fetchall()
        expected = last - first + 1 if chapter == c2 else None
        if not rows or (expected and len(rows) != expected):
            raise LookupError(f"{READING['code']} is missing verses of {ref} (chapter {chapter})")
        out.append({"chapter": chapter, "verses": [[r["verse"], r["text"].strip()] for r in rows]})
    return out


def main() -> None:
    songs = tomllib.loads(SOURCE.read_text(encoding="utf-8"))["song"]
    conn = query.connect()
    words = {s["id"]: chapters(conn, s["ref"]) for s in songs if "words" not in s}
    OUT.write_text(json.dumps({"code": READING["code"],
                               "source": f"{READING['name']}, {READING['licence']}", "songs": words},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    verses = sum(len(c["verses"]) for song in words.values() for c in song)
    print(f"wrote {OUT.relative_to(REPO)}: {len(words)} songs, {verses} verses")


if __name__ == "__main__":
    main()
