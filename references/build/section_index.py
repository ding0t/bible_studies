"""Generates a card-grid index.md landing page for every docs/content/ directory that has
children (pages or subdirectories) but no index.md of its own -- fixes mkdocs-awesome-pages
falling through to the first alphabetical leaf page when a nav section has no landing page.

Draft (draft: true) pages are excluded automatically -- the site is public now, so an
auto-generated "browse this section" page should never surface unfinished work.

Same delimited auto-section pattern as commentary_index.py: only the content between
SECTION_START/SECTION_END is regenerated, so hand-written intro prose on a generated page
survives re-runs. A directory that already has an index.md (hand-written, or previously
generated) is left alone -- this only ever creates the file that's missing, never edits an
existing one. Re-run it after adding a new study/section.

Usage: uv run python section_index.py
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "docs" / "content"

SECTION_START = "<!-- section-index:auto-start -->"
SECTION_END = "<!-- section-index:auto-end -->"

# Short blurbs for known sections, keyed by path relative to docs/content/. Edit freely --
# this is the one hand-maintained piece; everything else below is derived from frontmatter.
SECTION_BLURBS = {
    "studies": "In-depth studies developed through the exegesis-then-hermeneutics process.",
    "studies/archeology": "Archaeological findings and ancient manuscript evidence bearing on Scripture.",
    "studies/feasts": "The biblical feasts, their Old Testament instruction, and New Testament fulfillment.",
    "studies/prophecy": "End-times and biblical prophecy, read dispensationally.",
    "studies/prophecy-fulfilled-in-jesus": "Old Testament prophecies and how the Gospels record their fulfillment in Jesus.",
    "studies/sins": "Sin, temptation, and the pattern of redemption in Scripture.",
    "studies/spiritual-disciplines": "Prayer, fasting, and other practices of the Christian life.",
    "studies/teaching-resources": "Notes and tools for teaching and preparing to teach.",
    "studies/theology": "Broader theological topics not tied to a single feast, prophecy, or discipline.",
    "bible": "Commentary and reference material on the biblical text itself.",
    "bible/commentaries": "Verse-by-verse commentary, organized by book, with auto-linked studies (see commentary_index.py).",
    "sermons": "Sermon notes and presentation material.",
    "dreams-visions": "Dreams, visions, and spiritual warfare from a biblical perspective.",
    "hebrew-studies": "Learning biblical Hebrew -- alphabet, resources, and study aids.",
    "investigation": "Investigative studies into specific practices and questions.",
    "investigation/deliverance": "The biblical basis for and practice of deliverance ministry.",
    "resources": "External sources, tools, and datasets this project draws on.",
    "about": "About this project and its statement of faith.",
}


def load_frontmatter(md_path: Path) -> dict | None:
    content = md_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def render_page_card(fm: dict, link: str) -> str:
    title = fm.get("title", link)
    description = (fm.get("description") or "").strip()
    lines = [f"-   __{title}__", "", "    ---", ""]
    if description:
        lines.append(f"    {description}")
        lines.append("")
    lines.append(f"    [:octicons-arrow-right-24: Read]({link})")
    return "\n".join(lines)


def render_section_card(title: str, blurb: str, link: str) -> str:
    lines = [f"-   __{title}__", "", "    ---", ""]
    if blurb:
        lines.append(f"    {blurb}")
        lines.append("")
    lines.append(f"    [:octicons-arrow-right-24: Browse]({link})")
    return "\n".join(lines)


def title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").title()


def build_index(dir_path: Path) -> str | None:
    rel = dir_path.relative_to(CONTENT_DIR)
    cards = []

    for child in sorted(dir_path.iterdir()):
        if child.name.startswith(".") or child.name == "index.md":
            continue
        if child.is_dir():
            child_index = child / "index.md"
            if not child_index.exists():
                continue  # not generated/authored yet -- nothing to link to
            child_rel = str((rel / child.name)).replace("\\", "/")
            blurb = SECTION_BLURBS.get(child_rel, "")
            cards.append(render_section_card(title_from_slug(child.name.split("-", 1)[-1] if child.name[:2].isdigit() else child.name), blurb, f"{child.name}/"))
        elif child.suffix == ".md":
            fm = load_frontmatter(child)
            if fm is None or fm.get("draft") is True:
                continue
            cards.append(render_page_card(fm, child.name))

    if not cards:
        return None
    return f"{SECTION_START}\n<div class=\"grid cards\" markdown>\n\n" + "\n\n".join(cards) + "\n\n</div>\n{SECTION_END}".replace("{SECTION_END}", SECTION_END)


def main() -> None:
    # Deepest directories first: a parent's generated index links to its children's index.md
    # files, so those must already exist by the time the parent is processed.
    all_dirs = sorted(
        (d for d in CONTENT_DIR.rglob("*") if d.is_dir()),
        key=lambda d: (-len(d.relative_to(CONTENT_DIR).parts), str(d)),
    )
    created, updated = [], []
    for dir_path in all_dirs:
        index_path = dir_path / "index.md"
        has_children = any(
            (c.suffix == ".md" or (c.is_dir() and (c / "index.md").exists()))
            for c in dir_path.iterdir() if not c.name.startswith(".") and c.name != "index.md"
        )
        if not has_children:
            continue
        auto_section = build_index(dir_path)
        if auto_section is None:
            continue

        if index_path.exists():
            content = index_path.read_text(encoding="utf-8")
            if SECTION_START not in content or SECTION_END not in content:
                continue  # hand-written index with no auto section -- leave it alone entirely
            new_content = content.split(SECTION_START)[0] + auto_section + content.split(SECTION_END)[1]
            if new_content != content:
                index_path.write_text(new_content, encoding="utf-8")
                updated.append(str(index_path.relative_to(REPO_ROOT)))
        else:
            rel = dir_path.relative_to(CONTENT_DIR)
            title = title_from_slug(dir_path.name.split("-", 1)[-1] if dir_path.name[:2].isdigit() else dir_path.name)
            blurb = SECTION_BLURBS.get(str(rel).replace("\\", "/"), "")
            frontmatter = (
                f"---\ntitle: \"{title}\"\ncategory: \"other\"\n"
                f"description: \"{blurb or f'Browse {title}'}\"\ndraft: false\n---\n\n"
                f"# {title}\n\n"
            )
            if blurb:
                frontmatter += f"{blurb}\n\n"
            index_path.write_text(frontmatter + auto_section + "\n", encoding="utf-8")
            created.append(str(index_path.relative_to(REPO_ROOT)))

    print(f"Created {len(created)}, updated {len(updated)} index page(s).")
    for c in created:
        print(f"  new:     {c}")
    for u in updated:
        print(f"  updated: {u}")


if __name__ == "__main__":
    main()
