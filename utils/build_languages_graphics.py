"""Draw the charts for chronology/what-languages-declare.md in the Larkin hand (utils/lib/larkin.py).

    python3 utils/build_languages_graphics.py

Language figures come from docs/data/languages.json and the Masoretic dates from
docs/data/chronology.json, so a corrected count or date is one edit and a re-run. Solid is what a
source records or the arithmetic computes; dashed is a model date, a disputed reading, or the
Septuagint's alternative chronology.
"""

import json
import math
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, HALO, text, svg_open, heading, card, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "what-languages-declare"
DATA = json.loads((ROOT / "docs" / "data" / "languages.json").read_text(encoding="utf-8"))
CHRONOLOGY = json.loads((ROOT / "docs" / "data" / "chronology.json").read_text(encoding="utf-8"))

MT_CREATION_BC = 3959
# The population study's modelled dispersal, AM 1856, inside Peleg's lifetime.
BABEL_MODEL_AM = 1856
# Septuagint (Brenton) Flood and Peleg's lifetime, from combined-timeline.md's generated table:
# Peleg born 2652 BC and lived 339 years (Genesis 11:18-19 LXX).
LXX_FLOOD_BC = 3183
LXX_PELEG_BC = (2652, 2313)
PRESENT_AD = 2026


def marker(mid):
    for e in CHRONOLOGY["genesis_markers"]:
        if e["id"] == mid:
            return e
    raise SystemExit(f"chronology.json has no {mid} marker")


FLOOD_BC = MT_CREATION_BC - marker("flood")["am_year"]
babel = marker("babel")
PELEG_BC = (MT_CREATION_BC - babel["am_year"], MT_CREATION_BC - babel["am_end"])
BABEL_BC = MT_CREATION_BC - BABEL_MODEL_AM


def years_since(bc):
    return bc + PRESENT_AD


def note(x, y, lines, size=13, fill=INK, anchor="start", italic=False):
    return [text(x, y + i * (size + 4), ln, size, anchor, fill=fill, italic=italic)
            for i, ln in enumerate(lines)]


def lineages():
    sizes = DATA["lineage_sizes"]["all_family_sizes"]
    named = dict((n, s) for n, s in DATA["lineage_sizes"]["largest"])
    names_by_size = {}
    for n, s in DATA["lineage_sizes"]["largest"]:
        names_by_size.setdefault(s, []).append(n)
    isolates = DATA["world"]["isolates"]
    k = 58 / math.sqrt(max(sizes))

    def pack(radii, x0, x1, y0, gap=4):
        placed, x, y, row_h = [], x0, y0, 0
        for r in radii:
            if x + 2 * r > x1:
                x, y, row_h = x0, y + row_h + gap, 0
            placed.append((x + r, y + r, r))
            x += 2 * r + gap
            row_h = max(row_h, 2 * r)
        return placed, y + row_h

    # The named row holds as many of the largest families as fit across one line.
    big, run = [], 40
    for s in sizes:
        d = 2 * k * math.sqrt(s) + 22
        if run + d > W - 40 + 22:
            break
        big.append(s)
        run += d
    rest = sizes[len(big):]
    body = []
    y = 150
    placed, y = pack([k * math.sqrt(s) for s in big], 40, W - 40, y, gap=22)
    bottom = max(cy + r for _, cy, r in placed)
    used = {}
    for (cx, cy, r), s in zip(placed, big):
        name = names_by_size[s][used.get(s, 0)]
        used[s] = used.get(s, 0) + 1
        # Sit every circle on one baseline so the labels underneath line up.
        cy = bottom - r
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{GOLD_TINT}" '
                    f'stroke="{GOLD_EDGE}" stroke-width="1.4"/>')
        if r > 45:
            body.append(text(cx, cy - 2, name, 14, "middle", "bold"))
            body.append(text(cx, cy + 16, f"{named[name]:,}", 13, "middle", fill=MUTED))
            continue
        parts = name.replace("Nuclear Trans New Guinea", "Trans New|Guinea").split("|")
        if len(parts) == 1 and "-" in name:
            head, tail = name.split("-", 1)
            parts = [head + "-", tail]
        for i, p in enumerate(parts):
            body.append(text(cx, bottom + 16 + i * 14, p, 12, "middle", "bold"))
        body.append(text(cx, bottom + 16 + len(parts) * 14, f"{named[name]:,}", 12, "middle",
                         fill=MUTED))
    y = bottom + 16 + 3 * 14 + 30
    body.append(text(40, y, f"The other {len(rest)} families, each circle drawn to the same scale",
                     14, weight="bold"))
    placed, y = pack([max(2.6, k * math.sqrt(s)) for s in rest], 40, W - 40, y + 14, gap=3)
    for cx, cy, r in placed:
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{GOLD_TINT}" '
                    f'stroke="{GOLD_EDGE}" stroke-width="0.9"/>')
    y += 34
    body.append(text(40, y, f"{isolates} isolates: languages with no known relative at all",
                     14, weight="bold"))
    placed, y = pack([2.6] * isolates, 40, W - 40, y + 14, gap=3.2)
    for cx, cy, r in placed:
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{INK}"/>')
    y += 36
    stated = DATA["world"]["families_stated"]
    body += note(40, y, [
        f"{DATA['world']['spoken_l1_languages']:,} first languages, living and recorded extinct, in "
        f"{stated} families and {isolates} isolates.",
        "Each circle's area is its number of languages (the smallest are enlarged to be seen).",
        "No accepted reconstruction joins any two.",
        f"Genesis 10 lists {DATA['genesis_10_nations']} nations, “each with his own language” "
        "(Genesis 10:5, ESV).",
    ], 13)
    y += 4 * 17 + 6
    body += note(40, y, [
        f"Glottolog 5.3 (2026). Drawn from its data release, where {DATA['lineage_sizes']['families_with_language']} "
        f"of the {stated} families hold a language in this count.",
    ], 11.5, MUTED, italic=True)
    h = int(y + 48)
    desc = (f"Every independent language lineage Glottolog recognises, drawn as circles sized by "
            f"number of languages: the largest families are Atlantic-Congo (1,408), Austronesian "
            f"(1,276), Indo-European (586), Sino-Tibetan (519) and Afro-Asiatic (381); then "
            f"{len(rest)} smaller families, most with five languages or fewer; then {isolates} "
            f"isolates. No reconstruction joins any two. Genesis 10 lists seventy nations.")
    out = svg_open(h, "429 lineages with no common trunk", desc)
    out += heading("No Common Trunk", "Every independent language lineage on earth")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def decay():
    lees = DATA["retention"]["lees_1953"]["rate"]
    swadesh = DATA["retention"]["swadesh_1955"]["rate"]
    floor = DATA["retention"]["chance_floor_percent"]
    x0, x1, y0, y1, tmax = 90, 680, 140, 470, 20000

    def px(t):
        return x0 + (x1 - x0) * t / tmax

    def py(pct):
        return y1 - (y1 - y0) * pct / 100

    def shared(rate, t):
        return 100 * rate ** (2 * t / 1000)

    body = []
    for pct in (0, 25, 50, 75, 100):
        body.append(f'<path d="M{x0} {py(pct):.1f} H{x1}" stroke="{GOLD_EDGE}" stroke-width="0.5" '
                    f'stroke-opacity="0.5"/>')
        body.append(text(x0 - 8, py(pct) + 5, f"{pct}%", 13, "end", fill=MUTED))
    for t in range(0, tmax + 1, 5000):
        body.append(text(px(t), y1 + 20, f"{t:,}", 13, "middle", fill=MUTED))
    body.append(text((x0 + x1) / 2, y1 + 42, "Years since the languages were one", 14, "middle"))
    body.append(text(30, (y0 + y1) / 2, "Core vocabulary still shared", 14, "middle",
                     extra=f'transform="rotate(-90 30 {(y0 + y1) / 2})"'))
    ts = list(range(0, tmax + 1, 250))
    hi = [(px(t), py(shared(swadesh, t))) for t in ts]
    lo = [(px(t), py(shared(lees, t))) for t in ts]
    band = " ".join(f"{x:.1f},{y:.1f}" for x, y in hi + lo[::-1])
    body.append(f'<polygon points="{band}" fill="{BLUE_TINT}" stroke="none"/>')
    for pts in (hi, lo):
        body.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" '
                    f'stroke="{BLUE}" stroke-width="2"/>')
    body.append(f'<path d="M{x0} {py(floor):.1f} H{x1}" stroke="{INK}" stroke-width="1.2" '
                f'stroke-dasharray="6 4"/>')
    body.append(text(x1 - 4, py(floor) - 7, "about where look-alikes become chance", 12.5, "end",
                     italic=True, extra=HALO))

    t_mt = years_since(BABEL_BC)
    t_lxx = years_since(LXX_PELEG_BC[0])
    a, b = shared(lees, t_mt), shared(swadesh, t_mt)
    body.append(f'<path d="M{px(t_mt):.1f} {y0} V{y1}" stroke="{RED}" stroke-width="2"/>')
    body.append(f'<path d="M{px(t_lxx):.1f} {y0 + 40} V{y1}" stroke="{RED}" stroke-width="1.5" '
                f'stroke-dasharray="5 4"/>')
    body.append(text(px(t_mt) - 6, y0 + 14, f"Babel c. {BABEL_BC} BC", 13, "end", "bold", RED,
                     extra=HALO))
    body.append(text(px(t_lxx) + 6, y0 + 54, f"Septuagint: {LXX_PELEG_BC[0]} BC", 12.5, fill=RED,
                     italic=True, extra=HALO))
    for v in (a, b):
        body.append(f'<circle cx="{px(t_mt):.1f}" cy="{py(v):.1f}" r="4.5" fill="{RED}"/>')
    lx = px(t_lxx) + 10
    body.append(f'<path d="M{px(t_mt) + 6:.1f} {py(b):.1f} H{lx - 4:.1f}" stroke="{INK}" '
                f'stroke-width="0.8"/>')
    body.append(text(lx, py(b) - 4, f"{a:.0f}–{b:.0f}% if one tongue drifted", 13,
                     weight="bold", extra=HALO))
    body.append(text(lx, py(b) + 13, f"from {BABEL_BC} BC: shared between", 13, extra=HALO))
    body.append(text(lx, py(b) + 30, "any two languages on earth", 13, extra=HALO))

    y = y1 + 70
    body.append(text(40, y, "THREE WAYS TO GET TODAY'S LANGUAGES", 14, weight="bold", spacing="1.5"))
    y += 12
    cw = (W - 80 - 20) / 3
    models = [
        (["One tongue, drift,", "since c. 2100 BC", "Predicts 17–29% shared", "everywhere.",
          "Observed: chance level", "between families."], "Ruled out", False, RED),
        (["One tongue, drift,", "50,000+ years ago", "Predicts near 0%:", "matches, by giving",
          "the evidence time", "to vanish."], "The mainstream view", True, INK),
        (["One tongue, divided", "at a stroke, c. 2100 BC", "Predicts unrelated", "families from the",
          "start: matches."], "Genesis 11:7-9", False, INK),
    ]
    heights = []
    for i, (lines, ref, dashed, stroke) in enumerate(models):
        c, hh = card(40 + i * (cw + 10), y, cw, lines, ref, dashed=dashed, stroke=stroke, size=13)
        body += c
        heights.append(hh)
    y += max(heights) + 26
    body += note(40, y, [
        f"Band: {swadesh:.0%} of core words kept per thousand years (Swadesh 1955, 100-word list) down to",
        f"{lees:.1%} (Lees 1953, 200-word list), applied to both languages of a pair. Fixed rates are",
        "disputed (Bergsland & Vogt 1962), so the band is an order of magnitude, never a date.",
    ], 11.5, MUTED, italic=True)
    h = int(y + 3 * 16 + 40)
    desc = (f"Share of core vocabulary two languages keep in common, falling with time since they "
            f"were one: between {swadesh:.0%} and {lees:.1%} retention per millennium for each. At "
            f"Babel, c. {BABEL_BC} BC, drift alone would leave {a:.0f} to {b:.0f} percent shared "
            f"between any two languages; by 10,000 years it reaches the chance level of about "
            f"{floor} percent. Three models: one tongue drifting since c. 2100 BC is ruled out; one "
            f"tongue 50,000 years ago matches by erasing the evidence; one tongue divided at a "
            f"stroke, Genesis 11:7-9, matches.")
    out = svg_open(h, "The decay test", desc)
    out += heading("The Decay Test", "What drift alone would leave behind")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def rates():
    total = DATA["world"]["spoken_l1_languages"]
    start = DATA["genesis_10_nations"]
    ln2 = math.log(2)
    rows = []
    for f in DATA["diversification"]["families"]:
        d = f["years"] * ln2 / math.log(f["languages"])
        rows.append((f["name"], f"{f['languages']} languages in {f['years']:,} years", d,
                     f["dated_by"] == "model", GOLD_EDGE))
    t_mt = years_since(BABEL_BC)
    t_lxx = years_since(LXX_PELEG_BC[0])
    rows.append(("Babel, Masoretic", f"{start} to {total:,} since {BABEL_BC} BC",
                 t_mt * ln2 / math.log(total / start), False, RED))
    rows.append(("Babel, Septuagint", f"{start} to {total:,} since {LXX_PELEG_BC[0]} BC",
                 t_lxx * ln2 / math.log(total / start), True, RED))
    for yrs in (50000, 100000):
        rows.append((f"One tongue, {yrs // 1000}k years", f"1 to {total:,} since {yrs:,} years ago",
                     yrs * ln2 / math.log(total), True, BLUE))

    x0, x1, dmax = 300, 610, 8000
    body = [text(40, 140, "Years for the number of languages to double (recorded extinct ones counted)",
                 14, weight="bold")]
    y = 168
    for name, sub, d, dashed, colour in rows:
        w = (x1 - x0) * d / dmax
        dash = ' stroke-dasharray="5 3"' if dashed else ""
        body.append(text(40, y + 14, name, 14, weight="bold"))
        body.append(text(40, y + 31, sub, 12, fill=MUTED, italic=True))
        body.append(f'<rect x="{x0}" y="{y + 4}" width="{w:.1f}" height="24" fill="{colour}" '
                    f'fill-opacity="0.35" stroke="{colour}" stroke-width="1.4"{dash}/>')
        body.append(text(x0 + w + 8, y + 21, f"{d:,.0f}", 14, weight="bold"))
        y += 46
        if name == "Narrow Bantu" or name == "Babel, Septuagint":
            body.append(f'<path d="M40 {y - 4} H{W - 40}" stroke="{GOLD_EDGE}" stroke-width="0.6"/>')
            y += 8
    y += 14
    body += note(40, y, [
        "Gold: families whose growth history records. Red: what Babel needs. Blue: what one",
        "language long ago needs. Dashed: the age is a model date, or the Septuagint's chronology.",
        "Counts: Glottolog, including recorded extinct varieties. Doubling time = years × ln 2 / ln(growth).",
    ], 12, MUTED, italic=True)
    h = int(y + 3 * 16 + 40)
    desc = ("Doubling time of the number of languages: " +
            "; ".join(f"{name} every {d:,.0f} years" for name, _, d, _, _ in rows) +
            ". Families with a recorded history doubled faster than Babel requires; one language "
            "long ago requires a rate ten to thirty times slower than any of them.")
    out = svg_open(h, "How fast languages multiply", desc)
    out += heading("How Fast Tongues Multiply", "Measured rates beside the rates each history needs")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def first_writing():
    rows = DATA["first_writing"]["rows"]
    x0, x1, bc0, bc1 = 200, 690, 3400, 0

    def px(bc):
        return x0 + (x1 - x0) * (bc0 - bc) / (bc0 - bc1)

    top, row_h = 190, 34
    bottom = top + row_h * len(rows)
    body = []
    body.append(f'<rect x="{px(PELEG_BC[0]):.1f}" y="{top - 30}" width="{px(PELEG_BC[1]) - px(PELEG_BC[0]):.1f}" '
                f'height="{bottom - top + 30}" fill="{RED_TINT}"/>')
    for bc in LXX_PELEG_BC:
        body.append(f'<path d="M{px(bc):.1f} {top - 30} V{bottom}" stroke="{RED}" stroke-width="1.2" '
                    f'stroke-dasharray="5 4"/>')
    body.append(f'<path d="M{px(FLOOD_BC):.1f} {top - 50} V{bottom}" stroke="{BLUE}" stroke-width="2"/>')
    body.append(f'<path d="M{px(LXX_FLOOD_BC):.1f} {top - 50} V{bottom}" stroke="{BLUE}" '
                f'stroke-width="1.5" stroke-dasharray="5 4"/>')
    body.append(text(px(FLOOD_BC) + 4, top - 54, f"Flood {FLOOD_BC}", 12.5, weight="bold", fill=BLUE,
                     extra=HALO))
    body.append(text(px(LXX_FLOOD_BC) - 4, top - 54, f"LXX Flood {LXX_FLOOD_BC}", 12.5, "end",
                     fill=BLUE, italic=True, extra=HALO))
    body.append(text(px(PELEG_BC[1]) + 4, top - 36, f"Peleg {PELEG_BC[0]}–{PELEG_BC[1]}", 12.5,
                     weight="bold", fill=RED, extra=HALO))
    body.append(text(px(LXX_PELEG_BC[0]) - 4, top - 36, "LXX Peleg", 12.5, "end", fill=RED,
                     italic=True, extra=HALO))
    for bc in range(3400, -1, -400):
        body.append(f'<path d="M{px(bc):.1f} {bottom} V{bottom + 6}" stroke="{INK}"/>')
        body.append(text(px(bc), bottom + 22, f"{bc} BC" if bc else "BC | AD", 12.5, "middle",
                         fill=MUTED))
    body.append(f'<path d="M{x0} {bottom} H{x1}" stroke="{INK}" stroke-width="1.2"/>')
    for i, r in enumerate(rows):
        y = top + i * row_h + row_h / 2
        body.append(f'<path d="M{x0} {y:.1f} H{x1}" stroke="{GOLD_EDGE}" stroke-width="0.4" '
                    f'stroke-opacity="0.6"/>')
        body.append(text(40, y + 1, r["language"], 14, weight="bold"))
        body.append(text(40, y + 15, r["family"], 11.5, fill=MUTED, italic=True))
        dash = ' stroke-dasharray="3 2"' if r["dashed"] else ""
        fill = PAPER if r["dashed"] else INK
        body.append(f'<circle cx="{px(r["bc"]):.1f}" cy="{y:.1f}" r="6" fill="{fill}" stroke="{INK}" '
                    f'stroke-width="1.6"{dash}/>')
    y = bottom + 50
    body += note(40, y, [f"{r['language']}, c. {r['bc']} BC: {r['what']}."
                         for r in rows], 11.5)
    y += len(rows) * 15.5 + 14
    body += note(40, y, [
        "Solid dot: an agreed first record. Open dot: the date or the language is disputed.",
        "Red band: Peleg's lifetime, “in his days the earth was divided” (Genesis 10:25, ESV),",
        "on the Masoretic text this site follows; dashed: the same on the Septuagint. Dates are",
        "conventional archaeological ones; how they meet the Flood is weighed in The Flood and the King Lists.",
    ], 11.5, MUTED, italic=True)
    h = int(y + 4 * 16 + 40)
    desc = ("Timeline from 3400 BC to the start of the era of the first written record of each "
            "language family: " + "; ".join(f"{r['language']} c. {r['bc']} BC" for r in rows) +
            f". Marked against the Flood ({FLOOD_BC} BC Masoretic, {LXX_FLOOD_BC} BC Septuagint) and "
            f"Peleg's lifetime ({PELEG_BC[0]}-{PELEG_BC[1]} BC Masoretic, {LXX_PELEG_BC[0]}-"
            f"{LXX_PELEG_BC[1]} BC Septuagint). Egyptian and Sumerian writing is dated before both "
            "Flood dates; every Indo-European record falls after Peleg.")
    out = svg_open(h, "When each family first wrote", desc)
    out += heading("The First Written Witnesses", "Each family's earliest record, against Genesis")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def growing_families():
    sim = json.loads((ROOT / "docs" / "data" / "language-simulation.json").read_text(encoding="utf-8"))
    obs = sim["observed_ranks"]
    n = len(obs)
    x0, x1, y0, y1, ymax = 100, 680, 150, 520, 10000

    def px(rank):
        return x0 + (x1 - x0) * math.log(rank) / math.log(n)

    def py(size):
        return y1 - (y1 - y0) * math.log10(max(1, min(size, ymax))) / math.log10(ymax)

    body = [f'<clipPath id="plot"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>']
    for v in (1, 10, 100, 1000, 10000):
        body.append(f'<path d="M{x0} {py(v):.1f} H{x1}" stroke="{GOLD_EDGE}" stroke-width="0.5" '
                    f'stroke-opacity="0.5"/>')
        body.append(text(x0 - 8, py(v) + 5, f"{v:,}", 13, "end", fill=MUTED))
    for r in (1, 10, 100, n):
        body.append(text(px(r), y1 + 20, str(r), 13, "middle", fill=MUTED))
    body.append(text((x0 + x1) / 2, y1 + 42, "Lineages ranked from largest to smallest", 14, "middle"))
    body.append(text(30, (y0 + y1) / 2, "Languages in the lineage", 14, "middle",
                     extra=f'transform="rotate(-90 30 {(y0 + y1) / 2})"'))
    styles = {"homogeneous": (BLUE, BLUE_TINT), "varied": (GOLD_EDGE, GOLD_TINT)}
    for name in ("homogeneous", "varied"):
        curve = sim["curves"][name]
        stroke, tint = styles[name]
        top = [(px(i + 1), py(c[2])) for i, c in enumerate(curve)]
        bot = [(px(i + 1), py(c[0])) for i, c in enumerate(curve)]
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in top + bot[::-1])
        body.append(f'<polygon points="{pts}" fill="{tint}" fill-opacity="0.8" stroke="{stroke}" '
                    f'stroke-width="1" stroke-dasharray="5 3" clip-path="url(#plot)"/>')
    dots = "".join(f'<circle cx="{px(i + 1):.1f}" cy="{py(s):.1f}" r="2.4"/>' for i, s in enumerate(obs))
    body.append(f'<g fill="{INK}">{dots}</g>')
    body.append(f'<path d="M{x0} {y0} V{y1} H{x1}" fill="none" stroke="{INK}" stroke-width="1.2"/>')

    hom, var = sim["homogeneous"], sim["varied"]
    obs_s = sim["observed"]
    inside = sum(1 for i, s in enumerate(obs)
                 if sim["curves"]["varied"][i][0] <= s <= sim["curves"]["varied"][i][2])
    body.append(text(px(1) + 10, py(obs[0]) - 6, "Atlantic-Congo", 12.5, weight="bold", extra=HALO))
    body.append(text(px(3), py(60) + 4, "Every people grows alike", 13, weight="bold", fill=BLUE,
                     extra=HALO))
    body.append(text(px(2.4), py(6000), "Peoples grow unevenly", 13, weight="bold", fill=GOLD_EDGE,
                     extra=HALO))

    y = y1 + 72
    rows = [
        ("Observed (Glottolog)", f"{obs_s['isolates']} isolates · {obs_s['families']} families · "
         f"largest {obs_s['largest']:,} · median family {obs_s['median_family']}"),
        ("Every people grows alike", f"{hom['median']['isolates']} isolates · {hom['median']['families']} "
         f"families · largest {hom['median']['largest']:,} · median family {hom['median']['median_family']}"),
        ("Peoples grow unevenly", f"{var['median']['isolates']} isolates · {var['median']['families']} "
         f"families · median family {var['median']['median_family']} · inside the band at {inside} of {n} ranks"),
    ]
    for label, line in rows:
        body.append(text(40, y, label, 13.5, weight="bold"))
        body.append(text(40, y + 17, line, 12.5, fill=MUTED))
        y += 42
    req = sim["required_doubling_from_one_language"]
    body += note(40, y + 4, [
        f"{sim['observed']['isolates'] + sim['observed']['families']} lineages begun at Babel, c. "
        f"{sim['babel_bc']} BC. The largest needs a doubling every {req[0]['doubling_years']} years;",
        f"Romance, the fastest recorded family, doubled every {sim['rate_cap']['doubling_years']}. "
        "Bands: 10th to 90th percentile of 60 runs.",
        "A fitted model shows the shape is reachable; it does not show this is how it happened.",
    ], 11.5, MUTED, italic=True)
    h = int(y + 3 * 16 + 44)
    desc = (f"Rank-size plot of the {n} language lineages Glottolog recognises, against two Babel "
            f"models that start them all c. {sim['babel_bc']} BC. If every people's languages grew at "
            f"one rate, the largest lineage would hold about {hom['median']['largest']} languages and "
            f"there would be about {hom['median']['isolates']} isolates; the world has "
            f"{obs_s['largest']:,} and {obs_s['isolates']}. If peoples grew unevenly, the model's band "
            f"contains the observed lineage at {inside} of {n} ranks. The largest family needs a "
            f"doubling every {req[0]['doubling_years']} years, slower than Romance's "
            f"{sim['rate_cap']['doubling_years']}.")
    out = svg_open(h, "Can Babel grow today's families?", desc)
    out += heading("Growing the Families", "Can lineages begun at Babel reach today's sizes?")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def one_alphabet():
    sc = DATA["scripts"]
    body = [text(40, 140, "WRITING WAS INVENTED A FEW TIMES", 14, weight="bold", spacing="1.5")]
    y = 168
    for i, s in enumerate(sc["independent"]):
        x = 40 + (i % 2) * 330
        yy = y + (i // 2) * 52
        stroke = RED if s["near"] else INK
        c, _ = card(x, yy, 310, [s["name"], f"{s['place']} · {s['date']}"], "", stroke=stroke, size=13)
        body += c
    y += 2 * 52 + 30
    body.append(text(40, y, "AND ONE ALPHABET BECAME MOST OF THE REST", 14, weight="bold", spacing="1.5"))
    body.append(text(40, y + 20, "Its letter shapes drawn from Egyptian hieroglyphs", 12.5, fill=MUTED,
                     italic=True))
    y += 46
    row_h, indent = 30, 30
    last_at_depth = {}
    for name, place, date, depth, dashed, near in sc["alphabet"]:
        x = 52 + depth * indent
        cy = y + row_h / 2
        if depth > 0:
            px_, py_ = last_at_depth[depth - 1]
            dash = ' stroke-dasharray="4 3"' if dashed else ""
            body.append(f'<path d="M{px_:.1f} {py_ + 7:.1f} V{cy:.1f} H{x - 6:.1f}" fill="none" '
                        f'stroke="{INK}" stroke-width="1.2"{dash}/>')
        fill = RED if near else INK
        body.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="4.5" fill="{fill}"/>')
        body.append(text(x + 10, cy + 5, name, 13.5, weight="bold" if depth <= 2 else None, fill=fill))
        body.append(text(W - 40, cy + 5, f"{place} · {date}", 12, "end", fill=MUTED, italic=True))
        last_at_depth[depth] = (x, cy)
        y += row_h
    y += 20
    body += note(40, y, [
        "Red: arose within about 1,000 km of Jerusalem. Dashed: the link is disputed (Brahmi's descent",
        "from Aramaic; South Arabian's branching point) or the script was modelled on another, not descended.",
        "Dates conventional (Daniels & Bright 1996). Other independent or invented scripts, such as Korean",
        "Hangul (AD 1443) and Cherokee (1821), are later and few.",
    ], 11.5, MUTED, italic=True)
    h = int(y + 4 * 16 + 40)
    desc = ("Writing was invented independently a few times: Egyptian hieroglyphs c. 3250 BC and "
            "cuneiform at Uruk, the Erech of Genesis 10:10, c. 3200 BC, both within about 1,000 km "
            "of Jerusalem; Chinese characters c. 1250 BC; Maya glyphs c. 300 BC. The alphabet began "
            "as Proto-Sinaitic letters in Sinai and Egypt c. 1850 BC and passed through Phoenician to "
            "Paleo-Hebrew, Greek (then Latin, Cyrillic), Aramaic (then square Hebrew, Syriac, Arabic, "
            "Mongolian, Kharosthi and, disputed, Brahmi and the scripts of South and Southeast Asia); "
            "South Arabian (then Ge'ez) branched off before Phoenician, at a disputed point.")
    out = svg_open(h, "One alphabet, few inventions", desc)
    out += heading("One Alphabet", "Writing's few roots, most of them near Jerusalem")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "one-alphabet.svg").write_text(one_alphabet(), encoding="utf-8")
    for name, fn in (("no-common-trunk", lineages), ("decay-test", decay),
                     ("how-fast-tongues-multiply", rates), ("first-written-witnesses", first_writing),
                     ("growing-the-families", growing_families)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", OUT / f"{name}.svg")


if __name__ == "__main__":
    main()
