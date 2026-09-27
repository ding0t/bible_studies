"""Emit the data behind the site's verse and word pop-ups to docs/content/assets/popups/.

Committed rather than generated in CI, for the same reason as export_links.py: bible-text.db is a
gitignored build artifact the deploy workflow cannot rebuild. Re-run by hand when the data changes.

Everything written here ships to every reader's browser, so every source is `open` tier:

- verses/<Book>.json   World English Bible (public domain), the whole book, plus the strongest few
                       OpenBible.info cross-references per verse (CC BY). Whole books rather than
                       only the verses the site cites: a reader opening context around a cited
                       verse needs its neighbours, and a new study should not need a re-export.
- words/<H|G><nn>.json  one file per hundred Strong's numbers. Transliteration, part of speech and
                       gloss from STEPBible's TBESH/TBESG (CC BY); occurrence counts, where the
                       word occurs and its commonest contextual renderings from MACULA (CC BY
                       4.0) and the LXX lemmas.
                       TBESH's "Meaning" column is left out: its header says it derives from Online
                       Bible's abridged BDB and asks that permission be sought, which CC BY alone
                       does not settle.

Counts come from the data, never from a study's sentence, so a pop-up stays right when a study's
claim is wrong.

Usage: uv run python export_popups.py
"""
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import query

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs" / "content" / "assets" / "popups"
LEXICONS = REPO / "references" / "open-data" / "stepbible-data" / "Lexicons"
WEB = "ebible-eng-web"
CROSSREFS_PER_VERSE = 5
RENDERINGS = 5
EVERY_OCCURRENCE = 20
TOP_BOOKS = 5

POS = {
    "N": "noun", "V": "verb", "A": "adjective", "Adv": "adverb", "Conj": "conjunction",
    "Prep": "preposition", "Part": "particle", "Intj": "interjection", "Art": "article",
    "PerP": "pronoun", "DemP": "pronoun", "RelP": "pronoun", "IntP": "pronoun", "Intg": "interrogative",
    "Neg": "negative", "Cond": "conditional", "ImpP": "pronoun", "RecP": "pronoun", "RefP": "pronoun",
    "PosP": "pronoun", "IndP": "pronoun", "Cor": "correlative",
}
LANGUAGE = {"H": "Hebrew", "A": "Aramaic", "G": "Greek", "N": "name"}


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def export_verses(conn) -> int:
    books: dict[str, dict] = defaultdict(lambda: {"v": defaultdict(dict), "x": {}})
    for row in conn.execute(
            "SELECT book, chapter, verse, text FROM verses WHERE work_id=? ORDER BY book, chapter, verse",
            (WEB,)):
        books[row["book"]]["v"][str(row["chapter"])][str(row["verse"])] = row["text"].strip()

    # The OpenBible import carries duplicate rows; DISTINCT before ranking so a doubled row does
    # not take two of the five places.
    ranked = conn.execute(
        """SELECT DISTINCT from_book, from_chapter, from_verse, to_book, to_chapter,
                  to_verse_start, to_verse_end, votes
           FROM cross_references WHERE work_id='openbible-crossrefs' AND votes > 0
           ORDER BY from_book, from_chapter, from_verse, votes DESC""")
    for r in ranked:
        key = f"{r['from_chapter']}:{r['from_verse']}"
        refs = books[r["from_book"]]["x"].setdefault(key, [])
        if len(refs) < CROSSREFS_PER_VERSE:
            end = r["to_verse_end"] if r["to_verse_end"] != r["to_verse_start"] else None
            refs.append([r["to_book"], r["to_chapter"], r["to_verse_start"], end])

    for book, data in books.items():
        dump(OUT / "verses" / f"{book}.json", data)
    return len(books)


def read_lexicon(path: Path, prefix: str) -> dict[int, dict]:
    """First entry per Strong's number. Later rows for the same number are STEPBible's
    disambiguated sub-senses (usually proper names sharing the number); the first is the word.
    Where a number has no plain row at all -- H1350 is only H1350a "to redeem" and H1350b
    "redemption" -- the first lettered sense stands for it."""
    entries: dict[int, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if len(cols) < 7 or not re.fullmatch(rf"{prefix}\d{{4}}[a-zA-Z]?", cols[0]):
            continue
        number = int(cols[0][1:5])
        if number in entries:
            continue
        lang, _, rest = cols[5].partition(":")
        kind = rest.split("-")[0]
        entries[number] = {
            "l": cols[3].strip(),
            "t": cols[4].strip(),
            "p": "name" if lang == "N" else POS.get(kind, kind.lower()),
            "lang": LANGUAGE.get(lang, ""),
            "g": plain_gloss(cols[6]),
        }
    return entries


def plain_gloss(gloss: str) -> str:
    """STEPBible writes a sense as "word: sense" ("tree: wood", "to redeem: redeem"). Keep both
    halves unless the second only repeats the first."""
    head, _, sense = (part.strip() for part in gloss.partition(":"))
    return head if not sense or sense.lower() in head.lower() else f"{head}, {sense}"


# MACULA glosses each word in its own verse, so a participle can come back as "he" or a
# construct noun as "of". Those say nothing about the word.
FUNCTION_WORDS = {"he", "she", "it", "they", "him", "her", "them", "i", "you", "we", "the", "a",
                  "an", "of", "to", "and", "in", "that", "which", "who", "is", "be", "was", "his"}


def clean_gloss(gloss: str) -> str:
    gloss = re.sub(r"[\[\]<>]", "", gloss).replace(".", " ").replace("_", " ")
    return re.sub(r"\s+", " ", gloss).strip().lower()


def usage(conn, work_id: str) -> tuple[Counter, dict[int, Counter], dict[int, list]]:
    """Occurrences and contextual glosses per Strong's number, matched the way bible_concordance
    matches -- on the exact id -- so a pop-up agrees with the count a study was checked against.
    MACULA's lettered ids are not always senses of the plain word (0539a is "foster-father", a
    sense of H539; 0001b is the Aramaic emphatic ending, glossed "king", nothing to do with H1), so
    they count only for a number that has no plain rows at all.

    Also returns where each word occurs, one entry per verse in canonical order."""
    plain: Counter = Counter()
    lettered: Counter = Counter()
    glosses = {True: defaultdict(Counter), False: defaultdict(Counter)}
    places = {True: defaultdict(dict), False: defaultdict(dict)}
    for row in conn.execute(
            "SELECT strongs_id, gloss, book, chapter, verse FROM morphology "
            "WHERE work_id=? AND strongs_id != '' ORDER BY rowid", (work_id,)):
        m = re.fullmatch(r"(\d+)([a-zA-Z]?)", row["strongs_id"] or "")
        if not m:
            continue
        number, is_plain = int(m[1]), not m[2]
        (plain if is_plain else lettered)[number] += 1
        if row["gloss"]:
            glosses[is_plain][number][clean_gloss(row["gloss"])] += 1
        places[is_plain][number][(row["book"], row["chapter"], row["verse"])] = None
    counts = Counter({n: plain[n] or lettered[n] for n in plain.keys() | lettered.keys()})
    chosen = {n: glosses[True][n] if plain[n] else glosses[False][n] for n in counts}
    where = {n: list(places[bool(plain[n])][n]) for n in counts}
    return counts, defaultdict(Counter, chosen), defaultdict(list, where)


def spread(verses: list) -> dict:
    """A rare word lists every verse it is in -- the list a study's "only here" claim can be
    checked against. A common word gives the books it is concentrated in instead."""
    if len(verses) <= EVERY_OCCURRENCE:
        return {"o": [list(v) for v in verses]}
    return {"b": [[b, n] for b, n in Counter(b for b, _, _ in verses).most_common(TOP_BOOKS)]}


def export_words(conn) -> int:
    hebrew = read_lexicon(next(LEXICONS.glob("TBESH*.txt")), "H")
    greek = read_lexicon(next(LEXICONS.glob("TBESG*.txt")), "G")
    ot, ot_glosses, ot_places = usage(conn, "macula-hebrew-wlc")
    nt, nt_glosses, nt_places = usage(conn, "macula-greek-sblgnt")
    lxx, _, _ = usage(conn, "lxx-lemmas")

    written = 0
    for prefix, lexicon in (("H", hebrew), ("G", greek)):
        shards: dict[int, dict] = defaultdict(dict)
        for number, entry in lexicon.items():
            if prefix == "H":
                entry["c"] = {"ot": ot[number]}
                renderings = ot_glosses[number]
                entry.update(spread(ot_places[number]))
            else:
                entry["c"] = {"nt": nt[number], "lxx": lxx[number]}
                renderings = nt_glosses[number]
                entry.update(spread(nt_places[number]))
            useful = ((g, n) for g, n in renderings.most_common() if g and g not in FUNCTION_WORDS)
            entry["r"] = [[g, n] for g, n in list(useful)[:RENDERINGS]]
            shards[number // 100][str(number)] = entry
        for shard, data in shards.items():
            dump(OUT / "words" / f"{prefix}{shard:02d}.json", data)
            written += 1
    return written


def main() -> int:
    conn = query.connect()
    if OUT.exists():
        shutil.rmtree(OUT)
    books = export_verses(conn)
    shards = export_words(conn)
    size = sum(p.stat().st_size for p in OUT.rglob("*.json"))
    print(f"wrote {books} verse files and {shards} word files to {OUT.relative_to(REPO)} "
          f"({size / 1_000_000:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
