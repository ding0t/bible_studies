#!/usr/bin/env python3
"""Check that every reference source actually on disk is documented in references/README.md.

Why this exists: the catalog in references/README.md is the thing the develop- and
review-bible-study skills are told to consult before concluding a source is unavailable. When the
catalog falls behind reality, that instruction produces a confident wrong answer. It has:
`scrollmapper-bible-databases-deuterocanonical` was added as a submodule and never documented, so a
study went to press saying Tobit "is not in this repo's databases" while Tobit sat in
references/open-data/. `hebrew-vocab-tools` had drifted the same way -- ingested into bible-text.db
and cited by word-study-method.md, absent from the catalog.

Two checks, deliberately different in severity:

1. **Undocumented source (error).** A directory under references/open-data/ or
   references/restricted-data/ that references/README.md never mentions. Exits non-zero.

2. **Present but not queryable (warning).** A source set on disk that build.py does not ingest --
   so `query.py`, the MCP tools and every habit built on them will not see it, and it has to be
   read as raw files. This is the Tobit shape exactly. Not an error (build.py skips deuterocanonical
   books on purpose), but it is the thing worth knowing before you conclude a text is unavailable.

Run from the repo root:

    python3 references/check_sources.py            # human-readable
    python3 references/check_sources.py --quiet    # only problems

Name matching is deliberately loose -- a directory named `mounce-dictionary` counts as documented
if the README says "Mounce dictionary". Strict matching produced false positives, and a check that
cries wolf gets ignored, which is how the catalog drifted in the first place.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "references" / "README.md"
SOURCE_DIRS = [
    REPO_ROOT / "references" / "open-data",
    REPO_ROOT / "references" / "restricted-data",
]
BUILD_PY = REPO_ROOT / "references" / "build" / "build.py"


def documented_names(readme_text: str) -> str:
    """Lowercased README with punctuation flattened, so 'mounce-dictionary' matches 'Mounce dictionary'."""
    return re.sub(r"[^a-z0-9]+", " ", readme_text.lower())


def is_documented(dir_name: str, haystack: str) -> bool:
    flattened = re.sub(r"[^a-z0-9]+", " ", dir_name.lower()).strip()
    return flattened in haystack


def ingested_dirs() -> set[str]:
    """Source directories build.py actually reads, taken from build.py itself.

    Read from the build script rather than matched against work ids in bible-text.db: directory
    names and work ids do not correspond (the `scrollmapper-bible-databases` submodule produces
    `scrollmapper-ASV`, `scrollmapper-YLT` and forty more), so name-matching produced ten false
    positives out of twelve. Parsing the one place that states the relationship means adding an
    ingest to build.py updates this check for free.
    """
    if not BUILD_PY.is_file():
        return set()
    return set(re.findall(r'OPEN_DATA / "([a-z0-9-]+)"', BUILD_PY.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true", help="print only problems")
    args = parser.parse_args()

    if not README.is_file():
        print(f"ERROR: {README} not found", file=sys.stderr)
        return 2

    haystack = documented_names(README.read_text(encoding="utf-8"))
    ingested = ingested_dirs()

    undocumented: list[str] = []
    not_queryable: list[str] = []
    ok: list[str] = []

    for source_dir in SOURCE_DIRS:
        if not source_dir.is_dir():
            continue
        for child in sorted(source_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            rel = child.relative_to(REPO_ROOT)
            if not is_documented(child.name, haystack):
                undocumented.append(str(rel))
            elif child.name not in ingested:
                not_queryable.append(str(rel))
            else:
                ok.append(str(rel))

    if not args.quiet:
        for rel in ok:
            print(f"  ok           {rel}")

    for rel in not_queryable:
        print(f"  raw-only     {rel}")
        print("               documented, but build.py does not ingest it -- query.py and the MCP")
        print("               tools cannot see it. Read it as raw files under its sources/ tree.")

    for rel in undocumented:
        print(f"  UNDOCUMENTED {rel}", file=sys.stderr)
        print("               add a row to references/README.md's quick-guide table naming its", file=sys.stderr)
        print("               licence tier and how much of it may be quoted.", file=sys.stderr)

    if not ingested and not args.quiet:
        print("\n  note: could not read any ingests from build.py -- raw-only results are unreliable.")

    if not args.quiet:
        print(f"\n{len(ok)} documented and queryable, {len(not_queryable)} raw-only, {len(undocumented)} undocumented.")

    return 1 if undocumented else 0


if __name__ == "__main__":
    sys.exit(main())
