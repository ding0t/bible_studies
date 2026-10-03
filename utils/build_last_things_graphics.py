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
