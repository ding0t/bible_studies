"""The one-minute comic: a reusable cast, poses, scenes, speech bubbles and panel layouts.

A comic is data. utils/build_comics.py reads docs/data/comics/<slug>.toml and calls render(); this
module draws it in the same hand as the Larkin plates (lib/larkin.py: parchment, ink, the ruled
border, the serif), so a comic sits beside them as one set.

Every figure is drawn in its own units, feet at (0, 0), facing right, about 105 units tall, and
placed with translate/scale (a negative x-scale turns it to face left). Faces are left blank on
purpose: drawn-graphics.md rules out drawing the face of Jesus, and a cast where nobody has a face
keeps Him from being the one exception the eye goes looking for. Who is who is carried by costume,
colour and pose, the way a reader recognises a figure in a stained-glass window.
"""

import math

from lib.larkin import (W, INK, MUTED, PAPER, CARD, RED, GOLD, GOLD_EDGE, GOLD_TINT, text, svg_open, heading, banner, credit)

# --- palette -------------------------------------------------------------------------------------

SKINS = ["#b88a62", "#a8774f", "#c39a72", "#9a6a45", "#b07f58"]
HAIR = "#3b2a1a"
HAIR_GREY = "#8a8178"
SANDAL = "#5a3d22"
STONE = "#9a8f80"
STONE_EDGE = "#5e5547"
FOLD = "#00000030"
LITE = "#ffffff30"
GLOW = "#f6e2a0"
JESUS_ROBE = "#efe6d2"
JESUS_EDGE = "#b9ab8c"
JESUS_MANTLE = "#9b3b2c"
SHAWL = "#ece3cc"
SHAWL_STRIPE = "#2f4f7f"
SEPIA = "#a67c3d"

# Sky gradients, top to horizon.
SKIES = {
    "day": ("#cfdbe6", "#f3e2bd"),
    "winter": ("#93a3b3", "#d6d9d8"),
    "dusk": ("#5d5a78", "#e9b27a"),
    "night": ("#1d2236", "#3e4562"),
    "storm": ("#4a4652", "#9a9290"),
}
GROUND = "#d9cba4"
GROUND_NEAR = "#cbb98c"
WALL = "#d8c7a3"
WALL_EDGE = "#8d7650"
WATER = "#7d9bb0"

# --- the cast ------------------------------------------------------------------------------------
#
# Each entry is a costume. robes lists alternatives, so a crowd of the same kind varies by index.
# mantle: "stole" (over one shoulder, falling behind), "shawl" (a striped prayer mantle over the
# head with tassels at its corners, Numbers 15:38), "veil" (head to hem), "hood" (a head cloth with
# a band), "helmet", or None. name is how the generated <desc> refers to the figure.

CAST = {
    "jesus": dict(name="Jesus", robes=[JESUS_ROBE], edge=JESUS_EDGE, mantle="stole",
                  mantle_fill=JESUS_MANTLE, hair="long", beard=True, glow=True),
    "authority": dict(name="an authority", robes=["#3d4a63", "#4a3a28", "#3a3550", "#55603f", "#6b2c2c"],
                      mantle="shawl", mantle_fill=SHAWL, stripe=SHAWL_STRIPE, beard=True,
                      phylactery=True),
    "priest": dict(name="a priest", robes=["#f4f0e6"], edge="#b9ab8c", mantle="hood",
                   mantle_fill="#f4f0e6", band="#2f4f7f", beard=True),
    "man": dict(name="a man", robes=["#7a5a3a", "#5c6b4a", "#6e4a4a", "#4f5d70", "#8a7350"],
                mantle="hood", mantle_fill="#d8c9a6", band="#6b2c2c", beard=True),
    "woman": dict(name="a woman", robes=["#6e4a5a", "#4f5d70", "#7a5a3a", "#5c6b4a"],
                  mantle="veil", mantle_fill="#cdbf9e", beard=False),
    "disciple": dict(name="a disciple", robes=["#6b5a3e", "#4f5d70", "#5c6b4a", "#7a5a3a"],
                     mantle="stole", mantle_fill="#8d7650", hair="short", beard=True),
    "beggar": dict(name="the man born blind", robes=["#a68b62"], mantle=None, hair="short",
                   beard=True, ragged=True),
    "healed": dict(name="the healed man", robes=["#a68b62"], mantle="stole", mantle_fill="#c9b48a",
                   hair="short", beard=True),
    "soldier": dict(name="a soldier", robes=["#8b1e1e"], mantle="helmet", mantle_fill="#9a8f80",
                    beard=False, short=True),
    "child": dict(name="a child", robes=["#c9b48a", "#8a9a6a", "#b98a7a"], mantle=None,
                  hair="short", beard=False, child=True),
}

# --- poses ---------------------------------------------------------------------------------------
#
# (elbow, hand) for the near arm and the far arm, facing right. A pose is chosen by name in the
# comic file; add one here and every comic can use it.

POSES = {
    "stand":  {"near": ((10, -54), (10, -34)), "far": ((-10, -54), (-10, -34))},
    "point":  {"near": ((22, -72), (40, -76)), "far": ((-10, -54), (-10, -34))},
    "open":   {"near": ((22, -64), (36, -72)), "far": ((-20, -64), (-32, -72))},
    "praise": {"near": ((16, -96), (20, -118)), "far": ((-6, -96), (-4, -118))},
    "raise":  {"near": ((14, -96), (8, -120)), "far": ((16, -62), (28, -62))},
    "shout":  {"near": ((18, -94), (14, -114)), "far": ((22, -72), (40, -76))},
    "hold":   {"near": ((14, -56), (20, -44)), "far": ((-10, -54), (-10, -34))},
    "grope":  {"near": ((22, -66), (38, -64)), "far": ((18, -62), (34, -58))},
    "beg":    {"near": ((18, -58), (32, -56)), "far": ((-10, -54), (-10, -34))},
    "fold":   {"near": ((12, -60), (-4, -58)), "far": ((-12, -60), (6, -60))},
    "turn":   {"near": ((4, -56), (-14, -48)), "far": ((-14, -60), (-26, -52))},
    "heart":  {"near": ((14, -58), (4, -70)), "far": ((-10, -54), (-10, -34))},
}

# Where a figure's head sits, in its own units, by stance. The bubble tail aims here.
HEAD = {"stand": (2, -90), "walk": (2, -90), "kneel": (2, -66), "sit": (2, -70)}
SPEAKER_NAMES = {k: v["name"] for k, v in CAST.items()}


def _arm(shoulder, elbow, hand, fill, edge, skin):
    pts = f"M{shoulder[0]} {shoulder[1]} L{elbow[0]} {elbow[1]} L{hand[0]} {hand[1]}"
    return (f'<path d="{pts}" fill="none" stroke="{edge}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{pts}" fill="none" stroke="{fill}" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{hand[0]}" cy="{hand[1]}" r="4.3" fill="{skin}" stroke="{edge}" stroke-width="0.8"/>')


def _stone(x, y, r=6):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.8:.1f}" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="0.9"/>'
            f'<ellipse cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" rx="{r * 0.35:.1f}" ry="{r * 0.22:.1f}" fill="#c4bbad"/>')


def _prop(kind, hand):
    hx, hy = hand
    if kind == "stone":
        return _stone(hx + 2, hy - 6)
    if kind == "staff":
        return f'<path d="M{hx + 2} {hy - 44} L{hx + 6} 0" stroke="#6b4a2a" stroke-width="3.2" stroke-linecap="round"/>'
    if kind == "scroll":
        return (f'<rect x="{hx - 3}" y="{hy - 14}" width="16" height="12" fill="{CARD}" stroke="{WALL_EDGE}" stroke-width="0.9"/>'
                f'<rect x="{hx - 5}" y="{hy - 16}" width="4" height="16" rx="2" fill="#8d7650"/>'
                f'<rect x="{hx + 13}" y="{hy - 16}" width="4" height="16" rx="2" fill="#8d7650"/>')
    if kind == "spear":
        return (f'<path d="M{hx} {hy + 40} L{hx} {hy - 70}" stroke="#6b4a2a" stroke-width="3"/>'
                f'<path d="M{hx - 4} {hy - 68} L{hx} {hy - 84} L{hx + 4} {hy - 68} Z" fill="{STONE}" stroke="{STONE_EDGE}"/>')
    if kind == "lamp":
        return (f'<path d="M{hx - 8} {hy - 4} Q{hx} {hy + 4} {hx + 10} {hy - 4} Z" fill="#b5835a" stroke="#6b4a2a" stroke-width="0.8"/>'
                f'<path d="M{hx + 9} {hy - 5} q2 -8 -1 -12 q-1 6 -3 8 z" fill="{GOLD}"/>')
    return ""


def figure(who, x, y, s=1.0, face=1, pose="stand", stance="stand", holds=None, tone=0):
    """One cast member. (x, y) is the feet; face 1 looks right, -1 left; tone picks a robe."""
    c = CAST[who]
    robe = c["robes"][tone % len(c["robes"])]
    edge = c.get("edge", "#2a2016")
    skin = SKINS[(tone + len(who)) % len(SKINS)]
    p = POSES[pose]
    if c.get("child"):
        s *= 0.72
    kneel = stance == "kneel"
    up = 24 if kneel else 0
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face:.3f} {s:.3f})">']
    if c.get("glow"):
        g.append(f'<ellipse cx="0" cy="{-52 + up}" rx="46" ry="70" fill="url(#comic-glow)"/>')

    upper = [f'<g transform="translate(0 {up})">'] if up else []
    # Far arm and the far side of a mantle sit behind the body.
    if c.get("mantle") == "stole" and not kneel:
        upper.append(f'<path d="M-12 -76 Q-24 -44 -21 -8 L-13 -10 Q-14 -44 -6 -76 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>')
    upper.append(_arm((-5, -74), *p["far"], _shade(robe), edge, skin))
    if up:
        upper.append('</g>')
    g += upper

    # Feet and robe.
    if kneel:
        g.append(f'<ellipse cx="-14" cy="-1" rx="7" ry="3" fill="{SANDAL}"/>')
        g.append(f'<path d="M-13 -54 Q0 -59 13 -54 Q16 -30 14 -20 Q24 -16 26 -5 Q26 0 21 0 H-12 '
                 f'Q-19 -2 -17 -12 Q-16 -30 -13 -54 Z" fill="{robe}" stroke="{edge}" stroke-width="1"/>')
        g.append(f'<path d="M-6 -40 Q-4 -24 -8 -6 M6 -44 Q10 -30 8 -18" fill="none" stroke="{FOLD}" stroke-width="1.2"/>')
    else:
        spread = 12 if stance == "walk" else 7
        hem = 21 if stance == "walk" else 19
        if c.get("short"):
            g.append(f'<path d="M-6 -30 V-2 M7 -30 V-2" stroke="{skin}" stroke-width="5"/>')
        g.append(f'<ellipse cx="{-spread}" cy="0" rx="7" ry="3" fill="{SANDAL}"/>'
                 f'<ellipse cx="{spread + 2}" cy="0" rx="7" ry="3" fill="{SANDAL}"/>')
        bottom = -28 if c.get("short") else -2
        ragged = ""
        if c.get("ragged"):
            ragged = " ".join(f"L{-hem + i * hem / 4:.1f} {bottom + (3 if i % 2 else -2)}" for i in range(9))
        hemline = ragged if ragged else f"Q0 {bottom + 5} {hem} {bottom}"
        start = f"M-13 -78 Q-17 -40 {-hem} {bottom}"
        g.append(f'<path d="{start} {hemline} L{hem} {bottom} Q17 -40 13 -78 Q0 -83 -13 -78 Z" '
                 f'fill="{robe}" stroke="{edge}" stroke-width="1"/>')
        g.append(f'<path d="M-7 -60 Q-9 -30 -10 {bottom - 2} M4 -62 Q6 -30 5 {bottom} M12 -50 Q15 -30 15 {bottom - 2}" '
                 f'fill="none" stroke="{FOLD}" stroke-width="1.2"/>'
                 f'<path d="M-2 -66 Q-1 -36 -3 {bottom - 2}" fill="none" stroke="{LITE}" stroke-width="1.6"/>')
        if c.get("ragged"):
            g.append(f'<rect x="-11" y="-30" width="7" height="6" fill="{_shade(robe)}" transform="rotate(-8 -8 -27)"/>'
                     f'<rect x="6" y="-58" width="6" height="5" fill="{_shade(robe)}"/>')

    top = [f'<g transform="translate(0 {up})">'] if up else []
    # Belt.
    top.append(f'<path d="M-14 -48 Q0 -44 15 -48 L15 -43 Q0 -39 -15 -43 Z" fill="#00000035"/>')
    m = c.get("mantle")
    if m == "stole" and kneel:
        # Kneeling, the robe ends at the waist line, so the stole is cut to the torso.
        top.append(f'<path d="M-13 -78 Q-6 -81 -2 -80 L12 -50 L5 -46 Q0 -60 -13 -70 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>')
    elif m == "stole":
        top.append(f'<path d="M-13 -78 Q-6 -81 -2 -80 L19 -28 L12 -22 Q2 -44 -13 -70 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>'
                   f'<path d="M-6 -74 L12 -32" stroke="{FOLD}" stroke-width="1.2"/>')
    # Head.
    top.append(f'<rect x="-2" y="-82" width="7" height="6" fill="{skin}"/>')
    top.append(f'<circle cx="2" cy="-90" r="12" fill="{skin}" stroke="{edge}" stroke-width="0.8"/>')
    hair = HAIR_GREY if who == "authority" and tone % 3 == 2 else HAIR
    if c.get("hair") == "long":
        top.append(f'<path d="M-10 -94 Q-6 -105 6 -103 Q13 -101 14 -95 Q5 -97 -1 -93 Q-3 -84 -6 -72 '
                   f'Q-12 -72 -14 -76 Q-12 -84 -10 -94 Z" fill="{hair}"/>')
    elif c.get("hair") == "short":
        top.append(f'<path d="M-10 -93 Q-6 -105 6 -103 Q13 -101 14 -95 Q5 -97 -1 -93 Q-3 -86 -7 -82 '
                   f'Q-11 -86 -10 -93 Z" fill="{hair}"/>')
    if m == "shawl":
        top.append(f'<path d="M13 -99 Q2 -113 -12 -98 Q-17 -86 -16 -78 Q-23 -64 -22 -46 Q0 -42 19 -48 '
                   f'Q20 -66 14 -78 Q8 -84 9 -92 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.9"/>')
        for off in (0, 5):
            top.append(f'<path d="M-22 {-52 - off} Q0 {-48 - off} 19 {-54 - off}" fill="none" stroke="{c["stripe"]}" stroke-width="2"/>')
        for tx, ty in ((-21, -46), (18, -48)):
            top.append(f'<path d="M{tx - 2} {ty} v9 M{tx} {ty} v11 M{tx + 2} {ty} v9" stroke="{c["stripe"]}" stroke-width="1"/>')
        top.append(f'<path d="M-6 -104 Q-10 -90 -14 -70 M4 -86 Q0 -70 4 -52" fill="none" stroke="{FOLD}" stroke-width="1.1"/>')
    elif m == "hood":
        top.append(f'<path d="M13 -98 Q2 -112 -12 -98 Q-16 -86 -18 -70 L-8 -70 Q-4 -82 9 -92 Z" '
                   f'fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.9"/>'
                   f'<path d="M-11 -100 Q2 -108 13 -99" fill="none" stroke="{c["band"]}" stroke-width="3"/>')
    elif m == "veil":
        top.append(f'<path d="M13 -98 Q2 -113 -12 -98 Q-18 -80 -20 -40 Q-21 -16 -18 -6 L-12 -8 '
                   f'Q-12 -40 -6 -74 Q2 -84 9 -92 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.9"/>')
    elif m == "helmet":
        top.append(f'<path d="M-11 -92 Q-10 -106 3 -106 Q15 -105 15 -93 Z" fill="{c["mantle_fill"]}" stroke="{STONE_EDGE}" stroke-width="1"/>'
                   f'<path d="M-6 -106 Q2 -118 12 -106" fill="none" stroke="{RED}" stroke-width="4"/>'
                   f'<path d="M-11 -92 L-12 -80" stroke="{STONE_EDGE}" stroke-width="3"/>')
    if c.get("phylactery"):
        top.append(f'<rect x="7" y="-106" width="7" height="6" fill="#1f1810" transform="rotate(18 10 -103)"/>')
    if c.get("beard"):
        top.append(f'<path d="M7 -84 Q10 -81 14 -85 Q14 -77 9 -74 Q5 -75 5 -80 Z" fill="{hair}"/>')
    # Near arm, then whatever the hand holds.
    near_elbow, near_hand = p["near"]
    top.append(_arm((7, -74), near_elbow, near_hand, robe, edge, skin))
    if holds:
        top.append(_prop(holds, near_hand))
    if up:
        top.append('</g>')
    g += top
    g.append('</g>')
    hx, hy = HEAD.get(stance, HEAD["stand"])
    return "".join(g), (x + hx * s * face, y + hy * s, s)


def _shade(hexcol, k=0.82):
    r, g_, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return f"#{int(r * k):02x}{int(g_ * k):02x}{int(b * k):02x}"


# --- scenes --------------------------------------------------------------------------------------
#
# A scene draws a panel's background in panel coordinates (0, 0)-(w, h); the ground line is at
# GROUND_AT * h. Add a scene here and every comic can name it.

GROUND_AT = 0.86


def _sky(w, h, kind, gid):
    top, low = SKIES[kind]
    return [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{low}"/></linearGradient></defs>',
            f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>']


def _floor(w, h, fill=GROUND, near=GROUND_NEAR):
    gy = h * GROUND_AT
    return [f'<rect x="0" y="{gy - 26:.1f}" width="{w}" height="{h - gy + 26:.1f}" fill="{fill}"/>',
            f'<path d="M0 {gy + 4:.1f} Q{w / 2:.1f} {gy - 6:.1f} {w} {gy + 6:.1f} V{h} H0 Z" fill="{near}"/>']


def _paving(w, h):
    gy = h * GROUND_AT
    out = [f'<rect x="0" y="{gy - 26:.1f}" width="{w}" height="{h - gy + 26:.1f}" fill="#d7ccb2"/>']
    for i in range(1, 4):
        yy = gy - 26 + i * (h - gy + 26) / 4
        out.append(f'<path d="M0 {yy:.1f} H{w}" stroke="#b8aa8a" stroke-width="1"/>')
    for i in range(-6, 16):
        x0 = i * w / 10
        out.append(f'<path d="M{w / 2 + (x0 - w / 2) * 0.55:.1f} {gy - 26:.1f} L{x0:.1f} {h}" stroke="#c4b796" stroke-width="0.8"/>')
    return out


def _column(x, top, bottom, wd=18):
    return (f'<rect x="{x - wd / 2:.1f}" y="{top:.1f}" width="{wd}" height="{bottom - top:.1f}" fill="#e6dcc4" stroke="{WALL_EDGE}" stroke-width="1"/>'
            f'<path d="M{x - wd / 2 + 5:.1f} {top + 8:.1f} V{bottom - 8:.1f} M{x + wd / 2 - 5:.1f} {top + 8:.1f} V{bottom - 8:.1f}" stroke="#cbbd9c" stroke-width="1"/>'
            f'<rect x="{x - wd / 2 - 4:.1f}" y="{top:.1f}" width="{wd + 8}" height="7" fill="#e6dcc4" stroke="{WALL_EDGE}" stroke-width="1"/>'
            f'<rect x="{x - wd / 2 - 4:.1f}" y="{bottom - 7:.1f}" width="{wd + 8}" height="7" fill="#e6dcc4" stroke="{WALL_EDGE}" stroke-width="1"/>')


def scene_colonnade(w, h, sky, gid):
    """A covered portico: a row of columns under a roof beam, paving underfoot (John 10:23)."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    out.append(f'<rect x="0" y="{gy - 60:.1f}" width="{w}" height="40" fill="{WALL}" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    out += _paving(w, h)
    beam = h * 0.07
    out.append(f'<rect x="0" y="0" width="{w}" height="{beam + 16:.1f}" fill="#d9ccae"/>'
               f'<path d="M0 {beam + 16:.1f} H{w}" stroke="{WALL_EDGE}" stroke-width="1.5"/>'
               f'<path d="M0 {beam + 6:.1f} H{w}" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    n = max(3, int(w // 110) + 1)
    for i in range(n):
        out.append(_column(24 + i * (w - 48) / (n - 1), beam + 16, gy - 20))
    return out


def scene_temple(w, h, sky, gid):
    """Temple courts: Herodian ashlar with drafted margins, the sanctuary beyond."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    out.append(f'<rect x="{w * 0.55:.1f}" y="{h * 0.18:.1f}" width="{w * 0.3:.1f}" height="{gy - h * 0.18:.1f}" fill="#efe6cf" stroke="{WALL_EDGE}"/>'
               f'<rect x="{w * 0.65:.1f}" y="{h * 0.3:.1f}" width="{w * 0.1:.1f}" height="{h * 0.22:.1f}" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    top = gy - h * 0.34
    out.append(f'<rect x="0" y="{top:.1f}" width="{w}" height="{gy - top:.1f}" fill="{WALL}"/>')
    rows = 4
    for r in range(rows):
        yy = top + r * (gy - top) / rows
        off = 0 if r % 2 else 30
        for i in range(-1, int(w // 60) + 2):
            out.append(f'<rect x="{i * 60 + off + 3:.1f}" y="{yy + 3:.1f}" width="54" height="{(gy - top) / rows - 6:.1f}" '
                       f'fill="none" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    out += _paving(w, h)
    return out


def scene_synagogue(w, h, sky, gid):
    """A street with a synagogue, its door dark (John 9:22, 34)."""
    out = _sky(w, h, sky, gid)
    out += _floor(w, h)
    gy = h * GROUND_AT
    bx, bw, bt = w * 0.08, w * 0.42, h * 0.22
    out.append(f'<path d="M{bx:.1f} {gy - 20:.1f} V{bt + 30:.1f} L{bx + bw / 2:.1f} {bt:.1f} L{bx + bw:.1f} {bt + 30:.1f} V{gy - 20:.1f} Z" '
               f'fill="{WALL}" stroke="{WALL_EDGE}" stroke-width="1.2"/>')
    for i in range(4):
        cx = bx + bw * (0.14 + i * 0.24)
        out.append(f'<rect x="{cx - 4:.1f}" y="{bt + 36:.1f}" width="8" height="{gy - bt - 56:.1f}" fill="#fffdf7" stroke="{WALL_EDGE}" stroke-width="0.6"/>')
    dx = bx + bw / 2
    out.append(f'<path d="M{dx - 18:.1f} {gy - 20:.1f} V{gy - 70:.1f} Q{dx:.1f} {gy - 88:.1f} {dx + 18:.1f} {gy - 70:.1f} V{gy - 20:.1f} Z" fill="#3e3122"/>')
    return out


def scene_pool(w, h, sky, gid):
    """Steps down to a pool (Siloam, John 9:7)."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    out.append(f'<rect x="0" y="{gy - 26:.1f}" width="{w}" height="{h - gy + 26:.1f}" fill="{WALL}"/>')
    for i in range(4):
        yy = gy - 26 + i * 9
        out.append(f'<path d="M0 {yy:.1f} H{w}" stroke="{WALL_EDGE}" stroke-width="0.9"/>')
    out.append(f'<rect x="0" y="{gy + 10:.1f}" width="{w}" height="{h - gy:.1f}" fill="{WATER}"/>')
    for i in range(6):
        xx = (i + 0.5) * w / 6
        out.append(f'<path d="M{xx - 14:.1f} {gy + 22:.1f} q7 -4 14 0 t14 0" fill="none" stroke="#ffffff66" stroke-width="1.2"/>')
    return out


def scene_hills(w, h, sky, gid):
    """Open country: two ridges and a field."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    out.append(f'<path d="M0 {gy - 60:.1f} Q{w * 0.25:.1f} {gy - 110:.1f} {w * 0.5:.1f} {gy - 70:.1f} Q{w * 0.75:.1f} {gy - 40:.1f} {w} {gy - 90:.1f} V{h} H0 Z" fill="#c7b78f"/>')
    out += _floor(w, h)
    return out


def scene_plain(w, h, sky, gid):
    out = _sky(w, h, sky, gid)
    out += _floor(w, h)
    return out


def scene_room(w, h, sky, gid):
    """An interior: plastered wall, a lamp niche, beaten-earth floor."""
    gy = h * GROUND_AT
    out = [f'<rect width="{w}" height="{h}" fill="#e3d6b8"/>',
           f'<path d="M{w * 0.7:.1f} {h * 0.42:.1f} v-24 q14 -16 28 0 v24 z" fill="#c9b893" stroke="{WALL_EDGE}" stroke-width="0.8"/>',
           _prop("lamp", (w * 0.7 + 12, h * 0.42 - 2))]
    out.append(f'<rect x="0" y="{gy - 20:.1f}" width="{w}" height="{h - gy + 20:.1f}" fill="#bfa982"/>')
    return out


SCENES = {
    "colonnade": scene_colonnade,
    "temple": scene_temple,
    "synagogue": scene_synagogue,
    "pool": scene_pool,
    "hills": scene_hills,
    "plain": scene_plain,
    "room": scene_room,
}

# --- words ---------------------------------------------------------------------------------------

def wrap(s, chars):
    words, rows, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > chars and cur:
            rows.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    rows.append(cur)
    return rows


EM = 0.5  # Georgia averages about half an em per character in mixed-case prose.


def _chars(width, size):
    return max(8, int(width / (size * EM)))


def fit(s, width, size):
    """Wrap to the fewest lines that fit width, then even the lines out so none is left an orphan.

    Returns (rows, the width the longest row needs)."""
    n = len(wrap(s, _chars(width, size)))
    chars = max(len(w) for w in s.split())
    while len(wrap(s, chars)) > n:
        chars += 1
    rows = wrap(s, chars)
    return rows, max(len(r) for r in rows) * size * EM


def bubble(text_, x, y, w, target=None, style="speech", size=14.5):
    """A speech bubble centred on x with its top at y; its tail points at target (x, y).

    style: "speech" (rounded), "shout" (jagged, bold), "whisper" (dotted outline, for an aside).
    Returns (svg, height).
    """
    lh = size * 1.25
    rows, need = fit(text_, w - 28, size)
    w = min(w, need + 34)
    h = 18 + lh * len(rows)
    x0, x1, y1 = x - w / 2, x + w / 2, y + h
    out = []
    stroke = f'stroke="{INK}" stroke-width="1.8"'
    if style == "shout":
        out.append(_jagged(x0 - 4, y - 4, w + 8, h + 8, stroke))
    if target:
        tx, ty = target
        if ty > y1:
            bx = min(max(tx, x0 + 22), x1 - 22)
            base = ((bx - 9, y1 - 2), (bx + 9, y1 - 2))
        elif ty < y:
            bx = min(max(tx, x0 + 22), x1 - 22)
            base = ((bx - 9, y + 2), (bx + 9, y + 2))
        else:
            side = x1 - 2 if tx > x else x0 + 2
            base = ((side, y + h / 2 - 8), (side, y + h / 2 + 8))
        mx, my = (base[0][0] + base[1][0]) / 2, (base[0][1] + base[1][1]) / 2
        # Stop short of the head so the tail never covers it.
        d = math.hypot(tx - mx, ty - my) or 1
        reach = max(14, d - 22)
        px, py = mx + (tx - mx) * reach / d, my + (ty - my) * reach / d
        out.append(f'<path d="M{base[0][0]:.1f} {base[0][1]:.1f} L{px:.1f} {py:.1f} L{base[1][0]:.1f} {base[1][1]:.1f} Z" '
                   f'fill="{CARD}" {stroke} stroke-linejoin="round"/>')
    dash = ' stroke-dasharray="2 3"' if style == "whisper" else ""
    if style != "shout":
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="{CARD}" {stroke}{dash}/>')
    else:
        out.append(f'<rect x="{x0 + 2:.1f}" y="{y + 2:.1f}" width="{w - 4:.1f}" height="{h - 4:.1f}" fill="{CARD}"/>')
    if target:
        # Cover the tail's join with the outline.
        out.append(f'<path d="M{base[0][0]:.1f} {base[0][1]:.1f} L{base[1][0]:.1f} {base[1][1]:.1f}" stroke="{CARD}" stroke-width="3"/>')
    ty_ = y + 9 + lh * 0.8
    for r in rows:
        out.append(text(x, ty_, r, size, "middle", "bold" if style == "shout" else None))
        ty_ += lh
    return out, h


def _jagged(x, y, w, h, stroke, step=15, spike=7):
    pts, i = [], 0
    for (ax, ay, bx, by, nx, ny) in ((x, y, x + w, y, 0, -1), (x + w, y, x + w, y + h, 1, 0),
                                     (x + w, y + h, x, y + h, 0, 1), (x, y + h, x, y, -1, 0)):
        n = max(2, int(math.hypot(bx - ax, by - ay) // step))
        for k in range(n):
            t = k / n
            o = spike if i % 2 else 0
            pts.append(f"{ax + (bx - ax) * t + nx * o:.1f},{ay + (by - ay) * t + ny * o:.1f}")
            i += 1
    return f'<polygon points="{" ".join(pts)}" fill="{CARD}" {stroke} stroke-linejoin="round"/>'


def caption(text_, x, y, w, size=14):
    """A narrator's box: gold-tinted, square-cornered, italic. Returns (svg, height)."""
    lh = size * 1.25
    rows, _ = fit(text_, w - 20, size)
    h = 12 + lh * len(rows)
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{GOLD_TINT}" stroke="{INK}" stroke-width="1.4"/>']
    ty = y + 6 + lh * 0.8
    for r in rows:
        out.append(text(x + 10, ty, r, size, italic=True))
        ty += lh
    return out, h


# --- layouts -------------------------------------------------------------------------------------
#
# A layout is a list of rows, each [height, weight, weight, ...]: the row's height and the relative
# width of each panel in it. Name the story shape the layout serves, not its geometry, so an author
# picks by what the comic has to do.

LAYOUTS = {
    # Set the scene, two beats of exchange, the reveal across the foot.
    "setting-exchange-reveal": [[250, 1], [300, 1, 1], [300, 1]],
    # Scene, exchange, a flashback or piece of evidence, the verdict.
    "setting-exchange-evidence-verdict": [[300, 1], [300, 1, 1], [270, 1], [290, 1]],
    # Two scenes side by side, then what they mean together: a contrast.
    "contrast": [[320, 1, 1], [300, 1]],
    # Six equal beats: a sequence of events.
    "six-beats": [[270, 1, 1], [270, 1, 1], [270, 1, 1]],
    # Three wide panels: before, turn, after.
    "three-acts": [[280, 1], [280, 1], [280, 1]],
}

MARGIN, GUTTER = 30, 14


def panel_boxes(rows, top):
    boxes, y = [], top
    for row in rows:
        h, weights = row[0], row[1:]
        total = sum(weights)
        avail = W - 2 * MARGIN - GUTTER * (len(weights) - 1)
        x = MARGIN
        for wt in weights:
            pw = avail * wt / total
            boxes.append((x, y, pw, h))
            x += pw + GUTTER
        y += h + GUTTER
    return boxes, y - GUTTER


# --- assembly ------------------------------------------------------------------------------------

def _expand_cast(entries):
    """A cast entry with n > 1 is a crowd: spread from x to x2, poses cycled, robes varied."""
    out = []
    for e in entries:
        n = e.get("n", 1)
        if n == 1:
            out.append(e)
            continue
        poses = e.get("pose", "stand")
        poses = poses if isinstance(poses, list) else [poses]
        for i in range(n):
            m = dict(e)
            m["n"] = 1
            m["x"] = e["x"] + (e.get("x2", e["x"] + 0.3) - e["x"]) * i / (n - 1)
            m["pose"] = poses[i % len(poses)]
            m["tone"] = e.get("tone", 0) + i
            # Alternate depth so a crowd is not a row of cut-outs.
            m["dy"] = e.get("dy", 0) + (0 if i % 2 else 0.035)
            m["s"] = e.get("s", 1.0) * (1.0 if i % 2 else 0.94)
            m["id"] = e.get("id", e["who"]) if i == 0 else f'{e.get("id", e["who"])}{i + 1}'
            out.append(m)
    return out


def draw_panel(i, box, p):
    x, y, w, h = box
    cid = f"pane{i}"
    flash = p.get("flashback", False)
    out = [f'<defs><clipPath id="{cid}"><rect x="0" y="0" width="{w:.1f}" height="{h}" rx="{18 if flash else 4}"/></clipPath></defs>',
           f'<g transform="translate({x:.1f} {y:.1f})">', f'<g clip-path="url(#{cid})">']
    out += SCENES[p.get("scene", "plain")](w, h, p.get("sky", "day"), f"sky{i}")

    gy = h * GROUND_AT
    base = h / 300 * 1.3
    heads, drawn = {}, []
    for e in _expand_cast(p.get("cast", [])):
        fy = gy + 6 + (e.get("dy", 0)) * h
        fx = e["x"] * w
        svg, head = figure(e["who"], fx, fy, base * e.get("s", 1.0), -1 if e.get("face") == "left" else 1,
                           e.get("pose", "stand"), e.get("stance", "stand"), e.get("holds"), e.get("tone", 0))
        drawn.append((fy, svg))
        heads[e.get("id", e["who"])] = head
    for _, svg in sorted(drawn, key=lambda d: d[0]):
        out.append(svg)

    if flash:
        out.append(f'<rect width="{w:.1f}" height="{h}" fill="{SEPIA}" opacity="0.16"/>')

    cap_h = 0
    if p.get("caption"):
        c, cap_h = caption(p["caption"], 10, 10, min(w - 20, p.get("caption_w", w * 0.62)))
        out += c
    for b in p.get("say", []):
        hx, hy, hs = heads[b["by"]]
        bx = b.get("at", [0.5, 0.1])[0] * w
        by = b.get("at", [0.5, 0.1])[1] * h
        if cap_h and by < 10 + cap_h + 6 and bx - b.get("w", 200) / 2 < 10 + p.get("caption_w", w * 0.62):
            by = 10 + cap_h + 8
        bw = b.get("w", 200)
        _, bh = bubble(b["text"], bx, by, bw, None, b.get("style", "speech"))
        # A bubble over its own speaker's head hides who is talking: lift it clear.
        if by + bh > hy - 26 * hs and abs(bx - hx) < bw / 2 + 10:
            by = max(8, hy - 26 * hs - bh)
        cap_right = 10 + p.get("caption_w", w * 0.62)
        if cap_h and by < 10 + cap_h + 6 and bx - bw / 2 < cap_right:
            raise SystemExit(f"panel {i + 1}: bubble for {b['by']} cannot clear both its speaker and the "
                             f"caption; move it sideways (at), narrow it (w) or shorten the caption")
        svg, _ = bubble(b["text"], bx, by, bw, (hx, hy - 6 * hs), b.get("style", "speech"))
        out += svg

    ref = p.get("ref", "")
    if ref:
        tag = ref + (" · condensed" if any(b.get("source") == "condensed" for b in p.get("say", [])) else "")
        tw = len(tag) * 6.3 + 16
        out.append(f'<rect x="{w - tw - 6:.1f}" y="{h - 26:.1f}" width="{tw:.1f}" height="20" rx="3" fill="{PAPER}" opacity="0.92"/>')
        out.append(text(w - 14, h - 11.5, tag, 12, "end", fill=MUTED, italic=True))
    out.append('</g>')
    out.append(f'<rect x="0" y="0" width="{w:.1f}" height="{h}" rx="{18 if flash else 4}" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    if flash:
        out.append(f'<rect x="4" y="4" width="{w - 8:.1f}" height="{h - 8}" rx="15" fill="none" stroke="{SEPIA}" stroke-width="1"/>')
    out.append(text(12 if not p.get("caption") else w - 14, h - 11 if not p.get("caption") else 24, str(i + 1),
                    12, "start" if not p.get("caption") else "end", "bold", fill=MUTED))
    out.append('</g>')
    return out


def describe(comic):
    """The <desc>, and the alt text for the markdown embed: every panel, every word in it."""
    parts = [f'A one-minute comic in {len(comic["panel"])} panels.']
    for i, p in enumerate(comic["panel"]):
        names = {}
        for e in _expand_cast(p.get("cast", [])):
            names[e.get("id", e["who"])] = e.get("name", SPEAKER_NAMES[e["who"]])
        bits = [f'Panel {i + 1}' + (f' ({p["ref"]})' if p.get("ref") else "") +
                (", a flashback" if p.get("flashback") else "") + f': {p.get("shows", "")}'.rstrip(": ")]
        if p.get("caption"):
            bits.append(f'Caption: "{p["caption"]}"')
        for b in p.get("say", []):
            bits.append(f'{names[b["by"]][0].upper() + names[b["by"]][1:]} says: "{b["text"]}"')
        parts.append(" ".join(b if b.rstrip('"”’').endswith((".", "!", "?")) else b + "." for b in bits))
    if comic.get("point"):
        parts.append(f'The point: {comic["point"]}')
    return " ".join(parts)


def render(comic):
    layout = comic.get("layout", "setting-exchange-reveal")
    rows = LAYOUTS[layout] if isinstance(layout, str) else layout
    boxes, bottom = panel_boxes(rows, 108)
    if len(boxes) != len(comic["panel"]):
        raise SystemExit(f'{comic["slug"]}: layout has {len(boxes)} panels, file has {len(comic["panel"])}')

    point_rows = fit(comic.get("point", ""), 600, 16)[0] if comic.get("point") else []
    note = comic.get("note", "Each panel names its verses; “condensed” marks words shortened from the ESV.")
    h = int(bottom + 30 + (40 + 20 * len(point_rows) if point_rows else 0) + 56)

    out = svg_open(h, comic["title"], describe(comic))
    out.append(f'<defs><radialGradient id="comic-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{GLOW}" stop-opacity="0.9"/>'
               f'<stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient></defs>')
    out += heading(comic["title"], comic.get("subtitle", ""))
    for i, (box, p) in enumerate(zip(boxes, comic["panel"])):
        out += draw_panel(i, box, p)

    y = bottom + 30
    if point_rows:
        out += banner(W / 2, y, 160, "THE POINT", fill=RED)
        y += 52
        for r in point_rows:
            out.append(text(W / 2, y, r, 16, "middle", "bold"))
            y += 20
    out.append(text(W / 2, h - 40, note, 12, "middle", fill=MUTED, italic=True))
    out.append(credit(h))
    out.append('</svg>')
    return "\n".join(out)


def cast_sheet():
    """A model sheet: every cast member in every pose, for picking names when writing a comic."""
    poses = list(POSES)
    who = list(CAST)
    col, row = 52, 150
    h = 150 + row * len(who) + 60
    out = svg_open(h, "Comic cast", "Model sheet: every cast member of the one-minute comic in every pose.")
    out.append(f'<defs><radialGradient id="comic-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{GLOW}" stop-opacity="0.9"/>'
               f'<stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient></defs>')
    out += heading("The cast", "who = rows · pose = columns · utils/lib/comic.py")
    for j, pz in enumerate(poses):
        out.append(text(84 + j * col, 124, pz, 11, "middle", fill=MUTED))
    for i, wname in enumerate(who):
        y = 150 + row * i + 118
        out.append(text(24, y - 112, wname, 13, weight="bold"))
        for j, pz in enumerate(poses):
            hold = "stone" if pz in ("raise", "hold") else ("staff" if pz == "grope" else None)
            svg, _ = figure(wname, 84 + j * col, y, 0.9, 1, pz, "kneel" if pz == "praise" and wname == "healed" else "stand", hold)
            out.append(svg)
    out.append(credit(h))
    out.append('</svg>')
    return "\n".join(out)
