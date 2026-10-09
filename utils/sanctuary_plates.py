"""Draws the plates for the jesus/the-heavenly-pattern/ series: one SVG per furnishing, built from
what Scripture states about it. Stdlib only.

    python3 utils/sanctuary_plates.py              # every plate
    python3 utils/sanctuary_plates.py lampstand    # one plate

Each plate draws from a FACTS table in which every entry carries its source and a status:

    given      stated in the text: drawn solid
    inferred   derived from stated figures by arithmetic: drawn dashed, and the plate says how
    unstated   the text is silent: drawn dashed, labelled "not given", with any tradition that
               supplies it named as tradition

A plate that draws something Scripture does not state has to say so on the plate itself. The
lampstand is the sharpest case: Exodus gives no dimension at all, only counts and a weight, so
its height comes from the Talmud and its arm shape from two traditions that disagree -- the plate
draws one on each side.
"""
import argparse
from math import atan2, cos, degrees, radians, sin
from pathlib import Path

OUT_DIR = Path('docs/content/assets/img')

INK = '#3b2f1a'
RULE = '#5a4a2c'
MUTED = '#7a6d57'
PAPER = '#faf5e8'
DASH = 'stroke-dasharray="5 4"'

LAMPSTAND_FACTS = [
    ('One piece of hammered gold, base to flowers', 'given', 'Exodus 25:31, 36; Numbers 8:4'),
    ('Six branches, three from each side', 'given', 'Exodus 25:32'),
    ('Three almond cups on each branch, each with calyx and flower', 'given', 'Exodus 25:33'),
    ('Four almond cups on the shaft', 'given', 'Exodus 25:34'),
    ('A calyx under each pair of branches', 'given', 'Exodus 25:35'),
    ('Seven lamps, giving light in front of it', 'given', 'Exodus 25:37; Numbers 8:2'),
    ('A talent of gold with its utensils (about 34 kg)', 'given', 'Exodus 25:39'),
    ('Height, width, base', 'unstated', 'Talmud: 18 handbreadths high (b. Menahot 28b)'),
    ('Shape of the arms', 'unstated', 'curved: Arch of Titus; slantwise: Rashi on Exodus 25:32'),
    ('Order of the four shaft cups', 'unstated', 'spaced evenly here'),
    ('Lamps all at one level', 'unstated', 'Rashi on Exodus 25:32: tops level with the centre'),
]


LAMPSTAND_DESC = ("Plate in four parts. The lampstand of Exodus 25 in elevation: a central shaft and six branches, three on each side, with seven lamps at one level (Rashi's reading), three almond cups with calyx and flower on each branch, four cups on the shaft and a calyx under each pair of branches. The left arms are drawn curved, as on the Arch of Titus; the right arms straight and slanting, as Rashi describes them; the height of eighteen handbreadths comes from the Talmud, since Scripture gives no dimension. Beside it, what Exodus states and what it leaves unstated. Below, a plan of the Holy Place with the table on the north, the lampstand on the south and the incense altar before the veil; Zechariah's vision of a lampstand fed with oil from two olive trees; and a strip counting the lampstands from the tabernacle (one) through Solomon's temple (ten), Zechariah (one), the seven churches of Revelation 1, the two witnesses of Revelation 11, to the New Jerusalem, which has none because the Lamb is its lamp.")


def cup_group(x, y, deg, scale=1.0):
    """An almond cup, its calyx and its flower (Exodus 25:33), turned to follow the arm."""
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg:.1f}) scale({scale})">'
            '<path d="M-2.6 5 L2.6 5 L4.6 -2 L-4.6 -2 Z" fill="url(#gold)" stroke="#9a7424" stroke-width="0.7"/>'
            '<circle cx="0" cy="-5.2" r="3" fill="url(#gold)" stroke="#9a7424" stroke-width="0.7"/>'
            '<path d="M-6 -8.5 Q-3 -15 0 -9.5 Q3 -15 6 -8.5 Q0 -11 -6 -8.5 Z" fill="url(#gold)" '
            'stroke="#9a7424" stroke-width="0.7"/></g>')


def lamp(x, y):
    return (f'<g transform="translate({x:.1f},{y:.1f})">'
            '<ellipse cx="0" cy="0" rx="11" ry="5" fill="url(#gold)" stroke="#9a7424" stroke-width="0.8"/>'
            '<ellipse cx="0" cy="-13" rx="5" ry="10" fill="url(#flame)"/>'
            '<path d="M0 -21 Q3 -12 0 -5 Q-3 -12 0 -21 Z" fill="#fff6c8"/></g>')


def mini_lampstand(x, y, h, dashed=False):
    """A small seven-lamp icon for the strip that counts lampstands through Scripture."""
    style = f'fill="none" stroke="#b08a2e" stroke-width="2.2"{" " + DASH if dashed else ""}'
    top = y - h
    parts = [f'<line x1="{x}" y1="{y}" x2="{x}" y2="{top}" {style}/>',
             f'<line x1="{x - 7}" y1="{y}" x2="{x + 7}" y2="{y}" {style}/>']
    for i, s in enumerate((0.22, 0.36, 0.5)):
        w = h * s
        ya = top + h * (0.25 + 0.18 * i)
        parts.append(f'<path d="M{x} {ya:.1f} A{w:.1f} {ya - top:.1f} 0 0 1 {x - w:.1f} {top:.1f}" {style}/>')
        parts.append(f'<path d="M{x} {ya:.1f} A{w:.1f} {ya - top:.1f} 0 0 0 {x + w:.1f} {top:.1f}" {style}/>')
    for dx in (-0.5, -0.36, -0.22, 0, 0.22, 0.36, 0.5):
        parts.append(f'<circle cx="{x + dx * h:.1f}" cy="{top - 2:.1f}" r="2.4" fill="#f2b233"/>')
    return ''.join(parts)


def wrap_lines(text, width_chars):
    lines, line = [], ''
    for w in text.split():
        if len(line) + len(w) + 1 > width_chars and line:
            lines.append(line)
            line = w
        else:
            line = f'{line} {w}'.strip()
    return lines + [line]


def wrap(text, x, y, width_chars, size=13, colour=INK, anchor='start', leading=1.35, italic=False):
    lines = wrap_lines(text, width_chars)
    style = ' font-style="italic"' if italic else ''
    return ''.join(f'<text x="{x}" y="{y + i * size * leading:.1f}" font-size="{size}" fill="{colour}" '
                   f'text-anchor="{anchor}"{style}>{ln}</text>' for i, ln in enumerate(lines))


def facts_column(facts, heading, x=626, y=140):
    """The "What the text gives" list: stated facts solid, unstated ones dashed with their source."""
    rows = [f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="19" fill="{INK}">What the text gives</text>',
            f'<circle cx="{x + 6}" cy="{y + 26}" r="5" fill="#b08a2e"/><text x="{x + 20}" y="{y + 30}" font-size="11.5" fill="{INK}">stated: drawn solid</text>',
            f'<circle cx="{x + 6}" cy="{y + 46}" r="5" fill="{PAPER}" stroke="{MUTED}" stroke-width="1.3" {DASH}/><text x="{x + 20}" y="{y + 50}" font-size="11.5" fill="{MUTED}">not stated: dashed, or a tradition named</text>',
            f'<line x1="{x}" y1="{y + 66}" x2="920" y2="{y + 66}" stroke="{RULE}" stroke-width="0.6"/>',
            f'<text x="{x}" y="{y + 96}" font-size="12" fill="{INK}" font-weight="bold">{heading}</text>']
    fy = y + 122
    for text, status, src in facts:
        if status == 'given':
            rows.append(f'<circle cx="{x + 6}" cy="{fy - 4}" r="5" fill="#b08a2e"/>')
        else:
            rows.append(f'<circle cx="{x + 6}" cy="{fy - 4}" r="5" fill="{PAPER}" stroke="{MUTED}" stroke-width="1.3" {DASH}/>')
        rows.append(wrap(text, x + 20, fy, 36, 13, INK if status == 'given' else MUTED))
        n = 1 + len(text) // 36
        rows.append(wrap(src, x + 20, fy + 17 * n, 40, 11, MUTED, italic=True))
        fy += 17 * n + 15 * (1 + len(src) // 40) + 12
    return '\n  '.join(rows)


def stage_strip(stages, icon, y, W, heading, note):
    """A row of stages across the foot of a plate: an icon, a label and a reference for each.

    `stages` is a list of (label, name, reference, vision). `vision` is True for a stage seen in a
    vision (drawn dashed), False for one on earth, and None where there is nothing left to draw --
    the New Jerusalem, which has no temple -- so a glow stands in its place.
    """
    step = (W - 120) / len(stages)
    parts = [f'<line x1="40" y1="{y - 112}" x2="{W - 40}" y2="{y - 112}" stroke="{RULE}" stroke-width="0.6"/>',
             f'<text x="{W / 2}" y="{y - 80}" text-anchor="middle" font-family="Georgia, serif" font-size="19" fill="{INK}">{heading}</text>',
             f'<text x="{W / 2}" y="{y - 62}" text-anchor="middle" font-size="11" fill="{MUTED}" font-style="italic">{note}</text>']
    width = max(14, int(step / 6.2))
    for i, (label, name, ref, vision) in enumerate(stages):
        x = 60 + step * (i + 0.5)
        parts.append(icon(x, y + 4, vision) if vision is not None else
                     f'<circle cx="{x}" cy="{y - 20}" r="26" fill="url(#glory)"/>')
        if label:
            parts.append(f'<text x="{x}" y="{y + 36}" font-family="Georgia, serif" font-size="22" fill="{INK}" '
                         f'text-anchor="middle">{label}</text>')
        parts.append(wrap(name, x, y + 56, width, 12.5, INK, anchor='middle'))
        parts.append(wrap(ref, x, y + 56 + 17 * len(wrap_lines(name, width)), width + 4, 10.5, MUTED,
                          anchor='middle', italic=True))
        if i:
            parts.append(f'<text x="{x - step / 2}" y="{y - 12}" font-size="16" fill="{MUTED}" '
                         f'text-anchor="middle">›</text>')
    return '\n  '.join(parts)


def plate(W, H, title, subtitle, alt_title, desc, body):
    """The frame, gradients and title every plate shares, around a plate's own body."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" role="img" aria-labelledby="t d">
  <title id="t">{alt_title}</title>
  <desc id="d">{desc}</desc>
  <defs>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fbe7a1"/><stop offset="0.5" stop-color="#eec95c"/><stop offset="1" stop-color="#d9a93a"/>
    </linearGradient>
    <radialGradient id="flame" cx="50%" cy="65%" r="60%">
      <stop offset="0" stop-color="#fff3b0"/><stop offset="0.6" stop-color="#f7b733" stop-opacity="0.9"/><stop offset="1" stop-color="#f08a24" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glory" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#fffdf2"/><stop offset="0.45" stop-color="#fff0b8"/><stop offset="1" stop-color="#fff0b8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="smoke" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#b9b2c9" stop-opacity="0.9"/><stop offset="1" stop-color="#d9d4e3" stop-opacity="0"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0 L10 5 L0 10 Z" fill="#e0a526"/>
    </marker>
  </defs>

  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  <rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="none" stroke="{RULE}" stroke-width="1.5"/>
  <rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="{RULE}" stroke-width="0.6"/>

  <text x="{W / 2}" y="58" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" fill="{INK}" letter-spacing="1">{title}</text>
  <text x="{W / 2}" y="84" text-anchor="middle" font-size="14" fill="{MUTED}" font-style="italic">{subtitle}</text>
{body}
</svg>
'''


def dimension(x1, y1, x2, y2, label, dashed=False, side=1):
    """A dimension line with end ticks and a label beside its middle."""
    style = f'stroke="{MUTED}" stroke-width="1"{" " + DASH if dashed else ""}'
    vertical = x1 == x2
    tx, ty = ((x1 + 12 * side, (y1 + y2) / 2 + 4) if vertical else ((x1 + x2) / 2, y1 + 16 * side + (4 if side > 0 else 0)))
    anchor = ('start' if side > 0 else 'end') if vertical else 'middle'
    ticks = ((f'<line x1="{x1 - 5}" y1="{y1}" x2="{x1 + 5}" y2="{y1}" {style}/><line x1="{x2 - 5}" y1="{y2}" x2="{x2 + 5}" y2="{y2}" {style}/>')
             if vertical else
             (f'<line x1="{x1}" y1="{y1 - 5}" x2="{x1}" y2="{y1 + 5}" {style}/><line x1="{x2}" y1="{y2 - 5}" x2="{x2}" y2="{y2 + 5}" {style}/>'))
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {style}/>{ticks}'
            f'<text x="{tx}" y="{ty}" font-size="11.5" fill="{MUTED if dashed else INK}" text-anchor="{anchor}">{label}</text>')


def scale_bar(x, y, cubit, note=''):
    return (f'<line x1="{x}" y1="{y}" x2="{x + cubit}" y2="{y}" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}" stroke="{INK}"/>'
            f'<line x1="{x + cubit}" y1="{y - 5}" x2="{x + cubit}" y2="{y + 5}" stroke="{INK}"/>'
            f'<text x="{x + cubit / 2}" y="{y + 18}" text-anchor="middle" font-size="11.5" fill="{INK}">1 cubit (about 45 cm)</text>'
            + (wrap(note, x + cubit + 18, y - 4, 50, 11, MUTED, italic=True) if note else ''))


def build_lampstand():
    W, H = 960, 1500
    cx, y0, floor = 330, 250, 700  # shaft centre, lamp level, floor
    cubit = (floor - y0) / 3  # the Talmud's 18 handbreadths = 3 cubits of 6 handbreadths
    base_top = floor - 42
    pairs = [(345, 72), (440, 138), (535, 204)]  # (junction y, half-span): inner, middle, outer

    arms, cups, knobs, lamps = [], [], [], [lamp(cx, y0)]
    for ya, s in pairs:
        h = ya - y0
        # Left: the curved arm of the Arch of Titus, a quarter ellipse from the junction to lamp level.
        arms.append(f'<path d="M{cx} {ya} A{s} {h} 0 0 1 {cx - s} {y0}" fill="none" stroke="url(#gold)" '
                    f'stroke-width="7" stroke-linecap="round"/>')
        for t in (0.45, 0.66, 0.86):
            phi = radians(90 + 90 * t)
            px, py = cx + s * cos(phi), y0 + h * sin(phi)
            tx, ty = -s * sin(phi), h * cos(phi)
            cups.append(cup_group(px, py, degrees(atan2(tx, -ty))))
        # Right: Rashi's "slantwise" arm, a straight line to the same height.
        arms.append(f'<line x1="{cx}" y1="{ya}" x2="{cx + s}" y2="{y0}" stroke="url(#gold)" '
                    f'stroke-width="7" stroke-linecap="round"/>')
        for t in (0.4, 0.6, 0.8):
            cups.append(cup_group(cx + s * t, ya - h * t, degrees(atan2(s, h))))
        knobs.append(f'<circle cx="{cx}" cy="{ya + 11}" r="6.5" fill="url(#gold)" stroke="#9a7424" '
                     f'stroke-width="0.9"/>')
        lamps += [lamp(cx - s, y0), lamp(cx + s, y0)]
    shaft_cups = [cup_group(cx, y, 0, 1.25) for y in (300, 395, 490, 600)]

    top_w = pairs[-1][1]
    dim_x = cx + top_w + 34
    scale_y = floor + 38

    # Panel B: the Holy Place. Twenty by ten cubits is inferred, not stated -- see the note on it.
    bx, by, bs = 60, 970, 13  # origin and px per cubit
    hp_w, hp_h = 20 * bs, 10 * bs
    table_x, lamp_x = bx + 7 * bs, bx + 7 * bs
    panel_b = f'''
  <text x="{bx}" y="{by - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}">Where it stood</text>
  {wrap("Exodus 26:35; 40:24. The table on the north side, the lampstand on the south opposite it, the incense altar before the veil (Exodus 30:6).", bx, by - 42, 58, 11.5, MUTED)}
  <rect x="{bx}" y="{by}" width="{hp_w}" height="{hp_h}" fill="#f3ead2" stroke="{RULE}" stroke-width="1.2" {DASH}/>
  <line x1="{bx}" y1="{by}" x2="{bx}" y2="{by + hp_h}" stroke="#7b4a7a" stroke-width="4"/>
  <text x="{bx - 8}" y="{by + hp_h / 2}" font-size="11" fill="#7b4a7a" text-anchor="middle" transform="rotate(-90 {bx - 8} {by + hp_h / 2})">veil</text>
  <text x="{bx + hp_w + 12}" y="{by + hp_h / 2 + 4}" font-size="11" fill="{MUTED}">east: entrance</text>
  <rect x="{table_x - 13}" y="{by + 10}" width="26" height="13" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{table_x}" y="{by + 37}" font-size="11" fill="{INK}" text-anchor="middle">table</text>
  <text x="{bx + hp_w - 6}" y="{by + 14}" font-size="10.5" fill="{MUTED}" text-anchor="end" font-style="italic">north</text>
  <circle cx="{lamp_x}" cy="{by + hp_h - 18}" r="8" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{lamp_x}" y="{by + hp_h - 32}" font-size="11" fill="{INK}" text-anchor="middle">lampstand</text>
  <text x="{bx + hp_w - 6}" y="{by + hp_h - 6}" font-size="10.5" fill="{MUTED}" text-anchor="end" font-style="italic">south</text>
  <rect x="{bx + 1.5 * bs - 6}" y="{by + hp_h / 2 - 6}" width="12" height="12" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{bx + 1.5 * bs + 12}" y="{by + hp_h / 2 + 4}" font-size="11" fill="{INK}">incense altar</text>
  <path d="M{lamp_x + 14} {by + hp_h - 26} Q{lamp_x + 60} {by + hp_h / 2} {table_x + 18} {by + 30}" fill="none" stroke="#e0a526" stroke-width="1.6" marker-end="url(#arrow)"/>
  {wrap("Its light falls across the room: the lamps give light “in front of the lampstand” (Numbers 8:2).", bx, by + hp_h + 22, 58, 11, MUTED, italic=True)}
  {wrap("Dashed: the room’s 20 × 10 cubits are worked out from the frames and curtains (Exodus 26), not stated.", bx, by + hp_h + 52, 58, 11, MUTED, italic=True)}'''

    # Panel C: Zechariah's lampstand -- a vision, so drawn as a diagram and not to any scale.
    zx, zy = 700, by + 70
    trees = ''.join(f'<g transform="translate({zx + d},{zy + 20})"><rect x="-3" y="10" width="6" height="40" '
                    f'fill="#8a6a3a"/><ellipse cx="0" cy="0" rx="34" ry="30" fill="#6f9a52" stroke="#3f6b2e"/>'
                    f'<circle cx="-10" cy="-6" r="3.2" fill="#3d4a26"/><circle cx="8" cy="4" r="3.2" fill="#3d4a26"/>'
                    f'<circle cx="12" cy="-12" r="3.2" fill="#3d4a26"/></g>' for d in (-120, 120))
    z_lamps = ''.join(f'<circle cx="{zx + d}" cy="{zy - 40}" r="6" fill="url(#gold)" stroke="#9a7424"/>'
                      f'<line x1="{zx}" y1="{zy - 22}" x2="{zx + d}" y2="{zy - 36}" stroke="#b08a2e" stroke-width="1.2"/>'
                      for d in (-54, -36, -18, 0, 18, 36, 54))
    panel_c = f'''
  <text x="{zx}" y="{by - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}" text-anchor="middle">What Zechariah saw</text>
  {wrap("Zechariah 4:2-3, 12. A vision, so no scale: a bowl on top, seven lamps, oil flowing from two olive trees through two golden pipes. No priest fills it.", zx - 175, by - 42, 60, 11.5, MUTED)}
  {trees}
  <ellipse cx="{zx}" cy="{zy - 18}" rx="30" ry="9" fill="url(#gold)" stroke="#9a7424"/>
  {z_lamps}
  <rect x="{zx - 4}" y="{zy - 10}" width="8" height="110" fill="url(#gold)" stroke="#9a7424" stroke-width="0.8"/>
  <rect x="{zx - 24}" y="{zy + 98}" width="48" height="6" rx="3" fill="url(#gold)" stroke="#9a7424" stroke-width="0.8"/>
  <path d="M{zx - 100} {zy + 8} Q{zx - 60} {zy - 30} {zx - 26} {zy - 20}" fill="none" stroke="#d9a93a" stroke-width="3"/>
  <path d="M{zx + 100} {zy + 8} Q{zx + 60} {zy - 30} {zx + 26} {zy - 20}" fill="none" stroke="#d9a93a" stroke-width="3"/>
  {wrap("“Not by might, nor by power, but by my Spirit” (Zechariah 4:6, ESV)", zx, zy + 132, 46, 12, INK, anchor="middle", italic=True)}
  {wrap("Each lamp has “seven lips” (ESV) or “seven pipes” (WEB): the Hebrew allows both.", zx, zy + 168, 50, 11, MUTED, anchor="middle")}'''

    # Panel D: how many lampstands, stage by stage.
    stages = [
        ('1', 'Tabernacle', 'Exodus 25:31', False),
        ('10', 'Solomon’s temple', '1 Kings 7:49', False),
        ('1', 'Zechariah’s vision', 'Zechariah 4:2', True),
        ('7', 'Churches of Asia', 'Revelation 1:20', True),
        ('2', 'Two witnesses', 'Revelation 11:4', True),
        ('0', 'New Jerusalem', '“its lamp is the Lamb” (Revelation 21:23)', None),
    ]
    strip = stage_strip(stages, lambda x, y, vision: mini_lampstand(x, y, 44, dashed=vision),
                        1370, W, 'How many lampstands', 'Dashed icons are seen in visions.')

    body = f'''
  <text x="{cx}" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="19" fill="{INK}">What Moses was told to make</text>
  <text x="{cx - 120}" y="172" text-anchor="middle" font-size="12" fill="{MUTED}">curved arms</text>
  <text x="{cx - 120}" y="187" text-anchor="middle" font-size="10.5" fill="{MUTED}" font-style="italic">Arch of Titus, Rome, after AD 70</text>
  <text x="{cx + 120}" y="172" text-anchor="middle" font-size="12" fill="{MUTED}">straight arms</text>
  <text x="{cx + 120}" y="187" text-anchor="middle" font-size="10.5" fill="{MUTED}" font-style="italic">Rashi on Exodus 25:32: “slantwise”</text>
  <line x1="{cx}" y1="200" x2="{cx}" y2="222" stroke="{MUTED}" stroke-width="0.8" {DASH}/>

  <circle cx="{cx}" cy="{y0 + 70}" r="{top_w + 20}" fill="url(#glory)" opacity="0.45"/>
  {''.join(arms)}
  <rect x="{cx - 5}" y="{y0}" width="10" height="{base_top - y0}" fill="url(#gold)" stroke="#9a7424" stroke-width="0.8"/>
  {''.join(knobs)}
  {''.join(cups)}
  {''.join(shaft_cups)}
  {''.join(lamps)}
  <path d="M{cx - 5} {base_top} L{cx - 46} {floor} L{cx + 46} {floor} L{cx + 5} {base_top} Z" fill="none" stroke="{MUTED}" stroke-width="1.3" {DASH}/>
  <text x="{cx - 56}" y="{floor - 8}" text-anchor="end" font-size="11" fill="{MUTED}" font-style="italic">base: shape not given</text>
  <line x1="{cx - 230}" y1="{floor}" x2="{cx + 230}" y2="{floor}" stroke="{RULE}" stroke-width="0.8"/>

  <line x1="{dim_x}" y1="{y0}" x2="{dim_x}" y2="{floor}" stroke="{MUTED}" stroke-width="1" {DASH}/>
  <line x1="{dim_x - 6}" y1="{y0}" x2="{dim_x + 6}" y2="{y0}" stroke="{MUTED}"/>
  <line x1="{dim_x - 6}" y1="{floor}" x2="{dim_x + 6}" y2="{floor}" stroke="{MUTED}"/>
  <text x="{dim_x + 14}" y="{(y0 + floor) / 2}" font-size="11.5" fill="{MUTED}" text-anchor="middle" transform="rotate(90 {dim_x + 14} {(y0 + floor) / 2})">height not given</text>

  <line x1="{cx - 150}" y1="{scale_y}" x2="{cx - 150 + cubit}" y2="{scale_y}" stroke="{INK}" stroke-width="2"/>
  <line x1="{cx - 150}" y1="{scale_y - 5}" x2="{cx - 150}" y2="{scale_y + 5}" stroke="{INK}"/>
  <line x1="{cx - 150 + cubit}" y1="{scale_y - 5}" x2="{cx - 150 + cubit}" y2="{scale_y + 5}" stroke="{INK}"/>
  <text x="{cx - 150 + cubit / 2}" y="{scale_y + 18}" text-anchor="middle" font-size="11.5" fill="{INK}">1 cubit (about 45 cm)</text>
  {wrap("Drawn at the Talmud’s height of eighteen handbreadths, three cubits (b. Menahot 28b). Scripture gives the lampstand counts and a weight, and no measurement.", cx - 150 + cubit + 18, scale_y - 4, 50, 11, MUTED, italic=True)}

  {facts_column(LAMPSTAND_FACTS, 'Exodus 25:31-40; 37:17-24')}

  <line x1="40" y1="{by - 110}" x2="{W - 40}" y2="{by - 110}" stroke="{RULE}" stroke-width="0.6"/>
  {panel_b}
  {panel_c}

  {strip}'''
    return plate(W, H, 'The Golden Lampstand',
                 '“See that you make them after the pattern for them, which is being shown you on the mountain” (Exodus 25:40, ESV)',
                 'The golden lampstand, Exodus 25:31-40',
                 LAMPSTAND_DESC, body)


ALTAR_FACTS = [
    ('One cubit long, one cubit wide, square', 'given', 'Exodus 30:2'),
    ('Two cubits high', 'given', 'Exodus 30:2'),
    ('Horns of one piece with it', 'given', 'Exodus 30:2'),
    ('Acacia wood overlaid with pure gold: top, sides and horns', 'given', 'Exodus 30:1, 3'),
    ('A gold molding around it', 'given', 'Exodus 30:3'),
    ('Two gold rings under the molding, holding poles of gold-covered acacia', 'given', 'Exodus 30:4-5'),
    ('Before the veil, in front of the mercy seat', 'given', 'Exodus 30:6'),
    ('Incense morning and twilight, when the lamps are tended', 'given', 'Exodus 30:7-8'),
    ('Blood on its horns once a year', 'given', 'Exodus 30:10'),
    ('Rings: two in all, or two on each side', 'unstated',
     'ESV, CSB, NASB: two in all; NIV: two on each side. Drawn as one a side'),
    ('Size of the horns, shape of the molding, length of the poles', 'unstated', 'not given'),
]

ALTAR_DESC = (
    "Plate in four parts. The golden altar of incense of Exodus 30 in elevation and plan, drawn to "
    "scale at one cubit square and two cubits high, with a horn at each corner, a gold molding, a "
    "ring under the molding on each side holding a pole, and incense smoke rising from the top; "
    "the size of the horns is dashed as not given. Beside it, what Exodus states and what it leaves "
    "unstated. Below, a plan of the tent with the altar before the veil, in line with the ark behind "
    "it, the lampstand on the south and the table on the north, and the Day of Atonement incense "
    "carried inside the veil from an altar the text does not name; the four ingredients of the holy incense in equal parts, seasoned with "
    "salt; and a strip following the altar from the tabernacle through Solomon's temple, King "
    "Uzziah, the priest Zechariah and the golden altar before the throne in Revelation 8 and 9, to "
    "the New Jerusalem, which has no temple.")


def mini_altar(x, y, vision):
    style = f'fill="none" stroke="#b08a2e" stroke-width="2.2"{" " + DASH if vision else ""}'
    return (f'<rect x="{x - 11}" y="{y - 34}" width="22" height="34" {style}/>'
            f'<path d="M{x - 13} {y - 34} l0 -6 l4 0 l0 6 M{x + 9} {y - 34} l0 -6 l4 0 l0 6" {style}/>'
            f'<path d="M{x} {y - 40} q-5 -5 0 -9 q5 -4 0 -8" fill="none" stroke="#a9a1bb" stroke-width="2"/>')


def build_incense_altar():
    W, H = 960, 1560
    cubit = 150
    cx, floor = 270, 690
    top = floor - 2 * cubit
    half = cubit / 2
    horn_w, horn_h = 16, 18
    ring_y = top + 34

    smoke = (f'<path d="M{cx} {top - 22} C{cx - 30} {top - 60} {cx + 34} {top - 90} {cx - 6} {top - 130} '
             f'C{cx - 40} {top - 170} {cx + 20} {top - 200} {cx - 10} {top - 230}" fill="none" stroke="url(#smoke)" '
             f'stroke-width="22" stroke-linecap="round" opacity="0.8"/>')
    horns = ''.join(f'<rect x="{x}" y="{top - horn_h}" width="{horn_w}" height="{horn_h}" fill="url(#gold)" '
                    f'stroke="{MUTED}" stroke-width="1" {DASH}/>' for x in (cx - half, cx + half - horn_w))
    rings = ''.join(f'<circle cx="{x}" cy="{ring_y}" r="7" fill="none" stroke="#9a7424" stroke-width="3"/>'
                    f'<circle cx="{x}" cy="{ring_y}" r="3.5" fill="#c9a24a"/>' for x in (cx - half - 9, cx + half + 9))
    altar = f'''
  <rect x="{cx - half}" y="{top}" width="{cubit}" height="{2 * cubit}" fill="url(#gold)" stroke="#9a7424" stroke-width="1.2"/>
  <rect x="{cx - half - 4}" y="{top + 8}" width="{cubit + 8}" height="9" fill="url(#gold)" stroke="#9a7424" stroke-width="0.9"/>
  {horns}
  {rings}
  <text x="{cx - half - 50}" y="{top - 4}" font-size="11" fill="{MUTED}" text-anchor="end" font-style="italic">horns: size not given</text>
  <text x="{cx + half + 22}" y="{top + 16}" font-size="11" fill="{INK}">gold molding</text>
  <text x="{cx + half + 22}" y="{ring_y + 4}" font-size="11" fill="{INK}">ring and pole end</text>
  <line x1="{cx - 190}" y1="{floor}" x2="{cx + 190}" y2="{floor}" stroke="{RULE}" stroke-width="0.8"/>
  {dimension(cx - half, floor + 22, cx + half, floor + 22, '1 cubit')}
  {dimension(cx - half - 25, top, cx - half - 25, floor, '2 cubits', side=-1)}'''

    # Plan: one cubit square, a horn at each corner, poles through the rings on two opposite sides.
    px, py, ps = 550, 470, 90
    plan_horns = ''.join(f'<rect x="{px + dx * (ps / 2 - 6) - 6}" y="{py + ps / 2 + dy * (ps / 2 - 6) - 6}" width="12" '
                         f'height="12" fill="#e7c25a" stroke="{MUTED}" {DASH}/>' for dx in (-1, 1) for dy in (-1, 1))
    plan = f'''
  <text x="{px}" y="{py - 30}" font-size="12" fill="{INK}" text-anchor="middle">plan</text>
  <line x1="{px - ps / 2 - 9}" y1="{py - 40}" x2="{px - ps / 2 - 9}" y2="{py + ps + 40}" stroke="#b08a2e" stroke-width="3" {DASH}/>
  <line x1="{px + ps / 2 + 9}" y1="{py - 40}" x2="{px + ps / 2 + 9}" y2="{py + ps + 40}" stroke="#b08a2e" stroke-width="3" {DASH}/>
  <rect x="{px - ps / 2}" y="{py}" width="{ps}" height="{ps}" fill="url(#gold)" stroke="#9a7424" stroke-width="1.2"/>
  {plan_horns}
  <circle cx="{px - ps / 2 - 9}" cy="{py + ps / 2}" r="6" fill="none" stroke="#9a7424" stroke-width="2.5"/>
  <circle cx="{px + ps / 2 + 9}" cy="{py + ps / 2}" r="6" fill="none" stroke="#9a7424" stroke-width="2.5"/>
  {wrap("Poles through the rings on two opposite sides (Exodus 30:4); their length is not given.", px - 80, py + ps + 62, 30, 10.5, MUTED, italic=True)}'''

    # Panel B: where it stood. The tent's 30 x 10 cubits and the veil at 10 from the west are inferred.
    bx, by, bs = 60, 990, 11
    tent_w, tent_h = 30 * bs, 10 * bs
    veil_x = bx + 10 * bs
    axis = by + tent_h / 2
    panel_b = f'''
  <text x="{bx}" y="{by - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}">Where it stood</text>
  {wrap("“In front of the veil that is above the ark of the testimony, in front of the mercy seat” (Exodus 30:6, ESV).", bx, by - 42, 60, 11.5, MUTED)}
  <rect x="{bx}" y="{by}" width="{tent_w}" height="{tent_h}" fill="#f3ead2" stroke="{RULE}" stroke-width="1.2" {DASH}/>
  <line x1="{veil_x}" y1="{by}" x2="{veil_x}" y2="{by + tent_h}" stroke="#7b4a7a" stroke-width="4"/>
  <text x="{veil_x}" y="{by - 6}" font-size="11" fill="#7b4a7a" text-anchor="middle">veil</text>
  <rect x="{bx + 5 * bs - 14}" y="{axis - 9}" width="28" height="18" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{bx + 5 * bs}" y="{axis + 26}" font-size="11" fill="{INK}" text-anchor="middle">ark</text>
  <rect x="{veil_x + 2 * bs - 7}" y="{axis - 7}" width="14" height="14" fill="url(#gold)" stroke="#9a7424" stroke-width="1.4"/>
  <text x="{veil_x + 2 * bs + 12}" y="{axis + 4}" font-size="11" fill="{INK}" font-weight="bold">altar of incense</text>
  <rect x="{veil_x + 10 * bs - 13}" y="{by + 10}" width="26" height="13" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{veil_x + 10 * bs}" y="{by + 37}" font-size="11" fill="{INK}" text-anchor="middle">table (north)</text>
  <circle cx="{veil_x + 10 * bs}" cy="{by + tent_h - 18}" r="8" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{veil_x + 10 * bs}" y="{by + tent_h - 32}" font-size="11" fill="{INK}" text-anchor="middle">lampstand (south)</text>
  <text x="{bx + tent_w + 10}" y="{axis + 4}" font-size="11" fill="{MUTED}">east: entrance</text>
  <path d="M{veil_x + 18} {axis + 34} Q{veil_x} {axis - 44} {bx + 5 * bs + 20} {axis - 14}" fill="none" stroke="#a9a1bb" stroke-width="2" {DASH} marker-end="url(#arrow)"/>
  {wrap("Dashed arrow: once a year the high priest took coals “from the altar before the LORD” and incense inside the veil, so that its cloud covered the mercy seat (Leviticus 16:12-13); which altar is not said. Solomon’s altar is “the altar that belonged to the inner sanctuary” (1 Kings 6:22). Worked out, not stated: the tent’s 30 × 10 cubits (Exodus 26), the veil’s line, and the altar’s exact place in front of it.", bx, by + tent_h + 22, 64, 11, MUTED, italic=True)}'''

    # Panel C: the incense, four spices in equal parts (Exodus 30:34-35).
    ix, iy = 560, by
    jars = ''.join(
        f'<g transform="translate({ix + 30 + i * 90},{iy + 40})"><path d="M-18 0 Q-22 40 -12 52 L12 52 Q22 40 18 0 Z" '
        f'fill="#efe3c2" stroke="#9a7424"/><rect x="-14" y="-8" width="28" height="9" rx="2" fill="#d9c28a" stroke="#9a7424"/>'
        f'<text x="0" y="74" font-size="11.5" fill="{INK}" text-anchor="middle">{name}</text></g>'
        for i, name in enumerate(('stacte', 'onycha', 'galbanum', 'frankincense')))
    pluses = ''.join(f'<text x="{ix + 75 + i * 90}" y="{iy + 72}" font-size="16" fill="{MUTED}" text-anchor="middle">+</text>'
                     for i in range(3))
    panel_c = f'''
  <text x="{ix}" y="{iy - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}">The holy incense</text>
  {wrap("Exodus 30:34-38. Four spices “of each … an equal part,” blended as by a perfumer, “seasoned with salt, pure and holy” (ESV).", ix, iy - 42, 58, 11.5, MUTED)}
  {jars}
  {pluses}
  <text x="{ix + 165}" y="{iy + 146}" font-size="12" fill="{INK}" text-anchor="middle">+ salt</text>
  {wrap("Some was beaten very small and put “before the testimony” (Exodus 30:36). Making it for yourself was forbidden (Exodus 30:37-38).", ix, iy + 176, 58, 11, MUTED, italic=True)}'''

    stages = [
        ('', 'Tabernacle', 'Exodus 30:1-10', False),
        ('', 'Solomon: cedar overlaid with gold', '1 Kings 6:20-22', False),
        ('', 'Uzziah struck beside it', '2 Chronicles 26:19', False),
        ('', 'Zechariah’s prayer heard', 'Luke 1:11-13', False),
        ('', 'Before the throne', 'Revelation 8:3-5', True),
        ('', 'A voice from its horns', 'Revelation 9:13', True),
        ('', 'New Jerusalem: no temple', 'Revelation 21:22', None),
    ]
    strip = stage_strip(stages, mini_altar, 1420, W, 'Where the altar stands in Scripture',
                        'Dashed icons are seen in visions.')

    body = f'''
  <text x="{cx}" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="19" fill="{INK}">What Moses was told to make</text>
  {smoke}
  {altar}
  {plan}
  {scale_bar(cx - 190, floor + 70, cubit, "Drawn to scale: Exodus 30:2 gives every main dimension.")}
  {facts_column(ALTAR_FACTS, 'Exodus 30:1-10; 37:25-28')}

  <line x1="40" y1="{by - 110}" x2="{W - 40}" y2="{by - 110}" stroke="{RULE}" stroke-width="0.6"/>
  {panel_b}
  {panel_c}

  {strip}'''
    return plate(W, H, 'The Golden Altar of Incense',
                 '“In front of the mercy seat that is above the testimony, where I will meet with you” (Exodus 30:6, ESV)',
                 'The golden altar of incense, Exodus 30:1-10', ALTAR_DESC, body)


ARK_FACTS = [
    ('Acacia wood, 2½ × 1½ × 1½ cubits', 'given', 'Exodus 25:10'),
    ('Pure gold inside and out, with a gold molding around', 'given', 'Exodus 25:11'),
    ('Four gold rings on its four feet, two on each side', 'given', 'Exodus 25:12'),
    ('Poles of gold-covered acacia, never taken out', 'given', 'Exodus 25:13-15'),
    ('The testimony put inside it', 'given', 'Exodus 25:16, 21'),
    ('Mercy seat of pure gold, 2½ × 1½ cubits', 'given', 'Exodus 25:17'),
    ('Two cherubim of hammered gold, one piece with the mercy seat', 'given', 'Exodus 25:18-19'),
    ('Wings spread above, faces to each other and toward the mercy seat', 'given', 'Exodus 25:20'),
    ('Thickness of the mercy seat', 'unstated', 'not given'),
    ('Size and form of the cherubim', 'unstated', 'not given; drawn as outlines'),
    ('“Feet” or “corners”', 'unstated', 'ASV, ESV: feet; KJV: corners'),
]

ARK_DESC = (
    "Plate in four parts. The ark of the covenant of Exodus 25 in side elevation, drawn to scale at "
    "two and a half by one and a half cubits: a gold chest with a molding, rings at its feet holding "
    "the poles, the tablets inside, and the mercy seat on top with a cherub at each end whose wings "
    "spread over it, the cherubim drawn as outlines because their form is not given. Beside it, what "
    "Exodus states and what it leaves unstated. Below, Solomon's inner sanctuary, a twenty-cubit "
    "cube, with two olivewood cherubim ten cubits high whose wings reach from wall to wall over the "
    "ark; what was kept in and before the ark; and a strip following the ark from Sinai through the "
    "wilderness, the Jordan, its capture, Uzzah, Solomon's temple and King Josiah, to Jeremiah's word "
    "that it would not be made again and John's sight of it in the temple in heaven.")


def mini_ark(x, y, vision):
    style = f'fill="none" stroke="#b08a2e" stroke-width="2.2"{" " + DASH if vision else ""}'
    return (f'<rect x="{x - 18}" y="{y - 20}" width="36" height="20" {style}/>'
            f'<line x1="{x - 28}" y1="{y - 6}" x2="{x + 28}" y2="{y - 6}" {style}/>'
            f'<path d="M{x - 16} {y - 22} q4 -18 14 -14 M{x + 16} {y - 22} q-4 -18 -14 -14" {style}/>')


def cherub_outline(x, base, facing, wing_to_x, wing_y, h):
    """A cherub as a dashed outline: Exodus never describes its form, only its place and its wings."""
    style = f'fill="none" stroke="{MUTED}" stroke-width="1.3" {DASH}'
    return (f'<path d="M{x - 7} {base} L{x - 5} {base - h * 0.55} Q{x} {base - h * 0.75} {x + 5} {base - h * 0.55} '
            f'L{x + 7} {base} Z" {style}/>'
            f'<circle cx="{x + 3 * facing}" cy="{base - h * 0.7}" r="{h * 0.08:.1f}" {style}/>'
            f'<path d="M{x} {base - h * 0.55} Q{(x + wing_to_x) / 2} {wing_y - h * 0.1} {wing_to_x} {wing_y}" '
            f'fill="none" stroke="#b08a2e" stroke-width="2.4"/>')


def build_ark():
    W, H = 960, 1540
    cubit = 120
    cx, floor = 280, 620
    L, Hh = 2.5 * cubit, 1.5 * cubit
    x0, top = cx - L / 2, floor - Hh
    seat = 10

    ark = f'''
  <circle cx="{cx}" cy="{top - 60}" r="46" fill="url(#glory)"/>
  <rect x="{x0}" y="{top}" width="{L}" height="{Hh}" fill="url(#gold)" stroke="#9a7424" stroke-width="1.2"/>
  <rect x="{x0 - 4}" y="{top - 2}" width="{L + 8}" height="8" fill="url(#gold)" stroke="#9a7424" stroke-width="0.9"/>
  <rect x="{x0}" y="{top - seat - 2}" width="{L}" height="{seat}" fill="#f6dc86" stroke="{MUTED}" stroke-width="1.2" {DASH}/>
  <line x1="{x0 - 70}" y1="{floor - 22}" x2="{x0 + L + 70}" y2="{floor - 22}" stroke="#b08a2e" stroke-width="7" stroke-linecap="round"/>
  <line x1="{x0 - 110}" y1="{floor - 22}" x2="{x0 - 70}" y2="{floor - 22}" stroke="#b08a2e" stroke-width="7" {DASH}/>
  <line x1="{x0 + L + 70}" y1="{floor - 22}" x2="{x0 + L + 110}" y2="{floor - 22}" stroke="#b08a2e" stroke-width="7" {DASH}/>
  <circle cx="{x0 + 24}" cy="{floor - 22}" r="8" fill="none" stroke="#9a7424" stroke-width="3"/>
  <circle cx="{x0 + L - 24}" cy="{floor - 22}" r="8" fill="none" stroke="#9a7424" stroke-width="3"/>
  {cherub_outline(x0 + 26, top - seat - 2, 1, cx - 6, top - 120, 110)}
  {cherub_outline(x0 + L - 26, top - seat - 2, -1, cx + 6, top - 120, 110)}
  <rect x="{cx - 34}" y="{top + 40}" width="30" height="44" rx="12" fill="none" stroke="{MUTED}" {DASH}/>
  <rect x="{cx + 4}" y="{top + 40}" width="30" height="44" rx="12" fill="none" stroke="{MUTED}" {DASH}/>
  <text x="{cx}" y="{top + 102}" font-size="10.5" fill="{INK}" text-anchor="middle">the testimony (inside)</text>
  <text x="{x0 + L + 10}" y="{top - 90}" font-size="11" fill="{MUTED}" font-style="italic">cherubim: form not given</text>
  <text x="{x0 + L + 10}" y="{top - 8}" font-size="11" fill="{MUTED}" font-style="italic">mercy seat: thickness not given</text>
  <text x="{x0 + L + 10}" y="{floor - 34}" font-size="11" fill="{INK}">ring at a foot, pole through it</text>
  <text x="{x0 - 110}" y="{floor - 34}" font-size="10.5" fill="{MUTED}" font-style="italic">poles: length not given</text>
  <line x1="{cx - 220}" y1="{floor}" x2="{cx + 220}" y2="{floor}" stroke="{RULE}" stroke-width="0.8"/>
  {dimension(x0, floor + 22, x0 + L, floor + 22, '2½ cubits')}
  {dimension(x0 + L + 130, top, x0 + L + 130, floor, '1½ cubits', side=-1)}'''

    # Panel B: Solomon's inner sanctuary, 20 cubits each way, in section (1 Kings 6:20, 23-27; 8:6-8).
    sx, sy, ss = 70, 950, 12
    room = 20 * ss
    rfloor = sy + room
    ark_w = 2.5 * ss
    ch_h = 10 * ss
    wing_y = rfloor - ch_h + 0.5 * ss
    wings = ''.join(f'<line x1="{a}" y1="{wing_y}" x2="{b}" y2="{wing_y}" stroke="#b08a2e" stroke-width="3"/>'
                    for a, b in ((sx, sx + 10 * ss), (sx + 10 * ss, sx + 20 * ss)))
    bodies = ''.join(f'<path d="M{c - 10} {rfloor} L{c - 7} {wing_y + 6} Q{c} {wing_y - 10} {c + 7} {wing_y + 6} L{c + 10} {rfloor} Z" '
                     f'fill="none" stroke="{MUTED}" stroke-width="1.3" {DASH}/>' for c in (sx + 5 * ss, sx + 15 * ss))
    panel_b = f'''
  <text x="{sx - 10}" y="{sy - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}">Under Solomon’s cherubim</text>
  {wrap("1 Kings 6:20, 23-27; 8:6-8. A 20-cubit cube. Two olivewood cherubim, each 10 cubits high, with wings of 5 cubits that reach wall to wall and touch in the middle.", sx - 10, sy - 42, 58, 11.5, MUTED)}
  <rect x="{sx}" y="{sy}" width="{room}" height="{room}" fill="#f3ead2" stroke="{RULE}" stroke-width="1.2"/>
  {wings}
  {bodies}
  <rect x="{sx + 10 * ss - ark_w / 2}" y="{rfloor - 1.5 * ss}" width="{ark_w}" height="{1.5 * ss}" fill="url(#gold)" stroke="#9a7424"/>
  <text x="{sx + 10 * ss}" y="{rfloor - 1.5 * ss - 6}" font-size="10.5" fill="{INK}" text-anchor="middle">ark</text>
  {dimension(sx + room + 14, sy, sx + room + 14, rfloor, '20 cubits')}
  {dimension(sx + room + 110, rfloor - ch_h, sx + room + 110, rfloor, '10 cubits')}
  {wrap("At this scale the ark is 2½ cubits long. The cherubim’s bodies are outlines; only their height and wings are given.", sx - 10, rfloor + 26, 58, 11, MUTED, italic=True)}'''

    # Panel C: what was kept in the ark, and what was kept before it.
    cx2, cy2 = 610, sy - 20
    panel_c = f'''
  <text x="{cx2}" y="{sy - 64}" font-family="Georgia, serif" font-size="19" fill="{INK}">In the ark, and before it</text>
  <rect x="{cx2 + 10}" y="{cy2 + 20}" width="90" height="54" fill="none" stroke="#9a7424" stroke-width="2"/>
  <rect x="{cx2 + 30}" y="{cy2 + 30}" width="22" height="34" rx="9" fill="#d9d2c0" stroke="#7a6d57"/>
  <rect x="{cx2 + 56}" y="{cy2 + 30}" width="22" height="34" rx="9" fill="#d9d2c0" stroke="#7a6d57"/>
  <path d="M{cx2 + 170} {cy2 + 64} q-12 -26 0 -34 l14 0 q12 8 0 34 Z" fill="url(#gold)" stroke="{MUTED}" {DASH}/>
  <line x1="{cx2 + 220}" y1="{cy2 + 66}" x2="{cx2 + 232}" y2="{cy2 + 6}" stroke="#8a6a3a" stroke-width="3" {DASH}/>
  <circle cx="{cx2 + 232}" cy="{cy2 + 8}" r="4" fill="#f3d6e0"/><circle cx="{cx2 + 227}" cy="{cy2 + 24}" r="3.5" fill="#f3d6e0"/>
  <text x="{cx2 + 55}" y="{cy2 + 94}" font-size="11" fill="{INK}" text-anchor="middle">the tablets</text>
  <text x="{cx2 + 55}" y="{cy2 + 108}" font-size="10.5" fill="{MUTED}" text-anchor="middle" font-style="italic">Exodus 25:16; 40:20</text>
  <text x="{cx2 + 200}" y="{cy2 + 94}" font-size="11" fill="{INK}" text-anchor="middle">manna jar, Aaron’s staff</text>
  <text x="{cx2 + 200}" y="{cy2 + 108}" font-size="10.5" fill="{MUTED}" text-anchor="middle" font-style="italic">“before the testimony”</text>
  <text x="{cx2 + 200}" y="{cy2 + 121}" font-size="10.5" fill="{MUTED}" text-anchor="middle" font-style="italic">Exodus 16:34; Numbers 17:10</text>
  {wrap("Hebrews 9:4 speaks of the ark “in which was” the jar, the staff and the tablets. In Solomon’s day “there was nothing in the ark except the two tablets of stone” (1 Kings 8:9, ESV).", cx2, cy2 + 150, 52, 11, MUTED, italic=True)}'''

    stages = [
        ('', 'Placed in the tabernacle', 'Exodus 40:20-21', False),
        ('', 'Went before them', 'Numbers 10:33', False),
        ('', 'Led across the Jordan', 'Joshua 3:3', False),
        ('', 'Captured', '1 Samuel 4:11', False),
        ('', 'Uzzah struck', '2 Samuel 6:7', False),
        ('', 'Brought into the temple', '1 Kings 8:6', False),
        ('', 'Josiah: put it in the house', '2 Chronicles 35:3', False),
        ('', '“It shall not be made again”', 'Jeremiah 3:16', None),
        ('', 'Seen in the temple in heaven', 'Revelation 11:19', True),
    ]
    strip = stage_strip(stages, mini_ark, 1400, W, 'Where the ark went',
                        'Dashed: seen in a vision. In English Bible order, Jeremiah 3:16 is the last Old Testament book to name the ark.')

    body = f'''
  <text x="{cx}" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="19" fill="{INK}">What Moses was told to make</text>
  {ark}
  {scale_bar(cx - 220, floor + 70, cubit, "Drawn to scale from Exodus 25:10, 17. The cherubim and the mercy seat’s thickness are outlines.")}
  {facts_column(ARK_FACTS, 'Exodus 25:10-22; 37:1-9')}

  <line x1="40" y1="{sy - 110}" x2="{W - 40}" y2="{sy - 110}" stroke="{RULE}" stroke-width="0.6"/>
  {panel_b}
  {panel_c}

  {strip}'''
    return plate(W, H, 'The Ark of the Covenant',
                 '“There I will meet with you, and from above the mercy seat … I will speak with you” (Exodus 25:22, ESV)',
                 'The ark of the covenant, Exodus 25:10-22', ARK_DESC, body)


ALMOND_STATE = Path('references/study-state/almond.yml')
BLOSSOM = '#fdf4f2'
BLOSSOM_EDGE = '#d7a3a8'
BLOSSOM_HEART = '#b5536a'
LEAF = '#7d9a4c'
HULL = '#97a862'
SHELL = '#c49a5e'
WOOD = '#8a6a43'


def evidence_count(evidence_id):
    """A count the study verified, read from its state file's `evidence:` entry rather than retyped.
    The entries are one-line flow mappings, so a regex reads them without a YAML dependency."""
    import re
    line = next(ln for ln in ALMOND_STATE.read_text(encoding='utf-8').splitlines()
                if f'id: {evidence_id},' in ln)
    return int(re.search(r'expect_contains: "(\d+)"', line).group(1))


def blossom(x, y, r=7):
    petals = ''.join(f'<ellipse cx="{x + r * 0.62 * cos(radians(a)):.1f}" cy="{y + r * 0.62 * sin(radians(a)):.1f}" '
                     f'rx="{r * 0.55:.1f}" ry="{r * 0.42:.1f}" transform="rotate({a} {x + r * 0.62 * cos(radians(a)):.1f} '
                     f'{y + r * 0.62 * sin(radians(a)):.1f})" fill="{BLOSSOM}" stroke="{BLOSSOM_EDGE}" stroke-width="0.7"/>'
                     for a in range(-90, 270, 72))
    return petals + f'<circle cx="{x}" cy="{y}" r="{r * 0.22:.1f}" fill="{BLOSSOM_HEART}"/>'


def bud(x, y, r=4):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{r * 0.7:.1f}" ry="{r:.1f}" fill="#e9c3c3" stroke="{BLOSSOM_EDGE}" stroke-width="0.7"/>'
            f'<path d="M{x - r * 0.7:.1f} {y + r * 0.4:.1f} Q{x} {y + r * 1.6:.1f} {x + r * 0.7:.1f} {y + r * 0.4:.1f}" fill="{LEAF}"/>')


def almond(x, y, deg=0, ripe=True):
    """A fruit in its hull; a ripe one has split to show the shell (Numbers 17:8, "ripe almonds")."""
    split = (f'<path d="M0 -8 Q3 0 0 8 Q-3 0 0 -8 Z" fill="{SHELL}"/>' if ripe else '')
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg})">'
            f'<ellipse cx="0" cy="0" rx="6" ry="9.5" fill="{HULL}" stroke="#5f6e36" stroke-width="0.8"/>{split}</g>')


def leaf(x, y, deg):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.2" ry="9" transform="rotate({deg} {x:.1f} {y:.1f})" '
            f'fill="{LEAF}" stroke="#5c7434" stroke-width="0.5"/>')


def bare_staff(x, top, foot, dashed=False):
    style = f'stroke="{MUTED if dashed else WOOD}" stroke-width="5" stroke-linecap="round"' + (f' {DASH}' if dashed else '')
    if dashed:
        style = f'stroke="{MUTED}" stroke-width="2" {DASH}'
    return (f'<path d="M{x} {foot} Q{x + 3} {(top + foot) / 2} {x - 1} {top}" fill="none" {style}/>'
            f'<line x1="{x - 4}" y1="{top + 18}" x2="{x + 4}" y2="{top + 18}" stroke="{MUTED}" stroke-width="0.8"/>')


def blooming_staff(x, top, foot):
    """Aaron's staff the next morning: shoots, buds, blossoms and ripe almonds all drawn on it, since
    the plate has to show every verb. Whether all four stood on it at once is not stated; the key says so."""
    parts = [f'<path d="M{x} {foot} Q{x + 3} {(top + foot) / 2} {x - 1} {top}" fill="none" stroke="{WOOD}" '
             'stroke-width="6" stroke-linecap="round"/>']
    for i, y in enumerate(range(int(top) + 6, int(foot) - 40, 13)):
        side = -1 if i % 2 else 1
        parts.append(leaf(x + side * 9, y + 4, side * 50))
        kind = i % 4
        if kind == 0:
            parts.append(blossom(x + side * 15, y, 7.5))
        elif kind == 1:
            parts.append(almond(x + side * 14, y + 3, side * 20))
        elif kind == 2:
            parts.append(bud(x + side * 12, y))
        else:
            parts.append(blossom(x + side * 14, y + 2, 6.5))
    return ''.join(parts)


def heb(x, y, word, size=20, colour=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{colour}" text-anchor="middle" direction="rtl" font-family="\'SBL Hebrew\', \'Times New Roman\', serif">{word}</text>'


def section_head(W, y, title, note=''):
    out = [f'<line x1="40" y1="{y - 34}" x2="{W - 40}" y2="{y - 34}" stroke="{RULE}" stroke-width="0.6"/>',
           f'<text x="{W / 2}" y="{y}" text-anchor="middle" font-family="Georgia, serif" font-size="20" fill="{INK}">{title}</text>']
    if note:
        out.append(wrap(note, W / 2, y + 20, 88, 11.5, MUTED, anchor='middle', italic=True))
    return '\n  '.join(out)


ALMOND_DESC = ("Plate in four parts. First, the staffs before the testimony on the morning after (Numbers 17:4-9): a row of "
               "bare staffs, each with a name on it, and Aaron's in the middle covered in leaves, buds, white almond "
               "blossoms and ripe almonds; one bare staff is dashed because Numbers 17:6 can be read as twelve staffs "
               "with Aaron's or as twelve and Aaron's, thirteen. Second, the four verbs of Numbers 17:8 drawn as four "
               "stages of one branch: it sprouted (parach), brought out buds (yatsa with the noun perach), "
               "blossomed blossoms (tsuts with the noun tsits), and ripened almonds (gamal, with shaqed). Third, three things the staff shares a Hebrew word with: the lampstand's "
               "almond cups and their flower, perach (Exodus 25:33); the gold plate on Aaron's turban engraved Holy "
               "to the LORD, tsits (Exodus 28:36); and Jeremiah's almond branch, shaqed, which God answers with "
               "shoqed, 'I am watching' (Jeremiah 1:11-12). The words are stated; that Numbers meant the link is "
               "drawn dashed as likely. Fourth, where the staff went: back before the testimony (Numbers 17:10), "
               "possibly to the rock at Meribah (Numbers 20:9, dashed), with the ark (Hebrews 9:4; 1 Kings 8:9), "
               "and, as a type by resemblance only, the High Priest raised by the power of an indestructible life "
               "(Romans 1:4; Hebrews 7:16, dashed). Closing verse Jeremiah 1:12.")


def build_almond():
    W, H = 720, 1720
    shaqed, meshuqqad = evidence_count('shaqed-count'), evidence_count('meshuqqad-count')
    body = []

    # 1. The staffs on the morning after.
    body.append(section_head(W, 130, 'The next morning, before the testimony',
                             '“The staff of the man whom I choose shall sprout” (Numbers 17:5, ESV). '
                             'Each chief’s name was on his staff, and Aaron’s on Levi’s (17:2-3).'))
    foot, top = 400, 215
    body.append(f'<ellipse cx="{W / 2}" cy="{top + 70}" rx="250" ry="120" fill="url(#glory)" opacity="0.8"/>')
    body.append(f'<line x1="60" y1="{foot}" x2="{W - 60}" y2="{foot}" stroke="{RULE}" stroke-width="0.8" {DASH}/>')
    slots = 13
    step = (W - 140) / (slots - 1)
    aaron = slots // 2
    for i in range(slots):
        x = 70 + step * i
        if i == aaron:
            body.append(blooming_staff(x, top - 10, foot))
            body.append(f'<text x="{x}" y="{foot + 20}" text-anchor="middle" font-size="12" font-weight="bold" fill="{INK}">Aaron · Levi</text>')
        else:
            body.append(bare_staff(x, top + 20, foot, dashed=(i == slots - 1)))
    body.append(wrap('The other staffs are taken back unchanged, “and each man took his staff” (17:9).',
                     70 + step * 2.5, foot + 20, 30, 11, MUTED, anchor='middle', italic=True))
    body.append(wrap('Twelve with Aaron’s, or thirteen? (17:6) — the last staff is dashed.',
                     70 + step * 10, foot + 20, 30, 11, MUTED, anchor='middle', italic=True))
    body.append(f'<text x="{W / 2}" y="{foot + 78}" text-anchor="middle" font-size="11" fill="{MUTED}" font-style="italic">'
                'Their arrangement in the tent is not stated: the row and its ground line are dashed.</text>')

    # 2. Four verbs.
    y2 = 550
    body.append(section_head(W, y2, 'One night, four verbs (Numbers 17:8)',
                             'Two verbs carry their own noun, as in “blossomed blossoms.” Numbers does not say whether '
                             'all four stages stood on the staff at once.'))
    # (English, verb, verb transliteration, the noun it takes, noun transliteration). Two verbs carry
    # their own noun ("brought out buds", "blossomed blossoms"), and those nouns are the words the
    # staff shares with the lampstand and the high priest's plate below.
    stages = [('had sprouted', 'פָּרַח', 'parach, H6524', None, None),
              ('brought out buds', 'יָצָא', 'yatsa, H3318', 'פֶּרַח', 'perach, H6525'),
              ('blossomed blossoms', 'צוּץ', 'tsuts, H6692', 'צִיץ', 'tsits, H6731'),
              ('ripened almonds', 'גָּמַל', 'gamal, H1580', 'שְׁקֵדִים', 'shaqed, H8247')]
    col = (W - 80) / 4
    base = y2 + 190
    for i, (eng, word, xlit, noun, noun_xlit) in enumerate(stages):
        cx = 40 + col * (i + 0.5)
        body.append(f'<rect x="{cx - col / 2 + 8}" y="{y2 + 46}" width="{col - 16}" height="300" rx="6" fill="#fffdf6" stroke="{RULE}" stroke-width="0.8"/>')
        body.append(f'<path d="M{cx - 40} {base} Q{cx} {base - 30} {cx + 40} {base - 110}" fill="none" stroke="{WOOD}" stroke-width="5" stroke-linecap="round"/>')
        tips = [(cx - 14, base - 22), (cx + 8, base - 52), (cx + 28, base - 88)]
        for j, (tx, ty) in enumerate(tips):
            if i == 0:
                body.append(f'<path d="M{tx} {ty} q6 -12 16 -20" fill="none" stroke="{LEAF}" stroke-width="3.4" stroke-linecap="round"/>' + leaf(tx + 16, ty - 22, 50))
            elif i == 1:
                body.append(bud(tx + 2, ty - 8, 5))
            elif i == 2:
                body.append(blossom(tx + 2, ty - 10, 10))
            else:
                body.append(leaf(tx - 6, ty - 4, -40) + almond(tx + 4, ty - 10, 25))
        body.append(f'<text x="{cx}" y="{base + 34}" text-anchor="middle" font-size="13" fill="{INK}">{eng}</text>')
        body.append(heb(cx, base + 60, word, 20))
        body.append(f'<text x="{cx}" y="{base + 78}" text-anchor="middle" font-size="11" fill="{MUTED}" font-style="italic">{xlit}</text>')
        if noun:
            body.append(f'<text x="{cx}" y="{base + 96}" text-anchor="middle" font-size="10.5" fill="{MUTED}">noun:</text>')
            body.append(heb(cx, base + 114, noun, 16, '#5a4a2c'))
            body.append(f'<text x="{cx}" y="{base + 130}" text-anchor="middle" font-size="10.5" fill="{MUTED}" font-style="italic">{noun_xlit}</text>')
        if i:
            body.append(f'<text x="{40 + col * i}" y="{base - 40}" text-anchor="middle" font-size="18" fill="{MUTED}">›</text>')

    # 3. Words it shares.
    y3 = 970
    body.append(section_head(W, y3, 'The words the staff shares',
                             f'Shaqed, “almond,” occurs {shaqed} times in the Hebrew Bible; meshuqqad, “made like almond '
                             f'blossoms,” {meshuqqad} times, every one of them the lampstand.'))
    cards = [
        ('The lampstand’s flower', 'פֶּרַח', '“each with calyx and flower” — Exodus 25:33; Numbers 8:4',
         'Same noun as the staff’s “buds”: stated', 'That Numbers meant the link: likely'),
        ('Aaron’s gold plate', 'צִיץ', '“a plate of pure gold … ‘Holy to the LORD’” — Exodus 28:36',
         'Same noun as the staff’s “blossoms”: stated', 'That Numbers meant the link: likely'),
        ('Jeremiah’s almond branch', 'שָׁקֵד · שֹׁקֵד', '“I am watching over my word to perform it” — Jeremiah 1:11-12',
         'Almond / watching: God makes the pun', 'Heard in Numbers 17: a suggestion'),
    ]
    cw = (W - 100) / 3
    top3 = y3 + 52
    for i, (name, word, quote, stated, inferred) in enumerate(cards):
        x = 40 + i * (cw + 10)
        cx = x + cw / 2
        body.append(f'<rect x="{x}" y="{top3}" width="{cw}" height="270" rx="6" fill="#fffdf6" stroke="{RULE}" stroke-width="1"/>'.replace('height="270"', 'height="290"'))
        body.append(f'<text x="{cx}" y="{top3 + 24}" text-anchor="middle" font-family="Georgia, serif" font-size="14.5" fill="{INK}">{name}</text>')
        iy = top3 + 78
        if i == 0:
            body.append(cup_group(cx, iy + 12, 0, 3.2))
        elif i == 1:
            body.append(f'<rect x="{cx - 52}" y="{iy - 22}" width="104" height="40" rx="4" fill="url(#gold)" stroke="#9a7424"/>'
                        f'<line x1="{cx - 52}" y1="{iy - 2}" x2="{cx - 70}" y2="{iy - 2}" stroke="{BLUE_CORD}" stroke-width="2.5"/>'
                        f'<line x1="{cx + 52}" y1="{iy - 2}" x2="{cx + 70}" y2="{iy - 2}" stroke="{BLUE_CORD}" stroke-width="2.5"/>'
                        + heb(cx, iy + 4, 'קֹדֶשׁ לַיהוָה', 15, '#5a3f10'))
        else:
            body.append(f'<path d="M{cx - 50} {iy + 18} Q{cx - 5} {iy + 4} {cx + 48} {iy - 22}" fill="none" stroke="{WOOD}" stroke-width="4" stroke-linecap="round"/>'
                        + blossom(cx - 22, iy + 2, 9) + blossom(cx + 10, iy - 14, 8) + bud(cx + 40, iy - 30, 4.5)
                        + blossom(cx + 2, iy + 16, 7))
        body.append(heb(cx, top3 + 140, word, 20))
        body.append(wrap(quote, cx, top3 + 166, 27, 11, INK, anchor='middle', italic=True))
        body.append(f'<circle cx="{x + 14}" cy="{top3 + 225}" r="5" fill="#b08a2e"/>')
        body.append(wrap(stated, x + 26, top3 + 229, 30, 10.5, INK))
        body.append(f'<circle cx="{x + 14}" cy="{top3 + 253}" r="5" fill="{PAPER}" stroke="{MUTED}" stroke-width="1.3" {DASH}/>')
        body.append(wrap(inferred, x + 26, top3 + 257, 30, 10.5, MUTED))

    # 4. Where the staff went.
    y4 = 1490
    stops = [('Kept before the testimony', 'Numbers 17:10', False, 'staff'),
             ('Taken “from before the LORD” at Meribah?', 'Numbers 20:9 — 20:11 says “his staff”', True, 'rock'),
             ('With the ark', 'Hebrews 9:4; in it or before it, see 1 Kings 8:9', False, 'ark'),
             ('Life from the dead: a type', 'Romans 1:4; Hebrews 7:16 — resemblance, not stated', True, 'glory')]

    def stop_icon(kind, x, y, dashed):
        dash = f' {DASH}' if dashed else ''
        if kind == 'staff':
            return blooming_staff(x, y - 70, y)
        if kind == 'rock':
            return (f'<path d="M{x - 34} {y} L{x - 26} {y - 34} L{x - 4} {y - 46} L{x + 22} {y - 38} L{x + 34} {y} Z" '
                    f'fill="{EARTH}" stroke="{MUTED}" stroke-width="1.3"{dash}/>'
                    f'<path d="M{x + 6} {y - 12} q8 6 4 12" fill="none" stroke="#6f9bc4" stroke-width="2.5"/>')
        if kind == 'ark':
            return (f'<rect x="{x - 32}" y="{y - 30}" width="64" height="28" fill="url(#gold)" stroke="#9a7424"/>'
                    f'<rect x="{x - 34}" y="{y - 36}" width="68" height="7" fill="url(#gold)" stroke="#9a7424"/>'
                    f'<line x1="{x - 46}" y1="{y - 14}" x2="{x + 46}" y2="{y - 14}" stroke="{WOOD}" stroke-width="3"/>')
        return (f'<circle cx="{x}" cy="{y - 30}" r="34" fill="url(#glory)"/>'
                f'<circle cx="{x}" cy="{y - 30}" r="22" fill="none" stroke="#b08a2e" stroke-width="1.3" {DASH}/>')

    body.append(section_head(W, y4 - 120, 'Where the staff went',
                             '“To be kept as a sign for the rebels … lest they die” (Numbers 17:10, ESV)'))
    sw = (W - 80) / 4
    for i, (name, ref, dashed, kind) in enumerate(stops):
        cx = 40 + sw * (i + 0.5)
        body.append(stop_icon(kind, cx, y4 - 4, dashed))
        body.append(wrap(name, cx, y4 + 20, 20, 12.5, INK if not dashed else MUTED, anchor='middle'))
        body.append(wrap(ref, cx, y4 + 20 + 16 * len(wrap_lines(name, 20)), 24, 10.5, MUTED, anchor='middle', italic=True))
        if i:
            body.append(f'<text x="{40 + sw * i}" y="{y4 - 24}" text-anchor="middle" font-size="18" fill="{MUTED}">›</text>')

    body.append(f'<line x1="40" y1="{H - 104}" x2="{W - 40}" y2="{H - 104}" stroke="{RULE}" stroke-width="0.6"/>')
    body.append(f'<circle cx="190" cy="{H - 80}" r="5" fill="#b08a2e"/><text x="202" y="{H - 76}" font-size="11.5" fill="{INK}">stated: drawn solid</text>')
    body.append(f'<circle cx="370" cy="{H - 80}" r="5" fill="{PAPER}" stroke="{MUTED}" stroke-width="1.3" {DASH}/>'
                f'<text x="382" y="{H - 76}" font-size="11.5" fill="{MUTED}">not stated, or inferred: dashed</text>')
    body.append(f'<text x="{W / 2}" y="{H - 44}" text-anchor="middle" font-family="Georgia, serif" font-size="15" fill="{INK}" font-style="italic">'
                '“You have seen well, for I am watching over my word to perform it.”</text>')
    body.append(f'<text x="{W / 2}" y="{H - 26}" text-anchor="middle" font-size="11" fill="{MUTED}">Jeremiah 1:12, ESV</text>')

    return plate(W, H, 'The Almond', '“… and it bore ripe almonds” (Numbers 17:8, ESV)',
                 'The almond: Aaron’s staff, the lampstand and Jeremiah’s branch', ALMOND_DESC, '\n  '.join(body))


BLUE_CORD = '#2f5a8f'  # "a cord of blue" (Exodus 28:37)
EARTH = '#e6d6b8'


PLATES = {'lampstand': build_lampstand, 'incense-altar': build_incense_altar, 'ark': build_ark,
          'almond': build_almond}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('plates', nargs='*', metavar='plate', help=f'any of {", ".join(PLATES)} (default: all)')
    args = parser.parse_args()
    unknown = set(args.plates) - set(PLATES)
    if unknown:
        parser.error(f'no such plate: {", ".join(sorted(unknown))}')
    for name in args.plates or PLATES:
        out = OUT_DIR / f'sanctuary-{name}.svg'
        out.write_text(PLATES[name](), encoding='utf-8')
        print(f'wrote {out}')


if __name__ == '__main__':
    main()
