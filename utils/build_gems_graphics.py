"""Draw the precious-stones plate for god/precious-stones.md.

    uv run --with uharfbuzz --with fonttools python3 utils/build_gems_graphics.py

A relationship plate: the twelve stones of the high priest's breastpiece (Exodus 28:17-20) in their
four rows, which of them Ezekiel 28:13 names in the Hebrew, and which reappear among the twelve
foundations of the city (Revelation 21:19-20). Each swatch is coloured from what Pliny says the
stone's Greek name meant (Natural History 37), because the Greek names are what Revelation shares
with the Septuagint's breastpiece. The English beside each is the ESV's, which often follows a
different identification; the plate shows both so the mismatch is visible. A swatch is dashed where
the stone an ancient name meant is uncertain, and a foundation is dashed where its stone is absent
from the breastpiece.
"""

import math
from pathlib import Path

from lib.larkin import (W, INK, MUTED, CARD, GOLD, GOLD_EDGE, GOLD_TINT, text,
                        svg_open, heading, banner, credit, arrow_head)
from lib.outline_text import place, GREEK

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "gems"

# Swatch colours, one per ancient stone name, from Pliny's descriptions.
CARNELIAN = "#b8401f"     # sarda, "rubrae" (37.105)
PERIDOT = "#a8c046"       # topazos, "e virenti genere" (37.107)
EMERALD = "#1f8a5b"       # smaragdus (37.62)
FIRE_RED = "#8e1b24"      # carbunculus/anthrax, "a similitudine ignium" (37.92)
LAPIS = "#23408e"         # sapphirus, gold in spots (37.119), never translucent (37.120)
JASPER_GREEN = "#8fb89a"  # iaspis, "viret et saepe tralucet" (37.115)
AMBER = "#d98a2b"         # lyncurium, "colorem igneum" (37.53)
AGATE = "#b98a5e"         # achates, banded
AMETHYST = "#7a4b9c"      # amethystus, "violaceo decore" (37.121)
GOLDEN = "#d6b13a"        # chrysolithos, "aureo fulgore tralucentes" (37.126)
SEA_GREEN = "#7fbfb5"     # beryllus, "viriditatem maris puri" (37.76)
ONYX = "#2b2b2b"          # onyx, white like a fingernail over dark (37.90)
CHALCEDONY = "#8fa3b5"    # chalcedon: not in Pliny under this name
LEEK = "#6fbf4a"          # chrysoprasus, "porri sucum" (37.113)
HYACINTH = "#5a63b0"      # hyacinthus, a diluted violet (37.125)

# (Hebrew, transliteration, Septuagint Greek, ESV English, swatch, pattern, uncertain)
BREASTPIECE = [
    ("אֹדֶם", "ʾodem", "σάρδιον", "sardius", CARNELIAN, None, False),
    ("פִּטְדָה", "pitdah", "τοπάζιον", "topaz", PERIDOT, None, False),
    ("בָּרֶקֶת", "bareqet", "σμάραγδος", "carbuncle", EMERALD, None, False),
    ("נֹפֶךְ", "nofekh", "ἄνθραξ", "emerald", FIRE_RED, None, False),
    ("סַפִּיר", "sappir", "σάπφειρος", "sapphire", LAPIS, "flecks", False),
    ("יַהֲלֹם", "yahalom", "ἴασπις", "diamond", JASPER_GREEN, None, False),
    ("לֶשֶׁם", "leshem", "λιγύριον", "jacinth", AMBER, None, True),
    ("שְׁבוֹ", "shevo", "ἀχάτης", "agate", AGATE, "bands", False),
    ("אַחְלָמָה", "ʾachlamah", "ἀμέθυστος", "amethyst", AMETHYST, None, False),
    ("תַּרְשִׁישׁ", "tarshish", "χρυσόλιθος", "beryl", GOLDEN, None, False),
    ("שֹׁהַם", "shoham", "βηρύλλιον", "onyx", SEA_GREEN, None, False),
    ("יָשְׁפֵה", "yashpeh", "ὀνύχιον", "jasper", ONYX, "bands", False),
]
# Positions (1-12) the Hebrew of Ezekiel 28:13 names: all but the third row.
EZEKIEL_MT = {1, 2, 3, 4, 5, 6, 10, 11, 12}

ORDINALS = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]
# (Greek, ESV English, swatch, pattern, uncertain, breastpiece position or None, relation note)
FOUNDATIONS = [
    ("ἴασπις", "jasper", JASPER_GREEN, None, False, 6, None),
    ("σάπφειρος", "sapphire", LAPIS, "flecks", False, 5, None),
    ("χαλκηδών", "agate", CHALCEDONY, None, True, None, "not on the breastpiece"),
    ("σμάραγδος", "emerald", EMERALD, None, False, 3, None),
    ("σαρδόνυξ", "onyx", CARNELIAN, "bands", False, None, "sard and onyx in one stone"),
    ("σάρδιον", "carnelian", CARNELIAN, None, False, 1, None),
    ("χρυσόλιθος", "chrysolite", GOLDEN, None, False, 10, None),
    ("βήρυλλος", "beryl", SEA_GREEN, None, False, 11, None),
    ("τοπάζιον", "topaz", PERIDOT, None, False, 2, None),
    ("χρυσόπρασος", "chrysoprase", LEEK, None, False, None, "not on the breastpiece"),
    ("ὑάκινθος", "jacinth", HYACINTH, None, True, None, "not on the breastpiece"),
    ("ἀμέθυστος", "amethyst", AMETHYST, None, False, 9, None),
]


def swatch(cx, cy, r, colour, pattern, uncertain, gid):
    """A cabochon: the colour with a highlight, and the stone's figure where Pliny gives one."""
    out = [f'<radialGradient id="{gid}" cx="0.38" cy="0.32" r="0.75">'
           f'<stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/>'
           f'<stop offset="0.35" stop-color="{colour}" stop-opacity="1"/>'
           f'<stop offset="1" stop-color="{colour}" stop-opacity="1"/></radialGradient>',
           f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="url(#{gid})"/>']
    if pattern == "flecks":
        for dx, dy in [(-6, 4), (5, -2), (2, 8), (-2, -7), (8, 6)]:
            out.append(f'<circle cx="{cx + dx * r / 20:.1f}" cy="{cy + dy * r / 20:.1f}" '
                       f'r="{max(1.0, r / 14):.1f}" fill="{GOLD}"/>')
    if pattern == "bands":
        for k in (-0.35, 0.15):
            out.append(f'<path d="M{cx - r * 0.85:.1f} {cy + k * r:.1f} Q{cx:.1f} {cy + (k - 0.35) * r:.1f} '
                       f'{cx + r * 0.85:.1f} {cy + k * r:.1f}" stroke="#f5efe2" stroke-width="{r / 7:.1f}" '
                       f'fill="none" opacity="0.85"/>')
    dash = ' stroke-dasharray="4 3"' if uncertain else ""
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="{INK}" '
               f'stroke-width="1.4"{dash}/>')
    return out


def breastpiece(y0):
    cw, ch, gap = 208, 104, 10
    x0 = (W - 3 * cw - 2 * gap) / 2
    h = 4 * ch + 3 * gap
    # The stones are "set in gold filigree" (Exodus 28:20).
    out = [f'<rect x="{x0 - 10:.1f}" y="{y0 - 10}" width="{3 * cw + 2 * gap + 20:.1f}" height="{h + 20}" '
           f'rx="8" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>']
    for i, (he, tr, gr, en, colour, pattern, uncertain) in enumerate(BREASTPIECE):
        n = i + 1
        x = x0 + (i % 3) * (cw + gap)
        y = y0 + (i // 3) * (ch + gap)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw}" height="{ch}" rx="5" fill="{CARD}" '
                   f'stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
        out += swatch(x + 30, y + 42, 20, colour, pattern, uncertain, f"bp{n}")
        out.append(text(x + 30, y + 86, f"{n}", 12, "middle", fill=MUTED))
        path, _ = place(he, x + 62, y + 32, 21, anchor="start", fill=INK)
        out.append(path)
        out.append(text(x + 62, y + 50, tr, 13, italic=True))
        path, _ = place(gr, x + 62, y + 72, 15, anchor="start", fill=INK, font=GREEK, weight=400, rtl=False)
        out.append(path)
        out.append(text(x + 62, y + 92, f"ESV {en}", 12, fill=MUTED, italic=True))
        tags = []
        if n in EZEKIEL_MT:
            tags.append("Ezek 28")
        rev = [k + 1 for k, f in enumerate(FOUNDATIONS) if f[5] == n]
        if rev:
            tags.append(f"Rev 21 · {ORDINALS[rev[0] - 1]}")
        for k, tag in enumerate(tags):
            out.append(text(x + cw - 8, y + 16 + 15 * k, tag, 11, "end", fill=MUTED))
    return out, h


def foundations(y0):
    bw, bh, gap = 600, 32, 5
    x0 = (W - bw) / 2
    out = []
    for i, (gr, en, colour, pattern, uncertain, pos, note) in enumerate(FOUNDATIONS):
        y = y0 + i * (bh + gap)
        dash = ' stroke-dasharray="5 4"' if pos is None else ""
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{bw}" height="{bh}" rx="4" fill="{CARD}" '
                   f'stroke="{INK}" stroke-width="1.2"{dash}/>')
        out.append(text(x0 + 14, y + 21, ORDINALS[i], 13, weight="bold"))
        out += swatch(x0 + 66, y + bh / 2, 11, colour, pattern, uncertain, f"fd{i + 1}")
        path, _ = place(gr, x0 + 88, y + 22, 15, anchor="start", fill=INK, font=GREEK, weight=400, rtl=False)
        out.append(path)
        out.append(text(x0 + 232, y + 21, f"ESV {en}", 13, italic=True, fill=MUTED))
        if pos:
            row, col = (pos - 1) // 3 + 1, (pos - 1) % 3 + 1
            rel = f"breastpiece no. {pos} (row {row}, stone {col})"
        else:
            rel = note
        out.append(text(x0 + bw - 12, y + 21, rel, 13, "end"))
    return out, len(FOUNDATIONS) * (bh + gap) - gap


def plate():
    body = []
    body += heading("The stones in three lists", "Exodus 28 · Ezekiel 28 · Revelation 21")
    y = 120
    body.append(text(W / 2, y, "The breastpiece: twelve stones in four rows, each engraved with a tribe's name",
                     14, "middle"))
    body.append(text(W / 2, y + 18, "(Exodus 28:17-21). Hebrew, then the Septuagint's Greek, then the ESV.",
                     14, "middle"))
    grid, gh = breastpiece(y + 44)
    body += grid
    y = y + 44 + gh + 34
    body.append(text(W / 2, y, "Ezekiel 28:13 (Hebrew) names the nine marked “Ezek 28”: every row but the third.",
                     13.5, "middle"))
    body.append(text(W / 2, y + 18, "The Greek of Ezekiel 28:13 names all twelve in this order, with silver and gold after the sixth.",
                     13.5, "middle"))
    y += 48
    body += banner(W / 2, y, 540, "THE CITY’S FOUNDATIONS · REVELATION 21:19-20", size=13)
    fd, fh = foundations(y + 44)
    body += fd
    y = y + 44 + fh + 30
    key_y = y
    body += swatch(48, key_y, 9, "#cfc6b4", None, False, "key1")
    body.append(text(64, key_y + 5, "Colour of the stone the Greek name meant (Pliny, Natural History 37)", 12.5))
    body += swatch(48, key_y + 24, 9, "#cfc6b4", None, True, "key2")
    body.append(text(64, key_y + 29, "Which stone the ancient name meant is uncertain", 12.5))
    body.append(f'<rect x="38" y="{key_y + 40}" width="20" height="14" rx="3" fill="{CARD}" stroke="{INK}" '
                f'stroke-width="1.2" stroke-dasharray="5 4"/>')
    body.append(text(64, key_y + 52, "A foundation whose stone is not on the breastpiece", 12.5))
    body.append(text(64, key_y + 72, "The ESV’s English often follows a different identification from the swatch.",
                     12.5, fill=MUTED, italic=True))
    y = key_y + 108
    body.append(text(W / 2, y, "“The city has no need of sun or moon to shine on it, for the glory of God",
                     15, "middle", italic=True))
    body.append(text(W / 2, y + 20, "gives it light, and its lamp is the Lamb.”", 15, "middle", italic=True))
    body.append(text(W / 2, y + 40, "Revelation 21:23 (ESV)", 12.5, "middle", fill=MUTED))
    h = y + 80
    desc = ("A drawn plate in three parts. First, the high priest's breastpiece from Exodus 28:17-20 as a gold "
            "frame holding twelve stones in four rows of three. Each stone shows its Hebrew name and "
            "transliteration, the Septuagint's Greek name, the ESV's English name, and a coloured swatch "
            "showing the stone the Greek name meant according to Pliny: "
            + "; ".join(f"{n + 1}, {b[1]}, Greek {b[2]}, ESV {b[3]}" for n, b in enumerate(BREASTPIECE))
            + ". Stones 1 to 6 and 10 to 12 are marked as named in the Hebrew of Ezekiel 28:13; the third row "
            "is not. A note says the Greek of Ezekiel 28:13 names all twelve in the same order, with silver "
            "and gold after the sixth. Second, the twelve foundations of the city from Revelation 21:19-20 as "
            "stacked bands: "
            + "; ".join(f"{ORDINALS[n]}, Greek {f[0]}, ESV {f[1]}, "
                        + (f"breastpiece number {f[5]}" if f[5] else f[6]) for n, f in enumerate(FOUNDATIONS))
            + ". Eight foundations share their Greek name with a breastpiece stone. Ligyrion, chalcedon and "
            "hyacinth have dashed swatches because their identification is uncertain. Third, a key and "
            "Revelation 21:23: the glory of God gives the city light, and its lamp is the Lamb.")
    out = svg_open(h, "The stones in three lists", desc)
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# The light plate: five things a stone does with light, each set against the witness that saw it.
SUN = "#f2b84b"
GEM_TINT = "#cfe3ef"
GEM_EDGE = "#4f6f87"
STAR_BLUE = "#1d3f8f"
SPECTRUM = ["#c0392b", "#e67e22", "#f1c40f", "#27ae60", "#2e86c1", "#7d3c98"]
RAY = "#b8860b"
SPLIT_A = "#2e5fa8"
SPLIT_B = "#2f9e8f"

# (name, what happens, scripture line, witness line, stones line, drawing, attested before modern optics)
# The gemmologist's terms for each row, printed beside its name so the plate and the page agree.
LIGHT_TERMS = ["transparency · diaphaneity", "vitreous · adamantine", "refraction · “fire”",
               "phenomenal gem · silk", "birefringence · pleochroism"]
LIGHT_ROWS = [
    ("Clearness", "Light passes through the stone.",
     "“clear as crystal” (Revelation 21:11); “for clearness” (Exodus 24:10)",
     "Seen by: the prophets themselves",
     "Rock crystal, beryl, amethyst, emerald", "through", True),
    ("Lustre", "Light comes back off a polished face.",
     "“like the gleaming of beryl”, keʿeyn, the stone’s “eye” (Ezekiel 1:16)",
     "Seen by: the prophets themselves",
     "Every polished stone", "lustre", True),
    ("Dispersion", "White light spreads into its colours.",
     "the bow in the cloud around the throne (Ezekiel 1:28; Revelation 4:3)",
     "Seen by: Pliny, the iris crystal (Natural History 37.136)",
     "Every clear stone; strongest in diamond, its “fire”", "disperse", True),
    ("Asterism", "Fine needles inside return light as a star that moves.",
     "No verse names it. Pliny’s “pupil” echoes Ezekiel’s “eye”.",
     "Seen by: Pliny, the asteria (Natural History 37.131)",
     "Star sapphire; not diamond", "star", True),
    ("Double refraction", "The crystal splits light in two; colour shifts as it turns.",
     "No verse names it.",
     "Seen by: no ancient writer; first described in 1669",
     "Sapphire, emerald, beryl, amethyst; not diamond or garnet", "split", False),
]


def ray(x1, y1, x2, y2, colour=RAY, width=2.2, head=True):
    out = [f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{colour}" stroke-width="{width}" '
           f'stroke-linecap="round"/>']
    if head:
        out.append(arrow_head(x2, y2, math.degrees(math.atan2(y2 - y1, x2 - x1)), 8, colour))
    return out


def faceted(cx, cy, w, fill=GEM_TINT):
    """A cut stone in side view: crown above the girdle, pavilion below."""
    hc, hp = w * 0.22, w * 0.42
    return [f'<path d="M{cx - w / 2:.1f} {cy:.1f} L{cx - w / 3.2:.1f} {cy - hc:.1f} H{cx + w / 3.2:.1f} '
            f'L{cx + w / 2:.1f} {cy:.1f} L{cx:.1f} {cy + hp:.1f} Z" fill="{fill}" fill-opacity="0.85" '
            f'stroke="{GEM_EDGE}" stroke-width="1.4"/>',
            f'<path d="M{cx - w / 2:.1f} {cy:.1f} H{cx + w / 2:.1f}" stroke="{GEM_EDGE}" stroke-width="0.8"/>']


def sun(cx, cy, r=9):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SUN}" stroke="{GOLD_EDGE}" stroke-width="1"/>']
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M{cx + (r + 3) * math.cos(a):.1f} {cy + (r + 3) * math.sin(a):.1f} '
                   f'L{cx + (r + 8) * math.cos(a):.1f} {cy + (r + 8) * math.sin(a):.1f}" '
                   f'stroke="{GOLD_EDGE}" stroke-width="1.2"/>')
    return out


def eye(cx, cy, w=26):
    return [f'<path d="M{cx - w / 2} {cy} Q{cx} {cy - w / 2.4} {cx + w / 2} {cy} Q{cx} {cy + w / 2.4} '
            f'{cx - w / 2} {cy} Z" fill="{CARD}" stroke="{INK}" stroke-width="1.3"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{w / 6.5:.1f}" fill="{INK}"/>']


def drawing(kind, cx, cy):
    out = []
    if kind == "through":
        out += sun(cx - 78, cy - 34)
        out += faceted(cx, cy - 6, 84)
        out += ray(cx - 64, cy - 22, cx + 70, cy + 14)
        out += eye(cx + 82, cy + 20)
    elif kind == "lustre":
        out += sun(cx - 78, cy - 34)
        out += faceted(cx, cy + 6, 84)
        out += ray(cx - 64, cy - 24, cx - 10, cy - 12, head=False)
        out += ray(cx - 10, cy - 12, cx + 66, cy - 36)
        out += eye(cx + 80, cy - 40)
    elif kind == "disperse":
        out += sun(cx - 78, cy - 34)
        out += faceted(cx - 8, cy - 4, 80)
        out += ray(cx - 64, cy - 22, cx - 8, cy - 6, colour="#9a8f7a", head=False)
        for k, c in enumerate(SPECTRUM):
            out += ray(cx + 20, cy + 2, cx + 86, cy - 22 + k * 10, colour=c, width=2, head=False)
    elif kind == "star":
        r = 40
        out += sun(cx - 78, cy - 34)
        out.append(f'<radialGradient id="starfill" cx="0.45" cy="0.4" r="0.7"><stop offset="0" '
                   f'stop-color="#4f78c9"/><stop offset="1" stop-color="{STAR_BLUE}"/></radialGradient>')
        out.append(f'<circle cx="{cx + 10}" cy="{cy}" r="{r}" fill="url(#starfill)" stroke="{INK}" stroke-width="1.4"/>')
        # Three sets of needles, sixty degrees apart, each throwing back one arm of the star.
        for k in range(3):
            a = math.radians(k * 60)
            for off in (-18, -6, 6, 18):
                px, py = -math.sin(a) * off, math.cos(a) * off
                out.append(f'<path d="M{cx + 10 + px - math.cos(a) * 9:.1f} {cy + py - math.sin(a) * 9:.1f} '
                           f'L{cx + 10 + px + math.cos(a) * 9:.1f} {cy + py + math.sin(a) * 9:.1f}" '
                           f'stroke="#9fb6e6" stroke-width="0.8" opacity="0.6"/>')
            out.append(f'<path d="M{cx + 10 - math.sin(a) * (r - 4):.1f} {cy + math.cos(a) * (r - 4):.1f} '
                       f'L{cx + 10 + math.sin(a) * (r - 4):.1f} {cy - math.cos(a) * (r - 4):.1f}" '
                       f'stroke="#ffffff" stroke-width="2.2" opacity="0.9" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx + 10}" cy="{cy}" r="4" fill="#ffffff"/>')
    elif kind == "split":
        out += sun(cx - 78, cy - 34)
        out += faceted(cx - 8, cy - 4, 80)
        out += ray(cx - 64, cy - 22, cx - 10, cy - 6, head=False)
        out += ray(cx - 10, cy - 6, cx + 74, cy - 18, colour=SPLIT_A)
        out += ray(cx - 10, cy - 6, cx + 74, cy + 16, colour=SPLIT_B)
        out.append(f'<circle cx="{cx + 88}" cy="{cy - 20}" r="7" fill="{SPLIT_A}" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<circle cx="{cx + 88}" cy="{cy + 18}" r="7" fill="{SPLIT_B}" stroke="{INK}" stroke-width="1"/>')
    return out


def light_plate():
    body = heading("What a stone does with light", "Five ways a gem shows a light it does not make")
    y = 116
    rh, gap = 128, 12
    for i, (name, what, scripture, witness, stones, kind, attested) in enumerate(LIGHT_ROWS):
        dash = "" if attested else ' stroke-dasharray="6 4"'
        out_y = y + i * (rh + gap)
        body.append(f'<rect x="28" y="{out_y}" width="{W - 56}" height="{rh}" rx="6" fill="{CARD}" '
                    f'stroke="{INK}" stroke-width="1.4"{dash}/>')
        body += drawing(kind, 140, out_y + rh / 2 + 4)
        tx = 262
        body.append(text(tx, out_y + 26, f"{i + 1}. {name.upper()}", 15, weight="bold", spacing="1"))
        body.append(text(W - 40, out_y + 26, LIGHT_TERMS[i], 12, "end", fill=MUTED, italic=True))
        body.append(text(tx, out_y + 47, what, 13.5))
        body.append(text(tx, out_y + 70, scripture, 12.5, italic=True))
        body.append(text(tx, out_y + 91, witness, 12.5, fill=MUTED))
        body.append(text(tx, out_y + 112, stones, 12.5, fill=MUTED))
    y = y + len(LIGHT_ROWS) * (rh + gap) + 6
    body.append(f'<rect x="38" y="{y}" width="22" height="14" rx="3" fill="{CARD}" stroke="{INK}" stroke-width="1.2"/>')
    body.append(text(68, y + 12, "Seen and described before modern optics", 12.5))
    body.append(f'<rect x="360" y="{y}" width="22" height="14" rx="3" fill="{CARD}" stroke="{INK}" '
                f'stroke-width="1.2" stroke-dasharray="6 4"/>')
    body.append(text(390, y + 12, "Known only to modern mineralogy", 12.5))
    y += 48
    body.append(text(W / 2, y, "In every case the light comes from outside the stone.", 15, "middle", "bold"))
    body.append(text(W / 2, y + 26, "“having the glory of God, its radiance like a most rare jewel,", 15,
                     "middle", italic=True))
    body.append(text(W / 2, y + 46, "like a jasper, clear as crystal”", 15, "middle", italic=True))
    body.append(text(W / 2, y + 66, "Revelation 21:11 (ESV)", 12.5, "middle", fill=MUTED))
    h = y + 104
    desc = ("A drawn plate of five panels, each showing a light ray from the sun meeting a stone. "
            + " ".join(f"{i + 1}. {r[0]} ({LIGHT_TERMS[i]}): {r[1]} Scripture: {r[2]} {r[3]}. Stones: {r[4]}."
                       for i, r in enumerate(LIGHT_ROWS))
            + " The double refraction panel is drawn dashed because no ancient writer described it. "
            "The plate closes: in every case the light comes from outside the stone, with Revelation 21:11.")
    out = svg_open(h, "What a stone does with light", desc)
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# The ephod plates: how the high priest wore the stones, and the names on them.
LINEN = "#f3eee0"
LINEN_EDGE = "#b9ad90"
TEKHELET = "#2c4f8c"      # "blue" yarn (Exodus 28:6)
TEKHELET_EDGE = "#1c3463"
ARGAMAN = "#6b3b78"       # purple
SCARLET = "#a8322c"
SKIN = "#c39a72"
SKIN_EDGE = "#8a6440"
LIGHT_BLUE = "#7f9fd6"
DASH = ' stroke-dasharray="5 4"'

# The orders each tradition puts the tribes in (Exodus 28:21 names none). Birth order: Josephus,
# Antiquities 3.169; Targum Pseudo-Jonathan and Rashi on Exodus 28:17-21. Leah's six first:
# Numbers Rabbah 2:7; Exodus Rabbah 38:8 has the same order with Naphtali and Gad swapped.
BIRTH = ["Reuben", "Simeon", "Levi", "Judah", "Dan", "Naphtali", "Gad", "Asher", "Issachar",
         "Zebulun", "Joseph", "Benjamin"]
NUM_RABBAH = ["Reuben", "Simeon", "Levi", "Judah", "Issachar", "Zebulun", "Dan", "Gad", "Naphtali",
              "Asher", "Joseph", "Benjamin"]
EX_RABBAH = ["Reuben", "Simeon", "Levi", "Judah", "Issachar", "Zebulun", "Dan", "Naphtali", "Gad",
             "Asher", "Joseph", "Benjamin"]
TRIBE_HE = {"Reuben": "רְאוּבֵן", "Simeon": "שִׁמְעוֹן", "Levi": "לֵוִי", "Judah": "יְהוּדָה",
            "Dan": "דָּן", "Naphtali": "נַפְתָּלִי", "Gad": "גָּד", "Asher": "אָשֵׁר",
            "Issachar": "יִשָּׂשכָר", "Zebulun": "זְבוּלֻן", "Joseph": "יוֹסֵף",
            "Benjamin": "בִּנְיָמִין"}
# Rashi on Exodus 28:10: the first six born on one stone, the rest on the other, Benjamin spelled
# in full as at Genesis 35:18, which gives twenty-five letters on each (Sotah 36a).
SHOULDERS = [BIRTH[:6], BIRTH[6:]]


def consonants(s):
    return "".join(c for c in s if "א" <= c <= "ת")


def wrap(x, y, s, width, size=12.5, lead=1.38, **kw):
    """Lines of text no wider than `width`, estimated from the serif's average glyph width."""
    per = max(8, int(width / (size * 0.47)))
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > per:
            lines.append(cur)
            cur = w_
        else:
            cur = f"{cur} {w_}".strip()
    if cur:
        lines.append(cur)
    return [text(x, y + i * size * lead, ln, size, **kw) for i, ln in enumerate(lines)], len(lines) * size * lead


def weave_defs():
    """The ephod's cloth: gold, blue, purple and scarlet worked into fine linen (Exodus 28:6)."""
    return ['<defs>'
            f'<pattern id="weave" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
            f'<rect width="12" height="12" fill="{LINEN}"/><rect width="2.4" height="12" fill="{GOLD}"/>'
            f'<rect x="3" width="2.4" height="12" fill="{TEKHELET}"/><rect x="6" width="2.4" height="12" fill="{ARGAMAN}"/>'
            f'<rect x="9" width="2.4" height="12" fill="{SCARLET}"/></pattern>'
            f'<pattern id="checker" width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="{LINEN}"/>'
            f'<path d="M0 3.5 H7 M3.5 0 V7" stroke="{LINEN_EDGE}" stroke-width="0.6" opacity="0.7"/></pattern>'
            '</defs>']


def chain(x1, y1, x2, y2, width=2.6):
    """Gold chain "twisted like cords" (Exodus 28:14): two strands, one offset over the other."""
    d = f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}"
    return [f'<path d="{d}" stroke="{GOLD_EDGE}" stroke-width="{width + 1.4}" stroke-linecap="round"/>',
            f'<path d="{d}" stroke="{GOLD}" stroke-width="{width}" stroke-dasharray="3 2" stroke-linecap="round"/>']


def onyx(cx, cy, rx, ry, band=True):
    """A shoulder stone in its gold filigree setting (Exodus 28:11)."""
    if not band:
        return [f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 18}" ry="{ry + 16}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>',
                f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{ONYX}" stroke="{INK}" stroke-width="0.8"/>']
    return [f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + rx * 0.28:.1f}" ry="{ry + ry * 0.32:.1f}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.2"/>',
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{ONYX}" stroke="{INK}" stroke-width="0.8"/>',
            f'<path d="M{cx - rx * 0.8:.1f} {cy + ry * 0.15:.1f} Q{cx:.1f} {cy - ry * 0.35:.1f} {cx + rx * 0.8:.1f} {cy + ry * 0.15:.1f}" '
            f'stroke="#f5efe2" stroke-width="{max(1.0, ry / 6):.1f}" fill="none" opacity="0.7"/>']


def callout(n, x, y, tx, ty, dashed=False):
    dash = ' stroke-dasharray="3 3"' if dashed else ""
    return [f'<path d="M{x} {y} L{tx} {ty}" stroke="{INK}" stroke-width="0.9"{dash}/>',
            f'<circle cx="{tx}" cy="{ty}" r="2" fill="{INK}"/>',
            f'<circle cx="{x}" cy="{y}" r="11" fill="{CARD}" stroke="{INK}" stroke-width="1.3"/>',
            text(x, y + 4.5, str(n), 13, "middle", "bold")]


def priest(cx):
    """The high priest from the front, dressed in the order of Leviticus 8:7-9. No face is drawn."""
    o = []
    # The ephod's body: its shape is not stated. Rashi's apron hangs behind him to the heels.
    o.append(f'<path d="M{cx - 92} 362 L{cx - 98} 640 L{cx + 98} 640 L{cx + 92} 362 Z" fill="url(#weave)" '
             f'fill-opacity="0.45" stroke="{INK}" stroke-width="1.2"{DASH}/>')
    # The coat, checker work of fine linen, to the feet.
    o.append(f'<path d="M{cx - 50} 540 L{cx - 58} 655 L{cx + 58} 655 L{cx + 50} 540 Z" fill="url(#checker)" '
             f'stroke="{LINEN_EDGE}" stroke-width="1.2"/>')
    # The robe of the ephod, all blue, with an opening for the head (Exodus 28:31-32).
    o.append(f'<path d="M{cx - 20} 204 L{cx - 65} 218 Q{cx - 80} 240 {cx - 78} 300 L{cx - 88} 548 L{cx + 88} 548 '
             f'L{cx + 78} 300 Q{cx + 80} 240 {cx + 65} 218 L{cx + 20} 204 Z" fill="{TEKHELET}" stroke="{TEKHELET_EDGE}" stroke-width="1.4"/>')
    # Pomegranates of blue, purple and scarlet, with gold bells between them (28:33-34).
    for k, x in enumerate(range(cx - 82, cx + 83, 12)):
        if k % 2:
            o.append(f'<path d="M{x - 3.5} 550 L{x + 3.5} 550 L{x + 5} 560 L{x - 5} 560 Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="0.8"/>')
            o.append(f'<circle cx="{x}" cy="561.5" r="1.4" fill="{GOLD_EDGE}"/>')
        else:
            fill = [LIGHT_BLUE, ARGAMAN, SCARLET][(k // 2) % 3]
            o.append(f'<circle cx="{x}" cy="555" r="4.6" fill="{fill}" stroke="{INK}" stroke-width="0.6"/>')
            o.append(f'<path d="M{x - 2} 550 L{x} 548 L{x + 2} 550" stroke="{INK}" stroke-width="0.7" fill="none"/>')
    # Sleeves of the coat, and hands.
    for s in (-1, 1):
        d = f"M{cx + s * 64} 224 Q{cx + s * 86} 300 {cx + s * 92} 408"
        o.append(f'<path d="{d}" stroke="{LINEN_EDGE}" stroke-width="23" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="{d}" stroke="url(#checker)" stroke-width="20.5" fill="none" stroke-linecap="round"/>')
        o.append(f'<circle cx="{cx + s * 93}" cy="420" r="9" fill="{SKIN}" stroke="{SKIN_EDGE}" stroke-width="0.8"/>')
    # The woven binding round the robe's neck (28:32), the neck and the head, with no face.
    o.append(f'<rect x="{cx - 8}" y="190" width="16" height="16" fill="{SKIN}"/>')
    o.append(f'<ellipse cx="{cx}" cy="206" rx="21" ry="6" fill="none" stroke="{TEKHELET_EDGE}" stroke-width="3"/>')
    o.append(f'<circle cx="{cx}" cy="172" r="23" fill="{SKIN}" stroke="{SKIN_EDGE}" stroke-width="1"/>')
    # The turban of fine linen, with the gold plate on a blue cord at the front (28:36-39).
    o.append(f'<path d="M{cx - 27} 166 Q{cx - 31} 126 {cx} 122 Q{cx + 31} 126 {cx + 27} 166 Q{cx} 157 {cx - 27} 166 Z" '
             f'fill="{LINEN}" stroke="{LINEN_EDGE}" stroke-width="1.2"/>')
    for k in range(3):
        o.append(f'<path d="M{cx - 26} {158 - k * 10} Q{cx} {148 - k * 10} {cx + 26} {158 - k * 10}" stroke="{LINEN_EDGE}" stroke-width="0.8" fill="none"/>')
    o.append(f'<path d="M{cx - 27} 150 Q{cx} 140 {cx + 27} 150" stroke="{TEKHELET}" stroke-width="1.6" fill="none"/>')
    o.append(f'<rect x="{cx - 12}" y="141" width="24" height="9" rx="1.5" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="0.9"/>')
    # The shoulder pieces and the woven band, of one piece with the ephod (28:7-8).
    for s in (-1, 1):
        x0 = cx + s * 50 - 8
        o.append(f'<path d="M{x0} 206 H{x0 + 16} V362 H{x0} Z" fill="url(#weave)" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<rect x="{cx - 92}" y="352" width="184" height="18" fill="url(#weave)" stroke="{INK}" stroke-width="1"/>')
    # The breastpiece, a span square, resting on the band (28:16, 28).
    bx, by, bs = cx - 36, 278, 72
    o.append(f'<rect x="{bx}" y="{by}" width="{bs}" height="{bs}" fill="url(#weave)" stroke="{GOLD_EDGE}" stroke-width="2"/>')
    o.append(f'<rect x="{bx + 4}" y="{by + 4}" width="{bs - 8}" height="{bs - 8}" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="0.8"/>')
    for i, b in enumerate(BREASTPIECE):
        sx, sy = bx + 14 + (i % 3) * 22, by + 12.5 + (i // 3) * 15.5
        o.append(f'<circle cx="{sx}" cy="{sy}" r="6.2" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="0.6"/>')
        o.append(f'<circle cx="{sx}" cy="{sy}" r="4.6" fill="{b[4]}"/>')
    # Shoulder stones, the chains up to their settings, and the blue lace at the foot (28:9-14, 22-28).
    for s in (-1, 1):
        o += chain(cx + s * 33, by + 3, cx + s * 50, 222, 1.8)
        o += onyx(cx + s * 50, 212, 9, 6.5)
        o.append(f'<path d="M{cx + s * 33} {by + bs - 3} L{cx + s * 44} {by + bs + 1}" stroke="{TEKHELET}" stroke-width="2.6" stroke-linecap="round"/>')
    return o


DRESSING = [
    ("The coat", "Fine linen, woven in checker work (Exodus 28:39). Put on first (Leviticus 8:7)."),
    ("The sash", "Embroidered (28:39), tied round the coat (Leviticus 8:7). The robe covers it."),
    ("The robe of the ephod", "All of blue, with an opening for the head; pomegranates and gold bells round the hem, “its sound shall be heard” (28:31-35). Its length is not stated."),
    ("The ephod", "Gold, blue, purple and scarlet in fine linen (28:6): two shoulder pieces and a woven band of one piece with it, tied round him (28:7-8; Leviticus 8:7). The body’s shape is not stated: Rashi makes it an apron worn behind, to the heels (on 28:6); Josephus a short sleeved coat (Antiquities 3.162)."),
    ("Two onyx stones", "On the shoulder pieces, six names on each, in birth order: “stones of remembrance” (28:9-12)."),
    ("The breastpiece of judgment", "A span square, doubled; twelve stones in four rows (28:15-21). It hangs from the shoulder stones’ settings by gold chains and is tied to the ephod with blue lace (28:22-28). The Urim and Thummim go in it (28:30)."),
    ("The turban and the plate", "Fine linen; on its front a gold plate engraved “Holy to the LORD”, on a blue cord (28:36-39). Put on last (Leviticus 8:9)."),
]


def hanging(y0):
    """The breastpiece at one span, with the rings, chains and lace of Exodus 28:22-28."""
    o = []
    left, right, top, span = 110, 330, y0 + 70, 220
    band = top + span + 34
    for x in (74, 366):
        o.append(f'<path d="M{x - 12} {y0 + 20} H{x + 12} V{band} H{x - 12} Z" fill="url(#weave)" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<rect x="44" y="{band}" width="352" height="22" fill="url(#weave)" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<rect x="{left}" y="{top}" width="{span}" height="{span}" fill="url(#weave)" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    o.append(f'<rect x="{left + 8}" y="{top + 8}" width="{span - 16}" height="{span - 16}" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="1"/>')
    for i, b in enumerate(BREASTPIECE):
        sx, sy = left + 42 + (i % 3) * 68, top + 34 + (i // 3) * 51
        o.append(f'<ellipse cx="{sx}" cy="{sy}" rx="25" ry="20" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1"/>')
        o += swatch(sx, sy, 16, b[4], b[5], b[6], f"hang{i + 1}")
    rings = []
    for s, sx, ex in ((-1, left + 8, 74), (1, right - 8, 366)):
        o += chain(sx, top + 6, ex, y0 + 46, 3)
        o += onyx(ex, y0 + 32, 19, 13)
        o.append(f'<circle cx="{sx}" cy="{top + 6}" r="5.5" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.2"/>')
        # The lower rings are on the inside edge, toward the ephod, so drawn as if seen through.
        o.append(f'<circle cx="{sx}" cy="{top + span - 8}" r="5.5" fill="none" stroke="{GOLD_EDGE}" stroke-width="2"{DASH}/>')
        o.append(f'<circle cx="{ex - s * 6}" cy="{band - 9}" r="5.5" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.2"/>')
        o.append(f'<path d="M{sx} {top + span - 8} L{ex - s * 6} {band - 9}" stroke="{TEKHELET}" stroke-width="3.4" stroke-linecap="round"/>')
        rings.append((sx, ex))
    labels = [("A", left + 8, top + 6, -1), ("B", 92, y0 + 58, -1), ("C", left + 8, top + span - 8, -1),
              ("D", 80, band - 9, -1), ("E", right + 10, top + span + 8, 1)]
    for lab, x, y, _ in labels:
        o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{INK}"/>')
        o.append(text(x, y + 4, lab, 11.5, "middle", "bold", fill=CARD))
    # One span, the breastpiece's side (Exodus 28:16).
    sy = band + 52
    o.append(f'<path d="M{left} {sy} H{right} M{left} {sy - 6} V{sy + 6} M{right} {sy - 6} V{sy + 6}" stroke="{INK}" stroke-width="1.4"/>')
    path, _ = place("זֶרֶת", (left + right) / 2 + 52, sy - 7, 15, anchor="end", fill=INK)
    o.append(path)
    o.append(text((left + right) / 2 + 58, sy - 8, "zeret, one span (28:16)", 12.5, italic=True))
    o.append(text((left + right) / 2, sy + 20, "not stated in cm: about 22, if a span is half a cubit of 44.5 cm", 12,
                  "middle", fill=MUTED, italic=True))
    return o, sy + 30 - y0


HANGING_KEY = [
    ("A", "Two gold rings on the breastpiece’s top corners (28:23)."),
    ("B", "Two chains of pure gold, twisted like cords, from those rings to the settings of the shoulder stones (28:14, 24-25). The breastpiece hangs from the stones that carry the names."),
    ("C", "Two more rings on its lower corners, on the inside edge next to the ephod (28:26)."),
    ("D", "Two rings on the shoulder pieces, low in front, just above the woven band (28:27)."),
    ("E", "A lace of blue ties C to D, “so that it may lie on the skillfully woven band of the ephod, so that the breastpiece shall not come loose” (28:28, ESV)."),
]


def ephod_plate():
    body = weave_defs()
    body += heading("How the stones were worn", "Exodus 28:4-39, dressed in the order of Leviticus 8:7-9")
    cx = 200
    body += priest(cx)
    # Callouts, numbered in the order he was dressed.
    body += callout(1, 52, 615, cx - 54, 615)
    body += callout(2, 52, 392, cx - 76, 392, dashed=True)
    body += callout(3, 52, 520, cx - 84, 520)
    body += callout(4, 348, 362, cx + 92, 362)
    body += callout(5, 348, 205, cx + 60, 212)
    body += callout(6, 348, 300, cx + 36, 300)
    body += callout(7, 348, 140, cx + 20, 140)
    body.append(text(cx + 102, 610, "ephod’s body:", 11.5, "start", fill=MUTED, italic=True))
    body.append(text(cx + 102, 624, "shape not stated", 11.5, "start", fill=MUTED, italic=True))
    y = 120
    for n, (name, note) in enumerate(DRESSING, 1):
        body.append(f'<circle cx="392" cy="{y - 4}" r="9" fill="{CARD}" stroke="{INK}" stroke-width="1.2"/>')
        body.append(text(392, y + 0.5, str(n), 11.5, "middle", "bold"))
        body.append(text(408, y, name, 13.5, weight="bold"))
        lines, h = wrap(408, y + 17, note, 286, 12)
        body += lines
        y += 17 + h + 12
    y = max(y, 676) + 16
    body += banner(W / 2, y, 470, "HOW THE BREASTPIECE HANGS · EXODUS 28:22-28", size=13)
    hang, hh = hanging(y + 40)
    body += hang
    ky = y + 66
    for lab, note in HANGING_KEY:
        body.append(f'<circle cx="430" cy="{ky - 4}" r="9" fill="{INK}"/>')
        body.append(text(430, ky + 0.5, lab, 11.5, "middle", "bold", fill=CARD))
        lines, h = wrap(446, ky, note, 248, 12)
        body += lines
        ky += h + 10
    y = max(y + 40 + hh, ky) + 26
    # "Square and doubled" (28:16): folded, it makes a pocket, and the Urim and Thummim go in it (28:30).
    body.append(text(40, y, "“Square and doubled” (28:16)", 14, weight="bold"))
    fx = 60
    body.append(f'<rect x="{fx}" y="{y + 16}" width="50" height="100" fill="url(#weave)" fill-opacity="0.6" stroke="{INK}" stroke-width="1.2"{DASH}/>')
    body.append(f'<path d="M{fx} {y + 66} H{fx + 50}" stroke="{INK}" stroke-width="0.9" stroke-dasharray="2 3"/>')
    body.append(f'<path d="M{fx + 66} {y + 66} H{fx + 104}" stroke="{INK}" stroke-width="1.4"/>')
    body.append(arrow_head(fx + 108, y + 66, 0, 9))
    body.append(f'<rect x="{fx + 120}" y="{y + 41}" width="50" height="50" fill="url(#weave)" stroke="{GOLD_EDGE}" stroke-width="2"/>')
    # Side section: two layers joined at the fold, open at the top, with the Urim and Thummim inside.
    sx = fx + 214
    body.append(f'<path d="M{sx} {y + 40} V{y + 88} Q{sx + 9} {y + 98} {sx + 18} {y + 88} V{y + 40}" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.4"/>')
    body.append(f'<rect x="{sx + 5}" y="{y + 66}" width="8" height="10" rx="2" fill="{INK}" opacity="0.65"{DASH}/>')
    body.append(f'<rect x="{sx + 5}" y="{y + 52}" width="8" height="10" rx="2" fill="none" stroke="{INK}" stroke-width="1"{DASH}/>')
    body.append(text(sx + 9, y + 116, "side view", 11, "middle", fill=MUTED, italic=True))
    note = ("If “doubled” means folded, the breastpiece is a pocket, and the Urim and Thummim are put “in the "
            "breastpiece” (28:30). Rashi puts them “between the folds” (on 28:30). The text does not say what they "
            "were, so the drawing of them is a guess, and so is the fold.")
    lines, h = wrap(sx + 46, y + 30, note, W - sx - 46 - 34, 12)
    body += lines
    y += max(126, 30 + h) + 24
    body.append(f'<rect x="40" y="{y - 11}" width="22" height="14" rx="3" fill="{CARD}" stroke="{INK}" stroke-width="1.2"/>')
    body.append(text(70, y, "Stated in Exodus 28 and Leviticus 8", 12.5))
    body.append(f'<rect x="330" y="{y - 11}" width="22" height="14" rx="3" fill="{CARD}" stroke="{INK}" stroke-width="1.2"{DASH}/>')
    body.append(text(360, y, "Not stated: a tradition named, or a guess", 12.5))
    y += 22
    body.append(text(40, y, "Stone colours as on the plate of the three lists; their sizes are not stated. Four rows in a span", 12, fill=MUTED, italic=True))
    body.append(text(40, y + 16, "leave each row at most about 5.5 cm, setting included.", 12, fill=MUTED, italic=True))
    y += 54
    body.append(text(W / 2, y, "“So Aaron shall bear the names of the sons of Israel in the breastpiece of", 15, "middle", italic=True))
    body.append(text(W / 2, y + 20, "judgment on his heart, when he goes into the Holy Place …”", 15, "middle", italic=True))
    body.append(text(W / 2, y + 40, "Exodus 28:29 (ESV)", 12.5, "middle", fill=MUTED))
    h = y + 78
    desc = ("A drawn plate of the high priest from the front, without a face, wearing the garments of Exodus 28 "
            "numbered in the order Leviticus 8:7-9 puts them on: "
            + " ".join(f"{n}. {name}: {note}" for n, (name, note) in enumerate(DRESSING, 1))
            + " Below, how the breastpiece hangs, drawn at one span square with its twelve stones: "
            + " ".join(f"{lab}. {note}" for lab, note in HANGING_KEY)
            + " A scale bar marks one span, about 22 cm if a span is half a cubit of 44.5 cm. A small diagram shows "
            "a cloth two spans long folded to one span square, making a pocket for the Urim and Thummim, marked as "
            "a guess: the text says only that it was doubled and that they were put in it. Solid lines are what "
            "the text states; dashed lines are a tradition or a guess. The plate closes with Exodus 28:29.")
    out = svg_open(h, "How the stones were worn", desc)
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# Echoes between a stone's name and its tribe. None is drawn by the text; each says which order it
# needs, because an echo that holds only in one tradition's order is weaker than one that holds in all.
ECHOES = [
    ("Dan", 7, "only where Leah’s six come first",
     "The seventh stone’s name is the name of the city Dan took: they “fought against Leshem, captured it … and "
     "renamed it after their father Dan” (Joshua 19:47, BSB). The same word appears only there and at Exodus "
     "28:19 and 39:12. Numbers and Exodus Rabbah put Dan on it; birth order puts Gad there."),
    ("Joseph", 11, "every order",
     "Joseph’s stone is the stone of the two shoulder pieces, the ones that carry all twelve names (28:9, 20), and "
     "“the birthright belonged to Joseph” (1 Chronicles 5:2, ESV). In the Hebrew only: the Greek has emerald on the "
     "shoulders and beryl for the eleventh stone."),
    ("Levi", 3, "every order",
     "bareqet is “the flashing one”, from baraq, lightning. Moses gives the Urim, probably “lights”, to "
     "Levi (Deuteronomy 33:8), and Numbers Rabbah paints the Urim and Thummim on Levi’s banner. An echo of sense "
     "and nothing more."),
    ("Benjamin", 12, "every order",
     "Of Benjamin: the LORD “dwells between his shoulders” (Deuteronomy 33:12, ESV), and Benjamin’s stone hung "
     "between the priest’s. Jerusalem lay in Benjamin’s lot (Joshua 18:28). yashpeh is the word Greek writes "
     "iaspis, jasper, the city’s first foundation (Revelation 21:19), though the Septuagint renders it onychion here."),
    ("Reuben", 1, "every order",
     "The first stone is “the red one”, from ʾadom, red. Numbers Rabbah dyes Reuben’s banner red and "
     "paints on it the mandrakes he found (Genesis 30:14). A colour, no more."),
]
ALEPH_BET = "אבגדהוזחטיכלמנסעפצקרשת"
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}


def letters_used(words):
    return {FINALS.get(c, c) for w_ in words for c in consonants(w_)}


def shoulder_stone(cx, cy, names, side):
    o = onyx(cx, cy, 120, 78, band=False)
    for k, name in enumerate(names):
        y = cy - 50 + k * 20
        o.append(text(cx - 82, y + 5, name, 13, fill="#f5efe2"))
        path, _ = place(consonants(TRIBE_HE[name] if name != "Benjamin" else "בנימין"), cx + 80, y + 7, 16,
                        anchor="end", fill="#f5efe2")
        o.append(path)
    count = sum(len(consonants(TRIBE_HE[n])) for n in names if n != "Benjamin") + (6 if "Benjamin" in names else 0)
    o.append(text(cx, cy - 104, f"His {side} shoulder", 14, "middle", "bold"))
    o.append(text(cx, cy + 112, f"{count} letters", 12.5, "middle", fill=MUTED, italic=True))
    return o, count


def names_plate():
    body = weave_defs()
    body += heading("Twelve names, twice", "On his shoulders and on his heart · Exodus 28:9-30")
    y = 128
    lines, h = wrap(40, y, "Each shoulder stone carries six names “in the order of their birth” (Exodus 28:10). The "
                    "breastpiece carries one name on each stone and does not say which (28:21). Both are “for "
                    "remembrance before the LORD” (28:12, 29).", W - 80, 13)
    body += lines
    y += h + 120
    counts = []
    for cx, names, side in ((192, SHOULDERS[0], "right"), (528, SHOULDERS[1], "left")):
        o, n = shoulder_stone(cx, y, names, side)
        body += o
        counts.append(n)
    stones_y = y
    y += 150
    shoulder_note = ("As the priest faces you, his right shoulder is on your left. Elder sons on the right: "
                    "Josephus (Antiquities 3.166). Six and six in birth order with Benjamin spelled in full, as at "
                    "Genesis 35:18: Rashi on 28:10, which gives "
                    f"{counts[0]} and {counts[1]} letters; the Talmud records a view that set Judah first on one stone "
                    "(Sotah 36a). The stone is onyx in the Hebrew, emerald in the Greek, sardonyx in Josephus. Letters "
                    "drawn in square script without vowels; the engravers used the older Hebrew letters.")

    # The breastpiece hangs from the shoulder stones' settings (28:25): chains run down to it.
    gy = y + 20
    cw, ch, gap = 192, 112, 9
    gx = (W - 3 * cw - 2 * gap) / 2
    for s, cx in ((-1, 192), (1, 528)):
        body += chain(cx + s * 60, stones_y + 80, gx + (8 if s < 0 else 3 * cw + 2 * gap - 8), gy - 2, 3)
    body.append(text(W / 2, y - 4, "gold chains: the breastpiece hangs from the shoulder stones’ settings (28:25)",
                     12, "middle", fill=MUTED, italic=True))
    gh = 4 * ch + 3 * gap
    body.append(f'<rect x="{gx - 10:.1f}" y="{gy - 10}" width="{3 * cw + 2 * gap + 20:.1f}" height="{gh + 20}" rx="8" '
                f'fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>')
    for i, (he, tr, gr, en, colour, pattern, uncertain) in enumerate(BREASTPIECE):
        x, cy = gx + (i % 3) * (cw + gap), gy + (i // 3) * (ch + gap)
        agree = BIRTH[i] == NUM_RABBAH[i] == EX_RABBAH[i]
        body.append(f'<rect x="{x:.1f}" y="{cy:.1f}" width="{cw}" height="{ch}" rx="5" fill="{CARD}" '
                    f'stroke="{GOLD_EDGE}" stroke-width="1.3"{"" if agree else DASH}/>')
        body += swatch(x + 24, cy + 27, 15, colour, pattern, uncertain, f"nm{i + 1}")
        body.append(text(x + 24, cy + 58, str(i + 1), 11.5, "middle", "bold", fill=MUTED))
        path, _ = place(he, x + cw - 10, cy + 27, 19, anchor="end", fill=INK)
        body.append(path)
        body.append(text(x + 48, cy + 25, tr, 13, italic=True))
        if agree:
            body.append(text(x + 48, cy + 62, BIRTH[i], 15, weight="bold"))
            path, _ = place(TRIBE_HE[BIRTH[i]], x + cw - 10, cy + 64, 16, anchor="end", fill=INK)
            body.append(path)
            body.append(text(x + 48, cy + 82, "every tradition", 11.5, fill=MUTED, italic=True))
        else:
            rows = [("Birth order", BIRTH[i])]
            if NUM_RABBAH[i] == EX_RABBAH[i]:
                rows.append(("Rabbah", NUM_RABBAH[i]))
            else:
                rows += [("Num. R.", NUM_RABBAH[i]), ("Ex. R.", EX_RABBAH[i])]
            for k, (who, name) in enumerate(rows):
                body.append(text(x + 48, cy + 58 + k * 17, f"{who}:", 11.5, fill=MUTED, italic=True))
                body.append(text(x + cw - 12, cy + 58 + k * 17, name, 13, "end", weight="bold"))
    y = gy + gh + 34
    lines, h = wrap(40, y, shoulder_note, W - 80, 12, fill=MUTED, italic=True)
    body += lines
    y += h + 10
    lines, h = wrap(40, y, "Birth order: Josephus (Antiquities 3.169), Targum Pseudo-Jonathan and Rashi on 28:17-21. "
                    "Leah’s six first (“Rabbah”): Numbers Rabbah 2:7 and Exodus Rabbah 38:8, which swap Naphtali and Gad (“Num. R.”, “Ex. R.”). Every "
                    "tradition agrees on stones 1-4 and 11-12. Which end of a row came first is not stated either; a "
                    "Hebrew reader would begin at the right.", W - 80, 12, fill=MUTED, italic=True)
    body += lines
    y += h + 24
    body.append(f'<rect x="40" y="{y - 11}" width="22" height="14" rx="3" fill="{CARD}" stroke="{GOLD_EDGE}" stroke-width="1.3"/>')
    body.append(text(70, y, "Every tradition puts the same tribe here", 12.5))
    body.append(f'<rect x="372" y="{y - 11}" width="22" height="14" rx="3" fill="{CARD}" stroke="{GOLD_EDGE}" stroke-width="1.3"{DASH}/>')
    body.append(text(402, y, "The traditions divide", 12.5))
    y += 38
    body += banner(W / 2, y, 420, "WHERE A NAME AND A STONE ECHO", size=13)
    y += 48
    for tribe, pos, holds, note in ECHOES:
        he, tr = BREASTPIECE[pos - 1][:2]
        lines, h = wrap(54, y + 44, note, W - 118, 12)
        box_h = 44 + h
        body.append(f'<rect x="40" y="{y}" width="{W - 80}" height="{box_h:.0f}" rx="5" fill="{CARD}" '
                    f'stroke="{INK}" stroke-width="1.2"{DASH}/>')
        body.append(text(54, y + 24, f"{tribe} · stone {pos}, {tr}", 14.5, weight="bold"))
        path, _ = place(he, 54 + len(f"{tribe} · stone {pos}, {tr}") * 7.6 + 12, y + 25, 18, anchor="start", fill=INK)
        body.append(path)
        body.append(text(W - 54, y + 24, holds, 12, "end", fill=MUTED, italic=True))
        body += lines
        y += box_h + 10
    lines, h = wrap(40, y + 14, "No echo turns up for Simeon or Judah, or for the six middle stones beyond the banners "
                    "Numbers Rabbah colours like each tribe’s stone. Scripture draws none of these lines; they are "
                    "noticed, and marked as such.", W - 80, 12, fill=MUTED, italic=True)
    body += lines
    y += h + 44
    # The letters: the twelve names leave four of the twenty-two out.
    used = letters_used(TRIBE_HE[n] for n in BIRTH)
    missing = [c for c in ALEPH_BET if c not in used]
    body += banner(W / 2, y, 300, "THE LETTERS ON THE STONES", size=13)
    y += 46
    bw = 27
    x0 = W / 2 + 11 * bw - bw / 2
    for k, c in enumerate(ALEPH_BET):
        x = x0 - k * bw
        gone = c in missing
        body.append(f'<rect x="{x - bw / 2 + 2:.1f}" y="{y}" width="{bw - 4}" height="30" rx="3" '
                    f'fill="{GOLD_TINT if gone else CARD}" stroke="{GOLD_EDGE if gone else INK}" stroke-width="1.1"{DASH if gone else ""}/>')
        path, _ = place(c, x, y + 22, 18, anchor="middle", fill=GOLD_EDGE if gone else INK)
        body.append(path)
    y += 54
    lines, h = wrap(40, y, f"The twelve names use {len(used)} of the 22 letters; the four in gold are missing. The "
                    "Talmud says “Abraham, Isaac and Jacob” and “the tribes of Jeshurun” were engraved there too, so that "
                    "every letter was present for the Urim and Thummim to answer through (Yoma 73b). A tradition, "
                    "and an exact one: those words supply all four.", W - 80, 12.5)
    body += lines
    y += h + 30
    body.append(text(W / 2, y, "“Aaron shall bear their names before the LORD on his two shoulders for remembrance.”",
                     14, "middle", italic=True))
    body.append(text(W / 2, y + 18, "Exodus 28:12 (ESV)", 12, "middle", fill=MUTED))
    body.append(text(W / 2, y + 44, "“So Aaron shall bear the names of the sons of Israel … on his heart.”", 14,
                     "middle", italic=True))
    body.append(text(W / 2, y + 62, "Exodus 28:29 (ESV)", 12, "middle", fill=MUTED))
    h = y + 100
    desc = ("A drawn plate of the names on the high priest's stones. Two onyx shoulder stones, his right shoulder "
            f"on the viewer's left, carry six names each in birth order: {', '.join(SHOULDERS[0])} "
            f"({counts[0]} letters), and {', '.join(SHOULDERS[1])} ({counts[1]} letters), following Rashi on Exodus "
            "28:10, with Josephus placing the elder sons on the right. Gold chains run down to the breastpiece, which "
            "hangs from the shoulder stones' settings (Exodus 28:25). The breastpiece's twelve stones are shown with "
            "the tribe each tradition puts on it: "
            + "; ".join(f"{i + 1}, {b[1]}: " + (BIRTH[i] if BIRTH[i] == NUM_RABBAH[i] == EX_RABBAH[i] else
                        f"birth order {BIRTH[i]}, Numbers Rabbah {NUM_RABBAH[i]}, Exodus Rabbah {EX_RABBAH[i]}")
                        for i, b in enumerate(BREASTPIECE))
            + ". Every tradition agrees on stones 1 to 4 and 11 to 12; Scripture names none. Five echoes between a "
            "stone and its tribe are set out, each marked with the order it needs: "
            + " ".join(f"{t}: {n}" for t, _, _, n in ECHOES)
            + f" Last, the 22 Hebrew letters, with the {len(missing)} the twelve names lack marked in gold; the Talmud "
            "says the patriarchs' names and 'the tribes of Jeshurun' were added, which supplies them (Yoma 73b). "
            "The plate closes with Exodus 28:12 and 28:29.")
    out = svg_open(h, "Twelve names, twice", desc)
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "three-lists.svg").write_text(plate(), encoding="utf-8")
    print("wrote three-lists.svg")
    (OUT / "light-in-stone.svg").write_text(light_plate(), encoding="utf-8")
    print("wrote light-in-stone.svg")
    (OUT / "ephod.svg").write_text(ephod_plate(), encoding="utf-8")
    print("wrote ephod.svg")
    (OUT / "names-on-the-stones.svg").write_text(names_plate(), encoding="utf-8")
    print("wrote names-on-the-stones.svg")


if __name__ == "__main__":
    main()
