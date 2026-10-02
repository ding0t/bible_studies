"""Draw the feasts graphics: the year wheel for feasts.md and one medallion per feast study.

The wheel and the medallions share one set of pictograms and one status code, so a reader who
meets the Passover doorway on the overview sees the same doorway at the top of passover.md. Run
from the repo root after changing a pictogram or a status:

    python3 utils/build_feast_graphics.py

Status follows feasts.md, "The spring feasts and the first coming" and "The fall feasts and the
second coming": the four spring feasts are fulfilled, the Day of Atonement is half (the sacrifice
finished, Israel's national day ahead), Trumpets and Tabernacles await His return. The moon phases
are the calendar's own symbol: every month in Leviticus 23 began at the new moon.
"""

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "content" / "assets" / "img" / "feasts"

INK = "#3b2f1e"
MUTED = "#6b5a3e"
PAPER = "#faf6ec"
GOLD = "#e8c46a"
GOLD_EDGE = "#a67c3d"
BLOOD = "#8b1e1e"
LEAF = "#5e7d3a"
BREAD = "#e9cf98"
HORN = "#c9a46a"

SEASONS = [
    # (first month index, month count, name, note, fill)
    (0, 3, "Spring", "barley, then wheat harvest", "#dfe8c4"),
    (3, 3, "Summer", "dry season: grapes and figs", "#f2deb0"),
    (6, 2, "Autumn", "ingathering, early rain", "#ecd2b8"),
    (8, 4, "Winter", "the rains; the grain grows", "#d6e0e4"),
]

MONTHS = [
    ("ניסן", "Nisan", "Mar–Apr"),
    ("אייר", "Iyyar", "Apr–May"),
    ("סיון", "Sivan", "May–Jun"),
    ("תמוז", "Tammuz", "Jun–Jul"),
    ("אב", "Av", "Jul–Aug"),
    ("אלול", "Elul", "Aug–Sep"),
    ("תשרי", "Tishri", "Sep–Oct"),
    ("חשון", "Heshvan", "Oct–Nov"),
    ("כסלו", "Kislev", "Nov–Dec"),
    ("טבת", "Tevet", "Dec–Jan"),
    ("שבט", "Shevat", "Jan–Feb"),
    ("אדר", "Adar", "Feb–Mar"),
]

# slug, name lines, month index, day of its tick, status, when, the text that carries the status,
# placement angle. Leviticus dates Firstfruits and Weeks by count, not by day of the month.
FEASTS = [
    ("passover", ["Passover"], 0, 14, "full", "Nisan 14", "1 Cor 5:7", 140),
    ("unleavened-bread", ["Unleavened", "Bread"], 0, 15, "full", "Nisan 15–21", "1 Cor 5:8", 170),
    ("firstfruits", ["Firstfruits"], 0, 17, "full", "after the Sabbath", "1 Cor 15:20", 200),
    ("weeks", ["Weeks"], 2, 6, "full", "fifty days on", "Acts 2:1", 230),
    ("trumpets", ["Trumpets"], 6, 1, "new", "Tishri 1", "1 Thess 4:16?", 330),
    ("day-of-atonement", ["Atonement"], 6, 10, "half", "Tishri 10", "Heb 9:12; Zech 12:10", 0),
    ("tabernacles", ["Tabernacles"], 6, 15, "new", "Tishri 15–21", "Zech 14:16", 30),
]

STATUS_WORDS = {
    "full": "Fulfilled at His first coming",
    "half": "Sacrifice done; Israel's day ahead",
    "new": "Awaiting His return",
}


def icon(slug):
    """Each pictogram is drawn in a 64-unit box centred on the origin."""
    if slug == "passover":
        return f"""
      <rect x="-14" y="-16" width="28" height="40" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
      <rect x="-20" y="-24" width="40" height="8" rx="1" fill="{BLOOD}"/>
      <rect x="-20" y="-16" width="6" height="40" fill="{BLOOD}"/>
      <rect x="14" y="-16" width="6" height="40" fill="{BLOOD}"/>
      <line x1="-26" y1="24.5" x2="26" y2="24.5" stroke="{INK}" stroke-width="2"/>
      <path d="M-4 -30 q4 -4 8 0" fill="none" stroke="{LEAF}" stroke-width="2"/>"""
    if slug == "unleavened-bread":
        dots = "".join(
            f'<circle cx="{x}" cy="{y}" r="1.4" fill="{INK}"/>'
            for y in (-12, -4, 4, 12)
            for x in range(-16 + (4 if y in (-12, 12) else 0), 17 - (4 if y in (-12, 12) else 0), 5)
        )
        return f"""
      <circle r="24" fill="{BREAD}" stroke="{INK}" stroke-width="1.5"/>
      <path d="M-18 -8 h36 M-20 0 h40 M-18 8 h36" stroke="#b9894a" stroke-width="2" opacity=".55"/>
      {dots}"""
    if slug == "firstfruits":
        tips = [(-15, -20), (-8, -25), (0, -27), (8, -25), (15, -20)]
        stalks = "".join(f'<path d="M0 26 L{x * 0.25:.1f} 8 L{x} {y}" fill="none" stroke="#b08d3a" stroke-width="2"/>' for x, y in tips)
        heads = "".join(
            f'<ellipse cx="{x}" cy="{y - 4}" rx="3" ry="7" transform="rotate({x * 1.6:.0f} {x} {y - 4})" fill="#d9b350" stroke="#8a6a24" stroke-width="1"/>'
            for x, y in tips
        )
        return f"""
      {stalks}{heads}
      <rect x="-6" y="6" width="12" height="5" rx="1.5" fill="{BLOOD}"/>"""
    if slug == "weeks":
        loaf = (
            '<ellipse rx="15" ry="10" fill="#d8a95e" stroke="{ink}" stroke-width="1.5"/>'
            '<path d="M-8 -5 l4 9 M-1 -7 l4 10 M6 -5 l3 8" stroke="#8a5a24" stroke-width="1.6" fill="none"/>'
        ).format(ink=INK)
        return f"""
      <g transform="translate(-11 2) rotate(-18)">{loaf}</g>
      <g transform="translate(12 6) rotate(14)">{loaf}</g>
      <path d="M-22 18 h44" stroke="{INK}" stroke-width="1.5"/>"""
    if slug == "trumpets":
        return f"""
      <g transform="translate(-3 5) scale(.9)">
      <path d="M-26 14 C -14 18, 2 14, 12 -2 C 16 -9, 18 -16, 24 -22 L 28 -14 C 22 -10, 20 -2, 16 6 C 6 22, -12 24, -26 18 Z"
            fill="{HORN}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M-26 14 v4" stroke="{INK}" stroke-width="3"/>
      <path d="M-6 17 q2 -5 0 -9 M4 13 q3 -5 1 -10" stroke="#9c7a44" stroke-width="1.2" fill="none"/>
      </g>
      <path d="M24 -24 q4 5 0 10 M28 -28 q7 8 0 18" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>"""
    if slug == "day-of-atonement":
        return f"""
      <path d="M-20 0 C -24 -10, -16 -22, -3 -24 C -10 -16, -10 -8, -4 0 Z" fill="#f6e3a8" stroke="{INK}" stroke-width="1.3"/>
      <path d="M20 0 C 24 -10, 16 -22, 3 -24 C 10 -16, 10 -8, 4 0 Z" fill="#f6e3a8" stroke="{INK}" stroke-width="1.3"/>
      <rect x="-25" y="0" width="50" height="6" rx="1" fill="#f6e3a8" stroke="{INK}" stroke-width="1.3"/>
      <rect x="-22" y="6" width="44" height="18" fill="#c99a3c" stroke="{INK}" stroke-width="1.3"/>
      <circle cx="-6" cy="3" r="1.8" fill="{BLOOD}"/><circle cx="0" cy="3" r="1.8" fill="{BLOOD}"/><circle cx="6" cy="3" r="1.8" fill="{BLOOD}"/>"""
    if slug == "tabernacles":
        leaves = "".join(
            f'<ellipse cx="{x}" cy="{-12 + (3 if i % 2 else 0)}" rx="7" ry="3" transform="rotate({(-25 if i % 2 else 25)} {x} {-12 + (3 if i % 2 else 0)})" fill="{LEAF}"/>'
            for i, x in enumerate(range(-22, 23, 6))
        )
        return f"""
      <path d="M-20 -8 V24 M20 -8 V24 M-20 24 H20" stroke="#7a5a32" stroke-width="3" fill="none"/>
      <path d="M-20 4 H20" stroke="#7a5a32" stroke-width="1.5" opacity=".6"/>
      {leaves}
      <path d="M0 -30 l2.4 5 5.4 .8 -3.9 3.8 .9 5.4 -4.8 -2.6 -4.8 2.6 .9 -5.4 -3.9 -3.8 5.4 -.8z" fill="{GOLD}" stroke="{INK}" stroke-width=".8"/>"""
    raise ValueError(slug)


def medallion(slug, status, r, cx=0, cy=0, uid=""):
    """A moon-phase disc behind the pictogram: full, half (left lit), or new (an outline)."""
    scale = r / 36
    if status == "full":
        disc = f'<circle r="{r}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2.5"/>'
    elif status == "half":
        disc = (
            f'<circle r="{r}" fill="{PAPER}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="6 4"/>'
            f'<path d="M0 {-r} A{r} {r} 0 0 0 0 {r} Z" fill="{GOLD}"/>'
            f'<path d="M0 {-r} A{r} {r} 0 0 0 0 {r}" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.5"/>'
        )
    else:
        disc = f'<circle r="{r}" fill="{PAPER}" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    return f"""<g transform="translate({cx:.1f} {cy:.1f})">
    {disc}
    <g transform="scale({scale:.3f})">{icon(slug)}
    </g>
  </g>"""


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def annulus(cx, cy, r0, r1, a0, a1):
    large = 1 if (a1 - a0) % 360 > 180 else 0
    x0, y0 = polar(cx, cy, r1, a0)
    x1, y1 = polar(cx, cy, r1, a1)
    x2, y2 = polar(cx, cy, r0, a1)
    x3, y3 = polar(cx, cy, r0, a0)
    return (
        f"M{x0:.1f} {y0:.1f} A{r1} {r1} 0 {large} 1 {x1:.1f} {y1:.1f} "
        f"L{x2:.1f} {y2:.1f} A{r0} {r0} 0 {large} 0 {x3:.1f} {y3:.1f} Z"
    )


def arc_path(cx, cy, r, a0, a1, clockwise=True):
    large = 1 if (a1 - a0) % 360 > 180 else 0
    if clockwise:
        x0, y0 = polar(cx, cy, r, a0)
        x1, y1 = polar(cx, cy, r, a1)
        return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"
    x0, y0 = polar(cx, cy, r, a1)
    x1, y1 = polar(cx, cy, r, a0)
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 0 {x1:.1f} {y1:.1f}"


# Nisan sits at the left (180 degrees) and the year runs clockwise, so the spring feasts sit on the
# left, the summer harvest across the top, the seventh month on the right and winter underneath.
def month_start(i):
    return 165 + 30 * i


def day_angle(month, day):
    return month_start(month) + (day - 0.5)


def wheel():
    W, H = 900, 1000
    cx, cy = 450, 520
    r_core, r_month, r_season, r_orbit, r_med = 98, 205, 250, 330, 42
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" role="img" aria-labelledby="t d">',
        '<title id="t">The appointed times of the LORD through Israel\'s year</title>',
        '<desc id="d">A wheel of the Hebrew year, beginning with Nisan on the left and running clockwise: '
        "twelve months with their Hebrew names and approximate Gregorian months, ringed by the seasons. "
        "Around the outside, each of the seven feasts of Leviticus 23 is drawn as a moon with its picture, "
        "joined by a line to its day. The spring feasts are full gold moons, fulfilled at Christ's first coming: "
        "Passover, a blood-marked doorway (1 Corinthians 5:7); Unleavened Bread, a pierced flat loaf (1 Corinthians 5:8); "
        "Firstfruits, a barley sheaf (1 Corinthians 15:20); Weeks, two loaves (Acts 2:1). "
        "The seventh-month feasts await His return: Trumpets, a ram's horn, an outlined moon; "
        "the Day of Atonement, the mercy seat with blood, a half moon because the sacrifice is finished "
        "(Hebrews 9:12) and Israel's national day is ahead (Zechariah 12:10); Tabernacles, a booth of branches "
        "under a star, an outlined moon (Zechariah 14:16). A solid line joins the fulfilled feasts; a dashed line "
        "runs across the summer harvest to the feasts still to come.</desc>",
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        f'<text x="{cx}" y="52" text-anchor="middle" font-size="30" font-weight="bold" fill="{INK}">The appointed times of the LORD</text>',
        f'<text x="{cx}" y="84" text-anchor="middle" font-size="18" font-style="italic" fill="{MUTED}">Leviticus 23 · Israel\'s year, from “the beginning of months” (Exodus 12:2)</text>',
        f'<text x="34" y="150" font-size="20" font-weight="bold" fill="#7a5a14">Spring</text>',
        f'<text x="34" y="174" font-size="16" fill="{MUTED}">fulfilled at His first coming</text>',
        f'<text x="{W - 34}" y="150" text-anchor="end" font-size="20" font-weight="bold" fill="#7a5a14">The seventh month</text>',
        f'<text x="{W - 34}" y="174" text-anchor="end" font-size="16" fill="{MUTED}">awaiting His return</text>',
    ]

    defs = ["<defs>"]
    for i, (first, count, name, note, fill) in enumerate(SEASONS):
        a0 = month_start(first) + 1
        a1 = month_start(first + count) - 1
        out.append(f'<path d="{annulus(cx, cy, r_month + 2, r_season, a0, a1)}" fill="{fill}" stroke="{PAPER}" stroke-width="2"/>')
        mid = (a0 + a1) / 2 % 360
        bottom = 0 < mid < 180
        rr = (r_month + r_season) / 2 + (6 if bottom else -6)
        defs.append(f'<path id="season{i}" d="{arc_path(cx, cy, rr, a0, a1, clockwise=not bottom)}"/>')
        out.append(
            f'<text font-size="15" fill="{INK}"><textPath href="#season{i}" startOffset="50%" text-anchor="middle">'
            f'<tspan font-weight="bold">{name}</tspan> · {note}</textPath></text>'
        )
    defs.append("</defs>")
    out.insert(2, "".join(defs))

    seventh = 6
    for i, (heb, eng, greg) in enumerate(MONTHS):
        a0, a1 = month_start(i), month_start(i + 1)
        fill = "#f1e3c2" if i in (0, 2, seventh) else "#f7efdc"
        out.append(f'<path d="{annulus(cx, cy, r_core + 6, r_month, a0, a1)}" fill="{fill}" stroke="{GOLD_EDGE}" stroke-width="1"/>')
        mx, my = polar(cx, cy, 158, a0 + 15)
        out.append(f'<text x="{mx:.1f}" y="{my - 14:.1f}" text-anchor="middle" font-size="19" fill="{INK}" direction="rtl">{heb}</text>')
        out.append(f'<text x="{mx:.1f}" y="{my + 6:.1f}" text-anchor="middle" font-size="14" font-weight="bold" fill="{INK}">{i + 1} · {eng}</text>')
        out.append(f'<text x="{mx:.1f}" y="{my + 23:.1f}" text-anchor="middle" font-size="12" fill="{MUTED}">{greg}</text>')

    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="#efe2c4" stroke="{GOLD_EDGE}" stroke-width="1.5"/>')
    out.append(f'<text x="{cx}" y="{cy - 22}" text-anchor="middle" font-size="26" fill="{INK}" direction="rtl">מועדי יהוה</text>')
    out.append(f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="15" fill="{INK}">moʿade YHWH</text>')
    out.append(f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-size="13" font-style="italic" fill="{MUTED}">“my appointed feasts”</text>')
    out.append(f'<text x="{cx}" y="{cy + 44}" text-anchor="middle" font-size="13" fill="{MUTED}">Leviticus 23:2</text>')

    by_slug = {f[0]: f for f in FEASTS}
    first_angle, weeks_angle = by_slug["passover"][-1], by_slug["weeks"][-1]
    trumpets_angle, booths_angle = by_slug["trumpets"][-1], by_slug["tabernacles"][-1]
    out.append(f'<path d="{arc_path(cx, cy, r_orbit, first_angle, weeks_angle)}" fill="none" stroke="{GOLD_EDGE}" stroke-width="4"/>')
    out.append(f'<path d="{arc_path(cx, cy, r_orbit, weeks_angle, trumpets_angle + 360)}" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="3 7" stroke-linecap="round"/>')
    out.append(f'<path d="{arc_path(cx, cy, r_orbit, trumpets_angle, booths_angle + 360)}" fill="none" stroke="{GOLD_EDGE}" stroke-width="2.5" stroke-dasharray="10 6"/>')
    defs_summer = arc_path(cx, cy, r_orbit + 14, weeks_angle + 13, trumpets_angle - 13)
    out.append(f'<path id="summer" d="{defs_summer}" fill="none"/>')
    out.append(
        f'<text font-size="15" font-style="italic" fill="{MUTED}"><textPath href="#summer" startOffset="50%" text-anchor="middle">'
        "the summer harvest · gleanings left for the poor (Lev 23:22)</textPath></text>"
    )

    for slug, lines, month, day, status, when, ref, ang in FEASTS:
        tx, ty = polar(cx, cy, r_season + 3, day_angle(month, day))
        mx, my = polar(cx, cy, r_orbit, ang)
        ex, ey = polar(cx, cy, r_orbit - r_med, ang)
        out.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{MUTED}" stroke-width="1.3"/>')
        out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.5" fill="{INK}"/>')
        out.append(medallion(slug, status, r_med, mx, my))
        ly = my + r_med + 20
        halo = f'paint-order="stroke" stroke="{PAPER}" stroke-width="5" stroke-linejoin="round"'
        for k, line in enumerate(lines):
            out.append(f'<text x="{mx:.1f}" y="{ly + 19 * k:.1f}" text-anchor="middle" font-size="17" font-weight="bold" fill="{INK}" {halo}>{line}</text>')
        ly += 19 * len(lines) - 2
        out.append(f'<text x="{mx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="13" fill="{MUTED}" {halo}>{when}</text>')
        out.append(f'<text x="{mx:.1f}" y="{ly + 16:.1f}" text-anchor="middle" font-size="13" font-style="italic" fill="{MUTED}" {halo}>{ref}</text>')

    ly = H - 78
    out.append(f'<line x1="40" y1="{ly - 34}" x2="{W - 40}" y2="{ly - 34}" stroke="{GOLD_EDGE}" stroke-width="1"/>')
    for k, status in enumerate(("full", "half", "new")):
        x = (60, 335, 660)[k]
        out.append(f'<g transform="translate({x} {ly})">' + medallion_legend(status) + "</g>")
        out.append(f'<text x="{x + 30}" y="{ly + 6}" font-size="15" fill="{INK}">{STATUS_WORDS[status]}</text>')
    out.append(
        f'<text x="{cx}" y="{H - 24}" text-anchor="middle" font-size="13" font-style="italic" fill="{MUTED}">'
        "Every month began at the new moon. A full moon marks a feast the New Testament ties to His first coming; "
        "a “?” marks a link that is inferred.</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


def medallion_legend(status):
    r = 18
    if status == "full":
        return f'<circle r="{r}" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>'
    if status == "half":
        return (
            f'<circle r="{r}" fill="{PAPER}" stroke="{GOLD_EDGE}" stroke-width="2" stroke-dasharray="4 3"/>'
            f'<path d="M0 {-r} A{r} {r} 0 0 0 0 {r} Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="2"/>'
        )
    return f'<circle r="{r}" fill="{PAPER}" stroke="{GOLD_EDGE}" stroke-width="2" stroke-dasharray="4 3"/>'


def badge(slug, lines, status):
    name = " ".join(lines)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 100 100" role="img" aria-labelledby="t">
  <title id="t">{name}: {STATUS_WORDS[status].lower()}</title>
  {medallion(slug, status, 46)}
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "feasts-year-wheel.svg").write_text(wheel() + "\n", encoding="utf-8")
    for slug, lines, _month, _day, status, _when, _ref, _ang in FEASTS:
        (OUT / f"{slug}.svg").write_text(badge(slug, lines, status), encoding="utf-8")
    print(f"wrote {len(FEASTS) + 1} files to {OUT}")


if __name__ == "__main__":
    main()
