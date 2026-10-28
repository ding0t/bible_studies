"""Render the Songbook from docs/data/songbook.toml wherever a page carries one of its markers.

- `<!-- songbook: <group> -->`  the songs of one group (israel, psalms, first-church, heaven,
                                  early-church), as cards in file order.
- `<!-- songbook-occasions -->`  "Sing it when": each occasion with the songs for it.
- `<!-- songbook-jesus -->`      the songs Jesus sang, quoted, or had sung to Him.

Each card carries id="song-<id>", so a study links to one song as
`../resources/songbook.md#song-<id>`. References are written as plain text so the site's verse
pop-up finds them; the cards are not marked data-no-popups for that reason.

Each card folds away the song's full words: the site's reading translation, from
docs/data/songbook-words.json (written by references/build/export_songbook.py, which records which
translation it used), or the song's own `words` where they are not in Scripture's text.
"""

from __future__ import annotations

import json
import logging
import re
import tomllib
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.songbook")

_GROUP = re.compile(r"<!--\s*songbook:\s*([\w-]+)\s*-->")
_OCCASIONS = re.compile(r"<!--\s*songbook-occasions\s*-->")
_JESUS = re.compile(r"<!--\s*songbook-jesus\s*-->")

GROUPS = ("israel", "psalms", "first-church", "heaven", "early-church")

# Order is the order of the "Sing it when" index; labels finish the sentence "Sing it when…".
OCCASIONS = {
    "deliverance": "God has rescued you",
    "victory": "an enemy is defeated",
    "thanksgiving": "you want to give thanks",
    "provision": "God has provided",
    "answered-prayer": "a prayer is answered",
    "a-birth": "a child is given",
    "trouble": "you are in trouble",
    "persecution": "you suffer for Christ",
    "sickness": "you are sick or recovering",
    "repentance": "you have sinned",
    "trust": "you are afraid",
    "grief": "you are grieving",
    "a-death": "someone is dying",
    "remembering": "you need to remember",
    "the-lords-supper": "you take the Lord's Supper",
    "a-journey": "you travel to worship",
    "morning": "the day begins",
    "evening": "the day ends",
    "creation": "you look at creation",
    "worship": "the church gathers to worship",
}

JESUS = {
    "sang": "He sang",
    "quoted": "He quoted",
    "sung-to": "Sung to Him",
}

_songs: list[dict] = []
_words: dict[str, list[dict]] = {}
# Which translation the hand-written first lines quote, and which the exported words are in.
_sources: dict[str, str] = {"first_line": "", "words": ""}


def _toml_path(config) -> Path:
    return Path(config.config_file_path).parent / "docs" / "data" / "songbook.toml"


def on_serve(server, config, builder):  # noqa: ARG001 - hook signature
    # Outside docs_dir, so `mkdocs serve` would otherwise keep showing the old songbook.
    server.watch(str(_toml_path(config)))
    server.watch(str(_toml_path(config).with_name("songbook-words.json")))
    return server


def on_config(config):
    book = tomllib.loads(_toml_path(config).read_text(encoding="utf-8"))
    exported = json.loads(_toml_path(config).with_name("songbook-words.json").read_text(encoding="utf-8"))
    _songs.clear()
    _songs.extend(book["song"])
    _words.clear()
    _words.update(exported["songs"])
    _sources.update(first_line=book["first_line_source"], words=exported["code"])
    for song in _songs:
        if song["group"] not in GROUPS:
            log.warning("songbook: %s has unknown group %r", song["id"], song["group"])
        for occasion in song["sing_when"]:
            if occasion not in OCCASIONS:
                log.warning("songbook: %s has unknown occasion %r", song["id"], occasion)
        if "words" not in song and song["id"] not in _words:
            log.warning("songbook: %s has no words -- run references/build/export_songbook.py",
                        song["id"])
        if song.get("jesus") and (song["jesus"] not in JESUS or not song.get("jesus_note")):
            log.warning("songbook: %s needs jesus to be one of %s, with a jesus_note",
                        song["id"], ", ".join(JESUS))
    return config


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    html = _GROUP.sub(lambda m: _group(m[1], page.file.src_uri), html)
    html = _OCCASIONS.sub(lambda m: _occasions(), html)
    return _JESUS.sub(lambda m: _jesus(), html)


def _group(group: str, src: str) -> str:
    songs = [s for s in _songs if s["group"] == group]
    if not songs:
        log.warning("songbook: %s asks for group %r, which has no songs", src, group)
    return f'<div class="sb-group">{"".join(_card(s) for s in songs)}</div>'


def _card(song: dict) -> str:
    source = escape(song.get("source", _sources["first_line"]))
    occasions = "".join(f'<a class="sb-tag" href="#sing-{o}">{escape(OCCASIONS.get(o, o))}</a>'
                        for o in song["sing_when"])
    tune = ""
    if song.get("tune"):
        hebrew = song.get("tune_hebrew", "")
        tune = (f'<p class="sb-meta"><b>Tune</b> '
                + (f'<span dir="rtl" lang="he">{escape(hebrew)}</span> ' if hebrew else "")
                + f'{escape(song["tune"])}</p>')
    jesus = ""
    if song.get("jesus"):
        jesus = (f'<p class="sb-jesus"><b>{escape(JESUS[song["jesus"]])}.</b> '
                 f'{escape(song["jesus_note"])}</p>')
    return f"""<article class="sb-song" id="song-{escape(song["id"])}">
  <header class="sb-head"><b class="sb-title">{escape(song["title"])}</b>
    <span class="sb-ref">{escape(song["ref"])}</span></header>
  <blockquote class="sb-first">{escape(song["first_line"])} <cite>{source}</cite></blockquote>
  <p class="sb-meta"><b>Sung by</b> {escape(song["sung_by"])}</p>
  <p class="sb-meta"><b>When</b> {escape(song["occasion"])}</p>
  {tune}
  {jesus}
  <p class="sb-when"><b>Sing it when</b> {occasions}</p>
  {_full(song)}
</article>"""


def _full(song: dict) -> str:
    """The whole song, folded away: verse by verse from the reading translation, under a heading
    for each chapter when it runs across several, or the song's own lines."""
    if "words" in song:
        body = "".join(f"<p>{escape(line)}</p>" for line in song["words"])
        source = song.get("source", "")
    elif song["id"] in _words:
        chapters = _words[song["id"]]
        book = re.match(r"(.+?)\s+\d", song["ref"])[1].removesuffix("s")
        body = "".join(
            (f'<p class="sb-ch">{escape(book)} {c["chapter"]}</p>' if len(chapters) > 1 else "")
            + "".join(f"<p><sup>{v}</sup> {escape(t)}</p>" for v, t in c["verses"])
            for c in chapters)
        source = _sources["words"]
    else:
        return ""
    return (f'<details class="sb-words"><summary>The words</summary>'
            f'<div class="sb-lines">{body}</div><p class="sb-src">{escape(source)}</p></details>')


def _link(song: dict) -> str:
    return f'<a href="#song-{escape(song["id"])}">{escape(song["title"])}</a>'


def _occasions() -> str:
    rows = []
    for occasion, label in OCCASIONS.items():
        songs = [s for s in _songs if occasion in s["sing_when"]]
        if songs:
            rows.append(f'<dt id="sing-{occasion}">… {escape(label)}</dt>'
                        f'<dd>{" · ".join(_link(s) for s in songs)}</dd>')
    return f'<dl class="sb-index">{"".join(rows)}</dl>'


def _jesus() -> str:
    rows = []
    for kind, label in JESUS.items():
        songs = [s for s in _songs if s.get("jesus") == kind]
        if songs:
            items = "".join(f'<li>{_link(s)} ({escape(s["ref"])}): {escape(s["jesus_note"])}</li>'
                            for s in songs)
            rows.append(f'<dt>{escape(label)}</dt><dd><ul>{items}</ul></dd>')
    return f'<dl class="sb-index sb-jesus-index">{"".join(rows)}</dl>'
