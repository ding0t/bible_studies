"""Render the reference of the Old Testament's prophecies of Christ wherever a page carries a marker.

- `<!-- prophecies-of-christ: measures -->`        the counts by subject, as a table
- `<!-- prophecies-of-christ: dated -->`           one sentence: how many are tied to a dated event,
                                                   and how many were written and copied before it
- `<!-- prophecies-of-christ: category <name> -->` the entries of one category, as cards
- `<!-- prophecies-of-christ: nt -->`              the prophecies that begin in the New Testament
- `<!-- prophecies-of-christ: floor -->`           the chance floor a reader sets: the prophecies no
                                                   one could have arranged, one trial per moment,
                                                   and a slider for the chance given each
- `<!-- prophecies-of-christ: explorer -->`        three pictures of the ledger (a Sankey from the Law,
                                                   the Prophets and the Psalms to the New Testament, a
                                                   wheel of subjects, a grid of who could have arranged
                                                   each), every mark a filter over the cards
- `<!-- prophecies-of-christ: filter -->`          a bar of filters over the cards: pick any values
                                                   in any facets (or within a facet, and across
                                                   them), with a live count on every chip. The
                                                   labels are written here; the behaviour is
                                                   app/src/entries/prophecy-filter.js, and without
                                                   it the bar stays hidden and every card shows.

It also writes assets/popups/prophecies.json, so the verse pop-up on any page can say that a verse
is a prophecy of Christ, or a New Testament use of one, and link to its card.

The ledger is docs/data/prophecies-of-christ.toml. What needs a Bible database (the Qumran copies)
or the authorship table and the chronology (the years) comes from docs/data/prophecies-of-christ.json,
which references/build/export_prophecies.py writes; utils/check_prophecies.py fails while it is
stale, so the counts here are the ledger's. Every count on the page is written here, never by hand.

The cards live on the ledger page, prophecies-of-christ.md (under Explore); the study that argues
from them, jesus/foretold-long-ago.md, carries the chance floor. Each card carries id="prophecy-<id>",
so a study links to one entry as `../prophecies-of-christ.md#prophecy-<id>`. References are plain text so the verse pop-up
finds them. An entry's `notes` are the ledger's working notes (leads, questions for a later session)
and never reach the page; every field that does is kept free of working language by
utils/check_prophecies.py. The styles are in assets/stylesheets/prophecies.css.
"""

from __future__ import annotations

import json
import logging
import math
import re
import tomllib
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.prophecies")

_MARKER = re.compile(r"<!--\s*prophecies-of-christ:\s*(measures|explorer|dated|nt|filter|floor|category\s+[\w-]+)\s*-->")

# The labels utils/build_jesus_graphics.py's chart uses, so the page and the chart agree.
CATEGORIES = {
    "nature": "Nature", "lineage": "Lineage", "birth": "Birth", "childhood": "Childhood",
    "forerunner": "Forerunner", "ministry": "Ministry", "passion": "Passion",
    "resurrection": "Resurrection", "redemption": "Redemption", "office": "Prophet, priest, king",
    "future": "Future",
}
# The card's evidence rows, each under its own label (_facts); How to read a card explains them.
TIERS = {
    1: "Says it was fulfilled in Him, spoke of Him, or was shaped to point to Him",
    2: "Applies it to Him",
    3: "At most alludes to it: the reading is tradition's",
}
STATUS = {"fulfilled": "Fulfilled", "partly": "Partly fulfilled", "future": "Still to come"}
USE_KINDS = {
    "fulfilment": "fulfilled", "split": "part now, part still to come", "type": "a type",
    "application": "applied", "imagery": "its imagery", "allusion": "an allusion",
}
USE_TEXTS = {
    "mt": "follows the Hebrew", "lxx": "follows the Septuagint", "both": "the Hebrew and the Septuagint agree",
    "neither": "follows neither text", "none": "",
}
RECOGNITION = {
    "known-before": "Before Jesus, by a witness older than Him",
    "partly": "Before Jesus, of a part other than the one He fulfilled",
    "read-after": "Only in a later Jewish source",
    "veiled": "In no Jewish source, before Jesus or since",
    "unassessed": "Not yet assessed",
}
CONTROL = {
    "divine": "God alone, beyond any human agent",
    "opponents": "His opponents",
    "unwitting": "Someone with no thought of the prophecy",
    "followers": "His followers",
    "chosen": "Jesus Himself, knowingly",
    "unfulfilled": "",
}
SPEAKERS = {"jesus": "Jesus", "angel": "An angel", "apostle": "An apostle", "revelation": "Revelation"}
RECORDED = {
    "before": "Before it came to pass",
    "after": "After it came to pass",
    "contested": "Whether before it came to pass is contested",
}

# A run of Hebrew or Aramaic letters (with points and maqaf), spaces allowed inside the run.
_HEBREW = re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F]+(?:\s+[\u0590-\u05FF\uFB1D-\uFB4F]+)*")

# The page that carries the cards. The floor (on the study) and each commentary chapter link to them.
LEDGER_PAGE = "prophecies-of-christ.md"

_ledger: list[dict] = []
# The page the markers are on, for the pop-up's links; set when it renders.
_page_url: list[str] = []
_nt: list[dict] = []
_computed: dict[str, dict] = {}


def _data(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data"


def on_serve(server, config, builder):  # noqa: ARG001 - hook signature
    # Outside docs_dir, so `mkdocs serve` would otherwise keep the old ledger.
    server.watch(str(_data(config) / "prophecies-of-christ.toml"))
    server.watch(str(_data(config) / "prophecies-of-christ.json"))
    return server


def on_config(config):
    _page_url.clear()
    ledger = tomllib.loads((_data(config) / "prophecies-of-christ.toml").read_text(encoding="utf-8"))
    computed = json.loads((_data(config) / "prophecies-of-christ.json").read_text(encoding="utf-8"))
    _ledger[:] = ledger["prophecy"]
    _nt[:] = ledger.get("nt_prophecy", [])
    _computed.clear()
    _computed.update({row["id"]: row for row in computed["prophecies"]})
    missing = [e["id"] for e in _ledger if e["id"] not in _computed]
    if missing:
        log.warning("prophecies: %d entries have no computed row (%s) -- run "
                    "references/build/export_prophecies.py", len(missing), ", ".join(missing[:5]))
    return config


_COMMENTARY = re.compile(r"^commentaries/(\d{2})-[^/]+/chapter-(\d{3})\.md$")


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    if "<!-- prophecies-of-christ: category" in html and not _page_url:
        _page_url.append(page.url)
    if m := _COMMENTARY.match(page.file.src_uri):
        html += _chapter_section(int(m[1]), int(m[2]), files)
    ledger = files.get_file_from_path(LEDGER_PAGE)
    # The site is served at the root of its domain, so a site-absolute address needs no prefix.
    ledger_url = "/" + ledger.url if ledger else ""
    return _MARKER.sub(lambda m: _render(m[1], page.file.src_uri, ledger_url), html)


def _render(what: str, src: str, ledger_url: str) -> str:
    if what == "measures":
        return _measures()
    if what == "dated":
        return _dated()
    if what == "filter":
        return _filter()
    if what == "explorer":
        return _explorer()
    if what == "floor":
        return _floor(ledger_url)
    if what == "nt":
        return f'<div class="pc-group">{"".join(_nt_card(e) for e in _nt)}</div>'
    category = what.split()[1]
    entries = [e for e in _ledger if e["category"] == category]
    if not entries:
        log.warning("prophecies: %s asks for category %r, which has no entries", src, category)
    return f'<div class="pc-group" data-category="{escape(category)}">{"".join(_card(e) for e in entries)}</div>'


def _text(s: str) -> str:
    """Escaped, with Hebrew in its own right-to-left span, as the site's rule has it (never bold)."""
    return _HEBREW.sub(lambda m: f'<span dir="rtl" lang="he">{m[0]}</span>', escape(s))


def year_label(y: int) -> str:
    return f"{-y} BC" if y < 0 else f"AD {y}"


def _years(row: dict) -> str:
    if row.get("fulfilled") is None:
        return ""
    trad, crit = row["written_traditional"], row["written_critical"]
    line = (f"By {year_label(trad)}; came to pass {year_label(row['fulfilled'])}: "
            f"{row['years_ahead_traditional']:,} years ahead")
    # The critics' date matters only where it is later; an earlier one (Isaiah 7) moves nothing.
    if crit is not None and crit > trad:
        line += f", or {row['years_ahead_critical']:,} on the latest date critics give it ({year_label(crit)})"
    elif crit is None and row.get("existed_by") is not None:
        line += (f"; on any dating it existed by {year_label(row['existed_by'])}, when Sirach names the book: "
                 f"{row['years_ahead_at_least']:,} years ahead at the least")
    return line + "."


def _copy(row: dict) -> str:
    if row.get("manuscript_before") and "1Qisaa" in row["qumran"]:
        return "A copy older than the event survives: the Great Isaiah Scroll (about 125 BC)."
    if row.get("manuscript_before"):
        return f"A copy older than the event survives at Qumran: {', '.join(row['qumran'])}."
    if row.get("qumran"):
        return f"Copied at Qumran before AD 68: {', '.join(row['qumran'])}."
    return ""


def _use(use: dict) -> str:
    parts = [USE_KINDS.get(use["kind"], use["kind"])]
    if USE_TEXTS.get(use.get("text", "none")):
        parts.append(USE_TEXTS[use["text"]])
    note = f'<span class="pc-use-note">{_text(use["note"])}</span>' if use.get("note") else ""
    return f'<li><b>{escape(use["ref"])}</b> <span class="pc-kind">{escape("; ".join(parts))}</span> {note}</li>'


def _pole(kind: str, label: str, text: str) -> str:
    return f'<div class="pc-pole pc-{kind}"><span class="pc-label">{label}</span><p>{text}</p></div>'


def _gap(years: int | None, status: str) -> str:
    """The bridge between what was foretold and what came of it, carrying the years between."""
    count = (f'<b class="pc-gap-n">{years:,}</b><span class="pc-gap-unit">years</span>'
             if years and years > 0 else "")
    return f'<div class="pc-gap pc-gap-{status}" aria-hidden="true">{count}<i class="pc-arrow"></i></div>'


def _takeaway(e: dict, years: int | None, fulfilled: str, rest: str) -> str:
    """What was foretold beside what came to pass, and below them what is still to come."""
    left = "The pattern" if e.get("form") == "type" else "Foretold"
    said = _text(e.get("predicts", ""))
    said = said[:1].upper() + said[1:]
    if fulfilled:
        out = _pole("foretold", left, said) + _gap(years, e["status"]) + _pole("came", "Fulfilled", fulfilled)
    elif rest:
        out = _pole("foretold", left, said) + _gap(None, e["status"]) + _pole("awaits", "Still to come", rest)
        rest = ""
    else:
        out = _pole("foretold", left, said)
    if rest:
        out += _pole("awaits pc-after", "Still to come", rest)
    single = "" if fulfilled or rest or e.get("still_to_come") else " pc-single"
    return f'<div class="pc-takeaway{single}">{out}</div>'


def _facts(rows: list[tuple[str, str]]) -> str:
    return '<dl class="pc-facts">' + "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in rows if v) + "</dl>"


def _head(e: dict, extra: str = "") -> str:
    form = ' <span class="pc-form">a type</span>' if e.get("form") == "type" else ""
    return (f'<header class="pc-head"><b class="pc-ref">{escape(e["prophecy"])}</b>{form}{extra}'
            f'<span class="pc-status">{escape(STATUS[e["status"]])}</span></header>')


def _card(e: dict) -> str:
    row = _computed.get(e["id"], {})
    years = row.get("years_ahead_traditional") if row.get("fulfilled") is not None else None
    takeaway = _takeaway(e, years, _text(e.get("came_to_pass", "")), _text(e.get("still_to_come", "")))
    facts = _facts([("Written", _years(row)), ("Oldest copy", _copy(row)),
                    ("Read of the Messiah", RECOGNITION.get(e.get("recognition", "unassessed"), "")),
                    ("Brought about by", CONTROL.get(e.get("control", ""), "")),
                    ("The New Testament", TIERS[e["tier"]])])
    uses = "".join(_use(u) for u in e.get("uses", []))
    uses = f'<p class="pc-sub">Where the New Testament uses it</p><ul class="pc-uses">{uses}</ul>' if uses else ""
    first = ""
    if e.get("near"):
        first = f'<p class="pc-near"><b>First meant</b> {_text(e["near"])}'
        if e.get("exceeds"):
            first += f' <b>Where the words go further</b> {_text(e["exceeds"])}'
        first += "</p>"
    split = ""
    if e.get("split"):
        s = e["split"]
        split = (f'<p class="pc-split"><b>Two comings in one text</b> Fulfilled: {_text(s["first"])}. '
                 f'Still to come: {_text(s["rest"])}. Divided at {escape(s["at"])}.</p>')
    facets = " ".join(f'data-{k}="{escape(" ".join(v))}"' for k, v in _facets(e).items())
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}" {facets}>
  {_head(e)}
  {takeaway}
  <div class="pc-rule"><span>The evidence</span></div>
  {facts}{uses}{first}{split}
</article>"""


def _nt_card(e: dict) -> str:
    # A future prediction is itself what is still to come, so its card has the one panel.
    takeaway = _takeaway(e, None, _text(e.get("came_to_pass", "")), _text(e.get("still_to_come", "")))
    facts = _facts([("Spoken by", SPEAKERS[e["speaker"]]), ("Fulfilled in", e.get("fulfilment", "")),
                    ("Written down", RECORDED.get(e.get("recorded", ""), "")),
                    ("Brought about by", CONTROL.get(e.get("control", ""), ""))])
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}">
  {_head(e)}
  {takeaway}
  <div class="pc-rule"><span>The evidence</span></div>
  {facts}
</article>"""


def _measures() -> str:
    head = ("<tr><th>Subject</th><th>Prophecies</th><th>Fulfilled</th><th>In part</th><th>Still to come</th>"
            "<th>Read of the Messiah before Jesus</th><th>Brought about by His opponents</th></tr>")

    def row(label: str, entries: list[dict], tag: str = "td") -> str:
        cells = [len(entries)] + [sum(e["status"] == s for e in entries) for s in STATUS] + [
            sum(e.get("recognition") == "known-before" for e in entries),
            sum(e.get("control") == "opponents" for e in entries)]
        return f"<tr><{tag}>{escape(label)}</{tag}>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"

    body = "".join(row(label, [e for e in _ledger if e["category"] == key]) for key, label in CATEGORIES.items())
    return (f'<table class="pc-measures"><thead>{head}</thead><tbody>{body}</tbody>'
            f'<tfoot>{row("All", _ledger, "th")}</tfoot></table>')


def _dated() -> str:
    rows = [r for r in _computed.values() if r.get("fulfilled") is not None]
    before = sum(r["years_ahead_traditional"] > 0 for r in rows)
    critical = [r for r in rows if r["written_critical"] is not None]
    before_crit = sum(r["years_ahead_critical"] > 0 for r in critical)
    bracketed = [r for r in rows if r["written_critical"] is None and r.get("existed_by") is not None]
    before_bracket = sum(r["years_ahead_at_least"] > 0 for r in bracketed)
    open_ = len(rows) - len(critical) - len(bracketed)
    manuscript = sum(r["manuscript_before"] and "1Qisaa" in r["qumran"] for r in rows)
    qumran = sum(bool(r["qumran"]) for r in _computed.values())
    return (f'<p class="pc-dated">{len(rows)} of the {len(_ledger)} prophecies are tied to an event this '
            f"site's chronology dates, and {before} of them were written before it on the traditional dates. "
            f"For {len(critical)} of them this site records the date critical scholarship gives the text, "
            f"and {before_crit} of those were written before the event on that date too. For {len(bracketed)} more, "
            f"in Jeremiah, Ezekiel and the Twelve, Sirach names the book, so on any dating it existed by 132 BC: "
            f"{before_bracket} of those came before the event. The other {open_}, most of them in the Psalms, "
            f"carry only the traditional date here. {manuscript} survive in the "
            f"Great Isaiah Scroll, a manuscript older than the event. At least part of the Hebrew of "
            f"{qumran} of all {len(_ledger)} is among the Dead Sea Scrolls, copied before AD 68.</p>")


# The filter bar's facets: (data attribute, heading, [(value, chip label)]). The values are the
# ledger's own; the labels are the cards' wording, shortened to fit a chip.
FACETS = [
    ("category", "Subject", list(CATEGORIES.items())),
    ("status", "Fulfilled", [("fulfilled", "Fulfilled"), ("partly", "In part"), ("future", "Still to come")]),
    ("control", "Brought about by", [("divine", "God alone"), ("opponents", "His opponents"),
                                     ("unwitting", "Someone unaware"), ("followers", "His followers"),
                                     ("chosen", "Jesus, knowingly")]),
    ("recognition", "Read of the Messiah", [("known-before", "Before Jesus"), ("partly", "In part, before Jesus"),
                                            ("read-after", "Only in a later Jewish source"),
                                            ("veiled", "In no Jewish source")]),
    ("tier", "The New Testament", [("1", "Says it was fulfilled in Him"), ("2", "Applies it to Him"),
                                   ("3", "At most alludes (tradition)")]),
    ("text", "Its wording follows", [("mt", "The Hebrew, afresh"), ("lxx", "The Septuagint"),
                                     ("both", "Both, where they agree"), ("neither", "Neither")]),
    ("feature", "Features", [("split", "Two comings in one text"), ("yhwh", "The LORD's words, said of Jesus"),
                             ("type", "A type"), ("messiah", "Spoken in His voice"),
                             ("manuscript", "A copy older than the event"),
                             ("after", "Understood only afterwards")]),
]


def _facets(e: dict) -> dict[str, list[str]]:
    row = _computed.get(e["id"], {})
    features = [name for name, present in (
        ("split", "split" in e), ("yhwh", e.get("yhwh_text")), ("type", e.get("form") == "type"),
        ("messiah", e.get("speaker") == "messiah"), ("manuscript", row.get("manuscript_before")),
        ("after", e.get("understood_after"))) if present]
    return {
        "category": [e["category"]], "status": [e["status"]], "control": [e.get("control", "")],
        "recognition": [e.get("recognition", "unassessed")], "tier": [str(e["tier"])],
        "text": sorted({u["text"] for u in e.get("uses", []) if u.get("text") and u["text"] != "none"}),
        "feature": features,
        # The explorer's facets, which have no chips in the bar: a book, a division or a writer is
        # chosen by clicking it in a picture.
        "division": [_DIVISION.get(book_of(e["prophecy"]), "")],
        "book": [book_slug(book_of(e["prophecy"]))],
        "nt": sorted({book_slug(book_of(u["ref"])) for u in e.get("uses", [])}) or [NO_USE],
    }


def _filter() -> str:
    groups = []
    for key, heading, values in FACETS:
        chips = "".join(f'<button type="button" class="pc-chip" data-facet="{key}" data-value="{escape(value)}" '
                        f'aria-pressed="false">{escape(label)} <span class="pc-n"></span></button>'
                        for value, label in values)
        groups.append(f'<div class="pc-facet" role="group" aria-label="{escape(heading)}">'
                      f'<span class="pc-facet-name">{escape(heading)}</span>{chips}</div>')
    return (f'<div class="pc-filter" hidden><p class="pc-shown" aria-live="polite"></p>{"".join(groups)}'
            f'<button type="button" class="pc-clear">Clear the filters</button></div>'
            f'<script type="module" src="/assets/js/prophecy-filter.js"></script>')


# ---- The explorer: three pictures of the ledger over its cards ---------------------------------
# Drawn here, so every count is the ledger's and the plates show without JavaScript. In the Larkin
# hand of the site's other plates (parchment and ink, the same in light and dark). prophecy-filter.js
# makes each book, subject, writer and cell a filter, and dims what a choice leaves out: every
# clickable mark carries `data-pick` ("facet:value", two for a grid cell) and `data-units`, the
# entries it stands for ("<id>", or "<id>@<nt book>" for a New Testament use).

# Luke 24:44's three divisions, "the Law of Moses, the Prophets, and the Psalms" (BSB), each in English
# order. Daniel stands with the Prophets, as Jesus names him (Matthew 24:15), though the Hebrew canon
# sets him among the Writings, which "the Psalms" heads.
DIVISIONS = (
    ("law", "The Law", ("Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy")),
    ("prophets", "The Prophets", (
        "Joshua", "Judges", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "Isaiah", "Jeremiah", "Ezekiel",
        "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi")),
    ("writings", "The Psalms", (
        "Psalm", "Job", "Proverbs", "Ruth", "Song of Songs", "Ecclesiastes", "Lamentations", "Esther",
        "Ezra", "Nehemiah", "1 Chronicles", "2 Chronicles")),
)
NT_GROUPS = (
    ("Gospels", ("Matthew", "Mark", "Luke", "John")),
    ("Acts", ("Acts",)),
    ("Letters", (
        "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
        "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
        "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude")),
    ("Revelation", ("Revelation",)),
)
# The nt facet's value for a reading of tradition the New Testament never uses.
NO_USE = "none"
_DIVISION = {book: key for key, _, books in DIVISIONS for book in books}
_BOOK = re.compile(r"^((?:[1-3] )?[A-Z][A-Za-z ]*?) \d")

# The grid's rows and columns, in the cards' words shortened to fit.
GRID_ROWS = (("divine", "Beyond any human agent"), ("opponents", "His opponents"),
             ("unwitting", "Someone with no thought of it"), ("followers", "His followers"),
             ("chosen", "Jesus, knowingly"), ("unfulfilled", "Still to come"))
GRID_COLS = (("known-before", "Read of the Messiah before Jesus"),
             ("partly", "Before, but not the part He fulfilled"),
             ("read-after", "Only in a later Jewish source"), ("veiled", "In no Jewish source"))

SERIF = "Georgia, 'Times New Roman', serif"
X_INK, X_MUTED, X_CARD, X_RULE = "#3b2f1e", "#6b5a3e", "#fffdf7", "#d9ccb0"
X_GOLD, X_GOLD_EDGE, X_GOLD_TINT = "#e8c46a", "#a67c3d", "#f6ecd0"
STREAM = {"law": "#8b1e1e", "prophets": "#2f4f7f", "writings": "#a67c3d", NO_USE: "#9c8f78"}
TIER_FILL = {1: X_GOLD, 2: "#f2dfa6", 3: X_GOLD_TINT}


def book_of(ref: str) -> str:
    m = _BOOK.match(ref)
    return m[1] if m else ref


def book_slug(book: str) -> str:
    return book.lower().replace(" ", "-")


def book_label(book: str) -> str:
    return "Psalms" if book == "Psalm" else book


def _label(x: float, y: float, text: str, n: int | None = None, size: float = 12.5,
           anchor: str = "start", extra: str = "") -> str:
    count = f' <tspan class="px-n" data-n="{n}">{n}</tspan>' if n is not None else ""
    return (f'<text class="px-label" x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'{extra}>{escape(text)}{count}</text>')


def _pick(pairs: str, units: list[str], label: str, inner: str) -> str:
    return (f'<g class="px-pick" data-pick="{escape(pairs)}" data-units="{" ".join(units)}" '
            f'data-label="{escape(label)}" tabindex="0" role="button" aria-pressed="false" '
            f'aria-label="{escape(label)}">{inner}<title>{escape(label)}</title></g>')


def _svg(w: float, h: float, title: str, body: str, cls: str) -> str:
    return (f'<svg class="px-svg {cls}" viewBox="0 0 {w:.0f} {h:.0f}" role="img" font-family="{SERIF}" '
            f'aria-label="{escape(title)}">{body}</svg>')



def _flow() -> str:
    """Each New Testament use, from the Old Testament book through its subject to the New Testament
    book, as a Sankey. A reading of tradition with no use flows to a last node of its own."""
    units = []
    for e in _ledger:
        ot = book_of(e["prophecy"])
        if ot not in _DIVISION:
            log.warning("prophecies: %s is in no division of the explorer", e["prophecy"])
        for nt in [book_of(u["ref"]) for u in e.get("uses", [])] or [NO_USE]:
            units.append({"e": e, "ot": ot, "div": _DIVISION.get(ot, "prophets"), "cat": e["category"],
                          "nt": nt, "tok": f'{e["id"]}@{book_slug(nt)}'})
    have = {c: {u[c] for u in units} for c in ("ot", "cat", "nt")}
    cols = {
        "ot": [[b for b in books if b in have["ot"]] for _, _, books in DIVISIONS],
        "cat": [[c for c in CATEGORIES if c in have["cat"]]],
        "nt": [[b for b in books if b in have["nt"]] for _, books in NT_GROUPS] + [[NO_USE] if NO_USE in have["nt"] else []],
    }
    cols = {c: [g for g in groups if g] for c, groups in cols.items()}
    W, TOP, AVAIL, NW, PAD, GAP, SLOT = 980, 48, 700, 12, 4, 14, 13
    X = {"ot": 190, "cat": 480, "nt": 790}
    val = {c: {} for c in cols}
    toks = {c: {} for c in cols}
    for u in units:
        for c in cols:
            val[c][u[c]] = val[c].get(u[c], 0) + 1
            toks[c].setdefault(u[c], []).append(u["tok"])
    total = len(units)
    pads = {c: (sum(map(len, g)) - 1) * PAD + (len(g) - 1) * (GAP - PAD) for c, g in cols.items()}
    k = min((AVAIL - p) / total for p in pads.values())
    pos, bottom = {c: {} for c in cols}, 0.0
    for c, groups in cols.items():
        y = TOP + (AVAIL - pads[c] - total * k) / 2
        for gi, keys in enumerate(groups):
            y += (GAP - PAD) if gi else 0
            for key in keys:
                h = val[c][key] * k
                pos[c][key] = {"y": y, "h": h, "out": y, "in": y}
                y += max(h, SLOT) + PAD
        bottom = max(bottom, y)
    order = {c: {key: i for i, key in enumerate(k_ for g in cols[c] for k_ in g)} for c in cols}
    div_order = {key: i for i, (key, _, _) in enumerate(DIVISIONS)} | {NO_USE: len(DIVISIONS)}

    def band(sc, s, tc, t, n, colour, tokens, title):
        w = n * k
        ys, yt = pos[sc][s]["out"] + w / 2, pos[tc][t]["in"] + w / 2
        pos[sc][s]["out"] += w
        pos[tc][t]["in"] += w
        sx, tx = X[sc] + NW, X[tc]
        xm = (sx + tx) / 2
        return (f'<path class="px-band" d="M{sx} {ys:.1f} C{xm} {ys:.1f} {xm} {yt:.1f} {tx} {yt:.1f}" '
                f'fill="none" stroke="{colour}" stroke-width="{max(w, 0.8):.2f}" data-units="{" ".join(tokens)}">'
                f'<title>{escape(title)}: {n} use{"s" if n > 1 else ""}</title></path>')

    left, right = {}, {}
    for u in units:
        left.setdefault((u["ot"], u["cat"]), []).append(u)
        right.setdefault((u["cat"], u["nt"], NO_USE if u["nt"] == NO_USE else u["div"]), []).append(u)
    bands = []
    for (ot, cat), us in sorted(left.items(), key=lambda i: (order["ot"][i[0][0]], order["cat"][i[0][1]])):
        bands.append(band("ot", ot, "cat", cat, len(us), STREAM[us[0]["div"]], [u["tok"] for u in us],
                          f"{book_label(ot)} to {CATEGORIES[cat]}"))
    for (cat, nt, div), us in sorted(right.items(), key=lambda i: (order["cat"][i[0][0]], order["nt"][i[0][1]],
                                                                   div_order[i[0][2]])):
        where = "no New Testament use" if nt == NO_USE else nt
        bands.append(band("cat", cat, "nt", nt, len(us), STREAM[div], [u["tok"] for u in us],
                          f"{CATEGORIES[cat]} to {where}"))

    nodes = []

    def node(c, key, text, pair, colour, side):
        p, n = pos[c][key], val[c][key]
        h = max(p["h"], 1.5)
        tx = X[c] - 8 if side == "left" else X[c] + NW + 8
        hit_x = tx - 160 if side == "left" else X[c]
        inner = (f'<rect x="{X[c]}" y="{p["y"]:.1f}" width="{NW}" height="{h:.1f}" fill="{colour}" class="px-mark"/>'
                 + _label(tx, p["y"] + h / 2 + 4, text, n, 14 if c == "cat" else 12.5,
                          "end" if side == "left" else "start")
                 + f'<rect x="{hit_x:.1f}" y="{p["y"] - 2:.1f}" width="{160 + NW + 8}" height="{max(h + 4, SLOT + 1):.1f}" fill="transparent"/>')
        nodes.append(_pick(pair, toks[c][key], f"{text}: {n} use{'s' if n > 1 else ''}", inner))

    for key, _, books in DIVISIONS:
        for b in books:
            if b in pos["ot"]:
                node("ot", b, book_label(b), f"book:{book_slug(b)}", STREAM[key], "left")
    for c in cols["cat"][0]:
        node("cat", c, CATEGORIES[c], f"category:{c}", X_GOLD, "right")
    for group in cols["nt"]:
        for b in group:
            node("nt", b, "Tradition only" if b == NO_USE else b, f"nt:{book_slug(b)}",
                 STREAM[NO_USE] if b == NO_USE else X_INK, "right")

    marks = []
    for key, name, books in DIVISIONS:
        present = [b for b in books if b in pos["ot"]]
        if not present:
            continue
        y0, y1 = pos["ot"][present[0]]["y"], pos["ot"][present[-1]]["y"] + pos["ot"][present[-1]]["h"]
        ym = (y0 + y1) / 2
        inner = (f'<path d="M40 {y0:.1f} h-6 V{y1:.1f} h6" fill="none" stroke="{STREAM[key]}" stroke-width="2"/>'
                 f'<text x="22" y="{ym:.1f}" font-size="13" font-style="italic" fill="{STREAM[key]}" '
                 f'text-anchor="middle" transform="rotate(-90 22 {ym:.1f})">{escape(name)}</text>'
                 f'<rect x="4" y="{y0:.1f}" width="40" height="{y1 - y0:.1f}" fill="transparent"/>')
        marks.append(_pick(f"division:{key}", [t for b in present for t in toks["ot"][b]], name, inner))
    for name, books in NT_GROUPS:
        present = [b for b in books if b in pos["nt"]]
        if len(present) < 2:
            continue
        y0, y1 = pos["nt"][present[0]]["y"], pos["nt"][present[-1]]["y"] + pos["nt"][present[-1]]["h"]
        ym = (y0 + y1) / 2
        marks.append(f'<path d="M{W - 40} {y0:.1f} h6 V{y1:.1f} h-6" fill="none" stroke="{X_MUTED}" stroke-width="1.5"/>'
                     f'<text x="{W - 22}" y="{ym:.1f}" font-size="13" font-style="italic" fill="{X_MUTED}" '
                     f'text-anchor="middle" transform="rotate(90 {W - 22} {ym:.1f})">{escape(name)}</text>')
    heads = "".join(
        f'<text x="{x}" y="24" font-size="11" fill="{X_MUTED}" text-anchor="{a}" letter-spacing="1.5">{t}</text>'
        for x, t, a in ((X["ot"] + NW, "OLD TESTAMENT", "end"), (X["cat"], "WHAT IT FORETOLD", "start"),
                        (X["nt"], "NEW TESTAMENT", "start")))
    body = (f'<rect width="{W}" height="{bottom + 16:.0f}" fill="{X_CARD}"/>{heads}<g class="px-bands">{"".join(bands)}</g>'
            + "".join(marks) + "".join(nodes))
    return _svg(W, bottom + 16, "Each New Testament use of a prophecy, from its Old Testament book through its "
                "subject to the New Testament book that uses it", body, "px-flow")


def _wheel() -> str:
    """The subjects clockwise through His life, as the home page's wheel: equal angles, each wedge's
    area its number of prophecies, its rings the tiers from the centre out."""
    W, H, CX, CY, HUB, R = 780, 560, 390, 280, 48, 200
    cats = [c for c in CATEGORIES if any(e["category"] == c for e in _ledger)]
    by = {c: [e for e in _ledger if e["category"] == c] for c in cats}
    most = max(len(v) for v in by.values())
    step, gap = 2 * math.pi / len(cats), 0.02

    def pt(a, r):
        return CX + r * math.sin(a), CY - r * math.cos(a)

    def wedge(a0, a1, r0, r1):
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pt(a0, r0), pt(a1, r0), pt(a1, r1), pt(a0, r1)
        return (f"M{x0:.1f} {y0:.1f} A{r0:.1f} {r0:.1f} 0 0 1 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} "
                f"A{r1:.1f} {r1:.1f} 0 0 0 {x3:.1f} {y3:.1f}Z")

    def radius(count):
        return math.sqrt(HUB * HUB + (R * R - HUB * HUB) * count / most)

    out = [f'<rect width="{W}" height="{H}" fill="{X_CARD}"/>',
           f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{X_RULE}" stroke-dasharray="2 4"/>']
    for i, c in enumerate(cats):
        entries = by[c]
        a0, a1 = i * step - step / 2 + gap, (i + 1) * step - step / 2 - gap
        rings, cum, r0 = [], 0, HUB
        for tier in (1, 2, 3):
            n = sum(e["tier"] == tier for e in entries)
            if not n:
                continue
            cum += n
            r1 = radius(cum)
            rings.append(f'<path class="px-mark" d="{wedge(a0, a1, r0, r1)}" fill="{TIER_FILL[tier]}" '
                         f'stroke="{X_GOLD_EDGE}"/>')
            r0 = r1
        mid = (a0 + a1) / 2
        lx, ly = pt(mid, R + 26)
        anchor = "middle" if abs(math.sin(mid)) < 0.2 else ("start" if math.sin(mid) > 0 else "end")
        inner = ("".join(rings) + _label(lx, ly, CATEGORIES[c], None, 14, anchor)
                 + f'<text class="px-label" x="{lx:.1f}" y="{ly + 16:.1f}" font-size="12" fill="{X_MUTED}" '
                   f'text-anchor="{anchor}"><tspan class="px-n" data-n="{len(entries)}">{len(entries)}</tspan></text>'
                 + f'<path d="{wedge(a0, a1, HUB, R + 10)}" fill="transparent"/>')
        tiers = ", ".join(f"{sum(e['tier'] == t for e in entries)} {w}" for t, w in
                          ((1, "fulfilled in Him or spoke of Him"), (2, "applied to Him"), (3, "tradition")))
        out.append(_pick(f"category:{c}", [e["id"] for e in entries],
                         f"{CATEGORIES[c]}: {len(entries)} prophecies ({tiers})", inner))
    ids = " ".join(e["id"] for e in _ledger)
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{HUB - 6}" fill="{X_CARD}" stroke="{X_GOLD_EDGE}"/>'
               f'<text class="px-total" data-units="{ids}" x="{CX}" y="{CY + 4}" font-size="26" fill="{X_INK}" '
               f'text-anchor="middle">{len(_ledger)}</text>'
               f'<text class="px-total-of" x="{CX}" y="{CY + 22}" font-size="11" fill="{X_MUTED}" '
               f'text-anchor="middle" data-all="prophecies" data-total="{len(_ledger)}">prophecies</text>')
    return _svg(W, H, "The prophecies by subject, clockwise through His life", "".join(out), "px-wheel")


def _grid() -> str:
    """Who brought each prophecy about, against whether it was read of the Messiah before Him."""
    L, T, CW, CH = 220, 96, 124, 64
    W, H = L + CW * len(GRID_COLS) + 56, T + CH * len(GRID_ROWS) + 20
    cells = {}
    for e in _ledger:
        cells.setdefault((e.get("control"), e.get("recognition")), []).append(e["id"])
    most = max(len(v) for v in cells.values())
    out = [f'<rect width="{W}" height="{H}" fill="{X_CARD}"/>',
           f'<rect x="{L}" y="{T}" width="{CW * len(GRID_COLS)}" height="{CH * 3}" fill="{X_GOLD_TINT}" opacity="0.6"/>']
    for j, (_, name) in enumerate(GRID_COLS):
        lines, line = [], ""
        for word in name.split():
            if len(f"{line} {word}".strip()) > 16:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        lines.append(line)
        for i, s in enumerate(lines):
            out.append(f'<text x="{L + CW * j + CW / 2:.0f}" y="{T - 12 - (len(lines) - 1 - i) * 15}" '
                       f'font-size="12.5" fill="{X_INK}" text-anchor="middle">{escape(s)}</text>')
    for i, (control, row) in enumerate(GRID_ROWS):
        y = T + CH * i
        out.append(f'<text x="{L - 12}" y="{y + CH / 2 + 4:.0f}" font-size="13.5" fill="{X_INK}" text-anchor="end">{escape(row)}</text>'
                   f'<line x1="{L}" x2="{L + CW * len(GRID_COLS)}" y1="{y}" y2="{y}" stroke="{X_RULE}"/>')
        for j, (recognition, col) in enumerate(GRID_COLS):
            ids = cells.get((control, recognition), [])
            if not ids:
                continue
            cx, cy = L + CW * j + CW / 2, y + CH / 2
            r = 4 + 24 * (len(ids) / most) ** 0.5
            inner = (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="{X_CARD}" stroke="{X_GOLD_EDGE}"/>'
                     f'<circle class="px-fill" cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="{X_GOLD}" '
                     f'stroke="{X_GOLD_EDGE}" data-most="{most}"/>'
                     f'<text class="px-label" x="{cx + r + 6:.1f}" y="{cy + 4:.0f}" font-size="12.5" fill="{X_MUTED}">'
                     f'<tspan class="px-n" data-n="{len(ids)}">{len(ids)}</tspan></text>'
                     f'<rect x="{L + CW * j}" y="{y}" width="{CW}" height="{CH}" fill="transparent"/>')
            out.append(_pick(f"control:{control} recognition:{recognition}", ids,
                             f"{row}; {col.lower()}: {len(ids)}", inner))
    bottom = T + CH * len(GRID_ROWS)
    out.append(f'<line x1="{L}" x2="{L + CW * len(GRID_COLS)}" y1="{bottom}" y2="{bottom}" stroke="{X_RULE}"/>'
               f'<text x="{L + CW * len(GRID_COLS) - 6}" y="{T + CH * 3 - 6}" font-size="11.5" font-style="italic" '
               f'fill="{X_MUTED}" text-anchor="end">no follower of His could have arranged these</text>')
    return _svg(W, H, "Who brought each prophecy about, against whether it was read of the Messiah before Him",
                "".join(out), "px-grid")


def _swatch(colour: str, text: str) -> str:
    return f'<span class="px-key"><i style="background:{colour}"></i>{escape(text)}</span>'


def _explorer() -> str:
    uses = sum(len(e.get("uses", [])) for e in _ledger)
    unused = sum(not e.get("uses") for e in _ledger)
    views = (
        ("flow", "Law, Prophets, Psalms",
         f"&ldquo;Everything must be fulfilled that is written about Me in the Law of Moses, the Prophets, and "
         f"the Psalms&rdquo; (Luke 24:44, BSB). Each of the {uses} New Testament uses of a prophecy, traced from "
         f"its Old Testament book, through what it foretold of Him, to the New Testament book that uses it; "
         f"the band's width is the number of uses. The {unused} readings of tradition the New Testament never "
         f"uses run to a last node of their own.",
         [_swatch(STREAM["law"], "The Law"), _swatch(STREAM["prophets"], "The Prophets"),
          _swatch(STREAM["writings"], "The Psalms and the Writings"),
          _swatch(STREAM[NO_USE], "Tradition only")], _flow()),
        ("wheel", "His life, in a circle",
         f"The {len(_ledger)} prophecies by subject, clockwise through His life, from His nature before the world "
         f"at the top round to His return beside it. Each wedge's area is its number of prophecies, its rings "
         f"how firmly the New Testament reads them of Him.",
         [_swatch(TIER_FILL[1], "Fulfilled in Him or spoke of Him"), _swatch(TIER_FILL[2], "Applied to Him"),
          _swatch(TIER_FILL[3], "A reading of tradition")], _wheel()),
        ("grid", "Could it be arranged?",
         "Who brought each prophecy about, against whether anyone read it of the Messiah before Him. The top "
         "three rows are the prophecies no follower of His could have brought about; the right-hand column, "
         "those no one was looking for.", [], _grid()),
    )
    tabs = "".join(f'<button type="button" role="tab" class="px-tab" data-view="{key}" '
                   f'aria-selected="{"true" if i == 0 else "false"}">{escape(name)}</button>'
                   for i, (key, name, *_rest) in enumerate(views))
    figures = []
    for key, name, caption, keys, svg in views:
        legend = f'<span class="px-keys">{"".join(keys)}</span>' if keys else ""
        figures.append(f'<figure class="px-view" data-view="{key}"><figcaption><b class="px-name">{escape(name)}</b> '
                       f'{caption}{legend}</figcaption><div class="px-frame">{svg}</div></figure>')
    return (f'<div class="px"><div class="px-tabs" role="tablist" aria-label="Pictures of the ledger" hidden>{tabs}</div>'
            f'{"".join(figures)}</div>')

def on_post_build(config):
    """assets/popups/prophecies.json: for each verse key ("Ps 22:18", English numbering, as the
    pop-up reads it), the entries it belongs to. `p` marks the prophecy's own text, `u` a New
    Testament use of it with the use's kind, `n` a prediction that begins in the New Testament."""
    if not _page_url:
        return
    rows = {r["id"]: r for r in json.loads((_data(config) / "prophecies-of-christ.json").read_text(encoding="utf-8"))["prophecies"]}
    nt_rows = {r["id"]: r for r in json.loads((_data(config) / "prophecies-of-christ.json").read_text(encoding="utf-8")).get("nt_prophecies", [])}
    verses: dict[str, list] = {}
    for e in _ledger:
        row = rows.get(e["id"])
        if not row:
            continue
        fulfilled_in = [u["ref"] for u in e.get("uses", []) if u["kind"] in ("fulfilment", "split", "type")]
        for key in row["verses"]:
            verses.setdefault(key, []).append([e["id"], e["prophecy"], "p", "; ".join(fulfilled_in)])
        for use in row["uses"]:
            for key in use["verses"]:
                verses.setdefault(key, []).append([e["id"], e["prophecy"], "u", USE_KINDS.get(use["kind"], use["kind"])])
    for e in _nt:
        for key in nt_rows.get(e["id"], {}).get("verses", []):
            verses.setdefault(key, []).append([e["id"], e["prophecy"], "n", e.get("fulfilment", "")])
    out = Path(config["site_dir"]) / "assets" / "popups" / "prophecies.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"u": _page_url[0], "v": verses}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")


def _chapter_section(book: int, chapter: int, files) -> str:
    """On a generated commentary chapter page: the prophecies of Christ whose text is in this chapter,
    and those the chapter's verses fulfil or use. Linked to their cards on the reference page."""
    hub = files.get_file_from_path(LEDGER_PAGE)
    if hub is None:
        return ""
    # The site is served at the root of its domain, so a site-absolute address needs no prefix.
    url = "/" + hub.url
    by_id = {e["id"]: e for e in _ledger}
    said, used = [], []
    for row in _computed.values():
        e = by_id.get(row["id"])
        if not e or "chapters" not in row:
            continue
        if [book, chapter] in row["chapters"]["prophecy"]:
            said.append(e)
        if [book, chapter] in row["chapters"]["uses"]:
            used.append(e)
    if not said and not used:
        return ""

    def item(e: dict) -> str:
        return (f'<li><a href="{url}#prophecy-{escape(e["id"])}">{escape(e["prophecy"])}</a> '
                f'{_text(e.get("predicts", ""))}</li>')

    out = ['<h2 id="prophecies-of-christ">Prophecies of Christ</h2>']
    if said:
        out.append(f"<p>Foretold in this chapter:</p><ul>{''.join(item(e) for e in said)}</ul>")
    if used:
        out.append(f"<p>Fulfilled or taken up in this chapter:</p><ul>{''.join(item(e) for e in used)}</ul>")
    return "\n".join(out)


# Fulfilments no witness on earth could see. They are real on the New Testament's word, but a chance
# floor counts events in public history, so each is left out of it, with its reason.
UNSEEN = {
    "sit-at-my-right-hand": "the session at God's right hand is in heaven (Acts 2:34-35; Hebrews 10:12)",
    "priest-forever-melchizedek": "the priesthood is exercised in the heavenly sanctuary (Hebrews 8:1-2)",
    "a-new-covenant": "the covenant is written on the heart (Jeremiah 31:33); the supper's words are its sign",
}
# Who brought it about, among the values that rule out arranging it: His followers and His own
# knowing acts are left out, since a critic says those could be staged.
UNARRANGED = {"divine", "opponents", "unwitting"}


def floor_moments() -> list[tuple[str, list[dict]]]:
    """The tier 1 prophecies fulfilled, at least in part, at a dated event, by no one who could have
    arranged it, grouped by that event: one trial per moment, so the prophecies one act fulfils are
    counted once. The chronology's anchor for the years of His death and resurrection groups the
    fulfilments it does not place more finely, which counts them once too."""
    moments: dict[str, list[dict]] = {}
    for e in _ledger:
        row = _computed.get(e["id"], {})
        if (e["tier"] == 1 and e["status"] in ("fulfilled", "partly") and e.get("control") in UNARRANGED
                and row.get("fulfilled") is not None and (row.get("years_ahead_traditional") or 0) > 0
                and e["id"] not in UNSEEN):
            moments.setdefault(e["event"], []).append(e)
    return sorted(moments.items(), key=lambda kv: _computed[kv[1][0]["id"]]["fulfilled"])


def _floor(ledger_url: str) -> str:
    moments = floor_moments()
    n = len(moments)
    items = "".join(
        f'<li>{", ".join(f"<a href=\"{ledger_url}#prophecy-{escape(e["id"])}\">{escape(e["prophecy"])}</a>" for e in group)}</li>'
        for _, group in moments)
    left_out = "".join(f"<li>{escape(i)}: {escape(r)}</li>" for i, r in UNSEEN.items())
    return f"""<div class="pc-floor" data-n="{n}">
<p><label for="pc-k">Give each moment a chance of one in <output class="pc-k-out">2</output>:</label>
<input id="pc-k" class="pc-k" type="range" min="2" max="10" step="1" value="2"></p>
<p class="pc-floor-result">With {n} independent moments at one chance in 2 each, the chance that all came to
pass is one in 2<sup>{n}</sup>, that is one in {2 ** n:,}.</p>
<details><summary>The {n} moments</summary><ol>{items}</ol></details>
<details><summary>Left out, because no witness could see them</summary><ul>{left_out}</ul></details>
</div>
<script type="module" src="/assets/js/prophecy-filter.js"></script>"""
