"""Render A4 Hebrew handwriting sheets wherever a page carries `<!-- hebrew-writing -->`.

Four sets, one shown (and printed) at a time through a radio switch, CSS only:

- square    the printed letters of every Hebrew Bible, the 22 and their five final forms
- cursive   the same 27 forms as Israelis write them by hand (Gveret Levin, SIL OFL)
- paleo     the 22 letters in the script Israel wrote before the exile (Unicode Phoenician)
- names     the names of God from docs/data/hebrew-cards.json, to copy in all three scripts

Each row runs right to left as Hebrew is written: the model letter and its name, three grey
letters to trace, then empty places on the same four guide lines. The sheets reuse the memory
verse sheets' paper, crop-free print rules and sheet millimetres (memory-verses.css); the rows
are styled in hebrew.css.
"""

from __future__ import annotations

import json
import logging
import re
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.hebrew_writing")

_MARKER = re.compile(r"<!--\s*hebrew-writing\s*-->")
_ROWS_PER_SHEET = 9
_TRACES = 3
_BLANKS = 4
_NAMES_ROWS_PER_SHEET = 6

# (letter, name, Israeli sound) -- the sounds as alphabet.md gives them.
_LETTERS = (
    ("א", "alef", "silent"), ("ב", "bet", "b / v"), ("ג", "gimel", "g"), ("ד", "dalet", "d"),
    ("ה", "he", "h"), ("ו", "vav", "v"), ("ז", "zayin", "z"), ("ח", "het", "kh"),
    ("ט", "tet", "t"), ("י", "yod", "y"), ("כ", "kaf", "k / kh"), ("ך", "final kaf", "kh"),
    ("ל", "lamed", "l"), ("מ", "mem", "m"), ("ם", "final mem", "m"), ("נ", "nun", "n"),
    ("ן", "final nun", "n"), ("ס", "samekh", "s"), ("ע", "ayin", "silent"), ("פ", "pe", "p / f"),
    ("ף", "final pe", "f"), ("צ", "tsadi", "ts"), ("ץ", "final tsadi", "ts"), ("ק", "qof", "k"),
    ("ר", "resh", "r"), ("ש", "shin", "sh / s"), ("ת", "tav", "t"),
)
_ALPHABET = "אבגדהוזחטיכלמנסעפצקרשת"
_PALEO = {letter: chr(0x10900 + i) for i, letter in enumerate(_ALPHABET)}
_SETS = (
    ("square", "Square print", "the letters of every printed Hebrew Bible"),
    ("cursive", "Cursive", "how Israelis write by hand today"),
    ("paleo", "Paleo-Hebrew", "the script of Israel before the exile"),
    ("names", "Names of God", "copy each name in all three scripts"),
)
_NOTICE = "the-way.lewy.au/hebrew/writing-sheets · Cursive: Gveret Levin, SIL OFL · Paleo: Noto Sans Phoenician, SIL OFL"

_cards: list[dict] = []


def _json_path(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data" / "hebrew-cards.json"


def on_config(config):
    _cards.clear()
    try:
        data = json.loads(_json_path(config).read_text(encoding="utf-8"))
        _cards.extend(data["decks"]["names-of-god"]["cards"])
    except FileNotFoundError:
        log.info("hebrew_writing: hebrew-cards.json not found -- the names set will be empty")
    return config


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    return _MARKER.sub(lambda _: render(), html)


def render() -> str:
    letter_rows = {
        "square": [(c, n, s) for c, n, s in _LETTERS],
        "cursive": [(c, n, s) for c, n, s in _LETTERS],
        # Names only: Israeli sounds would be anachronistic for the pre-exile script (vav was w).
        "paleo": [(_PALEO[c], n, "") for c, n, s in _LETTERS if c in _PALEO],
    }
    radios = "".join(
        f'<label><input type="radio" name="hw-set" value="{key}" class="hw-opt-{key}"{" checked" if i == 0 else ""}>'
        f' {label} <small>{hint}</small></label>'
        for i, (key, label, hint) in enumerate(_SETS))
    sets = "".join(_letter_set(key, rows) for key, rows in letter_rows.items()) + _names_set()
    return f"""
<div class="mv-deck hw-deck" data-no-popups>
  <form class="mv-controls" aria-label="Writing sheets">
    <fieldset><legend>Sheets</legend>{radios}</fieldset>
    <button type="button" class="md-button md-button--primary" onclick="window.print()">Print</button>
  </form>
  {sets}
</div>
"""


def _letter_set(key: str, rows: list[tuple[str, str, str]]) -> str:
    pages = [rows[i:i + _ROWS_PER_SHEET] for i in range(0, len(rows), _ROWS_PER_SHEET)]
    title = next(label for k, label, _ in _SETS if k == key)
    sheets = "".join(
        _sheet(f"{title} · sheet {i + 1} of {len(pages)}", "".join(_letter_row(*row) for row in page),
               _ROWS_PER_SHEET)
        for i, page in enumerate(pages))
    return f'<div class="hw-set hw-{key}" lang="he">{sheets}</div>'


def _letter_row(glyph: str, name: str, sound: str) -> str:
    g = escape(glyph)
    traces = f'<span class="hw-cell hw-trace">{g}</span>' * _TRACES
    blanks = '<span class="hw-cell"></span>' * _BLANKS
    return (f'<div class="hw-row" dir="rtl"><span class="hw-cell hw-model">{g}'
            f'<small dir="ltr">{escape(name)}{" · " + escape(sound) if sound else ""}</small></span>{traces}{blanks}</div>')


def _names_set() -> str:
    pages = [_cards[i:i + _NAMES_ROWS_PER_SHEET] for i in range(0, len(_cards), _NAMES_ROWS_PER_SHEET)]
    sheets = "".join(
        _sheet(f"Names of God · sheet {i + 1} of {len(pages)}", "".join(_name_row(c) for c in page),
               _NAMES_ROWS_PER_SHEET)
        for i, page in enumerate(pages))
    return f'<div class="hw-set hw-names" lang="he">{sheets}</div>'


def _name_row(card: dict) -> str:
    hebrew = escape(card["hebrew"])
    paleo = escape(" ".join(w["paleo"] for w in card["words"]))
    return f"""<div class="hw-name">
  <header dir="ltr"><b>{escape(card["name"])}</b> {escape(card["meaning"])} <cite>{escape(card["ref"])}</cite></header>
  <div class="hw-line" dir="rtl"><span class="hw-script">Square</span><span class="hw-model-word">{hebrew}</span><span class="hw-copy"></span></div>
  <div class="hw-line hw-line-cursive" dir="rtl"><span class="hw-script">Cursive</span><span class="hw-model-word">{hebrew}</span><span class="hw-copy"></span></div>
  <div class="hw-line hw-line-paleo" dir="rtl"><span class="hw-script">Paleo</span><span class="hw-model-word">{paleo}</span><span class="hw-copy"></span></div>
</div>"""


def _sheet(label: str, rows: str, capacity: int) -> str:
    # The last sheet of a set keeps the row height of a full one, so letters stay the same size.
    return f"""<section class="mv-sheet hw-sheet" aria-label="{escape(label)}" style="--rows:{capacity}">
  <div class="hw-rows">{rows}</div>
  <footer class="mv-sheet-foot"><span>{escape(label)}</span><span>{_NOTICE}</span></footer>
</section>"""
