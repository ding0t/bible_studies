"""Draw the maps for the scripture/ archaeology studies, in the same hand as the Larkin-style charts
(utils/lib/larkin.py) and with the same confidence code: a solid mark is a place whose
identification is settled, a dashed one is a proposal.

    python3 utils/build_archaeology_graphics.py

cities_of_the_plain() reads the date of the overthrow from docs/data/chronology.json, so the map
cannot drift from the timeline.

sites_map() and texts_map() locate the numbered entries of scripture/archaeological-sites.md and
scripture/ancient-texts-manuscripts.md; the numbers on the map are the study's headings, so
renumbering a study means renumbering its list here. Coastlines, lakes and rivers come from Natural
Earth (public domain), downloaded on first run into a cache directory; the Jerusalem walls are
OpenStreetMap ways, simplified and kept below as constants so the build needs no OSM query.
"""

import json
import math
import tempfile
import urllib.request
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        EARTH_TINT, HALO, esc, text, svg_open, heading, card, credit)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "cities-of-the-plain"
MAP_OUT = ROOT / "docs" / "content" / "assets" / "img" / "archaeology"
CHRONOLOGY = ROOT / "docs" / "data" / "chronology.json"
NATURAL_EARTH = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/"
NE_CACHE = Path(tempfile.gettempdir()) / "natural-earth"

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


# ---------------------------------------------------------------------------------------------
# Where the evidence is: one map per catalogue study.

OPEN_SEA = "#dfe8f0"
INSET_EDGE = "#8a6d3b"

# OpenStreetMap barrier=city_wall ways, simplified to ~7 m. The first is the circuit, which crosses
# the Temple Mount along its west and north sides; the other two close its south and east sides.
OLD_CITY_WALLS = [
    [(31.77659, 35.22764), (31.77666, 35.22758), (31.77807, 35.22588), (31.77831, 35.22584),
     (31.77841, 35.22569), (31.77891, 35.22614), (31.77922, 35.22586), (31.7796, 35.22688),
     (31.77996, 35.22746), (31.77966, 35.22775), (31.78098, 35.2295), (31.78136, 35.22981),
     (31.78151, 35.2302), (31.78194, 35.23077), (31.78216, 35.23085), (31.78249, 35.2313),
     (31.78258, 35.23159), (31.78253, 35.23247), (31.78268, 35.23249), (31.78285, 35.23292),
     (31.78324, 35.23497), (31.78342, 35.23512), (31.78375, 35.23676), (31.78364, 35.23669),
     (31.78227, 35.23695), (31.78139, 35.237), (31.7803, 35.23706), (31.78003, 35.2337),
     (31.77567, 35.23462), (31.77584, 35.2358), (31.77558, 35.23567), (31.77505, 35.23577),
     (31.77475, 35.23356), (31.77428, 35.23324), (31.77401, 35.23254), (31.77336, 35.23234),
     (31.77323, 35.23148), (31.77294, 35.23077), (31.77282, 35.22974), (31.77291, 35.22774),
     (31.77453, 35.22766), (31.77554, 35.22786), (31.77562, 35.22762), (31.77629, 35.22782),
     (31.77651, 35.22775), (31.77659, 35.22764)],
    [(31.77565, 35.23463), (31.77608, 35.23756), (31.7803, 35.23706)],
]
TEMPLE_MOUNT = [(31.7803, 35.23706), (31.78003, 35.2337), (31.77567, 35.23462), (31.77608, 35.23756)]
# Valley floors, drawn from the walls and the Gihon/Siloam levels; schematic.
KIDRON = [(31.7905, 35.2385), (31.7830, 35.2390), (31.7775, 35.2388), (31.7730, 35.2374),
          (31.7700, 35.2362), (31.7660, 35.2370), (31.7600, 35.2400)]
HINNOM = [(31.7790, 35.2238), (31.7760, 35.2250), (31.7725, 35.2262), (31.7700, 35.2283),
          (31.7690, 35.2320), (31.7690, 35.2350), (31.7680, 35.2366)]
# The OpenStreetMap shoreline (today's), simplified to ~120 m: Natural Earth's is a rough oval.
GALILEE = [
    (32.827, 35.5162), (32.8134, 35.5222), (32.8055, 35.5288), (32.7972, 35.5406), (32.77, 35.548),
    (32.7584, 35.5612), (32.7483, 35.5668), (32.7342, 35.5702), (32.7273, 35.5707), (32.7251, 35.5685),
    (32.7211, 35.57), (32.7097, 35.5777), (32.7055, 35.5884), (32.7081, 35.5997), (32.7161, 35.6121),
    (32.7447, 35.6339), (32.7732, 35.6403), (32.7854, 35.6356), (32.7925, 35.6407), (32.7982, 35.6398),
    (32.8164, 35.6453), (32.8334, 35.6419), (32.8416, 35.6498), (32.8537, 35.6474), (32.8589, 35.6448),
    (32.8589, 35.6429), (32.8595, 35.6443), (32.8608, 35.6433), (32.8603, 35.6419), (32.8653, 35.6431),
    (32.8891, 35.624), (32.889, 35.6215), (32.891, 35.6217), (32.8949, 35.615), (32.8964, 35.6069),
    (32.892, 35.6003), (32.8907, 35.5924), (32.8881, 35.5916), (32.8803, 35.5769), (32.8793, 35.5674),
    (32.8733, 35.5598), (32.8707, 35.5446), (32.8615, 35.5357), (32.8532, 35.5328), (32.8546, 35.5316),
    (32.8533, 35.5322), (32.8495, 35.5277), (32.8481, 35.5285), (32.848, 35.5262), (32.8449, 35.5247),
    (32.8426, 35.5266), (32.8413, 35.5219), (32.827, 35.5162)]

# Gihon to Siloam. The tunnel winds in an S for 533 m; this keeps its ends and its westward bow.
TUNNEL = [(31.77324, 35.23683), (31.7728, 35.2360), (31.7720, 35.2364), (31.7713, 35.2355),
          (31.7704, 35.2351)]


def natural_earth(name):
    NE_CACHE.mkdir(parents=True, exist_ok=True)
    path = NE_CACHE / f"ne_{name}.geojson"
    if not path.exists():
        urllib.request.urlretrieve(f"{NATURAL_EARTH}ne_{name}.geojson", path)
    return json.loads(path.read_text(encoding="utf-8"))


class Frame:
    """An equirectangular panel: lon0..lon1 across w px, centred on lat_c, h px tall."""

    def __init__(self, key, lon0, lon1, lat_c, x, y, w, h):
        self.key, self.x, self.y, self.w, self.h = key, x, y, w, h
        self.lon0 = lon0
        self.kx = w / (lon1 - lon0)
        self.ky = self.kx / math.cos(math.radians(lat_c))
        self.lat1 = lat_c + h / self.ky / 2
        self.lat0 = lat_c - h / self.ky / 2
        self.lon1 = lon1

    def xy(self, lat, lon):
        return self.x + (lon - self.lon0) * self.kx, self.y + (self.lat1 - lat) * self.ky

    def path(self, rings, closed):
        """Rings are clamped to a box just outside the panel, so a continent costs a few hundred
        points rather than the whole coastline; the clamped edge falls outside the clip."""
        m = max(self.lon1 - self.lon0, self.lat1 - self.lat0) * 0.05
        bx0, bx1, by0, by1 = self.lon0 - m, self.lon1 + m, self.lat0 - m, self.lat1 + m
        d = []
        for ring in rings:
            lons, lats = [p[0] for p in ring], [p[1] for p in ring]
            if max(lons) < bx0 or min(lons) > bx1 or max(lats) < by0 or min(lats) > by1:
                continue
            pts, last = [], None
            for lon, lat in ring:
                X, Y = self.xy(min(max(lat, by0), by1), min(max(lon, bx0), bx1))
                if last and abs(X - last[0]) + abs(Y - last[1]) < 1.2:
                    continue
                pts.append(f"{X:.1f},{Y:.1f}")
                last = (X, Y)
            if len(pts) > 1:
                d.append("M" + "L".join(pts) + ("Z" if closed else ""))
        return "".join(d)


def rings(geo, names=None, skip=()):
    for f in geo["features"]:
        if names and f["properties"].get("name") not in names or f["properties"].get("name") in skip:
            continue
        g = f["geometry"]
        if g["type"] == "Polygon":
            yield from g["coordinates"]
        elif g["type"] == "MultiPolygon":
            for p in g["coordinates"]:
                yield from p
        elif g["type"] == "LineString":
            yield g["coordinates"]
        elif g["type"] == "MultiLineString":
            yield from g["coordinates"]


def latlon_line(f, pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in (f.xy(*p) for p in pts))


def scale_bar(f):
    km_per_px = 111.32 * math.cos(math.radians((f.lat0 + f.lat1) / 2)) / f.kx
    km = next(k for k in (0.25, 0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000)[::-1]
              if k / km_per_px <= f.w * 0.28)
    px = km / km_per_px
    x1, y = f.x + f.w - 12, f.y + f.h - 14
    label = f"{km:g} km" if km >= 1 else f"{int(km * 1000)} m"
    return [f'<path d="M{x1 - px:.1f} {y - 5} V{y} H{x1:.1f} V{y - 5}" fill="none" stroke="{INK}" stroke-width="1.5"/>',
            text(x1 - px / 2, y - 8, label, 11.5, "middle", extra=HALO)]


def panel(f, land, lakes, rivers):
    clip = f"clip-{f.key}"
    out = [f'<clipPath id="{clip}"><rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.h:.1f}"/></clipPath>',
           f'<g clip-path="url(#{clip})">',
           f'<rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.h:.1f}" fill="{OPEN_SEA if land else EARTH_TINT}"/>']
    if land:
        out.append(f'<path d="{f.path(land, True)}" fill="{EARTH_TINT}" stroke="{WATER_EDGE}" stroke-width="0.8" fill-rule="evenodd"/>')
    if rivers:
        out.append(f'<path d="{f.path(rivers, False)}" fill="none" stroke="{WATER_EDGE}" stroke-width="1.3"/>')
    if lakes:
        out.append(f'<path d="{f.path(lakes, True)}" fill="{WATER}" stroke="{WATER_EDGE}" stroke-width="0.8"/>')
    return out


def close_panel(f, title):
    out = ["</g>", f'<rect x="{f.x}" y="{f.y}" width="{f.w}" height="{f.h:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>']
    tw = len(title) * 9.4 + 16
    out.append(f'<rect x="{f.x}" y="{f.y}" width="{tw:.0f}" height="22" fill="{INK}"/>')
    out.append(text(f.x + 8, f.y + 15.5, title.upper(), 12, weight="bold", fill=PAPER, spacing="1"))
    return out + scale_bar(f)


def inset_box(parent, child, label, side="right"):
    x0, y0 = parent.xy(child.lat1, child.lon0)
    x1, y1 = parent.xy(child.lat0, child.lon1)
    w, h = max(x1 - x0, 6), max(y1 - y0, 6)
    out = [f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{INSET_EDGE}" stroke-width="1.6"/>']
    if side == "right":
        out.append(text(x0 + w + 5, y0 + h / 2 + 4, label, 11.5, fill=INSET_EDGE, italic=True, extra=HALO))
    else:
        out.append(text(x0 - 5, y0 + h / 2 + 4, label, 11.5, "end", fill=INSET_EDGE, italic=True, extra=HALO))
    return out


def pin(x, y, num, kind):
    """A numbered marker. settled: solid; proposed: dashed (debated, approximate or unrecorded);
    kept: a double ring, where an object is held but was not found."""
    r = 9
    w = max(0, (len(num) - 2) * 6.5)
    if kind == "settled":
        shape = f'<rect x="{x - r - w / 2:.1f}" y="{y - r:.1f}" width="{2 * r + w:.1f}" height="{2 * r}" rx="{r}" fill="{INK}"/>'
        fill = PAPER
    elif kind == "kept":
        shape = (f'<rect x="{x - r - w / 2:.1f}" y="{y - r:.1f}" width="{2 * r + w:.1f}" height="{2 * r}" rx="{r}" fill="{CARD}" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{x - r - w / 2 - 3:.1f}" y="{y - r - 3:.1f}" width="{2 * r + w + 6:.1f}" height="{2 * r + 6}" rx="{r + 3}" fill="none" stroke="{INK}" stroke-width="1"/>')
        fill = INK
    else:
        shape = f'<rect x="{x - r - w / 2:.1f}" y="{y - r:.1f}" width="{2 * r + w:.1f}" height="{2 * r}" rx="{r}" fill="{RED_TINT}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 2"/>'
        fill = RED
    size = 10.5 if len(num) < 3 else 9.5
    return shape + text(x, y + 3.7, num, size, "middle", "bold", fill=fill)


OFFSETS = {"r": (14, 4.5, "start"), "l": (-14, 4.5, "end"), "t": (0, -14, "middle"),
           "b": (0, 23, "middle"), "tr": (10, -10, "start"), "br": (10, 19, "start"),
           "tl": (-10, -10, "end"), "bl": (-10, 19, "end")}


def places(f, rows, size=13):
    """rows: (num, label, lat, lon, kind, side). A label may carry a second line after '|'."""
    marks, labels = [], []
    for num, label, lat, lon, kind, side in rows:
        x, y = f.xy(lat, lon)
        marks.append(pin(x, y, num, kind))
        dx, dy, anchor = OFFSETS[side]
        if side.startswith("t"):
            dy -= (size + 2) * label.count("|")
        if len(num) > 2 and side in ("r", "l"):
            dx += (len(num) - 2) * 3.3 * (1 if side == "r" else -1)
        for i, ln in enumerate(label.split("|")):
            labels.append(text(x + dx, y + dy + i * (size + 2), ln, size if i == 0 else size - 1.5, anchor,
                               "bold" if i == 0 else None, fill=INK if i == 0 else MUTED,
                               italic=i > 0, extra=HALO))
    return marks + labels


def water_label(f, lat, lon, s, size=12, spacing=None):
    x, y = f.xy(lat, lon)
    return text(x, y, s, size, "middle", italic=True, fill=BLUE, spacing=spacing, extra=HALO)


def key(x, y, rows, w=212):
    h = 14 + 25 * len(rows)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{CARD}" stroke="{INK}" stroke-width="1"/>']
    for i, (kind, label) in enumerate(rows):
        cy = y + 19 + 25 * i
        if kind == "inset":
            out.append(f'<rect x="{x + 9}" y="{cy - 8}" width="18" height="16" fill="none" stroke="{INSET_EDGE}" stroke-width="1.6"/>')
        else:
            out.append(pin(x + 18, cy, "", kind))
        out.append(text(x + 36, cy + 4.5, label, 12.5))
    return out, h


def jerusalem(f, rows):
    out = [f'<polygon points="{latlon_line(f, TEMPLE_MOUNT)}" fill="{GOLD_TINT}" stroke="none"/>']
    for valley in (KIDRON, HINNOM):
        out.append(f'<polyline points="{latlon_line(f, valley)}" fill="none" stroke="{MUTED}" '
                   f'stroke-width="7" stroke-opacity="0.22" stroke-linecap="round" stroke-linejoin="round"/>')
    for wall in OLD_CITY_WALLS:
        out.append(f'<polyline points="{latlon_line(f, wall)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<polyline points="{latlon_line(f, TUNNEL)}" fill="none" stroke="{WATER_EDGE}" '
               f'stroke-width="2.4" stroke-dasharray="2 3" stroke-linecap="round"/>')
    gx, gy = f.xy(31.77324, 35.23683)
    out.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="3.5" fill="{WATER}" stroke="{WATER_EDGE}" stroke-width="1.2"/>')
    out.append(text(gx + 7, gy - 4, "Gihon", 11, fill=BLUE, italic=True, extra=HALO))
    x, y = f.xy(31.7805, 35.2275)
    out.append(text(x, y, "OLD CITY", 12, "middle", fill=MUTED, spacing="2", extra=HALO))
    x, y = f.xy(31.7838, 35.2397)
    out.append(text(x, y, "Kidron", 11.5, "middle", italic=True, fill=MUTED, extra=HALO))
    out.append(text(x, y + 13, "Valley", 11.5, "middle", italic=True, fill=MUTED, extra=HALO))
    x, y = f.xy(31.7712, 35.2270)
    out.append(text(x, y, "Hinnom Valley", 11.5, "middle", italic=True, fill=MUTED, extra=HALO))
    return out + places(f, rows, 12.5)


def footnote(y, lines):
    return [text(40, y + 15 * i, ln, 11.5, fill=MUTED, italic=True) for i, ln in enumerate(lines)]


def map_credit(h):
    return text(40, h - 22, "Coastlines: Natural Earth. Jerusalem walls: © OpenStreetMap contributors.",
                10.5, fill=MUTED, italic=True)


def galilee_lakes(geo):
    return list(rings(geo, skip={"Sea of Galilee"})) + [[(lon, lat) for lat, lon in GALILEE]]


def sites_map():
    land10, lakes10 = list(rings(natural_earth("10m_land"))), galilee_lakes(natural_earth("10m_lakes"))
    land50 = list(rings(natural_earth("50m_land")))
    jordan = list(rings(natural_earth("10m_rivers_lake_centerlines"), {"Jordan"}))

    israel = Frame("il", 34.55, 35.90, 32.28, 40, 120, 410,
                   2.05 * 410 / 1.35 / math.cos(math.radians(32.28)))
    paul = Frame("paul", 21.9, 28.1, 37.9, 470, 120, 210, 150)
    key_y = paul.y + paul.h + 18
    galilee = Frame("gal", 35.49, 35.665, 32.83, 470, key_y + 107, 210, israel.y + israel.h - key_y - 107)
    jer = Frame("jer", 35.2205, 35.2445, 31.7772, 40, israel.y + israel.h + 26, 640, 520)
    h = int(jer.y + jer.h + 82)

    desc = (
        "Map locating the seventeen numbered sites of the Archaeological Sites study. A main panel of "
        "the land of Israel marks Jericho (1), Hazor (2), Megiddo (3), Gezer (5), Lachish (8), Nazareth "
        "(9), Jacob's Well at Shechem (13) and Caesarea Maritima (17). An inset of the Sea of Galilee "
        "marks Capernaum (10), the two proposed sites of Bethsaida, et-Tell and el-Araj (11, dashed), "
        "Magdala (12) and the shore near Ginosar where the Galilee boat was found (14). A panel of the "
        "Aegean marks Corinth, Athens and Ephesus, the cities of Paul's journeys in entry 17. A "
        "full-width panel of Jerusalem draws the Old City walls, the Temple Mount, and the Kidron and "
        "Hinnom valleys, and marks the City of David (4), Hezekiah's Tunnel from the Gihon spring to "
        "the Pool of Siloam (6), the Pool of Bethesda (7), the Temple Mount and Western Wall (15), and "
        "the two proposed sites of Golgotha and the tomb, the Church of the Holy Sepulchre and the "
        "Garden Tomb (16, dashed)."
    )
    out = svg_open(h, "Archaeological sites: where they are", desc)
    out += heading("Where the Sites Are", "The numbered sites of the Archaeological Sites study")

    # Israel.
    out += panel(israel, land10, lakes10, jordan)
    out.append(water_label(israel, 33.12, 34.80, "Mediterranean", 13, "1"))
    out.append(water_label(israel, 33.07, 34.80, "Sea", 13, "1"))
    out.append(water_label(israel, 31.55, 35.66, "Dead", 11.5))
    out.append(water_label(israel, 31.52, 35.66, "Sea", 11.5))
    out.append(water_label(israel, 32.25, 35.63, "Jordan", 11.5))
    out += inset_box(israel, galilee, "Inset: Galilee", "left")
    out += inset_box(israel, jer, "Inset: Jerusalem", "left")
    out += places(israel, [
        ("1", "Jericho|Tell es-Sultan", 31.8709, 35.4440, "settled", "r"),
        ("2", "Hazor", 33.0179, 35.5688, "settled", "l"),
        ("3", "Megiddo", 32.5854, 35.1842, "settled", "r"),
        ("5", "Gezer", 31.8597, 34.9225, "settled", "l"),
        ("8", "Lachish", 31.5655, 34.8492, "settled", "l"),
        ("9", "Nazareth", 32.7020, 35.2978, "settled", "r"),
        ("13", "Jacob's Well|Shechem (Nablus)", 32.2097, 35.2853, "settled", "r"),
        ("17", "Caesarea|Maritima", 32.4961, 34.8914, "settled", "l"),
    ])
    out += close_panel(israel, "The land")

    # Paul's cities.
    out += panel(paul, land50, [], [])
    out.append(water_label(paul, 37.2, 25.4, "Aegean Sea", 11.5))
    out += places(paul, [
        ("17", "Corinth", 37.9051, 22.8764, "settled", "b"),
        ("17", "Athens", 37.9724, 23.7231, "settled", "t"),
        ("17", "Ephesus", 37.9410, 27.3420, "settled", "b"),
    ], 11.5)
    out += close_panel(paul, "Paul's cities")

    k, kh = key(470, key_y, [("settled", "Site identified"),
                             ("proposed", "Proposed: site debated"),
                             ("inset", "Area shown in an inset")], 210)
    out += k

    # Sea of Galilee.
    out += panel(galilee, land10, lakes10, jordan)
    out.append(water_label(galilee, 32.77, 35.59, "Sea of", 12.5, "1"))
    out.append(water_label(galilee, 32.755, 35.59, "Galilee", 12.5, "1"))
    out += places(galilee, [
        ("10", "Capernaum", 32.8805, 35.5755, "settled", "t"),
        ("11", "et-Tell", 32.9104, 35.6306, "proposed", "l"),
        ("11", "el-Araj", 32.8888, 35.6188, "proposed", "b"),
        ("12", "Magdala", 32.8253, 35.5155, "settled", "r"),
        ("14", "Galilee boat", 32.8455, 35.5235, "settled", "r"),
    ], 12)
    out += close_panel(galilee, "Galilee")

    # Jerusalem.
    out += panel(jer, None, None, None)
    out += jerusalem(jer, [
        ("4", "City of David", 31.7738, 35.2359, "settled", "l"),
        ("6", "Pool of Siloam", 31.7704, 35.2351, "settled", "l"),
        ("7", "Pool of Bethesda", 31.7815, 35.2360, "settled", "t"),
        ("15", "Temple Mount", 31.7780, 35.2353, "settled", "r"),
        ("15", "Western Wall", 31.7767, 35.2344, "settled", "l"),
        ("16", "Holy Sepulchre", 31.7784, 35.2298, "proposed", "t"),
        ("16", "Garden Tomb", 31.7840, 35.2302, "proposed", "r"),
    ])
    tx, ty = jer.xy(31.7718, 35.2366)
    out.append(text(tx + 8, ty, "Hezekiah's", 11, fill=BLUE, italic=True, extra=HALO))
    out.append(text(tx + 8, ty + 12, "Tunnel", 11, fill=BLUE, italic=True, extra=HALO))
    out += close_panel(jer, "Jerusalem")

    out += footnote(jer.y + jer.h + 20, [
        "Entry 17 covers the theatres and public buildings of Paul's cities: Caesarea, Corinth, Athens and Ephesus.",
        "Valleys and the tunnel's course are schematic; the tunnel winds in an S between its two ends.",
    ])
    out.append(map_credit(h))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def texts_map():
    land10, lakes10 = list(rings(natural_earth("10m_land"))), galilee_lakes(natural_earth("10m_lakes"))
    land50, lakes50 = list(rings(natural_earth("50m_land"))), list(rings(natural_earth("50m_lakes")))
    rivers_all = natural_earth("10m_rivers_lake_centerlines")
    big_rivers = list(rings(rivers_all, {"Nile", "Euphrates", "Tigris"}))
    jordan = list(rings(rivers_all, {"Jordan"}))

    world = Frame("w", 10.5, 47.5, 34.0, 40, 120, 640, 420)
    israel = Frame("il2", 34.62, 35.92, 32.32, 40, world.y + world.h + 30, 310,
                   2.05 * 310 / 1.30 / math.cos(math.radians(32.32)))
    jer = Frame("jer2", 35.2195, 35.2445, 31.7725, 370, israel.y, 310, israel.h)
    h = int(israel.y + israel.h + 110)

    desc = (
        "Map locating the numbered texts, manuscripts and inscriptions of the Ancient Texts study where "
        "each was found. A wide panel from Italy to Mesopotamia marks Babylon, where the Cyrus Cylinder "
        "(5) and the Babylonian Chronicles (6) came from; Nineveh, the Taylor Prism (8); Amarna, the "
        "Amarna Letters (10); Thebes, the Merneptah Stele (11); St Catherine's Monastery in Sinai, "
        "Codex Sinaiticus (16); and Rome, where Codex Vaticanus (17) is kept, drawn as a double ring "
        "because its origin is unknown. A dashed ring over the Nile valley stands for the papyri P52, "
        "P46 and P66 (13 to 15), bought in Egypt with no recorded findspot. A panel of the land of "
        "Israel marks Qumran and the Dead Sea Scrolls (1), Dhiban and the Mesha Stele (3), Tel Dan (4), "
        "Lachish and its letters (7) and Caesarea Maritima and the Pilate Stone (18). An inset of "
        "Jerusalem marks Ketef Hinnom and its silver scrolls (2), the Siloam Inscription in Hezekiah's "
        "Tunnel (9), the bullae from the City of David and the Ophel (12), and the Peace Forest tomb of "
        "the Caiaphas ossuary (19, dashed, placed approximately). The historians, 20 to 24, are copied "
        "texts with no findspot and are not mapped."
    )
    out = svg_open(h, "Ancient texts and manuscripts: where they were found", desc)
    out += heading("Where They Were Found", "The numbered entries of the Ancient Texts study")

    out += panel(world, land50, lakes50, big_rivers)
    out.append(water_label(world, 34.2, 19.5, "Mediterranean Sea", 13, "1.5"))
    out.append(water_label(world, 24.4, 36.7, "Red Sea", 11.5))
    out.append(water_label(world, 26.6, 31.6, "Nile", 11.5))
    # The three papyri: a region, not a point.
    ex, ey = world.xy(28.0, 31.0)
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="16" ry="46" transform="rotate(-18 {ex:.1f} {ey:.1f})" '
               f'fill="{RED_TINT}" fill-opacity="0.55" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    out += inset_box(world, israel, "Israel: below", "right")
    out += places(world, [
        ("5·6", "Babylon", 32.5447, 44.4318, "settled", "b"),
        ("8", "Nineveh", 36.3594, 43.1528, "settled", "r"),
        ("10", "Amarna", 27.6597, 30.9039, "settled", "l"),
        ("11", "Thebes", 25.7248, 32.6080, "settled", "r"),
        ("16", "St Catherine's|Monastery, Sinai", 28.5559, 33.9760, "settled", "r"),
        ("17", "Rome|Vatican Library", 41.9045, 12.4545, "kept", "r"),
        ("13–15", "Papyri bought in Egypt", 29.6, 30.55, "proposed", "l"),
    ], 12.5)
    k, kh = key(world.x + 12, world.y + world.h - 101, [("settled", "Where it was found"),
                                                         ("proposed", "Findspot unrecorded or approx."),
                                                         ("kept", "Where it is kept; origin unknown")], 250)
    out += k
    out += close_panel(world, "The ancient Near East")

    out += panel(israel, land10, lakes10, jordan)
    out.append(water_label(israel, 33.0, 34.86, "Mediterranean", 12, "1"))
    out.append(water_label(israel, 31.40, 35.50, "Dead Sea", 11))
    out += inset_box(israel, jer, "Jerusalem", "left")
    out += places(israel, [
        ("1", "Qumran", 31.7411, 35.4590, "settled", "r"),
        ("3", "Dhiban|Mesha Stele", 31.4985, 35.7801, "settled", "t"),
        ("4", "Tel Dan", 33.2486, 35.6522, "settled", "l"),
        ("7", "Lachish", 31.5655, 34.8492, "settled", "r"),
        ("18", "Caesarea|Pilate Stone", 32.4961, 34.8914, "settled", "r"),
    ], 12.5)
    out += close_panel(israel, "The land")

    out += panel(jer, None, None, None)
    out += jerusalem(jer, [
        ("2", "Ketef Hinnom|silver scrolls", 31.7689, 35.2254, "settled", "b"),
        ("9", "Siloam|Inscription", 31.7708, 35.2353, "settled", "l"),
        ("12", "Bullae|Ophel,|City of David", 31.7748, 35.2362, "settled", "r"),
        ("19", "Caiaphas tomb|Peace Forest (approx.)", 31.7600, 35.2310, "proposed", "r"),
    ])
    out += close_panel(jer, "Jerusalem")

    out += footnote(israel.y + israel.h + 20, [
        "Where now: P52 Manchester; P46 Dublin and Ann Arbor; P66 Geneva (Cologny); Codex Sinaiticus mostly London.",
        "The Baruch bulla (12) came through the antiquities market, with no findspot. Josephus, Tacitus, Pliny,",
        "Suetonius and the Talmud (20–24) survive as copied texts, not found objects, and are not mapped.",
    ])
    out.append(map_credit(h))
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cities-of-the-plain-map.svg").write_text(cities_of_the_plain(), encoding="utf-8")
    print("wrote", OUT / "cities-of-the-plain-map.svg")
    for name, fn in (("archaeological-sites-map", sites_map), ("ancient-texts-map", texts_map)):
        (MAP_OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", MAP_OUT / f"{name}.svg")


if __name__ == "__main__":
    main()
