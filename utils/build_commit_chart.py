#!/usr/bin/env python3
"""Draw the repository's work over time from git history.

    python3 utils/build_commit_chart.py   # -> docs/content/assets/img/blog/commit-history.svg

Two measures. Velocity is commits. Volume is lines changed (added plus removed) in files a person
or an agent wrote by hand: generated pages (the commentary index, recent updates), lockfiles, JSON
exports, SVG drawings and binaries are left out, and a moved file counts once, so a reorganisation
does not read as a month of writing. Volume is split three ways: studies and pages, research
records (study-state files and the hand-edited data in docs/data), and tools (code, skills,
configuration and developer docs).

The whole history is drawn at true scale in a strip along the top, monthly. Nearly all the work
falls in the last four months, so that span is opened out underneath, week by week.
"""

import collections
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/content/assets/img/blog/commit-history.svg"

ZOOM_FROM = dt.date(2026, 7, 6)

# Dates from the commit log: the first commit of each kind, and the first commit each model
# co-authored (its Co-Authored-By trailer).
MILESTONES = [
    (dt.date(2026, 7, 18), "First skill"),
    (dt.date(2026, 7, 23), "MCP server"),
    (dt.date(2026, 8, 8), "Hedging purge"),
    (dt.date(2026, 8, 24), "Astro removed"),
    (dt.date(2026, 9, 5), "Cloudflare"),
    (dt.date(2026, 9, 27), "Pop-ups"),
    (dt.date(2026, 10, 12), "Comics"),
]
MODELS = [
    (dt.date(2026, 7, 18), "Sonnet 5"),
    (dt.date(2026, 7, 25), "Opus 5"),
    (dt.date(2026, 9, 24), "Opus 5.5"),
]
EARLY_NOTES = [
    (dt.date(2024, 4, 11), "First commit"),
    (dt.date(2025, 4, 25), "“fix ci”"),
    (dt.date(2026, 1, 11), "Astro"),
]

KINDS = [
    ("writing", "Studies and pages", "url(#p-writing)"),
    ("research", "Research records", "url(#p-research)"),
    ("tools", "Tools and checks", "url(#p-tools)"),
]

INK = "#1f2933"
MUTED = "#5b6670"
RULE = "#c9ced3"
PAPER = "#fbfaf7"
COMMIT = "#b3261e"


def kind_of(path):
    if re.search(r"(package-lock|uv\.lock|\.svg$|\.json$|\.png$|\.jpe?g$|\.db$|feed\.xml)", path):
        return None
    if path.startswith("docs/content/commentaries/") or "recent-updates" in path:
        return None
    if path.startswith(("references/study-state/", "docs/data/")):
        return "research"
    if re.search(r"\.(py|js|jsx|ts|tsx|astro|css|html|sh|toml|ya?ml|cjs|mjs)$", path):
        return "tools"
    if path.startswith((".claude/", "docs/dev/")) or path in ("AGENTS.md", "CLAUDE.md"):
        return "tools"
    if path.endswith(("README.md", "CONTENT_GUIDE.md")):
        return "tools"
    if path.endswith((".md", ".txt")):
        return "writing"
    return None


def read_history():
    log = subprocess.run(
        ["git", "log", "--reverse", "-M", "--numstat", "--format=@@%ad", "--date=short"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    commits, day = [], None
    for line in log.splitlines():
        if line.startswith("@@"):
            day = dt.date.fromisoformat(line[2:])
            commits.append({"day": day, "writing": 0, "research": 0, "tools": 0})
        elif "\t" in line:
            added, removed, path = line.split("\t")
            if added == "-":
                continue
            # A rename prints as "dir/{old => new}/file" or "old => new"; keep the new path.
            path = re.sub(r"\{[^{}]*=> ([^{}]*)\}", r"\1", path).split(" => ")[-1].replace("//", "/")
            kind = kind_of(path)
            if kind:
                commits[-1][kind] += int(added) + int(removed)
    return commits


def monday(day):
    return day - dt.timedelta(days=day.weekday())


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=11, fill=INK, anchor="start", weight="normal", italic=False, halo=False):
    style = ' font-style="italic"' if italic else ""
    if halo:
        style += f' stroke="{PAPER}" stroke-width="3" paint-order="stroke"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{style}>{esc(s)}</text>')


def nice_ceiling(v, steps=(1, 1.5, 2, 2.5, 3, 5, 10)):
    mag = 10 ** (len(str(int(v))) - 1)
    return next(s * mag for s in steps if s * mag >= v)


def build():
    commits = read_history()
    first, today = commits[0]["day"], commits[-1]["day"]
    W, H = 960, 700
    L, R = 70, 890
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
        "<title>Work on this site over time, from git history</title>",
        "<defs>",
        '<pattern id="p-writing" width="6" height="6" patternUnits="userSpaceOnUse">'
        '<rect width="6" height="6" fill="#2e5e7e"/></pattern>',
        '<pattern id="p-research" width="6" height="6" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(45)"><rect width="6" height="6" fill="#e3b45c"/>'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#7a5414" stroke-width="2.2"/></pattern>',
        '<pattern id="p-tools" width="5" height="5" patternUnits="userSpaceOnUse">'
        '<rect width="5" height="5" fill="#d9d2ea"/><circle cx="2.5" cy="2.5" r="1.1" fill="#4b3a78"/></pattern>',
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        text(L, 34, "Thirty months of commits, and where the work went", 19, weight="bold"),
        text(L, 54, f"From the first commit on {first:%-d %B %Y} to {today:%-d %B %Y}. "
             f"{len(commits)} commits.", 12, MUTED),
    ]

    # ---- The whole history at true scale: commits per month.
    months = collections.Counter((c["day"].year, c["day"].month) for c in commits)
    month_list, y_, m_ = [], first.year, first.month
    while (y_, m_) <= (today.year, today.month):
        month_list.append((y_, m_))
        y_, m_ = (y_ + (m_ == 12), m_ % 12 + 1)
    sT, sB = 92, 196
    sMax = nice_ceiling(max(months.values()))
    bw = (R - L) / len(month_list)
    out.append(text(L, 82, "THE WHOLE HISTORY, TRUE SCALE · commits each month", 10.5, MUTED, weight="bold"))
    for frac in (0.5, 1):
        y = sB - (sB - sT) * frac
        out.append(f'<line x1="{L}" x2="{R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RULE}" stroke-dasharray="2 3"/>')
        out.append(text(L - 6, y + 4, f"{int(sMax * frac)}", 10, MUTED, "end"))
    out.append(f'<line x1="{L}" x2="{R}" y1="{sB}" y2="{sB}" stroke="{INK}"/>')
    for i, ym in enumerate(month_list):
        n = months.get(ym, 0)
        x = L + i * bw
        if n:
            h = max(1.5, (sB - sT) * n / sMax)
            fill = COMMIT if dt.date(*ym, 1) >= ZOOM_FROM.replace(day=1) else MUTED
            out.append(f'<rect x="{x + 1:.1f}" y="{sB - h:.1f}" width="{bw - 2:.1f}" height="{h:.1f}" fill="{fill}"/>')
            out.append(text(x + bw / 2, sB - h - 4, str(n), 9.5, INK, "middle"))
        if ym[1] in (1, 7) or i == 0:
            out.append(text(x + 1, sB + 14, dt.date(*ym, 1).strftime("%b %Y"), 9.5, MUTED))
    early = sum(n for ym, n in months.items() if dt.date(*ym, 1) < ZOOM_FROM.replace(day=1))
    late = len(commits) - early
    span_months = len([ym for ym in month_list if dt.date(*ym, 1) < ZOOM_FROM.replace(day=1)])
    zx0 = L + month_list.index((ZOOM_FROM.year, ZOOM_FROM.month)) * bw
    out.append(text(L + 8, sT + 22, f"{early} commits in {span_months} months", 13, MUTED, weight="bold"))
    out.append(text(L + 8, sT + 38, "notes, a slide-deck pipeline, Proverbs, a website rebuild", 10.5, MUTED, italic=True))
    out.append(text(zx0 - 8, sT + 10, f"{late} commits", 13, COMMIT, "end", "bold"))
    out.append(text(zx0 - 8, sT + 25, "in four months", 10.5, COMMIT, "end"))
    for day, label in EARLY_NOTES:
        i = month_list.index((day.year, day.month))
        x = L + (i + 0.5) * bw
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{sB - 44}" y2="{sB - 22}" stroke="{MUTED}" stroke-width="0.8"/>')
        out.append(text(x - 4 if i == 0 else x, sB - 48, label, 9.5, MUTED, "start" if i == 0 else "middle"))

    # ---- The last four months opened out: weekly volume and velocity.
    weeks = collections.defaultdict(lambda: {"n": 0, "writing": 0, "research": 0, "tools": 0})
    for c in commits:
        if c["day"] >= ZOOM_FROM:
            w = weeks[monday(c["day"])]
            w["n"] += 1
            for k, _, _ in KINDS:
                w[k] += c[k]
    week_list, d = [], monday(ZOOM_FROM)
    while d <= today:
        week_list.append(d)
        d += dt.timedelta(days=7)
    mT, mB = 316, 590
    zoom = [zx0, R]
    # The lens: the strip's last four months widen into the panel below.
    out.append(f'<path d="M{zoom[0]:.1f},{sB + 20} L{zoom[1]:.1f},{sB + 20} L{R},{mT - 68} L{L},{mT - 68} Z" '
               f'fill="{COMMIT}" fill-opacity="0.06" stroke="{COMMIT}" stroke-opacity="0.35" stroke-dasharray="3 3"/>')
    out.append(text(L, mT - 76, f"THE LAST FOUR MONTHS, WEEK BY WEEK · from {ZOOM_FROM:%-d %B %Y}", 10.5, COMMIT, weight="bold"))

    vol = [sum(weeks[w][k] for k, _, _ in KINDS) for w in week_list]
    vMax = nice_ceiling(max(vol))
    cMax = nice_ceiling(max(weeks[w]["n"] for w in week_list))
    ww = (R - L) / len(week_list)

    def wx(day):
        return L + (day - monday(ZOOM_FROM)).days / 7 * ww

    for frac in (0.2, 0.4, 0.6, 0.8, 1):
        y = mB - (mB - mT) * frac
        out.append(f'<line x1="{L}" x2="{R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RULE}" stroke-dasharray="2 3"/>')
        out.append(text(L - 6, y + 4, f"{vMax * frac / 1000:g}k", 10, MUTED, "end"))
        out.append(text(R + 6, y + 4, f"{cMax * frac:g}", 10, COMMIT))
    out.append(text(L - 6, mT - 12, "lines changed", 10, MUTED, "end", italic=True))
    out.append(text(R + 6, mT - 12, "commits", 10, COMMIT, italic=True))

    # Model eras: from each model's first co-authored commit.
    for i, (day, name) in enumerate(MODELS):
        x = wx(day)
        top = mT - 34 + (i % 2) * 16
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{mB}" stroke="{INK}" stroke-opacity="0.25"/>')
        out.append(f'<path d="M{x:.1f},{top - 8} l7,4 l-7,4 z" fill="{INK}"/>')
        out.append(text(x + 10, top, f"{name} from {day:%-d %b}", 10.5, INK, weight="bold", halo=True))

    for w, total in zip(week_list, vol):
        x, y = wx(w), mB
        for k, _, fill in KINDS:
            h = (mB - mT) * weeks[w][k] / vMax
            if h > 0:
                out.append(f'<rect x="{x + 3:.1f}" y="{y - h:.1f}" width="{ww - 6:.1f}" height="{h:.1f}" '
                           f'fill="{fill}" stroke="{PAPER}" stroke-width="0.6"/>')
                y -= h

    pts = [(wx(w) + ww / 2, mB - (mB - mT) * weeks[w]["n"] / cMax) for w in week_list]
    out.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1])
               + f'" fill="none" stroke="{COMMIT}" stroke-width="2.4" stroke-linejoin="round"/>')
    # This week has only begun, so its point is drawn open and joined with a dashed line.
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{COMMIT}" '
               f'stroke-width="2" stroke-dasharray="4 3"/>')
    for i, ((x, y), w) in enumerate(zip(pts, week_list)):
        last = i == len(pts) - 1
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{PAPER if last else COMMIT}" '
                   f'stroke="{COMMIT}" stroke-width="1.8"/>')
        out.append(text(x, y - 9, str(weeks[w]["n"]), 10.5, COMMIT, "middle", "bold", halo=True))

    out.append(f'<line x1="{L}" x2="{R}" y1="{mB}" y2="{mB}" stroke="{INK}"/>')
    for w in week_list:
        if w.day <= 7 or w == week_list[0]:
            out.append(text(wx(w) + 3, mB + 15, f"{w:%-d %b}", 10, MUTED))
    out.append(text(wx(week_list[-1]) + ww / 2, mB + 28, "today", 10, MUTED, "middle", italic=True))

    for i, (day, label) in enumerate(MILESTONES):
        x = wx(day)
        y = mB + 46 + (i % 2) * 15
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{mB + 2}" y2="{y - 10}" stroke="{MUTED}" stroke-width="0.8"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{mB}" r="2.6" fill="{INK}"/>')
        out.append(text(x, y, label, 10, INK, "middle"))

    # Legend.
    lx, ly = L, H - 26
    for _, label, fill in KINDS:
        out.append(f'<rect x="{lx}" y="{ly - 10}" width="14" height="12" fill="{fill}" stroke="{INK}" stroke-width="0.5"/>')
        out.append(text(lx + 20, ly, label, 11))
        lx += 34 + len(label) * 6.2
    out.append(f'<line x1="{lx}" x2="{lx + 22}" y1="{ly - 4}" y2="{ly - 4}" stroke="{COMMIT}" stroke-width="2.4"/>')
    out.append(f'<circle cx="{lx + 11}" cy="{ly - 4}" r="3.5" fill="{COMMIT}"/>')
    out.append(text(lx + 28, ly, "Commits that week", 11))
    out.append(text(R + 20, ly, "Lines changed: added plus removed, hand-made files only.", 9.5, MUTED, "end", italic=True))

    out.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(commits)} commits, {len(week_list)} weeks opened out")
    return commits, weeks, week_list


if __name__ == "__main__":
    build()
