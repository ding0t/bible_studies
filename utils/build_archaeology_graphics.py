"""Draw the maps for the scripture/ archaeology studies, in the same hand as the Larkin-style charts
(utils/lib/larkin.py) and with the same confidence code: a solid mark is a place whose
identification is settled, a dashed one is a proposal.

    python3 utils/build_archaeology_graphics.py

cities_of_the_plain() reads the date of the overthrow from docs/data/chronology.json, so the map
cannot drift from the timeline.
"""

import json
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        EARTH_TINT, HALO, esc, text, svg_open, heading, card, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "cities-of-the-plain"
CHRONOLOGY = ROOT / "docs" / "data" / "chronology.json"

WATER = "#9fb8d3"
WATER_EDGE = "#5b7fa6"
FIRE = "#c4471c"

# Map frame: longitude and latitude bounds, drawn at true proportion for 31.4 N.
LON0, LON1, LAT0, LAT1 = 35.02, 35.86, 30.84, 31.98
MX, MY, MW = 40, 120, 640
PX_LON = MW / (LON1 - LON0)
PX_LAT = PX_LON / 0.853
MH = (LAT1 - LAT0) * PX_LAT


def xy(lat, lon):
    return MX + (lon - LON0) * PX_LON, MY + (LAT1 - lat) * PX_LAT


# The Dead Sea before the twentieth-century drop, simplified: the deep northern basin and the
# shallow southern one, with the Lisan peninsula drawn over them as land.
SEA = [(31.77, 35.53), (31.74, 35.46), (31.66, 35.44), (31.55, 35.41), (31.46, 35.39),
       (31.36, 35.38), (31.28, 35.37), (31.18, 35.37), (31.08, 35.38), (31.00, 35.41),
       (30.96, 35.44), (30.98, 35.47), (31.06, 35.49), (31.14, 35.50), (31.24, 35.53),
       (31.34, 35.56), (31.46, 35.58), (31.58, 35.59), (31.70, 35.58), (31.77, 35.56)]
LISAN = [(31.31, 35.555), (31.33, 35.50), (31.32, 35.45), (31.28, 35.42), (31.22, 35.43),
         (31.17, 35.47), (31.16, 35.52), (31.20, 35.54)]
JORDAN = [(31.98, 35.54), (31.92, 35.55), (31.86, 35.54), (31.81, 35.55), (31.77, 35.545)]

# (label, lat, lon, kind, label side). kind: settled | proposed-south | proposed-north | other
PLACES = [
    ("Jericho", 31.871, 35.444, "settled", "left"),
    ("Tall el-Hammam", 31.840, 35.673, "proposed-north", "right"),
    ("Madaba", 31.716, 35.794, "settled", "right"),
    ("Mount Nebo", 31.768, 35.726, "settled", "right"),
    ("Bethel", 31.930, 35.222, "settled", "right"),
    ("Hebron (Mamre)", 31.530, 35.095, "settled", "right"),
    ("En-gedi", 31.461, 35.392, "settled", "left"),
    ("Masada", 31.316, 35.354, "settled", "left"),
    ("Mount Sodom", 31.060, 35.395, "settled", "left"),
    ("Bab edh-Dhra", 31.255, 35.535, "proposed-south", "right"),
    ("Numeira", 31.130, 35.530, "proposed-south", "right"),
    ("es-Safi (Zoar)", 31.035, 35.470, "zoar", "right"),
    ("Feifa", 30.945, 35.430, "proposed-south", "right"),
    ("Khanazir", 30.890, 35.410, "proposed-south", "right"),
]

SOUTH_ROWS = [
    ("Sodom", "Bab edh-Dhra", "burned; never resettled"),
    ("Gomorrah", "Numeira", "burned; never resettled"),
    ("Admah", "Feifa", "burned; never resettled"),
    ("Zeboiim", "Khanazir", "burned; never resettled"),
    ("Zoar (Bela)", "es-Safi", "spared; Byzantine Zoara"),
]


def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(*p) for p in points))


def marker(x, y, kind):
    if kind == "settled":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{INK}"/>'
    if kind == "zoar":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{GOLD_TINT}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{GOLD_EDGE}"/>')
    colour = FIRE if kind == "proposed-south" else MUTED
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{RED_TINT}" stroke="{colour}" '
            f'stroke-width="2" stroke-dasharray="3 2.5"/>')


def overthrow_year():
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    for e in data["genesis_markers"]:
        if e["id"] == "sodom_overthrown":
            return e["am_year"], 3959 - e["am_year"]
    raise SystemExit("chronology.json has no sodom_overthrown marker")


def cities_of_the_plain():
    am, bc = overthrow_year()
    table_y = MY + MH + 40
    h = int(table_y + 26 + 30 * len(SOUTH_ROWS) + 250)
    desc = (
        "Map of the Dead Sea and its shores, with the shallow southern basin and the Lisan peninsula. "
        "Settled places are solid dots: Jericho, Bethel, Hebron, En-gedi, Masada, Mount Sodom, Mount Nebo "
        "and Madaba, where the sixth-century mosaic map shows Zoar. es-Safi, Byzantine Zoara and on this "
        "study's reading biblical Zoar, is a gold ring at the south-east corner. Dashed red rings mark the "
        "four southern sites Joel Kramer proposes for the burned cities: Bab edh-Dhra (Sodom), Numeira "
        "(Gomorrah), Feifa (Admah) and Khanazir (Zeboiim), all Early Bronze Age towns that burned and were "
        "never lived in again. A dashed grey ring marks Tall el-Hammam, the northern proposal. A table "
        "pairs each city with its proposed site. A note gives the date of the overthrow on this site's "
        f"chronology, AM {am} or {bc} BC, against the earlier conventional dates of the excavated sites."
    )
    out = svg_open(h, "The cities of the plain: the southern case", desc)
    out += heading("The Cities of the Plain", "Four overthrown, one spared (Genesis 19:21-25; Deuteronomy 29:23)")

    # Land, sea, peninsula, river.
    out.append(f'<rect x="{MX}" y="{MY}" width="{MW}" height="{MH:.1f}" fill="{EARTH_TINT}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<polygon points="{poly(SEA)}" fill="{WATER}" stroke="{WATER_EDGE}" stroke-width="1.5"/>')
    out.append(f'<polygon points="{poly(LISAN)}" fill="{EARTH_TINT}" stroke="{WATER_EDGE}" stroke-width="1.2"/>')
    jordan = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(*p) for p in JORDAN))
    out.append(f'<polyline points="{jordan}" fill="none" stroke="{WATER_EDGE}" stroke-width="2.5"/>')
    lx, ly = xy(31.25, 35.47)
    out.append(text(lx, ly + 5, "Lisan", 13, "middle", italic=True, fill=MUTED))
    sx, sy = xy(31.55, 35.49)
    out.append(text(sx, sy, "SALT SEA", 16, "middle", "bold", fill=BLUE, spacing="3"))
    out.append(text(sx, sy + 18, "(Genesis 14:3)", 12, "middle", italic=True, fill=BLUE))
    jx, jy = xy(31.93, 35.56)
    out.append(text(jx + 8, jy, "Jordan", 12.5, italic=True, fill=BLUE))
    kx, ky = xy(31.05, 35.62)
    out.append(text(kx, ky, "the plain", 12.5, "middle", italic=True, fill=MUTED))

    # Abraham's view of the smoke from near Hebron (Genesis 19:27-28).
    ax, ay = xy(31.53, 35.095)
    bx, by = xy(31.20, 35.48)
    out.append(f'<path d="M{ax:.1f} {ay:.1f} Q{(ax + bx) / 2:.1f} {ay + 20:.1f} {bx - 10:.1f} {by - 10:.1f}" '
               f'fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="2 4"/>')
    for i, ln in enumerate(["Abraham looks toward Sodom:", "“the smoke of the land went up",
                            "like the smoke of a furnace”", "(Genesis 19:27-28)"]):
        out.append(text(MX + 14, ay + 130 + i * 15, ln, 12, fill=MUTED, italic=True))

    for label, lat, lon, kind, side in PLACES:
        x, y = xy(lat, lon)
        out.append(marker(x, y, kind))
        dx = 12 if side == "right" else -12
        anchor = "start" if side == "right" else "end"
        weight = "bold" if kind in ("proposed-south", "zoar") else None
        fill = RED if kind == "proposed-south" else (GOLD_EDGE if kind == "zoar" else INK)
        out.append(text(x + dx, y + 5, label, 13.5, anchor, weight, fill=fill, extra=HALO))

    # Key, inside the map's south-west corner, where the land is empty.
    kx0, ky0 = MX + 12, MY + MH - 110
    out.append(f'<rect x="{kx0}" y="{ky0}" width="232" height="96" rx="5" fill="{CARD}" stroke="{INK}" stroke-width="1"/>')
    rows = [("settled", "Identification settled"), ("zoar", "Zoar: Byzantine Zoara"),
            ("proposed-south", "Proposed: southern case"), ("proposed-north", "Proposed: northern case")]
    for i, (kind, lab) in enumerate(rows):
        y = ky0 + 20 + i * 21
        out.append(marker(kx0 + 16, y, kind))
        out.append(text(kx0 + 32, y + 5, lab, 13))

    # The southern case as a table.
    y = table_y
    out.append(text(MX, y, "THE SOUTHERN CASE (JOEL KRAMER)", 14, weight="bold", spacing="1.5"))
    y += 12
    cols = (MX, MX + 150, MX + 300)
    for i, (city, site, fate) in enumerate(SOUTH_ROWS):
        ry = y + 30 * i
        spared = city.startswith("Zoar")
        fill = GOLD_TINT if spared else CARD
        out.append(f'<rect x="{MX}" y="{ry}" width="{MW}" height="26" fill="{fill}" stroke="{INK}" stroke-width="0.8"/>')
        out.append(text(cols[0] + 8, ry + 18, city, 14, weight="bold"))
        out.append(text(cols[1] + 8, ry + 18, site + ("" if spared else "?"), 14, fill=GOLD_EDGE if spared else RED))
        out.append(text(cols[2] + 8, ry + 18, fate, 14, italic=True))
    y += 30 * len(SOUTH_ROWS) + 26

    notes = [
        ("Settled: Zoar outlived the overthrow.", False,
         ["Isaiah 15:5 and Jeremiah 48:34 name it as a Moabite town; Josephus (Antiquities 1.204)",
          "says it is “to this day called Zoar”; the Madaba Map (c. AD 560) draws it among palms."]),
        ("Contested: which ruins are Sodom and Gomorrah.", True,
         [f"This site's chronology places the overthrow in AM {am}, {bc} BC, Abraham's 99th year.",
          "The excavators date Bab edh-Dhra's end c. 2350 BC and Numeira's earlier; lowered",
          "datings bring them nearer. The northern site, Tall el-Hammam, ends c. 1650 BC."]),
    ]
    for title, dashed, lines in notes:
        c, ch = card(MX, y, MW, [title] + lines, "", dashed=dashed, size=13.5)
        out += c
        y += ch + 14

    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cities-of-the-plain-map.svg").write_text(cities_of_the_plain(), encoding="utf-8")
    print("wrote", OUT / "cities-of-the-plain-map.svg")


if __name__ == "__main__":
    main()
