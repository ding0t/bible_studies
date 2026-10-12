"""Draw the plates for jesus/you-are-gods.md.

    python3 utils/build_you_are_gods_graphics.py

two-courts is a relationship diagram. Above, Psalm 82's court and the court at Dedication stand
side by side, rung for rung: each charge God brings against the judges of the psalm, beside what
John records of the men Jesus quoted it to. Below, the test Jesus set in John 10: their works and
His on one balance. Every card is Scripture's own wording (ESV). Solid rungs are parallels between
Psalm 82 and the authorities John records; the dashed rung joins Psalm 82:8 to John 5:22, a link
John does not make in this scene.

the-path is an imagery plate set on a road. The authorities walk it from the seat God gave them,
through the works they did, to the judgment those works bring. Behind the road, John 9 is drawn as
one continuous scene: the man born blind washes at Siloam, comes back seeing, is cast out of the
synagogue, and is found by Jesus and worships Him. The road runs on into darkness (Psalm 82:5) and
ends at the scales of judgment (Psalm 82:7-8). Gold is Jesus' work; red is theirs.
"""

import math
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, text, svg_open, heading, banner, arrow_head, credit)

OUT = Path(__file__).resolve().parent.parent / "docs" / "content" / "assets" / "img" / "you-are-gods"

LINE = 17
L_PAN, R_PAN = 190, 530
STONE = "#9a8f80"
STONE_EDGE = "#6e6455"


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


def quote_card(x, y, w, quote, ref, fill, stroke, chars):
    rows = wrap(quote, chars)
    h = 12 + LINE * len(rows) + LINE
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>']
    ty = y + 6 + LINE * 0.85
    for r in rows:
        out.append(text(x + 10, ty, r, 13.5, italic=True))
        ty += LINE
    out.append(text(x + w - 10, ty, ref, 12, "end", fill=MUTED))
    return out, h


def stones(x, y):
    """Three stones in a heap, for John 10:31."""
    out = []
    for dx, dy, rx, ry in [(0, 0, 9, 6), (14, 1, 8, 5.5), (7, -8, 7.5, 5)]:
        out.append(f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="{rx}" ry="{ry}" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1"/>')
    return out


def two_courts():
    rungs = [
        ("GIVEN GOD’S WORD",
         "“I said, ‘You are gods, sons of the Most High, all of you’”", "Psalm 82:6",
         "“he called them gods to whom the word of God came” — written “in your Law”", "John 10:34-35", False),
        ("JUDGING UNJUSTLY",
         "“How long will you judge unjustly and show partiality to the wicked?”", "Psalm 82:2",
         "“Do not judge by appearances, but judge with right judgment”", "John 7:24", False),
        ("THE WEAK ABANDONED",
         "“Give justice to the weak and the fatherless”", "Psalm 82:3",
         "The man born blind, given his sight, is cast out; Jesus goes and finds him", "John 9:34-35", False),
        ("WALKING IN DARKNESS",
         "“They have neither knowledge nor understanding, they walk about in darkness”", "Psalm 82:5",
         "“Are you the teacher of Israel and yet you do not understand these things?”", "John 3:10", False),
        ("THE SENTENCE",
         "“nevertheless, like men you shall die, and fall like any prince”", "Psalm 82:7",
         "“now that you say, ‘We see,’ your guilt remains”", "John 9:41", False),
        ("THE JUDGE",
         "“Arise, O God, judge the earth”", "Psalm 82:8",
         "“the Father judges no one, but has given all judgment to the Son”", "John 5:22", True),
    ]

    lx, rx, cw = 30, 420, 270
    mid = W / 2
    y0 = 176
    body = []
    y = y0 + 64
    for i, (label, lq, lr, rq, rr, dashed) in enumerate(rungs):
        lc, lh = quote_card(lx, y, cw, lq, lr, GOLD_TINT, GOLD_EDGE, 36)
        rc, rh = quote_card(rx, y, cw, rq, rr, BLUE_TINT, BLUE, 36)
        h = max(lh, rh)
        lc, _ = quote_card(lx, y + (h - lh) / 2, cw, lq, lr, GOLD_TINT, GOLD_EDGE, 36)
        rc, _ = quote_card(rx, y + (h - rh) / 2, cw, rq, rr, BLUE_TINT, BLUE, 36)
        body += lc + rc
        cy = y + h / 2
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        body.append(f'<path d="M{lx + cw} {cy} H{rx}" stroke="{INK}" stroke-width="1.6"{dash}/>')
        body.append(f'<circle cx="{mid}" cy="{cy}" r="15" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"{dash}/>')
        body.append(text(mid, cy + 5, str(i + 1), 15, "middle", "bold"))
        body.append(text(mid, y - 6, label, 11, "middle", "bold", fill=RED, spacing="1"))
        y += h + 30
    rungs_end = y - 30

    h = rungs_end + 800
    out = svg_open(
        h,
        "Two courts: Psalm 82 and John 10",
        "A relationship diagram in two parts. Above, two columns: Psalm 82, God's court, on the left, "
        "and the court at the Feast of Dedication in John on the right, joined by six numbered rungs. "
        "1, given God's word: 'I said, You are gods, sons of the Most High, all of you' (Psalm 82:6) "
        "beside 'he called them gods to whom the word of God came', written 'in your Law' (John "
        "10:34-35). 2, judging unjustly: 'How long will you judge unjustly and show partiality to the "
        "wicked?' (Psalm 82:2) beside 'Do not judge by appearances, but judge with right judgment' "
        "(John 7:24). 3, the weak abandoned: 'Give justice to the weak and the fatherless' (Psalm "
        "82:3) beside the man born blind, given his sight, cast out, and Jesus going to find him (John "
        "9:34-35). 4, walking in darkness: 'They have neither knowledge nor understanding, they walk "
        "about in darkness' (Psalm 82:5) beside 'Are you the teacher of Israel and yet you do not "
        "understand these things?' (John 3:10). 5, the sentence: 'nevertheless, like men you shall "
        "die, and fall like any prince' (Psalm 82:7) beside 'now that you say, We see, your guilt "
        "remains' (John 9:41). 6, the Judge, drawn dashed as a link John does not make in this scene: "
        "'Arise, O God, judge the earth' (Psalm 82:8) beside 'the Father judges no one, but has given "
        "all judgment to the Son' (John 5:22). Below, the test of works as a balance under the one "
        "'whom the Father consecrated and sent into the world' (John 10:36). The left pan holds their "
        "works: they cast out the man who was healed (John 9:34), 'you seek to kill me' (John 8:40), "
        "and stones taken up (John 10:31); its verdict, 'now they have seen and hated both me and my "
        "Father' (John 15:24). The right pan holds His works: 'The works that I do in my Father's "
        "name bear witness about me' (John 10:25), 'many good works from the Father' (John 10:32), "
        "'believe the works' (John 10:38); its verdict, 'that you may know and understand that the "
        "Father is in me and I am in the Father' (John 10:38).",
    )
    out += heading("Two Courts", "Psalm 82 and the Feast of Dedication · John 10:22-39")

    # Column heads: the two courts.
    out.append(f'<rect x="{lx}" y="{y0}" width="{cw}" height="44" rx="6" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.5"/>')
    out.append(text(lx + cw / 2, y0 + 19, "GOD’S COURT", 15, "middle", "bold", spacing="1.5"))
    out.append(text(lx + cw / 2, y0 + 36, "“God has taken his place” · Psalm 82", 12.5, "middle", italic=True))
    out.append(f'<rect x="{rx}" y="{y0}" width="{cw}" height="44" rx="6" fill="{BLUE}" stroke="{BLUE}" stroke-width="1.5"/>')
    out.append(text(rx + cw / 2, y0 + 19, "THE COURT AT DEDICATION", 13.5, "middle", "bold", fill=PAPER, spacing="1"))
    out.append(text(rx + cw / 2, y0 + 36, "Israel’s teachers, stones in hand · John", 12.5, "middle", italic=True, fill=PAPER))
    out.append(text(mid, y0 + 18, "he quotes", 11.5, "middle", italic=True, fill=MUTED))
    out.append(text(mid, y0 + 33, "10:34", 11.5, "middle", italic=True, fill=MUTED))
    out.append(f'<path d="M{lx + cw + 8} {y0 + 22} H{rx - 8}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 3"/>')
    out.append(banner(mid, y0 - 40, 360, "SIX CHARGES, RUNG FOR RUNG")[0])
    out.append(banner(mid, y0 - 40, 360, "SIX CHARGES, RUNG FOR RUNG")[1])
    out += body

    # Key.
    ky = rungs_end + 14
    out.append(f'<path d="M{lx} {ky + 7} H{lx + 40}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(text(lx + 48, ky + 12, "a charge of Psalm 82 John records of these men", 12))
    out.append(f'<path d="M{rx - 20} {ky + 7} H{rx + 20}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(text(rx + 28, ky + 12, "a link John does not make here", 12))

    # B. The test of works.
    y = ky + 48
    out += banner(mid, y, 380, "THE TEST OF WORKS · JOHN 10:37-38")
    y += 44
    out.append(text(mid, y + 4, "“If I am not doing the works of my Father, then do not believe me;", 14, "middle", italic=True))
    out.append(text(mid, y + 22, "but if I do them … believe the works”", 14, "middle", italic=True))
    y += 46

    # The one who stands accused, at the pivot.
    out.append(f'<rect x="{mid - 150}" y="{y}" width="300" height="48" rx="6" fill="{CARD}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(text(mid, y + 20, "“him whom the Father consecrated", 14, "middle", italic=True, weight="bold"))
    out.append(text(mid, y + 38, "and sent into the world” · John 10:36", 13, "middle", italic=True))
    piv = y + 48
    beam_y = piv + 34
    out.append(f'<path d="M{mid} {piv} V{beam_y}" stroke="{INK}" stroke-width="3"/>')
    out.append(f'<path d="M{mid - 6} {beam_y - 6} L{mid} {beam_y} L{mid + 6} {beam_y - 6}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<path d="M{L_PAN} {beam_y} H{R_PAN}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    out.append(f'<circle cx="{mid}" cy="{beam_y}" r="5" fill="{INK}"/>')

    pans = [
        (L_PAN, "THEIR WORKS", RED, RED_TINT,
         [("They cast out the man who was healed", "John 9:34"),
          ("“now you seek to kill me”", "John 8:40"),
          ("“picked up stones again to stone him”", "John 10:31")],
         ["“now they have seen and hated", "both me and my Father”"], "John 15:24", "CONDEMN THEM"),
        (R_PAN, "HIS WORKS", BLUE, BLUE_TINT,
         [("“The works that I do in my Father’s name bear witness about me”", "John 10:25"),
          ("“many good works from the Father”", "John 10:32"),
          ("“believe the works”", "John 10:38")],
         ["“that you may know … that the Father", "is in me and I am in the Father”"], "John 10:38", "VERIFY HIS CLAIM"),
    ]
    pan_top = beam_y + 70
    pw = 240

    def item_rows(items):
        return [(q, r, wrap(q, 33)) for q, r in items]

    def items_height(items):
        return sum(8 + LINE * len(rows) + LINE - 2 + 8 for _, _, rows in item_rows(items))

    verdict_y = pan_top + 32 + max(items_height(p[4]) for p in pans)
    for cx, title, ink, tint, items, verdict, vref, vword in pans:
        # Chains and the pan.
        out.append(f'<path d="M{cx} {beam_y} L{cx - 100} {pan_top} M{cx} {beam_y} L{cx + 100} {pan_top}" stroke="{INK}" stroke-width="1.2"/>')
        out.append(f'<path d="M{cx - 118} {pan_top} H{cx + 118} Q{cx + 108} {pan_top + 18} {cx} {pan_top + 18} '
                   f'Q{cx - 108} {pan_top + 18} {cx - 118} {pan_top} Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
        out.append(text(cx, pan_top - 8, title, 14, "middle", "bold", fill=ink, spacing="1.5"))
        if cx == L_PAN:
            out += stones(cx + 88, pan_top - 6)
        iy = pan_top + 32
        for q, r, rows in item_rows(items):
            hh = 8 + LINE * len(rows) + LINE - 2
            out.append(f'<rect x="{cx - pw / 2}" y="{iy}" width="{pw}" height="{hh}" rx="4" fill="{tint}" stroke="{ink}" stroke-width="1.2"/>')
            ty = iy + 4 + LINE * 0.85
            for row in rows:
                out.append(text(cx - pw / 2 + 10, ty, row, 13, italic=q.startswith("“")))
                ty += LINE
            out.append(text(cx + pw / 2 - 10, ty - 2, r, 11.5, "end", fill=MUTED))
            iy += hh + 8
        out.append(f'<path d="M{cx} {iy} V{verdict_y}" stroke="{ink}" stroke-width="1" stroke-dasharray="2 3"/>')
        iy = verdict_y
        # Verdict.
        out.append(f'<path d="M{cx} {iy} V{iy + 16}" stroke="{ink}" stroke-width="2"/>')
        out.append(arrow_head(cx, iy + 20, 90, 9, ink))
        out.append(banner(cx, iy + 24, 200, vword, fill=ink, size=13)[0])
        out.append(banner(cx, iy + 24, 200, vword, fill=ink, size=13)[1])
        out.append(text(cx, iy + 72, verdict[0], 13, "middle", italic=True))
        out.append(text(cx, iy + 89, verdict[1], 13, "middle", italic=True))
        out.append(text(cx, iy + 106, vref, 11.5, "middle", fill=MUTED))
        end = iy + 106

    h_needed = end + 50
    assert h_needed <= h, h_needed
    out[0] = out[0].replace(f'viewBox="0 0 {W} {h}"', f'viewBox="0 0 {W} {h_needed}"')
    out[3] = out[3].replace(f'height="{h}"', f'height="{h_needed}"')
    out[4] = out[4].replace(f'height="{h - 16}"', f'height="{h_needed - 16}"')
    out[5] = out[5].replace(f'height="{h - 28}"', f'height="{h_needed - 28}"')
    out.append(credit(h_needed))
    out.append("</svg>")
    return "\n".join(out)


ROAD = "#d9c595"
ROAD_EDGE = "#a88e5c"
SKY_TOP = "#cfdbe6"
SKY_LOW = "#f3e2bd"
FIELD = "#d9cba4"
FIELD_NEAR = "#cbb98c"
HILL = "#b9a77f"
WALL = "#d8c7a3"
WALL_EDGE = "#8d7650"
SKIN = "#b88a62"
HAIR = "#3b2a1a"
GLOW = "#f6e2a0"
ROBES = ["#3d4a63", "#6b2c2c", "#4a3a28", "#55603f", "#3a3550"]
JESUS_ROBE = "#efe6d2"
JESUS_MANTLE = "#9b3b2c"
HEALED_ROBE = "#a68b62"


def catmull(points, n=12):
    out = []
    pts = [points[0]] + points + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(3)))
    out.append(points[-1])
    return out


def road_polygon(spine):
    """spine: (x, y, half_width) from near to far. Returns the road's outline path."""
    pts = catmull(spine)
    left, right = [], []
    for i, (x, y, hw) in enumerate(pts):
        left.append((x - hw, y))
        right.append((x + hw, y))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left + right[::-1]) + " Z"
    centre = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y, _ in pts)
    return d, centre, pts


def person_front(x, y, s, robe, cloth, arm=None, stone=False):
    """A robed figure facing the reader, head covered; (x, y) is the feet."""
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">',
         f'<path d="M-11 0 Q-13 -30 -10 -50 Q0 -56 10 -50 Q13 -30 11 0 Z" fill="{robe}"/>',
         f'<path d="M-10 -50 Q-4 -30 -6 0" fill="none" stroke="#00000033" stroke-width="1.4"/>',
         f'<path d="M3 -48 Q6 -26 4 0" fill="none" stroke="#ffffff22" stroke-width="1.4"/>',
         f'<circle cx="0" cy="-60" r="6.5" fill="{SKIN}"/>',
         f'<path d="M-8 -58 Q-8 -70 0 -70 Q8 -70 8 -58 L10 -46 Q0 -50 -10 -46 Z" fill="{cloth}"/>',
         f'<path d="M-11 -2 H11" stroke="#00000044" stroke-width="2"/>']
    if arm == "raised":
        g.append(f'<path d="M8 -46 L16 -62 L19 -60 L12 -44 Z" fill="{robe}"/>')
        if stone:
            g.append(f'<ellipse cx="18" cy="-65" rx="5" ry="4" fill="#9a8f80" stroke="#6e6455" stroke-width="0.8"/>')
    elif arm == "point":
        g.append(f'<path d="M8 -44 L22 -40 L22 -37 L8 -40 Z" fill="{robe}"/>')
    g.append('</g>')
    return "".join(g)


def person_back(x, y, s):
    """Jesus seen from behind: hair to the shoulders, a light robe, a mantle over one shoulder."""
    return "".join([
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">',
        f'<path d="M-13 0 Q-15 -30 -12 -52 Q0 -58 12 -52 Q15 -30 13 0 Z" fill="{JESUS_ROBE}" stroke="#b9ab8c" stroke-width="0.8"/>',
        f'<path d="M-12 -52 Q2 -56 12 -50 L8 -26 Q-2 -14 -13 -2 Q-15 -30 -12 -52 Z" fill="{JESUS_MANTLE}"/>',
        f'<path d="M-4 -40 Q2 -30 6 -28" fill="none" stroke="#00000033" stroke-width="1.2"/>',
        f'<path d="M-6 -2 Q-2 -18 4 -26" fill="none" stroke="#00000022" stroke-width="1.2"/>',
        f'<circle cx="0" cy="-63" r="7.5" fill="{HAIR}"/>',
        f'<path d="M-7.5 -63 Q-8 -52 -5 -50 H5 Q8 -52 7.5 -63 Z" fill="{HAIR}"/>',
        f'<path d="M12 -48 L20 -34 L17 -32 L10 -44 Z" fill="{JESUS_ROBE}" stroke="#b9ab8c" stroke-width="0.6"/>',
        '</g>'])


def person_kneeling_front(x, y, s):
    """The healed man kneeling toward the reader, hands raised; (x, y) is the knees."""
    return "".join([
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">',
        f'<path d="M-14 0 Q-14 -8 -10 -10 H10 Q14 -8 14 0 Z" fill="{HEALED_ROBE}"/>',
        f'<path d="M-9 -10 Q-11 -26 -8 -36 Q0 -40 8 -36 Q11 -26 9 -10 Z" fill="{HEALED_ROBE}"/>',
        f'<path d="M-8 -34 L-15 -48 L-12 -50 L-5 -36 Z" fill="{HEALED_ROBE}"/>',
        f'<path d="M8 -34 L15 -48 L12 -50 L5 -36 Z" fill="{HEALED_ROBE}"/>',
        f'<circle cx="-13.5" cy="-50" r="2.6" fill="{SKIN}"/><circle cx="13.5" cy="-50" r="2.6" fill="{SKIN}"/>',
        f'<circle cx="0" cy="-45" r="6.5" fill="{SKIN}"/>',
        f'<path d="M-6.5 -47 Q-6 -53 0 -53 Q6 -53 6.5 -47 Q3 -50 0 -50 Q-3 -50 -6.5 -47 Z" fill="{HAIR}"/>',
        '</g>'])


def callout(n, x, y, dashed=False):
    dash = ' stroke-dasharray="3 2"' if dashed else ""
    return [f'<circle cx="{x}" cy="{y}" r="11" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"{dash}/>',
            text(x, y + 4.5, str(n), 13, "middle", "bold")]


def key_card(x, y, w, n, title, quotes, fill, stroke, chars, dashed=False):
    """A numbered card: a bold title, then each (quote, ref) wrapped with its reference."""
    rows = []
    for q, r in quotes:
        for line in wrap(q, chars):
            rows.append(("q", line))
        rows.append(("r", r))
    h = 20 + LINE + LINE * len(rows)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>']
    out += callout(n, x + 18, y + 18, dashed)
    out.append(text(x + 36, y + 23, title, 13, weight="bold", spacing="0.8"))
    ty = y + 14 + LINE + LINE * 0.85
    for kind, line in rows:
        if kind == "q":
            out.append(text(x + 14, ty, line, 13, italic=True))
        else:
            out.append(text(x + w - 10, ty - 2, line, 11.5, "end", fill=MUTED))
        ty += LINE if kind == "q" else LINE - 2
    return out, h


def stone_in_hand(x, y, r=5.5):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.8:.1f}" fill="#9a8f80" stroke="#5e5547" stroke-width="0.9"/>'
            f'<ellipse cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" rx="{r * 0.35:.1f}" ry="{r * 0.22:.1f}" fill="#c4bbad"/>')


def walker(x, y, s, robe, mantle, stripe, hands="right", stride=1, look=0):
    """An authority walking away from the reader, mantle over his head, a stone in hand.

    Drawn about seven and a half heads tall: sandalled feet in mid-stride, an ankle-length tunic
    with its folds and a sash, a mantle over head and shoulders with two woven stripes and a tassel
    at each corner, forearms out of the sleeves, a stone gripped in the fist. hands: "right",
    "left", "both", or "raised". look: 1 or -1 turns the head to show a bearded profile.
    """
    fold = "#00000030"
    lite = "#ffffff26"
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">']
    # Feet: the back foot lifts its heel mid-stride, sandal strap across it; the front foot is half hidden.
    g.append(f'<path d="M{-13 * stride} 2 q2 -9 13 -8 l1 9 z" fill="{SKIN}"/>'
             f'<path d="M{-12 * stride} -1 l12 -2 M{-11 * stride} 2 h12" stroke="#5a3d22" stroke-width="2"/>'
             f'<path d="M{4 * stride} -2 q6 -6 12 -2 v4 h-12 z" fill="{SKIN}"/>'
             f'<path d="M{4 * stride} 1 h12" stroke="#5a3d22" stroke-width="2"/>')
    # Tunic, ankle length, flaring with the stride.
    g.append(f'<path d="M-15 -118 Q-17 -86 -19 -60 Q-22 -30 -22 -4 Q0 2 22 -4 Q22 -30 19 -60 Q17 -86 15 -118 Z" fill="{robe}"/>')
    for d in ("M-9 -84 Q-12 -46 -10 -4", "M1 -82 Q3 -40 0 -2", "M11 -80 Q14 -44 14 -6", "M-16 -60 Q-18 -30 -18 -6"):
        g.append(f'<path d="{d}" fill="none" stroke="{fold}" stroke-width="1.3"/>')
    g.append(f'<path d="M-4 -80 Q-3 -44 -5 -4" fill="none" stroke="{lite}" stroke-width="1.6"/>')
    # Sash at the waist, its end hanging.
    g.append(f'<path d="M-17 -84 Q0 -80 17 -84 L17 -78 Q0 -74 -17 -78 Z" fill="#00000040"/>'
             f'<path d="M8 -79 l2 18 l3 -1 l-2 -17 z" fill="#00000040"/>')
    # Arms and hands.
    def arm(side, raised=False):
        sx = 17 * side
        if raised:
            return (f'<path d="M{sx} -114 Q{sx + 10 * side} -128 {sx + 12 * side} -148 L{sx + 4 * side} -150 '
                    f'Q{sx + 2 * side} -132 {sx - 4 * side} -116 Z" fill="{robe}"/>'
                    f'<circle cx="{sx + 8 * side}" cy="-152" r="4.2" fill="{SKIN}"/>' + stone_in_hand(sx + 9 * side, -160, 7.5))
        return (f'<path d="M{sx - 2 * side} -116 Q{sx + 6 * side} -100 {sx + 5 * side} -76 L{sx - 1 * side} -76 '
                f'Q{sx} -96 {sx - 6 * side} -112 Z" fill="{robe}"/>'
                f'<path d="M{sx + 4 * side} -78 l1 -2" stroke="{fold}"/>'
                f'<circle cx="{sx + 2 * side}" cy="-72" r="4.2" fill="{SKIN}"/>' + stone_in_hand(sx + 3 * side, -66, 7))
    if hands in ("right", "both"):
        g.append(arm(1))
    if hands in ("left", "both"):
        g.append(arm(-1))
    if hands == "raised":
        g.append(arm(1, raised=True))
    # Neck, and a profile when the head turns.
    g.append(f'<rect x="-4" y="-126" width="8" height="8" fill="{SKIN}"/>')
    if look:
        g.append(f'<path d="M{6 * look} -142 q{6 * look} 2 {7 * look} 6 l{-2 * look} 2 q{1 * look} 3 {-1 * look} 5 '
                 f'q{-3 * look} 4 {-8 * look} 2 z" fill="{SKIN}"/>'
                 f'<path d="M{5 * look} -131 q{5 * look} 2 {4 * look} 9 q{-5 * look} 2 {-9 * look} -2 z" fill="#2e2216"/>')
    # Mantle over the head and shoulders, falling to mid-back.
    g.append(f'<path d="M-9 -150 Q0 -156 9 -150 Q14 -142 15 -128 Q24 -122 25 -104 L23 -92 Q0 -86 -23 -92 '
             f'L-25 -104 Q-24 -122 -15 -128 Q-14 -142 -9 -150 Z" fill="{mantle}"/>')
    g.append(f'<path d="M-6 -146 Q-2 -130 -8 -110 M6 -146 Q4 -128 10 -108 M-14 -124 Q-10 -110 -16 -96" fill="none" stroke="{fold}" stroke-width="1.1"/>')
    for off in (8, 4):
        g.append(f'<path d="M-24 {-92 - off - 3} Q0 {-86 - off} 24 {-92 - off - 3}" fill="none" stroke="{stripe}" stroke-width="2"/>')
    for cx_ in (-23, 23):
        g.append(f'<path d="M{cx_ - 2} -91 v9 M{cx_} -90 v11 M{cx_ + 2} -91 v9" stroke="{mantle}" stroke-width="1.1"/>'
                 f'<path d="M{cx_} -90 v11" stroke="{stripe}" stroke-width="0.9"/>')
    g.append('</g>')
    return "".join(g)


def scales(x, y, s=1.0):
    """A balance standing on the hill: base, pillar, beam, two hanging pans; (x, y) is the base."""
    e = GOLD_EDGE
    return "".join([
        f'<g transform="translate({x} {y}) scale({s})">',
        f'<path d="M-20 0 H20 L14 -8 H-14 Z" fill="{GOLD}" stroke="{e}" stroke-width="1.2"/>',
        f'<rect x="-3" y="-78" width="6" height="70" fill="{GOLD}" stroke="{e}" stroke-width="1"/>',
        f'<circle cx="0" cy="-82" r="5" fill="{GOLD}" stroke="{e}" stroke-width="1"/>',
        f'<path d="M-46 -78 H46" stroke="{e}" stroke-width="4" stroke-linecap="round"/>',
        f'<path d="M-46 -78 L-60 -40 M-46 -78 L-32 -40 M46 -78 L32 -40 M46 -78 L60 -40" stroke="{e}" stroke-width="1"/>',
        f'<path d="M-64 -40 H-28 Q-32 -30 -46 -30 Q-60 -30 -64 -40 Z" fill="{GOLD}" stroke="{e}" stroke-width="1.2"/>',
        f'<path d="M28 -40 H64 Q60 -30 46 -30 Q32 -30 28 -40 Z" fill="{GOLD}" stroke="{e}" stroke-width="1.2"/>',
        '</g>'])


def the_path():
    h = 1700
    out = svg_open(
        h,
        "The authorities' path",
        "An imagery plate of John 9-10. A road winds from the foreground to a hill on the horizon. "
        "1, beside the road in the foreground, Moses' seat: a stone chair with a carved back, left "
        "empty, the scroll of the Law lying on it: 'The scribes and the Pharisees sit on Moses' seat' "
        "(Matthew 23:2); 'gods to whom the word of God came' (John 10:35). 2, five authorities walk "
        "the road away from the seat, backs to the reader, mantles with woven stripes and tassels "
        "over their heads, stones in their hands, one stone raised: 'And they reviled him' (John "
        "9:28); 'The Jews picked up stones again to stone him' (John 10:31). 3, in the background a "
        "synagogue, its door dark, and the healed man standing outside it: 'You were born in utter "
        "sin, and would you teach us?' And they cast him out (John 9:34). 4, in the foreground off "
        "the road, Jesus stands with His back to the reader, and the man He healed kneels before Him "
        "with his hands raised, in a soft light: he 'washed and came back seeing' (John 9:7); 'If "
        "this man were not from God, he could do nothing' (John 9:33); 'Lord, I believe,' and he "
        "worshiped him (John 9:38). 5, the far road runs into darkness: 'They have neither knowledge "
        "nor understanding, they walk about in darkness' (Psalm 82:5); 'now that you say, We see, "
        "your guilt remains' (John 9:41). 6, where the road ends, a pair of scales stands on the hill "
        "under a darkening sky: 'nevertheless, like men you shall die, and fall like any prince' "
        "(Psalm 82:7); 'Arise, O God, judge the earth' (Psalm 82:8). Across the foot: 'For judgment "
        "I came into this world, that those who do not see may see, and those who see may become "
        "blind' (John 9:39).",
    )
    out += heading("The Path They Walked", "John 9-10 · the seat they held, the works they did, the judgment ahead")

    px, py, pw, ph = 30, 120, 660, 600
    hz = py + 190
    out.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{SKY_TOP}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient>'
               f'<radialGradient id="storm" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#4a4038" stop-opacity="0.55"/>'
               f'<stop offset="1" stop-color="#4a4038" stop-opacity="0"/></radialGradient>'
               f'<linearGradient id="dark" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#2a2016" stop-opacity="0"/>'
               f'<stop offset="1" stop-color="#2a2016" stop-opacity="0.8"/></linearGradient>'
               f'<clipPath id="pane"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6"/></clipPath></defs>')
    out.append('<g clip-path="url(#pane)">')
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{hz - py + 2}" fill="url(#sky)"/>')
    # The hill of judgment on the horizon: the scales, under a darkening sky.
    tx, ty = 470, hz - 40
    out.append(f'<ellipse cx="{tx}" cy="{ty - 70}" rx="200" ry="90" fill="url(#storm)"/>')
    out.append(f'<path d="M{px} {hz} Q{px + 180} {hz - 16} {tx - 90} {hz - 8} Q{tx} {hz - 62} {tx + 90} {hz - 8} '
               f'Q{px + pw - 60} {hz - 18} {px + pw} {hz - 6} V{hz + 30} H{px} Z" fill="{HILL}"/>')
    out.append(scales(tx, ty + 4, 1.0))
    out.append(f'<rect x="{px}" y="{hz}" width="{pw}" height="{ph}" fill="{FIELD}"/>')
    out.append(f'<path d="M{px} {hz + 220} Q{px + 330} {hz + 190} {px + pw} {hz + 230} V{py + ph} H{px} Z" fill="{FIELD_NEAR}"/>')

    # The synagogue in the background, and the man cast out of it.
    sx, sy = 100, hz + 70
    out.append(f'<path d="M{sx - 60} {sy} V{sy - 70} L{sx} {sy - 98} L{sx + 60} {sy - 70} V{sy} Z" fill="{WALL}" stroke="{WALL_EDGE}" stroke-width="1.2"/>')
    for k in (-48, -30, 30, 48):
        out.append(f'<rect x="{sx + k - 3}" y="{sy - 64}" width="6" height="64" fill="{CARD}" stroke="{WALL_EDGE}" stroke-width="0.6"/>')
    out.append(f'<path d="M{sx - 16} {sy} V{sy - 40} Q{sx} {sy - 54} {sx + 16} {sy - 40} V{sy} Z" fill="#3e3122"/>')
    for dx in (-7, 6):
        out.append(person_front(sx + dx, sy - 2, 0.42, "#1f1810", "#2e2418"))
    out.append(person_front(sx + 40, sy + 18, 0.55, HEALED_ROBE, HEALED_ROBE))
    out.append(f'<path d="M{sx + 18} {sy - 12} H{sx + 34}" stroke="{RED}" stroke-width="1.6"/>')
    out.append(arrow_head(sx + 38, sy - 12, 0, 6, RED))

    # The road, near to far.
    spine = [(330, py + ph + 30, 150), (300, py + ph - 70, 120), (380, hz + 230, 82), (330, hz + 140, 52),
             (400, hz + 70, 28), (450, hz + 18, 12), (tx, ty + 6, 4)]
    road, centre, pts = road_polygon(spine)
    out.append(f'<path d="{road}" fill="{ROAD}" stroke="{ROAD_EDGE}" stroke-width="1.6"/>')
    out.append(f'<path d="{centre}" fill="none" stroke="{ROAD_EDGE}" stroke-width="1" stroke-dasharray="6 7" opacity="0.6"/>')

    def on_road(frac):
        x, y, hw = pts[int(frac * (len(pts) - 1))]
        return x, y, hw

    # 1. Moses' seat, beside the road in the foreground: a stone chair with a carved back, arms and a step,
    # left empty, the scroll of the Law lying on it.
    mx, my = 60, py + ph - 70
    st = f'fill="{WALL}" stroke="{WALL_EDGE}" stroke-width="1.5"'
    out.append(f'<path d="M{mx} {my} H{mx + 150} V{my - 12} H{mx} Z" {st}/>')                     # the step
    out.append(f'<path d="M{mx + 22} {my - 12} V{my - 128} Q{mx + 75} {my - 156} {mx + 128} {my - 128} V{my - 12} Z" {st}/>')  # the back
    out.append(f'<path d="M{mx + 40} {my - 64} V{my - 112} Q{mx + 75} {my - 132} {mx + 110} {my - 112} V{my - 64}" '
               f'fill="none" stroke="{WALL_EDGE}" stroke-width="1.2"/>')                          # carved panel
    for ax in (mx + 12, mx + 120):
        out.append(f'<path d="M{ax} {my - 12} V{my - 70} Q{ax} {my - 78} {ax + 9} {my - 78} Q{ax + 18} {my - 78} {ax + 18} {my - 70} V{my - 12} Z" {st}/>')
    out.append(f'<path d="M{mx + 30} {my - 12} V{my - 52} H{mx + 120} V{my - 12} Z" {st}/>')        # seat block
    out.append(f'<path d="M{mx + 30} {my - 52} L{mx + 36} {my - 60} H{mx + 114} L{mx + 120} {my - 52} Z" {st}/>')
    out.append(f'<rect x="{mx + 54}" y="{my - 66}" width="42" height="9" rx="4.5" fill="{CARD}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<circle cx="{mx + 55}" cy="{my - 61.5}" r="6" fill="{CARD}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<circle cx="{mx + 95}" cy="{my - 61.5}" r="6" fill="{CARD}" stroke="{INK}" stroke-width="1"/>')

    # 5. The far road runs into darkness.
    i0 = int(0.5 * (len(pts) - 1))
    far = pts[i0:]
    dark = ("M" + " L".join(f"{x - hw:.1f} {y:.1f}" for x, y, hw in far) + " L"
            + " L".join(f"{x + hw:.1f} {y:.1f}" for x, y, hw in far[::-1]) + " Z")
    out.append(f'<path d="{dark}" fill="url(#dark)"/>')
    cx_, cy_, _ = on_road(0.68)

    # 2. The authorities, walking the road away from the seat, stones in their hands.
    gx, gy_, ghw = on_road(0.2)
    gx += 24
    out.append(f'<ellipse cx="{gx}" cy="{gy_ + 4}" rx="86" ry="8" fill="#00000020"/>')
    group = [  # far to near, so the nearer figures overlap the farther
        (-40, -26, 0.78, 3, "#e3d8c2", "#2f4f7f", "left", 1, 0),
        (34, -30, 0.76, 1, "#efe6d2", "#2b2b2b", "raised", -1, 0),
        (-2, -18, 0.84, 4, "#e8dfcc", "#2f4f7f", "both", 1, -1),
        (-58, 0, 0.92, 0, "#efe6d2", "#2b2b2b", "right", -1, 1),
        (30, 2, 0.94, 2, "#e3d8c2", "#2f4f7f", "right", 1, 0),
    ]
    for dx, dy, sc, c, mantle, stripe, hands, stride, look in group:
        out.append(walker(gx + dx, gy_ + dy, sc, ROBES[c], mantle, stripe, hands, stride, look))

    # 4. In the foreground, off the road: the healed man kneeling, and Jesus with His back to the reader.
    jx, jy = 560, py + ph - 26
    out.append(f'<circle cx="{jx - 56}" cy="{jy - 96}" r="84" fill="{GLOW}" opacity="0.55"/>')
    out.append(person_kneeling_front(jx - 74, jy - 44, 1.45))
    out.append(f'<ellipse cx="{jx}" cy="{jy}" rx="34" ry="6" fill="#00000022"/>')
    out.append(person_back(jx, jy, 2.4))
    out.append('</g>')
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="none" stroke="{INK}" stroke-width="1.6"/>')

    # Callouts on the scene.
    out += callout(1, mx + 75, my - 168)
    out += callout(2, gx - 92, gy_ - 150)
    out += callout(3, sx, sy - 116)
    out += callout(4, jx - 90, jy - 196)
    out += callout(5, cx_ - 46, cy_ - 8)
    out += callout(6, tx + 78, ty - 70)

    # The key.
    y = py + ph + 18
    colw = (pw - 12) / 2
    keys = [
        (1, "THE SEAT THEY HELD", [("“The scribes and the Pharisees sit on Moses’ seat”", "Matthew 23:2"),
                                   ("“he called them gods to whom the word of God came”", "John 10:35")],
         GOLD_TINT, GOLD_EDGE, False),
        (4, "HIS WORK", [("He “washed and came back seeing”", "John 9:7"),
                         ("“If this man were not from God, he could do nothing”", "John 9:33"),
                         ("“Lord, I believe,” and he worshiped him", "John 9:38")],
         GOLD_TINT, GOLD_EDGE, False),
        (2, "THEIR WORKS", [("“And they reviled him”", "John 9:28"),
                            ("“The Jews picked up stones again to stone him”", "John 10:31")],
         RED_TINT, RED, False),
        (3, "THE MAN CAST OUT", [("“You were born in utter sin, and would you teach us?” And they cast him out.", "John 9:34")],
         RED_TINT, RED, False),
        (5, "THE ROAD INTO DARKNESS", [("“They have neither knowledge nor understanding, they walk about in darkness”", "Psalm 82:5"),
                                       ("“now that you say, ‘We see,’ your guilt remains”", "John 9:41")],
         CARD, INK, False),
        (6, "THE JUDGMENT", [("“nevertheless, like men you shall die, and fall like any prince”", "Psalm 82:7"),
                             ("“Arise, O God, judge the earth”", "Psalm 82:8")],
         CARD, INK, False),
    ]
    for i in range(0, len(keys), 2):
        row = []
        for j, (n, title, quotes, fill, stroke, dashed) in enumerate(keys[i:i + 2]):
            c, hh = key_card(px + j * (colw + 12), y, colw, n, title, quotes, fill, stroke, 40, dashed)
            row.append(hh)
            out += c
        y += max(row) + 12
    y += 24
    out.append(text(W / 2, y, "“For judgment I came into this world, that those who do not see may see,", 14.5, "middle", italic=True))
    out.append(text(W / 2, y + 20, "and those who see may become blind.” · John 9:39", 14.5, "middle", italic=True))
    end = y + 20

    h_needed = end + 50
    assert h_needed <= h, h_needed
    out[0] = out[0].replace(f'viewBox="0 0 {W} {h}"', f'viewBox="0 0 {W} {h_needed}"')
    out[3] = out[3].replace(f'height="{h}"', f'height="{h_needed}"')
    out[4] = out[4].replace(f'height="{h - 16}"', f'height="{h_needed - 16}"')
    out[5] = out[5].replace(f'height="{h - 28}"', f'height="{h_needed - 28}"')
    out.append(credit(h_needed))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("two-courts", two_courts), ("the-path", the_path)]:
        (OUT / f"{name}.svg").write_text(fn() + "\n", encoding="utf-8")
        print(f"wrote {OUT / name}.svg")


if __name__ == "__main__":
    main()
