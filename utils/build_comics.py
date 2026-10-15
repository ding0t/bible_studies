"""Draw the one-minute comics from docs/data/comics/*.toml.

    python3 utils/build_comics.py                 # every comic
    python3 utils/build_comics.py you-are-gods    # one comic
    python3 utils/build_comics.py --cast          # the model sheets: every cast member and pose, and the emphasis tools
    python3 utils/build_comics.py --alt you-are-gods   # print the alt text for the markdown embed
    python3 utils/build_comics.py --draft peter        # render despite layout faults, and list them
    python3 utils/build_comics.py --verify             # every source = "esv" bubble against the ESV text

A comic file names a layout, then lists its panels: a scene, a sky, the cast with their poses, the
caption and the speech bubbles, and the verses the panel draws on. The drawing is all in
utils/lib/comic.py, so a new comic is a new TOML file and nothing else. See
.claude/skills/one-minute-comic/SKILL.md for how to write one.
"""

import re
import sys
import tomllib
from pathlib import Path

from lib import comic as lib
from lib.comic import cast_sheet, describe, emphasis_sheet, render

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "data" / "comics"
OUT = ROOT / "docs" / "content" / "assets" / "img" / "comics"
SHEET = ROOT / ".claude" / "skills" / "one-minute-comic" / "cast.svg"
EMPHASIS = SHEET.with_name("emphasis.svg")


def load(slug):
    comic = tomllib.loads((SRC / f"{slug}.toml").read_text(encoding="utf-8"))
    comic["slug"] = slug
    return comic


_REF = re.compile(r"^(?:(?P<book>(?:[1-3] )?[A-Za-z][A-Za-z ]*?)\s+)?(?:(?P<chapter>\d+):)?(?P<start>\d+)(?:-(?P<end>\d+))?$")


def verses(ref):
    """(osis, chapter, start, end) for each piece of a panel's ref, reading a bare "8:1-9" or "59" as
    the book and chapter before it: "Mark 7:31; 8:1-9" and "John 6:22-35, 59" both expand."""
    sys.path.insert(0, str(ROOT / "references" / "build"))
    import book_map
    out, book, chapter = [], None, None
    for piece in re.split(r"[;,]", ref):
        m = _REF.match(piece.strip())
        if not m:
            raise ValueError(f"cannot read {piece!r} in {ref!r}")
        book = m["book"] or book
        chapter = int(m["chapter"]) if m["chapter"] else chapter
        num = book_map.REFERENCE_NAME_TO_NUM[book.strip().title()]
        out.append((book_map.NUM_TO_OSIS[num], chapter, int(m["start"]), int(m["end"] or m["start"])))
    return out


def _plain(s):
    s = s.translate(str.maketrans("“”‘’—–", "\"\"''--"))
    return re.sub(r"\s+", " ", re.sub(r"\s*-\s*", "-", s)).strip().lower()


def verify(slugs):
    """Check that every bubble marked source = "esv" is the ESV's own wording, found in the verses its
    panel's ref names. The bubble may end with different punctuation (a sentence cut at a clause) but
    every word must appear in that order. Condensed bubbles are listed for a person to read."""
    sys.path.insert(0, str(ROOT / "references" / "build"))
    import study_notes_query as q
    try:
        conn = q.connect()
    except q.SourceUnavailable as exc:
        print(f"unverified: study-notes.db is not reachable ({exc}). Nothing was checked.")
        return 1
    failures = 0
    for slug in slugs:
        comic = load(slug)
        panels = [p for p in comic["panel"] if p.get("kind") != "gap"]
        for i, p in enumerate(panels, 1):
            text = " ".join(r["text"] for o, c, a, z in verses(p.get("ref", ""))
                            for r in q.lookup_verse(conn, o, c, a, "esv-study-bible", z))
            for b in p.get("say", []):
                words = lib.plain(b.get("text", ""))
                if not words:
                    continue
                if b.get("source") == "esv":
                    if _plain(words).rstrip(".!?,;:") in _plain(text):
                        print(f"  ok        {slug} panel {i}: {words}")
                    else:
                        failures += 1
                        print(f"  NOT FOUND {slug} panel {i} ({p.get('ref')}): {words}")
                else:
                    print(f"  condensed {slug} panel {i} ({p.get('ref')}): {words}  -- read against the verses")
    return 1 if failures else 0


def main(args):
    if args[:1] == ["--verify"]:
        sys.exit(verify(args[1:] or sorted(p.stem for p in SRC.glob("*.toml"))))
    if args[:1] == ["--cast"]:
        SHEET.write_text(cast_sheet() + "\n", encoding="utf-8")
        print(f"wrote {SHEET.relative_to(ROOT)}")
        EMPHASIS.write_text(emphasis_sheet() + "\n", encoding="utf-8")
        print(f"wrote {EMPHASIS.relative_to(ROOT)}")
        return
    if args[:1] == ["--alt"]:
        print(describe(load(args[1])))
        return
    if args[:1] == ["--draft"]:
        lib.STRICT = False
        args = args[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in args or sorted(p.stem for p in SRC.glob("*.toml")):
        path = OUT / f"{slug}.svg"
        path.write_text(render(load(slug)) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for msg in lib.PROBLEMS:
        print(f"  fault: {msg}")


if __name__ == "__main__":
    main(sys.argv[1:])
