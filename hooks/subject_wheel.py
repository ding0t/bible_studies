"""Draw the subject wheel wherever a page carries `<!-- subject-wheel -->`.

The home page's picture of what the site is about: the subject sections set around a clock face,
each wedge's area in proportion to its number of published studies, each wedge a link to its
section. Counted at build time from the pages themselves, so the wheel can never disagree with the
site the way a committed SVG with typed-in numbers would after the next study ships.

What counts: a page under one of `_SECTIONS` that is not the section's own `index.md`, not a
generated landing or cross-reference page, and not `draft: true`. Drafts are checked here as well as dropped by
draft_pages.py, because that hook keeps them under `mkdocs serve` and the local wheel should match
the live one.

Drawn in the Larkin hand of utils/lib/larkin.py (parchment, ink, ruled border) so it reads as one
of the site's plates. The colours are repeated here rather than imported because hooks are loaded
by path and utils/ is not on their import path.
"""

from __future__ import annotations

import logging
import math
import re
from html import escape
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.subject_wheel")

_MARKER = re.compile(r"<!--\s*subject-wheel\s*-->")
_DRAFT = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)
# Landing pages a script writes. A nested index.md without one is a study in its own right.
_GENERATED = ("commentary-index:auto-start", "section-index:auto-start")
_DESCRIPTION = re.compile(r'^description:\s*"?(.*?)"?\s*$', re.MULTILINE)

# Clockwise from twelve o'clock, roughly in the order the story of Scripture meets them: God and
# the beings He made, the fall, the people and nation He worked through, the feasts that pictured
# His Son, the Son, what He won, the life that follows, and the end. about/, resources/, sermons/
# and commentaries/ are left off: they are a kind of page, not a subject.
_SECTIONS = (
    ("god", ("God",)),
    ("spiritual-beings", ("Spiritual", "beings")),
    ("sin", ("Sin",)),
    ("biblical-figures", ("Biblical", "figures")),
    ("israel-and-church", ("Israel &", "the Church")),
    ("feasts", ("Feasts",)),
    ("jesus", ("Jesus",)),
    ("salvation", ("Salvation",)),
    ("christian-life", ("Christian", "life")),
    ("wisdom", ("Wisdom",)),
    ("scripture", ("Scripture",)),
    ("chronology", ("Chronology",)),
    ("last-things", ("Last things",)),
)

SERIF = "Georgia, 'Times New Roman', serif"
INK = "#3b2f1e"
MUTED = "#6b5a3e"
PAPER = "#faf6ec"
GOLD = "#e8c46a"
GOLD_EDGE = "#a67c3d"
BLUE = "#2f4f7f"
BLUE_TINT = "#e3e9f2"

W, H = 760, 620
CX, CY = W / 2, 296
HUB = 92
RIM = 218
LABEL_R = 246

_counts: dict[str, int] = {}
_descriptions: dict[str, str] = {}


def on_files(files, config):  # noqa: ARG001 - hook signature
    _counts.clear()
    _descriptions.clear()
    wanted = {slug for slug, _ in _SECTIONS}
    for file in files.documentation_pages():
        section, _, rest = file.src_uri.partition("/")
        if section not in wanted or not rest:
            continue
        source = Path(file.abs_src_path).read_text(encoding="utf-8")
        if rest == "index.md":
            match = _DESCRIPTION.search(source)
            _descriptions[section] = match[1] if match else ""
            continue
        if _DRAFT.search(source) or any(marker in source for marker in _GENERATED):
            continue
        _counts[section] = _counts.get(section, 0) + 1
    return files


def on_page_content(html, page, config, files):  # noqa: ARG001 - hook signature
    if not _MARKER.search(html):
        return html
    up = "../" * page.url.count("/")
    return _MARKER.sub(lambda _: render(up), html)


def _point(angle, r):
    return CX + r * math.sin(angle), CY - r * math.cos(angle)


def _wedge(a0, a1, r0, r1):
    x0, y0 = _point(a0, r0)
    x1, y1 = _point(a1, r0)
    x2, y2 = _point(a1, r1)
    x3, y3 = _point(a0, r1)
    return (f"M{x0:.1f} {y0:.1f} A{r0} {r0} 0 0 1 {x1:.1f} {y1:.1f} "
            f"L{x2:.1f} {y2:.1f} A{r1:.1f} {r1:.1f} 0 0 0 {x3:.1f} {y3:.1f} Z")


def _text(x, y, s, size, anchor="middle", fill=INK, weight=None, italic=False, cls=None):
    attrs = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if italic:
        attrs += ' font-style="italic"'
    if cls:
        attrs += f' class="{cls}"'
    return f"<text {attrs}>{escape(s)}</text>"


def render(up: str) -> str:
    counts = [_counts.get(slug, 0) for slug, _ in _SECTIONS]
    total, most = sum(counts), max(counts) or 1
    step = 2 * math.pi / len(_SECTIONS)
    gap = 0.018

    summary = ", ".join(f"{' '.join(label)} {n}" for (_, label), n in zip(_SECTIONS, counts))
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{SERIF}" '
        f'class="subject-wheel" role="img" aria-labelledby="sw-t sw-d">',
        f'<title id="sw-t">What these studies cover</title>',
        f'<desc id="sw-d">A wheel of the {len(_SECTIONS)} subjects these {total} studies are '
        f"filed under, clockwise from the top, each wedge's area in proportion to its number of "
        f"studies: {escape(summary)}. Each wedge links to its section.</desc>",
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="none" stroke="{INK}" stroke-width="2.5"/>',
        f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="{INK}" stroke-width="0.8"/>',
        f'<circle cx="{CX}" cy="{CY}" r="{RIM}" fill="none" stroke="{MUTED}" stroke-width="0.6" stroke-dasharray="2 4"/>',
    ]

    for i, ((slug, label), n) in enumerate(zip(_SECTIONS, counts)):
        a0, a1 = i * step + gap, (i + 1) * step - gap
        mid = (a0 + a1) / 2
        # Area, not radius, in proportion to the count: an annulus grows with the square of its
        # outer radius, so a linear radius would make the biggest section look several times bigger.
        r = math.sqrt(HUB**2 + (RIM**2 - HUB**2) * n / most)
        description = _descriptions.get(slug, "")
        tooltip = f"{' '.join(label)}: {n} {'study' if n == 1 else 'studies'}"
        if description:
            tooltip += f" — {description}"

        out.append(f'<a href="{up}{slug}/" class="sw-sector">')
        out.append(f"<title>{escape(tooltip)}</title>")
        out.append(f'<path class="sw-track" d="{_wedge(a0, a1, HUB + 4, RIM)}" fill="{BLUE_TINT}" fill-opacity="0.45"/>')
        out.append(f'<path class="sw-bar" d="{_wedge(a0, a1, HUB + 4, r)}" fill="{BLUE}"/>')

        if r - HUB > 44:
            x, y = _point(mid, r - 20)
            out.append(_text(x, y + 6, str(n), 17, fill=PAPER, weight="bold"))
        else:
            x, y = _point(mid, r + 16)
            out.append(_text(x, y + 6, str(n), 17, weight="bold"))

        x, y = _point(mid, LABEL_R)
        sin = math.sin(mid)
        anchor = "middle" if abs(sin) < 0.3 else ("start" if sin > 0 else "end")
        # Labels below the equator hang down from their anchor point, above it they stack up to it.
        lines = len(label)
        top = y + 6 - (lines - 1) * 19 if math.cos(mid) > 0.3 else y + 6 + (8 if math.cos(mid) < -0.3 else 0)
        for j, line in enumerate(label):
            out.append(_text(x, top + j * 19, line, 17, anchor, cls="sw-label"))
        out.append("</a>")

    out += [
        f'<circle cx="{CX}" cy="{CY}" r="{HUB}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>',
        f'<circle cx="{CX}" cy="{CY}" r="{HUB - 7}" fill="none" stroke="{GOLD_EDGE}" stroke-width="0.8"/>',
        _text(CX, CY - 26, "THE WAY", 16, weight="bold"),
        _text(CX, CY + 2, "ὁδός", 22, italic=True),
        _text(CX, CY + 32, str(total), 26, weight="bold"),
        _text(CX, CY + 50, "studies", 13, fill=MUTED, italic=True),
        _text(CX, H - 26, "Wedge area in proportion to the number of studies · select a wedge to open its section",
              12, fill=MUTED, italic=True),
        "</svg>",
    ]
    return '<figure class="subject-wheel-figure">' + "".join(out) + "</figure>"
