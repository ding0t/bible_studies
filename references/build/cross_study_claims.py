#!/usr/bin/env python3
"""Show what every study says about the same chapter, side by side.

The class of defect this exists for reads perfectly in isolation. rapture.md said Noah was removed
BEFORE the flood in one section and preserved THROUGH it in four others, and olivet-discourse.md --
which links to rapture.md -- had already settled the question the other way with lexical evidence.
day-is-near.md prayed a reading of Mark 13:32 that a whole sibling study exists to refute, and
plotted an AD 32 crucifixion that the site's own dating study rules out on the weekday.

Nothing catches that, because every phase of review checks a study against SOURCES. This checks
studies against EACH OTHER. It cannot judge; it lays the sentences out so a reader can.

The surface is bounded. Ninety-seven chapters are cited by three or more studies, and the top of
that list -- Matthew 24, Daniel 9, Matthew 25 -- is exactly where the contradictions were.

    uv run python cross_study_claims.py --min-studies 4      # the whole surface, busiest first
    uv run python cross_study_claims.py "Matthew 24"         # one chapter, with the sentences
"""
import argparse
import collections
import pathlib
import re

CONTENT = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "content"
BOOK_IN_REF = re.compile(r'^((?:[1-3]\s)?[A-Za-z][A-Za-z ]*?\s\d+)')


def studies() -> list[tuple[str, str]]:
    """(slug, text) for every hand-written study, generated cross-reference pages excluded."""
    out = []
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "commentary-index:auto-start" in text or "section-index:auto-start" in text:
            continue
        out.append((str(path.relative_to(CONTENT)), text))
    return out


def chapter_index(corpus) -> dict[str, set[str]]:
    """chapter -> the studies naming it in bible_references or primary_passage."""
    index = collections.defaultdict(set)
    for slug, text in corpus:
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        head = fm.group(1) if fm else ""
        for field in ("bible_references", "primary_passage"):
            m = re.search(rf'^{field}:\s*(.+?)$', head, re.M | re.S)
            if not m:
                continue
            for ref in re.findall(r'"([^"]+)"', m.group(1)) or [m.group(1)]:
                for part in str(ref).split(";"):
                    hit = BOOK_IN_REF.match(part.strip().strip('"'))
                    if hit:
                        index[hit.group(1)].add(slug)
    return index


def sentences_about(text: str, chapter: str) -> list[str]:
    """Prose sentences naming the chapter. Frontmatter and scripture quote blocks are skipped --
    a quoted verse is not a claim the study is making."""
    fm = re.match(r"^---\n.*?\n---\n", text, re.S)
    body = text[fm.end():] if fm else text
    body = "\n".join(l for l in body.split("\n") if not l.lstrip().startswith(">"))
    book, num = chapter.rsplit(" ", 1)
    pattern = re.compile(rf'{re.escape(book)}\s+{num}\b(?!\d)')
    found = []
    for raw in re.split(r'(?<=[.!?])\s+(?=[A-Z"*])', body.replace("\n", " ")):
        if pattern.search(raw):
            found.append(re.sub(r"\s+", " ", raw).strip())
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("chapter", nargs="?", help='e.g. "Matthew 24"')
    ap.add_argument("--min-studies", type=int, default=3)
    args = ap.parse_args()

    corpus = studies()
    index = chapter_index(corpus)
    texts = dict(corpus)

    if args.chapter:
        slugs = sorted(index.get(args.chapter, ()))
        if not slugs:
            raise SystemExit(f"no study lists {args.chapter} in its frontmatter")
        print(f"{args.chapter} — {len(slugs)} studies\n")
        for slug in slugs:
            said = sentences_about(texts[slug], args.chapter)
            print(f"  {slug}")
            for s in said[:4]:
                print(f"      {s[:300]}")
            if not said:
                print("      (listed in frontmatter, never discussed in the prose)")
            print()
        return

    shared = {c: s for c, s in index.items() if len(s) >= args.min_studies}
    print(f"{len(shared)} chapters treated by {args.min_studies}+ studies — the surface where a "
          f"contradiction can hide.\nInspect one with: cross_study_claims.py \"Matthew 24\"\n")
    for chapter, slugs in sorted(shared.items(), key=lambda kv: -len(kv[1])):
        print(f"  {chapter:22} {len(slugs):2}  {', '.join(sorted(s.split('/')[-1][:-3] for s in slugs))[:96]}")


if __name__ == "__main__":
    main()
