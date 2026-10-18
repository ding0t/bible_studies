"""Render printable Hebrew word cards wherever a page carries `<!-- hebrew-cards: <deck> -->`.

The JSON is written by references/build/export_hebrew_cards.py from docs/data/hebrew-cards.toml,
which checks every word against the Hebrew text and every quotation against the ESV.

The sheets are the memory verse cards' sheets -- same A4 geometry, crop marks and print rules
(memory-verses.css, keyed on .mv-deck) -- with Hebrew word cards inside them (hebrew.css):

- cards       one-sided: the word, its Paleo-Hebrew form, the reading, the meaning and the verse.
- flashcards  double-sided: the word alone on the front with the letters it introduces, the rest
              on the back, columns swapped so flipping on the long edge lands each back behind
              its front.
"""

from __future__ import annotations

import json
import logging
import re
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.hebrew_cards")

_MARKER = re.compile(r"<!--\s*hebrew-cards:\s*([\w-]+)\s*-->")
_CARDS_PER_SHEET = 8
_REVIEW_DAYS = (1, 2, 4, 7, 14, 30)
# Must match .mv-grid in memory-verses.css -- see hooks/memory_verses.py.
_CUTS_X = (10, 105, 200)
_CUTS_Y = (10, 77.5, 145, 212.5, 280)
_LETTER_NAMES = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", (
    "alef", "bet", "gimel", "dalet", "he", "vav", "zayin", "het", "tet", "yod", "kaf", "lamed",
    "mem", "nun", "samekh", "ayin", "pe", "tsadi", "qof", "resh", "shin", "tav")))
_NOTICE = "ESV® © 2001 Crossway, used by permission · Hebrew: TAHOT, STEPBible.org CC BY"

_data: dict = {"decks": {}}


def _json_path(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data" / "hebrew-cards.json"


def on_serve(server, config, builder):  # noqa: ARG001 - hook signature
    server.watch(str(_json_path(config)))
    return server


def on_config(config):
    _data["decks"] = {}
    try:
        _data.update(json.loads(_json_path(config).read_text(encoding="utf-8")))
    except FileNotFoundError:
        log.info("hebrew_cards: hebrew-cards.json not found -- run references/build/export_hebrew_cards.py")
    return config


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    def deck(match: re.Match) -> str:
        found = _data["decks"].get(match[1])
        if not found:
            log.warning("hebrew_cards: %s asks for deck %r, which does not exist", page.file.src_uri, match[1])
            return ""
        return render_deck(found["cards"], f"hc-{match[1]}", match[1])

    return _MARKER.sub(deck, html)


def render_deck(cards: list[dict], deck_id: str, slug: str) -> str:
    sheets = [cards[i:i + _CARDS_PER_SHEET] for i in range(0, len(cards), _CARDS_PER_SHEET)]
    total = len(sheets)
    one_sided = "".join(_sheet("", [_full(c, n) for n, c in _numbered(sheets, i)], i, total)
                        for i in range(total))
    flash = "".join(
        _sheet("mv-front", [_front(c, n) for n, c in _numbered(sheets, i)], i, total, "fronts")
        + _sheet("mv-back", [_full(c, n, front=False) for n, c in _numbered(sheets, i)], i, total, "backs")
        for i in range(total))
    # The on-screen practice (app/src/entries/hebrew-cards.js) reads the deck from here.
    practice = json.dumps({"slug": slug, "cards": [
        {"id": f"{slug}-{i}", **{k: c[k] for k in ("hebrew", "name", "popular", "meaning", "quote", "quote_ref", "divine", "words")}}
        for i, c in enumerate(cards)]}, ensure_ascii=False).replace("</", "<\\/")
    return f"""
<div class="mv-deck hc-deck" data-no-popups>
  <form class="mv-controls" aria-label="Card layout">
    <fieldset>
      <legend>Print as</legend>
      <label><input type="radio" name="{deck_id}-layout" value="flash" class="mv-opt-flash" checked> Flashcards <small>double-sided, flip on long edge</small></label>
      <label><input type="radio" name="{deck_id}-layout" value="cards" class="mv-opt-cards"> Cards <small>one-sided</small></label>
      <label><input type="radio" name="{deck_id}-layout" value="screen" class="hc-opt-screen"> Practise on screen <small>one card at a time, with spaced review</small></label>
    </fieldset>
    <fieldset>
      <legend>Show</legend>
      <label><input type="checkbox" class="hc-opt-paleo" checked> Paleo-Hebrew</label>
      <label><input type="checkbox" class="hc-opt-modern" checked> Modern Hebrew note</label>
    </fieldset>
    <button type="button" class="md-button md-button--primary" onclick="window.print()">Print</button>
  </form>
  <div class="mv-cards">{one_sided}</div>
  <div class="mv-flash">{flash}</div>
  <div class="hc-screen" aria-live="polite"><p>The on-screen practice needs JavaScript.</p></div>
  <script type="application/json" class="hc-data">{practice}</script>
</div>
<script type="module" src="/assets/js/hebrew-cards.js"></script>
"""


def _numbered(sheets: list[list[dict]], i: int):
    start = i * _CARDS_PER_SHEET
    sheet = sheets[i] + [None] * (_CARDS_PER_SHEET - len(sheets[i]))
    return [(start + k + 1, c) for k, c in enumerate(sheet)]


def _sheet(kind: str, cards: list[str], index: int, total: int, side: str = "") -> str:
    ticks = "".join(f'<i class="mv-tick mv-tick-x" style="--at:{x}"></i>' for x in _CUTS_X)
    ticks += "".join(f'<i class="mv-tick mv-tick-y" style="--at:{y}"></i>' for y in _CUTS_Y)
    label = f"Sheet {index + 1} of {total}" + (f" · {side}" if side else "")
    return f"""<section class="mv-sheet {kind}" aria-label="{label}">
  {ticks}<span class="mv-scissors" aria-hidden="true">✂</span>
  <div class="mv-grid">{''.join(cards)}</div>
  <footer class="mv-sheet-foot"><span>{label}</span><span>{_NOTICE}</span></footer>
</section>"""


def _hebrew(card: dict) -> str:
    paleo = " ".join(w["paleo"] for w in card["words"])
    return (f'<p class="hc-word" lang="he" dir="rtl">{escape(card["hebrew"])}</p>'
            f'<p class="hc-paleo" dir="rtl" title="Paleo-Hebrew">{escape(paleo)}</p>')


def _front(card: dict | None, number: int) -> str:
    if card is None:
        return _blank(number)
    new = "".join(f'<span><b lang="he">{escape(c)}</b>{_LETTER_NAMES[c]}</span>' for c in card["new_letters"])
    new += "".join(f'<span><b lang="he">{escape(c)}</b>final</span>' for c in card["new_finals"])
    boxes = "".join(f"<span><i></i>{d}</span>" for d in _REVIEW_DAYS)
    return f"""<article class="mv-card hc-card hc-prompt">
  {_hebrew(card)}
  <div class="hc-new">{('<em>New</em>' + new) if new else '<em>No new letters: read it</em>'}</div>
  <div class="hc-progress" style="--known:{card['letters_known']}" title="{card['letters_known']} of 22 letters"><i></i><span>{card['letters_known']}/22</span></div>
  <div class="mv-review" title="Tick a box each time you read it: days after learning">{boxes}<em>days</em></div>
  <span class="mv-num">{number}</span>
</article>"""


def _full(card: dict | None, number: int, front: bool = True) -> str:
    if card is None:
        return _blank(number)
    popular = f'<small>also “{escape(card["popular"])}”</small>' if card["popular"] else ""
    strongs = " ".join(w["strongs"] for w in card["words"] if w["strongs"])
    return f"""<article class="mv-card hc-card hc-full">
  <header class="mv-head"><b>{escape(card["name"])}</b><span>{escape(strongs)}</span></header>
  {_hebrew(card) if front else ''}
  <p class="hc-reading" dir="rtl">{''.join(_reading(w, card["divine"]) for w in card["words"])}</p>
  <p class="hc-meaning">{escape(card["meaning"])}{popular}</p>
  <p class="mv-en">{escape(card["quote"])} <cite>{escape(card["quote_ref"])} ESV</cite></p>
  <p class="hc-modern"><b>Today</b> {escape(card["modern"])}</p>
  <span class="mv-num">{number}</span>
</article>"""


def _reading(word: dict, divine: bool) -> str:
    if divine and not word["t"]:
        # H3069 is the name pointed for Elohim, as after Adonai in "Adonai YHWH" (Isaiah 61:1).
        read = "Elohim" if word["strongs"] == "H3069" else "Adonai"
        return f'<span class="hc-syl"><b lang="he">{escape(word["w"])}</b><i>read <em>{read}</em></i></span>'
    # A one-syllable word has nowhere else for the stress to fall, so it is not marked.
    stress = word["s"] if len(word["t"]) > 1 else None
    syllables = "·".join(f"<u>{escape(s)}</u>" if i == stress else escape(s) for i, s in enumerate(word["t"]))
    return f'<span class="hc-syl"><b lang="he">{escape(word["w"])}</b><i>{syllables}</i></span>'


def _blank(number: int) -> str:
    return f"""<article class="mv-card mv-blank">
  <header class="mv-head"><b>Word</b><span>Meaning</span></header>
  <div class="mv-lines"></div>
  <span class="mv-num">{number}</span>
</article>"""
