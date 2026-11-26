"""Render the reference of the Old Testament's prophecies of Christ wherever a page carries a marker.

- `<!-- prophecies-of-christ: measures -->`        the counts by subject, as a table
- `<!-- prophecies-of-christ: dated -->`           one sentence: how many are tied to a dated event,
                                                   and how many were written and copied before it
- `<!-- prophecies-of-christ: category <name> -->` the entries of one category, as cards
- `<!-- prophecies-of-christ: nt -->`              the prophecies that begin in the New Testament

The ledger is docs/data/prophecies-of-christ.toml. What needs a Bible database (the Qumran copies)
or the authorship table and the chronology (the years) comes from docs/data/prophecies-of-christ.json,
which references/build/export_prophecies.py writes; utils/check_prophecies.py fails while it is
stale, so the counts here are the ledger's. Every count on the page is written here, never by hand.

Each card carries id="prophecy-<id>", so a study links to one entry as
`../jesus/prophecies-of-christ.md#prophecy-<id>`. References are plain text so the verse pop-up
finds them. A note's research leads (from "lead:" on) are the ledger's working notes, unchecked,
and are left off the page. The styles are in assets/stylesheets/prophecies.css.
"""

from __future__ import annotations

import json
import logging
import re
import tomllib
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.prophecies")

_MARKER = re.compile(r"<!--\s*prophecies-of-christ:\s*(measures|dated|nt|category\s+[\w-]+)\s*-->")

# The labels utils/build_jesus_graphics.py's chart uses, so the page and the chart agree.
CATEGORIES = {
    "nature": "Nature", "lineage": "Lineage", "birth": "Birth", "childhood": "Childhood",
    "forerunner": "Forerunner", "ministry": "Ministry", "passion": "Passion",
    "resurrection": "Resurrection", "redemption": "Redemption", "office": "Prophet, priest, king",
    "future": "Future",
}
TIERS = {
    1: "The New Testament says it was fulfilled in Him",
    2: "The New Testament applies it to Him",
    3: "A reading of tradition; the New Testament at most alludes",
}
STATUS = {"fulfilled": "Fulfilled", "partly": "Partly fulfilled", "future": "Still to come"}
USE_KINDS = {
    "fulfilment": "fulfilled", "split": "fulfilled in part", "type": "a type",
    "application": "applied", "imagery": "its imagery", "allusion": "an allusion",
}
USE_TEXTS = {
    "mt": "follows the Hebrew", "lxx": "follows the Septuagint", "both": "the Hebrew and the Septuagint agree",
    "neither": "follows neither text", "none": "",
}
RECOGNITION = {
    "known-before": "Read of the Messiah before Jesus",
    "partly": "Read of the Messiah in part before Jesus",
    "read-after": "Read of the Messiah only in a later Jewish source",
    "veiled": "Read of the Messiah by no one, before Jesus or since",
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

_ledger: list[dict] = []
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


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    return _MARKER.sub(lambda m: _render(m[1], page.file.src_uri), html)


def _render(what: str, src: str) -> str:
    if what == "measures":
        return _measures()
    if what == "dated":
        return _dated()
    if what == "nt":
        return f'<div class="pc-group">{"".join(_nt_card(e) for e in _nt)}</div>'
    category = what.split()[1]
    entries = [e for e in _ledger if e["category"] == category]
    if not entries:
        log.warning("prophecies: %s asks for category %r, which has no entries", src, category)
    return f'<div class="pc-group">{"".join(_card(e) for e in entries)}</div>'


def _text(s: str) -> str:
    """Escaped, with Hebrew in its own right-to-left span, as the site's rule has it (never bold)."""
    return _HEBREW.sub(lambda m: f'<span dir="rtl" lang="he">{m[0]}</span>', escape(s))


def year_label(y: int) -> str:
    return f"{-y} BC" if y < 0 else f"AD {y}"


def _public(note: str) -> str:
    """The ledger's checked observations; a research lead, from "lead:" on, is not yet checked."""
    return note.split("lead:")[0].strip()


def _years(row: dict) -> str:
    if row.get("fulfilled") is None:
        return ""
    trad, crit = row["written_traditional"], row["written_critical"]
    written = f"Written by {year_label(trad)}"
    if crit != trad:
        written += f" ({year_label(crit)} on the critics' dates)"
    ahead = f"{row['years_ahead_traditional']:,} years ahead"
    if crit != trad:
        ahead += f", {row['years_ahead_critical']:,} on theirs"
    return f"{written}; came to pass {year_label(row['fulfilled'])}: {ahead}."


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
    note = f'<span class="pc-use-note">{_text(_public(use["note"]))}</span>' if use.get("note") and _public(use["note"]) else ""
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
    notes = _public(e.get("notes", ""))
    notes = f'<details class="pc-notes"><summary>Notes</summary><p>{_text(notes)}</p></details>' if notes else ""
    form = ' <span class="pc-form">a type</span>' if e.get("form") == "type" else ""
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}">
  <header class="pc-head"><b class="pc-ref">{escape(e['prophecy'])}</b>{form}
    <span class="pc-status">{escape(STATUS[e['status']])}</span></header>
  <p class="pc-says">{_text(e.get('predicts', ''))}</p>
  <p class="pc-tier">{escape(TIERS[e['tier']])}</p>
  <ul class="pc-uses">{uses}</ul>
  {first}{split}
  <ul class="pc-meta">{"".join(f"<li>{escape(m)}</li>" for m in meta)}</ul>
  {notes}
</article>"""


def _nt_card(e: dict) -> str:
    meta = [m for m in (RECORDED.get(e.get("recorded", ""), ""), CONTROL.get(e.get("control", ""), "")) if m]
    fulfilment = f'<p class="pc-says"><b>Fulfilled</b> {escape(e["fulfilment"])}</p>' if e.get("fulfilment") else ""
    notes = _public(e.get("notes", ""))
    notes = f'<details class="pc-notes"><summary>Notes</summary><p>{_text(notes)}</p></details>' if notes else ""
    return f"""<article class="pc-entry pc-{escape(e['status'])}" id="prophecy-{escape(e['id'])}">
  <header class="pc-head"><b class="pc-ref">{escape(e['prophecy'])}</b>
    <span class="pc-speaker">{escape(SPEAKERS[e['speaker']])}</span>
    <span class="pc-status">{escape(STATUS[e['status']])}</span></header>
  <p class="pc-says">{_text(e['predicts'])}</p>
  {fulfilment}
  <ul class="pc-meta">{"".join(f"<li>{escape(m)}</li>" for m in meta)}</ul>
  {notes}
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
    before_crit = sum(r["years_ahead_critical"] > 0 for r in rows)
    translated = sum(r["translated_before"] for r in rows)
    manuscript = sum(r["manuscript_before"] and "1Qisaa" in r["qumran"] for r in rows)
    qumran = sum(bool(r["qumran"]) for r in _computed.values())
    return (f'<p class="pc-dated">{len(rows)} of the {len(_ledger)} prophecies are tied to an event this '
            f"site's chronology dates. {before_crit} of the {len(rows)} were written before it, even on "
            f"the latest date critical scholarship gives them, and {translated} were already read in "
            f"Greek by about 132 BC, on the witness of Sirach's prologue. {manuscript} survive in the "
            f"Great Isaiah Scroll, a manuscript you can see that is older than the event. The Hebrew of "
            f"{qumran} of all {len(_ledger)} is among the Dead Sea Scrolls.</p>")
