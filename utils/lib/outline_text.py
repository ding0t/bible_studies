"""Text drawn as outlines, so a plate shows Hebrew and Paleo-Hebrew with no font on the reader's side.

An SVG shown through <img> cannot load a web font, and few devices carry one that places niqqud
well. HarfBuzz shapes the text with the font's own mark positioning (the vowel points sit where the
type designer put them) and fontTools turns each glyph into a path. Needs uharfbuzz and fonttools:

    uv run --with uharfbuzz --with fonttools python3 utils/build_names_of_god_graphics.py

The fonts are Noto Serif Hebrew and Noto Sans Phoenician (SIL Open Font License, fonts/OFL.txt).
"""

from functools import lru_cache
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(__file__).resolve().parent / "fonts"
HEBREW = "NotoSerifHebrew.ttf"
PALEO = "NotoSansPhoenician.ttf"


@lru_cache(maxsize=None)
def _font(name, weight):
    tt = TTFont(FONTS / name)
    if "fvar" in tt:
        tt = instantiateVariableFont(tt, {"wght": weight, "wdth": 100})
    buf = BytesIO()
    tt.save(buf)
    data = buf.getvalue()
    return TTFont(BytesIO(data)), hb.Font(hb.Face(data))


def outline(s, size, font=HEBREW, weight=500, rtl=True):
    """Return (path_d, width) for s set at `size` units, baseline at y=0, starting at x=0."""
    tt, hbfont = _font(font, weight)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    if rtl:
        buf.direction = "rtl"
    hb.shape(hbfont, buf, {})
    glyphs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    scale = size / upem
    pen = SVGPathPen(glyphs, lambda v: f"{v:.1f}")
    x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        gx, gy = (x + pos.x_offset) * scale, pos.y_offset * scale
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, -gy)))
        x += pos.x_advance
    return pen.getCommands(), x * scale


def place(s, x, y, size, anchor="middle", fill="#000", **kw):
    """An SVG <path> for s with its baseline at y, anchored at x like text-anchor."""
    d, w = outline(s, size, **kw)
    dx = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    return f'<path transform="translate({dx:.1f} {y:.1f})" fill="{fill}" d="{d}"/>', w
