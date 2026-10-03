"""Shared drawing hand for the Larkin-style charts: parchment, ink, ruled border, ribbons, cards.

Used by utils/build_tribulation_graphics.py and utils/build_last_things_graphics.py, so every chart
in last-things/ reads as one set. The confidence code lives here too: card(..., dashed=True) is an
event placed by inference, a solid card is one the text dates.
"""

import math

SERIF = "Georgia, 'Times New Roman', serif"
INK = "#3b2f1e"
MUTED = "#6b5a3e"
PAPER = "#faf6ec"
CARD = "#fffdf7"
RED = "#8b1e1e"
RED_TINT = "#f1dcd4"
GOLD = "#e8c46a"
GOLD_EDGE = "#a67c3d"
GOLD_TINT = "#f6ecd0"
BLUE = "#2f4f7f"
BLUE_TINT = "#e3e9f2"
EARTH_TINT = "#efe4d0"
CLOUD = "#ffffff"

W = 720
HALO = f'stroke="{PAPER}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=15, anchor="start", weight=None, fill=INK, italic=False, spacing=None,
         extra=""):
    attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{size}"', f'fill="{fill}"']
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if italic:
        attrs.append('font-style="italic"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if extra:
        attrs.append(extra)
    return f'<text {" ".join(attrs)}>{esc(s)}</text>'


def svg_open(h, title, desc):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" font-family="{SERIF}" '
        f'role="img" aria-labelledby="t d">',
        f'<title id="t">{esc(title)}</title>',
        f'<desc id="d">{esc(desc)}</desc>',
        f'<rect width="{W}" height="{h}" fill="{PAPER}"/>',
        # Larkin's charts sit inside a ruled double border.
        f'<rect x="8" y="8" width="{W - 16}" height="{h - 16}" fill="none" stroke="{INK}" stroke-width="2.5"/>',
        f'<rect x="14" y="14" width="{W - 28}" height="{h - 28}" fill="none" stroke="{INK}" stroke-width="0.8"/>',
    ]


def heading(title, subtitle, y=50):
    return [
        text(W / 2, y, title.upper(), 26, "middle", "bold", spacing="2"),
        text(W / 2, y + 28, subtitle, 15, "middle", fill=MUTED, italic=True),
        f'<path d="M{W / 2 - 150} {y + 42} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>',
        f'<circle cx="{W / 2}" cy="{y + 42}" r="3" fill="{INK}"/>',
    ]


def banner(cx, y, w, label, fill=INK, ink=PAPER, size=14):
    """A ribbon with swallow-tailed ends, Larkin's label for an age or a realm."""
    h, n = 26, 10
    x0, x1 = cx - w / 2, cx + w / 2
    d = (f"M{x0 - n} {y} H{x1 + n} L{x1} {y + h / 2} L{x1 + n} {y + h} H{x0 - n} "
         f"L{x0} {y + h / 2} Z")
    return [f'<path d="{d}" fill="{fill}"/>',
            text(cx, y + h / 2 + size * 0.36, label, size, "middle", "bold", fill=ink, spacing="1.5")]


def cloud(cx, cy, w, fill=CLOUD, stroke=GOLD_EDGE):
    """A row of overlapping puffs; the flat base sits on cy."""
    n = max(3, int(w // 34))
    r = w / (n * 1.55)
    parts = []
    for i in range(n):
        x = cx - w / 2 + r + i * (w - 2 * r) / (n - 1)
        rr = r * (1.25 if i % 2 else 1.0)
        parts.append(f'<circle cx="{x:.1f}" cy="{cy - rr:.1f}" r="{rr:.1f}"/>')
    return [f'<g fill="{fill}" stroke="{stroke}" stroke-width="1.2">{"".join(parts)}</g>',
            f'<rect x="{cx - w / 2 + r * 0.6:.1f}" y="{cy - r * 0.9:.1f}" width="{w - r * 1.2:.1f}" '
            f'height="{r * 0.9:.1f}" fill="{fill}"/>',
            f'<path d="M{cx - w / 2 + r * 0.3:.1f} {cy} H{cx + w / 2 - r * 0.3:.1f}" stroke="{stroke}" stroke-width="1.2"/>']


def arrow_head(x, y, angle_deg, size=9, fill=INK):
    a = math.radians(angle_deg)
    p1 = (x - size * math.cos(a - 0.45), y - size * math.sin(a - 0.45))
    p2 = (x - size * math.cos(a + 0.45), y - size * math.sin(a + 0.45))
    return (f'<path d="M{x:.1f} {y:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" '
            f'fill="{fill}"/>')


LINE = 17


def card(x, y, w, lines, ref, dashed=False, stroke=INK, fill=CARD, size=14):
    """An event: first line bold, then the rest, then the reference in italic. Returns (svg, height)."""
    h = 10 + LINE * len(lines) + (LINE if ref else 0)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="5" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="1.4"{dash}/>']
    ty = y + 4 + LINE * 0.85
    for i, ln in enumerate(lines):
        out.append(text(x + 8, ty, ln, size, weight="bold" if i == 0 else None))
        ty += LINE
    if ref:
        out.append(text(x + 8, ty, ref, size - 1.5, fill=MUTED, italic=True))
    return out, h


def legend_row(x, y, span=True):
    out = []
    c, _ = card(x, y, 150, ["The text dates it"], "", size=13)
    out += c
    c, _ = card(x + 175, y, 210, ["Placed by its order"], "", dashed=True, size=13)
    out += c
    if not span:
        return out
    out.append(f'<path d="M{x + 412} {y + 2} V{y + 26}" stroke="{RED}" stroke-width="3"/>')
    out.append(f'<path d="M{x + 406} {y + 2} H{x + 418} M{x + 406} {y + 26} H{x + 418}" stroke="{RED}" stroke-width="1.5"/>')
    out.append(text(x + 426, y + 19, "A span the text counts", 13))
    return out


def credit(h):
    return text(W - 24, h - 22, "After the manner of Clarence Larkin · the-way.lewy.au", 11,
                "end", fill=MUTED, italic=True)


