"""Render printable memory verse cards wherever a page carries `<!-- memory-verses -->`.

`<!-- memory-verses -->` renders every verse in docs/data/memory-verses.json;
`<!-- memory-verses: foundations -->` renders one set. The JSON is written by
references/build/export_memory_verses.py from docs/data/memory-verses.toml.

Each deck is a run of A4 sheets of eight 95 x 67.5 mm cards, in two layouts the reader picks
between on the page (CSS only, no script):

- cards       one-sided. Each card carries everything: the original words with transliteration
              and gloss beneath each, then the English.
- flashcards  double-sided. Each sheet of fronts (reference, theme, a first-letter cue) is followed
              by its sheet of backs (everything else), columns swapped so that flipping on the long
              edge puts each back behind its front.

Sizes in the stylesheet are in sheet-relative units, so the on-screen sheet is an exact scale
model of the printed one. Empty places on the last sheet become blank ruled cards to write a
verse of your own on.
"""

from __future__ import annotations

import json
import logging
import re
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.memory_verses")

_MARKER = re.compile(r"<!--\s*memory-verses(?::\s*([\w-]+))?\s*-->")
_CARDS_PER_SHEET = 8
# Days after learning a verse to say it again -- widening gaps, the spacing that fixes a memory.
_REVIEW_DAYS = (1, 2, 4, 7, 14, 30)
_FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+Hebrew:wght@400;600"
          "&family=Noto+Serif:ital,wght@0,400;0,600;1,400&display=swap")
# Cut lines on the sheet, in mm: two columns and four rows of 95 x 67.5 mm, inside a 10 mm margin
# with 17 mm at the foot for the attribution line. Must match .mv-grid in memory-verses.css.
_CUTS_X = (10, 105, 200)
_CUTS_Y = (10, 77.5, 145, 212.5, 280)

_NOTICE = "ESV® © 2001 Crossway, used by permission · WEB public domain · TAHOT/TAGNT STEPBible.org CC BY"

_data: dict = {"verses": [], "sources": {}}


def _json_path(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data" / "memory-verses.json"


def on_serve(server, config, builder):  # noqa: ARG001 - hook signature
    # Outside docs_dir, so `mkdocs serve` would otherwise show stale cards after an export.
    server.watch(str(_json_path(config)))
    return server


def on_config(config):
    path = _json_path(config)
    _data.update({"verses": [], "sources": {}})
    try:
        _data.update(json.loads(path.read_text(encoding="utf-8")))
    except FileNotFoundError:
        log.info("memory_verses: %s not found -- run references/build/export_memory_verses.py", path.name)
    return config


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    count = 0

    def deck(match: re.Match) -> str:
        nonlocal count
        count += 1
        wanted = match[1]
        verses = [v for v in _data["verses"] if not wanted or v["set"] == wanted]
        if not verses:
            log.warning("memory_verses: %s asks for set %r, which has no verses", page.file.src_uri, wanted)
        return render_deck(verses, f"mv{count}")

    return _MARKER.sub(deck, html)


def first_letters(text: str) -> str:
    """'In the beginning, God created' -> 'I t b, G c': the cue to recite from."""
    return re.sub(r"([A-Za-z])[A-Za-z’'-]*", r"\1", text)


def render_deck(verses: list[dict], deck_id: str) -> str:
    sheets = [verses[i:i + _CARDS_PER_SHEET] for i in range(0, max(len(verses), 1), _CARDS_PER_SHEET)]
    cards = "".join(_sheet("", [_full(v, n) for n, v in _numbered(sheets, i)], i, len(sheets))
                    for i in range(len(sheets)))
    flash = "".join(
        _sheet("mv-front", [_front(v, n) for n, v in _numbered(sheets, i)], i, len(sheets), "fronts")
        + _sheet("mv-back", [_full(v, n) for n, v in _numbered(sheets, i)], i, len(sheets), "backs")
        for i in range(len(sheets)))
    return f"""
<link rel="stylesheet" href="{_FONTS}">
<div class="mv-deck" data-no-popups>
  <form class="mv-controls" aria-label="Card layout">
    <fieldset>
      <legend>Print as</legend>
      <label><input type="radio" name="{deck_id}-layout" value="cards" class="mv-opt-cards" checked> Cards <small>one-sided</small></label>
      <label><input type="radio" name="{deck_id}-layout" value="flash" class="mv-opt-flash"> Flashcards <small>double-sided, flip on long edge</small></label>
    </fieldset>
    <fieldset>
      <legend>Show</legend>
      <label><input type="checkbox" class="mv-opt-gloss" checked> Word glosses</label>
      <label><input type="checkbox" class="mv-opt-web" checked> WEB alongside ESV</label>
    </fieldset>
    <button type="button" class="md-button md-button--primary" onclick="window.print()">Print</button>
  </form>
  <div class="mv-cards">{cards}</div>
  <div class="mv-flash">{flash}</div>
</div>
"""


def _numbered(sheets: list[list[dict]], i: int):
    """(card number, verse or None) for every place on sheet i, padding with blanks."""
    start = i * _CARDS_PER_SHEET
    sheet = sheets[i] + [None] * (_CARDS_PER_SHEET - len(sheets[i]))
    return [(start + k + 1, v) for k, v in enumerate(sheet)]


def _sheet(kind: str, cards: list[str], index: int, total: int, side: str = "") -> str:
    ticks = "".join(f'<i class="mv-tick mv-tick-x" style="--at:{x}"></i>' for x in _CUTS_X)
    ticks += "".join(f'<i class="mv-tick mv-tick-y" style="--at:{y}"></i>' for y in _CUTS_Y)
    label = f"Sheet {index + 1} of {total}" + (f" · {side}" if side else "")
    return f"""<section class="mv-sheet {kind}" aria-label="{label}">
  {ticks}<span class="mv-scissors" aria-hidden="true">✂</span>
  <div class="mv-grid">{''.join(cards)}</div>
  <footer class="mv-sheet-foot"><span>{label}</span><span>{_NOTICE}</span></footer>
</section>"""


def _full(verse: dict | None, number: int) -> str:
    if verse is None:
        return _blank(number)
    hebrew = verse["language"] == "hebrew"
    words = "".join(
        f'<span class="mv-word"><span class="mv-orig">{escape(w["w"])}</span>'
        f'<span class="mv-translit">{_translit(w)}</span>'
        f'<span class="mv-gloss">{escape(w["g"])}</span></span>'
        for w in verse["words"])
    return f"""<article class="mv-card mv-full{_density(verse)}">
  <header class="mv-head"><b>{escape(verse["ref"])}</b><span>{escape(verse["theme"])}</span></header>
  <div class="mv-words" dir="{'rtl' if hebrew else 'ltr'}" lang="{'he' if hebrew else 'grc'}">{words}</div>
  {_english(verse["translations"])}
  <span class="mv-num">{number}</span>
</article>"""


def _front(verse: dict | None, number: int) -> str:
    if verse is None:
        return _blank(number)
    cue_source = verse["translations"].get("ESV") or verse["translations"]["WEB"]
    incipit = verse["words"][0]
    hebrew = verse["language"] == "hebrew"
    boxes = "".join(f"<span><i></i>{d}</span>" for d in _REVIEW_DAYS)
    return f"""<article class="mv-card mv-prompt">
  <span class="mv-theme">{escape(verse["theme"])}</span>
  <b class="mv-ref">{escape(verse["ref"])}</b>
  <span class="mv-incipit" lang="{'he' if hebrew else 'grc'}">{escape(incipit["w"])}
    <small>{_translit(incipit)} …</small></span>
  <p class="mv-cue">{escape(first_letters(cue_source))}</p>
  <div class="mv-review" title="Tick a box each time you recite it: days after learning">{boxes}<em>days</em></div>
  <span class="mv-num">{number}</span>
</article>"""


def _blank(number: int) -> str:
    return f"""<article class="mv-card mv-blank">
  <header class="mv-head"><b>Reference</b><span>Theme</span></header>
  <div class="mv-lines"></div>
  <span class="mv-num">{number}</span>
</article>"""


def _translit(word: dict) -> str:
    return "·".join(f"<b>{escape(s)}</b>" if i == word["s"] else escape(s) for i, s in enumerate(word["t"]))


def _english(translations: dict) -> str:
    esv, web = translations.get("ESV"), translations.get("WEB")
    if esv and web and _same(esv, web):
        return f'<p class="mv-en">{escape(esv)} <cite>ESV · WEB</cite></p>'
    out = f'<p class="mv-en">{escape(esv)} <cite>ESV</cite></p>' if esv else ""
    if web:
        out += f'<p class="mv-en{" mv-en-second" if esv else ""}">{escape(web)} <cite>WEB</cite></p>'
    return out


def _same(a: str, b: str) -> bool:
    return " ".join(a.split()) == " ".join(b.split())


def _density(verse: dict) -> str:
    """Long verses step the type down so they still fit a 95 x 67.5 mm card."""
    size = len(verse["words"]) + sum(len(t) for t in verse["translations"].values()) / 25
    return " mv-dense2" if size > 34 else " mv-dense1" if size > 22 else ""
