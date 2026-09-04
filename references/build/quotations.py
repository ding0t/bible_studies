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
