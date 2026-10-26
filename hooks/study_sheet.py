"""Add a printable group study sheet to every study that has a point and discussion questions.

Four A4 pages, two sheets printed double-sided, for a 40-minute small group or a study with a
friend, set at 12 pt for older eyes:

- page 1  the point, an opening question, the primary passage to read aloud (WEB) and a "look
          closer" box to write in.
- page 2  the study's primary graphic (its comic, else its first drawn diagram) as large as the
          page allows, and the Study outline as "the study in brief".
- page 3  the discussion questions under the Study outline's steps, each step with its share of the
          minutes, the same room to write under each (by facet, for a study with no outline).
- page 4  Be transformed (its question, then think/attitude/do), the first memory verse and the
          study's prayer, room for notes, and a QR code back to the full study.

Or, for a study with a Study outline, one sheet double-sided ("Two pages"), for a leader who does
not know the study well: Open, Read it aloud, then each outline step (its note and key verses)
followed straight away by the questions that belong to it, then Be transformed, and the point to
finish on, poured across the two pages. A question belongs to the step whose section cites the
same verses.

Everything on the sheet is lifted from the rendered study, so it says nothing the study does not
and needs no checking of its own. The facet labels on the questions (develop-bible-study's
discussion-questions.md) mark Be transformed, which closes the sheet, and place the rest on the
clock where a study has no outline to group them by.

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

# (key, label, from minute, to minute): the badges' times on pages 1 and 3.
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

# More passage than page 1 holds at 12 pt; the rest of the fitting is _FIT_SCRIPT's.
_MOST_WORDS = 500

# Fits page 1 to its page, which a word count cannot: the point, the opener and the passage all
# vary, and the type never shrinks below 12 pt to make room. Moves trailing passages to "Also read",
# then trims verses from the end; on page 2, drops the outline's annotations, then the outline.
# Every size is in sheet millimetres, so a fit measured on the screen preview holds on paper. Runs
# on open and on print.
_FIT_SCRIPT = """<script>
function ssFit(details) {
  const p1 = details.querySelector(".ss-p1"), main = p1.querySelector(".ss-main");
  const p2 = details.querySelector(".ss-p2"), brief = p2.querySelector(".ss-brief");
  const read = p1.querySelector(".ss-read"), also = p1.querySelector(".ss-also");
  const passages = [...read.querySelectorAll(".ss-passage")];
  const over = (e) => e && e.scrollHeight > e.clientHeight + 1;
  details.querySelectorAll("[data-fit]").forEach((e) => { e.hidden = false; delete e.dataset.fit; });
  p2.classList.remove("ss-titles", "ss-nobrief");
  const dropped = [];
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
  // The hook's own cut ("John 4:1-42 from 4:30") gives way to the fit's, which starts earlier.
  const passage = (e) => e.split(" from ")[0], fitted = new Set(dropped.map(passage));
  const cut = also.dataset.also ? also.dataset.also.split("; ") : [];
  const rest = dropped.concat(cut.filter((e) => !fitted.has(passage(e))));
  also.textContent = "Also read: " + rest.join("; ");
  also.hidden = !rest.length;
  if (over(brief)) p2.classList.add("ss-titles");
  if (over(brief)) p2.classList.add("ss-nobrief");
  // Page 3 closes up its gaps, then drops the steps that have no questions; page 4 gives up its
  // notes, then Be transformed's answer space drops to one line.
  const p3 = details.querySelector(".ss-p3"), p4 = details.querySelector(".ss-p4");
  p3.classList.remove("ss-snug", "ss-noempty");
  p4.classList.remove("ss-nonotes", "ss-tight");
  if (over(p3.querySelector(".ss-questions"))) p3.classList.add("ss-snug");
  if (over(p3.querySelector(".ss-questions"))) p3.classList.add("ss-noempty");
  const foot = p4.querySelector(".ss-foot");
  const low = () => [...p4.children].some((e) => e !== foot && e.getBoundingClientRect().bottom > foot.getBoundingClientRect().top + 1);
  if (low()) p4.classList.add("ss-nonotes");
  if (low()) p4.classList.add("ss-tight");
  ssFlow(details);
}
// The two-page sheet is one run of blocks poured across two pages. Answer spaces start at two
// lines; whatever does not fit page 1 moves to page 2, and a heading moves with the question under
// it. If page 2 overflows, the key verses go, then the QR code, then the gaps between blocks close
// up, then the step notes (which a leader new to the study leans on most), then the answer spaces
// drop to one line. What room is left is shared out: every answer on both pages gets
// the same extra height, in sheet millimetres so the fit holds on paper.
function ssFlow(details) {
  const t1 = details.querySelector(".ss-t1"), t2 = details.querySelector(".ss-t2");
  if (!t1 || !t1.offsetParent) return;
  const f1 = t1.querySelector(".ss-flow"), f2 = t2.querySelector(".ss-flow");
  const answers = [...details.querySelectorAll(".ss-two .ss-q i")];
  const used = (f) => f.lastElementChild ? f.lastElementChild.getBoundingClientRect().bottom - f.getBoundingClientRect().top : 0;
  const fits = (f) => used(f) <= f.clientHeight + 1;
  const steps = ["ss-nokeys", "ss-noqr", "ss-snug", "ss-titles", "ss-tight"];
  const pour = (on) => {
    [t1, t2].forEach((t) => steps.forEach((c) => t.classList.toggle(c, on.includes(c))));
    f1.append(...f2.children);
    while (!fits(f1) && f1.children.length > 1) f2.prepend(f1.lastElementChild);
    while (f1.children.length > 1 && f1.lastElementChild.hasAttribute("data-keep")) f2.prepend(f1.lastElementChild);
    return fits(f2);
  };
  answers.forEach((i) => { i.style.height = ""; });
  let on = [];
  while (!pour(on) && on.length < steps.length) on = steps.slice(0, on.length + 1);
  // A later step can make room for an earlier one: put back whatever still fits.
  for (const c of on.slice(0, -1)) {
    const fewer = on.filter((x) => x !== c);
    if (pour(fewer)) on = fewer;
  }
  pour(on);
  const mm = t1.getBoundingClientRect().width / 210;
  const spare = [f1, f2].map((f) => {
    const n = f.querySelectorAll(".ss-q i").length;
    return n ? (f.clientHeight - used(f)) / n : Infinity;
  });
  const extra = Math.max(0, Math.min(...spare));
  if (!isFinite(extra)) return;
  answers.forEach((i) => { i.style.height = `calc(${(i.getBoundingClientRect().height + extra) / mm} * var(--mm))`; });
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
  if (!e.target.matches?.("details.ss") || !e.target.open) return;
  const two = e.target.querySelector(".ss-opt-two");
  try { if (two && localStorage.getItem("ss-two") === "1") two.checked = true; } catch {}
  document.fonts.ready.then(() => ssFit(e.target));
}, true);
// A hidden set measures nothing, so the newly shown one is fitted when the reader switches.
addEventListener("change", (e) => {
  if (!e.target.matches?.(".ss-opt-two")) return;
  try { localStorage.setItem("ss-two", e.target.checked ? "1" : "0"); } catch {}
  ssFit(e.target.closest("details.ss"));
}, true);
</script>"""

# Material Design Icons "printer", the set mkdocs-material ships.
_JUMP = """<a href="#group-study-sheet" class="md-content__button md-icon ss-jump"
  title="Print the group study sheet" aria-label="Print the group study sheet"
  onclick="const d=document.getElementById('group-study-sheet');if(!d.open){d.open=true;ssOn(true)}">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M18 3H6v4h12m1 5a1 1 0 0 1-1-1 1 1 0 0 1 1-1 1 1 0 0 1 1 1 1 1 0 0 1-1 1m-3 7H8v-5h8m3-6H5a3 3 0 0 0-3 3v6h4v4h12v-4h4v-6a3 3 0 0 0-3-3Z"/></svg></a>"""

_BOOK_NAMES = "|".join(sorted(map(re.escape, _BOOKS), key=len, reverse=True))
# A reference with or without its book ("John 4:13", "4:13"), or a whole chapter ("Matthew 24").
_SCAN = re.compile(rf"(?:\b({_BOOK_NAMES})\s+)?(?<![\d:])(\d+)(?::(\d+)(?:[-–](\d+)(?![\d:]))?)?(?![\d:])")

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
    read = _read(_passages(page.meta.get("primary_passage"), config))
    url = page.canonical_url

    head = f'<header class="ss-head ss-head-back"><h2>{escape(title)}</h2></header>'

    def foot(n: int) -> str:
        return f"""<footer class="ss-foot"><span>Page {n} of 4 · print double-sided, flip on long edge</span><span>{_NOTICE}</span></footer>"""

    p1 = f"""<section class="ss-sheet ss-p1" aria-label="Study sheet, page 1">
  <header class="ss-head">
    <span class="ss-kicker">Group study · 40 minutes</span>
    <h2>{escape(title)}</h2>
    <span class="ss-ref">{escape(str(page.meta.get("primary_passage") or ""))}</span>
  </header>
  <p class="ss-point"><b>The point</b> {_clean(point)}</p>
  <div class="ss-main">
    <div class="ss-open">{_badge("open")}<p>{_opener(page.meta, title)}</p></div>
    <div class="ss-read"><span class="ss-h">{_badge("read")}Read it aloud <small>WEB</small></span>{read}</div>
    <div class="ss-look"><span class="ss-h">{_badge("discover")}Look closer</span>
      <div class="ss-look-rows"><div><b>What does it say?</b><i></i></div><div><b>What did it mean to them?</b><i></i></div><div><b>What does it mean for us?</b><i></i></div></div>
    </div>
  </div>
  {foot(1)}
</section>"""

    picture = f'<img class="ss-graphic" src="{graphic["src"]}" alt="">' if graphic else ""
    notes = '<div class="ss-notes"><span class="ss-h">Notes</span><i></i></div>'
    p2 = f"""<section class="ss-sheet ss-p2 ss-{layout}" aria-label="Study sheet, page 2">
  {head}
  <div class="ss-p2-body">{picture}{_brief(_section(article, 2, "study-outline"))}{notes if not graphic else ""}</div>
  {foot(2)}
</section>"""

    asked = [q for segment, q in _segments(questions) if segment != "respond"]
    respond = [q for segment, q in _segments(questions) if segment == "respond"]
    plan = _steps(page, article, questions)
    p3 = f"""<section class="ss-sheet ss-p3" aria-label="Study sheet, page 3">
  {head}
  <div class="ss-questions">{_by_step(*plan) if plan else _questions(asked)}</div>
  {foot(3)}
</section>"""

    qr = f"""<span class="ss-qr">{segno.make(url, error="m").svg_inline(border=0, omitsize=True, dark="#1d1b19")}</span>
    <span class="ss-url"><b>The whole study, with every verse a tap away</b>{escape(url)}</span>"""
    p4 = f"""<section class="ss-sheet ss-p4" aria-label="Study sheet, page 4">
  {head}
  <div class="ss-respond">{_respond(article, respond, len(asked) + 1)}</div>
  {notes}
  <div class="ss-link">{qr}</div>
  {foot(4)}
</section>"""

    two = _two_pages(page, article, point, plan, respond, title, qr) if plan else ""
    option = ('<label><input type="checkbox" class="ss-opt-two"> Two pages <small>one sheet: each '
              'step of the study with its questions</small></label>') if two else ""
    return f"""
<details class="ss" id="group-study-sheet" data-no-popups>
  <summary>Group study sheet <small>for a 40-minute group: two A4 sheets, or one with the guided path</small></summary>
  <div class="ss-controls">
    <p>The point, the passage, the questions and the response, from this study.
    Print on both sides of two A4 sheets, flipping on the long edge. While this block is open,
    printing the page prints the sheet; close it to print the study.</p>
    <label><input type="checkbox" class="ss-opt-mono"> Black &amp; white <small>for a black-only printer</small></label>
    {option}
    <button type="button" class="md-button md-button--primary"
      onclick="const d=this.closest('details');d.open=true;ssOn(true);ssFit(d);window.print()">Print sheet</button>
  </div>
  <div class="ss-set ss-four">{p1}{p2}{p3}{p4}</div>
  {two}
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
    """The study's primary graphic: its comic, else the first drawn (SVG) image on the page that is
    a diagram, not an emblem."""
    srcs = re.findall(r'<img\b[^>]*\bsrc="([^"]+\.svg)"', article)
    srcs = [s for s in srcs if "/assets/img/" in "/" + s and "favicon" not in s]
    srcs = sorted(srcs, key=lambda s: "/comics/" not in s)
    for src in srcs:
        path = Path(config.docs_dir) / posixpath.normpath(posixpath.join(page.url, src))
        try:
            box = re.search(r'viewBox="([\d.\s-]+)"', path.read_text(encoding="utf-8")[:2000])
        except FileNotFoundError:
            log.warning("study_sheet: %s has no file at %s", page.file.src_uri, path)
            continue
        w, h = (float(n) for n in box[1].split()[2:4]) if box else (1, 1)
        # A feast's 100-unit emblem is decoration, and blown up to a page it says nothing.
        if w < 300:
            continue
        return {"src": src, "shape": "landscape" if w / h > 1.1 else "portrait"}
    return None


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
    # Each outline line opens with its section's name: a link, bold, or a bold link, in a bulleted
    # or a numbered list.
    lists = re.search(r"<(ul|ol)>", outline_html)
    items = [_clean(re.sub(r"^\s*(<strong>.*?</strong>|<a\b[^>]*>.*?</a>)(.*)",
                           lambda m: f"<b>{re.sub(r'<[^>]+>', '', m[1])}</b><span>{m[2]}</span>", i, flags=re.DOTALL))
             for i in _items(outline_html, lists[1])] if lists else []
    items = [i for i in items if not i.startswith("<b>Discussion questions")]
    if not items:
        return ""
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<div class="ss-brief"><span class="ss-h">The study in brief</span><ol>{lis}</ol></div>'


def _segments(questions: list[str]) -> list[tuple[str, str]]:
    """Each question with its place on the clock. A question without a facet label stays in the
    segment of the one before it."""
    out, segment = [], "discover"
    for q in questions:
        label = re.match(r"\s*<strong>(.*?)\.?</strong>", q)
        segment = _FACETS.get(label[1].strip().rstrip(".").lower(), segment) if label else segment
        out.append((segment, q))
    return out


def _questions(questions: list[str]) -> str:
    """Page 3 for a study with no outline to walk: the questions under Discover and Wrestle."""
    groups: dict[str, list[str]] = {"discover": [], "wrestle": []}
    for segment, q in _segments(questions):
        groups.setdefault(segment, []).append(_clean(q))
    out, number = "", 0
    for key, label, a, b in _PLAN[2:4]:
        if not groups[key]:
            continue
        qs = ""
        for q in groups[key]:
            number += 1
            qs += _question(number, q)
        out += f'<div class="ss-group ss-group-{key}"><span class="ss-h">{_badge(key)}{label}</span>{qs}</div>'
    return out


def _question(number: int, q: str, cls: str = "ss-q") -> str:
    return f'<div class="{cls}"><p><span class="ss-n">{number}</span>{q}</p><i></i></div>'


def _minutes(a: int, b: int) -> str:
    return f'<span class="ss-badge" title="{a}–{b} minutes">{a}–{b}<small>min</small></span>'


def _citations(html: str, book: str) -> list[set[tuple[str, int, int]]]:
    """Each reference in the HTML, as the verses it covers. A bare "4:13" is in `book`, the study's
    own passage, as the pop-up reads it; a whole chapter covers all its verses. A bare number is not
    a reference. Image alt text describes a picture and often lists every verse on the page, so it
    is skipped."""
    text = re.sub(r"<[^>]+>", " ", re.sub(r"<img\b[^>]*>", "", html))
    out, prev, end = [], book, 0
    for m in _SCAN.finditer(text):
        if not m[1] and not m[3]:
            continue
        # A continuation in the same citation ("Revelation 21:2, 9; 22:17") keeps its book.
        if not m[1] and not re.fullmatch(r"[\s,;]*", text[end:m.start()]):
            prev = book
        prev, end = m[1] or prev, m.end()
        name, first = prev.rstrip("s"), int(m[3] or 1)
        last = int(m[4] or m[3] or 176)
        out.append({(name, int(m[2]), v) for v in range(first, min(last, first + 175) + 1)})
    return out


def _anchored(article: str, anchor: str) -> str:
    """The HTML under the heading with this id, to the next heading of its level or higher."""
    m = re.search(rf'<h([2-4]) id="{re.escape(anchor)}"', article)
    return _section(article, int(m[1]), anchor) if m else ""


def _steps(page, article: str, questions: list[str]) -> tuple[list[dict], list[str]] | None:
    """The Study outline's steps, each with the questions that belong to it, and the questions no
    step claims. Be transformed questions are left out: they close the sheet. None when the study
    has no outline of two or more steps to walk."""
    outline = _section(article, 2, "study-outline")
    passage = _REF.match(str(page.meta.get("primary_passage") or "").split(";")[0].strip())
    book = passage["book"].strip() if passage and passage["book"] else ""
    lists = re.search(r"<(ul|ol)>", outline)
    steps = []
    for item in _items(outline, lists[1]) if lists else []:
        # "Name — note" or "Name. Note", the name linking its section.
        head = re.match(r"\s*(?:<strong>)?\s*<a\b[^>]*href=\"#([^\"]+)\"[^>]*>(.*?)</a>\s*(?:</strong>)?\s*(?:[—–-]|\.)?\s*(.*)$",
                        item, re.DOTALL)
        if not head:
            continue
        name = re.sub(r"<[^>]+>", "", head[2]).strip()
        if name.lower().startswith("discussion questions"):
            continue
        # A step that links several sections covers all of them.
        anchors = [head[1]] + re.findall(r'href="#([^"]+)"', head[3])
        section = "".join(_anchored(article, a) for a in anchors)
        note = head[3]
        keys = []
        if not _citations(note, book):
            keys = re.findall(r"<blockquote>\s*<p>✝️?\s*(.+?)\s*\([A-Z0-9]+\)", section)[:3]
        steps.append({"name": name, "note": note, "keys": keys,
                      "cited": set().union(*_citations(section, book)), "qs": []})
    if len(steps) < 2:
        return None

    other = []
    for segment, q in _segments(questions):
        if segment == "respond":
            continue
        # The step that cites most of the question's references; a tie goes to the earlier step,
        # where the group meets the verse first. Counting references, not verses, keeps a
        # four-verse range from outweighing three single verses.
        asked = _citations(q, book)
        scores = [sum(bool(c & s["cited"]) for c in asked) for s in steps]
        best = max(scores)
        (steps[scores.index(best)]["qs"] if best else other).append(q)
    return steps, other


def _by_step(steps: list[dict], other: list[str]) -> str:
    """Page 3 for a study with an outline: the questions under the step they belong to, in the
    outline's order, with Discover and Wrestle's minutes (12 to 35) shared out by question count.
    A step with no questions keeps its heading, so the page still shows the way through, unless the
    page runs out of room."""
    # "Step 2", never a bare numeral: the numbers on the page belong to the questions.
    groups = [(f'Step {i} · {escape(s["name"])}', s["qs"]) for i, s in enumerate(steps, 1)]
    groups += [("Talk it over", other)] if other else []
    total = sum(len(qs) for _, qs in groups) or 1
    out, number, start = "", 0, 12
    for label, qs in groups:
        end = 12 + round(23 * (number + len(qs)) / total)
        badge = _minutes(start, end) if qs else ""
        body = "".join(_question(number + k, _clean(q)) for k, q in enumerate(qs, 1))
        out += f'<div class="ss-group{"" if qs else " ss-empty"}"><span class="ss-h">{badge}{label}</span>{body}</div>'
        number, start = number + len(qs), end
    return out


def _transform(article: str, respond: list[str], first: int, cls: str = "ss-q") -> tuple[str, str] | None:
    """Be transformed: its discussion questions, then the think / attitude / do list."""
    items = _items(_section(article, 3, "be-transformed"), "ul")
    if not respond and not items:
        return None
    qs = "".join(_question(first + k, _clean(q), cls) for k, q in enumerate(respond))
    tad = f'<ul>{"".join(f"<li>{_clean(i)}</li>" for i in items)}</ul>' if items else ""
    return qs, tad


def _two_pages(page, article: str, point: str, plan, respond: list[str], title: str, qr: str) -> str:
    """One sheet that walks the Study outline, for a leader who does not know the study well: each
    step with its key verses, then straight away the questions that belong to it. The hook writes
    the blocks in order onto page 1; ssFlow carries what does not fit over to page 2."""
    steps, other = plan
    blocks, number = [], 0
    passage = escape(str(page.meta.get("primary_passage") or ""))
    blocks.append(f'<p class="ss-b ss-lead"><b>Open</b> {_opener(page.meta, title)}</p>')
    if passage:
        blocks.append(f'<p class="ss-b ss-lead"><b>Read it aloud</b> {passage}</p>')
    for i, s in enumerate(steps, 1):
        keys = f'<span class="ss-keys">Key verses: {escape("; ".join(s["keys"]))}</span>' if s["keys"] else ""
        note = _clean(s["note"])
        # data-keep: a heading goes to the next page with the question under it, never alone.
        # A tinted band headed "Step 2", never a bare numeral: the numbers on the page belong to
        # the questions.
        blocks.append(f'<div class="ss-b ss-stephead" data-keep><span class="ss-step">Step {i}</span>'
                      f'<b>{escape(s["name"])}</b>{f'<span class="ss-note"> — {note}</span>' if note else ""}{keys}</div>')
        for q in s["qs"]:
            number += 1
            blocks.append(_question(number, _clean(q), "ss-b ss-q"))
    if other:
        blocks.append('<div class="ss-b ss-grouphead" data-keep>Talk it over</div>')
        for q in other:
            number += 1
            blocks.append(_question(number, _clean(q), "ss-b ss-q"))
    transform = _transform(article, respond, number + 1, "ss-b ss-q")
    if transform:
        qs, tad = transform
        blocks.append('<div class="ss-b ss-grouphead" data-keep>Be transformed</div>')
        blocks.append(qs)
        if tad:
            blocks.append(f'<div class="ss-b ss-tad">{tad}</div>')

    def foot(n: int) -> str:
        return f'<footer class="ss-foot"><span>Page {n} of 2 · print double-sided, flip on long edge</span><span>{_NOTICE}</span></footer>'

    return f"""<div class="ss-set ss-two">
<section class="ss-sheet ss-t1" aria-label="Two-page study sheet, page 1">
  <header class="ss-head">
    <span class="ss-kicker">Group study · step by step</span>
    <h2>{escape(title)}</h2>
    <span class="ss-ref">{passage}</span>
  </header>
  <div class="ss-flow">{"".join(blocks)}</div>
  {foot(1)}
</section>
<section class="ss-sheet ss-t2" aria-label="Two-page study sheet, page 2">
  <header class="ss-head ss-head-back"><h2>{escape(title)}</h2></header>
  <div class="ss-flow"></div>
  <p class="ss-point"><b>The point</b> {_clean(point)}</p>
  <div class="ss-link">{qr}</div>
  {foot(2)}
</section>
</div>"""


def _unnumber(text: str, ref: str) -> str:
    """Drop the verse numbers from a quoted passage: the leading one, and each later number in the
    reference's range (17, 18, 19 for "Ephesians 3:16-19"), so a number in the verse itself stays."""
    text = re.sub(r"^\s*\d+\s+", "", text)
    span = re.search(r":(\d+)-(\d+)", ref)
    for n in range(int(span[1]) + 1, int(span[2]) + 1) if span else ():
        text = re.sub(rf"(?<=\s){n}\s+", "", text, count=1)
    return text


def _respond(article: str, respond: list[str], first: int) -> str:
    transform = _transform(article, respond, first)
    tad = ""
    if transform:
        qs, items = transform
        tad = f'<div class="ss-tad"><span class="ss-h">{_badge("respond")}Be transformed</span>{qs}{items}</div>'
    # Markdown merges consecutive quote blocks into one, so the verses are told apart by their
    # "✝️ Reference (TRANSLATION)" lines. One verse to learn this week: the first.
    paragraphs = re.findall(r"<p>(.*?)</p>", _section(article, 3, "memory-verses"), re.DOTALL)
    memory = ""
    if paragraphs and paragraphs[0].startswith("✝"):
        ref = paragraphs[0].lstrip("✝️ ")
        text = "".join(f"<p>{_unnumber(p, ref)}</p>"
                       for p in itertools.takewhile(lambda p: not p.startswith("✝"), paragraphs[1:]))
        memory = f'<div class="ss-memory"><span class="ss-h">Memory verse</span>{_clean(text)}<cite>{_clean(ref)}</cite></div>'
    prayer = _section(article, 3, "prayer").strip()
    prayer = f'<div class="ss-prayer"><span class="ss-h">Pray together</span>{_clean(prayer)}</div>' if prayer else ""
    return tad + memory + prayer
