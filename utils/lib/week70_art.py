"""Pictures for Daniel's seventieth week on the chart (docs/content/timeline.md, #week70).

Each function draws one 240 x 180 plate for a scene the text of Revelation (or Daniel, Matthew,
Zechariah) describes, as a string of SVG shapes; build_chart_sprites.py wraps each in a <symbol>
(`v-<event id>`) beside the comic-panel vignettes. The riders and the horse are the plates' own
(utils/build_tribulation_graphics.py), the people are the comics' cast (lib/comic.py), and the rest is
drawn here: wings, the seven-headed beasts, the sky coming apart.

The rules of the comics hold. Nothing is drawn that the text does not give, no figure has a face, and
a detail Scripture leaves open is drawn plainly (the beast's body is a leopard's, 13:2, and nothing
more). `SHOWS` carries the alt text, which names every detail drawn.

Run through build_chart_sprites.py; to look at one plate, `python3 utils/build_chart_sprites.py` and
render docs/content/assets/chart/sprites.svg.
"""

import math

from . import comic

GOLD = "#e0b24a"
GOLD_DK = "#9c7a2e"
INK = "#2a2118"
WHITE = "#fbf7ee"
LINEN = "#f4ecd6"
RED = "#a3202a"
BLOOD = "#8b1b1b"
WING = "#f3efe4"
WING_EDGE = "#b2a88f"


def _grad(gid, top, bottom, x2=0, y2=1):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient>')


def _sky(gid, top, bottom):
    return [f"<defs>{_grad(gid, top, bottom)}</defs>", f'<rect width="240" height="180" fill="url(#{gid})"/>']


def _star(x, y, r, fill="#f6e7a8"):
    pts = []
    for k in range(10):
        a = math.pi * k / 5 - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.42
        pts.append(f"{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}")
    return f'<path d="M{" L".join(pts)} Z" fill="{fill}"/>'


def wings(x, y, s=1.0, face=1, spread=1.0, fill=WING, edge=WING_EDGE):
    """A pair of feathered wings raised behind a figure whose shoulders are at (x, y): a back row of
    long flight feathers fanned from the shoulder and a shorter row of coverts over them."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face:.3f} {s:.3f})">']
    for m in (1, -1):
        for row, (length, width, fillc) in enumerate(((62, 8.0, fill), (40, 7.0, "#fffdf6"))):
            for k in range(7):
                ang = -80 + k * 10 * spread
                ln = length - k * (3.6 if row == 0 else 2.4)
                a = math.radians(ang)
                cx, cy = m * (8 + math.cos(a) * ln / 2), math.sin(a) * ln / 2
                rot = ang if m == 1 else 180 - ang
                out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{ln / 2:.1f}" ry="{width:.1f}" transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})" '
                           f'fill="{fillc}" stroke="{edge}" stroke-width="0.9"/>')
    out.append("</g>")
    return "".join(out)


def angel(x, y, s=1.0, face=1, pose="stand", holds=None, spread=1.0):
    """An angel: the comic's white-robed figure with wings. (x, y) is the feet."""
    body, _ = comic.figure("robed", x, y, s, face, pose=pose, holds=holds)
    return wings(x, y - 62 * s, s, face, spread) + body


def _lamb(x, y, s=1.0):
    """The Lamb standing, as though it had been slain (Revelation 5:6): a woolly body, a small round head
    in profile and the wound on the neck. The seven horns of 5:6 are drawn as seven short rays."""
    wool = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}" stroke="{INK}" stroke-width="1.2"/>'
                   for cx, cy, r in ((-22, -28, 11), (-9, -36, 12), (6, -35, 12), (19, -29, 11), (-15, -20, 11), (2, -20, 12), (16, -19, 10)))
    horns = "".join(f'<path d="M{40 + (i - 3) * 2.6:.1f} -50 l{(i - 3) * 1.5:.1f} -7" stroke="{GOLD_DK}" stroke-width="1.5" stroke-linecap="round"/>' for i in range(7))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<path d="M-22 -12 V0 M-8 -10 V0 M10 -10 V0 M22 -12 V0" stroke="{INK}" stroke-width="3.6" stroke-linecap="round"/>'
            f'{wool}'
            f'<ellipse cx="40" cy="-34" rx="10" ry="9.5" fill="{WHITE}" stroke="{INK}" stroke-width="1.3"/>'
            f'<ellipse cx="33" cy="-44" rx="4" ry="6" fill="{WHITE}" stroke="{INK}" stroke-width="1.1" transform="rotate(-24 33 -44)"/>'
            f'<ellipse cx="47" cy="-43" rx="4" ry="6" fill="{WHITE}" stroke="{INK}" stroke-width="1.1" transform="rotate(26 47 -43)"/>'
            f'<ellipse cx="47" cy="-31" rx="3.4" ry="2.6" fill="{INK}"/><circle cx="41" cy="-37" r="1.5" fill="{INK}"/>{horns}'
            f'<path d="M26 -34 Q29 -28 28 -22" stroke="{RED}" stroke-width="3" fill="none" stroke-linecap="round"/></g>')


def lamb_scroll():
    """Revelation 4-5: the throne under its rainbow, twenty-four around it, the Lamb as though slain."""
    out = _sky("w70-lamb-sky", "#fff6d6", "#efcd7a")
    for k in range(18):
        a = math.pi * (0.1 + 0.8 * k / 17)
        out.append(f'<path d="M120 88 L{120 + 190 * math.cos(a):.1f} {88 - 190 * math.sin(a):.1f}" stroke="#fff" stroke-width="3" opacity="0.28"/>')
    for r, c in ((60, "#7da36b"), (53, "#a8c890"), (46, "#7da36b")):
        out.append(f'<path d="M{120 - r} 100 A{r} {r * 0.9:.0f} 0 0 1 {120 + r} 100" fill="none" stroke="{c}" stroke-width="3.4" opacity="0.85"/>')
    out.append(comic.PROPS["throne"](120, 108, 0.46))
    for k in range(24):
        a = math.radians(196 + 148 * k / 23)
        cx, cy = 120 + 104 * math.cos(a), 118 + 84 * math.sin(a)
        out.append(f'<path d="M{cx - 5:.1f} {cy + 3:.1f} L{cx - 5:.1f} {cy - 3:.1f} L{cx - 2.5:.1f} {cy:.1f} L{cx:.1f} {cy - 4:.1f} L{cx + 2.5:.1f} {cy:.1f} L{cx + 5:.1f} {cy - 3:.1f} L{cx + 5:.1f} {cy + 3:.1f} Z" '
                   f'fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/>')
    out.append(f'<path d="M0 170 Q120 150 240 170 V180 H0 Z" fill="#d9b868"/>')
    out.append(_lamb(104, 174, 1.0))
    # The scroll with seven seals, held out before the throne.
    out.append(f'<g transform="rotate(-8 178 112)"><rect x="150" y="104" width="56" height="16" rx="3" fill="#efe2bf" stroke="{GOLD_DK}" stroke-width="1.3"/>'
               f'<ellipse cx="150" cy="112" rx="4" ry="8" fill="#e2d0a2" stroke="{GOLD_DK}" stroke-width="1.2"/><ellipse cx="206" cy="112" rx="4" ry="8" fill="#e2d0a2" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    for i in range(7):
        out.append(f'<circle cx="{157 + i * 7.5:.1f}" cy="112" r="3" fill="{RED}" stroke="#5b1010" stroke-width="0.6"/>')
    out.append("</g>")
    return "".join(out)


def horsemen_four():
    """Revelation 6:1-8: the four riders, white, red, black and pale, with Death's Hades behind."""
    import build_tribulation_graphics as plate

    out = _sky("w70-horse-sky", "#2c2338", "#d99b5a")
    out.append('<path d="M0 142 Q60 128 120 138 T240 130 V180 H0 Z" fill="#3a2a22"/>')
    out.append('<path d="M0 156 Q80 144 160 152 T240 150 V180 H0 Z" fill="#241913"/>')
    riders = (("#b9c3a6", "#5f6b55", "#16201a", -20, 148, 56, 0.30),
              ("#1e1b1d", "#8a8070", "#0f0d0e", 0, 112, 66, 0.34),
              ("#b3241c", "#5a120e", "#1c1310", 22, 70, 76, 0.38),
              ("#f5f1e6", "#7d7464", "#2b2420", 10, 22, 88, 0.42))
    for n, (fill, edge, ink, arm, x, y, sc) in enumerate(riders):
        out.append(plate.horse(x, y, fill, edge, sc))
        rs = sc * 1.1
        sx, sy = x + plate.SEAT[0] * sc, y + plate.SEAT[1] * sc
        r, (hx, hy) = plate.rider(sx, sy, ink, s=rs, arm=(arm,))
        out.append(r)
        if n == 3:   # the first rider: a bow in his hand and a crown given to him (6:2)
            out.append(f'<path d="M{hx + 1:.1f} {hy - 13:.1f} Q{hx + 13:.1f} {hy:.1f} {hx + 1:.1f} {hy + 13:.1f}" stroke="#5b4632" stroke-width="1.6" fill="none"/>'
                       f'<path d="M{hx + 1:.1f} {hy - 13:.1f} V{hy + 13:.1f}" stroke="#5b4632" stroke-width="0.6"/>')
            hdx, hdy = sx + 8 * rs, sy - 50 * rs
            out.append(f'<ellipse cx="{hdx:.1f}" cy="{hdy - 7 * rs:.1f}" rx="{7 * rs:.1f}" ry="{2.4 * rs:.1f}" fill="none" stroke="{GOLD}" stroke-width="1.8"/>')
        if n == 2:   # the second: a great sword (6:4)
            out.append(f'<path d="M{hx:.1f} {hy:.1f} L{hx + 20:.1f} {hy - 18:.1f}" stroke="#e0e0e0" stroke-width="2.6" stroke-linecap="round"/>')
    return "".join(out)


def seal6():
    """Revelation 6:12-17: earthquake, the sun black, the moon like blood, the stars falling, the sky rolled up."""
    out = _sky("w70-seal6-sky", "#140f26", "#6a2a30")
    for k in range(12):
        a = 2 * math.pi * k / 12
        out.append(f'<path d="M72 48 L{72 + 30 * math.cos(a):.1f} {48 + 30 * math.sin(a):.1f}" stroke="#3a3040" stroke-width="2" opacity="0.8"/>')
    out.append(f'<circle cx="72" cy="48" r="19" fill="#0c0a0c" stroke="#4a3d52" stroke-width="1.4"/>')
    out.append(f'<circle cx="172" cy="42" r="15" fill="{BLOOD}" stroke="#d2493d" stroke-width="1.2"/>')
    for x, y in ((24, 20), (104, 26), (130, 12), (208, 24), (150, 62), (36, 76)):
        out.append(f'<path d="M{x + 10} {y - 10} L{x} {y}" stroke="#f6e7a8" stroke-width="1.2" opacity="0.7"/>' + _star(x, y, 4.4))
    # The sky "vanished like a scroll that is being rolled up": curled at both edges.
    out.append(f'<path d="M0 0 H34 C26 20 8 28 0 56 Z" fill="#2a2038" stroke="{WING_EDGE}" stroke-width="0.8"/>'
               f'<path d="M240 0 H206 C214 20 232 28 240 56 Z" fill="#2a2038" stroke="{WING_EDGE}" stroke-width="0.8"/>')
    out.append('<path d="M0 128 L34 88 L52 108 L88 70 L120 112 L158 80 L190 108 L214 84 L240 110 V180 H0 Z" fill="#241a20"/>')
    out.append('<path d="M88 70 L92 96 L84 118 M158 80 L154 104 L162 126" stroke="#8a4a3a" stroke-width="1.6" fill="none"/>')
    out.append('<path d="M0 150 Q40 142 80 152 T160 150 T240 152 V180 H0 Z" fill="#17101a"/>')
    return "".join(out)


def sealed144():
    """Revelation 7:1-4: four angels hold the four winds; an angel rises from the east with the seal."""
    out = _sky("w70-sealed-sky", "#f7d9a0", "#8fb4cf")
    out.append(f'<circle cx="212" cy="108" r="26" fill="#fff1bf" opacity="0.85"/>')
    for k in range(9):
        a = math.radians(-100 + 22 * k)
        out.append(f'<path d="M212 108 L{212 + 60 * math.cos(a):.1f} {108 + 60 * math.sin(a):.1f}" stroke="#fff1bf" stroke-width="2" opacity="0.4"/>')
    out.append('<path d="M0 118 L240 118 L240 180 L0 180 Z" fill="#c9b985"/>')
    out.append('<path d="M18 118 L222 118 L240 180 L0 180 Z" fill="#b9a874"/>')
    for ax, ay, face in ((22, 126, 1), (196, 126, -1), (6, 176, 1), (214, 176, -1)):
        out.append(angel(ax + 14, ay, 0.38, face, pose="open", spread=0.8))
        for r in (10, 16):
            out.append(f'<path d="M{ax + 14 + face * 8:.0f} {ay - 60 + r:.0f} q{face * 14} -6 {face * 22} 4" stroke="#fff" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(angel(120, 164, 0.7, 1, pose="offer", holds="scroll", spread=1.0))
    out.append(f'<circle cx="150" cy="108" r="8" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.6"/>'
               f'<circle cx="150" cy="108" r="3.8" fill="none" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    for i in range(12):
        out.append(f'<circle cx="{26 + i * 17.2:.1f}" cy="168" r="3.6" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/>')
    return "".join(out)


def trumpets():
    """Revelation 8:8-9: a great burning mountain thrown into the sea; a third of the sea becomes blood."""
    import build_tribulation_graphics as plate

    out = _sky("w70-trumpet-sky", "#26151c", "#b5502d")
    out.append('<defs><radialGradient id="w70-blood-spread" cx="0.5" cy="0" r="0.75"><stop offset="0" stop-color="#7a1010"/>'
               '<stop offset="0.65" stop-color="#8b1b1b" stop-opacity="0.9"/><stop offset="1" stop-color="#8b1b1b" stop-opacity="0"/></radialGradient>'
               '<radialGradient id="w70-mtn-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb347" stop-opacity="0.9"/>'
               '<stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient></defs>')
    out.append('<path d="M0 100 H240 V180 H0 Z" fill="#35597a"/>')
    out.append('<ellipse cx="122" cy="104" rx="130" ry="84" fill="url(#w70-blood-spread)" clip-path="inset(100px 0 0 0)"/>')
    for y in (112, 128, 144, 162):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#fff" stroke-width="1.2" fill="none" opacity="0.26"/>')
    out.append('<ellipse cx="108" cy="62" rx="62" ry="50" fill="url(#w70-mtn-glow)"/>')
    out.append('<g transform="rotate(24 112 64)"><path d="M76 96 L84 64 L72 52 L90 38 L96 20 L110 30 L124 14 L134 36 L152 46 L142 66 L150 96 Z" fill="#4a3226" stroke="#1c120d" stroke-width="1.6" stroke-linejoin="round"/>'
               '<path d="M90 46 L104 60 L96 80 M122 34 L118 56 L132 74" stroke="#e0662a" stroke-width="2" fill="none"/>'
               '<path d="M86 38 Q96 8 108 28 Q112 4 124 12 Q138 24 134 36 Q122 24 118 38 Q108 22 100 40 Q94 30 86 38 Z" fill="#f08a3a"/>'
               '<path d="M96 36 Q104 20 112 34 Q118 24 126 34 Q114 30 108 42 Q102 30 96 36 Z" fill="#f8d56a"/></g>')
    out.append('<path d="M150 18 Q176 40 160 70 M160 14 Q186 36 170 62" stroke="#8a8278" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.5"/>')
    out.append('<path d="M96 100 Q106 88 112 100 Q120 84 130 98 Q138 86 146 100" fill="none" stroke="#fff" stroke-width="2.4" opacity="0.8"/>')
    out.append(plate.ship(196, 120, 0.44, wrecked=True))
    out.append(plate.ship(34, 126, 0.42))
    out.append(plate.fish(64, 152, 0.5, dead=False))
    out.append(plate.fish(190, 156, 0.5, dead=True))
    out.append(plate.fish(150, 146, 0.45, dead=True))
    ax, ay, asc = 30, 58, 0.5
    out.append(angel(ax, ay, asc, 1, pose="offer", spread=0.9))
    hx, hy = ax + 36 * asc, ay - 58 * asc
    out.append(f'<path d="M{hx:.1f} {hy:.1f} L{hx + 30:.1f} {hy - 6:.1f}" stroke="{GOLD_DK}" stroke-width="3" stroke-linecap="round"/>'
               f'<path d="M{hx + 30:.1f} {hy - 6:.1f} L{hx + 42:.1f} {hy - 14:.1f} L{hx + 42:.1f} {hy + 4:.1f} Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    return "".join(out)


def _head(x, y, s, face=1, crown=True, horns=1, fill=BLOOD, edge="#2a0c0c", open_mouth=True):
    """A dragon's head in profile, facing right at face = 1: a long snout, a mouth with teeth, a swept horn."""
    parts = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face:.3f} {s:.3f})">']
    for h in range(horns):
        d = h * 9
        parts.append(f'<path d="M{-2 - d} -10 C{-10 - d} -20 {-20 - d} -18 {-26 - d} -8 C{-18 - d} -12 {-10 - d} -10 {-4 - d} -6 Z" fill="{edge}"/>')
    parts.append(f'<path d="M-11 6 C-13 -4 -5 -12 8 -12 C17 -12 25 -9 32 -4 C35 -2 34 1 31 2 L25 2 L30 6 C28 8 25 8 22 7 '
                 f'C16 11 6 11 -3 10 C-7 10 -10 9 -11 6 Z" fill="{fill}" stroke="{edge}" stroke-width="1.5" stroke-linejoin="round"/>')
    parts.append(f'<path d="M12 2 L31 1" stroke="{edge}" stroke-width="1.4" fill="none"/>')
    parts.append(f'<path d="M16 2 l2 4 l2 -4 M22 2 l2 3.6 l2 -3.6" fill="#fff" stroke="{edge}" stroke-width="0.6"/>')
    parts.append(f'<circle cx="9" cy="-5" r="2" fill="#f6d36a" stroke="{edge}" stroke-width="0.6"/><circle cx="9.4" cy="-5" r="0.8" fill="{edge}"/>')
    if crown:
        parts.append(f'<path d="M-6 -12 L-5 -18 L-1 -14 L3 -19 L7 -14 L11 -18 L12 -12 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/>')
    parts.append("</g>")
    return "".join(parts)


def _seven_heads(cx, cy, s, fill, edge, crown, rise=0):
    """Seven heads on seven necks, ten horns among them (Revelation 12:3; 13:1): the middle head tallest."""
    horns = (2, 1, 2, 1, 1, 2, 1)
    out = []
    for i in range(7):
        off = i - 3
        hx, hy = cx + off * 15.5 * s, cy - (46 - abs(off) * 7 + rise) * s
        c1x, c1y = cx + off * 4 * s, cy - 26 * s
        out.append(f'<path d="M{cx + off * 5 * s:.1f} {cy:.1f} C{c1x:.1f} {c1y:.1f} {hx - off * 2 * s:.1f} {hy + 18 * s:.1f} {hx:.1f} {hy + 4 * s:.1f}" '
                   f'stroke="{edge}" stroke-width="{9.4 * s:.1f}" fill="none" stroke-linecap="round"/>')
        out.append(f'<path d="M{cx + off * 5 * s:.1f} {cy:.1f} C{c1x:.1f} {c1y:.1f} {hx - off * 2 * s:.1f} {hy + 18 * s:.1f} {hx:.1f} {hy + 4 * s:.1f}" '
                   f'stroke="{fill}" stroke-width="{7 * s:.1f}" fill="none" stroke-linecap="round"/>')
        out.append(_head(hx, hy, s * 0.9, 1 if off >= 0 else -1, crown, horns[i], fill, edge))
    return "".join(out)


def dragon():
    """Revelation 12:3-9: the great red dragon with seven heads, ten horns and seven diadems, thrown down."""
    out = _sky("w70-dragon-sky", "#0f0b1c", "#7a2a22")
    for x, y in ((22, 18), (60, 40), (96, 14), (150, 30), (206, 22), (226, 60), (30, 70)):
        out.append(_star(x, y, 3.6))
    for k, (x, y) in enumerate(((170, 70), (190, 92), (206, 116), (216, 140))):
        out.append(f'<path d="M{x - 18} {y - 20} L{x} {y}" stroke="#f6e7a8" stroke-width="1.4" opacity="0.7"/>' + _star(x, y, 4.2, "#f6e7a8"))
    out.append(f'<path d="M96 170 C60 160 70 120 110 116 C150 112 150 84 120 76" stroke="{BLOOD}" stroke-width="22" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="M96 170 C60 160 70 120 110 116 C150 112 150 84 120 76" stroke="#c9382d" stroke-width="2" fill="none" stroke-dasharray="3 6" opacity="0.7"/>')
    out.append(f'<path d="M30 172 C60 178 96 176 150 160 C190 148 220 120 232 80" stroke="{BLOOD}" stroke-width="10" fill="none" stroke-linecap="round"/>')
    out.append(_seven_heads(120, 80, 1.05, BLOOD, "#2a0c0c", True, rise=-6))
    out.append(angel(34, 70, 0.5, 1, pose="point", spread=0.9))
    out.append(f'<path d="M50 28 L96 58" stroke="#d8d8d8" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(out)


def beast():
    """Revelation 13:1-8: the beast out of the sea, a leopard's body, a bear's feet, seven heads, ten horns, worshipped."""
    out = _sky("w70-beast-sky", "#1d1722", "#8a7058")
    out.append('<path d="M0 108 H240 V180 H0 Z" fill="#2f4a62"/>')
    for y in (118, 134, 152, 168):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#fff" stroke-width="1.1" fill="none" opacity="0.2"/>')
    spots = "".join(f'<ellipse cx="{x}" cy="{y}" rx="4.2" ry="3" fill="#3a2812"/>' for x, y in ((84, 100), (102, 106), (122, 98), (142, 104), (160, 98), (96, 116), (118, 118), (140, 116)))
    out.append('<path d="M184 96 Q214 84 218 112 Q206 98 188 108 Z" fill="#b98a4a" stroke="#2a1d10" stroke-width="1.4"/>')
    for lx in (84, 106, 138, 160):
        out.append(f'<path d="M{lx} 112 V128" stroke="#2a1d10" stroke-width="11" stroke-linecap="round"/>'
                   f'<path d="M{lx} 112 V128" stroke="#5a3f26" stroke-width="8.6" stroke-linecap="round"/>'
                   f'<ellipse cx="{lx}" cy="130" rx="8" ry="4" fill="#5a3f26" stroke="#2a1d10" stroke-width="1.2"/>')
    out.append('<path d="M70 104 C70 84 96 80 122 82 C150 82 178 84 180 104 C178 118 150 122 122 120 C96 122 70 118 70 104 Z" fill="#b98a4a" stroke="#2a1d10" stroke-width="1.6"/>')
    out.append(spots)
    out.append(_seven_heads(125, 86, 0.98, "#b98a4a", "#2a1d10", True, rise=-4))
    for k, x in enumerate((26, 54, 84, 150, 182, 210)):
        body, _ = comic.figure("man" if k % 2 else "woman", x, 176, 0.48, 1 if x < 120 else -1, pose="fold", stance="kneel", tone=k)
        out.append(body)
    return "".join(out)


def woman_wings():
    """Revelation 12:1, 14-16: a woman with the sun, the moon and twelve stars, given the two wings of the great eagle."""
    out = _sky("w70-woman-sky", "#f2b98a", "#e8d7a8")
    out.append('<circle cx="120" cy="84" r="52" fill="#fff0b8" opacity="0.85"/>')
    out.append('<path d="M0 126 Q50 110 100 124 T240 114 V180 H0 Z" fill="#c9b07e"/>')
    out.append('<path d="M0 150 Q60 138 120 148 T240 142 V180 H0 Z" fill="#b59a66"/>')
    # The serpent's flood, poured out of his mouth after her (12:15) and swallowed by the earth (12:16).
    out.append('<path d="M40 30 C56 46 70 60 82 80 C92 98 70 116 108 124 C140 132 170 134 196 146" fill="none" stroke="#6aa0cf" stroke-width="5.6" stroke-linecap="round" opacity="0.9"/>')
    out.append('<path d="M40 30 C56 46 70 60 82 80 C92 98 70 116 108 124 C140 132 170 134 196 146" fill="none" stroke="#fff" stroke-width="1" stroke-dasharray="3 7" opacity="0.7"/>')
    out.append('<ellipse cx="204" cy="150" rx="16" ry="5" fill="#2a1d10"/><path d="M190 146 L200 140 M218 146 L208 140" stroke="#3e3122" stroke-width="1.6"/>')
    out.append(_head(26, 28, 1.05, 1, False, 1, BLOOD, "#2a0c0c"))
    for k in range(4):
        out.append(f'<path d="M{20 + k * 3} {44 + k * 2} Q{34 + k * 4} {58} {42 + k * 5} {50 + k * 4}" fill="none" stroke="{BLOOD}" stroke-width="5" stroke-linecap="round"/>' if k == 0 else '')
    out.append(wings(120, 92, 1.3, 1, 1.15))
    body, _ = comic.figure("woman", 120, 160, 1.04, 1, pose="open")
    out.append(body)
    out.append('<path d="M104 160 A17 17 0 1 0 104 170 A13 13 0 1 1 104 160 Z" fill="#f2efe8" stroke="#8a8278" stroke-width="1" transform="translate(4 -2)"/>')
    for k in range(12):
        a = math.radians(208 + 124 * k / 11)
        out.append(_star(120 + 26 * math.cos(a), 38 + 12 * math.sin(a), 3.2, GOLD))
    return "".join(out)


def bowls():
    """Revelation 15:5-16:3: the tent of witness opened in heaven and full of smoke, an angel in bright linen pouring a golden bowl."""
    out = _sky("w70-bowls-sky", "#3a1620", "#c25a34")
    out.append('<path d="M0 128 H240 V180 H0 Z" fill="#6e1c1c"/>')
    for y in (140, 152, 166):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#e0867a" stroke-width="1.1" fill="none" opacity="0.4"/>')
    # The tent, its flap drawn back, smoke from the glory of God (15:8).
    out.append('<path d="M6 128 L46 52 L86 128 Z" fill="#e8dcc0" stroke="#8d7650" stroke-width="1.5"/>'
               '<path d="M46 52 L30 128 H62 Z" fill="#2a1d18"/><path d="M46 52 L36 128 M46 52 L56 128" stroke="#8d7650" stroke-width="1.2"/>'
               '<path d="M46 50 C26 38 56 24 40 8 C34 2 44 -2 50 4" fill="none" stroke="#bdb2a4" stroke-width="10" stroke-linecap="round" opacity="0.65"/>')
    out.append(angel(150, 120, 0.8, -1, pose="offer", spread=1.0))
    out.append(f'<path d="M108 66 q-14 -2 -18 6 q10 10 24 4 q10 -2 -6 -10 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    out.append(f'<path d="M96 76 C88 92 94 110 90 128" fill="none" stroke="{BLOOD}" stroke-width="3.6" stroke-linecap="round"/>')
    out.append(f'<path d="M80 130 Q90 138 100 130" fill="none" stroke="#d2493d" stroke-width="2.4"/>')
    for i in range(7):
        out.append(f'<path d="M{150 + i * 11} 22 h8 a4 3.6 0 0 1 -8 0 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.9"/>')
    return "".join(out)


def second_coming():
    """Revelation 19:11-16: heaven opened, a rider on a white horse, the armies of heaven following on white horses."""
    import build_tribulation_graphics as plate

    out = _sky("w70-return-sky", "#1c2a4d", "#a9bfe0")
    out.append('<defs><radialGradient id="w70-return-glow" cx="0.5" cy="0.42" r="0.5"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.7"/>'
               '<stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-return-glow)"/>')
    for k in range(14):
        a = math.pi * (0.06 + 0.88 * k / 13)
        out.append(f'<path d="M120 60 L{120 + 200 * math.cos(a):.1f} {60 - 200 * math.sin(a) * 0.3:.1f}" stroke="#fff" stroke-width="2" opacity="0.16"/>')
    out.append(f'<path d="M0 36 Q60 20 120 34 T240 30 V0 H0 Z" fill="#101a33"/>')
    out.append('<path d="M0 160 Q60 148 120 156 T240 150 V180 H0 Z" fill="#6e7d5a"/>')
    for x, y, s in ((120, 96, 0.34), (12, 106, 0.36)):
        out.append(plate.horse(x, y, "#f5f1e6", "#7d7464", s))
        r, _ = plate.rider(x + plate.SEAT[0] * s, y + plate.SEAT[1] * s, "#f4ecd6", s=s * 1.1, arm=(30,))
        out.append(r)
    s = 0.62
    x, y = 62, 82
    out.append(plate.horse(x, y, "#fbf8ee", "#8a8070", s))
    rx, ry = x + plate.SEAT[0] * s, y + plate.SEAT[1] * s
    r, hand = plate.rider(rx, ry, "#7a1a1a", s=s * 1.15, arm=(40,))
    out.append(r)
    out.append(f'<path d="M{rx - 10 * s:.1f} {ry - 4 * s:.1f} C{rx - 28 * s:.1f} {ry - 2 * s:.1f} {rx - 40 * s:.1f} {ry + 10 * s:.1f} {rx - 46 * s:.1f} {ry + 26 * s:.1f}" stroke="{BLOOD}" stroke-width="{6 * s:.1f}" fill="none" opacity="0.85"/>')
    hx, hy = rx + 9 * s * 1.15, ry - 50 * s * 1.15
    for k in range(5):
        out.append(f'<ellipse cx="{hx:.1f}" cy="{hy - 9 - k * 2.4:.1f}" rx="{8 - k * 0.3:.1f}" ry="1.8" fill="none" stroke="{GOLD}" stroke-width="1.4"/>')
    out.append(f'<path d="M{hx + 4:.1f} {hy:.1f} L{hx + 70:.1f} {hy - 10:.1f}" stroke="#e8e8f0" stroke-width="2.2" stroke-linecap="round"/>')
    return "".join(out)


def martyrs():
    """Revelation 6:9-11: the souls of the slain under the altar, each given a white robe."""
    out = _sky("w70-martyr-sky", "#efe3c4", "#cdb888")
    out.append('<path d="M0 142 H240 V180 H0 Z" fill="#a8956a"/>')
    out.append(f'<rect x="48" y="40" width="144" height="26" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.6"/>'
               f'<path d="M48 40 L44 28 L56 40 M192 40 L196 28 L184 40 M120 40 L120 30" stroke="{GOLD_DK}" stroke-width="2.4" fill="none"/>'
               f'<rect x="56" y="66" width="128" height="76" fill="#cdb26a" stroke="{GOLD_DK}" stroke-width="1.4"/>'
               f'<rect x="62" y="66" width="116" height="76" fill="#241c14"/>')
    out.append('<path d="M120 38 C112 28 128 20 120 10" fill="none" stroke="#bdb2a4" stroke-width="3.4" stroke-linecap="round" opacity="0.8"/>')
    for k, x in enumerate((82, 108, 134, 160)):
        body, _ = comic.figure("robed", x, 140, 0.5, 1 if k % 2 == 0 else -1, pose="look_up", stance="kneel", tone=k)
        out.append(body)
    return "".join(out)


def two_witnesses():
    """Revelation 11:3-5: two witnesses in sackcloth, fire pouring from their mouths on those who would harm them."""
    out = list(comic.SCENES["street"](240, 180, "storm", "w70-witness-sky"))
    for x, tone, face in ((52, 0, 1), (88, 1, 1)):
        body, (hx, hy, hs) = comic.figure("witness", x, 150, 0.95, face, pose="open" if tone == 0 else "point", tone=tone)
        out.append(body)
    out.append(comic.flame_jet(68, 84, 168, 92, 0.5))
    out.append(comic.flame_jet(104, 86, 176, 104, 0.4))
    for x, face in ((178, -1), (206, -1)):
        body, _ = comic.figure("soldier", x, 150, 0.9, face, pose="stand", holds="spear")
        out.append(body)
    out.append('<path d="M40 24 L56 10 L52 24 L66 16" stroke="#f6e7a8" stroke-width="2" fill="none" opacity="0.8"/>')
    return "".join(out)


ART = {
    "lamb_scroll": ("the throne under its rainbow with twenty-four crowns round it, the Lamb standing as though slain, and the scroll with seven seals (Revelation 4-5)", lamb_scroll),
    "seals_1_4": ("four riders on a white, a red, a black and a pale horse galloping under a storm sky (Revelation 6:1-8)", horsemen_four),
    "two_witnesses": ("two men in sackcloth with fire pouring from their mouths toward soldiers with spears (Revelation 11:3-5)", two_witnesses),
    "martyrs": ("white-robed souls kneeling under the altar (Revelation 6:9-11)", martyrs),
    "seal6": ("the sun black as sackcloth, the moon like blood, stars falling and the sky rolled up like a scroll (Revelation 6:12-14)", seal6),
    "sealed144": ("four angels holding the four winds at the corners of the earth and an angel rising from the east with the seal of the living God; twelve seals along the foot, one for each tribe (Revelation 7:1-8)", sealed144),
    "trumpets_1_6": ("a great burning mountain thrown into the sea, a third of the sea turned to blood, a wrecked ship and dead fish, and an angel with a trumpet (Revelation 8:8-9)", trumpets),
    "war_heaven": ("the great red dragon with seven heads, ten horns and seven diadems thrown down with a third of the stars, and an angel with a spear (Revelation 12:3-9)", dragon),
    "wilderness": ("a woman with the sun behind her, the moon under her feet and twelve stars above, borne on the two wings of the great eagle over the wilderness, the serpent's flood swallowed by the earth (Revelation 12:1, 14-16)", woman_wings),
    "beast_mark": ("the beast from the sea with a leopard's body, seven heads and ten horns, and people kneeling before it (Revelation 13:1-8)", beast),
    "bowls": ("the temple opened and filled with smoke, and an angel in bright linen pouring a golden bowl on the sea turned to blood, with seven golden bowls (Revelation 15:5-16:3)", bowls),
    "second_coming": ("heaven opened, a rider on a white horse with many diadems and a sword from His mouth, the armies of heaven following on white horses (Revelation 19:11-16)", second_coming),
}
