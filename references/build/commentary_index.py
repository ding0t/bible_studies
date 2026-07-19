"""Maintains docs/content/bible/commentaries/<NN>-<book>/ as an auto-generated cross-reference
index into docs/content/studies/**/*.md, keyed by which passage each study is actually about.

Source of truth: every study's `bible_references` (supporting) and `primary_passage` (the
passage(s) the study is centrally about) frontmatter fields. Only 4 of 24 study files have
either populated as of writing this -- the index will be sparse until more studies gain that
frontmatter. That's expected; this script doesn't invent references that aren't there.

Safe to re-run any time (idempotent) and safe to hand-edit commentary content around what this
script writes: every chapter file and book index.md gets exactly one delimited auto-generated
section (between AUTO_START/AUTO_END below); everything outside those markers is left alone,
including on files this script didn't create.

Usage: uv run python commentary_index.py
"""
import re
from datetime import date
from pathlib import Path

from book_map import NUM_TO_SLUG, REFERENCE_NAME_TO_NUM

REPO_ROOT = Path(__file__).resolve().parents[2]
STUDIES_DIR = REPO_ROOT / "docs" / "content" / "studies"
COMMENTARIES_DIR = REPO_ROOT / "docs" / "content" / "bible" / "commentaries"
TODAY = date.today().isoformat()

AUTO_START = "<!-- commentary-index:auto-start -->"
AUTO_END = "<!-- commentary-index:auto-end -->"

_NAME_TO_NUM_LOWER = {name.lower(): num for name, num in REFERENCE_NAME_TO_NUM.items()}
_REF_PATTERN = re.compile(r"^\s*(\d?\s?[A-Za-z][A-Za-z ]*?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?\s*$")


def parse_reference(ref: str) -> tuple[int, int, str] | None:
    """'Mark 5:25-34' -> (41, 5, '5:25-34'). 'Leviticus 23' (chapter only, no verse -- CONTENT_GUIDE.md's
    own example format) -> (3, 23, '23'). Single-chapter references only (a range spanning chapters
    returns None rather than guessing)."""
    match = _REF_PATTERN.match(ref.strip())
    if not match:
        return None
    book_name, chapter, verse_start, verse_end = match.groups()
    book_num = _NAME_TO_NUM_LOWER.get(book_name.strip().lower())
    if book_num is None:
        return None
    verse_display = chapter if verse_start is None else f"{chapter}:{verse_start}" + (f"-{verse_end}" if verse_end else "")
    return book_num, int(chapter), verse_display


def split_compound(ref: str) -> list[str]:
    """'Matthew 26:26-29; Mark 14:22-26' -> two references."""
    return [part.strip() for part in ref.split(";") if part.strip()]


def collect_references() -> dict[tuple[int, int], list[dict]]:
    """book/chapter -> list of {title, url, ref_display, is_primary} for every study touching it."""
    import yaml

    by_chapter: dict[tuple[int, int], list[dict]] = {}
    unparsed: list[str] = []

    for md_file in sorted(STUDIES_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            continue

        if fm.get("draft") is True:
            continue

        title = fm.get("title", md_file.stem)
        rel_path = md_file.relative_to(STUDIES_DIR)  # e.g. feasts/last-supper-four-cups.md

        entries = [(r, True) for r in split_compound(fm.get("primary_passage") or "")]
        entries += [(r, False) for r in (fm.get("bible_references") or [])]

        seen_this_file: set[tuple[int, int]] = set()
        for ref, is_primary in entries:
            parsed = parse_reference(ref)
            if parsed is None:
                unparsed.append(f"{md_file.relative_to(REPO_ROOT)}: {ref!r}")
                continue
            book_num, chapter, verse_display = parsed
            key = (book_num, chapter)
            # A study can list the same chapter via both primary_passage and bible_references;
            # keep the primary flag if either mention was primary, don't duplicate the entry.
            if key in seen_this_file:
                if is_primary:
                    for e in by_chapter[key]:
                        if e["rel_path"] == str(rel_path):
                            e["is_primary"] = True
                            e["ref_display"] = verse_display
                continue
            seen_this_file.add(key)
            by_chapter.setdefault(key, []).append({
                "title": title, "rel_path": str(rel_path),
                "ref_display": verse_display, "is_primary": is_primary,
            })

    if unparsed:
        print("Unparsed references (skipped, not guessed at):")
        for u in unparsed:
            print(f"  {u}")

    return by_chapter


def render_auto_section(entries: list[dict], depth_prefix: str) -> str:
    entries = sorted(entries, key=lambda e: (not e["is_primary"], e["title"]))
    lines = [AUTO_START, "## Studies referencing this chapter", ""]
    for e in entries:
        marker = " (primary passage)" if e["is_primary"] else ""
        lines.append(f"- [{e['title']}]({depth_prefix}studies/{e['rel_path']}) — {e['ref_display']}{marker}")
    lines.append(AUTO_END)
    return "\n".join(lines)


def upsert_auto_section(path: Path, auto_section: str, stub_frontmatter: str) -> None:
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if AUTO_START in content and AUTO_END in content:
            pre = content.split(AUTO_START)[0]
            post = content.split(AUTO_END)[1]
            path.write_text(pre + auto_section + post, encoding="utf-8")
        else:
            # Hand-authored file with no auto section yet -- append one rather than guessing
            # where it belongs.
            path.write_text(content.rstrip("\n") + "\n\n" + auto_section + "\n", encoding="utf-8")
    else:
        path.write_text(stub_frontmatter + "\n" + auto_section + "\n", encoding="utf-8")


def cleanup_orphaned(
    by_chapter: dict[tuple[int, int], list[dict]], books_touched: dict[int, list[int]]
) -> tuple[list[str], list[str]]:
    """Remove chapter files (always fully auto-generated) and empty out book indexes for
    books/chapters that no longer have any referencing study -- e.g. a study went back to
    draft, or a reference was removed. Chapter files are safe to delete outright since this
    script never leaves hand-written content in them; book index.md files can carry real
    hand-written prose (see 27-daniel/index.md), so those are only ever emptied, never deleted."""
    removed_chapters, emptied_books = [], []
    if not COMMENTARIES_DIR.exists():
        return removed_chapters, emptied_books

    for book_dir in sorted(COMMENTARIES_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        try:
            book_num = int(book_dir.name.split("-", 1)[0])
        except ValueError:
            continue

        for chapter_path in sorted(book_dir.glob("chapter-*.md")):
            try:
                chapter = int(chapter_path.stem.split("-", 1)[1])
            except (IndexError, ValueError):
                continue
            if (book_num, chapter) not in by_chapter:
                chapter_path.unlink()
                removed_chapters.append(str(chapter_path.relative_to(REPO_ROOT)))

        index_path = book_dir / "index.md"
        if book_num not in books_touched and index_path.exists():
            content = index_path.read_text(encoding="utf-8")
            if AUTO_START in content and AUTO_END in content:
                empty_auto = f"{AUTO_START}\n*No studies currently reference this book.*\n{AUTO_END}"
                pre, post = content.split(AUTO_START)[0], content.split(AUTO_END)[1]
                new_content = pre + empty_auto + post
                if new_content != content:
                    index_path.write_text(new_content, encoding="utf-8")
                    emptied_books.append(str(index_path.relative_to(REPO_ROOT)))

    return removed_chapters, emptied_books


def main() -> None:
    by_chapter = collect_references()
    books_touched: dict[int, list[int]] = {}
    for (book_num, chapter) in by_chapter:
        books_touched.setdefault(book_num, []).append(chapter)

    removed_chapters, emptied_books = cleanup_orphaned(by_chapter, books_touched)

    for book_num, chapters in sorted(books_touched.items()):
        slug = NUM_TO_SLUG[book_num]
        book_dir = COMMENTARIES_DIR / f"{book_num:02d}-{slug}"
        book_dir.mkdir(parents=True, exist_ok=True)
        book_title = slug.replace("-", " ").title()

        for chapter in sorted(chapters):
            entries = by_chapter[(book_num, chapter)]
            chapter_path = book_dir / f"chapter-{chapter:03d}.md"
            auto_section = render_auto_section(entries, "../../../")
            stub = (
                f"---\ntitle: \"{book_title} {chapter}\"\ncategory: \"bible\"\n"
                f"description: \"Commentary and cross-referenced studies for {book_title} chapter {chapter}\"\n"
                f"tags: [\"{slug}\", \"commentary\"]\ndraft: false\n---\n\n"
                f"# {book_title} {chapter}\n\n"
            )
            upsert_auto_section(chapter_path, auto_section, stub)

        # Book index: chapter listing, auto-maintained the same way.
        index_path = book_dir / "index.md"
        chapter_links = "\n".join(
            f"- [Chapter {c}](chapter-{c:03d}.md) — {len(by_chapter[(book_num, c)])} study(ies)"
            for c in sorted(chapters)
        )
        index_auto = f"{AUTO_START}\n## Chapters with linked studies\n\n{chapter_links}\n{AUTO_END}"
        index_stub = (
            f"---\ntitle: \"{book_title}\"\ncategory: \"bible\"\n"
            f"description: \"Commentary on {book_title}\"\ntags: [\"{slug}\", \"commentary\"]\ndraft: false\n---\n\n"
            f"# {book_title}\n\n"
        )
        upsert_auto_section(index_path, index_auto, index_stub)

    print(f"\n{len(books_touched)} book(s), {len(by_chapter)} chapter(s) with linked studies.")
    if removed_chapters:
        print(f"Removed {len(removed_chapters)} orphaned chapter file(s):")
        for r in removed_chapters:
            print(f"  removed: {r}")
    if emptied_books:
        print(f"Emptied {len(emptied_books)} book index(es) with no remaining chapters:")
        for e in emptied_books:
            print(f"  emptied: {e}")
    print(f"Regenerated: {TODAY}")


if __name__ == "__main__":
    main()
