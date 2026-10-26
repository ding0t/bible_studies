"""Draw the prayer plates: three for christian-life/prayer-as-communion.md, and the household guide's
card and week emblems.

    python3 utils/build_prayer_graphics.py

daniel-at-the-window is an imagery plate of Daniel 6:10-11: every element is numbered against its
verse, and what the text leaves open (the hours, the number of windows, the words of the prayer) is
keyed as not stated. ephesians-3-prayer is a relationship diagram of Ephesians 3:14-21: the address,
the six appeals in their order, the dwelling-and-fullness words beside them, and the doxology. Solid
is Ephesians' own wording; dashed is the link to Colossians, which the study marks as its reading.
lords-prayer-shape is a relationship diagram of Matthew 6:9-13: the address and three "your"
petitions in heaven, "on earth as it is in heaven" as the hinge, three "us" petitions on earth, and
Gethsemane's "your will be done" (Matthew 26:42) beside the prayer's, the same Greek words. Dashed are
the doxology (a later addition the ESV footnotes) and the question of how far the hinge reaches.
seven-pictures is a card for christian-life/teaching-the-lords-prayer-at-home.md: each week's line,
its "what it shows about God" sentence and the picture of its story, ending on the four steps that
Prayer as Communion gives; week-1 to week-7 are the pictures alone, for the head of each week.
"""

import math
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, CLOUD, text, svg_open, heading, banner, arrow_head, card,
                        credit, esc)

OUT = Path(__file__).resolve().parent.parent / "docs" / "content" / "assets" / "img" / "prayer"

SKY_TOP = "#cfdbe6"
SKY_LOW = "#f3e2bd"
SKY_PALE = "#eef2f6"
SAND = "#e2cc9a"
SAND_DEEP = "#cdb07a"
BRICK = "#c9a77a"
BRICK_DARK = "#8d6c45"
ROOM = "#f4e8cf"
RUIN = "#9a8a72"
FIGURE = "#4a3a28"


def callout(n, x, y, r=11):
    return [f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>',
            text(x, y + 4.5, str(n), 13, "middle", "bold")]


def wrap(s, width):
    words, rows, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            rows.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    rows.append(cur)
    return rows


def kneeling(x, y, s=1.0, fill=FIGURE):
    """A small faceless figure kneeling, facing left; (x, y) is where the knees meet the floor."""
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{fill}">'
            f'<path d="M-2 0 H26 Q30 0 30 -4 L28 -8 H8 Z"/>'          # shins along the floor
            f'<path d="M6 -6 Q2 -26 10 -40 L22 -38 Q16 -22 24 -8 Z"/>'  # thigh and back, upright
            f'<path d="M12 -38 Q2 -34 -6 -40 L-4 -44 Q4 -40 12 -44 Z"/>'  # arms forward, hands raised
            f'<circle cx="17" cy="-49" r="7.5"/>'
            f'</g>')


def standing(x, y, s=1.0, fill=FIGURE):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{fill}">'
            f'<circle cx="0" cy="-40" r="6"/><path d="M-7 -32 H7 L9 -10 H5 L4 0 H-4 L-5 -10 H-9 Z"/>'
            f'</g>')


def daniel_at_the_window():
    h = 1120
    out = svg_open(
        h,
        "Daniel at the window",
        "An illustrated plate of Daniel 6:10-11. Above, a cut-away house in Babylon: in the upper "
        "chamber a small kneeling figure faces open windows toward Jerusalem, drawn far to the west "
        "across the desert with its walls broken and the temple burned (2 Kings 25:9-10). Seven "
        "numbered callouts quote the verses: the document signed; his house; windows in his upper "
        "chamber open toward Jerusalem; on his knees; three times a day he prayed and gave thanks, "
        "as he had done previously; the men who came by agreement and found him making petition and "
        "plea (Daniel 6:11); and Jerusalem. A dashed key line says the text does not state the hours, "
        "the number of windows, or the words he prayed. Below, two source cards: Solomon's prayer "
        "asking God to hear exiles who pray toward the land, the city and the house (1 Kings 8:48-49), "
        "and Jeremiah's letter to the exiles, that after seventy years 'you will call upon me "
        "and come and pray to me, and I will hear you' (Jeremiah 29:10-12; Daniel 9:2). At the foot, "
        "Daniel 9:18: 'because of your great mercy'.",
    )
    out.append(
        '<defs>'
        '<linearGradient id="dw-sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>'
        '<linearGradient id="dw-sand" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SAND}"/><stop offset="1" stop-color="{SAND_DEEP}"/></linearGradient>'
        '<radialGradient id="dw-lamp" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#fff3cf" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{ROOM}" stop-opacity="0"/></radialGradient>'
        '<clipPath id="dw-scene"><rect x="30" y="150" width="660" height="430" rx="4"/></clipPath>'
        '</defs>'
    )
    out += heading("Daniel at the Window", "Daniel 6:10-11 · Babylon, in the reign of Darius")
    out.append(text(30, 140, "THE UPPER CHAMBER · DANIEL 6:10-11", 13, weight="bold", fill=MUTED,
                    spacing="1.5"))

    x0, x1, top, hz, bot = 30, 690, 150, 330, 580
    out.append('<g clip-path="url(#dw-scene)">')
    out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{hz - top}" fill="url(#dw-sky)"/>')
    out.append(f'<rect x="{x0}" y="{hz}" width="{x1 - x0}" height="{bot - hz}" fill="url(#dw-sand)"/>')
    # Dunes receding west, to the left.
    for k, (y, a) in enumerate([(hz + 18, 0.35), (hz + 46, 0.3), (hz + 84, 0.25)]):
        out.append(f'<path d="M{x0} {y} Q120 {y - 14} 200 {y} T360 {y}" fill="none" stroke="{SAND_DEEP}" '
                   f'stroke-width="2" opacity="{a}"/>')
    # Jerusalem on the far horizon: broken wall, burned house, smoke long gone (no smoke drawn).
    jx = 92
    out.append(f'<path d="M{jx - 46} {hz} V{hz - 14} H{jx - 34} V{hz - 8} H{jx - 20} V{hz - 18} '
               f'H{jx - 10} V{hz - 6} H{jx + 6} V{hz - 20} L{jx + 12} {hz - 12} H{jx + 26} V{hz - 16} '
               f'H{jx + 36} V{hz - 4} H{jx + 50} V{hz} Z" fill="{RUIN}" stroke="{BRICK_DARK}" stroke-width="1"/>')
    for bx in (jx - 26, jx + 18, jx + 40):
        out.append(f'<rect x="{bx}" y="{hz - 3}" width="6" height="3" fill="{BRICK_DARK}"/>')
    out.append(text(jx + 2, hz + 20, "JERUSALEM", 11, "middle", "bold", fill=MUTED, spacing="1.5"))
    out.append(text(jx + 2, hz + 34, "far to the west", 11, "middle", italic=True, fill=MUTED))

    # The house, cut away: ground floor, roof, and the upper chamber on the roof.
    hx0, hx1 = 380, 660
    gy = 560
    roof = 430
    ux0, ux1, uy = 410, 640, 300
    out.append(f'<rect x="{hx0}" y="{roof}" width="{hx1 - hx0}" height="{gy - roof}" fill="{BRICK}" '
               f'stroke="{BRICK_DARK}" stroke-width="2"/>')
    for row in range(roof + 14, gy, 16):
        off = 0 if (row // 16) % 2 else 18
        out.append(f'<path d="M{hx0} {row} H{hx1}" stroke="{BRICK_DARK}" stroke-width="0.6" opacity="0.5"/>')
        for bx in range(hx0 + off, hx1, 36):
            out.append(f'<path d="M{bx} {row - 16} V{row}" stroke="{BRICK_DARK}" stroke-width="0.6" opacity="0.4"/>')
    out.append(f'<rect x="{hx0 + 116}" y="{gy - 64}" width="40" height="64" rx="18" fill="{BRICK_DARK}"/>')
    out.append(f'<rect x="{hx0 - 8}" y="{roof - 8}" width="{hx1 - hx0 + 16}" height="10" fill="{BRICK_DARK}"/>')
    # Upper chamber, drawn open so the reader sees in.
    out.append(f'<rect x="{ux0}" y="{uy}" width="{ux1 - ux0}" height="{roof - 8 - uy}" fill="{ROOM}" '
               f'stroke="{BRICK_DARK}" stroke-width="2.5"/>')
    out.append(f'<circle cx="{ux0 + 70}" cy="{uy + 70}" r="80" fill="url(#dw-lamp)"/>')
    out.append(f'<path d="M{ux0 - 10} {uy} H{ux1 + 10}" stroke="{BRICK_DARK}" stroke-width="7"/>')
    # Two windows in the west wall (plural in the text; how many is not stated, so the second is dashed).
    for k, wy in enumerate((uy + 22, uy + 70)):
        dash = ' stroke-dasharray="5 4"' if k else ""
        out.append(f'<rect x="{ux0 - 6}" y="{wy}" width="14" height="40" fill="{SKY_LOW}" stroke="{BRICK_DARK}" '
                   f'stroke-width="2"{dash}/>')
        out.append(f'<path d="M{ux0 + 8} {wy} L{ux0 + 30} {wy + 6} V{wy + 46} L{ux0 + 8} {wy + 40} Z" '
                   f'fill="#b88d5a" stroke="{BRICK_DARK}" stroke-width="1.2" opacity="0.85"{dash}/>')
    # Sight line toward Jerusalem.
    out.append(f'<path d="M{ux0 - 8} {uy + 50} Q300 {uy + 10} {jx + 30} {hz - 24}" fill="none" stroke="{GOLD_EDGE}" '
               f'stroke-width="2" stroke-dasharray="7 6"/>')
    out.append(arrow_head(jx + 30, hz - 24, 200, 10, GOLD_EDGE))
    out.append(text(250, uy - 4, "toward Jerusalem", 13, "middle", italic=True, fill=BRICK_DARK))
    out.append(kneeling(ux0 + 64, roof - 9, 1.25))
    # Stairs from the roof down, and the men in the street.
    for i in range(6):
        out.append(f'<rect x="{hx0 - 40 + i * 6}" y="{roof + i * 21}" width="{40 - i * 6}" height="21" '
                   f'fill="{BRICK}" stroke="{BRICK_DARK}" stroke-width="0.8"/>')
    for k, sx in enumerate((300, 326, 352)):
        out.append(standing(sx, gy + 2, 1.05))
    out.append(f'<path d="M{x0} {gy} H{x1}" stroke="{BRICK_DARK}" stroke-width="2"/>')
    # The signed document: a sealed sheet, in the sky's corner as an emblem.
    dx, dy = 600, 196
    out.append(f'<rect x="{dx - 28}" y="{dy - 24}" width="56" height="44" rx="3" fill="{CARD}" stroke="{INK}" stroke-width="1.4"/>')
    for ly in (dy - 14, dy - 6, dy + 2):
        out.append(f'<path d="M{dx - 20} {ly} H{dx + 18}" stroke="{MUTED}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{dx + 14}" cy="{dy + 12}" r="8" fill="{RED}"/>')
    out.append('</g>')
    out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bot - top}" rx="4" fill="none" stroke="{INK}" stroke-width="2"/>')
    for n, x, y in [(1, 640, 178), (2, 670, 470), (3, 452, uy + 28), (4, ux0 + 120, roof - 30),
                    (5, ux0 + 200, uy + 40), (6, 270, gy - 52), (7, 60, hz - 50)]:
        out += callout(n, x, y)

    ky = bot + 32
    keys = [
        ("“When Daniel knew that the document had been signed”", "Daniel 6:10"),
        ("“he went to his house”", "Daniel 6:10"),
        ("“where he had windows in his upper chamber open toward Jerusalem”", "Daniel 6:10"),
        ("“He got down on his knees” · bārēk ʿal birkōhî, “kneeling on his knees”", "Daniel 6:10"),
        ("“three times a day and prayed and gave thanks… as he had done previously”", "Daniel 6:10"),
        ("“these men came by agreement and found Daniel making petition and plea”", "Daniel 6:11"),
        ("“he burned the house of the LORD… broke down the walls around Jerusalem”", "2 Kings 25:9-10"),
    ]
    for i, (q, ref) in enumerate(keys):
        y = ky + i * 24
        out += callout(i + 1, 44, y - 4, r=9)
        out.append(text(62, y, q, 12.5))
        out.append(text(x1, y, ref, 12, "end", italic=True, fill=MUTED))
    ny = ky + len(keys) * 24 + 2
    out.append(f'<path d="M{x0 + 6} {ny - 4} h20" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    out.append(text(62, ny, "Not stated: the hours (Psalm 55:17 has “evening and morning and at noon”), how many",
                    12, italic=True, fill=MUTED))
    out.append(text(62, ny + 16, "windows, the room’s shape, or the words he prayed.", 12, italic=True, fill=MUTED))

    # The two texts the window answers to.
    py = ny + 56
    cw = 320
    out.append(text(30, py - 12, "THE PRAYER HE WAS ANSWERING", 13, weight="bold", fill=MUTED, spacing="1.2"))
    out.append(text(370, py - 12, "THE PROMISE TO THE EXILES", 13, weight="bold", fill=MUTED, spacing="1.2"))
    left = ["Solomon, at the temple’s dedication:"] + wrap(
        "“if they repent… in the land of their enemies, who carried them captive, and pray to you "
        "toward their land… the city that you have chosen, and the house that I have built for your "
        "name, then hear in heaven your dwelling place their prayer and their plea”", 44)
    right = ["Jeremiah, writing to the exiles in Babylon:"] + wrap(
        "“When seventy years are completed for Babylon, I will visit you… Then you will call upon me "
        "and come and pray to me, and I will hear you.”", 44)
    c, hl = card(30, py, cw, left, "1 Kings 8:48-49", fill=GOLD_TINT, size=12.5)
    out += c
    c, hr = card(370, py, cw, right, "Jeremiah 29:10, 12 · Daniel 9:2", fill=BLUE_TINT, size=12.5)
    out += c
    fy = py + max(hl, hr) + 50
    out.append(f'<path d="M{W / 2 - 150} {fy - 30} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(text(W / 2, fy, "“we do not present our pleas before you because of our righteousness,", 15,
                    "middle", italic=True))
    out.append(text(W / 2, fy + 22, "but because of your great mercy.”", 15, "middle", italic=True))
    out.append(text(W / 2, fy + 44, "Daniel 9:18 (ESV)", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    assert fy + 80 <= h, fy
    out.append("</svg>")
    return "\n".join(out)


def appeal_card(x, y, w, n, title, quote, ref, gk=None, fill=CARD):
    rows = wrap(quote, 46)
    hh = 30 + 17 * len(rows) + (17 if gk else 0) + 8
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" rx="6" fill="{fill}" stroke="{INK}" stroke-width="1.4"/>',
           f'<circle cx="{x + 18}" cy="{y + 18}" r="11" fill="{INK}"/>',
           text(x + 18, y + 22.5, str(n), 13, "middle", "bold", fill=PAPER),
           text(x + 38, y + 23, title, 14.5, weight="bold"),
           text(x + w - 10, y + 23, ref, 12, "end", italic=True, fill=MUTED)]
    ty = y + 42
    for r in rows:
        out.append(text(x + 38, ty, r, 12.5, italic=True))
        ty += 17
    if gk:
        out.append(text(x + 38, ty, gk, 12, fill=BLUE))
    return out, hh


def thread_card(x, y, w, lines, ref, dashed=False, fill=CARD):
    hh = 12 + 16 * len(lines) + 18
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" rx="5" fill="{fill}" stroke="{BLUE}" '
           f'stroke-width="1.5"{dash}/>']
    ty = y + 19
    for i, ln in enumerate(lines):
        out.append(text(x + 8, ty, ln, 12.5, weight="bold" if i == 0 else None))
        ty += 16
    out.append(text(x + 8, ty + 2, ref, 11.5, italic=True, fill=MUTED))
    return out, hh


def ephesians_3_prayer():
    h = 1330
    out = svg_open(
        h,
        "Paul's prayer in Ephesians 3",
        "A diagram of Ephesians 3:14-21 in three bands. The address: a prisoner (Ephesians 3:1) bows "
        "his knees before the Father, from whom every family is named; the Greek for family, patria, "
        "is built on patēr, father. The appeals, numbered in their order: strengthened with power "
        "through His Spirit in the inner being (3:16); Christ dwelling in your hearts through faith "
        "(3:17); rooted and grounded in love, drawn as roots and a foundation (3:17); strength to "
        "comprehend with all the saints the breadth, length, height and depth (3:18); to know the love "
        "of Christ that surpasses knowledge (3:19); filled with all the fullness of God (3:19). Beside "
        "them, a column traces the dwelling and fullness words: a dwelling place for God by the Spirit "
        "(Ephesians 2:22); all the fullness of God pleased to dwell in Christ (Colossians 1:19; 2:9) and "
        "you have been filled in Him (Colossians 2:10), both drawn dashed as links to another letter; "
        "Christ dwelling in your hearts (3:17); filled with the fullness of God (3:19). The adoration: "
        "nested bars show what we ask, what we think, and 'far more abundantly than all that we ask or "
        "think' running past the frame (3:20-21).",
    )
    out += heading("Paul’s Prayer on His Knees", "Ephesians 3:14-21 · address, appeals, adoration")

    # A. Address.
    y = 130
    out += banner(W / 2, y, 300, "THE ADDRESS · 3:14-15", fill=INK)
    y += 44
    out.append(f'<rect x="30" y="{y}" width="660" height="118" rx="6" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.5"/>')
    out.append(kneeling(64, y + 92, 1.1))
    out.append(text(80, y + 112, "a prisoner (3:1)", 11.5, "middle", italic=True, fill=MUTED))
    out.append(text(130, y + 30, "“I bow my knees before the Father,", 15, italic=True))
    out.append(text(130, y + 50, "from whom every family in heaven and on earth is named”", 15, italic=True))
    out.append(text(130, y + 78, "πατήρ  patēr, “father”", 14, weight="bold", fill=BLUE))
    out.append(f'<path d="M318 {y + 74} H352" stroke="{BLUE}" stroke-width="1.6"/>')
    out.append(arrow_head(358, y + 74, 0, 8, BLUE))
    out.append(text(366, y + 78, "πατριά  patria, “family, fatherhood”", 14, weight="bold", fill=BLUE))
    out.append(text(130, y + 100, "Every fatherhood takes its name from the Father. Kneeling: most stood to pray.", 12.5,
                    fill=MUTED, italic=True))

    # B. Appeals and the dwelling thread.
    y += 150
    out += banner(W / 2, y, 300, "THE APPEALS · 3:16-19", fill=INK)
    y += 44
    out.append(text(30, y + 4, "IN PAUL’S ORDER", 12, weight="bold", fill=MUTED, spacing="1.2"))
    out.append(text(472, y + 4, "DWELLING AND FULLNESS", 12, weight="bold", fill=BLUE, spacing="1"))
    y += 14
    lx, lw = 30, 420
    appeals = [
        ("Strength, by the Spirit", "“strengthened with power through his Spirit in your inner being”",
         "3:16", None),
        ("Christ settling in", "“so that Christ may dwell in your hearts through faith”", "3:17",
         "κατοικέω  katoikeō, “dwell, take up residence”"),
        ("Rooted and grounded", "“being rooted and grounded in love”", "3:17",
         "ῥιζόω  rhizoō, “root” · θεμελιόω  themelioō, “found”"),
        ("Strength to grasp it", "“to comprehend with all the saints what is the breadth and length and "
         "height and depth”", "3:18", None),
        ("A love beyond knowing", "“to know the love of Christ that surpasses knowledge”", "3:19", None),
        ("Filled with God", "“that you may be filled with all the fullness of God”", "3:19",
         "πλήρωμα  plērōma, “fullness”"),
    ]
    tops = []
    cy = y
    for i, (t, q, r, gk) in enumerate(appeals):
        c, hh = appeal_card(lx, cy, lw, i + 1, t, q, r, gk, fill=GOLD_TINT if i in (1, 5) else CARD)
        out += c
        tops.append((cy, hh))
        if i < len(appeals) - 1:
            out.append(f'<path d="M{lx + 18} {cy + hh} V{cy + hh + 14}" stroke="{INK}" stroke-width="1.6"/>')
            out.append(arrow_head(lx + 18, cy + hh + 16, 90, 8))
        cy += hh + 18
    # Roots and a foundation beside card 3; the four dimensions beside card 4.
    r3y, r3h = tops[2]
    bx = lx + lw - 70
    out.append(f'<rect x="{bx}" y="{r3y + 34}" width="56" height="12" fill="{BRICK}" stroke="{BRICK_DARK}" stroke-width="1"/>')
    for k, dxx in enumerate((-14, 0, 14)):
        out.append(f'<path d="M{bx + 28} {r3y + 46} q{dxx} 10 {dxx * 1.6:.0f} 20" fill="none" stroke="{BRICK_DARK}" stroke-width="1.6"/>')
    r4y, r4h = tops[3]
    qx, qy = lx + lw - 46, r4y + r4h / 2 + 4
    for ang, lab, (ox, oy) in [(0, "breadth", (14, 4)), (180, "", (0, 0)), (90, "depth", (6, 14)),
                               (270, "height", (6, -8))]:
        a = math.radians(ang)
        ex, ey = qx + 24 * math.cos(a), qy + 24 * math.sin(a)
        out.append(f'<path d="M{qx} {qy} L{ex:.1f} {ey:.1f}" stroke="{RED}" stroke-width="1.6"/>')
        out.append(arrow_head(ex, ey, ang, 6, RED))
    out.append(f'<path d="M{qx} {qy} l-14 10" stroke="{RED}" stroke-width="1.6"/>')
    out.append(arrow_head(qx - 14, qy + 10, 145, 6, RED))

    # The thread column.
    tx, tw = 470, 220
    thread = [
        (["a dwelling place for God", "by the Spirit", "κατοικητήριον"], "Ephesians 2:22", False, 1),
        (["all the fullness of God", "pleased to dwell in Him", "πλήρωμα · κατοικέω"], "Colossians 1:19; 2:9", True, 1),
        (["Christ dwells", "in your hearts", "κατοικέω"], "Ephesians 3:17", False, 1),
        (["filled with all the", "fullness of God", "πλήρωμα"], "Ephesians 3:19", False, 5),
        (["you have been filled", "in Him"], "Colossians 2:10", True, 5),
    ]
    ty = y
    anchors = []
    for lines, ref, dashed, target in thread:
        if target == 5 and ty < tops[5][0] - 30:
            ty = tops[5][0] - 30
        c, hh = thread_card(tx, ty, tw, lines, ref, dashed, fill=BLUE_TINT if not dashed else CARD)
        out += c
        anchors.append((ty + hh / 2, target, dashed))
        ty += hh + 12
    for ay, target, dashed in anchors:
        t_y, t_h = tops[target]
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        out.append(f'<path d="M{tx} {ay:.1f} C{tx - 10} {ay:.1f} {lx + lw + 10} {t_y + t_h / 2:.1f} {lx + lw + 2} '
                   f'{t_y + t_h / 2:.1f}" fill="none" stroke="{BLUE}" stroke-width="1.3"{dash}/>')
    end_y = max(cy, ty)

    # Key for the thread.
    ky = end_y + 6
    out.append(f'<rect x="{tx}" y="{ky}" width="34" height="14" rx="3" fill="{BLUE_TINT}" stroke="{BLUE}" stroke-width="1.5"/>')
    out.append(text(tx + 42, ky + 12, "Ephesians’ own words", 12))
    out.append(f'<rect x="{tx}" y="{ky + 22}" width="34" height="14" rx="3" fill="{CARD}" stroke="{BLUE}" '
               f'stroke-width="1.5" stroke-dasharray="6 4"/>')
    out.append(text(tx + 42, ky + 34, "Colossians: the study’s link", 12))

    # C. Adoration.
    y = ky + 62
    out += banner(W / 2, y, 320, "THE ADORATION · 3:20-21", fill=INK)
    y += 46
    out.append(text(W / 2, y + 4, "“Now to him who is able to do far more abundantly than all that we ask or think,", 14,
                    "middle", italic=True))
    out.append(text(W / 2, y + 24, "according to the power at work within us, to him be glory…”", 14, "middle", italic=True))
    y += 46
    bars = [("all that we ask", 180, CARD, False), ("or think", 330, GOLD_TINT, False),
            ("far more abundantly", 660, GOLD, True)]
    for i, (lab, wv, fill, open_end) in enumerate(bars):
        by = y + i * 30
        if open_end:
            out.append(f'<rect x="30" y="{by}" width="{wv}" height="22" fill="{fill}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
            out.append(f'<path d="M{30 + wv} {by} v22" stroke="{GOLD}" stroke-width="3" stroke-dasharray="4 3"/>')
            out.append(arrow_head(30 + wv + 4, by + 11, 0, 9, GOLD_EDGE))
        else:
            out.append(f'<rect x="30" y="{by}" width="{wv}" height="22" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>')
        out.append(text(40, by + 16, lab, 13, weight="bold"))
    out.append(text(W - 34, y + 30 * 3 + 12, "the last bar runs past the frame: the verse sets no edge to it", 12,
                    "end", italic=True, fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)



def petition_card(x, y, w, h, n, label, quote, ref, gk, fill, edge):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{edge}" stroke-width="1.5"/>',
           f'<circle cx="{x + 17}" cy="{y + 18}" r="11" fill="{INK}"/>',
           text(x + 17, y + 22.5, str(n), 13, "middle", "bold", fill=PAPER),
           text(x + 34, y + 23, label, 14, weight="bold"),
           text(x + w - 8, y + 23, ref, 11.5, "end", italic=True, fill=MUTED)]
    ty = y + 44
    for r in wrap(quote, int((w - 20) / 6.4)):
        out.append(text(x + 10, ty, r, 13, italic=True))
        ty += 17
    out.append(text(x + 10, y + h - 10, gk, 12, fill=BLUE))
    return out


def loaf_glyph(x, y):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="0" rx="20" ry="10" fill="#d9a85f" stroke="{BRICK_DARK}" '
            f'stroke-width="1.2"/><path d="M-10 -4 q4 6 0 10 M0 -6 q4 7 0 12 M10 -4 q4 6 0 10" fill="none" '
            f'stroke="{BRICK_DARK}" stroke-width="1"/></g>')


def ledger_glyph(x, y):
    out = [f'<rect x="{x - 16}" y="{y - 14}" width="32" height="26" rx="2" fill="{CARD}" stroke="{INK}" stroke-width="1.2"/>']
    for k in range(3):
        out.append(f'<path d="M{x - 11} {y - 7 + k * 7} H{x + 11}" stroke="{MUTED}" stroke-width="1"/>')
    out.append(f'<path d="M{x - 13} {y - 11} L{x + 13} {y + 9}" stroke="{RED}" stroke-width="2"/>')
    return "".join(out)


def path_glyph(x, y):
    return (f'<path d="M{x - 22} {y + 10} Q{x - 6} {y + 8} {x - 4} {y - 2} T{x + 22} {y - 12}" fill="none" '
            f'stroke="{BRICK_DARK}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{x - 22} {y + 10} Q{x - 6} {y + 8} {x - 4} {y - 2} T{x + 22} {y - 12}" fill="none" '
            f'stroke="{SAND}" stroke-width="2" stroke-dasharray="3 3"/>')


def lords_prayer_shape():
    h = 1170
    out = svg_open(
        h,
        "The shape of the Lord's Prayer",
        "A diagram of Matthew 6:9-13 (ESV) drawn as heaven above and earth below. In the heaven band: "
        "the address, 'Our Father in heaven' (6:9), then three petitions, each with the Greek 'your' "
        "(sou): 1 'hallowed be your name' (6:9), 2 'Your kingdom come' (6:10), 3 'your will be done' "
        "(6:10). A gold band joins heaven to earth with the words 'on earth as it is in heaven' (6:10), "
        "noted dashed as debated: whether the phrase governs all three petitions or only the third. In "
        "the earth band: three petitions spoken as 'us': 4 'Give us this day our daily bread' (6:11), "
        "with a loaf; 5 'and forgive us our debts, as we also have forgiven our debtors' (6:12), with a "
        "ledger struck through; 6 'And lead us not into temptation, but deliver us from evil' (6:13), "
        "with a path. A small figure kneels on the ground. A count: 'your' three times in 6:9-10, "
        "'us', 'our' and 'we' eight times in 6:11-13. A dashed card: the doxology 'For yours is the "
        "kingdom and the power and the glory, forever. Amen' is not in the earliest manuscripts; the "
        "ESV prints it in a footnote. Below, 'He prayed it Himself': Matthew 6:10 and Matthew 26:42, "
        "'My Father, if this cannot pass unless I drink it, your will be done', share the Greek words "
        "genēthētō to thelēma sou. The plate closes with the line 'The attitude of prayer is that we "
        "are God's.'",
    )
    out += heading("The Shape of the Prayer", "Matthew 6:9-13 · heaven first, then earth")

    # Heaven.
    top, mid = 112, 410
    out.append(f'<defs><linearGradient id="lp-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY_TOP}"/>'
               f'<stop offset="1" stop-color="{SKY_PALE}"/></linearGradient>'
               f'<linearGradient id="lp-earth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{EARTH_TINT}"/>'
               f'<stop offset="1" stop-color="{SAND}"/></linearGradient></defs>')
    out.append(f'<rect x="30" y="{top}" width="660" height="{mid - top}" rx="8" fill="url(#lp-sky)" stroke="{BLUE}" stroke-width="1.2"/>')
    out.append(text(46, top + 24, "IN HEAVEN", 12, weight="bold", fill=BLUE, spacing="1.5"))
    out.append(text(674, top + 24, "about God", 12, "end", italic=True, fill=BLUE))
    ay = top + 40
    out.append(f'<rect x="150" y="{ay}" width="420" height="72" rx="6" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.5"/>')
    out.append(text(W / 2, ay + 30, "“Our Father in heaven,”", 20, "middle", "bold", italic=True))
    out.append(text(W / 2, ay + 54, "πάτερ ἡμῶν  pater hēmōn · a child, and a creature · 6:9", 12.5, "middle", fill=BLUE))
    for cx in (220, 360, 500):
        out.append(f'<path d="M{W / 2} {ay + 72} L{cx} {ay + 96}" stroke="{INK}" stroke-width="1.3"/>')
        out.append(arrow_head(cx, ay + 98, math.degrees(math.atan2(26, cx - W / 2)), 8))
    py, pw, ph = ay + 104, 206, 112
    yours = [("His name", "“hallowed be your name.”", "6:9", "τὸ ὄνομά σου · your name"),
             ("His kingdom", "“Your kingdom come,”", "6:10", "ἡ βασιλεία σου · your kingdom"),
             ("His will", "“your will be done,”", "6:10", "τὸ θέλημά σου · your will")]
    for i, (lab, q, ref, gk) in enumerate(yours):
        out += petition_card(42 + i * (pw + 12), py, pw, ph, i + 1, lab, q, ref, gk, CARD, BLUE)
    for i in range(3):
        bx = 42 + i * (pw + 12) + pw - 26
        out.append(f'<circle cx="{bx}" cy="{py + ph - 46}" r="15" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
        out.append(text(bx, py + ph - 41, "σου", 13, "middle", "bold"))

    # The hinge.
    hy = mid - 18
    out.append(f'<rect x="60" y="{hy}" width="600" height="58" rx="29" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>')
    out.append(text(W / 2, hy + 25, "“on earth as it is in heaven.”", 18, "middle", "bold", italic=True))
    out.append(text(W / 2, hy + 46, "ὡς ἐν οὐρανῷ καὶ ἐπὶ γῆς · the hinge · 6:10", 12.5, "middle", fill=INK))
    out.append(text(W / 2, hy + 74, "Whether it governs all three petitions above or only the third is debated.", 12,
                    "middle", italic=True, fill=MUTED))

    # Earth.
    ey = hy + 88
    eh = 240
    out.append(f'<rect x="30" y="{ey}" width="660" height="{eh}" rx="8" fill="url(#lp-earth)" stroke="{BRICK_DARK}" stroke-width="1.2"/>')
    out.append(text(46, ey + 24, "ON EARTH", 12, weight="bold", fill=BRICK_DARK, spacing="1.5"))
    out.append(text(674, ey + 24, "for us", 12, "end", italic=True, fill=BRICK_DARK))
    ours = [("Bread", "“Give us this day our daily bread,”", "6:11", "δὸς ἡμῖν · give us", loaf_glyph),
            ("Debts", "“and forgive us our debts, as we also have forgiven our debtors.”", "6:12",
             "ἄφες ἡμῖν · forgive us", ledger_glyph),
            ("Keeping", "“And lead us not into temptation, but deliver us from evil.”", "6:13",
             "ῥῦσαι ἡμᾶς · deliver us", path_glyph)]
    qy = ey + 38
    for i, (lab, q, ref, gk, glyph) in enumerate(ours):
        x = 42 + i * (pw + 12)
        out += petition_card(x, qy, pw, 150, i + 4, lab, q, ref, gk, CARD, BRICK_DARK)
        out.append(glyph(x + pw - 34, qy + 118))
    out.append(kneeling(636, ey + eh - 8, 0.7))
    out.append(text(616, ey + eh - 12, "the one praying", 11.5, "end", italic=True, fill=BRICK_DARK))

    # The count.
    cy = ey + eh + 34
    out.append(text(W / 2, cy, "COUNT THE PRONOUNS IN THE GREEK", 12, "middle", "bold", fill=MUTED, spacing="1.2"))
    cy += 22
    out.append(text(196, cy + 5, "your (σου), 6:9-10", 13, "end"))
    for k in range(3):
        out.append(f'<circle cx="{214 + k * 26}" cy="{cy}" r="9" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
    out.append(text(300, cy + 5, "3", 14, weight="bold"))
    cy += 28
    out.append(text(196, cy + 5, "us, our, we, 6:11-13", 13, "end"))
    for k in range(8):
        out.append(f'<circle cx="{214 + k * 26}" cy="{cy}" r="9" fill="{SAND_DEEP}" stroke="{BRICK_DARK}" stroke-width="1.2"/>')
    out.append(text(430, cy + 5, "8", 14, weight="bold"))
    out.append(text(456, cy - 9, "Every request for yourself", 12.5, italic=True, fill=MUTED))
    out.append(text(456, cy + 8, "is prayed in the plural.", 12.5, italic=True, fill=MUTED))

    # The doxology.
    dy = cy + 30
    out.append(f'<rect x="90" y="{dy}" width="540" height="58" rx="6" fill="{CARD}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    out.append(text(W / 2, dy + 24, "“For yours is the kingdom and the power and the glory, forever. Amen.”", 13.5,
                    "middle", italic=True, fill=MUTED))
    out.append(text(W / 2, dy + 44, "Not in the earliest manuscripts; the ESV prints it in a footnote to 6:13.", 12,
                    "middle", fill=MUTED))

    # Gethsemane.
    gy = dy + 92
    out += banner(W / 2, gy, 300, "HE PRAYED IT HIMSELF", fill=RED)
    gy += 44
    cards = [("Taught on the mountain", "“your will be done,”", "Matthew 6:10"),
             ("Prayed in Gethsemane", "“My Father, if this cannot pass unless I drink it, your will be done.”",
              "Matthew 26:42")]
    for i, (lab, q, ref) in enumerate(cards):
        x = 42 + i * 336
        out.append(f'<rect x="{x}" y="{gy}" width="300" height="96" rx="6" fill="{CARD}" stroke="{RED}" stroke-width="1.5"/>')
        out.append(text(x + 12, gy + 22, lab, 14, weight="bold"))
        out.append(text(x + 288, gy + 22, ref, 11.5, "end", italic=True, fill=MUTED))
        ty = gy + 42
        for r in wrap(q, 44):
            out.append(text(x + 12, ty, r, 13, italic=True))
            ty += 17
        out.append(text(x + 12, gy + 86, "γενηθήτω τὸ θέλημά σου", 13, weight="bold", fill=BLUE))
    out.append(f'<path d="M342 {gy + 81} H376" stroke="{RED}" stroke-width="2"/>')
    out.append(text(W / 2, gy + 116, "The same Greek words. The cup was not taken away, and He drank it.", 13,
                    "middle", italic=True))

    out.append(text(W / 2, gy + 156, "The attitude of prayer is that we are God’s.", 19, "middle", "bold", italic=True))
    out.append(credit(h))
    assert gy + 200 <= h, (gy, h)
    out.append("</svg>")
    return "\n".join(out)


def home_glyph(x, y):
    """A house with its door open: the son coming home (Luke 15:20)."""
    return (f'<path d="M{x - 20} {y - 2} L{x} {y - 20} L{x + 20} {y - 2}" fill="none" stroke="{BRICK_DARK}" stroke-width="3" '
            f'stroke-linejoin="round"/><rect x="{x - 15}" y="{y - 4}" width="30" height="20" fill="{ROOM}" stroke="{BRICK_DARK}" '
            f'stroke-width="1.6"/><rect x="{x - 5}" y="{y + 3}" width="10" height="13" fill="{GOLD}"/>'
            f'<path d="M{x - 5} {y + 3} L{x - 11} {y + 6} V{y + 18} L{x - 5} {y + 16} Z" fill="{BRICK}" stroke="{BRICK_DARK}" stroke-width="1"/>')


def sinai_glyph(x, y):
    """The mountain and the cloud: the LORD proclaiming His name to Moses (Exodus 34:5-7)."""
    return (f'<path d="M{x - 22} {y + 14} L{x - 4} {y - 10} L{x + 4} {y - 2} L{x + 10} {y - 8} L{x + 22} {y + 14} Z" '
            f'fill="{RUIN}" stroke="{BRICK_DARK}" stroke-width="1.2"/>'
            f'<ellipse cx="{x - 2}" cy="{y - 14}" rx="15" ry="6" fill="{CLOUD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>'
            f'<ellipse cx="{x + 8}" cy="{y - 18}" rx="9" ry="5" fill="{CLOUD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>')


def crown_glyph(x, y):
    """A crown: God is King, and Jesus is coming back to reign."""
    return (f'<path d="M{x - 18} {y + 10} L{x - 20} {y - 10} L{x - 9} {y} L{x} {y - 14} L{x + 9} {y} L{x + 20} {y - 10} '
            f'L{x + 18} {y + 10} Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<circle cx="{x}" cy="{y + 4}" r="3" fill="{RED}"/>')


def amen_glyph(x, y):
    """A seal reading AMEN: "it is so", the Yes of 2 Corinthians 1:20."""
    return (f'<circle cx="{x}" cy="{y}" r="18" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>'
            f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{GOLD_EDGE}" stroke-width="0.8"/>'
            + text(x, y + 4, "AMEN", 10, "middle", "bold", fill=INK, spacing="0.5"))


# The seven weeks of christian-life/teaching-the-lords-prayer-at-home.md: each line of Matthew 6:9-13
# (ESV), the week's "what it shows about God" sentence as the guide words it, and the picture of the
# week's story. Week 7 has no line of its own; it prays the whole prayer and its Amen.
WEEKS = [
    ("Our Father in heaven,", "6:9", "God is our Father, because Jesus made us His children.", home_glyph,
     "a house with its door open"),
    ("hallowed be your name.", "6:9", "God's name is who He is, and He is holy.", sinai_glyph,
     "a mountain under a cloud"),
    ("Your kingdom come, your will be done, on earth as it is in heaven.", "6:10",
     "God is King, Jesus is coming back to reign, and God's way is best.", crown_glyph, "a crown"),
    ("Give us this day our daily bread,", "6:11", "God gives us what we need, one day at a time.", loaf_glyph,
     "a loaf"),
    ("and forgive us our debts, as we also have forgiven our debtors.", "6:12",
     "God forgives us because Jesus paid what we owed, so we forgive each other.", ledger_glyph,
     "a ledger struck through"),
    ("And lead us not into temptation, but deliver us from evil.", "6:13",
     "God is stronger than the devil, and He keeps His children.", path_glyph, "a path"),
    ("Amen.", "2 Corinthians 1:20", "Every promise God makes is \u201cYes\u201d in Jesus.", amen_glyph,
     "a gold seal reading Amen"),
]


def emblem(n, x, y):
    _, _, _, glyph, _ = WEEKS[n - 1]
    return [f'<circle cx="{x}" cy="{y}" r="30" fill="{CARD}" stroke="{GOLD_EDGE}" stroke-width="2"/>', glyph(x, y)]


def week_emblem(n):
    """One week's picture alone, for the head of its section in the guide."""
    _, _, _, _, what = WEEKS[n - 1]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" role="img" aria-label="Week {n}: {esc(what)}">',
        *emblem(n, 36, 34),
        f'<circle cx="58" cy="58" r="11" fill="{INK}"/>',
        text(58, 62.5, str(n), 13, "middle", "bold", fill=PAPER),
        "</svg>"])


def seven_pictures():
    top = 128
    rows = []
    for i, (line, ref, shows, _, _) in enumerate(WEEKS, 1):
        quote = wrap(f"\u201c{line}\u201d" if i < len(WEEKS) else line, 60)
        says = wrap(shows, 64)
        rows.append((quote, says, max(96, 50 + 20 * len(quote) + 18 * len(says))))
    h = top + sum(r[2] + 12 for r in rows) + 140
    desc = ("A card for the fridge: the Lord's Prayer (Matthew 6:9-13, ESV) in seven pictures, one for each "
            "week of the household guide. " + " ".join(
                f"Week {i}: {what}, beside '{line}' ({ref}) and '{shows}'" for i, (line, ref, shows, _, what)
                in enumerate(WEEKS, 1)) +
            " Below: pray the whole prayer together every day, and in your own words in four steps: Our Father, "
            "Your will, Today, Forgive and keep.")
    out = svg_open(h, "The Prayer in Seven Pictures", desc)
    out += heading("The Prayer in Seven Pictures", "Matthew 6:9-13 · one line a week · for the fridge")
    y = top
    for i, ((quote, says, rh), (_, ref, _, _, _)) in enumerate(zip(rows, WEEKS), 1):
        out.append(f'<rect x="34" y="{y}" width="652" height="{rh}" rx="8" fill="{CARD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
        out += emblem(i, 92, y + rh / 2)
        out.append(text(140, y + 26, f"WEEK {i}", 12, weight="bold", fill=RED, spacing="1.5"))
        out.append(text(670, y + 26, ref, 12, "end", italic=True, fill=MUTED))
        ty = y + 48
        for r in quote:
            out.append(text(140, ty, r, 16, italic=True))
            ty += 20
        for r in says:
            out.append(text(140, ty + 2, r, 14.5, weight="bold", fill=BLUE))
            ty += 18
        y += rh + 12
    fy = y + 16
    out.append(text(W / 2, fy + 10, "Pray the whole prayer together every day.", 18, "middle", "bold", italic=True))
    out.append(text(W / 2, fy + 42, "In your own words, in four steps:", 14, "middle", fill=MUTED))
    out.append(text(W / 2, fy + 66, "Our Father  ·  Your will  ·  Today  ·  Forgive and keep", 16, "middle", "bold"))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("daniel-at-the-window", daniel_at_the_window), ("ephesians-3-prayer", ephesians_3_prayer),
                     ("lords-prayer-shape", lords_prayer_shape), ("seven-pictures", seven_pictures)):
        (OUT / f"{name}.svg").write_text(fn() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")
    for n in range(1, len(WEEKS) + 1):
        (OUT / f"week-{n}.svg").write_text(week_emblem(n) + "\n", encoding="utf-8")
    print(f"wrote week-1..{len(WEEKS)}.svg")


if __name__ == "__main__":
    main()
