"""Put a strip of the drawn plates, and one of the one-minute comics, on each section's landing page.

Every published study under a top-level section is scanned for the SVGs it embeds from
assets/img/, and the section's `index.md` gets a scrolling row of thumbnails, each opening the
study the plate belongs to. Found at build time, so a plate added to a study reaches its section
page without anyone editing the landing page, and section_index.py's generated card list below it
is left alone: the strip goes in just above its auto-start marker, with a heading for each.

Comics (assets/img/comics/, utils/build_comics.py) get their own strip, "Comics in these studies",
above the plates: a comic tells a study's point as a story and is the quickest way into it, where a
plate explains one part of it. A section with only one kind shows only that strip.

A plate embedded by several studies is credited to the first in path order. Drafts are skipped
here as well as by draft_pages.py, which keeps them under `mkdocs serve`, so the local strip
matches the live one. The styles are .plate-strip in assets/stylesheets/home.css.
"""

from __future__ import annotations

import logging
import posixpath
import re
from html import unescape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.section_plates")

_SVG_REF = re.compile(r"\]\(([^)\s]+?\.svg)\)")
_SVG_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.DOTALL)
_PAGE_TITLE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.MULTILINE)
_DRAFT = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)
_SKIP = {"assets/img/favicon.svg"}
_COMICS = "assets/img/comics/"

# section -> [(svg path from docs_dir, plate title, page src_uri, page title)]
_plates: dict[str, list[tuple[str, str, str, str]]] = {}


def on_files(files, config):
    _plates.clear()
    docs_dir = Path(config.docs_dir)
    seen: set[tuple[str, str]] = set()
    for file in sorted(files.documentation_pages(), key=lambda f: f.src_uri):
        section, _, rest = file.src_uri.partition("/")
        if not rest or rest == "index.md" or section == "commentaries":
            continue
        source = Path(file.abs_src_path).read_text(encoding="utf-8")
        if _DRAFT.search(source):
            continue
        page_title = (_PAGE_TITLE.search(source) or [None, file.src_uri])[1]
        for ref in _SVG_REF.findall(source):
            svg = posixpath.normpath(posixpath.join(posixpath.dirname(file.src_uri), ref))
            if svg in _SKIP or (section, svg) in seen or not (docs_dir / svg).exists():
                continue
            seen.add((section, svg))
            head = (docs_dir / svg).read_text(encoding="utf-8")[:4000]
            match = _SVG_TITLE.search(head)
            plate_title = unescape(match[1]).strip() if match else page_title
            _plates.setdefault(section, []).append((svg, plate_title, file.src_uri, page_title))
    return files


def on_page_markdown(markdown, page, config, files):  # noqa: ARG001 - hook signature
    section, _, rest = page.file.src_uri.partition("/")
    plates = _plates.get(section)
    if rest != "index.md" or not plates:
        return markdown

    here = posixpath.dirname(page.file.src_uri)

    def gallery(heading, entries, extra_class=""):
        if not entries:
            return ""
        items = []
        for svg, plate_title, src_uri, page_title in entries:
            image = posixpath.relpath(svg, here)
            link = posixpath.relpath(src_uri, here)
            alt = plate_title.replace("[", "(").replace("]", ")")
            items.append(
                f"-   [![{alt}]({image})]({link})\n\n"
                f"    __{plate_title}__ · {page_title}\n"
            )
        return (
            f"## {heading}\n\n"
            f'<div class="grid cards plate-gallery plate-strip{extra_class}" markdown>\n\n'
            + "\n".join(items)
            + "\n</div>\n\n"
        )

    comics = [entry for entry in plates if entry[0].startswith(_COMICS)]
    drawn = [entry for entry in plates if not entry[0].startswith(_COMICS)]
    strip = gallery("Comics in these studies", comics, " comic-strip") + gallery("Drawn in these studies", drawn)
    marker = markdown.find("<!-- section-index:auto-start -->")
    if marker == -1:
        return markdown
    # A landing page that already heads its list ("## In this section") keeps that heading.
    before = markdown[:marker].rstrip()
    heading_at = before.rfind("\n") + 1
    if before[heading_at:].startswith("## "):
        return markdown[:heading_at] + strip + markdown[heading_at:]
    return markdown[:marker] + strip + "## The studies\n\n" + markdown[marker:]
