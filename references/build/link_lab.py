"""Experiments for finding the quotations the surface method misses. Not part of the build.

Measures each candidate technique against two answer keys that have no connection to the method:

  * the WEB translators' quotation footnotes (`web-crossrefs`, 423 New Testament -> Old Testament
    references), for recall, and
  * openbible's crowd cross-references, for precision -- the share of a technique's links that the
    crowd also records, binned by score, exactly as quotations.py's thresholds were set.

Usage (from references/build):  uv run python link_lab.py [nt|ot|xl|all]
"""
import collections
import math
import sqlite3
import sys

import versification
from build import chapter_lengths

DB = "out/bible-text.db"
NT_BOOKS = "Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev".split()
# lxx-lemmas splits some books into two Greek forms; both answer to the one English book.
LXX_BOOK = {"DanOG": "Dan", "BelOG": "Bel", "SusOG": "Sus", "JoshA": "Josh", "JoshB": "Josh",
            "JudgA": "Judg", "JudgB": "Judg", "TobBA": "Tob", "TobS": "Tob"}
DEUTERO = {"1Esd", "2Esd", "1Macc", "2Macc", "3Macc", "4Macc", "Bar", "Bel", "BelOG", "EpJer", "Jdt", "Odes",
           "PsSol", "Sir", "Sus", "SusOG", "TobBA", "TobS", "Wis"}
# Strong's numbers the two Greek lemma sources assign differently to the same word.
KEY_FIX = {"3801": "3588"}

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


# --- references ---------------------------------------------------------------------------------

_eng_cache: dict = {}


def english_of(book, chapter, verse, scheme):
    """A verse in the LXX or Masoretic numbering, as an English reference (or None)."""
    key = (book, chapter, verse, scheme)
    if key in _eng_cache:
        return _eng_cache[key]
    b = LXX_BOOK.get(book, book) if scheme == "lxx" else book
    aligned = versification.align(b, chapter, verse, scheme, "english")
    result = None
    if aligned is not None:
        src = "ebible-grcbrent" if scheme == "lxx" else "morphhb-wlc"
        offset = versification.superscription_offset(chapter_lengths(conn, src, b, chapter),
                                                     chapter_lengths(conn, "ebible-eng-web", aligned[0], aligned[1]))
        v = aligned[2] - offset
        result = (aligned[0], aligned[1], v if v >= 1 else aligned[2])
    _eng_cache[key] = result
    return result


def load_gold():
    gold = collections.defaultdict(list)
    for r in conn.execute("SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse_start, to_verse_end "
                          "FROM cross_references WHERE work_id='web-crossrefs'"):
        if r[0] in NT_BOOKS:
            gold[(r[0], r[1], r[2])].append((r[3], r[4], r[5], r[6]))
    return gold


def openbible():
    xr = collections.defaultdict(list)
    for r in conn.execute("SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse_start "
                          "FROM cross_references WHERE work_id='openbible-crossrefs'"):
        xr[(r[0], r[1], r[2])].append((r[3], r[4], r[5]))
    return xr


def corroborated(xr, src, eng):
    if eng is None:
        return False
    return any(b == eng[0] and c == eng[1] and abs(v - eng[2]) <= 2 for b, c, v in xr.get(src, ()))


def hits_gold(gold, src, eng):
    if eng is None:
        return None
    for g in gold.get(src, ()):
        if g[0] == eng[0] and g[1] == eng[1] and g[2] - 1 <= eng[2] <= g[3] + 1:
            return g
    return None


# --- tokens -------------------------------------------------------------------------------------

def key_sequences(work_id, books=None):
    """Each verse as a sequence of Strong's keys (lemma where there is none), in word order."""
    seqs = collections.defaultdict(list)
    q = "SELECT book, chapter, verse, strongs_id, lemma FROM morphology WHERE work_id=? ORDER BY book, chapter, verse, word_position"
    for b, c, v, s, lemma in conn.execute(q, (work_id,)):
        if books is not None and b not in books:
            continue
        k = (s or "").split("+")[0].strip() or (lemma or "")
        if not k:
            continue
        seqs[(b, c, v)].append(KEY_FIX.get(k, k))
    return seqs


def idf_table(*corpora):
    df = collections.Counter()
    n = 0
    for corpus in corpora:
        for seq in corpus.values():
            n += 1
            df.update(set(seq))
    return {k: math.log(n / d) for k, d in df.items()}, n


def weighted_alignment(a, b, w, gap=0.6, mismatch=0.4):
    """Smith-Waterman where a match is worth the word's rarity: two rare words in order outweigh
    six articles. Returns (score, matched keys)."""
    best = 0.0
    prev = [0.0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0.0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            m = prev[j - 1] + (w.get(a[i - 1], 0.5) if a[i - 1] == b[j - 1] else -mismatch)
            cur[j] = max(0.0, m, prev[j] - gap, cur[j - 1] - gap)
            best = max(best, cur[j])
        prev = cur
    return best


def skip_bigrams(seq, stop, window=3):
    content = [k for k in seq if k not in stop]
    out = set()
    for i, k in enumerate(content):
        for j in range(i + 1, min(len(content), i + window + 1)):
            out.add((k, content[j]))
    return out


# --- experiments --------------------------------------------------------------------------------

FORMULA = {"1125", "1124", "4137", "4483"}  # γράφω, γραφή, πληρόω, ῥέω/εἶπον-ῥηθέν


def has_formula(nt_seq, ref):
    b, c, v = ref
    here = set(nt_seq.get(ref, ())) | set(nt_seq.get((b, c, v - 1), ()))
    return bool(here & FORMULA)


def run_nt():
    gold, xr = load_gold(), openbible()
    nt = key_sequences("macula-greek-sblgnt")
    lxx = key_sequences("lxx-lemmas")
    w, n = idf_table(nt, lxx)
    freq = collections.Counter(k for seq in lxx.values() for k in seq)
    stop = {k for k, _ in freq.most_common(70)}

    index = collections.defaultdict(set)
    for ref, seq in lxx.items():
        for bg in skip_bigrams(seq, stop):
            index[bg].add(ref)

    scored = []
    for ref, seq in nt.items():
        cands = collections.Counter()
        for bg in skip_bigrams(seq, stop):
            if len(index.get(bg, ())) > 400:
                continue
            for t in index.get(bg, ()):
                cands[t] += 1
        for t, shared in cands.items():
            if shared < 2:
                continue
            s = weighted_alignment(seq, lxx[t], w)
            if s >= 8:
                scored.append((ref, t, s))
    print(f"lemma-key candidates scored: {len(scored)}")

    # Calibrate: corroboration by score bin.
    bins = collections.defaultdict(lambda: [0, 0, 0])
    for ref, t, s in scored:
        eng = english_of(*t, "lxx")
        b = min(int(s // 4) * 4, 60)
        bins[b][0] += 1
        bins[b][1] += corroborated(xr, ref, eng)
        bins[b][2] += has_formula(nt, ref)
    print("\nscore  pairs  corroborated  with-formula")
    for b in sorted(bins):
        p, c, f = bins[b]
        print(f"{b:5}  {p:5}  {100 * c / p:6.0f}%      {f}")
    return scored, gold, xr, nt


def recall_report(name, links, gold):
    """links: iterable of (nt_ref, english_ref)."""
    found = set()
    for src, eng in links:
        g = hits_gold(gold, src, eng)
        if g:
            found.add((src, g))
    total = sum(len(v) for v in gold.values())
    print(f"{name:42} recall {len(found):4}/{total} = {100 * len(found) / total:5.1f}%")
    return found


def baseline_links(min_align=18, types=("quotation-greek",)):
    out = []
    q = (f"SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse, link_type, alignment, "
         f"to_english_chapter, to_english_verse FROM scripture_links WHERE link_type IN ({','.join('?' * len(types))})")
    for r in conn.execute(q, types):
        if r[7] < min_align:
            continue
        eng = (r[3], r[8], r[9]) if r[8] else None
        out.append(((r[0], r[1], r[2]), eng))
    return out


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "compare":
    pass
elif __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "nt"
    if what in ("nt", "all"):
        scored, gold, xr, nt = run_nt()
        print()
        base = recall_report("baseline: Greek surface, alignment >= 18", baseline_links(18), gold)
        recall_report("baseline: Greek surface, all candidates", baseline_links(0), gold)
        recall_report("baseline + Hebrew-NT candidates", baseline_links(18, ("quotation-greek", "quotation-hebrew")), gold)
        for thr in (12, 14, 16, 18, 20, 24):
            links = [(r, english_of(*t, "lxx")) for r, t, s in scored if s >= thr]
            recall_report(f"lemma-key weighted, score >= {thr}", links, gold)
        for thr in (10, 12):
            links = [(r, english_of(*t, "lxx")) for r, t, s in scored if s >= thr and has_formula(nt, r)] + \
                    [(r, english_of(*t, "lxx")) for r, t, s in scored if s >= 18]
            recall_report(f"lemma-key: >=18, or >={thr} with a formula", links, gold)


def curve(name, scored_links, gold, xr, thresholds):
    """scored_links: list of (nt_ref, english_ref, score). Precision = openbible corroboration."""
    total = sum(len(v) for v in gold.values())
    print(f"\n{name}\n  thr   links  corrob%  recall")
    for t in thresholds:
        sel = [(r, e) for r, e, s in scored_links if s >= t]
        if not sel:
            continue
        c = sum(corroborated(xr, r, e) for r, e in sel)
        found = {(r, hits_gold(gold, r, e)) for r, e in sel if hits_gold(gold, r, e)}
        print(f"  {t:4}  {len(sel):5}  {100 * c / len(sel):6.0f}%  {100 * len(found) / total:5.1f}%")


def probe(scored, pairs):
    for (nb, nc, nv), (ob, oc) in pairs:
        hits = sorted(((s, t) for r, t, s in scored if r == (nb, nc, nv) and LXX_BOOK.get(t[0], t[0]) == ob), reverse=True)[:3]
        print(f"  {nb} {nc}:{nv} -> {ob} {oc}: {[(round(s, 1), t) for s, t in hits] or 'nothing'}")


def run_compare():
    scored, gold, xr, nt = run_nt()
    surf = []
    for r in conn.execute("SELECT from_book, from_chapter, from_verse, to_book, to_english_chapter, to_english_verse, alignment "
                          "FROM scripture_links WHERE link_type='quotation-greek'"):
        surf.append(((r[0], r[1], r[2]), (r[3], r[4], r[5]) if r[4] else None, r[6]))
    curve("surface (current method)", surf, gold, xr, (10, 12, 14, 16, 18, 20, 24, 30))
    lem = [(r, english_of(*t, "lxx"), s) for r, t, s in scored]
    curve("lemma-key weighted", lem, gold, xr, (12, 16, 20, 24, 28, 32, 36, 40))
    print("\nfamous misses, lemma-key scores:")
    probe(scored, [(("Jas", 2, 8), ("Lev", 19)), (("Rom", 1, 17), ("Hab", 2)), (("Matt", 4, 7), ("Deut", 6)),
                   (("Matt", 4, 10), ("Deut", 6)), (("John", 1, 23), ("Isa", 40)), (("Jas", 2, 23), ("Gen", 15)),
                   (("Mark", 1, 2), ("Mal", 3)), (("Matt", 24, 15), ("Dan", 12)), (("Matt", 24, 15), ("Dan", 9)),
                   (("Matt", 2, 15), ("Hos", 11)), (("Matt", 2, 6), ("Mic", 5)), (("John", 12, 40), ("Isa", 6)),
                   (("John", 19, 37), ("Zech", 12)), (("Matt", 26, 64), ("Dan", 7)), (("Gal", 3, 11), ("Hab", 2))])


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "compare":
    run_compare()


# --- a combined scorer: several signals, weighed by one answer key, tested on the other ----------

def surface_tokens():
    import quotations
    out = {}
    for b, c, v, t in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id IN ('sblgnt','ebible-grcbrent')"):
        out[(b, c, v)] = quotations.normalise_greek(t)
    return out


def candidates(nt, lxx, w, stop):
    """Verses sharing two content skip-bigrams, or one rare word (the short-quotation case)."""
    lxx_df = collections.Counter(k for seq in lxx.values() for k in set(seq))
    bigram_ix = collections.defaultdict(set)
    rare_ix = collections.defaultdict(set)
    for ref, seq in lxx.items():
        for bg in skip_bigrams(seq, stop):
            bigram_ix[bg].add(ref)
        for k in set(seq):
            if lxx_df[k] <= 40:
                rare_ix[k].add(ref)
    for ref, seq in nt.items():
        c = collections.Counter()
        for bg in skip_bigrams(seq, stop):
            if len(bigram_ix.get(bg, ())) <= 400:
                for t in bigram_ix.get(bg, ()):
                    c[t] += 1
        rare = collections.Counter()
        for k in set(seq):
            for t in rare_ix.get(k, ()):
                rare[t] += 1
        for t in set(c) | set(rare):
            very_rare = any(lxx_df[k] <= 12 for k in set(seq) & set(lxx[t]))
            if c[t] >= 2 or (rare[t] >= 1 and c[t] >= 1) or rare[t] >= 2 or very_rare:
                yield ref, t


def features(ref, t, nt, lxx, w, stop, surf, formula):
    import quotations
    a, b = nt[ref], lxx[t]
    shared = set(a) & set(b)
    content = [k for k in shared if k not in stop]
    lem = weighted_alignment(a, b, w, gap=1.0, mismatch=0.8)
    sa, sb = surf.get(ref, []), surf.get((LXX_BOOK.get(t[0], t[0]), t[1], t[2]), [])
    sur = quotations.local_alignment(sa, sb) if sa and sb else 0
    rare = sum(w.get(k, 0) for k in content if w.get(k, 0) > 4)
    nca = max(1, len([k for k in a if k not in stop]))
    run = quotations.longest_shared_run(a, b)
    top = max((w.get(k, 0) for k in content), default=0)
    return [lem, sur, rare, len(content), len(content) / nca, float(formula), math.log(len(a) + 1), math.log(len(b) + 1),
            run, top, lem * float(formula)]


def fit_logistic(X, y, l2=1.0, iters=3000, lr=0.1):
    import numpy as np
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (p - y) / len(y) + l2 * w / len(y)
        w -= lr * g
    return w


def fingerprint_tables(nt, lxx):
    """Unique phrases: surface 3- and 4-grams found in one Septuagint verse, and lemma-key bigrams
    found in at most two -- the lemma level reaches a phrase whose inflection changed."""
    import quotations
    lxx_rows = [r for r in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id='ebible-grcbrent'") if r[0] not in DEUTERO]
    nt_rows = conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id='sblgnt'").fetchall()
    out = []
    for n in (4, 3):
        df = collections.defaultdict(set)
        for b, c, v, t in lxx_rows:
            toks = quotations.normalise_greek(t)
            for i in range(len(toks) - n + 1):
                df[tuple(toks[i:i + n])].add((b, c, v))
        nt_df = collections.Counter()
        toks_of = {}
        for b, c, v, t in nt_rows:
            toks_of[(b, c, v)] = quotations.normalise_greek(t)
            nt_df.update({tuple(toks_of[(b, c, v)][i:i + n]) for i in range(len(toks_of[(b, c, v)]) - n + 1)})
        pairs = collections.defaultdict(list)
        for ref, toks in toks_of.items():
            for i in range(len(toks) - n + 1):
                g = tuple(toks[i:i + n])
                hits = df.get(g)
                if hits and len(hits) == 1 and nt_df[g] <= 3:
                    for t in hits:
                        pairs[(ref, t)].append(g)
        out.append(pairs)
    df = collections.defaultdict(set)
    for ref, seq in lxx.items():
        for i in range(len(seq) - 1):
            df[(seq[i], seq[i + 1])].add(ref)
    nt_df = collections.Counter()
    for seq in nt.values():
        nt_df.update({(seq[i], seq[i + 1]) for i in range(len(seq) - 1)})
    lem = collections.defaultdict(list)
    for ref, seq in nt.items():
        for i in range(len(seq) - 1):
            g = (seq[i], seq[i + 1])
            hits = df.get(g, ())
            if 0 < len(hits) <= 2 and nt_df[g] <= 3:
                for t in hits:
                    lem[(ref, t)].append(g)
    return out[0], out[1], lem


def run_model():
    import numpy as np
    gold, xr = load_gold(), openbible()
    nt = key_sequences("macula-greek-sblgnt")
    lxx = {k: v for k, v in key_sequences("lxx-lemmas").items() if k[0] not in DEUTERO}
    w, _ = idf_table(nt, lxx)
    freq = collections.Counter(k for seq in lxx.values() for k in seq)
    stop = {k for k, _ in freq.most_common(70)}
    surf = surface_tokens()
    fp4, fp3, fpl = fingerprint_tables(nt, lxx)
    pool = set(candidates(nt, lxx, w, stop)) | set(fp3) | set(fpl)
    rows, meta = [], []
    for ref, t in pool:
        if t not in lxx:
            continue
        f = features(ref, t, nt, lxx, w, stop, surf, has_formula(nt, ref))
        f += [len(fp4.get((ref, t), ())), len(fp3.get((ref, t), ())), len(fpl.get((ref, t), ())),
              len(fp3.get((ref, t), ())) * float(has_formula(nt, ref))]
        if f[0] < 6 and f[1] < 8 and f[12] == 0 and f[13] == 0:
            continue
        eng = english_of(*t, "lxx")
        rows.append(f)
        meta.append((ref, t, eng, corroborated(xr, ref, eng)))
    X = np.array(rows, dtype=float)
    y = np.array([m[3] for m in meta], dtype=float)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = np.hstack([(X - mu) / sd, np.ones((len(X), 1))])
    print(f"pairs: {len(X)}, corroborated: {int(y.sum())}")
    # Five folds, split by New Testament verse so a verse never trains its own score.
    folds = np.array([hash(m[0]) % 5 for m in meta])
    p = np.zeros(len(X))
    for k in range(5):
        tr, te = folds != k, folds == k
        wk = fit_logistic(Xs[tr], y[tr])
        p[te] = 1 / (1 + np.exp(-Xs[te] @ wk))
    wall = fit_logistic(Xs, y)
    names = ["lemma-align", "surface-align", "rare-weight", "shared-content", "containment", "formula", "log-len-nt", "log-len-lxx", "key-run", "max-idf", "lemma*formula", "fp4", "fp3", "fp-lemma", "fp3*formula", "bias"]
    print("weights:", ", ".join(f"{n} {v:+.2f}" for n, v in zip(names, wall)))
    scored = [(m[0], m[2], float(pp)) for m, pp in zip(meta, p)]
    curve("combined model (cross-validated probability)", scored, gold, xr, (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9))
    surf_links = []
    for r in conn.execute("SELECT from_book, from_chapter, from_verse, to_book, to_english_chapter, to_english_verse, alignment "
                          "FROM scripture_links WHERE link_type='quotation-greek'"):
        surf_links.append(((r[0], r[1], r[2]), (r[3], r[4], r[5]) if r[4] else None, r[6]))
    curve("surface (current method)", surf_links, gold, xr, (14, 16, 18, 20))
    print("\nfamous short quotations, model probability:")
    want = {("Jas", 2, 8): "Lev", ("Rom", 1, 17): "Hab", ("Matt", 4, 7): "Deut", ("Matt", 4, 10): "Deut", ("John", 1, 23): "Isa",
            ("Jas", 2, 23): "Gen", ("Mark", 1, 2): "Mal", ("Matt", 24, 15): "Dan", ("Gal", 3, 11): "Hab", ("1Pet", 1, 16): "Lev", ("John", 10, 34): "Ps"}
    for (ref, t, eng, c), pp in zip(meta, p):
        if ref in want and LXX_BOOK.get(t[0], t[0]) == want[ref]:
            print(f"  {ref} -> {t}: {pp:.2f}")
    return scored, meta, p


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "model":
    run_model()


# --- phrase fingerprints: a run of common words that occurs in only one Septuagint verse --------

def run_fingerprints(n_values=(3, 4), max_df=1):
    import quotations
    gold, xr = load_gold(), openbible()
    nt_keys = key_sequences("macula-greek-sblgnt")
    lxx_rows = [r for r in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id='ebible-grcbrent'") if r[0] not in DEUTERO]
    nt_rows = conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id='sblgnt'").fetchall()
    results = {}
    for n in n_values:
        df = collections.defaultdict(set)
        for b, c, v, t in lxx_rows:
            toks = quotations.normalise_greek(t)
            for i in range(len(toks) - n + 1):
                df[tuple(toks[i:i + n])].add((b, c, v))
        nt_df = collections.Counter()
        nt_tok = {}
        for b, c, v, t in nt_rows:
            toks = quotations.normalise_greek(t)
            nt_tok[(b, c, v)] = toks
            for g in {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}:
                nt_df[g] += 1
        pairs = collections.defaultdict(list)
        for ref, toks in nt_tok.items():
            for i in range(len(toks) - n + 1):
                g = tuple(toks[i:i + n])
                hits = df.get(g)
                # unique in the Septuagint, and rare in the New Testament too: a phrase, not an idiom
                if hits and len(hits) <= max_df and nt_df[g] <= 3:
                    for t in hits:
                        pairs[(ref, t)].append(g)
        results[n] = pairs
    four, three = results[4], results[3]
    print(f"pairs sharing a unique 4-gram: {len(four)}; a unique 3-gram: {len(three)}")
    scored = []
    for (ref, t), grams in {**three, **four}.items():
        k4 = len(four.get((ref, t), ()))
        k3 = len(three.get((ref, t), ()))
        form = has_formula(nt_keys, ref)
        scored.append((ref, t, k4, k3, form))
    def show(label, sel):
        links = [(r, english_of(*t, "lxx")) for r, t, *_ in sel]
        c = sum(corroborated(xr, r, e) for r, e in links)
        found = {(r, hits_gold(gold, r, e)) for r, e in links if hits_gold(gold, r, e)}
        total = sum(len(v) for v in gold.values())
        print(f"  {label:44} links {len(links):5}  corrob {100 * c / max(1, len(links)):4.0f}%  recall {100 * len(found) / total:5.1f}%")
    show("unique 4-gram >= 1", [s for s in scored if s[2] >= 1])
    show("unique 4-gram >= 2", [s for s in scored if s[2] >= 2])
    show("unique 4-gram >= 1 with a formula", [s for s in scored if s[2] >= 1 and s[4]])
    show("unique 3-gram >= 2 with a formula", [s for s in scored if s[3] >= 2 and s[4]])
    show("unique 3-gram >= 3", [s for s in scored if s[3] >= 3])
    for s in scored:
        if s[0] in {("John", 10, 34), ("Matt", 4, 7), ("Matt", 4, 10), ("Rom", 1, 17), ("Matt", 24, 15), ("Jas", 2, 8)}:
            print("   ", s)
    return scored


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "fp":
    run_fingerprints()


# --- the Hebrew Old Testament quoting itself, on lemmas -----------------------------------------

KNOWN_OT = [  # well-known parallels, as (book, chapter, first verse, last verse) pairs
    (("1Chr", 16, 8, 22), ("Ps", 105, 1, 15)), (("1Chr", 16, 23, 33), ("Ps", 96, 1, 13)),
    (("1Chr", 16, 34, 36), ("Ps", 106, 1, 48)), (("Joel", 4, 16, 16), ("Amos", 1, 2, 2)),
    (("Obad", 1, 1, 5), ("Jer", 49, 9, 16)), (("Ps", 108, 2, 6), ("Ps", 57, 8, 12)),
    (("Ps", 108, 7, 14), ("Ps", 60, 7, 14)), (("Ps", 70, 2, 6), ("Ps", 40, 14, 18)),
    (("Isa", 2, 2, 4), ("Mic", 4, 1, 3)), (("2Sam", 22, 2, 51), ("Ps", 18, 3, 51)),
    (("Ps", 14, 1, 7), ("Ps", 53, 2, 7)), (("1Chr", 17, 1, 27), ("2Sam", 7, 1, 29)),
    (("Ezra", 2, 1, 70), ("Neh", 7, 6, 73)), (("Exod", 20, 2, 17), ("Deut", 5, 6, 21)),
    (("2Chr", 36, 22, 23), ("Ezra", 1, 1, 3)), (("Isa", 37, 1, 38), ("2Kgs", 19, 1, 37)),
]


def run_ot():
    import quotations
    keyed = key_sequences("macula-hebrew-wlc")       # lemma or Strong's per word
    # MACULA splits prefixes into their own words, which is what a spelling-proof key wants.
    w, _ = idf_table(keyed)
    surf = {}
    for b, c, v, t in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id='morphhb-wlc'"):
        surf[(b, c, v)] = quotations.normalise_hebrew(t)
    def best(a_rng, b_rng, scorer, seqs):
        (ab, ac, av1, av2), (bb, bc, bv1, bv2) = a_rng, b_rng
        hits = 0
        for v in range(av1, av2 + 1):
            a = seqs.get((ab, ac, v))
            if not a:
                continue
            top = max((scorer(a, seqs.get((bb, bc, u), [])) for u in range(bv1, bv2 + 1) if seqs.get((bb, bc, u))), default=0)
            hits += top
        return hits
    print("parallel                         verses  surface>=18  lemma-key>=18  lemma-weighted>=14")
    for a, b in KNOWN_OT:
        n = a[3] - a[2] + 1
        def count(scorer, seqs, thr):
            k = 0
            for v in range(a[2], a[3] + 1):
                x = seqs.get((a[0], a[1], v))
                if not x:
                    continue
                if any(scorer(x, seqs.get((b[0], b[1], u), [])) >= thr for u in range(b[2], b[3] + 1) if seqs.get((b[0], b[1], u))):
                    k += 1
            return k
        s1 = count(quotations.local_alignment, surf, 18)
        s2 = count(quotations.local_alignment, keyed, 18)
        s3 = count(lambda x, y: weighted_alignment(x, y, w, gap=1.0, mismatch=0.8), keyed, 14)
        print(f"{a[0]} {a[1]}:{a[2]}-{a[3]} ~ {b[0]} {b[1]}  {n:6}  {s1:11}  {s2:13}  {s3:18}")


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "ot":
    run_ot()


def run_ot_global():
    import quotations
    keyed = key_sequences("macula-hebrew-wlc")
    w, _ = idf_table(keyed)
    freq = collections.Counter(k for s in keyed.values() for k in s)
    stop = {k for k, _ in freq.most_common(40)}
    xr = openbible()
    ix = collections.defaultdict(set)
    grams = {}
    for ref, seq in keyed.items():
        g = {tuple(seq[i:i + 3]) for i in range(len(seq) - 2) if not set(seq[i:i + 3]) <= stop}
        grams[ref] = g
        for x in g:
            ix[x].add(ref)
    existing = set()
    for r in conn.execute("SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse FROM scripture_links WHERE link_type='inner-biblical'"):
        existing.add(tuple(sorted([(r[0], r[1], r[2]), (r[3], r[4], r[5])])))
    found = {}
    for ref, g in grams.items():
        c = collections.Counter()
        for x in g:
            if len(ix[x]) <= 60:
                for t in ix[x]:
                    if t != ref:
                        c[t] += 1
        for t, n in c.items():
            if n < 2 or (ref[0] == t[0] and abs(ref[1] - t[1]) <= 1):
                continue
            key = tuple(sorted([ref, t]))
            if key in found:
                continue
            found[key] = (quotations.local_alignment(keyed[ref], keyed[t]),
                          weighted_alignment(keyed[ref], keyed[t], w, gap=1.0, mismatch=0.8))
    def corr(a, b):
        ea, eb = english_of(*a, "masoretic"), english_of(*b, "masoretic")
        return corroborated(xr, ea, eb) or corroborated(xr, eb, ea) if ea and eb else False
    print("rule                          links  new  corrob%  corrob% of new")
    known = set()
    for (ab, ac, a1, a2), (bb, bc, b1, b2) in KNOWN_OT:
        for v in range(a1, a2 + 1):
            for u in range(b1, b2 + 1):
                known.add(tuple(sorted([(ab, ac, v), (bb, bc, u)])))
    known_verses = {(ab, ac, v) for (ab, ac, a1, a2), _ in KNOWN_OT for v in range(a1, a2 + 1)}
    def kv(sel):
        return len({k[0] if k[0] in known_verses else k[1] for k in sel if k in known})
    print(f"known-parallel verses: {len(known_verses)}; current surface finds {kv(existing)}")
    for name, test in (("lemma-key SW >= 22", lambda p: p[0] >= 22), ("lemma-key SW >= 26", lambda p: p[0] >= 26),
                       ("lemma-key SW >= 30", lambda p: p[0] >= 30), ("weighted >= 26", lambda p: p[1] >= 26),
                       ("weighted >= 30", lambda p: p[1] >= 30), ("weighted >= 36", lambda p: p[1] >= 36)):
        sel = [k for k, p in found.items() if test(p)]
        new = [k for k in sel if k not in existing]
        c = sum(corr(*k) for k in sel)
        cn = sum(corr(*k) for k in new)
        print(f"{name:28} {len(sel):6} {len(new):5}  {100 * c / max(1, len(sel)):5.0f}%   {100 * cn / max(1, len(new)):5.0f}%   known {kv(sel)}")
    # Passage-level evidence: parallels come in runs. A weak verse pair whose neighbours on the same
    # diagonal also match is part of a borrowed passage, the way plagiarism detectors chain local hits.
    def diag_ok(key, thr):
        (a, b) = key
        for d in (-1, 1):
            na, nb = (a[0], a[1], a[2] + d), (b[0], b[1], b[2] + d)
            p = found.get(tuple(sorted([na, nb])))
            if p and p[1] >= thr:
                return True
        return False
    for lo in (14, 18, 22):
        sel = [k for k, p in found.items() if p[1] >= 36 or (p[1] >= lo and diag_ok(k, lo))]
        new = [k for k in sel if k not in existing]
        c = sum(corr(*k) for k in sel)
        cn = sum(corr(*k) for k in new)
        print(f"{'weighted>=36 or run>=' + str(lo):28} {len(sel):6} {len(new):5}  {100 * c / max(1, len(sel)):5.0f}%   {100 * cn / max(1, len(new)):5.0f}%   known {kv(sel)}")
    old_c = sum(corr(*k) for k in existing)
    print(f"{'current surface (822)':28} {len(existing):6}     -  {100 * old_c / len(existing):5.0f}%")


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "otg":
    run_ot_global()


# --- unfoldingWord: Translation Notes as an answer key, Translation Words as a bridge -----------

UW = dict(zip("GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV".split(),
              "Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal".split() + NT_BOOKS))


def load_tn_quotations(uw_dir):
    """New Testament verses whose Translation Note links an Old Testament verse, split by whether the
    note is filed under the quotation support article."""
    import csv
    import glob
    import os
    import re
    link = re.compile(r"\.\./\.\./([0-9a-z]{3})/(\d{3})/(\d{3})\.md")
    names = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
             "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalm", "Psalms",
             "Proverbs", "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea",
             "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"]
    codes = "Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal".split()
    NAMES = {n.lower(): c for n, c in zip(names, codes)}
    named = re.compile(r"\b(" + "|".join(sorted(names, key=len, reverse=True)) + r")\s+(\d{1,3}):(\d{1,3})", re.I)
    out = collections.defaultdict(set)
    tagged = collections.defaultdict(set)
    for path in glob.glob(os.path.join(uw_dir, "tn_*.tsv")):
        book = UW[os.path.basename(path)[3:6]]
        with open(path, encoding="utf-8") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if len(row) < 7 or ":" not in row[0]:
                    continue
                c, v = row[0].split(":", 1)
                if not (c.isdigit() and v.split("-")[0].isdigit()):
                    continue
                found = [(UW.get(x.upper()), oc, ov) for x, oc, ov in link.findall(row[6])]
                found += [(NAMES.get(n.lower()), oc, ov) for n, oc, ov in named.findall(row[6])]
                for ob, oc, ov in found:
                    if ob and ob not in NT_BOOKS:
                        ref = (book, int(c), int(v.split("-")[0]))
                        out[ref].add((ob, int(oc), int(ov)))
                        if "quotation" in row[3]:
                            tagged[ref].add((ob, int(oc), int(ov)))
    return out, tagged


def run_uw(uw_dir):
    tn, tagged = load_tn_quotations(uw_dir)
    web = load_gold()
    print(f"Translation Notes: {sum(len(v) for v in tn.values())} NT->OT verse links on {len(tn)} NT verses; "
          f"{sum(len(v) for v in tagged.values())} filed under a quotation article")
    web_pairs = {(r, (g[0], g[1], g[2])) for r, gs in web.items() for g in gs}
    tn_pairs = {(r, t) for r, ts in tagged.items() for t in ts}
    both = {(r, t) for r, t in tn_pairs if any(rr == r and t[0] == g[0] and t[1] == g[1] and abs(t[2] - g[2]) <= 1 for rr, g in web_pairs)}
    print(f"quotation-tagged pairs also in the WEB footnotes: {len(both)} of {len(tn_pairs)}")
    tn_gold = collections.defaultdict(list)
    for r, ts in tagged.items():
        for t in ts:
            tn_gold[r].append((t[0], t[1], t[2], t[2]))
    for name, links in (("surface >= 18", baseline_links(18)), ("surface, all candidates", baseline_links(0))):
        recall_report(f"{name} vs Translation Notes key", links, tn_gold)
    return tn_gold


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "uw":
    run_uw(sys.argv[2])


def load_twl(uw_dir):
    """Each verse as its sequence of Translation Words concepts (one per tagged Hebrew/Greek word)."""
    import csv
    import glob
    import os
    seqs = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(uw_dir, "twl_*.tsv"))):
        book = UW[os.path.basename(path)[4:7]]
        with open(path, encoding="utf-8") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if len(row) < 6 or ":" not in row[0]:
                    continue
                c, v = row[0].split(":", 1)
                if c.isdigit() and v.isdigit():
                    seqs[(book, int(c), int(v))].append(row[5].rsplit("/", 1)[-1])
    return seqs


HEBREW_FOLLOWING = [(("Matt", 2, 15), ("Hos", 11, 1)), (("John", 19, 37), ("Zech", 12, 10)), (("Matt", 8, 17), ("Isa", 53, 4)),
                    (("1Cor", 3, 19), ("Job", 5, 13)), (("Rom", 11, 35), ("Job", 41, 3)), (("Matt", 2, 6), ("Mic", 5, 1)),
                    (("Matt", 27, 10), ("Zech", 11, 13)), (("John", 12, 40), ("Isa", 6, 10)), (("Matt", 12, 18), ("Isa", 42, 1)),
                    (("John", 13, 18), ("Ps", 41, 10)), (("Matt", 24, 15), ("Dan", 12, 11)), (("Matt", 26, 64), ("Dan", 7, 13)),
                    (("John", 10, 34), ("Ps", 82, 6)), (("Rom", 1, 17), ("Hab", 2, 4))]


def run_twl(uw_dir):
    seqs = load_twl(uw_dir)
    nt = {k: v for k, v in seqs.items() if k[0] in NT_BOOKS}
    ot = {k: v for k, v in seqs.items() if k[0] not in NT_BOOKS}
    w, _ = idf_table(nt, ot)
    ix = collections.defaultdict(set)
    for ref, seq in ot.items():
        for k in set(seq):
            ix[k].add(ref)
    def rank(src, target):
        a = nt.get(src, [])
        if not a:
            return None, None
        cands = set()
        for k in set(a):
            if len(ix[k]) <= 800:
                cands |= ix[k]
        scores = sorted(((weighted_alignment(a, ot[t], w, gap=1.0, mismatch=0.5), t) for t in cands), reverse=True)
        for i, (s, t) in enumerate(scores):
            if t == target:
                return i + 1, round(s, 1)
        return None, None
    print("Hebrew-following quotations: rank of the right verse among all Old Testament verses, by concept match")
    for src, tgt in HEBREW_FOLLOWING:
        r, s = rank(src, tgt)
        print(f"  {src[0]} {src[1]}:{src[2]:<3} -> {tgt[0]} {tgt[1]}:{tgt[2]:<3} rank {r}  score {s}   NT concepts {nt.get(src)}")


if __name__ == "__main__" and (sys.argv[1:2] or ["nt"])[0] == "twl":
    run_twl(sys.argv[2])
