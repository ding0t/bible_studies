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

from lib.larkin import (W, INK, MUTED, PAPER, CARD, RED, GOLD, GOLD_EDGE, GOLD_TINT, text, svg_open, heading, banner,
                        cloud as larkin_cloud)

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
    "dawn": ("#8fa3c0", "#f2c99a"),
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
# a band), "helmet", or None. name is how the generated <desc> refers to the figure. beard: True is
# a short beard, "full" runs jaw to jaw past the chin. Most men wore one: the Law kept its edges
# (Leviticus 19:27), and shaving half of it was a public disgrace (2 Samuel 10:4-5). Jesus' is full,
# the beard the Servant gave to those who pulled it out (Isaiah 50:6).

CAST = {
    "jesus": dict(name="Jesus", robes=[JESUS_ROBE], edge=JESUS_EDGE, mantle="stole",
                  mantle_fill=JESUS_MANTLE, hair="long", beard="full", glow=True),
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
    "witness": dict(name="a witness", robes=["#4a4238", "#5a4c3c"], mantle=None, hair="short",
                    beard=True, coarse=True, belt="#2a2016"),
    "child": dict(name="a child", robes=["#c9b48a", "#8a9a6a", "#b98a7a"], mantle=None,
                  hair="short", beard=False, child=True),
}

# --- reserved figures ----------------------------------------------------------------------------
#
# A biblical figure is drawn the same way in every comic, so a reader who met Peter in one knows him
# in the next. Each is reserved here once: the study that introduces him, and in `why` the Scripture
# behind any detail of his dress (what Scripture does not give is a fixed choice, recorded so it is
# never re-decided). No generic role above wears a reserved figure's tunic colour, and no two
# reserved figures share one. Jesus is reserved by the entry above.

FIGURES = {
    "peter": dict(name="Peter", study="biblical-figures/peter.md", robes=["#2f5f6a"], mantle="stole",
                  mantle_fill="#a0522d", hair="short", hair_color="#4a4038", beard=True, build=1.12,
                  belt="#c9b48a",
                  why="A fisherman (Matthew 4:18): broad-built, a rope belt, a deep teal work tunic and a "
                      "sienna outer garment, the one he put on to throw himself into the sea (John 21:7)."),
    "andrew": dict(name="Andrew", study="biblical-figures/andrew.md", robes=["#7d6a3a"], mantle="stole",
                   mantle_fill="#8a8178", hair="short", beard=True, belt="#c9b48a",
                   why="Peter's brother, fishing from the same boat (Matthew 4:18): Peter's rope belt, "
                       "a mustard tunic and a grey cloak."),
    "pilate": dict(name="Pilate", study="last-things/two-witnesses.md", robes=["#b59a6a"], mantle="stole",
                   mantle_fill="#7a1f2b", hair="short", beard=False,
                   why="The Roman prefect (Luke 3:1): a red military cloak over a tan tunic, and clean-shaven "
                       "in the Roman manner of the day, so he reads apart from every bearded Judean round him."),
    "john": dict(name="John", study="christian-life/test-the-spirits.md", robes=["#2e4a7a"], mantle="stole",
                 mantle_fill="#e6dcc4", hair="short", beard=True, belt="#c9b48a",
                 why="A fisherman with his brother James (Matthew 4:21), so the fishermen's rope belt; a deep "
                     "blue tunic and a cream mantle are a fixed choice. Scripture gives no detail of his dress."),
    "paul": dict(name="Paul", study="christian-life/test-the-spirits.md", robes=["#8a4a2a"], mantle="stole",
                 mantle_fill="#3e3a36", hair="short", beard=True, belt="#5a3d22",
                 why="A travelling tentmaker (Acts 18:3): a rust tunic under a charcoal travelling cloak and a "
                     "leather belt, a fixed choice. Scripture gives no detail of his dress or looks."),
}
CAST.update(FIGURES)

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
    "look_up": {"near": ((18, -90), (30, -110)), "far": ((-10, -54), (-10, -34))},
    "turn":   {"near": ((4, -56), (-14, -48)), "far": ((-14, -60), (-26, -52))},
    "heart":  {"near": ((14, -58), (4, -70)), "far": ((-10, -54), (-10, -34))},
}

# Where a figure's head sits, in its own units, by stance. The bubble tail aims here.
HEAD = {"stand": (2, -90), "walk": (2, -90), "kneel": (2, -66), "sit": (2, -50), "lie": (-90, -14)}
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
    if kind == "jar":
        return prop_jar(hx, hy + 4, 0.9)
    if kind == "gift":
        return prop_gift(hx, hy + 4, 0.8)
    if kind == "loaf":
        return prop_loaf(hx, hy + 2, 1.0)
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
    sit = stance == "sit"
    up = {"kneel": 24, "sit": 40}.get(stance, 0)
    if stance == "lie":
        # Laid on the ground, head toward the side the figure faces (Revelation 11:8).
        g = [f'<g transform="translate({x:.1f} {y - 16 * s:.1f}) rotate({90 * face}) scale({s * c.get("build", 1):.3f} {s:.3f})">']
    else:
        g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s * face * c.get("build", 1):.3f} {s:.3f})">']
    if c.get("glow"):
        g.append(f'<ellipse cx="0" cy="{-52 + up}" rx="46" ry="70" fill="url(#comic-glow)"/>')

    upper = [f'<g transform="translate(0 {up})">'] if up else []
    # Far arm and the far side of a mantle sit behind the body.
    if c.get("mantle") == "stole" and not up:
        upper.append(f'<path d="M-12 -76 Q-24 -44 -21 -8 L-13 -10 Q-14 -44 -6 -76 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>')
    upper.append(_arm((-5, -74), *p["far"], _shade(robe), edge, skin))
    if up:
        upper.append('</g>')
    g += upper

    # Feet and robe.
    if sit:
        # Cross-legged on the ground: the robe spreads into a low mound around the knees.
        g.append(f'<path d="M-13 -38 Q0 -42 13 -38 Q15 -22 24 -10 Q28 -2 22 2 H-22 Q-28 -2 -24 -10 '
                 f'Q-15 -22 -13 -38 Z" fill="{robe}" stroke="{edge}" stroke-width="1"/>'
                 f'<path d="M-16 -8 Q0 -14 18 -8" fill="none" stroke="{FOLD}" stroke-width="1.2"/>')
    elif kneel:
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
        if c.get("coarse"):
            # Sackcloth: goat's hair, coarsely woven, the dress of mourning (Revelation 11:3).
            g.append('<path d="M-9 -74 V-6 M-3 -76 V-4 M3 -76 V-4 M9 -74 V-6 M14 -60 V-8" stroke="#00000040" '
                     'stroke-width="1" stroke-dasharray="2 2.5"/>'
                     '<path d="M-15 -62 H15 M-17 -36 H17 M-18 -16 H18" stroke="#ffffff22" stroke-width="1" stroke-dasharray="3 2"/>')
        if c.get("ragged"):
            g.append(f'<rect x="-11" y="-30" width="7" height="6" fill="{_shade(robe)}" transform="rotate(-8 -8 -27)"/>'
                     f'<rect x="6" y="-58" width="6" height="5" fill="{_shade(robe)}"/>')

    top = [f'<g transform="translate(0 {up})">'] if up else []
    # Belt.
    top.append(f'<path d="M-14 -48 Q0 -44 15 -48 L15 -43 Q0 -39 -15 -43 Z" fill="{c.get("belt", "#00000035")}"/>')
    m = c.get("mantle")
    if m == "stole" and up:
        # Kneeling, the robe ends at the waist line, so the stole is cut to the torso.
        top.append(f'<path d="M-13 -78 Q-6 -81 -2 -80 L12 -50 L5 -46 Q0 -60 -13 -70 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>')
    elif m == "stole":
        top.append(f'<path d="M-13 -78 Q-6 -81 -2 -80 L19 -28 L12 -22 Q2 -44 -13 -70 Z" fill="{c["mantle_fill"]}" stroke="{edge}" stroke-width="0.8"/>'
                   f'<path d="M-6 -74 L12 -32" stroke="{FOLD}" stroke-width="1.2"/>')
    # Head.
    top.append(f'<rect x="-2" y="-82" width="7" height="6" fill="{skin}"/>')
    top.append(f'<circle cx="2" cy="-90" r="12" fill="{skin}" stroke="{edge}" stroke-width="0.8"/>')
    hair = HAIR_GREY if who == "authority" and tone % 3 == 2 else c.get("hair_color", HAIR)
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
    if c.get("beard") == "full":
        # Jaw to jaw and past the chin, with a moustache; the face above it stays blank.
        top.append(f'<path d="M-3 -88 Q-5 -78 1 -72 Q7 -66 13 -69 Q17 -73 16 -86 Q14 -84 10 -85 '
                   f'Q5 -86 3 -83 Q1 -86 -3 -88 Z" fill="{hair}"/>'
                   f'<path d="M7 -86 Q11 -89 15.5 -86.5 Q15 -81 8 -82 Z" fill="{hair}"/>')
    elif c.get("beard"):
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


def scene_shore(w, h, sky, gid):
    """A lake shore: water to the far hills, a fishing boat drawn up, shingle underfoot (John 21)."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    hz = gy - 70
    out.append(f'<path d="M0 {hz - 14:.1f} Q{w * 0.3:.1f} {hz - 34:.1f} {w * 0.6:.1f} {hz - 16:.1f} Q{w * 0.85:.1f} {hz - 6:.1f} {w} {hz - 22:.1f} V{hz} H0 Z" fill="#9aa48a"/>')
    out.append(f'<rect x="0" y="{hz:.1f}" width="{w}" height="{gy - hz:.1f}" fill="{WATER}"/>')
    for i in range(7):
        xx, yy = (i + 0.5) * w / 7, hz + 14 + (i % 3) * 14
        out.append(f'<path d="M{xx - 16:.1f} {yy:.1f} q8 -4 16 0 t16 0" fill="none" stroke="#ffffff55" stroke-width="1.2"/>')
    bx, by = w * 0.84, gy - 22
    out.append(f'<path d="M{bx - 54:.1f} {by - 14:.1f} H{bx + 54:.1f} Q{bx + 46:.1f} {by + 6:.1f} {bx + 30:.1f} {by + 8:.1f} H{bx - 34:.1f} Q{bx - 50:.1f} {by + 4:.1f} {bx - 54:.1f} {by - 14:.1f} Z" '
               f'fill="#7a5a3a" stroke="#3e3122" stroke-width="1.2"/>'
               f'<path d="M{bx - 50:.1f} {by - 8:.1f} H{bx + 50:.1f}" stroke="#3e3122" stroke-width="0.8"/>'
               f'<path d="M{bx - 6:.1f} {by - 14:.1f} V{by - 90:.1f}" stroke="#3e3122" stroke-width="3"/>')
    out.append(f'<path d="M0 {gy - 16:.1f} Q{w / 2:.1f} {gy - 26:.1f} {w} {gy - 12:.1f} V{h} H0 Z" fill="#cdbb94"/>')
    for i in range(18):
        out.append(f'<ellipse cx="{(i * 37.3) % w:.1f}" cy="{gy + 4 + (i * 13) % (h - gy - 8):.1f}" rx="4" ry="2.4" fill="#b3a07a"/>')
    return out


def scene_courtyard(w, h, sky, gid):
    """A walled courtyard at night, a lit doorway in the wall (Matthew 26:69, 71)."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    top = gy - h * 0.42
    out.append(f'<rect x="0" y="{top:.1f}" width="{w}" height="{gy - top:.1f}" fill="#6e5c44"/>')
    for r in range(5):
        yy = top + r * (gy - top) / 5
        off = 0 if r % 2 else 24
        for i in range(-1, int(w // 48) + 2):
            out.append(f'<rect x="{i * 48 + off + 2:.1f}" y="{yy + 2:.1f}" width="44" height="{(gy - top) / 5 - 4:.1f}" fill="none" stroke="#5a4a36" stroke-width="0.8"/>')
    out.append(f'<rect x="0" y="{top - 6:.1f}" width="{w}" height="8" fill="#5a4a36"/>')
    dx = w * 0.14
    out.append(f'<path d="M{dx - 20:.1f} {gy - 20:.1f} V{gy - 84:.1f} Q{dx:.1f} {gy - 104:.1f} {dx + 20:.1f} {gy - 84:.1f} V{gy - 20:.1f} Z" fill="#e8b860" opacity="0.85"/>')
    out.append(f'<rect x="0" y="{gy - 26:.1f}" width="{w}" height="{h - gy + 26:.1f}" fill="#4e4234"/>')
    return out


def scene_street(w, h, sky, gid):
    """A city street: flat-roofed houses, doors and windows."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    x, i = 0.0, 0
    while x < w:
        bw, bh = 90 + (i * 37) % 50, 70 + (i * 53) % 60
        out.append(f'<rect x="{x:.1f}" y="{gy - 20 - bh:.1f}" width="{bw}" height="{bh}" fill="{WALL if i % 2 else "#e3d6b8"}" stroke="{WALL_EDGE}" stroke-width="1"/>'
                   f'<rect x="{x - 2:.1f}" y="{gy - 24 - bh:.1f}" width="{bw + 4}" height="6" fill="#bfa982" stroke="{WALL_EDGE}" stroke-width="0.8"/>'
                   f'<rect x="{x + bw * 0.6:.1f}" y="{gy - 20 - bh * 0.55:.1f}" width="14" height="{bh * 0.55:.1f}" fill="#5a4a36"/>'
                   f'<rect x="{x + bw * 0.2:.1f}" y="{gy - 20 - bh * 0.8:.1f}" width="10" height="10" fill="#5a4a36"/>')
        x += bw
        i += 1
    out += _floor(w, h)
    return out


GRASS = "#9db06a"
GRASS_NEAR = "#86a055"
DRY = "#d6bd8c"
DRY_NEAR = "#c9ab74"


def scene_grassland(w, h, sky, gid):
    """Spring on a Galilean hillside above the lake: much green grass (Mark 6:39; John 6:10)."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    hz = gy - h * 0.36
    out.append(f'<path d="M0 {hz - 10:.1f} Q{w * 0.4:.1f} {hz - 30:.1f} {w * 0.75:.1f} {hz - 12:.1f} Q{w * 0.9:.1f} {hz - 6:.1f} {w} {hz - 16:.1f} V{hz} H0 Z" fill="#8e9b86"/>')
    out.append(f'<rect x="0" y="{hz:.1f}" width="{w}" height="22" fill="{WATER}"/>')
    out.append(f'<path d="M0 {hz + 18:.1f} Q{w * 0.3:.1f} {hz + 4:.1f} {w * 0.6:.1f} {hz + 14:.1f} Q{w * 0.85:.1f} {hz + 22:.1f} {w} {hz + 10:.1f} V{h} H0 Z" fill="{GRASS}"/>')
    out.append(f'<path d="M0 {gy - 10:.1f} Q{w / 2:.1f} {gy - 22:.1f} {w} {gy - 6:.1f} V{h} H0 Z" fill="{GRASS_NEAR}"/>')
    for i in range(int(w // 16)):
        xx = i * 16 + (i * 7) % 11
        yy = hz + 30 + (i * 37) % int(h - hz - 34)
        out.append(f'<path d="M{xx:.1f} {yy:.1f} l-2 -6 M{xx + 2:.1f} {yy:.1f} l0 -8 M{xx + 4:.1f} {yy:.1f} l2 -6" stroke="#6f8a44" stroke-width="1.1"/>')
    return out


def scene_decapolis(w, h, sky, gid):
    """Dry hill country east of the lake, a Greek city on the far ridge (Mark 7:31): the crowd sat
    "on the ground" (Mark 8:6). The city is the region's name drawn: the Decapolis, ten Greek cities."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    ridge = gy - h * 0.34
    out.append(f'<path d="M0 {ridge + 10:.1f} Q{w * 0.25:.1f} {ridge - 14:.1f} {w * 0.55:.1f} {ridge - 4:.1f} Q{w * 0.8:.1f} {ridge + 6:.1f} {w} {ridge - 10:.1f} V{h} H0 Z" fill="#c7ad80"/>')
    cx, cy = w * 0.68, ridge - 4
    out.append(f'<rect x="{cx - 46:.1f}" y="{cy - 14:.1f}" width="92" height="14" fill="#e3d6b8" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    for k in range(6):
        out.append(f'<rect x="{cx - 22 + k * 8:.1f}" y="{cy - 34:.1f}" width="3" height="20" fill="#f1e9d6" stroke="{WALL_EDGE}" stroke-width="0.4"/>')
    out.append(f'<path d="M{cx - 26:.1f} {cy - 34:.1f} L{cx + 1:.1f} {cy - 46:.1f} L{cx + 28:.1f} {cy - 34:.1f} Z" fill="#e3d6b8" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    for k in range(5):
        out.append(f'<rect x="{cx - 44 + k * 20:.1f}" y="{cy - 22 - (k * 5) % 9:.1f}" width="12" height="{8 + (k * 5) % 9:.1f}" fill="#dccdae" stroke="{WALL_EDGE}" stroke-width="0.4"/>')
    out.append(f'<path d="M0 {gy - 18:.1f} Q{w * 0.5:.1f} {gy - 34:.1f} {w} {gy - 14:.1f} V{h} H0 Z" fill="{DRY}"/>')
    out.append(f'<path d="M0 {gy - 4:.1f} Q{w / 2:.1f} {gy - 14:.1f} {w} {gy:.1f} V{h} H0 Z" fill="{DRY_NEAR}"/>')
    for i in range(9):
        rx_, ry_ = (i * 71.3) % w, gy - 20 + (i * 29) % int(h - gy + 14)
        out.append(f'<ellipse cx="{rx_:.1f}" cy="{ry_:.1f}" rx="{5 + i % 3 * 2}" ry="3.5" fill="#a89070"/>')
    return out


def scene_hall(w, h, sky, gid):
    """Inside a synagogue: ashlar walls, a colonnade, stone benches along the wall (John 6:59)."""
    gy = h * GROUND_AT
    out = [f'<rect width="{w}" height="{h}" fill="#e3d6b8"/>']
    for r in range(6):
        yy = r * (gy - 30) / 6
        off = 0 if r % 2 else 30
        for i in range(-1, int(w // 60) + 2):
            out.append(f'<rect x="{i * 60 + off + 2:.1f}" y="{yy + 2:.1f}" width="56" height="{(gy - 30) / 6 - 4:.1f}" fill="none" stroke="#cbbd9c" stroke-width="0.8"/>')
    out.append(f'<rect x="0" y="{gy - 44:.1f}" width="{w}" height="14" fill="#cbbd9c" stroke="{WALL_EDGE}" stroke-width="0.8"/>')
    out.append(f'<rect x="0" y="{gy - 30:.1f}" width="{w}" height="{h - gy + 30:.1f}" fill="#bfa982"/>')
    n = max(3, int(w // 140) + 1)
    for i in range(n):
        out.append(_column(30 + i * (w - 60) / (n - 1), 10, gy - 30, 16))
    return out


def scene_lake(w, h, sky, gid):
    """Open water: the boat itself is the `hull` prop, drawn in front of whoever stands in it."""
    out = _sky(w, h, sky, gid)
    gy = h * GROUND_AT
    hz = gy - h * 0.38
    out.append(f'<path d="M0 {hz - 12:.1f} Q{w * 0.3:.1f} {hz - 30:.1f} {w * 0.6:.1f} {hz - 14:.1f} Q{w * 0.85:.1f} {hz - 4:.1f} {w} {hz - 18:.1f} V{hz} H0 Z" fill="#9aa48a"/>')
    out.append(f'<rect x="0" y="{hz:.1f}" width="{w}" height="{h - hz:.1f}" fill="{WATER}"/>')
    for i in range(int(w // 50)):
        xx, yy = i * 50 + 20, hz + 16 + (i * 23) % int(h - hz - 20)
        out.append(f'<path d="M{xx - 14:.1f} {yy:.1f} q7 -4 14 0 t14 0" fill="none" stroke="#ffffff55" stroke-width="1.2"/>')
    return out


# --- panel props ---------------------------------------------------------------------------------
#
# Things standing in a scene rather than held; (x, y) is where the prop meets the ground.

def prop_fire(x, y, s):
    """A charcoal fire: a ring of stones, glowing coals, low flames (John 18:18; 21:9)."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">',
           '<ellipse cx="0" cy="-20" rx="70" ry="60" fill="url(#comic-fire)"/>',
           '<ellipse cx="0" cy="-2" rx="22" ry="6" fill="#3e3122"/>']
    for k in range(7):
        a = math.pi * k / 6
        out.append(f'<ellipse cx="{-22 * math.cos(a):.1f}" cy="{-1 + 3 * math.sin(a):.1f}" rx="5" ry="4" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="0.8"/>')
    out.append('<path d="M-14 -4 Q-10 -26 -4 -14 Q0 -36 6 -16 Q12 -28 14 -4 Z" fill="#e8873a"/>'
               '<path d="M-8 -4 Q-4 -18 0 -10 Q4 -22 8 -4 Z" fill="#f6d36a"/>'
               '<ellipse cx="0" cy="-3" rx="16" ry="3" fill="#c0392b"/>')
    out.append('</g>')
    return "".join(out)


def prop_rooster(x, y, s):
    """A rooster standing, head up (Matthew 26:74)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-2 -2 L-4 -12 M4 -2 L4 -12" stroke="#c9a040" stroke-width="2"/>'
            '<path d="M-14 -24 Q-22 -34 -16 -46 Q-10 -36 -10 -30 Q-2 -14 12 -18 Q18 -22 16 -34 L20 -40 Q24 -42 24 -36 L26 -34 L22 -32 Q24 -22 18 -14 Q4 -6 -8 -12 Q-14 -16 -14 -24 Z" fill="#6b2c2c" stroke="#2a2016" stroke-width="1"/>'
            '<path d="M19 -41 q1 -6 4 -4 q2 -4 3 1" fill="#c0392b"/>'
            '<path d="M-16 -46 Q-26 -40 -22 -28 M-14 -42 Q-20 -30 -14 -24" fill="none" stroke="#2f4f3f" stroke-width="3"/>'
            '</g>')


def prop_kophinos(x, y, s):
    """A κόφινος: the small wicker basket a traveller carried his food in, full of broken pieces."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-7 -14 Q0 -26 7 -14" fill="none" stroke="#6b4a2a" stroke-width="1.6"/>'
            '<circle cx="-3" cy="-14" r="3" fill="#d9b679"/><circle cx="3" cy="-15" r="3.4" fill="#c9a060"/>'
            '<path d="M-8 -13 H8 L6 0 H-6 Z" fill="#b5895a" stroke="#6b4a2a" stroke-width="1"/>'
            '<path d="M-7 -8 H7 M-6.5 -4 H6.5" stroke="#8d6a3e" stroke-width="0.8"/>'
            '</g>')


def prop_spyris(x, y, s):
    """A σπυρίς: the large plaited hamper, big enough to lower a man down a wall in (Acts 9:25)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<circle cx="-7" cy="-26" r="5" fill="#d9b679"/><circle cx="1" cy="-28" r="5.5" fill="#c9a060"/>'
            '<circle cx="8" cy="-25" r="4.5" fill="#d9b679"/>'
            '<path d="M-14 -24 Q0 -28 14 -24 L12 0 Q0 3 -12 0 Z" fill="#a8824e" stroke="#5e4224" stroke-width="1.1"/>'
            '<path d="M-13 -17 Q0 -20 13 -17 M-12.5 -10 Q0 -13 12.5 -10 M-12 -4 Q0 -6 12 -4" fill="none" stroke="#7d5c32" stroke-width="0.9"/>'
            '<path d="M-6 -25 V1 M6 -25 V1" stroke="#7d5c32" stroke-width="0.7"/>'
            '</g>')


def prop_hull(x, y, s, span=200):
    """A fishing boat's hull from x across span, drawn in front: whoever stands at its line is in the
    boat, seen from the waist up."""
    x0, x1, t = x, x + span, 36 * s
    return (f'<path d="M{x0 - 10:.1f} {y - t:.1f} H{x1 + 18:.1f} Q{x1 + 4:.1f} {y - 4 * s:.1f} {x1 - 24:.1f} {y:.1f} H{x0 + 20:.1f} '
            f'Q{x0 - 4:.1f} {y - 6 * s:.1f} {x0 - 10:.1f} {y - t:.1f} Z" fill="#7a5a3a" stroke="#3e3122" stroke-width="1.4"/>'
            f'<path d="M{x0 - 6:.1f} {y - t * 0.66:.1f} H{x1 + 12:.1f} M{x0:.1f} {y - t * 0.33:.1f} H{x1 + 4:.1f}" stroke="#5a4028" stroke-width="1"/>'
            f'<rect x="{x0 - 10:.1f}" y="{y - t - 4 * s:.1f}" width="{span + 28:.1f}" height="{5 * s:.1f}" fill="#5a4028"/>')


def prop_loaf(x, y, s):
    """A round flat loaf, for a hand or a boat (Mark 8:14)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<ellipse cx="0" cy="-5" rx="9" ry="5" fill="#d9a85e" stroke="#8d6a3e" stroke-width="1"/>'
            '<path d="M-4 -7 L-1 -3 M2 -8 L5 -4" stroke="#8d6a3e" stroke-width="0.8"/></g>')


def prop_gift(x, y, s):
    """A wrapped present (Revelation 11:10)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<rect x="-8" y="-14" width="16" height="14" fill="#8b1e1e" stroke="#4a1010" stroke-width="0.9"/>'
            f'<path d="M0 -14 V0 M-8 -7 H8" stroke="{GOLD}" stroke-width="2"/>'
            f'<path d="M0 -14 q-7 -8 -7 -2 q0 3 7 2 q7 1 7 -2 q0 -6 -7 2" fill="none" stroke="{GOLD}" stroke-width="1.6"/></g>')


def prop_crosses(x, y, s):
    """Three crosses on a rise outside the city (Luke 23:33). The figures on them are not drawn."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">',
           '<path d="M-90 0 Q-40 -34 0 -38 Q40 -34 90 0 Z" fill="#a8946a"/>']
    for dx, hgt in ((-40, 70), (0, 92), (40, 70)):
        top = -30 - hgt
        out.append(f'<rect x="{dx - 2.5}" y="{top}" width="5" height="{hgt}" fill="#4a3826"/>'
                   f'<rect x="{dx - 16}" y="{top + 14}" width="32" height="5" fill="#4a3826"/>')
    out.append('</g>')
    return "".join(out)


def prop_tomb(x, y, s):
    """A tomb cut in the rock, open, its round stone rolled back (Mark 16:4)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-70 0 V-60 Q-60 -96 0 -98 Q60 -96 70 -60 V0 Z" fill="#b8a888" stroke="#7d6c4e" stroke-width="1.2"/>'
            '<path d="M-20 0 V-40 Q0 -58 20 -40 V0 Z" fill="#2a2016"/>'
            '<circle cx="46" cy="-24" r="24" fill="#a39274" stroke="#6e5f44" stroke-width="1.4"/>'
            '<circle cx="46" cy="-24" r="16" fill="none" stroke="#8a7a5e" stroke-width="1"/></g>')


def prop_tomb_sealed(x, y, s):
    """A tomb cut in the rock, the stone rolled against its entrance (Mark 15:46)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-70 0 V-60 Q-60 -96 0 -98 Q60 -96 70 -60 V0 Z" fill="#b8a888" stroke="#7d6c4e" stroke-width="1.2"/>'
            '<path d="M-20 0 V-40 Q0 -58 20 -40 V0 Z" fill="#2a2016"/>'
            '<circle cx="2" cy="-26" r="26" fill="#a39274" stroke="#6e5f44" stroke-width="1.4"/>'
            '<circle cx="2" cy="-26" r="18" fill="none" stroke="#8a7a5e" stroke-width="1"/></g>')


def prop_jar(x, y, s):
    """A small jar of spices or ointment (Mark 16:1; Luke 23:56)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-5 -16 H5 V-13 Q9 -10 9 -5 Q9 0 0 0 Q-9 0 -9 -5 Q-9 -10 -5 -13 Z" fill="#e8dcc0" stroke="#8d7650" stroke-width="0.9"/>'
            '<rect x="-4" y="-19" width="8" height="3" fill="#8d7650"/></g>')


def prop_cloud(x, y, s):
    """A cloud to be taken up in (Acts 1:9; Revelation 11:12); its flat base sits on y."""
    return "".join(larkin_cloud(x, y, 120 * s, fill="#fbf7ee", stroke="#c9c2b0"))


def prop_ruin(x, y, s):
    """A building breaking: a cracked wall leaning, blocks falling, the ground split (Revelation 11:13)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<g transform="rotate(9 0 0)"><rect x="-34" y="-96" width="60" height="96" fill="{WALL}" stroke="{WALL_EDGE}" stroke-width="1.2"/>'
            '<path d="M-4 -96 L4 -70 L-6 -48 L6 -22 L-2 0" fill="none" stroke="#3e3122" stroke-width="2"/>'
            '<rect x="-20" y="-80" width="10" height="12" fill="#5a4a36"/></g>'
            '<rect x="30" y="-120" width="14" height="10" fill="#cbbd9c" stroke="#8d7650" transform="rotate(24 37 -115)"/>'
            '<rect x="46" y="-84" width="12" height="9" fill="#cbbd9c" stroke="#8d7650" transform="rotate(-18 52 -80)"/>'
            '<rect x="38" y="-46" width="10" height="8" fill="#cbbd9c" stroke="#8d7650" transform="rotate(40 43 -42)"/>'
            '<path d="M-70 4 L-40 0 L-30 8 L-6 2 L10 10 L40 2 L70 8" fill="none" stroke="#3e3122" stroke-width="2.2"/></g>')


def prop_breath(x, y, s):
    """The breath of life from God entering a body: gold currents turning in on it (Revelation 11:11)."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})" fill="none" stroke="{GOLD}" stroke-width="2.4" stroke-linecap="round" opacity="0.9">']
    for k, (dx, dy) in enumerate(((-34, -110), (30, -96), (-30, -50), (34, -40))):
        sx = 1 if dx < 0 else -1
        out.append(f'<path d="M{dx} {dy} q{14 * sx} -10 {22 * sx} 4 q{6 * sx} 12 {-6 * sx} 14"/>')
    out.append('</g>')
    return "".join(out)


def flame_jet(x0, y0, x1, y1, s):
    """Fire from a mouth to a foe (Revelation 11:5): a tongue of flame that swells, then tapers."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    def tongue(width):
        left, right = [], []
        for k in range(13):
            t = k / 12
            wv = width * s * math.sin(math.pi * min(t * 1.15, 1)) ** 0.8 * (1.25 if k % 2 else 0.85)
            cx_, cy_ = x0 + dx * t, y0 + dy * t
            left.append(f"{cx_ + nx * wv:.1f},{cy_ + ny * wv:.1f}")
            right.append(f"{cx_ - nx * wv:.1f},{cy_ - ny * wv:.1f}")
        return " ".join(left + right[::-1])
    return (f'<polygon points="{tongue(11)}" fill="#e8873a" stroke="#a5421f" stroke-width="1" stroke-linejoin="round"/>'
            f'<polygon points="{tongue(5)}" fill="#f6d36a"/>')


def prop_sheep(x, y, s):
    """A sheep facing right, in its fleece (John 10:3-4, 27); a flock is a counted row of them."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M-12 -2 V-12 M-6 0 V-12 M8 -2 V-12 M14 0 V-12" stroke="#3b2f22" stroke-width="2.4" stroke-linecap="round"/>'
            '<path d="M-20 -14 q-4 -10 4 -14 q2 -8 10 -6 q6 -6 12 -1 q8 -3 11 4 q7 2 4 10 q2 7 -6 9 h-30 q-8 -1 -5 -2 z" '
            'fill="#f1ead8" stroke="#a89a7a" stroke-width="1"/>'
            '<ellipse cx="22" cy="-24" rx="6" ry="4.5" fill="#3b2f22" transform="rotate(25 22 -24)"/>'
            '<ellipse cx="18" cy="-27" rx="3" ry="1.6" fill="#3b2f22" transform="rotate(-30 18 -27)"/></g>')


PROPS = {"sheep": prop_sheep, "tomb_sealed": prop_tomb_sealed, "jar": prop_jar, "gift": prop_gift, "crosses": prop_crosses, "tomb": prop_tomb, "cloud": prop_cloud,
         "ruin": prop_ruin, "breath": prop_breath, "fire": prop_fire, "rooster": prop_rooster, "kophinos": prop_kophinos, "spyris": prop_spyris,
         "hull": prop_hull, "loaf": prop_loaf}


SCENES = {
    "grassland": scene_grassland,
    "decapolis": scene_decapolis,
    "hall": scene_hall,
    "lake": scene_lake,
    "shore": scene_shore,
    "courtyard": scene_courtyard,
    "street": scene_street,
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
    if not s.strip():
        return [], 0
    n = len(wrap(s, _chars(width, size)))
    chars = max(len(w) for w in s.split())
    while len(wrap(s, chars)) > n:
        chars += 1
    rows = wrap(s, chars)
    return rows, max(len(r) for r in rows) * size * EM


PIC_STEP = {"kophinos": 14, "spyris": 23, "loaf": 20, "gift": 22}
PIC_H = 36


def _picture_width(picture):
    return picture["n"] * PIC_STEP.get(picture["what"], 24) if picture else 0


def bubble(text_, x, y, w, target=None, style="speech", size=14.5, picture=None):
    """A speech bubble centred on x with its top at y; its tail points at target (x, y).

    style: "speech" (rounded), "shout" (jagged, bold), "whisper" (dotted outline, for an aside),
    "memory" (a cloud trailing small circles: what the speaker remembers), "voice" (gold, bold: a
    voice from heaven, whose tail points to the sky rather than a face). picture = {what, n} draws
    a counted row of props under the words, so a memory can show what it remembers.
    Returns (svg, height).
    """
    lh = size * 1.25
    rows, need = fit(text_, w - 28, size)
    w = max(min(w, need + 34), _picture_width(picture) + 30)
    h = 18 + lh * len(rows) + (PIC_H if picture else 0)
    x0, x1, y1 = x - w / 2, x + w / 2, y + h
    out = []
    stroke = f'stroke="{GOLD_EDGE if style == "voice" else INK}" stroke-width="{2.4 if style == "voice" else 1.8}"'
    bg = GOLD_TINT if style == "voice" else CARD
    if style == "shout":
        out.append(_jagged(x0 - 4, y - 4, w + 8, h + 8, stroke))
    if style == "memory":
        out += _cloud(x0, y, w, h, stroke)
        if target:
            tx, ty = target
            sx, sy = (x, y + h + 6) if ty > y + h else ((x0 - 4, y + h / 2) if tx < x else (x1 + 4, y + h / 2))
            for k, r in enumerate((5, 3.6, 2.4)):
                f = (k + 1) / 4
                out.append(f'<circle cx="{sx + (tx - sx) * f * 0.8:.1f}" cy="{sy + (ty - sy) * f * 0.8:.1f}" r="{r}" fill="{CARD}" {stroke}/>')
        target = None
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
                   f'fill="{bg}" {stroke} stroke-linejoin="round"/>')
    dash = ' stroke-dasharray="2 3"' if style == "whisper" else ""
    if style not in ("shout", "memory"):
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="{bg}" {stroke}{dash}/>')
    elif style == "memory":
        pass
    else:
        out.append(f'<rect x="{x0 + 2:.1f}" y="{y + 2:.1f}" width="{w - 4:.1f}" height="{h - 4:.1f}" fill="{CARD}"/>')
    if target:
        # Cover the tail's join with the outline.
        out.append(f'<path d="M{base[0][0]:.1f} {base[0][1]:.1f} L{base[1][0]:.1f} {base[1][1]:.1f}" stroke="{bg}" stroke-width="3"/>')
    ty_ = y + 9 + lh * 0.8
    for r in rows:
        out.append(text(x, ty_, r, size, "middle", "bold" if style in ("shout", "voice") else None,
                        italic=style == "memory"))
        ty_ += lh
    if picture:
        step = PIC_STEP.get(picture["what"], 24)
        px0 = x - step * (picture["n"] - 1) / 2
        for k in range(picture["n"]):
            out.append(PROPS[picture["what"]](px0 + k * step, y + h - 10, 0.8))
    return out, h


def _cloud(x, y, w, h, stroke):
    """A thought-cloud: scalloped puffs round the edge, then the body laid over their inner halves."""
    puffs = []
    nx, ny = max(3, int(w // 26)), max(2, int(h // 24))
    for k in range(nx + 1):
        for yy in (y, y + h):
            puffs.append((x + w * k / nx, yy))
    for k in range(1, ny):
        for xx in (x, x + w):
            puffs.append((xx, y + h * k / ny))
    out = [f'<circle cx="{px:.1f}" cy="{py:.1f}" r="13" fill="{CARD}" {stroke}/>' for px, py in puffs]
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{CARD}"/>')
    return out


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


def bubble_width(text_, w, style="speech", size=14.5, picture=None):
    """The width bubble() will actually draw: shrunk to the text, never wider than w (unless a
    picture needs the room), plus the spikes of a shout or the puffs of a memory."""
    core = max(min(w, fit(text_, w - 28, size)[1] + 34), _picture_width(picture) + 30)
    return core + {"shout": 8, "memory": 26}.get(style, 0)


def caption(text_, x, y, w, size=14, dashed=False):
    """A narrator's box: gold-tinted, square-cornered, italic. dashed=True is an aside that marks a
    reading or an inference, in the site's confidence code. Returns (svg, height)."""
    lh = size * 1.25
    rows, _ = fit(text_, w - 20, size)
    h = 12 + lh * len(rows)
    look = f'fill="{PAPER}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 4"' if dashed else \
        f'fill="{GOLD_TINT}" stroke="{INK}" stroke-width="1.4"'
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {look}/>']
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
    # A life: the call, two pairs of beats (high then low, fall then return), the mission it reached.
    "call-pairs-mission": [[280, 1], [330, 1, 1], [330, 1, 1], [300, 1]],
    # Two meals side by side, what was said about them, then the reckoning and a silent beat.
    "two-tables": [[380, 1, 1], [300, 1], [340, 3, 1]],
    # An echo: one story beside another, beat for beat, a narrow column and a wide one.
    "echo": [[260, 1, 2], [260, 1, 2], [260, 1, 2], [260, 1, 2]],
    # Days as columns, the night above the daylight, as the Hebrew day runs from sunset; a tally below.
    "day-by-day": [[260, 1, 1, 1], [260, 1, 1, 1], [110, 1]],
    # Three wide panels: before, turn, after.
    "three-acts": [[280, 1], [280, 1], [280, 1]],
}

MARGIN, GUTTER = 30, 14

# A layout fault stops the build; build_comics.py --draft sets this False to render anyway and list
# the faults, so the author can see what to move.
STRICT = True
PROBLEMS = []


def problem(msg):
    if STRICT:
        raise SystemExit(msg)
    PROBLEMS.append(msg)


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


def _sun(x, y, r, fill):
    rays = "".join(f'<path d="M{x + r * 1.25 * math.cos(a):.1f} {y + r * 1.25 * math.sin(a):.1f} '
                   f'L{x + r * 1.6 * math.cos(a):.1f} {y + r * 1.6 * math.sin(a):.1f}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>'
                   for a in [k * math.pi / 4 for k in range(8)])
    if fill == "part":
        body = (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PAPER}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>'
                f'<path d="M{x} {y - r} A{r} {r} 0 0 1 {x} {y + r} Z" fill="{GOLD}"/>')
    else:
        body = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>'
    return rays + body


def _moon(x, y, r, style):
    if style == "dashed":
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>'
                f'<text x="{x}" y="{y + 5}" font-size="14" text-anchor="middle" fill="{RED}" font-weight="bold">?</text>')
    fill = "#26304a" if style != "muted" else "#a9a3b8"
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'
            f'<circle cx="{x + r * 0.45:.1f}" cy="{y - r * 0.2:.1f}" r="{r * 0.85:.1f}" fill="{CARD}"/>')


def draw_tally(i, box, p):
    """A counting strip: suns and moons in order, sunsets between the days, one label under each.
    A mark with style "dashed" is one the count needs and the text does not give."""
    x, y, w, h = box
    marks = p["marks"]
    span = p.get("span", 0.64) * w
    out = [f'<g transform="translate({x:.1f} {y:.1f})">',
           f'<rect width="{w:.1f}" height="{h}" rx="4" fill="{CARD}" stroke="{INK}" stroke-width="2.6"/>']
    slots = [m for m in marks if not m.get("sunset")]
    step = span / len(slots)
    cx, cy = 14 + step / 2, h * 0.42
    for m in marks:
        if m.get("sunset"):
            sx = cx - step / 2
            out.append(f'<path d="M{sx:.1f} 14 V{h - 16:.1f}" stroke="{SEPIA}" stroke-width="1.4" stroke-dasharray="3 3"/>'
                       + text(sx, h - 6, "sunset", 10, "middle", fill=SEPIA, italic=True))
            continue
        if m["icon"] == "sun":
            out.append(_sun(cx, cy, 11, m.get("fill", "full")))
        else:
            out.append(_moon(cx, cy, 11, m.get("style", "")))
        col = RED if m.get("style") == "dashed" else (MUTED if m.get("style") == "muted" else INK)
        for k, line in enumerate(m.get("label", "").split("\n")):
            out.append(text(cx, cy + 30 + k * 13, line, 11.5, "middle", "bold" if k == 0 else None, fill=col))
        cx += step
    if p.get("caption"):
        tx = 14 + span + 14
        rows, _ = fit(p["caption"], w - tx - 14, 13.5)
        ty = h / 2 - (len(rows) - 1) * 8.5 + 4
        for r in rows:
            out.append(text(tx, ty, r, 13.5, weight="bold"))
            ty += 17
    if p.get("ref"):
        out.append(text(w - 12, h - 8, p["ref"], 11, "end", fill=MUTED, italic=True))
    out.append('</g>')
    return out


def draw_panel(i, box, p):
    if p.get("kind") == "tally":
        return draw_tally(i, box, p)
    x, y, w, h = box
    cid = f"pane{i}"
    flash = p.get("flashback", False)
    out = [f'<defs><clipPath id="{cid}"><rect x="0" y="0" width="{w:.1f}" height="{h}" rx="{18 if flash else 4}"/></clipPath></defs>',
           f'<g transform="translate({x:.1f} {y:.1f})">', f'<g clip-path="url(#{cid})">']
    out += SCENES[p.get("scene", "plain")](w, h, p.get("sky", "day"), f"sky{i}")

    gy = h * GROUND_AT
    base = h / 300 * 1.3
    heads, faces, drawn, tags, front = {}, {}, [], [], []
    for pr in p.get("props", []):
        py = pr.get("y", (gy + 6) / h) * h
        ps = base * pr.get("s", 1.0)
        if pr["what"] == "hull":
            svg = prop_hull(pr["x"] * w, py, ps, (pr["x2"] - pr["x"]) * w)
        else:
            # n > 1 spreads a counted row from x to x2: twelve baskets are drawn as twelve.
            n = pr.get("n", 1)
            xs = [pr["x"] + (pr.get("x2", pr["x"]) - pr["x"]) * k / max(1, n - 1) for k in range(n)]
            svg = "".join(PROPS[pr["what"]](xx * w, py, ps) for xx in xs)
            if pr.get("face") == "left":
                svg = "".join(f'<g transform="matrix(-1 0 0 1 {2 * xx * w:.1f} 0)">{PROPS[pr["what"]](xx * w, py, ps)}</g>' for xx in xs)
        (front if pr.get("front") else drawn).append((py - 0.5, svg))
    for e in _expand_cast(p.get("cast", [])):
        fy = gy + 6 + (e.get("dy", 0)) * h
        fx = e["x"] * w
        svg, head = figure(e["who"], fx, fy, base * e.get("s", 1.0), -1 if e.get("face") == "left" else 1,
                           e.get("pose", "stand"), e.get("stance", "stand"), e.get("holds"), e.get("tone", 0))
        drawn.append((fy, svg))
        heads[e.get("id", e["who"])] = head
        faces[e.get("id", e["who"])] = -1 if e.get("face") == "left" else 1
        if e.get("in_cloud"):
            # Taken up in a cloud (Acts 1:9; Revelation 11:12): the cloud's top meets the waist, so the
            # figure shows from the waist up whatever its scale.
            fs = base * e.get("s", 1.0)
            cw = 150 * fs
            r = cw / (max(3, int(cw // 34)) * 1.55)
            front.append((fy, "".join(larkin_cloud(fx, fy - 42 * fs + 2.5 * r, cw, fill="#fbf7ee", stroke="#c9c2b0"))))
        if e.get("tag"):
            tags.append(text(fx, fy + 17, e["tag"].upper(), 11.5, "middle", "bold", spacing="1.2",
                             extra=f'stroke="{PAPER}" stroke-width="3.5" paint-order="stroke"'))
    for _, svg in sorted(drawn, key=lambda d: d[0]):
        out.append(svg)
    out += [svg for _, svg in front]
    out += tags

    if flash:
        out.append(f'<rect width="{w:.1f}" height="{h}" fill="{SEPIA}" opacity="0.16"/>')

    cap_h = 0
    if p.get("caption"):
        room = w - (20 if p.get("_no_number") else 44)
        c, cap_h = caption(p["caption"], 10, 10, min(room, p.get("caption_w", w * 0.62)))
        out += c
    if p.get("aside"):
        # The aside hangs under the caption, so bubbles keep clear of both as one block.
        aw = min(w - 44, p.get("aside_w", w * 0.5))
        a, ah = caption(p["aside"], 10, 10 + cap_h + (4 if cap_h else 0), aw, 12.5, dashed=True)
        out += a
        cap_h += ah + (4 if cap_h else 0)
        p = dict(p, caption_w=max(p.get("caption_w", w * 0.62) if p.get("caption") else 0, aw))
    cap_right = 10 + min(w - (20 if p.get("_no_number") else 44), p.get("caption_w", w * 0.62)) if cap_h else -1
    cap_bottom = 10 + cap_h + 8 if cap_h else 8
    placed = []
    for b in p.get("say", []):
        style = b.get("style", "speech")
        if style == "fire":
            # Revelation 11:5: what comes from the witnesses' mouth is fire, so the jet is their bubble.
            sx, sy, ss = heads[b["by"]]
            if "to" in b:
                tx, ty, ts = heads[b["to"]]
                ty += 30 * ts
            else:
                tx, ty = b["at"][0] * w, b["at"][1] * h
            out.append(flame_jet(sx + 12 * ss * faces[b["by"]], sy + 4 * ss, tx, ty, ss))
            continue
        offstage = "from" in b
        # A voice with no figure in the panel (heaven, an angel) aims its tail at a place instead.
        hx, hy, hs = (b["from"][0] * w, b["from"][1] * h, base) if offstage else heads[b["by"]]
        bw = b.get("w", 200)
        pic = b.get("picture")
        _, bh = bubble(b["text"], 0, 0, bw, None, style, picture=pic)
        bh += 26 if style == "memory" else 0
        bw = bubble_width(b["text"], bw, style, picture=pic)
        bx, by = b.get("at", [0.5, 0.1])[0] * w, b.get("at", [0.5, 0.1])[1] * h
        top_limit = lambda x_: cap_bottom if x_ - bw / 2 < cap_right else 8
        by = max(by, top_limit(bx))
        clear = hy - 26 * hs
        # A bubble over its own speaker's head hides who is talking: lift it clear, and if the
        # caption or the panel's top is in the way, set it beside the head, toward the panel's centre.
        if not offstage and by + bh > clear and abs(bx - hx) < bw / 2 + 10:
            by = clear - bh
            if by < top_limit(bx):
                side = 1 if hx < w / 2 else -1
                bx = hx + side * (bw / 2 + 30 * hs)
                by = max(top_limit(bx), hy - bh / 2 - 14 * hs)
        where = f"panel {i + 1}: bubble for {b['by']}"
        if bx - bw / 2 < 4 or bx + bw / 2 > w - 4:
            problem(f"{where} runs past the panel edge; narrow it (w) or move its speaker")
        for (ox, oy, ow, oh) in placed:
            if abs(bx - ox) < (bw + ow) / 2 + 4 and by < oy + oh + 4 and oy < by + bh + 4:
                problem(f"{where} overlaps another bubble; move one (at) or narrow it (w)")
        placed.append((bx, by, bw, bh))
        inset = 13 if style == "memory" else 0
        svg, _ = bubble(b["text"], bx, by + inset, bw - 2 * inset, (hx, hy - 6 * hs), style, picture=pic)
        out += svg

    badge_right = 0
    if p.get("badge"):
        # A count on the panel, in the panel's own terms: "NIGHT 1", "DAY 2 · ALL".
        b = p["badge"]
        tone = b.get("tone", "day")
        fill, ink, extra = {"night": ("#26304a", PAPER, ""), "day": (GOLD, INK, ""),
                            "muted": (PAPER, MUTED, ' stroke-dasharray="4 3"')}[tone]
        bw_ = len(b["text"]) * 7.4 + 18
        out.append(f'<rect x="8" y="{h - 30:.1f}" width="{bw_:.1f}" height="22" rx="11" fill="{fill}" stroke="{INK}" stroke-width="1.2"{extra}/>')
        out.append(text(8 + bw_ / 2, h - 14.5, b["text"].upper(), 11.5, "middle", "bold", fill=ink, spacing="1"))
        badge_right = 8 + bw_
    ref = p.get("ref", "")
    if ref:
        tag = ref + (" · condensed" if any(b.get("source") == "condensed" for b in p.get("say", [])) else "")
        tw = len(tag) * 6.3 + 16
        lift = 24 if badge_right and w - tw - 6 < badge_right + 6 else 0
        out.append(f'<rect x="{w - tw - 6:.1f}" y="{h - 26 - lift:.1f}" width="{tw:.1f}" height="20" rx="3" fill="{PAPER}" opacity="0.92"/>')
        out.append(text(w - 14, h - 11.5 - lift, tag, 12, "end", fill=MUTED, italic=True))
    out.append('</g>')
    out.append(f'<rect x="0" y="0" width="{w:.1f}" height="{h}" rx="{18 if flash else 4}" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    if flash:
        out.append(f'<rect x="4" y="4" width="{w - 8:.1f}" height="{h - 8}" rx="15" fill="none" stroke="{SEPIA}" stroke-width="1"/>')
    if not p.get("_no_number"):
        out.append(text(12 if not p.get("caption") else w - 14, h - 11 if not p.get("caption") else 24, str(i + 1),
                        12, "start" if not p.get("caption") else "end", "bold", fill=MUTED))
    out.append('</g>')
    return out


def describe(comic):
    """The <desc>, and the alt text for the markdown embed: every panel, every word in it."""
    parts = [f'A one-minute comic in {len(comic["panel"])} panels.']
    if comic.get("headers"):
        hs = comic["headers"]
        names = ", ".join(hs[:-1]) + " and " + hs[-1] if len(hs) > 1 else hs[0]
        parts.append(f"{['', 'One column', 'Two columns', 'Three columns', 'Four columns'][len(hs)]} side by side: {names}, row for row.")
    for i, p in enumerate(comic["panel"]):
        names = {}
        for e in _expand_cast(p.get("cast", [])):
            names[e.get("id", e["who"])] = e.get("name", SPEAKER_NAMES[e["who"]])
        bits = [f'Panel {i + 1}' + (f' ({p["ref"]})' if p.get("ref") else "") +
                (", a flashback" if p.get("flashback") else "") + f': {p.get("shows", "")}'.rstrip(": ")]
        if p.get("caption"):
            bits.append(f'Caption: "{p["caption"]}"')
        for b in p.get("say", []):
            who = b.get("name") or names.get(b["by"], b["by"])
            who = who[0].upper() + who[1:]
            if b.get("style") == "fire":
                bits.append(f'Fire pours from the mouth of {who[0].lower() + who[1:]} toward {names.get(b.get("to"), "a foe")}')
            elif not b.get("text") and b.get("picture"):
                bits.append(f'{who}: a speech bubble with no words, holding {b["picture"]["n"]} {b["picture"].get("label", b["picture"]["what"])}')
            else:
                bits.append(f'{who} says: "{b["text"]}"')
        if p.get("aside"):
            bits.append(f'Note: "{p["aside"]}"')
        if p.get("badge"):
            bits.append(f'Counted: {p["badge"]["text"]}')
        if p.get("kind") == "tally":
            bits.append("The count: " + ", ".join(m["label"].replace("\n", " ") for m in p["marks"] if not m.get("sunset")))
            if p.get("caption"):
                bits[-1] += f'. "{p["caption"]}"' 
        parts.append(" ".join(b if b.rstrip('"”’').endswith((".", "!", "?")) else b + "." for b in bits))
    if comic.get("point"):
        parts.append(f'The point: {comic["point"]}')
    return " ".join(parts)


DEFS = (f'<defs><radialGradient id="comic-glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{GLOW}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="comic-fire" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#f6b04a" stop-opacity="0.75"/>'
        '<stop offset="1" stop-color="#f6b04a" stop-opacity="0"/></radialGradient></defs>')


def credit(h):
    return text(W - 24, h - 22, "A one-minute comic · the-way.lewy.au", 11, "end", fill=MUTED, italic=True)


def render(comic):
    layout = comic.get("layout", "setting-exchange-reveal")
    rows = LAYOUTS[layout] if isinstance(layout, str) else layout
    headers = comic.get("headers", [])
    subheaders = comic.get("subheaders", [])
    boxes, bottom = panel_boxes(rows, 108 + (40 if headers else 0) + (16 if subheaders else 0))
    if len(boxes) != len(comic["panel"]):
        raise SystemExit(f'{comic["slug"]}: layout has {len(boxes)} panels, file has {len(comic["panel"])}')

    point_rows = fit(comic.get("point", ""), 600, 16)[0] if comic.get("point") else []
    note = comic.get("note", "Each panel names its verses; “condensed” marks words shortened from the ESV.")
    h = int(bottom + 30 + (40 + 20 * len(point_rows) if point_rows else 0) + 56)

    out = svg_open(h, comic["title"], describe(comic))
    out.append(DEFS)
    out += heading(comic["title"], comic.get("subtitle", ""))
    # Column headers name what each column of panels is, when the columns run in parallel.
    for (bx, by_, bw_, _), label in zip(boxes, headers):
        out += banner(bx + bw_ / 2, by_ - 34 - (16 if subheaders else 0), min(bw_ - 40, len(label) * 9 + 20), label.upper(),
                      fill=SEPIA if label == headers[0] and comic.get("first_column_past") else INK, size=12)
    for (bx, by_, bw_, _), sub in zip(boxes, subheaders):
        out.append(text(bx + bw_ / 2, by_ - 6, sub, 11.5, "middle", fill=MUTED, italic=True))
    for i, (box, p) in enumerate(zip(boxes, comic["panel"])):
        # numbers = false: the columns or headers already give the reading order.
        out += draw_panel(i, box, dict(p, _no_number=not comic.get("numbers", True)))

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
    out.append(DEFS)
    out += heading("The cast", "who = rows · pose = columns · utils/lib/comic.py")
    for j, pz in enumerate(poses):
        out.append(text(84 + j * col, 124, pz, 11, "middle", fill=MUTED))
    for i, wname in enumerate(who):
        y = 150 + row * i + 118
        label = f'{wname} — reserved: {CAST[wname]["name"]}' if wname in FIGURES else wname
        out.append(text(24, y - 112, label, 13, weight="bold"))
        for j, pz in enumerate(poses):
            hold = "stone" if pz in ("raise", "hold") else ("staff" if pz == "grope" else None)
            svg, _ = figure(wname, 84 + j * col, y, 0.9, 1, pz, "kneel" if pz == "praise" and wname == "healed" else "stand", hold)
            out.append(svg)
    out.append(credit(h))
    out.append('</svg>')
    return "\n".join(out)
