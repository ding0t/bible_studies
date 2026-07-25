"""Generates docs/content/about/recent-updates.md (a full chronological list) and refreshes the
"Recently Updated" teaser on docs/content/index.md, both driven by git commit history rather than
a hand-maintained date field -- a page counts as recently updated exactly when its last commit
says so, so there's nothing to remember to update by hand.

Same delimited auto-section pattern as section_index.py/commentary_index.py: only the text
between the AUTO_START/AUTO_END markers on each page is regenerated, so hand-written prose
around it survives re-runs. Both target pages must already have their marker pair in place --
this script fills the section in, it doesn't create the surrounding page (recent-updates.md
ships with the markers already; if it's ever deleted, recreate it with an intro paragraph and
empty <!-- recent-updates:auto-start/end --> markers before re-running).

stdlib-only (git log via subprocess, hand-rolled frontmatter scalars) on purpose, so it can run
in CI without syncing the references/build/ venv (that pyproject pulls in bibleorgsys, pymupdf,
etc. -- far more than parsing `title`/`description`/`draft` needs). Requires a working tree with
full git history (`fetch-depth: 0` in CI, already set for the deploy job).

Usage: python3 utils/generate_recent_updates.py
"""
import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "docs" / "content"

FULL_PAGE = CONTENT_DIR / "about" / "recent-updates.md"
HOME_PAGE = CONTENT_DIR / "index.md"

FULL_START = "<!-- recent-updates:auto-start -->"
FULL_END = "<!-- recent-updates:auto-end -->"
TEASER_START = "<!-- recent-updates-teaser:auto-start -->"
TEASER_END = "<!-- recent-updates-teaser:auto-end -->"

FULL_COUNT = 20
TEASER_COUNT = 5
# A page counts as "New" rather than "Updated" if its whole commit history so far fits in this
# window -- i.e. it hasn't been revised since shortly after it was first published.
NEW_WINDOW_DAYS = 14

FRONT_SCALAR = re.compile(r"^(\w+):\s*(.*)$")


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
            value = value[1:-1]
        fm[key] = value
    return fm


def git_dates(md_path: Path) -> tuple[date, date] | None:
    """(first_commit_date, last_commit_date) for this file, or None if it has no commit history
    yet (freshly created and uncommitted -- nothing to report until it's committed)."""
    rel = md_path.relative_to(REPO_ROOT)
    out = subprocess.run(
        ["git", "log", "--follow", "--format=%ad", "--date=short", "--", str(rel)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not out:
        return None
    commit_dates = out.splitlines()
    last = datetime.strptime(commit_dates[0], "%Y-%m-%d").date()
    first = datetime.strptime(commit_dates[-1], "%Y-%m-%d").date()
    return first, last


def is_auto_generated_stub(md_path: Path) -> bool:
    """commentary_index.py's chapter-*.md files are fully machine-written every run -- title,
    description, and the whole body are template-filled, never hand-authored prose (see the
    cleanup_orphaned docstring in references/build/commentary_index.py, which deletes them
    outright on that basis). They carry real frontmatter so collect_pages() would otherwise
    treat them as new/updated content -- a study that touches one chapter cross-ref regenerates
    dozens of these, and they'd bury the actual studies that made those links in the process."""
    rel_parts = md_path.relative_to(CONTENT_DIR).parts
    return rel_parts[:2] == ("bible", "commentaries") and md_path.stem.startswith("chapter-")


def collect_pages() -> list[dict]:
    pages = []
    for md_path in CONTENT_DIR.rglob("*.md"):
        if md_path.name == "index.md" or md_path == FULL_PAGE:
            continue  # section landing pages and this list itself aren't "content"
        if is_auto_generated_stub(md_path):
            continue
        fm = parse_frontmatter(md_path)
        if not fm or fm.get("draft") == "true":
            continue
        dates = git_dates(md_path)
        if dates is None:
            continue
        first, last = dates
        pages.append({
            "title": fm.get("title", md_path.stem),
            "description": fm.get("description", ""),
            "path": md_path,
            "last": last,
            "is_new": (last - first).days <= NEW_WINDOW_DAYS,
        })
    pages.sort(key=lambda p: p["last"], reverse=True)
    return pages


def link_from(page: dict, from_dir: Path) -> str:
    rel = os.path.relpath(page["path"], from_dir)
    return rel.replace("\\", "/")


def badge(page: dict) -> str:
    label = "New" if page["is_new"] else "Updated"
    icon = ":material-new-box:" if page["is_new"] else ":material-update:"
    return f"{icon} {label} {page['last'].isoformat()}"


def render_full_section(pages: list[dict]) -> str:
    from_dir = FULL_PAGE.parent
    cards = []
    for page in pages[:FULL_COUNT]:
        lines = [f"-   __{page['title']}__", "", "    ---", ""]
        if page["description"]:
            lines.append(f"    {page['description']}")
            lines.append("")
        lines.append(f"    {badge(page)} · [:octicons-arrow-right-24: Read]({link_from(page, from_dir)})")
        cards.append("\n".join(lines))
    if not cards:
        return f"{FULL_START}\n*Nothing published yet.*\n{FULL_END}"
    return f"{FULL_START}\n<div class=\"grid cards\" markdown>\n\n" + "\n\n".join(cards) + f"\n\n</div>\n{FULL_END}"


def render_teaser_section(pages: list[dict]) -> str:
    from_dir = HOME_PAGE.parent
    items = []
    for page in pages[:TEASER_COUNT]:
        items.append(f"- **[{page['title']}]({link_from(page, from_dir)})** — {badge(page)}")
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


def main() -> None:
    pages = collect_pages()
    changed = []
    if replace_section(FULL_PAGE, FULL_START, FULL_END, render_full_section(pages)):
        changed.append(str(FULL_PAGE.relative_to(REPO_ROOT)))
    if replace_section(HOME_PAGE, TEASER_START, TEASER_END, render_teaser_section(pages)):
        changed.append(str(HOME_PAGE.relative_to(REPO_ROOT)))
    if changed:
        print(f"Updated: {', '.join(changed)}")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
