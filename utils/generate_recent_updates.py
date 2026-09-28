"""Generates docs/content/about/recent-updates.md (a full chronological list) and refreshes the
"Recently Updated" teaser on docs/content/index.md, both driven by git commit history rather than
a hand-maintained date field -- a page counts as recently updated exactly when its last commit
says so, so there's nothing to remember to update by hand.

New pages are listed apart from updated ones, because with updates landing daily a new study
otherwise scrolls off the list within a day or two. "New" means *first published*: the commit that
took the page out of `draft: true`, or its first commit if it was never a draft. `date_created`
will not do, because it is the first commit, and a study drafted for three weeks before going live
would count as three weeks old on the day it appears. The same dates are written to
docs/data/published.json, which hooks/new_pages.py reads to mark each new page, and its sidebar
entry, for the same window.

Same delimited auto-section pattern as section_index.py/commentary_index.py: only the text
between the AUTO_START/AUTO_END markers on each page is regenerated, so hand-written prose
around it survives re-runs. Both target pages must already have their marker pairs in place --
this script fills the sections in, it doesn't create the surrounding page (recent-updates.md
ships with the markers already; if it's ever deleted, recreate it with an intro paragraph and
empty <!-- new-pages:auto-start/end --> and <!-- recent-updates:auto-start/end --> markers
before re-running).

stdlib-only (git log via subprocess, hand-rolled frontmatter scalars) on purpose, so it can run
in CI without syncing the references/build/ venv (that pyproject pulls in bibleorgsys, pymupdf,
etc. -- far more than parsing `title`/`description`/`draft` needs). Requires a working tree with
full git history (`fetch-depth: 0` in CI, already set for the deploy job).
"""
import argparse
import json
import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "docs" / "content"

FULL_PAGE = CONTENT_DIR / "about" / "recent-updates.md"
HOME_PAGE = CONTENT_DIR / "index.md"
PUBLISHED_JSON = REPO_ROOT / "docs" / "data" / "published.json"

FULL_START = "<!-- recent-updates:auto-start -->"
FULL_END = "<!-- recent-updates:auto-end -->"
NEW_START = "<!-- new-pages:auto-start -->"
NEW_END = "<!-- new-pages:auto-end -->"
TEASER_START = "<!-- recent-updates-teaser:auto-start -->"
TEASER_END = "<!-- recent-updates-teaser:auto-end -->"
NEW_TEASER_START = "<!-- new-pages-teaser:auto-start -->"
NEW_TEASER_END = "<!-- new-pages-teaser:auto-end -->"

FULL_COUNT = 20
TEASER_COUNT = 5
NEW_TEASER_COUNT = 6
# A rolling window rather than the calendar month, so the list is never empty on the 1st. The
# hook reads this from published.json, so the page badge and the lists expire together.
NEW_WINDOW_DAYS = 30

FRONT_SCALAR = re.compile(r"^(\w+):\s*(.*)$")
# --unified=0 diff lines that add or remove the frontmatter flag. The "+++ b/..." file header
# cannot match, since it has no "draft:" after the sign.
DRAFT_LINE = re.compile(r"^([+-])draft:\s*[\"']?(\w+)", re.MULTILINE)


def parse_frontmatter(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].splitlines():
        match = FRONT_SCALAR.match(line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1].replace('\\"', '"')
        fm[key] = value
    return fm


def git_history(md_path: Path) -> list[tuple[date, str]]:
    """Every commit that touched this file, oldest first, as (date, --unified=0 diff). Empty if
    it has no history yet (freshly created and uncommitted -- nothing to report until then)."""
    rel = md_path.relative_to(REPO_ROOT)
    out = subprocess.run(
        ["git", "log", "--follow", "--reverse", "-p", "--unified=0",
         "--format=%x01%ad", "--date=short", "--", str(rel)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    history = []
    for record in out.split("\x01")[1:]:
        day, _, diff = record.partition("\n")
        history.append((datetime.strptime(day.strip(), "%Y-%m-%d").date(), diff))
    return history


def first_published(history: list[tuple[date, str]]) -> date | None:
    """The date of the commit where the page first stopped being a draft: created without
    `draft: true`, flipped to false, or had the flag deleted. None if every commit so far left
    it a draft."""
    for i, (day, diff) in enumerate(history):
        flag_lines = DRAFT_LINE.findall(diff)
        added = {value.lower() for sign, value in flag_lines if sign == "+"}
        if i == 0:
            if "true" not in added:
                return day
        elif "false" in added or (flag_lines and not added):
            return day
    return None


def is_auto_generated_stub(md_path: Path) -> bool:
    """commentary_index.py's chapter-*.md files are fully machine-written every run -- title,
    description, and the whole body are template-filled, never hand-authored prose (see the
    cleanup_orphaned docstring in references/build/commentary_index.py, which deletes them
    outright on that basis). They carry real frontmatter so collect_pages() would otherwise
    treat them as new/updated content -- a study that touches one chapter cross-ref regenerates
    dozens of these, and they'd bury the actual studies that made those links in the process."""
    return md_path.relative_to(CONTENT_DIR).parts[0] == "commentaries" and md_path.stem.startswith("chapter-")


def collect_pages(today: date) -> list[dict]:
    pages = []
    for md_path in CONTENT_DIR.rglob("*.md"):
        if md_path.name == "index.md" or md_path == FULL_PAGE:
            continue  # section landing pages and this list itself aren't "content"
        if is_auto_generated_stub(md_path):
            continue
        fm = parse_frontmatter(md_path)
        if not fm or fm.get("draft") == "true":
            continue
        history = git_history(md_path)
        if not history:
            continue
        # Never published in git but not a draft on disk: the flip is in the working tree, so
        # it is being published by the commit about to be made.
        published = first_published(history) or today
        pages.append({
            "title": fm.get("title", md_path.stem),
            "description": fm.get("description", ""),
            "path": md_path,
            "last": history[-1][0],
            "published": published,
            "is_new": (today - published).days < NEW_WINDOW_DAYS,
        })
    pages.sort(key=lambda p: (-p["last"].toordinal(), p["title"]))
    return pages


def link_from(page: dict, from_dir: Path) -> str:
    rel = os.path.relpath(page["path"], from_dir)
    return rel.replace("\\", "/")


def long_date(day: date) -> str:
    return f"{day.day} {day:%B %Y}"


def new_pages(pages: list[dict]) -> list[dict]:
    return sorted((p for p in pages if p["is_new"]), key=lambda p: (-p["published"].toordinal(), p["title"]))


def card(page: dict, from_dir: Path, footer: str) -> str:
    lines = [f"-   __{page['title']}__", "", "    ---", ""]
    if page["description"]:
        lines.append(f"    {page['description']}")
        lines.append("")
    lines.append(f"    {footer} · [:octicons-arrow-right-24: Read]({link_from(page, from_dir)})")
    return "\n".join(lines)


def grid(start: str, end: str, cards: list[str], empty: str) -> str:
    if not cards:
        return f"{start}\n*{empty}*\n{end}"
    return f"{start}\n<div class=\"grid cards\" markdown>\n\n" + "\n\n".join(cards) + f"\n\n</div>\n{end}"


def new_footer(page: dict) -> str:
    footer = f":material-new-box: Published {long_date(page['published'])}"
    if page["last"] > page["published"]:
        footer += f", revised {long_date(page['last'])}"
    return footer


def updated_footer(page: dict) -> str:
    return f":material-update: Updated {long_date(page['last'])}"


def render_new_section(pages: list[dict]) -> str:
    from_dir = FULL_PAGE.parent
    cards = [card(page, from_dir, new_footer(page)) for page in new_pages(pages)]
    return grid(NEW_START, NEW_END, cards, f"Nothing new in the last {NEW_WINDOW_DAYS} days.")


def render_full_section(pages: list[dict]) -> str:
    # A new page's revisions are part of its being new, so it stays in the section above
    # instead of appearing twice.
    from_dir = FULL_PAGE.parent
    updated = [p for p in pages if not p["is_new"]][:FULL_COUNT]
    cards = [card(page, from_dir, updated_footer(page)) for page in updated]
    return grid(FULL_START, FULL_END, cards, "Nothing published yet.")


def render_new_teaser_section(pages: list[dict]) -> str:
    from_dir = HOME_PAGE.parent
    cards = [card(page, from_dir, new_footer(page)) for page in new_pages(pages)[:NEW_TEASER_COUNT]]
    return grid(NEW_TEASER_START, NEW_TEASER_END, cards, f"Nothing new in the last {NEW_WINDOW_DAYS} days.")


def render_teaser_section(pages: list[dict]) -> str:
    from_dir = HOME_PAGE.parent
    items = []
    for page in [p for p in pages if not p["is_new"]][:TEASER_COUNT]:
        items.append(f"- **[{page['title']}]({link_from(page, from_dir)})** — {updated_footer(page)}")
    if not items:
        return f"{TEASER_START}\n*Nothing published yet.*\n{TEASER_END}"
    return f"{TEASER_START}\n" + "\n".join(items) + f"\n{TEASER_END}"


def replace_section(path: Path, start: str, end: str, section: str) -> bool:
    content = path.read_text(encoding="utf-8")
    if start not in content or end not in content:
        print(f"skip {path.relative_to(REPO_ROOT)}: no {start} marker pair -- add it by hand first")
        return False
    new_content = content.split(start)[0] + section + content.split(end)[1]
    if new_content == content:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def write_published_json(pages: list[dict]) -> bool:
    """Every published page's first-published date, keyed by its path under docs/content (the
    `src_uri` mkdocs gives the hook). All pages, not only new ones, so the file changes only
    when a page is published, not every day a page ages out of the window."""
    data = {
        "window_days": NEW_WINDOW_DAYS,
        "published": {
            p["path"].relative_to(CONTENT_DIR).as_posix(): p["published"].isoformat()
            for p in sorted(pages, key=lambda p: p["path"])
        },
    }
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if PUBLISHED_JSON.exists() and PUBLISHED_JSON.read_text(encoding="utf-8") == text:
        return False
    PUBLISHED_JSON.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    ).parse_args()
    today = date.today()
    pages = collect_pages(today)
    changed = []
    sections = [
        (FULL_PAGE, NEW_START, NEW_END, render_new_section(pages)),
        (FULL_PAGE, FULL_START, FULL_END, render_full_section(pages)),
        (HOME_PAGE, NEW_TEASER_START, NEW_TEASER_END, render_new_teaser_section(pages)),
        (HOME_PAGE, TEASER_START, TEASER_END, render_teaser_section(pages)),
    ]
    for path, start, end, section in sections:
        if replace_section(path, start, end, section):
            changed.append(str(path.relative_to(REPO_ROOT)))
    if write_published_json(pages):
        changed.append(str(PUBLISHED_JSON.relative_to(REPO_ROOT)))
    if changed:
        print(f"Updated: {', '.join(sorted(set(changed)))}")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
