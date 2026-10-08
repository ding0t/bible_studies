"""Draw the Larkin-style charts for the last-things/ studies other than the tribulation study, and
for the Zadok calendar page their chronology runs on (written to assets/img/feasts/).

Same hand as utils/build_tribulation_graphics.py (both draw with utils/lib/larkin.py) and the same
confidence code: a solid outline is dated or stated by the text, a dashed one is this site's
inference. Each chart follows the study it sits in; if the study changes its reading, change the
chart here and re-run from the repo root:

    python3 utils/build_last_things_graphics.py            # all of them
    python3 utils/build_last_things_graphics.py seventy-weeks

seven_thousand_years() reads its dates from docs/data/chronology.json, the site's one chronology,
so the chart cannot drift from Chronology Anchors. Run it again after that file changes.
"""

import datetime
import json
import math
import re
import sys
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, HALO, esc, text, svg_open, heading, banner, cloud, arrow_head,
                        card, legend_row, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "last-things"
CHRONOLOGY = ROOT / "docs" / "data" / "chronology.json"

WATER = "#5b7fa6"
FIRE = "#c4471c"


def lines_at(x, y, rows, size=13.5, lh=17, anchor="start", **kw):
    return [text(x, y + i * lh, r, size, anchor, **kw) for i, r in enumerate(rows)]


def person(cx, cy, s=1.0, fill=INK):
    """A stick figure standing on (cx, cy)."""
    return (f'<g stroke="{fill}" stroke-width="{2 * s:.1f}" fill="none" stroke-linecap="round">'
            f'<circle cx="{cx}" cy="{cy - 26 * s:.1f}" r="{5 * s:.1f}" fill="{fill}"/>'
            f'<path d="M{cx} {cy - 21 * s:.1f} V{cy - 9 * s:.1f} M{cx - 7 * s:.1f} {cy - 17 * s:.1f} '
            f'H{cx + 7 * s:.1f} M{cx} {cy - 9 * s:.1f} L{cx - 5 * s:.1f} {cy} M{cx} {cy - 9 * s:.1f} '
            f'L{cx + 5 * s:.1f} {cy}"/></g>')


def waves(x0, x1, y, amp=4, period=18, color=WATER, width=2):
    pts, x = [f"M{x0} {y}"], x0
    while x + period <= x1:
        pts.append(f"q{period / 4} {-amp} {period / 2} 0 t{period / 2} 0")
        x += period
    return f'<path d="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{width}"/>'


def flames(x0, x1, y, h=22, color=FIRE):
    out, x = [], x0
    while x < x1:
        out.append(f'<path d="M{x} {y} q4 {-h * 0.6} 0 {-h} q10 {h * 0.45} 8 {h} z" fill="{color}" opacity="0.85"/>')
        x += 12
    return "".join(out)


def bracket_note(x, y, w, rows, fill=CARD, stroke=INK, dashed=False, size=13.5, bold_first=True):
    h = 14 + 17 * len(rows)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}"{dash}/>']
    for i, r in enumerate(rows):
        out.append(text(x + 12, y + 21 + 17 * i, r, size, weight="bold" if (i == 0 and bold_first) else None))
    return out, h


# ---------------------------------------------------------------------------------------------
# 1. The seven thousand years, on this site's chronology (prophecy-chart.md, day-is-a-thousand-years.md)


def am_label(am):
    """AM 3959 is AD 1 (chronology.json, epochs[0]); there is no year zero."""
    return f"{3959 - am} BC" if am < 3959 else f"AD {am - 3958}"


DAY_THEMES = [
    ("Light from darkness", "Genesis 1:3-5"),
    ("The waters divided", "Genesis 1:6-8"),
    ("Dry land and seed", "Genesis 1:9-13"),
    ("Lights for the appointed times", "Genesis 1:14-19"),
    ("The swarming sea of the nations", "Genesis 1:20-23"),
    ("The image, and its counterfeit", "Genesis 1:24-31"),
    ("The rest that is numbered", "Genesis 2:1-3"),
]

# id in chronology.json -> the short label the chart prints. The year always comes from the file.
CHART_EVENTS = {
    "creation": "Creation",
    "adam_dies": "Adam dies",
    "enoch_taken": "Enoch taken",
    "flood": "The Flood",
    "babel": "Babel",
    "abram_called": "Abram called",
    "jacob_to_egypt": "Into Egypt",
    "exodus_early_date": "The Exodus",
    "anchor_01": "Temple begun",
    "anchor_03": "Kingdom divides",
    "anchor_12": "Jerusalem falls",
    "anchor_15": "Cyrus's decree",
    "anchor_37": "Nativity",
    "anchor_41": "The cross",
}


def chronology_events():
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    found = {}
    for key in ("genesis_markers", "milestones", "anchor_table"):
        for e in data[key]:
            if e["id"] in CHART_EVENTS:
                if "am_year" in e:
                    am = e["am_year"]
                elif "zadok_year" in e:
                    am = e["zadok_year"]
                else:
                    am = e["gregorian_year"] + 3959 if e["gregorian_year"] < 0 else e["gregorian_year"] + 3958
                found[e["id"]] = (am, CHART_EVENTS[e["id"]])
    missing = set(CHART_EVENTS) - set(found)
    assert not missing, f"chronology.json no longer has {missing}"
    events = sorted(found.values())
    events.append((70 + 3958, "Temple destroyed"))      # AD 70 (Daniel 9:26), not in the anchor table
    return events


def seven_thousand_years():
    events = chronology_events()
    today_am = datetime.date.today().year + 3958
    events.append((today_am, "Today"))
    events.sort()

    bx0, bx1 = 168, 692
    per = (bx1 - bx0) / 1000
    top, bh = 118, 150
    h = top + 7 * bh + 196

    out = svg_open(
        h,
        "The seven thousand years",
        "A chart of history as a week of seven thousand-year days, on this site's chronology "
        "(creation 3959 BC, Masoretic numbers, Exodus 1446 BC). Each day is a band with its theme "
        "from Genesis 1 and its years. Day 1: creation, Adam dies AM 930, Enoch taken AM 987. Day 2: "
        "the Flood AM 1656, Babel. Day 3: Abram's call, Jacob into Egypt, the Exodus in 1446 BC. Day "
        "4: the temple begun in 966 BC, the kingdom divided, Jerusalem's fall in 586 BC, Cyrus's "
        "decree, the Nativity, and the cross in AD 33. Day 5: the temple destroyed in AD 70 and the "
        "gospel to the nations. Day 6 runs to the year 6000, AD 2042 on this chronology, with today "
        "marked. Day 7 is the thousand years of Revelation 20. An eighth day, the new heaven and new "
        "earth, opens beyond it. A note says the shape is Scripture's and the matching of days to "
        "millennia is this site's reading, and that the year 6000 is no date for Christ's return.",
    )
    out += heading("The Seven Thousand Years",
                   "“With the Lord one day is as a thousand years” (2 Peter 3:8, ESV)")

    for d in range(7):
        y = top + d * bh
        am0 = d * 1000
        mill = d == 6
        fill = GOLD if mill else (EARTH_TINT if d % 2 == 0 else GOLD_TINT)
        out.append(f'<path d="M24 {y} H{W - 24}" stroke="{INK}" stroke-width="0.6"/>')
        out.append(text(28, y + 34, f"DAY {d + 1}", 22, weight="bold", spacing="1.5",
                        fill=GOLD_EDGE if mill else INK))
        out.append(text(28, y + 54, f"AM {am0:,}–{am0 + 1000:,}", 12.5, fill=MUTED))
        out.append(text(28, y + 70, f"{am_label(am0)} –", 12.5, fill=MUTED))
        out.append(text(28, y + 86, am_label(am0 + 1000), 12.5, fill=MUTED))
        theme, ref = DAY_THEMES[d]
        out.append(text(28, y + 110, theme if len(theme) < 20 else theme.rsplit(" ", 2)[0], 12.5,
                        italic=True))
        if len(theme) >= 20:
            out.append(text(28, y + 125, theme.rsplit(" ", 2)[1] + " " + theme.rsplit(" ", 2)[2], 12.5,
                            italic=True))
        out.append(text(28, y + 140, ref, 11.5, fill=MUTED, italic=True))

        by = y + 64
        out.append(f'<rect x="{bx0}" y="{by}" width="{bx1 - bx0}" height="24" fill="{fill}" stroke="{INK}"/>')
        for c in range(1, 10):
            out.append(f'<path d="M{bx0 + c * 100 * per:.1f} {by} v5 M{bx0 + c * 100 * per:.1f} {by + 24} v-5" '
                       f'stroke="{INK}" stroke-width="0.7"/>')
        if mill:
            out.append(text((bx0 + bx1) / 2, by + 17, "THE THOUSAND YEARS · REVELATION 20:2-7", 13.5,
                            "middle", "bold", spacing="1"))
            out += lines_at((bx0 + bx1) / 2, by + 50, ["Christ reigns; Satan bound (Revelation 20:2-4);",
                                                       "the Sabbath rest still to come (Hebrews 4:9)"],
                            13, anchor="middle", italic=True)
            continue

        # Markers: alternate above and below the bar, and stack a second row where labels would touch.
        marks = [(am - am0, lab, am) for am, lab in events if am0 <= am < am0 + 1000]
        last_end = {(-1, 0): -999, (-1, 1): -999, (1, 0): -999, (1, 1): -999}
        side = -1
        for k, (off, lab, am) in enumerate(marks):
            x = bx0 + off * per
            label = f"{lab} · {am_label(am)}" if lab not in ("Creation",) else "Creation · 3959 BC"
            wlab = len(label) * 6.4
            anchor = "start" if x + wlab < bx1 + 4 else "end"
            lx0 = x - 2 if anchor == "start" else x - wlab
            for tier in (0, 1):
                if lx0 > last_end[(side, tier)] + 6:
                    break
            else:
                side, tier = -side, 0
            last_end[(side, tier)] = lx0 + wlab
            ly = by - 10 - tier * 17 if side < 0 else by + 40 + tier * 17
            color = RED if lab in ("The cross", "Today") else INK
            out.append(f'<path d="M{x:.1f} {by - (2 if side < 0 else -26)} V{ly + (4 if side < 0 else -12)}" '
                       f'stroke="{color}" stroke-width="1"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{by + 12}" r="4" fill="{color}" stroke="{PAPER}"/>')
            out.append(text(x + (4 if anchor == "start" else -4), ly, label, 12.5, anchor,
                            "bold" if lab in ("The cross", "The Flood", "The Exodus", "Today") else None,
                            fill=color, extra=HALO))
            side = -side
        if d == 4:
            out.append(text((bx0 + bx1) / 2, by + 17, "the gospel over the sea of the nations", 12.5,
                            "middle", italic=True))
        if d == 5:
            out.append(text(bx1 - 4, by - 30, "Year 6000 · AD 2042", 13, "end", "bold", fill=RED))
            out.append(f'<path d="M{bx1} {by - 26} V{by + 30}" stroke="{RED}" stroke-width="2.5"/>')

    ey = top + 7 * bh + 8
    out.append(f'<path d="M{bx0} {ey} H{bx1 - 10}" stroke="{GOLD_EDGE}" stroke-width="22"/>')
    out.append(arrow_head(bx1 + 10, ey, 0, 22, GOLD_EDGE))
    out.append(text(bx0 + 10, ey + 5, "THE EIGHTH DAY · A NEW HEAVEN AND NEW EARTH · REV 21:1", 12.5,
                    weight="bold", fill=PAPER, spacing="0.5"))
    out.append(text(28, ey + 5, "Beyond", 15, weight="bold", fill=GOLD_EDGE))

    ny = ey + 34
    note, nh = bracket_note(28, ny, W - 56, [
        "The shape is Scripture's: six days and a seventh (Exodus 20:11; Hebrews 4:9), and a thousand",
        "years numbered in Revelation 20. Matching each day to a millennium is this site's reading",
        "(A Day Is a Thousand Years). Year 6000 follows from the chronology; it is no date for His",
        "return, which Jesus kept hidden (Mark 13:32). Dates: Masoretic Genesis 5 and 11, Exodus 1446 BC.",
    ], bold_first=False, size=13)
    out += note
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 2. Two stages of His coming (rapture.md)


def two_stages():
    h = 850
    out = svg_open(
        h,
        "Two stages of His coming",
        "A chart of Christ's coming in two stages across Daniel's seventieth week. On the earth a line "
        "runs from the church age through the seven years to the thousand years. At the end of the "
        "church age a dashed arc rises to the clouds: He comes for His saints, who are caught up to "
        "meet Him in the air (1 Thessalonians 4:16-17; John 14:3); the arc is dashed because the "
        "rapture's timing is inferred. In heaven, above the seven years, are the judgment seat of "
        "Christ (2 Corinthians 5:10) and the marriage of the Lamb (Revelation 19:7-9). At the end of "
        "the seven years a solid arc descends: He comes with His saints to the earth (Revelation "
        "19:11-16; Colossians 3:4; Zechariah 14:4-5), a timing the text states, 'immediately after "
        "the tribulation' (Matthew 24:29). A table below sets the two side by side: direction, signs, "
        "who sees, judgment, resurrection, and whether the timing is stated.",
    )
    out += heading("Two Stages of His Coming", "For His saints, then with His saints")

    gy = 400                                  # the earth's line
    ca, wk0, wk1, ml = (40, 236), 256, 556, (576, 692)
    out += cloud(W / 2 + 10, 236, 520)
    out.append(text(W / 2 + 10, 128, "IN HEAVEN", 14, "middle", "bold", fill=GOLD_EDGE, spacing="2"))
    c, _ = card(wk0 + 6, 142, 140, ["Judgment seat", "of Christ"], "2 Cor 5:10", dashed=True, size=13)
    out += c
    c, _ = card(wk1 - 146, 142, 140, ["Marriage of", "the Lamb"], "Rev 19:7-9", size=13)
    out += c
    out += lines_at(412, 266, ["“so we will always be with the Lord”", "1 Thessalonians 4:17"], 13,
                    anchor="middle", italic=True)

    out.append(f'<rect x="{ca[0]}" y="{gy}" width="{ca[1] - ca[0]}" height="30" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    out.append(text((ca[0] + ca[1]) / 2, gy + 20, "THE CHURCH AGE", 13.5, "middle", "bold", spacing="1"))
    out.append(f'<rect x="{wk0}" y="{gy}" width="{wk1 - wk0}" height="30" fill="{RED_TINT}" stroke="{INK}"/>')
    out.append(f'<path d="M{(wk0 + wk1) / 2} {gy} v30" stroke="{RED}" stroke-width="2.5"/>')
    out.append(text((wk0 + wk1) / 2, gy + 20, "THE WEEK · 7 YEARS", 13.5, "middle", "bold", spacing="1", extra=HALO))
    out.append(f'<rect x="{ml[0]}" y="{gy}" width="{ml[1] - ml[0]}" height="30" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}"/>')
    out.append(text((ml[0] + ml[1]) / 2, gy + 20, "1,000 YEARS", 13, "middle", "bold"))
    out.append(text((wk0 + wk1) / 2, gy + 52, "Daniel 9:27 · on the earth", 12.5, "middle", italic=True, fill=MUTED))
    out.append(f'<path d="M24 {gy + 31} H{W - 24}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(text(28, gy + 64, "ON THE EARTH", 12.5, weight="bold", fill=MUTED, spacing="1.5"))

    # Stage one: up, dashed (inferred timing). Stage two: down, solid (stated timing).
    out.append(f'<path d="M{ca[1] - 10} {gy - 2} C{ca[1] - 10} 320 {wk0 - 10} 280 {wk0 + 16} 252" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3" stroke-dasharray="7 5"/>')
    out.append(arrow_head(wk0 + 18, 250, -45, 13, GOLD_EDGE))
    out += lines_at(40, 300, ["1 · FOR HIS SAINTS"], 14, weight="bold", fill=GOLD_EDGE)
    out += lines_at(40, 318, ["caught up to meet Him", "in the air", "1 Thess 4:16-17 · John 14:3"], 13)
    out.append(f'<path d="M{wk1 - 4} 252 C{wk1 + 30} 280 {ml[0] + 20} 330 {ml[0] + 24} {gy - 6}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="4"/>')
    out.append(arrow_head(ml[0] + 24, gy - 2, 88, 14, GOLD_EDGE))
    out += lines_at(wk1 - 16, 300, ["2 · WITH HIS SAINTS"], 14, anchor="end", weight="bold", fill=GOLD_EDGE)
    out += lines_at(wk1 - 16, 318, ["to the earth, every eye", "seeing Him",
                                    "Rev 19:11-16 · Zech 14:4-5"], 13, anchor="end")

    # The comparison, from rapture.md, "The features do sort".
    ty = 500
    rows = [
        ("", "For His saints", "With His saints"),
        ("Which way", "up, to meet Him in the air", "down, to the earth"),
        ("Signs before", "none: “in the twinkling of an eye”", "“immediately after the tribulation”"),
        ("Who sees", "not stated", "“every eye” (Rev 1:7)"),
        ("Judgment", "absent", "flaming fire; the sword"),
        ("Resurrection", "central (1 Cor 15:52-53)", "absent"),
        ("Purpose", "comfort (1 Thess 4:18)", "“to judge and make war”"),
        ("Timing", "inferred", "stated (Matthew 24:29)"),
    ]
    cx = [40, 170, 440]
    for i, (a, b, c3) in enumerate(rows):
        y = ty + i * 32
        if i == 0:
            out.append(f'<rect x="{cx[0] - 10}" y="{y - 22}" width="{W - 60}" height="32" fill="{GOLD_TINT}"/>')
        elif i % 2 == 0:
            out.append(f'<rect x="{cx[0] - 10}" y="{y - 22}" width="{W - 60}" height="32" fill="{EARTH_TINT}" opacity="0.5"/>')
        out.append(text(cx[0], y, a, 13.5, weight="bold"))
        out.append(text(cx[1], y, b, 13.5, weight="bold" if i == 0 else None,
                        fill=GOLD_EDGE if i == 0 else INK))
        out.append(text(cx[2], y, c3, 13.5, weight="bold" if i == 0 else None,
                        fill=GOLD_EDGE if i == 0 else INK))
    out.append(f'<rect x="{cx[0] - 10}" y="{ty - 22}" width="{W - 60}" height="{len(rows) * 32}" fill="none" stroke="{INK}"/>')
    ny = ty + len(rows) * 32 + 22
    out += lines_at(W / 2, ny, ["The same people are at both, on opposite sides of the journey: the bride’s",
                                "fine linen (Revelation 19:8) is what the armies wear (Revelation 19:14)."],
                    13.5, anchor="middle", italic=True)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 3. Daniel's seventy weeks, on this site's reckoning (immediately-after.md)


def seventy_weeks():
    h = 1196
    sx0, sx1 = 128, 168                          # the spine
    y_dec, y7, y69 = 150, 196, 560               # decree, 7 weeks, 69 weeks
    g0, g1 = 584, 760                            # the gap
    w0, wm, w1 = 784, 894, 1004                  # the seventieth week, drawn larger
    out = svg_open(
        h,
        "Daniel's seventy weeks",
        "A chart of Daniel 9:24-27 on this site's reckoning, read top to bottom. Seventy weeks, 490 "
        "years, are decreed about Daniel's people and city. The first sixty-nine weeks run from the "
        "decree to restore Jerusalem, 1 Nisan 444 BC (Nehemiah 2:1-8), in two parts, seven weeks and "
        "sixty-two weeks, to 10 Nisan AD 33, when the King enters Jerusalem (Harold Hoehner's count, "
        "which this site follows). The Messiah is cut off after the sixty-ninth week (Daniel 9:26), "
        "and the city and sanctuary are destroyed in AD 70. A break marks the gap, the church age, "
        "which was not revealed to Daniel (Ephesians 3:5). The seventieth week, still future, is drawn "
        "larger: a covenant for one week, the abomination at its middle, and the decreed end, when "
        "the King returns to the Mount of Olives (Daniel 9:27; Zechariah 14:4). A note gives the "
        "arithmetic: 69 weeks of 360-day years is 173,880 days.",
    )
    out += heading("Daniel's Seventy Weeks",
                   "“Seventy weeks are decreed about your people and your holy city” (Daniel 9:24)")

    out.append(f'<rect x="{sx0}" y="{y_dec}" width="{sx1 - sx0}" height="{y7 - y_dec}" fill="{GOLD_TINT}" stroke="{INK}"/>')
    out.append(f'<rect x="{sx0}" y="{y7}" width="{sx1 - sx0}" height="{y69 - y7}" fill="{GOLD}" stroke="{INK}"/>')
    out += lines_at(sx0 - 10, y_dec + 20, ["7 weeks", "49 years"], 13, anchor="end", weight="bold")
    out += lines_at(sx0 - 10, (y7 + y69) / 2 - 8, ["62 weeks", "434 years"], 15, lh=19, anchor="end", weight="bold")
    out += lines_at(sx0 - 10, (y_dec + y69) / 2 + 60, ["69 weeks", "483 years"], 12.5, anchor="end",
                    italic=True, fill=MUTED)

    out.append(f'<path d="M{(sx0 + sx1) / 2} {g0} V{g1}" stroke="{MUTED}" stroke-width="2.5" stroke-dasharray="3 6"/>')
    for gy in (g0 + 2, g1 - 12):
        out.append(f'<path d="M{sx0 - 6} {gy + 12} l52 -12 M{sx0 - 6} {gy + 20} l52 -12" stroke="{MUTED}" stroke-width="1.6"/>')
    out += lines_at(sx0 - 10, (g0 + g1) / 2 - 4, ["THE", "GAP"], 14, anchor="end", weight="bold", fill=MUTED)

    out.append(f'<rect x="{sx0}" y="{w0}" width="{sx1 - sx0}" height="{w1 - w0}" fill="{RED_TINT}" stroke="{INK}" stroke-dasharray="5 4"/>')
    out.append(f'<path d="M{sx0 - 8} {wm} H{sx1 + 8}" stroke="{RED}" stroke-width="3"/>')
    out += lines_at(sx0 - 10, w0 + 40, ["70th", "week"], 15, lh=19, anchor="end", weight="bold", fill=RED)
    out += lines_at(sx0 - 10, w0 + 84, ["7 years,", "drawn", "larger"], 12, anchor="end", italic=True, fill=MUTED)

    gx, gy0 = sx1 + 54, 262
    out.append(f'<rect x="{gx}" y="{gy0}" width="{W - gx - 30}" height="232" rx="6" fill="{CARD}" stroke="{INK}"/>')
    out.append(text(gx + 14, gy0 + 28, "WHAT THE SEVENTY WEEKS ARE FOR", 13.5, weight="bold", spacing="1"))
    out.append(text(gx + 14, gy0 + 48, "“decreed about your people and your holy city”", 13, italic=True))
    for i, goal in enumerate(["to finish the transgression", "to put an end to sin", "to atone for iniquity",
                              "to bring in everlasting righteousness", "to seal both vision and prophet",
                              "to anoint a most holy place"]):
        out.append(f'<circle cx="{gx + 22}" cy="{gy0 + 74 + i * 24}" r="3" fill="{GOLD_EDGE}"/>')
        out.append(text(gx + 34, gy0 + 79 + i * 24, goal, 14))
    out.append(text(gx + 14, gy0 + 220, "Daniel 9:24 (ESV)", 12.5, italic=True, fill=MUTED))

    def event(y, rows, ref, color=INK, solid=True):
        r = [f'<path d="M{sx1} {y} H{sx1 + 46}" stroke="{color}" stroke-width="1.4"/>',
             f'<circle cx="{sx1}" cy="{y}" r="4.5" fill="{color}" stroke="{PAPER}"/>']
        for i, row in enumerate(rows):
            r.append(text(sx1 + 54, y + 5 + i * 18, row, 15 if i == 0 else 14, weight="bold" if i == 0 else None,
                          fill=color))
        r.append(text(sx1 + 54, y + 5 + len(rows) * 18, ref, 12.5, fill=MUTED, italic=True))
        return r

    out += event(y_dec, ["1 Nisan 444 BC: the decree", "“to restore and build Jerusalem”"], "Nehemiah 2:1-8; Daniel 9:25")
    out += event(y69 - 24, ["10 Nisan AD 33: the King enters Jerusalem", "the sixty-nine weeks complete (Hoehner)"],
                 "Luke 19:41-44; Daniel 9:25")
    out += event(y69 + 40, ["“An anointed one shall be cut off", "and shall have nothing”: the cross, AD 33"],
                 "Daniel 9:26", color=RED)
    out += event(g0 + 70, ["AD 70: the city and the sanctuary destroyed"], "Daniel 9:26; Luke 21:20-24")
    out.append(f'<rect x="{sx1 + 54}" y="{g0 + 108}" width="{W - sx1 - 84}" height="54" rx="5" fill="{BLUE_TINT}" stroke="{BLUE}"/>')
    out.append(text(sx1 + 66, g0 + 130, "THE CHURCH AGE · outside Daniel's count", 14, weight="bold", fill=BLUE))
    out.append(text(sx1 + 66, g0 + 150, "“not made known to the sons of men in other generations” (Eph 3:5)", 12.5,
                    italic=True, fill=BLUE))
    out += event(w0, ["A strong covenant “for one week”"], "Daniel 9:27")
    out += event(wm, ["The middle: sacrifice stopped,", "the abomination set up"], "Daniel 9:27; Matthew 24:15",
                 color=RED)
    out += event(w1, ["The decreed end; the King returns", "to the Mount of Olives"], "Daniel 9:27; Zechariah 14:4")

    ny = w1 + 66
    note, _ = bracket_note(28, ny, W - 56, [
        "69 weeks × 7 years × 360 days = 173,880 days",
        "1 Nisan 444 BC to 10 Nisan AD 33 is Harold Hoehner's count, which this site follows; Sir Robert",
        "Anderson counted 445 BC to AD 32. Counted directly, both intervals run 2-4 days long, and both",
        "land in Passion Week. The seventieth week is future: its length is stated, its start withheld.",
    ], size=13)
    out += note
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 4. After the thousand years (new-heaven-and-new-earth.md)


def after_thousand():
    lanes = [(24, 186), (194, 356), (364, 526), (534, 696)]
    names = ["SATAN", "THE DEAD", "EARTH AND SKY", "FIRE"]
    fills = [RED_TINT, BLUE_TINT, EARTH_TINT, "#f6e1cf"]
    inks = [RED, BLUE, INK, FIRE]
    desc = (
        "A chart in four lanes, Satan, the dead, earth and sky, and fire, read top to bottom from "
        "Christ's coming to the new creation. At His coming Satan is bound in the abyss (Revelation "
        "20:1-3), the first resurrection raises those who reign with Christ (Revelation 20:4-6), the "
        "earth stands for the kingdom, and He comes in flaming fire on the living nations (2 "
        "Thessalonians 1:8; Luke 17:30). The thousand years follow, the seventh day. After them Satan "
        "is released for a little while and gathers Gog and Magog against the camp of the saints, "
        "and fire from heaven consumes them (Revelation 20:7-9); the devil is thrown into the lake of "
        "fire (Revelation 20:10). At the great white throne earth and sky flee away (Revelation "
        "20:11), the rest of the dead are judged by their deeds (Revelation 20:12-13), Death and "
        "Hades are thrown into the lake (Revelation 20:14), and on this site's reading Peter's fire "
        "dissolves the heavens there (2 Peter 3:10-12), drawn dashed as an inference. The eighth day "
        "opens: a new heaven and a new earth, the holy city coming down, and death no more "
        "(Revelation 21:1-4)."
    )
    out = heading("After the Thousand Years", "Revelation 20:1–21:4, from His coming to the eighth day")

    y = 120
    for (a, b), n, f, ink in zip(lanes, names, fills, inks):
        out += banner((a + b) / 2, y, b - a - 30, n, fill=ink, size=12.5)
    y = 162

    def stage(y, title, color=INK):
        r = [f'<path d="M24 {y} H{W - 24}" stroke="{color}" stroke-width="1.2"/>']
        r.append(text(W / 2, y + 22, title, 14, "middle", "bold", fill=color, spacing="1.5", extra=HALO))
        return r

    def row(y, cells):
        r, tallest = [], 0
        for k, cell in enumerate(cells):
            if not cell:
                continue
            lines, ref, dashed = cell
            a, b = lanes[k]
            c, hh = card(a + 4, y, b - a - 8, lines, ref, dashed, stroke=inks[k], size=13.5)
            r += c
            tallest = max(tallest, hh)
        return r, tallest

    lanes_top, lanes_at_index = y, len(out)

    out += stage(y, "AT HIS COMING")
    r, hh = row(y + 36, [
        (["Bound in the", "abyss, a", "thousand years"], "Revelation 20:1-3", False),
        (["The first", "resurrection:", "“blessed and holy”"], "Revelation 20:4-6", False),
        (["The earth stands;", "the kingdom on it"], "Revelation 20:4", False),
        (["“In flaming fire”", "on the living", "nations"], "2 Thess 1:8; Lk 17:30", False),
    ])
    out += r
    y = y + 36 + hh + 22

    out.append(f'<rect x="{lanes[0][0]}" y="{y}" width="{lanes[3][1] - lanes[0][0]}" height="150" fill="{GOLD}" '
               f'stroke="{GOLD_EDGE}" stroke-width="2"/>')
    out.append(text(W / 2, y + 50, "THE THOUSAND YEARS", 22, "middle", "bold", spacing="2"))
    out.append(text(W / 2, y + 78, "the seventh day · the Sabbath of the week of history", 14.5, "middle", italic=True))
    out.append(text(W / 2, y + 102, "Christ reigns; His saints reign with Him", 14, "middle"))
    out.append(text(W / 2, y + 126, "Revelation 20:2-7 · Hebrews 4:9", 12.5, "middle", italic=True, fill=MUTED))
    y += 172

    out += stage(y, "AFTER THE THOUSAND YEARS")
    r, hh = row(y + 36, [
        (["Released for a", "little while;", "deceives the", "nations"], "Revelation 20:3, 7-8", False),
        None,
        (["Gog and Magog", "surround “the", "camp of the", "saints”"], "Revelation 20:8-9", False),
        (["“Fire came down", "from heaven and", "consumed them”"], "Revelation 20:9", False),
    ])
    out += r
    y2 = y + 36 + hh + 10
    r, hh = row(y2, [(["Thrown into the", "lake of fire"], "Revelation 20:10", False), None, None, None])
    out += r
    y = y2 + hh + 22

    out += stage(y, "THE GREAT WHITE THRONE", RED)
    r, hh = row(y + 36, [
        None,
        (["The rest of the", "dead raised,", "judged by their", "deeds"], "Revelation 20:5, 12-13", False),
        (["“Earth and sky", "fled away, and no", "place was found", "for them”"], "Revelation 20:11", False),
        (["Heavens set on", "fire and dissolved:", "placed here on", "this site's reading"], "2 Peter 3:10-12", True),
    ])
    out += r
    y2 = y + 36 + hh + 10
    r, hh = row(y2, [None, (["Death and Hades", "into the lake"], "Revelation 20:14", False), None, None])
    out += r
    y = y2 + hh + 26

    out.append(f'<rect x="{lanes[0][0]}" y="{y}" width="{lanes[3][1] - lanes[0][0]}" height="120" rx="8" '
               f'fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(text(W / 2, y + 36, "THE EIGHTH DAY", 22, "middle", "bold", spacing="2", fill=GOLD_EDGE))
    out.append(text(W / 2, y + 64, "A new heaven and a new earth; the holy city comes down", 15, "middle"))
    out.append(text(W / 2, y + 88, "“death shall be no more” (Revelation 21:1-4, ESV)", 14, "middle", italic=True))
    grounds = [f'<rect x="{a}" y="{lanes_top}" width="{b - a}" height="{y - lanes_top}" fill="{f}" opacity="0.55"/>'
               for (a, b), f in zip(lanes, fills)]
    out[lanes_at_index:lanes_at_index] = grounds
    out_h = y + 120 + 110
    out += legend_row(150, out_h - 84, span=False)
    out.append(credit(out_h))
    out.append("</svg>")
    return "\n".join(svg_open(out_h, "After the thousand years", desc) + out)


# ---------------------------------------------------------------------------------------------
# 5. Taken before judgment (taken-before-judgment.md)


def taken_before_judgment():
    ph, top = 196, 120
    h = top + 4 * ph + 170
    out = svg_open(
        h,
        "Taken before judgment",
        "Four panels, one for each life, each a short line of events with the judgment drawn in. "
        "Enoch walked with God and was taken alive (Genesis 5:24; Hebrews 11:5), 669 years before "
        "the flood he had announced (Jude 14-15). Noah went into the ark, the LORD shut him in, and he "
        "was preserved through the flood (Genesis 7:16; 2 Peter 2:5). Lot was brought out of Sodom; "
        "the angel could do nothing until he reached Zoar, then fire fell the same day (Genesis 19:16-24; "
        "Luke 17:29). Elijah was taken up by a whirlwind in full view, with no judgment behind him "
        "(2 Kings 2:11). A closing panel sets out what they picture on this site's reading: the "
        "church taken before the week, as Enoch, Lot and Elijah were, and a remnant kept through it, "
        "as Noah was, with the note that a type illustrates and the plain teaching establishes "
        "(1 Thessalonians 1:10; 5:9).",
    )
    out += heading("Taken Before Judgment", "“The Lord knows how to rescue the godly” (2 Peter 2:9, ESV)")
    lx0, lx1 = 200, 692

    def panel(i, name, tag, tag_color, verb):
        y = top + i * ph
        r = [f'<path d="M24 {y} H{W - 24}" stroke="{INK}" stroke-width="0.6"/>',
             text(28, y + 34, name.upper(), 22, weight="bold", spacing="1.5"),
             text(28, y + 56, tag, 13, weight="bold", fill=tag_color, spacing="1"),
             text(28, y + 74, verb, 12.5, italic=True, fill=MUTED)]
        return r, y

    # Enoch: taken at AM 987; the flood at AM 1656.
    r, y = panel(0, "Enoch", "TAKEN BEFORE", GOLD_EDGE, "לָקַח, “took” · Genesis 5:24")
    out += r
    gy = y + 130
    out.append(f'<path d="M{lx0} {gy} H{lx1}" stroke="{INK}" stroke-width="1.5"/>')
    ex, fx = lx0 + 40, lx1 - 150
    out.append(person(ex, gy, 0.9, GOLD_EDGE))
    out.append(f'<path d="M{ex} {gy - 34} V{y + 30}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    out.append(arrow_head(ex, y + 26, -90, 11, GOLD_EDGE))
    out += lines_at(ex + 14, y + 34, ["walked with God, and", "God took him · AM 987"], 13)
    for k in range(4):
        out.append(waves(fx, lx1, gy - 4 - k * 8, color=WATER))
    out += lines_at(fx, y + 60, ["The Flood · AM 1656"], 13, weight="bold", fill=WATER)
    out += lines_at(fx, y + 76, ["which he had announced", "Jude 14-15"], 12.5)
    out.append(f'<path d="M{ex + 12} {gy + 22} H{fx - 6}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(text((ex + fx) / 2, gy + 40, "669 years: not on the earth when it fell", 12.5, "middle", italic=True))

    # Noah: through the water in the ark.
    r, y = panel(1, "Noah", "KEPT THROUGH", WATER, "φυλάσσω, “preserved” · 2 Peter 2:5")
    out += r
    gy = y + 140
    for k in range(5):
        out.append(waves(lx0, lx1, gy - k * 9, color=WATER))
    ax = (lx0 + lx1) / 2 - 40
    out.append(f'<path d="M{ax - 70} {gy - 54} H{ax + 70} L{ax + 52} {gy - 26} H{ax - 52} Z" fill="#8a6a3a" stroke="{INK}"/>')
    out.append(f'<rect x="{ax - 34}" y="{gy - 78}" width="68" height="24" fill="#a88452" stroke="{INK}"/>')
    out.append(f'<path d="M{ax - 40} {gy - 78} L{ax} {gy - 94} L{ax + 40} {gy - 78} Z" fill="#7a5a2e" stroke="{INK}"/>')
    out += lines_at(ax + 86, y + 40, ["“the LORD shut him in”", "Genesis 7:16"], 13)
    out += lines_at(lx0, y + 40, ["into the flood,", "and out the other side"], 13)

    # Lot: out to Zoar, then fire on Sodom.
    r, y = panel(2, "Lot", "BROUGHT OUT FIRST", GOLD_EDGE, "ῥύομαι, “rescued” · 2 Peter 2:7")
    out += r
    gy = y + 140
    out.append(f'<path d="M{lx0} {gy} H{lx1}" stroke="{INK}" stroke-width="1.5"/>')
    sx = lx0 + 70
    for k, (dx, hh) in enumerate([(-34, 30), (-12, 44), (10, 36), (30, 26)]):
        out.append(f'<rect x="{sx + dx}" y="{gy - hh}" width="20" height="{hh}" fill="#c9b48a" stroke="{INK}"/>')
    out.append(flames(sx - 40, sx + 54, gy - 30, 26))
    out.append(text(sx, gy + 20, "Sodom", 13, "middle", weight="bold"))
    zx = lx1 - 60
    out.append(f'<rect x="{zx - 16}" y="{gy - 24}" width="32" height="24" fill="{GOLD_TINT}" stroke="{INK}"/>')
    out.append(text(zx, gy + 20, "Zoar", 13, "middle", weight="bold"))
    out.append(person(zx - 40, gy, 0.85, GOLD_EDGE))
    out.append(f'<path d="M{sx + 60} {gy - 12} H{zx - 56}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(zx - 52, gy - 12, 0, 10, GOLD_EDGE))
    out.append(text((sx + zx) / 2, gy - 24, "1 · out to Zoar", 12.5, "middle", italic=True))
    out.append(text(sx, gy - 64, "2 · then the fire", 12.5, "middle", italic=True, fill=FIRE))
    out += lines_at((sx + zx) / 2, y + 40, ["“I can do nothing till you arrive there”",
                                            "Genesis 19:22 · then fire the same day, Luke 17:29"],
                    13, anchor="middle")

    # Elijah: up by a whirlwind, no judgment behind.
    r, y = panel(3, "Elijah", "TAKEN UP ALIVE", GOLD_EDGE, "לֻקָּח, “taken” · 2 Kings 2:10")
    out += r
    gy = y + 150
    out.append(f'<path d="M{lx0} {gy} H{lx1}" stroke="{INK}" stroke-width="1.5"/>')
    wx = lx0 + 130
    for k in range(9):
        rx, cy = 6 + k * 5.5, gy - 10 - k * 13
        out.append(f'<ellipse cx="{wx + k * 1.5:.1f}" cy="{cy}" rx="{rx:.1f}" ry="{2.5 + k * 0.6:.1f}" fill="none" '
                   f'stroke="{MUTED}" stroke-width="1.6"/>')
    out.append(person(wx + 14, gy - 136, 0.85, GOLD_EDGE))
    out.append(f'<path d="M{wx + 14} {gy - 172} V{y + 16}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    out.append(arrow_head(wx + 14, y + 12, -90, 11, GOLD_EDGE))
    out.append(flames(wx - 112, wx - 46, gy - 100, 24))
    out.append(text(wx - 80, gy - 82, "chariots of fire", 12, "middle", italic=True, fill=FIRE))
    out.append(person(wx - 80, gy, 0.85, INK))
    out.append(text(wx - 80, gy + 20, "Elisha", 12.5, "middle", italic=True))
    out += lines_at(wx + 120, y + 60, ["“Elijah went up by a whirlwind", "into heaven,” in full view",
                                       "2 Kings 2:11 · no judgment follows:", "he shows the manner, a living",
                                       "body taken up (1 Cor 15:51-52)"], 13)

    y = top + 4 * ph
    out.append(f'<path d="M24 {y} H{W - 24}" stroke="{INK}" stroke-width="0.6"/>')
    note, nh = bracket_note(28, y + 20, W - 56, [
        "What they picture, on this site's reading",
        "Enoch, Lot and Elijah: the church taken before the week (1 Thessalonians 4:17).",
        "Noah: the remnant kept through it, alive on the earth when Jesus returns (Matthew 24:37-39).",
        "A type illustrates what Scripture teaches plainly elsewhere (1 Thessalonians 1:10; 5:9);",
        "it does not establish it. Both sides read the same four lives and weigh them differently.",
    ], size=13)
    out += note
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 6. Meeting the Lord in the air (meet-the-lord-in-the-air.md)


def meeting_the_lord():
    h = 1180
    out = svg_open(
        h,
        "Meeting the Lord in the air",
        "A chart of the word apantesis, 'meeting', and the two readings of 1 Thessalonians 4:17. At "
        "the top, the word occurs three times in the New Testament (1 Thessalonians 4:17; Matthew "
        "25:6; Acts 28:15), and four Septuagint meetings show its range of outcomes: a greeting (1 "
        "Samuel 13:10), a battle (1 Samuel 4:1), a rebuke (2 Samuel 6:20) and a massacre (Jeremiah "
        "41:6-7). Next, the civic custom of Acts 28:15: believers go out from Rome to the Forum of "
        "Appius, meet Paul, and return with him. Below, two columns. The posttribulational reading: "
        "the church is caught up to meet the Lord and escorts Him down at once. The pretribulational "
        "reading, this site's: the church is caught up to meet Him, goes with Him to the Father's "
        "house (John 14:2-3) and the marriage feast (Matthew 25:10), and returns with Him at the end "
        "of the seventieth week among the armies of heaven (Revelation 19:14). Both directions are "
        "inferred; Paul states the company, 'always with the Lord'.",
    )
    out += heading("Meeting the Lord in the Air", "ἀπάντησις (apantēsis, G529): the going out, and what follows")

    # The word's range.
    y = 120
    out.append(text(28, y + 6, "THE WORD", 14, weight="bold", spacing="1.5"))
    out.append(text(28, y + 26, "3 times in the New Testament: 1 Thess 4:17 · Matthew 25:6 · Acts 28:15", 13.5))
    out.append(text(28, y + 46, "In the Septuagint, “to meet” ends in whatever the occasion brings:", 13.5))
    cw = (W - 56 - 30) / 4
    for k, (what, ref, fill) in enumerate([("a greeting", "1 Samuel 13:10", GOLD_TINT),
                                           ("a battle", "1 Samuel 4:1", RED_TINT),
                                           ("a rebuke", "2 Samuel 6:20", EARTH_TINT),
                                           ("a massacre", "Jeremiah 41:6-7", "#e8d0cc")]):
        x = 28 + k * (cw + 10)
        out.append(f'<rect x="{x:.1f}" y="{y + 62}" width="{cw:.1f}" height="50" rx="5" fill="{fill}" stroke="{INK}"/>')
        out.append(text(x + cw / 2, y + 84, what, 14.5, "middle", "bold"))
        out.append(text(x + cw / 2, y + 102, ref, 12, "middle", italic=True, fill=MUTED))

    # The civic custom, Acts 28:15.
    y = 268
    out.append(f'<path d="M24 {y} H{W - 24}" stroke="{INK}" stroke-width="0.6"/>')
    out.append(text(28, y + 28, "THE CIVIC CUSTOM", 14, weight="bold", spacing="1.5"))
    out.append(text(28, y + 46, "Acts 28:15: believers walk out of Rome to meet Paul, then return with him", 13.5))
    ry = y + 120
    out.append(f'<path d="M60 {ry} H{W - 60}" stroke="{MUTED}" stroke-width="6" stroke-linecap="round"/>')
    out.append(f'<path d="M60 {ry} H{W - 60}" stroke="{PAPER}" stroke-width="1.5" stroke-dasharray="8 8"/>')
    for dx, hh in [(-22, 30), (-4, 46), (14, 36), (30, 24)]:
        out.append(f'<rect x="{80 + dx}" y="{ry - 8 - hh}" width="16" height="{hh}" fill="#c9b48a" stroke="{INK}"/>')
    out.append(text(88, ry + 28, "Rome", 13.5, "middle", "bold"))
    mx = W - 170
    out.append(person(mx, ry - 8, 0.85, RED))
    out.append(text(mx, ry + 28, "Forum of Appius · Paul arrives", 13, "middle", "bold"))
    out.append(f'<path d="M140 {ry - 26} H{mx - 40}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(mx - 36, ry - 26, 0, 10, GOLD_EDGE))
    out.append(text((140 + mx) / 2, ry - 34, "1 · they go out to meet him", 13, "middle"))
    out.append(f'<path d="M{mx - 40} {ry + 44} H144" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(140, ry + 44, 180, 10, GOLD_EDGE))
    out.append(text((140 + mx) / 2, ry + 62, "2 · they escort him back to the city", 13, "middle"))

    # Two readings.
    y = 470
    out.append(f'<path d="M24 {y} H{W - 24}" stroke="{INK}" stroke-width="0.6"/>')
    out.append(text(W / 2, y + 28, "TWO READINGS OF 1 THESSALONIANS 4:17", 14, "middle", "bold", spacing="1.5"))
    cols = [(28, 352), (368, 692)]
    out.append(f'<path d="M{W / 2} {y + 44} V{y + 560}" stroke="{INK}" stroke-width="0.6"/>')
    gy, airy, house_y = y + 470, y + 260, y + 100
    for k, (a, b) in enumerate(cols):
        cx = (a + b) / 2
        title = ["POSTTRIBULATIONAL", "PRETRIBULATIONAL · THIS SITE"][k]
        out.append(text(cx, y + 62, title, 13.5, "middle", "bold", fill=[MUTED, GOLD_EDGE][k], spacing="1"))
        out.append(f'<path d="M{a + 10} {gy} H{b - 10}" stroke="{INK}" stroke-width="2"/>')
        out.append(text(a + 14, gy + 20, "the earth", 12.5, italic=True, fill=MUTED))
        out += cloud(cx, airy + 16, 200)
        out.append(text(cx, airy + 4, "“in the air”", 13, "middle", italic=True))

    # Posttribulational: up and straight back down.
    a, b = cols[0]
    cx = (a + b) / 2
    out.append(person(cx - 40, gy, 0.85, INK))
    out.append(f'<path d="M{cx - 40} {gy - 36} V{airy + 26}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(cx - 40, airy + 22, -90, 10, GOLD_EDGE))
    out.append(f'<path d="M{cx + 40} {airy + 26} V{gy - 8}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(cx + 40, gy - 4, 90, 10, GOLD_EDGE))
    out += lines_at(cx - 50, gy - 90, ["caught", "up"], 13, anchor="end")
    out += lines_at(cx + 50, gy - 90, ["down with", "Him at once"], 13)
    out += lines_at(cx, y + 110, ["The custom supplies the", "direction: the escort turns",
                                  "back with the King to the earth"], 13.5, anchor="middle")

    # Pretribulational: up, on to the Father's house, back at the end of the week.
    a, b = cols[1]
    cx = (a + b) / 2
    out.append(person(cx - 60, gy, 0.85, INK))
    out.append(f'<path d="M{cx - 60} {gy - 36} V{airy + 26}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    out.append(arrow_head(cx - 60, airy + 22, -90, 10, GOLD_EDGE))
    out.append(f'<path d="M{cx - 30} {airy - 30} V{house_y + 76}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    out.append(arrow_head(cx - 30, house_y + 72, -90, 10, GOLD_EDGE))
    c, _ = card(cx - 130, house_y, 260, ["The Father's house;", "the marriage feast"], "John 14:2-3 · Matthew 25:10", size=13.5)
    out += c
    out.append(f'<path d="M{cx + 70} {house_y + 76} C{cx + 165} {airy} {cx + 155} {gy - 60} {cx + 95} {gy - 8}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3.5"/>')
    out.append(arrow_head(cx + 92, gy - 4, 115, 11, GOLD_EDGE))
    out += lines_at(cx - 14, airy + 96, ["with Him at the end", "of the week, among", "the armies of heaven",
                                         "Revelation 19:14"], 13)
    out.append(text(cx - 70, gy - 90, "caught up", 13, "end"))

    ny = y + 580
    note, _ = bracket_note(28, ny, W - 56, [
        "Paul states the company: “and so we will always be with the Lord” (1 Thessalonians 4:17, ESV).",
        "Which way the company goes next is inferred on both readings. This site reads the verse with",
        "John 14:3, “that where I am you may be also,” and marks the point as contested.",
    ], bold_first=False, size=13)
    out += note
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 7. The end of the ages: one break expected, two points given (end-of-the-age.md)


def end_of_the_ages():
    h = 1060
    out = svg_open(
        h,
        "The end of the ages",
        "Two timelines. The first is the Jewish two-age frame of 1 Enoch 16:1 and 2 Esdras 7:43: this "
        "age and the age to come, divided by one judgment. The second is the New Testament's: a red span "
        "marked 'the end of the ages' opens at the cross, where Hebrews 9:26 and 1 Corinthians 10:11 say "
        "it has already come, and closes at Christ's return after Daniel's seventieth week, the 'close "
        "of the age' of Matthew 13:39-43 and 24:3. Between them runs the church age, under Matthew "
        "28:20's promise, 'I am with you all the days, to the end of the age.' A dashed arc rises from "
        "the end of the church age to the clouds, the rapture, placed by inference; a solid arc comes "
        "down at the end of the week, the return. Beyond the return is the age to come: the thousand "
        "years, dashed as its first stage by inference, and the new creation. Cards below sort the "
        "texts by where they fall: at the cross, in the days between, and at His return.",
    )
    out += heading("The End of the Ages", "Opened at the cross, closed at His return")

    # A. The frame Jesus inherited: one break.
    out.append(text(W / 2, 138, "AS JEWISH TEACHING EXPECTED IT", 13, "middle", "bold", fill=MUTED,
                    spacing="2"))
    split = W / 2
    out.append(f'<rect x="40" y="172" width="{split - 40}" height="30" fill="{EARTH_TINT}" stroke="{INK}"/>')
    out.append(text((40 + split) / 2, 192, "THIS AGE", 14, "middle", "bold", spacing="1.5"))
    out.append(f'<rect x="{split}" y="172" width="{W - 40 - split}" height="30" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}"/>')
    out.append(text((split + W - 40) / 2, 192, "THE AGE TO COME", 14, "middle", "bold", spacing="1.5"))
    out.append(f'<path d="M{split} 160 V214" stroke="{RED}" stroke-width="3"/>')
    out.append(text(split, 154, "Messiah · the judgment", 13, "middle", italic=True, fill=RED))
    out.append(text(W / 2, 232, "One line, one break · 1 Enoch 16:1 · 2 Esdras 7:43", 12.5, "middle",
                    italic=True, fill=MUTED))
    out.append(f'<path d="M{W / 2 - 220} 256 H{W / 2 + 220}" stroke="{INK}" stroke-width="0.6"/>')

    # B. What the New Testament says happened: the break opens and closes.
    out.append(text(W / 2, 286, "AS THE NEW TESTAMENT TELLS IT", 13, "middle", "bold", fill=MUTED,
                    spacing="2"))
    x0, xc, xrap, xr, xm, x1 = 30, 140, 370, 470, 580, 690
    gy = 550
    out += banner((x0 + xr) / 2, 306, xr - x0 - 40, "THIS AGE", fill=INK)
    out += banner((xr + x1) / 2, 306, x1 - xr - 40, "THE AGE TO COME", fill=GOLD_EDGE, size=12.5)

    # The span the study is about.
    sy = 372
    out.append(f'<path d="M{xc} {sy} H{xr}" stroke="{RED}" stroke-width="3"/>')
    out.append(f'<path d="M{xc} {sy - 9} V{sy + 9} M{xr} {sy - 9} V{sy + 9}" stroke="{RED}" stroke-width="2"/>')
    out.append(text((xc + xr) / 2 - 40, sy - 10, "THE END OF THE AGES", 14, "middle", "bold", fill=RED,
                    spacing="1.5"))
    out.append(text(xc + 4, sy + 24, "“has come”", 13, italic=True, fill=RED))
    out.append(text(xr - 4, sy + 24, "“the close of the age”", 13, "end", italic=True, fill=RED, extra=HALO))

    # Heaven: the cloud the church is caught up to, and from which He returns.
    out += cloud((xrap + xr) / 2, 482, 140)
    out.append(text((xrap + xr) / 2, 504, "with the Lord", 12.5, "middle", italic=True, fill=GOLD_EDGE))

    # The line of time.
    out.append(f'<rect x="{x0}" y="{gy}" width="{xc - x0}" height="30" fill="{EARTH_TINT}" stroke="{INK}"/>')
    out.append(text((x0 + xc) / 2, gy + 20, "AGES PAST", 13, "middle", "bold"))
    out.append(f'<rect x="{xc}" y="{gy}" width="{xrap - xc}" height="30" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
    out.append(text((xc + xrap) / 2, gy + 20, "THE CHURCH AGE", 13.5, "middle", "bold", spacing="1"))
    out.append(f'<rect x="{xrap}" y="{gy}" width="{xr - xrap}" height="30" fill="{RED_TINT}" stroke="{INK}"/>')
    out.append(text((xrap + xr) / 2, gy + 20, "70TH WEEK", 13, "middle", "bold"))
    out.append(f'<rect x="{xr}" y="{gy}" width="{xm - xr}" height="30" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" '
               f'stroke-dasharray="5 4"/>')
    out.append(text((xr + xm) / 2, gy + 20, "1,000 YEARS", 12.5, "middle", "bold"))
    out.append(f'<rect x="{xm}" y="{gy}" width="{x1 - xm}" height="30" fill="{CARD}" stroke="{GOLD_EDGE}"/>')
    out.append(text((xm + x1) / 2, gy + 20, "NEW CREATION", 11.5, "middle", "bold"))
    out.append(f'<path d="M{x0 - 6} {gy + 31} H{x1 + 6}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(text((xrap + xr) / 2, gy + 48, "Daniel 9:27", 12, "middle", italic=True, fill=MUTED))
    out.append(text((xr + x1) / 2, gy + 48, "Rev 20:4-6 · 21:1", 12, "middle", italic=True, fill=MUTED))

    # The cross, where Hebrews dates the opening.
    out.append(f'<path d="M{xc} {gy - 58} V{gy - 4} M{xc - 14} {gy - 44} H{xc + 14}" stroke="{INK}" '
               f'stroke-width="5" stroke-linecap="round"/>')
    out.append(text(xc + 22, gy - 34, "once for all", 13, italic=True))

    # Up, dashed (the rapture's timing is inferred); down, solid (Matthew 24:29 states it).
    out.append(f'<path d="M{xrap - 6} {gy - 4} C{xrap - 30} {gy - 30} {xrap - 18} 500 {xrap + 14} 488" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3" stroke-dasharray="7 5"/>')
    out.append(arrow_head(xrap + 16, 487, -20, 12, GOLD_EDGE))
    out.append(f'<path d="M{xr - 12} 488 C{xr + 18} 496 {xr + 16} {gy - 30} {xr + 2} {gy - 6}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="4"/>')
    out.append(arrow_head(xr + 2, gy - 2, 100, 13, GOLD_EDGE))
    out.append(text(xr + 22, 492, "He returns", 13, weight="bold", fill=GOLD_EDGE))
    out.append(text(xr + 22, 509, "Matt 24:29-31", 12, italic=True, fill=MUTED))

    # Matthew 28:20, under the line: solid on earth, dashed where the church is with Him.
    ay = gy + 76
    out.append(f'<path d="M{xc} {ay} H{xrap}" stroke="{BLUE}" stroke-width="3"/>')
    out.append(f'<path d="M{xrap} {ay} H{xr}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="7 5"/>')
    out.append(f'<path d="M{xc} {ay - 8} V{ay + 8} M{xr} {ay - 8} V{ay + 8}" stroke="{BLUE}" stroke-width="2"/>')
    out.append(text((xc + xr) / 2, ay + 24, "“I am with you all the days, to the end of the age”", 13.5,
                    "middle", italic=True, fill=BLUE))
    out.append(text((xc + xr) / 2, ay + 42, "Matthew 28:20 (lit.) · then “always with the Lord” (1 Thess 4:17)",
                    12.5, "middle", fill=MUTED))

    # Where each text falls.
    cy0 = ay + 78
    cols = [
        (30, "AT THE CROSS", [
            (["The end of the ages", "has come"], "Heb 9:26 · 1 Cor 10:11", False),
            (["“In these last days”", "God has spoken"], "Heb 1:2", False),
            (["Rescued from the", "present evil age"], "Gal 1:4", False),
        ]),
        (257, "ALL THE DAYS BETWEEN", [
            (["Jesus with His", "disciples every day"], "Matt 28:20", False),
            (["Weeds and wheat", "grow together"], "Matt 13:30", False),
            (["The church caught up", "before the week"], "1 Thess 4:17 · Rev 3:10", True),
        ]),
        (484, "AT HIS RETURN", [
            (["Daniel’s end:", "the week closes"], "Dan 9:27 · 12:4, 13", True),
            (["The harvest: angels", "separate the wicked"], "Matt 13:39-43, 49", False),
            (["“Your coming and the", "end of the age”"], "Matt 24:3", False),
        ]),
    ]
    cw = 206
    for cx, head, cards in cols:
        out.append(text(cx + cw / 2, cy0, head, 13, "middle", "bold", fill=GOLD_EDGE, spacing="1.5"))
        y = cy0 + 12
        for lines, ref, dashed in cards:
            c, ch = card(cx, y, cw, lines, ref, dashed=dashed, size=13.5)
            out += c
            y += ch + 10
    ly = h - 96
    out += legend_row(40, ly, span=False)
    out += lines_at(W / 2, ly + 52, ["The end began when Jesus offered Himself, and it closes when He comes back."],
                    13.5, anchor="middle", italic=True)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 8. Six days, three ages: the Talmud's two readings of the world-week (day-is-a-thousand-years.md)


def six_days_three_ages():
    h = 900
    out = svg_open(
        h,
        "Six days, three ages",
        "The Talmud reads the six thousand years two ways on one page, b. Sanhedrin 97a. The top row "
        "is the week: six days of a thousand years and a seventh that is all Sabbath, from Psalm 92:1 "
        "and Psalm 90:4. The second row is the school of Elijah's three ages of two thousand years: "
        "chaos, Torah, and the days of Messiah. b. Avodah Zarah 9a starts the age of Torah when Abraham "
        "was 52, which on its own count is 2,000 years after creation, with Sinai at 2,448, and notes "
        "that years had already passed from the days of Messiah without His coming. Two rabbis on the "
        "same page give the world's ruin as a thousand years (Isaiah 2:11) or two thousand (Hosea 6:2). "
        "A dashed row below places Abram's call and the cross on this site's own chronology, where the "
        "cross falls a few years before the four-thousandth year.",
    )
    out += heading("Six Days, Three Ages", "b. Sanhedrin 97a reads the world-week two ways")
    x0, x1 = 40, 680
    dw = (x1 - x0) / 7

    def xa(am):
        return x0 + am / 1000 * dw

    # Row 1: the week.
    y1 = 150
    out.append(text(x0, y1 - 14, "THE WEEK OF HISTORY", 13, weight="bold", fill=MUTED, spacing="1.5"))
    for i in range(7):
        fill, stroke = (GOLD, GOLD_EDGE) if i == 6 else (EARTH_TINT if i % 2 == 0 else CARD, INK)
        out.append(f'<rect x="{x0 + i * dw:.1f}" y="{y1}" width="{dw:.1f}" height="34" fill="{fill}" stroke="{stroke}"/>')
        out.append(text(x0 + (i + 0.5) * dw, y1 + 22, f"DAY {i + 1}", 13, "middle", "bold"))
    out.append(text(x0 + 6.5 * dw, y1 + 54, "all Shabbat", 12.5, "middle", italic=True, fill=GOLD_EDGE))
    out.append(text(x0, y1 + 54, "“a day, i.e., one thousand years” · Psalm 92:1; 90:4", 12.5,
                    italic=True, fill=MUTED))

    # Row 2: the three ages.
    y2 = 260
    out.append(text(x0, y2 - 14, "THE SCHOOL OF ELIJAH: THREE AGES", 13, weight="bold", fill=MUTED,
                    spacing="1.5"))
    ages = [("CHAOS", EARTH_TINT, INK), ("TORAH", BLUE_TINT, BLUE), ("DAYS OF MESSIAH", GOLD_TINT, GOLD_EDGE)]
    for i, (lab, fill, stroke) in enumerate(ages):
        out.append(f'<rect x="{x0 + 2 * i * dw:.1f}" y="{y2}" width="{2 * dw:.1f}" height="34" fill="{fill}" stroke="{stroke}"/>')
        out.append(text(x0 + (2 * i + 1) * dw, y2 + 16, lab, 13.5, "middle", "bold", fill=stroke))
        out.append(text(x0 + (2 * i + 1) * dw, y2 + 29, "2,000 years", 11.5, "middle", fill=MUTED))
    out.append(f'<rect x="{x0 + 6 * dw:.1f}" y="{y2}" width="{dw:.1f}" height="34" fill="none" stroke="{GOLD_EDGE}" stroke-dasharray="5 4"/>')
    out.append(text(x1, y2 - 14, "b. Sanhedrin 97a · b. Avodah Zarah 9a", 12.5, "end", italic=True, fill=MUTED))

    # Avodah Zarah 9a's own count: the age of Torah starts at Abraham, 448 years before Sinai.
    ym = y2 + 34
    for am, lab, sub, anchor in [(2000, "Abraham, aged 52", "“the souls … in Haran”", "end"),
                                 (2448, "Sinai", "AM 2448", "start")]:
        x = xa(am)
        out.append(f'<path d="M{x:.1f} {ym} V{ym + 70}" stroke="{BLUE}" stroke-width="2"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{ym}" r="4" fill="{BLUE}"/>')
        dx = -6 if anchor == "end" else 6
        out.append(text(x + dx, ym + 56, lab, 13, anchor, "bold", fill=BLUE))
        out.append(text(x + dx, ym + 72, sub, 12, anchor, italic=True, fill=MUTED))
    # The baraita's lament over the third age.
    xb0, xb1 = xa(4000), xa(4600)
    out.append(f'<path d="M{xb0:.1f} {ym + 30} H{xb1:.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="7 5"/>')
    out.append(f'<path d="M{xb0:.1f} {ym + 22} V{ym + 38}" stroke="{RED}" stroke-width="2"/>')
    out.append(arrow_head(xb1 + 4, ym + 30, 0, 10, RED))
    out += lines_at(xb0, ym + 56, ["“such and such years have", "already passed … and the", "Messiah has not yet arrived”"],
                    12.5, italic=True, fill=RED)

    # Row 3: two more voices on the same page.
    y3 = 470
    out.append(text(x0, y3 - 14, "ON THE SAME PAGE: HOW LONG THE RUIN?", 13, weight="bold", fill=MUTED,
                    spacing="1.5"))
    c, ch = card(x0, y3, 305, ["Rav Ketina: one thousand", "years, “on that day”"], "Isaiah 2:11 · b. Sanhedrin 97a")
    out += c
    c, _ = card(x0 + 335, y3, 305, ["Abaye: two thousand years,", "“after two days”"], "Hosea 6:2 · b. Sanhedrin 97a")
    out += c

    # Row 4: this site's chronology, dashed (a Christian reading laid over the rabbinic frame).
    y4 = y3 + ch + 80
    out.append(text(x0, y4 - 40, "THE SAME FRAME ON THIS SITE'S CHRONOLOGY", 13, weight="bold", fill=MUTED,
                    spacing="1.5"))
    ev = {lab: am for am, lab in chronology_events()}
    out.append(f'<rect x="{x0}" y="{y4}" width="{x1 - x0}" height="30" fill="{CARD}" stroke="{INK}" stroke-dasharray="5 4"/>')
    for k in range(1, 7):
        out.append(f'<path d="M{x0 + k * dw:.1f} {y4} v30" stroke="{MUTED}" stroke-width="0.8"/>')
    out.append(f'<path d="M{xa(4000):.1f} {y4 - 6} v42" stroke="{RED}" stroke-width="2.5"/>')
    out.append(text(xa(4000) + 8, y4 + 54, "AM 4000", 12.5, weight="bold", fill=RED))
    for key, y_lab, anchor in [("Abram called", y4 - 10, "start"), ("The cross", y4 + 54, "end")]:
        am = ev[key]
        x = xa(am)
        out.append(f'<circle cx="{x:.1f}" cy="{y4 + 15}" r="5" fill="{INK}"/>')
        dx = 6 if anchor == "start" else -8
        out.append(text(x + dx, y_lab, f"{key} · AM {am} · {am_label(am)}", 12.5, anchor, weight="bold",
                        extra=HALO))
    out += lines_at(x0, y4 + 90, [
        "Read from docs/data/chronology.json. The Talmud's ages use its own count (Sinai at 2,448);",
        "this site's Masoretic count places Abram's call later and the cross a few years before 4,000.",
    ], 12.5, italic=True, fill=MUTED)

    ly = h - 110
    c, _ = card(x0, ly, 230, ["The source states it"], "", size=13)
    out += c
    c, _ = card(x0 + 255, ly, 300, ["A reading laid over the source"], "", dashed=True, size=13)
    out += c
    out += lines_at(W / 2, ly + 62, ["The week is Scripture’s shape (Exodus 20:11). The ages are the rabbis’ reading of it."],
                    13.5, anchor="middle", italic=True)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 9. The eighth day: seven complete something, the eighth begins it (new-heaven-and-new-earth.md)


def eighth_day():
    rows = [
        ("A son’s circumcision", "enters the covenant", "Gen 17:12 · Lev 12:3", False),
        ("A firstborn ox or sheep", "“you shall give it to me”", "Exodus 22:30", False),
        ("The priests’ ordination", "the glory of the LORD appears", "Lev 9:1, 23-24", False),
        ("A cleansed leper", "brought back “before the LORD”", "Lev 14:10, 23", False),
        ("The Feast of Booths", "“a solemn rest”", "Lev 23:36, 39", False),
        ("The day Jesus rose", "the first day after the Sabbath", "Matt 28:1 · Barnabas 15", True),
        ("The week of history", "a new heaven and a new earth", "Rev 20:2-7; 21:1", True),
    ]
    rh = 70
    top = 150
    h = top + len(rows) * rh + 300
    out = svg_open(
        h,
        "The eighth day",
        "Seven rows, each with seven small squares followed by a larger gold eighth. Five come from the "
        "Law: circumcision, the firstborn, the priests' ordination, the cleansed leper and the Feast of "
        "Booths, where seven days complete something and the eighth begins what the seven were for. Two "
        "are dashed as readings: the day Jesus rose, the first day after the Sabbath, which the Epistle "
        "of Barnabas calls the eighth day; and this site's week of history, seven thousand-year days "
        "followed by the new heaven and new earth. Below, eight figures stand for Noah's household, the "
        "eight persons brought through water, which Peter makes the pattern of baptism and the "
        "resurrection (1 Peter 3:20-21).",
    )
    out += heading("The Eighth Day", "Seven complete it; the eighth begins what the seven were for")
    sq, gap = 20, 5
    xs = 235
    out.append(text(xs + 3.5 * (sq + gap), top - 12, "SEVEN DAYS", 12.5, "middle", "bold", fill=MUTED, spacing="1.5"))
    x8 = xs + 7 * (sq + gap) + 14
    out.append(text(x8 + 22, top - 12, "THE EIGHTH", 12.5, "middle", "bold", fill=GOLD_EDGE, spacing="1.5"))
    for i, (name, what, ref, dashed) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="30" y="{y - 8}" width="{W - 60}" height="{rh - 6}" fill="{EARTH_TINT}" opacity="0.45"/>')
        out.append(text(40, y + 14, name, 14, weight="bold"))
        out.append(text(40, y + 32, ref, 12.5, italic=True, fill=MUTED))
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        for k in range(7):
            out.append(f'<rect x="{xs + k * (sq + gap)}" y="{y + 2}" width="{sq}" height="{sq}" fill="{CARD}" '
                       f'stroke="{INK}" stroke-width="1.2"{dash}/>')
        out.append(f'<rect x="{x8}" y="{y - 4}" width="44" height="38" rx="4" fill="{GOLD}" stroke="{GOLD_EDGE}" '
                   f'stroke-width="1.6"{dash}/>')
        out.append(text(x8 + 22, y + 21, "8", 18, "middle", "bold"))
        out.append(text(x8 + 54, y + 21, what, 12.5))
    ny = top + len(rows) * rh + 20
    out.append(f'<path d="M40 {ny} H{W - 40}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(text(W / 2, ny + 30, "“EIGHT PERSONS … BROUGHT SAFELY THROUGH WATER”", 13.5, "middle", "bold",
                    spacing="1"))
    out.append(text(W / 2, ny + 48, "1 Peter 3:20-21 · baptism “corresponds to this”, through the resurrection",
                    12.5, "middle", italic=True, fill=MUTED))
    out.append(waves(150, 570, ny + 112, color=WATER))
    for k in range(8):
        out.append(person(200 + k * 46, ny + 104, 1.0, GOLD_EDGE if k == 0 else INK))
    out.append(text(200, ny + 132, "Noah", 12, "middle", italic=True, fill=GOLD_EDGE))
    ly = h - 104
    c, _ = card(40, ly, 230, ["The Law sets the day"], "", size=13)
    out += c
    c, _ = card(295, ly, 300, ["A reading of the pattern"], "", dashed=True, size=13)
    out += c
    out += lines_at(W / 2, ly + 62, ["The eighth day carries the rest past the count of seven (Leviticus 23:39)."],
                    13.5, anchor="middle", italic=True)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 10. Weeks within weeks: the Zadok calendar's nested sevens (feasts/zadok-calendar.md)


def weeks_within_weeks():
    h = 1210
    out = svg_open(
        h,
        "Weeks within weeks",
        "The Zadok calendar's nested sevens. At the top, the 364-day year: four quarters, each of three "
        "30-day months and one Tekufah day, 91 days or 13 weeks, so the year is exactly 52 weeks and 1 "
        "Abib always falls on a Wednesday. Below, a ladder: the week of seven days, the year of 52 weeks, "
        "the sabbatical of seven years (Leviticus 25:1-7), and the jubilee, forty-nine years and then "
        "the fiftieth (Leviticus 25:8-10). There the count divides. On the Rabbis' count the jubilee "
        "stands alone and a cycle is 50 years; on Rabbi Yehuda's, and in the book of Jubilees, the "
        "fiftieth year also begins the next cycle and a cycle is 49 (b. Nedarim 61a; b. Arakhin 12b; "
        "Jubilees 50:4). Ten jubilees make 500 or 490 years, forty make 2,000 or 1,960, and so on. "
        "dsscalendar.org's 500-year Onah and 140-jubilee wheel are dashed as its own construction; "
        "Daniel's 490 years and the Talmud's 2,000-year ages and 85 jubilees are solid.",
    )
    out += heading("Weeks Within Weeks", "The Zadok calendar’s nested sevens, and where the count divides")
    x0, x1 = 40, 680

    # A. The year.
    ya = 140
    out.append(text(x0, ya, "THE YEAR · 364 DAYS · 52 WEEKS", 13, weight="bold", fill=MUTED, spacing="1.5"))
    qw = (x1 - x0) / 4
    tw = 10
    mw = (qw - tw) / 3
    for q in range(4):
        qx = x0 + q * qw
        for m in range(3):
            n = q * 3 + m + 1
            out.append(f'<rect x="{qx + m * mw:.1f}" y="{ya + 14}" width="{mw:.1f}" height="36" fill="{CARD if n % 2 else EARTH_TINT}" stroke="{INK}"/>')
            out.append(text(qx + (m + 0.5) * mw, ya + 31, f"{n}", 13, "middle", "bold"))
            out.append(text(qx + (m + 0.5) * mw, ya + 45, "30", 10.5, "middle", fill=MUTED))
        out.append(f'<rect x="{qx + 3 * mw:.1f}" y="{ya + 14}" width="{tw}" height="36" fill="{GOLD}" stroke="{GOLD_EDGE}"/>')
        out.append(f'<path d="M{qx + 2:.1f} {ya + 62} H{qx + qw - 2:.1f}" stroke="{INK}" stroke-width="1"/>')
        out.append(text(qx + qw / 2, ya + 80, "91 days = 13 weeks", 12, "middle", fill=MUTED))
    out.append(text(x0, ya + 104, "1 Abib, month 1, always a Wednesday (Genesis 1:14-19)", 12.5, italic=True))
    out.append(text(x1, ya + 104, "gold: the 4 Tekufah days", 12.5, "end", italic=True, fill=GOLD_EDGE))
    out.append(text(W / 2, ya + 124, "1 Enoch 72-82 · Jubilees 6", 12, "middle", italic=True, fill=MUTED))

    # B. The ladder up to the jubilee: one column, sources state every rung.
    yb = ya + 170
    out.append(text(x0, yb, "THE LADDER", 13, weight="bold", fill=MUTED, spacing="1.5"))
    rungs = [
        (["Week", "7 days"], "Genesis 2:2-3 · Exodus 20:11"),
        (["Year", "52 weeks"], "1 Enoch 72-82 · Jubilees 6"),
        (["Sabbatical", "7 years; the seventh is a rest"], "Leviticus 25:1-7"),
        (["Jubilee", "7 × 7 = 49 years, then “the fiftieth year”"], "Leviticus 25:8-10"),
    ]
    cw = 400
    cx = (W - cw) / 2
    y = yb + 14
    for lines, ref in rungs:
        c, ch = card(cx, y, cw, lines, ref)
        out += c
        y += ch
        out.append(f'<path d="M{W / 2} {y} v18" stroke="{INK}" stroke-width="1.5"/>')
        out.append(arrow_head(W / 2, y + 20, 90, 9))
        y += 22
    # The fork.
    fy = y + 4
    out.append(f'<rect x="{x0}" y="{fy}" width="{x1 - x0}" height="64" rx="6" fill="{RED_TINT}" stroke="{RED}"/>')
    out.append(text(W / 2, fy + 24, "DOES THE FIFTIETH YEAR ALSO BEGIN THE NEXT COUNT?", 14, "middle", "bold", fill=RED))
    out.append(text(W / 2, fy + 45, "Leviticus does not say. The Talmud records both answers.", 13, "middle", italic=True))
    lx, rx, colw = x0, W / 2 + 10, (x1 - x0) / 2 - 10
    hy = fy + 92
    out += banner(lx + colw / 2, hy - 18, colw - 40, "NO · A 50-YEAR CYCLE", fill=BLUE, size=12.5)
    out += banner(rx + colw / 2, hy - 18, colw - 40, "YES · A 49-YEAR CYCLE", fill=GOLD_EDGE, size=12.5)
    left = [
        (["The Rabbis"], "b. Nedarim 61a · Rosh Hashanah 9a", False),
        (["10 jubilees = 500 years:", "the “Onah”"], "dsscalendar.org only", True),
        (["40 jubilees = 2,000 years:", "an age"], "the ages of b. Sanhedrin 97a", False),
        (["85 jubilees = 4,250 years"], "b. Sanhedrin 97b", False),
        (["140 jubilees = 7,000 years"], "dsscalendar.org’s Enoch wheel", True),
    ]
    right = [
        (["Rabbi Yehuda; Jubilees"], "b. Arakhin 12b · Jubilees 50:4", False),
        (["10 jubilees = 490 years:", "seventy weeks"], "Daniel 9:24 · 11Q13", False),
        (["40 jubilees = 1,960 years"], "no ancient scheme found", True),
        (["50 jubilees = 2,450 years:", "Adam to the Jordan"], "Jubilees 50:4", False),
    ]
    for col, items in ((lx, left), (rx, right)):
        y = hy + 20
        for lines, ref, dashed in items:
            c, ch = card(col, y, colw, lines, ref, dashed=dashed, stroke=BLUE if col == lx else GOLD_EDGE)
            out += c
            y += ch + 10
    ly = h - 104
    c, _ = card(x0, ly, 230, ["A source states it"], "", size=13)
    out += c
    c, _ = card(x0 + 255, ly, 330, ["A modern construction or reading"], "", dashed=True, size=13)
    out += c
    out += lines_at(W / 2, ly + 62, ["This site counts in fifties with dsscalendar.org, and holds it as a choice."],
                    13.5, anchor="middle", italic=True)
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 11. Larkin's "The Underworld", redrawn (at-home-with-the-lord.md, "Larkin's own chart")
#
# A redraw of the 1920 plate, not a chart of this site's reading: every label is Larkin's, in his
# order, and the study says where it parts from him. The dome is two concentric half-ellipses, the
# earth's surface over the underworld's, and the grave is the band between them.

UW_CX, UW_CY = 325, 1120
UW_EARTH = (338, 820)
UW_DOME = (300, 780)
UW_MID = (319, 800)
UW_OUTER = (329, 810)                   # "the wicked dead" runs along the grave's outer half
UW_INNER = (308, 790)                   # and "the righteous dead" along its inner half
UW_FLOOR = 965
UW_GRAVE_END = 31                       # degrees: the grave runs from Eden round to here
DARK = "#2a2018"
LAND = "#7f9a6a"
ADDED = BLUE                            # a reference this site adds to Larkin's point

# Each stream is shaded by who travels it, and each realm in the shade of those it holds, so a
# flow can be followed by colour from where it starts to where it ends.
FLOWS = {
    "christ": ("#ecd08a", "Christ"),
    "righteous": ("#d8e8c8", "The righteous"),
    "wicked": ("#efc6b8", "The wicked"),
    "angels": ("#d9d3ea", "The fallen angels"),
}
REALM = {"paradise": "#eef5e6", "hell": "#f7e1d9", "tartarus": "#ece9f5", "lake": "#f0cdbf",
         "grave": EARTH_TINT, "hill": "#8a7a5c"}


def uw_point(t_deg, r):
    t = math.radians(t_deg)
    return UW_CX + r[0] * math.cos(t), UW_CY - r[1] * math.sin(t)


def uw_t_at_x(x, r):
    return math.degrees(math.acos((x - UW_CX) / r[0]))


def uw_y(x, r):
    return uw_point(uw_t_at_x(x, r), r)[1]


def uw_arc(t0, t1, r):
    """The ellipse from t0 to t1 as an SVG arc, over the top when t0 > t1."""
    (x0, y0), (x1, y1) = uw_point(t0, r), uw_point(t1, r)
    return f"M{x0:.1f} {y0:.1f} A{r[0]} {r[1]} 0 0 {1 if t0 > t1 else 0} {x1:.1f} {y1:.1f}"


def along(pid, d, lines, size=10.5):
    """Lettering run along a path, centred on it. A line reads "bold|plain~added": the part before
    "|" is set bold, the part after "~" in ADDED, for a reference this site supplies."""
    out = [f'<defs><path id="{pid}" d="{d}"/></defs>']
    lh = size * 1.15
    for i, ln in enumerate(lines):
        dy = (i - (len(lines) - 1) / 2) * lh + size * 0.35
        main, _, added = ln.partition("~")
        bold, _, rest = main.partition("|") if "|" in main else ("", "", main)
        body = ((f'<tspan font-weight="bold">{esc(bold)}</tspan>' if bold else "") + esc(rest)
                + (f'<tspan fill="{ADDED}" font-style="italic">{esc(added)}</tspan>' if added else ""))
        out.append(f'<text font-size="{size}" fill="{INK}" dy="{dy:.1f}"><textPath href="#{pid}" '
                   f'startOffset="50%" text-anchor="middle">{body}</textPath></text>')
    return out


def ribbon(pid, d, w, flow, lines=(), label_d=None, size=10.5, mask=None):
    """Larkin's stream: a band ruled on both edges, shaded by who travels it. `mask` is a clip that
    hides the part inside the realms it leaves or enters, so it opens into them with no seam."""
    m = f' clip-path="url(#{mask})"' if mask else ""
    out = [f'<g{m}><path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2.6}"/>'
           f'<path d="{d}" fill="none" stroke="{FLOWS[flow][0]}" stroke-width="{w}"/></g>']
    if lines:
        out += along(pid, label_d or d, lines, size)
    return out


LEOPARD = "#c99a4c"
MANE = "#8a5a24"
# Revelation 13:1, "ten horns and seven heads, with ten diadems on its horns": the horns on each
# head, read left to right. The text does not say how they are shared out, only that there are ten.
BEAST_HORNS = [2, 1, 2, 1, 1, 2, 1]


def beast_from_sea(cx, base, s=1.0):
    """The beast of Revelation 13:1-2, facing left: a leopard's body, a bear's feet, seven heads each
    with a lion's mouth, and ten horns each crowned."""
    assert len(BEAST_HORNS) == 7 and sum(BEAST_HORNS) == 10

    def P(x, y):
        return f"{cx + x * s:.1f} {base + y * s:.1f}"

    out = [f'<path d="M{P(44, -20)} q{14 * s:.1f} {4 * s:.1f} {16 * s:.1f} {-10 * s:.1f} '
           f'q{2 * s:.1f} {-8 * s:.1f} {-6 * s:.1f} {-10 * s:.1f}" fill="none" stroke="{INK}" '
           f'stroke-width="{3.6 * s:.1f}" stroke-linecap="round"/>'
           f'<path d="M{P(44, -20)} q{14 * s:.1f} {4 * s:.1f} {16 * s:.1f} {-10 * s:.1f} '
           f'q{2 * s:.1f} {-8 * s:.1f} {-6 * s:.1f} {-10 * s:.1f}" fill="none" stroke="{LEOPARD}" '
           f'stroke-width="{2 * s:.1f}" stroke-linecap="round"/>']
    # A bear's feet: short heavy legs ending in broad clawed paws.
    for x in (-22, -11, 22, 34):
        out.append(f'<path d="M{P(x - 4, -14)} V{base - 3 * s:.1f} H{cx + (x + 4) * s:.1f} V{base - 14 * s:.1f}" '
                   f'fill="{LEOPARD}" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<ellipse cx="{cx + (x - 1) * s:.1f}" cy="{base - 2 * s:.1f}" rx="{6.5 * s:.1f}" '
                   f'ry="{2.8 * s:.1f}" fill="{MANE}" stroke="{INK}" stroke-width="1"/>')
        out.append("".join(f'<path d="M{P(x - 7 + 2.5 * k, -1)} l{-1.5 * s:.1f} {2.5 * s:.1f}" '
                           f'stroke="{INK}" stroke-width="0.9"/>' for k in range(3)))
    # A leopard's body, spotted.
    out.append(f'<path d="M{P(30, -32)} C{P(42, -32)} {P(48, -24)} {P(45, -16)} C{P(41, -10)} {P(30, -12)} '
               f'{P(20, -12)} L{P(-14, -12)} C{P(-25, -12)} {P(-31, -17)} {P(-31, -24)} C{P(-31, -32)} '
               f'{P(-22, -36)} {P(-12, -36)} C{P(0, -35)} {P(18, -33)} {P(30, -32)} Z" fill="{LEOPARD}" '
               f'stroke="{INK}" stroke-width="1.2"/>')
    spots = [(-18, -28), (-8, -31), (2, -27), (12, -31), (22, -27), (32, -26), (-12, -20), (6, -19),
             (26, -18), (38, -21), (-24, -22), (16, -23)]
    out.append("".join(f'<circle cx="{cx + x * s:.1f}" cy="{base + y * s:.1f}" r="{1.6 * s:.1f}" '
                       f'fill="none" stroke="{DARK}" stroke-width="{1.1 * s:.1f}"/>' for x, y in spots))
    # Seven necks fanned from the shoulders, each head a lion's: mane, open jaw, eye; its horns crowned.
    sx, sy = -24, -32
    for i, horns in enumerate(BEAST_HORNS):
        a = math.radians(205 - i * 25)
        ux, uy = math.cos(a), -math.sin(a)
        reach = 31 if i % 2 else 25
        hx, hy = sx + reach * ux, sy + reach * uy
        out.append(f'<path d="M{P(sx, sy)} L{P(hx, hy)}" stroke="{INK}" stroke-width="{4.6 * s:.1f}" '
                   f'stroke-linecap="round"/><path d="M{P(sx, sy)} L{P(hx, hy)}" stroke="{LEOPARD}" '
                   f'stroke-width="{2.8 * s:.1f}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx + hx * s:.1f}" cy="{base + hy * s:.1f}" r="{5 * s:.1f}" fill="{MANE}" '
                   f'stroke="{INK}" stroke-width="0.9"/>')
        out.append(f'<circle cx="{cx + (hx + ux) * s:.1f}" cy="{base + (hy + uy) * s:.1f}" r="{3.6 * s:.1f}" '
                   f'fill="{LEOPARD}" stroke="{INK}" stroke-width="0.8"/>')
        # The jaw opens on the side away from the shoulders: a dark wedge, toothed at its lips.
        jx, jy = hx + 2.6 * ux, hy + 2.6 * uy
        px, py = -uy, ux
        out.append(f'<path d="M{P(jx, jy)} L{P(jx + 5 * ux + 3 * px, jy + 5 * uy + 3 * py)} '
                   f'L{P(jx + 5 * ux - 3 * px, jy + 5 * uy - 3 * py)} Z" fill="{RED}" stroke="{INK}" stroke-width="0.6"/>')
        for k in range(horns):
            spread = 0 if horns == 1 else (-0.45 if k == 0 else 0.45)
            ha = -math.pi / 2 + 0.55 * ux + spread
            tx, ty = hx + 4 * math.cos(ha), hy + 4 * math.sin(ha)
            ex, ey = tx + 6 * math.cos(ha), ty + 6 * math.sin(ha)
            out.append(f'<path d="M{P(tx, ty)} L{P(ex, ey)}" stroke="{INK}" stroke-width="{1.4 * s:.1f}" '
                       f'stroke-linecap="round"/>')
            # Each horn's diadem: a small three-pointed crown at the tip.
            out.append(f'<path d="M{P(ex - 1.8, ey)} l{0.6 * s:.1f} {-2.4 * s:.1f} l{0.6 * s:.1f} {1.4 * s:.1f} '
                       f'l{0.6 * s:.1f} {-1.4 * s:.1f} l{0.6 * s:.1f} {1.4 * s:.1f} l{0.6 * s:.1f} {-1.4 * s:.1f} '
                       f'l{0.6 * s:.1f} {2.4 * s:.1f} Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="0.5"/>')
        out.append(f'<circle cx="{cx + (hx + 1.2 * ux - 1.4 * px) * s:.1f}" cy="{base + (hy + 1.2 * uy - 1.4 * py) * s:.1f}" '
                   f'r="{0.8 * s:.1f}" fill="{INK}"/>')
    return "".join(out)


def lamb_false_prophet(cx, base, s=1.0):
    """The beast from the earth of Revelation 13:11, the false prophet of 19:20, facing left: a lamb
    with two horns, speaking with a dragon's fire."""
    def P(x, y):
        return f"{cx + x * s:.1f} {base + y * s:.1f}"

    out = []
    for x in (-11, -5, 8, 14):
        out.append(f'<path d="M{P(x, -12)} V{base - 1.5 * s:.1f}" stroke="{INK}" stroke-width="{2 * s:.1f}"/>'
                   f'<path d="M{P(x - 1.4, -1.5)} h{2.8 * s:.1f} v{1.5 * s:.1f} h{-2.8 * s:.1f} Z" fill="{INK}"/>')
    wool = [(-12, -20), (-5, -25), (3, -26), (11, -24), (17, -19), (12, -14), (2, -13), (-8, -14)]
    out.append(f'<ellipse cx="{cx + 2 * s:.1f}" cy="{base - 19 * s:.1f}" rx="{17 * s:.1f}" ry="{8.5 * s:.1f}" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="1.1"/>')
    out.append("".join(f'<circle cx="{cx + x * s:.1f}" cy="{base + y * s:.1f}" r="{4.2 * s:.1f}" fill="{CARD}" '
                       f'stroke="{INK}" stroke-width="0.9"/>' for x, y in wool))
    out.append(f'<ellipse cx="{cx + 2 * s:.1f}" cy="{base - 19 * s:.1f}" rx="{14 * s:.1f}" ry="{6.5 * s:.1f}" fill="{CARD}"/>')
    out.append(f'<path d="M{P(-12, -22)} L{P(-17, -27)}" stroke="{INK}" stroke-width="{5 * s:.1f}" stroke-linecap="round"/>'
               f'<path d="M{P(-12, -22)} L{P(-17, -27)}" stroke="{CARD}" stroke-width="{3.4 * s:.1f}" stroke-linecap="round"/>')
    out.append(f'<ellipse cx="{cx - 21 * s:.1f}" cy="{base - 29 * s:.1f}" rx="{6.5 * s:.1f}" ry="{4.6 * s:.1f}" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<ellipse cx="{cx - 15.5 * s:.1f}" cy="{base - 29.5 * s:.1f}" rx="{3 * s:.1f}" ry="{1.6 * s:.1f}" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="0.8" transform="rotate(25 {cx - 15.5 * s:.1f} {base - 29.5 * s:.1f})"/>')
    # Two horns like a lamb's: short and curled.
    for x0 in (-23, -19):
        out.append(f'<path d="M{P(x0, -33)} q{-1 * s:.1f} {-5 * s:.1f} {3 * s:.1f} {-6 * s:.1f}" fill="none" '
                   f'stroke="{INK}" stroke-width="{1.5 * s:.1f}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx - 23 * s:.1f}" cy="{base - 30 * s:.1f}" r="{0.8 * s:.1f}" fill="{INK}"/>')
    # "It spoke like a dragon": fire from the lamb's mouth.
    out.append(f'<path d="M{P(-27, -27.5)} q{-6 * s:.1f} {-3 * s:.1f} {-11 * s:.1f} {-1 * s:.1f} '
               f'q{4 * s:.1f} {1 * s:.1f} {3 * s:.1f} {3 * s:.1f} q{-3 * s:.1f} {0 * s:.1f} {-5 * s:.1f} {2 * s:.1f} '
               f'q{6 * s:.1f} {1 * s:.1f} {13 * s:.1f} {-2.5 * s:.1f} Z" fill="{FIRE}" stroke="{RED}" stroke-width="0.6"/>')
    return "".join(out)


def dragon(cx, cy):
    """The dragon bound in the abyss (Revelation 20:1-3): coiled, wings raised, head turned up."""
    scale = "#9b7a4a"
    body = (f"M{cx - 50} {cy + 46} C{cx - 70} {cy + 14} {cx - 14} {cy + 4} {cx - 2} {cy + 24} "
            f"S{cx + 44} {cy + 56} {cx + 50} {cy + 14} S{cx + 26} {cy - 30} {cx} {cy - 22}")
    wing = lambda x, y, d: (f'<path d="M{x} {y} L{x + 30 * d} {y - 50} L{x + 22 * d} {y - 26} '
                            f'L{x + 44 * d} {y - 36} L{x + 30 * d} {y - 12} L{x + 50 * d} {y - 10} Z" '
                            f'fill="#7a5a34" stroke="{scale}" stroke-width="1.2"/>')
    return (wing(cx + 22, cy + 30, 1) + wing(cx + 4, cy + 28, -1)
            + f'<path d="{body}" fill="none" stroke="{scale}" stroke-width="10" stroke-linecap="round"/>'
            + f'<path d="{body}" fill="none" stroke="#5a4226" stroke-width="2" stroke-dasharray="3 6"/>'
            + f'<path d="M{cx + 2} {cy - 18} L{cx - 22} {cy - 34} L{cx - 30} {cy - 24} L{cx - 18} {cy - 22} '
              f'L{cx - 28} {cy - 14} L{cx - 4} {cy - 12} Z" fill="{scale}"/>'
            + f'<circle cx="{cx - 14}" cy="{cy - 25}" r="2" fill="{GOLD}"/>')


def the_underworld():
    h = 1125
    out = svg_open(
        h,
        "The Underworld, after Clarence Larkin",
        "A redrawing of Clarence Larkin's chart 'The Underworld' from Dispensational Truth (1918; "
        "expanded 1920), with his labels. A dome stands for the underworld, and the band over it is "
        "'The Grave', running from Eden, where Abel is the first laid in it, past the Flood, where the "
        "'Sons of God' (Genesis 6:1-4) go down to Tartarus. Inside the dome, 'Paradise', 'the abode of "
        "the souls of the righteous dead until Christ's resurrection; it is now empty', and 'Hell', "
        "'the abode of the souls of the wicked dead; still occupied', sit either side of 'The Great "
        "Gulf' (Luke 16:19-31), which opens down into the Abyss or Bottomless Pit, where a dragon lies "
        "bound. Below them are Tartarus, 'prison of the fallen angels' (2 Peter 2:4; Jude 6), and 'The "
        "Lake of Fire', 'Gehenna, the final hell' (Matthew 25:41; Revelation 19:20; 20:10, 14-15), with "
        "the Beast and the False Prophet in it, drawn as Revelation 13 describes them: the Beast like a "
        "leopard with a bear's feet and seven heads, each with a lion's mouth, carrying ten horns each "
        "crowned with a diadem (13:1-2); the False Prophet a lamb with two horns, speaking with a "
        "dragon's fire (13:11). A dotted line arcs over the Gulf from Hell to Paradise: seen and heard "
        "across, none may cross (Luke 16:23-26); whether Luke 16:19-31 is a parable or an account of the "
        "far side of death is debated. On the hill above stand three crosses. The soul of the "
        "penitent thief and the soul of Christ go down to Paradise; the impenitent thief's soul goes to "
        "Hell; Christ's soul returns to His body, and the righteous souls Christ took out of the "
        "underworld rise with Him as 'the First Fruits' (Ephesians 4:8-10; Psalm 68:18; Revelation "
        "1:18). On the right, the souls of the righteous return for their bodies and rise as 'The "
        "Harvest', the translation and first-resurrection saints (1 Thessalonians 4:15-17); seven "
        "years later 'The Gleanings', the tribulation saints (Revelation 20:4); a thousand years after "
        "that the wicked souls go for their bodies and rise as 'The Tares', the second resurrection "
        "(Revelation 20:11-15), with the fallen angels brought to judgment (Jude 6). 'The Sinner's "
        "Doom' comes back down into the lake of fire. Each stream is shaded by who travels it: gold "
        "for Christ, green for the righteous, red for the wicked, lavender for the fallen angels. "
        "References in blue are added from the study "
        "'At Home with the Lord': Luke 16:22 and 23:43 for Paradise, Luke 16:23 and Revelation 20:13 "
        "for Hell, 2 Corinthians 5:8, Philippians 1:23, 2 Corinthians 12:2-4 and Revelation 2:7 for "
        "the righteous now with Christ, 1 Corinthians 15:20-23 and Leviticus 23:10 for the first "
        "fruits, 1 Thessalonians 4:14 for the souls returning, 1 Corinthians 15:51-53 for the harvest, "
        "and Revelation 20:5 for the rest of the dead. Larkin's Ephesians 4:8-10 caption is boxed with "
        "a dashed line, as the one the study does not follow.",
    )
    defs = [f'<pattern id="uw-stip" width="7" height="7" patternUnits="userSpaceOnUse">'
            f'<circle cx="1.5" cy="1.5" r="0.8" fill="{MUTED}"/><circle cx="5" cy="5" r="0.6" fill="{MUTED}"/>'
            f'</pattern><clipPath id="uw-floor"><rect x="14" y="14" width="{W - 28}" height="{UW_FLOOR - 14}"/></clipPath>']
    head = len(out)

    out.append(text(34, 50, "THE", 22, weight="bold", spacing="1.5"))
    out.append(text(34, 76, "UNDERWORLD", 22, weight="bold", spacing="1.5"))
    out.append(f'<path d="M34 85 H228" stroke="{INK}" stroke-width="1.5"/>')
    out += lines_at(34, 106, ["Clarence Larkin, Dispensational Truth (1920)", "redrawn, with the study’s verses added"],
                    12.5, italic=True, fill=MUTED)

    # Every realm a stream can open into. Each is drawn at inset 0; a stream is clipped to the
    # outside of the same shape inset by most of its outline, so where it crosses the outline it
    # covers it, and the join reads as an opening.
    g0, g1 = 147, UW_GRAVE_END
    hx, hy = UW_CX, UW_CY - UW_EARTH[1]
    row0, row1 = 600, 716
    par, gulf, hell = (122, 276), (286, 364), (374, 480)
    tar, lake = (50, 248, 790), (410, 596, 786)

    def grave_d(i=0):
        outer, inner = (UW_EARTH[0] - i, UW_EARTH[1] - i), (UW_DOME[0] + i, UW_DOME[1] + i)
        (ox0, oy0), (ix0, iy0), (ix1, iy1) = uw_point(g0, outer), uw_point(g0, inner), uw_point(g1, inner)
        return (f"{uw_arc(g0, g1, outer)} L{ix1:.1f} {iy1:.1f} A{inner[0]} {inner[1]} 0 0 0 {ix0:.1f} {iy0:.1f} "
                f"A{19 - i} {19 - i} 0 0 1 {ox0:.1f} {oy0:.1f} Z")

    def hill_d(i=0):
        return (f"M{hx - 95 + i} {hy + 22 - i} C{hx - 80 + i} {hy - 22 + i} {hx - 40} {hy - 34 + i} {hx} {hy - 36 + i} "
                f"C{hx + 40} {hy - 34 + i} {hx + 85 - i} {hy - 22 + i} {hx + 100 - i} {hy + 22 - i} Z")

    def box_d(x0, x1, i=0):
        return f"M{x0 + i} {row0 + i} H{x1 - i} V{row1 - i} H{x0 + i} Z"

    def domed(x0, x1, top, i=0):
        x0, x1, top = x0 + i, x1 - i, top + i
        return (f"M{x0} {UW_FLOOR - 12} V{top + 50} Q{x0} {top} {x0 + 60} {top} H{x1 - 60} "
                f"Q{x1} {top} {x1} {top + 50} V{UW_FLOOR - 12} Z")

    shapes = {
        "grave": grave_d, "hill": hill_d,
        "paradise": lambda i=0: box_d(*par, i), "hell": lambda i=0: box_d(*hell, i),
        "tartarus": lambda i=0: domed(*tar, i), "lake": lambda i=0: domed(*lake, i),
    }
    masks = {}

    def realm(name):
        d = shapes[name]()
        if name in ("paradise", "hell"):
            x0, x1 = par if name == "paradise" else hell
            return (f'<rect x="{x0}" y="{row0}" width="{x1 - x0}" height="{row1 - row0}" rx="12" '
                    f'fill="{REALM[name]}" stroke="{INK}" stroke-width="1.6"/>')
        return f'<path d="{d}" fill="{REALM[name]}" stroke="{INK}" stroke-width="1.6"/>'

    def opening(*names):
        cid = "uw-out-" + "-".join(names)
        if cid not in masks:
            holes = " ".join(shapes[n](1.4) for n in names)
            masks[cid] = (f'<clipPath id="{cid}"><path clip-rule="evenodd" '
                          f'd="M0 0 H{W} V{h} H0 Z {holes}"/></clipPath>')
        return cid

    # The underworld, and the grave over it from Eden round to where the wicked dead rise.
    out.append(f'<g clip-path="url(#uw-floor)"><ellipse cx="{UW_CX}" cy="{UW_CY}" rx="{UW_DOME[0]}" '
               f'ry="{UW_DOME[1]}" fill="url(#uw-stip)" stroke="{INK}" stroke-width="1.6"/></g>')
    out.append(f'<path d="M14 {UW_FLOOR} H{W - 14}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(realm("grave"))
    ox0, oy0 = uw_point(g0, UW_EARTH)
    rt, hv, gl, ta, an, dm = 470, 497, 545, 596, 655, 686
    out += along("uw-grave", uw_arc(133, 115, UW_MID), ["THE GRAVE"], 19)
    out[-1] = out[-1].replace('<text ', '<text font-weight="bold" letter-spacing="3" ')
    out += along("uw-rdead", uw_arc(uw_t_at_x(488, UW_INNER), uw_t_at_x(550, UW_INNER), UW_INNER),
                 ["The righteous dead|"], 9.5)
    out += along("uw-wdead", uw_arc(uw_t_at_x(gl + 11, UW_OUTER), uw_t_at_x(ta - 15, UW_OUTER), UW_OUTER),
                 ["The wicked dead|"], 9)

    # Eden, Abel the first in the grave, and the Flood.
    ex, ey = ox0 + 2, oy0 + 36
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="22" fill="{BLUE_TINT}" stroke="{INK}" stroke-width="1.4"/>'
               f'<path d="M{ex - 14:.1f} {ey - 6:.1f} q8 -10 16 -4 q6 6 -2 12 q-10 4 -14 -8 z '
               f'M{ex + 4:.1f} {ey + 8:.1f} q8 -4 12 2 q-4 8 -12 -2 z" fill="{LAND}"/>')
    out.append(text(ex, ey - 28, "EDEN", 11, "middle", "bold", spacing="1"))
    ax, ay = uw_point(141, UW_MID)
    out.append(text(ax + 2, ay + 4, "Abel", 10.5, "middle", italic=True, extra=f'transform="rotate(-58 {ax + 2:.1f} {ay + 4:.1f})"'))
    fx, fy = uw_point(134, UW_EARTH)
    out.append(f'<g transform="translate({fx:.1f} {fy - 4:.1f}) rotate(-40)">'
               f'<path d="M-16 0 H16 L11 9 H-11 Z" fill="{MUTED}" stroke="{INK}"/>'
               f'<rect x="-8" y="-8" width="16" height="8" fill="{CARD}" stroke="{INK}"/>'
               f'<path d="M-10 -8 L0 -14 L10 -8" fill="none" stroke="{INK}"/></g>')
    out += lines_at(fx - 8, fy - 30, ["THE FLOOD"], 10.5, weight="bold", anchor="middle")
    out += lines_at(fx - 36, fy - 6, ["Sons of God", "Gen 6:1-4"], 10.5, anchor="end", italic=True, extra=HALO)

    # The realms of the dead.
    out.append(realm("paradise"))
    pm = (par[0] + par[1]) / 2
    out.append(text(pm, row0 + 28, "“PARADISE”", 16, "middle", "bold", spacing="1"))
    out += lines_at(pm, row0 + 42, ["The abode of the souls of", "the “righteous dead” until",
                                    "Christ’s resurrection."], 11.5, anchor="middle")
    out.append(text(pm, row0 + 90, "Luke 16:22", 10.5, "middle", italic=True, fill=ADDED))
    out.append(text(pm, row0 + 108, "It is now EMPTY", 11.5, "middle", "bold"))
    out.append(realm("hell"))
    out.append(flames(hell[0] + 6, hell[1] - 10, row1 - 2, 18))
    hm = (hell[0] + hell[1]) / 2
    out.append(text(hm, row0 + 28, "“HELL”", 16, "middle", "bold", spacing="1"))
    out += lines_at(hm, row0 + 42, ["The abode of the", "souls of the", "“wicked dead”"], 11.5, anchor="middle", extra=HALO)
    out.append(text(hm, row0 + 90, "Luke 16:23 · Rev 20:13", 9.5, "middle", italic=True, fill=ADDED, extra=HALO))
    out.append(text(hm, row0 + 108, "Still occupied", 11.5, "middle", "bold", extra=HALO))
    out.append(realm("tartarus"))
    tm = (tar[0] + tar[1]) / 2
    out.append(text(tm, tar[2] + 70, "“TARTARUS”", 15, "middle", "bold", spacing="1"))
    out += lines_at(tm, tar[2] + 92, ["Prison of the", "“fallen angels”"], 12, anchor="middle")
    out.append(text(tm, tar[2] + 132, "2 Peter 2:4 · Jude 6", 11, "middle", italic=True))
    out.append(realm("lake"))
    lm = (lake[0] + lake[1]) / 2
    out.append(text(lm, lake[2] + 30, "“THE LAKE OF FIRE”", 13.5, "middle", "bold"))
    out += lines_at(lm, lake[2] + 46, ["“Gehenna,” the final hell", "Matt 25:41",
                                       "Rev 19:20; 20:10, 14-15"], 11, lh=14.5, anchor="middle", italic=True)
    out.append(flames(lake[0] + 8, lake[1] - 10, UW_FLOOR - 26, 18))
    out.append(beast_from_sea(470, 938, 0.84))
    out.append(lamb_false_prophet(567, 938, 1.05))
    out.append(flames(lake[0] + 4, lake[1] - 6, UW_FLOOR - 13, 12))
    out.append(text(462, 950, "The Beast", 10.5, "middle", "bold", extra=HALO))
    out.append(text(558, 950, "False Prophet", 10.5, "middle", "bold", extra=HALO))

    # The fallen angels, out of Tartarus to judgment. They pass behind the gulf, which is drawn next.
    fa = 740
    out += ribbon("uw-fa", f"M150 {tar[2] + 24} V{fa + 14} Q150 {fa} 164 {fa} H{an - 14} Q{an} {fa} {an} {fa - 14} V14",
                  16, "angels", mask=opening("tartarus"))
    out += along("uw-fa1", f"M164 {fa} H{gulf[0]}", ["Fallen angels to judgment"], 9)
    out += along("uw-fa2", f"M{gulf[1]} {fa} H{an - 14}", ["Fallen angels to judgment"], 9)
    out += along("uw-fa3", f"M{an} {fa - 40} V14", ["Fallen angels to judgment · Jude 6"], 9.5)
    out.append(arrow_head(150, tar[2] - 8, -90, 8))

    # The gulf, opening down into the abyss.
    neck0, neck1, jar_top = 306, 344, 780
    jar = (256, 394)
    out.append(f'<path d="M{jar[0]} {UW_FLOOR} V{jar_top + 40} Q{jar[0]} {jar_top} {neck0} {jar_top} V{jar_top - 14} '
               f'H{neck1} V{jar_top} Q{jar[1]} {jar_top} {jar[1]} {jar_top + 40} V{UW_FLOOR} Z" fill="{DARK}" stroke="{INK}" stroke-width="1.6"/>')
    for i in range(5):
        out.append(f'<path d="M{jar[0] + 6} {jar_top + 46 + i * 30} q16 -10 32 0 t32 0 t32 0 t32 0" fill="none" '
                   f'stroke="#5a4a36" stroke-width="1.4"/>')
    out.append(dragon(318, 852))
    out.append(text(325, 926, "ABYSS", 13, "middle", "bold", fill=PAPER, spacing="1.5"))
    out.append(text(325, 945, "Bottomless Pit", 11.5, "middle", fill=PAPER, italic=True))
    out.append(f'<path d="M{gulf[0]} {row0} H{gulf[1]} V{jar_top - 32} Q{gulf[1]} {jar_top - 22} {neck1} {jar_top - 22} '
               f'V{jar_top - 14} H{neck0} V{jar_top - 22} Q{gulf[0]} {jar_top - 22} {gulf[0]} {jar_top - 32} Z" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="1.6"/>')
    # Across the gulf: seen and heard, never crossed (Luke 16:23-26). Dotted, as a line of sight and
    # speech, so that nobody reads it as a way through.
    out.append(f'<path d="M{par[1] - 8} {row0 - 2} Q325 {row0 - 34} {hell[0] + 8} {row0 - 2}" fill="none" '
               f'stroke="{INK}" stroke-width="1.8" stroke-dasharray="0.1 4.5" stroke-linecap="round"/>')
    out += [arrow_head(par[1] - 7, row0, 115, 7), arrow_head(hell[0] + 7, row0, 65, 7)]
    out.append(f'<path d="M321 {row0 - 24} v-12 M329 {row0 - 24} v-12" stroke="{RED}" stroke-width="1.8"/>')
    out += lines_at(344, row0 - 60, ["seen and heard across,", "none may cross"], 9.5, lh=11, anchor="middle",
                    italic=True, extra=HALO)
    out.append(text(344, row0 - 38, "Luke 16:23-26", 9.5, "middle", italic=True, fill=ADDED, extra=HALO))
    out += lines_at(325, row0 + 26, ["THE", "GREAT", "GULF"], 14, lh=18, anchor="middle", weight="bold")
    out.append(text(325, row0 + 90, "Luke 16:19-31", 10.5, "middle", italic=True))

    # The hill and the tomb. Souls go down out of the hill's foot into the earth; Christ rises out of
    # its top.
    out.append(realm("hill"))
    out.append(f'<path d="M{hx + 4} {hy - 12} v-12 a10 10 0 0 1 20 0 v12 z" fill="{DARK}"/>'
               f'<circle cx="{hx - 6}" cy="{hy - 16}" r="9" fill="{CARD}" stroke="{INK}" stroke-width="1.2"/>')
    pc, cc, ic = hx - 58, hx - 12, hx + 72
    up1, up2 = hx + 14, hx + 36
    into = row0 + 24
    out += ribbon("uw-ps", f"M148 {into} C148 470 {pc - 14} 400 {pc} 300", 17, "righteous",
                  ["The soul of penitent thief to Paradise~ · Luke 23:43"], mask=opening("hill", "paradise"))
    out += ribbon("uw-cs", f"M182 {into} C182 480 {cc - 8} 410 {cc} 300", 17, "christ",
                  ["The soul of Christ went to Paradise"], mask=opening("hill", "paradise"))
    out += ribbon("uw-cr", f"M216 {into} C216 500 {cc + 22} 430 {cc + 22} 300", 17, "christ",
                  ["Return of Christ’s soul to His body"], mask=opening("hill", "paradise"))
    out += ribbon("uw-ff", f"M{up1} 300 V14", 17, "christ", ["First fruits of the resurrection"],
                  label_d=f"M{up1} {hy - 34} V14", mask=opening("hill"))
    out += ribbon("uw-to", f"M252 {into} C252 500 {up2} 480 {up2} 390 V14", 19, "righteous",
                  ["The righteous souls Christ took out of the underworld~ · 2 Cor 5:8 · Phil 1:23 · 2 Cor 12:2-4 · Rev 2:7"],
                  size=10, mask=opening("paradise"))
    out += ribbon("uw-is", f"M{ic} 300 C{ic + 6} 400 440 470 440 {into}", 17, "wicked",
                  ["The impenitent thief’s soul went to Hell"], mask=opening("hill", "hell"))
    for x in (148, 182, 440):
        out.append(arrow_head(x, row0 + 9, 90, 7))
    out.append(arrow_head(216, row0 - 30, -90, 8))
    out.append(arrow_head(252, row0 - 30, -90, 8))
    out.append(arrow_head(up1, 40, -90, 7))
    out.append(arrow_head(up2, 40, -90, 7))

    for name, x in (("penitent", pc), ("christ", cc), ("impenitent", ic)):
        top, foot = (hy - 120, hy - 30) if name == "christ" else (hy - 104, hy - 16)
        out.append(f'<path d="M{x} {top} V{foot} M{x - 15} {top + 18} H{x + 15}" stroke="{INK}" stroke-width="5.5"/>')
    out += lines_at(pc - 17, hy - 92, ["Penitent", "thief"], 10.5, anchor="end", weight="bold")
    out.append(text(cc + 12, hy - 128, "CHRIST", 12.5, "end", "bold", spacing="1"))
    out += lines_at(ic + 10, hy - 122, ["Impenitent", "thief"], 10.5, lh=12, anchor="middle", weight="bold")

    # Larkin's "body to grave", each thief's body down into the earth beside his cross.
    for x0, side in ((pc - 6, -1), (ic + 6, 1)):
        x1 = x0 + 26 * side
        out.append(f'<path d="M{x0} {hy - 24} L{x1} {hy + 22}" stroke="{INK}" stroke-width="1.3"/>')
        out.append(arrow_head(x1, hy + 26, 90 - 29 * side, 7))
        ang = 61 if side > 0 else -61
        lx, ly = (x0 + 13, hy - 20) if side > 0 else (x1 - 10, hy + 18)
        out.append(text(lx, ly, "body to grave", 9.5, italic=True, extra=f'{HALO} transform="rotate({ang} {lx} {ly})"'))

    out.append(text(up1 - 22, 156, "THE “FIRST FRUITS”", 11, "start", "bold", spacing="0.5",
                    extra=f'transform="rotate(-90 {up1 - 22} 156)"'))
    out.append(text(up1 - 36, 156, "1 Cor 15:20-23 · Lev 23:10", 10, italic=True, fill=ADDED,
                    extra=f'transform="rotate(-90 {up1 - 36} 156)"'))
    ex1 = up2 + 20
    out += [text(ex1, 160, "Eph 4:8-10 (Psa 68:18)", 10.5, italic=True, extra=f'transform="rotate(-90 {ex1} 160)"'),
            text(ex1 + 13, 160, "Rev 1:18", 10.5, italic=True, extra=f'transform="rotate(-90 {ex1 + 13} 160)"')]
    # The caption this study does not follow (see "Did the descent empty Abraham's side?").
    out.append(f'<rect x="{ex1 - 12}" y="38" width="16" height="128" rx="3" fill="none" stroke="{INK}" '
               f'stroke-width="1" stroke-dasharray="4 3"/>')

    # The resurrections, up the right-hand side, each out of the grave: the harvest, the gleanings
    # seven years on, the tares a thousand years after that.
    def base(x, w, sink=24):
        return uw_y(x, UW_EARTH) + sink, uw_y(x - w / 2, UW_EARTH)

    rt_y, _ = base(rt, 14)
    out += ribbon("uw-rt", f"M{rt} 14 V{rt_y}", 14, "righteous",
                  ["Souls of the righteous returning for their bodies~ · 1 Thess 4:14"],
                  label_d=f"M{rt} 30 V{rt_y - 30}", size=10, mask=opening("grave"))
    out.append(arrow_head(rt, uw_y(rt, UW_EARTH) + 8, 90, 7))
    hv_y, hv_top = base(hv, 27)
    out += ribbon("uw-hv", f"M{hv} {hv_y} V14", 27, "righteous",
                  ["“The Harvest”|  1 Thess 4:15-17 · Translation saints",
                   "First resurrection saints · “The dead in Christ shall rise first”~ · 1 Cor 15:51-53"],
                  label_d=f"M{hv} {hv_top} V14", size=10, mask=opening("grave"))
    gl_y, gl_top = base(gl, 19)
    out += ribbon("uw-gl", f"M{gl} {gl_y} V14", 19, "righteous", ["“The Gleanings”|  Rev 20:4 · Tribulation saints"],
                  label_d=f"M{gl} {gl_top} V14", mask=opening("grave"))
    _, ta_top = base(ta, 27)
    out += ribbon("uw-ta", f"M{ta} 690 V14", 27, "wicked",
                  ["“The Tares”|  Rev 20:11-15 · The second resurrection — the wicked dead",
                   "“The rest of the dead live not until the end of 1000 years”~ Rev 20:5"],
                  label_d=f"M{ta} {ta_top} V14", size=10, mask=opening("grave"))
    out += ribbon("uw-ws", f"M{hell[1] - 14} 664 C520 664 552 660 576 626", 22, "wicked",
                  ["Wicked souls going", "for their bodies"], label_d=f"M{hell[1]} 664 C516 664 540 662 560 648",
                  size=8.5, mask=opening("hell", "grave"))
    for x in (hv, gl, ta):
        out.append(arrow_head(x, 40, -90, 7))

    # The sinner's doom, back down into the lake of fire.
    dd = 768
    out += ribbon("uw-dm", f"M{dm} 14 V{dd - 14} Q{dm} {dd} {dm - 14} {dd} H{lm + 14} Q{lm} {dd} {lm} {dd + 14} V{lake[2] + 24}",
                  16, "wicked", mask=opening("lake"))
    out += along("uw-dm1", f"M{lm + 20} {dd} H{dm - 20}", ["The sinner’s doom"], 9.5)
    out += along("uw-dm2", f"M{dm} {dd - 40} V14", ["The sinner’s doom"], 9.5)
    out.append(arrow_head(lm, lake[2] + 14, 90, 9))
    out.append(arrow_head(dm, 40, 90, 7))

    # The sons of God, from the Flood down to Tartarus.
    sx, sy = uw_point(136, UW_MID)
    out += ribbon("uw-sg", f"M{sx:.1f} {sy:.1f} C{sx + 4:.1f} {sy + 120:.1f} 98 700 104 {tar[2] + 24}", 12, "angels",
                  mask=opening("grave", "tartarus"))
    out.append(arrow_head(105, tar[2] + 14, 88, 9))

    # The years between the resurrections.
    out.append(f'<path d="M{hv + 15} 60 H{gl - 11} M{gl + 11} 60 H{ta - 15}" stroke="{INK}" stroke-width="1"/>')
    out += [arrow_head(hv + 15, 60, 180, 6), arrow_head(gl - 11, 60, 0, 6),
            arrow_head(gl + 11, 60, 180, 6), arrow_head(ta - 15, 60, 0, 6)]
    out += lines_at((hv + gl) / 2, 80, ["7", "years"], 8.5, lh=11, anchor="middle", weight="bold")
    out += lines_at((gl + ta) / 2, 80, ["1000", "years"], 8.5, lh=11, anchor="middle", weight="bold")

    # The key: who travels each stream, then whose words are whose.
    ky = UW_FLOOR + 26
    out.append(text(34, ky, "The streams:", 12.5, weight="bold"))
    x = 128
    for colour, label in FLOWS.values():
        out.append(f'<rect x="{x}" y="{ky - 11}" width="26" height="13" fill="{colour}" stroke="{INK}" stroke-width="1"/>')
        out.append(text(x + 32, ky, label, 12.5))
        x += 50 + len(label) * 6.6
    out.append(text(34, ky + 22, "Black: Larkin’s labels and references.", 12.5, weight="bold"))
    out.append(text(286, ky + 22, "Blue: the verses the study beside it rests each point on.", 12.5,
                    italic=True, fill=ADDED))
    out.append(f'<rect x="34" y="{ky + 32}" width="34" height="14" rx="3" fill="none" stroke="{INK}" '
               f'stroke-dasharray="4 3"/>')
    out.append(text(76, ky + 44, "Dashed: Larkin’s caption the study does not follow (Ephesians 4:8-10).",
                    12.5, italic=True, fill=MUTED))
    out.append(f'<path d="M36 {ky + 61} H66" stroke="{INK}" stroke-width="1.8" stroke-dasharray="0.1 4.5" '
               f'stroke-linecap="round"/>')
    out.append(text(76, ky + 66, "Dotted: seen and heard across the gulf, never crossed (Luke 16:23-26). Whether",
                    12.5, italic=True, fill=MUTED))
    out.append(text(76, ky + 83, "Luke 16:19-31 is a parable or an account of the far side of death is debated.",
                    12.5, italic=True, fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    out.insert(head, f'<defs>{"".join(defs)}{"".join(masks.values())}</defs>')
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# 12. Sown and raised: the body God has promised (we-shall-all-be-changed.md)
#
# One plate in five panels, one for each question 1 Corinthians 15:35-58 answers, in the study's
# order: how (the seed), what kind (four contrasts), whose image (two Adams), when (the last
# trumpet), and death swallowed up. Each panel is also cut out as a detail and set beside its
# section. Quotations are the ESV as the study quotes it; a dashed outline is a reading the study
# marks contested or a variant.

SOIL = "#cdb48a"
SOIL_DARK = "#a88a5c"
GRAIN = "#d9b25a"
STALK = "#8a9a4a"
DIM = "#b9ab90"
BODY_PANELS = []        # top of each panel and the plate's height, as sown_and_raised() last laid them out
BODY_GAP = 50


def panel_head(y, label, ask):
    return banner(W / 2, y, 380, label) + [text(W / 2, y + 50, ask, 14, "middle", italic=True, fill=MUTED)]


def kernel(cx, cy, s=1.0, fill=GRAIN, rot=-20):
    return (f'<g transform="translate({cx} {cy}) rotate({rot}) scale({s})">'
            f'<ellipse rx="13" ry="8" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>'
            f'<path d="M-9 0 Q0 -2 9 0" fill="none" stroke="{GOLD_EDGE}" stroke-width="1.2"/></g>')


def wheat(cx, base, top, full=True, droop=0):
    """A wheat stalk from base up to top. full=False is a thin, empty ear; droop bends the head."""
    hx = cx + droop
    out = [f'<path d="M{cx} {base} C{cx} {base - (base - top) * 0.5} {cx + droop * 0.2} {top + 30} {hx} {top}" '
           f'fill="none" stroke="{STALK}" stroke-width="{3 if full else 2}"/>']
    if full:
        mid = base - (base - top) * 0.45
        out.append(f'<path d="M{cx} {mid} q-26 -10 -34 -36 q16 10 34 22" fill="{STALK}" opacity="0.9"/>'
                   f'<path d="M{cx} {mid + 26} q26 -8 36 -34 q-18 10 -36 20" fill="{STALK}" opacity="0.9"/>')
    n, gap = (7, 7) if full else (4, 5)
    ang = math.degrees(math.atan2(droop, 30)) if droop else 0
    grains = []
    for i in range(n):
        y = -i * gap
        for side in (-1, 1):
            grains.append(f'<ellipse cx="{side * 4.5}" cy="{y - 4}" rx="{4.2 if full else 2.6}" ry="{6.5 if full else 4}" '
                          f'transform="rotate({side * 18} {side * 4.5} {y - 4})" fill="{GRAIN if full else DIM}" '
                          f'stroke="{GOLD_EDGE if full else MUTED}" stroke-width="0.8"/>')
            if full:
                grains.append(f'<path d="M{side * 6} {y - 9} l{side * 9} -16" stroke="{GOLD_EDGE}" stroke-width="0.7"/>')
    out.append(f'<g transform="translate({hx} {top}) rotate({ang})">{"".join(grains)}</g>')
    return "".join(out)


def star(cx, cy, r, fill, stroke, rays=False):
    pts = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        rr = r if k % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    out = ""
    if rays:
        out = "".join(f'<path d="M{cx + (r + 3) * math.cos(math.radians(a)):.1f} {cy + (r + 3) * math.sin(math.radians(a)):.1f} '
                      f'L{cx + (r + 9) * math.cos(math.radians(a)):.1f} {cy + (r + 9) * math.sin(math.radians(a)):.1f}" '
                      f'stroke="{GOLD_EDGE}" stroke-width="1.4"/>' for a in range(-72, 288, 36))
    return out + f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'


def glow(cx, cy, r, gid):
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.85"/>'
            f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>')


def flame(cx, base, h=26):
    return (f'<path d="M{cx} {base} c-12 0 -14 -12 -8 -20 c2 6 6 6 6 2 c0 -6 -2 -10 2 -{h - 6} '
            f'c4 8 12 12 12 24 c0 8 -6 14 -12 14 z" fill="{GOLD}" stroke="{FIRE}" stroke-width="1.3"/>'
            f'<path d="M{cx} {base - 2} c-5 0 -6 -6 -3 -10 c1 3 3 3 3 0 c3 4 6 6 6 9 c0 2 -3 4 -6 1 z" fill="{FIRE}" opacity="0.8"/>')


def breath(cx, cy):
    return "".join(f'<path d="M{cx - 16} {cy + k * 8} q6 -6 12 0 t12 0 t12 0" fill="none" stroke="{MUTED}" '
                   f'stroke-width="1.6" stroke-linecap="round"/>' for k in (-1, 0, 1))


def open_tomb(cx, base):
    return (f'<path d="M{cx - 46} {base} Q{cx - 44} {base - 52} {cx} {base - 56} Q{cx + 44} {base - 52} {cx + 46} {base} Z" '
            f'fill="#8a7a5c" stroke="{INK}" stroke-width="1.3"/>'
            f'<path d="M{cx - 12} {base} v-22 a12 12 0 0 1 24 0 v22 z" fill="{DARK}"/>'
            f'<circle cx="{cx + 34}" cy="{base - 13}" r="13" fill="{CARD}" stroke="{INK}" stroke-width="1.3"/>')


def trumpet(cx, cy):
    return (f'<path d="M{cx - 70} {cy - 3} H{cx + 20} L{cx + 52} {cy - 18} V{cy + 18} L{cx + 20} {cy + 3} H{cx - 70} Z" '
            f'fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>'
            f'<rect x="{cx - 78}" y="{cy - 5}" width="9" height="10" rx="2" fill="{GOLD}" stroke="{GOLD_EDGE}"/>'
            + "".join(f'<path d="M{cx + 60 + k * 9} {cy - 14 - k * 5} q{8 + k * 3} {14 + k * 5} 0 {28 + k * 10}" fill="none" '
                      f'stroke="{GOLD_EDGE}" stroke-width="1.5" stroke-linecap="round"/>' for k in range(3)))


def grave(cx, base):
    return f'<path d="M{cx - 26} {base} Q{cx} {base - 20} {cx + 26} {base} Z" fill="{SOIL_DARK}" stroke="{INK}" stroke-width="1.1"/>'


def sown_and_raised():
    out = []
    head = dict(
        title=
"Sown and raised: the body God has promised",
        desc="A plate in five panels on 1 Corinthians 15:35-58. "
        "1, The seed (15:36-38): a bare kernel is sown in the soil and dies, and God gives it a body as He "
        "has chosen, a full wheat plant growing from the same seed, as 'this perishable body' puts on the "
        "imperishable (15:53). Beneath, Jesus' risen body shows both halves: the same body, His hands and "
        "feet, flesh and bones, eating fish, the wounds still there (Luke 24:39-43; John 20:27), and "
        "changed, not recognised on the road and standing among them with the doors locked (Luke 24:16; "
        "John 20:19). "
        "2, Four contrasts (15:42-44): sown perishable, raised imperishable; sown in dishonour, raised in "
        "glory; sown in weakness, raised in power; sown a natural body, raised a spiritual body, each with "
        "its Greek. 'Spiritual' says what animates the body, the Holy Spirit (Romans 8:11), and the body "
        "is still flesh and bones (Luke 24:39). "
        "3, Two Adams (15:45-49): the first man Adam, from the earth, a man of dust, became a living being "
        "(Genesis 2:7); the last Adam, from heaven, became a life-giving spirit, beside an open tomb. First "
        "the natural, then the spiritual. We have borne the image of the man of dust; we shall bear the "
        "image of the man of heaven, with the variant 'let us bear' in two early manuscripts marked "
        "dashed. "
        "4, Changed in a moment (15:50-53): at the last trumpet, in a moment, in the twinkling of an eye, "
        "the dead rise from their graves imperishable and the living are changed, at one sound. The "
        "perishable puts on the imperishable and the mortal puts on immortality, which God alone has "
        "(1 Timothy 6:16). A dashed note marks the timing as contested. "
        "5, Death swallowed up (15:54-57): the law gives sin its power, and sin is death's sting; Christ "
        "died for our sins (15:3), and the chain is broken there. Death is swallowed up in victory "
        "(Isaiah 25:8); O death, where is your sting? (Hosea 13:14). The plate closes with 15:57: thanks be "
        "to God, who gives us the victory through our Lord Jesus Christ.",
    )
    out += heading("We Shall All Be Changed", "Sown and raised · 1 Corinthians 15:35-58")
    p1 = 110

    # 1. The seed: how are the dead raised?
    out += panel_head(p1, "1 · THE SEED", "“How are the dead raised?” (1 Corinthians 15:35)")
    gy, sy = p1 + 260, p1 + 330
    out.append(f'<rect x="30" y="{gy}" width="{W - 60}" height="{sy - gy}" fill="{SOIL}"/>')
    out.append("".join(f'<circle cx="{40 + (k * 53) % 640}" cy="{gy + 12 + (k * 29) % 56}" r="1.4" fill="{SOIL_DARK}"/>'
                       for k in range(40)))
    out.append(f'<path d="M30 {gy} H{W - 30}" stroke="{INK}" stroke-width="1.6"/>')
    kx, px = 170, 540
    out.append(kernel(kx, gy + 34, 1.2))
    out += lines_at(kx, gy - 64, ["SOWN"], 15, anchor="middle", weight="bold", spacing="1.5")
    out += lines_at(kx, gy - 40, ["“a bare kernel”", "1 Cor 15:37"], 13, anchor="middle", italic=True)
    out.append(text(kx, gy + 62, "“unless it dies” (15:36)", 12, "middle", italic=True))
    # The plant grows from the same seed: its husk stays in the ground, rooted.
    out.append(kernel(px, gy + 34, 1.2, fill=SOIL_DARK))
    out.append("".join(f'<path d="M{px} {gy + 38} q{dx * 0.5} 10 {dx} {dy}" fill="none" stroke="{SOIL_DARK}" stroke-width="1.4"/>'
                       for dx, dy in ((-30, 24), (-14, 30), (6, 32), (22, 26), (34, 18))))
    out.append(wheat(px, gy + 30, p1 + 132))
    out += lines_at(px + 92, gy - 64, ["RAISED"], 15, anchor="middle", weight="bold", spacing="1.5")
    out += lines_at(px + 92, gy - 40, ["“the body", "that is to be”", "1 Cor 15:37"], 13, anchor="middle", italic=True)
    out.append(f'<path d="M{kx + 40} {gy - 96} C{kx + 100} {p1 + 126} {px - 120} {p1 + 126} {px - 34} {gy - 110}" '
               f'fill="none" stroke="{GOLD_EDGE}" stroke-width="3"/>')
    out.append(arrow_head(px - 32, gy - 107, 55, 12, GOLD_EDGE))
    out += lines_at((kx + px) / 2, p1 + 82, ["“God gives it a body", "as he has chosen”", "1 Cor 15:38"], 13.5,
                    anchor="middle", italic=True)
    out.append(f'<path d="M{kx + 20} {gy + 34} H{px - 22}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    out.append(text((kx + px) / 2, gy + 28, "the same seed: “this perishable body” (15:53)", 12.5, "middle",
                    weight="bold"))
    cy0 = sy + 34
    out.append(text(W / 2, cy0, "Jesus’ risen body shows both halves", 14, "middle", "bold"))
    c, ch = card(40, cy0 + 12, 310, ["The same body", "“See my hands and my feet…", "Touch me, and see” (Luke 24:39)",
                                      "ate broiled fish before them", "the wounds still there"],
                 "Luke 24:39-43 · John 20:27", size=13)
    out += c
    c, _ = card(370, cy0 + 12, 310, ["Changed", "not recognised on the road", "stood among them, “the doors",
                                      "being locked”"], "Luke 24:16 · John 20:19", size=13)
    out += c
    p2 = cy0 + 12 + ch + BODY_GAP
    out.append(f'<path d="M30 {p2 - 24} H{W - 30}" stroke="{MUTED}" stroke-width="0.8"/>')

    # 2. Four contrasts: what kind of body?
    out += panel_head(p2, "2 · FOUR CONTRASTS", "“With what kind of body do they come?” (1 Corinthians 15:35)")
    r0, rh = p2 + 104, 58
    out.append(f'<rect x="40" y="{p2 + 66}" width="290" height="{38 + 4 * rh}" rx="8" fill="{EARTH_TINT}" stroke="{INK}"/>')
    out.append(f'<rect x="390" y="{p2 + 66}" width="290" height="{38 + 4 * rh}" rx="8" fill="{GOLD_TINT}" stroke="{INK}"/>')
    out.append(text(185, p2 + 92, "SOWN", 15, "middle", "bold", spacing="1.5"))
    out.append(text(535, p2 + 92, "RAISED", 15, "middle", "bold", spacing="1.5", fill=GOLD_EDGE))
    rows = [
        ("perishable", "ἐν φθορᾷ · phthora, decay", "imperishable", "ἐν ἀφθαρσίᾳ · aphtharsia"),
        ("in dishonour", "ἐν ἀτιμίᾳ · atimia", "in glory", "ἐν δόξῃ · doxa"),
        ("in weakness", "ἐν ἀσθενείᾳ · astheneia", "in power", "ἐν δυνάμει · dynamis"),
        ("a natural body", "σῶμα ψυχικόν · psychikon", "a spiritual body", "σῶμα πνευματικόν · pneumatikon"),
    ]
    for i, (a, ag, b, bg) in enumerate(rows):
        y = r0 + i * rh
        gx0, gx1, gc = 72, 422, y + 18
        if i == 0:
            out.append(f'<circle cx="{gx0}" cy="{gc}" r="12" fill="{DIM}" stroke="{MUTED}" stroke-width="1.2"/>'
                       f'<path d="M{gx0 - 6} {gc - 9} l5 7 l-3 5 l6 6 M{gx0 + 7} {gc - 8} l-4 6 l4 3" fill="none" stroke="{INK}" stroke-width="1"/>')
            out.append(f'<circle cx="{gx1}" cy="{gc}" r="12" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>'
                       f'<circle cx="{gx1}" cy="{gc}" r="7" fill="none" stroke="{GOLD_EDGE}" stroke-width="1"/>')
        elif i == 1:
            out.append(star(gx0, gc, 12, "none", MUTED))
            out.append(star(gx1, gc, 12, GOLD, GOLD_EDGE, rays=True))
        elif i == 2:
            out.append(wheat(gx0, gc + 16, gc - 8, full=False, droop=12))
            out.append(f'<g transform="translate({gx1} {gc + 16}) scale(0.42) translate({-gx1} {-gc - 16})">'
                       f'{wheat(gx1, gc + 16, gc - 52)}</g>')
        else:
            out.append(breath(gx0 - 2, gc))
            out.append(flame(gx1, gc + 14))
        out.append(text(100, y + 16, a, 15, weight="bold"))
        out.append(text(100, y + 35, ag, 12.5, italic=True, fill=MUTED))
        out.append(text(450, y + 16, b, 15, weight="bold"))
        out.append(text(450, y + 35, bg, 12.5, italic=True, fill=MUTED))
        out.append(f'<path d="M336 {y + 16} H380" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
        out.append(arrow_head(384, y + 16, 0, 9, GOLD_EDGE))
    out.append(text(360, r0 - 18, "“sown … raised”", 12, "middle", italic=True, fill=MUTED))
    out.append(text(W / 2, r0 + 4 * rh + 18, "1 Corinthians 15:42-44, ESV", 12, "middle", italic=True, fill=MUTED))
    c, nh = bracket_note(40, r0 + 4 * rh + 30, 640, [
        "“Spiritual body”: a body the Holy Spirit gives life to",
        "ψυχικός (from ψυχή, life) and πνευματικός (from πνεῦμα, Spirit) both say what animates",
        "the body. It is raised flesh and bones (Luke 24:39), given life “through his Spirit",
        "who dwells in you” (Romans 8:11).",
    ], size=13)
    out += c
    p3 = r0 + 4 * rh + 30 + nh + BODY_GAP
    out.append(f'<path d="M30 {p3 - 24} H{W - 30}" stroke="{MUTED}" stroke-width="0.8"/>')

    # 3. Two Adams: whose image?
    out += panel_head(p3, "3 · TWO ADAMS", "Whose image will you bear? (1 Corinthians 15:45-49)")
    lx, rx, gb = 185, 535, p3 + 172
    out.append(text(lx, p3 + 90, "THE FIRST MAN ADAM", 14.5, "middle", "bold", spacing="1"))
    out.append(text(rx, p3 + 90, "THE LAST ADAM", 14.5, "middle", "bold", spacing="1", fill=GOLD_EDGE))
    out.append(f'<path d="M{lx - 60} {gb} Q{lx} {gb - 44} {lx + 60} {gb} Z" fill="{SOIL}" stroke="{INK}" stroke-width="1.2"/>')
    out.append("".join(f'<circle cx="{lx - 40 + (k * 17) % 80}" cy="{gb - 6 - (k * 7) % 22}" r="1.3" fill="{SOIL_DARK}"/>' for k in range(16)))
    out.append(f'<path d="M{lx - 70} {p3 + 118} q20 4 34 18 q8 10 26 10" fill="none" stroke="{MUTED}" stroke-width="1.6" '
               f'stroke-dasharray="1 4" stroke-linecap="round"/>')
    out.append(arrow_head(lx - 6, p3 + 146, 20, 8, MUTED))
    out.append(text(lx - 74, p3 + 112, "“the breath of life”", 11.5, italic=True, fill=MUTED))
    out.append(glow(rx, gb - 30, 70, "bd-tomb"))
    out.append(open_tomb(rx, gb))
    out += lines_at(lx, gb + 26, ["“from the earth, a man of dust”", "“became a living being”",
                                  "received life · Genesis 2:7"], 13, anchor="middle")
    out += lines_at(rx, gb + 26, ["“from heaven”", "“a life-giving spirit”", "raised · gives life"], 13, anchor="middle")
    out.append(text(W / 2, gb + 86, "1 Corinthians 15:45, 47", 12, "middle", italic=True, fill=MUTED))
    out += lines_at(W / 2, p3 + 116, ["first the natural,", "then the spiritual", "(15:46)"], 12, anchor="middle", italic=True)
    out.append(f'<path d="M318 {p3 + 160} H392" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(398, p3 + 160, 0, 10, GOLD_EDGE))
    iy = gb + 104
    c, _ = card(40, iy, 300, ["We have borne", "“the image of the man of dust”"], "1 Cor 15:49", size=13)
    out += c
    c, _ = card(380, iy, 300, ["We shall also bear", "“the image of the man of heaven”"], "1 Cor 15:49", size=13,
                fill=GOLD_TINT)
    out += c
    out.append(f'<path d="M344 {iy + 30} H372" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    out.append(arrow_head(376, iy + 30, 0, 9, GOLD_EDGE))
    c, _ = bracket_note(380, iy + 82, 300, ["Two early manuscripts read", "“let us also bear”"], dashed=True,
                        size=12, bold_first=False)
    out += c
    out += lines_at(40, iy + 98, ["σύμμορφος, sharing the form of:", "“conformed to the image of his Son”",
                                  "(Romans 8:29); “like his glorious", "body” (Philippians 3:21)"], 12.5, italic=True)
    out.append(text(W / 2, iy + 182, "“As in Adam all die, so also in Christ shall all be made alive” (1 Corinthians 15:22)",
                    13, "middle", italic=True))
    p4 = iy + 182 + BODY_GAP
    out.append(f'<path d="M30 {p4 - 24} H{W - 30}" stroke="{MUTED}" stroke-width="0.8"/>')

    # 4. Changed in a moment: when?
    out += panel_head(p4, "4 · CHANGED IN A MOMENT", "When? “At the last trumpet” (1 Corinthians 15:52)")
    tg = p4 + 290
    out.append(glow(W / 2, p4 + 108, 110, "bd-trump"))
    out.append(trumpet(W / 2 - 4, p4 + 104))
    out.append(text(W / 2, p4 + 146, "“the trumpet will sound”", 13, "middle", italic=True))
    out.append(f'<path d="M60 {p4 + 172} V{p4 + 164} H{W - 60} V{p4 + 172}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<path d="M{W / 2} {p4 + 152} V{p4 + 164}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(text(W / 2, p4 + 188, "in a moment (ἄτομος) · in the twinkling of an eye (ῥιπή) · one sound, one instant",
                    12.5, "middle", weight="bold"))
    out.append(f'<rect x="30" y="{tg}" width="{W - 60}" height="22" fill="{SOIL}"/>'
               f'<path d="M30 {tg} H{W - 30}" stroke="{INK}" stroke-width="1.5"/>')
    for k, x in enumerate((110, 190, 270)):
        out.append(grave(x, tg))
        out.append(f'<path d="M{x} {tg - 14} V{tg - 40}" stroke="{GOLD_EDGE}" stroke-width="1.4" stroke-dasharray="3 3"/>')
        out.append(arrow_head(x, tg - 42, -90, 7, GOLD_EDGE))
        out.append(glow(x, tg - 64, 22, f"bd-dead{k}"))
        out.append(person(x, tg - 46, 0.85))
    for k, x in enumerate((450, 530, 610)):
        out.append(glow(x, tg - 18, 24, f"bd-alive{k}"))
        out.append(person(x, tg, 0.95))
    out += lines_at(190, tg + 44, ["“the dead will be raised", "imperishable”"], 13, anchor="middle", italic=True)
    out += lines_at(530, tg + 44, ["“and we shall be changed”", "the living, with them"], 13, anchor="middle", italic=True)
    out.append(text(W / 2, tg + 80, "1 Corinthians 15:52 · 1 Thessalonians 4:16-17", 12, "middle", italic=True, fill=MUTED))
    c, ch = bracket_note(40, tg + 92, 640, [
        "Put on, as clothes (ἐνδύω)",
        "“this perishable body must put on the imperishable, and this mortal body must put on",
        "immortality” (15:53). Immortality (ἀθανασία) is God’s, who “alone has immortality”",
        "(1 Timothy 6:16), and He clothes you in it.",
    ], size=13, fill=GOLD_TINT)
    out += c
    c, dh = bracket_note(40, tg + 104 + ch, 640, [
        "When the trumpet sounds is contested",
        "This site reads it with 1 Thessalonians 4:16-17 as the rapture, before the tribulation;",
        "others take it as the trumpet of Matthew 24:31, at His return after it. The body is the same.",
    ], dashed=True, size=13)
    out += c
    p5 = tg + 104 + ch + dh + BODY_GAP
    out.append(f'<path d="M30 {p5 - 24} H{W - 30}" stroke="{MUTED}" stroke-width="0.8"/>')

    # 5. Death swallowed up: the chain of law, sin and death, broken at the cross.
    out += panel_head(p5, "5 · DEATH SWALLOWED UP", "“O death, where is your sting?” (1 Corinthians 15:55)")
    by = p5 + 124
    boxes = [(40, "THE LAW"), (280, "SIN"), (520, "DEATH")]
    for x, label in boxes:
        out.append(f'<rect x="{x}" y="{by}" width="160" height="44" rx="6" fill="{CARD}" stroke="{INK}" stroke-width="1.6"/>')
        out.append(text(x + 80, by + 28, label, 15, "middle", "bold", spacing="1.5"))
    for x0, x1, rows_ in ((200, 280, ["“the power of sin", "is the law”"]), (440, 520, ["“the sting of", "death is sin”"])):
        out.append(f'<path d="M{x0 + 4} {by + 22} H{x1 - 8}" stroke="{INK}" stroke-width="2"/>')
        out.append(arrow_head(x1 - 2, by + 22, 0, 9))
        out += lines_at((x0 + x1) / 2, by - 24, rows_, 11.5, lh=13, anchor="middle", italic=True)
    out.append(text(W / 2, by - 46, "1 Corinthians 15:56", 12, "middle", italic=True, fill=MUTED))
    # The cross takes the sin; the link from sin to death is broken there.
    cxx, cyy = 360, by + 132
    out.append(f'<path d="M{cxx} {cyy - 40} V{cyy + 30} M{cxx - 20} {cyy - 22} H{cxx + 20}" stroke="{INK}" stroke-width="6"/>')
    out.append(f'<path d="M{cxx} {by + 46} V{cyy - 44}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="3 3"/>')
    out.append(f'<path d="M472 {by + 10} L488 {by + 34} M488 {by + 10} L472 {by + 34}" stroke="{RED}" stroke-width="3"/>')
    out += lines_at(cxx + 34, cyy - 6, ["“Christ died for our sins”", "1 Corinthians 15:3"], 13, italic=True)
    out += lines_at(600, by + 70, ["swallowed up"], 13, anchor="middle", weight="bold", fill=GOLD_EDGE)
    out += lines_at(600, by + 90, ["“Death is swallowed", "up in victory”", "15:54, from Isaiah 25:8", "",
                                   "“O death, where", "is your sting?”", "15:55, from Hosea 13:14"], 12.5, lh=15, anchor="middle", italic=True)
    out += lines_at(40, by + 80, ["“The last enemy to be", "destroyed is death”", "1 Corinthians 15:26"], 12.5, lh=15, italic=True)
    vy = by + 200
    out.append(f'<rect x="60" y="{vy}" width="600" height="46" rx="8" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
    out.append(text(W / 2, vy + 20, "“thanks be to God, who gives us the victory", 14.5, "middle", italic=True))
    out.append(text(W / 2, vy + 38, "through our Lord Jesus Christ” (1 Corinthians 15:57)", 14.5, "middle", italic=True))
    ly = vy + 72
    c, _ = card(60, ly, 170, ["Stated in the text"], "", size=13)
    out += c
    c, _ = card(250, ly, 260, ["Contested, or a variant reading"], "", dashed=True, size=13)
    out += c
    out.append(text(530, ly + 19, "Quotations: ESV", 12.5, italic=True, fill=MUTED))
    h = ly + 76
    BODY_PANELS[:] = [p1, p2, p3, p4, p5, h]
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(svg_open(h, head["title"], head["desc"]) + out)


BODY_DETAILS = {
    f"changed-{slug}": (i, title, desc) for i, (slug, title, desc) in enumerate([
        ("seed", "The seed: the same body, changed",
         "Panel 1 of Sown and raised: a bare kernel sown in the soil (1 Corinthians 15:37) and a full wheat "
         "plant God gives from the same seed (15:38), with Jesus' risen body the same (Luke 24:39-43; John "
         "20:27) and changed (Luke 24:16; John 20:19)."),
        ("contrasts", "Four contrasts: sown and raised",
         "Panel 2 of Sown and raised: sown perishable, raised imperishable; in dishonour, in glory; in "
         "weakness, in power; a natural body, a spiritual body (1 Corinthians 15:42-44), each with its "
         "Greek, and a note that 'spiritual' names what animates the body (Romans 8:11; Luke 24:39)."),
        ("adams", "Two Adams: whose image you will bear",
         "Panel 3 of Sown and raised: the first man Adam, a man of dust who became a living being "
         "(Genesis 2:7), and the last Adam, from heaven, a life-giving spirit, beside an open tomb; we have "
         "borne the image of the man of dust and shall bear the image of the man of heaven (1 Corinthians "
         "15:45-49)."),
        ("moment", "Changed in a moment, at the last trumpet",
         "Panel 4 of Sown and raised: at the last trumpet, in a moment, the dead rise from their graves "
         "imperishable and the living are changed (1 Corinthians 15:52); the perishable puts on the "
         "imperishable and the mortal immortality (15:53). The timing is marked contested."),
        ("swallowed", "Death swallowed up",
         "Panel 5 of Sown and raised: the law gives sin its power and sin is death's sting (1 Corinthians "
         "15:56); Christ died for our sins (15:3) and the chain is broken there; death is swallowed up in "
         "victory (Isaiah 25:8; Hosea 13:14), and God gives us the victory through our Lord Jesus Christ "
         "(15:57)."),
    ])
}


def body_detail(name):
    i, title, desc = BODY_DETAILS[name]
    svg = sown_and_raised()
    top = BODY_PANELS[i] - 12
    bottom = BODY_PANELS[i + 1] - (30 if i < 4 else 88)
    return plate_detail(svg, (0, top, W, bottom - top), 1.0, title, desc)


def plate_detail(svg, box, scale, title, desc):
    x, y, w, h = box
    svg = re.sub(r'viewBox="0 0 \d+ \d+"', f'viewBox="{x} {y} {w} {h}" width="{w * scale:.0f}" '
                 f'height="{h * scale:.0f}"', svg, count=1)
    svg = re.sub(r'<title id="t">.*?</title>', f'<title id="t">{esc(title)}</title>', svg, count=1)
    return re.sub(r'<desc id="d">.*?</desc>', f'<desc id="d">{esc(desc)}</desc>', svg, count=1, flags=re.S)


# Details of the redrawn chart, each set beside the section of the study it pictures, so the reader
# meets the part of the picture with the words about it. A detail is the whole chart under a
# narrower viewBox, so it can never drift from the full one.
UNDERWORLD_DETAILS = {
    "larkin-underworld-with-christ": (
        (110, 150, 300, 500), 1.3, "The souls go down to Paradise, and the righteous rise with Christ",
        "Detail of the redrawn Underworld chart. From the hill of the three crosses the soul of the "
        "penitent thief (Luke 23:43) and the soul of Christ go down to Paradise, and Christ's soul "
        "returns to His body. The righteous souls Christ took out of the underworld rise from "
        "Paradise past the crosses, marked with 2 Corinthians 5:8, Philippians 1:23, 2 Corinthians "
        "12:2-4 and Revelation 2:7."),
    "larkin-underworld-resurrection": (
        (320, 14, 320, 540), 1.3, "The first fruits, then the harvest",
        "Detail of the redrawn Underworld chart. Christ rises from the tomb as the first fruits "
        "(1 Corinthians 15:20-23; Leviticus 23:10). On the right the souls of the righteous return "
        "for their bodies (1 Thessalonians 4:14), and the righteous dead rise out of the grave as "
        "the Harvest: translation and first-resurrection saints, 'the dead in Christ shall rise "
        "first' (1 Thessalonians 4:15-17; 1 Corinthians 15:51-53). Seven years later the Gleanings "
        "rise, the tribulation saints (Revelation 20:4)."),
    "larkin-underworld-gulf": (
        (100, 515, 400, 215), 1.6, "Paradise and Hell, either side of the Great Gulf",
        "Detail of the redrawn Underworld chart. Paradise, 'the abode of the souls of the righteous "
        "dead until Christ's resurrection; it is now empty' (Luke 16:22), and Hell, 'the abode of the "
        "souls of the wicked dead; still occupied' (Luke 16:23; Revelation 20:13), either side of the "
        "Great Gulf (Luke 16:19-31). A dotted line arcs over the gulf: seen and heard across, none "
        "may cross (Luke 16:23-26)."),
    "larkin-underworld-caption": (
        (285, 20, 145, 230), 1.8, "Larkin's caption for the first fruits",
        "Detail of the redrawn Underworld chart. Beside the stream of righteous souls rising with "
        "Christ as 'the first fruits', Larkin wrote Ephesians 4:8-10 (Psalm 68:18) and Revelation "
        "1:18. The Ephesians caption is boxed with a dashed line, as the one this study does not "
        "follow; in blue beside it are 1 Corinthians 15:20-23 and Leviticus 23:10."),
}


def underworld_detail(name):
    box, scale, title, desc = UNDERWORLD_DETAILS[name]
    return plate_detail(the_underworld(), box, scale, title, desc)


# ---------------------------------------------------------------------------------------------
# Why Not 4004 BC? (why-not-4004-bc.md): Ussher's chain against this site's, and the one stretch of
# Kings that both kingdoms count.

GENEALOGY_INDEX = ROOT / "docs" / "data" / "genealogy" / "index.json"

# Ussher's own figures, which no data file holds: his anchor at Amel-Marduk's accession
# (2 Kings 25:27), his fall of Jerusalem, and the temple his sum of Judah's kings reached
# (Annales Veteris Testamenti, 1650; summarised in the study's references). Everything on this
# site's side is read from chronology.json and genealogy/index.json.
EVIL_MERODACH_BC = 562
USSHER_FALL_BC = 588
USSHER_TEMPLE_BC = 1012
JUDAH_STRAIGHT_SUM = 430


def anchor_bc(anchor_id):
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    return -next(e["gregorian_year"] for e in data["anchor_table"] if e["id"] == anchor_id)


def genesis_am(marker_id):
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    return next(e["am_year"] for e in data["genesis_markers"] if e["id"] == marker_id)


def epoch(scenario):
    s = json.loads(GENEALOGY_INDEX.read_text(encoding="utf-8"))["chronology_scenarios"]["scenarios"][scenario]
    return s["anchor_exodus_bc"], s["derived_creation_bc_mt"]


def counting_back_from_babylon():
    u_exodus, u_creation = epoch("ussher_published")
    s_exodus, s_creation = epoch("a_prime")
    s_temple, s_fall = anchor_bc("anchor_01"), anchor_bc("anchor_12")
    assert s_exodus - s_temple == 480, "the site's Exodus no longer sits 480 years above its temple"
    assert u_creation - u_exodus == s_creation - s_exodus, "the two Genesis chains no longer match"
    chain = u_creation - u_exodus
    flood, abram = genesis_am("flood"), genesis_am("abram_born")

    top_bc, k, y0 = 4030, 0.26, 214

    def y(bc):
        return y0 + (top_bc - bc) * k

    ux0, ux1 = 150, 272        # Ussher's column
    sx0, sx1 = 372, 494        # this site's column
    gx0, gx1 = 596, 696        # the gap gauge: 0-50 years
    gk = (gx1 - gx0) / 50
    bottom = y(EVIL_MERODACH_BC)
    h = int(bottom) + 368

    events = [  # (label, Ussher BC, site BC, solid on the site's side?)
        ("Creation", u_creation, s_creation, False),
        ("The Flood", u_creation - flood, s_creation - flood, False),
        ("Abram born", u_creation - abram, s_creation - abram, False),
        ("The Exodus", u_exodus, s_exodus, False),
        ("Temple begun", USSHER_TEMPLE_BC, s_temple, True),
        ("Jerusalem falls", USSHER_FALL_BC, s_fall, True),
    ]
    gaps = [(lab, u - s, s) for lab, u, s, _ in events] + [("Evil-merodach", 0, EVIL_MERODACH_BC)]

    out = svg_open(
        h,
        "Counting back from Babylon",
        f"Two columns on one scale of years. Both start from the same anchor, Evil-merodach's accession "
        f"in {EVIL_MERODACH_BC} BC (2 Kings 25:27), and count upward. Ussher's column: {USSHER_FALL_BC - EVIL_MERODACH_BC} "
        f"years back to Jerusalem's fall in {USSHER_FALL_BC} BC; step 1, the kings of Judah, "
        f"{USSHER_FALL_BC - USSHER_TEMPLE_BC} years to the temple in {USSHER_TEMPLE_BC} BC; step 2, 1 Kings 6:1's "
        f"480th year, to the Exodus in {u_exodus} BC; step 3, Genesis 5 and 11, {chain:,} years to creation "
        f"in {u_creation} BC. This site's column: {s_fall - EVIL_MERODACH_BC} years to {s_fall} BC, {s_temple - s_fall} "
        f"years of kings to {s_temple} BC, 480 years to {s_exodus} BC, and the same {chain:,} years to "
        f"{s_creation} BC. Lines join each event across the columns. A gauge on the right plots the gap: "
        f"0 at the anchor, 2 at Jerusalem's fall, {USSHER_TEMPLE_BC - s_temple} at the temple, then "
        f"{u_exodus - s_exodus} unchanged to creation. Below, the {USSHER_TEMPLE_BC - s_temple} years are "
        f"taken apart: 2 at Jerusalem's fall and {(USSHER_TEMPLE_BC - USSHER_FALL_BC) - (s_temple - s_fall)} "
        f"in the kings, where Ussher allowed for some overlapping reigns and Thiele's reconstruction "
        f"for more.",
    )
    out += heading("Counting Back from Babylon",
                   "Two chains from one anchor, on one scale of years")

    out.append(text((ux0 + ux1) / 2, 132, "USSHER, 1650", 14, "middle", "bold", spacing="1.2"))
    out.append(text((sx0 + sx1) / 2, 132, "THIS SITE", 14, "middle", "bold", spacing="1.2"))
    out.append(text((ux0 + ux1) / 2, 150, "counted upward ↑", 12.5, "middle", fill=MUTED, italic=True))
    out.append(text((sx0 + sx1) / 2, 150, "counted upward ↑", 12.5, "middle", fill=MUTED, italic=True))
    out.append(text((gx0 + gx1) / 2, 132, "THE GAP", 14, "middle", "bold", spacing="1.2"))
    out.append(text((gx0 + gx1) / 2, 150, "Ussher minus", 12, "middle", fill=MUTED, italic=True))
    out.append(text((gx0 + gx1) / 2, 165, "this site, years", 12, "middle", fill=MUTED, italic=True))

    def column(x0, x1, segs, step_marks):
        o = []
        for i, (b0, b1, fill, rows) in enumerate(segs):
            ya, yb = y(b0), y(b1)
            o.append(f'<rect x="{x0}" y="{ya:.1f}" width="{x1 - x0}" height="{yb - ya:.1f}" fill="{fill}" '
                     f'stroke="{INK}" stroke-width="1.2"/>')
            if rows:
                ty = ya + 22
                for j, r in enumerate(rows):
                    o.append(text((x0 + x1) / 2, ty + j * 16, r, 12.5 if j else 13, "middle",
                                  "bold" if j == 0 else None))
            if step_marks and step_marks[i]:
                o.append(f'<circle cx="{x0}" cy="{ya + 17:.1f}" r="10" fill="{INK}"/>')
                o.append(text(x0, ya + 22, step_marks[i], 13, "middle", "bold", fill=PAPER))
        return o

    u_kings = USSHER_FALL_BC - USSHER_TEMPLE_BC
    out += column(ux0, ux1, [
        (u_creation, u_exodus, EARTH_TINT, ["GENESIS 5, 11", f"{chain:,} years", "Adam to the", "Exodus"]),
        (u_exodus, USSHER_TEMPLE_BC, GOLD_TINT, ["1 KINGS 6:1", "“480th year”", f"{u_exodus - USSHER_TEMPLE_BC} elapsed"]),
        (USSHER_TEMPLE_BC, USSHER_FALL_BC, RED_TINT, ["THE KINGS", f"{-u_kings} years", f"{JUDAH_STRAIGHT_SUM} added up,",
                                                       f"{JUDAH_STRAIGHT_SUM + u_kings} off for", "overlaps"]),
        (USSHER_FALL_BC, EVIL_MERODACH_BC, CARD, []),
    ], ["3", "2", "1", None])
    out += column(sx0, sx1, [
        (s_creation, s_exodus, EARTH_TINT, ["GENESIS 5, 11", f"{chain:,} years", "the same", "count"]),
        (s_exodus, s_temple, GOLD_TINT, ["1 KINGS 6:1", "480 years"]),
        (s_temple, s_fall, BLUE_TINT, ["THE KINGS", f"{s_temple - s_fall} years", "Thiele, fixed", "by Assyria"]),
        (s_fall, EVIL_MERODACH_BC, CARD, []),
    ], None)

    # Genesis markers drawn inside both columns: same AM, so the same distance down from creation.
    for lab, am in (("The Flood", flood), ("Abram born", abram)):
        for x0, x1, c in ((ux0, ux1, u_creation), (sx0, sx1, s_creation)):
            yy = y(c - am)
            out.append(f'<path d="M{x0} {yy:.1f} H{x1}" stroke="{INK}" stroke-width="0.8" stroke-dasharray="3 3"/>')
            out.append(text((x0 + x1) / 2, yy - 5, f"AM {am:,}", 11.5, "middle", fill=MUTED, extra=HALO))

    # Connectors across the gutter, with the event name above each and its two dates outside.
    for lab, u, s, solid in events + [("Evil-merodach", EVIL_MERODACH_BC, EVIL_MERODACH_BC, True)]:
        yu, ys = y(u), y(s)
        is_anchor = lab == "Evil-merodach"
        # Jerusalem's fall sits 7 units above the anchor, so its labels step up a line on leaders.
        lift = 16 if lab == "Jerusalem falls" else 0
        color = RED if is_anchor else INK
        out.append(f'<path d="M{ux1} {yu:.1f} L{sx0} {ys:.1f}" stroke="{color}" stroke-width="{2.4 if is_anchor else 1.2}"/>')
        name_y = max(yu, ys) + 17 if is_anchor else min(yu, ys) - 6 - lift
        out.append(text((ux1 + sx0) / 2, name_y, lab, 12.5, "middle", "bold", fill=color, extra=HALO))
        u_dash = "" if (is_anchor or lab == "Jerusalem falls") else ' stroke-dasharray="4 3"'
        s_dash = "" if (solid or is_anchor) else ' stroke-dasharray="4 3"'
        out.append(f'<path d="M{ux0 - 34} {yu - lift:.1f} L{ux0 - 14} {yu - lift:.1f} L{ux0} {yu:.1f}" fill="none" '
                   f'stroke="{color}" stroke-width="1.2"{u_dash}/>')
        out.append(f'<path d="M{sx1} {ys:.1f} L{sx1 + 14} {ys - lift:.1f} L{sx1 + 34} {ys - lift:.1f}" fill="none" '
                   f'stroke="{color}" stroke-width="1.2"{s_dash}/>')
        out.append(text(ux0 - 38, yu - lift + 4.5, f"{u} BC", 13, "end",
                        "bold" if u in (u_creation, USSHER_TEMPLE_BC) else None, fill=color, extra=HALO))
        out.append(text(sx1 + 38, ys - lift + 4.5, f"{s} BC", 13, "start",
                        "bold" if s in (s_creation, s_temple) else None, fill=color, extra=HALO))

    out.append(text((ux1 + sx0) / 2, bottom + 36, "THE ANCHOR · 2 Kings 25:27 · Babylonian sources", 12,
                    "middle", fill=RED, italic=True))

    # The gap gauge: Ussher minus this site at each event, plotted on the site's date.
    out.append(f'<rect x="{gx0}" y="{y(top_bc - 10):.1f}" width="{gx1 - gx0}" height="{bottom - y(top_bc - 10):.1f}" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="0.8"/>')
    for g in (10, 20, 30, 40):
        gx = gx0 + g * gk
        out.append(f'<path d="M{gx:.1f} {y(top_bc - 10):.1f} V{bottom:.1f}" stroke="{INK}" stroke-width="0.3"/>')
    for g in (0, 25, 50):
        out.append(text(gx0 + g * gk, bottom + 36, str(g), 11.5, "middle", fill=MUTED))
    pts = sorted(((s, gap) for _, gap, s in gaps), reverse=True)
    area = " ".join(f"L{gx0 + gap * gk:.1f} {y(s):.1f}" for s, gap in pts)
    out.append(f'<path d="M{gx0} {y(pts[0][0]):.1f} {area} L{gx0} {bottom:.1f} Z" fill="{RED_TINT}"/>')
    for (sa, ga), (sb, gb) in zip(pts, pts[1:]):
        # Where inside the kings the 44 years entered is not known, so that leg is drawn dashed.
        dash = ' stroke-dasharray="5 4"' if (sa == s_temple and sb == s_fall) else ""
        out.append(f'<path d="M{gx0 + ga * gk:.1f} {y(sa):.1f} L{gx0 + gb * gk:.1f} {y(sb):.1f}" '
                   f'stroke="{RED}" stroke-width="2.2"{dash}/>')
    for s, gap in pts:
        out.append(f'<circle cx="{gx0 + gap * gk:.1f}" cy="{y(s):.1f}" r="3.5" fill="{RED}" stroke="{PAPER}"/>')
    # Label where the gap changes: creation (45), the temple (46), the fall (2), the anchor (0).
    for s, gap, dy in ((s_creation, u_creation - s_creation, 4.5), (s_temple, USSHER_TEMPLE_BC - s_temple, 4.5),
                       (s_fall, USSHER_FALL_BC - s_fall, -8), (EVIL_MERODACH_BC, 0, 16)):
        lx = gx0 + gap * gk + (-6 if gap > 25 else 6)
        out.append(text(lx, y(s) + dy, str(gap), 13, "end" if gap > 25 else "start", "bold", fill=RED, extra=HALO))
    mid = (y(s_temple) + y(s_fall)) / 2
    out += lines_at(gx0 + 8 + 30 * gk, mid - 8, ["the gap", "enters", "here"], 12, anchor="middle",
                    italic=True, fill=RED, extra=HALO)
    out += lines_at((gx0 + gx1) / 2, y(2700), ["carried up", "unchanged"], 12, anchor="middle", italic=True,
                    fill=MUTED, extra=HALO)

    # The forty-six years taken apart, as a bridge from Ussher's temple to the site's.
    py = bottom + 76
    temple_gap = USSHER_TEMPLE_BC - s_temple
    fall_gap = USSHER_FALL_BC - s_fall
    kings_gap = temple_gap - fall_gap
    out.append(text(W / 2, py + 4, f"THE {temple_gap} YEARS AT THE TEMPLE, TAKEN APART", 15, "middle", "bold", spacing="1"))
    bx0, bk = 300, 7.0
    rows = [
        (f"Ussher: {USSHER_FALL_BC} + {-u_kings} =", USSHER_TEMPLE_BC, USSHER_TEMPLE_BC, INK, f"{USSHER_TEMPLE_BC} BC"),
        (f"Jerusalem's fall, {USSHER_FALL_BC} → {s_fall}", USSHER_TEMPLE_BC, USSHER_TEMPLE_BC - fall_gap, RED, f"−{fall_gap}"),
        (f"The kings, {-u_kings} → {s_temple - s_fall}", USSHER_TEMPLE_BC - fall_gap, s_temple, RED, f"−{kings_gap}"),
        (f"This site: {s_fall} + {s_temple - s_fall} =", s_temple, s_temple, BLUE, f"{s_temple} BC"),
    ]
    for i, (lab, a, b, color, val) in enumerate(rows):
        ry = py + 24 + i * 30
        out.append(text(bx0 - 12, ry + 15, lab, 13, "end"))
        xa = bx0 + (USSHER_TEMPLE_BC - a) * bk
        xb = bx0 + (USSHER_TEMPLE_BC - b) * bk
        if a == b:
            out.append(f'<path d="M{xa:.1f} {ry} V{ry + 22}" stroke="{color}" stroke-width="4"/>')
            out.append(text(xa + 8, ry + 16, val, 13.5, weight="bold", fill=color))
        else:
            out.append(f'<rect x="{xa:.1f}" y="{ry + 3}" width="{xb - xa:.1f}" height="16" fill="{RED_TINT}" '
                       f'stroke="{RED}" stroke-width="1.2"/>')
            out.append(text(xb + 8, ry + 16, val, 13.5, weight="bold", fill=color))
    ny = py + 24 + 4 * 30 + 6
    note, nh = bracket_note(28, ny, W - 56, [
        f"Above the temple both chains count the same numbers, so the gap is carried up: {u_exodus - s_exodus} at",
        f"the Exodus (Ussher reads the 480th year as 479 elapsed) and {u_creation - s_creation} at creation. On this",
        "site's line the six-thousandth year moves from AD 1997 to AD 2042.",
    ], bold_first=False, size=13)
    out += note
    ly = ny + nh + 14
    out.append(f'<path d="M40 {ly} H80" stroke="{INK}" stroke-width="1.4"/>')
    out.append(text(88, ly + 4.5, "fixed by an outside record", 13))
    out.append(f'<path d="M300 {ly} H340" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.append(text(348, ly + 4.5, "reached by adding Scripture's numbers", 13))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# Reign lengths in the order Kings gives them, division to Jehu's revolt. `start` and `end` are
# Thiele's reconstruction (The Mysterious Numbers of the Hebrew Kings, 3rd ed.), rounded to whole
# years BC; `counted` is the number Kings itself gives, which the chart lays end to end.
ISRAEL_REIGNS = [  # name, counted, reference, start, end
    ("Jeroboam", 22, "1 Kings 14:20", 931, 910),
    ("Nadab", 2, "1 Kings 15:25", 910, 909),
    ("Baasha", 24, "1 Kings 15:33", 909, 886),
    ("Elah", 2, "1 Kings 16:8", 886, 885),
    ("Zimri", 0, "1 Kings 16:15", 885, 885),
    ("Omri", 12, "1 Kings 16:23", 885, 874),
    ("Ahab", 22, "1 Kings 16:29", 874, 853),
    ("Ahaziah", 2, "1 Kings 22:51", 853, 852),
    ("Joram", 12, "2 Kings 3:1", 852, 841),
]
JUDAH_REIGNS = [  # name, counted, reference, start, end, counted the way Israel counted?
    ("Rehoboam", 17, "1 Kings 14:21", 931, 914, False),
    ("Abijam", 3, "1 Kings 15:2", 914, 911, False),
    ("Asa", 41, "1 Kings 15:10", 911, 870, False),
    ("Jehoshaphat", 25, "1 Kings 22:42", 873, 848, False),
    ("Jehoram", 8, "2 Kings 8:17", 848, 841, True),
    ("Ahaziah", 1, "2 Kings 8:26", 841, 841, True),
]


def one_stretch_counted_twice():
    division, qarqar, jehu = anchor_bc("anchor_03"), anchor_bc("anchor_05"), anchor_bc("anchor_06")
    israel_total = sum(r[1] for r in ISRAEL_REIGNS)
    judah_total = sum(r[1] for r in JUDAH_REIGNS)
    elapsed = division - jehu
    assert (israel_total, judah_total) == (98, 95), "the study's table says 98 and 95"
    assert ISRAEL_REIGNS[0][3] == division and ISRAEL_REIGNS[-1][4] == jehu
    israel_doubled = sum(1 for r in ISRAEL_REIGNS if r[1])
    assert israel_total - israel_doubled == elapsed
    coreg = JUDAH_REIGNS[3][3] - JUDAH_REIGNS[2][4]
    judah_doubled = sum(1 for r in JUDAH_REIGNS if r[5])
    assert judah_total - coreg - judah_doubled == elapsed

    x0, x_end = 64, 692
    left_bc, right_bc = division + 2, division - israel_total - 3
    k = (x_end - x0) / (left_bc - right_bc)

    def x(bc):
        return x0 + (left_bc - bc) * k

    h = 1070
    out = svg_open(
        h,
        "One stretch, counted twice",
        f"From the division of the kingdom in {division} BC to Jehu's revolt in {jehu} BC, when Joram of "
        f"Israel and Ahaziah of Judah were killed in one chase (2 Kings 9:24, 27). Four rows on one scale "
        f"of years. Israel's reigns as Kings numbers them, laid end to end: {israel_total} years, running "
        f"{israel_total - elapsed} years past Jehu. The same reigns on the calendar after Thiele: each "
        f"king's first year was also his predecessor's last, so each reign carries one year counted twice, "
        f"{israel_doubled} in all, and they end at {jehu} BC. Judah's reigns laid end to end: {judah_total} "
        f"years, {judah_total - elapsed} past Jehu. On the calendar: Jehoshaphat reigned {coreg} years beside "
        f"Asa, and Jehoram's and Ahaziah's first years were counted twice, and they too end at {jehu} BC. "
        f"Ahab at Qarqar in {qarqar} BC and Jehu's tribute in {jehu} BC are marked from the Assyrian "
        f"records. Below, the arithmetic: {israel_total} minus {israel_doubled} is {elapsed}; {judah_total} minus "
        f"{coreg} minus {judah_doubled} is {elapsed}; and Ahaziah's 2 plus Joram's 12 minus 2 is the "
        f"{qarqar - jehu} years between Qarqar and Jehu. A detail shows Nadab's two years falling between "
        f"Asa's second year and his third (1 Kings 15:25, 28).",
    )
    out += heading("One Stretch, Counted Twice",
                   "The division of the kingdom to Jehu's revolt, in Israel's list and Judah's")

    axis_y = 126
    out.append(f'<path d="M{x0} {axis_y} H{x_end}" stroke="{INK}" stroke-width="1"/>')
    for bc in range(930, right_bc - 1, -10):
        out.append(f'<path d="M{x(bc):.1f} {axis_y - 4} V{axis_y + 4}" stroke="{INK}" stroke-width="1"/>')
        out.append(text(x(bc), axis_y - 9, f"{bc}", 11.5, "middle", fill=MUTED))
    out.append(text(x_end, axis_y + 18, "years BC", 11.5, "end", fill=MUTED, italic=True))

    rows_top = 160
    row_h = 112
    body_bottom = rows_top + 4 * row_h

    # Marker lines run through the bar bands only, so they never cross a row's title.
    for bc, lab, sub, drop in ((division, "Kingdom divides", "1 Kings 12", 0),
                               (qarqar, "Ahab at Qarqar", "Kurkh Monolith", 34),
                               (jehu, "Jehu's revolt", "2 Kings 9:24, 27 · Black Obelisk", 0)):
        color = RED if bc != division else INK
        sw = 2 if bc == jehu else 1.2
        for i in range(4):
            by = rows_top + i * row_h + 64
            out.append(f'<path d="M{x(bc):.1f} {by - 40} V{by + 34}" stroke="{color}" stroke-width="{sw}"/>')
        out.append(f'<path d="M{x(bc):.1f} {body_bottom - 14} V{body_bottom + 2 + drop}" stroke="{color}" stroke-width="{sw}"/>')
        anchor = "start" if bc == division else "end"
        dx = 5 if bc == division else -5
        out.append(text(x(bc) + dx, body_bottom + 16 + drop, lab, 12.5, anchor, "bold", fill=color, extra=HALO))
        out.append(text(x(bc) + dx, body_bottom + 31 + drop, sub, 11.5, anchor, fill=MUTED, italic=True, extra=HALO))

    def names(spans, ny, tiers=3):
        """Names above their bars, stepping up a tier where they would touch."""
        o, last = [], [-999] * tiers
        for name, xa, xb in spans:
            cx = (xa + xb) / 2
            wlab = len(name) * 6.4
            for t in range(tiers):
                if cx - wlab / 2 > last[t] + 4:
                    break
            last[t] = cx + wlab / 2
            ty = ny - t * 14
            if t:
                o.append(f'<path d="M{cx:.1f} {ty + 3} V{ny + 4}" stroke="{MUTED}" stroke-width="0.6"/>')
            o.append(text(cx, ty, name, 11.5, "middle", extra=HALO))
        return o

    def row_title(ry, title, sub):
        return [text(x0 - 40, ry, title, 13, weight="bold", spacing="0.8"),
                text(x0 - 40, ry + 15, sub, 12, fill=MUTED, italic=True)]

    def paper_row(ry, reigns, total, fill):
        o = row_title(ry, f"{'ISRAEL' if fill == BLUE_TINT else 'JUDAH'} · {total} YEARS",
                      "as Kings numbers the reigns, laid end to end")
        by = ry + 64
        bc, spans = division, []
        for r in reigns:
            n = r[1]
            if n:
                o.append(f'<rect x="{x(bc):.1f}" y="{by}" width="{n * k:.1f}" height="22" fill="{fill}" '
                         f'stroke="{INK}" stroke-width="1"/>')
                if n >= 8:
                    o.append(text(x(bc - n / 2), by + 16, str(n), 12.5, "middle", "bold"))
            spans.append((r[0], x(bc), x(bc - max(n, 0.5))))
            bc -= n
        over = total - elapsed
        o.append(f'<rect x="{x(jehu):.1f}" y="{by - 3}" width="{over * k:.1f}" height="28" fill="{RED}" '
                 f'opacity="0.18" stroke="{RED}" stroke-dasharray="4 3"/>')
        o.append(text(x(jehu) + over * k / 2, by + 42, f"{over} past Jehu", 12, "middle", "bold", fill=RED,
                      extra=HALO))
        o += names(spans, by - 6)
        return o

    def calendar_row(ry, reigns, fill, judah):
        o = [text(x0 - 40, ry, "ON THE CALENDAR", 13, weight="bold", spacing="0.8"),
             text(x0 - 40, ry + 15, "Thiele's reconstruction, whole years", 12, fill=MUTED, italic=True)]
        by = ry + 64
        spans = []
        for i, r in enumerate(reigns):
            name, n, _, start, end = r[:5]
            if not n:
                continue
            lane = by + (12 if i % 2 else 0)
            doubled = r[5] if judah else True
            width = (start - end) * k
            if width:
                o.append(f'<rect x="{x(start):.1f}" y="{lane}" width="{width:.1f}" height="12" fill="{fill}" '
                         f'stroke="{INK}" stroke-width="1" stroke-dasharray="4 2"/>')
            if doubled:
                o.append(f'<rect x="{x(end):.1f}" y="{lane}" width="{k:.1f}" height="12" fill="{RED}"/>')
            spans.append((name, x(start), x(end) + (k if doubled else 0)))
        if judah:
            a_end, j_start = JUDAH_REIGNS[2][4], JUDAH_REIGNS[3][3]
            out_y = by - 2
            o.append(f'<rect x="{x(j_start):.1f}" y="{out_y}" width="{(j_start - a_end) * k:.1f}" height="28" '
                     f'fill="none" stroke="{RED}" stroke-width="1.6"/>')
        o += names(spans, by - 6)
        return o

    y1 = rows_top
    out += paper_row(y1, ISRAEL_REIGNS, israel_total, BLUE_TINT)
    out += calendar_row(y1 + row_h, ISRAEL_REIGNS, BLUE_TINT, False)
    out += paper_row(y1 + 2 * row_h, JUDAH_REIGNS, judah_total, GOLD_TINT)
    out += calendar_row(y1 + 3 * row_h, JUDAH_REIGNS, GOLD_TINT, True)
    for i in (1, 2, 3):
        out.append(f'<path d="M24 {y1 + i * row_h - 14} H{W - 24}" stroke="{INK}" stroke-width="0.5"/>')

    # The arithmetic.
    ty = body_bottom + 96
    out.append(text(W / 2, ty, "THE ARITHMETIC", 15, "middle", "bold", spacing="1"))
    sums = [
        ("Israel", f"{israel_total} on paper", f"− {israel_doubled} first years that were also a predecessor's last", f"= {elapsed}"),
        ("Judah", f"{judah_total} on paper", f"− {coreg} Jehoshaphat beside Asa  − {judah_doubled} years counted twice", f"= {elapsed}"),
        ("Assyria's check", "2 + 12 on paper", "Ahaziah and Joram, − 2 shared years", f"= {qarqar - jehu}"),
    ]
    for i, (who, a, b, c) in enumerate(sums):
        ry = ty + 28 + i * 26
        out.append(text(40, ry, who, 13.5, weight="bold"))
        out.append(text(166, ry, a, 13.5))
        out.append(text(282, ry, b, 13.5, fill=RED))
        out.append(text(W - 40, ry, c, 14.5, "end", "bold"))
    out.append(text(40, ty + 28 + 3 * 26, f"{division} to {jehu} BC is {elapsed} years. "
                    f"Qarqar ({qarqar}) to Jehu ({jehu}) is {qarqar - jehu}.", 12.5, fill=MUTED, italic=True))

    # Detail: Nadab's two years inside Asa's second and third.
    dy = ty + 150
    out.append(text(W / 2, dy, "DETAIL · NADAB'S “TWO YEARS”", 15, "middle", "bold", spacing="1"))
    cx0, cw = 170, 95
    for i, lab in enumerate(["Asa's 1st year", "Asa's 2nd", "Asa's 3rd", "Asa's 4th"]):
        cx = cx0 + i * cw
        out.append(f'<rect x="{cx}" y="{dy + 18}" width="{cw}" height="26" fill="{CARD}" stroke="{INK}"/>')
        out.append(text(cx + cw / 2, dy + 36, lab, 12.5, "middle"))
    lanes = [("Jeroboam", 0, 1.45, BLUE_TINT), ("Nadab", 1.45, 2.4, RED_TINT), ("Baasha", 2.4, 4, BLUE_TINT)]
    for name, a, b, fill in lanes:
        out.append(f'<rect x="{cx0 + a * cw:.1f}" y="{dy + 52}" width="{(b - a) * cw:.1f}" height="20" fill="{fill}" '
                   f'stroke="{INK}" stroke-dasharray="4 2"/>')
        out.append(text(cx0 + (a + b) / 2 * cw, dy + 66, name, 12.5, "middle", "bold" if name == "Nadab" else None))
    out.append(text(cx0 - 10, dy + 36, "Judah", 12.5, "end", fill=MUTED, italic=True))
    out.append(text(cx0 - 10, dy + 66, "Israel", 12.5, "end", fill=MUTED, italic=True))
    out += lines_at(W / 2, dy + 96, [
        "Nadab “began to reign … in the second year of Asa … and he reigned over Israel two years”",
        "(1 Kings 15:25, ESV); Baasha killed him “in the third year of Asa” (1 Kings 15:28, ESV).",
        "Two calendar years touched, two years counted. Where in each year the change fell is not stated.",
    ], 12.5, anchor="middle", italic=True)

    ly = dy + 160
    out.append(f'<rect x="40" y="{ly - 10}" width="34" height="12" fill="{BLUE_TINT}" stroke="{INK}"/>')
    out.append(text(82, ly, "the text's number", 12.5))
    out.append(f'<rect x="210" y="{ly - 10}" width="34" height="12" fill="{BLUE_TINT}" stroke="{INK}" stroke-dasharray="4 2"/>')
    out.append(text(252, ly, "placed by reconstruction", 12.5))
    out.append(f'<rect x="420" y="{ly - 10}" width="12" height="12" fill="{RED}"/>')
    out.append(text(440, ly, "a year counted twice", 12.5))
    out.append(f'<rect x="590" y="{ly - 10}" width="24" height="12" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    out.append(text(620, ly, "co-regency", 12.5))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


FEAST_OUT = ROOT / "docs" / "content" / "assets" / "img" / "feasts"
FEAST_CHARTS = {
    "weeks-within-weeks": weeks_within_weeks,
}


CHARTS = {
    "seven-thousand-years": seven_thousand_years,
    "two-stages-of-his-coming": two_stages,
    "seventy-weeks": seventy_weeks,
    "after-the-thousand-years": after_thousand,
    "taken-before-judgment": taken_before_judgment,
    "meeting-the-lord": meeting_the_lord,
    "end-of-the-ages": end_of_the_ages,
    "six-days-three-ages": six_days_three_ages,
    "eighth-day": eighth_day,
    "counting-back-from-babylon": counting_back_from_babylon,
    "one-stretch-counted-twice": one_stretch_counted_twice,
    "larkin-underworld": the_underworld,
    **{n: (lambda n=n: underworld_detail(n)) for n in UNDERWORLD_DETAILS},
    "sown-and-raised": sown_and_raised,
    **{n: (lambda n=n: body_detail(n)) for n in BODY_DETAILS},
}


def main():
    every = {**{n: (f, OUT) for n, f in CHARTS.items()}, **{n: (f, FEAST_OUT) for n, f in FEAST_CHARTS.items()}}
    for name in sys.argv[1:] or every:
        draw, out_dir = every[name]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{name}.svg").write_text(draw() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
