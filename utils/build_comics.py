"""Draw the one-minute comics from docs/data/comics/*.toml.

    python3 utils/build_comics.py                 # every comic
    python3 utils/build_comics.py you-are-gods    # one comic
    python3 utils/build_comics.py --cast          # the model sheet of every cast member and pose
    python3 utils/build_comics.py --alt you-are-gods   # print the alt text for the markdown embed

A comic file names a layout, then lists its panels: a scene, a sky, the cast with their poses, the
caption and the speech bubbles, and the verses the panel draws on. The drawing is all in
utils/lib/comic.py, so a new comic is a new TOML file and nothing else. See
.claude/skills/one-minute-comic/SKILL.md for how to write one.
"""

import sys
import tomllib
from pathlib import Path

from lib.comic import cast_sheet, describe, render

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "data" / "comics"
OUT = ROOT / "docs" / "content" / "assets" / "img" / "comics"
SHEET = ROOT / ".claude" / "skills" / "one-minute-comic" / "cast.svg"


def load(slug):
    comic = tomllib.loads((SRC / f"{slug}.toml").read_text(encoding="utf-8"))
    comic["slug"] = slug
    return comic


def main(args):
    if args[:1] == ["--cast"]:
        SHEET.write_text(cast_sheet() + "\n", encoding="utf-8")
        print(f"wrote {SHEET.relative_to(ROOT)}")
        return
    if args[:1] == ["--alt"]:
        print(describe(load(args[1])))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in args or sorted(p.stem for p in SRC.glob("*.toml")):
        path = OUT / f"{slug}.svg"
        path.write_text(render(load(slug)) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
