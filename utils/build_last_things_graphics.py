"""Draw the Larkin-style charts for the last-things/ studies other than the tribulation study.

Same hand as utils/build_tribulation_graphics.py (both draw with utils/lib/larkin.py) and the same
confidence code: a solid outline is dated or stated by the text, a dashed one is this site's
inference. Each chart follows the study it sits in; if the study changes its reading, change the
chart here and re-run from the repo root:

    python3 utils/build_last_things_graphics.py            # all six
    python3 utils/build_last_things_graphics.py seventy-weeks

seven_thousand_years() reads its dates from docs/data/chronology.json, the site's one chronology,
so the chart cannot drift from Chronology Anchors. Run it again after that file changes.
"""

import datetime
import json
import sys
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, HALO, text, svg_open, heading, banner, cloud, arrow_head,
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


CHARTS = {
    "seven-thousand-years": seven_thousand_years,
    "two-stages-of-his-coming": two_stages,
    "seventy-weeks": seventy_weeks,
    "after-the-thousand-years": after_thousand,
    "taken-before-judgment": taken_before_judgment,
    "meeting-the-lord": meeting_the_lord,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or CHARTS:
        (OUT / f"{name}.svg").write_text(CHARTS[name]() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
