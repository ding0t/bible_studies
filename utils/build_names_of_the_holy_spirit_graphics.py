"""Draw the name plates for holy-spirit/names-of-the-holy-spirit.md.

    uv run --with uharfbuzz --with fonttools python3 utils/build_names_of_the_holy_spirit_graphics.py

The third set after The Names of God, drawn by the same plate (build_names_of_god_graphics.py) and
the same rules: the name in large type with its old script beneath, the meaning, the verse (ESV),
and a scene of the moment the name belongs to, with every element keyed to its verse and anything
the text does not state drawn dashed and listed as such. Following drawn-graphics.md, the Spirit
has no form in these scenes. He is drawn as the text pictures Him: light, moving air, breath,
tongues as of fire.

Five plates are Hebrew names from the Old Testament, read from docs/data/hebrew-cards.json; two are
Greek names from the New Testament, read from docs/data/greek-cards.json, with the uncial capitals
where the Hebrew plates have Paleo-Hebrew.
"""

import json
from pathlib import Path

from build_names_of_god_graphics import (SW, SH, SKY_DAY, SKY_DUSK, NIGHT_TOP, NIGHT_LOW, SAND, SAND_DARK,
                                         HILL, HILL_FAR, STONE, STONE_EDGE, WOOD, WATER, WATER_DARK, FLAME,
                                         FLAME_HOT, FIGURE, FIGURE_LIGHT, sky, glow, ground, hill, star_field,
                                         figure, tent, flames, plate)
from lib.larkin import MUTED, CARD, GOLD, GOLD_TINT, text

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "names-of-the-holy-spirit"
HEBREW = ROOT / "docs" / "data" / "hebrew-cards.json"
GREEK = ROOT / "docs" / "data" / "greek-cards.json"
SERIES = "The Names of the Holy Spirit"

DEEP = "#0f1422"
WIND = "#f4e6bf"
WIND_DAY = "#a6844c"   # the same moving air, darkened to show against a daylight sky


def wind(paths, opacity=0.75, width=1.6, dashed=False, colour=WIND):
    """Moving air: open curves with a curl at the end, the way the scenes picture wind and breath."""
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return [f'<path d="{d}" stroke="{colour}" stroke-width="{width}" fill="none" stroke-linecap="round" '
            f'opacity="{opacity}"{dash}/>' for d in paths]


def tongue(cx, base, h=12):
    """A small flame, as of fire, resting on one head (Acts 2:3)."""
    return [f'<path d="M{cx - 3.5} {base} C{cx - 4} {base - h * 0.5} {cx - 1} {base - h * 0.6} {cx} {base - h} '
            f'C{cx + 1.5} {base - h * 0.55} {cx + 4} {base - h * 0.45} {cx + 3.5} {base} Z" fill="{FLAME}"/>',
            f'<path d="M{cx - 1.6} {base} C{cx - 1.8} {base - h * 0.4} {cx} {base - h * 0.5} {cx + 0.4} '
            f'{base - h * 0.7} C{cx + 1} {base - h * 0.4} {cx + 2} {base - h * 0.3} {cx + 1.6} {base} Z" fill="{FLAME_HOT}"/>']


def bone(x, y, length, angle):
    return [f'<g transform="rotate({angle} {x} {y})">'
            f'<path d="M{x - length / 2} {y} H{x + length / 2}" stroke="{CARD}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<circle cx="{x - length / 2}" cy="{y - 1.6}" r="2.1" fill="{CARD}"/>'
            f'<circle cx="{x - length / 2}" cy="{y + 1.6}" r="2.1" fill="{CARD}"/>'
            f'<circle cx="{x + length / 2}" cy="{y - 1.6}" r="2.1" fill="{CARD}"/>'
            f'<circle cx="{x + length / 2}" cy="{y + 1.6}" r="2.1" fill="{CARD}"/></g>']


def sheep(x, y, s=1.0):
    return [f'<ellipse cx="{x}" cy="{y}" rx="{9 * s}" ry="{6 * s}" fill="{CARD}" stroke="{STONE_EDGE}" stroke-width="1"/>',
            f'<circle cx="{x + 9 * s}" cy="{y - 3 * s}" r="{3.4 * s}" fill="{FIGURE_LIGHT}"/>']


# ---------------------------------------------------------------- the scenes

def scene_elohim():
    out = sky(DEEP, NIGHT_TOP, "hs1")
    # The face of the waters: dark swells across the lower half.
    for i, y in enumerate(range(150, 262, 16)):
        d = f"M-10 {y} " + " ".join(f"Q{x + 20} {y - 6 if (x // 40 + i) % 2 else y + 6} {x + 40} {y}"
                                    for x in range(-10, SW + 40, 40))
        out.append(f'<path d="{d} V{SH + 10} H-10 Z" fill="{WATER_DARK}" opacity="{0.35 + i * 0.07:.2f}"/>')
    out += glow(158, 128, 120, WIND, "hg1", 0.42)
    out += wind([f"M30 118 C90 96 150 140 210 112 S290 100 300 118 q6 10 -4 14",
                 f"M50 138 C110 120 170 158 236 132 q14 -4 18 6",
                 f"M70 100 C120 84 180 110 246 92 q10 -2 10 8"])
    out += [text(158, 34, "darkness over the face of the deep", 12, "middle", fill="#c9c2b0", italic=True)]
    return out


def scene_yhwh():
    out = sky(SKY_DAY, SKY_DUSK, "hs2")
    out += hill(170, 360, 176, 120, HILL_FAR, px=270)
    for x, y in [(236, 150), (262, 146), (290, 152), (276, 162)]:
        out += sheep(x, y, 0.8)
    out += ground(206)
    out += glow(112, 120, 70, GOLD, "hg2", 0.7)
    out += [f'<path d="M112 20 L96 132 M112 20 L128 132 M112 20 V132" stroke="{GOLD_TINT}" stroke-width="2" opacity="0.8"/>']
    # Samuel pours the horn of oil over David, the youngest, among his brothers (1 Samuel 16:13).
    out += figure(150, 226, "stand", 62)
    out += [f'<path d="M140 168 Q126 152 118 156 L114 150 Q130 140 146 162 Z" fill="{CARD}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<path d="M116 156 Q114 166 112 172" stroke="{GOLD}" stroke-width="2.4" stroke-dasharray="2 3"/>']
    out += figure(110, 226, "kneel", 50, fill=FIGURE_LIGHT)
    for i, x in enumerate((32, 196, 216, 236, 256, 276, 296)):
        out += figure(x, 226, "stand", 50 + (i % 3) * 4)
    out += [text(250, 246, "his brothers", 11.5, "middle", fill=MUTED, italic=True)]
    return out


def scene_qodshekha():
    out = sky(NIGHT_TOP, NIGHT_LOW, "hs3")
    out += star_field(30, 7, 90)
    # A room in the king's house at night: one window, a lamp, a man on his knees.
    out += [f'<rect x="0" y="96" width="{SW}" height="{SH}" fill="#4e4130"/>',
            f'<rect x="28" y="116" width="62" height="70" rx="31" fill="{NIGHT_LOW}" stroke="#26221a" stroke-width="2"/>',
            f'<path d="M59 116 V186 M28 150 H90" stroke="#26221a" stroke-width="2"/>',
            f'<rect x="0" y="214" width="{SW}" height="40" fill="#3a3024"/>']
    out += glow(214, 186, 46, FLAME_HOT, "hg3", 0.6)
    out += [f'<path d="M204 214 V196 H224 V214 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1" stroke-dasharray="3 2"/>',
            f'<path d="M206 196 Q214 188 222 196 Z" fill="{WOOD}" stroke-dasharray="3 2"/>']
    out += flames(214, 190, 8, 14)
    out += figure(160, 218, "kneel", 60, fill="#24201a")
    # Nathan has gone (2 Samuel 12:1, 15), leaving through the doorway.
    out += [f'<rect x="262" y="132" width="40" height="82" fill="#2c2418"/>']
    out += figure(286, 214, "stand", 50, fill="#5a4c38", facing=-1)
    out += [text(158, 244, "take not your Holy Spirit from me", 11.5, "middle", fill="#d8cfbb", italic=True)]
    return out


def scene_tovah():
    out = sky(SKY_DAY, SKY_DUSK, "hs4")
    out += hill(-30, 180, 190, 110, HILL_FAR, px=70)
    # The pillar of cloud that led them by day (Nehemiah 9:19).
    out += [f'<path d="M226 20 C206 40 244 60 222 84 C202 106 246 124 226 150 C214 170 236 184 228 196 '
            f'L262 196 C254 184 276 170 264 150 C244 124 288 106 268 84 C246 60 284 40 264 20 Z" '
            f'fill="#f7f3ea" stroke="{STONE}" stroke-width="1.2" opacity="0.92"/>']
    out += ground(200)
    for x, w in [(20, 52), (70, 46), (114, 50)]:
        out += tent(x, 206, w, 30, dashed=True)
    # Water out of the rock (Nehemiah 9:15, 20).
    out += [f'<path d="M150 210 Q146 160 186 150 Q214 150 214 210 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.4"/>',
            f'<path d="M186 172 Q182 196 170 214 Q190 222 214 216" stroke="{WATER}" stroke-width="5" fill="none" stroke-linecap="round"/>']
    # Manna on the ground, gathered each morning (9:20).
    for x in range(14, 310, 11):
        y = 222 + (x * 7) % 22
        out.append(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#fbf8ee" stroke="{SAND_DARK}" stroke-width="0.5"/>')
    out += figure(240, 226, "stand", 44)
    out += [f'<path d="M232 196 Q240 206 248 196" stroke="{FIGURE}" stroke-width="2" fill="none"/>']
    return out


def scene_ruchi():
    out = sky(SKY_DUSK, SKY_DAY, "hs5")
    out += hill(-40, 140, 186, 70, HILL, px=20)
    out += hill(190, 380, 186, 76, HILL, px=330)
    out += ground(186, SAND, SAND_DARK, wobble=3)
    # The valley full of bones, very dry (Ezekiel 37:1-2).
    for i, (x, y) in enumerate([(30, 214), (52, 230), (74, 208), (96, 226), (40, 244), (118, 236), (84, 246),
                                (130, 214), (150, 240), (62, 196)]):
        out += bone(x, y, 16 + (i % 3) * 4, (i * 47) % 180)
    # Breath from the four winds (37:9); the army standing on its feet (37:10).
    out += wind(["M8 20 C40 50 60 90 120 120", "M308 18 C280 50 250 90 196 120",
                 "M6 120 C40 116 90 130 140 150", "M310 116 C276 118 230 132 182 150"], opacity=0.8, width=2,
                colour=WIND_DAY)
    for i, x in enumerate(range(170, 310, 16)):
        out += figure(x, 222 + (i % 2) * 8, "stand", 40)
    out += [text(158, 34, "Come from the four winds, O breath", 12, "middle", fill=MUTED, italic=True)]
    return out


def scene_parakletos():
    out = [f'<rect width="{SW}" height="{SH}" fill="#4e4130"/>']
    # A large upper room, furnished (Mark 14:15), and outside the window, night (John 13:30).
    out += [f'<rect x="226" y="30" width="64" height="72" rx="32" fill="{NIGHT_TOP}" stroke="#26221a" stroke-width="2"/>']
    out += [f'<circle cx="{x}" cy="{y}" r="1.3" fill="#f6e7b0"/>' for x, y in [(244, 52), (268, 46), (276, 72), (252, 80)]]
    out += [f'<rect x="0" y="196" width="{SW}" height="60" fill="#3a3024"/>']
    out += glow(150, 150, 110, FLAME_HOT, "hg6", 0.42)
    out += [f'<rect x="60" y="172" width="180" height="12" rx="3" fill="{WOOD}" stroke="#3f2b16" stroke-width="1.2"/>',
            f'<path d="M78 184 V214 M222 184 V214" stroke="#3f2b16" stroke-width="4"/>',
            f'<ellipse cx="150" cy="168" rx="9" ry="3.5" fill="{STONE}" stroke="{STONE_EDGE}"/>']
    out += flames(152, 164, 6, 12)
    for i, x in enumerate((70, 98, 126, 174, 202, 230)):
        out += figure(x, 196, "seated", 46, fill="#2a231a" if i % 2 else "#33291e")
    # The basin and the towel (John 13:5).
    out += [f'<path d="M30 230 Q46 246 62 230 Z" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="1.2"/>',
            f'<path d="M66 232 q6 -12 14 -2 q4 6 10 0" stroke="{CARD}" stroke-width="4" fill="none" stroke-linecap="round"/>']
    out += [text(150, 30, "I will not leave you as orphans", 12, "middle", fill="#e6dcc6", italic=True)]
    return out


def scene_pentecost():
    out = sky(SKY_DAY, SKY_DUSK, "hs7")
    # A sound from heaven like a mighty rushing wind, filling the house (Acts 2:2).
    out += wind(["M10 14 C60 30 90 70 112 104", "M90 6 C120 30 140 66 150 100",
                 "M200 6 C190 36 184 70 186 102", "M306 18 C262 34 236 70 220 104"], opacity=0.8, width=2.2,
                colour=WIND_DAY)
    out += [f'<path d="M28 112 H288 L270 92 H46 Z" fill="#8a6f4c" stroke="#3f2b16" stroke-width="1.4"/>',
            f'<rect x="38" y="112" width="240" height="140" fill="#e8dcc4" stroke="#3f2b16" stroke-width="1.4"/>',
            f'<rect x="50" y="124" width="216" height="128" fill="#6b5a3e"/>']
    out += glow(158, 176, 100, FLAME_HOT, "hg7", 0.38)
    # All together in one place, sitting (2:1-2), and on each a tongue as of fire (2:3).
    for row, (y, xs) in enumerate([(206, (76, 108, 140, 172, 204, 236)), (240, (90, 124, 158, 192, 226))]):
        for x in xs:
            out += figure(x, y, "seated", 40, fill="#2a231a" if (x // 10) % 2 else "#3a2e20")
            out += tongue(x, y - 40 * 0.72 - 2)
    return out


# ---------------------------------------------------------------- the plates

PLATES = [
    # slug, card name, deck, scene, transliteration shown, quote, ref, key: [(element, ref, stated)]
    ("ruach-elohim", "Ruach Elohim", "hebrew", scene_elohim, "Ruach Elohim",
     "And the Spirit of God was hovering over the face of the waters.", "Genesis 1:2 (ESV)",
     [("darkness over the face of the deep", "Genesis 1:2", True),
      ("the face of the waters", "1:2", True),
      ("the Spirit of God hovering over them", "1:2", True),
      ("the light and moving air that picture Him", "", False)]),
    ("ruach-yhwh", "Ruach YHWH", "hebrew", scene_yhwh, "Ruach YHWH",
     "And the Spirit of the LORD rushed upon David from that day forward.", "1 Samuel 16:13 (ESV)",
     [("Samuel anoints David with the horn of oil", "1 Samuel 16:13", True),
      ("in the midst of his brothers, the seven Jesse had brought before Samuel", "16:10, 13", True),
      ("the sheep the youngest was keeping", "16:11", True),
      ("the Spirit of the LORD rushing upon David, drawn as light", "16:13", True),
      ("David kneeling", "", False)]),
    ("ruach-qodshekha", "Ruach Qodshekha", "hebrew", scene_qodshekha, "Ruach Qodshekha",
     "Cast me not away from your presence, and take not your Holy Spirit from me.", "Psalm 51:11 (ESV)",
     [("Nathan sent to David, and gone", "2 Samuel 12:1, 15", True),
      ("the night, the room, the lamp, and David on his knees", "", False)]),
    ("ruchakha-hatovah", "VeRuchakha Hattovah", "hebrew", scene_tovah, "Ruchakha Hattovah",
     "You gave your good Spirit to instruct them and did not withhold your manna from their mouth and "
     "gave them water for their thirst.", "Nehemiah 9:20 (ESV)",
     [("the pillar of cloud to lead them by day", "Nehemiah 9:19", True),
      ("water out of the rock", "9:15, 20", True), ("manna on the ground", "9:20", True),
      ("the camp's tents", "", False)]),
    ("ruchi", "Ruchi", "hebrew", scene_ruchi, "Ruchi",
     "And I will put my Spirit within you, and you shall live.", "Ezekiel 37:14 (ESV)",
     [("the valley full of bones, very dry", "Ezekiel 37:1-2", True),
      ("breath from the four winds", "37:9", True),
      ("they lived and stood on their feet, an exceedingly great army", "37:10", True)]),
    ("parakletos", "Paraklētos", "greek", scene_parakletos, "Paraklētos",
     "And I will ask the Father, and he will give you another Helper, to be with you forever.",
     "John 14:16 (ESV)",
     [("a large upper room, furnished", "Mark 14:15", True), ("and it was night", "John 13:30", True),
      ("the basin and the towel", "13:5", True),
      ("the disciples, drawn without faces; Jesus, who is speaking, is not drawn", "", False)]),
    ("to-pneuma-to-hagion", "To Pneuma to Hagion", "greek", scene_pentecost, "To Pneuma to Hagion",
     "And they were all filled with the Holy Spirit.", "Acts 2:4 (ESV)",
     [("all together in one place, sitting", "Acts 2:1-2", True),
      ("a sound from heaven like a mighty rushing wind, filling the house", "2:2", True),
      ("divided tongues as of fire, resting on each one", "2:3", True),
      ("the house drawn open to show them", "", False)]),
]


def main():
    decks = {
        "hebrew": {c["name"]: c for c in json.loads(HEBREW.read_text(encoding="utf-8"))["decks"]["names-of-the-holy-spirit"]["cards"]},
        "greek": {c["name"]: c for c in json.loads(GREEK.read_text(encoding="utf-8"))["decks"]["names-of-the-holy-spirit"]["cards"]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, name, deck, scene, translit, quote, ref, key in PLATES:
        svg = plate(slug, decks[deck][name], scene, translit, quote, ref, key, series=SERIES, greek=deck == "greek")
        (OUT / f"{slug}.svg").write_text(svg, encoding="utf-8")
        print(f"wrote {slug}.svg")


if __name__ == "__main__":
    main()
