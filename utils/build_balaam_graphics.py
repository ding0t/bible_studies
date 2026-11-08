"""Draw the graphics for biblical-figures/the-donkey-and-her-prophet.md, in the Larkin hand
(utils/lib/larkin.py) and with the archaeology maps' confidence code.

    python3 utils/build_balaam_graphics.py

plains_of_moab() draws Balaam's three viewpoints over the camp on real relief: the SRTM grid in
docs/data/maps/plains-of-moab-relief.json (sampled once through OpenTopoData; fetch_relief() rebuilds
it). Site coordinates are OpenBible.info's identifications, which for Shittim, Pisgah and Peor match
Joel Kramer's walk; the study holds his assessment, and a site whose location is only approximate is
drawn dashed. balaam_remembered() lays the Old Testament's memory of Balaam beside the New
Testament's warnings.
"""

import json
import math
import urllib.request
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, HALO, text, svg_open, heading, card, banner, credit, arrow_head)
from build_archaeology_graphics import (Frame, natural_earth, rings, pin, places, key, water_label,
                                        close_panel, inset_box, latlon_line, WATER, WATER_EDGE,
                                        PLACES as ARCH_PLACES)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "balaam"
RELIEF = ROOT / "docs" / "data" / "maps" / "plains-of-moab-relief.json"

# Hypsometric bands, metres: the Jordan Valley floor (below sea level) up to the Moab plateau.
BANDS = [(-1000, -300, "#dfe4c9"), (-300, -150, "#e7e5c8"), (-150, 0, "#ede3c4"),
         (0, 250, "#e8d4ad"), (250, 500, "#ddc196"), (500, 700, "#cfaa79"), (700, 2000, "#bd9564")]
CONTOURS = [(0, "4 3"), (400, None), (800, None)]
CONTOUR_INK = "#8a6d4a"
CAMP = "#f3e3b5"
SIGHT = "#8b1e1e"

# (num, label, lat, lon, kind, side). kind settled = the site this study holds; proposed = approximate.
JERICHO = next((lat, lon) for name, lat, lon, *_ in ARCH_PLACES if name == "Jericho")
SITES = [
    ("1", "Bamoth-baal|Kh. el-Quweiqiyeh", 31.731791, 35.740891, "proposed", "l"),
    ("2", "Pisgah, Mount Nebo|Rujm Siyaghah", 31.767778, 35.725556, "settled", "l"),
    ("3", "Peor, Beth-peor|Kh. Ayun Musa", 31.777021, 35.738498, "settled", "tr"),
    ("4", "Shittim|Tall el-Hammam", 31.84018, 35.67368, "settled", "tr"),
    ("5", "Beth-jeshimoth|Tell Azeimeh", 31.782551, 35.62125, "settled", "bl"),
    ("6", "Jericho", JERICHO[0], JERICHO[1], "settled", "r"),
    ("7", "Gilgal", 31.881883, 35.459969, "proposed", "t"),
    ("8", "Heshbon", 31.800811, 35.809062, "settled", "t"),
]
SITE = {s[0]: (s[2], s[3]) for s in SITES}
DEIR_ALLA = (32.1966, 35.62118)      # OpenBible: Succoth, Tell Deir Alla (600)
ARNON = (31.465833, 35.573333)       # OpenBible: Wadi Mujib (1000)
PETHOR = (36.7014, 38.0865)          # OpenBible: Til Barsip (408), disputed
JERUSALEM = (31.778, 35.235)


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def fetch_relief(lat0=31.69, lat1=31.94, lon0=35.38, lon1=35.86, dlat=0.005, dlon=0.006):
    lats = [round(lat1 - i * dlat, 4) for i in range(int(round((lat1 - lat0) / dlat)) + 1)]
    lons = [round(lon0 + j * dlon, 4) for j in range(int(round((lon1 - lon0) / dlon)) + 1)]
    pts = [(a, o) for a in lats for o in lons]
    elev = []
    for k in range(0, len(pts), 100):
        q = "|".join(f"{a},{o}" for a, o in pts[k:k + 100])
        req = urllib.request.Request(f"https://api.opentopodata.org/v1/srtm90m?locations={q}",
                                     headers={"User-Agent": "bible-studies-map-builder"})
        with urllib.request.urlopen(req, timeout=60) as r:
            elev += [x["elevation"] for x in json.load(r)["results"]]
    RELIEF.parent.mkdir(parents=True, exist_ok=True)
    RELIEF.write_text(json.dumps({
        "source": "SRTM 90 m (NASA, public domain), sampled through OpenTopoData srtm90m",
        "lat0": lat0, "lat1": lat1, "lon0": lon0, "lon1": lon1, "dlat": dlat, "dlon": dlon,
        "rows": len(lats), "cols": len(lons),
        "elevation_m": [elev[i * len(lons):(i + 1) * len(lons)] for i in range(len(lats))]},
        separators=(",", ":")), encoding="utf-8")


def load_relief():
    if not RELIEF.exists():
        fetch_relief()
    return json.loads(RELIEF.read_text(encoding="utf-8"))


def band(e):
    return next(i for i, (lo, hi, _) in enumerate(BANDS) if lo <= e < hi)


def relief_cells(f, R):
    """Each grid point as a cell, run-length merged along a row so the file stays small."""
    E, out = R["elevation_m"], []
    for i, row in enumerate(E):
        lat = R["lat1"] - i * R["dlat"]
        j = 0
        while j < len(row):
            b = band(row[j])
            k = j
            while k + 1 < len(row) and band(row[k + 1]) == b:
                k += 1
            x0, y0 = f.xy(lat + R["dlat"] / 2, R["lon0"] + (j - 0.5) * R["dlon"])
            x1, y1 = f.xy(lat - R["dlat"] / 2, R["lon0"] + (k + 0.5) * R["dlon"])
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0 + 0.4:.1f}" '
                       f'height="{y1 - y0 + 0.4:.1f}" fill="{BANDS[b][2]}"/>')
            j = k + 1
    return out


def contour(f, R, level):
    """Marching squares: one segment per crossed cell."""
    E, segs = R["elevation_m"], []

    def pt(i, j):
        return f.xy(R["lat1"] - i * R["dlat"], R["lon0"] + j * R["dlon"])

    def lerp(p, q, a, b):
        t = (level - a) / (b - a)
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)

    for i in range(len(E) - 1):
        for j in range(len(E[0]) - 1):
            c = [(E[i][j], pt(i, j)), (E[i][j + 1], pt(i, j + 1)),
                 (E[i + 1][j + 1], pt(i + 1, j + 1)), (E[i + 1][j], pt(i + 1, j))]
            cross = []
            for (a, p), (b, q) in zip(c, c[1:] + c[:1]):
                if (a < level) != (b < level):
                    cross.append(lerp(p, q, a, b))
            for k in range(0, len(cross) - 1, 2):
                (x0, y0), (x1, y1) = cross[k], cross[k + 1]
                segs.append(f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}")
    return "".join(segs)


def plains_of_moab():
    R = load_relief()
    lakes = list(rings(natural_earth("10m_lakes"), {"Dead Sea"}))
    jordan = list(rings(natural_earth("10m_rivers_lake_centerlines"), {"Jordan"}))

    f = Frame("moab", 35.40, 35.85, 31.815, 40, 120, 640, 0.23 * (640 / 0.45) / math.cos(math.radians(31.815)))
    reg = Frame("region", 34.95, 36.25, 31.92, 40, f.y + f.h + 34, 300,
                1.42 * (300 / 1.30) / math.cos(math.radians(31.92)))
    right_x = 360
    side_h = 470  # the three cards and the key, stacked beside the inset
    h = int(reg.y + max(reg.h, side_h) + 130)

    shittim, pisgah, peor = SITE["4"], SITE["2"], SITE["3"]
    pethor_km = round(km(shittim, PETHOR), -1)
    desc = (
        "Relief map of the plains of Moab at the north end of the Dead Sea, drawn from SRTM elevation: "
        "the Jordan Valley floor below sea level in pale tints, the escarpment and the Moab plateau in "
        "deepening browns, with contours at sea level, 400 and 800 metres. Israel's camp is a dashed "
        "gold band along the Jordan from Beth-jeshimoth to Abel-shittim (Numbers 33:49), with Shittim "
        "at Tall el-Hammam. Three numbered high places on the plateau edge to the "
        "south-east are the viewpoints Balak used: 1 Bamoth-baal (dashed as approximate), "
        "2 Pisgah on Mount Nebo and 3 Peor at Khirbet Ayun Musa, each with a red sight line to the camp labelled with what Balaam saw: "
        "the outskirts (Numbers 22:41), not all of them (Numbers 23:13), and Israel encamped tribe by "
        "tribe (Numbers 24:2), set out in a card below the map. Jericho, Gilgal (dashed) and Heshbon are marked, and a dashed line "
        "marks the Roman road from Heshbon past Peor down to the plain, which Joel Kramer suggests the "
        "Magi used. An inset shows the wider region: the Arnon, Moab's border where Balak met Balaam "
        "(Numbers 22:36), Tell Deir Alla where the Balaam inscription was found, Jerusalem, and an "
        f"arrow to Pethor by the Euphrates, about {pethor_km:.0f} km to the north (Numbers 22:5), its site "
        "disputed. Two cards separate what the text states from Kramer's identifications, which the "
        "study holds. The plate closes with Numbers 24:5."
    )
    out = svg_open(h, "Where Balaam looked down: the plains of Moab", desc)
    out += heading("Where Balaam Looked Down", "The plains of Moab, Numbers 22:1-25:1, on Joel Kramer's identifications")

    clip = "clip-moab"
    out.append(f'<clipPath id="{clip}"><rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.h:.1f}"/></clipPath>')
    out.append(f'<g clip-path="url(#{clip})">')
    out += relief_cells(f, R)
    for level, dash in CONTOURS:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<path d="{contour(f, R, level)}" fill="none" stroke="{CONTOUR_INK}" stroke-width="0.7" '
                   f'stroke-opacity="0.75"{d}/>')
    out.append(f'<path d="{f.path(jordan, False)}" fill="none" stroke="{WATER_EDGE}" stroke-width="2.2"/>')
    out.append(f'<path d="{f.path(lakes, True)}" fill="{WATER}" stroke="{WATER_EDGE}" stroke-width="1"/>')

    # The camp: "from Beth-jeshimoth to Abel-shittim" (Numbers 33:49). Its endpoints are stated; its
    # outline is not, so it is dashed.
    bj, ab = f.xy(*SITE["5"]), f.xy(*shittim)
    cx, cy = (bj[0] + ab[0]) / 2 - 6, (bj[1] + ab[1]) / 2
    ang = math.degrees(math.atan2(ab[1] - bj[1], ab[0] - bj[0]))
    half = math.dist(bj, ab) / 2 + 16
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{half:.1f}" ry="22" transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})" '
               f'fill="{CAMP}" fill-opacity="0.75" stroke="{GOLD_EDGE}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    tx, ty = f.xy(31.805, 35.628)
    out.append(text(tx, ty, "ISRAEL'S CAMP", 11.5, "middle", "bold", fill=GOLD_EDGE, spacing="1.5", extra=HALO))
    out.append(text(tx, ty + 13, "Numbers 33:49", 10.5, "middle", fill=GOLD_EDGE, italic=True, extra=HALO))

    # The Roman road Kramer traces from Heshbon past Peor to the plain (dashed: his reading, Eusebius).
    road = [SITE["8"], (31.79, 35.775), peor, (31.80, 35.705), shittim]
    out.append(f'<polyline points="{latlon_line(f, road)}" fill="none" stroke="{INK}" stroke-width="1.3" '
               f'stroke-dasharray="1.5 3.5" stroke-linecap="round"/>')

    # Sight lines from the three viewpoints to the camp.
    sights = [("1", (31.80, 35.655), "the outskirts", "Numbers 22:41"),
              ("2", (31.815, 35.66), "“not all of them”", "Numbers 23:13"),
              ("3", (31.835, 35.668), "“tribe by tribe”", "Numbers 24:2")]
    for num, target, lab, ref in sights:
        x0, y0 = f.xy(*SITE[num])
        x1, y1 = f.xy(*target)
        out.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{SIGHT}" stroke-width="1.4" '
                   f'stroke-dasharray="6 3" fill="none"/>')
        out.append(arrow_head(x1, y1, math.degrees(math.atan2(y1 - y0, x1 - x0)), 8, SIGHT))

    out += places(f, SITES, 12.5)
    out.append(water_label(f, 31.735, 35.53, "SALT SEA", 12.5, "2"))
    out.append(water_label(f, 31.719, 35.53, "modern shoreline", 10))
    out.append(water_label(f, 31.905, 35.565, "Jordan", 11.5))
    vx, vy = f.xy(31.905, 35.76)
    out.append(text(vx, vy, "MOAB PLATEAU", 11.5, "middle", fill=MUTED, spacing="2", extra=HALO))
    wx, wy = f.xy(31.705, 35.43)
    out.append(text(wx, wy, "Judean wilderness", 10.5, "middle", fill=MUTED, italic=True, extra=HALO))
    out += close_panel(f, "The plains of Moab")
    nx, ny = f.x + f.w - 26, f.y + 40
    out.append(f'<path d="M{nx} {ny + 18} V{ny - 4}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(arrow_head(nx, ny - 6, -90, 9))
    out.append(text(nx, ny + 32, "N", 12, "middle", "bold"))

    # Elevation key, under the map.
    ky = f.y + f.h + 8
    out.append(text(f.x, ky + 10, "Metres:", 10.5, fill=MUTED))
    bx = f.x + 50
    for lo, hi, col in BANDS:
        lab = "below −300" if lo == -1000 else (f"over {lo}" if hi == 2000 else f"{lo} to {hi}")
        out.append(f'<rect x="{bx}" y="{ky}" width="14" height="12" fill="{col}" stroke="{MUTED}" stroke-width="0.5"/>')
        out.append(text(bx + 18, ky + 10, lab.replace("-", "−"), 9.5, fill=MUTED))
        bx += 84

    # Inset: the region, with the way to Pethor.
    land = []
    out.append(f'<clipPath id="clip-region"><rect x="{reg.x}" y="{reg.y}" width="{reg.w}" height="{reg.h:.1f}"/></clipPath>')
    out.append('<g clip-path="url(#clip-region)">')
    out.append(f'<rect x="{reg.x}" y="{reg.y}" width="{reg.w}" height="{reg.h:.1f}" fill="{BANDS[4][2]}"/>')
    out.append(f'<path d="{reg.path(jordan, False)}" fill="none" stroke="{WATER_EDGE}" stroke-width="1.4"/>')
    out.append(f'<path d="{reg.path(list(rings(natural_earth("10m_lakes"), {"Dead Sea", "Sea of Galilee"})), True)}" '
               f'fill="{WATER}" stroke="{WATER_EDGE}" stroke-width="0.8"/>')
    ax, ay = reg.xy(*ARNON)
    out.append(f'<path d="M{ax:.1f} {ay:.1f} Q{ax + 18:.1f} {ay - 3:.1f} {ax + 40:.1f} {ay + 4:.1f}" fill="none" '
               f'stroke="{WATER_EDGE}" stroke-width="1.3"/>')
    out += inset_box(reg, f, "")
    out += places(reg, [("A", "Arnon|Numbers 22:36", ARNON[0], ARNON[1], "settled", "r"),
                        ("D", "Tell Deir Alla|the Balaam inscription", DEIR_ALLA[0], DEIR_ALLA[1], "settled", "r"),
                        ("J", "Jerusalem", JERUSALEM[0], JERUSALEM[1], "settled", "r")], 11.5)
    px, py = reg.x + reg.w - 24, reg.y + 30
    out.append(f'<path d="M{px - 40:.1f} {py + 50:.1f} L{px:.1f} {py:.1f}" stroke="{SIGHT}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    out.append(arrow_head(px, py, math.degrees(math.atan2(-50, 40)), 9, SIGHT))
    tx = px - 46
    out.append(text(tx, py + 18, "to Pethor, by the Euphrates,", 11, "end", fill=SIGHT, italic=True, extra=HALO))
    out.append(text(tx, py + 31, f"about {pethor_km:.0f} km (site disputed)", 11, "end", fill=SIGHT, italic=True, extra=HALO))
    out.append(text(tx, py + 44, "Numbers 22:5; Deuteronomy 23:4", 10.5, "end", fill=SIGHT, italic=True, extra=HALO))
    out += close_panel(reg, "The region")

    # Cards: what Balaam saw, what the text states, and what this study holds from Kramer.
    y = reg.y
    c, ch = card(right_x, y, W - 40 - right_x,
                 ["What Balaam saw", "1 Bamoth-baal: “the outskirts of the",
                  "  camp” (Numbers 22:41)", "2 Pisgah: “not all of them” (Numbers 23:13)",
                  "3 Peor: “Israel encamped tribe by", "  tribe” (Numbers 24:2)"], "", stroke=SIGHT, size=12.5)
    out += c
    y += ch + 12
    c, ch = card(right_x, y, W - 40 - right_x,
                 ["Stated in the text", "Camp: Beth-jeshimoth to Abel-shittim",
                  "  (Numbers 33:49), across from Jericho", "Viewpoints: Bamoth-baal, Pisgah, Peor",
                  "  (Numbers 22:41; 23:14, 28)", "Pisgah faces Jericho (Deuteronomy 34:1)",
                  "Beth-peor faces the valley (Deut. 3:29)"], "", size=12.5)
    out += c
    y += ch + 12
    c, ch = card(right_x, y, W - 40 - right_x,
                 ["Kramer's identifications, held here", "Shittim is Tall el-Hammam", "Peor is the ridge north of Pisgah",
                  "The viewpoints run south to north,", "  the view widening as they near",
                  "The Magi may have come by Peor"], "", dashed=True, size=12.5)
    out += c
    y += ch + 12
    k, kh = key(right_x, y, [("settled", "Site as held here"), ("proposed", "Site approximate")], w=W - 40 - right_x)
    out += k
    out.append(f'<path d="M{right_x + 160} {y + 19} H{right_x + 190}" stroke="{SIGHT}" stroke-width="1.4" stroke-dasharray="6 3"/>')
    out.append(text(right_x + 196, y + 23, "what he saw", 12))
    out.append(f'<path d="M{right_x + 160} {y + 44} H{right_x + 190}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="1.5 3.5"/>')
    out.append(text(right_x + 196, y + 48, "road", 12))

    vy = reg.y + max(reg.h, side_h) + 40
    out.append(text(W / 2, vy, "“How lovely are your tents, O Jacob, your dwellings, O Israel!”", 15, "middle", italic=True))
    out.append(text(W / 2, vy + 20, "Numbers 24:5 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(text(40, h - 40, "Relief: SRTM 90 m (NASA) via OpenTopoData. Water: Natural Earth. Sites: OpenBible.info,",
                    10, fill=MUTED, italic=True))
    out.append(text(40, h - 28, "as Joel Kramer (Expedition Bible) identifies them.", 10, fill=MUTED, italic=True))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# How Scripture remembers Balaam: the Old Testament's memory of the LORD's act, the New Testament's
# three warnings, each tied to the verse in Numbers it reads.

OT = [
    ("Deuteronomy 23:4-5", "Moses",
     ["the LORD “turned the curse into", "a blessing for you, because the", "LORD your God loves you”"]),
    ("Joshua 24:9-10", "The LORD, through Joshua",
     ["“I would not listen to Balaam ...", "I delivered you from his hand”"]),
    ("Nehemiah 13:1-2", "Read aloud after the exile",
     ["“our God had turned the curse", "into a blessing”"]),
    ("Micah 6:5", "The prophet",
     ["“remember ... so that you may", "acknowledge the righteousness", "of the LORD”"]),
]
NT = [
    ("2 Peter 2:15-16", "THE WAY OF BALAAM",
     ["“loved the wages of wickedness”", "rebuked by a donkey that spoke"], "reads Numbers 22:7, 17, 28-30", False),
    ("Jude 11", "THE ERROR OF BALAAM",
     ["“rushed for profit”", "beside Cain and Korah"], "reads Numbers 22:7, 17", False),
    ("Revelation 2:14", "THE TEACHING OF BALAAM",
     ["“a stumbling block”: “food sacrificed", "to idols”, “sexual immorality”"], "reads Numbers 25:1-3; 31:16", False),
    ("1 Corinthians 10:8, 11", "PEOR AS A WARNING",
     ["“written down as warnings for us”", "names Peor's sin, not Balaam"], "reads Numbers 25:1-9", True),
]


def balaam_remembered():
    colw, gap, x0 = 310, 20, 40
    x1 = x0 + colw + gap
    top = 140
    rowh = 108
    h = top + 120 + rowh * 4 + 200
    desc = (
        "Chart of how Scripture remembers Balaam. At the top, Numbers 22 to 25 and 31 hold two things: "
        "his mouth, which spoke the LORD's blessing (Numbers 23:5), and his counsel, which led Israel "
        "into sin at Peor (Numbers 31:16). The left column, the Old Testament, remembers what the LORD "
        "did: Deuteronomy 23:4-5, the LORD turned the curse into a blessing because He loves Israel; "
        "Joshua 24:9-10, the LORD says I would not listen to Balaam; Nehemiah 13:1-2, the same read "
        "aloud after the exile; Micah 6:5, remember, so that you may acknowledge the righteousness of "
        "the LORD. The right column, the New Testament, warns what Balaam did: 2 Peter 2:15-16, the "
        "way of Balaam, who loved the wages of wickedness and was rebuked by a donkey; Jude 11, the "
        "error of Balaam, rushing for profit beside Cain and Korah; Revelation 2:14, the teaching of "
        "Balaam, a stumbling block of idol food and immorality; and, dashed because it names Peor and "
        "not Balaam, 1 Corinthians 10:8 and 11, written down as warnings for us. Each card names the "
        "verses in Numbers it reads. The chart closes with Deuteronomy 23:5."
    )
    out = svg_open(h, "How Scripture remembers Balaam", desc)
    out += heading("How Scripture Remembers Balaam", "One man, two memories (Numbers 22-25; 31)")

    c, ch = card(x0 + 110, top - 34, W - 2 * (x0 + 110),
                 ["NUMBERS 22-25; 31", "His mouth: the LORD's word (Numbers 23:5)",
                  "His counsel: the sin at Peor (Numbers 31:16)"], "", fill=GOLD_TINT, stroke=GOLD_EDGE, size=13.5)
    out += c
    by = top - 34 + ch + 22
    out += banner(x0 + colw / 2, by, colw - 40, "THE LORD'S ACT", fill=BLUE, size=13)
    out += banner(x1 + colw / 2, by, colw - 40, "BALAAM'S WAY", fill=RED, size=13)
    out.append(text(x0 + colw / 2, by + 44, "the Old Testament remembers", 12.5, "middle", fill=MUTED, italic=True))
    out.append(text(x1 + colw / 2, by + 44, "the New Testament warns", 12.5, "middle", fill=MUTED, italic=True))

    y0 = by + 58
    for i, (ref, who, lines) in enumerate(OT):
        c, _ = card(x0, y0 + i * rowh, colw, [who] + lines, ref, fill=BLUE_TINT, stroke=BLUE, size=13)
        out += c
    for i, (ref, title, lines, anchor, dashed) in enumerate(NT):
        c, _ = card(x1, y0 + i * rowh, colw, [title] + lines + [anchor], ref, dashed=dashed,
                    fill=RED_TINT if not dashed else CARD, stroke=RED, size=13)
        out += c

    y = y0 + 4 * rowh + 6
    c, ch = card(x0, y, W - 2 * x0,
                 ["Both memories together",
                  "No curse from outside can touch the people God has blessed, and He claims",
                  "the victory as His own. A man can still stand under that blessing and choose",
                  "the wages, and the warning is written down for the church."], "", size=13.5)
    out += c
    vy = y + ch + 36
    out.append(text(W / 2, vy, "“the LORD your God turned the curse into a blessing for you,", 15, "middle", italic=True))
    out.append(text(W / 2, vy + 20, "because the LORD your God loves you.”", 15, "middle", italic=True))
    out.append(text(W / 2, vy + 40, "Deuteronomy 23:5 (BSB)", 12.5, "middle", fill=MUTED))
    out.append(text(40, h - 24, "Solid: the text names Balaam. Dashed: it names Peor only.", 10.5, fill=MUTED, italic=True))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("plains-of-moab-map", plains_of_moab), ("balaam-remembered", balaam_remembered)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", OUT / f"{name}.svg", (OUT / f"{name}.svg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
