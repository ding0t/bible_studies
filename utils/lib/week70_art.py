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


def wings(x, y, s=1.0, face=1, spread=1.0, fill=WING, edge=WING_EDGE, covert="#fffdf6", eyes=False):
    """A pair of feathered wings raised behind a figure whose shoulders are at (x, y): a back row of
    long flight feathers fanned from the shoulder and a shorter row of coverts over them."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face:.3f} {s:.3f})">']
    for m in (1, -1):
        for row, (length, width, fillc) in enumerate(((62, 8.0, fill), (40, 7.0, covert))):
            for k in range(7):
                ang = -80 + k * 10 * spread
                ln = length - k * (3.6 if row == 0 else 2.4)
                a = math.radians(ang)
                cx, cy = m * (8 + math.cos(a) * ln / 2), math.sin(a) * ln / 2
                rot = ang if m == 1 else 180 - ang
                out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{ln / 2:.1f}" ry="{width:.1f}" transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})" '
                           f'fill="{fillc}" stroke="{edge}" stroke-width="0.9"/>')
                if eyes:
                    out.append(f'<circle cx="{cx + 0.2 * ln * math.cos(a) * m:.1f}" cy="{cy + 0.2 * ln * math.sin(a):.1f}" r="1.7" fill="#bfe6f2" stroke="{GOLD_DK}" stroke-width="0.4"/>'
                               f'<circle cx="{cx + 0.2 * ln * math.cos(a) * m:.1f}" cy="{cy + 0.2 * ln * math.sin(a):.1f}" r="0.7" fill="#2a2118"/>')
    out.append("</g>")
    return "".join(out)


def angel(x, y, s=1.0, face=1, pose="stand", holds=None, spread=1.0):
    """An angel: the comic's white-robed figure with wings. (x, y) is the feet."""
    body, _ = comic.figure("robed", x, y, s, face, pose=pose, holds=holds)
    return wings(x, y - 62 * s, s, face, spread) + body


def _lamb(x, y, s=1.0, look_up=0):
    """The Lamb standing, as though it had been slain (Revelation 5:6), facing right: a tufted woolly body, slender legs and dark hooves, a lamb's
    long face with ears out to the sides, seven small gold horns and seven gold eyes, and the wound at the throat. look_up tilts the head."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">']
    # Legs and hooves (far pair first, in shade).
    for lx, shade in ((-22, "#d9d2c0"), (14, "#d9d2c0"), (-12, "#f4eee0"), (24, "#f4eee0")):
        out.append(f'<path d="M{lx} -16 V-3" stroke="{INK}" stroke-width="6.2" stroke-linecap="round"/><path d="M{lx} -16 V-3" stroke="{shade}" stroke-width="4" stroke-linecap="round"/>'
                   f'<path d="M{lx - 3} -2 q3 4 6 0 v3 h-6 Z" fill="#2a2118"/>')
    # The fleece: a ring of curls round an ellipse, then an inner fill so the edge reads as tufts.
    for k in range(26):
        a = math.pi * 2 * k / 26
        cx, cy = 2 + 31 * math.cos(a), -34 + 19 * math.sin(a)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{8.4 + (k % 3) * 0.8:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="1.1"/>')
    out.append(f'<ellipse cx="2" cy="-34" rx="30" ry="18" fill="{WHITE}"/>')
    for cx, cy in ((-14, -40), (0, -44), (14, -40), (-8, -30), (8, -30), (-20, -30), (20, -32)):
        out.append(f'<path d="M{cx - 4} {cy} q4 -5 8 0" fill="none" stroke="#cfc6b0" stroke-width="1.1"/>')
    out.append(f'<path d="M-32 -34 q-8 -2 -10 6 q5 -1 10 2" fill="{WHITE}" stroke="{INK}" stroke-width="1.1"/>')
    # The head, tilted up toward the throne.
    out.append(f'<g transform="translate(30 -44) rotate({-look_up})">')
    out.append(f'<path d="M-6 8 C-8 -2 -2 -10 8 -10 C16 -10 22 -4 24 4 C25 10 21 14 15 14 C8 15 0 14 -6 8 Z" fill="{WHITE}" stroke="{INK}" stroke-width="1.3"/>')
    out.append(f'<ellipse cx="3" cy="-9" rx="8" ry="3.4" transform="rotate(-26 3 -9)" fill="#efe6d4" stroke="{INK}" stroke-width="1"/>'
               f'<ellipse cx="14" cy="-8" rx="8" ry="3.4" transform="rotate(28 14 -8)" fill="#efe6d4" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<ellipse cx="20" cy="9" rx="6" ry="4.6" fill="#f1dcd0" stroke="{INK}" stroke-width="0.9"/><ellipse cx="23" cy="8" rx="2" ry="1.4" fill="{INK}"/>'
               f'<path d="M14 12 q5 2 9 0" stroke="{INK}" stroke-width="0.9" fill="none"/>'
               f'<circle cx="10" cy="1" r="2.1" fill="{INK}"/><circle cx="10.7" cy="0.4" r="0.7" fill="#fff"/>')
    # Seven horns, small and gold, curled like a crown above the head (5:6).
    for i in range(7):
        hx = -1 + i * 3.6
        out.append(f'<path d="M{hx:.1f} -10 q{(i - 3) * 1.4:.1f} -7 {(i - 3) * 2.4:.1f} -9" stroke="{GOLD_DK}" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
                   f'<path d="M{hx:.1f} -10 q{(i - 3) * 1.4:.1f} -7 {(i - 3) * 2.4:.1f} -9" stroke="{GOLD}" stroke-width="1" stroke-linecap="round" fill="none"/>')
    # Seven eyes, gold, in an arc over them (5:6).
    for i in range(7):
        ex = -5 + i * 4.2
        ey = -24 - 3.6 * math.sin(math.pi * i / 6)
        out.append(f'<path d="M{ex - 1.8:.1f} {ey:.1f} q1.8 -2.2 3.6 0 q-1.8 2.2 -3.6 0 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.4"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="0.7" fill="{INK}"/>')
    out.append("</g>")
    # As though slain: the wound at the neck, the blood running down the fleece.
    out.append(f'<path d="M26 -34 q3 4 2 10" stroke="{RED}" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
               f'<path d="M27 -30 q-2 8 0 13 M30 -28 q0 6 1 10" stroke="{RED}" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.85"/>')
    out.append("</g>")
    return "".join(out)


def _scroll(x, y, w, h, rot=0):
    """The scroll written within and on the back, sealed with seven seals (Revelation 5:1): two gilt rollers, the sheet ruled with writing on its
    face, its curled edge showing writing on the back, and seven red wax seals hanging from cords along the foot."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot})">']
    out.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#f1e4bd" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    # Writing within: ruled lines of small marks.
    rows = max(3, int((h - 10) / 4.4))
    for r in range(rows):
        yy = -h / 2 + 6 + r * 4.4
        k = 0
        xx = -w / 2 + 4
        while xx < w / 2 - 5:
            seg = 3 + (k * 7 + r * 5) % 9
            out.append(f'<path d="M{xx:.1f} {yy:.1f} h{min(seg, w / 2 - 4 - xx):.1f}" stroke="#5a4632" stroke-width="1.1" stroke-linecap="round" opacity="0.85"/>')
            xx += seg + 2.4
            k += 1
    # The curled right edge: the back of the sheet, also written on.
    out.append(f'<path d="M{w / 2 - 7:.1f} {-h / 2:.1f} q9 {h * 0.25:.1f} 0 {h * 0.5:.1f} q-9 {h * 0.25:.1f} 0 {h * 0.5:.1f} V{h / 2:.1f} H{w / 2 - 7:.1f} Z" fill="#e6d4a4" stroke="{GOLD_DK}" stroke-width="1"/>')
    for r in range(rows - 1):
        out.append(f'<path d="M{w / 2 - 5:.1f} {-h / 2 + 7 + r * 4.4:.1f} h5" stroke="#5a4632" stroke-width="1" opacity="0.7"/>')
    # Top and bottom rollers with gilt knobs.
    for ry in (-h / 2, h / 2):
        out.append(f'<rect x="{-w / 2 - 3:.1f}" y="{ry - 2.4:.1f}" width="{w + 6:.1f}" height="4.8" rx="2.4" fill="#8a6a3a" stroke="#4a3418" stroke-width="0.9"/>'
                   f'<circle cx="{-w / 2 - 3:.1f}" cy="{ry:.1f}" r="3.4" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.9"/><circle cx="{w / 2 + 3:.1f}" cy="{ry:.1f}" r="3.4" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.9"/>')
    # Seven seals on cords hanging from the lower roller.
    for i in range(7):
        sx = -w / 2 + 6 + i * (w - 12) / 6
        out.append(f'<path d="M{sx:.1f} {h / 2:.1f} V{h / 2 + 6:.1f}" stroke="#6a1818" stroke-width="1.1"/>'
                   f'<circle cx="{sx:.1f}" cy="{h / 2 + 9.6:.1f}" r="4.2" fill="#a3202a" stroke="#4a0c0c" stroke-width="0.9"/>'
                   f'<circle cx="{sx:.1f}" cy="{h / 2 + 9.6:.1f}" r="2.4" fill="none" stroke="#d2493d" stroke-width="0.7"/>'
                   f'<path d="M{sx - 1.2:.1f} {h / 2 + 8.4:.1f} l2.4 2.4 M{sx + 1.2:.1f} {h / 2 + 8.4:.1f} l-2.4 2.4" stroke="#4a0c0c" stroke-width="0.6"/>')
    out.append("</g>")
    return "".join(out)


def _hand(x, y, s=1.0, rot=0, flip=False):
    """The right hand of him who sits on the throne, palm up, glowing (Revelation 5:1): drawn as light, since Scripture gives no form."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({-s if flip else s} {s})">',
           '<defs><radialGradient id="w70-hand-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fffdf0" stop-opacity="0.95"/><stop offset="1" stop-color="#fffdf0" stop-opacity="0"/></radialGradient></defs>',
           '<ellipse cx="0" cy="0" rx="34" ry="26" fill="url(#w70-hand-glow)"/>',
           '<path d="M-30 -8 C-20 -6 -12 -4 -6 0 L-4 10 C-14 10 -24 8 -32 4 Z" fill="#fffef6" stroke="#d9cfa8" stroke-width="0.8"/>',
           '<path d="M-8 -4 C0 -8 12 -8 18 -4 C20 0 18 6 12 8 L-4 10 Z" fill="#fffef6" stroke="#d9cfa8" stroke-width="0.9"/>']
    for fx, fy, fl in ((10, -8, 12), (14, -3, 13), (14, 2, 12), (11, 6, 9)):
        out.append(f'<path d="M{fx} {fy} q{fl} -1 {fl + 2} 1" stroke="#fffef6" stroke-width="4.2" stroke-linecap="round" fill="none"/>'
                   f'<path d="M{fx} {fy} q{fl} -1 {fl + 2} 1" stroke="#d9cfa8" stroke-width="0.6" stroke-linecap="round" fill="none" transform="translate(0 -2)"/>')
    out.append('<path d="M-4 8 q6 6 14 4" stroke="#fffef6" stroke-width="4" stroke-linecap="round" fill="none"/>')
    out.append("</g>")
    return "".join(out)


def _creature(kind, x, y, s=1.0):
    """One of the four living creatures round the throne, full of eyes, each with six wings (Revelation 4:6-8)."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">']
    for m in (1, -1):
        for k, (dx, dy) in enumerate(((10, -4), (12, 2), (9, 7))):
            out.append(f'<ellipse cx="{m * dx}" cy="{dy}" rx="9" ry="3" transform="rotate({m * (-25 + k * 25)} {m * dx} {dy})" fill="{WING}" stroke="{WING_EDGE}" stroke-width="0.8"/>')
    out.append(f'<circle r="8.4" fill="#f0e4c4" stroke="{GOLD_DK}" stroke-width="1"/>')
    if kind == "lion":
        out.append('<circle r="7" fill="#c98a3a" stroke="#6a4416" stroke-width="0.8"/><circle r="4.4" fill="#e3b56a"/>'
                   '<path d="M-2 0 h4 l-2 3 z" fill="#3a2412"/><circle cx="-2" cy="-1.4" r="0.8" fill="#3a2412"/><circle cx="2" cy="-1.4" r="0.8" fill="#3a2412"/>')
    elif kind == "ox":
        out.append('<ellipse rx="5" ry="5.4" fill="#8a5a32" stroke="#4a2c14" stroke-width="0.8"/><path d="M-5 -3 Q-9 -8 -5 -9 M5 -3 Q9 -8 5 -9" stroke="#f1e6c8" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
                   '<ellipse cy="3" rx="3" ry="2" fill="#d9a77a"/>')
    elif kind == "man":
        out.append('<circle r="5" fill="#b98a5e" stroke="#4a2c14" stroke-width="0.8"/><path d="M-4 1 Q0 8 4 1 Q0 5 -4 1 Z" fill="#3a2412"/>'
                   '<circle cx="-1.8" cy="-1" r="0.7" fill="#3a2412"/><circle cx="1.8" cy="-1" r="0.7" fill="#3a2412"/>')
    else:
        out.append('<ellipse rx="5" ry="5.4" fill="#6a4a2a" stroke="#3a2412" stroke-width="0.8"/><path d="M0 -1 L7 1 L0 3 Z" fill="#e0b24a" stroke="#9c7a2e" stroke-width="0.6"/>'
                   '<circle cx="-1" cy="-2" r="0.9" fill="#f6d36a"/>')
    for k in range(8):
        a = math.pi * 2 * k / 8
        out.append(f'<circle cx="{11.2 * math.cos(a):.1f}" cy="{11.2 * math.sin(a):.1f}" r="0.9" fill="{GOLD}"/>')
    out.append("</g>")
    return "".join(out)


def _elder(x, y, s, face=1, tone=0):
    """One of the twenty-four elders, in white, a golden crown on his head, on his own throne (Revelation 4:4)."""
    body, _ = comic.figure("robed", x, y, s, face, stance="sit", tone=tone)
    seat = f'<rect x="{x - 9 * s * 1.6:.1f}" y="{y - 2 * s:.1f}" width="{18 * s * 1.6:.1f}" height="{5 * s:.1f}" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.5"/>'
    crown = (f'<path d="M{x - 4 * s:.1f} {y - 66 * s:.1f} l{1 * s:.1f} {-6 * s:.1f} l{3 * s:.1f} {3 * s:.1f} l{3 * s:.1f} {-5 * s:.1f} l{3 * s:.1f} {5 * s:.1f} l{3 * s:.1f} {-3 * s:.1f} l{1 * s:.1f} {6 * s:.1f} Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.4"/>')
    return seat + body + crown


def _creature_big(kind, x, y, s=1.0, flip=1):
    """One of the four living creatures, large: six wings and eyes all over them and round about (Revelation 4:6-8), the face of a lion, an ox,
    a man or a flying eagle."""
    cols = {"lion": ("#c98a3a", "#e3b56a"), "ox": ("#8a5a32", "#d9a77a"), "man": ("#b98a5e", "#d8b88a"), "eagle": ("#6a4a2a", "#e0b24a")}
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * flip:.3f} {s:.3f})">']
    for ang, sp in ((-62, 0.8), (-8, 0.9), (46, 0.8)):
        out.append(f'<g transform="rotate({ang})">{wings(0, 0, 0.55, 1, sp, "#e8dcc0", GOLD_DK, "#f6ecd2", eyes=True)}</g>')
    out.append(f'<circle r="11" fill="#f0e4c4" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    body, face = cols[kind]
    if kind == "lion":
        out.append(f'<circle r="9" fill="{body}" stroke="#6a4416" stroke-width="1"/><circle r="5.6" fill="{face}"/><path d="M-2.4 0.4 h4.8 l-2.4 3.4 z" fill="#3a2412"/><circle cx="-2.4" cy="-1.6" r="0.9" fill="#3a2412"/><circle cx="2.4" cy="-1.6" r="0.9" fill="#3a2412"/>')
    elif kind == "ox":
        out.append(f'<ellipse rx="6.4" ry="6.8" fill="{body}" stroke="#4a2c14" stroke-width="1"/><path d="M-6 -3.6 Q-11 -9 -6 -10 M6 -3.6 Q11 -9 6 -10" stroke="#f1e6c8" stroke-width="2" fill="none" stroke-linecap="round"/><ellipse cy="3.6" rx="3.6" ry="2.4" fill="{face}"/>')
    elif kind == "man":
        out.append(f'<circle r="6.2" fill="{body}" stroke="#4a2c14" stroke-width="1"/><path d="M-5 1 Q0 10 5 1 Q0 6 -5 1 Z" fill="#3a2412"/><circle cx="-2.2" cy="-1.2" r="0.9" fill="#3a2412"/><circle cx="2.2" cy="-1.2" r="0.9" fill="#3a2412"/>')
    else:
        out.append(f'<ellipse rx="6.2" ry="6.6" fill="{body}" stroke="#3a2412" stroke-width="1"/><path d="M0 -1 L9 1.4 L0 3.8 Z" fill="{face}" stroke="{GOLD_DK}" stroke-width="0.8"/><circle cx="-1.4" cy="-2.4" r="1.1" fill="#f6d36a"/>')
    out.append("</g>")
    return "".join(out)


def _elder_back(x, y, s=1.0, tone=0, arms="up"):
    """An elder seen from behind, in white with a gold sash and a gold band round his head, hands raised in worship (Revelation 4:4, 10)."""
    skin = ("#b98a5e", "#8a5a3a", "#d8b08a", "#6a4a2e")[tone % 4]
    hair = ("#2a1d10", "#d8d4cc", "#3a2a1a", "#8a8478")[tone % 4]
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">']
    o.append('<path d="M-24 0 C-26 -26 -22 -48 -12 -60 L12 -60 C22 -48 26 -26 24 0 Z" fill="#f6f2e6" stroke="#bdb49c" stroke-width="1"/>')
    o.append('<path d="M-14 -58 C-8 -30 -10 -12 -14 0 M14 -58 C8 -30 10 -12 14 0 M0 -58 V0" stroke="#d6cfba" stroke-width="1.2" fill="none"/>')
    o.append('<path d="M-23 -38 H23 V-30 H-23 Z" fill="#e0b24a" stroke="#9c7a2e" stroke-width="1"/><path d="M-23 -34 H23" stroke="#c9962a" stroke-width="0.8"/>')
    if arms == "up":
        o.append('<path d="M-12 -56 C-24 -52 -32 -62 -30 -78" stroke="#f6f2e6" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M-12 -56 C-24 -52 -32 -62 -30 -78" stroke="#bdb49c" stroke-width="1" fill="none" transform="translate(0 0)"/>'
                 '<path d="M12 -56 C24 -52 32 -62 30 -78" stroke="#f6f2e6" stroke-width="9" fill="none" stroke-linecap="round"/>')
        o.append(f'<ellipse cx="-30" cy="-82" rx="5" ry="6" fill="{skin}"/><ellipse cx="30" cy="-82" rx="5" ry="6" fill="{skin}"/>')
    o.append(f'<circle cx="0" cy="-67" r="9" fill="{skin}"/><path d="M-9 -68 C-9 -80 9 -80 9 -68 C8 -72 -8 -72 -9 -68 Z" fill="{hair}"/>')
    o.append(f'<path d="M-9.4 -72 h18.8 v4.2 h-18.8 Z" fill="#e0b24a" stroke="#9c7a2e" stroke-width="0.8"/>')
    o.append("</g>")
    return "".join(o)


def _lamb_front(x, y, s=1.0):
    """The Lamb facing us, as though slain: fleece with the red marks of the wounds, a lamb's face, seven upright gold horns and seven eyes."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">']
    for lx in (-9, 9):
        o.append(f'<path d="M{lx} -30 V-4" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><path d="M{lx} -30 V-4" stroke="#f4eee0" stroke-width="4.8" stroke-linecap="round"/><path d="M{lx - 3.4} -3 q3.4 5 6.8 0 v3.6 h-6.8 Z" fill="#2a2118"/>')
    for k in range(20):
        a = math.pi * 2 * k / 20
        o.append(f'<circle cx="{26 * math.cos(a):.1f}" cy="{-44 + 20 * math.sin(a):.1f}" r="{8 + (k % 3) * 0.8:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<ellipse cx="0" cy="-44" rx="26" ry="20" fill="{WHITE}"/>')
    for cx, cy in ((-8, -38), (8, -34), (0, -28), (-14, -44)):
        o.append(f'<path d="M{cx - 4} {cy} q4 -5 8 0" fill="none" stroke="#d4cbb4" stroke-width="1.1"/>')
    # The marks of the slaying on the fleece (Revelation 5:6).
    o.append(f'<path d="M-16 -50 q4 -4 8 0 q2 5 -3 7 q-6 0 -5 -7 Z M10 -52 q5 -2 8 2 q-2 5 -7 4 Z" fill="{RED}" opacity="0.8"/><path d="M-2 -30 q2 6 0 12" stroke="{RED}" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.85"/>')
    # The head.
    o.append(f'<g transform="translate(0 -62)">')
    o.append(f'<ellipse cx="-13" cy="3" rx="9" ry="3.6" transform="rotate(-18 -13 3)" fill="#efe6d4" stroke="{INK}" stroke-width="1"/><ellipse cx="13" cy="3" rx="9" ry="3.6" transform="rotate(18 13 3)" fill="#efe6d4" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<path d="M-9 -4 C-9 -12 9 -12 9 -4 C10 8 6 16 0 17 C-6 16 -10 8 -9 -4 Z" fill="{WHITE}" stroke="{INK}" stroke-width="1.2"/>')
    o.append(f'<ellipse cx="0" cy="11" rx="4.2" ry="3.6" fill="#f1dcd0" stroke="{INK}" stroke-width="0.8"/><path d="M-1.6 10 h1 M0.6 10 h1" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<circle cx="-4.4" cy="0" r="1.6" fill="{INK}"/><circle cx="4.4" cy="0" r="1.6" fill="{INK}"/>')
    for i in range(7):
        a = math.radians(-150 + i * 20)
        hx, hy = 15 * math.cos(a) * 0.62, -5 + 12 * math.sin(a)
        o.append(f'<path d="M{hx:.1f} {hy:.1f} l{9 * math.cos(a) * 0.55:.1f} {11 * math.sin(a):.1f}" stroke="#2a2118" stroke-width="2.2" stroke-linecap="round"/>'
                 f'<path d="M{hx:.1f} {hy:.1f} l{9 * math.cos(a) * 0.55:.1f} {11 * math.sin(a):.1f}" stroke="{GOLD}" stroke-width="0.9" stroke-linecap="round"/>')
    for i in range(7):
        ex = -9 + i * 3
        o.append(f'<path d="M{ex - 1.2:.1f} -9 q1.2 -1.6 2.4 0 q-1.2 1.6 -2.4 0 Z" fill="#8fd0e8" stroke="{GOLD_DK}" stroke-width="0.4"/>')
    o.append("</g></g>")
    return "".join(o)


def lamb_scroll():
    """Revelation 4-5, from where the elders stand: the glowing throne with the one who sits on it as light, the scroll in His right hand, the
    rainbow and the rays, the four living creatures covered in eyes, the elders crowned and worshipping, the Lamb as though slain with seven
    horns and seven eyes standing before the throne on the sea of glass like crystal."""
    out = _sky("w70-lamb-sky", "#fff9e0", "#f2d48a")
    out.append('<defs><radialGradient id="w70-throne-glow" cx="0.5" cy="0.28" r="0.55"><stop offset="0" stop-color="#ffffff" stop-opacity="1"/><stop offset="0.5" stop-color="#fff6cf" stop-opacity="0.7"/><stop offset="1" stop-color="#fff6cf" stop-opacity="0"/></radialGradient>'
               '<linearGradient id="w70-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3c4"/><stop offset="1" stop-color="#e8c470"/></linearGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-throne-glow)"/>')
    for k in range(26):
        a = math.pi * (0.05 + 0.9 * k / 25)
        out.append(f'<path d="M120 52 L{120 + 260 * math.cos(a):.1f} {52 - 260 * math.sin(a):.1f}" stroke="#fff" stroke-width="{2.4 + (k % 3)}" opacity="0.3"/>')
    # The rainbow like an emerald round the throne (4:3).
    for r, c in ((56, "#7fb06a"), (50, "#c6dd9a"), (44, "#f2e39a"), (38, "#f0b88a")):
        out.append(f'<path d="M{120 - r} 78 A{r} {r * 0.8:.0f} 0 0 1 {120 + r} 78" fill="none" stroke="{c}" stroke-width="3.6" opacity="0.65"/>')
    # The floor: golden steps and the sea of glass, with reflections.
    out.append('<path d="M0 102 H240 V180 H0 Z" fill="url(#w70-floor)"/>')
    for i, y in enumerate((106, 116, 128, 142, 160)):
        out.append(f'<path d="M{70 - i * 14} {y} H{170 + i * 14}" stroke="#fffbe6" stroke-width="{1.6 + i * 0.5}" opacity="0.8"/>')
    for k in range(9):
        out.append(f'<path d="M{104 + k * 4} 104 L{40 + k * 20} 180" stroke="#fffbe6" stroke-width="0.9" opacity="0.5"/>')
    # The throne: the One who sits on it drawn only as light, a seat of white and gold.
    out.append('<rect x="84" y="78" width="72" height="8" fill="#fbf4d8" stroke="#d8c78a" stroke-width="1"/><rect x="94" y="70" width="52" height="9" fill="#fffbe6" stroke="#d8c78a" stroke-width="1"/>')
    out.append('<path d="M92 70 V24 Q120 6 148 24 V70 Z" fill="#fffdf0" stroke="#e6d9a8" stroke-width="1.2" opacity="0.95"/>')
    out.append('<ellipse cx="120" cy="44" rx="30" ry="40" fill="#ffffff" opacity="0.85"/>')
    out.append('<path d="M88 70 C86 46 98 34 112 32 L128 32 C142 34 154 46 152 70 Z" fill="#ffffff" stroke="#efe6c4" stroke-width="1" opacity="0.96"/>')
    out.append('<path d="M104 38 C102 52 104 62 100 70 M136 38 C138 52 136 62 140 70 M120 36 V70" stroke="#e8dfc2" stroke-width="1.1" fill="none"/>')
    out.append('<circle cx="120" cy="26" r="9" fill="#ffffff" stroke="#efe6c4" stroke-width="1"/><path d="M112 30 C112 40 128 40 128 30 C126 34 114 34 112 30 Z" fill="#f4efdc"/>')
    # His right hand held out with the scroll (5:1): the arm of light and the scroll hanging from it, seals showing.
    out.append('<path d="M104 46 C100 52 98 60 96 68" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/><path d="M104 46 C92 50 84 58 76 66" stroke="#efe6c4" stroke-width="0.8" fill="none"/>')
    out.append(_scroll(68, 78, 46, 20, -8))
    out.append(_hand(94, 70, 0.3, 10, flip=True))
    # The four living creatures, huge, winged and full of eyes.
    out.append(_creature_big("lion", 30, 44, 0.72))
    out.append(_creature_big("man", 66, 18, 0.5))
    out.append(_creature_big("eagle", 172, 26, 0.6, -1))
    out.append(_creature_big("ox", 206, 58, 0.8, -1))
    # The elders beyond: rows of small ones in white and gold on either side of the pavement.
    for k in range(6):
        out.append(_elder_back(70 - k * 7, 112 + (k % 2) * 3, 0.22, tone=k))
        out.append(_elder_back(170 + k * 7, 112 + (k % 2) * 3, 0.22, tone=k + 1))
    for k in range(6):
        out.append(_elder_back(66 - k * 9, 126 + (k % 2) * 3, 0.3, tone=k + 2))
        out.append(_elder_back(174 + k * 9, 126 + (k % 2) * 3, 0.3, tone=k + 3))
    # The Lamb, facing us, and His reflection in the glass.
    out.append('<g transform="translate(0 322) scale(1 -1)" opacity="0.14">' + _lamb_front(120, 161, 0.86) + "</g>")
    out.append(_lamb_front(120, 160, 0.86))
    # Seven lamps of fire burning before the throne (4:5).
    for i in range(7):
        lx = 92 + i * 9.4
        out.append(f'<path d="M{lx} 104 v-6" stroke="{GOLD_DK}" stroke-width="1.1"/><path d="M{lx - 2} 98 q2 -8 4 0 q-2 3 -4 0 Z" fill="#f08a3a" stroke="#c25a1a" stroke-width="0.5"/><path d="M{lx - 0.9} 98 q0.9 -4.4 1.8 0 Z" fill="#f8d56a"/>')
    # The foreground elders, seen from behind, hands lifted in worship.
    out.append(_elder_back(18, 184, 0.82, tone=0))
    out.append(_elder_back(52, 186, 0.74, tone=1))
    out.append(_elder_back(188, 186, 0.74, tone=2))
    out.append(_elder_back(222, 184, 0.82, tone=3))
    return "".join(out)


def horsemen_four():
    """Revelation 6:1-8: the first four seals opened, the riders on white, red, black and pale horses, with Hades following."""
    import build_tribulation_graphics as plate

    out = _sky("w70-horse-sky", "#2c2338", "#d99b5a")
    out.append('<path d="M0 142 Q60 128 120 138 T240 130 V180 H0 Z" fill="#3a2a22"/>')
    out.append('<path d="M0 156 Q80 144 160 152 T240 150 V180 H0 Z" fill="#241913"/>')
    # The scroll with its seals, four broken (6:1, 3, 5, 7), in the corner of the sky.
    out.append(f'<rect x="8" y="8" width="64" height="12" rx="3" fill="#efe2bf" stroke="{GOLD_DK}" stroke-width="1"/>'
               f'<ellipse cx="8" cy="14" rx="3" ry="6.5" fill="#e2d0a2" stroke="{GOLD_DK}" stroke-width="1"/><ellipse cx="72" cy="14" rx="3" ry="6.5" fill="#e2d0a2" stroke="{GOLD_DK}" stroke-width="1"/>')
    for i in range(7):
        sx = 14 + i * 8.6
        if i < 4:
            out.append(f'<circle cx="{sx:.1f}" cy="14" r="3.2" fill="#c45a50" stroke="#5b1010" stroke-width="0.5"/><path d="M{sx - 2:.1f} 12 l4 4 M{sx + 2:.1f} 12 l-4 4" stroke="#faf0d8" stroke-width="0.9"/>')
        else:
            out.append(f'<circle cx="{sx:.1f}" cy="14" r="3.2" fill="{BLOOD}" stroke="#5b1010" stroke-width="0.5"/>')
    # Hades follows after Death (6:8): a dark, dashed shadow of a horse behind the last rider.
    out.append(plate.horse(176, 60, "#0d0d0d", "#0d0d0d", 0.3, ghost=True))
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
            out.append(f'<path d="M{hx:.1f} {hy:.1f} L{hx + 20:.1f} {hy - 18:.1f}" stroke="#e0e0e0" stroke-width="2.6" stroke-linecap="round"/>'
                       f'<path d="M{hx - 3:.1f} {hy + 2:.1f} l6 -4" stroke="{GOLD}" stroke-width="2"/>')
        if n == 1:   # the third: a pair of scales in his hand (6:5)
            bx, by = hx + 4, hy - 9
            out.append(f'<path d="M{bx:.1f} {by:.1f} V{hy:.1f}" stroke="#d8cfb8" stroke-width="1"/><path d="M{bx - 12:.1f} {by:.1f} H{bx + 12:.1f}" stroke="#d8cfb8" stroke-width="1.6"/>'
                       f'<path d="M{bx - 12:.1f} {by:.1f} l-3 8 h6 z M{bx + 12:.1f} {by:.1f} l-3 8 h6 z" fill="#d8cfb8" opacity="0.9"/>')
    return "".join(out)


def seal6():
    """Revelation 6:12-17: a great earthquake, the sun black as sackcloth, the moon like blood, the stars falling like
    figs shaken from a tree, the sky rolled up like a scroll, every mountain and island moved, and all ranks of men hiding."""
    out = _sky("w70-seal6-sky", "#140f26", "#6a2a30")
    for k in range(14):
        a = 2 * math.pi * k / 14
        out.append(f'<path d="M96 40 L{96 + 28 * math.cos(a):.1f} {40 + 28 * math.sin(a):.1f}" stroke="#3a3040" stroke-width="1.6" opacity="0.8"/>')
    out.append('<circle cx="96" cy="40" r="17" fill="#0c0a0c" stroke="#4a3d52" stroke-width="1.4"/>')
    out.append(f'<circle cx="176" cy="34" r="13" fill="{BLOOD}" stroke="#d2493d" stroke-width="1.2"/>')
    for x, y in ((62, 18), (130, 18), (150, 56), (208, 62), (70, 66), (196, 12)):
        out.append(f'<path d="M{x + 12} {y - 12} L{x} {y}" stroke="#f6e7a8" stroke-width="1.2" opacity="0.7"/>' + _star(x, y, 4.2))
    # The sky rolled up like a scroll, curling away at both sides (6:14).
    out.append('<path d="M0 0 H44 C44 30 40 60 26 84 C14 100 4 96 0 100 Z" fill="#2a2038" stroke="#b2a88f" stroke-width="0.9"/>'
               '<path d="M6 12 C22 12 30 28 24 44 C20 56 8 56 8 44 C8 36 16 32 18 38" fill="none" stroke="#b2a88f" stroke-width="1.4"/>'
               '<path d="M240 0 H208 C208 24 214 44 228 62 C234 70 240 70 240 72 Z" fill="#2a2038" stroke="#b2a88f" stroke-width="0.9"/>'
               '<path d="M236 14 C224 14 218 26 222 36 C225 44 234 42 233 35" fill="none" stroke="#b2a88f" stroke-width="1.2"/>')
    # Mountains shaken and split, rocks falling; an island sliding under the sea.
    out.append('<path d="M0 132 L30 98 L54 118 L92 76 L124 116 L160 86 L190 112 L214 92 L240 118 V180 H0 Z" fill="#3b2c34" stroke="#5a4650" stroke-width="1"/>')
    out.append('<path d="M92 76 L96 98 L88 118 M160 86 L156 106 L164 126" stroke="#9a5a3a" stroke-width="1.6" fill="none"/>')
    for x, y, r in ((74, 96, 3.4), (110, 90, 2.6), (178, 98, 3), (136, 100, 2.4), (44, 104, 2.4)):
        out.append(f'<rect x="{x}" y="{y}" width="{r * 2}" height="{r * 1.6}" fill="#3a2a2a" transform="rotate({x * 3 % 50} {x} {y})"/>')
    out.append('<path d="M0 156 Q40 148 80 156 T160 154 T240 156 V180 H0 Z" fill="#17101a"/>')
    out.append('<path d="M172 150 q10 -12 24 -2 q8 -6 14 2 Z" fill="#2a1d20"/><path d="M168 154 q10 4 22 0 t22 0" stroke="#6a4a5a" stroke-width="1.2" fill="none"/>')
    # A fig tree shaken by a gale, its unripe figs dropping (6:13).
    out.append('<path d="M20 160 C16 146 24 136 18 124 M18 138 L8 130 M20 134 L32 124" stroke="#4a3a2a" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
               '<ellipse cx="14" cy="120" rx="14" ry="9" fill="#3d5a3a" transform="rotate(-18 14 120)"/><ellipse cx="32" cy="124" rx="9" ry="6" fill="#4a6a44" transform="rotate(-24 32 124)"/>')
    for x, y in ((8, 138), (26, 146), (36, 156), (14, 156)):
        out.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#6b4a6b" stroke="#2a1830" stroke-width="0.5"/>')
    # The kings, the great ones, the generals, the rich, the strong, the slave and the free, hiding in a cave (6:15).
    out.append('<path d="M78 170 C80 124 160 122 164 170 Z" fill="#0a0608" stroke="#6a5560" stroke-width="2"/>')
    for who, x, tone, st in (("authority", 94, 0, 1), ("soldier", 112, 0, 1), ("man", 132, 2, -1), ("woman", 148, 1, -1), ("beggar", 104, 0, 1), ("man", 124, 1, -1)):
        body, _ = comic.figure(who, x, 170 if who != "beggar" else 172, 0.5, st, pose="fold", stance="kneel", tone=tone)
        out.append(body)
    out.append(f'<path d="M88 131 l1.5 -5 l1.8 3 l1.8 -4 l1.8 4 l1.8 -3 l1.5 5 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.5"/>')
    return "".join(out)


def sealed144():
    """Revelation 7:1-8: four angels at the four corners of the earth hold back the winds from earth, sea and tree; another
    rises from the east with the seal of the living God; twelve tribes, each of twelve thousand, sealed on the forehead."""
    out = _sky("w70-sealed-sky", "#f7d9a0", "#8fb4cf")
    out.append('<circle cx="206" cy="84" r="24" fill="#fff1bf" opacity="0.9"/>')
    for k in range(10):
        a = math.radians(-110 + 20 * k)
        out.append(f'<path d="M206 84 L{206 + 70 * math.cos(a):.1f} {84 + 70 * math.sin(a):.1f}" stroke="#fff1bf" stroke-width="2" opacity="0.4"/>')
    # The earth: land, the sea at its edge, and a tree that no wind may touch (7:1).
    out.append('<path d="M0 100 H240 V180 H0 Z" fill="#c9b985"/><path d="M18 100 L222 100 L240 150 H0 Z" fill="#b9a874"/>')
    out.append('<path d="M0 98 Q60 92 120 98 T240 96 V104 H0 Z" fill="#6f9cc0"/>')
    out.append('<path d="M120 124 v-22" stroke="#6a4a2a" stroke-width="3"/><ellipse cx="120" cy="96" rx="13" ry="10" fill="#5f8a4a" stroke="#34522a" stroke-width="1"/>')
    # The four winds, held at the four corners: streamers straining against the angels' hands.
    for ax, ay, face in ((24, 118, 1), (216, 118, -1), (10, 172, 1), (230, 172, -1)):
        out.append(angel(ax + 14 * face, ay, 0.4, face, pose="open", spread=0.8))
        for r in (-6, 2, 10):
            out.append(f'<path d="M{ax + 20 * face:.0f} {ay - 34 + r:.0f} q{face * 12} -8 {face * 26} 0 t{face * 18} 0" stroke="#fff" stroke-width="1.5" fill="none" opacity="0.85" stroke-linecap="round"/>')
    # The angel from the rising of the sun with the seal of the living God (7:2), the first of the sealed beside him.
    out.append(angel(176, 166, 0.6, -1, pose="offer", spread=0.95))
    out.append(f'<circle cx="153" cy="129" r="7" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.5"/><circle cx="153" cy="129" r="3.2" fill="none" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    body, _ = comic.figure("man", 118, 166, 0.55, 1, pose="fold", stance="kneel", tone=1)
    out.append(body)
    out.append(f'<circle cx="123" cy="132" r="2.2" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.4"/>')
    # Twelve tribes, a gold seal on every forehead: twelve thousand from each.
    for i in range(12):
        tx = 12 + i * 19.6
        for j, (dx, dy) in enumerate(((0, 0), (-3.4, 2.4), (3.4, 2.4))):
            body, _ = comic.figure("man" if j else "woman", tx + dx, 178 + dy - 2, 0.12, 1, tone=i + j)
            out.append(body)
        out.append(f'<circle cx="{tx:.1f}" cy="167" r="1.1" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.3"/>')
    return "".join(out)


def trumpets():
    """Revelation 8:6-12: seven angels with seven trumpets; a great burning mountain thrown into the sea, a third of the sea
    blood, a third of the creatures dead, a third of the ships wrecked; a great star falling on the rivers."""
    import build_tribulation_graphics as plate

    out = _sky("w70-trumpet-sky", "#26151c", "#b5502d")
    out.append('<defs><radialGradient id="w70-blood-spread" cx="0.5" cy="0" r="0.75"><stop offset="0" stop-color="#7a1010"/>'
               '<stop offset="0.65" stop-color="#8b1b1b" stop-opacity="0.9"/><stop offset="1" stop-color="#8b1b1b" stop-opacity="0"/></radialGradient>'
               '<radialGradient id="w70-mtn-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb347" stop-opacity="0.9"/>'
               '<stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>'
               '<clipPath id="w70-sea"><rect x="0" y="108" width="240" height="72"/></clipPath></defs>')
    out.append('<path d="M0 108 H240 V180 H0 Z" fill="#35597a"/>')
    out.append('<ellipse cx="108" cy="112" rx="120" ry="76" fill="url(#w70-blood-spread)" clip-path="url(#w70-sea)"/>')
    for y in (118, 132, 146, 162):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#fff" stroke-width="1.2" fill="none" opacity="0.24"/>')
    out.append('<ellipse cx="106" cy="76" rx="56" ry="44" fill="url(#w70-mtn-glow)"/>')
    out.append('<g transform="rotate(22 106 76)"><path d="M72 108 L80 78 L68 66 L86 52 L92 36 L106 46 L120 30 L130 52 L148 62 L138 82 L146 108 Z" fill="#4a3226" stroke="#1c120d" stroke-width="1.6" stroke-linejoin="round"/>'
               '<path d="M86 62 L100 76 L92 96 M118 50 L114 72 L128 90" stroke="#e0662a" stroke-width="2" fill="none"/>'
               '<path d="M82 54 Q92 24 104 44 Q108 20 120 28 Q134 40 130 52 Q118 40 114 54 Q104 38 96 56 Q90 46 82 54 Z" fill="#f08a3a"/>'
               '<path d="M92 52 Q100 36 108 50 Q114 40 122 50 Q110 46 104 58 Q98 46 92 52 Z" fill="#f8d56a"/></g>')
    out.append('<path d="M96 108 Q106 96 112 108 Q120 92 130 106 Q138 94 146 108" fill="none" stroke="#fff" stroke-width="2.4" opacity="0.8"/>')
    # The third trumpet: a great star falling from heaven, blazing like a torch, on a third of the rivers (8:10-11).
    out.append('<path d="M232 22 L214 56" stroke="#f6d36a" stroke-width="3" opacity="0.7" stroke-linecap="round"/>' + _star(212, 60, 7, "#ffe28a"))
    out.append('<path d="M200 96 C204 88 214 92 216 98 Q222 108 232 110" fill="none" stroke="#8b1b1b" stroke-width="5" stroke-linecap="round"/><path d="M220 96 L214 60" stroke="#ffb347" stroke-width="1.6" stroke-dasharray="2 3" opacity="0.8"/>')
    # Six ships, two wrecked: a third (8:9). Nine creatures, three dead.
    for cx, cy, wr in ((20, 124, False), (50, 130, False), (162, 122, False), (196, 128, True), (126, 138, True), (84, 134, False)):
        out.append(plate.ship(cx, cy, 0.34, wrecked=wr))
    for k, (fx, fy) in enumerate(((22, 156), (56, 150), (88, 160), (118, 154), (150, 160), (180, 152), (206, 160), (40, 168), (140, 170))):
        out.append(plate.fish(fx, fy, 0.38, dead=k in (3, 5, 6)))
    # Seven angels, each with a trumpet, standing before God (8:2, 6).
    for i in range(7):
        ax = 18 + i * 34
        out.append(angel(ax, 38, 0.3, 1, pose="offer", spread=0.8))
        hx, hy = ax + 36 * 0.3, 38 - 58 * 0.3
        out.append(f'<path d="M{hx:.1f} {hy:.1f} L{hx + 11:.1f} {hy - 2:.1f}" stroke="{GOLD_DK}" stroke-width="1.4" stroke-linecap="round"/>'
                   f'<path d="M{hx + 11:.1f} {hy - 2:.1f} L{hx + 15:.1f} {hy - 5:.1f} L{hx + 15:.1f} {hy + 2:.1f} Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.6"/>')
    return "".join(out)


def _head(x, y, s, face=1, crown=True, horns=1, fill=BLOOD, edge="#2a0c0c", horn_crowns=False, names=False):
    """A dragon's head in profile, facing right at face = 1: a long snout, a mouth with teeth, a swept horn.
    crown: a diadem on the head (the dragon's seven, 12:3); horn_crowns: a diadem on each horn (the beast's ten, 13:1);
    names: blasphemous writing across the head (13:1)."""
    parts = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face:.3f} {s:.3f})">']
    for h in range(horns):
        d = h * 9
        parts.append(f'<path d="M{-2 - d} -10 C{-10 - d} -20 {-20 - d} -18 {-26 - d} -8 C{-18 - d} -12 {-10 - d} -10 {-4 - d} -6 Z" fill="{edge}"/>')
        if horn_crowns:
            parts.append(f'<path d="M{-12 - d} -17 l-1 -5 l3 2 l2 -3 l2 3 l3 -2 l0 5 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.6"/>')
    parts.append(f'<path d="M-11 6 C-13 -4 -5 -12 8 -12 C17 -12 25 -9 32 -4 C35 -2 34 1 31 2 L25 2 L30 6 C28 8 25 8 22 7 '
                 f'C16 11 6 11 -3 10 C-7 10 -10 9 -11 6 Z" fill="{fill}" stroke="{edge}" stroke-width="1.5" stroke-linejoin="round"/>')
    parts.append(f'<path d="M12 2 L31 1" stroke="{edge}" stroke-width="1.4" fill="none"/>')
    parts.append(f'<path d="M16 2 l2 4 l2 -4 M22 2 l2 3.6 l2 -3.6" fill="#fff" stroke="{edge}" stroke-width="0.6"/>')
    parts.append(f'<circle cx="9" cy="-5" r="2" fill="#f6d36a" stroke="{edge}" stroke-width="0.6"/><circle cx="9.4" cy="-5" r="0.8" fill="{edge}"/>')
    if names:
        parts.append(f'<path d="M-6 0 h5 M0 0 h4 M-6 3 h3 M-1 3 h6 M-5 -3 h6" stroke="#f6e7a8" stroke-width="0.9" opacity="0.9"/>')
    if crown:
        parts.append(f'<path d="M-6 -12 L-5 -18 L-1 -14 L3 -19 L7 -14 L11 -18 L12 -12 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/>')
    parts.append("</g>")
    return "".join(parts)


def _seven_heads(cx, cy, s, fill, edge, crown, rise=0, horn_crowns=False, names=False):
    """Seven heads on seven necks, ten horns among them (Revelation 12:3; 13:1): the middle head tallest."""
    horns = (2, 1, 2, 1, 1, 2, 1)
    out = []
    for i in range(7):
        off = i - 3
        hx, hy = cx + off * 15.5 * s, cy - (46 - abs(off) * 7 + rise) * s
        c1x, c1y = cx + off * 4 * s, cy - 26 * s
        path = (f'M{cx + off * 5 * s:.1f} {cy:.1f} C{c1x:.1f} {c1y:.1f} {hx - off * 2 * s:.1f} {hy + 18 * s:.1f} {hx:.1f} {hy + 4 * s:.1f}')
        out.append(f'<path d="{path}" stroke="{edge}" stroke-width="{9.4 * s:.1f}" fill="none" stroke-linecap="round"/>')
        out.append(f'<path d="{path}" stroke="{fill}" stroke-width="{7 * s:.1f}" fill="none" stroke-linecap="round"/>')
        out.append(_head(hx, hy, s * 0.9, 1 if off >= 0 else -1, crown, horns[i], fill, edge, horn_crowns, names))
    return "".join(out)


def _fallen(x, y, rot, s=0.5):
    """One of the dragon's angels, thrown down (Revelation 12:9): dark wings and a dark body, tumbling."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({s})">'
            f'{wings(0, 0, 1.0, 1, 0.9, "#4a3a5a", "#1c141c", "#5a4a6a")}'
            '<path d="M-8 4 C-10 30 -6 46 -2 54 L10 54 C12 38 10 20 8 4 Z" fill="#4a3a5a" stroke="#1c141c" stroke-width="1.4"/><circle cx="0" cy="-2" r="8" fill="#4a3a5a" stroke="#1c141c" stroke-width="1.4"/></g>')


def dragon():
    """Revelation 12:3-9: war in heaven. Michael and his angels fight the great red dragon, seven heads, ten horns and seven diadems;
    his tail sweeps down a third of the stars; he and his angels are thrown down."""
    out = _sky("w70-dragon-sky", "#0f0b1c", "#7a2a22")
    for x, y in ((22, 14), (60, 40), (96, 12), (150, 24), (206, 14), (226, 50), (116, 44)):
        out.append(_star(x, y, 3.4))
    # His tail sweeping a third of the stars out of the sky (12:4).
    out.append(f'<path d="M30 172 C60 178 100 176 150 164 C196 152 226 120 236 70" stroke="{BLOOD}" stroke-width="10" fill="none" stroke-linecap="round"/>')
    for k, (x, y) in enumerate(((224, 96), (232, 118), (214, 124), (206, 106))):
        out.append(f'<path d="M{x - 14} {y - 22} L{x} {y}" stroke="#f6e7a8" stroke-width="1.3" opacity="0.7"/>' + _star(x, y, 4, "#f6e7a8"))
    out.append(f'<path d="M124 172 C88 162 98 126 138 120 C176 114 178 96 156 86" stroke="{BLOOD}" stroke-width="22" fill="none" stroke-linecap="round"/>')
    out.append('<path d="M124 172 C88 162 98 126 138 120 C176 114 178 96 156 86" stroke="#c9382d" stroke-width="2" fill="none" stroke-dasharray="3 6" opacity="0.7"/>')
    out.append(_seven_heads(156, 90, 0.95, BLOOD, "#2a0c0c", True, rise=-6))
    # Michael and his angels, with spears and a sword, on the left of the sky (12:7).
    out.append(angel(36, 120, 0.6, 1, pose="point", spread=0.9))
    out.append('<path d="M56 80 L98 62" stroke="#e6e6ee" stroke-width="2.6" stroke-linecap="round"/><path d="M52 84 l6 -8" stroke="#e0b24a" stroke-width="2.2"/>')
    out.append(angel(14, 76, 0.4, 1, pose="point", spread=0.8))
    out.append('<path d="M26 58 L62 44" stroke="#d8d8d8" stroke-width="1.8" stroke-linecap="round"/>')
    out.append(angel(64, 40, 0.36, 1, pose="point", spread=0.8))
    out.append('<path d="M72 24 L96 14" stroke="#d8d8d8" stroke-width="1.6" stroke-linecap="round"/>')
    # The dragon's angels falling.
    out.append(_fallen(196, 30, 140, 0.34))
    out.append(_fallen(222, 56, 120, 0.3))
    out.append(_fallen(96, 150, 160, 0.3))
    return "".join(out)


def _stone_beast(x, y, s):
    """The image made for the beast (Revelation 13:14-15): a grey stone statue of the seven-headed beast on a plinth."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">',
           '<rect x="-34" y="-12" width="68" height="12" fill="#b3a897" stroke="#5e5547" stroke-width="1.2"/><rect x="-26" y="-26" width="52" height="14" fill="#a39886" stroke="#5e5547" stroke-width="1.2"/>',
           '<path d="M-22 -26 C-22 -44 22 -44 22 -26 Z" fill="#a39886" stroke="#5e5547" stroke-width="1.2"/>',
           _seven_heads(0, -34, 0.62, "#a39886", "#5e5547", False, rise=-2),
           '</g>']
    return "".join(out)


def beast():
    """Revelation 13:1-17: the beast from the sea (a leopard's body, a bear's feet, seven heads, ten horns crowned, blasphemous names),
    the beast from the earth with two horns like a lamb, the image of the beast, fire from heaven, and people marked on the forehead or hand."""
    out = _sky("w70-beast-sky", "#1d1722", "#8a7058")
    out.append('<path d="M0 100 H240 V180 H0 Z" fill="#2f4a62"/>')
    for y in (110, 124, 142, 160):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#fff" stroke-width="1.1" fill="none" opacity="0.2"/>')
    # The sea beast, standing in the shallows at the right.
    spots = "".join(f'<ellipse cx="{x}" cy="{y}" rx="3.6" ry="2.5" fill="#3a2812"/>' for x, y in ((122, 92), (138, 96), (154, 90), (168, 96), (132, 104), (150, 106)))
    for lx in (126, 142, 164, 178):
        out.append(f'<path d="M{lx} 102 V114" stroke="#2a1d10" stroke-width="9" stroke-linecap="round"/><path d="M{lx} 102 V114" stroke="#5a3f26" stroke-width="7" stroke-linecap="round"/>'
                   f'<ellipse cx="{lx}" cy="116" rx="7" ry="3.4" fill="#5a3f26" stroke="#2a1d10" stroke-width="1.1"/>')
    out.append('<path d="M116 94 C116 78 140 74 160 76 C178 76 196 80 198 94 C196 106 178 108 158 108 C138 108 116 106 116 94 Z" fill="#b98a4a" stroke="#2a1d10" stroke-width="1.5"/>')
    out.append(spots)
    out.append('<path d="M196 86 Q222 76 224 100 Q214 90 200 98 Z" fill="#b98a4a" stroke="#2a1d10" stroke-width="1.3"/>')
    out.append(_seven_heads(158, 80, 0.86, "#b98a4a", "#2a1d10", False, rise=-3, horn_crowns=True, names=True))
    # Fire out of heaven on the earth (13:13).
    out.append('<path d="M70 0 L58 30 L68 28 L52 62" stroke="#f8d56a" stroke-width="3.4" fill="none" stroke-linejoin="round"/><path d="M70 0 L58 30 L68 28 L52 62" stroke="#fff" stroke-width="1.2" fill="none"/>')
    # The image of the beast on its plinth (13:14-15).
    out.append(_stone_beast(52, 128, 0.9))
    # The second beast, out of the earth, two horns like a lamb and a dragon's speech (13:11).
    out.append('<g transform="translate(204 136)"><path d="M-14 -4 V0 M-6 -4 V0 M8 -4 V0 M16 -4 V0" stroke="#2a1d10" stroke-width="3.4" stroke-linecap="round"/>'
               '<ellipse cx="0" cy="-14" rx="22" ry="11" fill="#6a5a4a" stroke="#2a1d10" stroke-width="1.3"/>'
               '<path d="M16 -20 Q24 -30 30 -24 Q36 -20 34 -14 L26 -14 Q20 -12 16 -14 Z" fill="#6a5a4a" stroke="#2a1d10" stroke-width="1.2"/>'
               '<path d="M22 -28 q-3 -8 3 -10 M28 -27 q2 -8 7 -8" stroke="#2a1d10" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M26 -16 l8 1" stroke="#8b1b1b" stroke-width="1.6"/></g>')
    # People kneeling to the image, each marked on the forehead or on the right hand (13:16).
    for k, x in enumerate((104, 126, 148, 170)):
        body, _ = comic.figure("man" if k % 2 else "woman", x, 176, 0.5, -1 if x > 90 else 1, pose="fold", stance="kneel", tone=k)
        out.append(body)
        out.append(f'<rect x="{x - 6 - 3 * (1 if x > 90 else -1) :.1f}" y="146" width="3.6" height="3.6" fill="{BLOOD}" stroke="#2a0c0c" stroke-width="0.4"/>')
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
    """Revelation 15:5-16:21: the tent of witness opened in heaven and full of smoke; seven angels in bright linen with golden
    sashes, each with a golden bowl of the wrath of God; the first two poured out on the earth and the sea, which becomes blood."""
    out = _sky("w70-bowls-sky", "#3a1620", "#c25a34")
    out.append('<path d="M0 132 H240 V180 H0 Z" fill="#6e1c1c"/>')
    for y in (142, 154, 168):
        out.append(f'<path d="M0 {y} q10 -5 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" stroke="#e0867a" stroke-width="1.1" fill="none" opacity="0.4"/>')
    out.append('<path d="M2 132 L34 62 L66 132 Z" fill="#e8dcc0" stroke="#8d7650" stroke-width="1.5"/>'
               '<path d="M34 62 L22 132 H46 Z" fill="#2a1d18"/><path d="M34 62 L26 132 M34 62 L42 132" stroke="#8d7650" stroke-width="1.2"/>'
               '<path d="M34 60 C16 48 44 34 30 18 C24 12 34 8 40 14" fill="none" stroke="#bdb2a4" stroke-width="9" stroke-linecap="round" opacity="0.65"/>')
    # Seven angels come out of the temple, each carrying a golden bowl: four in front, three behind.
    spots = [(84 + i * 38, 150, 0.46) for i in range(4)] + [(104 + i * 38, 124, 0.38) for i in range(3)]
    for ax, ay, sc in sorted(spots, key=lambda t: t[1]):
        out.append(angel(ax, ay, sc, 1, pose="offer", spread=0.8))
        hx, hy = ax + 36 * sc, ay - 58 * sc
        out.append(f'<path d="M{hx - 5:.1f} {hy - 1:.1f} h10 a5 3.6 0 0 1 -10 0 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.9"/>')
        out.append(f'<path d="M{ax - 5 * sc:.1f} {ay - 34 * sc:.1f} h{10 * sc:.1f}" stroke="{GOLD}" stroke-width="1.6"/>')
    # The first bowl on the earth, the second on the sea (16:2-3): blood running from the bowls.
    for ax, ay, sc in spots[:2]:
        hx, hy = ax + 36 * sc, ay - 58 * sc + 3
        out.append(f'<path d="M{hx + 6:.1f} {hy:.1f} C{hx + 12:.1f} {hy + 14:.1f} {hx + 10:.1f} {hy + 28:.1f} {hx + 14:.1f} {ay + 12:.1f}" stroke="{BLOOD}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
        out.append(f'<ellipse cx="{hx + 14:.1f}" cy="{ay + 14:.1f}" rx="9" ry="2.4" fill="#d2493d" opacity="0.85"/>')
    return "".join(out)


def second_coming():
    """Revelation 19:11-21: heaven opened; Faithful and True on a white horse, many diadems, a robe dipped in blood, a sword from His
    mouth; the armies of heaven in fine linen on white horses; an angel in the sun calling the birds; the beast and the kings below."""
    import build_tribulation_graphics as plate

    out = _sky("w70-return-sky", "#1c2a4d", "#a9bfe0")
    out.append('<defs><radialGradient id="w70-return-glow" cx="0.5" cy="0.4" r="0.55"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.7"/>'
               '<stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-return-glow)"/>')
    for k in range(16):
        a = math.pi * (0.04 + 0.92 * k / 15)
        out.append(f'<path d="M120 56 L{120 + 220 * math.cos(a):.1f} {56 - 220 * math.sin(a) * 0.3:.1f}" stroke="#fff" stroke-width="2" opacity="0.14"/>')
    out.append('<path d="M0 30 Q60 14 120 28 T240 24 V0 H0 Z" fill="#101a33"/>')
    # An angel standing in the sun, calling the birds to the great supper of God (19:17).
    out.append('<circle cx="206" cy="26" r="13" fill="#ffe9a0" stroke="#e0b24a" stroke-width="1.2"/>')
    out.append(angel(206, 36, 0.3, -1, pose="raise", spread=0.8))
    for bx, by in ((164, 18), (180, 30), (150, 36), (190, 12), (228, 48), (140, 14), (174, 46)):
        out.append(f'<path d="M{bx - 5} {by} q2.5 -3.6 5 0 q2.5 -3.6 5 0" fill="none" stroke="#1a1a2a" stroke-width="1.3" stroke-linecap="round"/>')
    # The beast, the kings and their armies gathered below to make war (19:19).
    out.append('<path d="M0 156 Q60 144 120 152 T240 146 V180 H0 Z" fill="#5a6a4a"/>')
    for k in range(13):
        body, _ = comic.figure("soldier", 10 + k * 18, 176, 0.27, 1 if k % 2 else -1, pose="stand", holds="spear", tone=k)
        out.append(body)
    # The armies of heaven, in fine linen, white and pure, on white horses (19:14).
    for x, y, sc in ((150, 78, 0.3), (186, 86, 0.28), (4, 96, 0.3), (36, 112, 0.28)):
        out.append(plate.horse(x, y, "#f5f1e6", "#7d7464", sc))
        r, _ = plate.rider(x + plate.SEAT[0] * sc, y + plate.SEAT[1] * sc, "#f4ecd6", s=sc * 1.1, arm=(30,))
        out.append(r)
    sc = 0.62
    x, y = 70, 76
    out.append(plate.horse(x, y, "#fbf8ee", "#8a8070", sc))
    rx, ry = x + plate.SEAT[0] * sc, y + plate.SEAT[1] * sc
    r, hand = plate.rider(rx, ry, "#7a1a1a", s=sc * 1.15, arm=(40,))
    out.append(r)
    # The robe dipped in blood (19:13), and a name on the thigh: King of kings and Lord of lords (19:16).
    out.append(f'<path d="M{rx - 10 * sc:.1f} {ry - 4 * sc:.1f} C{rx - 28 * sc:.1f} {ry - 2 * sc:.1f} {rx - 40 * sc:.1f} {ry + 10 * sc:.1f} {rx - 46 * sc:.1f} {ry + 26 * sc:.1f}" stroke="{BLOOD}" stroke-width="{6 * sc:.1f}" fill="none" opacity="0.85"/>')
    out.append(f'<path d="M{rx + 2:.1f} {ry + 4 * sc:.1f} l{9 * sc:.1f} {10 * sc:.1f}" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"/>')
    hx, hy = rx + 9 * sc * 1.15, ry - 50 * sc * 1.15
    for k in range(5):
        out.append(f'<ellipse cx="{hx:.1f}" cy="{hy - 9 - k * 2.4:.1f}" rx="{8 - k * 0.3:.1f}" ry="1.8" fill="none" stroke="{GOLD}" stroke-width="1.4"/>')
    out.append(f'<path d="M{hx + 4:.1f} {hy:.1f} L{hx + 66:.1f} {hy - 8:.1f}" stroke="#e8e8f0" stroke-width="2.2" stroke-linecap="round"/>')
    # Eyes like a flame of fire (19:12), the face itself left blank like every figure here.
    out.append(f'<path d="M{hx - 3:.1f} {hy - 1:.1f} q2 -4 4 0 q-2 2 -4 0 Z" fill="#f08a3a"/>')
    return "".join(out)


def martyrs():
    """Revelation 6:9-11: under the altar the souls of those slain for the word of God, crying 'How long?', each given a white robe."""
    out = _sky("w70-martyr-sky", "#f7ecce", "#cdb888")
    for k in range(14):
        a = math.pi * (0.1 + 0.8 * k / 13)
        out.append(f'<path d="M110 52 L{110 + 160 * math.cos(a):.1f} {52 - 160 * math.sin(a):.1f}" stroke="#fff" stroke-width="3" opacity="0.3"/>')
    out.append('<path d="M0 146 H240 V180 H0 Z" fill="#a8956a"/>')
    out.append(f'<rect x="22" y="40" width="176" height="14" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.6"/>')
    for hx in (22, 198):
        out.append(f'<path d="M{hx - 3} 40 q-2 -12 5 -14 q0 8 3 14 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.2" transform="translate({0 if hx < 100 else -3} 0)"/>')
    out.append(f'<rect x="28" y="54" width="164" height="6" fill="#cdb26a" stroke="{GOLD_DK}" stroke-width="1"/>')
    for gx in range(36, 190, 12):
        out.append(f'<path d="M{gx} 54 v6" stroke="{GOLD_DK}" stroke-width="1"/>')
    out.append('<rect x="32" y="60" width="156" height="86" fill="#241c14"/>')
    out.append(f'<rect x="26" y="60" width="8" height="86" fill="#cdb26a" stroke="{GOLD_DK}" stroke-width="1.2"/><rect x="186" y="60" width="8" height="86" fill="#cdb26a" stroke="{GOLD_DK}" stroke-width="1.2"/>')
    out.append('<path d="M70 38 C58 28 82 20 70 8 M110 38 C98 28 122 20 110 6 M150 38 C138 28 162 20 150 8" fill="none" stroke="#9c8a74" stroke-width="3.4" stroke-linecap="round" opacity="0.8"/>')
    out.append('<path d="M60 40 q4 -8 8 0 q4 -10 8 0 Z M104 40 q4 -9 8 0 q4 -9 8 0 Z" fill="#f08a3a"/>')
    for k, x in enumerate((46, 68, 90, 112, 134, 156)):
        body, _ = comic.figure("robed", x, 146, 0.46, 1 if k < 4 else -1, pose="look_up", stance="kneel", tone=k)
        out.append(body)
    out.append(angel(214, 150, 0.62, -1, pose="offer", holds="robe", spread=0.9))
    return "".join(out)


def _frog(x, y, s=1.0, rot=0):
    """An unclean spirit like a frog (Revelation 16:13)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({s})"><ellipse cx="0" cy="0" rx="9" ry="6" fill="#5f8a3a" stroke="#2a4a1a" stroke-width="1"/>'
            '<circle cx="-4" cy="-6" r="3" fill="#7ea84a" stroke="#2a4a1a" stroke-width="0.8"/><circle cx="4" cy="-6" r="3" fill="#7ea84a" stroke="#2a4a1a" stroke-width="0.8"/>'
            '<circle cx="-4" cy="-6" r="1" fill="#1a1a1a"/><circle cx="4" cy="-6" r="1" fill="#1a1a1a"/>'
            '<path d="M-8 3 L-15 8 L-10 10 M8 3 L15 8 L10 10 M-5 5 L-9 11 M5 5 L9 11" stroke="#2a4a1a" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>')


def armageddon():
    """Revelation 16:12-16: the great river Euphrates dried up to make way for the kings from the east; three unclean spirits like frogs
    from the mouths of the dragon, the beast and the false prophet; the kings of the whole world gathered at Armageddon."""
    out = _sky("w70-arm-sky", "#3b2a3a", "#c8744a")
    for k in range(10):
        a = math.pi * (0.1 + 0.8 * k / 9)
        out.append(f'<path d="M120 100 L{120 + 160 * math.cos(a):.1f} {100 - 160 * math.sin(a):.1f}" stroke="#f6d36a" stroke-width="1.6" opacity="0.14"/>')
    # Three mouths, three frogs: the dragon, the beast and the false prophet (16:13).
    out.append(_head(28, 28, 0.9, 1, False, 1, BLOOD, "#2a0c0c"))
    out.append(_head(112, 22, 0.9, 1, False, 2, "#b98a4a", "#2a1d10"))
    body, _ = comic.figure("man", 196, 70, 0.55, -1, pose="shout", tone=2)
    out.append(body)
    out.append(_frog(60, 36, 0.9, -10) + _frog(144, 30, 0.9, 8) + _frog(176, 36, 0.8, -20))
    out.append('<path d="M46 32 C52 34 56 34 60 36 M130 28 C136 30 140 30 144 30 M186 40 C182 38 180 38 176 36" stroke="#9ac35a" stroke-width="1.2" fill="none" stroke-dasharray="2 2"/>')
    # Har-Magedon, the mountain of Megiddo, and the plain beneath it.
    out.append('<path d="M60 110 Q110 70 150 98 Q176 112 200 110 L200 130 H60 Z" fill="#8a6a4a" stroke="#4a3626" stroke-width="1.2"/>')
    out.append('<path d="M0 118 H240 V180 H0 Z" fill="#b99a66"/>')
    # The Euphrates, dried up: a cracked bed with the last water shrinking at its edges (16:12).
    out.append('<path d="M-4 130 Q60 120 120 134 T244 130 L244 152 Q180 148 120 156 T-4 152 Z" fill="#a8855a" stroke="#6a4a2a" stroke-width="1"/>')
    out.append('<path d="M-4 134 Q60 126 120 138 T244 134 M-4 148 Q60 142 120 152 T244 148" stroke="#6fa0c8" stroke-width="2.4" fill="none" opacity="0.9"/>')
    for x in range(8, 236, 22):
        out.append(f'<path d="M{x} 138 l5 4 l-2 6 l6 3 M{x + 9} 140 l-4 5 l3 5" stroke="#5a3e24" stroke-width="1" fill="none"/>')
    # The kings of the east crossing the dry bed, and the kings of the whole world gathered on the plain.
    for k in range(7):
        body, _ = comic.figure("soldier", 130 + k * 15, 160, 0.34, -1, pose="stand", holds="spear", tone=k)
        out.append(body)
    for k in range(7):
        body, _ = comic.figure("soldier", 12 + k * 14, 176, 0.38, 1, pose="stand", holds="spear", tone=k + 1)
        out.append(body)
    return "".join(out)


def rapture():
    """1 Thessalonians 4:16-17; 1 Corinthians 15:51-52: the Lord descends with a cry of command, the voice of the archangel and the trumpet of God;
    the dead in Christ rise first, then the living are caught up together with them in the clouds to meet Him in the air."""
    out = _sky("w70-rapture-sky", "#6f9fd8", "#f4e3b8")
    out.append('<defs><radialGradient id="w70-rapt-glow" cx="0.5" cy="0" r="0.8"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.95"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-rapt-glow)"/>')
    for k in range(12):
        a = math.pi * (0.2 + 0.6 * k / 11)
        out.append(f'<path d="M120 0 L{120 + 200 * math.cos(a):.1f} {200 * math.sin(a):.1f}" stroke="#fff" stroke-width="3" opacity="0.2"/>')
    out.append('<path d="M0 148 Q60 136 120 146 T240 140 V180 H0 Z" fill="#8da06a"/>')
    # The trumpet of God, its blast rippling out from the clouds.
    out.append(f'<path d="M156 20 L204 8" stroke="{GOLD_DK}" stroke-width="4" stroke-linecap="round"/><path d="M204 8 L222 -2 L222 20 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.4"/>')
    for r in (10, 16, 22):
        out.append(f'<path d="M{222 + r * 0.3} {9 - r} Q{222 + r} 9 {222 + r * 0.3} {9 + r}" fill="none" stroke="#fff" stroke-width="1.3" opacity="{0.9 - r * 0.02:.2f}"/>')
    for cx, cy, cs in ((38, 26, 1.0), (128, 20, 1.1), (200, 52, 0.8)):
        out.append(comic.PROPS["cloud"](cx, cy, cs))
    # The dead in Christ rising from their graves, first.
    for tx in (22, 54, 86):
        out.append(comic.PROPS["tomb"](tx, 152, 0.34))
    for k, (x, y) in enumerate(((22, 112), (54, 92), (86, 118), (36, 62), (72, 54))):
        out.append(f'<path d="M{x} {y + 8} V150" stroke="#fffbe6" stroke-width="3" opacity="0.28"/>')
        body, _ = comic.figure("robed", x, y + 8, 0.42, 1, pose="raise", tone=k)
        out.append(body)
    # The living, caught up together with them.
    for k, (x, y) in enumerate(((140, 128), (162, 100), (186, 124), (206, 84), (150, 66), (224, 118))):
        out.append(f'<path d="M{x} {y + 8} V150" stroke="#fffbe6" stroke-width="3" opacity="0.28"/>')
        body, _ = comic.figure("robed", x, y + 8, 0.42, -1, pose="raise", tone=k + 2)
        out.append(body)
    return "".join(out)


def multitude():
    """Revelation 7:9-17: a great multitude that no one could number, from every nation, tribe, people and language,
    in white robes with palm branches, standing before the throne and before the Lamb."""
    out = _sky("w70-multi-sky", "#fff3cf", "#d9e6c4")
    for k in range(14):
        a = math.pi * (0.1 + 0.8 * k / 13)
        out.append(f'<path d="M120 24 L{120 + 220 * math.cos(a):.1f} {24 + 220 * math.sin(a) * 0.5:.1f}" stroke="#fff" stroke-width="3" opacity="0.3"/>')
    out.append(comic.PROPS["throne"](120, 54, 0.42))
    out.append(_lamb(122, 76, 0.42))
    out.append('<path d="M0 84 Q60 74 120 82 T240 78 V180 H0 Z" fill="#cbd9a8"/>')
    n = 0
    for row, (y, sc, count) in enumerate(((98, 0.2, 20), (112, 0.26, 16), (130, 0.32, 13), (152, 0.4, 10), (178, 0.5, 8))):
        for k in range(count):
            x = (k + 0.5) * 240 / count + (6 if row % 2 else -2)
            who = ("robed", "man", "woman")[n % 3] if False else "robed"
            body, _ = comic.figure(who, x, y, sc, 1 if k % 2 else -1, pose="praise" if n % 3 else "raise", holds="palm" if n % 2 == 0 else None, tone=n)
            out.append(body)
            n += 1
    out.append(angel(24, 70, 0.34, 1, pose="open", spread=0.8))
    out.append(angel(216, 70, 0.34, -1, pose="open", spread=0.8))
    return "".join(out)


def look_pierced():
    """Zechariah 12:10; 14:4: Jesus stands on the Mount of Olives, which splits in two from east to west; Jerusalem mourns as for an only child,
    looking on Him whom they have pierced."""
    out = _sky("w70-mourn-sky", "#a9bfd8", "#f2d9a8")
    out.append('<defs><radialGradient id="w70-mourn-glow" cx="0.72" cy="0.38" r="0.4"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.95"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-mourn-glow)"/>')
    # Jerusalem behind: wall, towers, the temple.
    out.append('<path d="M0 104 H90 V120 H0 Z" fill="#d8c7a3" stroke="#8d7650" stroke-width="1"/>')
    for x in (6, 30, 56, 80):
        out.append(f'<rect x="{x}" y="92" width="10" height="14" fill="#cbb98c" stroke="#8d7650" stroke-width="0.8"/>')
    out.append('<rect x="38" y="70" width="34" height="34" fill="#eee4c8" stroke="#8d7650" stroke-width="1"/><rect x="50" y="82" width="10" height="22" fill="#e0b24a"/>')
    # The Mount of Olives split in two with a great valley between (14:4).
    out.append('<path d="M96 180 L96 130 Q112 96 132 86 L140 86 L134 180 Z" fill="#b8a374" stroke="#6a5634" stroke-width="1.4"/>')
    out.append('<path d="M146 180 L152 90 L170 82 Q214 90 240 124 V180 Z" fill="#c4ad7c" stroke="#6a5634" stroke-width="1.4"/>')
    out.append('<path d="M134 180 L140 86 L152 90 L146 180 Z" fill="#241a14"/><path d="M137 100 L141 130 L137 160 M146 100 L144 140" stroke="#5a4634" stroke-width="1" fill="none"/>')
    # Jesus on the mountain, in light, the marks of the nails in His hands (the pierced).
    jb, _ = comic.figure("jesus", 188, 92, 0.6, -1, pose="open")
    out.append(jb)
    out.append('<circle cx="170" cy="62" r="4" fill="none"/><circle cx="168" cy="73" r="1.4" fill="#a3202a"/><circle cx="202" cy="73" r="1.4" fill="#a3202a"/>')
    # The mourners of Jerusalem: a mother with her only child, men and women kneeling, looking up.
    out.append('<path d="M0 150 Q60 140 120 148 T240 146 V180 H0 Z" fill="#c9b07e"/>')
    for k, (who, x, st, pose) in enumerate((("woman", 20, "kneel", "look_up"), ("man", 44, "kneel", "look_up"), ("woman", 70, "kneel", "heart"),
                                              ("man", 92, "kneel", "look_up"), ("woman", 54, "kneel", "fold"))):
        body, _ = comic.figure(who, x, 176 if k != 4 else 164, 0.62 if k != 4 else 0.46, 1, pose=pose, stance=st, tone=k)
        out.append(body)
    cb, _ = comic.figure("child", 64, 178, 0.6, 1, tone=1)
    out.append(cb)
    for k, (who, x) in enumerate((("man", 150), ("woman", 176), ("man", 202), ("woman", 226))):
        body, _ = comic.figure(who, x, 178, 0.58, -1, pose="look_up", stance="kneel", tone=k + 1)
        out.append(body)
    return "".join(out)


def abomination():
    """Daniel 9:27; 2 Thessalonians 2:3-4; Matthew 24:15-16: sacrifice and offering stopped, the altar cold; the man of lawlessness takes his seat
    in the temple of God, proclaiming himself to be God, an image set up; those in Judea flee to the mountains."""
    out = list(comic.SCENES["temple"](240, 180, "dusk", "w70-abom-sky"))
    # The altar of burnt offering with no fire: sacrifice and offering put to an end (Daniel 9:27).
    out.append('<rect x="14" y="128" width="46" height="26" fill="#b3a897" stroke="#5e5547" stroke-width="1.4"/><path d="M14 128 l-3 -6 h8 M60 128 l3 -6 h-8" stroke="#5e5547" stroke-width="2" fill="none"/>'
               '<ellipse cx="37" cy="127" rx="20" ry="4" fill="#5a5248"/><path d="M27 124 q4 -4 8 0 M40 124 q5 -4 10 0" stroke="#8a8278" stroke-width="1.4" fill="none"/>')
    # The man of lawlessness, seated on a throne in the temple court, arms raised, proclaiming himself to be God (2 Thessalonians 2:4).
    out.append('<defs><radialGradient id="w70-abom-halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#c0382a" stop-opacity="0.8"/><stop offset="1" stop-color="#c0382a" stop-opacity="0"/></radialGradient></defs>')
    out.append('<ellipse cx="116" cy="108" rx="52" ry="58" fill="url(#w70-abom-halo)"/>')
    out.append('<rect x="92" y="120" width="48" height="30" fill="#6a5a4a" stroke="#2a1d10" stroke-width="1.4"/><rect x="86" y="148" width="60" height="8" fill="#5a4a3a" stroke="#2a1d10" stroke-width="1.2"/>'
               '<path d="M96 120 V84 Q116 74 136 84 V120" fill="#5a4a3a" stroke="#2a1d10" stroke-width="1.4"/>')
    body, _ = comic.figure("man", 116, 140, 0.9, 1, stance="sit", pose="open")
    out.append(comic.recolour(body, "silhouette"))
    out.append(f'<path d="M100 76 L104 66 L109 72 L116 62 L123 72 L128 66 L132 76 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/>')
    # An image set up in the holy place, and its smoking altar (Matthew 24:15).
    out.append(comic.PROPS["idol"](166, 152, 0.72))
    # Those in Judea fleeing to the mountains (Matthew 24:16).
    out.append('<path d="M196 112 Q204 84 222 80 Q236 82 240 92 V112 Z" fill="#9a8a6a"/>')
    for k, x in enumerate((200, 212, 224, 236)):
        body, _ = comic.figure("man" if k % 2 else "woman", x, 116, 0.2, 1, pose="run", stance="walk", tone=k)
        out.append(body)
    return "".join(out)


def marriage_of_lamb():
    """Revelation 19:6-9: the marriage supper of the Lamb. The Bride has made herself ready in fine linen, bright and pure; a great multitude cries
    Hallelujah; the guests are blessed."""
    out = list(comic.SCENES["room"](240, 180, "day", "w70-marr-sky"))
    out.append('<defs><radialGradient id="w70-marr-glow" cx="0.5" cy="0.45" r="0.55"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.9"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient></defs>')
    out.append('<rect width="240" height="180" fill="url(#w70-marr-glow)"/>')
    out.append(_lamb(120, 98, 0.46))
    # The long table, spread with a white cloth, golden cups, bread and fruit.
    out.append('<path d="M10 118 L230 118 L240 132 L0 132 Z" fill="#fffdf7" stroke="#cdbf9e" stroke-width="1.2"/><rect x="0" y="132" width="240" height="14" fill="#f4ecd6" stroke="#cdbf9e" stroke-width="1"/>')
    for x in range(26, 220, 24):
        out.append(f'<path d="M{x - 4} 120 h8 l-1.5 8 h-5 Z" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="0.8"/><ellipse cx="{x + 12}" cy="124" rx="5" ry="2" fill="#e8d4a0" stroke="#a8924a" stroke-width="0.6"/><circle cx="{x + 12}" cy="121.6" r="1.6" fill="#a3202a"/>')
    # Guests on both sides, hands lifted: Hallelujah (19:6).
    for k, x in enumerate((20, 46, 72, 98)):
        body, _ = comic.figure("robed", x, 124, 0.5, 1, pose="praise", stance="sit", tone=k)
        out.append(body)
    for k, x in enumerate((142, 168, 194, 220)):
        body, _ = comic.figure("robed", x, 124, 0.5, -1, pose="praise", stance="sit", tone=k + 4)
        out.append(body)
    # The Bride in fine linen, bright and pure (19:8), in front.
    bb, _ = comic.figure("bride", 120, 180, 0.62, 1, pose="open")
    out.append(bb)
    return "".join(out)


def _lampstand(x, y, s=1.0):
    """A seven-branched golden lampstand (Revelation 11:4; Zechariah 4:2), flames lit."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})" fill="none" stroke="{GOLD_DK}" stroke-width="2.2" stroke-linecap="round">',
           f'<path d="M0 0 V-34 M-6 0 H6 M-3 -6 H3" />']
    for k in (1, 2, 3):
        out.append(f'<path d="M0 -10 C{-8 * k} -10 {-8 * k} -22 {-8 * k} -30 M0 -10 C{8 * k} -10 {8 * k} -22 {8 * k} -30"/>')
    out.append("</g>")
    for dx in (-24, -16, -8, 0, 8, 16, 24):
        h = 30 if abs(dx) < 1 else 28
        out.append(f'<path d="M{x + dx * s - 1.6 * s:.1f} {y - h * s:.1f} q{1.6 * s:.1f} {-8 * s:.1f} {3.2 * s:.1f} 0 q{-1.6 * s:.1f} {2.4 * s:.1f} {-3.2 * s:.1f} 0 Z" fill="#f08a3a"/>')
    return "".join(out)


def _olive(x, y, s=1.0):
    """An olive tree, grey-green and gnarled (Revelation 11:4; Zechariah 4:3)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M0 0 C-2 -14 4 -22 0 -34 M0 -18 L-8 -28 M0 -22 L8 -32" stroke="#5b4632" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
            '<ellipse cx="-2" cy="-40" rx="16" ry="10" fill="#8aa07a" stroke="#4f6544" stroke-width="1"/><ellipse cx="10" cy="-33" rx="9" ry="6" fill="#9db38d"/>'
            '<ellipse cx="-12" cy="-34" rx="9" ry="6" fill="#7d936f"/>'
            '<circle cx="-6" cy="-36" r="1.6" fill="#3a3a2a"/><circle cx="6" cy="-44" r="1.6" fill="#3a3a2a"/></g>')


def two_witnesses():
    """Revelation 11:3-6: two witnesses in sackcloth, the two olive trees and the two lampstands, fire from their mouths on those who would harm them."""
    out = list(comic.SCENES["street"](240, 180, "storm", "w70-witness-sky"))
    out.append(_olive(16, 150, 0.95))
    out.append(_lampstand(34, 150, 0.9))
    out.append(_olive(122, 150, 0.8))
    out.append(_lampstand(140, 150, 0.8))
    for x, tone in ((50, 0), (96, 1)):
        body, _ = comic.figure("witness", x, 154, 1.0, 1, pose="open" if tone == 0 else "point", tone=tone)
        out.append(body)
    out.append(comic.flame_jet(70, 86, 168, 94, 0.5))
    out.append(comic.flame_jet(104, 88, 178, 106, 0.4))
    for x in (182, 210):
        body, _ = comic.figure("soldier", x, 154, 0.92, -1, pose="stand", holds="spear")
        out.append(body)
    return "".join(out)


ART = {
    "lamb_scroll": ("the throne under its rainbow with twenty-four crowns round it, the Lamb standing as though slain, and the scroll with seven seals (Revelation 4-5)", lamb_scroll),
    "seals_1_4": ("four riders on a white, a red, a black and a pale horse galloping under a storm sky (Revelation 6:1-8)", horsemen_four),
    "two_witnesses": ("two men in sackcloth with fire pouring from their mouths toward soldiers with spears (Revelation 11:3-5)", two_witnesses),
    "rapture": ("believers in white rising from open graves and from the ground in columns of light toward clouds, a trumpet sounding above (1 Thessalonians 4:16-17)", rapture),
    "abomination": ("a man in silhouette seated on a throne in the temple court, arms raised, an image beside him and the altar cold; people fleeing toward the mountains (Daniel 9:27; 2 Thessalonians 2:4; Matthew 24:15-16)", abomination),
    "multitude": ("a great crowd in white robes with palm branches before the throne and the Lamb, angels at either side (Revelation 7:9-10)", multitude),
    "armageddon": ("the dried Euphrates, three frog-like spirits from the mouths of the dragon, the beast and the false prophet, and the armies of the kings gathered under the hill of Megiddo (Revelation 16:12-16)", armageddon),
    "marriage_of_lamb": ("the Bride in fine linen before a long table with guests lifting their hands and the Lamb behind (Revelation 19:6-9)", marriage_of_lamb),
    "look_pierced": ("Jesus standing in light on the Mount of Olives split in two, the nail marks in His hands, Jerusalem mourning, a mother and child among those kneeling (Zechariah 12:10; 14:4)", look_pierced),
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
