#!/usr/bin/env python3
"""Check the agent skills in .claude/skills/ against the repo they describe.

Why this exists: a skill is instructions for an agent that will follow them literally, and nothing
fails when one goes stale. A review on 2026-10-31 found the placement table still calling
`salvation/` and `biblical-figures/` "not yet created" weeks after both had studies, a check for
"Astro-served tools" a month after Astro was removed, and read-bible-study's rule list numbered one
off from the page it summarised. Every one of those was a fact about the repo that the repo could
have checked.

Errors (exit non-zero):

1. **Frontmatter.** `name` matches its directory and is lowercase-hyphenated, at most 64
   characters; `description` is present and at most 1,024 (Anthropic's published skill limits).
2. **Broken link.** A relative markdown link whose file or `#anchor` does not exist.
3. **Unknown MCP tool.** A backticked name shaped like a bible-references tool (`bible_*`,
   `twot_*`, ...) that `references/build/mcp_server.py` does not register. A renamed tool otherwise
   leaves every skill naming it pointing at nothing.
4. **Missing path.** A backticked repo path with a directory in it (`hooks/youth.py`,
   `docs/content/wisdom/`) that is not on disk. Paths with placeholders (`<slug>`, `*`) are skipped.

Warning: a SKILL.md over WORD_BUDGET words. SKILL.md is loaded whole every time the skill runs;
detail belongs in a companion file it links to. See .claude/skills/README.md.

Run from the repo root:  python3 utils/check_skills.py
"""

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"
MCP_SERVER = ROOT / "references" / "build" / "mcp_server.py"

WORD_BUDGET = 5000

TOOL_SHAPE = re.compile(
    r"^(bible|twot|study|passage|research_batch|review|read|evidence|source)_[a-z_]+$"
)

# Backticked names that match TOOL_SHAPE but are not tool names. The value is the reason, so an
# exemption can be told apart from an oversight (AGENTS.md, "An exemption in a checking tool...").
NOT_TOOLS = {
    "study_note": "a note_type value in study-notes.db (also a tool, but used as the value)",
    "bible_references": "a frontmatter field",
    "study_path": "read_structure's parameter name",
    "source_profile": "registered; listed so a rename is noticed here too",
}

# Backticked paths that are legitimately absent from a checkout. Value is the reason.
ABSENT_PATHS = {
    "docs/content/assets/js/": "esbuild output of `npm run build:tools`, gitignored",
    "docs/content/assets/lang/": "export_connector.py output, gitignored (130 MB)",
    "app/dist/worker.js": "npm run build:worker output, gitignored",
    "out/bible-text.db": "build.py output, gitignored",
    "references/build/out/bible-text.db": "build.py output, gitignored",
    "references/open-data/macula-greek/SBLGNT/tsv/macula-greek-SBLGNT.tsv": (
        "open-data submodule content; deploy.yml checks out without submodules"
    ),
    "references/open-data/macula-hebrew/WLC/tsv/macula-hebrew.tsv": (
        "open-data submodule content; deploy.yml checks out without submodules"
    ),
    "studies/": "named as the wrapper directory the taxonomy does not have",
    "bible/": "named as the wrapper directory the taxonomy does not have",
}

# Skills write paths relative to whichever of these the reader is working in.
PATH_BASES = [
    ROOT,
    ROOT / "references" / "build",
    ROOT / "docs" / "content",
    ROOT / "docs" / "content" / "assets" / "img",
    SKILLS,
]

# Tags look like paths (`method/word-study`, `person/peter`) and are checked by the validator.
TAG_FACETS = {"method", "lang", "status", "audience", "person", "provider", "anthropic"}

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
CODE = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.M)


def registered_tools() -> set[str]:
    return set(re.findall(r"@mcp\.tool\(\)\s*\ndef (\w+)", MCP_SERVER.read_text(encoding="utf-8")))


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    block = text[4 : text.index("\n---", 4)]
    return dict(re.findall(r"^(\w+):\s*(.*)$", block, re.M))


def slugs(heading: str) -> set[str]:
    """Anchor ids a heading may get: Python-Markdown's toc slugify (mkdocs) and GitHub's."""
    plain = re.sub(r"[*`_]|\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    ascii_ = unicodedata.normalize("NFKD", plain).encode("ascii", "ignore").decode()
    mkdocs = re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", ascii_).strip().lower())
    github = re.sub(r"[^\w\- ]", "", plain.lower()).replace(" ", "-")
    return {mkdocs, github}


def anchors(path: Path) -> set[str]:
    text = FENCE.sub("", path.read_text(encoding="utf-8"))
    found = set()
    for h in HEADING.findall(text):
        found |= slugs(h)
    return found


def path_exists(token: str) -> bool:
    for base in PATH_BASES:
        candidate = base / token
        if candidate.exists():
            return True
        # A graphic named by its stem: `tribulation/sea-to-blood` is sea-to-blood.svg.
        if not candidate.suffix and candidate.parent.is_dir():
            if any(candidate.parent.glob(candidate.name + ".*")):
                return True
    return False


def looks_like_path(token: str) -> bool:
    if token.split("/")[0] in TAG_FACETS:
        return False
    if "/" not in token or " " in token or token.startswith(("/", "http", "$", "~", "-", ".")):
        return False
    if re.search(r"[<>*{}|=\[\]()]", token) or ".." in token:
        return False
    return bool(re.match(r"^[\w.-]+(/[\w.-]+)*/?$", token))


def check_file(md: Path, tools: set[str], errors: list[str]) -> None:
    text = md.read_text(encoding="utf-8")
    rel = md.relative_to(ROOT)
    prose = FENCE.sub("", text)
    # Links inside inline code or a quoted specimen are examples, not links.
    linkable = "\n".join(
        CODE.sub("", line) for line in prose.splitlines() if not line.lstrip().startswith(">")
    )

    for target in LINK.findall(linkable):
        if re.match(r"^[a-z]+:", target):
            continue
        file_part, _, anchor = target.partition("#")
        dest = (md.parent / file_part).resolve() if file_part else md
        if not dest.exists():
            errors.append(f"{rel}: broken link {target}")
        elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
            errors.append(f"{rel}: no heading for #{anchor} in {dest.relative_to(ROOT)}")

    for token in CODE.findall(prose):
        name = token.split("(")[0].strip()
        if TOOL_SHAPE.match(name) and name not in tools and name not in NOT_TOOLS:
            if not (ROOT / "references" / "build" / f"{name}.py").exists():
                errors.append(f"{rel}: `{name}` looks like an MCP tool but mcp_server.py has none")
        if looks_like_path(token) and token not in ABSENT_PATHS:
            if not path_exists(token):
                errors.append(f"{rel}: path `{token}` does not exist")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    tools = registered_tools()

    for skill in sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()):
        skill_md = skill / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        fm = frontmatter(text)
        rel = skill_md.relative_to(ROOT)
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != skill.name:
            errors.append(f"{rel}: name '{name}' does not match directory '{skill.name}'")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            errors.append(f"{rel}: name must be lowercase letters, digits and hyphens, <= 64 chars")
        if not desc:
            errors.append(f"{rel}: description missing")
        elif len(desc) > 1024:
            errors.append(f"{rel}: description is {len(desc)} chars (limit 1024)")

        words = len(text.split())
        if words > WORD_BUDGET:
            warnings.append(f"{rel}: {words} words (budget {WORD_BUDGET}); move detail to a companion file")

    for md in sorted(SKILLS.rglob("*.md")):
        check_file(md, tools, errors)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
