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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "three-lists.svg").write_text(plate(), encoding="utf-8")
    print("wrote three-lists.svg")
    (OUT / "light-in-stone.svg").write_text(light_plate(), encoding="utf-8")
    print("wrote light-in-stone.svg")


if __name__ == "__main__":
    main()
