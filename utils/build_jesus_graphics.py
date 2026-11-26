"""Draw the Larkin-style plates for the jesus/ studies, with utils/lib/larkin.py.

Same confidence code as the last-things charts: a solid outline is what the text states, a dashed
one is inference or a span the text does not count. Run from the repo root:

    python3 utils/build_jesus_graphics.py                    # all of them
    python3 utils/build_jesus_graphics.py where-jesus-stopped-reading

where_jesus_stopped_reading() reads its "same pattern" rows from docs/data/prophecies-of-christ.toml
(each entry's `prophecy` and `split.at`), so the plate follows the ledger.
"""

import sys
import tomllib
from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, HALO, text, svg_open, heading, arrow_head, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "jesus"
LEDGER = ROOT / "docs" / "data" / "prophecies-of-christ.toml"
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
    ("veiled", "read of Him by no one, before Jesus or since", CARD, GREY, False),
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
            ". The prophecies of His line and reign were known; the prophecies of His suffering, and "
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


CHARTS = {"where-jesus-stopped-reading": where_jesus_stopped_reading,
          "known-before-seen-after": known_before_seen_after}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or CHARTS:
        (OUT / f"{name}.svg").write_text(CHARTS[name]() + "\n", encoding="utf-8")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
