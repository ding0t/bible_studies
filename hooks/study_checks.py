"""A collapsed "How this study was checked" panel on every study with a state file.

The panel says only what the study's state file (references/study-state/<slug>.yml) records:

- the dated review, readability and simplify passes, from their `review_<date>`, `read_<date>` and
  `simplify_<date>` blocks, with the corrections and author questions the reviews list;
- the `evidence:` entries, each a lookup someone ran and recorded, counted by kind and listed in
  full in a nested panel.

It writes no sentence about the study itself, so it needs no checking of its own. The evidence is
shown as recorded; nothing here replays it (the build has no Bible databases), so the panel gives
each check's date and never says "verified".

It sits before the References heading, or at the end of the article. It runs at on_post_page, as
study_sheet.py does, so the search index never sees it, and carries data-no-popups so the shorthand
references in the evidence lines ("22:19") are not resolved against the page's last book.
"""

from __future__ import annotations

import datetime as dt
import logging
import re
import sys
from collections import Counter
from html import escape
from pathlib import Path

import yaml

# Hooks are loaded by path, so the sibling module is imported from this directory. study_sheet.py
# holds the book-name map; it is used here inverted, to name an evidence entry's verse.
sys.path.insert(0, str(Path(__file__).parent))
from study_sheet import _BOOKS  # noqa: E402

log = logging.getLogger("mkdocs.hooks.study_checks")

_STATE_DIR = Path("references/study-state")
_DATED = re.compile(r"^([a-z_]+?)_(\d{4})[-_](\d{2})[-_](\d{2})")
# Review blocks name their lists differently across two years of state files. Only lists are
# counted: a bare number (critical_fixed: 2) often totals a list beside it, and counting both would
# double it. So the panel says the reviews "list" N corrections, which is exactly what it counted.
_FIXED = re.compile(r"^(?:fixed|applied|corrected|fixes_applied.*|findings_fixed|.+_fixed)$")
_FOR_AUTHOR = re.compile(r"^(?:left_for_author|open_for_author|for_author|still_open)$")
# Each evidence tool, as a reader would describe the check.
_QUOTE = ("Scripture quotation checked against the printed translation",
          "Scripture quotations checked against the printed translation")
_COUNT = ("word count re-run in the Hebrew or Greek", "word counts re-run in the Hebrew or Greek")
_WORD = ("word checked beneath the English", "words checked beneath the English")
_KINDS = {
    "study_verse": _QUOTE, "bible_verse": _QUOTE, "bible_passage": _QUOTE, "bible_parallel": _QUOTE,
    "bible_concordance": _COUNT,
    "bible_interlinear": _WORD, "bible_word": _WORD, "twot_strongs": _WORD, "twot_root": _WORD,
    "study_note": ("study-Bible note checked", "study-Bible notes checked"),
    "bible_trace": ("cross-reference traced", "cross-references traced"),
}
_OTHER = ("other check", "other checks")
_BOOK_NAMES = {code: name for name, code in reversed(_BOOKS.items())}
_REFERENCES = re.compile(r'<h2 id="(?:references|sources|further-reading)[^"]*"')

_panels: dict[str, str] = {}


def _date(parts: tuple[str, str, str]) -> dt.date | None:
    try:
        return dt.date(*map(int, parts))
    except ValueError:
        return None


def _long(d: dt.date) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


def _count(block: dict, keys: re.Pattern) -> int:
    return sum(len(v) for k, v in block.items() if keys.match(str(k)) and isinstance(v, (list, dict)))


def _n(n: int, forms: tuple[str, str]) -> str:
    return f"{n} {forms[n != 1]}"


def _passes(state: dict, name: str) -> list[tuple[dt.date, object]]:
    found = []
    for key, value in state.items():
        m = _DATED.match(str(key))
        if m and m[1] == name and (d := _date(m.groups()[1:])):
            found.append((d, value))
    return sorted(found, key=lambda p: p[0])


def _evidence_date(e: dict) -> dt.date | None:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(e.get("checked", "")))
    return _date(m.groups()) if m else None


def _where(args: dict) -> str:
    """The verse or word an evidence entry looked up, from its args, for a note that omits it."""
    book = _BOOK_NAMES.get(str(args.get("book")), args.get("book"))
    chapter = args.get("chapter")
    verse = args.get("verse", args.get("verse_start"))
    if book and chapter and verse:
        end = args.get("verse_end")
        return f"{book} {chapter}:{verse}{f'-{end}' if end and end != verse else ''}"
    strongs = args.get("strongs") or args.get("strongs_id")
    if strongs:
        return f"{strongs} in {book}" if book else str(strongs)
    return ""


def _panel(state: dict, state_file: str, repo_url: str, site_url: str) -> str:
    items = []
    reviews = _passes(state, "review")
    if reviews:
        blocks = [v for _, v in reviews if isinstance(v, dict)]
        fixed = sum(_count(b, _FIXED) for b in blocks)
        asked = sum(_count(b, _FOR_AUTHOR) for b in blocks)
        if len(reviews) == 1:
            line = f"<strong>Reviewed</strong> on {_long(reviews[0][0])}."
        else:
            line = (f"<strong>Reviewed</strong> {len(reviews)} times, most recently on "
                    f"{_long(reviews[-1][0])}.")
        recorded = [_n(n, forms) for n, forms in ((fixed, ("correction", "corrections")),
                    (asked, ("question for the author", "questions for the author"))) if n]
        if recorded:
            line += f" {'The review lists' if len(reviews) == 1 else 'The reviews list'} "
            line += f"{' and '.join(recorded)}."
        items.append(line)
    for name, label in (("read", "Read for structure"), ("simplify", "Simplified")):
        if dates := sorted({d for d, _ in _passes(state, name)}):
            items.append(f"<strong>{label}</strong> on {', '.join(_long(d) for d in dates)}.")

    evidence = [e for e in state.get("evidence") or [] if isinstance(e, dict)]
    rows = []
    if evidence:
        kinds = Counter(_KINDS.get(str(e.get("tool")), _OTHER) for e in evidence)
        order = sorted(kinds.items(), key=lambda kv: (kv[0] == _OTHER, -kv[1]))
        dates = [d for e in evidence if (d := _evidence_date(e))]
        latest = f", the latest on {_long(max(dates))}" if dates else ""
        parts = "; ".join(_n(n, kind) for kind, n in order)
        items.append(f"<strong>{len(evidence)} checks recorded</strong>{latest}: {parts}.")
        for e in evidence:
            what = str(e.get("what") or e.get("claim") or e.get("id") or "").strip()
            where = _where(e.get("args") or {})
            ref = where.rsplit(" ", 1)[-1] if ":" in where else where
            if where and ref not in what:
                what = f"{where}: {what}"
            what = escape(what)
            when = _evidence_date(e)
            tool = escape(str(e.get("tool", "")))
            rows.append(f"<li>{what} <small>({tool}{', ' + str(when) if when else ''})</small></li>")

    if not items:
        return ""
    source = f"{repo_url.rstrip('/')}/blob/main/{_STATE_DIR.as_posix()}/{state_file}"
    method = f"{site_url.rstrip('/')}/skills/review-bible-study/SKILL.md"
    guide = f"{site_url.rstrip('/')}/resources/guiding-ai-in-bible-study/"
    html = [
        '<details class="abstract study-checks" data-no-popups>',
        "<summary>How this study was checked</summary>",
        f'<p>From the study\'s <a href="{source}">working file</a>, written as the work was done. '
        f'Each review follows the site\'s <a href="{method}">review method</a>, which re-checks '
        "every quotation, count and claim against its source. "
        f'<a href="{guide}">Guiding AI in Bible Study</a> gives the mistakes behind it.</p>',
        "<ul>", *(f"<li>{i}</li>" for i in items), "</ul>",
    ]
    if rows:
        html += [
            "<details><summary>Every recorded check</summary>",
            "<p>Each line is the note written when the lookup was run, with the tool and the date.</p>",
            "<ul>", *rows, "</ul>", "</details>",
        ]
    html.append("</details>")
    return "\n".join(html) + "\n"


def on_files(files, config):
    _panels.clear()
    by_uri = {f.src_uri: f for f in files.documentation_pages()}
    by_stem: dict[str, list[str]] = {}
    for uri in by_uri:
        by_stem.setdefault(Path(uri).stem, []).append(uri)
    for path in sorted(_STATE_DIR.glob("*.yml")):
        try:
            state = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as err:
            log.warning("study_checks: skipping %s (%s)", path.name, err)
            continue
        if not isinstance(state, dict):
            continue
        targets = state.get("target_path") or []
        targets = [targets] if isinstance(targets, str) else list(targets)
        uris = [t.removeprefix("docs/content/") for t in targets if isinstance(t, str)]
        # Older state files have no target_path; their slug is the page's file name.
        if not uris and len(by_stem.get(path.stem, [])) == 1:
            uris = by_stem[path.stem]
        for uri in uris:
            if uri in by_uri and uri not in _panels:
                panel = _panel(state, path.name, config["repo_url"] or "", config["site_url"] or "")
                if panel:
                    _panels[uri] = panel
    return files


def on_post_page(output, page, config):  # noqa: ARG001 - hook signature
    panel = _panels.get(page.file.src_uri)
    if not panel:
        return output
    start, end = output.find("<article"), output.find("</article>")
    if start < 0 or end < 0:
        return output
    m = _REFERENCES.search(output, start, end)
    at = m.start() if m else end
    return output[:at] + panel + output[at:]
