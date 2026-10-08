"""Draw the data-sources graphic for docs/content/about/about-our-datasets.md.

A relationship graphic: the three licence tiers, the two databases they feed, the one query layer
over both, and what reaches a published page. Solid is ingested and queried; dashed is held and
read by hand. Every count is read at draw time -- works, verses and the tiers from bible-text.db,
the study-Bible works from study-notes.db, the tool count from mcp_server.py -- so the graphic
cannot drift from the data it describes. Both databases must be present. Run from the repo root:

    python3 utils/build_about_graphics.py
"""

import re
import sqlite3
import sys
from pathlib import Path

from lib.larkin import (W, PAPER, INK, MUTED, CARD, RED, RED_TINT, GOLD_EDGE, GOLD_TINT, BLUE,
                        BLUE_TINT, text, svg_open, heading, arrow_head, credit)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "references" / "build"))
import source_catalog as cat  # noqa: E402

OUT = ROOT / "docs" / "content" / "assets" / "img" / "about"

LEAF = "#4f6b2f"
LEAF_TINT = "#e4ead6"

# x, colour, tint for the three tier columns.
COL_W = 212
COL_X = [28, 28 + COL_W + 14, 28 + 2 * (COL_W + 14)]


def counts():
    bt = cat.database("bible-text")["resolved_path"]
    sn = cat.database("study-notes")["resolved_path"]
    for p in (bt, sn):
        if not p.exists():
            sys.exit(f"missing {p}: build it first (see references/README.md)")
    c = sqlite3.connect(f"file:{bt}?mode=ro", uri=True)
    one = lambda q: c.execute(q).fetchone()[0]  # noqa: E731
    n = {
        "works": one("select count(*) from works"),
        "verses": one("select count(*) from verses"),
        "english_open": one("select count(*) from works where license_tier='open' "
                            "and language in ('en','eng')"),
        "dss": one("select count(*) from works where source_id='dss'"),
        "xrefs": one("select count(*) from cross_references"),
    }
    s = sqlite3.connect(f"file:{sn}?immutable=1", uri=True)
    n["study_works"] = s.execute("select count(*) from works").fetchone()[0]
    src = (ROOT / "references" / "build" / "mcp_server.py").read_text(encoding="utf-8")
    n["tools"] = len(re.findall(r"@mcp\.tool\([^)]*\)\s*\ndef ", src))
    return n


# --- pictograms, each drawn in a 24-unit box from its top-left corner ---------------------------

def _g(x, y, body, stroke=INK):
    return (f'<g transform="translate({x:.1f} {y:.1f})" fill="none" stroke="{stroke}" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{body}</g>')


def icon(kind, x, y, stroke=INK):
    shapes = {
        # a scroll: the sheet and its two rolled ends
        "scroll": '<rect x="5" y="3" width="14" height="18" rx="1"/><circle cx="5" cy="5" r="2.5"/>'
                  '<circle cx="19" cy="19" r="2.5"/><path d="M8 9 H16 M8 13 H16 M8 17 H13"/>',
        # a torn fragment, for the scrolls from the caves
        "fragment": '<path d="M4 5 L10 3 L13 6 L19 4 L20 12 L17 15 L19 21 L9 20 L6 16 L3 13 Z"/>'
                    '<path d="M8 9 H15 M7 13 H14"/>',
        # an open book
        "book": '<path d="M12 6 C9 4 5 4 2 5 V20 C5 19 9 19 12 21 C15 19 19 19 22 20 V5 '
                'C19 4 15 4 12 6 Z"/><path d="M12 6 V21"/>',
        # a closed study Bible, with its ribbon
        "studybible": '<rect x="4" y="2" width="16" height="20" rx="1.5"/><path d="M8 2 V22"/>'
                      '<path d="M15 22 V25 L17 23.5 L19 25 V22" />',
        # a tag, for word data: parsing, lemma, Strong's
        "tag": '<path d="M3 12 L11 4 H21 V14 L13 22 Z"/><circle cx="16.5" cy="8.5" r="1.8"/>',
        # two chain links, for cross-references
        "link": '<rect x="2" y="9" width="12" height="7" rx="3.5" transform="rotate(-30 8 12.5)"/>'
                '<rect x="10" y="9" width="12" height="7" rx="3.5" transform="rotate(-30 16 12.5)"/>',
        # two lines of text joined word to word, for alignment
        "align": '<path d="M2 6 H22 M2 18 H22"/><path d="M5 6 L8 18 M12 6 L11 18 M19 6 L16 18" '
                 'stroke-dasharray="2 2"/>',
        # a database: a cylinder
        "db": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5 V19 C3 21 21 21 21 19 V5"/>'
              '<path d="M3 12 C3 14 21 14 21 12"/>',
        # a padlock
        "lock": '<rect x="5" y="11" width="14" height="10" rx="1.5"/><path d="M8 11 V8 a4 4 0 0 1 8 0 V11"/>',
        # a plug, for the MCP server an agent connects to
        "plug": '<path d="M8 2 V7 M16 2 V7"/><rect x="5" y="7" width="14" height="7" rx="2"/>'
                '<path d="M12 14 V18 C12 21 16 21 18 21 H22"/>',
        # a terminal prompt, for the CLI
        "terminal": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 10 L9 13 L6 16 M11 16 H16"/>',
        # a quill, for a study being written
        "quill": '<path d="M21 3 C13 4 7 10 5 19 L4 22"/><path d="M21 3 C20 11 14 16 6 17"/>'
                 '<path d="M9 13 L14 8"/>',
        # a page with a pop-up card over it
        "popup": '<rect x="2" y="3" width="16" height="18" rx="1.5"/><path d="M5 8 H15 M5 12 H11"/>'
                 '<rect x="10" y="12" width="12" height="9" rx="1.5" fill="' + PAPER + '"/>'
                 '<path d="M13 15.5 H19 M13 18 H17"/>',
        # a lamp, for the church fathers read by hand
        "lamp": '<path d="M3 15 C3 19 17 19 19 15 L22 13 L17 13 C15 12 5 12 3 15 Z"/>'
                '<path d="M20 13 C21 10 19 8 19 6 C18 8 17 10 18 13"/>',
        # a notebook, for unvetted teaching notes
        "notes": '<rect x="5" y="2" width="15" height="20" rx="1.5"/><path d="M3 6 H7 M3 11 H7 M3 16 H7"/>'
                 '<path d="M10 8 H17 M10 12 H17 M10 16 H14"/>',
    }
    return _g(x, y, shapes[kind], stroke)


# --- building blocks ----------------------------------------------------------------------------

def item(x, y, w, kind, lines, colour, dashed=False):
    """A source in a tier column: pictogram on the left, a bold name, then up to two lines."""
    h = 12 + 16 * len(lines)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="5" fill="{CARD}" '
           f'stroke="{colour}" stroke-width="1.3"{dash}/>',
           icon(kind, x + 7, y + (h - 24) / 2, colour)]
    ty = y + 19
    for i, ln in enumerate(lines):
        out.append(text(x + 38, ty, ln, 13, weight="bold" if i == 0 else None,
                        fill=INK if i == 0 else MUTED))
        ty += 16
    return out, h


def tier_column(x, y, title, rule, colour, tint, items):
    out = [f'<rect x="{x}" y="{y}" width="{COL_W}" height="34" rx="5" fill="{colour}"/>',
           text(x + COL_W / 2, y + 22, title.upper(), 13.5, "middle", "bold", fill=PAPER, spacing="1.2"),
           text(x + COL_W / 2, y + 52, rule, 13, "middle", fill=colour, italic=True)]
    cy = y + 64
    for kind, lines, dashed in items:
        svg, h = item(x, cy, COL_W, kind, lines, colour, dashed)
        out += svg
        cy += h + 8
    return out, cy


def down_arrow(x, y0, y1, colour=INK, dashed=False):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return [f'<path d="M{x:.1f} {y0:.1f} V{y1 - 7:.1f}" stroke="{colour}" stroke-width="1.8"{dash}/>',
            arrow_head(x, y1, 90, 9, colour)]


def box(x, y, w, h, kind, lines, colour=INK, fill=CARD, dashed=False, extra_icon=None):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="6" fill="{fill}" '
           f'stroke="{colour}" stroke-width="1.6"{dash}/>',
           icon(kind, x + 10, y + 12, colour)]
    if extra_icon:
        out.append(icon(extra_icon, x + 30, y + 22, colour))
    ty = y + 25
    for i, ln in enumerate(lines):
        out.append(text(x + 62, ty, ln, 14.5 if i == 0 else 13, weight="bold" if i == 0 else None,
                        fill=INK if i == 0 else MUTED))
        ty += 18 if i == 0 else 16
    return out


# --- the graphic --------------------------------------------------------------------------------

def data_sources(n):
    out = []
    out += heading("Where the data comes from", "Three licence tiers, two databases, one way in")

    top = 118
    open_items = [
        ("scroll", ["Hebrew & Greek texts", "WLC, UHB, SBLGNT, UGNT,", "Brenton LXX, Tischendorf"], False),
        ("tag", ["Word data", "MACULA: parsing, syntax,", "domains; Strong's numbers"], False),
        ("book", [f"{n['english_open']} English versions", "WEB (the default), ASV,", "YLT, BSB, KJV, JPS 1917"], False),
        ("link", ["Cross-references", f"{n['xrefs']:,}: OpenBible.info,", "WEB translators' notes"], False),
        ("align", ["Word alignment", "English to the original,", "unfoldingWord ULT"], False),
    ]
    restricted_items = [
        ("fragment", ["Dead Sea Scrolls", f"{n['dss']} scrolls, CC BY-NC"], False),
        ("scroll", ["Other witnesses", "Byzantine and TR Greek,", "Samaritan Pentateuch"], False),
        ("book", ["A few English versions", "LITV, MKJV, AKJV"], False),
        ("tag", ["Held, not ingested", "BHSA syntax trees,", "Mounce's dictionary"], True),
    ]
    quotation_items = [
        ("studybible", [f"{n['study_works']} study Bibles & texts", "ESV, NIV, NKJV, CSB,", "NASB, LSB, NLT, NA28"], False),
        ("book", ["TWOT discussion", "cited by root number;", "its ids and glosses are open"], False),
        ("book", ["Bible Knowledge", "Commentary: read by hand,", "not ingested"], True),
    ]
    cols = [
        ("Open", "quoted at any length", LEAF, LEAF_TINT, open_items),
        ("Restricted", "used, flagged non-commercial", GOLD_EDGE, GOLD_TINT, restricted_items),
        ("Quotation-only", "a sentence or two, attributed", RED, RED_TINT, quotation_items),
    ]
    bottoms = []
    for x, (title, rule, colour, tint, items) in zip(COL_X, cols):
        svg, b = tier_column(x, top, title, rule, colour, tint, items)
        out += svg
        bottoms.append(b)

    # The two databases. Open and restricted feed bible-text.db; quotation-only feeds study-notes.db.
    db_y = max(bottoms) + 34
    left_w = COL_X[1] + COL_W - COL_X[0]
    for x, b, c in ((COL_X[0] + COL_W / 2, bottoms[0], LEAF), (COL_X[1] + COL_W / 2, bottoms[1], GOLD_EDGE)):
        out += down_arrow(x, b, db_y, c)
    out += down_arrow(COL_X[2] + COL_W / 2, bottoms[2], db_y, RED)
    out += box(COL_X[0], db_y, left_w, 74, "db",
               ["bible-text.db", "in the public repository, rebuilt from source by build.py",
                f"{n['works']} works · {n['verses']:,} verses · every row re-derivable"],
               INK, BLUE_TINT)
    out += box(COL_X[2], db_y, COL_W, 74, "db",
               ["study-notes.db", "on local storage,", "never committed"],
               RED, RED_TINT, extra_icon="lock")

    # One way in: the MCP server and the CLI over both databases.
    q_y = db_y + 74 + 34
    out += down_arrow(COL_X[0] + left_w / 2, db_y + 74, q_y, INK)
    out += down_arrow(COL_X[2] + COL_W / 2, db_y + 74, q_y, RED)
    q_h = 100
    out.append(f'<rect x="28" y="{q_y}" width="{W - 56}" height="{q_h}" rx="6" fill="{GOLD_TINT}" '
               f'stroke="{INK}" stroke-width="1.8"/>')
    out.append(icon("plug", 40, q_y + 14))
    out.append(text(74, q_y + 28, f"MCP server: {n['tools']} lookup tools for the agent", 15, weight="bold"))
    out.append(text(74, q_y + 47, "passage_brief · bible_trace · study_verse · research_batch_run ·", 13, fill=MUTED))
    out.append(text(74, q_y + 63, "source_profile · evidence_check · and the rest", 13, fill=MUTED))
    out.append(icon("terminal", 40, q_y + q_h - 30))
    out.append(text(74, q_y + q_h - 13, "query.py: the same lookups from the command line, for anyone", 13))

    # What reaches a page. Pop-ups read bible-text.db directly, and only its open tier ships to
    # the browser, so their route runs down the left margin, clear of the query layer.
    o_y = q_y + q_h + 30
    o_w = (W - 56 - 14) / 2
    out += box(28, o_y, o_w, 74, "popup",
               ["Pop-ups on every page", "verse and word cards, built", "from the open tier only"], LEAF)
    out.append(f'<path d="M40 {db_y + 74} V{db_y + 82} H21 V{o_y - 14} H46 V{o_y - 7}" fill="none" '
               f'stroke="{LEAF}" stroke-width="1.6"/>')
    out.append(arrow_head(46, o_y, 90, 9, LEAF))
    out.append(text(54, o_y - 18, "export_popups.py", 12, fill=LEAF, italic=True))
    sx = 28 + o_w + 14
    out += down_arrow(sx + o_w / 2, q_y + q_h, o_y, INK)
    out += box(sx, o_y, o_w, 74, "quill",
               ["A study", "every language claim resolves", "to a row; quotations checked"], INK)

    # Kept beside the databases and read by hand.
    side_y = o_y + 74 + 30
    out.append(text(W / 2, side_y + 4, "Also held: read by hand, never queried", 13,
                    "middle", fill=MUTED, italic=True))
    half = (W - 56 - 14) / 2
    out += box(28, side_y + 16, half, 56, "lamp",
               ["Church fathers", "translations and original-language editions"], MUTED, CARD, dashed=True)
    out += box(28 + half + 14, side_y + 16, half, 56, "notes",
               ["Teaching notes", "unvetted leads, never cited in a study"], MUTED, CARD, dashed=True)

    # Key.
    k_y = side_y + 16 + 56 + 26
    out.append(f'<rect x="28" y="{k_y}" width="120" height="24" rx="5" fill="{CARD}" stroke="{INK}" stroke-width="1.3"/>')
    out.append(text(88, k_y + 16.5, "ingested, queried", 12.5, "middle"))
    out.append(f'<rect x="160" y="{k_y}" width="160" height="24" rx="5" fill="{CARD}" stroke="{INK}" '
               f'stroke-width="1.3" stroke-dasharray="5 4"/>')
    out.append(text(240, k_y + 16.5, "held, read by hand", 12.5, "middle"))
    out.append(text(336, k_y + 16.5, "Colour is the licence tier.", 12.5, fill=MUTED, italic=True))

    h = k_y + 64
    out.append(credit(h))
    desc = (
        "How this site's data is organised. Three licence tiers sit across the top. Open, quoted at "
        f"any length: the Hebrew and Greek texts (WLC, SBLGNT, Brenton LXX, UHB, UGNT, Tischendorf); "
        f"word data (MACULA parsing, syntax and semantic domains, Strong's numbers, TWOT ids); "
        f"{n['english_open']} English versions with the WEB as the default; {n['xrefs']:,} "
        "cross-references from OpenBible.info and the WEB translators' notes; and unfoldingWord's "
        f"word alignment. Restricted, used and flagged non-commercial: {n['dss']} Dead Sea Scrolls, "
        "the Byzantine and Textus Receptus Greek, the Samaritan Pentateuch, a few English versions, "
        "and, held but not ingested, BHSA and Mounce. Quotation-only, a sentence or two with "
        f"attribution: {n['study_works']} study Bibles and texts (ESV, NIV, NKJV, CSB, NASB, LSB, "
        "NLT, NA28), TWOT's discussion prose, and the Bible Knowledge Commentary, read by hand. "
        f"Open and restricted sources feed bible-text.db, in the public repository, {n['works']} "
        f"works and {n['verses']:,} verses rebuilt from source. Quotation-only sources feed "
        "study-notes.db, on local storage and never committed. The church fathers and unvetted "
        f"teaching notes are kept beside them and read by hand. An MCP server with {n['tools']} "
        "lookup tools, and the query.py command line, read both databases. What reaches a page: a "
        "study whose every language claim resolves to a row, and verse and word pop-ups built from "
        "the open tier only by export_popups.py."
    )
    return "\n".join(svg_open(h, "Where the data comes from", desc) + out + ["</svg>"]) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "data-sources.svg"
    path.write_text(data_sources(counts()), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
