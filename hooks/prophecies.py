"""Render the reference of the Old Testament's prophecies of Christ wherever a page carries a marker.

- `<!-- prophecies-of-christ: measures -->`        the counts by subject, as a table
- `<!-- prophecies-of-christ: dated -->`           one sentence: how many are tied to a dated event,
                                                   and how many were written and copied before it
- `<!-- prophecies-of-christ: category <name> -->` the entries of one category, as cards
- `<!-- prophecies-of-christ: nt -->`              the prophecies that begin in the New Testament
- `<!-- prophecies-of-christ: floor -->`           the chance floor a reader sets: the prophecies no
                                                   one could have arranged, one trial per moment,
                                                   and a slider for the chance given each
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
import re
import tomllib
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.prophecies")

_MARKER = re.compile(r"<!--\s*prophecies-of-christ:\s*(measures|dated|nt|filter|floor|category\s+[\w-]+)\s*-->")

# The labels utils/build_jesus_graphics.py's chart uses, so the page and the chart agree.
CATEGORIES = {
    "nature": "Nature", "lineage": "Lineage", "birth": "Birth", "childhood": "Childhood",
    "forerunner": "Forerunner", "ministry": "Ministry", "passion": "Passion",
    "resurrection": "Resurrection", "redemption": "Redemption", "office": "Prophet, priest, king",
    "future": "Future",
}
TIERS = {
    1: "The New Testament says it was fulfilled in Him, spoke of Him, or was shaped to point to Him",
    2: "The New Testament applies it to Him",
    3: "A reading of tradition; the New Testament at most alludes",
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
    "known-before": "Read of the Messiah before Jesus",
    "partly": "Read of the Messiah before Jesus, but not of the part He fulfilled",
    "read-after": "Read of the Messiah only in a later Jewish source",
    "veiled": "Read of the Messiah in no Jewish source, before Jesus or since",
    "unassessed": "Not yet assessed",
}
CONTROL = {
    "divine": "Beyond any human agent",
    "opponents": "Brought about by His opponents",
    "unwitting": "Brought about by someone with no thought of it",
    "followers": "Brought about by His followers",
    "chosen": "Jesus fulfilled it knowingly",
    "unfulfilled": "",
}
SPEAKERS = {"jesus": "Jesus", "angel": "An angel", "apostle": "An apostle", "revelation": "Revelation"}
RECORDED = {
    "before": "Written down before it came to pass",
    "after": "Written down after it came to pass",
    "contested": "Whether it was written down before is contested",
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
    line = (f"Written by {year_label(trad)}; came to pass {year_label(row['fulfilled'])}: "
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


def _card(e: dict) -> str:
    row = _computed.get(e["id"], {})
    meta = [m for m in (_years(row), _copy(row), RECOGNITION.get(e.get("recognition", "unassessed"), ""),
                        CONTROL.get(e.get("control", ""), "")) if m]
    uses = "".join(_use(u) for u in e.get("uses", []))
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
    form = ' <span class="pc-form">a type</span>' if e.get("form") == "type" else ""
    facets = " ".join(f'data-{k}="{escape(" ".join(v))}"' for k, v in _facets(e).items())
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}" {facets}>
  <header class="pc-head"><b class="pc-ref">{escape(e['prophecy'])}</b>{form}
    <span class="pc-status">{escape(STATUS[e['status']])}</span></header>
  <p class="pc-says">{_text(e.get('predicts', ''))}</p>
  <p class="pc-tier">{escape(TIERS[e['tier']])}</p>
  <ul class="pc-uses">{uses}</ul>
  {first}{split}
  <ul class="pc-meta">{"".join(f"<li>{escape(m)}</li>" for m in meta)}</ul>
</article>"""


def _nt_card(e: dict) -> str:
    meta = [m for m in (RECORDED.get(e.get("recorded", ""), ""), CONTROL.get(e.get("control", ""), "")) if m]
    fulfilment = f'<p class="pc-says"><b>Fulfilled</b> {escape(e["fulfilment"])}</p>' if e.get("fulfilment") else ""
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}">
  <header class="pc-head"><b class="pc-ref">{escape(e['prophecy'])}</b>
    <span class="pc-speaker">{escape(SPEAKERS[e['speaker']])}</span>
    <span class="pc-status">{escape(STATUS[e['status']])}</span></header>
  <p class="pc-says">{_text(e['predicts'])}</p>
  {fulfilment}
  <ul class="pc-meta">{"".join(f"<li>{escape(m)}</li>" for m in meta)}</ul>
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
