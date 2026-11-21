"""Draw the graphics for docs/content/israel-and-church/.

promised-messiah.svg, for hebrew-roots.md: a relationship graphic. Across the top, the line the
promises travel (the patriarchs, Israel's Scriptures, the Messiah, the nations, Romans 9:4-5;
15:8-9). Below, each promise Israel's Scriptures make about the Messiah beside the New Testament
text that names Jesus as its fulfilment, grouped by His line, birth, ministry, suffering and glory,
and what awaits His return. Solid is stated by the New Testament; dashed is a timing the church
reads differently, with both readings on the plate.

For bride-of-christ.md: bride-through-scripture.svg (the Husband and the Bride lane by lane, Israel's
line kept apart from the church's), wedding-pattern.svg (the eight components, four done in the
aorist), bride-and-the-ages.svg (where 6, 7 and 8 fall, with the age between 7 and 8) and
type-stands-on.svg (Scripture, documented custom, and the details with no ancient source). Run from
the repo root:

    python3 utils/build_israel_church_graphics.py
"""

from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, RED, RED_TINT, GOLD, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, EARTH_TINT, text, svg_open, heading, banner, cloud, arrow_head,
                        card, legend_row, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "israel-and-church"

LEFT_X, RIGHT_X, CARD_W = 36, 384, 300
ROW = 52

# (group, [(promise, its reference, fulfilment, its reference, contested)])
PROMISES = [
    ("HIS LINE", [
        ("Offspring of Abraham", "Genesis 22:18", "“your offspring,” who is Christ",
         "Galatians 3:16 · Matthew 1:1", False),
        ("From the tribe of Judah", "Genesis 49:10", "“our Lord was descended from Judah”",
         "Hebrews 7:14", False),
        ("A son of David on his throne", "2 Samuel 7:12-13", "“descended from David”",
         "Romans 1:3 · Acts 2:30", False),
    ]),
    ("HIS BIRTH", [
        ("“The virgin shall conceive”", "Isaiah 7:14", "Born of Mary, “to fulfill” it",
         "Matthew 1:22-23", False),
        ("A ruler out of Bethlehem", "Micah 5:2", "Born “in Bethlehem of Judea”",
         "Matthew 2:5-6", False),
    ]),
    ("HIS MINISTRY", [
        ("A messenger prepares the way", "Malachi 3:1 · Isaiah 40:3", "John the Baptist",
         "Mark 1:2-4", False),
        ("A prophet like Moses", "Deuteronomy 18:15", "Peter names Jesus as that prophet",
         "Acts 3:20-22", False),
        ("Your king comes on a donkey", "Zechariah 9:9", "He rides into Jerusalem",
         "Matthew 21:4-5", False),
    ]),
    ("HIS SUFFERING AND GLORY", [
        ("Led like a lamb to the slaughter", "Isaiah 53:7-8", "“the good news about Jesus”",
         "Acts 8:32-35 · Acts 3:18", False),
        ("Not abandoned to the grave", "Psalm 16:10", "“This Jesus God raised up”",
         "Acts 2:31-32", False),
        ("“Sit at my right hand”", "Psalm 110:1", "“both Lord and Christ”",
         "Acts 2:34-36", False),
    ]),
    ("AT HIS RETURN", [
        ("His feet on the Mount of Olives", "Zechariah 14:4", "“will come in the same way”",
         "Acts 1:11-12", False),
        ("David’s throne, for ever", "2 Samuel 7:16 · Isaiah 9:7",
         "“will reign over the house of Jacob”", "Luke 1:32-33", True),
        ("The kingdom restored to Israel", "Amos 9:11 · Jeremiah 23:5-6",
         "“restoring all the things”", "Acts 1:6-7 · Acts 3:21", True),
    ]),
]


def lineage_strip(y):
    """The line the promises travel along, left to right."""
    boxes = [
        ("THE PATRIARCHS", "Abraham, Isaac, Jacob", "Romans 9:5", CARD, INK),
        ("ISRAEL", "the Law, the Prophets,", "the Psalms · Luke 24:44", CARD, INK),
        ("JESUS THE MESSIAH", "“We have found", "the Messiah” · John 1:41", GOLD_TINT, GOLD_EDGE),
        ("THE NATIONS", "“that the Gentiles might", "glorify God” · Romans 15:9", BLUE_TINT, BLUE),
    ]
    w, gap = 150, 22
    x0 = (W - (4 * w + 3 * gap)) / 2
    out = []
    for i, (title, l1, l2, fill, stroke) in enumerate(boxes):
        x = x0 + i * (w + gap)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w}" height="74" rx="5" fill="{fill}" '
                   f'stroke="{stroke}" stroke-width="{2.2 if i == 2 else 1.4}"/>')
        out.append(text(x + w / 2, y + 22, title, 11.5, "middle", "bold", fill=stroke if i else INK))
        out.append(text(x + w / 2, y + 42, l1, 12, "middle"))
        out.append(text(x + w / 2, y + 59, l2, 11.5, "middle", italic=True, fill=MUTED))
        if i < 3:
            ax = x + w + 2
            out.append(f'<path d="M{ax:.1f} {y + 37} H{ax + gap - 6:.1f}" stroke="{INK}" stroke-width="1.6"/>')
            out.append(arrow_head(ax + gap - 3, y + 37, 0, 8))
    out.append(text(W / 2, y + 102, "“Christ became a servant to the circumcised … to confirm the "
                    "promises given to the patriarchs”", 13, "middle", italic=True))
    out.append(text(W / 2, y + 120, "Romans 15:8 (ESV)", 12, "middle", fill=MUTED, italic=True))
    return out


def promise_row(y, promise, p_ref, fulfil, f_ref, contested, future):
    stroke = BLUE if future else INK
    c, h = card(LEFT_X, y, CARD_W, [promise], p_ref, size=14)
    out = c
    c, _ = card(RIGHT_X, y, CARD_W, [fulfil], f_ref, dashed=contested, stroke=stroke,
                fill=BLUE_TINT if future else CARD, size=14)
    out += c
    mid = y + h / 2
    colour = BLUE if future else RED
    dash = ' stroke-dasharray="5 4"' if contested else ""
    out.append(f'<path d="M{LEFT_X + CARD_W + 4} {mid} H{RIGHT_X - 8}" stroke="{colour}" '
               f'stroke-width="2"{dash}/>')
    out.append(arrow_head(RIGHT_X - 3, mid, 0, 9, colour))
    return out


def promised_messiah():
    h = 1560
    out = heading("The Promised Messiah", "Israel’s Scriptures promised Him; the New Testament names Him")
    out += lineage_strip(120)

    y = 290
    out.append(text(LEFT_X + CARD_W / 2, y, "PROMISED", 15, "middle", "bold", spacing="2"))
    out.append(text(LEFT_X + CARD_W / 2, y + 18, "in Israel’s Scriptures", 13, "middle",
                    italic=True, fill=MUTED))
    out.append(text(RIGHT_X + CARD_W / 2, y, "FULFILLED IN JESUS", 15, "middle", "bold",
                    spacing="2"))
    out.append(text(RIGHT_X + CARD_W / 2, y + 18, "as the New Testament records it", 13, "middle",
                    italic=True, fill=MUTED))

    y += 40
    for group, rows in PROMISES:
        future = group == "AT HIS RETURN"
        out += banner(W / 2, y, 300, group, fill=BLUE if future else INK)
        y += 40
        for row in rows:
            out += promise_row(y, *row, future)
            y += ROW
        y += 6

    # Both readings of the contested timing, beside the rows they qualify.
    note = [
        ("Contested timing (dashed).", True),
        ("This site reads the throne of David and Israel’s restoration as still to come at His", False),
        ("return: Jesus answered the apostles’ question about it with the Father’s timing", False),
        ("(Acts 1:6-7), and heaven receives Him “until the time for restoring” (Acts 3:21).", False),
        ("Many others read Acts 2:30-36 as the throne already taken at His ascension.", False),
    ]
    nh = 14 + 18 * len(note)
    out.append(f'<rect x="{LEFT_X}" y="{y}" width="{RIGHT_X + CARD_W - LEFT_X}" height="{nh}" rx="5" '
               f'fill="{CARD}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    for i, (ln, bold) in enumerate(note):
        out.append(text(LEFT_X + 12, y + 24 + 18 * i, ln, 13, weight="bold" if bold else None,
                        fill=BLUE if bold else INK))
    y += nh + 24

    # Legend.
    c, _ = card(LEFT_X, y, 210, ["The New Testament states it"], "", size=13)
    out += c
    c, _ = card(LEFT_X + 222, y, 190, ["Timing read two ways"], "", dashed=True, stroke=BLUE,
                fill=BLUE_TINT, size=13)
    out += c
    out.append(f'<path d="M{LEFT_X + 432} {y + 14} H{LEFT_X + 466}" stroke="{RED}" stroke-width="2"/>')
    out.append(arrow_head(LEFT_X + 470, y + 14, 0, 9, RED))
    out.append(text(LEFT_X + 478, y + 19, "fulfilled", 13))
    out.append(f'<path d="M{LEFT_X + 548} {y + 14} H{LEFT_X + 582}" stroke="{BLUE}" stroke-width="2"/>')
    out.append(arrow_head(LEFT_X + 586, y + 14, 0, 9, BLUE))
    out.append(text(LEFT_X + 594, y + 19, "to come", 13))
    y += 66

    out.append(f'<path d="M{W / 2 - 150} {y - 18} H{W / 2 + 150}" stroke="{GOLD}" stroke-width="1"/>')
    out.append(text(W / 2, y + 6, "“For all the promises of God find their Yes in him.”", 17,
                    "middle", italic=True))
    out.append(text(W / 2, y + 28, "2 Corinthians 1:20 (ESV)", 13, "middle", fill=MUTED,
                    italic=True))
    out.append(credit(h))

    rows = "; ".join(f"{p} ({pr}), fulfilled: {f} ({fr})" + (", timing contested" if c3 else "")
                     for _, rs in PROMISES for p, pr, f, fr, c3 in rs)
    desc = (
        "A chart of Jesus as the Messiah Israel's Scriptures promised. Across the top, the line the "
        "promises travel: the patriarchs (Romans 9:5), then Israel with the Law, the Prophets and the "
        "Psalms (Luke 24:44), then Jesus the Messiah (John 1:41), then the nations (Romans 15:9), "
        "under Romans 15:8, Christ became a servant to the circumcised to confirm the promises given "
        "to the patriarchs. Below, each promise beside the New Testament text that names its "
        f"fulfilment, grouped as His line, His birth, His ministry, His suffering and glory, and at "
        f"His return: {rows}. A dashed note marks the contested timing: this site reads David's "
        "throne and Israel's restoration as still to come at His return (Acts 1:6-7; 3:21), while "
        "many read Acts 2:30-36 as the throne already taken at His ascension. It closes on 2 "
        "Corinthians 1:20, all the promises of God find their Yes in him."
    )
    return "\n".join(svg_open(h, "The promised Messiah", desc) + out + ["</svg>"]) + "\n"


# ---------------------------------------------------------------------------------------------
# The bride of Christ (bride-of-christ.md): four plates.
# ---------------------------------------------------------------------------------------------

def lines_card(x, y, w, rows, dashed=False, stroke=INK, fill=CARD, lh=18, pad=10):
    """A card of (text, size, style) rows; style is 'bold', 'italic', 'muted', 'red' or ''."""
    h = pad * 2 + lh * len(rows) - 4
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="5" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="1.4"{dash}/>']
    ty = y + pad + lh * 0.72
    for s, size, style in rows:
        out.append(text(x + 10, ty, s, size,
                        weight="bold" if style in ("bold", "red") else None,
                        italic=style in ("italic", "muted"),
                        fill=MUTED if style == "muted" else RED if style == "red" else INK))
        ty += lh
    return out, h


def closing_verse(y, line, ref):
    return [f'<path d="M{W / 2 - 150} {y - 22} H{W / 2 + 150}" stroke="{GOLD}" stroke-width="1"/>',
            text(W / 2, y, line, 17, "middle", italic=True),
            text(W / 2, y + 22, ref, 13, "middle", fill=MUTED, italic=True)]


# (era, husband rows, bride rows or None, bride continues from the row above)
BRIDE_THREAD = [
    ("THE PROPHETS",
     [("The LORD, your Maker", 15, "bold"), ("“your Maker is your husband”", 13.5, "italic"),
      ("Isaiah 54:5 · Jeremiah 31:32", 12.5, "muted")],
     [("Israel, betrothed to Him", 15, "bold"), ("“I will betroth you to me forever”", 13.5, "italic"),
      ("Hosea 2:19-20 · Jeremiah 2:2 · Ezekiel 16:8", 12.5, "muted")], False),
    ("THE GOSPELS",
     [("Jesus, the bridegroom", 15, "bold"), ("“The one who has the bride", 13.5, "italic"),
      ("is the bridegroom”", 13.5, "italic"),
      ("John 3:29 · Matthew 9:15 · Matthew 25:1", 12.5, "muted")],
     [("A place promised", 15, "bold"), ("“I will come again and will", 13.5, "italic"),
      ("take you to myself”", 13.5, "italic"), ("John 14:2-3", 12.5, "muted")], False),
    ("THE EPISTLES",
     [("Christ, who gave Himself", 15, "bold"), ("“Christ loved the church and", 13.5, "italic"),
      ("gave himself up for her”", 13.5, "italic"), ("Ephesians 5:25", 12.5, "muted")],
     [("The church, betrothed", 15, "bold"), ("“I betrothed you to one husband”", 13.5, "italic"),
      ("2 Corinthians 11:2", 12.5, "muted"), ("Ephesians 5:31-32", 12.5, "muted")], True),
    ("REVELATION",
     [("The Lamb", 15, "bold"), ("“the marriage of the Lamb", 13.5, "italic"),
      ("has come”", 13.5, "italic"), ("Revelation 19:7", 12.5, "muted")],
     [("The Bride, the wife of the Lamb", 15, "bold"),
      ("“his Bride has made herself ready”", 13.5, "italic"),
      ("Revelation 19:7-8 · 21:2, 9", 12.5, "muted")], True),
]


def bride_through_scripture():
    LX, RX, LW = 40, 390, 290
    out = heading("The Bride Through Scripture",
                  "The Husband God called Himself, and the Bridegroom who took the title")
    y = 128
    out.append(text(LX + LW / 2, y, "THE HUSBAND", 15, "middle", "bold", spacing="2"))
    out.append(text(RX + LW / 2, y, "THE BRIDE", 15, "middle", "bold", spacing="2"))
    y += 24
    prev_bottom = None
    for i, (era, husband, bride, continues) in enumerate(BRIDE_THREAD):
        out += banner(W / 2, y, 150, era, size=12.5)
        top = y + 40
        if prev_bottom is not None:
            # The husband lane runs unbroken; the first step is the title passing to Jesus.
            colour = RED if i == 1 else INK
            out.append(f'<path d="M{LX + 26} {prev_bottom + 4} V{top - 10}" stroke="{colour}" '
                       f'stroke-width="{2.4 if i == 1 else 1.6}"/>')
            out.append(arrow_head(LX + 26, top - 4, 90, 9, colour))
            if i == 1:
                out.append(text(LX + 36, prev_bottom + 24, "the title", 12.5, fill=RED,
                                italic=True))
                out.append(text(LX + 36, prev_bottom + 39, "passes to Jesus", 12.5, fill=RED,
                                italic=True))
            if continues:
                out.append(f'<path d="M{RX + LW - 26} {prev_bottom + 4} V{top - 10}" stroke="{INK}" '
                           f'stroke-width="1.6"/>')
                out.append(arrow_head(RX + LW - 26, top - 4, 90, 9))
        c, hh = lines_card(LX, top, LW, husband, fill=GOLD_TINT if i else CARD,
                           stroke=GOLD_EDGE if i else INK)
        out += c
        c, hb = lines_card(RX, top, LW, bride, fill=BLUE_TINT if i == 0 else CARD,
                           stroke=BLUE if i == 0 else INK)
        out += c
        # Husband and bride joined: a gold bond across the gutter.
        mid = top + min(hh, hb) / 2
        out.append(f'<path d="M{LX + LW + 2} {mid} H{RX - 2}" stroke="{GOLD_EDGE}" stroke-width="2"/>')
        out.append(f'<circle cx="{W / 2 - 7}" cy="{mid}" r="7" fill="none" stroke="{GOLD_EDGE}" stroke-width="2"/>')
        out.append(f'<circle cx="{W / 2 + 7}" cy="{mid}" r="7" fill="none" stroke="{GOLD_EDGE}" stroke-width="2"/>')
        prev_bottom = top + max(hh, hb)
        y = prev_bottom + 26

    # Israel's line does not run into the church's: two peoples, one Husband. A reading, so dashed.
    y += 6
    note = [
        ("One Husband, two covenanted peoples (this site’s reading).", 13.5, "bold"),
        ("Israel’s betrothal is not cancelled: “I will betroth you to me forever” is", 13, ""),
        ("still future when Hosea writes it (Hosea 2:19). Israel remains the wife of", 13, ""),
        ("the LORD; the church is the bride of Christ, betrothed in this present age;", 13, ""),
        ("and the Son is the LORD who married Israel. Readers who hold one people", 13, ""),
        ("of God read Revelation 21:9-14 as a single bride instead.", 13, ""),
    ]
    c, nh = lines_card(LX, y, RX + LW - LX, note, dashed=True, stroke=BLUE, lh=19)
    out += c
    y += nh + 26

    c, _ = card(LX, y, 200, ["Scripture states it"], "", size=13)
    out += c
    c, _ = card(LX + 216, y, 150, ["A reading"], "", dashed=True, stroke=BLUE, size=13)
    out += c
    out.append(f'<path d="M{LX + 392} {y + 14} H{LX + 426}" stroke="{RED}" stroke-width="2.4"/>')
    out.append(arrow_head(LX + 430, y + 14, 0, 9, RED))
    out.append(text(LX + 438, y + 19, "the title God kept, taken by Jesus", 13))
    y += 92
    out += closing_verse(y, "“The Spirit and the Bride say, ‘Come.’”", "Revelation 22:17 (ESV)")
    h = y + 74
    out.append(credit(h))

    desc = (
        "A chart of the bride through Scripture in two lanes, the Husband on the left and the Bride "
        "on the right, joined in each era. The prophets: the LORD, your Maker, is your husband "
        "(Isaiah 54:5; Jeremiah 31:32), and Israel is betrothed to Him, I will betroth you to me "
        "forever (Hosea 2:19-20; Jeremiah 2:2; Ezekiel 16:8). A red arrow marks the title passing "
        "to Jesus. The Gospels: Jesus is the bridegroom, the one who has the bride (John 3:29; "
        "Matthew 9:15; 25:1), and He promises, I will come again and will take you to myself (John "
        "14:2-3). The Epistles: Christ loved the church and gave himself up for her (Ephesians "
        "5:25), and the church is betrothed to one husband (2 Corinthians 11:2; Ephesians "
        "5:31-32). Revelation: the marriage of the Lamb has come, and his Bride has made herself "
        "ready, the Bride, the wife of the Lamb (Revelation 19:7-8; 21:2, 9). Israel's lane does "
        "not run into the church's. A dashed note gives this site's reading, one Husband with two "
        "covenanted peoples, since Hosea 2:19's betrothal is still future, and names the "
        "one-bride reading of Revelation 21:9-14. It closes on Revelation 22:17, The Spirit and "
        "the Bride say, Come."
    )
    return "\n".join(svg_open(h, "The bride through Scripture", desc) + out + ["</svg>"]) + "\n"


# (number, name, quotation, reference, aorist form or None, the custom behind it)
COMPONENTS = [
    (1, "Purchased", "“you were bought with a price”", "1 Corinthians 6:20", "ἠγοράσθητε",
     "betrothal “by money” · m. Kiddushin 1:1"),
    (2, "Betrothed", "“I betrothed you to one husband”", "2 Corinthians 11:2", "ἡρμοσάμην",
     "betrothal “by document” · m. Kiddushin 1:1"),
    (3, "Pledged", "“sealed with the promised Holy Spirit”", "Ephesians 1:13-14", "ἐσφραγίσθητε",
     "a deposit against the rest · ἀρραβών"),
    (4, "Set apart", "“you were washed, you were sanctified”", "1 Corinthians 6:11", "ἡγιάσθητε",
     "“the sanctification of the bride”"),
    (5, "Preparing", "“I go to prepare a place for you”", "John 14:2 · Revelation 19:7", None,
     "twelve months, for both · m. Ketubot 5:2"),
    (6, "Fetched", "“to meet the Lord in the air”", "1 Thessalonians 4:17 · Matthew 25:6", None,
     "the groom comes for her"),
    (7, "Married, and feasting", "“the marriage supper of the Lamb”", "Revelation 19:7-9", None,
     "a seven-day feast · Genesis 29:27"),
    (8, "Homed", "“the dwelling place of God is with man”", "Revelation 21:3 · John 14:2", None,
     "the groom’s father’s house"),
]

GROUPS = [
    ("DONE · ALREADY TRUE OF YOU", (1, 2, 3, 4), INK, CARD),
    ("NOW · WHERE YOU STAND", (5,), GOLD_EDGE, GOLD_TINT),
    ("AHEAD · ANNOUNCED, NOT YET DONE", (6, 7, 8), BLUE, BLUE_TINT),
]


def wedding_pattern():
    SPINE, CW, STEP = W / 2, 300, 74
    out = heading("Four Done, One Now, Three Ahead", "The wedding pattern, and where the church stands in it")
    y = 130
    by_num = {c[0]: c for c in COMPONENTS}
    spine_top = None
    for label, nums, colour, tint in GROUPS:
        band_top = y
        out.append(("BANNER", y, label, colour))
        y += 46
        for n in nums:
            num, name, quote, ref, aorist, custom = by_num[n]
            left = num % 2 == 1
            rows = [(f"{num} · {name}", 15.5, "bold"), (quote, 13.5, "italic"), (ref, 12.5, "muted")]
            if aorist:
                rows.append((f"{aorist} · aorist: done", 13, "red"))
            rows.append((custom, 12, "muted"))
            cx = SPINE - 36 - CW if left else SPINE + 36
            c, ch = lines_card(cx, y, CW, rows, stroke=colour, fill=tint if n == 5 else CARD, lh=18)
            out += c
            my = y + 24
            ex = cx + CW if left else cx
            out.append(f'<path d="M{ex} {my} H{SPINE}" stroke="{colour}" stroke-width="1.4"/>')
            if spine_top is None:
                spine_top = my
            out.append(("MEDAL", SPINE, my, num, colour))
            if n == 5:
                out.append(text(SPINE + 28, my + 6, "◀ you are here", 15, "start", "bold",
                                fill=GOLD_EDGE, italic=True))
            y += STEP if n not in (4, 5, 8) else ch + 14
        y += 26
        out.insert(0, f'<rect x="28" y="{band_top - 8}" width="{W - 56}" height="{y - band_top - 4}" '
                      f'rx="8" fill="{tint}" opacity="0.35"/>')
    # The spine runs behind the ribbons and cards; the medallions sit on top of it.
    medals = [o for o in out if isinstance(o, tuple) and o[0] == "MEDAL"]
    banners = [o for o in out if isinstance(o, tuple) and o[0] == "BANNER"]
    out = [o for o in out if not isinstance(o, tuple)]
    first, last = medals[0][2], medals[-1][2]
    split = next(m[2] for m in medals if m[3] == 6)
    bands = [o for o in out if o.startswith("<rect x=\"28\"")]
    out = [o for o in out if o not in bands]
    spine = [f'<path d="M{SPINE} {first} V{split}" stroke="{INK}" stroke-width="3"/>',
             f'<path d="M{SPINE} {split} V{last}" stroke="{BLUE}" stroke-width="3"/>']
    out = bands + spine + out
    for _, by, label, colour in banners:
        out += banner(W / 2, by, 380, label, fill=colour, size=13)
    for _, x, my, num, colour in medals:
        fill = INK if num <= 4 else GOLD if num == 5 else CARD
        ink = CARD if num <= 4 else INK if num == 5 else BLUE
        out.append(f'<circle cx="{x}" cy="{my}" r="17" fill="{fill}" stroke="{colour}" stroke-width="2"/>')
        out.append(text(x, my + 6, str(num), 16, "middle", "bold", fill=ink))

    y += 10
    out.append(text(W / 2, y, "Each Greek verb in red is aorist: an act done and over.", 13.5,
                    "middle", italic=True, fill=MUTED))
    y += 76
    out += closing_verse(y, "“He who began a good work in you will bring it to completion”",
                         "Philippians 1:6 (ESV)")
    h = y + 74
    out.append(credit(h))

    steps = "; ".join(
        f"{num}, {name}: {quote.strip('“”')} ({ref})" + (f", {aorist}, aorist" if aorist else "")
        + f"; the custom: {custom}" for num, name, quote, ref, aorist, custom in COMPONENTS)
    desc = (
        "The wedding pattern's eight components down a central line, in three bands. Done, already "
        "true of you: components 1 to 4. Now, where you stand: component 5, marked you are here. "
        f"Ahead, announced and not yet done: components 6 to 8. {steps}. A note says each Greek "
        "verb in red is aorist, an act done and over. It closes on Philippians 1:6, he who began a "
        "good work in you will bring it to completion."
    )
    return "\n".join(svg_open(h, "Four done, one now, three ahead", desc) + out + ["</svg>"]) + "\n"


def bride_and_the_ages():
    h = 880
    out = heading("From the Supper to the House", "The wedding runs 7 into 8; Scripture puts an age between")
    base = 470
    # Segments along the line of time: (label, x, w, fill, stroke, note beneath)
    segs = [
        ("THE CHURCH AGE", 36, 166, GOLD, GOLD_EDGE, ""),
        ("THE WEEK · 7 YEARS", 214, 158, RED_TINT, INK, "Daniel 9:27 · on the earth"),
        ("1,000 YEARS", 384, 132, GOLD_TINT, GOLD_EDGE, ""),
        ("NEW CREATION", 528, 156, CARD, INK, "Revelation 21:1"),
    ]
    out.append(f'<path d="M28 {base + 32} H{W - 28}" stroke="{INK}" stroke-width="1.6"/>')
    for label, x, w, fill, stroke, note in segs:
        out.append(f'<rect x="{x}" y="{base}" width="{w}" height="32" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        out.append(text(x + w / 2, base + 21, label, 12, "middle", "bold", spacing="1"))
        if note:
            out.append(text(x + w / 2, base + 50, note, 12, "middle", italic=True, fill=MUTED))
    # The thousand years: a span the text counts.
    out.append(f'<path d="M384 {base - 16} H516" stroke="{RED}" stroke-width="3"/>')
    out.append(f'<path d="M384 {base - 22} V{base - 10} M516 {base - 22} V{base - 10}" stroke="{RED}" stroke-width="1.5"/>')
    out.append(text(450, base - 26, "Revelation 20:1-6", 12, "middle", italic=True, fill=RED))

    # Heaven, over the week: the marriage of the Lamb, placed by Revelation 19's order.
    out.append(text(300, 120, "IN HEAVEN", 14, "middle", "bold", fill=GOLD_EDGE, spacing="2"))
    out += cloud(300, 236, 330)
    c, _ = card(194, 140, 212, ["7 · Married, and feasting", "the marriage of the Lamb"],
                "Revelation 19:7-9", dashed=True)
    out += c

    # 6: fetched, up from the end of the church age (placed by inference: dashed).
    out.append(f'<path d="M196 {base - 6} Q180 340 194 254" fill="none" stroke="{GOLD_EDGE}" '
               f'stroke-width="2.4" stroke-dasharray="6 5"/>')
    out.append(arrow_head(195, 248, -84, 10, GOLD_EDGE))
    c, _ = card(36, 300, 140, ["6 · Fetched", "caught up to meet", "the Lord in the air"],
                "1 Thessalonians 4:17", dashed=True, size=13)
    out += c

    # Christ returns in power at the end of the week: solid, Revelation 19:11.
    out.append(f'<path d="M448 238 Q430 360 376 {base - 8}" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.6"/>')
    out.append(arrow_head(373, base - 5, 120, 10, GOLD_EDGE))
    c, _ = card(466, 258, 214, ["Christ returns in power", "the tribulation ends"],
                "Revelation 19:11 · Matthew 24:29", size=13)
    out += c

    # The great white throne, between the thousand years and the new creation.
    out.append(f'<path d="M522 {base - 2} V416" stroke="{INK}" stroke-width="1.4"/>')
    c, _ = card(512, 352, 172, ["Great white throne", "the final judgment"],
                "Revelation 20:11-15", size=13)
    out += c

    # Under the line: where the components fall.
    y = base + 74
    out.append(f'<path d="M36 {y} V{y + 10} H202 V{y}" fill="none" stroke="{GOLD_EDGE}" stroke-width="1.6"/>')
    out.append(text(119, y + 30, "1-5 · Purchased, betrothed,", 13, "middle", "bold"))
    out.append(text(119, y + 48, "pledged, set apart, preparing", 13, "middle", "bold"))
    out.append(text(119, y + 68, "▲ you are here", 13.5, "middle", "bold", fill=GOLD_EDGE, italic=True))

    out.append(f'<path d="M372 {y} V{y + 10} H528 V{y}" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    out.append(text(450, y + 30, "Between 7 and 8: an age", 13, "middle", "bold", fill=RED))
    out.append(text(450, y + 48, "the return, the reign,", 13, "middle"))
    out.append(text(450, y + 66, "the judgment", 13, "middle"))

    c, _ = card(548, y + 4, 136, ["8 · Homed", "God dwells", "with them"], "Revelation 21:3",
                dashed=True, size=13)
    out += c

    y += 140
    out += legend_row(36, y)
    y += 90
    out += closing_verse(y, "“that where I am you may be also”", "John 14:3 (ESV)")
    h = y + 74
    out.append(credit(h))

    desc = (
        "A time line from the church age through the seven-year week (Daniel 9:27) and the "
        "thousand years (Revelation 20:1-6, a span the text counts) to the new heaven and new "
        "earth. Components 1 to 5, purchased, betrothed, pledged, set apart and preparing, fall in "
        "the church age, marked you are here. Component 6, fetched, caught up to meet the Lord in "
        "the air (1 Thessalonians 4:17), is a dashed arrow up from the end of the church age to a "
        "cloud labelled in heaven, where component 7, married and feasting, the marriage of the "
        "Lamb (Revelation 19:7-9), is placed by its order. A solid arrow brings Christ back in "
        "power at the end of the week (Revelation 19:11; Matthew 24:29). The great white throne (Revelation "
        "20:11-15) stands between the thousand years and the new creation. A red bracket marks "
        "the age between components 7 and 8: the return, the reign and the judgment. Component 8, "
        "homed, God dwells with them (Revelation 21:3), is in the new heaven and new earth. Solid "
        "is dated by the text; dashed is placed by its order. It closes on John 14:3, that where I "
        "am you may be also."
    )
    return "\n".join(svg_open(h, "From the supper to the house", desc) + out + ["</svg>"]) + "\n"


SCRIPTURE_TIER = ["Ephesians 5:31-32 · 2 Corinthians 11:2 · John 3:29",
                  "Revelation 19:7-9 · 21:2, 9 · Hosea 2:19-20 · Isaiah 54:5; 62:5"]
CUSTOM_STONES = [
    ("Betrothal", "binding", "m. Kiddushin 1:1"),
    ("Twelve months", "to prepare", "m. Ketubot 5:2"),
    ("The father’s", "house", "Tobit 7:13"),
    ("A seven-day", "feast", "Genesis 29:27"),
]
LOOSE_STONES = [
    ("The father", "inspects the", "addition"),
    ("“Only my", "father knows”", "as an idiom"),
    ("John 14:2 as", "a bridal", "chamber"),
]


def type_stands_on():
    h = 900
    out = heading("What the Picture Stands On", "Scripture, documented custom, and details with no ancient source")
    HX0, HX1 = 50, 470
    cx = (HX0 + HX1) / 2
    # The house: roof and wall.
    roof_y, wall_y, course_y, rock_y = 140, 250, 350, 438
    out.append(f'<path d="M{HX0 - 10} {wall_y} L{cx} {roof_y} L{HX1 + 10} {wall_y} Z" fill="{GOLD_TINT}" '
               f'stroke="{GOLD_EDGE}" stroke-width="2"/>')
    out.append(text(cx, wall_y - 38, "THE CHURCH AS", 13.5, "middle", "bold", spacing="1.5"))
    out.append(text(cx, wall_y - 18, "CHRIST’S BETROTHED BRIDE", 13.5, "middle", "bold", spacing="1.5"))
    out.append(f'<rect x="{HX0 + 20}" y="{wall_y}" width="{HX1 - HX0 - 40}" height="{course_y - wall_y}" '
               f'fill="{CARD}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<path d="M{cx - 22} {course_y} V{wall_y + 40} Q{cx} {wall_y + 22} {cx + 22} {wall_y + 40} V{course_y}" '
               f'fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.4"/>')
    for wx in (HX0 + 60, HX1 - 110):
        out.append(f'<rect x="{wx}" y="{wall_y + 28}" width="50" height="40" fill="{EARTH_TINT}" '
                   f'stroke="{INK}" stroke-width="1.2"/>')
        out.append(f'<path d="M{wx + 25} {wall_y + 28} V{wall_y + 68}" stroke="{INK}" stroke-width="0.8"/>')
    # Tier 2: a course of dressed stones.
    sw = (HX1 - HX0) / len(CUSTOM_STONES)
    for i, (a, b, ref) in enumerate(CUSTOM_STONES):
        x = HX0 + i * sw
        out.append(f'<rect x="{x + 2:.1f}" y="{course_y}" width="{sw - 4:.1f}" height="{rock_y - course_y - 2}" '
                   f'rx="3" fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1.4"/>')
        out.append(text(x + sw / 2, course_y + 26, a, 13, "middle", "bold"))
        out.append(text(x + sw / 2, course_y + 44, b, 13, "middle", "bold"))
        out.append(text(x + sw / 2, course_y + 68, ref, 11.5, "middle", italic=True, fill=MUTED))
    # Tier 1: bedrock.
    out.append(f'<path d="M{HX0 - 20} {rock_y} H{HX1 + 20} L{HX1 + 32} {rock_y + 96} H{HX0 - 32} Z" '
               f'fill="{INK}" stroke="{INK}"/>')
    out.append(text(cx, rock_y + 30, "SCRIPTURE STATES IT", 14.5, "middle", "bold", fill=CARD, spacing="2"))
    for i, ln in enumerate(SCRIPTURE_TIER):
        out.append(text(cx, rock_y + 54 + 20 * i, ln, 12.5, "middle", italic=True, fill=GOLD_TINT))

    # The tier key, beside the house.
    kx = HX1 + 44
    for y0, title, sub in [
        (roof_y + 50, "THE DOCTRINE", ["what Scripture", "calls the church"]),
        (course_y + 22, "TIER 2", ["documented custom:", "the Mishnah, Tobit,", "Scripture’s weddings"]),
        (rock_y + 30, "TIER 1", ["stated by Scripture", "in its own voice"]),
    ]:
        out.append(text(kx, y0, title, 13.5, "start", "bold", spacing="1.5"))
        for j, s in enumerate(sub):
            out.append(text(kx, y0 + 19 + 17 * j, s, 13, italic=True, fill=MUTED))

    # Tier 3: loose stones on the ground, set aside.
    gy = rock_y + 140
    out.append(text(W / 2, gy, "TIER 3 · NO ANCIENT SOURCE", 14.5, "middle", "bold", fill=RED, spacing="2"))
    out.append(text(W / 2, gy + 20, "set aside: no Mishnah, Talmud or Josephus passage is produced for them",
                    13, "middle", italic=True, fill=MUTED))
    lw, gap = 180, 30
    lx0 = (W - (3 * lw + 2 * gap)) / 2
    for i, rows in enumerate(LOOSE_STONES):
        x = lx0 + i * (lw + gap)
        tilt = (-4, 3, -2)[i]
        out.append(f'<g transform="rotate({tilt} {x + lw / 2} {gy + 90})">'
                   f'<rect x="{x}" y="{gy + 44}" width="{lw}" height="88" rx="10" fill="{CARD}" '
                   f'stroke="{RED}" stroke-width="1.4" stroke-dasharray="6 5"/>'
                   + "".join(text(x + lw / 2, gy + 72 + 19 * j, s, 13.5, "middle", "bold" if j == 0 else None)
                             for j, s in enumerate(rows)) + '</g>')
    out.append(f'<path d="M40 {gy + 140} H{W - 40}" stroke="{MUTED}" stroke-width="1"/>')

    out += closing_verse(gy + 196, "“times or seasons that the Father has fixed by his own authority”",
                         "Acts 1:7 (ESV)")
    out.append(credit(h))

    stones = "; ".join(f"{a} {b} ({r})" for a, b, r in CUSTOM_STONES)
    loose = "; ".join(" ".join(r) for r in LOOSE_STONES)
    desc = (
        "A house labelled the church as Christ's betrothed bride, standing on two tiers. Its "
        "foundation, tier 1, is bedrock: Scripture states it, "
        f"{' · '.join(SCRIPTURE_TIER)}. Above the bedrock, tier 2 is a course of dressed stones, "
        f"documented custom: {stones}. Below, on the ground and outside the house, tier 3 is three "
        f"loose stones in dashed red, with no ancient source and set aside: {loose}. It closes on "
        "Acts 1:7, times or seasons that the Father has fixed by his own authority."
    )
    return "\n".join(svg_open(h, "What the picture stands on", desc) + out + ["</svg>"]) + "\n"


PLATES = {
    "promised-messiah": promised_messiah,
    "bride-through-scripture": bride_through_scripture,
    "wedding-pattern": wedding_pattern,
    "bride-and-the-ages": bride_and_the_ages,
    "type-stands-on": type_stands_on,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, draw in PLATES.items():
        path = OUT / f"{name}.svg"
        path.write_text(draw(), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
