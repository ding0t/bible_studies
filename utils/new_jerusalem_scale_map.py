"""Draws docs/content/assets/img/new-jerusalem-scale.svg: the New Jerusalem's 12,000-stadia square
(Revelation 21:16) set over today's map, plus a side view of its height against the curve of the
earth. Stdlib only. Coastlines come from Natural Earth (public domain) and are downloaded on first
run into a cache directory.

    python3 utils/new_jerusalem_scale_map.py
    python3 utils/new_jerusalem_scale_map.py --centre 31.778 35.235 --centre-name Jerusalem

Scripture names the city Jerusalem without placing it on a map, so the centre is a choice made for
scale; the plate's footnote says so and should keep saying so if the centre changes.
"""
import argparse
import json
import tempfile
import urllib.request
from math import acos, cos, radians, sin, sqrt
from pathlib import Path

EARTH_RADIUS_KM = 6371.0
CITY_SIDE_KM = 2220  # 12,000 stadia; the ESV Study Bible gives 2,221 km, the LSB footnote 2,220
NATURAL_EARTH = 'https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/'

# (lat, lon, label position). Whether each falls inside the square is computed, not declared,
# so moving the centre re-sorts them.
PLACES = {
    'Patmos': (37.31, 26.55, 'e'), 'Ephesus': (37.94, 27.34, 'ne'), 'Athens': (37.98, 23.73, 'w'),
    'Istanbul': (41.01, 28.98, 'e'), 'Ankara': (39.93, 32.86, 'e'), 'Damascus': (33.51, 36.29, 'e'),
    'Cairo': (30.04, 31.24, 'w'), 'Alexandria': (31.20, 29.92, 'nw'), 'Nineveh': (36.36, 43.15, 'e'),
    'Babylon': (32.54, 44.42, 'se'), 'Baghdad': (33.31, 44.36, 'ne'), 'Ur': (30.96, 46.10, 'w'),
    'Medina': (24.47, 39.61, 'e'), 'Mecca': (21.42, 39.83, 'e'), 'Riyadh': (24.71, 46.68, 'e'),
    'Tehran': (35.69, 51.39, 'e'), 'Benghazi': (32.12, 20.07, 'e'), 'Kuwait': (29.37, 47.98, 'e'),
}
LABEL_OFFSETS = {'e': (7, 4, 'start'), 'w': (-7, 4, 'end'), 'ne': (6, -5, 'start'),
                 'nw': (-6, -5, 'end'), 'se': (6, 13, 'start')}

# Map frame (px) and the km it shows either side of the centre.
MX, MY, MW, MH = 40, 150, 880, 720
XK = 1800
YK = XK * MH / MW
S = MW / (2 * XK)


def natural_earth(name, cache):
    path = cache / f'ne_50m_{name}.geojson'
    if not path.exists():
        urllib.request.urlretrieve(f'{NATURAL_EARTH}ne_50m_{name}.geojson', path)
    return json.loads(path.read_text(encoding='utf-8'))


def make_projection(lat0, lon0):
    """Azimuthal equidistant, so every distance from the centre is true."""
    p0, l0 = radians(lat0), radians(lon0)

    def aeqd(lat, lon):
        p, l = radians(lat), radians(lon)
        c = acos(max(-1, min(1, sin(p0) * sin(p) + cos(p0) * cos(p) * cos(l - l0))))
        if c == 0:
            return 0.0, 0.0
        k = EARTH_RADIUS_KM * c / sin(c)
        return k * cos(p) * sin(l - l0), k * (cos(p0) * sin(p) - sin(p0) * cos(p) * cos(l - l0))
    return aeqd


def px(x, y):
    return MX + MW / 2 + x * S, MY + MH / 2 - y * S


def outline(geo, aeqd, lat0, lon0):
    out = []
    for f in geo['features']:
        g = f['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for ring in (ring for poly in polys for ring in poly):
            if not any(abs(lon - lon0) < 45 and abs(lat - lat0) < 35 for lon, lat in ring):
                continue
            pts = [aeqd(lat, lon) for lon, lat in ring]
            if not any(abs(x) < XK * 1.3 and abs(y) < YK * 1.3 for x, y in pts):
                continue
            d, last = [], None
            for x, y in pts:
                X, Y = px(x, y)
                # Drop points under ~1px apart: the 50m coastline is otherwise 1.6 MB of SVG.
                if last and abs(X - last[0]) + abs(Y - last[1]) < 1.2:
                    continue
                d.append(f'{X:.1f},{Y:.1f}')
                last = (X, Y)
            if len(d) > 2:
                out.append('M' + 'L'.join(d) + 'Z')
    return ''.join(out)


def place_label(name, lat, lon, pos, aeqd):
    x, y = aeqd(lat, lon)
    inside = abs(x) <= CITY_SIDE_KM / 2 and abs(y) <= CITY_SIDE_KM / 2
    X, Y = px(x, y)
    dx, dy, anchor = LABEL_OFFSETS[pos]
    colour = '#3b2f1a' if inside else '#7a6d57'
    style = '' if inside else ' font-style="italic"'
    return (f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{3.2 if inside else 2.6}" fill="{colour}"/>'
            f'<text x="{X + dx:.1f}" y="{Y + dy:.1f}" text-anchor="{anchor}" font-size="13" '
            f'fill="{colour}"{style} class="lbl">{name}</text>')


def build(lat0, lon0, centre_name, cache):
    aeqd = make_projection(lat0, lon0)
    land = outline(natural_earth('land', cache), aeqd, lat0, lon0)
    lakes = outline(natural_earth('lakes', cache), aeqd, lat0, lon0)
    half = CITY_SIDE_KM / 2 * S
    cx, cy = px(0, 0)

    labels = '\n    '.join(place_label(n, a, b, p, aeqd) for n, (a, b, p) in PLACES.items())
    gates = []
    for f in (-0.5, 0.0, 0.5):  # three gates on each side (Revelation 21:13)
        g = f * half
        gates += [(cx + g, cy - half), (cx + g, cy + half), (cx - half, cy + g), (cx + half, cy + g)]
    gates_svg = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fffdf6" stroke="#9b90ad" '
                        f'stroke-width="1"/>' for x, y in gates)
    scale_bar = 500 * S

    # Side view: 5,200 km of the earth's surface across the frame, drawn on a true-radius arc.
    PY = MY + MH + 70
    IX, IY, IW, IH = 40, PY + 20, 880, 560
    PK = IW / 5200.0
    gx = IX + IW / 2
    ground_y = IY + IH - 125
    Rp = EARTH_RADIUS_KM * PK
    ccy = ground_y + Rp

    def arc_y(x):
        return ccy - sqrt(Rp * Rp - (x - gx) ** 2)
    xs = [IX + i * IW / 100 for i in range(101)]
    arc = 'M' + ' L'.join(f'{x:.1f},{arc_y(x):.1f}' for x in xs)

    def orbit(km):
        return f'M{IX} {arc_y(IX) - km * PK:.1f} ' + ' '.join(f'L{x:.1f},{arc_y(x) - km * PK:.1f}' for x in xs)
    cube = CITY_SIDE_KM * PK
    iss_km, karman_km = 420, 100
    height = IY + IH + 150

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height:.0f}" font-family="Helvetica, Arial, sans-serif" role="img" aria-labelledby="t d">
  <title id="t">The size of the New Jerusalem on today's map</title>
  <desc id="d">A map of the eastern Mediterranean and Middle East with a gold square 12,000 stadia (about 2,220 km) on each side centred on present-day {centre_name}. Below, a side view shows the city's height of about 2,220 km against the curve of the earth, five times the height at which the International Space Station orbits.</desc>
  <defs>
    <clipPath id="frame"><rect x="{MX}" y="{MY}" width="{MW}" height="{MH}"/></clipPath>
    <clipPath id="inset"><rect x="{IX}" y="{IY}" width="{IW}" height="{IH}"/></clipPath>
    <radialGradient id="glory" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#fff4c9" stop-opacity="0.9"/>
      <stop offset="1" stop-color="#fff4c9" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fbe7a1"/><stop offset="0.5" stop-color="#eec95c"/><stop offset="1" stop-color="#d9a93a"/>
    </linearGradient>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1d2a44"/><stop offset="0.75" stop-color="#3d5a80"/><stop offset="1" stop-color="#a9c6de"/>
    </linearGradient>
    <marker id="tick" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M5 0 V10" stroke="#5a4a2c" stroke-width="1.5"/></marker>
    <marker id="tickw" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M5 0 V10" stroke="#f5ecd4" stroke-width="1.5"/></marker>
  </defs>
  <style>.lbl{{paint-order:stroke;stroke:#f3ecd9;stroke-width:3px;stroke-linejoin:round}}</style>

  <rect width="960" height="{height:.0f}" fill="#faf5e8"/>
  <rect x="12" y="12" width="936" height="{height - 24:.0f}" fill="none" stroke="#5a4a2c" stroke-width="1.5"/>
  <rect x="18" y="18" width="924" height="{height - 36:.0f}" fill="none" stroke="#5a4a2c" stroke-width="0.6"/>

  <text x="480" y="52" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" fill="#3b2f1a" letter-spacing="1">The New Jerusalem to Scale</text>
  <text x="480" y="80" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-style="italic" font-size="16" fill="#5a4a2c">12,000 stadia each way (Revelation 21:16), set over today’s map for size</text>
  <text x="40" y="136" font-size="13" fill="#5a4a2c" letter-spacing="2" font-weight="bold">PLAN · CENTRED ON PRESENT-DAY {centre_name.upper()}</text>

  <g clip-path="url(#frame)">
    <rect x="{MX}" y="{MY}" width="{MW}" height="{MH}" fill="#d6e6ec"/>
    <path d="{land}" fill="#efe6cf" stroke="#8a7a5a" stroke-width="0.7" stroke-linejoin="round"/>
    <path d="{lakes}" fill="#d6e6ec" stroke="#8a7a5a" stroke-width="0.5"/>
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{half * 1.25:.1f}" fill="url(#glory)" opacity="0.8"/>
    <rect x="{cx - half:.1f}" y="{cy - half:.1f}" width="{2 * half:.1f}" height="{2 * half:.1f}" fill="#e8bf55" fill-opacity="0.28" stroke="#7fb8a3" stroke-width="5"/>
    <rect x="{cx - half:.1f}" y="{cy - half:.1f}" width="{2 * half:.1f}" height="{2 * half:.1f}" fill="none" stroke="#a87d22" stroke-width="1.2"/>
    {gates_svg}
    {labels}
    <g transform="translate({cx:.1f} {cy:.1f})">
      <circle r="6" fill="#fffdf4" stroke="#a87d22" stroke-width="2"/>
      <circle r="2" fill="#a87d22"/>
    </g>
    <text x="{cx + 9:.1f}" y="{cy - 9:.1f}" font-size="14" font-weight="bold" fill="#3b2f1a" class="lbl">{centre_name}</text>
  </g>
  <rect x="{MX}" y="{MY}" width="{MW}" height="{MH}" fill="none" stroke="#5a4a2c" stroke-width="1"/>

  <g stroke="#5a4a2c" stroke-width="1"><line x1="{cx - half:.1f}" y1="{MY + 14}" x2="{cx + half:.1f}" y2="{MY + 14}" marker-start="url(#tick)" marker-end="url(#tick)"/></g>
  <text x="{cx:.1f}" y="{MY + 32}" text-anchor="middle" font-size="14" fill="#3b2f1a" class="lbl">12,000 stadia ≈ 2,220 km</text>

  <g transform="translate({MX + 14} {MY + MH - 74})">
    <rect width="236" height="62" fill="#faf5e8" fill-opacity="0.92" stroke="#8a7a5a" stroke-width="0.6"/>
    <circle cx="14" cy="18" r="3.2" fill="#3b2f1a"/><text x="24" y="22" font-size="12.5" fill="#3b2f1a">inside the city’s footprint</text>
    <circle cx="14" cy="38" r="2.6" fill="#7a6d57"/><text x="24" y="42" font-size="12.5" font-style="italic" fill="#7a6d57">outside it</text>
    <line x1="14" y1="54" x2="{14 + scale_bar:.1f}" y2="54" stroke="#3b2f1a" stroke-width="2"/>
    <text x="{20 + scale_bar:.1f}" y="58" font-size="12" fill="#3b2f1a">500 km</text>
  </g>
  <g transform="translate({MX + MW - 30} {MY + MH - 40})">
    <circle r="15" fill="#faf5e8" stroke="#5a4a2c" stroke-width="1"/>
    <path d="M0 -12 L4.5 4 L0 0 L-4.5 4 Z" fill="#3b2f1a"/>
    <text y="-19" text-anchor="middle" font-size="12" font-weight="bold" fill="#3b2f1a">N</text>
  </g>

  <text x="40" y="{PY:.0f}" font-size="13" fill="#5a4a2c" letter-spacing="2" font-weight="bold">SIDE VIEW · HEIGHT AGAINST THE CURVE OF THE EARTH</text>
  <g clip-path="url(#inset)">
    <rect x="{IX}" y="{IY}" width="{IW}" height="{IH}" fill="url(#sky)"/>
    <circle cx="{gx:.1f}" cy="{ground_y - cube / 2:.1f}" r="{cube * 0.95:.1f}" fill="url(#glory)" opacity="0.55"/>
    <path d="{arc} L{IX + IW},{IY + IH} L{IX},{IY + IH} Z" fill="#8b9a6b" stroke="#55623d" stroke-width="1.2"/>
    <path d="{orbit(karman_km)}" fill="none" stroke="#c9d8e6" stroke-width="1" stroke-dasharray="3 4"/>
    <path d="{orbit(iss_km)}" fill="none" stroke="#f5ecd4" stroke-width="1" stroke-dasharray="6 4"/>
    <rect x="{gx - cube / 2:.1f}" y="{ground_y - cube:.1f}" width="{cube:.1f}" height="{cube:.1f}" fill="url(#gold)" stroke="#a87d22" stroke-width="1.5"/>
    <polygon points="{gx - cube / 2 + 12:.1f},{ground_y - cube:.1f} {gx - cube / 2 + 60:.1f},{ground_y - cube:.1f} {gx - cube / 2:.1f},{ground_y - cube + 90:.1f} {gx - cube / 2:.1f},{ground_y - cube + 20:.1f}" fill="#fff" opacity="0.35"/>
  </g>
  <rect x="{IX}" y="{IY}" width="{IW}" height="{IH}" fill="none" stroke="#5a4a2c" stroke-width="1"/>
  <g font-size="13" fill="#f5ecd4">
    <text x="{IX + 12}" y="{arc_y(IX + 12) - iss_km * PK - 7:.1f}">International Space Station orbit, about 420 km</text>
    <text x="{IX + 12}" y="{arc_y(IX + 12) - karman_km * PK - 7:.1f}">edge of space, 100 km</text>
    <text x="{IX + IW - 12}" y="{IY + IH - 12}" text-anchor="end" fill="#2b3320">the ground: a jet flies at 11 km, Everest stands 8.8 km, both inside this line</text>
  </g>
  <g stroke="#f5ecd4" stroke-width="1">
    <line x1="{gx + cube / 2 + 18:.1f}" y1="{ground_y - cube:.1f}" x2="{gx + cube / 2 + 18:.1f}" y2="{ground_y:.1f}" marker-start="url(#tickw)" marker-end="url(#tickw)"/>
  </g>
  <text transform="translate({gx + cube / 2 + 34:.1f} {ground_y - cube / 2:.1f}) rotate(90)" text-anchor="middle" font-size="14" fill="#f5ecd4">2,220 km high (21:16)</text>

  <line x1="40" y1="{IY + IH + 22:.0f}" x2="920" y2="{IY + IH + 22:.0f}" stroke="#5a4a2c" stroke-width="0.6"/>
  <g font-size="12.5" fill="#3b2f1a">
    <text x="40" y="{IY + IH + 44:.0f}">Scripture names the city Jerusalem and brings it down to the new earth (21:2, 10) without placing it on a map. Centring it on</text>
    <text x="40" y="{IY + IH + 61:.0f}">today’s {centre_name} shows its size only; the first earth “passed away” and “the sea was no more” (21:1), so today’s coasts may not carry over.</text>
    <text x="40" y="{IY + IH + 84:.0f}">For comparison, 2,220 km is a little more than Perth to Adelaide (about 2,130 km). Map: azimuthal equidistant projection centred on</text>
    <text x="40" y="{IY + IH + 101:.0f}">{centre_name}, so distances from the centre are true. Coastlines from Natural Earth (public domain).</text>
  </g>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--centre', nargs=2, type=float, default=(31.778, 35.235), metavar=('LAT', 'LON'))
    parser.add_argument('--centre-name', default='Jerusalem')
    parser.add_argument('--out', default='docs/content/assets/img/new-jerusalem-scale.svg')
    parser.add_argument('--cache', default=str(Path(tempfile.gettempdir()) / 'natural-earth'))
    args = parser.parse_args()
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    svg = build(*args.centre, args.centre_name, cache)
    Path(args.out).write_text(svg, encoding='utf-8')
    print(f'wrote {args.out} ({len(svg):,} bytes)')


if __name__ == '__main__':
    main()
