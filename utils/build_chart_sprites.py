"""Draw the History Chart's pictures into one SVG sprite sheet.

    python3 utils/build_chart_sprites.py

Writes docs/content/assets/chart/sprites.svg: a <symbol> for every vignette in
docs/data/chart-vignettes.toml (`v-<event id>`, a comic panel with no bubbles), an icon for each of
the creation days (`day-1` to `day-8`), one for each kind of text or artifact (`kind-*`), and
Nebuchadnezzar's image and the stone for the Daniel's kingdoms plate (`statue`, `stone`). The
chart (app/src/components/chronology/HistoryChart.jsx) places them with <use>, so each picture is
stored once however many sheets show it. Committed, like the comics, because CI does not run Python.
Re-run after editing the vignettes or the comic library.
"""

import tomllib
from pathlib import Path

from lib import comic
from lib.larkin import INK, esc

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "data" / "chart-vignettes.toml"
OUT = ROOT / "docs" / "content" / "assets" / "chart" / "sprites.svg"

VW, VH = 240, 180
LINE = f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
PALE = "#f3ead6"

# The creation days, for the band that maps each to its thousand years (2 Peter 3:8). Line drawings
# with a pale fill, so they read the same printed in black and white.
DAYS = {
    1: ("Light (Genesis 1:3-5)",
        f'<path d="M20 8 A12 12 0 0 1 20 32 Z" fill="{INK}"/><circle cx="20" cy="20" r="12" {LINE}/>'
        + "".join(f'<path d="M{20 + 15 * c:.1f} {20 + 15 * s:.1f} L{20 + 18 * c:.1f} {20 + 18 * s:.1f}" {LINE}/>'
                  for c, s in ((1, 0), (0.7, -0.7), (0, -1), (-0.7, -0.7), (-1, 0), (-0.7, 0.7), (0, 1), (0.7, 0.7)))),
    2: ("Waters divided by an expanse (Genesis 1:6-8)",
        f'<path d="M5 20 Q20 2 35 20" {LINE}/><path d="M4 28 q4 -4 8 0 t8 0 t8 0 t8 0" {LINE}/>'
        f'<path d="M4 35 q4 -4 8 0 t8 0 t8 0 t8 0" {LINE}/>'),
    3: ("Dry land and plants (Genesis 1:9-13)",
        f'<path d="M3 34 Q14 22 24 28 Q31 32 37 34 Z" fill="{PALE}" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M20 26 V10 M20 18 Q13 14 12 8 Q19 9 20 16 M20 14 Q27 10 28 5 Q21 6 20 12" {LINE}/>'),
    4: ("Sun, moon and stars (Genesis 1:14-19)",
        f'<circle cx="12" cy="15" r="8" fill="{PALE}" stroke="{INK}" stroke-width="2.2"/>'
        f'<path d="M31 6 A9 9 0 1 0 34 22 A7 7 0 1 1 31 6 Z" fill="{INK}"/>'
        f'<path d="M8 33 l1.5 -3 1.5 3 -3 -2 h3 z M20 29 l1.2 -2.4 1.2 2.4 -2.4 -1.6 h2.4 z M30 34 l1.2 -2.4 1.2 2.4 -2.4 -1.6 h2.4 z" fill="{INK}"/>'),
    5: ("Sea creatures and birds (Genesis 1:20-23)",
        f'<path d="M6 28 Q14 20 24 28 Q14 36 6 28 Z M24 28 L31 23 V33 Z" fill="{PALE}" stroke="{INK}" stroke-width="2"/>'
        f'<path d="M8 12 q5 -5 10 0 q5 -5 10 0" {LINE}/>'),
    6: ("Land animals and mankind (Genesis 1:24-31)",
        f'<path d="M4 30 V22 Q4 17 10 17 H20 Q24 17 25 13 L28 13 Q29 18 26 21 V30 M8 22 V30 M22 22 V30" {LINE}/>'
        f'<circle cx="33" cy="12" r="3" {LINE}/><path d="M33 15 V25 M33 25 L30 32 M33 25 L36 32 M29 19 H37" {LINE}/>'),
    7: ("Rest (Genesis 2:2-3), the thousand years of Christ's reign (Revelation 20:4)",
        f'<path d="M8 28 L6 12 L14 19 L20 9 L26 19 L34 12 L32 28 Z" fill="{PALE}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M8 33 H32" {LINE}/>'),
    8: ("The new creation, with no night (Revelation 21:1; 22:5)",
        f'<path d="M4 30 H36" {LINE}/><path d="M9 30 A11 11 0 0 1 31 30" fill="{PALE}" stroke="{INK}" stroke-width="2.2"/>'
        + "".join(f'<path d="M{20 + 14 * c:.1f} {30 - 14 * s:.1f} L{20 + 18 * c:.1f} {30 - 18 * s:.1f}" {LINE}/>'
                  for c, s in ((1, 0.15), (0.75, 0.66), (0.26, 0.97), (-0.26, 0.97), (-0.75, 0.66), (-1, 0.15)))),
}

# The texts-and-archaeology lane's markers, by kind (chronology.json `artifacts`; the anchors are
# 'archaeology').
KINDS = {
    "manuscript": ("A copy of Scripture",
                   f'<rect x="7" y="5" width="10" height="14" fill="{PALE}" stroke="{INK}" stroke-width="1.4"/>'
                   f'<rect x="4" y="3" width="3.5" height="18" rx="1.7" fill="{INK}"/><rect x="16.5" y="3" width="3.5" height="18" rx="1.7" fill="{INK}"/>'
                   f'<path d="M9 9 H15 M9 12 H15 M9 15 H14" stroke="{INK}" stroke-width="0.9"/>'),
    "inscription": ("An inscription in stone, clay or metal",
                    f'<path d="M5 21 V8 A7 7 0 0 1 19 8 V21 Z" fill="{PALE}" stroke="{INK}" stroke-width="1.6"/>'
                    f'<path d="M8 10 H16 M8 13 H16 M8 16 H15" stroke="{INK}" stroke-width="0.9"/>'),
    "historian": ("An ancient historian or writer",
                  f'<path d="M12 7 Q7 4 3 6 V19 Q7 17 12 20 Q17 17 21 19 V6 Q17 4 12 7 Z" fill="{PALE}" stroke="{INK}" stroke-width="1.4"/>'
                  f'<path d="M12 7 V20" stroke="{INK}" stroke-width="1.2"/>'),
    "archaeology": ("A dated record that anchors the chronology",
                    f'<path d="M3 17 L12 4 L21 17 Z" fill="{PALE}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
                    f'<path d="M3 20 H21" stroke="{INK}" stroke-width="1.6"/>'),
}


# Nebuchadnezzar's image (Daniel 2:31-33), for the Daniel's kingdoms plate. Drawn in its own units,
# 120 wide and 320 tall, with each part's band fixed so the plate can rule a line from the part to its
# kingdom: head 8-52, chest and arms 52-118, middle and thighs 118-178, legs 178-268, feet 268-300.
# Faceless like the comic cast, and no crown or ornament: Daniel gives the metals and nothing more.
# Each metal has a texture of its own as well as a colour, so the parts stay apart printed in grey.
GOLD, GOLD_EDGE = "#d9a820", "#8a6510"
SILVER, SILVER_EDGE = "#c9ced3", "#6e757c"
BRONZE, BRONZE_EDGE = "#b8743a", "#6e4520"
IRON, IRON_EDGE = "#5d636a", "#2b2f33"
CLAY = "#c49a6c"


def statue():
    o = []
    # Head of fine gold
    o.append(f'<path d="M48 52 V44 Q38 40 38 28 Q38 8 60 8 Q82 8 82 28 Q82 40 72 44 V52 Z" fill="{GOLD}" stroke="{GOLD_EDGE}" stroke-width="1.6"/>')
    o += [f'<circle cx="{x}" cy="{y}" r="1.1" fill="{GOLD_EDGE}"/>' for x, y in ((50, 20), (60, 16), (70, 20), (55, 30), (65, 30), (60, 40))]
    # Chest and arms of silver
    o.append(f'<path d="M26 58 Q30 52 48 52 H72 Q90 52 94 58 L90 118 H30 Z" fill="{SILVER}" stroke="{SILVER_EDGE}" stroke-width="1.6"/>')
    o.append(f'<path d="M26 58 L14 70 L12 114 L22 116 L26 76 Z M94 58 L106 70 L108 114 L98 116 L94 76 Z" fill="{SILVER}" stroke="{SILVER_EDGE}" stroke-width="1.6"/>')
    o += [f'<path d="M34 {y} H86" stroke="{SILVER_EDGE}" stroke-width="0.8" opacity="0.7"/>' for y in range(66, 116, 8)]
    # Middle and thighs of bronze
    o.append(f'<path d="M30 118 H90 L92 150 L88 178 H63 L60 156 L57 178 H32 L28 150 Z" fill="{BRONZE}" stroke="{BRONZE_EDGE}" stroke-width="1.6"/>')
    o += [f'<path d="M{x} 120 l-12 12" stroke="{BRONZE_EDGE}" stroke-width="0.8" opacity="0.7"/>' for x in range(44, 92, 8)]
    o += [f'<path d="M{x} 146 l-10 10" stroke="{BRONZE_EDGE}" stroke-width="0.8" opacity="0.7"/>' for x in (44, 52, 76, 84)]
    # Legs of iron
    o.append(f'<path d="M33 178 H57 L55 268 H37 Z M63 178 H87 L83 268 H65 Z" fill="{IRON}" stroke="{IRON_EDGE}" stroke-width="1.6"/>')
    o.append(f'<path d="M42 184 V262 M72 184 V262" stroke="#8d949b" stroke-width="1.4" opacity="0.8"/>')
    # Feet and toes, partly iron and partly clay: ten toes (Daniel 2:42)
    for fx in (28, 62):
        o.append(f'<path d="M{fx + 8} 268 H{fx + 26} L{fx + 30} 290 H{fx + 2} Z" fill="{IRON}" stroke="{IRON_EDGE}" stroke-width="1.4"/>')
        o.append(f'<path d="M{fx + 12} 274 h6 v8 h-6 Z M{fx + 20} 280 h5 v8 h-5 Z M{fx + 6} 282 h5 v6 h-5 Z" fill="{CLAY}"/>')
        for t in range(5):
            tx = fx + 3 + t * 5.6
            o.append(f'<rect x="{tx:.1f}" y="290" width="4.8" height="10" rx="2" fill="{IRON if t % 2 else CLAY}" stroke="{IRON_EDGE}" stroke-width="1"/>')
    return "".join(o)


def stone():
    """The stone cut out by no human hand (Daniel 2:34, 45), in flight."""
    return ('<path d="M8 22 Q6 10 18 6 Q30 2 34 14 Q38 26 26 32 Q12 36 8 22 Z" fill="#b3a897" stroke="#5e5547" stroke-width="1.6"/>'
            '<path d="M16 14 l6 3 M24 22 l5 -2 M14 24 l4 3" stroke="#5e5547" stroke-width="1"/>')


def vignette(v):
    parts, _, _ = comic._stage(VW, VH, v, f"v{v['event']}")
    return (f'<symbol id="v-{v["event"]}" viewBox="0 0 {VW} {VH}"><title>{esc(v["shows"])}</title>'
            + "".join(parts) + "</symbol>")


def main():
    data = tomllib.loads(SRC.read_text(encoding="utf-8"))
    # Zero-sized, never display:none: Chrome paints no gradient that lives in an undisplayed SVG, and
    # every comic sky is a gradient.
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">']
    out += [vignette(v) for v in data["vignette"]]
    out += [f'<symbol id="day-{n}" viewBox="0 0 40 40"><title>{esc(t)}</title>{body}</symbol>'
            for n, (t, body) in DAYS.items()]
    out += [f'<symbol id="kind-{k}" viewBox="0 0 24 24"><title>{esc(t)}</title>{body}</symbol>'
            for k, (t, body) in KINDS.items()]
    out.append(f'<symbol id="statue" viewBox="0 0 120 320"><title>Nebuchadnezzar\'s image: head of gold, chest and arms of silver, middle and thighs of bronze, legs of iron, feet of iron and clay (Daniel 2:32-33)</title>{statue()}</symbol>')
    out.append(f'<symbol id="stone" viewBox="0 0 40 40"><title>A stone cut out by no human hand (Daniel 2:34)</title>{stone()}</symbol>')
    out.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data['vignette'])} vignettes, {len(DAYS)} days, {len(KINDS)} kinds")
    for msg in comic.PROBLEMS:
        print(f"  fault: {msg}")


if __name__ == "__main__":
    main()
