"""Draw the chart for scripture/what-literary-criticism-declares.md in the Larkin hand.

    python3 utils/build_criticism_graphics.py

Arcs come from docs/data/unity-measures.json (references/build/unity_measures.py: OpenBible
cross-references with ten or more votes, each end placed at the middle of its book's date range on
that scheme) and the era labels from docs/data/book-authorship.toml, so a corrected date is one
edit and two re-runs. Harrison and Romhild's 2007 arc diagram laid the same cross-references out in
canon order; this one lays them out by when each book was written.
"""

import json
import math
import tomllib
from pathlib import Path

from lib.larkin import (W, INK, MUTED, RED, BLUE, GOLD_EDGE, HALO, text, svg_open, heading, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "what-literary-criticism-declares"
MEASURES = json.loads((ROOT / "docs" / "data" / "unity-measures.json").read_text(encoding="utf-8"))
BOOKS = {b["id"]: b for b in tomllib.loads(
    (ROOT / "docs" / "data" / "book-authorship.toml").read_text(encoding="utf-8"))["book"]}

YEAR_FROM, YEAR_TO = -1500, 150
X0, X1 = 44, W - 44
ARC_RISE = 0.62
FAR = 1000
MIDDLE = 500


def x_of(year):
    return X0 + (year - YEAR_FROM) / (YEAR_TO - YEAR_FROM) * (X1 - X0)


def year_label(y):
    return f"{-y} BC" if y < 0 else ("AD 1" if y == 0 else f"AD {y}")


def mid(book_id, scheme, part=None):
    b = BOOKS[book_id]
    if scheme == "critical":
        if part is not None:
            return sum(b["critical_parts"][part]["date"]) / 2
        if "critical" in b:
            return sum(b["critical"]) / 2
    return sum(b["date"]) / 2


def colour(gap):
    return RED if gap >= FAR else BLUE if gap >= MIDDLE else MUTED


def panel(y_axis, scheme, title, labels):
    out = [text(X0, y_axis - 205, title, 16, weight="bold")]
    arcs = MEASURES["links"][scheme]["arcs"]
    # draw the short, common arcs first so the long ones stay visible on top
    for a, b, n in sorted(arcs, key=lambda r: r[1] - r[0]):
        xa, xb = x_of(a), x_of(b)
        r = (xb - xa) / 2
        if r < 0.5:
            continue
        opacity = min(0.85, 0.08 + 0.16 * math.log10(n))
        width = 0.5 + 0.45 * math.log10(n)
        out.append(f'<path d="M{xa:.1f} {y_axis} A{r:.1f} {r * ARC_RISE:.1f} 0 0 1 {xb:.1f} {y_axis}" '
                   f'fill="none" stroke="{colour(b - a)}" stroke-width="{width:.2f}" '
                   f'stroke-opacity="{opacity:.2f}"/>')
    out.append(f'<path d="M{X0} {y_axis} H{X1}" stroke="{INK}" stroke-width="1.6"/>')
    for i, (label, year) in enumerate(labels):
        x = x_of(year)
        y = y_axis + 40 + (i % 2) * 17
        out.append(f'<circle cx="{x:.1f}" cy="{y_axis}" r="3" fill="{GOLD_EDGE}"/>')
        out.append(f'<path d="M{x:.1f} {y_axis + 4} V{y - 12}" stroke="{GOLD_EDGE}" stroke-width="0.8"/>')
        out.append(text(x, y, label, 13, "middle", extra=HALO))
    for year in (-1500, -1000, -500, 0):
        x = x_of(year)
        out.append(f'<path d="M{x:.1f} {y_axis} v6" stroke="{INK}" stroke-width="1.2"/>')
        out.append(text(x, y_axis + 20, year_label(year), 12, "middle", fill=MUTED, extra=HALO))
    return out


def one_web():
    trad = MEASURES["links"]["traditional"]
    crit = MEASURES["links"]["critical"]
    links = trad["openbible_votes_10"]["links"]
    writers = MEASURES["network"]["writers_critical"]
    nt = [mid(b, "traditional") for b in ("Matt", "Rom", "Rev")]
    h = 818
    out = svg_open(
        h, "One web across the centuries",
        f"Two arc diagrams of the {links:,} cross-references that ten or more readers endorse, each "
        f"book placed on a line of time at the middle of its date range. On traditional dates "
        f"{trad['openbible_votes_10']['over_500_years']:.0%} of the links reach back more than 500 "
        f"years and {trad['openbible_votes_10']['over_1000_years']:.0%} more than 1,000. On the latest "
        f"dates critical scholarship gives, {crit['openbible_votes_10']['over_500_years']:.0%} still reach "
        f"back more than 500 years. On both, every one of the {writers['writers']} writers the critical "
        f"view counts is within {writers['most_steps_between_writers']} steps of every other. Red arcs "
        f"span 1,000 years or more, blue 500 to 1,000, grey under 500. A book the critical view gives "
        f"no date of its own, such as Psalms, keeps its traditional date.")
    out += heading("One web across the centuries",
                   "Cross-references placed by when each book was written, not by canon order")
    out += panel(330, "traditional", "Traditional dates", [
        ("Moses", mid("Gen", "traditional")), ("Psalms", mid("Ps", "traditional")),
        ("Isaiah", mid("Isa", "traditional")), ("Daniel", mid("Dan", "traditional")),
        ("Malachi", mid("Mal", "traditional")), ("New Testament", sum(nt) / 3)])
    out += panel(625, "critical", "Latest critical dates", [
        ("Psalms", mid("Ps", "critical")), ("Isaiah 1-39", mid("Isa", "critical", 0)), ("Isaiah 40-55", mid("Isa", "critical", 1)),
        ("Genesis", mid("Gen", "critical")), ("Daniel", mid("Dan", "critical")),
        ("New Testament", sum(mid(b, "critical") for b in ("Matt", "Rom", "Rev")) / 3)])
    y = 712
    for i, (fill, label) in enumerate(((RED, "1,000 years or more"), (BLUE, "500 to 1,000 years"),
                                       (MUTED, "under 500 years"))):
        x = X0 + i * 200
        out.append(f'<path d="M{x} {y} h34" stroke="{fill}" stroke-width="3"/>')
        out.append(text(x + 42, y + 5, label, 13))
    out.append(text(X0, y + 34, f"{links:,} links endorsed by ten or more readers (OpenBible.info). "
                    "Each end sits at the middle of its", 12.5, fill=MUTED, italic=True))
    out.append(text(X0, y + 52, "book's date range; Psalms spans Moses to the exile, so its links "
                    "meet at one point. A book the", 12.5, fill=MUTED, italic=True))
    out.append(text(X0, y + 70, "critical view gives no date of its own keeps its traditional date "
                    "(ESV Study Bible introductions).", 12.5, fill=MUTED, italic=True))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "one-web.svg").write_text(one_web(), encoding="utf-8")
    print("wrote", OUT / "one-web.svg")


if __name__ == "__main__":
    main()
