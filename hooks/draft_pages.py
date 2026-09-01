"""Keep `draft: true` pages out of the built site.

`draft: true` has been this repo's marker for unfinished content since the site went public, and
`section_index.py`, `commentary_index.py` and `generate_recent_updates.py` all honour it -- so a
draft stays off the section landing pages, off Recently Updated and off the homepage teaser.

MkDocs itself never honoured it. There is no built-in notion of a draft page outside
mkdocs-material's blog plugin, which this site does not use, so `draft: true` was simply an
unrecognised frontmatter key: the page was built, published at its real URL, linked from its
section's sidebar nav, and indexed in site search. Because every *curated* list correctly hid
them, they looked unpublished while being fully reachable. Three were live on the-way.lewy.au
that way (olivet-discourse and olivet-discourse-parables from 2026-08-29, woman-at-well from
2026-08-07) before anyone noticed.

This hook closes the gap at `on_files`, the one event where the whole file set is visible at once.

`mkdocs serve` keeps drafts so local preview still works; `mkdocs build` -- and therefore the
deploy workflow -- drops them. That asymmetry is the point: you want to read what you are writing
without publishing it.

Two consequences worth knowing before adding a `draft: true` page:

- A published page that markdown-links a draft will fail `mkdocs build --strict` with a broken
  link, because the target is no longer in the build. That is the correct outcome -- a public page
  should not link to something the public cannot read -- but it turns a silent leak into a loud
  build failure, so expect it.
- A draft `index.md` takes its directory's landing page with it. If the directory still has
  published children they remain reachable by URL and nav, so prefer finishing a section's index
  over leaving it drafted.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml
from mkdocs.structure.files import Files

log = logging.getLogger("mkdocs.hooks.draft_pages")

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)

# Set by on_startup. Defaults to "build" so that anything invoking the config without the
# normal lifecycle errs toward excluding drafts rather than publishing them.
_command = "build"


def on_startup(command, dirty):  # noqa: ARG001 - `dirty` is part of the hook signature
    global _command
    _command = command


def _is_draft(abs_src_path: str | None) -> bool:
    if not abs_src_path:
        return False
    try:
        text = Path(abs_src_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    match = _FRONTMATTER.match(text)
    if not match:
        return False
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return False
    if not isinstance(frontmatter, dict):
        return False
    value = frontmatter.get("draft")
    # section_index.py tests `is True` (it parses with yaml, so it gets a bool);
    # generate_recent_updates.py tests `== "true"` (its hand-rolled parser yields strings).
    # Accept both rather than introducing a third convention that disagrees with either.
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


def on_files(files: Files, config) -> Files:  # noqa: ARG001 - `config` is part of the signature
    if _command == "serve":
        return files

    kept = []
    dropped = []
    for f in files:
        if f.is_documentation_page() and _is_draft(f.abs_src_path):
            dropped.append(f.src_uri)
        else:
            kept.append(f)

    for src_uri in sorted(dropped):
        log.info("draft_pages: excluding %s", src_uri)
    if dropped:
        log.info("draft_pages: excluded %d draft page(s) from the build", len(dropped))

    return Files(kept)
