"""Add a printable group study sheet to every study that has a point and discussion questions.

One A4 sheet, printed double-sided, for a 40-minute small group or a study with a friend:

- side 1  the point, an opening question, the primary passage to read aloud (WEB), a "look closer"
          box to write in, the study's primary graphic (its comic, else its first drawn diagram)
          and the Study outline as "the study in brief".
- side 2  the discussion questions on a timed plan, with room to write, then the response: the
          Be Transformed think/attitude/do, the first memory verse and the study's prayer, and a QR
          code back to the full study.

Everything on the sheet is lifted from the rendered study, so it says nothing the study does not
and needs no checking of its own. The facet labels on the questions (develop-bible-study's
discussion-questions.md) place each one on the clock.

It runs at on_post_page, after the search plugin has indexed the page, so the sheet's copy of the
questions is not a second search hit for every study.
"""

from __future__ import annotations

import itertools
import json
import logging
import posixpath
import re
from html import escape
from pathlib import Path

import segno

log = logging.getLogger("mkdocs.hooks.study_sheet")

# The full names primary_passage uses, to the OSIS codes the pop-up verse files are named by
# (app/src/utils/scriptureRefs.js BOOKS).
_BOOKS = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num", "Deuteronomy": "Deut",
    "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth", "1 Samuel": "1Sam", "2 Samuel": "2Sam",
    "1 Kings": "1Kgs", "2 Kings": "2Kgs", "1 Chronicles": "1Chr", "2 Chronicles": "2Chr",
    "Ezra": "Ezra", "Nehemiah": "Neh", "Esther": "Esth", "Job": "Job", "Psalm": "Ps", "Psalms": "Ps",
    "Proverbs": "Prov", "Ecclesiastes": "Eccl", "Song of Songs": "Song", "Song of Solomon": "Song",
    "Isaiah": "Isa", "Jeremiah": "Jer", "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan",
    "Hosea": "Hos", "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah",
    "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag",
    "Zechariah": "Zech", "Malachi": "Mal", "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke",
    "John": "John", "Acts": "Acts", "Romans": "Rom", "1 Corinthians": "1Cor",
    "2 Corinthians": "2Cor", "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil",
    "Colossians": "Col", "1 Thessalonians": "1Thess", "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim", "2 Timothy": "2Tim", "Titus": "Titus", "Philemon": "Phlm",
    "Hebrews": "Heb", "James": "Jas", "1 Peter": "1Pet", "2 Peter": "2Pet", "1 John": "1John",
    "2 John": "2John", "3 John": "3John", "Jude": "Jude", "Revelation": "Rev",
}
_SINGLE_CHAPTER = {"Obad", "Phlm", "2John", "3John", "Jude"}
_REF = re.compile(r"^(?:(?P<book>(?:[123]\s)?\D+?)\s+)?(?P<c1>\d+)(?::(?P<v1>\d+))?(?:-(?:(?P<c2>\d+):)?(?P<v2>\d+))?$")

# (key, label, from minute, to minute). The widths of the plan bar on side 2 are these minutes.
_PLAN = (
    ("open", "Open", 0, 5),
    ("read", "Read", 5, 12),
    ("discover", "Discover", 12, 25),
    ("wrestle", "Wrestle", 25, 35),
    ("respond", "Respond", 35, 40),
)
_FACETS = {
    "the language": "discover",
    "the text in its context": "discover",
    "christ": "wrestle",
    "the hard part": "wrestle",
    "be transformed": "respond",
}

# More passage than side 1 holds at any size; the rest of the fitting is _FIT_SCRIPT's.
_MOST_WORDS = 900

# Fits side 1 to its page, which a word count cannot: the point, the opener and the outline all
# vary. Steps the passage type down, then moves trailing passages to "Also read", then trims verses
# from the end; and tightens the outline column, then drops its annotations, then the outline. Every size is in sheet
# millimetres, so a fit measured on the screen preview holds on paper. Runs on open and on print.
_FIT_SCRIPT = """<script>
function ssFit(details) {
  const sheet = details.querySelector(".ss-front"), main = sheet.querySelector(".ss-main");
  const side = sheet.querySelector(".ss-side"), read = sheet.querySelector(".ss-read");
  const also = sheet.querySelector(".ss-also"), passages = [...read.querySelectorAll(".ss-passage")];
  const over = (e) => e && e.scrollHeight > e.clientHeight + 1;
  sheet.querySelectorAll("[data-fit]").forEach((e) => { e.hidden = false; delete e.dataset.fit; });
  sheet.classList.remove("ss-dense", "ss-tight", "ss-titles", "ss-nobrief");
  const dropped = [];
  if (over(main)) sheet.classList.add("ss-dense");
  while (over(main) && passages.length > 1) {
    const p = passages.pop();
    p.hidden = true; p.dataset.fit = ""; dropped.unshift(p.dataset.passage);
  }
  const verses = passages.length ? [...passages[0].querySelectorAll(".ss-v")] : [];
  let from = null;
  while (over(main) && verses.length > 1) {
    const v = verses.pop();
    v.hidden = true; v.dataset.fit = ""; from = v.dataset.verse;
  }
  if (from) dropped.unshift(passages[0].dataset.passage + " from " + from);
  const rest = dropped.concat(also.dataset.also ? [also.dataset.also] : []);
  also.textContent = "Also read: " + rest.join("; ");
  also.hidden = !rest.length;
  if (over(side)) sheet.classList.add("ss-tight");
  if (over(side)) sheet.classList.add("ss-titles");
  if (over(side)) sheet.classList.add("ss-nobrief");
}
// Print follows html.ss-on, which only the reader sets, by clicking the summary or Print sheet:
// mkdocs-material opens every <details> when printing, so [open] cannot tell a sheet the reader
// opened from one Material opened. Safari keeps its default margins under the stylesheet's named
// @page study-sheet and shrinks the sheet to fit them, so an unnamed @page goes in with the class.
function ssOn(on) {
  document.documentElement.classList.toggle("ss-on", on);
  let s = document.getElementById("ss-page");
  if (on && !s) {
    s = document.head.appendChild(document.createElement("style"));
    s.id = "ss-page";
    s.textContent = "@page { size: A4 portrait; margin: 0; }";
  }
  if (!on && s) s.remove();
}
addEventListener("click", (e) => {
  const summary = e.target.closest?.("details.ss > summary");
  if (summary) ssOn(!summary.parentElement.open);
}, true);
addEventListener("toggle", (e) => {
  if (e.target.matches?.("details.ss") && e.target.open) document.fonts.ready.then(() => ssFit(e.target));
}, true);
</script>"""

# Material Design Icons "printer", the set mkdocs-material ships.
_JUMP = """<a href="#group-study-sheet" class="md-content__button md-icon ss-jump"
  title="Print the group study sheet" aria-label="Print the group study sheet"
  onclick="const d=document.getElementById('group-study-sheet');if(!d.open){d.open=true;ssOn(true)}">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M18 3H6v4h12m1 5a1 1 0 0 1-1-1 1 1 0 0 1 1-1 1 1 0 0 1 1 1 1 1 0 0 1-1 1m-3 7H8v-5h8m3-6H5a3 3 0 0 0-3 3v6h4v4h12v-4h4v-6a3 3 0 0 0-3-3Z"/></svg></a>"""

_NOTICE = "Scripture: WEB, public domain · ESV® © 2001 Crossway, used by permission"

_verses: dict[str, dict] = {}


def on_config(config):
    _verses.clear()
    return config


def on_post_page(output, page, config):
    start, end = output.find("<article"), output.find("</article>")
    if start < 0 or end < 0:
        return output
    article = output[start:end]
    point = re.search(r"<p><strong>In one sentence:</strong>\s*(.*?)</p>", article, re.DOTALL)
    questions = _items(_section(article, 2, "discussion-questions"), "ol")
    if not point or not questions:
        return output

    sheet = render_sheet(page, config, article, point[1], questions)
    after = re.search(r'<h2 id="discussion-questions".*?(?=<h2\b|$)', article, re.DOTALL)
    at = start + after.end()
    output = output[:at] + sheet + output[at:]
    # A leader decides to print before the group, from the top, and the sheet sits by the
    # questions it is built from, so the title carries a way down to it.
    top = output.find("<h1", start)
    if top < 0:
        top = output.index(">", start) + 1
    return output[:top] + _JUMP + output[top:]


def render_sheet(page, config, article: str, point: str, questions: list[str]) -> str:
    title = page.meta.get("title") or page.title
    graphic = _graphic(page, config, article)
    layout = graphic["shape"] if graphic else "none"
    passages = _passages(page.meta.get("primary_passage"), config)
    read = _read(passages)
    url = page.canonical_url

    side = ""
    if layout == "portrait":
        side = f'<img class="ss-graphic" src="{graphic["src"]}" alt="">'
    side += _brief(_section(article, 2, "study-outline"))
    wide = f'<img class="ss-graphic ss-graphic-wide" src="{graphic["src"]}" alt="">' if layout == "landscape" else ""

    front = f"""<section class="ss-sheet ss-front ss-{layout}" aria-label="Study sheet, side 1">
  <header class="ss-head">
    <span class="ss-kicker">Group study · 40 minutes</span>
    <h2>{escape(title)}</h2>
    <span class="ss-ref">{escape(str(page.meta.get("primary_passage") or ""))}</span>
  </header>
  <p class="ss-point"><b>The point</b> {_clean(point)}</p>
  <div class="ss-body">
    <div class="ss-main">
      <div class="ss-open">{_badge("open")}<p>{_opener(page.meta, title)}</p></div>
      <div class="ss-read"><span class="ss-h">{_badge("read")}Read it aloud <small>WEB</small></span>{read}</div>
      {wide}
      <div class="ss-look"><span class="ss-h">{_badge("discover")}Look closer <small>before you turn over</small></span>
        <div class="ss-look-rows"><div><b>What does it say?</b><i></i></div><div><b>What did it mean to them?</b><i></i></div><div><b>What does it mean for us?</b><i></i></div></div>
      </div>
    </div>
    {f'<aside class="ss-side">{side}</aside>' if side else ""}
  </div>
  <footer class="ss-foot"><span>Side 1 of 2 · print double-sided, flip on long edge</span><span>{_NOTICE}</span></footer>
</section>"""

    back = f"""<section class="ss-sheet ss-back" aria-label="Study sheet, side 2">
  <header class="ss-head ss-head-back"><h2>{escape(title)}</h2>{_plan()}</header>
  <div class="ss-questions">{_questions(questions)}</div>
  <div class="ss-respond">{_respond(article)}</div>
  <footer class="ss-foot ss-foot-back">
    <span class="ss-qr">{segno.make(url, error="m").svg_inline(border=0, omitsize=True, dark="#1d1b19")}</span>
    <span class="ss-url"><b>The whole study, with every verse a tap away</b>{escape(url)}</span>
    <span>Side 2 of 2 · {_NOTICE}</span>
  </footer>
</section>"""

    return f"""
<details class="ss" id="group-study-sheet" data-no-popups>
  <summary>Group study sheet <small>one A4 sheet, double-sided, for a 40-minute group</small></summary>
  <div class="ss-controls">
    <p>The point, the passage, the questions on a timed plan and the response, from this study.
    Print on both sides of one A4 sheet, flipping on the long edge. While this block is open,
    printing the page prints the sheet; close it to print the study.</p>
    <label><input type="checkbox" class="ss-opt-mono"> Black &amp; white <small>for a black-only printer</small></label>
    <button type="button" class="md-button md-button--primary"
      onclick="const d=this.closest('details');d.open=true;ssOn(true);ssFit(d);window.print()">Print sheet</button>
  </div>
  {front}
  {back}
  {_FIT_SCRIPT}
</details>
"""


def _section(article: str, level: int, anchor: str) -> str:
    """The HTML under a heading, up to the next heading of the same level or higher."""
    m = re.search(rf'<h{level} id="{anchor}".*?</h{level}>(.*?)(?=<h[1-{level}]\b|$)', article, re.DOTALL)
    return m[1] if m else ""


def _items(html: str, tag: str) -> list[str]:
    block = re.search(rf"<{tag}>(.*?)</{tag}>", html, re.DOTALL)
    return re.findall(r"<li>(.*?)</li>", block[1], re.DOTALL) if block else []


def _clean(html: str) -> str:
    """Inline HTML fit for paper: links lose their href (and the outline its anchors), footnote
    markers go."""
    html = re.sub(r'<sup id="fnref[^"]*".*?</sup>', "", html, flags=re.DOTALL)
    html = re.sub(r"</?a\b[^>]*>", "", html)
    return " ".join(html.split())


def _badge(key: str) -> str:
    _, label, a, b = next(p for p in _PLAN if p[0] == key)
    return f'<span class="ss-badge ss-badge-{key}" title="{label}">{a}–{b}<small>min</small></span>'


def _opener(meta: dict, title: str) -> str:
    asked = meta.get("questions") or []
    if asked:
        return f"Ask: <q>{escape(asked[0])}</q> Hear a few answers before anyone reads."
    short = title.split(":")[0].strip()
    return f"Ask: what comes to mind when you hear <q>{escape(short)}</q>? Hear a few answers before anyone reads."


def _graphic(page, config, article: str) -> dict | None:
    """The study's primary graphic: its comic, else the first drawn (SVG) image on the page."""
    srcs = re.findall(r'<img\b[^>]*\bsrc="([^"]+\.svg)"', article)
    srcs = [s for s in srcs if "/assets/img/" in "/" + s and "favicon" not in s]
    src = next((s for s in srcs if "/comics/" in s), srcs[0] if srcs else None)
    if not src:
        return None
    path = Path(config.docs_dir) / posixpath.normpath(posixpath.join(page.url, src))
    try:
        box = re.search(r'viewBox="([\d.\s-]+)"', path.read_text(encoding="utf-8")[:2000])
    except FileNotFoundError:
        log.warning("study_sheet: %s has no file at %s", page.file.src_uri, path)
        return None
    w, h = (float(n) for n in box[1].split()[2:4]) if box else (1, 1)
    return {"src": src, "shape": "landscape" if w / h > 1.1 else "portrait"}


def _passages(value, config) -> list[dict]:
    out, name = [], None
    for part in [p.strip() for p in str(value or "").split(";") if p.strip()]:
        m = _REF.match(part)
        if not m:
            log.warning("study_sheet: cannot read the reference %r", part)
            continue
        # A bare "11:15-19" continues the book before it, and is printed with that book's name.
        name = m["book"].strip() if m["book"] else name
        book = _BOOKS.get(name or "")
        if not book:
            log.warning("study_sheet: no book in %r", part)
            continue
        verses = _range(_chapters(book, config), book, m)
        out.append({"ref": part if m["book"] else f"{name} {part}", "verses": verses})
    return out


def _chapters(book: str, config) -> dict:
    if book not in _verses:
        path = Path(config.docs_dir) / "assets" / "popups" / "verses" / f"{book}.json"
        _verses[book] = json.loads(path.read_text(encoding="utf-8"))["v"]
    return _verses[book]


def _range(chapters: dict, book: str, m: re.Match) -> list[tuple[int, int, str]]:
    c1, v1, c2, v2 = (int(m[k]) if m[k] else None for k in ("c1", "v1", "c2", "v2"))
    if book in _SINGLE_CHAPTER and v1 is None:
        c1, v1, v2, c2 = 1, c1, v2 or c1, None
    if v1 is None:
        first, last = (c1, 1), (v2 or c1, 999)  # "Psalm 23", "Proverbs 1-9": whole chapters
    else:
        first, last = (c1, v1), (c2 or c1, v2 or v1)
    return [(c, v, t)
            for c in range(first[0], last[0] + 1)
            for v, t in sorted(((int(v), t) for v, t in chapters.get(str(c), {}).items()))
            if first <= (c, v) <= last]


def _read(passages: list[dict]) -> str:
    """Every passage, each verse in its own span, so _FIT_SCRIPT can trim from the end to what fits.
    Past _MOST_WORDS nothing could fit, so a whole-chapter passage is cut here rather than shipped."""
    body, words, also = "", 0, []
    for p in passages:
        verses = []
        for c, v, t in p["verses"]:
            words += len(t.split())
            if words > _MOST_WORDS:
                also.append(f'{p["ref"]} from {c}:{v}' if verses else p["ref"])
                break
            verses.append((c, v, t))
        if not verses:
            continue
        chapters = {c for c, _, _ in verses}
        text = " ".join(
            f'<span class="ss-v" data-verse="{c}:{v}"><sup>{f"{c}:{v}" if len(chapters) > 1 and (v == 1 or (c, v) == verses[0][:2]) else v}</sup>{escape(t)}</span>'
            for c, v, t in verses)
        body += f'<p class="ss-passage" data-passage="{escape(p["ref"])}"><b>{escape(p["ref"])}</b> {text}</p>'
    return body + f'<p class="ss-also" data-also="{escape("; ".join(also))}"{"" if also else " hidden"}>Also read: {escape("; ".join(also))}</p>'


def _brief(outline_html: str) -> str:
    # Each outline line opens with a link to its section; the link text is the section's name.
    items = [_clean(re.sub(r"^\s*<a\b[^>]*>(.*?)</a>(.*)", r"<b>\1</b><span>\2</span>", i, flags=re.DOTALL))
             for i in _items(outline_html, "ul")]
    items = [i for i in items if not i.startswith("<b>Discussion questions")]
    if not items:
        return ""
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<div class="ss-brief"><span class="ss-h">The study in brief</span><ol>{lis}</ol></div>'


def _plan() -> str:
    cells = "".join(f'<span style="flex:{b - a}"><b>{label}</b>{a}–{b}</span>'
                    for k, label, a, b in _PLAN)
    return f'<div class="ss-plan" aria-label="Timed plan, in minutes">{cells}</div>'


def _questions(questions: list[str]) -> str:
    groups: dict[str, list[str]] = {"discover": [], "wrestle": [], "respond": []}
    segment = "discover"
    for q in questions:
        label = re.match(r"\s*<strong>(.*?)\.?</strong>", q)
        segment = _FACETS.get(label[1].strip().rstrip(".").lower(), segment) if label else segment
        groups[segment].append(_clean(q))
    out, number = "", 0
    for key, label, a, b in _PLAN[2:]:
        if not groups[key]:
            continue
        qs = ""
        for q in groups[key]:
            number += 1
            qs += f'<div class="ss-q"><p><span class="ss-n">{number}</span>{q}</p><i></i></div>'
        out += f'<div class="ss-group ss-group-{key}"><span class="ss-h">{_badge(key)}{label}</span>{qs}</div>'
    return out


def _respond(article: str) -> str:
    transform = _section(article, 3, "be-transformed")
    tad = "".join(f"<li>{_clean(i)}</li>" for i in _items(transform, "ul"))
    # Markdown merges consecutive quote blocks into one, so the verses are told apart by their
    # "✝️ Reference (TRANSLATION)" lines. One verse to learn this week: the first.
    paragraphs = re.findall(r"<p>(.*?)</p>", _section(article, 3, "memory-verses"), re.DOTALL)
    memory = ""
    if paragraphs and paragraphs[0].startswith("✝"):
        ref = paragraphs[0].lstrip("✝️ ")
        text = "".join(f"<p>{re.sub(r'^\s*\d+\s+', '', p)}</p>"
                       for p in itertools.takewhile(lambda p: not p.startswith("✝"), paragraphs[1:]))
        memory = f'<div class="ss-memory"><span class="ss-h">Memory verse</span>{_clean(text)}<cite>{_clean(ref)}</cite></div>'
    prayer = _section(article, 3, "prayer").strip()
    prayer = f'<div class="ss-prayer"><span class="ss-h">Pray together</span>{_clean(prayer)}</div>' if prayer else ""
    tad = f'<div class="ss-tad"><span class="ss-h">This week</span><ul>{tad}</ul></div>' if tad else ""
    return tad + memory + prayer
