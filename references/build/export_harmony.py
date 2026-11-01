"""Emit STEP Bible's harmony of the gospels to docs/data/gospel-harmony.json for the timeline.

Committed, like the pop-up data, because the deploy cannot rebuild bible-text.db. The timeline
reads it to show, under any event citing a gospel passage, the other gospels' accounts of the same
event ("Passover and Last Supper": Matthew 26:17-29, Mark 14:12-25, Luke 22:7-30, John 13:1-35).
References only: STEP's list is BSD-3-Clause, and nothing here is anyone's Bible text.

Usage: uv run python export_harmony.py      (re-run after build.py moves STEP_APP_COMMIT)
"""
import json
from pathlib import Path

import query

OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "gospel-harmony.json"


def main() -> int:
    conn = query.connect()
    events: dict[int, dict] = {}
    for row in conn.execute(
            "SELECT entry, label, book, chapter, verse, end_chapter, end_verse FROM reference_lists "
            "WHERE list_id='gospel-harmony' ORDER BY entry, rowid"):
        event = events.setdefault(row["entry"], {"label": row["label"], "accounts": []})
        event["accounts"].append({"book": row["book"], "c1": row["chapter"], "v1": row["verse"],
                                  "c2": row["end_chapter"], "v2": row["end_verse"]})
    commit = conn.execute("SELECT source_commit FROM works WHERE work_id='step-lists'").fetchone()[0]
    OUT.write_text(json.dumps({
        "source": "STEP Bible (www.STEPBible.org), Tyndale House Cambridge: Harmony of the Gospels "
                  f"(github.com/STEPBible/step at {commit[:12]}, BSD-3-Clause)",
        "events": list(events.values()),
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(events)} harmony events to {OUT.relative_to(OUT.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
