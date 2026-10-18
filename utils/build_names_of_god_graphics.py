"""Draw the name plates for god/names-of-god.md.

    uv run --with uharfbuzz --with fonttools python3 utils/build_names_of_god_graphics.py

One plate per name, set above the section that treats it. Each plate puts the name in large Hebrew
with its Paleo-Hebrew form beneath, the transliteration and meaning, the verse where the name was
given (ESV), and a small imagery scene of that moment: the burning bush, the spring in the
wilderness, the ram in the thicket, Moses' hands held up on the hill. The key under the scene gives
the verse for every element drawn. Elements the text does not state are drawn dashed and listed as
such. Following drawn-graphics.md, no face of God is drawn: His presence is light or fire, as the
text gives it, and people are small unindividuated figures.

The Hebrew, its Paleo form, the transliteration and the meaning are read from
docs/data/hebrew-cards.json (export_hebrew_cards.py), the same machine-checked forms the word cards
print. The Hebrew is drawn as outlines (lib/outline_text.py), so it needs no font on the reader's
side.
"""

import json
import math
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        EARTH_TINT, esc, text)
from lib.outline_text import place, PALEO

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "names-of-god"
CARDS = ROOT / "docs" / "data" / "hebrew-cards.json"

# Scene palette, named here rather than scattered through the shapes.
SKY_DAY = "#f4e9cf"
SKY_DUSK = "#e9cfa2"
NIGHT_TOP = "#1d2740"
NIGHT_LOW = "#3d4c70"
SAND = "#e4d2ab"
SAND_DARK = "#cdb487"
HILL = "#c9b48c"
HILL_FAR = "#d8c8a5"
STONE = "#a89a84"
STONE_EDGE = "#6e6455"
WOOD = "#8a6236"
LEAF = "#6f7f45"
LEAF_DARK = "#4f5d30"
WATER = "#8fb0c4"
WATER_DARK = "#5f8299"
FLAME = "#e07a2e"
FLAME_HOT = "#f2b84b"
FIGURE = "#4a3b28"
FIGURE_LIGHT = "#7a6648"
STAR = "#f6e7b0"

SX, SY, SW, SH = 28, 28, 316, 252   # the scene frame
RX = 532                             # centre of the name column
FIGURE_STROKE = f'stroke="{FIGURE}" stroke-width="2.4" stroke-linecap="round" fill="none"'


def wrap(s, width):
    words, rows, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            rows.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        rows.append(cur)
    return rows


# ---------------------------------------------------------------- scene primitives (local coords)

def sky(top, low, gid):
    return [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{low}"/>'
            f'</linearGradient></defs>',
            f'<rect width="{SW}" height="{SH}" fill="url(#{gid})"/>']


def glow(cx, cy, r, colour, gid, strength=0.85):
    return [f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{colour}" '
            f'stop-opacity="{strength}"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/>'
            f'</radialGradient></defs>',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>']


def ground(y, colour=SAND, edge=SAND_DARK, wobble=6):
    d = f"M0 {y} " + " ".join(
        f"Q{x + 20} {y - wobble * (1 if (x // 40) % 2 else -1)} {x + 40} {y}" for x in range(0, SW, 40))
    return [f'<path d="{d} V{SH} H0 Z" fill="{colour}" stroke="{edge}" stroke-width="1.2"/>']


def hill(x0, x1, base, peak, colour=HILL, edge=SAND_DARK, px=None):
    px = (x0 + x1) / 2 if px is None else px
    return [f'<path d="M{x0} {base} C{x0 + (px - x0) * 0.5} {base} {px - 30} {peak} {px} {peak} '
            f'C{px + 30} {peak} {x1 - (x1 - px) * 0.5} {base} {x1} {base} Z" fill="{colour}" '
            f'stroke="{edge}" stroke-width="1.2"/>']


def stars(points, r=1.6):
    out = []
    for x, y, s in points:
        rr = r * s
        out.append(f'<path d="M{x} {y - rr * 2.2} L{x + rr * 0.6} {y - rr * 0.6} L{x + rr * 2.2} {y} '
                   f'L{x + rr * 0.6} {y + rr * 0.6} L{x} {y + rr * 2.2} L{x - rr * 0.6} {y + rr * 0.6} '
                   f'L{x - rr * 2.2} {y} L{x - rr * 0.6} {y - rr * 0.6} Z" fill="{STAR}"/>')
    return out


def star_field(n, seed, y_max):
    pts, a = [], seed
    for i in range(n):
        a = (a * 1103515245 + 12345) % 2 ** 31
        x = 6 + a % (SW - 12)
        a = (a * 1103515245 + 12345) % 2 ** 31
        y = 6 + a % y_max
        pts.append((x, y, 0.5 + (i % 5) * 0.22))
    return stars(pts)


def figure(x, y, pose="stand", h=46, fill=FIGURE, facing=1):
    """A small unindividuated figure; (x, y) is where the feet meet the ground."""
    f = facing
    head = h * 0.13
    if pose == "prostrate":
        return [f'<path d="M{x - f * h * 0.55} {y} Q{x} {y - h * 0.22} {x + f * h * 0.45} {y} Z" fill="{fill}"/>',
                f'<circle cx="{x + f * h * 0.52}" cy="{y - head * 0.8}" r="{head}" fill="{fill}"/>']
    if pose == "kneel":
        top = y - h * 0.62
        return [f'<path d="M{x - h * 0.2} {y} L{x - h * 0.16} {top + head * 2} Q{x} {top + head * 1.2} '
                f'{x + h * 0.16} {top + head * 2} L{x + h * 0.32} {y} Z" fill="{fill}"/>',
                f'<circle cx="{x + f * h * 0.03}" cy="{top + head * 0.9}" r="{head}" fill="{fill}"/>']
    if pose == "seated":
        top = y - h * 0.72
        return [f'<path d="M{x - h * 0.16} {y - h * 0.18} L{x - h * 0.13} {top + head * 2} '
                f'Q{x} {top + head * 1.2} {x + h * 0.13} {top + head * 2} L{x + h * 0.26} {y - h * 0.18} '
                f'L{x + h * 0.3} {y} L{x - h * 0.2} {y} Z" fill="{fill}"/>',
                f'<circle cx="{x}" cy="{top + head * 0.9}" r="{head}" fill="{fill}"/>']
    top = y - h
    body = (f'<path d="M{x - h * 0.17} {y} L{x - h * 0.12} {top + head * 2.1} Q{x} {top + head * 1.3} '
            f'{x + h * 0.12} {top + head * 2.1} L{x + h * 0.17} {y} Z" fill="{fill}"/>')
    out = [body, f'<circle cx="{x}" cy="{top + head}" r="{head}" fill="{fill}"/>']
    if pose == "arms_up":
        out.append(f'<path d="M{x - h * 0.1} {top + head * 2.6} L{x - h * 0.3} {top - h * 0.05} '
                   f'M{x + h * 0.1} {top + head * 2.6} L{x + h * 0.3} {top - h * 0.05}" '
                   f'stroke="{fill}" stroke-width="{h * 0.07:.1f}" stroke-linecap="round"/>')
    if pose == "look_up":
        out.append(f'<path d="M{x + f * h * 0.1} {top + head * 2.6} L{x + f * h * 0.42} {top - h * 0.02}" '
                   f'stroke="{fill}" stroke-width="{h * 0.07:.1f}" stroke-linecap="round"/>')
    return out


def tent(x, y, w=70, h=44, dashed=False):
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    return [f'<path d="M{x} {y} L{x + w * 0.5} {y - h} L{x + w} {y} Z" fill="{EARTH_TINT}" '
            f'stroke="{INK}" stroke-width="1.3"{dash}/>',
            f'<path d="M{x + w * 0.5} {y - h} L{x + w * 0.42} {y} L{x + w * 0.58} {y} Z" fill="{FIGURE_LIGHT}"/>',
            f'<path d="M{x + w * 0.5} {y - h} V{y - h - 8}" stroke="{INK}" stroke-width="1.3"/>']


def stones(x, y, w, rows=3, h=12, fill=STONE, dashed=False):
    """A heap-built altar of unhewn stones, bottom row at y."""
    dash = ' stroke-dasharray="3 2"' if dashed else ""
    out = []
    for r in range(rows):
        n = max(2, int((w - r * 10) // 22))
        ww = (w - r * 10) / n
        for i in range(n):
            sx = x + r * 5 + i * ww
            out.append(f'<rect x="{sx:.1f}" y="{y - (r + 1) * h:.1f}" width="{ww - 1.5:.1f}" height="{h - 1.5}" '
                       f'rx="4" fill="{fill}" stroke="{STONE_EDGE}" stroke-width="1"{dash}/>')
    return out


def flames(cx, base, w, h):
    out = []
    for i, (dx, sc, col) in enumerate([(-0.32, 0.7, FLAME), (0.3, 0.75, FLAME), (0, 1.0, FLAME),
                                       (-0.12, 0.62, FLAME_HOT), (0.14, 0.58, FLAME_HOT)]):
        x = cx + dx * w
        hh = h * sc
        ww = w * 0.32
        out.append(f'<path d="M{x - ww} {base} C{x - ww} {base - hh * 0.5} {x - ww * 0.2} {base - hh * 0.6} '
                   f'{x} {base - hh} C{x + ww * 0.3} {base - hh * 0.55} {x + ww} {base - hh * 0.45} '
                   f'{x + ww} {base} Z" fill="{col}" opacity="0.88"/>')
    return out


def palm(x, y, h=18):
    return [f'<path d="M{x} {y} Q{x + 1.5} {y - h * 0.5} {x} {y - h}" stroke="{WOOD}" stroke-width="1.3" fill="none"/>',
            f'<path d="M{x} {y - h} q-6 -1 -8 4 M{x} {y - h} q6 -1 8 4 M{x} {y - h} q-4 -5 -9 -3 '
            f'M{x} {y - h} q4 -5 9 -3" stroke="{LEAF}" stroke-width="1.4" fill="none"/>']


def tree(x, y, h=110, w=110):
    """A broad terebinth: trunk and a rounded crown of overlapping masses."""
    out = [f'<path d="M{x - 7} {y} Q{x - 3} {y - h * 0.4} {x - 9} {y - h * 0.62} M{x + 7} {y} '
           f'Q{x + 4} {y - h * 0.45} {x + 14} {y - h * 0.6}" stroke="{WOOD}" stroke-width="9" '
           f'stroke-linecap="round" fill="none"/>']
    for dx, dy, r, c in [(-w * 0.3, -h * 0.68, w * 0.24, LEAF_DARK), (w * 0.28, -h * 0.66, w * 0.24, LEAF_DARK),
                         (0, -h * 0.82, w * 0.3, LEAF), (-w * 0.12, -h * 0.66, w * 0.22, LEAF),
                         (w * 0.14, -h * 0.72, w * 0.22, LEAF)]:
        out.append(f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="{r:.1f}" fill="{c}" stroke="{LEAF_DARK}" stroke-width="0.8"/>')
    return out


# ---------------------------------------------------------------- the scenes

def scene_ehyeh():
    out = sky(SKY_DUSK, SKY_DAY, "s1")
    out += hill(-20, 250, 200, 52, HILL_FAR, px=120)
    out += [text(120, 46, "Horeb", 12, "middle", fill=MUTED, italic=True)]
    out += ground(196)
    out += glow(196, 150, 70, FLAME_HOT, "g1", 0.7)
    out += [f'<path d="M184 200 L178 172 M190 200 L188 164 M200 200 L204 166 M208 200 L216 174" '
            f'stroke="{WOOD}" stroke-width="2.2" stroke-linecap="round"/>']
    for dx, dy, r in [(-22, -16, 13), (20, -18, 14), (-8, -28, 15), (10, -32, 14), (0, -12, 16),
                      (-30, -6, 9), (30, -8, 10)]:
        out.append(f'<circle cx="{196 + dx}" cy="{198 + dy}" r="{r}" fill="{LEAF_DARK}" '
                   f'stroke="{LEAF}" stroke-width="1"/>')
    out += flames(196, 176, 52, 80)
    out += figure(96, 218, "stand", 52, facing=1)
    # The sandals, taken off (Exodus 3:5).
    out += [f'<ellipse cx="118" cy="226" rx="7" ry="2.6" fill="{WOOD}"/>',
            f'<ellipse cx="132" cy="229" rx="7" ry="2.6" fill="{WOOD}"/>']
    for sx in (34, 52, 274):
        out += [f'<ellipse cx="{sx}" cy="214" rx="9" ry="6" fill="{CARD}" stroke="{STONE_EDGE}" stroke-width="1"/>',
                f'<circle cx="{sx + 9}" cy="210" r="3.4" fill="{FIGURE_LIGHT}"/>']
    return out


def scene_yhwh(paleo):
    out = [f'<rect width="{SW}" height="{SH}" fill="{SKY_DAY}"/>']
    # A scroll column, schematic: grey strokes for the square-script text, the name in the old letters.
    out.append(f'<path d="M34 28 L282 22 L286 226 L30 232 Z" fill="{GOLD_TINT}" stroke="{STONE_EDGE}" '
               f'stroke-width="1.3" stroke-dasharray="5 3"/>')
    for i, y in enumerate(range(48, 216, 18)):
        if i == 4:
            out.append(f'<rect x="50" y="{y - 5}" width="96" height="4" rx="2" fill="{STONE}"/>')
            p, _ = place(paleo, 196, y + 7, 30, font=PALEO, weight=400, fill=INK)
            out.append(p)
            out.append(f'<rect x="232" y="{y - 5}" width="38" height="4" rx="2" fill="{STONE}"/>')
            out.append(f'<rect x="160" y="{y - 22}" width="72" height="34" rx="5" fill="none" '
                       f'stroke="{RED}" stroke-width="1.6"/>')
        else:
            out.append(f'<rect x="{50 + (i % 3) * 6}" y="{y - 5}" width="{220 - (i % 4) * 14}" height="4" '
                       f'rx="2" fill="{STONE}"/>')
    return out


def scene_shaddai():
    out = sky(SKY_DAY, SKY_DUSK, "s3")
    out += glow(158, 30, 110, CARD, "g3", 0.95)
    out += [f'<path d="M158 0 L96 210 H220 Z" fill="{CARD}" opacity="0.35"/>']
    out += ground(200)
    out += tent(214, 204, 74, 50)
    out += figure(150, 210, "prostrate", 56, facing=1)
    out += [text(158, 40, "Abram → Abraham", 15, "middle", "bold", fill=INK),
            text(158, 58, "“father of a multitude”", 12.5, "middle", fill=MUTED, italic=True)]
    return out


def scene_adonai():
    out = sky(NIGHT_TOP, NIGHT_LOW, "s4")
    out += star_field(150, 7, 170)
    out += ground(206, "#3a3426", "#26221a")
    out += tent(206, 212, 70, 46)
    out += figure(130, 222, "look_up", 54, fill="#17120b", facing=1)
    return out


def scene_elyon():
    out = sky(SKY_DAY, SKY_DUSK, "s5")
    out += hill(90, 340, 200, 96, HILL_FAR, px=230)
    # Salem's walls on the hill.
    out += [f'<path d="M188 102 H272 V80 H262 V88 H252 V80 H242 V88 H232 V80 H222 V88 H212 V80 H202 V88 H188 Z" '
            f'fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.2"/>',
            text(230, 122, "Salem", 12, "middle", fill=MUTED, italic=True)]
    out += ground(190)
    out += figure(110, 222, "stand", 54, facing=1)
    out += figure(214, 222, "stand", 54, facing=-1)
    # Bread and a jar of wine set down between them (Genesis 14:18).
    out += [f'<ellipse cx="150" cy="222" rx="13" ry="7" fill="#d9a85a" stroke="{WOOD}" stroke-width="1"/>',
            f'<ellipse cx="166" cy="225" rx="10" ry="5.5" fill="#d9a85a" stroke="{WOOD}" stroke-width="1"/>',
            f'<path d="M180 228 Q174 214 181 206 H189 Q196 214 190 228 Z" fill="{RED}" stroke="{INK}" stroke-width="1"/>',
            f'<rect x="181" y="201" width="8" height="6" fill="{RED}" stroke="{INK}" stroke-width="1"/>']
    return out


def scene_roi():
    out = sky(SKY_DUSK, SKY_DAY, "s6")
    out += glow(250, 50, 60, FLAME_HOT, "g6", 0.6)
    out += ground(168, SAND, SAND_DARK, 8)
    out += [f'<path d="M0 190 Q80 180 160 192 T{SW} 186" stroke="{SAND_DARK}" stroke-width="1.2" fill="none"/>']
    # The spring, ringed with stones.
    out += [f'<ellipse cx="190" cy="212" rx="60" ry="16" fill="{WATER}" stroke="{WATER_DARK}" stroke-width="1.4"/>',
            f'<ellipse cx="184" cy="210" rx="26" ry="5" fill="{CARD}" opacity="0.45"/>']
    for i in range(14):
        a = math.pi * 2 * i / 14
        out.append(f'<ellipse cx="{190 + 66 * math.cos(a):.1f}" cy="{212 + 20 * math.sin(a):.1f}" rx="7" ry="4.5" '
                   f'fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="0.9"/>')
    out += figure(96, 214, "seated", 52, facing=1)
    out += [text(158, 30, "Beer-lahai-roi", 14, "middle", "bold"),
            text(158, 46, "“the well of the Living One who sees me”", 11.5, "middle", fill=MUTED, italic=True)]
    out += [text(298, 158, "to Shur →", 11, "end", fill=MUTED, italic=True)]
    return out


def scene_yireh():
    out = sky(SKY_DAY, SKY_DUSK, "s7")
    out += hill(-40, 360, 250, 96, HILL, px=160)
    out += stones(112, 196, 96, rows=3, h=14)
    # The wood laid in order on top (Genesis 22:9).
    for i in range(5):
        out.append(f'<rect x="{118 + i * 2}" y="{148 - i * 5}" width="{82 - i * 4}" height="5" rx="2" '
                   f'fill="{WOOD}" stroke="#5b3f20" stroke-width="0.8"/>')
    # The thicket, and the ram caught in it by his horns (Genesis 22:13).
    out += [f'<path d="M226 206 C214 176 236 160 252 168 C262 150 290 158 288 182 C302 192 296 210 284 210 Z" '
            f'fill="{LEAF_DARK}"/>']
    for d in ["M232 200 L246 172", "M244 206 L262 166", "M262 204 L280 172", "M276 206 L290 186"]:
        out.append(f'<path d="{d}" stroke="#3c2a16" stroke-width="1.6"/>')
    out += [f'<ellipse cx="254" cy="208" rx="26" ry="13" fill="{CARD}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<ellipse cx="230" cy="196" rx="9" ry="7.5" fill="{CARD}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<path d="M232 190 C240 180 252 186 246 196" stroke="{WOOD}" stroke-width="3.5" fill="none"/>',
            f'<path d="M238 222 V232 M248 222 V233 M262 222 V233 M272 220 V231" stroke="{STONE_EDGE}" stroke-width="2.4"/>']
    return out


def scene_rofekha():
    out = sky(SKY_DAY, SKY_DUSK, "s8")
    out += ground(130, SAND, SAND_DARK, 4)
    # Elim on the horizon: twelve springs and seventy palms (Exodus 15:27), counted, not suggested.
    for i in range(70):
        col, row = i % 14, i // 14
        out += palm(184 + col * 8.6 + (row % 2) * 4, 122 - row * 7 + (col % 3), 13)
    for i in range(12):
        out.append(f'<ellipse cx="{186 + i * 9.6:.1f}" cy="130" rx="3.2" ry="1.4" fill="{WATER_DARK}"/>')
    out += [text(244, 66, "Elim", 12, "middle", fill=MUTED, italic=True)]
    # Marah's pool, and the log thrown into it (Exodus 15:25).
    out += [f'<ellipse cx="140" cy="196" rx="108" ry="30" fill="{WATER}" stroke="{WATER_DARK}" stroke-width="1.4"/>',
            f'<path d="M70 196 Q100 190 130 196 M150 204 Q180 198 210 204" stroke="{CARD}" stroke-width="1.4" fill="none" opacity="0.7"/>',
            f'<path d="M96 168 L178 214" stroke="{WOOD}" stroke-width="7" stroke-linecap="round"/>',
            f'<path d="M120 182 l-8 -12 M150 198 l6 -12" stroke="{WOOD}" stroke-width="2.4" stroke-linecap="round"/>',
            text(140, 244, "Marah", 12, "middle", fill=MUTED, italic=True)]
    out += figure(268, 218, "arms_up", 48)
    return out


def scene_nissi():
    out = sky(SKY_DAY, SKY_DUSK, "s9")
    out += glow(40, 190, 50, FLAME_HOT, "g9", 0.5)
    out += hill(100, 380, 214, 58, HILL, px=236)
    out += ground(206)
    # On the hilltop: Moses seated on the stone, Aaron and Hur holding up his hands (Exodus 17:12).
    out += stones(222, 84, 30, rows=1, h=10)
    out += figure(236, 84, "seated", 40)
    out += figure(214, 86, "stand", 38)
    out += figure(258, 86, "stand", 38)
    out += [f'<path d="M232 60 L222 40 M240 60 L250 40" stroke="{FIGURE}" stroke-width="3" stroke-linecap="round"/>',
            f'<path d="M218 62 L222 44 M254 62 L250 44" stroke="{FIGURE}" stroke-width="2.4" stroke-linecap="round"/>',
            f'<path d="M250 40 L256 10" stroke="{WOOD}" stroke-width="3" stroke-linecap="round"/>']
    # Joshua's battle with Amalek on the plain below (Exodus 17:10).
    for i in range(6):
        x1, x2 = 30 + i * 15, 126 + i * 15
        y1, y2 = 228 + (i % 2) * 4, 228 + ((i + 1) % 2) * 4
        out += figure(x1, y1, "stand", 22)
        out += figure(x2, y2, "stand", 22, fill=FIGURE_LIGHT)
        out.append(f'<path d="M{x1 + 2} {y1 - 14} l9 -9 M{x2 - 2} {y2 - 14} l-9 -9" stroke="{STONE_EDGE}" '
                   f'stroke-width="1.4" stroke-linecap="round"/>')
    return out


def scene_shalom():
    out = sky(SKY_DAY, SKY_DUSK, "s10")
    out += ground(196)
    out += tree(84, 204, 150, 130)
    # Fire springing up from the rock (Judges 6:21).
    out += [f'<path d="M150 214 Q146 186 176 180 Q214 178 222 196 L226 214 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.3"/>']
    out += glow(188, 160, 46, FLAME_HOT, "g10", 0.6)
    out += flames(188, 184, 40, 52)
    # The winepress cut in the ground (Judges 6:11).
    out += [f'<ellipse cx="270" cy="222" rx="30" ry="9" fill="{SAND_DARK}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<ellipse cx="270" cy="220" rx="20" ry="5" fill="#b49c70"/>']
    out += figure(240, 232, "kneel", 50, facing=-1)
    return out


def scene_tsevaot():
    out = [f'<rect width="{SW}" height="{SH}" fill="{SKY_DAY}"/>']
    # The temple doorway at Shiloh, and Eli's seat beside the doorpost (1 Samuel 1:9).
    out += [f'<rect x="150" y="26" width="140" height="190" fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.3"/>',
            f'<rect x="186" y="78" width="68" height="138" fill="#5a4630"/>',
            f'<rect x="174" y="62" width="92" height="16" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<rect x="174" y="78" width="12" height="138" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<rect x="254" y="78" width="12" height="138" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>']
    out += ground(214, SAND, SAND_DARK, 0)
    out += [f'<rect x="124" y="196" width="40" height="8" fill="{WOOD}"/>',
            f'<path d="M128 204 V220 M160 204 V220" stroke="{WOOD}" stroke-width="3"/>']
    out += figure(144, 198, "seated", 44)
    out += figure(64, 230, "kneel", 52, facing=1)
    out += [text(66, 182, "only her lips moved", 11.5, "middle", fill=MUTED, italic=True)]
    return out


def scene_immanuel():
    out = sky(NIGHT_TOP, NIGHT_LOW, "s11")
    out += star_field(60, 3, 150)
    out += glow(170, 46, 60, STAR, "g11", 0.8)
    out += stars([(170, 46, 4)], r=2.4)
    out += [f'<path d="M170 60 V128" stroke="{STAR}" stroke-width="1.2" stroke-dasharray="2 4" opacity="0.8"/>']
    out += ground(206, "#3a3426", "#26221a")
    out += [f'<rect x="120" y="148" width="100" height="62" fill="#6b5a3e" stroke="#26221a" stroke-width="1.3"/>',
            f'<path d="M112 150 H228 L216 136 H124 Z" fill="#4e4130" stroke="#26221a" stroke-width="1.3"/>',
            f'<rect x="140" y="166" width="20" height="16" fill="{FLAME_HOT}"/>',
            f'<rect x="178" y="172" width="22" height="38" fill="#2c2418"/>']
    return out


def scene_gibbor():
    out = sky(SKY_DAY, SKY_DUSK, "s12")
    out += glow(158, 110, 110, GOLD, "g12", 0.55)
    out += [f'<path d="M60 236 H256 V222 H70 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<path d="M80 222 H236 V208 H90 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>']
    # The throne of David (Isaiah 9:7), with the crown upon it.
    out += [f'<path d="M110 208 V92 Q158 62 206 92 V208 Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>',
            f'<rect x="100" y="156" width="116" height="16" fill="{GOLD_EDGE}"/>',
            f'<rect x="104" y="172" width="12" height="36" fill="{GOLD_EDGE}"/>',
            f'<rect x="200" y="172" width="12" height="36" fill="{GOLD_EDGE}"/>',
            f'<path d="M134 152 L136 128 L146 140 L158 122 L170 140 L180 128 L182 152 Z" fill="{GOLD_TINT}" '
            f'stroke="{GOLD_EDGE}" stroke-width="1.6"/>']
    out += [text(158, 34, "the throne of David", 13, "middle", fill=MUTED, italic=True)]
    return out


def scene_tsidkenu():
    out = sky(SKY_DAY, SKY_DUSK, "s13")
    out += ground(200)
    # A stump, cut low, and the shoot coming up from it (Isaiah 11:1), the picture behind "Branch".
    out += [f'<path d="M100 214 L110 150 H206 L216 214 Z" fill="{WOOD}" stroke="#5b3f20" stroke-width="1.4"/>',
            f'<ellipse cx="158" cy="150" rx="48" ry="10" fill="#c79a62" stroke="#5b3f20" stroke-width="1.4"/>',
            f'<ellipse cx="158" cy="150" rx="30" ry="6" fill="none" stroke="#a87c48" stroke-width="1"/>',
            f'<ellipse cx="158" cy="150" rx="14" ry="3" fill="none" stroke="#a87c48" stroke-width="1"/>',
            f'<path d="M190 150 Q196 110 186 72 Q182 52 196 34" stroke="{LEAF}" stroke-width="4" fill="none" stroke-linecap="round"/>']
    for x, y, a in [(192, 120, -30), (186, 96, 30), (190, 72, -35), (194, 50, 25), (198, 36, -20)]:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="12" ry="5" fill="{LEAF}" transform="rotate({a} {x} {y})"/>')
    out += [f'<circle cx="202" cy="64" r="5" fill="{RED}"/>']
    return out


def scene_yeshua():
    out = sky(SKY_DUSK, SKY_DAY, "s14")
    out += glow(300, 160, 90, FLAME_HOT, "g14", 0.55)
    out += hill(-30, 210, 200, 60, HILL_FAR, px=80)
    # Three crosses, empty now (Matthew 27:38).
    for x, hh in [(50, 46), (80, 56), (110, 46)]:
        out.append(f'<path d="M{x} {66 + (56 - hh)} V{60 + 56} M{x - hh * 0.3:.1f} {80 + (56 - hh) * 0.6:.1f} '
                   f'H{x + hh * 0.3:.1f}" stroke="{INK}" stroke-width="3"/>')
    out += ground(190)
    # The tomb, its stone rolled back (Matthew 28:2).
    out += [f'<path d="M150 214 Q150 112 236 104 Q316 104 316 214 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.4"/>',
            f'<path d="M206 214 V176 Q206 152 230 152 Q254 152 254 176 V214 Z" fill="#2c2418"/>',
            f'<circle cx="152" cy="190" r="30" fill="#b9ab94" stroke="{STONE_EDGE}" stroke-width="1.6"/>',
            f'<circle cx="152" cy="190" r="22" fill="none" stroke="{STONE_EDGE}" stroke-width="0.8"/>',
            text(232, 238, "He is not here", 12.5, "middle", fill=INK, italic=True)]
    return out


# ---------------------------------------------------------------- the plates

PLATES = [
    # slug, card name, scene, transliteration shown, quote, ref, key: [(element, ref, stated)]
    ("ehyeh", "Ehyeh asher Ehyeh", scene_ehyeh, "Ehyeh asher Ehyeh",
     "“But I will be with you” … God said to Moses, “I AM WHO I AM.”", "Exodus 3:12, 14 (ESV)",
     [("Horeb, the mountain of God, and the flock", "Exodus 3:1", True),
      ("the bush burning, yet not consumed", "3:2", True),
      ("sandals off on holy ground", "3:5", True)]),
    ("yhwh", "YHWH", None, "YHWH, read Adonai",
     "This is my name forever, and thus I am to be remembered throughout all generations.",
     "Exodus 3:15 (ESV)",
     [("a scroll column in square script with the name in the old letters, as the Great Psalms Scroll "
       "(11Q5) writes it 164 times of 165", "Three Scripts", True),
      ("the column is schematic, not a facsimile", "", False)]),
    ("shaddai", "El Shaddai", scene_shaddai, "El Shaddai",
     "I am God Almighty; walk before me, and be blameless, that I may make my covenant between me and "
     "you, and may multiply you greatly.", "Genesis 17:1-2 (ESV)",
     [("the LORD appeared, drawn as light", "Genesis 17:1", True),
      ("Abram fell on his face", "17:3", True), ("Abram renamed Abraham", "17:5", True),
      ("his tent", "12:8", True)]),
    ("adonai", "Adonai", scene_adonai, "Adonai",
     "O Lord GOD, what will you give me, for I continue childless … “Look toward heaven, and number "
     "the stars, if you are able to number them.”", "Genesis 15:2, 5 (ESV)",
     [("brought outside", "Genesis 15:5", True), ("the stars he could not number", "15:5", True),
      ("his tent", "12:8", True)]),
    ("elyon", "El Elyon", scene_elyon, "El Elyon",
     "Blessed be Abram by God Most High, Possessor of heaven and earth.", "Genesis 14:19 (ESV)",
     [("Melchizedek king of Salem meets Abram", "Genesis 14:18", True),
      ("bread and wine", "14:18", True)]),
    ("roi", "El Roi", scene_roi, "El Roi",
     "So she called the name of the LORD who spoke to her, “You are a God of seeing.”",
     "Genesis 16:13 (ESV)",
     [("a spring of water in the wilderness, on the way to Shur", "Genesis 16:7", True),
      ("the well called Beer-lahai-roi", "16:14", True),
      ("the ring of stones round the spring", "", False)]),
    ("yireh", "YHWH Yireh", scene_yireh, "YHWH Yireh",
     "So Abraham called the name of that place, “The LORD will provide.”", "Genesis 22:14 (ESV)",
     [("the altar, and the wood laid in order", "Genesis 22:9", True),
      ("a ram caught in a thicket by his horns", "22:13", True),
      ("on the mount of the LORD", "22:14", True)]),
    ("rofekha", "YHWH Rofekha", scene_rofekha, "YHWH Rofekha",
     "for I am the LORD, your healer.", "Exodus 15:26 (ESV)",
     [("the bitter water of Marah, and the log thrown in", "Exodus 15:23-25", True),
      ("Moses cried to the LORD", "15:25", True),
      ("Elim's twelve springs and seventy palm trees, all drawn", "15:27", True)]),
    ("nissi", "YHWH Nissi", scene_nissi, "YHWH Nissi",
     "And Moses built an altar and called the name of it, The LORD Is My Banner.",
     "Exodus 17:15 (ESV)",
     [("Moses on the hill with the staff of God", "Exodus 17:9-10", True),
      ("seated on a stone, his hands held up by Aaron and Hur", "17:12", True),
      ("Joshua's battle with Amalek below, with the sword", "17:10, 13", True)]),
    ("shalom", "YHWH Shalom", scene_shalom, "YHWH Shalom",
     "But the LORD said to him, “Peace be to you. Do not fear; you shall not die.”",
     "Judges 6:23 (ESV)",
     [("the terebinth at Ophrah", "Judges 6:11", True), ("the winepress", "6:11", True),
      ("fire springing up from the rock", "6:21", True)]),
    ("tsevaot", "YHWH Tsevaot", scene_tsevaot, "YHWH Tsevaot",
     "O LORD of hosts, if you will indeed look on the affliction of your servant and remember me …",
     "1 Samuel 1:11 (ESV)",
     [("Eli on the seat beside the doorpost of the temple", "1 Samuel 1:9", True),
      ("Hannah praying; only her lips moved", "1:12-13", True),
      ("Hannah kneeling", "", False)]),
    ("immanuel", "Immanuel", scene_immanuel, "Immanuel",
     "they shall call his name Immanuel” (which means, God with us).", "Matthew 1:23 (ESV)",
     [("the star came to rest over the place where the child was", "Matthew 2:9", True),
      ("the house", "2:11", True)]),
    ("gibbor", "El Gibbor", scene_gibbor, "El Gibbor",
     "his name shall be called Wonderful Counselor, Mighty God, Everlasting Father, Prince of Peace.",
     "Isaiah 9:6 (ESV)",
     [("the throne of David", "Isaiah 9:7", True), ("the crown on it", "", False)]),
    ("tsidkenu", "YHWH Tsidkenu", scene_tsidkenu, "YHWH Tsidkenu",
     "And this is the name by which he will be called: ‘The LORD is our righteousness.’",
     "Jeremiah 23:6 (ESV)",
     [("a righteous Branch raised up for David", "Jeremiah 23:5", True),
      ("drawn as Isaiah's shoot from the stump of Jesse, bearing fruit", "Isaiah 11:1", True)]),
    ("yeshua", "Yeshua", scene_yeshua, "Yeshua, Jesus",
     "you shall call his name Jesus, for he will save his people from their sins.",
     "Matthew 1:21 (ESV)",
     [("three crosses: two robbers were crucified with him", "Matthew 27:38", True),
      ("the stone rolled back", "28:2", True), ("“He is not here, for he has risen”", "28:6", True),
      ("toward the dawn of the first day", "28:1", True)]),
]


def key_lines(items, width=104):
    stated = [f"{e} ({r})" if r else e for e, r, s in items if s]
    inferred = [f"{e} ({r})" if r else e for e, r, s in items if not s]
    rows = [(r, False) for r in wrap("In the scene: " + "; ".join(stated) + ".", width)]
    if inferred:
        rows += [(r, True) for r in wrap("Not stated, drawn for the scene: " + "; ".join(inferred) + ".", width)]
    return rows


def plate(slug, card, scene, translit, quote, ref, key):
    he, paleo, meaning = card["hebrew"], " ".join(w["paleo"] for w in card["words"]), card["meaning"]
    quote_rows = wrap(quote, 40)
    rows = key_lines(key)
    h = max(SY + SH, 254 + 18 * len(quote_rows)) + 22 + 17 * len(rows) + 30
    desc = (f"{translit}, {he}: {meaning}. {quote} ({ref}). "
            + " ".join(r for r, _ in rows))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" font-family="Georgia, \'Times New Roman\', serif" '
           f'role="img" aria-labelledby="t d">',
           f'<title id="t">{esc(translit)}: {esc(meaning)}</title>',
           f'<desc id="d">{esc(desc)}</desc>',
           f'<rect width="{W}" height="{h}" fill="{PAPER}"/>',
           f'<rect x="8" y="8" width="{W - 16}" height="{h - 16}" fill="none" stroke="{INK}" stroke-width="2.5"/>',
           f'<rect x="14" y="14" width="{W - 28}" height="{h - 28}" fill="none" stroke="{INK}" stroke-width="0.8"/>',
           f'<defs><clipPath id="frame-{slug}"><rect width="{SW}" height="{SH}" rx="6"/></clipPath></defs>',
           f'<g transform="translate({SX} {SY})"><g clip-path="url(#frame-{slug})">']
    out += scene_yhwh(paleo) if slug == "yhwh" else scene()
    out += ['</g>', f'<rect width="{SW}" height="{SH}" rx="6" fill="none" stroke="{INK}" stroke-width="1.6"/></g>']

    size = 78
    d, w = place(he, 0, 0, size, fill=INK)
    if w > 300:
        size = size * 300 / w
    path, _ = place(he, RX, 112, size, fill=INK)
    ppath, _ = place(paleo, RX, 158, 30, font=PALEO, weight=400, fill=GOLD_EDGE)
    out += [path, ppath,
            text(RX, 196, translit, 22, "middle", "bold", italic=True),
            text(RX, 219, meaning, 15, "middle", fill=MUTED, italic=True),
            f'<path d="M{RX - 120} 234 H{RX + 120}" stroke="{INK}" stroke-width="0.8"/>',
            f'<circle cx="{RX}" cy="234" r="2.6" fill="{INK}"/>']
    y = 256
    for row in quote_rows:
        out.append(text(RX, y, row, 14.5, "middle"))
        y += 18
    out.append(text(RX, y, ref, 12.5, "middle", fill=MUTED, italic=True))

    y = max(SY + SH, y) + 26
    for row, inferred in rows:
        out.append(text(30, y, row, 12.5, fill=MUTED if not inferred else BLUE, italic=inferred))
        y += 17
    out.append(text(W - 24, h - 22, "The Names of God · the-way.lewy.au", 11, "end", fill=MUTED, italic=True))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    cards = {c["name"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["decks"]["names-of-god"]["cards"]}
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, name, scene, translit, quote, ref, key in PLATES:
        (OUT / f"{slug}.svg").write_text(plate(slug, cards[name], scene, translit, quote, ref, key),
                                         encoding="utf-8")
        print(f"wrote {slug}.svg")


if __name__ == "__main__":
    main()
