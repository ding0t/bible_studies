"""Draw the two plates for last-things/ezekiels-temple.md, in the Larkin hand of utils/lib/larkin.py.

    python3 utils/build_ezekiel_temple_graphics.py                     # both
    python3 utils/build_ezekiel_temple_graphics.py route-of-the-glory

route-of-the-glory is a relationship plate: the glory's departure (Ezekiel 8-11) and return
(Ezekiel 43-44) drawn on one west-to-east profile of the temple, the city and the mountain east of
it, with the road Jesus walked beneath. Ezekiel's stages are solid because the text states them; the
Jesus panel is dashed because its link to Ezekiel is a pattern no New Testament writer draws.

ezekiels-river is an imagery plate of Ezekiel 47:1-12, every detail numbered against its verse, with
the depth strip (ankle, knee, waist, swimming, at each thousand cubits) and Revelation 22:1-2 beside it.
"""

import sys
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, GOLD, GOLD_EDGE, GOLD_TINT, BLUE, BLUE_TINT,
                        EARTH_TINT, HALO, text, svg_open, heading, arrow_head, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "last-things"

WATER = "#5b7fa6"
WATER_DEEP = "#2f557f"
SALT = "#f4f1e6"
LEAF = "#5f7d3a"
LEAF_DARK = "#3f5a24"
SKY_TOP = "#f3e6c4"
SKY_LOW = "#fbf3df"
HILL = "#d9c59b"
HILL_DARK = "#b9a173"
DEAD_SEA = "#7fa3b8"


def lines_at(x, y, rows, size=13, lh=17, anchor="start", **kw):
    return [text(x, y + i * lh, r, size, anchor, **kw) for i, r in enumerate(rows)]


def callout(n, x, y, r=11, fill=INK, ink=PAPER):
    return [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{PAPER}" stroke-width="1.5"/>',
            text(x, y + r * 0.42, str(n), r * 1.15, "middle", "bold", fill=ink)]


def person(cx, base, s=1.0, fill=INK):
    """A stick figure standing on (cx, base)."""
    return (f'<g stroke="{fill}" stroke-width="{2 * s:.1f}" fill="none" stroke-linecap="round">'
            f'<circle cx="{cx}" cy="{base - 26 * s:.1f}" r="{5 * s:.1f}" fill="{fill}"/>'
            f'<path d="M{cx} {base - 21 * s:.1f} V{base - 9 * s:.1f} M{cx - 7 * s:.1f} {base - 17 * s:.1f} '
            f'H{cx + 7 * s:.1f} M{cx} {base - 9 * s:.1f} L{cx - 5 * s:.1f} {base} M{cx} {base - 9 * s:.1f} '
            f'L{cx + 5 * s:.1f} {base}"/></g>')


def wave(x0, x1, y, amp=3, period=16, colour="#ffffff", width=1.4, opacity=0.6):
    d, x = [f"M{x0:.1f} {y:.1f}"], x0
    while x + period <= x1:
        d.append(f"q{period / 4} {-amp} {period / 2} 0 t{period / 2} 0")
        x += period
    return (f'<path d="{" ".join(d)}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'opacity="{opacity}"/>')


def tree(cx, base, h=34, s=1.0):
    return (f'<path d="M{cx} {base} V{base - h * 0.45 * s:.1f}" stroke="#6b4a2a" stroke-width="{2.4 * s:.1f}"/>'
            f'<circle cx="{cx}" cy="{base - h * 0.62 * s:.1f}" r="{h * 0.3 * s:.1f}" fill="{LEAF}" '
            f'stroke="{LEAF_DARK}" stroke-width="1"/>'
            f'<circle cx="{cx - h * 0.16 * s:.1f}" cy="{base - h * 0.5 * s:.1f}" r="{h * 0.2 * s:.1f}" fill="{LEAF}"/>'
            f'<circle cx="{cx + h * 0.17 * s:.1f}" cy="{base - h * 0.52 * s:.1f}" r="{h * 0.21 * s:.1f}" fill="{LEAF}"/>'
            f'<circle cx="{cx + 3 * s:.1f}" cy="{base - h * 0.66 * s:.1f}" r="{2.2 * s:.1f}" fill="#c4471c"/>'
            f'<circle cx="{cx - 6 * s:.1f}" cy="{base - h * 0.55 * s:.1f}" r="{2.2 * s:.1f}" fill="#c4471c"/>')


def temple(x, base, s=1.0, fill=CARD):
    """The house in profile: a raised hall with its porch to the east (right)."""
    w, hh = 74 * s, 46 * s
    return [f'<rect x="{x:.1f}" y="{base - hh:.1f}" width="{w:.1f}" height="{hh:.1f}" fill="{fill}" stroke="{INK}" stroke-width="1.6"/>',
            f'<rect x="{x + w:.1f}" y="{base - hh * 0.72:.1f}" width="{14 * s:.1f}" height="{hh * 0.72:.1f}" fill="{fill}" stroke="{INK}" stroke-width="1.4"/>',
            f'<path d="M{x - 4 * s:.1f} {base - hh:.1f} H{x + w + 4 * s:.1f}" stroke="{INK}" stroke-width="2"/>']


def gate(x, base, shut=False, s=1.0):
    gw, gh = 34 * s, 40 * s
    out = [f'<rect x="{x - gw / 2:.1f}" y="{base - gh:.1f}" width="{gw:.1f}" height="{gh:.1f}" fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.5"/>',
           f'<path d="M{x - gw / 2 + 7 * s:.1f} {base} V{base - gh + 16 * s:.1f} a{gw / 2 - 7 * s:.1f} {gw / 2 - 7 * s:.1f} 0 0 1 {gw - 14 * s:.1f} 0 V{base}" '
           f'fill="{INK if shut else PAPER}" stroke="{INK}" stroke-width="1.2"/>']
    if shut:
        out.append(f'<path d="M{x - 8 * s:.1f} {base - 12 * s:.1f} H{x + 8 * s:.1f}" stroke="{GOLD}" stroke-width="2.5"/>')
    return out


# ---------------------------------------------------------------------------------------------
# 1. The route of the glory

ROUTE_OUT = [  # Ezekiel 8-11: (stop label, reference, x on the profile)
    ("From the cherub to the threshold", "Ezekiel 9:3; 10:4", 150),
    ("Out to the east gate", "Ezekiel 10:18-19", 265),
    ("Stood on the mountain east of the city", "Ezekiel 11:22-23", 560),
]
ROUTE_IN = [  # Ezekiel 43-44
    ("Comes from the east, “like the sound of many waters”", "Ezekiel 43:2", 655),
    ("Enters by the gate facing east", "Ezekiel 43:4", 265),
    ("Fills the house: “the place of my throne”", "Ezekiel 43:5-7", 150),
    ("The east gate shut: “the LORD… has entered by it”", "Ezekiel 44:1-2", 265),
]
JESUS_ROAD = [
    ("Comes down the Mount of Olives and weeps over the city", "Luke 19:37, 41-44"),
    ("“Your house is left to you desolate… until you say…”", "Matthew 23:38-39"),
    ("Leaves the temple and sits on the Mount of Olives", "Matthew 24:1-3"),
    ("Taken up from “the mount called Olivet”", "Acts 1:9-12"),
    ("“His feet shall stand on the Mount of Olives”", "Zechariah 14:4"),
]


def profile(y0, scale=1.0, label=True):
    """Temple, east gate, city wall, the Kidron, the mountain: west (left) to east (right)."""
    g = y0
    out = [f'<path d="M30 {g} H330 Q370 {g} 400 {g + 26 * scale:.1f} Q430 {g + 40 * scale:.1f} 460 {g + 26 * scale:.1f} '
           f'Q520 {g - 70 * scale:.1f} 570 {g - 82 * scale:.1f} Q630 {g - 76 * scale:.1f} 690 {g - 30 * scale:.1f} V{g + 60 * scale:.1f} H30 Z" '
           f'fill="{HILL}" stroke="{HILL_DARK}" stroke-width="1.4"/>']
    for x in range(150, 690, 24):  # olive trees on the slope
        if 470 < x < 680:
            yy = g - 70 * scale * (1 - abs(x - 570) / 130) if abs(x - 570) < 130 else g
            out.append(f'<circle cx="{x}" cy="{yy - 5:.1f}" r="5" fill="#8a9a5b" opacity="0.8"/>')
    out += temple(113, g, 1.0)
    out += gate(265, g)
    out.append(f'<rect x="322" y="{g - 30}" width="14" height="30" fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.2"/>')
    if label:
        out.append(text(150, g + 22, "the house", 12, "middle", italic=True, fill=MUTED))
        out.append(text(265, g + 22, "east gate", 12, "middle", italic=True, fill=MUTED))
        out.append(text(329, g + 22, "city wall", 11.5, "middle", italic=True, fill=MUTED))
        out.append(text(430, g + 56 * scale, "Kidron", 11.5, "middle", italic=True, fill=MUTED))
        out.append(text(468, g - 52 * scale, "the mountain east of the city", 12, "end", italic=True, fill=INK))
        out.append(text(468, g - 52 * scale + 15, "named in Zechariah 14:4:", 11.5, "end", italic=True, fill=MUTED))
        out.append(text(468, g - 52 * scale + 29, "the Mount of Olives", 11.5, "end", italic=True, fill=MUTED))
    out.append(text(40, g + 48 * scale, "WEST", 11, weight="bold", fill=MUTED, spacing="2"))
    out.append(text(680, g + 48 * scale, "EAST", 11, "end", weight="bold", fill=MUTED, spacing="2"))
    return out


def route_of_the_glory():
    h = 1500
    out = svg_open(
        h,
        "The route of the glory",
        "A plate in three parts on one west-to-east profile of the temple, its east gate, the city wall, "
        "the Kidron valley and the mountain east of the city. Above, Ezekiel 8-11, drawn solid: the glory "
        "goes from the cherub to the threshold (Ezekiel 9:3; 10:4), out to the east gate (Ezekiel "
        "10:18-19), and stands on the mountain east of the city (Ezekiel 11:22-23). In the middle, "
        "Ezekiel 43-44, drawn solid: the glory comes from the east with a sound like many waters "
        "(Ezekiel 43:2), enters by the east gate (Ezekiel 43:4), fills the house, the place of the LORD's "
        "throne (Ezekiel 43:5-7), and the east gate is shut because the LORD has entered by it (Ezekiel "
        "44:1-2). Zechariah 14:4 names the mountain: the Mount of Olives. Below, in a dashed frame "
        "because no New Testament writer draws the link, the road Jesus walked: down the Mount of Olives "
        "weeping over the city (Luke 19:37, 41-44), 'your house is left to you desolate' (Matthew "
        "23:38-39), out of the temple to the Mount of Olives (Matthew 24:1-3), taken up from Olivet (Acts "
        "1:9-12), and his feet standing on the Mount of Olives (Zechariah 14:4). The plate closes with "
        "Ezekiel 43:7.",
    )
    out.append('<defs><linearGradient id="rg-sky" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>'
               '<radialGradient id="rg-glow" cx="0.5" cy="0.5" r="0.5">'
               '<stop offset="0" stop-color="#fff6d0" stop-opacity="1"/>'
               f'<stop offset="0.5" stop-color="{GOLD}" stop-opacity="0.75"/>'
               f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient></defs>')
    out += heading("The Route of the Glory", "Ezekiel 8-11 and 43-44, and the road Jesus walked")

    def panel(y, label, hh, dashed=False):
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        return [text(30, y - 10, label, 13, weight="bold", fill=MUTED, spacing="1.5"),
                f'<rect x="30" y="{y}" width="660" height="{hh}" rx="4" fill="url(#rg-sky)" stroke="{INK}" stroke-width="1.8"{dash}/>']

    def glow(x, y, r=16):
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#rg-glow)"/>'

    # A. The glory goes out.
    ay = 130
    out += panel(ay, "EZEKIEL 8-11 · THE GLORY GOES OUT (592 BC)", 250)
    g = ay + 200
    out += profile(g)
    path = [(150, g - 70), (265, g - 80), (560, g - 150)]
    out.append(f'<path d="M{path[0][0]} {path[0][1]} Q205 {g - 120} {path[1][0]} {path[1][1]} '
               f'Q420 {g - 175} {path[2][0]} {path[2][1]}" fill="none" stroke="{GOLD_EDGE}" stroke-width="3.5"/>')
    out.append(arrow_head(path[2][0], path[2][1], -8, 12, GOLD_EDGE))
    for i, (x, y) in enumerate(path):
        out.append(glow(x, y, 18))
        out += callout(i + 1, x, y - 24)

    # B. The glory comes back.
    by = ay + 300
    out += panel(by, "EZEKIEL 43-44 · THE GLORY COMES BACK (573 BC)", 250)
    g2 = by + 200
    out += profile(g2)
    out.append(f'<path d="M680 {g2 - 150} Q600 {g2 - 190} 470 {g2 - 130} Q360 {g2 - 82} 285 {g2 - 72}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3.5"/>')
    out.append(f'<path d="M245 {g2 - 66} Q205 {g2 - 64} 170 {g2 - 60}" fill="none" stroke="{GOLD_EDGE}" stroke-width="3.5"/>')
    out.append(arrow_head(170, g2 - 60, 180, 12, GOLD_EDGE))
    for k in range(3):  # "the sound of many waters"
        out.append(f'<path d="M{652 - k * 10} {g2 - 182 + k * 6} q-8 10 0 20" fill="none" stroke="{BLUE}" '
                   f'stroke-width="1.4" opacity="{0.8 - k * 0.2:.1f}"/>')
    out.append(f'<rect x="113" y="{g2 - 46}" width="88" height="46" fill="{GOLD}" opacity="0.35"/>')
    out.append(glow(150, g2 - 60, 34))
    out += gate(265, g2, shut=True)
    for i, (x, y) in enumerate([(655, g2 - 150), (265, g2 - 78), (150, g2 - 60), (265, g2 - 2)]):
        out += callout(i + 4, x + (22 if i == 3 else 0), y - (24 if i < 3 else 30))

    # Key for A and B.
    ky = by + 286
    rows = [(n + 1, s, r) for n, (s, r, _) in enumerate(ROUTE_OUT)] + \
           [(n + 4, s, r) for n, (s, r, _) in enumerate(ROUTE_IN)]
    for i, (n, s, ref) in enumerate(rows):
        y = ky + i * 23
        out += callout(n, 44, y - 4, r=9)
        out.append(text(62, y, s, 13))
        out.append(text(690, y, ref, 12, "end", italic=True, fill=MUTED))

    # C. The road Jesus walked: a pattern, so dashed.
    cy = ky + len(rows) * 23 + 46
    out += panel(cy, "A PATTERN · THE ROAD JESUS WALKED", 240, dashed=True)
    g3 = cy + 190
    out += profile(g3, scale=0.8, label=False)
    stops = [(505, g3 - 34), (165, g3 - 58), (548, g3 - 62), (600, g3 - 160), (612, g3 - 64)]
    out.append(f'<path d="M{stops[0][0]} {stops[0][1]} Q330 {g3 - 110} {stops[1][0]} {stops[1][1]}" fill="none" '
               f'stroke="{BLUE}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    out.append(arrow_head(stops[1][0], stops[1][1], 170, 10, BLUE))
    out.append(f'<path d="M190 {g3 - 70} Q380 {g3 - 170} {stops[2][0] - 6} {stops[2][1] - 6}" fill="none" '
               f'stroke="{BLUE}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    out.append(arrow_head(stops[2][0] - 6, stops[2][1] - 6, 45, 10, BLUE))
    out.append(f'<path d="M{stops[2][0] + 10} {stops[2][1] - 12} L{stops[3][0]} {stops[3][1] + 10}" stroke="{BLUE}" '
               f'stroke-width="2.4" stroke-dasharray="6 4"/>')
    out.append(arrow_head(stops[3][0], stops[3][1] + 10, -70, 10, BLUE))
    out.append(f'<path d="M{stops[3][0] + 14} {stops[3][1] + 6} Q650 {g3 - 120} {stops[4][0] + 2} {stops[4][1] - 6}" '
               f'fill="none" stroke="{BLUE}" stroke-width="2.4" stroke-dasharray="2 5"/>')
    out.append(arrow_head(stops[4][0] + 2, stops[4][1] - 6, 110, 10, BLUE))
    for i, (x, y) in enumerate(stops):
        out += callout(chr(65 + i), x + (16 if i in (2, 4) else 0), y - 18, fill=BLUE)
    ky2 = cy + 268
    for i, (s, ref) in enumerate(JESUS_ROAD):
        y = ky2 + i * 23
        out += callout(chr(65 + i), 44, y - 4, r=9, fill=BLUE)
        out.append(text(62, y, s, 13))
        out.append(text(690, y, ref, 12, "end", italic=True, fill=MUTED))
    ny = ky2 + len(JESUS_ROAD) * 23 + 6
    out.append(f'<path d="M34 {ny - 4} h22" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    out += lines_at(62, ny, ["Dashed: the events are stated; their link to Ezekiel 11:23 and 43:2 is a pattern no",
                             "New Testament writer draws. E is still to come."], 12.5, italic=True, fill=MUTED)

    # Close on the theology.
    fy = ny + 62
    out.append(f'<path d="M{W / 2 - 150} {fy - 26} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>')
    out += lines_at(W / 2, fy, ["“This is the place of my throne and the place of the soles of my feet,",
                                "where I will dwell in the midst of the people of Israel forever.”"],
                    15, 20, anchor="middle", italic=True)
    out.append(text(W / 2, fy + 46, "Ezekiel 43:7, ESV", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 2. Ezekiel's river

DEPTHS = [  # (cubits, depth word, verse, water level as a share of a standing figure's height)
    (1000, "ankle-deep", "Ezekiel 47:3", 0.08),
    (2000, "knee-deep", "Ezekiel 47:4", 0.3),
    (3000, "waist-deep", "Ezekiel 47:4", 0.55),
    (4000, "deep enough to swim in", "Ezekiel 47:5", 1.25),
]
RIVER_KEY = [
    ("“water was issuing from below the threshold of the temple toward the east”", "Ezekiel 47:1"),
    ("A thousand cubits: “it was ankle-deep”", "Ezekiel 47:3"),
    ("Two thousand: “it was knee-deep”", "Ezekiel 47:4"),
    ("Three thousand: “it was waist-deep”", "Ezekiel 47:4"),
    ("Four thousand: “deep enough to swim in, a river that could not be passed through”", "Ezekiel 47:5"),
    ("“very many trees on the one side and on the other” · “their leaves for healing”", "Ezekiel 47:7, 12"),
    ("“goes down into the Arabah, and enters the sea… the water will become fresh”", "Ezekiel 47:8"),
    ("“Fishermen will stand beside the sea. From Engedi to Eneglaim”", "Ezekiel 47:10"),
    ("“its swamps and marshes will not become fresh; they are to be left for salt”", "Ezekiel 47:11"),
]


def ezekiels_river():
    h = 1560
    out = svg_open(
        h,
        "Ezekiel's river",
        "An illustrated plate of Ezekiel 47:1-12. Above, a scene from the temple on its mountain down to "
        "the Dead Sea, with numbered callouts: 1, water issues from below the threshold toward the east "
        "(Ezekiel 47:1); 2 to 5, at each thousand cubits the river is ankle-deep, knee-deep, waist-deep, "
        "and then deep enough to swim in, a river that cannot be crossed (Ezekiel 47:3-5); 6, very many "
        "trees on both banks, with fruit every month and leaves for healing (Ezekiel 47:7, 12); 7, the "
        "river goes down into the Arabah and the sea becomes fresh (Ezekiel 47:8); 8, fishermen spread "
        "nets from Engedi to Eneglaim (Ezekiel 47:10); 9, the swamps and marshes are left for salt "
        "(Ezekiel 47:11). A dashed note says the river's course is not mapped and Eneglaim's site is not "
        "known. Below, a strip shows the four depths on a standing figure at 1,000, 2,000, 3,000 and "
        "4,000 cubits. Beside it, Revelation 22:1-2: the river of the water of life from the throne of "
        "God and of the Lamb, the tree of life on either side, and no sea (Revelation 21:1). The plate "
        "closes with Ezekiel 47:9: everything will live where the river goes.",
    )
    out.append('<defs>'
               '<linearGradient id="er-sky" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#f6d995"/><stop offset="0.55" stop-color="#fbeccb"/>'
               f'<stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>'
               '<linearGradient id="er-water" x1="0" y1="0" x2="1" y2="1">'
               f'<stop offset="0" stop-color="#8fb3d1"/><stop offset="1" stop-color="{WATER_DEEP}"/></linearGradient>'
               '<linearGradient id="er-sea" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{DEAD_SEA}"/><stop offset="1" stop-color="{WATER_DEEP}"/></linearGradient>'
               '<radialGradient id="er-glow" cx="0.5" cy="0.5" r="0.5">'
               '<stop offset="0" stop-color="#fff8dc" stop-opacity="1"/>'
               f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
               '<clipPath id="er-scene"><rect x="30" y="130" width="660" height="520" rx="4"/></clipPath>'
               '</defs>')
    out += heading("Ezekiel’s River", "Ezekiel 47:1-12, from the threshold to the sea")

    x0, x1, top, bot = 30, 690, 130, 650
    out.append('<g clip-path="url(#er-scene)">')
    out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bot - top}" fill="url(#er-sky)"/>')
    # The mountain the house stands on (Ezekiel 40:2), falling east to the Arabah.
    out.append(f'<path d="M30 300 Q110 230 200 250 Q300 280 380 380 Q470 470 560 500 Q630 520 690 520 V650 H30 Z" '
               f'fill="{HILL}" stroke="{HILL_DARK}" stroke-width="1.5"/>')
    out.append(f'<path d="M30 360 Q160 330 260 380 Q360 440 460 520 Q540 570 690 580 V650 H30 Z" '
               f'fill="{HILL_DARK}" opacity="0.45"/>')
    out.append(f'<circle cx="150" cy="210" r="90" fill="url(#er-glow)"/>')
    out += temple(108, 252, 1.0)
    # The sea, healed, with the marshes left for salt along its southern edge.
    out.append(f'<path d="M470 560 Q560 528 690 530 V650 H440 Q440 600 470 560 Z" fill="url(#er-sea)"/>')
    for yy in (560, 580, 602, 624):
        out.append(wave(470 if yy > 570 else 520, 688, yy, colour="#ffffff", opacity=0.45))
    out.append(f'<path d="M440 650 Q450 615 476 600 Q470 630 500 650 Z" fill="{SALT}" stroke="#d8d0b8" stroke-width="1"/>')
    for sx, sy in [(452, 636), (466, 624), (480, 642), (458, 646)]:
        out.append(f'<circle cx="{sx}" cy="{sy}" r="1.6" fill="#c9bfa4"/>')
    # The river: a thread at the threshold, widening at each thousand cubits.
    river = [(190, 250, 2), (240, 290, 6), (300, 345, 12), (360, 400, 20), (420, 470, 32), (480, 548, 44)]
    for (ax, ay, aw), (bx, by, bw) in zip(river, river[1:]):
        out.append(f'<path d="M{ax} {ay} Q{(ax + bx) / 2 + 12} {(ay + by) / 2 - 10} {bx} {by}" '
                   f'stroke="url(#er-water)" stroke-width="{(aw + bw) / 2}" stroke-linecap="round" fill="none"/>')
    for (ax, ay, aw), (bx, by, bw) in zip(river[2:], river[3:]):
        out.append(wave(ax + 4, bx - 6, (ay + by) / 2 - 4, amp=2, period=12, opacity=0.5))
    # Trees on both banks (Ezekiel 47:7, 12).
    for tx, ty in [(250, 268), (232, 318), (318, 322), (290, 372), (372, 378), (350, 428), (432, 444),
                   (400, 492), (500, 520), (446, 520)]:
        out.append(tree(tx, ty, 30, 1.0))
    # Fishermen and their nets on the shore (Ezekiel 47:10).
    for fx in (560, 612, 664):
        out.append(person(fx, 532, 0.8))
        out.append(f'<path d="M{fx + 6} 520 l14 14 M{fx + 6} 520 l-2 18" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<path d="M572 538 q20 18 40 0 M624 538 q20 18 40 0" fill="none" stroke="{INK}" stroke-width="1" '
               f'stroke-dasharray="2 2"/>')
    for fx, fy in [(540, 600), (600, 590), (650, 612), (510, 622)]:
        out.append(f'<path d="M{fx} {fy} q8 -5 16 0 q-8 5 -16 0 Z M{fx + 16} {fy} l6 -4 v8 Z" fill="#e6eef4"/>')
    out.append(text(612, 494, "Engedi … Eneglaim", 12.5, "middle", italic=True, fill=INK, extra=HALO))
    out.append(text(560, 642, "the sea", 12, "middle", italic=True, fill=PAPER))
    out.append('</g>')
    out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bot - top}" rx="4" fill="none" stroke="{INK}" stroke-width="2"/>')
    for n, x, y in [(1, 196, 226), (2, 248, 270), (3, 312, 324), (4, 378, 384), (5, 452, 448), (6, 214, 330),
                    (7, 520, 494), (8, 540, 470), (9, 470, 600)]:
        out += callout(n, x, y)

    ky = bot + 32
    for i, (q, ref) in enumerate(RIVER_KEY):
        y = ky + i * 23
        out += callout(i + 1, 44, y - 4, r=9)
        out.append(text(62, y, q, 12.5))
        out.append(text(x1, y, ref, 12, "end", italic=True, fill=MUTED))
    ny = ky + len(RIVER_KEY) * 23 + 2
    out.append(f'<path d="M34 {ny - 4} h22" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    out += lines_at(62, ny, ["Not stated: the river's course between the house and the Arabah. Eneglaim's site is",
                             "not known (the best proposed site scores 120 of 1000 in OpenBible.info)."], 12.5,
                    italic=True, fill=MUTED)

    # The depth strip: Scripture measures the rise, so the strip shows it.
    sy = ny + 66
    out.append(text(30, sy - 12, "THE RISE · A THOUSAND CUBITS AT A TIME", 13, weight="bold", fill=MUTED, spacing="1.5"))
    cw, sh = 165, 150
    for i, (cubits, word, ref, level) in enumerate(DEPTHS):
        cx = 30 + i * cw
        out.append(f'<rect x="{cx}" y="{sy}" width="{cw}" height="{sh}" fill="{SKY_LOW}" stroke="{INK}" stroke-width="1.2"/>')
        base = sy + sh - 22
        fig = 64
        wl = base - fig * min(level, 1.0) if level <= 1 else sy + 62
        out.append(f'<rect x="{cx + 1}" y="{wl:.1f}" width="{cw - 2}" height="{sy + sh - wl - 1:.1f}" fill="{WATER}" opacity="0.55"/>')
        out.append(wave(cx + 6, cx + cw - 6, wl, colour="#ffffff", opacity=0.8))
        if level <= 1:
            out.append(person(cx + cw / 2, base, 2.4))
        else:  # swimming: the figure lies on the surface
            out.append(f'<g transform="rotate(-80 {cx + cw / 2} {wl + 14:.1f})">{person(cx + cw / 2, wl + 40, 2.0)}</g>')
        out.append(text(cx + cw / 2, sy + 18, f"{cubits:,} cubits", 13, "middle", "bold"))
        out.append(text(cx + cw / 2, sy + sh + 18, word, 12.5, "middle"))
        out.append(text(cx + cw / 2, sy + sh + 34, ref, 11.5, "middle", italic=True, fill=MUTED))
    out.append(text(W / 2, sy + sh + 56, "No tributary is named. The water rises from the threshold alone.", 12.5,
                    "middle", italic=True, fill=MUTED))

    # Revelation's river beside Ezekiel's.
    ry = sy + sh + 100
    out.append(text(30, ry - 12, "THE SECOND WITNESS · REVELATION 22:1-2", 13, weight="bold", fill=MUTED, spacing="1.5"))
    rh = 190
    out.append(f'<rect x="30" y="{ry}" width="660" height="{rh}" rx="4" fill="{GOLD_TINT}" stroke="{INK}" stroke-width="1.8"/>')
    tx = 160
    out.append(f'<circle cx="{tx}" cy="{ry + 50}" r="46" fill="url(#er-glow)"/>')
    out.append(f'<path d="M{tx - 22} {ry + 66} V{ry + 30} Q{tx} {ry + 16} {tx + 22} {ry + 30} V{ry + 66} Z" '
               f'fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>')
    out.append(f'<path d="M{tx} {ry + 66} Q{tx + 6} {ry + 120} {tx} {ry + rh - 4}" stroke="#a9cbe6" stroke-width="14" fill="none"/>')
    out.append(tree(tx - 34, ry + 150, 46, 1.0))
    out.append(tree(tx + 36, ry + 150, 46, 1.0))
    out += lines_at(260, ry + 34, [
        "“the river of the water of life, bright as crystal,",
        "flowing from the throne of God and of the Lamb”",
    ], 13, 17, italic=True)
    out.append(text(260, ry + 72, "Revelation 22:1", 12, italic=True, fill=MUTED))
    out += lines_at(260, ry + 102, [
        "“on either side of the river, the tree of life… The leaves",
        "of the tree were for the healing of the nations”",
    ], 13, 17, italic=True)
    out.append(text(260, ry + 140, "Revelation 22:2", 12, italic=True, fill=MUTED))
    out.append(text(260, ry + 170, "No sea is drawn: “the sea was no more” (Revelation 21:1).", 12.5, fill=INK))

    fy = ry + rh + 56
    out.append(f'<path d="M{W / 2 - 150} {fy - 26} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>')
    out += lines_at(W / 2, fy, ["“And wherever the river goes, every living creature that swarms will live…",
                                "so everything will live where the river goes.”"], 15, 20, anchor="middle", italic=True)
    out.append(text(W / 2, fy + 46, "Ezekiel 47:9, ESV", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


CHARTS = {
    "route-of-the-glory": route_of_the_glory,
    "ezekiels-river": ezekiels_river,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or CHARTS:
        (OUT / f"{name}.svg").write_text(CHARTS[name]() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
