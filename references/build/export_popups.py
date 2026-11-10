"""Emit the data behind the site's verse and word pop-ups to docs/content/assets/popups/.

Committed rather than generated in CI, for the same reason as export_links.py: bible-text.db is a
gitignored build artifact the deploy workflow cannot rebuild. Re-run by hand when the data changes.

Everything written here ships to every reader's browser, so every source is `open` tier:

- verses/<Book>.json   the site's reading translation (sources.toml [reading_translation], the BSB
                       since 2026-10-28), the whole book, with its footnotes and the strongest few
                       OpenBible.info cross-references per verse (CC BY). Whole books rather than
                       only the verses the site cites: a reader opening context around a cited
                       verse needs its neighbours, and a new study should not need a re-export.
                       `t` names the translation, so nothing downstream hard-codes one; a verse
                       the reading text omits (Matthew 17:21) comes from the fallback and is
                       listed in `f`, so it can be labelled rather than shown as though printed.
- words/<H|G><nn>.json  one file per hundred Strong's numbers. Transliteration, part of speech and
                       gloss from STEPBible's TBESH/TBESG (CC BY); occurrence counts, where the
                       word occurs and its commonest contextual renderings from MACULA (CC BY
                       4.0) and the LXX lemmas.
                       TBESH's "Meaning" column is left out: its header says it derives from Online
                       Bible's abridged BDB and asks that permission be sought, which CC BY alone
                       does not settle.
- forms/<hex>.json     every inflected form in the Hebrew Bible (OSHB morphhb, CC BY), the Greek NT
                       (MACULA) and the LXX lemmas, keyed by form_key and sharded by first two letters,
                       mapped to its Strong's number. This is what lets ὑψωθῆναι open G5312 and a
                       quoted Hebrew sentence open word by word, with no tag in the study.
- parse/<hex>.json     the same keys, mapped to the form's morphology code where one parsing covers
                       nearly all its occurrences, and grammar.json, STEPBible's plain-English
                       reading of each code (TEGMC/TEHMC, CC BY): "a male PERSON that is having
                       something done to them". A form with two common parsings gets none, since
                       the card cannot know which the page means.
- original/<Book>/<chapter>.json  each verse in the language it was written in, numbered as the
                       reading translation numbers it: the Berean Interlinear's words (public domain),
                       the text the BSB translates, each with its Strong's number, transliteration,
                       the BSB's English for it and where that English sits in the BSB verse, plus
                       MACULA's parsing code (CC BY 4.0) for grammar.json. An Old Testament chapter
                       also carries Brenton's Septuagint, a New Testament one Salkinson-Ginsburg's
                       Hebrew translation. See export_originals.
- A name's entry also says who it is: each individual STEPBible's TIPNR files under the number
  (CC BY), with STEP's one-line description, parents, spouses and children, and the id of the
  person in this site's family tree where genealogy_check.py matches one. A Greek name points at
  its Hebrew original (TBESG's "the Greek of"), and the Hebrew name back, so Jesse's card counts
  both testaments.

Counts come from the data, never from a study's sentence, so a pop-up stays right when a study's
claim is wrong.

Usage: uv run python export_popups.py
"""
import difflib
import json
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import genealogy_check
import query
import source_catalog
import versification

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs" / "content" / "assets" / "popups"
LEXICONS = REPO / "references" / "open-data" / "stepbible-data" / "Lexicons"
MORPHOLOGY = REPO / "references" / "open-data" / "stepbible-data" / "Morphology codes"
PEOPLE_PER_NAME = 4
FAMILY_SHOWN = 6
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
    reading = source_catalog.reading_translation()
    meta = {"code": reading["code"], "name": reading["name"], "licence": reading["licence"],
            "fallback": {"code": reading["fallback_code"], "name": reading["fallback_name"],
                         "note": reading["fallback_note"]}}
    books: dict[str, dict] = defaultdict(lambda: {"t": meta, "v": defaultdict(dict), "f": [],
                                                  "n": {}, "x": {}})
    for row in conn.execute(
            "SELECT book, chapter, verse, text FROM verses WHERE work_id=? ORDER BY book, chapter, verse",
            (reading["work_id"],)):
        books[row["book"]]["v"][str(row["chapter"])][str(row["verse"])] = row["text"].strip()
    for row in conn.execute(
            "SELECT book, chapter, verse, text FROM verses WHERE work_id=? ORDER BY book, chapter, verse",
            (reading["fallback_work_id"],)):
        chapter = books[row["book"]]["v"][str(row["chapter"])]
        if str(row["verse"]) not in chapter:
            chapter[str(row["verse"])] = row["text"].strip()
            books[row["book"]]["f"].append(f"{row['chapter']}:{row['verse']}")
    for row in conn.execute(
            "SELECT book, chapter, verse, text FROM notes WHERE work_id=? ORDER BY rowid",
            (reading["work_id"],)):
        books[row["book"]]["n"].setdefault(f"{row['chapter']}:{row['verse']}", []).append(row["text"])

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


# STEPBible's own ids, "H3448" or the disambiguated "H5660G": the language, then the number.
_STEP_STRONGS = re.compile(r"([HG])(\d{1,4})")


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
        # "G2421 = the Greek of  H3448": the Greek spelling of a Hebrew word, nearly always a name.
        if "the Greek of" in cols[1] and (target := _STEP_STRONGS.match(cols[2].strip())):
            entries[number]["e"] = f"{target[1]}{int(target[2])}"
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
    """Occurrences and contextual glosses per Strong's number, parsed by query.parse_strongs_id as
    bible_concordance parses it, so a pop-up agrees with the count a study was checked against.
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
        parsed = query.parse_strongs_id(row["strongs_id"])
        if not parsed:
            continue
        number, is_plain = parsed[0], not parsed[1]
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


def individuals(conn) -> dict[str, list[dict]]:
    """Each TIPNR individual under its plain Strong's number, most often named first. STEP
    disambiguates by letter -- H5660G and H5660H are two men called Abdi -- and a page tags only
    the number, so the card lists them all rather than pick one."""
    in_tree = {}
    for person_id, person in genealogy_check.site_people().items():
        name_id, _ = genealogy_check.match(conn, person)
        if name_id:
            in_tree.setdefault(name_id, person_id)
    verses = Counter(dict(conn.execute(
        "SELECT name_id, COUNT(*) FROM name_references GROUP BY name_id").fetchall()))

    def names(value: str | None) -> list[str]:
        found = [re.sub(r"@[^(]*", "", part).replace("_", " ").strip()
                 for part in (value or "").split(",") if part.strip()]
        if len(found) > FAMILY_SHOWN:
            return found[:FAMILY_SHOWN] + [f"{len(found) - FAMILY_SHOWN} more"]
        return found

    found: dict[str, list] = defaultdict(list)
    for row in conn.execute(
            "SELECT name_id, kind, name, strongs, description, parents, partners, offspring, "
            "group_or_area, brief FROM proper_names WHERE strongs IS NOT NULL"):
        parsed = _STEP_STRONGS.match(row["strongs"])
        if not parsed:
            continue
        person = {"n": row["name"], "k": row["kind"],
                  "d": row["brief"] or row["description"] or row["group_or_area"] or ""}
        for field, key in (("parents", "pa"), ("partners", "sp"), ("offspring", "ch")):
            if row[field] and row["kind"] != "place":
                person[key] = names(row[field])
        if row["name_id"] in in_tree:
            person["id"] = in_tree[row["name_id"]]
        found[f"{parsed[1]}{int(parsed[2])}"].append((verses[row["name_id"]], person))
    return {number: [p for _, p in sorted(people, key=lambda x: -x[0])]
            for number, people in found.items()}


# STEPBible heads the divine name יְהֹוָה and transliterates it ye.ho.vah: the minority pointing (46
# times in the WLC, against 5,677 for יְהוָה) read as though its vowels were the name's own, which
# is how "Jehovah" was coined (docs/content/hebrew/pronunciation.md). The card prints the name as
# the text does and says how it is read, as the word cards do.
DIVINE_NAME = {
    3068: {"l": "יְהוָה", "t": "Yahweh (read Adonai)"},
    3069: {"l": "יְהוִה", "t": "Yahweh (read Elohim)"},
}
# STEPBible files ὕψιστος "Most High" as "the Greek of" H3068, yet its own entry says the LXX uses it
# "chiefly for עֶלְיוֹן"; kept, the YHWH card called it "the Greek spelling" of the name.
NOT_THE_GREEK_OF = {5310}


def export_words(conn) -> int:
    hebrew = read_lexicon(next(LEXICONS.glob("TBESH*.txt")), "H")
    greek = read_lexicon(next(LEXICONS.glob("TBESG*.txt")), "G")
    for number, fix in DIVINE_NAME.items():
        hebrew[number].update(fix)
    for number in NOT_THE_GREEK_OF:
        greek[number].pop("e", None)
    ot, ot_glosses, ot_places = usage(conn, "macula-hebrew-wlc")
    nt, nt_glosses, nt_places = usage(conn, "macula-greek-sblgnt")
    lxx, _, _ = usage(conn, "lxx-lemmas")

    greek_of = defaultdict(list)
    for number, entry in greek.items():
        if "e" in entry:
            greek_of[int(entry["e"][1:])].append(number)
    who = individuals(conn)

    written = 0
    for prefix, lexicon in (("H", hebrew), ("G", greek)):
        shards: dict[int, dict] = defaultdict(dict)
        for number, entry in lexicon.items():
            # Both halves of a name's count: Jesse is 42 times in the OT as H3448, 5 in the NT as G2421.
            if prefix == "G" and "e" in entry:
                hebrew_number = int(entry["e"][1:])
                entry["x"] = [{"id": entry["e"], "ot": ot[hebrew_number]}]
                people = who.get(entry["e"], [])
            else:
                if prefix == "H" and greek_of.get(number):
                    entry["x"] = [{"id": f"G{g}", "nt": nt[g]} for g in greek_of[number]]
                people = who.get(f"{prefix}{number}", [])
            if entry["p"] == "name" and people:
                entry["w"] = people[:PEOPLE_PER_NAME]
                if len(people) > PEOPLE_PER_NAME:
                    entry["wn"] = len(people)
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


# form_key must stay identical to formKey in app/src/utils/scriptureRefs.js: the browser looks a
# page's word up by it. Greek keeps its breathings, acute, circumflex and iota subscript, because
# those are what tell ἦν "was" from ἥν "whom"; a grave is the same accent as an acute. Hebrew drops
# cantillation, meteg and maqaf and keeps its vowel points. bare_key drops every mark, for studies
# that quote an unaccented or unpointed text, and is consulted only when the full key misses.
_HEBREW_MARKS = re.compile("[֑-ֽ֯־׀׃;·ʼ’']")
_GREEK_MARKS = re.compile("[̀-ͯ]")
_GREEK_KEPT = {"́", "̓", "̔", "͂", "ͅ"}
_ALL_MARKS = re.compile("[̀-ְͯ-ׇ]")
# A form whose commonest number has less than this share of its occurrences is ambiguous: the
# browser links it only when the page has already tagged one of its numbers.
DOMINANT = 0.8
MAX_CANDIDATES = 4


def form_key(word: str) -> str:
    plain = unicodedata.normalize("NFD", word).replace("̀", "́")
    plain = _GREEK_MARKS.sub(lambda m: m[0] if m[0] in _GREEK_KEPT else "", _HEBREW_MARKS.sub("", plain))
    return unicodedata.normalize("NFC", plain).lower().replace("ς", "σ")


def bare_key(key: str) -> str:
    return unicodedata.normalize("NFC", _ALL_MARKS.sub("", unicodedata.normalize("NFD", key)))


def shard_of(key: str) -> str:
    """The first two letters, points dropped: one letter alone leaves the vav shard at 640 KB,
    since every "and" form starts with it."""
    return "".join(f"{ord(ch):04x}" for ch in bare_key(key)[:2])


def export_forms(conn, grammar: dict, used: dict) -> int:
    """A key takes its numbers from the first source that has it: the forms attested in the Hebrew
    Bible and the Greek NT, then the lexicons' dictionary forms (so δίδωμι or שָׁבַת named with no
    number still resolves), then the bare keys of both, then the Septuagint's lemmas, which carry
    no accents at all."""
    known = {
        "H": set(read_lexicon(next(LEXICONS.glob("TBESH*.txt")), "H")),
        "G": set(read_lexicon(next(LEXICONS.glob("TBESG*.txt")), "G")),
    }
    attested, lexicon, septuagint = (defaultdict(Counter) for _ in range(3))
    parsings: dict[tuple[str, str], Counter] = defaultdict(Counter)

    def add(tier: dict, prefix: str, word: str | None, strongs: str | None,
            morph: str | None = None) -> None:
        parsed = query.parse_strongs_id(strongs)
        if not word or not parsed or parsed[0] not in known[prefix]:
            return
        key = form_key(word.replace("/", ""))
        if sum(ch.isalpha() for ch in key) >= 2:
            tier[key][f"{prefix}{parsed[0]}"] += 1
            if morph:
                parsings[key, f"{prefix}{parsed[0]}"][morph] += 1

    for row in conn.execute(
            "SELECT surface_form, strongs_id, morph_code FROM morphology WHERE work_id='morphhb-wlc'"):
        add(attested, "H", row["surface_form"], row["strongs_id"], row["morph_code"])
    for row in conn.execute(
            "SELECT surface_form, strongs_id, morph_code FROM morphology "
            "WHERE work_id='macula-greek-sblgnt'"):
        add(attested, "G", row["surface_form"], row["strongs_id"], row["morph_code"])
    for row in conn.execute(
            "SELECT lemma, strongs_id FROM morphology WHERE work_id='lxx-lemmas'"):
        add(septuagint, "G", row["lemma"], row["strongs_id"])
    for prefix, glob in (("H", "TBESH*.txt"), ("G", "TBESG*.txt")):
        for number, entry in read_lexicon(next(LEXICONS.glob(glob)), prefix).items():
            add(lexicon, prefix, entry["l"], str(number))

    def bare(tier: dict) -> dict:
        stripped: dict[str, Counter] = defaultdict(Counter)
        for key, ids in tier.items():
            stripped[bare_key(key)].update(ids)
        return stripped

    forms: dict[str, Counter] = {}
    for tier in (attested, lexicon, bare(attested), bare(lexicon), septuagint):
        for key, ids in tier.items():
            forms.setdefault(key, ids)

    shards: dict[str, dict] = defaultdict(dict)
    parses: dict[str, dict] = defaultdict(dict)
    for key, ids in forms.items():
        total = sum(ids.values())
        ranked = ids.most_common()
        if ranked[0][1] / total >= DOMINANT:
            value = ranked[0][0]
            code = dominant_parsing(parsings.get((key, value)))
            explained = code and explain(code, value[0], grammar)
            if explained:
                parses[shard_of(key)][key] = code
                used.update(explained)
        else:
            value = [i for i, n in ranked[:MAX_CANDIDATES] if n / total >= 0.1]
        shards[shard_of(key)][key] = value
    for shard, data in shards.items():
        dump(OUT / "forms" / f"{shard}.json", dict(sorted(data.items())))
    for shard, data in parses.items():
        dump(OUT / "parse" / f"{shard}.json", dict(sorted(data.items())))
    return len(shards)


# OSHB morphemes that attach to a word rather than carry it: the prefixed preposition, conjunction,
# article and interrogative, and every suffix. A word's own number is its last morpheme not in this
# list, so וְאֵת is H853 and לְדָוִד H1732; עָלַי, all prefix and suffix, is its preposition.
_ATTACHED = ("R", "C", "Td", "Ti", "S")
_CRITICAL_SIGNS = re.compile("[⸀-⸅]")
_CANTILLATION = re.compile("[֑-֯׀]")
_STOPS = ".,;·:—()[]’'\""


def macula_hebrew(conn, book: str, chapter: int, verse: int, aramaic: set[int]) -> list[tuple]:
    """(number, OSHB code) for each word of a Hebrew verse, MACULA's morphemes rejoined into words
    (a word is its node id without the last digit). The code carries its language letter
    ("HC/To", "ANcmsd/Td"), as grammar.json is keyed."""
    grouped: dict[str, list] = {}
    for r in conn.execute(
            "SELECT node_id, strongs_id, morph_code FROM morphology WHERE work_id='macula-hebrew-wlc' "
            "AND book=? AND chapter=? AND verse=? AND node_id IS NOT NULL ORDER BY word_position",
            (book, chapter, verse)):
        grouped.setdefault(r["node_id"][:-1], []).append(r)
    words = []
    for parts in grouped.values():
        main = next((p for p in reversed(parts) if not (p["morph_code"] or "").startswith(_ATTACHED)),
                    parts[0])
        parsed = query.parse_strongs_id(main["strongs_id"])
        number = parsed[0] if parsed else None
        codes = [p["morph_code"] for p in parts]
        words.append((number, ("A" if number in aramaic else "H") + "/".join(codes) if all(codes) else None))
    return words


def hebrew_verses_of(conn, book: str) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """The Hebrew verses each English verse of a book holds. A Hebrew verse is placed by UHB's own
    per-verse record of its number, else the scheme map; one no English verse claims -- a psalm's
    title, which the BSB prints inside verse 1 -- goes to the English verse after it."""
    english = [(r["chapter"], r["verse"]) for r in conn.execute(
        "SELECT chapter, verse FROM verses WHERE work_id='berean-bsb' AND book=? ORDER BY chapter, verse",
        (book,))]
    claimed = {}
    for c, v in english:
        stated = query._stated_alt_ref(conn, book, c, v)
        ref = ((book, stated["alt_chapter"], stated["alt_verse"]) if stated
               else versification.align(book, c, v, "english", "masoretic"))
        if ref and (ref[1], ref[2]) not in claimed:
            claimed[(ref[1], ref[2])] = (c, v)
    held: dict[tuple[int, int], list] = defaultdict(list)
    pending = []
    for r in conn.execute("SELECT DISTINCT chapter, verse FROM morphology WHERE work_id='macula-hebrew-wlc' "
                          "AND book=? ORDER BY chapter, verse", (book,)):
        hv = (r["chapter"], r["verse"])
        if hv in claimed:
            held[claimed[hv]] += pending + [hv]
            pending = []
        else:
            pending.append(hv)
    return held


def english_spans(text: str, words: list[list], english_order: list[int | None]) -> list[tuple[int, int] | None]:
    """Where each word's BSB English sits in the BSB verse. The tables list the English in the BSB's
    own order, so the phrases are found left to right from a moving cursor: the second "that" in
    John 3:16 is ἵνα's because ὥστε's was found first."""
    spans: list[tuple[int, int] | None] = [None] * len(words)
    cursor = 0
    lowered = text.lower()
    for i in sorted((i for i, o in enumerate(english_order) if o is not None), key=lambda i: english_order[i]):
        phrase = re.sub(r"\s+", " ", words[i][3].replace("[", "").replace("]", "")).strip()
        at = text.find(phrase, cursor)
        if at < 0:
            at = lowered.find(phrase.lower(), cursor)
        if at >= 0:
            spans[i] = (at, at + len(phrase))
            cursor = at + len(phrase)
    return spans


def pair(numbers_a: list, numbers_b: list) -> dict[int, int]:
    """Index in a -> index in b, matching the two Strong's sequences."""
    matcher = difflib.SequenceMatcher(None, numbers_a, numbers_b, autojunk=False)
    return {block.a + i: block.b + i for block in matcher.get_matching_blocks() for i in range(block.size)}


QUOTED_PER_VERSE = 2
SHARED_RUN = 2


def septuagint_quoted(conn, book: str, chapter: int, verse: int, words: list[list]) -> list:
    """The Septuagint verses a New Testament verse quotes (scripture_links 'quotation-greek', the
    strong links only, strongest first), each with the words the two share marked: runs of at least
    two words in the same order, so a shared article alone marks nothing. A run marks the NT word's
    index into `words` and the Septuagint word's index into its text split on spaces.

    Each entry is [English reference, Septuagint number, text, Septuagint indices]; the NT indices
    of all of them are merged into the verse's last entry, [None, None, None, NT indices]."""
    nt_keys = [bare_key(form_key(w[0].strip(_STOPS))) for w in words]
    entries, nt_marked = [], set()
    for link in conn.execute(
            "SELECT to_book, to_chapter, to_verse, to_english_chapter, to_english_verse FROM scripture_links "
            "WHERE link_type='quotation-greek' AND strong=1 AND from_book=? AND from_chapter=? AND "
            "from_verse=? ORDER BY alignment DESC LIMIT ?", (book, chapter, verse, QUOTED_PER_VERSE)):
        if link["to_english_chapter"] is None:
            continue
        text = conn.execute("SELECT text FROM verses WHERE work_id='ebible-grcbrent' AND book=? AND "
                            "chapter=? AND verse=?", (link["to_book"], link["to_chapter"], link["to_verse"])).fetchone()
        if not text:
            continue
        lxx_keys = [bare_key(form_key(t.strip(_STOPS))) for t in text["text"].split()]
        lxx_marked = []
        matcher = difflib.SequenceMatcher(None, nt_keys, lxx_keys, autojunk=False)
        for block in matcher.get_matching_blocks():
            if block.size >= SHARED_RUN:
                nt_marked.update(range(block.a, block.a + block.size))
                lxx_marked += range(block.b, block.b + block.size)
        entries.append([f"{link['to_book']} {link['to_english_chapter']}:{link['to_english_verse']}",
                        f"{link['to_chapter']}:{link['to_verse']}", text["text"].strip(), lxx_marked])
    if entries:
        entries.append([None, None, None, sorted(nt_marked)])
    return entries


def export_originals(conn, grammar: dict, used: dict) -> int:
    """original/<Book>/<chapter>.json: each verse in the language it was written in, word by word,
    for the verse card's Hebrew, Greek and word-by-word views and for linking the BSB's English to
    the word it renders. An Old Testament chapter also carries Brenton's Septuagint (`g`), a New
    Testament one Salkinson-Ginsburg's Hebrew translation (`s`).

    The words are the Berean Interlinear's (interlinear_words): the text the BSB translates, in the
    BSB's own numbering, so the card shows the Greek behind the English the reader is reading. Each
    word is [form, Strong's id, grammar code, BSB English, transliteration, start, end]: the code is
    MACULA's (OSHB or Robinson, which grammar.json reads in plain English), matched to the word by
    Strong's sequence; start and end place the English in the BSB verse. A Hebrew verse the Hebrew
    Bible numbers differently is split into its Hebrew verses, each labelled with its number."""
    aramaic = {n for n, e in read_lexicon(next(LEXICONS.glob("TBESH*.txt")), "H").items()
               if e["lang"] == "Aramaic"}
    files = 0
    books = [r[0] for r in conn.execute("SELECT DISTINCT book FROM interlinear_words")]
    for book in books:
        chapters: dict[int, dict] = defaultdict(lambda: {"v": {}})
        greek = conn.execute("SELECT 1 FROM interlinear_words WHERE book=? AND work_id='berean-greek' LIMIT 1",
                             (book,)).fetchone() is not None
        held = {} if greek else hebrew_verses_of(conn, book)
        verses = defaultdict(list)
        for r in conn.execute("SELECT chapter, verse, surface_form, strongs_id, morph_code, transliteration, "
                              "english, english_position FROM interlinear_words WHERE book=? "
                              "ORDER BY chapter, verse, word_position", (book,)):
            verses[(r["chapter"], r["verse"])].append(r)
        bsb = {(r["chapter"], r["verse"]): r["text"].strip() for r in conn.execute(
            "SELECT chapter, verse, text FROM verses WHERE work_id='berean-bsb' AND book=?", (book,))}
        for (c, v), rows in verses.items():
            numbers = [int(r["strongs_id"]) if (r["strongs_id"] or "").isdigit() else None for r in rows]
            prefix = "G" if greek else "H"
            words = [[_CANTILLATION.sub("", r["surface_form"]), f"{prefix}{n}" if n else 0, 0,
                      r["english"] or 0, r["transliteration"] or 0] for r, n in zip(rows, numbers)]
            labels: list[str | None] = [None] * len(words)
            if greek:
                macula = conn.execute(
                    "SELECT surface_form, strongs_id, morph_code FROM morphology WHERE "
                    "work_id='macula-greek-sblgnt' AND book=? AND chapter=? AND verse=? ORDER BY word_position",
                    (book, c, v)).fetchall()
                text = conn.execute("SELECT text FROM verses WHERE work_id='sblgnt' AND book=? AND chapter=? "
                                    "AND verse=?", (book, c, v)).fetchone()
                tokens = _CRITICAL_SIGNS.sub("", text["text"]).split() if text else []
                if len(tokens) != len(macula):
                    tokens = []
                matched = pair(numbers, [(p[0] if (p := query.parse_strongs_id(m["strongs_id"])) else None)
                                         for m in macula])
                for i, j in matched.items():
                    words[i][2] = macula[j]["morph_code"] or 0
                    # The SBLGNT's punctuation, where the two texts have the same word here.
                    if tokens and bare_key(form_key(tokens[j].strip(_STOPS))) == bare_key(form_key(words[i][0])):
                        words[i][0] = words[i][0] + tokens[j][len(tokens[j].rstrip(".,;·:—")):]
            else:
                segments = held.get((c, v), [])
                hebrew = [(hv, w) for hv in segments for w in macula_hebrew(conn, book, *hv, aramaic)]
                matched = pair(numbers, [w[0] for _, w in hebrew])
                for i, j in matched.items():
                    words[i][2] = hebrew[j][1][1] or 0
                    labels[i] = f"{hebrew[j][0][0]}:{hebrew[j][0][1]}"
                # A word the match missed belongs to the Hebrew verse of the word before it.
                for i in range(1, len(labels)):
                    labels[i] = labels[i] or labels[i - 1]
                first = next((lab for lab in labels if lab), None)
                labels = [lab or first for lab in labels]
            for i, span in enumerate(english_spans(bsb.get((c, v), ""), words,
                                                   [r["english_position"] if r["english"] else None for r in rows])):
                if span:
                    words[i] += list(span)
            for word in words:
                if word[2] and (explained := explain(word[2], prefix, grammar)):
                    used.update(explained)
            distinct = list(dict.fromkeys(labels))
            if greek or distinct == [f"{c}:{v}"] or distinct == [None]:
                chapters[c]["v"][str(v)] = words
            else:
                chapters[c]["v"][str(v)] = {"p": [[label, [w for w, lab in zip(words, labels) if lab == label]]
                                                  for label in distinct]}
            if greek:
                text = conn.execute("SELECT text FROM verses WHERE work_id='ebible-hebsg' AND book=? AND "
                                    "chapter=? AND verse=?", (book, c, v)).fetchone()
                if text:
                    chapters[c].setdefault("s", {})[str(v)] = text["text"].strip()
                quoted = septuagint_quoted(conn, book, c, v, words)
                if quoted:
                    chapters[c].setdefault("q", {})[str(v)] = quoted
                continue
            # Brenton numbers a psalm's title as its verse 1, as the Hebrew does, so the Septuagint is
            # found from each Hebrew verse rather than from the English one.
            septuagint = []
            for hv in held.get((c, v), []):
                ref = versification.align(book, *hv, "masoretic", "lxx")
                text = ref and conn.execute("SELECT text FROM verses WHERE work_id='ebible-grcbrent' AND "
                                            "book=? AND chapter=? AND verse=?", ref).fetchone()
                if text:
                    septuagint.append([f"{ref[1]}:{ref[2]}", text["text"].strip()])
            if len(septuagint) == 1 and septuagint[0][0] == f"{c}:{v}":
                chapters[c].setdefault("g", {})[str(v)] = septuagint[0][1]
            elif septuagint:
                chapters[c].setdefault("g", {})[str(v)] = {"p": septuagint}
        for c, data in chapters.items():
            dump(OUT / "original" / book / f"{c}.json", data)
            files += 1
    return files


def dominant_parsing(codes: Counter | None) -> str | None:
    if not codes:
        return None
    code, n = codes.most_common(1)[0]
    return code if n / sum(codes.values()) >= DOMINANT else None


def explain(code: str, prefix: str, grammar: dict) -> dict | None:
    """The grammar entries a code needs, keyed as the browser looks them up: the Greek code
    whole, a Hebrew one per segment with its language letter ("HC/Vqw3ms" is "HC" and "HVqw3ms").
    None if any part has no reading, so a card never explains half a word."""
    if prefix == "G":
        parts = [code]
    else:
        language, rest = code[0], code[1:]
        parts = [language + segment for segment in rest.split("/")]
    found = {part: grammar.get(part) for part in parts}
    return found if all(found.values()) else None


def tidy(text: str) -> str:
    """STEP's quoting and emphasis marks off, and its low comma (U+201A) made a comma."""
    text = text.replace("\u201a", ",").replace("_", "")
    return re.sub(r"\s+", " ", text).strip().strip('"').strip()


def read_grammar() -> dict[str, list[str]]:
    """STEPBible's plain-English reading of each morphology code: [label, meaning, example].

    A record is a code line with its Function= fields, three indented lines, then "$". OSHB writes
    a few codes STEP does not -- a proper noun without its gender ("HNp"), an infinitive without
    its state ("HVqc") -- so a Hebrew code missing outright takes the label its whole family
    shares ("Noun Proper name"), with no meaning or example, which would claim more than the
    code says."""
    grammar: dict[str, list[str]] = {}
    for path in (next(MORPHOLOGY.glob("TEGMC*.txt")), next(MORPHOLOGY.glob("TEHMC*.txt"))):
        code, lines = None, []
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("$"):
                if code and len(lines) >= 2:
                    clean = [tidy(l) for l in lines[:3]]
                    if len(clean) == 3:  # 'Example: "of, from": "of, to"' gives two; keep one
                        clean[2] = tidy(re.sub(r"^Example:\s*", "", clean[2]).split('": "')[0])
                    grammar.setdefault(code, (clean + [""] * 3)[:3])
                code, lines = None, []
            elif line and not line[0].isspace() and "\tFunction=" in line:
                code, lines = line.split("\t")[0].strip(), []
            elif code and line.strip():
                lines.append(line)
    # TEHMC's suffix examples are swapped between singular and plural ("Sp1bs", my, is glossed
    # "we, us, our"; "Sp1bp" "I, me, my"), so they are left off; the labels are right.
    for code, entry in grammar.items():
        if code[:2] in ("HS", "AS"):
            entry[2] = ""
    hebrew = [k for k in grammar if k[0] in "HA" and not k.startswith(("H:", "A:"))]

    class WithFamilies(dict):
        def get(self, key, default=None):
            if key in self:
                return self[key]
            if key[0] not in "HA":
                return default
            # OSHB's infinitive "Vqc" is STEP's "Vqcc" (the state written twice), and OSHB's
            # "common" gender STEP's "either" ("Sp1cs" is "Sp1bs").
            for spelling in (key + key[-1], key[:2] + key[2:].replace("c", "b")):
                if spelling in self:
                    return self[spelling]
            family = [self[k][0].split() for k in hebrew if k.startswith(key)]
            if not family:
                return default
            shared = []
            for words in zip(*family):
                if len(set(words)) > 1:
                    break
                shared.append(words[0])
            label = " ".join(shared).rstrip("(:;, ")
            if not label:
                return default
            self[key] = [label, "", ""]
            return self[key]

    return WithFamilies(grammar)


def main() -> int:
    conn = query.connect()
    if OUT.exists():
        shutil.rmtree(OUT)
    books = export_verses(conn)
    shards = export_words(conn)
    grammar, used = read_grammar(), {}
    forms = export_forms(conn, grammar, used)
    chapters = export_originals(conn, grammar, used)
    dump(OUT / "grammar.json", dict(sorted(used.items())))
    size = sum(p.stat().st_size for p in OUT.rglob("*.json"))
    print(f"wrote {books} verse files, {shards} word files, {forms} form files and {chapters} "
          f"original-language chapters to "
          f"{OUT.relative_to(REPO)} ({size / 1_000_000:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
