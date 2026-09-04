"""What the tradition connects to a study's passages that the study never mentions.

The point of backlog item 1.2, and the thing that has to prove out before anything downstream is
worth building: if it doesn't change a study, the rest isn't worth having.

Takes a study's own `primary_passage` and `bible_references` frontmatter, gathers what links to
those passages from two independent directions, subtracts everything the study already cites, and
reports what is left. Two sources, kept apart rather than merged:

  quotation    derived from the texts themselves (see quotations.py). The New Testament quoting the
               Septuagint in Greek, and the Hebrew Old Testament quoting itself, are both textual
               facts rather than opinions.
  candidate    a Hebrew New Testament matching the Hebrew Old Testament. Those are 19th-century
               translations, so this is a Hebraist's judgement -- it catches quotations the Greek
               misses, but verify each one in Greek before it carries weight.
  crossref     openbible's crowd-assembled cross-references. A lead worth chasing, and no more --
               the votes are consensus from a largely covenantal readership, so a high score is
               popularity rather than evidence.

Usage:  uv run python study_gaps.py docs/content/last-things/rapture.md
        uv run python study_gaps.py --all --limit 5
"""
import argparse
import sqlite3
import sys
from pathlib import Path

import yaml

import versification
from book_map import NUM_TO_OSIS, REFERENCE_NAME_TO_NUM
from commentary_index import CONTENT_DIR, SUBJECT_DIRS, parse_reference, split_compound

DB_PATH = Path(__file__).resolve().parent / "out" / "bible-text.db"
REPO_ROOT = Path(__file__).resolve().parents[2]
STRONG_ALIGNMENT = 18   # see quotations.py for the audit that set it
MIN_VOTES = 12          # openbible's long tail is noise; this keeps the well-attested links


def study_references(md_file: Path) -> tuple[str, set[tuple[str, int]], list[str]]:
    """(title, {(osis_book, chapter)}, raw reference strings) from a study's frontmatter."""
    content = md_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return md_file.stem, set(), []
    parts = content.split("---", 2)
    frontmatter = yaml.safe_load(parts[1]) or {}
    raw = split_compound(frontmatter.get("primary_passage") or "")
    raw += list(frontmatter.get("bible_references") or [])
    chapters = set()
    for ref in raw:
        parsed = parse_reference(ref)
        if parsed:
            book_num, chapter, _ = parsed
            chapters.add((NUM_TO_OSIS[book_num], chapter))
    return frontmatter.get("title", md_file.stem), chapters, raw


def gaps_for(conn: sqlite3.Connection, chapters: set[tuple[str, int]]) -> list[dict]:
    """Links out of the study's passages that land on a chapter the study never cites."""
    found: dict[tuple[str, int], dict] = {}

    def note(book, chapter, verse, kind, detail, source_ref):
        if (book, chapter) in chapters:
            return                      # the study already treats this chapter
        entry = found.setdefault((book, chapter), {
            "book": book, "chapter": chapter, "quotation": 0, "candidate": 0, "crossref": 0,
            "detail": [], "from": set()})
        entry[kind] += 1
        entry["from"].add(source_ref)
        if detail and detail not in entry["detail"] and len(entry["detail"]) < 3:
            entry["detail"].append(detail)

    for book, chapter in sorted(chapters):
        source = f"{book} {chapter}"
        # links out of this chapter, in every class
        for r in conn.execute(
            "SELECT link_type, from_verse, to_book, to_english_chapter, to_english_verse, "
            "alignment, corroborated FROM scripture_links WHERE from_book=? AND from_chapter=? "
            "AND alignment>=? AND to_english_chapter IS NOT NULL", (book, chapter, STRONG_ALIGNMENT)):
            mark = "*" if r["corroborated"] else " "
            kind = "candidate" if r["link_type"] == "quotation-hebrew" else "quotation"
            note(r["to_book"], r["to_english_chapter"], r["to_english_verse"], kind,
                 f"{source}:{r['from_verse']} quotes {r['to_book']} "
                 f"{r['to_english_chapter']}:{r['to_english_verse']} (align {r['alignment']}){mark}",
                 source)

        # and links INTO it -- the reference has to be aligned into each class's own scheme first
        for link_type, scheme in (("quotation-greek", "lxx"), ("inner-biblical", "masoretic"),
                                  ("quotation-hebrew", "masoretic")):
            target = versification.align(book, chapter, 1, "english", scheme)
            if target is None:
                continue
            for r in conn.execute(
                "SELECT from_book, from_chapter, from_verse, alignment, corroborated "
                "FROM scripture_links WHERE link_type=? AND to_book=? AND to_chapter=? AND alignment>=?",
                (link_type, target[0], target[1], STRONG_ALIGNMENT)):
                mark = "*" if r["corroborated"] else " "
                kind = "candidate" if link_type == "quotation-hebrew" else "quotation"
                note(r["from_book"], r["from_chapter"], r["from_verse"], kind,
                     f"{r['from_book']} {r['from_chapter']}:{r['from_verse']} quotes {source} "
                     f"(align {r['alignment']}){mark}", source)

        for r in conn.execute(
            "SELECT DISTINCT to_book, to_chapter, to_verse_start, votes FROM cross_references "
            "WHERE from_book=? AND from_chapter=? AND votes>=? ORDER BY votes DESC LIMIT 60",
            (book, chapter, MIN_VOTES)):
            note(r["to_book"], r["to_chapter"], r["to_verse_start"], "crossref", None, source)

    ranked = sorted(found.values(),
                    key=lambda e: (-e["quotation"], -e["candidate"], -e["crossref"],
                                   e["book"], e["chapter"]))
    return ranked


def report(conn, md_file: Path, limit: int) -> int:
    title, chapters, raw = study_references(md_file)
    rel = md_file.relative_to(REPO_ROOT)
    if not chapters:
        print(f"\n{title}  ({rel})\n  no primary_passage or bible_references -- invisible to this check")
        return 0
    ranked = gaps_for(conn, chapters)
    print(f"\n{title}  ({rel})")
    print(f"  cites {len(chapters)} chapters; {len(ranked)} chapters link in that it never mentions")
    for entry in ranked[:limit]:
        kinds = []
        if entry["quotation"]:
            kinds.append(f"{entry['quotation']} quotation")
        if entry["candidate"]:
            kinds.append(f"{entry['candidate']} hebrew-candidate")
        if entry["crossref"]:
            kinds.append(f"{entry['crossref']} crossref")
        print(f"    {entry['book']} {entry['chapter']:<4} {', '.join(kinds)}"
              f"   <- {', '.join(sorted(entry['from'])[:3])}")
        for d in entry["detail"]:
            print(f"        {d}")
    return len(ranked)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("study", nargs="?", help="path to a study markdown file")
    parser.add_argument("--all", action="store_true", help="every study with reference frontmatter")
    parser.add_argument("--limit", type=int, default=8, help="gaps to show per study")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"{DB_PATH} not found -- run `uv run python build.py` first", file=sys.stderr)
        return 1
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    if args.all:
        files = sorted(md for section in SUBJECT_DIRS
                       if (CONTENT_DIR / section).is_dir()
                       for md in (CONTENT_DIR / section).rglob("*.md"))
    elif args.study:
        # accept a repo-relative path as well as one relative to the cwd -- this script lives in
        # references/build but the natural thing to type is docs/content/<section>/<study>.md
        given = Path(args.study)
        candidates = [given, REPO_ROOT / given]
        found = next((c for c in candidates if c.is_file()), None)
        if found is None:
            parser.error(f"no such study: {args.study}")
        files = [found.resolve()]
    else:
        parser.error("give a study path or --all")

    for md_file in files:
        report(conn, md_file, args.limit)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
