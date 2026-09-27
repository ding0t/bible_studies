"""Write the site-derived half of the verse pop-up's data: which studies treat a passage.

The Bible text, cross-references and lexicon are exported from bible-text.db by
references/build/export_popups.py and committed, because CI cannot rebuild that database. This
half needs no database -- it is read from each page's own frontmatter and text -- so it is built here on
every deploy and can never go stale. Listed after draft_pages.py, it only sees the pages that
hook kept, so a draft never appears in a published pop-up.

Output: assets/popups/studies.json in the built site.
  studies     [{t: title, u: url, p: [primary_passage refs], r: [bible_references]}]
  words       {"G126": [index into studies, ...]} -- the studies that tag a word with its Strong's
              number, so a word's pop-up can send the reader to where it is discussed
  commentary  {book number: {chapter: url}} for the generated commentary chapter pages
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
_COMMENTARY = re.compile(r"^commentaries/(\d{2})-[^/]+/chapter-(\d{3})\.md$")
# The same tag the page script finds (app/src/utils/scriptureRefs.js findStrongs), inside the
# lexicons' range: H1-8674, G1-5624.
_STRONGS = re.compile(r"(?<![\w-])([HG])0*(\d{1,4})[a-z]?(?![\w-])")
_STRONGS_MAX = {"H": 8674, "G": 5624}

_studies: list[dict] = []
_words: dict[str, list[int]] = {}
_commentary: dict[str, dict[str, str]] = {}


def _refs(value) -> list[str]:
    if not value:
        return []
    items = value if isinstance(value, list) else [value]
    # primary_passage is often "Ruth 3:9-13; Ruth 4:1-17" in one string.
    return [part.strip() for item in items for part in str(item).split(";") if part.strip()]


def on_files(files, config):  # noqa: ARG001 - `config` is part of the signature
    _studies.clear()
    _words.clear()
    _commentary.clear()
    for f in files:
        if not f.is_documentation_page():
            continue
        if m := _COMMENTARY.match(f.src_uri):
            _commentary.setdefault(str(int(m[1])), {})[str(int(m[2]))] = f.url
            continue
        try:
            text = Path(f.abs_src_path).read_text(encoding="utf-8")
            meta = yaml.safe_load(_FRONTMATTER.match(text).group(1))
        except (AttributeError, OSError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if not isinstance(meta, dict):
            continue
        primary, references = _refs(meta.get("primary_passage")), _refs(meta.get("bible_references"))
        words = sorted({f"{m[1]}{int(m[2])}" for m in _STRONGS.finditer(text)
                        if 0 < int(m[2]) <= _STRONGS_MAX[m[1]]})
        if primary or references or words:
            for word in words:
                _words.setdefault(word, []).append(len(_studies))
            _studies.append({"t": meta.get("title") or f.name, "u": f.url, "p": primary, "r": references})
    return files


def on_post_build(config):
    out = Path(config["site_dir"]) / "assets" / "popups" / "studies.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"studies": _studies, "words": _words, "commentary": _commentary}
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
