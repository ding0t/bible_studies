"""Draw the Larkin-style plates for the jesus/ studies, with utils/lib/larkin.py.

Same confidence code as the last-things charts: a solid outline is what the text states, a dashed
one is inference or a span the text does not count. Run from the repo root:

    python3 utils/build_jesus_graphics.py                    # all of them
    python3 utils/build_jesus_graphics.py where-jesus-stopped-reading

prophets_view_historys_view() reads every row from the ledger and its computed years
(docs/data/prophecies-of-christ.json); re-run references/build/export_prophecies.py first.

where_jesus_stopped_reading() reads its "same pattern" rows from docs/data/prophecies-of-christ.toml
(each entry's `prophecy` and `split.at`), so the plate follows the ledger.
"""

import json
import re
import statistics
import sys
import tomllib
from pathlib import Path

from lib.larkin import (W, INK, MUTED, PAPER as PAPER_, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, HALO, text, svg_open, heading, arrow_head, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "jesus"
LEDGER = ROOT / "docs" / "data" / "prophecies-of-christ.toml"
# The years each prophecy was written and fulfilled, from references/build/export_prophecies.py.
COMPUTED = ROOT / "docs" / "data" / "prophecies-of-christ.json"
GREY = "#9a8b72"


def lines_at(x, y, lines, size=14, step=None, **kw):
    step = step or size * 1.3
    return [text(x, y + i * step, ln, size, **kw) for i, ln in enumerate(lines)]


# Isaiah 61:1-3 clause by clause (BSB), as Luke 4:18-19 has it. kind: read | out | changed | in |
# stop | after. `note` is the right-hand label; `luke` is Luke's wording where it differs.
SCROLL = [
    ("61:1", "The Spirit of the Lord GOD is on Me,", "read", "read", None),
    ("61:1", "because the LORD has anointed Me", "read", "read", None),
    ("", "to preach good news to the poor.", "read", "read", None),
    ("61:1", "He has sent Me to bind up the brokenhearted,", "out", "not in Luke 4:18’s", "earliest manuscripts"),
    ("61:1", "to proclaim liberty to the captives", "read", "read", None),
    ("61:1", "and freedom to the prisoners,", "changed", "read as the Septuagint has it:",
     "“and recovery of sight to the blind”"),
    ("58:6", "“to release the oppressed”", "in", "brought in from Isaiah 58:6",
     "(Septuagint), joined on ἄφεσις, “release”"),
    ("61:2", "to proclaim the year of the LORD’s favor", "read", "read: “Today this Scripture",
     "is fulfilled” (Luke 4:21)"),
    ("", "", "stop", "", None),
    ("61:2", "and the day of our God’s vengeance,", "after", "not read", None),
    ("61:2", "to comfort all who mourn,", "after", "not read", None),
    ("61:3", "to console the mourners in Zion…", "after", "not read", None),
]

# The ledger entries whose split the New Testament signals in its own words. Captions are the
# signal in a few words; the reference and the dividing text come from the ledger.
PATTERN = [
    ("bethlehem", "“until she who is in labor has given birth” (Micah 5:3)"),
    ("eyes-of-the-blind", "the healings, without “your God will come with vengeance”"),
    ("elijah-before-the-day", "Elijah “has already come” and “will restore”"),
    ("sit-at-my-right-hand", "seated now; “He waits for His enemies to be made a footstool” (Heb 10:13)"),
    ("blessed-is-he-who-comes", "“you will not see Me again until you say…”"),
    ("booth-of-david-rebuilt", "the nations now; David’s tent and the land after"),
    ("israel-seeks-david-their-king", "“many days without king”, then “afterward”, David their king (Hosea 3:4-5)"),
    ("all-things-under-his-feet", "crowned now; “at present we do not see everything subject to him”"),
]


def where_jesus_stopped_reading():
    ledger = {e["id"]: e for e in tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]}
    # The first reference of each, to fit the row; the ledger carries the rest.
    rows = [(ledger[i]["prophecy"].split(";")[0], ledger[i]["split"]["at"].split(";")[0], cap)
            for i, cap in PATTERN]
    h = 1450
    out = svg_open(
        h,
        "Where Jesus stopped reading",
        "Isaiah 61:1-3 set out clause by clause as Jesus read it in the synagogue at Nazareth "
        "(Luke 4:16-21). He read that the Spirit of the Lord GOD is on Me, that the LORD has anointed "
        "Me to preach good news to the poor, and to proclaim liberty to the captives. He left out 'to "
        "bind up the brokenhearted'. For 'freedom to the prisoners' He read, as the Septuagint has it, "
        "'recovery of sight to the blind', and He brought in 'to release the oppressed' from Isaiah "
        "58:6, joined on the Greek word aphesis, release; the line He left out is missing from the earliest manuscripts of Luke. He read 'to proclaim the year of the LORD's "
        "favor' and said 'Today this Scripture is fulfilled' (Luke 4:21). Then He rolled up the scroll "
        "(Luke 4:20), before 'and the day of our God's vengeance, to comfort all who mourn, to console "
        "the mourners in Zion'. Below, a line of time runs from His first coming, 'today', through the "
        "year of favor, 'now' (2 Corinthians 6:2), drawn dashed because Scripture does not count its "
        "length, to His revealing from heaven with vengeance (2 Thessalonians 1:7-8). A table lists "
        "eight other prophecies the New Testament divides between His two comings, each with the text "
        "that divides it: Micah 5:2, Isaiah 35:5-6, Malachi 4:5-6, Psalm 110:1, Psalm 118:26, Amos 9:11-12, "
        "Hosea 3:4-5 and Psalm 8:4-6.",
    )
    out += heading("Where Jesus Stopped Reading", "Isaiah 61:1-3, as Luke 4:16-21 records it")

    # --- the scroll: two rollers and the sheet between ---------------------------------------
    top, row, left, right = 150, 38, 70, 650
    sheet_h = row * len(SCROLL) + 24
    out.append(f'<rect x="{left}" y="{top}" width="{right - left}" height="{sheet_h}" fill="{CARD}" '
               f'stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
    for x in (left - 22, right):
        out.append(f'<rect x="{x}" y="{top - 14}" width="22" height="{sheet_h + 28}" rx="10" '
                   f'fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
    out.append(text(W / 2, top - 24, "THE SCROLL OF THE PROPHET ISAIAH  ·  Luke 4:17", 12.5, "middle",
                    "bold", fill=GOLD_EDGE, spacing="1.5"))

    y = top + 30
    for ref, clause, kind, note, more in SCROLL:
        if kind == "stop":
            out.append(f'<rect x="{left}" y="{y - 24}" width="{right - left}" height="30" fill="{RED_TINT}"/>')
            out.append(f'<path d="M{left} {y - 24} H{right} M{left} {y + 6} H{right}" stroke="{RED}" '
                       f'stroke-width="2.5"/>')
            out.append(text(W / 2, y - 4, "HE ROLLED UP THE SCROLL AND SAT DOWN  ·  Luke 4:20", 13.5,
                            "middle", "bold", fill=RED, spacing="1"))
            y += row
            continue
        fill = {"read": INK, "changed": INK, "in": BLUE, "out": GREY, "after": GREY}[kind]
        if kind == "in":
            out.append(f'<rect x="{left + 8}" y="{y - 19}" width="{right - left - 16}" height="{row - 4}" '
                       f'rx="4" fill="{BLUE_TINT}" stroke="{BLUE}" stroke-dasharray="5 4"/>')
            out.append(arrow_head(left + 4, y - 4, 0, 10, BLUE))
        out.append(text(left + 14, y, ref, 12, fill=MUTED, italic=True))
        out.append(text(left + 58, y, clause, 14.5, fill=fill, italic=kind == "in"))
        if kind == "out":
            w = 6.5 * len(clause)
            out.append(f'<path d="M{left + 56} {y - 5} h{w:.0f}" stroke="{RED}" stroke-width="1.3" '
                       f'stroke-dasharray="6 3"/>')
        note_fill = {"read": GOLD_EDGE, "changed": GOLD_EDGE, "in": BLUE, "out": RED, "after": GREY}[kind]
        out.append(text(right - 8, y - (6 if more else 0), note, 11.5, "end", fill=note_fill, italic=True))
        if more:
            out.append(text(right - 8, y + 8, more, 11.5, "end", fill=note_fill, italic=True))
        y += row

    # --- two comings on one line ------------------------------------------------------------
    ty = top + sheet_h + 70
    out.append(text(W / 2, ty - 18, "ONE SENTENCE, TWO COMINGS", 15, "middle", "bold", spacing="2"))
    x0, x1, ly = 120, 600, ty + 52
    out.append(f'<path d="M40 {ly} H{W - 40}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(arrow_head(W - 38, ly, 0, 11))
    out.append(f'<path d="M{x0 + 10} {ly - 12} H{x1 - 10}" stroke="{GOLD_EDGE}" stroke-width="3" '
               f'stroke-dasharray="8 6"/>')
    out.append(text(W / 2, ly - 22, "the year of the Lord’s favor: “now” (2 Corinthians 6:2)", 13.5,
                    "middle", italic=True))
    out.append(text(W / 2, ly + 26, "dashed: Scripture does not count its length", 12, "middle",
                    fill=MUTED, italic=True))
    for x, label, lines in ((x0, "HIS FIRST COMING", ["“Today this Scripture", "is fulfilled”", "Luke 4:21"]),
                            (x1, "HIS REVEALING", ["“inflicting vengeance”", "2 Thess 1:7-8",
                                                   "comfort for Zion", "Isaiah 61:2-3"])):
        out.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="1.5"/>')
        out.append(text(x, ly + 54, label, 13, "middle", "bold", spacing="1"))
        out += lines_at(x, ly + 72, lines, 12.5, anchor="middle", fill=INK)

    # --- the same pattern, from the ledger ----------------------------------------------------
    py = ly + 150
    out.append(text(W / 2, py, "THE SAME DIVISION ELSEWHERE", 15, "middle", "bold", spacing="2"))
    out.append(text(W / 2, py + 20, "Old Testament prophecies the New Testament divides between His comings",
                    12.5, "middle", fill=MUTED, italic=True))
    ry, rh = py + 50, 46
    out.append(f'<rect x="36" y="{ry - 24}" width="{W - 72}" height="{rh * len(rows) + 8}" fill="none" '
               f'stroke="{INK}"/>')
    for i, (prophecy, at, cap) in enumerate(rows):
        y = ry + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="36" y="{y - 24}" width="{W - 72}" height="{rh}" fill="{EARTH_TINT}" opacity="0.6"/>')
        out.append(text(48, y - 2, prophecy, 13.5, weight="bold"))
        out.append(text(W - 48, y - 2, "divided at " + at.split(" with ")[0].split(", which")[0], 12, "end",
                        fill=MUTED, italic=True))
        out.append(text(48, y + 15, cap, 12.5))

    cy = ry + rh * len(rows) + 46
    out.append(text(W / 2, cy, "“Behold, now is the time of favor; now is the day of salvation!”", 15,
                    "middle", italic=True))
    out.append(text(W / 2, cy + 20, "2 Corinthians 6:2 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# Recognition, in the ledger's own words, with the fill each is drawn in. Known before is the solid
# gold the larkin hand uses for what the text states; veiled is the paper the bar is drawn on.
RECOGNITION = [
    ("known-before", "read of the Messiah before Jesus", GOLD, GOLD_EDGE, False),
    ("partly", "read of Him in part", GOLD_TINT, GOLD_EDGE, False),
    ("read-after", "read of Him only in a later Jewish source", BLUE_TINT, BLUE, True),
    ("veiled", "read of Him in no Jewish source, before Jesus or since", CARD, GREY, False),
]
CATEGORY_ROWS = [("lineage", "Lineage"), ("birth", "Birth"), ("childhood", "Childhood"),
                 ("forerunner", "Forerunner"), ("nature", "Nature"), ("ministry", "Ministry"),
                 ("office", "Prophet, priest, king"), ("passion", "Passion"),
                 ("resurrection", "Resurrection"), ("redemption", "Redemption"), ("future", "Future")]
CONTROL_ROWS = [("opponents", "His opponents"), ("unwitting", "Unwitting agents"),
                ("followers", "His followers"), ("chosen", "Jesus, knowingly"),
                ("divine", "God alone"), ("unfulfilled", "Still to come")]


def known_before_seen_after():
    entries = tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]

    def counts(field, key):
        mine = [e for e in entries if e.get(field) == key]
        return [sum(1 for e in mine if e["recognition"] == r[0]) for r in RECOGNITION]

    cat = [(label, counts("category", key)) for key, label in CATEGORY_ROWS]
    ctl = [(label, counts("control", key)) for key, label in CONTROL_ROWS]
    total = len(entries)
    known = sum(1 for e in entries if e["recognition"] == "known-before")
    h = 1110
    desc = ("A chart of the " + str(total) + " Old Testament prophecies of Christ in this site's ledger, "
            "by whether anyone read each one of the Messiah before Jesus. By subject: " +
            "; ".join(f"{label}: {c[0]} of {sum(c)} known before, {c[1]} in part, {c[2]} read only "
                      f"later, {c[3]} veiled" for label, c in cat) +
            ". By who brought the fulfilment about: " +
            "; ".join(f"{label}: {c[0]} of {sum(c)} known before" for label, c in ctl) +
            ". The prophecies of His line and throne were known; the prophecies of His suffering, and "
            "every prophecy His opponents fulfilled, were not. Luke 24:45: Then He opened their minds "
            "to understand the Scriptures.")
    out = svg_open(h, "Known before, seen after", desc)
    out += heading("Known Before, Seen After", f"{total} prophecies of Christ: who read them of the Messiah, and when")

    left, bar_x, bar_w, row = 36, 230, 380, 34
    unit = bar_w / max(sum(c) for _, c in cat + ctl)

    def bars(y, rows, title, note):
        parts = [text(W / 2, y, title, 15, "middle", "bold", spacing="2"),
                 text(W / 2, y + 20, note, 12.5, "middle", fill=MUTED, italic=True)]
        y += 52
        for label, c in rows:
            parts.append(text(bar_x - 12, y + 5, label, 14, "end", "bold"))
            x = bar_x
            for n, (_, _, fill, edge, dashed) in zip(c, RECOGNITION):
                if not n:
                    continue
                w = n * unit
                dash = ' stroke-dasharray="4 3"' if dashed else ""
                parts.append(f'<rect x="{x:.1f}" y="{y - 12}" width="{w:.1f}" height="22" fill="{fill}" '
                             f'stroke="{edge}" stroke-width="1.1"{dash}/>')
                if w >= 16:
                    parts.append(text(x + w / 2, y + 4, str(n), 12, "middle", "bold",
                                      fill=INK if fill != CARD else GREY))
                x += w
            parts.append(text(x + 8, y + 4, f"{c[0]} of {sum(c)}", 12, fill=GOLD_EDGE if c[0] else RED,
                              italic=True))
            y += row
        return parts, y

    y = 118
    for i, (_, label, fill, edge, dashed) in enumerate(RECOGNITION):
        lx, ly = (left + 20, y + i // 2 * 26) if i % 2 == 0 else (W / 2 + 10, y + i // 2 * 26)
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        out.append(f'<rect x="{lx}" y="{ly - 12}" width="22" height="16" fill="{fill}" stroke="{edge}"{dash}/>')
        out.append(text(lx + 30, ly + 1, label, 12.5))
    parts, y = bars(y + 80, cat, "BY SUBJECT", "the right-hand figure counts the prophecies known before")
    out += parts
    parts, y = bars(y + 34, ctl, "BY WHO FULFILLED IT", "those who brought each fulfilment about")
    out += parts

    y += 22
    out.append(f'<path d="M{W / 2 - 150} {y} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>')
    out += lines_at(W / 2, y + 34, ["“The people of Jerusalem and their rulers did not recognize Jesus, yet",
                                    "in condemning Him they fulfilled the words of the prophets”"],
                    14, anchor="middle", italic=True)
    out.append(text(W / 2, y + 76, "Acts 13:27 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(text(W / 2, y + 110, "“Then He opened their minds to understand the Scriptures.”", 15,
                    "middle", italic=True))
    out.append(text(W / 2, y + 130, "Luke 24:45 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def year_label(y):
    return f"{-y} BC" if y < 0 else f"AD {y}"


def prophets_view_historys_view():
    """Larkin's two mountain peaks (immediately-after.md#two-mountain-peaks), drawn from the ledger.
    Above, what a prophet saw: the sufferings and the glory as two peaks lined up, one text holding
    both. Below, what history shows: every dated prophecy as a line from the year it was written to
    the year it came to pass, and the ones fulfilled in part carried on across the valley."""
    entries = {e["id"]: e for e in tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]}
    rows = json.loads(COMPUTED.read_text(encoding="utf-8"))["prophecies"]
    dated = [r for r in rows if r["fulfilled"] is not None]
    splits = [e for e in entries.values() if "split" in e]
    ahead = statistics.median(r["years_ahead_traditional"] for r in dated)
    # Only where the authorship table records a critical date of the book's own, and it is later.
    later = [r for r in dated if r["written_critical"] is not None and r["written_critical"] > r["written_traditional"]]
    # The bracket where no critical date is recorded: the book existed by then on any dating.
    bracket = [r for r in dated if r["written_critical"] is None and r["existed_by"] is not None]

    def latest(r):
        return r["written_critical"] if r in later else r["existed_by"]
    earliest = min(dated, key=lambda r: r["written_traditional"])
    partly = [r for r in dated if entries[r["id"]]["status"] == "partly"]

    left, x0, x1, far = 36, 190, 590, 668
    lo, hi = -1500, 100

    def x(year):
        return x0 + (max(year, lo) - lo) * (x1 - x0) / (hi - lo)

    bands = [(key, label, sorted((r for r in dated if entries[r["id"]]["category"] == key),
                                 key=lambda r: r["written_traditional"]))
             for key, label in CATEGORY_ROWS]
    bands = [b for b in bands if b[2]]
    step, gap = 6, 16
    chart_h = sum(len(b[2]) * step + gap for b in bands)
    top_h = 400
    h = 150 + top_h + 120 + chart_h + 190
    desc = (f"Two views of the {len(entries)} prophecies of Christ in this site's ledger. The prophet's view: "
            f"{len(splits)} of them the New Testament divides between His first coming and His coming in "
            "glory, one text holding both like two "
            "mountain peaks lined up, the valley between them hidden (1 Peter 1:11, the sufferings of "
            f"Christ and the glories to follow). History's view: the {len(dated)} prophecies tied to a "
            "dated event, each drawn from the year it was written to the year it came to pass. The median "
            f"is {ahead:,.0f} years ahead on the traditional dates; {len(later)} are in texts critical "
            f"scholarship dates later, {sum(r['years_ahead_critical'] > 0 for r in later)} of them still before the event. The earliest is "
            f"{earliest['prophecy']}. {len(partly)} were fulfilled "
            "in part, and the rest of each waits beyond the valley, at His return.")
    out = svg_open(h, "The prophet's view and history's view", desc)
    out += heading("The Prophet's View, History's View", "the prophecies of Christ, as they were seen and as they came to pass")

    # --- the prophet's view ---------------------------------------------------------------------
    y = 140
    out.append(text(W / 2, y, "THE PROPHET'S VIEW", 15, "middle", "bold", spacing="2"))
    out.append(text(W / 2, y + 20, "one text, two comings: the valley between them out of sight", 12.5,
                    "middle", fill=MUTED, italic=True))
    base = y + 190
    eye_x, near_x, far_x = 70, 330, 520
    out.append(f'<path d="M{left} {base} H{W - left}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<path d="M{far_x - 150} {base} L{far_x} {base - 140} L{far_x + 150} {base} Z" '
               f'fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
    out.append(f'<path d="M{near_x - 110} {base} L{near_x} {base - 95} L{near_x + 110} {base} Z" '
               f'fill="{RED_TINT}" stroke="{RED}" stroke-width="1.4"/>')
    out.append(f'<circle cx="{eye_x}" cy="{base - 60}" r="6" fill="{INK}"/>')
    out.append(f'<path d="M{eye_x} {base - 54} V{base}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<path d="M{eye_x + 8} {base - 62} L{far_x} {base - 142}" stroke="{MUTED}" '
               f'stroke-width="1" stroke-dasharray="4 4"/>')
    out.append(text(eye_x, base + 18, "the prophet", 12.5, "middle", italic=True))
    out.append(text(near_x, base - 40, "the sufferings", 13, "middle", "bold", fill=RED))
    out.append(text(far_x + 60, base - 70, "the glories", 13, "middle", "bold", fill=GOLD_EDGE))
    out.append(text(far_x + 60, base - 54, "to follow", 13, "middle", "bold", fill=GOLD_EDGE))
    out.append(text(W / 2, base + 42, f"{len(splits)} prophecies the New Testament divides between His two comings", 13.5,
                    "middle", "bold"))
    refs = sorted((e["prophecy"].split(";")[0] for e in splits), key=str)
    cols = 3
    per = -(-len(refs) // cols)
    for i, ref in enumerate(refs):
        cx = left + 24 + (i // per) * ((W - 2 * left - 24) / cols)
        out.append(text(cx, base + 66 + (i % per) * 16, ref, 12))

    # --- history's view -------------------------------------------------------------------------
    y = 150 + top_h + 14
    out.append(f'<path d="M{W / 2 - 150} {y - 30} H{W / 2 + 150}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(text(W / 2, y, "HISTORY'S VIEW", 15, "middle", "bold", spacing="2"))
    out.append(text(W / 2, y + 20, f"the {len(dated)} prophecies tied to a dated event: written, then fulfilled",
                    12.5, "middle", fill=MUTED, italic=True))
    y += 48
    # legend
    out.append(f'<circle cx="{left + 26}" cy="{y}" r="3.2" fill="{INK}"/>')
    out.append(text(left + 36, y + 4, "written by (the traditional date)", 12))
    out.append(f'<circle cx="{left + 240}" cy="{y}" r="3.2" fill="{PAPER_}" stroke="{BLUE}" stroke-width="1.3"/>')
    out.append(text(left + 250, y + 4, "by the latest any dating allows", 12))
    out.append(f'<path d="M{left + 420} {y} H{left + 446}" stroke="{GREY}" stroke-width="1.3" stroke-dasharray="3 3"/>')
    out.append(text(left + 454, y + 4, "still to come in part", 12))
    y += 44
    axis_top = y
    for key, label, band in bands:
        out.append(text(x0 - 12, y + len(band) * step / 2 + 4, label, 12.5, "end", "bold"))
        for r in band:
            yy = y + step / 2
            wt, ff = x(r["written_traditional"]), x(r["fulfilled"])
            out.append(f'<path d="M{wt:.1f} {yy:.1f} H{ff:.1f}" stroke="{INK}" stroke-width="1"/>')
            if entries[r["id"]]["status"] == "partly":
                out.append(f'<path d="M{ff:.1f} {yy:.1f} H{far:.1f}" stroke="{GREY}" stroke-width="1" '
                           f'stroke-dasharray="3 3"/>')
            if r in later or r in bracket:
                wc = x(latest(r))
                out.append(f'<circle cx="{wc:.1f}" cy="{yy:.1f}" r="2.2" fill="{PAPER_}" stroke="{BLUE}" stroke-width="1"/>')
            out.append(f'<circle cx="{wt:.1f}" cy="{yy:.1f}" r="2.4" fill="{INK}"/>')
            y += step
        y += gap
    axis_y = y
    out.append(f'<path d="M{x0} {axis_y} H{x1}" stroke="{INK}" stroke-width="1"/>')
    for year in (-1500, -1000, -500, 1):
        out.append(f'<path d="M{x(year):.1f} {axis_y} V{axis_y + 5}" stroke="{INK}"/>')
        out.append(text(x(year), axis_y + 19, year_label(year), 11.5, "middle"))
    # the life of Christ, and the valley beyond it
    out.append(f'<rect x="{x(-5):.1f}" y="{axis_top - 8}" width="{x(33) - x(-5):.1f}" height="{axis_y - axis_top + 8}" '
               f'fill="{RED_TINT}" opacity="0.55"/>')
    out.append(text(x(33) + 2, axis_top - 14, "His first coming", 11.5, "end", "bold", fill=RED))
    out.append(f'<path d="M{x1 + 14} {axis_top - 8} V{axis_y}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(f'<path d="M{x1 + 20} {axis_top - 8} V{axis_y}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(f'<rect x="{far - 22}" y="{axis_top - 8}" width="44" height="{axis_y - axis_top + 8}" fill="{GOLD_TINT}" '
               f'stroke="{GOLD_EDGE}" stroke-width="1"/>')
    out.append(text(far, axis_y + 19, "His return", 11.5, "middle", "bold", fill=GOLD_EDGE))
    out.append(text(far + 22, axis_y + 36, "the valley between: the church age, which no text counts", 11.5,
                    "end", italic=True, fill=MUTED))

    y = axis_y + 70
    out += lines_at(W / 2, y, [
        f"Median {ahead:,.0f} years ahead on the traditional dates. On the latest date any dating allows,",
        f"{sum(latest(r) < r['fulfilled'] for r in later + bracket)} of the {len(later + bracket)} shown still came before the event.",
        f"The earliest: {earliest['prophecy']}, written by {year_label(earliest['written_traditional'])}."],
        13, anchor="middle")
    out.append(text(W / 2, y + 70, "“the sufferings of Christ and the glories to follow”", 15, "middle", italic=True))
    out.append(text(W / 2, y + 90, "1 Peter 1:11 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


CHRONOLOGY = ROOT / "docs" / "data" / "chronology.json"


def clock(at):
    """Hours from midnight at the start of Saturday 28 March (the chronology's count) as a clock time.
    A fractional hour in the chronology orders events within the hour; it is no clock reading, so
    those show as "about" the nearest hour."""
    about = at != int(at)
    hour = int(round(at)) % 24
    suffix = "am" if hour < 12 else "pm"
    return f"{'about ' if about else ''}{hour % 12 or 12} {suffix}"


def passion_week():
    """Each prophecy fulfilled in the last week, hung on its day and hour. The days and hours are the
    chronology's (passion_sequence); which prophecy belongs to which moment is the ledger's `event`.
    The Hebrew day runs from evening to evening, so 14 Nisan holds the supper, the arrest, the trials,
    the cross and the burial."""
    entries = tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]
    seq = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))["passion_sequence"]
    events = {e["id"]: e for e in seq["events"]}
    days = [d for d in seq["days"] if 10 <= d["k"] <= 16]
    hung = {}
    for e in entries:
        if e.get("event") in events:
            hung.setdefault(e["event"], []).append(e)
    rows = []
    for d in days:
        here = sorted((events[i] for i in hung if d["start"] <= events[i]["at"] < d["end"]), key=lambda x: x["at"])
        rows.append((d, here))
    count = sum(len(v) for v in hung.values())
    on_14 = sum(len(hung[ev["id"]]) for d, here in rows if d["k"] == 14 for ev in here)

    left, x0, right = 36, 190, W - 36
    char = 6.6

    def chip_rows(refs, width):
        lines, line, used = [], [], 0
        for ref in refs:
            w = len(ref) * char + 16
            if line and used + w > width:
                lines.append(line)
                line, used = [], 0
            line.append((ref, w))
            used += w + 6
        if line:
            lines.append(line)
        return lines

    # measure first, then draw
    layout, y = [], 150
    for d, here in rows:
        top = y
        blocks = []
        y += 8
        for ev in here:
            refs = [e["prophecy"].split(";")[0] for e in hung[ev["id"]]]
            lines = chip_rows(refs, right - x0 - 10)
            blocks.append((ev, lines, y))
            y += 22 + len(lines) * 24
        if not here:
            y += 60 if d.get("sabbath") else 44
        layout.append((d, top, y, blocks))
        y += 10
    h = y + 120
    desc = (f"The {count} prophecies of Christ in this site's ledger that were fulfilled in His last week, on "
            "the day and hour the site's chronology gives each event (AD 33, the Hebrew day running from "
            f"evening to evening). {on_14} of them fall on one day, 14 Nisan, from the Last Supper on Thursday "
            "evening to the burial before sunset on Friday. " +
            "; ".join(f"{d['hebrew']}: " + ", ".join(f"{ev['label']} ({', '.join(e['prophecy'] for e in hung[ev['id']])})"
                                                    for ev in here) for d, here in rows if here))
    out = svg_open(h, "Passion Week: the prophecies, day by day", desc)
    out += heading("The Prophecies of Passion Week", "each fulfilled prophecy on its day and hour, AD 33")
    out.append(text(W / 2, 128, "the Hebrew day runs from sunset to sunset", 12.5, "middle", fill=MUTED, italic=True))
    for d, top, bottom, blocks in layout:
        key = d["k"] == 14
        out.append(f'<rect x="{left}" y="{top}" width="{W - 2 * left}" height="{bottom - top}" rx="4" '
                   f'fill="{RED_TINT if key else (EARTH_TINT if d.get("sabbath") else CARD)}" stroke="{RED if key else GREY}" '
                   f'stroke-width="{1.6 if key else 0.8}"/>')
        out.append(text(left + 12, top + 24, d["hebrew"], 15, weight="bold", fill=RED if key else INK))
        weekday = d["daylight"].split(" ")[0]
        out.append(text(left + 12, top + 42, weekday, 12.5, fill=MUTED, italic=True))
        if key:
            out.append(text(left + 12, top + 58, "from Thursday's", 12, fill=MUTED, italic=True))
            out.append(text(left + 12, top + 73, "sunset", 12, fill=MUTED, italic=True))
        if d.get("sabbath"):
            out.append(text(left + 12, top + 58, "Sabbath", 12.5, fill=MUTED, italic=True))
        if not blocks:
            out.append(text(x0, top + 26, "no prophecy in the ledger is fulfilled on this day", 12, fill=MUTED, italic=True))
        for ev, lines, by in blocks:
            out.append(text(x0, by + 12, f"{clock(ev['at'])} · {ev['label']}", 12.5, weight="bold"))
            cy = by + 20
            for line in lines:
                cx = x0
                for ref, w in line:
                    out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="19" rx="9.5" fill="{GOLD_TINT}" '
                               f'stroke="{GOLD_EDGE}" stroke-width="0.9"/>')
                    out.append(text(cx + w / 2, cy + 13.5, ref, 11.5, "middle"))
                    cx += w + 6
                cy += 24
    y = h - 100
    out.append(text(W / 2, y, f"{on_14} of the {count} fall on 14 Nisan, the day the Passover lambs were slain.", 13.5,
                    "middle", "bold"))
    out.append(text(W / 2, y + 30, "“For Christ, our Passover lamb, has been sacrificed.”", 15, "middle", italic=True))
    out.append(text(W / 2, y + 50, "1 Corinthians 5:7 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# The LORD's words said of Jesus: one row per ledger entry with yhwh_text, in canonical order of the
# Old Testament text. The phrases are the BSB's, checked against bible-text.db 2026-11-26; the entry
# id ties each row to the ledger, and the plate fails to build if an id is missing or unmarked.
YHWH_PAIRS = [
    ("first-and-last", "Isaiah 44:6", "“I am the first and I am the last”", "Revelation 1:17", "“I am the First and the Last”"),
    ("isaiah-saw-his-glory", "Isaiah 6:5", "“my eyes have seen the King, the LORD of Hosts”", "John 12:41", "“he saw Jesus’ glory and spoke about Him”"),
    ("lord-of-hosts-holy", "Isaiah 8:13", "“The LORD of Hosts is the One you shall regard as holy”", "1 Peter 3:15", "“in your hearts sanctify Christ as Lord”"),
    ("stone-of-stumbling", "Isaiah 8:14", "the LORD of Hosts “a stone of stumbling and a rock of offense”", "Romans 9:33", "the stone; “the one who believes in Him”"),
    ("voice-in-the-wilderness", "Isaiah 40:3", "“Prepare the way for the LORD”", "Mark 1:3", "“Prepare the way for the Lord”: John, before Jesus"),
    ("his-reward-is-with-him", "Isaiah 40:10", "the Lord GOD: “His reward is with Him”", "Revelation 22:12", "“My reward is with Me”"),
    ("every-knee-shall-bow", "Isaiah 45:23", "“Every knee will bow before Me”", "Philippians 2:10", "“at the name of Jesus every knee should bow”"),
    ("the-branch", "Jeremiah 23:6", "“The LORD Our Righteousness”", "1 Corinthians 1:30", "“Christ Jesus, who has become for us… our righteousness”"),
    ("call-on-the-name", "Joel 2:32", "“everyone who calls on the name of the LORD will be saved”", "Romans 10:9, 13", "“Jesus is Lord”… “the name of the Lord”"),
    ("pierced-one", "Zechariah 12:10", "the LORD: “they will look on Me, the One they have pierced”", "John 19:37", "“They will look on the One they have pierced”"),
    ("feet-on-the-mount-of-olives", "Zechariah 14:4", "the LORD: “His feet will stand on the Mount of Olives”", "Acts 1:11-12", "“This same Jesus… will come back”, from Olivet"),
    ("messenger-before", "Malachi 3:1", "“prepare the way before Me”", "Matthew 11:10", "“prepare Your way before You”"),
    ("king-of-glory", "Psalm 24:10", "“The LORD of Hosts—He is the King of Glory”", "1 Corinthians 2:8", "“they… crucified the Lord of glory”"),
    ("you-laid-the-foundation", "Psalm 102:25", "“You laid the foundations of the earth”", "Hebrews 1:10", "said “about the Son” (1:8): “O Lord, You laid…”"),
]


def wrap(s, width_chars):
    words, lines, line = s.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width_chars:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return lines + [line] if line else lines


def the_lords_words():
    entries = {e["id"]: e for e in tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]}
    marked = {i for i, e in entries.items() if e.get("yhwh_text")}
    rows = [r for r in YHWH_PAIRS if r[0] in entries]
    missing = marked - {r[0] for r in rows}
    if missing or len(rows) != len(YHWH_PAIRS) or any(r[0] not in marked for r in rows):
        raise SystemExit(f"the-lords-words: the pairs and the ledger's yhwh_text entries differ ({sorted(missing)})")
    left, mid, cw = 30, W / 2, 300
    out_rows, y = [], 168
    for _, ot_ref, ot, nt_ref, nt in rows:
        a, b = wrap(ot, 44), wrap(nt, 44)
        hgt = 26 + 16 * max(len(a), len(b))
        out_rows.append((ot_ref, a, nt_ref, b, y, hgt))
        y += hgt + 10
    h = y + 110
    desc = (f"{len(rows)} Old Testament texts that speak of the LORD (יהוה, YHWH), each set beside the New "
            "Testament text that says the same words of Jesus. " +
            "; ".join(f"{o} ({ot_ref}) is said of Jesus in {n_ref}: {n}" for _, ot_ref, o, n_ref, n in rows))
    out = svg_open(h, "The LORD's words, said of Jesus", desc)
    out += heading("The LORD’s Words, Said of Jesus", "what the prophets said of the LORD, the apostles say of Him")
    out.append(text(left + cw / 2, 146, "OF THE LORD (יהוה)", 13, "middle", "bold", fill=GOLD_EDGE, spacing="1.5"))
    out.append(text(W - left - cw / 2, 146, "OF JESUS", 13, "middle", "bold", fill=RED, spacing="1.5"))
    for ot_ref, a, nt_ref, b, ry, hgt in out_rows:
        out.append(f'<rect x="{left}" y="{ry}" width="{cw}" height="{hgt}" rx="5" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1.1"/>')
        out.append(f'<rect x="{W - left - cw}" y="{ry}" width="{cw}" height="{hgt}" rx="5" fill="{RED_TINT}" stroke="{RED}" stroke-width="1.1"/>')
        out.append(text(left + 10, ry + 17, ot_ref, 12.5, weight="bold"))
        out.append(text(W - left - cw + 10, ry + 17, nt_ref, 12.5, weight="bold"))
        out += lines_at(left + 10, ry + 34, a, 12, step=16)
        out += lines_at(W - left - cw + 10, ry + 34, b, 12, step=16)
        ay = ry + hgt / 2
        out.append(f'<path d="M{left + cw + 6} {ay} H{W - left - cw - 10}" stroke="{INK}" stroke-width="1.3"/>')
        out.append(arrow_head(W - left - cw - 4, ay, 0, 8))
    y = h - 84
    out += lines_at(W / 2, y, ["“so that you may consider and believe Me and understand that I am He”"], 14,
                    anchor="middle", italic=True)
    out.append(text(W / 2, y + 20, "Isaiah 43:10 (BSB); “so that… you will believe that I am He” (John 13:19)", 12, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# Which text each New Testament writer's wording follows, over the ledger's uses that quote words
# (`text` on each use). Writers grouped as the New Testament groups them; the order runs from the
# Gospels to Revelation.
WRITERS = [("Matthew", ("Matthew",)), ("Mark", ("Mark",)), ("Luke and Acts", ("Luke", "Acts")),
           ("John", ("John",)), ("Paul", ("Romans", "1 Corinthians", "2 Corinthians", "Galatians",
                                          "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
                                          "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus")),
           ("Hebrews", ("Hebrews",)), ("Peter", ("1 Peter", "2 Peter")), ("Revelation", ("Revelation",))]
TEXTS = [("mt", "the Hebrew, rendered afresh", RED_TINT, RED), ("both", "both, where they agree", GOLD_TINT, GOLD_EDGE),
         ("lxx", "the Septuagint's wording", BLUE_TINT, BLUE), ("neither", "neither", CARD, GREY)]


def which_text():
    entries = tomllib.loads(LEDGER.read_text(encoding="utf-8"))["prophecy"]
    counts = {name: {k: 0 for k, *_ in TEXTS} for name, _ in WRITERS}
    for e in entries:
        for u in e.get("uses", []):
            if u.get("text") in (None, "none"):
                continue
            book = re.match(r"((?:[12] )?[A-Z][a-z]+)", u["ref"])[1]
            for name, books in WRITERS:
                if book in books:
                    counts[name][u["text"]] += 1
    total = {name: sum(c.values()) for name, c in counts.items()}
    all_uses = sum(total.values())
    left, bar_x, bar_w, row = 36, 190, 420, 40
    h = 150 + 70 + row * len(WRITERS) + 150
    desc = (f"For the {all_uses} New Testament uses of the prophecies of Christ in this site's ledger that quote "
            "words, which text each writer's wording follows: the Hebrew rendered afresh, the Septuagint, both "
            "where they agree, or neither. " +
            "; ".join(f"{name}: " + ", ".join(f"{counts[name][k]} {label}" for k, label, *_ in TEXTS)
                      for name, _ in WRITERS))
    out = svg_open(h, "Which text the New Testament follows", desc)
    out += heading("Hebrew or Greek?", "which text each writer's wording follows, in the prophecies of Christ")
    y = 140
    for i, (k, label, fill, edge) in enumerate(TEXTS):
        lx = left + 30 + (i % 2) * 330
        ly = y + (i // 2) * 24
        out.append(f'<rect x="{lx}" y="{ly - 12}" width="22" height="15" fill="{fill}" stroke="{edge}"/>')
        out.append(text(lx + 30, ly, label, 12.5))
    y += 76
    for name, _ in WRITERS:
        n = total[name]
        out.append(text(bar_x - 12, y + 5, name, 14, "end", "bold"))
        x = bar_x
        for k, label, fill, edge in TEXTS:
            c = counts[name][k]
            if not c:
                continue
            w = bar_w * c / n
            out.append(f'<rect x="{x:.1f}" y="{y - 12}" width="{w:.1f}" height="22" fill="{fill}" stroke="{edge}" stroke-width="1"/>')
            if w >= 16:
                out.append(text(x + w / 2, y + 4, str(c), 12, "middle", "bold"))
            x += w
        out.append(text(bar_x + bar_w + 10, y + 4, f"{n} uses", 12, fill=MUTED, italic=True))
        y += row
    y += 30
    out += lines_at(W / 2, y, [
        "Each bar is one writer's share; the figures count uses, and the ledger's are a sample of the",
        "New Testament's quotations. Where the Greek misses the point, the apostles render the Hebrew",
        "afresh: “pierced” (John 19:37), “the potter” (Matthew 27:10), “heel” (John 13:18)."], 12.5, anchor="middle")
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


CHARTS = {"where-jesus-stopped-reading": where_jesus_stopped_reading,
          "known-before-seen-after": known_before_seen_after,
          "prophets-view-historys-view": prophets_view_historys_view,
          "passion-week": passion_week,
          "the-lords-words": the_lords_words,
          "which-text": which_text}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or CHARTS:
        (OUT / f"{name}.svg").write_text(CHARTS[name]() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
