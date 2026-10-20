"""Test the Babel model against the sizes of the world's language families.

    python3 utils/simulate_language_families.py

The model: at Babel, N0 unrelated languages begin at once. Each then splits into daughters and
dies out at constant rates, so after T years every founder has left a lineage of 0, 1, 2, ...
languages. A lineage of one is an isolate; two or more is a family. The question is whether this
reproduces Glottolog's actual lineages (docs/data/languages.json) -- 183 isolates, 238 families,
two giants over 1,200, a median family of five -- using only growth rates no faster than the
fastest family whose growth history records (Romance).

Each founder's lineage size is drawn from the exact birth-death distribution (Kendall 1948): with
birth rate b, death rate u and r = b - u, a single language leaves none with probability
a = u(e^rT - 1)/(b e^rT - u), and otherwise a geometric number with parameter
g = b(e^rT - 1)/(b e^rT - u). Founders differ in rate (some peoples spread and split, others stayed
put), so each founder's net rate is drawn from a lognormal and capped at the Romance rate; the
homogeneous model is the same with no spread. The fit searches the median rate, its spread and the
share of splits cancelled by deaths, and sets N0 so the expected number of surviving lineages
matches the observed count.

Writes docs/data/language-simulation.json, which utils/build_languages_graphics.py draws.
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "docs" / "data" / "languages.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / "data" / "language-simulation.json"

BABEL_BC = 2103
T = BABEL_BC + 2026
REPS = 60
SEED = 11

families = sorted(DATA["lineage_sizes"]["all_family_sizes"], reverse=True)
isolates = DATA["world"]["isolates"]
observed = families + [1] * isolates
romance = next(f for f in DATA["diversification"]["families"] if f["name"] == "Romance")
R_CAP = math.log(romance["languages"]) / romance["years"]


def stats(sizes):
    fam = sorted((s for s in sizes if s >= 2), reverse=True)
    if len(fam) < 50:
        return None
    return {
        "isolates": sum(1 for s in sizes if s == 1),
        "families": len(fam),
        "languages": sum(sizes),
        "largest": fam[0],
        "second": fam[1],
        "tenth": fam[9],
        "fiftieth": fam[49],
        "median_family": fam[len(fam) // 2],
    }


OBS = stats(observed)


def lineage(r, d, rng):
    """Languages left after T years by one founder with net rate r and death/birth ratio d."""
    b = r / (1 - d)
    u = d * b
    e = math.exp(r * T)
    a = u * (e - 1) / (b * e - u)
    if rng.random() < a:
        return 0
    g = b * (e - 1) / (b * e - u)
    # Geometric on 1, 2, ... with P(n) = (1 - g) g^(n-1).
    return 1 + int(math.log(1 - rng.random()) / math.log(g)) if g > 0 else 1


def founder_rate(median, spread, rng):
    return min(R_CAP, median * math.exp(spread * rng.gauss(0, 1)))


def survival(median, spread, d, rng, n=4000):
    """Share of founders whose lineage survives to today."""
    total = 0.0
    for _ in range(n):
        r = founder_rate(median, spread, rng)
        b = r / (1 - d)
        u = d * b
        e = math.exp(r * T)
        total += 1 - u * (e - 1) / (b * e - u)
    return total / n


def run(median, spread, d, n0, rng):
    sizes = [lineage(founder_rate(median, spread, rng), d, rng) for _ in range(n0)]
    return stats([s for s in sizes if s > 0])


def loss(s):
    return sum(math.log((s[k] + 1) / (OBS[k] + 1)) ** 2 for k in OBS)


def evaluate(median, spread, d, rng, reps=REPS):
    n0 = round((OBS["isolates"] + OBS["families"]) / survival(median, spread, d, rng))
    runs = [run(median, spread, d, n0, rng) for _ in range(reps)]
    runs = [s for s in runs if s]
    if len(runs) < reps // 2:
        return None
    # Medians across runs: a mean of the largest lineage is ruled by rare outliers.
    mid = {k: sorted(s[k] for s in runs)[len(runs) // 2] for k in OBS}
    return {"median_rate": median, "spread": spread, "death_ratio": d, "founders": n0,
            "loss": loss(mid), "median": mid,
            "range": {k: [min(s[k] for s in runs), max(s[k] for s in runs)] for k in OBS},
            "capped_share": sum(founder_rate(median, spread, rng) >= R_CAP for _ in range(4000)) / 4000}


def search(spreads):
    rng = random.Random(SEED)
    best = None
    for spread in spreads:
        for d in (0.0, 0.2, 0.4, 0.6, 0.75, 0.9):
            for k in range(26):
                median = 1e-4 * 1.15 ** k
                res = evaluate(median, spread, d, rng, reps=20)
                if res and (best is None or res["loss"] < best["loss"]):
                    best = res
    # Re-run the winner with full replication.
    return evaluate(best["median_rate"], best["spread"], best["death_ratio"], random.Random(SEED + 1))


def rank_curve(median, spread, d, n0, reps=REPS):
    """Median simulated rank-size curve: the k-th largest lineage, k = 1..421."""
    rng = random.Random(SEED + 2)
    n = len(observed)
    cols = [[] for _ in range(n)]
    for _ in range(reps):
        sizes = sorted((s for s in (lineage(founder_rate(median, spread, rng), d, rng)
                                    for _ in range(n0)) if s > 0), reverse=True)
        sizes += [0] * max(0, n - len(sizes))
        for i in range(n):
            cols[i].append(sizes[i])
    q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
    return [[q(c, 0.1), q(c, 0.5), q(c, 0.9)] for c in cols]


def main():
    homogeneous = search([0.0])
    varied = search([0.25 * i for i in range(1, 11)])
    required = [{"family": name, "languages": n,
                 "doubling_years": round(T * math.log(2) / math.log(n))}
                for name, n in DATA["lineage_sizes"]["largest"][:5]]
    result = {
        "_about": "Written by utils/simulate_language_families.py. Babel model fitted to Glottolog lineage sizes.",
        "babel_bc": BABEL_BC,
        "years": T,
        "rate_cap": {"family": "Romance", "net_rate": R_CAP,
                     "doubling_years": round(math.log(2) / R_CAP)},
        "observed": OBS,
        "observed_ranks": observed,
        "required_doubling_from_one_language": required,
        "homogeneous": homogeneous,
        "varied": varied,
        "curves": {
            "homogeneous": rank_curve(homogeneous["median_rate"], 0.0, homogeneous["death_ratio"],
                                      homogeneous["founders"]),
            "varied": rank_curve(varied["median_rate"], varied["spread"], varied["death_ratio"],
                                 varied["founders"]),
        },
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    for name in ("homogeneous", "varied"):
        r = result[name]
        print(name, {k: r[k] for k in ("median_rate", "spread", "death_ratio", "founders", "loss",
                                       "capped_share")})
        print("  median", r["median"], "\n  range", r["range"])
    print("observed", OBS)
    print("required", required, "cap doubling", result["rate_cap"]["doubling_years"])


if __name__ == "__main__":
    main()
