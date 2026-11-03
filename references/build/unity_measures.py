"""Measures for What Literary Criticism Declares: many writers, over many centuries, one story.

Writes docs/data/unity-measures.json. Every measure runs twice where dating matters, once on the
traditional dates and once on the dates critical scholarship assigns (docs/data/book-authorship.toml
holds both, each sourced), because the study's claim is that the result survives the critics' own
model. Re-run after bible-text.db or the authorship table changes:

    uv run python unity_measures.py

The measures, and what each can and cannot show:

  authorship   how many writers, over what span, in what languages and places
  links        cross-references and quotations, and how many centuries each one spans
  network      whether every book and every writer is joined to the others
  bookends     rare words Genesis 1-3 and Revelation 20-22 share, across the whole span
  prophecy     OT texts the NT quotes, how long before, and whether a Qumran scroll holds them
  validator    fulfilled prophecies (docs/data/fulfilled-prophecy.toml): written, and surviving in
               a copy, before the event -- on the latest date any critic gives the prophecy
  style        whether the writers write differently (function-word profiles, Burrows' Delta)
  control      the same quotation test run against books of the same era outside the canon

None of these measures a miracle. They measure structure: many hands, one connected story. The
inference from structure to Author is the study's, and it says so.
"""
from __future__ import annotations

import json
import re
import sqlite3
import statistics
import tomllib
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from book_map import NUM_TO_OSIS, REFERENCE_NAME_TO_NUM
from versification import align

ROOT = Path(__file__).resolve().parents[2]
DB = Path(__file__).resolve().parent / "out" / "bible-text.db"
AUTHORSHIP = ROOT / "docs" / "data" / "book-authorship.toml"
PROPHECY = ROOT / "docs" / "data" / "fulfilled-prophecy.toml"
CHRONOLOGY = ROOT / "docs" / "data" / "chronology.json"
OUT = ROOT / "docs" / "data" / "unity-measures.json"

NT_BOOKS = ("Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim "
            "Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev").split()

# OpenBible votes are a crowd judgement. 10 keeps links a meaningful number of readers endorsed;
# the network section reports the count at every threshold so the choice is visible.
VOTE_THRESHOLD = 10
TEXTUAL_LINKS = ("quotation-greek", "inner-biblical", "quotation-crosslang")

# Septuagint books outside the 66, for the control. Duplicate recensions are dropped so no text is
# counted twice (Old Greek Daniel and its additions, Tobit's second text); Odes are excluded from
# both sides because most of them are canonical songs.
DEUTERO = {"1Esd", "2Esd", "1Macc", "2Macc", "3Macc", "4Macc", "Bar", "Bel", "EpJer", "Jdt",
           "PsSol", "Sir", "Sus", "TobBA", "Wis"}
LXX_SKIP = {"DanOG", "BelOG", "SusOG", "TobS", "JoshA", "JudgA", "Odes"}
LXX_CANON_ALIAS = {"JoshB": "Josh", "JudgB": "Judg"}

# Caves 1-11 only: Qumran was destroyed in AD 68, so every scroll found there was copied before.
# Masada (AD 73), Murabba'at and Nahal Hever (to AD 135) and unprovenanced fragments are excluded.
QUMRAN = re.compile(r"^dss-(\d{1,2}Q|1Qisa)")

# Witnesses whose date no theory of authorship moves. The prologue to Sirach, written in "the
# thirty-eighth year of King Euergetes" (about 132 BC), says "the law itself, and the prophecies,
# and the rest of the books" were already read in Greek. The Great Isaiah Scroll is c. 125 BC.
SIRACH_PROLOGUE = -132
GREAT_ISAIAH_SCROLL = -125
QUMRAN_FALLS = 68

FUNCTION_WORDS = 60
CHUNK_WORDS = {"greek": 1500, "hebrew": 2500}
NGRAM = 5


def load_authorship() -> dict[str, dict]:
    with open(AUTHORSHIP, "rb") as f:
        return {b["id"]: b for b in tomllib.load(f)["book"]}


def date_range(book: dict, scheme: str, chapter: int | None = None) -> tuple[int, int]:
    if scheme == "critical":
        for part in book.get("critical_parts", []):
            lo, hi = part["chapters"]
            if chapter is not None and lo <= chapter <= hi:
                return tuple(part["date"])
        if "critical" in book:
            return tuple(book["critical"])
        if "critical_after" in book:
            return (book["critical_after"], book["critical_after"])
    return tuple(book["date"])


def midpoint(book: dict, scheme: str, chapter: int | None = None) -> float:
    lo, hi = date_range(book, scheme, chapter)
    return (lo + hi) / 2


def author_keys(book: dict, scheme: str) -> set[str]:
    if scheme == "critical" and "critical_parts" in book:
        return {p["author_key"] for p in book["critical_parts"]}
    if scheme == "critical" and "critical_author_key" in book:
        return {book["critical_author_key"]}
    return {book["author_key"]}


def author_of(book: dict, scheme: str, chapter: int | None) -> str:
    if scheme == "critical":
        for part in book.get("critical_parts", []):
            lo, hi = part["chapters"]
            if chapter is not None and lo <= chapter <= hi:
                return part["author_key"]
        if "critical_author_key" in book:
            return book["critical_author_key"]
    return book["author_key"]


def normalise_greek(lemma: str) -> str:
    stripped = "".join(c for c in unicodedata.normalize("NFD", lemma or "")
                       if unicodedata.category(c) != "Mn")
    return stripped.lower().replace("ς", "σ")


def year_label(y: float) -> str:
    y = round(y)
    return f"{-y} BC" if y < 0 else f"AD {y}"


# --- authorship ------------------------------------------------------------------------------

def measure_authorship(books: dict[str, dict]) -> dict:
    out = {}
    for scheme in ("traditional", "critical"):
        keys = set().union(*(author_keys(b, scheme) for b in books.values()))
        anon = {k for k in keys if k.startswith("anon") or k in ("chronicler", "pastor")
                or k.startswith("pseudo") or k in ("second-isaiah", "third-isaiah")}
        starts = [date_range(b, scheme)[0] for b in books.values()]
        ends = [date_range(b, scheme)[1] for b in books.values()]
        for b in books.values():
            for p in b.get("critical_parts", []) if scheme == "critical" else []:
                starts.append(p["date"][0])
                ends.append(p["date"][1])
        out[scheme] = {
            "writers": len(keys),
            "named_writers": len(keys - anon),
            "unnamed_or_disputed_writers": len(anon),
            "earliest": year_label(min(starts)),
            "latest": year_label(max(ends)),
            "span_years": max(ends) - min(starts) - (1 if min(starts) < 0 < max(ends) else 0),
        }
    # the span on dates the critical view itself states, and nothing else: its earliest stated
    # date to its latest. No traditional date enters, so no critic can object to either end.
    stated = [(tuple(b["critical"]), b["id"]) for b in books.values() if "critical" in b]
    stated += [(tuple(p["date"]), f'{b["id"]} {p["chapters"][0]}-{p["chapters"][1]}')
               for b in books.values() for p in b.get("critical_parts", [])]
    first, last = min(stated), max(stated, key=lambda x: x[0][1])
    out["critical_floor"] = {
        "earliest": f"{first[1]}, {year_label(first[0][0])}", "latest": f"{last[1]}, {year_label(last[0][1])}",
        "span_years": last[0][1] - first[0][0] - 1,
        "note": "only dates the critical view states; the true span on that view is longer",
    }
    regions = Counter()
    for b in books.values():
        for r in b.get("region", "").split(";"):
            if r.strip():
                regions[r.strip()] += 1
    out["regions"] = dict(regions)
    out["languages"] = dict(Counter(b["language"] for b in books.values()))
    out["aramaic_portions"] = [b["aramaic_portion"] for b in books.values() if "aramaic_portion" in b]
    out["genres"] = len({b["genre"].split("-")[0] for b in books.values()})
    return out


# --- links and the network -------------------------------------------------------------------

def openbible_links(conn, threshold: int):
    return conn.execute(
        "SELECT from_book, from_chapter, to_book, to_chapter, votes FROM cross_references "
        "WHERE work_id='openbible-crossrefs' AND votes >= ? AND from_book != to_book", (threshold,))


def textual_links(conn):
    q = ",".join("?" * len(TEXTUAL_LINKS))
    return conn.execute(
        f"SELECT link_type, from_book, from_chapter, to_book, to_chapter FROM scripture_links "
        f"WHERE link_type IN ({q})", TEXTUAL_LINKS)


def gap_summary(gaps: list[float]) -> dict:
    if not gaps:
        return {"links": 0}
    a = np.array(gaps)
    return {
        "links": len(gaps),
        "median_years": round(float(np.median(a))),
        "over_500_years": round(float((a > 500).mean()), 3),
        "over_1000_years": round(float((a > 1000).mean()), 3),
    }


def measure_links(conn, books) -> dict:
    out = {}
    rows_ob = [r for r in openbible_links(conn, VOTE_THRESHOLD) if r[0] in books and r[2] in books]
    rows_tx = [r for r in textual_links(conn) if r[1] in books and r[3] in books]
    for scheme in ("traditional", "critical"):
        ob = [abs(midpoint(books[fb], scheme, fc) - midpoint(books[tb], scheme, tc))
              for fb, fc, tb, tc, _ in rows_ob]
        same_author = sum(1 for fb, fc, tb, tc, _ in rows_ob
                          if author_of(books[fb], scheme, fc) == author_of(books[tb], scheme, tc))
        tx = defaultdict(list)
        for kind, fb, fc, tb, tc in rows_tx:
            tx[kind].append(abs(midpoint(books[fb], scheme, fc) - midpoint(books[tb], scheme, tc)))
        # one arc per pair of writing dates, for the graphic in utils/build_criticism_graphics.py
        arcs = Counter(tuple(sorted((midpoint(books[fb], scheme, fc), midpoint(books[tb], scheme, tc))))
                       for fb, fc, tb, tc, _ in rows_ob)
        out[scheme] = {
            "arcs": sorted([a, b, n] for (a, b), n in arcs.items() if a != b),
            f"openbible_votes_{VOTE_THRESHOLD}": gap_summary(ob),
            "openbible_share_between_different_writers": round(1 - same_author / len(rows_ob), 3),
            **{kind: gap_summary(g) for kind, g in tx.items()},
        }
    return out


def components(nodes, edges) -> list[set]:
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, comps = set(), []
    for n in nodes:
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        comps.append(comp)
    return comps


def max_path(nodes, edges) -> int:
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    worst = 0
    for s in nodes:
        dist, frontier = {s: 0}, [s]
        while frontier:
            nxt = []
            for x in frontier:
                for y in adj[x] - dist.keys():
                    dist[y] = dist[x] + 1
                    nxt.append(y)
            frontier = nxt
        worst = max(worst, max(dist.values()))
    return worst


def mean_path(nodes, edges) -> float:
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    total = pairs = 0
    for s in nodes:
        dist = {s: 0}
        frontier = [s]
        while frontier:
            nxt = []
            for x in frontier:
                for y in adj[x]:
                    if y not in dist:
                        dist[y] = dist[x] + 1
                        nxt.append(y)
            frontier = nxt
        total += sum(dist.values())
        pairs += len(dist) - 1
    return round(total / pairs, 2)


def measure_network(conn, books) -> dict:
    ids = list(books)
    out = {"books": len(ids), "by_vote_threshold": {}}
    for threshold in (1, 10, 50):
        edges = {frozenset((r[0], r[2])) for r in openbible_links(conn, threshold)
                 if r[0] in books and r[2] in books}
        edges = [tuple(e) for e in edges]
        comps = components(ids, edges)
        degree = Counter()
        for a, b in edges:
            degree[a] += 1
            degree[b] += 1
        out["by_vote_threshold"][threshold] = {
            "book_pairs_linked": len(edges),
            "book_pairs_possible": len(ids) * (len(ids) - 1) // 2,
            "components": len(comps),
            "least_linked_books": sorted(((degree[b], b) for b in ids))[:5],
            "mean_steps_between_books": mean_path(ids, edges),
        }
    # writers, on the traditional and critical keys, joined by any textual link or 10-vote link
    for scheme in ("traditional", "critical"):
        writer_edges = set()
        for fb, fc, tb, tc, _ in openbible_links(conn, VOTE_THRESHOLD):
            if fb in books and tb in books:
                a, b = author_of(books[fb], scheme, fc), author_of(books[tb], scheme, tc)
                if a != b:
                    writer_edges.add(frozenset((a, b)))
        writers = sorted(set().union(*(author_keys(b, scheme) for b in books.values())))
        writer_edges = [tuple(e) for e in writer_edges]
        out[f"writers_{scheme}"] = {
            "writers": len(writers),
            "writer_pairs_linked": len(writer_edges),
            "writer_pairs_possible": len(writers) * (len(writers) - 1) // 2,
            "components": len(components(writers, writer_edges)),
            "mean_steps_between_writers": mean_path(writers, writer_edges),
            "most_steps_between_writers": max_path(writers, writer_edges),
        }
    return out


# --- bookends --------------------------------------------------------------------------------

def measure_bookends(conn) -> dict:
    nt_freq = Counter(normalise_greek(l) for (l,) in conn.execute(
        "SELECT lemma FROM morphology WHERE work_id='macula-greek-sblgnt'"))
    gen = defaultdict(set)
    for v, l in conn.execute("SELECT chapter||':'||verse, lemma FROM morphology "
                             "WHERE work_id='lxx-lemmas' AND book='Gen' AND chapter<=3"):
        gen[normalise_greek(l)].add(f"Genesis {v}")
    rev = defaultdict(set)
    for v, l in conn.execute("SELECT chapter||':'||verse, lemma FROM morphology "
                             "WHERE work_id='macula-greek-sblgnt' AND book='Rev' AND chapter>=20"):
        rev[normalise_greek(l)].add(f"Revelation {v}")
    shared = [{"lemma": w, "nt_occurrences": nt_freq[w],
               "genesis": sorted(gen[w])[:4], "revelation": sorted(rev[w])[:4]}
              for w in gen.keys() & rev.keys() if 0 < nt_freq[w] <= 40]
    shared.sort(key=lambda x: (x["nt_occurrences"], x["lemma"]))
    crossrefs = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(votes),0) FROM cross_references WHERE work_id='openbible-crossrefs' "
        "AND ((from_book='Gen' AND from_chapter<=3 AND to_book='Rev' AND to_chapter>=20) OR "
        "(from_book='Rev' AND from_chapter>=20 AND to_book='Gen' AND to_chapter<=3))").fetchone()
    return {"rare_shared_lemmas": shared, "openbible_crossrefs": {"rows": crossrefs[0],
                                                                    "votes": crossrefs[1]}}


# --- prophecy written before ---------------------------------------------------------------

def measure_prophecy(conn, books) -> dict:
    entries = defaultdict(dict)
    for entry, role, b, c, v in conn.execute(
            "SELECT entry, role, book, chapter, verse FROM reference_lists WHERE list_id='ot-quotations'"):
        entries[entry].setdefault(role, (b, c, v))
    qumran = defaultdict(set)
    for work, b, c, v in conn.execute("SELECT DISTINCT work_id, book, chapter, verse FROM morphology "
                                      "WHERE work_id LIKE 'dss-%'"):
        if QUMRAN.match(work):
            qumran[(b, c, v)].add(work.removeprefix("dss-"))
    fulfil = {(b, c, v) for b, c, v in conn.execute(
        "SELECT book, chapter, verse FROM morphology WHERE work_id='macula-greek-sblgnt' "
        "AND lemma IN ('πληρόω','τελέω')")}

    pairs = [(e["quoting"], e["quoted"]) for e in entries.values()
             if "quoting" in e and "quoted" in e and e["quoted"][0] in books and e["quoting"][0] in books]
    out = {"quotations": len(pairs)}
    for scheme in ("traditional", "critical"):
        gaps = [midpoint(books[nt[0]], scheme, nt[1]) - midpoint(books[ot[0]], scheme, ot[1])
                for nt, ot in pairs]
        out[scheme] = {"median_years_before": round(statistics.median(gaps)),
                       "shortest": round(min(gaps)), "longest": round(max(gaps)),
                       "over_400_years": round(sum(g > 400 for g in gaps) / len(gaps), 3)}

    def attested(ref):
        b, c, v = ref
        m = align(b, c, v, "english", "masoretic")
        return qumran.get(tuple(m), set()) if m else set()

    def formula(nt):
        b, c, v = nt
        return any((b, c, v - k) in fulfil for k in range(0, 3))

    rows = [(nt, ot, attested(ot), formula(nt)) for nt, ot in pairs]
    fulfilled = [r for r in rows if r[3]]
    out["qumran_attested"] = round(sum(1 for r in rows if r[2]) / len(rows), 3)
    out["fulfilment_formula"] = {
        "quotations": len(fulfilled),
        "qumran_attested": sum(1 for r in fulfilled if r[2]),
        "in_great_isaiah_scroll": sum(1 for r in fulfilled if "1Qisaa" in r[2]),
        "examples": [{"nt": f"{nt[0]} {nt[1]}:{nt[2]}", "ot": f"{ot[0]} {ot[1]}:{ot[2]}",
                      "scrolls": sorted(sc)[:4]} for nt, ot, sc, _ in fulfilled if sc][:40],
    }
    return out


# --- style -----------------------------------------------------------------------------------

def book_tokens(conn, work: str, books: list[str]) -> dict[str, list[tuple[int, str]]]:
    q = ",".join("?" * len(books))
    out = defaultdict(list)
    for b, c, l in conn.execute(
            f"SELECT book, chapter, lemma FROM morphology WHERE work_id=? AND book IN ({q}) "
            f"ORDER BY book, chapter, verse, word_position", (work, *books)):
        if l:
            out[b].append((c, l))
    return out


def chunk(tokens: list[str], size: int) -> list[list[str]]:
    return [tokens[i:i + size] for i in range(0, len(tokens) - size + 1, size)]


def profiles(texts: dict[str, list[str]], features: list[str]) -> tuple[list[str], np.ndarray]:
    names = list(texts)
    m = np.array([[Counter(t)[f] / len(t) for f in features] for t in texts.values()])
    sd = m.std(axis=0)
    sd[sd == 0] = 1
    return names, (m - m.mean(axis=0)) / sd


def delta(z: np.ndarray) -> np.ndarray:
    return np.abs(z[:, None, :] - z[None, :, :]).mean(axis=2)


def measure_style(conn, books) -> dict:
    out = {}
    for lang, work, book_ids in (("greek", "macula-greek-sblgnt", NT_BOOKS),
                                 ("hebrew", "macula-hebrew-wlc",
                                  [b for b in books if b not in NT_BOOKS])):
        toks = book_tokens(conn, work, book_ids)
        features = [w for w, _ in Counter(l for t in toks.values() for _, l in t).most_common(FUNCTION_WORDS)]
        size = CHUNK_WORDS[lang]
        chunks = {}
        for b, t in toks.items():
            for i, ch in enumerate(chunk([l for _, l in t], size)):
                chunks[f"{b}#{i}"] = ch
        names, z = profiles(chunks, features)
        d = delta(z)
        np.fill_diagonal(d, np.inf)
        # leave-one-book-out nearest neighbour: does a chunk's closest chunk from ANOTHER book
        # belong to the same writer? Tested only on writers with more than one book.
        writer = {n: books[n.split("#")[0]]["author_key"] for n in names}
        multi = {w for w, c in Counter(books[b]["author_key"] for b in toks).items() if c > 1}
        hits = trials = 0
        for i, n in enumerate(names):
            if writer[n] not in multi:
                continue
            other = [j for j, m in enumerate(names) if m.split("#")[0] != n.split("#")[0]]
            j = min(other, key=lambda j: d[i, j])
            hits += int(writer[names[j]] == writer[n])
            trials += 1
        share = Counter(writer[n] for n in names)
        chance = sum((share[w] / len(names)) ** 2 for w in multi) / max(1, sum(
            share[w] / len(names) for w in multi))
        out[lang] = {"function_words": FUNCTION_WORDS, "chunk_words": size, "chunks": len(names),
                     "same_writer_nearest": round(hits / trials, 3) if trials else None,
                     "trials": trials, "chance_rate": round(chance, 3)}
        if lang == "hebrew":
            out[lang]["isaiah"] = isaiah_split(toks, features, size)
    return out


def isaiah_split(toks, features, size) -> dict:
    """Distance between Isaiah 1-39 and 40-66, set against the same split of other long books."""
    def halves(b, cut):
        t = toks[b]
        return [l for c, l in t if c <= cut], [l for c, l in t if c > cut]
    long_books = {"Gen": 25, "Exod": 20, "Jer": 26, "Ezek": 24, "Ps": 75, "Deut": 17, "1Sam": 15,
                  "2Kgs": 13, "1Chr": 16, "2Chr": 18, "Job": 21, "Prov": 15}
    texts = {}
    a, b = halves("Isa", 39)
    texts["Isa 1-39"], texts["Isa 40-66"] = a, b
    for bk, cut in long_books.items():
        x, y = halves(bk, cut)
        texts[f"{bk} first"], texts[f"{bk} second"] = x, y
    names, z = profiles(texts, features)
    d = delta(z)
    idx = {n: i for i, n in enumerate(names)}
    isa = d[idx["Isa 1-39"], idx["Isa 40-66"]]
    within = {bk: round(float(d[idx[f"{bk} first"], idx[f"{bk} second"]]), 3) for bk in long_books}
    between = [d[i, j] for i, n in enumerate(names) for j, m in enumerate(names)
               if i < j and n.split()[0] != m.split()[0]]
    return {"isaiah_1_39_vs_40_66": round(float(isa), 3), "same_book_halves": within,
            "different_books_median": round(float(np.median(between)), 3),
            "rank_among_same_book_splits": 1 + sum(int(v > isa) for v in within.values())}


# --- control ---------------------------------------------------------------------------------




def grams(lemmas: list[str], stop: set[str]) -> set[tuple[str, ...]]:
    return {tuple(lemmas[i:i + NGRAM]) for i in range(len(lemmas) - NGRAM + 1)
            if sum(w not in stop for w in lemmas[i:i + NGRAM]) >= 3}


def measure_control(conn) -> dict:
    nt = defaultdict(list)
    for b, c, v, l in conn.execute("SELECT book, chapter, verse, lemma FROM morphology "
                                   "WHERE work_id='macula-greek-sblgnt' ORDER BY book, chapter, verse, word_position"):
        nt[(b, c, v)].append(normalise_greek(l))
    lxx = defaultdict(list)
    for b, c, v, l in conn.execute("SELECT book, chapter, verse, lemma FROM morphology "
                                   "WHERE work_id='lxx-lemmas' ORDER BY book, chapter, verse, word_position"):
        if b not in LXX_SKIP:
            lxx[(LXX_CANON_ALIAS.get(b, b), c, v)].append(normalise_greek(l))
    freq = Counter(w for ls in lxx.values() for w in ls)
    stop = {w for w, _ in freq.most_common(80)}
    index = defaultdict(set)
    for ref, ls in lxx.items():
        for g in grams(ls, stop):
            index[g].add(ref)
    hits = defaultdict(set)
    for ref, ls in nt.items():
        for g in grams(ls, stop):
            for target in index.get(g, ()):
                hits[target].add(ref)
    side = {"canon": [r for r in lxx if r[0] not in DEUTERO],
            "outside": [r for r in lxx if r[0] in DEUTERO]}
    out = {"method": f"NT verses sharing a {NGRAM}-lemma run (3+ content words) with a Septuagint verse"}
    for name, refs in side.items():
        reached = [r for r in refs if r in hits]
        out[name] = {"verses": len(refs), "verses_reached": len(reached),
                     "per_1000_verses": round(1000 * len(reached) / len(refs), 1),
                     "nt_verses_reaching": len(set().union(*(hits[r] for r in reached))) if reached else 0}
    out["outside_by_book"] = dict(Counter(r[0] for r in side["outside"] if r in hits).most_common())
    return out


REF = re.compile(r"((?:[1-3] )?[A-Z][a-z]+)? ?(\d+):(\d+)")


def parse_refs(text: str) -> list[tuple[str, int, int]]:
    """'Isaiah 44:28; 45:1' -> [('Isa', 44, 28), ('Isa', 45, 1)]. A bare chapter:verse continues
    the previous book. Anything after a parenthesis is commentary, not a reference."""
    out, book, chapter = [], None, None
    for part in re.split(r"[;,]", text.split("(")[0]):
        part = part.strip()
        m = REF.search(part)
        if m:
            if m.group(1):
                name = "Psalms" if m.group(1) == "Psalm" else m.group(1)
                book = NUM_TO_OSIS[REFERENCE_NAME_TO_NUM[name]]
            chapter = int(m.group(2))
            out.append((book, chapter, int(m.group(3))))
        elif re.fullmatch(r"\d+(-\d+)?", part) and chapter:
            out.append((book, chapter, int(part.split("-")[0])))
    return out


def chronology_years() -> dict[str, int]:
    years = {}
    data = json.loads(CHRONOLOGY.read_text(encoding="utf-8"))
    for key in ("anchors", "anchor_table", "milestones", "life_events"):
        for e in data.get(key, []):
            year = e.get("gregorian_year", e.get("gregorian"))
            if year is not None:
                years[e["id"]] = year
    return years


def measure_validator(conn, books) -> dict:
    with open(PROPHECY, "rb") as f:
        entries = tomllib.load(f)["prophecy"]
    years = chronology_years()
    qumran = defaultdict(set)
    for work, b, c, v in conn.execute("SELECT DISTINCT work_id, book, chapter, verse FROM morphology "
                                      "WHERE work_id LIKE 'dss-%'"):
        if QUMRAN.match(work):
            qumran[(b, c, v)].add(work.removeprefix("dss-"))
    rows = []
    for e in entries:
        refs = parse_refs(e["prophecy"])
        hebrew = parse_refs(e.get("masoretic", e["prophecy"]))
        fulfilled = years[e["event"]] if "event" in e else e["year"]
        # the latest moment the earliest witness could have been written: the end of its range
        written = {s: min(date_range(books[b], s, c)[1] for b, c, _ in refs)
                   for s in ("traditional", "critical")}
        if "written" in e:
            written["traditional"] = e["written"]
        scrolls = sorted(set().union(*(qumran.get(r, set()) for r in hebrew)))
        copies = []
        if any(b not in NT_BOOKS for b, _, _ in refs):
            copies.append(("Greek translation, Sirach prologue", SIRACH_PROLOGUE))
        if "1Qisaa" in scrolls:
            copies.append(("Great Isaiah Scroll", GREAT_ISAIAH_SCROLL))
        if scrolls:
            copies.append(("Qumran, before the site fell", QUMRAN_FALLS))
        earliest_copy = min(copies, key=lambda c: c[1]) if copies else None
        rows.append({
            "id": e["id"], "prophecy": e["prophecy"], "group": e["group"], "standing": e["standing"],
            "specific": e["specific"], "fulfilled": fulfilled,
            "written_traditional": written["traditional"], "written_critical": written["critical"],
            "years_ahead_traditional": fulfilled - written["traditional"],
            "years_ahead_critical": fulfilled - written["critical"],
            "qumran": scrolls,
            "earliest_copy": earliest_copy[0] if earliest_copy else None,
            "years_ahead_of_copy": fulfilled - earliest_copy[1] if earliest_copy else None,
            # a manuscript you can hold, dated before the event: the Great Isaiah Scroll, or any
            # Qumran copy of a prophecy fulfilled after the site fell
            "manuscript_before": ("1Qisaa" in scrolls and fulfilled > GREAT_ISAIAH_SCROLL)
                                 or (bool(scrolls) and fulfilled > QUMRAN_FALLS),
        })
    usable = [r for r in rows if r["standing"] != "record-after"]
    summary = {}
    for group in ("history", "messiah", "after"):
        g = [r for r in usable if r["group"] == group]
        summary[group] = {
            "prophecies": len(g),
            "before_on_traditional_dates": sum(r["years_ahead_traditional"] > 0 for r in g),
            "before_on_critical_dates": sum(r["years_ahead_critical"] > 0 for r in g),
            "before_a_surviving_copy": sum((r["years_ahead_of_copy"] or 0) > 0 for r in g),
            "before_a_manuscript": sum(r["manuscript_before"] for r in g),
            "contested": sum(r["standing"] != "stated" for r in g),
        }
    return {"summary": summary, "prophecies": rows,
            "excluded": [r["id"] for r in rows if r["standing"] == "record-after"]}


def main() -> int:
    books = load_authorship()
    conn = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
    result = {
        "authorship": measure_authorship(books),
        "links": measure_links(conn, books),
        "network": measure_network(conn, books),
        "bookends": measure_bookends(conn),
        "prophecy": measure_prophecy(conn, books),
        "validator": measure_validator(conn, books),
        "style": measure_style(conn, books),
        "control": measure_control(conn),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
