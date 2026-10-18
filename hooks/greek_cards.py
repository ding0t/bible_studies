"""Render printable Greek word cards wherever a page carries `<!-- greek-cards: <deck> -->`.

The Greek counterpart of hooks/hebrew_cards.py, on the same sheets (memory-verses.css) and the
same card layout (hebrew.css's .hc-* rules, with greek.css for the script). The JSON is written
by references/build/export_greek_cards.py from docs/data/greek-cards.toml, which checks every word
against the SBL Greek New Testament and every quotation against the ESV.

Where a Hebrew card shows the word in Paleo-Hebrew, a Greek card shows it in uncial capitals, as
the codices wrote it. The two decks share the on-screen practice (app/src/entries/hebrew-cards.js),
which reads the language from the deck's JSON.
"""

from __future__ import annotations

import json
import logging
import re
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.greek_cards")

_MARKER = re.compile(r"<!--\s*greek-cards:\s*([\w-]+)\s*-->")
_CARDS_PER_SHEET = 8
_REVIEW_DAYS = (1, 2, 4, 7, 14, 30)
# Must match .mv-grid in memory-verses.css -- see hooks/memory_verses.py.
_CUTS_X = (10, 105, 200)
_CUTS_Y = (10, 77.5, 145, 212.5, 280)
_LETTERS = 24
_LETTER_NAMES = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", (
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda",
    "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega")))
_NOTICE = "ESV® © 2001 Crossway, used by permission · Greek: SBLGNT"

_data: dict = {"decks": {}}


def _json_path(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data" / "greek-cards.json"


def on_serve(server, config, builder):  # noqa: ARG001 - hook signature
    server.watch(str(_json_path(config)))
    return server


def on_config(config):
    _data["decks"] = {}
    try:
        _data.update(json.loads(_json_path(config).read_text(encoding="utf-8")))
    except FileNotFoundError:
        log.info("greek_cards: greek-cards.json not found -- run references/build/export_greek_cards.py")
    return config


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    def deck(match: re.Match) -> str:
        found = _data["decks"].get(match[1])
        if not found:
            log.warning("greek_cards: %s asks for deck %r, which does not exist", page.file.src_uri, match[1])
            return ""
        return render_deck(found["cards"], f"gc-{match[1]}", match[1])

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
    practice = json.dumps({
        "slug": slug, "store": "greek-cards", "lang": "grc", "dir": "ltr", "voice": "el",
        "cards": [{"id": f"{slug}-{i}", "word": c["greek"], "second": _uncial(c), "divine": False,
                   **{k: c[k] for k in ("name", "popular", "meaning", "quote", "quote_ref", "words")}}
                  for i, c in enumerate(cards)]}, ensure_ascii=False).replace("</", "<\\/")
    return f"""
<div class="mv-deck hc-deck gc-deck" data-no-popups>
  <form class="mv-controls" aria-label="Card layout">
    <fieldset>
      <legend>Print as</legend>
      <label><input type="radio" name="{deck_id}-layout" value="flash" class="mv-opt-flash" checked> Flashcards <small>double-sided, flip on long edge</small></label>
      <label><input type="radio" name="{deck_id}-layout" value="cards" class="mv-opt-cards"> Cards <small>one-sided</small></label>
      <label><input type="radio" name="{deck_id}-layout" value="screen" class="hc-opt-screen"> Practise on screen <small>one card at a time, with spaced review</small></label>
    </fieldset>
    <fieldset>
      <legend>Show</legend>
      <label><input type="checkbox" class="hc-opt-paleo" checked> Uncial capitals</label>
      <label><input type="checkbox" class="hc-opt-modern" checked> Modern Greek note</label>
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


def _uncial(card: dict) -> str:
    return " ".join(w["uncial"] for w in card["words"])


def _greek(card: dict) -> str:
    return (f'<p class="hc-word" lang="grc">{escape(card["greek"])}</p>'
            f'<p class="hc-paleo gc-uncial" title="Uncial capitals">{escape(_uncial(card))}</p>')


def _front(card: dict | None, number: int) -> str:
    if card is None:
        return _blank(number)
    new = "".join(f'<span><b lang="grc">{escape(c)}</b>{_LETTER_NAMES[c]}</span>' for c in card["new_letters"])
    new += "".join(f'<span><b lang="grc">{escape(c)}</b>final</span>' for c in card["new_finals"])
    boxes = "".join(f"<span><i></i>{d}</span>" for d in _REVIEW_DAYS)
    return f"""<article class="mv-card hc-card hc-prompt">
  {_greek(card)}
  <div class="hc-new">{('<em>New</em>' + new) if new else '<em>No new letters: read it</em>'}</div>
  <div class="hc-progress" style="--known:{card['letters_known']};--total:{_LETTERS}" title="{card['letters_known']} of {_LETTERS} letters"><i></i><span>{card['letters_known']}/{_LETTERS}</span></div>
  <div class="mv-review" title="Tick a box each time you read it: days after learning">{boxes}<em>days</em></div>
  <span class="mv-num">{number}</span>
</article>"""


def _full(card: dict | None, number: int, front: bool = True) -> str:
    if card is None:
        return _blank(number)
    popular = f'<small>also “{escape(card["popular"])}”</small>' if card["popular"] else ""
    strongs = " ".join(w["strongs"] for w in card["words"] if w["strongs"] and w["strongs"] != "G3588")
    return f"""<article class="mv-card hc-card hc-full">
  <header class="mv-head"><b>{escape(card["name"])}</b><span>{escape(strongs)}</span></header>
  {_greek(card) if front else ''}
  <p class="hc-reading">{''.join(_reading(w) for w in card["words"])}</p>
  <p class="hc-meaning">{escape(card["meaning"])}{popular}</p>
  <p class="mv-en">{escape(card["quote"])} <cite>{escape(card["quote_ref"])} ESV</cite></p>
  <p class="hc-modern"><b>Today</b> {escape(card["modern"])}</p>
  <span class="mv-num">{number}</span>
</article>"""


def _reading(word: dict) -> str:
    if not word["t"]:
        return f'<span class="hc-syl"><b lang="grc">{escape(word["w"])}</b><i></i></span>'
    # A one-syllable word has nowhere else for the stress to fall, so it is not marked.
    stress = word["s"] if len(word["t"]) > 1 else None
    syllables = "·".join(f"<u>{escape(s)}</u>" if i == stress else escape(s) for i, s in enumerate(word["t"]))
    return f'<span class="hc-syl"><b lang="grc">{escape(word["w"])}</b><i>{syllables}</i></span>'


def _blank(number: int) -> str:
    return f"""<article class="mv-card mv-blank">
  <header class="mv-head"><b>Word</b><span>Meaning</span></header>
  <div class="mv-lines"></div>
  <span class="mv-num">{number}</span>
</article>"""
