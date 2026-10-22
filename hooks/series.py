"""Study series: existing studies, in an order, for a group to take one a week.

A series is any page whose frontmatter has a `series:` block. Each study keeps its one home in the
subject taxonomy, and a series only points at it, so the same study can sit in a topic series, a
book series and a foundations series at once:

    series:
      cut: foundations          # foundations | topic | book | passage | season | one-off
      sessions:
        - study: last-things/rapture.md      # path from docs/content
          why: "what this week adds"        # optional, shown under the title
        - planned: "The Millennium"          # not written yet: shown as coming, never linked

Three things are written from it:

- `<!-- series-sessions -->` on the series page becomes the week-by-week list. A series page that
  lists its studies by hand (jesus/the-heavenly-pattern/) leaves the marker out and keeps its list.
- `<!-- series-hub -->` on series/index.md becomes every series, grouped by cut.
- Every study in a series gets a line under its title: "Week 2 of 7 in ..., next: ...", so the
  series reaches a reader who arrives at the study from search.

A draft series is skipped entirely, and a session pointing at a draft study is shown as planned,
so neither ever ships a link to a page draft_pages.py dropped (validate-content.js Check 24 cannot
see links written by a hook). Drafts are skipped under `mkdocs serve` too, as section_plates.py
does, so the local site matches the live one. The styles are in assets/stylesheets/series.css.
"""

from __future__ import annotations

import logging
import posixpath
import re
from pathlib import Path

import yaml

log = logging.getLogger("mkdocs.hooks.series")

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
_H1 = re.compile(r"^# .+$", re.MULTILINE)
_WORD = re.compile(r"\w+")
# study_sheet.py finds the heading by its id, so "Discussion Questions" counts too.
_QUESTIONS = re.compile(r"^## Discussion questions\s*$", re.MULTILINE | re.IGNORECASE)
_HUB = "series/index.md"
_SESSIONS_MARKER = "<!-- series-sessions -->"
_HUB_MARKER = "<!-- series-hub -->"
# The hub's order: where a newcomer starts, then the ways to go deeper.
_CUTS = {
    "foundations": "Foundations",
    "topic": "By topic",
    "book": "Through a book",
    "passage": "Through a passage",
    "season": "For a season",
    "one-off": "One session",
}
# Silent reading. A leader reads the study, and the group reads the sheet.
_WORDS_PER_MINUTE = 200

_series: list[dict] = []
# study src_uri -> [(index into _series, week number)]
_memberships: dict[str, list[tuple[int, int]]] = {}


def _read(path: Path) -> tuple[dict, str] | None:
    try:
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER.match(text)
        meta = yaml.safe_load(match.group(1)) if match else None
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    if not isinstance(meta, dict):
        return None
    return meta, text[match.end():]


def _session(entry: dict, files, series_src: str) -> dict | None:
    if "planned" in entry:
        return {"title": entry["planned"], "why": entry.get("why"), "src": None}
    src = entry.get("study")
    file = files.get_file_from_path(src) if src else None
    read = _read(Path(file.abs_src_path)) if file else None
    if read is None:
        log.warning("series: %s lists %r, which is not a page", series_src, src)
        return None
    meta, body = read
    title = meta.get("title") or src
    if meta.get("draft") is True:
        log.info("series: %s lists draft %s; shown as coming until it is published", series_src, src)
        return {"title": title, "why": entry.get("why"), "src": None}
    return {
        "title": title,
        "why": entry.get("why"),
        "src": src,
        "passage": meta.get("primary_passage"),
        "minutes": max(5, round(len(_WORD.findall(body)) / _WORDS_PER_MINUTE / 5) * 5),
        # The same two things hooks/study_sheet.py needs before it builds a sheet.
        "sheet": "**In one sentence:**" in body and bool(_QUESTIONS.search(body)),
    }


def on_files(files, config):  # noqa: ARG001 - `config` is part of the signature
    _series.clear()
    _memberships.clear()
    for file in sorted(files.documentation_pages(), key=lambda f: f.src_uri):
        if file.src_uri.startswith("commentaries/"):
            continue
        read = _read(Path(file.abs_src_path))
        if read is None or not isinstance(read[0].get("series"), dict) or read[0].get("draft") is True:
            continue
        meta = read[0]
        spec = meta["series"]
        if spec.get("cut") not in _CUTS:
            log.warning("series: %s has cut %r; use one of %s", file.src_uri, spec.get("cut"), ", ".join(_CUTS))
            continue
        sessions = [s for e in spec.get("sessions") or [] if (s := _session(e, files, file.src_uri))]
        index = len(_series)
        _series.append({
            "src": file.src_uri,
            "title": meta.get("title") or file.src_uri,
            "description": meta.get("description") or "",
            "cut": spec["cut"],
            "sessions": sessions,
        })
        for week, session in enumerate(sessions, 1):
            if session["src"]:
                _memberships.setdefault(session["src"], []).append((index, week))
    return files


def _link(src: str, here: str) -> str:
    return posixpath.relpath(src, posixpath.dirname(here) or ".")


def _sessions_list(series: dict, here: str) -> str:
    items = []
    for week, s in enumerate(series["sessions"], 1):
        if s["src"] is None:
            head = f"**{s['title']}** · *coming*"
            notes = []
        else:
            head = f"**[{s['title']}]({_link(s['src'], here)})**"
            if s["passage"]:
                head += f" · {s['passage']}"
            notes = [f"about {s['minutes']} minutes to read"]
            if s["sheet"]:
                notes.append("printable group sheet")
        body = f"1.  {head}\n"
        if s["why"]:
            body += f"\n    {s['why']}\n"
        if notes:
            body += f"\n    <small>Week {week} · {' · '.join(notes)}</small>\n"
        items.append(body)
    return '<div class="series-sessions" markdown>\n\n' + "\n".join(items) + "\n</div>\n"


def _hub(here: str) -> str:
    out = []
    for cut, heading in _CUTS.items():
        members = [s for s in _series if s["cut"] == cut]
        if not members:
            continue
        cards = []
        for s in members:
            written = sum(1 for x in s["sessions"] if x["src"])
            count = f"{written} session{'s' if written != 1 else ''}"
            if coming := len(s["sessions"]) - written:
                count += f", {coming} coming"
            cards.append(
                f"-   __[{s['title']}]({_link(s['src'], here)})__\n\n"
                f"    ---\n\n"
                f"    {s['description']}\n\n"
                f"    <small>{count}</small>\n"
            )
        out.append(f"## {heading}\n\n<div class=\"grid cards\" markdown>\n\n" + "\n".join(cards) + "\n</div>\n")
    return "\n".join(out)


def _banner(src: str) -> str:
    lines = []
    for index, week in _memberships.get(src, []):
        series = _series[index]
        sessions = series["sessions"]
        link = f"[{series['title']}]({_link(series['src'], src)})"
        if len(sessions) == 1:
            lines.append(f":material-bookshelf: Also a single group session: {link}\n{{ .page-series }}\n")
            continue
        line = f":material-bookshelf: Week {week} of {len(sessions)} in {link}"
        following = sessions[week] if week < len(sessions) else None
        if following and following["src"]:
            line += f" · next: [{following['title']}]({_link(following['src'], src)})"
        lines.append(f"{line}\n{{ .page-series }}\n")
    return "\n".join(lines)


def on_page_markdown(markdown, page, config, files):  # noqa: ARG001 - hook signature
    src = page.file.src_uri
    if src == _HUB and _HUB_MARKER in markdown:
        return markdown.replace(_HUB_MARKER, _hub(src))
    own = next((s for s in _series if s["src"] == src), None)
    if own and _SESSIONS_MARKER in markdown:
        markdown = markdown.replace(_SESSIONS_MARKER, _sessions_list(own, src))
    if src not in _memberships:
        return markdown
    banner = _banner(src)
    match = _H1.search(markdown)
    if match is None:
        return f"{banner}\n{markdown}"
    return f"{markdown[:match.end()]}\n\n{banner}{markdown[match.end():]}"
