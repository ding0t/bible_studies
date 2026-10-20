"""Detecting where the New Testament quotes the Septuagint, and grading how strongly.

Retrieval is an n-gram inverted index, not an edit distance. Quotation is a *local* phenomenon --
a short span inside a longer verse -- so a whole-string similarity is dominated by the material the
two verses don't share, and 7,939 x 22,948 pairwise alignments is not a computation anyone runs.
Cheap recall first, precise scoring on the handful that survive.

Four graded measures, kept separate and never summed into one number:

  containment   shared 4-grams / the quoting verse's 4-grams -- how much of this verse is quotation.
  longest_run   the longest contiguous shared token run. Interpretable, and kept for that reason --
                a reader can go and count nine verbatim words. But it breaks at the first inserted
                or omitted one, and adapted quotation is the normal case.
  alignment     Smith-Waterman, which tolerates those edits. THE PRIMARY MEASURE.
  idf_overlap   shared n-grams weighted by rarity in the source corpus.

Both thresholds were set by auditing every pair against two cross-reference lists of independent
provenance -- openbible's crowd-voted set and the WEB translators' own footnotes, both in the
English scheme, neither with any connection to the method. Alignment separates far more sharply:

    alignment 20-29   86% corroborated        run 12+    85%
    alignment 15-19   55% corroborated        run 8-11   79%
    alignment 10-14   14% corroborated        run 4-5    11%

QUOTATION_ALIGNMENT marks 18: 140 pairs at 84%, against run>=8's 138 at 80%. Similar volume,
better precision, and it recovers quotations the run measure missed outright -- Matthew 1:23
quoting Isaiah 7:14 (run 5, alignment 24), Luke 4:18 quoting Isaiah 61:1 (run 6, alignment 25),
Acts 13:41 quoting Habakkuk 1:5 (run 7, alignment 33). Every one of those is corroborated.

Accents are stripped before matching: Brenton (1851) and the SBLGNT accent differently, so raw
surface forms fail to match even on identical words.

Every candidate above MIN_SHARED_NGRAMS is kept -- there is deliberately no per-verse cap. Capping
at the best few discarded 27% of qualifying pairs and, because ties broke on set iteration order,
returned a different set on each run. This feeds content, so a re-run that produces a different
answer would make every diff unreviewable.
"""
import collections
import math
import re
import unicodedata

MIN_SHARED_NGRAMS = 2
NGRAM = 4
QUOTATION_RUN = 8          # interpretable secondary measure, kept for readers to check
QUOTATION_ALIGNMENT = 18   # the primary threshold -- see the audit below

# Rare-lemma allusion is a different measurement and takes its own thresholds. A lemma occurring in
# at most RARE_LEMMA_VERSES verses across the whole Greek corpus is distinctive enough to carry
# evidence; two passages sharing several such lemmas are linked even with no shared phrasing.
# ALLUSION_WEIGHT is the summed rarity of what they share. Calibrated the same way as the others:
# random New Testament / Septuagint verse pairs are corroborated by a cross-reference 0.3% of the
# time, and pairs above this weight 52% of the time -- a 173x enrichment.
RARE_LEMMA_VERSES = 30
ALLUSION_WEIGHT = 14.0

_NON_GREEK = re.compile(r"[^Ͱ-Ͽἀ-῿\s]")
_NON_HEBREW = re.compile(r"[^\u05d0-\u05ea\s]")


def normalise_greek(text: str) -> list[str]:
    """Accent- and punctuation-free Greek tokens."""
    bare = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    return _NON_GREEK.sub(" ", bare.lower().replace("ς", "σ")).split()


def normalise_hebrew(text: str) -> list[str]:
    """Consonantal Hebrew tokens, with morpheme separators JOINED rather than split.

    This is the one that bites. The WLC marks morpheme boundaries with '/' and the scrolls with a
    geresh, while the Hebrew New Testaments mark nothing -- so splitting on the separator compares
    the WLC's ["ו", "יהי"] against Delitzsch's ["ויהי"] and they can never match. Splitting scored
    12% recall against the Greek-derived quotations; joining scores 81%. An easy way to get a
    confidently wrong answer about whether Hebrew works at all.
    """
    bare = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    bare = bare.replace("/", "").replace("\u05f3", "").replace("\u05be", " ")
    return _NON_HEBREW.sub(" ", bare).split()


# kept for callers that predate the Greek/Hebrew split
normalise = normalise_greek


def ngrams(tokens: list[str], n: int = NGRAM) -> set[str]:
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def local_alignment(a: list[str], b: list[str], match: int = 2, mismatch: int = -1,
                     gap: int = -1) -> int:
    """Smith-Waterman: the best-scoring shared span, tolerating insertions and omissions.

    The measure that matters, because adapted quotation is the normal case and a contiguous run
    breaks at the first edit. Luke 4:18 omits a clause from Isaiah 61:1 and scores a run of 6 --
    under the quotation threshold, so the method missed it outright -- while its alignment scores
    25, above verbatim Hebrews 10:5. Matthew 21:5 abbreviates Zechariah 9:9 to a run of 4 and
    aligns at 15.

    Kept alongside longest_run rather than replacing it: "nine verbatim tokens" is something a
    reader can go and check, an alignment score is not.
    """
    best, previous = 0, [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            current[j] = max(0,
                             previous[j - 1] + (match if a[i - 1] == b[j - 1] else mismatch),
                             previous[j] + gap,
                             current[j - 1] + gap)
            if current[j] > best:
                best = current[j]
        previous = current
    return best


def longest_shared_run(a: list[str], b: list[str]) -> int:
    best, previous = 0, [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def build_index(source_verses, tokenise=normalise_greek, n=NGRAM):
    """(ref -> tokens, ngram -> {ref}) for the text being quoted FROM."""
    tokens, index = {}, collections.defaultdict(set)
    for book, chapter, verse, text in source_verses:
        toks = tokenise(text)
        tokens[(book, chapter, verse)] = toks
        for gram in ngrams(toks, n):
            index[gram].add((book, chapter, verse))
    return tokens, index


def find_quotations(quoting_verses, source_tokens, index, tokenise=normalise_greek, n=NGRAM,
                     min_shared=MIN_SHARED_NGRAMS, exclude=None):
    """One dict per candidate pair, in an order independent of how the index happened to iterate.

    `idf_overlap` weights each shared n-gram by how rare it is in the source corpus, so a shared
    "and it came to pass" stops scoring like a shared rare phrase. Ranking by it puts 85% real
    quotations in the top 100, against 78% for the raw run.
    """
    documents = len(source_tokens) or 1
    for book, chapter, verse, text in quoting_verses:
        source_ref = (book, chapter, verse)
        toks = tokenise(text)
        grams = ngrams(toks, n)
        if not grams:
            continue
        hits = collections.Counter()
        for gram in grams:
            for ref in index.get(gram, ()):
                hits[ref] += 1
        candidates = [(ref, count) for ref, count in hits.items()
                      if count >= min_shared and not (exclude and exclude(source_ref, ref))]
        for ref, shared in sorted(candidates, key=lambda pair: (-pair[1], pair[0])):
            target = source_tokens[ref]
            common = grams & ngrams(target, n)
            yield {
                "from": source_ref,
                "to": ref,
                "shared_ngrams": shared,
                "containment": round(shared / len(grams), 4),
                "longest_run": longest_shared_run(toks, target),
                "alignment": local_alignment(toks, target),
                "idf_overlap": round(sum(math.log(documents / len(index[g])) for g in common), 3),
            }


# --- 2026-10: what the surface method missed ------------------------------------------------------
#
# Measured in link_lab.py against two answer keys with no connection to the method (the WEB
# translators' quotation footnotes and unfoldingWord's Translation Notes) and calibrated, like the
# thresholds above, on openbible corroboration. docs/dev/link-detection-research.md has the tables.
# Each rule below admits a link on its own and the row records which rule did (`basis`), so a link
# can always be explained and no score is ever a blend of the others.

# Unique phrases. A run of everyday words can be unique as a phrase: John 10:34 shares four common
# words with Psalm 82:6 (LXX 81:6), "I said, you are gods", and the phrase occurs in one Septuagint
# verse. That uniqueness is the evidence -- the fingerprinting idea plagiarism detectors use.
PHRASE_N = 3
UNIQUE_PHRASES = 3          # three phrases, each in one Septuagint verse: 87% corroborated
FORMULA_PHRASES = 2         # two, where the verse cites Scripture: 81% corroborated
PHRASE_NT_CAP = 12          # a phrase in more NT verses than this is an idiom, not a quotation
# The citing forms themselves -- "it is written", "the Scripture", "that it might be fulfilled", "what
# was spoken" -- in the verse or the one before. Forms, not lemmas: Revelation's "write" and
# Colossians' "be filled" are the same lemmas and are not citations, and admitted 13 false links.
# The Hebrew answer key: sixteen well-known parallels, (book, chapter, first verse, last verse) in the
# Masoretic numbering. link_lab.py set the Hebrew rules against it; export_links.py reports recall on it.
KNOWN_OT = [
    (("1Chr", 16, 8, 22), ("Ps", 105, 1, 15)), (("1Chr", 16, 23, 33), ("Ps", 96, 1, 13)),
    (("1Chr", 16, 34, 36), ("Ps", 106, 1, 48)), (("Joel", 4, 16, 16), ("Amos", 1, 2, 2)),
    (("Obad", 1, 1, 5), ("Jer", 49, 9, 16)), (("Ps", 108, 2, 6), ("Ps", 57, 8, 12)),
    (("Ps", 108, 7, 14), ("Ps", 60, 7, 14)), (("Ps", 70, 2, 6), ("Ps", 40, 14, 18)),
    (("Isa", 2, 2, 4), ("Mic", 4, 1, 3)), (("2Sam", 22, 2, 51), ("Ps", 18, 3, 51)),
    (("Ps", 14, 1, 7), ("Ps", 53, 2, 7)), (("1Chr", 17, 1, 27), ("2Sam", 7, 1, 29)),
    (("Ezra", 2, 1, 70), ("Neh", 7, 6, 73)), (("Exod", 20, 2, 17), ("Deut", 5, 6, 21)),
    (("2Chr", 36, 22, 23), ("Ezra", 1, 1, 3)), (("Isa", 37, 1, 38), ("2Kgs", 19, 1, 37)),
]

FORMULA_FORMS = {"γεγραπται", "γεγραμμενον", "γεγραμμενοσ", "γραφη", "γραφην", "γραφησ",
                 "πληρωθη", "πληρωθωσιν", "επληρωθη", "πληρωθηναι", "ρηθεν", "ειρηται", "ειρημενον"}

# Hebrew on lemmas. MACULA splits prefixes and normalises spelling, so 1 Chronicles 16:8 and Psalm
# 105:1 -- the same seven words, one written with a vowel letter -- align fully where the surface
# scored 12. Rarity-weighted; a weaker pair counts when its neighbours on the same diagonal also
# match, because borrowed passages come as runs. 61% corroborated against the surface method's 59%,
# and 211 of 266 verses of sixteen known parallels against 68.
LEMMA_ALIGNMENT = 36
LEMMA_RUN = 22

# Across the languages: New Testament Greek against the Hebrew, through a lexicon learned from the
# Septuagint's own translation choices. Only in verses that cite Scripture, only the best match, and
# only with a clear margin over the next. 75% corroborated. It reaches quotations that follow the
# Hebrew, and Matthew 24:15's "abomination of desolation" (Daniel 12:11), which no Greek method finds.
CROSSLANG_SCORE = 14.0
CROSSLANG_MARGIN = 2.0


def unique_phrases(quoting_rows, source_rows, n=PHRASE_N, nt_cap=PHRASE_NT_CAP):
    """{(quoting_ref, source_ref): number of shared phrases found in exactly one source verse}."""
    where = collections.defaultdict(set)
    for book, chapter, verse, text in source_rows:
        toks = normalise_greek(text)
        for i in range(len(toks) - n + 1):
            where[tuple(toks[i:i + n])].add((book, chapter, verse))
    quoting = {(b, c, v): normalise_greek(t) for b, c, v, t in quoting_rows}
    spread = collections.Counter()
    for toks in quoting.values():
        spread.update({tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)})
    out = collections.Counter()
    for ref, toks in quoting.items():
        for gram in {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}:
            hits = where.get(gram)
            if hits and len(hits) == 1 and spread[gram] <= nt_cap:
                out[(ref, next(iter(hits)))] += 1
    return out


def weighted_alignment(a, b, weights, gap=1.0, mismatch=0.8, default=0.5):
    """Smith-Waterman where a match is worth its key's rarity: two rare words in order outweigh six
    particles. Keys are lemmas or Strong's numbers, so spelling and inflection drop out."""
    best = 0.0
    prev = [0.0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0.0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            m = prev[j - 1] + (weights.get(a[i - 1], default) if a[i - 1] == b[j - 1] else -mismatch)
            cur[j] = max(0.0, m, prev[j] - gap, cur[j - 1] - gap)
            if cur[j] > best:
                best = cur[j]
        prev = cur
    return best


def learn_lexicon(verse_pairs, iterations=6, floor=0.05, keep=4):
    """P(hebrew | greek) by IBM Model 1 over aligned Septuagint/Masoretic verses: the translators'
    own choices, learned. Returns {greek key: [hebrew keys, most likely first]}."""
    t: dict = collections.defaultdict(lambda: 1e-3)
    for _ in range(iterations):
        count: dict = collections.defaultdict(float)
        total: dict = collections.defaultdict(float)
        for greek, hebrew in verse_pairs:
            for h in hebrew:
                z = sum(t[(h, g)] for g in greek)
                for g in greek:
                    c = t[(h, g)] / z
                    count[(h, g)] += c
                    total[g] += c
        t = collections.defaultdict(float, {k: v / total[k[1]] for k, v in count.items()})
    lexicon: dict = collections.defaultdict(list)
    for (h, g), p in t.items():
        if p >= floor:
            lexicon[g].append((p, h))
    return {g: [h for _, h in sorted(opts, reverse=True)[:keep]] for g, opts in lexicon.items()}


def crosslang_alignment(translated, hebrew, weights, stop, gap=0.8, mismatch=0.6):
    """Weighted alignment where a Greek position matches any of its learned Hebrew renderings."""
    best = 0.0
    prev = [0.0] * (len(hebrew) + 1)
    for i in range(1, len(translated) + 1):
        options = translated[i - 1]
        cur = [0.0] * (len(hebrew) + 1)
        for j in range(1, len(hebrew) + 1):
            h = hebrew[j - 1]
            m = prev[j - 1] + (weights.get(h, 0.5) if h in options and h not in stop else -mismatch)
            cur[j] = max(0.0, m, prev[j] - gap, cur[j - 1] - gap)
            if cur[j] > best:
                best = cur[j]
        prev = cur
    return best
