"""Draw the graphics for docs/content/israel-and-church/.

promised-messiah.svg, for hebrew-roots.md: a relationship graphic. Across the top, the line the
promises travel (the patriarchs, Israel's Scriptures, the Messiah, the nations, Romans 9:4-5;
15:8-9). Below, each promise Israel's Scriptures make about the Messiah beside the New Testament
text that names Jesus as its fulfilment, grouped by His line, birth, ministry, suffering and glory,
and what awaits His return. Solid is stated by the New Testament; dashed is a timing the church
reads differently, with both readings on the plate. Run from the repo root:

    python3 utils/build_israel_church_graphics.py
"""

from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, RED, GOLD, GOLD_EDGE, GOLD_TINT, BLUE, BLUE_TINT,
                        text, svg_open, heading, banner, arrow_head, card, credit)

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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "promised-messiah.svg"
    path.write_text(promised_messiah(), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
