"""Emit the data behind the printable memory verse cards to docs/data/memory-verses.json.

The verse list is docs/data/memory-verses.toml; hooks/memory_verses.py renders the JSON into
A4 card sheets wherever a page carries a `<!-- memory-verses -->` marker. Committed rather than
generated in CI, like export_popups.py: neither database is reachable from the deploy workflow.

Per verse:

- words         the original-language text word by word, with a syllabified transliteration and
                a gloss, from STEPBible's TAHOT (Hebrew, the Leningrad text, Qere followed where
                it differs) and TAGNT (Greek, the words printed in Nestle-Aland). CC BY. TAHOT
                capitalises the stressed syllable; that becomes `stress`, so the card can mark it.
- translations  WEB from bible-text.db (public domain) and ESV from study-notes.db. The ESV is
                quotation-only: one verse per card with the notice on every sheet is within
                Crossway's terms, which allow 1,000 verses provided Scripture is under half the
                work. If study-notes.db is unreachable the ESV already in the JSON is kept, never
                recalled from memory, and a verse with none yet is printed with WEB alone.

Usage: uv run python export_memory_verses.py
"""
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

import book_map
import query
import study_notes_query

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "data" / "memory-verses.toml"
OUT = REPO / "docs" / "data" / "memory-verses.json"
TAGGED = REPO / "references" / "open-data" / "stepbible-data" / "Translators Amalgamated OT+NT"
WEB = "ebible-eng-web"
ESV = "esv-study-bible"
FIRST_NT_BOOK = 40
POETIC_BOOKS = {"Job", "Ps", "Prov"}

OSIS_TO_STEP = {osis: usfm.title() for usfm, osis in book_map.MACULA_USFM_TO_OSIS.items()}
_REF = re.compile(r"^(?P<book>.+?)\s+(?P<chapter>\d+):(?P<start>\d+)(?:-(?P<end>\d+))?$")
# Cantillation (U+0591-05AF) and meteg (U+05BD) guide chanting, not reading; a learner's card
# is clearer without them. Vowels, dagesh, shin/sin dots and maqaf stay.
_CANTILLATION = re.compile("[֑-ֽ֯]")
_HEBREW_SEPARATORS = re.compile(r"[/\\׃׀]")
_GREEK_WORD = re.compile(r"^(?P<word>.+?)\s*\((?P<translit>[^)]*)\)$")


def parse_ref(ref: str) -> dict:
    m = _REF.match(ref.strip())
    if not m:
        raise ValueError(f"cannot read reference {ref!r} -- expected e.g. 'Genesis 1:1' or 'Proverbs 3:5-6'")
    num = book_map.REFERENCE_NAME_TO_NUM.get(m["book"].title())
    if num is None:
        raise ValueError(f"unknown book in {ref!r}")
    start = int(m["start"])
    return {"num": num, "osis": book_map.NUM_TO_OSIS[num], "chapter": int(m["chapter"]),
            "start": start, "end": int(m["end"] or start)}


def tagged_file(num: int, step_book: str) -> Path:
    prefix = "TAGNT" if num >= FIRST_NT_BOOK else "TAHOT"
    for path in sorted(TAGGED.glob(f"{prefix} *.txt")):
        first, last = path.name.split(" ")[1].split("-")
        if _book_in_range(step_book, first, last):
            return path
    raise FileNotFoundError(f"no {prefix} file covers {step_book}")


def _book_in_range(book: str, first: str, last: str) -> bool:
    order = [code.title() for code in book_map.MACULA_USFM_TO_OSIS]
    return order.index(first) <= order.index(book) <= order.index(last)


def tagged_rows(path: Path, step_book: str, chapter: int, verses: range) -> list[tuple[str, list[str]]]:
    """(row type, columns) for each word of the verses, in order. Refs carry a Hebrew number in
    brackets where it differs, e.g. 'Mal.4.1(3.19)#01' -- the English one is the key."""
    wanted = {f"{step_book}.{chapter}.{v}" for v in verses}
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or "#" not in line[:40] or "=" not in line[:40]:
                continue
            cols = line.rstrip("\n").split("\t")
            key, row_type = cols[0].split("=", 1)
            if re.sub(r"\(.*?\)", "", key.split("#")[0]) in wanted:
                rows.append((row_type, cols))
    return rows


def hebrew_words(rows: list[tuple[str, list[str]]], poetic: bool = False) -> list[dict]:
    """One entry per word, preferring the Qere where TAHOT records both readings of a word."""
    chosen: dict[str, tuple[str, list[str]]] = {}
    for row_type, cols in rows:
        key = cols[0].split("=")[0]
        if row_type[0] in "LRQ" and (key not in chosen or row_type.startswith("Q")):
            chosen[key] = (row_type, cols)
    words = []
    for _, cols in chosen.values():
        text = _CANTILLATION.sub("", _HEBREW_SEPARATORS.sub("", cols[1])).strip()
        if not text:
            continue
        syllables, stress = hebrew_syllables(cols[2], poetic)
        words.append({"w": unicodedata.normalize("NFC", text), "t": syllables, "s": stress,
                      "g": clean_gloss(cols[3])})
    return words


def hebrew_syllables(translit: str, poetic: bool = False) -> tuple[list[str], int | None]:
    """TAHOT's 'be./re.Shit' -> (['be', 're', 'shit'], 2): syllables split on '.', prefixes
    joined on, and the capitalised (stressed) syllable recorded by index and lower-cased.

    The capital marks where the accent sits, which is usually the stress. The last capital wins,
    because a name is capitalised too: 'E.lo.Him is stressed on -him. In Job, Psalms and
    Proverbs the accent system has a prepositive accent (dehi) written on a word's first letter
    whatever its stress -- Psalm 119:11 has 'Be./li.b/i' for libbí -- so a first-syllable capital
    there is dropped: an unmarked stress is better than a wrong one."""
    syllables = [s for s in translit.replace("/", "").split(".") if s]
    capitals = [i for i, s in enumerate(syllables) if any(c.isupper() for c in s)]
    if poetic and capitals == [0] and len(syllables) > 1:
        capitals = []
    stress = capitals[-1] if capitals else None
    return [s.lower() for s in syllables], stress


def greek_words(rows: list[tuple[str, list[str]]]) -> list[dict]:
    """The words Nestle-Aland prints -- an upper-case N in the row type, outside any bracket."""
    words = []
    for row_type, cols in rows:
        if "N" not in row_type.split("(")[0]:
            continue
        m = _GREEK_WORD.match(cols[1].strip())
        if not m:
            continue
        words.append({"w": unicodedata.normalize("NFC", m["word"]), "t": [m["translit"]], "s": None,
                      "g": clean_gloss(cols[2])})
    return words


def clean_gloss(gloss: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[/<>\[\]{}]", " ", gloss)).strip()


def web_text(conn, ref: dict) -> str:
    rows = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse BETWEEN ? AND ? "
        "ORDER BY verse", (WEB, ref["osis"], ref["chapter"], ref["start"], ref["end"])).fetchall()
    if len(rows) != ref["end"] - ref["start"] + 1:
        raise LookupError(f"WEB is missing verses of {ref['osis']} {ref['chapter']}")
    return " ".join(r["text"].strip() for r in rows)


def esv_text(conn, ref: dict) -> str | None:
    rows = study_notes_query.lookup_verse(conn, ref["osis"], ref["chapter"], ref["start"], ESV,
                                          verse_end=ref["end"])
    return " ".join(r["text"].strip() for r in rows) or None


def main() -> None:
    source = tomllib.loads(SOURCE.read_text(encoding="utf-8"))
    previous = {}
    if OUT.exists():
        previous = {v["ref"]: v for v in json.loads(OUT.read_text(encoding="utf-8"))["verses"]}

    try:
        notes = study_notes_query.connect()
    except study_notes_query.SourceUnavailable as exc:
        print(f"ESV: study-notes.db unreachable ({exc}); keeping ESV already exported", file=sys.stderr)
        notes = None

    conn = query.connect()
    verses = []
    for entry in source["verse"]:
        ref = parse_ref(entry["ref"])
        step_book = OSIS_TO_STEP[ref["osis"]]
        verse_range = range(ref["start"], ref["end"] + 1)
        rows = tagged_rows(tagged_file(ref["num"], step_book), step_book, ref["chapter"], verse_range)
        nt = ref["num"] >= FIRST_NT_BOOK
        words = greek_words(rows) if nt else hebrew_words(rows, ref["osis"] in POETIC_BOOKS)
        if not words:
            raise LookupError(f"{entry['ref']}: no original-language words found")

        translations = {}
        for name in source["translations"]:
            if name == "WEB":
                translations["WEB"] = web_text(conn, ref)
            elif name == "ESV":
                text = esv_text(notes, ref) if notes else None
                text = text or previous.get(entry["ref"], {}).get("translations", {}).get("ESV")
                if text:
                    translations["ESV"] = text
                else:
                    print(f"ESV: no text for {entry['ref']}; card prints without it", file=sys.stderr)
            else:
                raise ValueError(f"unsupported translation {name!r} -- ESV and WEB are wired up")

        verses.append({
            "ref": entry["ref"], "theme": entry.get("theme", ""), "set": entry.get("set", ""),
            "language": "greek" if nt else "hebrew", "words": words, "translations": translations,
        })

    OUT.write_text(json.dumps({
        "sources": {
            "hebrew": "STEPBible TAHOT (Translators Amalgamated Hebrew OT), CC BY, STEPBible.org",
            "greek": "STEPBible TAGNT (Translators Amalgamated Greek NT), CC BY, STEPBible.org",
            "WEB": "World English Bible, public domain",
            "ESV": "ESV® Bible, © 2001 by Crossway. Used by permission. All rights reserved.",
        },
        "verses": verses,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(verses)} verses to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
