"""Draw the graphics for docs/content/jesus/melchizedek-priesthood.md.

two-orders.svg: a relationship plate. The problem first (Levi held the priesthood and Judah the
throne, Numbers 3:10; Hebrews 7:14), then God's oath (Psalm 110:4), then the two orders side by
side, row by row, each cell in Hebrews' own words.

oath-came-later.svg: a sequence plate. Genesis 14 before the Law, with Levi in Abraham's loins
(Hebrews 7:9-10); Sinai and Aaron's sons; Psalm 110's oath after the Law (Hebrews 7:28); and Jesus
seated, a priest forever (Hebrews 6:20; 8:1; 7:24). The one span drawn is Galatians 3:17's 430
years, from God's covenant with Abraham (Genesis 15:18), which comes after the Melchizedek meeting
(Genesis 15:1); where the count starts is read two ways (Exodus 12:40), so its start is dashed. The
plate is not drawn to scale and says so. "Later than the Law" is Hebrews 7:28's phrase: the Law
still stood in David's day.

made-like.svg: a relationship plate. Which way the likeness runs: in the sanctuary column heaven is
the original and the tabernacle its copy (Hebrews 8:2, 5; 9:24); in the priest column the Son is the
original and Melchizedek is "made like" Him (Hebrews 7:3). Reading Melchizedek the way Hebrews reads
the tent is the study's reading, so it is dashed. Run from the repo root:

    python3 utils/build_melchizedek_graphics.py
"""

from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, PAPER, esc, text, svg_open, heading, banner, arrow_head, card,
                        credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "melchizedek"

STYLE = {"bold": dict(weight="bold"), "italic": dict(italic=True), "muted": dict(italic=True, fill=MUTED),
         "red": dict(weight="bold", fill=RED), "": {}}
SIZE = {"bold": 14.5, "italic": 13.5, "muted": 12.5, "red": 14.5, "": 13.5}


def rows_card(x, y, w, rows, h=None, dashed=False, stroke=INK, fill=CARD, lh=18, pad=10,
              centre=False):
    """A card of (text, style) rows, optionally of a fixed height. Returns (svg, height)."""
    h = h or pad * 2 + lh * len(rows) - 4
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="5" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="1.4"{dash}/>']
    ty = y + pad + lh * 0.72
    for s, style in rows:
        tx, anchor = (x + w / 2, "middle") if centre else (x + 10, "start")
        out.append(text(tx, ty, s, SIZE[style], anchor, **STYLE[style]))
        ty += lh
    return out, h


def down_arrow(x, y0, y1, colour=INK, dashed=False, width=1.8):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return [f'<path d="M{x} {y0} V{y1 - 6}" stroke="{colour}" stroke-width="{width}"{dash}/>',
            arrow_head(x, y1, 90, 9, colour)]


def closing_verse(y, lines, ref):
    out = [f'<path d="M{W / 2 - 150} {y - 24} H{W / 2 + 150}" stroke="{GOLD}" stroke-width="1"/>']
    for i, ln in enumerate(lines):
        out.append(text(W / 2, y + 22 * i, ln, 17, "middle", italic=True))
    out.append(text(W / 2, y + 22 * len(lines), ref, 13, "middle", fill=MUTED, italic=True))
    return out


def legend(x, y, items):
    """items: (label, dashed, stroke, fill, width)."""
    out = []
    for label, dashed, stroke, fill, w in items:
        c, _ = card(x, y, w, [label], "", dashed=dashed, stroke=stroke, fill=fill, size=13)
        out += c
        x += w + 16
    return out


# ---------------------------------------------------------------------------------------------
# 1. Two orders of priests
# ---------------------------------------------------------------------------------------------

# (question, Aaron's order, Melchizedek's order); every quoted line is the ESV of its reference.
ORDERS = [
    ("WHAT MAKES HIM A PRIEST",
     [("“a legal requirement", "italic"), ("concerning bodily descent”", "italic"),
      ("Hebrews 7:16 · Ezra 2:62", "muted")],
     [("“the power of an", "italic"), ("indestructible life”", "italic"), ("Hebrews 7:16", "muted")]),
    ("HOW HE IS INSTALLED",
     [("“made such without an oath”", "italic"), ("Hebrews 7:20", "muted")],
     [("“made a priest with an oath”", "italic"), ("Hebrews 7:21 · Psalm 110:4", "muted")]),
    ("HOW LONG HE SERVES",
     [("“many in number, because they", "italic"), ("were prevented by death”", "italic"),
      ("Hebrews 7:23", "muted")],
     [("“he holds his priesthood", "italic"), ("permanently”", "italic"), ("Hebrews 7:24", "muted")]),
    ("HIS SACRIFICE",
     [("“sacrifices daily, first for", "italic"), ("his own sins”", "italic"), ("Hebrews 7:27", "muted")],
     [("“once for all when he", "italic"), ("offered up himself”", "italic"), ("Hebrews 7:27", "muted")]),
    ("WHERE HE SERVES",
     [("“a copy and shadow of the", "italic"), ("heavenly things”", "italic"), ("Hebrews 8:5", "muted")],
     [("“the true tent that the", "italic"), ("Lord set up”", "italic"), ("Hebrews 8:2", "muted")]),
    ("THE COVENANT",
     [("“under it the people", "italic"), ("received the law”", "italic"), ("Hebrews 7:11", "muted")],
     [("“the guarantor of a", "italic"), ("better covenant”", "italic"), ("Hebrews 7:22", "muted")]),
]


def wall(x, y, h):
    """The line between Levi's altar and Judah's throne, drawn as a red brick wall."""
    out = [f'<rect x="{x}" y="{y}" width="20" height="{h}" fill="{RED_TINT}" stroke="{RED}" stroke-width="1.6"/>']
    for i, by in enumerate(range(int(y) + 12, int(y + h), 12)):
        out.append(f'<path d="M{x} {by} H{x + 20}" stroke="{RED}" stroke-width="0.8"/>')
        bx = x + (10 if i % 2 else 5)
        out.append(f'<path d="M{bx} {by - 12} V{by}" stroke="{RED}" stroke-width="0.8"/>')
    return out


def two_orders():
    LX, RX, CW = 40, 380, 300
    out = heading("Two Orders of Priests", "What makes the priest, and how long he serves (Hebrews 7)")

    # The problem: Levi's altar and Judah's throne, kept apart.
    y = 120
    levi = [("LEVI: THE ALTAR", "bold"), ("“you shall appoint Aaron and his", "italic"),
            ("sons … if any outsider comes near,", "italic"), ("he shall be put to death”", "italic"),
            ("Numbers 3:10", "muted")]
    judah = [("JUDAH: THE THRONE", "bold"), ("“our Lord was descended from", "italic"),
             ("Judah, and in connection with that", "italic"), ("tribe Moses said nothing about", "italic"),
             ("priests”  · Hebrews 7:14 · Genesis 49:10", "muted")]
    c, h = rows_card(LX, y, CW, levi)
    out += c
    c, _ = rows_card(RX, y, CW, judah, h=h)
    out += c
    out += wall(W / 2 - 10, y, h)
    y += h + 26
    out.append(text(W / 2, y, "King Uzziah of Judah entered the temple to burn incense and was struck with "
                    "leprosy (2 Chronicles 26:16-21).", 13, "middle", italic=True, fill=RED))
    y += 24
    out.append(text(W / 2, y, "“if he were on earth, he would not be a priest at all” (Hebrews 8:4, ESV)",
                    14, "middle", "bold"))
    y += 14
    out += down_arrow(W / 2, y, y + 30, GOLD_EDGE, width=2.2)
    y += 36

    oath = [("GOD’S OATH", "bold"), ("“The LORD has sworn and will not change his mind, ‘You are", "italic"),
            ("a priest forever after the order of Melchizedek’”", "italic"),
            ("Psalm 110:4 · quoted at Hebrews 5:6; 7:17, 21", "muted")]
    c, h = rows_card(LX, y, RX + CW - LX, oath, stroke=GOLD_EDGE, fill=GOLD_TINT, centre=True)
    out += c
    y += h + 44

    # The two orders, row by row.
    # The right column is said of Jesus, the priest Hebrews puts in Melchizedek's order (6:20).
    for x, title, sub in ((LX, "AARON’S SONS", "after the order of Aaron · Hebrews 7:11"),
                          (RX, "JESUS", "after the order of Melchizedek · Hebrews 6:20")):
        out.append(text(x + CW / 2, y, title, 15, "middle", "bold", spacing="2"))
        out.append(text(x + CW / 2, y + 18, sub, 12.5, "middle", italic=True, fill=MUTED))
    y += 36
    for question, aaron, melch in ORDERS:
        out += banner(W / 2, y, 250, question, size=12)
        y += 34
        h = 20 + 18 * max(len(aaron), len(melch)) - 4
        c, _ = rows_card(LX, y, CW, aaron, h=h)
        out += c
        c, _ = rows_card(RX, y, CW, melch, h=h, stroke=GOLD_EDGE, fill=GOLD_TINT)
        out += c
        y += h + 16

    y += 10
    out += legend(LX, y, [("Every cell is Hebrews’ own words (ESV)", False, INK, CARD, 290),
                          ("Jesus, after the order of Melchizedek", False, GOLD_EDGE, GOLD_TINT, 270)])
    y += 92
    out += closing_verse(y, ["“he always lives to make intercession for them”"], "Hebrews 7:25 (ESV)")
    h = y + 74
    out.append(credit(h))

    rows = "; ".join(f"{q.lower()}: Aaron's sons, {' '.join(s for s, st in a if st != 'muted')} "
                     f"({a[-1][0]}); Jesus, {' '.join(s for s, st in m if st != 'muted')} "
                     f"({m[-1][0]})" for q, a, m in ORDERS)
    desc = (
        "A chart of the two orders of priests in Hebrews 7. At the top, the problem: Levi held the "
        "altar, you shall appoint Aaron and his sons, and any outsider who comes near shall be put to "
        "death (Numbers 3:10); Judah held the throne, our Lord was descended from Judah, and Moses said "
        "nothing about priests in connection with that tribe (Hebrews 7:14; Genesis 49:10). A red wall "
        "stands between them, and King Uzziah of Judah entered the temple to burn incense and was struck "
        "with leprosy (2 Chronicles 26:16-21). If he were on earth, he would not be a priest at all "
        "(Hebrews 8:4). An arrow leads "
        "to God's oath, You are a priest forever after the order of Melchizedek (Psalm 110:4, quoted at "
        "Hebrews 5:6; 7:17, 21). Below, Aaron's sons, after the order of Aaron (Hebrews 7:11), and "
        f"Jesus, after the order of Melchizedek (Hebrews 6:20), side by side, in Hebrews' own words: {rows}. It closes on Hebrews 7:25, he always lives to "
        "make intercession for them."
    )
    return "\n".join(svg_open(h, "Two orders of priests", desc) + out + ["</svg>"]) + "\n"


# ---------------------------------------------------------------------------------------------
# 2. The oath came later
# ---------------------------------------------------------------------------------------------

# (era, station card, note card, gold) -- the note says what Hebrews draws from the station.
STATIONS = [
    ("BEFORE THE LAW",
     [("Genesis 14: Melchizedek, king of", "bold"), ("Salem and priest of God Most High,", ""),
      ("blesses Abram and receives a tenth", ""), ("“the inferior is blessed by the", "italic"),
      ("superior”", "italic"), ("Genesis 14:18-20 · Hebrews 7:1-2, 7", "muted")],
     None, False),
    ("UNDER THE LAW",
     [("Sinai: the Law is given, and", "bold"), ("Aaron and his sons are appointed", ""),
      ("“under it the people received", "italic"), ("the law”", "italic"),
      ("Exodus 28:1 · Numbers 3:10 · Hebrews 7:11", "muted")],
     [("Priests by descent, until death", "bold"), ("“many in number, because they", "italic"),
      ("were prevented by death”", "italic"), ("Hebrews 7:16, 23", "muted")], False),
    ("LATER THAN THE LAW",
     [("David’s psalm: God swears an oath", "bold"), ("“You are a priest forever after", "italic"),
      ("the order of Melchizedek”", "italic"), ("Psalm 110:1, 4", "muted")],
     [("The oath is God’s last word", "bold"), ("“the word of the oath, which came", "italic"),
      ("later than the law, appoints a Son”", "italic"), ("Hebrews 7:28", "muted")], False),
    ("FULFILLED",
     [("Jesus, risen and seated in heaven", "bold"), ("“a high priest forever after the", "italic"),
      ("order of Melchizedek”", "italic"), ("Hebrews 6:20 · 7:16 · 8:1", "muted")],
     [("One priest, who never dies", "bold"), ("“he holds his priesthood", "italic"),
      ("permanently, because he", "italic"), ("continues forever”", "italic"), ("Hebrews 7:24", "muted")],
     True),
]

LINEAGE = ["Abraham", "Isaac", "Jacob", "Levi", "Kohath", "Amram", "Aaron"]


def lineage_card(x, y, w):
    """Levi in Abraham's loins: the line from Abraham down to Aaron, Levi marked."""
    out = []
    rows_h = 20 + 18 * 8 - 4
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{rows_h}" rx="5" fill="{CARD}" stroke="{INK}" '
               f'stroke-width="1.4"/>')
    out.append(text(x + 10, y + 23, "Levi, in Abraham’s loins", 14.5, weight="bold", fill=RED))
    # The chain, in two lines, Levi in red.
    def chain(names, ty, lead=""):
        spans = [f'<tspan>{esc(lead)}</tspan>'] if lead else []
        for i, n in enumerate(names):
            sep = " › " if i else ""
            colour = RED if n == "Levi" else INK
            weight = ' font-weight="bold"' if n == "Levi" else ""
            spans.append(f'<tspan>{sep}</tspan><tspan fill="{colour}"{weight}>{esc(n)}</tspan>')
        return f'<text x="{x + 10}" y="{ty}" font-size="13.5" fill="{INK}">{"".join(spans)}</text>'
    out.append(chain(LINEAGE[:4], y + 41))
    out.append(chain(LINEAGE[4:], y + 59, "› "))
    for i, (s, st) in enumerate([("“Levi himself, who receives tithes,", "italic"),
                                 ("paid tithes through Abraham, for he", "italic"),
                                 ("was still in the loins of his ancestor”", "italic"),
                                 ("Hebrews 7:9-10 · Genesis 21:3; 25:26;", "muted"),
                                 ("29:34 · Exodus 6:16-20", "muted")]):
        out.append(text(x + 10, y + 77 + 18 * i, s, SIZE[st], **STYLE[st]))
    return out, rows_h


def oath_came_later():
    AX, CX, CW, NX, NW = 52, 80, 320, 420, 270
    out = heading("The Oath Came Later", "Genesis 14 and Psalm 110 on either side of the Law (Hebrews 7)")
    y = 130
    tops = []
    for i, (era, station, note, gold) in enumerate(STATIONS):
        out += banner(CX + CW / 2, y, 220, era, fill=GOLD_EDGE if gold else INK, size=12.5)
        y += 40
        c, h = rows_card(CX, y, CW, station, stroke=GOLD_EDGE if gold else INK,
                         fill=GOLD_TINT if gold else CARD)
        out += c
        if note:
            c, nh = rows_card(NX, y, NW, note, stroke=GOLD_EDGE if gold else INK,
                              fill=GOLD_TINT if gold else CARD)
        else:
            c, nh = lineage_card(NX, y, NW)
        out += c
        tops.append(y)
        out.append(f'<circle cx="{AX}" cy="{y + 18}" r="7" fill="{GOLD if gold else PAPER}" stroke="{INK}" '
                   f'stroke-width="2"/>')
        # What Hebrews draws from it, joined to the station.
        out.append(f'<path d="M{CX + CW + 2} {y + 18} H{NX - 2}" stroke="{INK}" stroke-width="1.2" '
                   f'stroke-dasharray="2 3"/>')
        y += max(h, nh)
        if i == 0:
            # Galatians 3:17 counts from the covenant (3:16-17), ratified in Genesis 15, "after these
            # things" (15:1). Where the count starts is read two ways (Exodus 12:40), so the span's start
            # is dashed.
            y += 22
            span_top = y
            out.append(f'<path d="M{AX - 9} {y} H{AX + 9}" stroke="{RED}" stroke-width="2"/>')
            out.append(text(CX, y + 5, "God’s covenant with Abraham (Genesis 15:18), after this meeting", 13.5,
                            weight="bold"))
            out.append(text(CX, y + 24, "“the law, which came 430 years afterward” (Galatians 3:17)", 13.5,
                            italic=True, fill=RED))
            out.append(text(CX, y + 42, "Where the count starts is read two ways: Exodus 12:40 counts 430 years in Egypt.",
                            12.5, italic=True, fill=MUTED))
            y += 62
        else:
            y += 30
    # The timeline itself: red where Paul counts the span, then ink, then open-ended.
    out.append(f'<path d="M{AX} {tops[0] + 26} V{span_top}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<path d="M{AX} {span_top} V{span_top + 30}" stroke="{RED}" stroke-width="4" stroke-dasharray="5 4"/>')
    out.append(f'<path d="M{AX} {span_top + 30} V{tops[1] + 10}" stroke="{RED}" stroke-width="4"/>')
    out.append(f'<path d="M{AX - 7} {tops[1] + 10} H{AX + 7}" stroke="{RED}" stroke-width="1.6"/>')
    out.append(f'<path d="M{AX} {tops[1] + 26} V{tops[3] + 10}" stroke="{INK}" stroke-width="2"/>')
    out += down_arrow(AX, tops[3] + 26, y + 4, GOLD_EDGE, width=2.4)
    out.append(text(AX + 14, y, "forever", 13.5, italic=True, weight="bold", fill=GOLD_EDGE))
    y += 34

    out.append(text(W / 2, y, "Not drawn to scale. The one span drawn is Galatians 3:17’s 430 years.",
                    12.5, "middle", italic=True, fill=MUTED))
    y += 22
    c, _ = card(CX, y, 200, ["The text gives the order"], "", size=13)
    out += c
    out.append(f'<path d="M{CX + 236} {y + 2} V{y + 26}" stroke="{RED}" stroke-width="3"/>')
    out.append(f'<path d="M{CX + 230} {y + 2} H{CX + 242} M{CX + 230} {y + 26} H{CX + 242}" stroke="{RED}" stroke-width="1.5"/>')
    out.append(text(CX + 250, y + 19, "A span the text counts", 13))
    y += 40
    out.append(f'<path d="M{CX + 14} {y + 2} V{y + 26}" stroke="{RED}" stroke-width="3" stroke-dasharray="5 4"/>')
    out.append(text(CX + 28, y + 19, "Where its count starts, inferred", 13))
    c, _ = card(CX + 260, y, 190, ["Fulfilled in Jesus"], "", stroke=GOLD_EDGE, fill=GOLD_TINT, size=13)
    out += c
    y += 96
    out += closing_verse(y, ["“The LORD has sworn and will not change his mind”"], "Psalm 110:4 (ESV)")
    h = y + 74
    out.append(credit(h))

    desc = (
        "A timeline of the priesthood in Hebrews 7, running down the page. Before the Law: in Genesis 14 "
        "Melchizedek, king of Salem and priest of God Most High, blesses Abram and receives a tenth, and "
        "the inferior is blessed by the superior (Genesis 14:18-20; Hebrews 7:1-2, 7). Beside it, Levi in "
        "Abraham's loins: Abraham, Isaac, Jacob, Levi, Kohath, Amram, Aaron, with Levi marked; Levi "
        "himself paid tithes through Abraham, for he was still in the loins of his ancestor (Hebrews "
        "7:9-10; Genesis 21:3; 25:26; 29:34; Exodus 6:16-20). After this meeting comes God's covenant with "
        "Abraham (Genesis 15:18), where a red span begins, dashed at its start: the law, which came 430 "
        "years afterward (Galatians 3:17). Where the count starts is read two ways, since Exodus 12:40 "
        "counts 430 years in Egypt. Under the Law: at Sinai the Law is given and Aaron and his sons are "
        "appointed, and under it the people received the law (Exodus 28:1; Numbers 3:10; Hebrews 7:11); "
        "beside it, priests by descent, until death, many in number because they were prevented by death "
        "(Hebrews 7:16, 23). Later than the Law: in David's psalm God swears an oath, You are a priest "
        "forever after the order of Melchizedek (Psalm 110:1, 4); beside it, the oath is God's last word, "
        "the word of the oath, which came later than the law, appoints a Son (Hebrews 7:28). Fulfilled: "
        "Jesus, risen and seated in heaven, a high priest forever after the order of Melchizedek (Hebrews "
        "6:20; 7:16; 8:1); beside it, one priest who never dies, he holds his priesthood permanently, because "
        "he continues forever (Hebrews 7:24). The line runs on past Him, marked forever. The plate is not "
        "drawn to scale, and the one span drawn is Galatians 3:17's 430 years. It closes on Psalm 110:4, The LORD has sworn and will not change his mind."
    )
    return "\n".join(svg_open(h, "The oath came later", desc) + out + ["</svg>"]) + "\n"


# ---------------------------------------------------------------------------------------------
# 3. Made like the Son
# ---------------------------------------------------------------------------------------------

# (left: the sanctuary, right: the priest) for each tier, then the arrow labels between tiers.
LIKENESS = [
    ([("The original: heaven itself", "bold"), ("“the true tent that the Lord", "italic"),
      ("set up, not man”", "italic"), ("Hebrews 8:2 · 9:24", "muted")],
     [("The original: the Son of God", "bold"), ("“whom he appointed the heir of", "italic"),
      ("all things, through whom also he", "italic"), ("created the world”", "italic"),
      ("Hebrews 1:2", "muted")]),
    ([("The copy: the tabernacle", "bold"), ("“a copy and shadow of the", "italic"),
      ("heavenly things”", "italic"), ("Exodus 25:40 · Hebrews 8:5 · 9:24", "muted")],
     [("Made like the Son: Melchizedek", "bold"), ("“resembling the Son of God he", "italic"),
      ("continues a priest forever”", "italic"), ("Genesis 14:18-20 · Hebrews 7:3", "muted")]),
    ([("Christ enters the original", "bold"), ("“into heaven itself, now to appear", "italic"),
      ("in the presence of God on our behalf”", "italic"), ("Hebrews 9:24", "muted")],
     [("Jesus arises in that likeness", "bold"), ("“another priest arises in the", "italic"),
      ("likeness of Melchizedek”", "italic"), ("Hebrews 7:15", "muted")]),
]
ARROWS = [
    (["“the pattern that was shown", "you on the mountain”", "Hebrews 8:5"],
     ["ἀφωμοιωμένος, “made like”", "usually read as passive", "Hebrews 7:3"]),
    (["in Christ"], ["fulfilled in Christ"]),
]


def made_like():
    LX, RX, CW = 76, 400, 290
    out = heading("Made Like the Son", "Which way the likeness runs in Hebrews")
    y = 124
    for x, title, sub in ((LX, "THE SANCTUARY", "Hebrews 8-9"), (RX, "THE PRIEST", "Hebrews 7")):
        out.append(text(x + CW / 2, y, title, 15, "middle", "bold", spacing="2"))
        out.append(text(x + CW / 2, y + 18, sub, 12.5, "middle", italic=True, fill=MUTED))
    y += 36
    tiers = []
    for i, (left, right) in enumerate(LIKENESS):
        gold = i == 0
        h = 20 + 18 * max(len(left), len(right)) - 4
        for x, rows in ((LX, left), (RX, right)):
            c, _ = rows_card(x, y, CW, rows, h=h, stroke=GOLD_EDGE if gold else INK,
                             fill=GOLD_TINT if gold else CARD)
            out += c
        tiers.append((y, h))
        y += h
        if i < len(ARROWS):
            labels = ARROWS[i]
            gap = 22 + 17 * max(len(labels[0]), len(labels[1]))
            for x, lab in ((LX, labels[0]), (RX, labels[1])):
                out += down_arrow(x + 34, y + 4, y + gap - 4, RED if i == 0 else GOLD_EDGE, width=2)
                for j, s in enumerate(lab):
                    if i:
                        out.append(text(x + 52, y + 24, s, 13.5, italic=True, weight="bold", fill=GOLD_EDGE))
                        continue
                    st = "muted" if j == len(lab) - 1 else "italic"
                    out.append(text(x + 52, y + 20 + 17 * j, s, 13, italic=True,
                                    fill=MUTED if st == "muted" else INK))
            y += gap

    # The time axis: the copy and the outline came first; the original is revealed in Christ.
    t0, t1 = tiers[1][0], tiers[2][0] + tiers[2][1]
    out.append(f'<path d="M40 {t0 + 4} V{t1 - 10}" stroke="{MUTED}" stroke-width="1.4"/>')
    out.append(arrow_head(40, t1 - 4, 90, 8, MUTED))
    mid = (t0 + t1) / 2
    out.append(f'<text x="30" y="{mid:.1f}" font-size="12.5" fill="{MUTED}" font-style="italic" '
               f'text-anchor="middle" transform="rotate(-90 30 {mid:.1f})">earlier in time, then later</text>')
    y += 24

    # The study reads Melchizedek the way Hebrews reads the tent: dashed, a reading.
    note = [("Read the same way (this study’s reading)", "bold"),
            ("Hebrews 9:24 calls the earthly holy places ἀντίτυπα, “copies of the true things”. This", ""),
            ("study reads the word as a coin struck from a die, and reads Melchizedek the same way:", ""),
            ("the Son is the die, and Genesis 14 drew the outline first, to show what kind of priest", ""),
            ("the Son would be.", "")]
    c, nh = rows_card(LX - 36, y, RX + CW - LX + 36, note, dashed=True, stroke=BLUE, fill=BLUE_TINT, lh=19)
    out += c
    y += nh + 22
    third = [("And the Son was made like us", "bold"),
             ("“he had to be made like his brothers in every respect, so that he might become", "italic"),
             ("a merciful and faithful high priest”", "italic"), ("Hebrews 2:17 · 4:15", "muted")]
    c, th = rows_card(LX - 36, y, RX + CW - LX + 36, third)
    out += c
    y += th + 24
    out += legend(LX - 36, y, [("Hebrews states it", False, INK, CARD, 170),
                               ("The original", False, GOLD_EDGE, GOLD_TINT, 130),
                               ("This study’s reading", True, BLUE, BLUE_TINT, 180)])
    y += 92
    out += closing_verse(y, ["“These are a shadow of the things to come,", "but the substance belongs to Christ.”"],
                         "Colossians 2:17 (ESV)")
    h = y + 96
    out.append(credit(h))

    desc = (
        "A chart of which way the likeness runs in Hebrews, in two columns. The sanctuary: the original "
        "is heaven itself, the true tent that the Lord set up, not man (Hebrews 8:2; 9:24); a red arrow, "
        "the pattern that was shown you on the mountain (Hebrews 8:5), leads down to the copy, the "
        "tabernacle, a copy and shadow of the heavenly things (Exodus 25:40; Hebrews 8:5; 9:24); a gold "
        "arrow, in Christ, leads to Christ entering the original, into "
        "heaven itself, now to appear in the presence of God on our behalf (Hebrews 9:24). The priest: "
        "the original is the Son of God, whom he appointed the heir of all things, through whom also he "
        "created the world (Hebrews 1:2); a red arrow, aphomoiomenos, made like, usually read as passive (Hebrews 7:3), "
        "leads down to Melchizedek, made like the Son, resembling the Son of God he continues a priest forever "
        "(Genesis 14:18-20; Hebrews 7:3); a gold arrow, fulfilled in Christ, leads to "
        "Jesus arising in that likeness, another priest arises in the likeness of Melchizedek (Hebrews "
        "7:15). A side arrow marks the copy and the outline as earlier in time. A dashed note gives this "
        "study's reading: Hebrews 9:24 calls the earthly holy places antitypa, copies of the true things; "
        "this study reads the word as a coin struck from a die, and reads Melchizedek the same way, the "
        "Son the die and Genesis 14 the outline drawn first, to show what kind of priest the Son would be. Below, the Son was "
        "made like us: he had to be made like his brothers in every respect, so that he might become a "
        "merciful and faithful high priest (Hebrews 2:17; 4:15). It closes on Colossians 2:17, these are "
        "a shadow of the things to come, but the substance belongs to Christ."
    )
    return "\n".join(svg_open(h, "Made like the Son", desc) + out + ["</svg>"]) + "\n"


PLATES = {
    "two-orders": two_orders,
    "oath-came-later": oath_came_later,
    "made-like": made_like,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, draw in PLATES.items():
        path = OUT / f"{name}.svg"
        path.write_text(draw(), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
