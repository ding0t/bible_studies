"""Youth pages: a study cut down for young readers (8-16), from docs/data/youth/<slug>.toml.

A page under youth/ carries `<!-- youth: <slug> -->` and the hook writes the rest in a fixed shape:
who it is for and a link to the full study (the leader's notes), the big idea, the young readers'
comic, the passage to read, then one tab per age band (story, questions, something to do), the
key word in the language the passage was written in, the memory verse and the prayer. The shape is fixed so a youth page cannot grow the
way a study does; a youth page says nothing its study does not.

Written as markdown at on_page_markdown, so the study link is checked by mkdocs, the tabs and
admonitions are ordinary pymdownx (the `youth` class sets their text at body size,
in series.css), and the verse and word pop-ups find every reference. The comic's
alt text comes from utils/lib/comic.py's describe(), the same text `build_comics.py --alt` prints.
"""

from __future__ import annotations

import logging
import posixpath
import re
import sys
import textwrap
import tomllib
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.youth")

_MARKER = re.compile(r"<!--\s*youth:\s*([\w-]+)\s*-->")
_ROOT = Path(__file__).resolve().parent.parent


def _comic_alt(slug: str) -> str:
    sys.path.insert(0, str(_ROOT / "utils"))
    from lib.comic import describe

    comic = tomllib.loads((_ROOT / "docs" / "data" / "comics" / f"{slug}.toml").read_text(encoding="utf-8"))
    return describe(comic).replace("[", "(").replace("]", ")")


def _comic(slug: str, here: str) -> str:
    """The comic, and its one-panel-per-row phone version when build_comics.py drew one; series.css
    shows whichever fits the screen."""
    alt = _comic_alt(slug)
    wide = posixpath.relpath(f"assets/img/comics/{slug}.svg", here)
    if not (_ROOT / "docs" / "content" / "assets" / "img" / "comics" / f"{slug}-phone.svg").exists():
        return f"[![{alt}]({wide})]({wide})\n"
    phone = posixpath.relpath(f"assets/img/comics/{slug}-phone.svg", here)
    return f"[![{alt}]({wide})]({wide}){{ .comic-wide }}\n[![{alt}]({phone})]({phone}){{ .comic-phone }}\n"


def _indent(text: str) -> str:
    return textwrap.indent(text.strip(), "    ")


def _band(band: dict) -> str:
    questions = "\n".join(f"{n}. {q}" for n, q in enumerate(band["questions"], 1))
    body = f"{band['story'].strip()}\n\n**Talk about it**\n\n{questions}\n\n**Try this week**\n\n{band['activity']}"
    return f'=== "Ages {band["ages"]}"\n\n{_indent(body)}\n'


def _render(slug: str, src: str) -> str:
    data = tomllib.loads((_ROOT / "docs" / "data" / "youth" / f"{slug}.toml").read_text(encoding="utf-8"))
    here = posixpath.dirname(src)
    study = posixpath.relpath(data["study"], here)
    word, verse = data["key_word"], data["memory_verse"]
    return "\n".join([
        f"For young readers, ages {data['ages']}. "
        f"Leading a group? [The full study]({study}) is your notes.\n{{ .youth-for }}\n",
        f'!!! abstract youth "The big idea"\n\n{_indent(data["big_idea"])}\n',
        _comic(data["comic"], here),
        f"**Read it together:** {data['read']}\n",
        "\n".join(_band(b) for b in data["band"]),
        f'!!! question youth "Key word in {word["language"]}: {word["word"]}"\n\n'
        + _indent(f"{word['written']} **{word['word']}**, *{word['translit']}* ({word['strongs']}), said *{word['say']}*. It means "
                  f"{word['means']}. {word['note']}") + "\n",
        f'!!! quote youth "Memory verse"\n\n'
        + _indent(f"{verse['text']}\n\n{verse['ref']} ({verse['translation']})") + "\n",
        f"## Pray\n\n{data['prayer'].strip()}\n",
    ])


def on_page_markdown(markdown, page, config, files):  # noqa: ARG001 - hook signature
    return _MARKER.sub(lambda m: _render(m[1], page.file.src_uri), markdown)
