"""Draw the home page's banner: the way, one road through Scripture.

A sequence graphic. The road runs from Isaiah's "This is the way" to the believers Acts calls "the
Way", each milestone a verse that names the way (Hebrew derek, Greek hodos), and ends in the light
of the Father that John 14:6 says the way leads to. The milestones follow the order traced in
docs/content/jesus/the-way.md; the quotations are the ESV, checked against study-notes.db. Every
milestone is a text that says "way", so every card is drawn solid. Run from the repo root:

    python3 utils/build_home_graphics.py
"""

import math
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, GOLD, GOLD_EDGE, GOLD_TINT, EARTH_TINT, text,
                        svg_open, banner, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "about"

H = 466
ROAD = ((28, 286), (250, 316), (400, 110), (604, 140))
LIGHT = (650, 126)

# (x of the milestone, reference, ESV words a line at a time, above the road?)
MILESTONES = (
    (82, "Isaiah 30:21", ("“This is the way,", "walk in it”"), True),
    (162, "Isaiah 40:3", ("“prepare the way", "of the LORD”"), False),
    (242, "Malachi 3:1", ("“he will prepare", "the way before me”"), True),
    (322, "Mark 1:3", ("“Prepare the way", "of the Lord”"), False),
    (402, "John 14:6", ("“I am the way”",), True),
    (482, "Hebrews 10:20", ("“the new and", "living way”"), False),
    (562, "Acts 9:2", ("“belonging to", "the Way”"), True),
)
ERAS = ((36, 284, "THE PROPHETS"), (290, 448, "THE GOSPELS"), (454, 622, "THE CHURCH"))
CARD_W, LINE = 146, 16


def bezier(t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = ROAD
    u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
            u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)


def road_y(x):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if bezier(mid)[0] < x:
            lo = mid
        else:
            hi = mid
    return bezier(lo)[1]


def milestone(x, ref, words, above):
    y = road_y(x)
    card_h = 28 + LINE * len(words)
    gold = ref == "John 14:6"
    fill, stroke = (GOLD_TINT, GOLD_EDGE) if gold else (CARD, INK)
    top = y - 50 - card_h if above else y + 42
    stem0, stem1 = (top + card_h, y - 22) if above else (y + 22, top)
    return [
        f'<path d="M{x:.1f} {stem0:.1f} V{stem1:.1f}" stroke="{MUTED}" stroke-width="1"/>',
        # The milestone itself: a stone post at the roadside.
        f'<path d="M{x - 5:.1f} {y - (20 if above else -24):.1f} v-14 a5 5 0 0 1 10 0 v14 Z" '
        f'fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.2"/>' if above else
        f'<path d="M{x - 5:.1f} {y + 24:.1f} v-12 a5 5 0 0 1 10 0 v12 Z" '
        f'fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.2"/>',
        f'<rect x="{x - CARD_W / 2:.1f}" y="{top:.1f}" width="{CARD_W}" height="{card_h}" rx="5" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{1.8 if gold else 1.3}"/>',
        text(x, top + 18, ref, 13, "middle", "bold"),
    ] + [text(x, top + 36 + i * LINE, line, 12.5, "middle", fill=MUTED, italic=True)
         for i, line in enumerate(words)]


def walker(x, y, s=1.0):
    """A small, unindividuated figure on the road -- the believers of Acts 9:2, "men or women"."""
    return [
        f'<circle cx="{x:.1f}" cy="{y - 15 * s:.1f}" r="{3 * s:.1f}" fill="{INK}"/>',
        f'<path d="M{x:.1f} {y - 12 * s:.1f} L{x + 1 * s:.1f} {y - 4 * s:.1f} '
        f'M{x + 1 * s:.1f} {y - 4 * s:.1f} L{x - 3 * s:.1f} {y + 2 * s:.1f} '
        f'M{x + 1 * s:.1f} {y - 4 * s:.1f} L{x + 4 * s:.1f} {y + 2 * s:.1f} '
        f'M{x:.1f} {y - 10 * s:.1f} L{x + 4 * s:.1f} {y - 7 * s:.1f}" '
        f'stroke="{INK}" stroke-width="{1.6 * s:.1f}" stroke-linecap="round" fill="none"/>',
    ]


def the_way():
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = ROAD
    d = f"M{x0} {y0} C{x1} {y1} {x2} {y2} {x3} {y3}"
    lx, ly = LIGHT
    out = [
        '<defs><radialGradient id="glory" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0" stop-color="#fffbe9"/><stop offset="0.45" stop-color="{GOLD}"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient></defs>',
        # Upper left: the two words for the road.
        text(40, 60, "THE WAY", 24, weight="bold", spacing="2"),
        text(40, 84, "one road through Scripture", 14, fill=MUTED, italic=True),
        text(40, 118, "דֶּרֶךְ", 22),
        text(80, 118, "derek", 14, italic=True, fill=MUTED),
        text(128, 118, "·", 14, fill=MUTED),
        text(142, 118, "ὁδός", 20),
        text(192, 118, "hodos", 14, italic=True, fill=MUTED),
    ]
    # The Father's light at the road's end: rays, then the glow over them.
    for i in range(16):
        a = i * math.pi / 8
        out.append(f'<path d="M{lx + 30 * math.cos(a):.1f} {ly + 30 * math.sin(a):.1f} '
                   f'L{lx + 52 * math.cos(a):.1f} {ly + 52 * math.sin(a):.1f}" stroke="{GOLD_EDGE}" '
                   f'stroke-width="1.2" stroke-opacity="0.7"/>')
    out += [
        f'<circle cx="{lx}" cy="{ly}" r="50" fill="url(#glory)"/>',
        f'<circle cx="{lx}" cy="{ly}" r="22" fill="#fffbe9" stroke="{GOLD_EDGE}" stroke-width="1.2"/>',
        text(lx, ly + 80, "to the Father", 13, "middle", "bold"),
        text(lx, ly + 96, "John 14:6", 12, "middle", fill=MUTED, italic=True),
        # The road: an inked edge, the bed, the centre line.
        f'<path d="{d}" stroke="{INK}" stroke-width="30" fill="none" stroke-linecap="round"/>',
        f'<path d="{d}" stroke="{EARTH_TINT}" stroke-width="26" fill="none" stroke-linecap="round"/>',
        f'<path d="{d}" stroke="{MUTED}" stroke-width="1.4" fill="none" stroke-dasharray="9 8"/>',
    ]
    for x in (578, 590, 602):
        out += walker(x, road_y(x) + 6, 0.95)
    for m in MILESTONES:
        out += milestone(*m)
    for a, b, label in ERAS:
        out += banner((a + b) / 2, H - 64, b - a - 20, label, size=12)
    out.append(credit(H))

    desc = (
        "A road drawn rising from left to right across the plate, labelled with the Hebrew derek "
        "and the Greek hodos, the words for a road or way. Seven milestones stand beside it, each "
        "a verse that names the way, in the ESV: Isaiah 30:21, \"This is the way, walk in it\"; "
        "Isaiah 40:3, \"prepare the way of the LORD\"; Malachi 3:1, \"he will prepare the way "
        "before me\"; Mark 1:3, \"Prepare the way of the Lord\"; John 14:6, \"I am the way\", "
        "picked out in gold; Hebrews 10:20, \"the new and living way\"; and Acts 9:2, "
        "\"belonging to the Way\", beside three small figures walking the road. Ribbons beneath "
        "group them as the Prophets, the Gospels and the Church. The road ends in a circle of "
        "light, marked \"to the Father\" (John 14:6)."
    )
    return "\n".join(svg_open(H, "The Way: one road through Scripture", desc) + out + ["</svg>"]) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "the-way.svg"
    path.write_text(the_way(), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
