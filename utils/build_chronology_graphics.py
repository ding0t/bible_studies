"""Draw the charts for chronology/chronology-anchors.md in the Larkin hand.

    python3 utils/build_chronology_graphics.py

Everything comes from docs/data/chronology.json: the anchor table's rows (date, tier, error bar,
dated_by, witnesses), the five dating_roots, the outside records in artifacts, and the counted spans
in threads. A corrected date is one edit there and a re-run here, and the Prophetic Timeline reads
the same file, so the page, the charts and the timeline cannot drift apart.

- what-dates-what.svg (relationship): the five outside records the rail rests on, each beside the
  rows it dates and the witnesses that bear on them.
- the-rail.svg (sequence): every row on one line of time at a constant scale, with its error bar,
  and the spans Scripture counts across it.
"""

import json
import re
from pathlib import Path

from lib.larkin import (W, INK, MUTED, PAPER, CARD, RED, BLUE_TINT, EARTH_TINT, GOLD_TINT, RED_TINT,
                        GOLD_EDGE, HALO, text, svg_open, heading, credit, arrow_head, esc)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "content" / "assets" / "img" / "chronology"
DATA = json.loads((ROOT / "docs" / "data" / "chronology.json").read_text(encoding="utf-8"))
ROWS = sorted(DATA["anchor_table"], key=lambda r: r["n"])
ROOTS = DATA["dating_roots"]
RECORDS = {a["id"]: a for a in DATA["artifacts"] + DATA["anchors"]}
EPOCH_BC = -next(e["am0_gregorian"] for e in DATA["epochs"] if e["id"] == "genealogy")
EXODUS_BC = -next(m["gregorian_year"] for m in DATA["milestones"] if m["id"] == "exodus_early_date")

# One tint per root, so the two charts colour the same stretch of history the same way.
ROME_TINT = "#e4ece1"
ROOT_TINT = {"assyria": BLUE_TINT, "babylon": EARTH_TINT, "persia": GOLD_TINT, "greece": RED_TINT,
             "rome": ROME_TINT}


def year_label(g):
    return f"{-g} BC" if g < 0 else f"AD {g}"


def astro(g):
    """BC/AD (no year zero) to a continuous year number for placing on a scale."""
    return g + 1 if g < 0 else g


def am(g):
    return EPOCH_BC + g if g < 0 else EPOCH_BC + g - 1


def width_of(s, size):
    return len(s) * size * 0.52


def wrap(s, size, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if width_of(trial, size) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur] if cur else lines


def short_name(record_id):
    label = RECORDS[record_id]["label"]
    label = re.split(r"[:(]", label)[0].strip()
    return re.sub(r"^The ", "", label)


def tier_glyph(x, y, tier, r=4.2):
    if tier == "Fixed":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>'
    if tier == "Anchored":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>'
    return (f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{PAPER}" '
            f'stroke="{INK}" stroke-width="1.4" stroke-dasharray="2.5 2"/>')


def error_range(row):
    """(earliest, latest) BC/AD year the row's error bar allows."""
    err, g = row["error"], row["gregorian_year"]
    m = re.fullmatch(r"±(\d+)", err)
    if m:
        return g - int(m.group(1)), g + int(m.group(1))
    if err == "0":
        return g, g
    m = re.fullmatch(r"(AD )?(\d+)-(\d+)( BC)?", err)
    a, b = int(m.group(2)), int(m.group(3))
    return (-a, -b) if m.group(4) else (a, b)


def thread(tid):
    return next(t for t in DATA["threads"] if t["id"] == tid)


def event_year(eid):
    for key in ("anchor_table", "milestones", "anchors"):
        for e in DATA[key]:
            if e["id"] == eid and e.get("gregorian_year") is not None:
                return e["gregorian_year"]
    raise KeyError(eid)


def tier_legend(x, y):
    out = []
    for i, (tier, label) in enumerate((("Fixed", "Fixed: computable, or a record naming the event"),
                                       ("Anchored", "Anchored: a stated interval from a fixed point"),
                                       ("Bracketed", "Bracketed: held between two dated points"))):
        yy = y + i * 20
        out.append(tier_glyph(x + 5, yy - 4, tier))
        out.append(text(x + 18, yy, label, 13))
    return out


# --- what dates what -----------------------------------------------------------------------------

def what_dates_what():
    LX, LW = 28, 206          # the root panel
    RX = LX + LW + 16         # the rows
    ROW, WIT = 19, 14
    top = 128
    body = []

    # The elastic zone hangs from the first band: Solomon's temple counted back to the Exodus and
    # the Genesis chain counted back to AM 0. Dashed, because the text's intervals place it.
    ez_h = 62
    body.append(f'<rect x="{LX}" y="{top}" width="{W - 2 * LX}" height="{ez_h}" rx="6" fill="{CARD}" '
                f'stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 4"/>')
    body.append(text(W / 2, top + 22, f"Counted back from row 1: the Exodus in {EXODUS_BC} BC (1 Kings 6:1's 480 years)",
                     14, "middle", "bold"))
    body.append(text(W / 2, top + 42, f"and creation in {EPOCH_BC} BC, AM 0 (Genesis 5 and 11). The elastic zone, on Genealogy and Times.",
                     13, "middle", fill=MUTED, italic=True))
    y = top + ez_h + 26
    body.append(f'<path d="M{W / 2} {y - 2} V{top + ez_h + 4}" stroke="{INK}" stroke-width="1.4"/>')
    body.append(arrow_head(W / 2, top + ez_h + 4, -90))

    for root in ROOTS:
        rows = [r for r in ROWS if r["dated_by"] == root["id"]]
        heights = [ROW + (WIT if r.get("witnesses") else 0) for r in rows]
        lines = wrap(root["record"], 13.5, LW - 20)
        sky = wrap(root["sky"] or "Year-by-year lists; no eclipse needed", 12, LW - 34)
        panel_h = max(sum(heights) + 14, 52 + 17 * len(lines) + 15 * len(sky) + 10)
        tint = ROOT_TINT[root["id"]]
        body.append(f'<rect x="{LX}" y="{y}" width="{W - 2 * LX}" height="{panel_h}" rx="6" fill="{tint}" '
                    f'stroke="{INK}" stroke-width="1"/>')
        body.append(f'<rect x="{LX}" y="{y}" width="{LW}" height="{panel_h}" rx="6" fill="{CARD}" '
                    f'stroke="{INK}" stroke-width="1.4"/>')
        body.append(text(LX + 12, y + 24, root["label"].upper(), 15, weight="bold", spacing="1.5"))
        ty = y + 46
        for ln in lines:
            body.append(text(LX + 12, ty, ln, 13.5))
            ty += 17
        ty += 4
        if root["sky"]:
            # An eclipsed disc marks a date the sky fixes.
            body.append(f'<circle cx="{LX + 19}" cy="{ty - 4}" r="7" fill="{GOLD_EDGE}"/>')
            body.append(f'<circle cx="{LX + 23}" cy="{ty - 6}" r="6.2" fill="{CARD}"/>')
        for ln in sky:
            body.append(text(LX + 34, ty, ln, 12, fill=MUTED, italic=True))
            ty += 15
        ry = y + 7
        for r, h in zip(rows, heights):
            cy = ry + ROW / 2 + 1
            body.append(tier_glyph(RX + 6, cy - 4, r["tier"]))
            body.append(text(RX + 18, cy, f"{r['n']}", 12, fill=MUTED))
            body.append(text(RX + 40, cy, year_label(r["gregorian_year"]), 13, weight="bold"))
            body.append(text(RX + 106, cy, r["label"], 13))
            if r.get("witnesses"):
                wit = " · ".join(f"{short_name(w['id'])} ({w['job']})" for w in r["witnesses"])
                body.append(text(RX + 106, cy + WIT - 1, wit, 11.5, fill=MUTED, italic=True))
            ry += h
        y += panel_h + 12

    legend_y = y + 18
    body += tier_legend(LX + 4, legend_y)
    body.append(f'<circle cx="{LX + 430}" cy="{legend_y - 4}" r="7" fill="{GOLD_EDGE}"/>')
    body.append(f'<circle cx="{LX + 434}" cy="{legend_y - 6}" r="6.2" fill="{PAPER}"/>')
    body.append(text(LX + 446, legend_y, "Fixed by the sky", 13))
    body.append(text(LX + 422, legend_y + 20, "(fix) dates it · (check) another", 12, fill=MUTED, italic=True))
    body.append(text(LX + 422, legend_y + 36, "route · (confirm) names it, no year", 12, fill=MUTED, italic=True))
    h = legend_y + 80

    n_fixed = sum(r["tier"] == "Fixed" for r in ROWS)
    desc = (f"Five outside records, from the top: "
            + "; ".join(f"{r['label']}, dated by {r['record']}"
                        + (f" and fixed by {r['sky']}" if r['sky'] else "")
                        + f", which dates rows {', '.join(str(x['n']) for x in ROWS if x['dated_by'] == r['id'])}"
                        for r in ROOTS)
            + f". {n_fixed} of the {len(ROWS)} rows are Fixed. Above them all, dashed, the elastic zone "
            f"counted back from row 1: the Exodus in {EXODUS_BC} BC and creation in {EPOCH_BC} BC. "
            "Each row lists the witnesses that bear on it and the job each does.")
    out = svg_open(h, "What dates what", desc)
    out += heading("What dates what", "Five outside records, and the rows each one dates")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


# --- the rail ------------------------------------------------------------------------------------

def the_rail():
    START, END = -1000, 40
    TOP = 250
    S = 1.25                     # pixels per year
    AXIS = 236
    LABEL_X = 284

    def yof(g):
        return TOP + (astro(g) - astro(START)) * S

    bottom = yof(END)
    body = []

    # Bands: each root's stretch of history, from the first row it dates.
    starts = []
    for root in ROOTS:
        first = min(r["gregorian_year"] for r in ROWS if r["dated_by"] == root["id"])
        starts.append((root, first))
    for i, (root, first) in enumerate(starts):
        y0 = yof(START) if i == 0 else yof(first) - 6
        y1 = bottom if i == len(starts) - 1 else yof(starts[i + 1][1]) - 6
        body.append(f'<rect x="22" y="{y0:.1f}" width="{W - 44}" height="{y1 - y0:.1f}" '
                    f'fill="{ROOT_TINT[root["id"]]}" opacity="0.75"/>')
        body.append(text(32, y0 + 20, root["label"].upper(), 12.5, weight="bold", spacing="1.5"))

    # Centuries.
    for g in range(START, END, 100):
        if g == 0:
            continue
        y = yof(g)
        body.append(f'<path d="M{AXIS - 8} {y:.1f} H{AXIS}" stroke="{INK}" stroke-width="1"/>')
        body.append(text(AXIS - 12, y + 4, year_label(g), 11, "end", fill=MUTED, extra=HALO))
    body.append(f'<path d="M{AXIS} {yof(START):.1f} V{bottom:.1f}" stroke="{INK}" stroke-width="2"/>')

    # The spans Scripture counts across the rail: a red bar the text counts, dashed where the
    # placement is this site's reading or contested.
    spans = [("seventy_years_exile", 176), ("seventy_years_temple", 196), ("seventy_weeks", 176),
             ("daniel_8_14_days", 196)]
    for k, (tid, x) in enumerate(spans, 1):
        t = thread(tid)
        y0, y1 = yof(event_year(t["events"][0])), yof(event_year(t["events"][-1]))
        dash = "" if t["certainty"] == "stated" else ' stroke-dasharray="6 3"'
        body.append(f'<path d="M{x} {y0:.1f} V{y1:.1f}" stroke="{RED}" stroke-width="3"{dash}/>')
        body.append(f'<path d="M{x - 5} {y0:.1f} H{x + 5} M{x - 5} {y1:.1f} H{x + 5}" stroke="{RED}" stroke-width="1.5"/>')
        body += span_key(x - 14, y0 + 8, k)

    # Rows: the error bar on the axis, and a label pushed clear of its neighbours.
    placed = []
    gap = 16
    for r in ROWS:
        want = yof(r["gregorian_year"])
        y = max(want, placed[-1][1] + gap) if placed else want
        placed.append((r, y))
    overflow = placed[-1][1] - (bottom + 30)
    if overflow > 0:
        # Pull the tail back up so the last label stays inside the frame.
        fixed = []
        limit = bottom + 30
        for r, y in reversed(placed):
            y = min(y, limit)
            fixed.append((r, y))
            limit = y - gap
        placed = list(reversed(fixed))
    for r, ly in placed:
        g = r["gregorian_year"]
        lo, hi = error_range(r)
        y, ylo, yhi = yof(g), yof(lo), yof(hi)
        if r["tier"] == "Bracketed":
            body.append(f'<path d="M{AXIS} {ylo:.1f} V{yhi:.1f}" stroke="{GOLD_EDGE}" stroke-width="7" '
                        f'stroke-dasharray="3 2" opacity="0.9"/>')
        elif yhi - ylo > 0:
            body.append(f'<path d="M{AXIS} {ylo:.1f} V{yhi:.1f}" stroke="{GOLD_EDGE}" stroke-width="7" opacity="0.9"/>')
        body.append(tier_glyph(AXIS, y, r["tier"], r=3.6))
        body.append(f'<path d="M{AXIS + 6} {y:.1f} L{LABEL_X - 24} {y:.1f} L{LABEL_X - 8} {ly - 4:.1f}" '
                    f'fill="none" stroke="{MUTED}" stroke-width="0.6"/>')
        body.append(text(LABEL_X - 4, ly, f"{r['n']}", 11, "end", fill=MUTED))
        body.append(text(LABEL_X, ly, year_label(g), 12.5, weight="bold"))
        body.append(text(LABEL_X + 62, ly, f"{r['label']}  {r['error'] if r['error'] != '0' else '±0'}", 12.5))

    # The elastic zone above the rail, counted back from row 1.
    body.append(f'<rect x="40" y="134" width="{W - 80}" height="62" rx="6" fill="{CARD}" stroke="{INK}" '
                f'stroke-width="1.3" stroke-dasharray="6 4"/>')
    body.append(text(W / 2, 158, f"Above the rail: the Exodus, {EXODUS_BC} BC, 480 years before row 1 (1 Kings 6:1)",
                     13.5, "middle", "bold"))
    body.append(text(W / 2, 178, f"and creation, {EPOCH_BC} BC, AM 0, counted back through Genesis 5 and 11",
                     13, "middle", fill=MUTED, italic=True))
    body.append(f'<path d="M{AXIS} {yof(START) - 4:.1f} V202" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    body.append(arrow_head(AXIS, 202, -90))

    legend_y = bottom + 74
    body += tier_legend(40, legend_y)
    key_y = legend_y + 84
    body.append(text(40, key_y - 22, "The spans Scripture counts, beside the line:", 13, weight="bold"))
    for k, (tid, _) in enumerate(spans, 1):
        t = thread(tid)
        g0, g1 = event_year(t["events"][0]), event_year(t["events"][-1])
        body += span_key(48, key_y - 4, k)
        line = (f"{t['label']}, {year_label(g0)} to {year_label(g1)}"
                + (f": {t['span_label']}" if t.get("span_label") else "") + f" ({t['refs']})")
        for j, ln in enumerate(wrap(line, 12.5, W - 120)):
            body.append(text(62, key_y + j * 16, ln, 12.5, fill=INK if j == 0 else INK))
        key_y += 16 * len(wrap(line, 12.5, W - 120)) + 6
    body.append(f'<path d="M420 {legend_y - 10} V{legend_y + 6}" stroke="{GOLD_EDGE}" stroke-width="7"/>')
    body.append(text(434, legend_y, "Error bar, to scale", 13))
    body.append(f'<path d="M420 {legend_y + 12} V{legend_y + 28}" stroke="{RED}" stroke-width="3"/>')
    body.append(text(434, legend_y + 24, "A span the text counts", 13))
    body.append(f'<path d="M420 {legend_y + 34} V{legend_y + 50}" stroke="{RED}" stroke-width="3" stroke-dasharray="6 3"/>')
    body.append(text(434, legend_y + 46, "Dashed: this site's reading, or contested", 13))
    h = key_y + 40

    within = sum(1 for r in ROWS if (lambda lo_hi: lo_hi[1] - lo_hi[0] <= 2)(error_range(r)) and r["tier"] != "Bracketed")
    desc = ("A line of time from 1000 BC at the top to AD 40 at the bottom, 1.25 units a year, with every "
            f"row of the anchor table on it: {len(ROWS)} rows, each drawn as Fixed (solid), Anchored "
            "(hollow) or Bracketed (dashed range), with its error bar to scale. "
            f"{within} rows carry a year or less. Bands mark the five outside records that date each stretch: "
            + ", ".join(r["label"] for r in ROOTS) + ". Red bars beside the line are the spans Scripture counts: "
            + "; ".join(f"{thread(t)['label']} ({year_label(event_year(thread(t)['events'][0]))} to "
                        f"{year_label(event_year(thread(t)['events'][-1]))})" for t, _ in spans)
            + f". Above the line, dashed, the Exodus in {EXODUS_BC} BC and creation in {EPOCH_BC} BC, "
            "counted back from row 1.")
    out = svg_open(h, "The rail", desc)
    out += heading("The rail", "Forty-one anchors from Solomon's temple to the cross, to scale")
    out += body
    out.append(credit(h))
    out.append("</svg>")
    return "\n".join(out)


def span_key(x, y, k):
    """A numbered red disc tying a span bar to its line in the key."""
    return [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{PAPER}" stroke="{RED}" stroke-width="1.2"/>',
            text(x, y + 4, str(k), 10.5, "middle", "bold", fill=RED)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("what-dates-what.svg", what_dates_what), ("the-rail.svg", the_rail)):
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()
