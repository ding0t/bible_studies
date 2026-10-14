#!/usr/bin/env python3
"""Show what every study says about the same chapter, side by side.

The class of defect this exists for reads perfectly in isolation. rapture.md said Noah was removed
BEFORE the flood in one section and preserved THROUGH it in four others, and olivet-discourse.md --
which links to rapture.md -- had already settled the question the other way with lexical evidence.
day-is-near.md prayed a reading of Mark 13:32 that a whole sibling study exists to refute, and
plotted an AD 32 crucifixion that the site's own dating study rules out on the weekday.

Nothing catches that, because every phase of review checks a study against SOURCES. This checks
studies against EACH OTHER. It cannot judge; it lays the sentences out so a reader can.

The same lookup answers the question a new study should ask before it is researched, not after it
is drafted: what has this site already said about this chapter, so the new study can link to it,
build on it, or enrich it instead of re-arguing it. `sibling_studies` is that lookup, and
passage_brief returns it as its `existing_studies` section.

Frontmatter is the primary signal, but older studies often left `bible_references` empty, so a
study that discusses a chapter only in its prose is reported too, as role "prose". Book names are
matched by number, so "Psalm 23" and "Psalms 23" are one chapter.

    uv run python cross_study_claims.py --min-studies 4      # the whole surface, busiest first
    uv run python cross_study_claims.py "Matthew 24"         # one chapter, with the sentences
"""
import argparse
import collections
import pathlib
import re

import book_map

CONTENT = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "content"
REF_HEAD = re.compile(r'^((?:[1-3]\s)?[A-Za-z][A-Za-z ]*?)\s(\d+)')
ROLE_ORDER = {"primary": 0, "cited": 1, "prose": 2}

_NAME_TO_NUM = {name.lower(): num for name, num in book_map.REFERENCE_NAME_TO_NUM.items()}
_NAME_TO_NUM.update({slug.replace("-", " "): num for num, slug in book_map.NUM_TO_SLUG.items()})
_OSIS_TO_NUM = {osis: num for num, osis in book_map.NUM_TO_OSIS.items()}


def book_number(name: str) -> int | None:
    """A book given as a frontmatter-style name ("Song of Solomon", "Psalm") or an OSIS code."""
    return _NAME_TO_NUM.get(name.strip().lower()) or _OSIS_TO_NUM.get(name.strip())


def display(num: int, chapter: int) -> str:
    name = book_map.NUM_TO_SLUG[num].replace("-", " ").title().replace(" Of ", " of ")
    return f"{name} {chapter}"


def parse_chapter(text: str) -> tuple[int, int] | None:
    """"Matthew 24", "Psalm 23:1-4", "Matt 24" -> (book number, chapter)."""
    hit = REF_HEAD.match(text.strip().strip('"'))
    if not hit:
        return None
    num = book_number(hit.group(1))
    return (num, int(hit.group(2))) if num else None


def studies() -> list[tuple[str, str]]:
    """(slug, text) for every hand-written study, generated cross-reference pages excluded."""
    out = []
    for path in sorted(CONTENT.rglob("*.md")):
        # about/ holds the backlog, the statement of faith and site pages: none is a study, and the
        # backlog names nearly every chapter the site plans to cover.
        if path.relative_to(CONTENT).parts[0] == "about":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "commentary-index:auto-start" in text or "section-index:auto-start" in text:
            continue
        out.append((str(path.relative_to(CONTENT)), text))
    return out


def _frontmatter(text: str) -> str:
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return fm.group(1) if fm else ""


def frontmatter_refs(text: str, field: str) -> list[str]:
    m = re.search(rf'^{field}:\s*(.+?)$', _frontmatter(text), re.M)
    if not m:
        return []
    refs = []
    for ref in re.findall(r'"([^"]+)"', m.group(1)) or [m.group(1)]:
        refs.extend(p.strip().strip('"') for p in ref.split(";") if p.strip())
    return refs


def chapter_index(corpus) -> dict[tuple[int, int], set[str]]:
    """(book number, chapter) -> the studies naming it in bible_references or primary_passage."""
    index = collections.defaultdict(set)
    for slug, text in corpus:
        for field in ("bible_references", "primary_passage"):
            for ref in frontmatter_refs(text, field):
                key = parse_chapter(ref)
                if key:
                    index[key].add(slug)
    return index


def _chapter_pattern(num: int, chapter: int) -> re.Pattern:
    names = sorted({n for n, k in book_map.REFERENCE_NAME_TO_NUM.items() if k == num}
                   | {book_map.NUM_TO_SLUG[num].replace("-", " ").title().replace(" Of ", " of ")},
                   key=len, reverse=True)
    alternation = "|".join(re.escape(n) for n in names)
    # The lookbehinds keep "John 3" from matching inside "1 John 3" or "Johnson 3".
    return re.compile(rf'(?<![123] )(?<!\w)(?:{alternation})\s+{chapter}(?!\d)')


def sentences_about(text: str, num: int, chapter: int) -> list[str]:
    """Prose sentences naming the chapter. Frontmatter and scripture quote blocks are skipped --
    a quoted verse is not a claim the study is making."""
    fm = re.match(r"^---\n.*?\n---\n", text, re.S)
    body = text[fm.end():] if fm else text
    body = "\n".join(l for l in body.split("\n") if not l.lstrip().startswith(">"))
    pattern = _chapter_pattern(num, chapter)
    # A heading, list item or table row ends a sentence even without a full stop.
    blocks = re.split(r'\n\s*\n|\n(?=\s*(?:#|[-*] |\d+\. |\|))', body)
    found = []
    for block in blocks:
        for raw in re.split(r'(?<=[.!?])\s+(?=[A-Z"*])', block.replace("\n", " ")):
            if pattern.search(raw):
                found.append(re.sub(r"\s+", " ", raw).strip(" -#*|"))
    return found


def sibling_studies(book: str, chapter: int, exclude: str | None = None,
                    corpus=None, max_sentences: int = 2) -> list[dict]:
    """Every study that treats this chapter, the ones centrally about it first.

    role: primary  -- the chapter is in its primary_passage; a new study should link to it
                      rather than re-argue it, and check it agrees
          cited    -- the chapter is in its bible_references
          prose    -- named in the prose only; the frontmatter under-reports it
    `exclude` is a slug (path under docs/content) to leave out -- the study being written.
    """
    num = book_number(book)
    if num is None:
        raise ValueError(f"{book!r} is not a book name or OSIS code")
    out = []
    for slug, text in corpus if corpus is not None else studies():
        if slug == exclude:
            continue
        primary = [r for r in frontmatter_refs(text, "primary_passage")
                   if parse_chapter(r) == (num, chapter)]
        cited = [r for r in frontmatter_refs(text, "bible_references")
                 if parse_chapter(r) == (num, chapter)]
        said = sentences_about(text, num, chapter)
        if not (primary or cited or said):
            continue
        head = _frontmatter(text)
        title = re.search(r'^title:\s*"?(.*?)"?\s*$', head, re.M)
        out.append({
            "slug": slug,
            "title": title.group(1) if title else slug,
            "draft": bool(re.search(r'^draft:\s*true\b', head, re.M)),
            "role": "primary" if primary else "cited" if cited else "prose",
            "refs": list(dict.fromkeys(primary + cited)),
            "prose_mentions": len(said),
            "sentences": [s[:300] for s in said[:max_sentences]],
        })
    out.sort(key=lambda s: (ROLE_ORDER[s["role"]], -s["prose_mentions"], s["slug"]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("chapter", nargs="?", help='e.g. "Matthew 24"')
    ap.add_argument("--min-studies", type=int, default=3)
    ap.add_argument("--exclude", help="slug under docs/content to leave out (the study being written)")
    args = ap.parse_args()

    if args.chapter:
        key = parse_chapter(args.chapter)
        if not key:
            raise SystemExit(f"cannot read {args.chapter!r} as a book and chapter")
        found = sibling_studies(book_map.NUM_TO_OSIS[key[0]], key[1], exclude=args.exclude,
                                max_sentences=4)
        if not found:
            raise SystemExit(f"no study treats {display(*key)}")
        print(f"{display(*key)} — {len(found)} studies\n")
        for s in found:
            flags = s["role"] + (", draft" if s["draft"] else "")
            refs = f"  [{', '.join(s['refs'])}]" if s["refs"] else ""
            print(f"  {s['slug']}  ({flags}){refs}")
            for sentence in s["sentences"]:
                print(f"      {sentence}")
            if not s["sentences"]:
                print("      (listed in frontmatter, never discussed in the prose)")
            print()
        return

    index = chapter_index(studies())
    shared = {c: s for c, s in index.items() if len(s) >= args.min_studies}
    print(f"{len(shared)} chapters treated by {args.min_studies}+ studies — the surface where a "
          f"contradiction can hide.\nInspect one with: cross_study_claims.py \"Matthew 24\"\n")
    for key, slugs in sorted(shared.items(), key=lambda kv: -len(kv[1])):
        print(f"  {display(*key):22} {len(slugs):2}  "
              f"{', '.join(sorted(s.split('/')[-1][:-3] for s in slugs))[:96]}")


if __name__ == "__main__":
    main()
