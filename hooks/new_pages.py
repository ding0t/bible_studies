"""Mark a newly published page as new, on the page and in the sidebar, for 30 days.

The dates come from docs/data/published.json, which utils/generate_recent_updates.py derives from
git (the commit that took each page out of draft) and which CI regenerates just before this build.
Reading them from a file keeps git out of the build: `mkdocs serve` rebuilds on every save, and a
`git log` per page on each rebuild would be felt.

Two marks, from one date:

- `status: new` in the page's meta, which mkdocs-material shows as an icon beside the page in the
  navigation, with `extra.status.new` in mkdocs.yml as its tooltip. The nav is rendered after
  every page's markdown has been read, so setting it here reaches every sidebar, not only the
  page's own.
- A line under the page's title, which also reaches a phone reader who never opens the sidebar,
  linking to the list of everything else that is new.

A page that sets its own `status` keeps it. The window is published.json's `window_days`, the same
number the generator used for the New lists, so the badge and the lists expire together. Both are
measured from the day of the build, so a badge outlives its window by however long the site goes
without a deploy.
"""

from __future__ import annotations

import json
import logging
import posixpath
import re
from datetime import date
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.new_pages")

_H1 = re.compile(r"^# .+$", re.MULTILINE)
_NEW_LIST = "about/recent-updates.md"

_published: dict[str, date] = {}
_window_days = 0


def on_config(config):
    global _window_days
    path = Path(config.config_file_path).parent / "docs" / "data" / "published.json"
    _published.clear()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log.info("new_pages: %s not found -- run utils/generate_recent_updates.py", path.name)
        return config
    _window_days = data["window_days"]
    _published.update({uri: date.fromisoformat(day) for uri, day in data["published"].items()})
    return config


def on_page_markdown(markdown, page, config, files):  # noqa: ARG001 - hook signature
    published = _published.get(page.file.src_uri)
    if published is None or (date.today() - published).days >= _window_days:
        return markdown
    page.meta.setdefault("status", "new")

    link = posixpath.relpath(_NEW_LIST, posixpath.dirname(page.file.src_uri) or ".")
    badge = (
        f":material-new-box: New, published {published.day} {published:%B %Y}. "
        f"[What else is new]({link}#new)\n{{ .page-new }}\n"
    )
    match = _H1.search(markdown)
    if match is None:
        return f"{badge}\n{markdown}"
    return f"{markdown[:match.end()]}\n\n{badge}{markdown[match.end():]}"
