"""Draw the tribulation charts for last-things/tribulation.md, after the manner of Clarence Larkin.

Four charts share one hand: parchment, ink, red for judgment, gold for heaven, blue for Israel, and
one confidence code. A solid outline means the text itself dates the event (Daniel 9:27's covenant,
the abomination at the midpoint, a span counted in days or months). A dashed outline means the
event is placed by its order in Revelation, which is inference. Run from the repo root after
changing an event, a reference or a count:

    python3 utils/build_tribulation_graphics.py

The counts in church_and_saints() are SBLGNT occurrences from bible-text.db (macula-greek-sblgnt),
recorded with their queries in references/study-state/tribulation.yml. Re-run the queries before
changing them.

Charts are portrait and 720 units wide so that 14-15 unit lettering still reads at the site's
~560px content column; mermaid's lesson (diagrams.md) applies to a drawn SVG just as much.
"""

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "content" / "assets" / "img" / "tribulation"

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, HALO, text, svg_open, heading, banner, cloud, arrow_head,
                        card, legend_row, credit)

# ---------------------------------------------------------------------------------------------
# 1. The seventieth week: heaven, earth and Israel, year by year


def seventieth_week():
    y0, half = 360, 500
    mid, end = y0 + half, y0 + 2 * half
    ax0, ax1 = 24, 84
    lanes = [(92, 288), (296, 492), (500, 696)]
    lane_fill = [GOLD_TINT, EARTH_TINT, BLUE_TINT]
    lane_name = ["IN HEAVEN", "ON THE EARTH", "ISRAEL"]
    h = end + 290

    out = svg_open(
        h,
        "Daniel's seventieth week",
        "A chart of the seven years of Daniel 9:27, read top to bottom, in three lanes: heaven, the "
        "earth, and Israel. Above the week, the church age ends as the church is caught up to meet "
        "the Lord (1 Thessalonians 4:16-17). The week opens with a covenant (Daniel 9:27). In the "
        "first half the Lamb opens the seals, the 144,000 are sealed and the trumpets sound. John "
        "sees the great multitude in chapter 7, and a dotted line carries them to the second half, "
        "where the elder says they are 'coming out of the great tribulation' (Revelation 7:14). At the midpoint, day "
        "1,260, sacrifice is stopped and the abomination set up (Daniel 9:27; Matthew 24:15), the "
        "dragon is thrown down from heaven (Revelation 12:9), the woman flees to the wilderness for "
        "1,260 days (Revelation 12:6) and the beast is given authority for forty-two months "
        "(Revelation 13:5). In the second half the bowls are poured out, Babylon falls, and the "
        "kings gather at Armageddon. At the end the King comes from heaven with His armies "
        "(Revelation 19:11-16) and Israel looks on Him whom they pierced (Zechariah 12:10). The "
        "thousand years follow. Solid boxes are dated by the text; dashed boxes are placed by "
        "their order in Revelation.",
    )
    out += heading("Daniel's Seventieth Week",
                   "“Seventy weeks are decreed about your people and your holy city” (Daniel 9:24, ESV)")

    # Heaven above: the throne under its rainbow (Revelation 4:2-3), on a bank of cloud.
    out += cloud(W / 2, 214, 520)
    out.append(f'<path d="M{W / 2 - 46} 156 A46 40 0 0 1 {W / 2 + 46} 156" fill="none" '
               f'stroke="#7da36b" stroke-width="5" opacity="0.8"/>')
    out.append(f'<rect x="{W / 2 - 18}" y="128" width="36" height="26" rx="3" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    out.append(f'<rect x="{W / 2 - 24}" y="150" width="48" height="8" rx="2" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    out.append(text(W / 2 - 60, 140, "THE THRONE", 13, "end", "bold", fill=GOLD_EDGE, spacing="2"))
    out.append(text(W / 2 + 60, 140, "Revelation 4–5", 13, fill=MUTED, italic=True))

    # The church age, and the church caught up out of it.
    out.append(f'<rect x="{lanes[0][0]}" y="250" width="{lanes[2][1] - lanes[0][0]}" height="30" '
               f'fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    out.append(text((lanes[0][0] + lanes[2][1]) / 2, 270, "THE CHURCH AGE", 15, "middle", "bold",
                    spacing="2"))
    rx = 150
    out.append(f'<path d="M{rx} 250 C{rx - 24} 236 {rx - 16} 226 {rx} 218" fill="none" '
               f'stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    out.append(arrow_head(rx, 216, -70, 11, GOLD_EDGE))
    out.append(text(40, 226, "Caught up", 14, weight="bold"))
    out.append(text(40, 242, "1 Thess 4:16-17", 12.5, fill=MUTED, italic=True))
    out.append(text(lanes[2][1], 232, "The restrainer “out of the way”", 13, "end"))
    out.append(text(lanes[2][1], 246, "2 Thessalonians 2:7", 12.5, "end", fill=MUTED, italic=True))
    out.append(text(W / 2, 304, "an interval Scripture does not measure", 13, "middle", fill=MUTED,
                    italic=True))
    out.append(f'<path d="M{W / 2} 284 V292 M{W / 2} 310 V318" stroke="{MUTED}" stroke-dasharray="2 3"/>')

    # Lane grounds and headers.
    for (a, b), fill, name in zip(lanes, lane_fill, lane_name):
        out.append(f'<rect x="{a}" y="{y0}" width="{b - a}" height="{end - y0}" fill="{fill}"/>')
        out += banner((a + b) / 2, y0 - 34, b - a - 34, name,
                      fill={GOLD_TINT: GOLD_EDGE, EARTH_TINT: INK, BLUE_TINT: BLUE}[fill], size=13)

    # The year axis.
    out.append(f'<rect x="{ax0}" y="{y0}" width="{ax1 - ax0}" height="{end - y0}" fill="none" stroke="{INK}"/>')
    for i in range(8):
        y = y0 + i * (end - y0) / 7
        out.append(f'<path d="M{ax0} {y:.1f} H{ax1}" stroke="{INK}" stroke-width="0.8"/>')
        if i < 7:
            ly = y + (end - y0) / 14 + 5 + (22 if i == 3 else 0)
            out.append(text((ax0 + ax1) / 2, ly, f"Year {i + 1}", 13, "middle", fill=MUTED))
    for y, label in ((y0, "day 1"), (mid, "1,260"), (end, "2,520")):
        out.append(text(ax0 + 3, y - 4 if y != y0 else y + 14, label, 11.5, fill=RED, weight="bold"))

    # The midpoint, ruled across all three lanes.
    out.append(f'<rect x="{ax0}" y="{mid - 3}" width="{lanes[2][1] - ax0}" height="6" fill="{RED}"/>')
    out += banner(W / 2 + 40, mid - 34, 300, "THE MIDPOINT · DANIEL 9:27", fill=RED, size=13)

    def lane_cards(lane, items):
        a, b = lanes[lane]
        res, bottom = [], 0
        for top, lines, ref, dashed, narrow in items:
            assert top >= bottom, f"overlap in lane {lane} at {lines[0]}"
            w = (b - a - 12) - (22 if narrow else 0)
            c, hh = card(a + 6, top, w, lines, ref, dashed)
            res += c
            bottom = top + hh + 6
        assert bottom <= end - 4 or lane == 1, f"lane {lane} overruns the week"
        return res

    def span(lane, ya, yb, label, dashed=False, color=RED):
        a, b = lanes[lane]
        x = b - 11
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        r = [f'<path d="M{x} {ya + 4} V{yb - 4}" stroke="{color}" stroke-width="3"{dash}/>',
             f'<path d="M{x - 6} {ya + 4} H{x + 6} M{x - 6} {yb - 4} H{x + 6}" stroke="{color}" stroke-width="1.5"/>']
        cy = (ya + yb) / 2
        r.append(text(x - 5, cy, label, 12, "middle", "bold", fill=color,
                      extra=f'transform="rotate(-90 {x - 5} {cy})"'))
        return r

    out += lane_cards(0, [
        (y0 + 10, ["The Lamb takes the", "scroll and opens", "its seals"], "Revelation 5:7; 6:1", True, False),
        (y0 + 120, ["The church before", "Christ's judgment seat"], "2 Corinthians 5:10", True, False),
        (y0 + 212, ["Martyrs under the", "altar, given robes"], "Revelation 6:9-11", True, False),
        (mid + 14, ["War in heaven: the", "dragon thrown down"], "Revelation 12:7-12", True, False),
        (mid + 106, ["“Woe to you, O earth”:", "the devil's short time"], "Revelation 12:12", True, False),
        (mid + 198, ["Seven angels with", "the last plagues"], "Revelation 15:1-8", True, False),
        (mid + 270, ["The multitude", "“coming out of the", "great tribulation”"],
         "Revelation 7:9-17", True, False),
        (end - 132, ["The marriage of the", "Lamb; the bride in", "fine linen"], "Revelation 19:7-9", True, False),
    ])
    out += lane_cards(1, [
        (y0 + 10, ["A strong covenant", "with many, for one", "week"], "Daniel 9:27", False, False),
        (y0 + 106, ["Seals 1–6: conquest,", "war, famine, death", "on a fourth of the", "earth"],
         "Revelation 6:1-17", True, False),
        (y0 + 222, ["Trumpets 1–6: a third", "of earth, sea, rivers,", "lights and mankind"],
         "Revelation 8:6-9:21", True, False),
        (y0 + 322, ["“They did not repent”"], "Revelation 9:20-21", True, False),
        (mid + 14, ["The beast given", "authority over every", "nation"], "Revelation 13:5-8", False, True),
        (mid + 112, ["The image, and the", "mark on hand or", "forehead"], "Revelation 13:14-17", True, True),
        (mid + 210, ["Bowls 1–7: “the", "wrath of God is", "finished”"], "Revelation 15:1; 16", True, True),
        (mid + 304, ["Babylon the great", "falls"], "Rev 16:19; 17–18", True, True),
        (mid + 384, ["Kings gathered at", "Armageddon"], "Revelation 16:12-16", True, True),
    ])
    out += span(1, mid, end, "42 MONTHS · REVELATION 13:5")
    out += lane_cards(2, [
        (y0 + 10, ["144,000 sealed", "from every tribe", "of Israel"], "Revelation 7:3-8", True, True),
        (y0 + 104, ["Temple measured;", "two witnesses", "prophesy"], "Revelation 11:1-3", True, True),
        (y0 + 210, ["Which half? The text", "does not say; the", "cascade favours", "the first"], "Revelation 11:7-15", True, True),
        (mid + 14, ["Sacrifice stopped;", "the abomination", "set up"], "Dan 9:27; Matt 24:15", False, True),
        (mid + 120, ["“Flee to the", "mountains”: the woman", "in the wilderness"],
         "Matt 24:16; Rev 12:6, 14", False, True),
        (mid + 226, ["“A time of distress", "for Jacob; yet he shall", "be saved out of it”"],
         "Jer 30:7; Dan 12:1", True, True),
        (end - 116, ["They look on Him", "whom they have", "pierced"], "Zechariah 12:10; Rev 1:7", False, True),
    ])
    out += span(2, y0, mid, "1,260 DAYS?", dashed=True, color=BLUE)

    # John sees the multitude in chapter 7; they arrive out of the second half (7:14, present participle).
    hx = lanes[0][0] + 3
    out += [text(lanes[0][0] + 10, y0 + 322, "John sees the", 13, italic=True, fill=GOLD_EDGE),
            text(lanes[0][0] + 10, y0 + 339, "multitude here,", 13, italic=True, fill=GOLD_EDGE),
            text(lanes[0][0] + 10, y0 + 356, "in chapter 7", 13, italic=True, fill=GOLD_EDGE),
            f'<path d="M{hx} {y0 + 316} V{mid + 296}" stroke="{GOLD_EDGE}" stroke-width="1.8" stroke-dasharray="2 4"/>',
            arrow_head(hx + 4, mid + 300, 0, 8, GOLD_EDGE)]
    out += span(2, mid, end, "1,260 DAYS · REVELATION 12:6")

    # The King comes: out of the heaven lane, down onto the earth and Israel.
    ky = end + 26
    out.append(f'<path d="M190 {end - 20} C190 {end + 10} 230 {ky + 34} {lanes[1][0] - 4} {ky + 34}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3"/>')
    out.append(arrow_head(lanes[1][0] - 2, ky + 34, 0, 12, GOLD_EDGE))
    out.append(f'<rect x="{lanes[1][0]}" y="{ky}" width="{lanes[2][1] - lanes[1][0]}" height="78" '
               f'rx="6" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>')
    # A crown of many diadems (Revelation 19:12).
    cx0 = lanes[1][0] + 34
    out.append(f'<path d="M{cx0 - 18} {ky + 52} L{cx0 - 18} {ky + 28} L{cx0 - 9} {ky + 40} L{cx0} {ky + 22} '
               f'L{cx0 + 9} {ky + 40} L{cx0 + 18} {ky + 28} L{cx0 + 18} {ky + 52} Z" fill="{PAPER}" '
               f'stroke="{GOLD_EDGE}" stroke-width="1.5"/>')
    out.append(text(lanes[1][0] + 66, ky + 26, "THE KING COMES", 17, weight="bold", spacing="1.5"))
    out.append(text(lanes[1][0] + 66, ky + 46, "with the armies of heaven, to the earth", 14))
    out.append(text(lanes[1][0] + 66, ky + 65, "Rev 19:11-16 · Matt 24:29-30 · Zech 14:4", 12.5,
                    fill=MUTED, italic=True))
    out.append(text(40, ky + 62, "“immediately after", 13, italic=True))
    out.append(text(40, ky + 78, "the tribulation”", 13, italic=True))
    out.append(text(40, ky + 94, "Matthew 24:29", 12, fill=MUTED, italic=True))

    my = ky + 104
    out.append(f'<rect x="{lanes[0][0]}" y="{my}" width="{lanes[2][1] - lanes[0][0]}" height="32" '
               f'fill="{GOLD_TINT}" stroke="{GOLD_EDGE}"/>')
    out.append(text(W / 2, my + 21, "THE THOUSAND YEARS · REVELATION 20:1-6", 14, "middle", "bold",
                    spacing="1.5"))

    out += legend_row(70, h - 84)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 2. Seals, trumpets and bowls: each seventh opens the next seven


SEALS = [
    ("White horse", "a rider with a bow", "6:1-2", "#f7f4ea"),
    ("Red horse", "peace taken away", "6:3-4", "#a8322d"),
    ("Black horse", "famine, scales", "6:5-6", "#2b2622"),
    ("Pale horse", "Death and Hades", "6:7-8", "#a3ad92"),
    ("Under the altar", "“How long?”", "6:9-11", RED),
    ("Great earthquake", "sky rolled up", "6:12-17", RED),
    ("Silence in heaven", "trumpets given", "8:1-2", RED),
]
TRUMPETS = [
    ("Hail and fire", "a third of the earth", "8:7"),
    ("Burning mountain", "a third of the sea", "8:8-9"),
    ("Wormwood", "a third of the waters", "8:10-11"),
    ("Lights struck", "a third of sun, moon", "8:12"),
    ("Locusts · woe 1", "five months' torment", "9:1-11"),
    ("Army · woe 2", "a third of mankind", "9:13-21"),
    ("Seventh trumpet", "the kingdom proclaimed", "11:15-19"),
]
BOWLS = [
    ("Sores", "on those with the mark", "16:2", "#8a6a3a"),
    ("The sea", "every living thing died", "16:3", "#7a1c1c"),
    ("Rivers, springs", "turned to blood", "16:4-7", "#9b2b2b"),
    ("The sun", "scorching heat", "16:8-9", "#d9a531"),
    ("Beast's throne", "darkness", "16:10-11", "#2b2622"),
    ("Euphrates dried", "kings gather", "16:12-16", BLUE),
    ("Into the air", "“It is done!”", "16:17-21", "#7d7d86"),
]


def seal_glyph(cx, cy, i, fill):
    numeral = "I II III IV V VI VII".split()[i]
    ink = PAPER if fill not in ("#f7f4ea", "#a3ad92") else INK
    # A wax seal: a scalloped disc.
    pts = []
    for k in range(32):
        r = 24 if k % 2 == 0 else 21.5
        a = math.pi * 2 * k / 32
        pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return [f'<path d="M{" L".join(pts)} Z" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>',
            text(cx, cy + 5, numeral, 14, "middle", "bold", fill=ink)]


def trumpet_glyph(cx, cy, i):
    return [f'<circle cx="{cx}" cy="{cy}" r="23" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>',
            f'<path d="M{cx - 15} {cy + 2} L{cx + 6} {cy - 3} L{cx + 15} {cy - 10} L{cx + 15} {cy + 10} '
            f'L{cx + 6} {cy + 3} Z" fill="{GOLD_EDGE}"/>',
            text(cx - 10, cy + 17, str(i + 1), 11, "middle", "bold", fill=INK)]


def bowl_glyph(cx, cy, i, fill):
    return [f'<circle cx="{cx}" cy="{cy}" r="23" fill="{RED_TINT}" stroke="{RED}" stroke-width="1.4"/>',
            f'<path d="M{cx - 15} {cy - 4} H{cx + 15} A15 13 0 0 1 {cx - 15} {cy - 4} Z" fill="{fill}" stroke="{INK}" stroke-width="1"/>',
            f'<path d="M{cx - 7} {cy - 7} q4 -6 0 -10 M{cx + 3} {cy - 7} q4 -6 0 -10" fill="none" stroke="{RED}" stroke-width="1.3"/>',
            text(cx, cy + 19, str(i + 1), 10, "middle", "bold", fill=INK)]


def pie(cx, cy, r, frac, fill, label):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>']
    if frac >= 1:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>')
    else:
        a = 2 * math.pi * frac
        x, y = cx + r * math.sin(a), cy - r * math.cos(a)
        large = 1 if frac > 0.5 else 0
        out.append(f'<path d="M{cx} {cy} L{cx} {cy - r} A{r} {r} 0 {large} 1 {x:.1f} {y:.1f} Z" '
                   f'fill="{fill}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(text(cx, cy + r + 20, label, 15, "middle", "bold"))
    return out


def judgments_unfolded():
    cols = [(24, 240), (252, 468), (480, 696)]
    R, IR = 70, 72
    seal_top = 300

    seal_y = [seal_top + i * R for i in range(6)] + [seal_top + 6 * R + IR]
    trum_y = [seal_y[6] + i * R for i in range(6)] + [seal_y[6] + 6 * R + IR]
    bowl_top = trum_y[6] + 72
    IB = 52                                      # Revelation 16:15, the one pause in the bowls
    bowl_y = [bowl_top + i * R for i in range(6)] + [bowl_top + 6 * R + IB]
    h = bowl_y[6] + 180

    out = svg_open(
        h,
        "The judgments unfolded",
        "A cascading chart of Revelation's three series of judgments. The seven seals run down the "
        "left: the white, red, black and pale horses, the martyrs under the altar, the great "
        "earthquake, and the seventh seal, silence in heaven, when seven trumpets are given "
        "(Revelation 8:1-2). From the seventh seal a bracket opens the seven trumpets in the middle "
        "column: hail and fire, a burning mountain, Wormwood, the lights struck, the locusts, the "
        "army from the Euphrates, and the seventh trumpet proclaiming the kingdom (Revelation "
        "11:15). From the seventh trumpet a bracket opens the seven bowls on the right, after "
        "chapters 12 to 14, which step back to show the woman, the dragon and the beasts: sores, the "
        "sea, the rivers, the sun, the beast's throne, the Euphrates dried, and the seventh bowl "
        "poured into the air with the cry 'It is done!' (Revelation 16:17). The pauses are marked: "
        "chapter 7 between the sixth and seventh seals, 10:1-11:14 between the sixth and seventh "
        "trumpets, and between the sixth and seventh bowls a single verse, Jesus' warning 'Behold, I "
        "am coming like a thief!' (Revelation 16:15). "
        "Three circles show the reach growing: a fourth of the earth under the seals (Revelation "
        "6:8), a third under the trumpets (Revelation 8:7-12; 9:15), every living thing in the sea "
        "under the bowls (Revelation 16:3). An inset shows the other reading, in which the three "
        "series retell one period. The King comes at the foot (Revelation 19:11-16).",
    )
    out += heading("The Judgments Unfolded",
                   "Each seventh opens the next seven (Revelation 8:1-2; 11:15; 15:1)")

    # The reach, growing: top right, where the later columns have not yet begun.
    px = cols[1][0]
    out.append(f'<rect x="{px}" y="{seal_top - 160}" width="{cols[2][1] - px}" height="300" rx="8" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="1"/>')
    out.append(text((px + cols[2][1]) / 2, seal_top - 132, "HOW FAR EACH SERIES REACHES", 14,
                    "middle", "bold", spacing="1.5"))
    for k, (frac, fill, lab, sub, ref) in enumerate([
        (0.25, "#a3ad92", "a fourth", "of the earth", "Revelation 6:8"),
        (1 / 3, GOLD, "a third", "earth, sea, mankind", "Revelation 8:7-12; 9:15"),
        (1.0, RED, "every", "living thing in the sea", "Revelation 16:3"),
    ]):
        cx = px + 74 + k * 148
        out += pie(cx, seal_top - 74, 34, frac, fill, lab)
        out.append(text(cx, seal_top - 1, sub, 12.5, "middle"))
        out.append(text(cx, seal_top + 15, ref, 11.5, "middle", fill=MUTED, italic=True))
    out.append(text((px + cols[2][1]) / 2, seal_top + 52, "“…seven plagues, which are the last, for with", 13.5,
                    "middle", italic=True))
    out.append(text((px + cols[2][1]) / 2, seal_top + 70, "them the wrath of God is finished” (Revelation 15:1, ESV)",
                    13.5, "middle", italic=True))
    out.append(text((px + cols[2][1]) / 2, seal_top + 100, "“They did not repent”: 9:20, 21; 16:9, 11",
                    13.5, "middle", weight="bold", fill=RED))

    def header(col, y, title, ref, fill):
        a, b = cols[col]
        r = banner((a + b) / 2, y, b - a - 30, title, fill=fill, size=14)
        r.append(text((a + b) / 2, y + 46, ref, 13, "middle", fill=MUTED, italic=True))
        return r

    def row(col, y, glyph, title, sub, ref):
        a, _ = cols[col]
        r = list(glyph)
        r.append(text(a + 64, y - 6, title, 14.5, weight="bold"))
        r.append(text(a + 64, y + 11, sub, 13.5))
        r.append(text(a + 64, y + 27, ref, 12, fill=MUTED, italic=True))
        return r

    def interlude(col, y, title, sub):
        a, b = cols[col]
        return [f'<rect x="{a + 6}" y="{y - 26}" width="{b - a - 12}" height="46" rx="4" fill="{BLUE_TINT}" '
                f'stroke="{BLUE}" stroke-dasharray="4 3"/>',
                text(a + 16, y - 7, title, 13, weight="bold", fill=BLUE),
                text(a + 16, y + 11, sub, 12.5, fill=BLUE)]

    def opens(col_from, y_from, col_to, y_first, y_last, label):
        """The bracket: from the seventh glyph, across, then down the whole next series."""
        xa = cols[col_from][0] + 34
        xb = cols[col_to][0] + 4
        yl = y_from - 26
        r = [f'<path d="M{xa} {y_from - 24} V{yl} H{xb - 4}" fill="none" stroke="{INK}" stroke-width="2"/>',
             f'<path d="M{xb - 4} {yl} V{y_last}" stroke="{INK}" stroke-width="2"/>',
             f'<path d="M{xb - 4} {y_last} H{xb + 4}" stroke="{INK}" stroke-width="2"/>',
             arrow_head(xb + 8, y_first, 0, 10)]
        r.append(f'<path d="M{xb - 4} {y_first} H{xb + 4}" stroke="{INK}" stroke-width="2"/>')
        r.append(text(xa + 40, yl - 6, label, 12, italic=True, fill=MUTED))
        return r

    out += header(0, seal_top - 84, "SEVEN SEALS", "Revelation 6:1–8:1", INK)
    for i, (t, s, ref, fill) in enumerate(SEALS):
        out += row(0, seal_y[i], seal_glyph(cols[0][0] + 34, seal_y[i], i, fill), t, s, ref)
    out += interlude(0, (seal_y[5] + seal_y[6]) / 2 + 4, "Interlude · ch. 7", "the sealed; the multitude")

    out += header(1, trum_y[0] - 100, "SEVEN TRUMPETS", "Revelation 8:2–11:19", GOLD_EDGE)
    for i, (t, s, ref) in enumerate(TRUMPETS):
        out += row(1, trum_y[i], trumpet_glyph(cols[1][0] + 34, trum_y[i], i), t, s, ref)
    out += interlude(1, (trum_y[5] + trum_y[6]) / 2 + 4, "Interlude · 10:1–11:14",
                     "little scroll; two witnesses")

    out += header(2, bowl_top - 190, "SEVEN BOWLS", "Revelation 15:1–16:21", RED)
    out += interlude(2, bowl_top - 92, "Before the bowls · chs. 12–14", "steps back: woman, dragon, beasts")
    a2, b2 = cols[2]
    py = (bowl_y[5] + bowl_y[6]) / 2 + 2
    out += [f'<rect x="{a2 + 6}" y="{py - 20}" width="{b2 - a2 - 12}" height="36" rx="4" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}"/>',
            text(a2 + 16, py - 4, "16:15 · the one pause:", 12.5, weight="bold", fill=GOLD_EDGE),
            text(a2 + 16, py + 11, "“Behold, I am coming like a thief!”", 12, italic=True)]
    for i, (t, s, ref, fill) in enumerate(BOWLS):
        out += row(2, bowl_y[i], bowl_glyph(cols[2][0] + 34, bowl_y[i], i, fill), t, s, ref)

    out += opens(0, seal_y[6], 1, trum_y[0], trum_y[6] + 30, "opens the trumpets")
    out += opens(1, trum_y[6], 2, bowl_y[0], bowl_y[6] + 30, "opens the bowls")

    # The other reading, in the space the cascade leaves at the lower left.
    ix, iy, iw = cols[0][0] + 6, seal_y[6] + 80, cols[0][1] - cols[0][0] - 12
    out.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="330" rx="6" fill="{CARD}" stroke="{MUTED}" '
               f'stroke-dasharray="5 4"/>')
    out.append(text(ix + iw / 2, iy + 24, "ANOTHER READING", 13, "middle", "bold", spacing="1.5", fill=MUTED))
    out.append(text(ix + iw / 2, iy + 44, "recapitulation", 13.5, "middle", italic=True, fill=MUTED))
    for k, (lab, fill) in enumerate([("Seals", INK), ("Trumpets", GOLD_EDGE), ("Bowls", RED)]):
        y = iy + 80 + k * 42
        out.append(text(ix + 12, y + 5, lab, 13, weight="bold"))
        out.append(f'<rect x="{ix + 84}" y="{y - 7}" width="{iw - 100}" height="14" fill="{fill}" opacity="0.75"/>')
    out.append(f'<path d="M{ix + iw - 16} {iy + 62} V{iy + 182}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 3"/>')
    out.append(text(ix + iw - 16, iy + 200, "the end", 12, "middle", italic=True))
    for k, ln in enumerate(["Three tellings of one", "period, each reaching", "the end (6:12-17;",
                            "11:15-18; 16:17-21).", "This study follows the", "cascade: each seventh",
                            "holds the next seven."]):
        out.append(text(ix + 12, iy + 228 + k * 15, ln, 12.5))

    # The end of the cascade.
    ky = bowl_y[6] + 70
    out.append(f'<rect x="{cols[1][0]}" y="{ky}" width="{cols[2][1] - cols[1][0]}" height="62" rx="6" '
               f'fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>')
    out.append(text((cols[1][0] + cols[2][1]) / 2, ky + 27, "THE KING COMES", 17, "middle", "bold", spacing="1.5"))
    out.append(text((cols[1][0] + cols[2][1]) / 2, ky + 48, "Babylon fallen (17–18) · Revelation 19:11-16",
                    13, "middle", fill=INK, italic=True))
    out.append(f'<path d="M{cols[2][0] + 34} {bowl_y[6] + 30} V{ky - 4}" stroke="{INK}" stroke-width="2"/>')
    out.append(arrow_head(cols[2][0] + 34, ky - 2, 90, 10))

    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 3. The week in days: Revelation's three measures, and Daniel's 1,290 and 1,335


def week_in_days():
    x0, xm, x1 = 40, 320, 600           # day 1, day 1,260, day 2,520
    tail = 0.88                         # the 75 days after the week, drawn larger
    per = (x1 - x0) / 2520

    def X(day):
        return x0 + day * per if day <= 2520 else x1 + 14 + (day - 2520) * tail

    rows_top, rh = 272, 62
    h = rows_top + 7 * rh + 170
    out = svg_open(
        h,
        "The week in days",
        "A ruler of Daniel's seventieth week, 2,520 days, split at day 1,260. Under the second half "
        "run the spans Scripture counts: the woman nourished in the wilderness 1,260 days "
        "(Revelation 12:6); a time, times and half a time (Daniel 7:25; 12:7; Revelation 12:14); "
        "the beast's forty-two months (Revelation 13:5); the holy city trampled forty-two months "
        "(Revelation 11:2). The two witnesses' 1,260 days (Revelation 11:3) are drawn dashed over "
        "either half, since the text does not say which. Two of Daniel's counts run from the "
        "abomination past the end of the week: 1,290 days (Daniel 12:11), thirty days beyond it, "
        "and 1,335 days (Daniel 12:12), forty-five more, drawn on an enlarged scale after a break. "
        "A note gives the arithmetic: forty-two months of thirty days and three and a half years "
        "of 360 days are both 1,260 days.",
    )
    out += heading("The Week in Days", "One span, counted three ways, and Daniel's two extra counts")

    by = 178
    out.append(f'<path d="M{x0} {by - 18} V{by - 26} H{x1} V{by - 18}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    out.append(text((x0 + x1) / 2, by - 34, "ONE WEEK · SEVEN YEARS · DANIEL 9:27", 14, "middle", "bold", spacing="1.5"))
    out.append(f'<rect x="{x0}" y="{by}" width="{xm - x0}" height="34" fill="{GOLD_TINT}" stroke="{INK}"/>')
    out.append(f'<rect x="{xm}" y="{by}" width="{x1 - xm}" height="34" fill="{RED_TINT}" stroke="{INK}"/>')
    out.append(text((x0 + xm) / 2, by + 22, "First half", 15, "middle", "bold"))
    out.append(text((xm + x1) / 2, by + 22, "“Great tribulation”", 15, "middle", "bold", fill=RED))
    out.append(f'<path d="M{x1 + 3} {by + 24} l4 -14 M{x1 + 8} {by + 24} l4 -14" stroke="{MUTED}" stroke-width="1.2"/>')
    out.append(f'<rect x="{X(2520)}" y="{by + 10}" width="{X(2595) - X(2520):.1f}" height="14" fill="{PAPER}" '
               f'stroke="{MUTED}" stroke-dasharray="3 2"/>')
    out.append(text(X(2558), by - 14, "+75 days,", 11.5, "middle", fill=MUTED, italic=True))
    out.append(text(X(2558), by - 2, "drawn larger", 11.5, "middle", fill=MUTED, italic=True))
    out.append(text(X(0), by + 54, "day 1", 13, "start", fill=RED, weight="bold"))
    out.append(text(xm - 5, by + 54, "1,260", 13, "end", fill=RED, weight="bold"))
    out.append(text(X(2520), by + 54, "2,520", 13, "middle", fill=RED, weight="bold"))

    out.append(f'<path d="M{xm} {by - 12} V{rows_top + 7 * rh}" stroke="{RED}" stroke-width="2.5"/>')
    out.append(text(xm + 6, by + 78, "The abomination · Daniel 9:27; Matthew 24:15", 13, fill=RED, italic=True))

    def bar(i, a, b, label, ref, dashed=False, color=INK):
        y = rows_top + i * rh + 34
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        return [f'<path d="M{X(a):.1f} {y} H{X(b):.1f}" stroke="{color}" stroke-width="5"{dash}/>',
                f'<path d="M{X(a):.1f} {y - 8} V{y + 8} M{X(b):.1f} {y - 8} V{y + 8}" stroke="{color}" stroke-width="2"/>',
                text(X(a) + 4 if a else x0, y - 12, label, 14, weight="bold", fill=color, extra=HALO),
                text(X(a) + 4 if a else x0, y + 21, ref, 12.5, fill=MUTED, italic=True)]

    out += bar(0, 1260, 2520, "1,260 days · the woman sheltered", "Revelation 12:6")
    out += bar(1, 1260, 2520, "A time, times and half a time", "Daniel 7:25; 12:7; Revelation 12:14")
    out += bar(2, 1260, 2520, "42 months · the beast's authority", "Revelation 13:5")
    out += bar(3, 1260, 2520, "42 months · the holy city trampled", "Revelation 11:2")
    y4 = rows_top + 4 * rh + 34
    out += [f'<path d="M{X(0)} {y4} H{xm - 16}" stroke="{BLUE}" stroke-width="5" stroke-dasharray="7 5"/>',
            f'<path d="M{xm + 16} {y4} H{X(2520)}" stroke="{BLUE}" stroke-width="5" stroke-dasharray="7 5"/>',
            f'<path d="M{X(0)} {y4 - 8} V{y4 + 8} M{X(2520)} {y4 - 8} V{y4 + 8}" stroke="{BLUE}" stroke-width="2"/>',
            text(xm, y4 + 5, "or", 14, "middle", "bold", fill=BLUE, extra=HALO),
            text(x0, y4 - 12, "1,260 days · the two witnesses: which half?", 14, weight="bold", fill=BLUE,
                 extra=HALO),
            text(x0, y4 + 21, "Revelation 11:3 · unstated; the cascade favours the first", 12.5, fill=MUTED, italic=True)]
    out += bar(5, 1260, 2550, "1,290 days from the abomination", "Daniel 12:11 · thirty days past the end",
               color=RED)
    out += bar(6, 1260, 2595, "1,335 days · “Blessed is he who waits”", "Daniel 12:12 · forty-five days more",
               color=RED)

    ny = rows_top + 7 * rh + 22
    out.append(f'<rect x="40" y="{ny}" width="{W - 80}" height="96" rx="6" fill="{CARD}" stroke="{INK}"/>')
    out.append(text(W / 2, ny + 28, "42 months × 30 days = 1,260 days = 3½ years × 360 days", 15, "middle", "bold"))
    out.append(text(W / 2, ny + 52, "The three measures agree only on a 360-day prophetic year.", 13.5, "middle"))
    out.append(text(W / 2, ny + 74, "Daniel does not say what the extra 30 and 45 days hold.", 13.5, "middle",
                    italic=True, fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 4. Church, saints, tribulation and repentance, chapter by chapter


# Verses per chapter, SBLGNT (macula-greek-sblgnt). The queries are in the state file.
EKKLESIA = {1: 4, 2: 9, 3: 6, 22: 1}                                          # G1577, 20
THLIPSIS = {1: 1, 2: 3, 7: 1}                                                  # G2347, 5
HAGIOI = {5: 1, 8: 2, 11: 1, 13: 2, 14: 1, 16: 1, 17: 1, 18: 2, 19: 1, 20: 1}  # G40 "saints", 13
REPENT_CALL = {2: 5, 3: 2}                  # G3340 in the letters: a call or a warning
REPENT_REFUSED = {2: 1, 9: 2, 16: 2}         # 2:21b "she refuses to repent"; 9:20-21; 16:9, 11, all negated


def church_and_saints():
    lx, cx0, cx1 = 24, 176, 696
    cw = (cx1 - cx0) / 22

    def CX(ch):
        return cx0 + (ch - 0.5) * cw

    h = 820
    out = svg_open(
        h,
        "Church and saints in Revelation",
        "A chapter-by-chapter count of four Greek words across Revelation's twenty-two chapters, "
        "one dot per occurrence, under the book's own division (Revelation 1:19): what John has "
        "seen (chapter 1), what is (chapters 2 and 3), and what must take place after this "
        "(chapters 4 to 22), opened at 4:1 by a door in heaven. The judgments of chapters 6 to 19 "
        "are shaded. ekklesia, church, occurs twenty times: nineteen in chapters 1 to 3 and once in "
        "22:16, and not at all in between. hagioi, saints, occurs thirteen times, all in chapters "
        "5 to 20. thlipsis, tribulation, occurs five times: four in chapters 1 and 2, where it is "
        "the churches' present suffering, and once in 7:14, 'the great tribulation'. metanoeo, "
        "repent, occurs eight times in the letters, as a call or a warning to the churches and once "
        "already refused, 'she refuses to repent' (2:21), and four times in chapters 9 and 16, where "
        "every one is 'they did not repent'.",
    )
    out += heading("Church and Saints in Revelation", "One dot for each occurrence, chapter by chapter (SBLGNT)")

    # Revelation 1:19's three parts.
    ty = 128
    for a, b, lab in ((1, 1, "seen"), (2, 3, "what is"), (4, 22, "“what must take place after this” (4:1)")):
        xa, xb = cx0 + (a - 1) * cw + 2, cx0 + b * cw - 2
        out.append(f'<path d="M{xa:.1f} {ty + 10} V{ty} H{xb:.1f} V{ty + 10}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        out.append(text((xa + xb) / 2, ty - 8, lab, 13 if b > 1 else 11.5, "middle", italic=True))
    out.append(text(lx, ty + 4, "Revelation 1:19", 13, weight="bold"))

    # Chapter numbers, the door at 4:1, and the judgments shaded.
    ny = 168
    jy0, jy1 = ny + 12, h - 160
    out.append(f'<rect x="{cx0 + 5 * cw:.1f}" y="{jy0}" width="{14 * cw:.1f}" height="{jy1 - jy0}" fill="{RED_TINT}" opacity="0.7"/>')
    out.append(text(cx0 + 12 * cw, jy1 - 8, "the judgments · chapters 6–19", 13, "middle", italic=True, fill=RED))
    out.append(f'<path d="M{cx0 + 3 * cw:.1f} {ny - 14} V{jy1}" stroke="{GOLD_EDGE}" stroke-width="2" stroke-dasharray="5 3"/>')
    out.append(text(cx0 + 3 * cw + 4, jy1 + 18, "4:1 “Come up here”", 12.5, fill=GOLD_EDGE, weight="bold"))
    for ch in range(1, 23):
        out.append(text(CX(ch), ny, str(ch), 12.5, "middle", fill=MUTED, weight="bold"))

    def dot_row(y_base, counts, label, gloss, total, fill, hollow=None):
        r = [f'<path d="M{cx0} {y_base + 8} H{cx1}" stroke="{MUTED}" stroke-width="0.6"/>',
             text(lx, y_base - 14, label, 17, weight="bold"),
             text(lx, y_base + 4, gloss, 13, italic=True, fill=MUTED),
             text(lx, y_base + 20, total, 12.5, fill=MUTED)]
        for ch, n in counts.items():
            for k in range(n):
                r.append(f'<circle cx="{CX(ch):.1f}" cy="{y_base - k * 10.5:.1f}" r="4.4" fill="{fill}"/>')
        for ch, n in (hollow or {}).items():
            for k in range(counts.get(ch, 0), counts.get(ch, 0) + n):
                r.append(f'<circle cx="{CX(ch):.1f}" cy="{y_base - k * 10.5:.1f}" r="4" fill="{PAPER}" '
                         f'stroke="{RED}" stroke-width="1.6"/>')
        return r

    out += dot_row(ny + 128, EKKLESIA, "ἐκκλησία", "ekklēsia, “church”", "G1577 · 20 times", GOLD_EDGE)
    out += dot_row(ny + 220, HAGIOI, "ἅγιοι", "hagioi, “saints”", "G40 · 13 times", BLUE)
    out += dot_row(ny + 312, THLIPSIS, "θλῖψις", "thlipsis, “tribulation”", "G2347 · 5 times", INK)
    out += dot_row(ny + 410, REPENT_CALL, "μετανοέω", "metanoeō, “repent”", "G3340 · 12 times", INK,
                   hollow=REPENT_REFUSED)

    out.append(text(CX(7) + 8, ny + 296, "7:14 “the great tribulation”", 12, italic=True))
    out.append(text(CX(22) - 6, ny + 106, "22:16", 12, "end", italic=True))
    out.append(text(CX(9) + 10, ny + 378, "○ refused: 2:21; “they did not repent”", 12.5, fill=RED, weight="bold"))

    ky = h - 108
    out.append(f'<circle cx="{lx + 10}" cy="{ky}" r="4.4" fill="{GOLD_EDGE}"/>')
    out.append(text(lx + 22, ky + 5, "Pretribulational reading: the church, named nineteen times to the end of", 13))
    out.append(text(lx + 22, ky + 22, "chapter 3, is in heaven while chapters 6–19 unfold on earth.", 13))
    out.append(f'<circle cx="{lx + 10}" cy="{ky + 44}" r="4.4" fill="{BLUE}"/>')
    out.append(text(lx + 22, ky + 49, "Other readers: the “saints” of chapters 5–20 are the church on earth.", 13))
    out.append(text(lx + 22, ky + 66, "A count shows where a word is; it cannot say who the saints are.", 13,
                    italic=True, fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("seventieth-week", seventieth_week), ("judgments-unfolded", judgments_unfolded),
                     ("week-in-days", week_in_days), ("church-and-saints", church_and_saints)):
        (OUT / f"{name}.svg").write_text(fn() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
