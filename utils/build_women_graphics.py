"""Draw the plates for jesus/jesus-and-women.md and christian-life/submission-in-context.md.

    python3 utils/build_women_graphics.py

the-serving-word is a relationship diagram: one Greek verb, διακονέω (G1247), and its noun
διάκονος (G1249), joining what the women of Galilee did for Jesus (Luke 8:3; Mark 15:41) to what
Jesus says He came to do (Mark 10:45; Luke 22:27) and to what Paul calls Phoebe (Romans 16:1).
Every card quotes the ESV. The Greek forms are the NA28's.

one-verb-for-everyone is a relationship diagram in three parts. Ephesians 5:21's participle,
"submitting to one another", stands over the household code, and 5:22 (which has no verb of its own
in the Greek) hangs from it; the husband's charge sits beside the wife's, measured by Christ. Below,
1 Corinthians 7:4 is drawn as the mirror it is: ἐξουσιάζει in both directions, joined by ὁμοίως.
Last, the four New Testament uses of ἐξουσιάζω, with Luke 22:25-26 where Jesus forbids the Gentile
kind of authority to His disciples. Solid lines are the text's own grammar; the dashed line marks
the study's inference that 7:4 must be read through 7:5's "by agreement".
"""

from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, text, svg_open, heading, banner, arrow_head, credit)

ROOT = Path(__file__).resolve().parent.parent / "docs" / "content" / "assets" / "img"
LINE = 17


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


def quote_card(x, y, w, title, greek, quote, ref, fill, stroke, chars, dashed=False):
    rows = wrap(quote, chars)
    h = 14 + LINE * (len(rows) + 3)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" '
           f'stroke-width="1.5"{dash}/>']
    ty = y + 6 + LINE * 0.9
    out.append(text(x + 10, ty, title, 14, weight="bold"))
    ty += LINE
    out.append(text(x + 10, ty, greek, 14, fill=RED))
    ty += LINE
    for r in rows:
        out.append(text(x + 10, ty, r, 13.5, italic=True))
        ty += LINE
    out.append(text(x + w - 10, ty, ref, 12, "end", fill=MUTED))
    return out, h


def line(x1, y1, x2, y2, stroke=INK, dashed=False, width=1.4):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{stroke}" stroke-width="{width}" fill="none"{dash}/>'


def the_serving_word():
    h = 800
    out = svg_open(
        h, "The serving word",
        "One Greek verb, diakoneō, to serve, joins three groups of texts. At the centre, Jesus: "
        "'the Son of Man came not to be served but to serve' (Mark 10:45) and 'I am among you as "
        "the one who serves' (Luke 22:27). On the left, the women of Galilee: they 'provided for "
        "them out of their means' (Luke 8:3) and 'followed him and ministered to him' (Mark 15:41), "
        "both the same verb. On the right, Phoebe, 'a servant of the church at Cenchreae' (Romans "
        "16:1), the noun diakonos. The Gospels name the women's service with the word Jesus chose for His own.")
    out += heading("The serving word", "διακονέω (diakoneō, G1247): to serve, to minister, to provide")

    cx = W / 2
    c, ch = quote_card(cx - 170, 130, 340, "Jesus, the One who serves", "διακονῆσαι · ὡς ὁ διακονῶν",
                       "The Son of Man came not to be served but to serve, and to give his life as a "
                       "ransom for many. … I am among you as the one who serves.",
                       "Mark 10:45; Luke 22:27", GOLD_TINT, GOLD_EDGE, 44)
    out += c
    centre_bottom = 130 + ch

    y2 = centre_bottom + 90
    left, lh = quote_card(36, y2, 312, "The women of Galilee", "διηκόνουν (Luke 8:3; Mark 15:41)",
                          "Mary, called Magdalene … and Joanna … and Susanna, and many others, who "
                          "provided for them out of their means. … they followed him and ministered to him.",
                          "Luke 8:2-3; Mark 15:41", BLUE_TINT, BLUE, 40)
    right, rh = quote_card(W - 348, y2, 312, "Phoebe of Cenchreae", "διάκονον · προστάτις",
                           "Our sister Phoebe, a servant of the church at Cenchreae … she has been a "
                           "patron of many and of myself as well.",
                           "Romans 16:1-2", BLUE_TINT, BLUE, 40)
    out += left + right
    for x in (192, W - 192):
        out.append(line(cx, centre_bottom, x, y2 - 4, GOLD_EDGE, width=2))
        ang = 90 + (25 if x < cx else -25)
        out.append(arrow_head(x, y2 - 2, ang, 10, GOLD_EDGE))
    out.append(text(cx, centre_bottom + 52, "the same word", 14, "middle", italic=True, fill=MUTED))

    yb = y2 + max(lh, rh) + 40
    out += banner(cx, yb, 420, "WHAT THE WORD SAYS")
    notes = [
        "Luke names the women beside the Twelve: “the twelve were with him, and also some women”",
        "(Luke 8:1-2). The verb is imperfect: they kept on providing. Mark adds that they followed",
        "Him from Galilee and stood at the cross (Mark 15:40-41). Jesus chose the same verb for His",
        "own mission (Mark 10:45). Phoebe carries the word into the church, and the only New",
        "Testament προστάτις, “patron”, is hers (Romans 16:2).",
    ]
    ty = yb + 58
    for n in notes:
        out.append(text(48, ty, n, 14))
        ty += 22
    out.append(text(cx, ty + 30, "“Whoever would be great among you must be your servant.”", 15,
                    "middle", italic=True))
    out.append(text(cx, ty + 52, "Mark 10:43, ESV", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def one_verb_for_everyone():
    h = 1250
    out = svg_open(
        h, "One verb for everyone",
        "Three panels. First, Ephesians 5:21-33. Over the whole household code stands 5:21: "
        "'submitting to one another out of reverence for Christ'. In the Greek, 5:22 has no verb of "
        "its own (literally 'wives, to your own husbands, as to the Lord'); it borrows 'submitting' "
        "from 5:21, and 5:24 states it in full: 'wives should submit in everything to their husbands'. Beside the wives' instruction stands the husbands': love as Christ loved "
        "the church and gave himself up for her, nourish and cherish. Second, 1 Corinthians 7:4 as a "
        "mirror: the wife does not have authority over her own body, but the husband does; likewise "
        "the husband does not have authority over his own body, but the wife does. The same verb "
        "runs both ways, joined by 'likewise', and 7:5 limits even abstaining to 'agreement'. Third, "
        "the four New Testament uses of the verb exousiazō: 1 Corinthians 6:12, 7:4 twice, and "
        "Luke 22:25, where Jesus says the Gentile rulers exercise authority over people, 'but not "
        "so with you'.")
    out += heading("One verb for everyone", "Ephesians 5:21-33 and 1 Corinthians 7:4, as the Greek runs")

    # Panel 1: Ephesians 5
    y = 120
    out += banner(W / 2, y, 300, "EPHESIANS 5:21-33")
    y += 46
    umb_h = 70
    out.append(f'<rect x="60" y="{y}" width="{W - 120}" height="{umb_h}" rx="8" fill="{GOLD_TINT}" '
               f'stroke="{GOLD_EDGE}" stroke-width="2"/>')
    out.append(text(W / 2, y + 26, "“submitting to one another out of reverence for Christ”", 16,
                    "middle", italic=True))
    out.append(text(W / 2, y + 50, "ὑποτασσόμενοι ἀλλήλοις · 5:21 · said to the whole church", 14,
                    "middle", fill=RED))
    top = y + umb_h
    y = top + 50
    wives, wh = quote_card(48, y, 296, "Wives · 5:22-24, 33", "5:22 has no verb of its own",
                           "Literally: “wives, to your own husbands, as to the Lord.” The verb is "
                           "borrowed from 5:21. … As the church submits to Christ, so also wives "
                           "should submit in everything to their husbands.",
                           "Ephesians 5:22 (NA28), 24 (ESV)", BLUE_TINT, BLUE, 38)
    husb, hh = quote_card(W - 344, y, 296, "Husbands · 5:25-29, 33", "ἀγαπᾶτε · ἐκτρέφει καὶ θάλπει",
                          "Love your wives, as Christ loved the church and gave himself up for her. "
                          "… nourishes and cherishes it, just as Christ does the church.",
                          "Ephesians 5:25, 29", BLUE_TINT, BLUE, 38)
    out += wives + husb
    for x in (196, W - 196):
        out.append(line(x, top, x, y - 4, GOLD_EDGE, width=2))
        out.append(arrow_head(x, y - 2, 90, 10, GOLD_EDGE))
    y += max(wh, hh) + 26
    out.append(f'<rect x="60" y="{y}" width="{W - 120}" height="58" rx="8" fill="{CARD}" stroke="{INK}" stroke-width="1.4"/>')
    out.append(text(W / 2, y + 24, "The measure of both: Christ, who “loved us and gave himself up for us”", 14.5,
                    "middle", weight="bold"))
    out.append(text(W / 2, y + 45, "Ephesians 5:2 · the head defined by the cross (5:23, 25)", 13, "middle",
                    fill=MUTED, italic=True))
    y += 100

    # Panel 2: 1 Corinthians 7:4 mirror
    out += banner(W / 2, y, 300, "1 CORINTHIANS 7:4")
    y += 52
    bw, bh = 260, 128
    lx, rx = 56, W - 56 - bw
    for x, who, body, other in ((lx, "THE WIFE", "her own body", "the husband"),
                                (rx, "THE HUSBAND", "his own body", "the wife")):
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{BLUE_TINT}" stroke="{BLUE}" stroke-width="1.6"/>')
        out.append(text(x + bw / 2, y + 28, who, 15, "middle", "bold", spacing="1.5"))
        out.append(text(x + bw / 2, y + 52, "does not have authority", 13.5, "middle", italic=True))
        out.append(text(x + bw / 2, y + 72, f"over {body},", 13.5, "middle", italic=True))
        out.append(text(x + bw / 2, y + 92, f"but {other} does", 13.5, "middle", italic=True))
        out.append(text(x + bw / 2, y + 116, "ἐξουσιάζει", 14, "middle", fill=RED))
    mid_y = y + bh / 2
    out.append(line(lx + bw + 8, mid_y - 12, rx - 12, mid_y - 12, RED, width=2))
    out.append(arrow_head(rx - 8, mid_y - 12, 0, 10, RED))
    out.append(line(rx - 8, mid_y + 12, lx + bw + 12, mid_y + 12, RED, width=2))
    out.append(arrow_head(lx + bw + 8, mid_y + 12, 180, 10, RED))
    out.append(text(W / 2, mid_y + 4, "ὁμοίως", 15, "middle", "bold", fill=RED))
    out.append(text(W / 2, mid_y + 40, "“likewise”", 13, "middle", italic=True, fill=MUTED))
    y += bh + 22
    out.append(f'<rect x="110" y="{y}" width="{W - 220}" height="52" rx="8" fill="{CARD}" stroke="{INK}" '
               f'stroke-width="1.4" stroke-dasharray="5 4"/>')
    out.append(text(W / 2, y + 22, "Read with 7:5: “except perhaps by agreement” (ἐκ συμφώνου)", 14, "middle"))
    out.append(text(W / 2, y + 42, "Each is given to the other; neither is licensed to take", 13, "middle",
                    italic=True, fill=MUTED))
    y += 100

    # Panel 3: the four uses of ἐξουσιάζω
    out += banner(W / 2, y, 420, "ἐξουσιάζω IN THE NEW TESTAMENT: 4 USES")
    y += 50
    rows = [
        ("1 Corinthians 6:12", "“I will not be dominated by anything.”", BLUE_TINT, BLUE),
        ("1 Corinthians 7:4", "The husband has authority over the wife’s body.", BLUE_TINT, BLUE),
        ("1 Corinthians 7:4", "The wife has authority over the husband’s body.", BLUE_TINT, BLUE),
        ("Luke 22:25-26", "“Those in authority over them … But not so with you.”", RED_TINT, RED),
    ]
    for ref, s, fill, stroke in rows:
        out.append(f'<rect x="60" y="{y}" width="{W - 120}" height="40" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
        out.append(text(76, y + 26, ref, 14, weight="bold"))
        out.append(text(250, y + 26, s, 14, italic=True))
        y += 50
    y += 10
    out.append(text(W / 2, y + 10, "Jesus forbids His people the Gentile kind of authority, and Paul’s only", 14, "middle"))
    out.append(text(W / 2, y + 30, "use of the verb inside marriage gives it equally to both.", 14, "middle"))
    out.append(text(W / 2, y + 70, "“I am among you as the one who serves.”", 15, "middle", italic=True))
    out.append(text(W / 2, y + 92, "Luke 22:27, ESV", 12.5, "middle", fill=MUTED))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    for folder, name, fn in (("jesus-and-women", "the-serving-word", the_serving_word),
                             ("submission-in-context", "one-verb-for-everyone", one_verb_for_everyone)):
        d = ROOT / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(f"wrote {d / name}.svg")


if __name__ == "__main__":
    main()
