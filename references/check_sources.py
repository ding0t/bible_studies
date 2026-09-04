#!/usr/bin/env python3
"""Check that every reference source actually on disk is documented in references/README.md.

Why this exists: the catalog in references/README.md is the thing the develop- and
review-bible-study skills are told to consult before concluding a source is unavailable. When the
catalog falls behind reality, that instruction produces a confident wrong answer. It has:
`scrollmapper-bible-databases-deuterocanonical` was added as a submodule and never documented, so a
study went to press saying Tobit "is not in this repo's databases" while Tobit sat in
references/open-data/. `hebrew-vocab-tools` had drifted the same way -- ingested into bible-text.db
and cited by word-study-method.md, absent from the catalog.

Three checks, deliberately different in severity:

1. **Undocumented source (error).** A directory under references/open-data/ or
   references/restricted-data/ that references/README.md never mentions. Exits non-zero.

2. **Present but not queryable (warning).** A source set on disk that build.py does not ingest --
   so `query.py`, the MCP tools and every habit built on them will not see it, and it has to be
   read as raw files. This is the Tobit shape exactly. Not an error (build.py skips deuterocanonical
   books on purpose), but it is the thing worth knowing before you conclude a text is unavailable.

3. **Undocumented patristic text (error).** A file under the media volume's `reference/patristics/`
   that any of the three places describing that corpus fails to mention. They drift because they
   serve different readers -- `references/README.md` tells an agent what may be quoted,
   `PROVENANCE.md` on the volume records where each text came from and what was verified inside it,
   and `docs/content/resources/patristic-sources.md` tells a reader which sources back the site's
   claims. All three were correct on 2026-09-04 only because they were written in one pass. The
   reader-facing one is the likeliest to go stale, and did: it still promised that every patristic
   claim had been checked against one of three sources, months after seven more were added and one
   claim checked against a translation had been retracted.

   Skipped, not failed, when the volume is unmounted -- that is routine, and CI never has it.

   Known limit, found by testing it: the reader-page match is by author, so adding a *second* text
   by an author already named there passes. That is the deliberate trade -- matching the reader page
   on filenames would demand it list filenames, which would make it worse writing -- but it means
   this check catches a new voice appearing in the corpus, not a new volume of an existing one.

Run from the repo root:

    python3 references/check_sources.py            # human-readable
    python3 references/check_sources.py --quiet    # only problems

Name matching is deliberately loose -- a directory named `mounce-dictionary` counts as documented
if the README says "Mounce dictionary". Strict matching produced false positives, and a check that
cries wolf gets ignored, which is how the catalog drifted in the first place.
"""

from __future__ import annotations

import argparse
import os
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

# The patristics corpus lives off-repo; see references/build/media_root.py for why the location is
# an environment variable rather than a committed path.
MEDIA_ROOT = Path(os.environ.get("BIBLE_MEDIA_ROOT", "/Volumes/media/bible"))
PATRISTICS_DIR = MEDIA_ROOT / "reference" / "patristics"
# Each entry: the doc, and whether it names texts by filename or by author.
PATRISTICS_DOCS = [
    (README, "file"),
    (PATRISTICS_DIR / "PROVENANCE.md", "file"),
    (REPO_ROOT / "docs" / "content" / "resources" / "patristic-sources.md", "author"),
]


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

    Both source trees count. The check originally looked only for OPEN_DATA, which was true when
    it was written and stopped being true the moment a restricted-nc source was ingested -- the
    Dead Sea Scrolls then reported as raw-only while being fully queryable.
    """
    if not BUILD_PY.is_file():
        return set()
    source = BUILD_PY.read_text(encoding="utf-8")
    return set(re.findall(r'(?:OPEN_DATA|RESTRICTED_DATA) / "([a-z0-9-]+)"', source))


def patristics_drift() -> tuple[list[str], list[str]]:
    """Every text in the patristics corpus, against the three docs that describe it.

    Matched two ways because the docs are written for different readers. The two technical ones name
    files, so a filename stem matches directly. The reader-facing page names editions and editors --
    "Kroymann", "CSEL 47" -- and would be worse writing if it listed filenames, so it is matched on
    the author key instead: the first segment of the filename. That also collapses the two Eusebius
    volumes onto one mention, which is what the page should have.

    Returns (problems, checked). An unmounted volume returns ([], []) -- routine, not a failure.
    """
    if not PATRISTICS_DIR.is_dir():
        return [], []

    docs = []
    for path, match_by in PATRISTICS_DOCS:
        if not path.is_file():
            return [f"{path} is missing -- cannot check the patristics corpus against it"], []
        docs.append((path, match_by, documented_names(path.read_text(encoding="utf-8"))))

    problems, checked = [], []
    for child in sorted(PATRISTICS_DIR.iterdir()):
        if child.name.startswith(".") or child.name == "PROVENANCE.md":
            continue
        stem = child.name.removesuffix(".txt")
        author = re.split(r"[-_]", stem)[0]
        checked.append(child.name)
        for path, match_by, haystack in docs:
            needle = author if match_by == "author" else stem
            if not is_documented(needle, haystack):
                rel = path.name if path.parent == PATRISTICS_DIR else path.relative_to(REPO_ROOT)
                problems.append(f"{child.name} is not named in {rel} (looked for '{needle}')")
    return problems, checked


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

    patristics_problems, patristics_checked = patristics_drift()
    for problem in patristics_problems:
        print(f"  UNDOCUMENTED {problem}", file=sys.stderr)
    if patristics_problems:
        print("               the three docs describing the patristics corpus have drifted apart.",
              file=sys.stderr)
        print("               references/README.md is what an agent reads, PROVENANCE.md records",
              file=sys.stderr)
        print("               where a text came from, and resources/patristic-sources.md is what a",
              file=sys.stderr)
        print("               reader sees. A text missing from any of them is invisible to someone.",
              file=sys.stderr)

    if not args.quiet:
        if patristics_checked:
            print(f"  ok           {len(patristics_checked)} patristic texts, documented in all three places")
        elif not PATRISTICS_DIR.is_dir():
            print(f"  skipped      patristics corpus -- {PATRISTICS_DIR} not mounted")
        print(f"\n{len(ok)} documented and queryable, {len(not_queryable)} raw-only, "
              f"{len(undocumented) + len(patristics_problems)} undocumented.")

    return 1 if undocumented or patristics_problems else 0


if __name__ == "__main__":
    sys.exit(main())
