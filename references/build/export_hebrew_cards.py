"""Emit the Hebrew word cards to docs/data/hebrew-cards.json, from docs/data/hebrew-cards.toml.

hooks/hebrew_cards.py renders the JSON into A4 flashcard sheets wherever a page carries
`<!-- hebrew-cards: <deck> -->`. Committed, like export_memory_verses.py's output: neither
database is reachable from the deploy workflow.

The TOML is the only hand-written part, and nothing in it ships unchecked:

- every Hebrew word must occur, pointed exactly so, in STEPBible's TAHOT at the card's verse
  (the Leningrad text, Qere where it differs), or the export fails. Its syllables, stress and
  Strong's number come from the same TAHOT row;
- the quotation must occur in the ESV of its verse in study-notes.db, or the export fails. If
  study-notes.db is unreachable the quotation already in the JSON is kept, never assumed;
- the letters each card introduces are counted here from the words, so a card's "new letters"
  cannot disagree with what it prints.

Usage: uv run python export_hebrew_cards.py
"""
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

import export_memory_verses as mv
import study_notes_query

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "data" / "hebrew-cards.toml"
OUT = REPO / "docs" / "data" / "hebrew-cards.json"

ALPHABET = "אבגדהוזחטיכלמנסעפצקרשת"
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
# Unicode encodes Paleo-Hebrew as Phoenician: the same 22 letters, in the same order.
PALEO = {letter: chr(0x10900 + i) for i, letter in enumerate(ALPHABET)}
_POINTS = re.compile("[֑-ׇ]")
_MAQAF = "־"
_QUOTES = str.maketrans("“”‘’", "\"\"''")


def normalise(word: str) -> str:
    word = mv._CANTILLATION.sub("", mv._HEBREW_SEPARATORS.sub("", word)).replace(_MAQAF, "")
    return unicodedata.normalize("NFC", word.strip())


def consonants(word: str) -> str:
    return _POINTS.sub("", unicodedata.normalize("NFD", word))


def verse_parts(ref: dict) -> list[dict]:
    """Every TAHOT word of the verse, and every '/'-separated part of it (prefix, stem, suffix),
    each with its own transliteration and Strong's number where TAHOT's parts line up."""
    step_book = mv.OSIS_TO_STEP[ref["osis"]]
    rows = mv.tagged_rows(mv.tagged_file(ref["num"], step_book), step_book, ref["chapter"],
                          range(ref["start"], ref["end"] + 1))
    parts = []
    for row_type, cols in rows:
        if row_type[0] not in "LRQ":
            continue
        # After TAHOT's backslash comes punctuation only: maqaf, sof pasuq, a paragraph mark.
        heb = cols[1].split("\\")[0].split("/")
        translit = cols[2].split("\\")[0].rstrip("-").split("/")
        strongs = re.findall(r"H\d{4}", cols[4])
        # H9001-H9049 are STEPBible's numbers for prefixes and suffixes; a whole word takes its stem's.
        stems = [h for h in strongs if not h.startswith("H90")] or strongs
        parts.append({"w": normalise("".join(heb)), "t": "".join(translit), "h": stems[0] if stems else None})
        if len(heb) > 1:
            for i, segment in enumerate(heb):
                parts.append({"w": normalise(segment),
                              "t": translit[i] if len(translit) == len(heb) else None,
                              "h": strongs[i] if len(strongs) == len(heb) else None})
    return parts


def find_word(word: str, parts: list[dict], ref: str) -> dict:
    for part in parts:
        if part["w"] == word:
            return part
    near = [p["w"] for p in parts if consonants(p["w"]) == consonants(word)]
    hint = f" -- same letters, different points: {', '.join(near)}" if near else ""
    raise LookupError(f"{ref}: {word} is not in TAHOT's text of the verse{hint}")


def strongs_id(raw: str | None) -> str | None:
    return f"H{int(raw[1:])}" if raw else None


def esv_quote(conn, quote_ref: str, quote: str) -> str:
    ref = mv.parse_ref(quote_ref)
    text = mv.esv_text(conn, ref) or ""
    at = text.translate(_QUOTES).find(quote.translate(_QUOTES))
    if at < 0:
        raise LookupError(f"{quote_ref}: {quote!r} is not in the ESV, which reads {text!r}")
    return text[at:at + len(quote)]


def letters_in(words: list[str]) -> list[str]:
    seen = []
    for c in consonants("".join(words)):
        c = FINALS.get(c, c)
        if c in ALPHABET and c not in seen:
            seen.append(c)
    return seen


def main() -> None:
    source = tomllib.loads(SOURCE.read_text(encoding="utf-8"))
    previous = {}
    if OUT.exists():
        for deck in json.loads(OUT.read_text(encoding="utf-8"))["decks"].values():
            previous.update({(c["ref"], c["hebrew"]): c["quote"] for c in deck["cards"]})
    try:
        notes = study_notes_query.connect()
    except study_notes_query.SourceUnavailable as exc:
        print(f"ESV: study-notes.db unreachable ({exc}); keeping quotations already exported", file=sys.stderr)
        notes = None

    decks = {}
    for slug, deck in source["deck"].items():
        known: set[str] = set()
        finals_seen: set[str] = set()
        cards = []
        for entry in deck["card"]:
            ref = mv.parse_ref(entry["ref"])
            parts = verse_parts(ref)
            words = []
            for word in entry["hebrew"].split():
                part = find_word(normalise(word), parts, entry["ref"])
                syllables, stress = mv.hebrew_syllables(part["t"]) if part["t"] else ([], None)
                if entry.get("divine") and part["h"] and mv._DIVINE_NAME.search(part["h"]):
                    syllables, stress = [], None
                words.append({"w": part["w"], "t": syllables, "s": stress, "strongs": strongs_id(part["h"]),
                              "paleo": "".join(PALEO[FINALS.get(c, c)] for c in consonants(part["w"]) if FINALS.get(c, c) in PALEO)})

            hebrew = " ".join(w["w"] for w in words)
            quote_ref = entry.get("quote_ref", entry["ref"])
            quote = esv_quote(notes, quote_ref, entry["quote"]) if notes else previous.get((entry["ref"], hebrew))
            if not quote:
                raise LookupError(f"{quote_ref}: no ESV to check the quotation against, and none exported before")

            letters = letters_in([w["w"] for w in words])
            new = [c for c in letters if c not in known]
            known.update(letters)
            finals = sorted({c for c in consonants(hebrew) if c in FINALS} - finals_seen)
            finals_seen.update(finals)
            cards.append({
                "hebrew": hebrew, "ref": entry["ref"], "name": entry["name"],
                "popular": entry.get("popular", ""), "meaning": entry["meaning"],
                "quote": quote, "quote_ref": quote_ref, "modern": entry["modern"],
                "divine": bool(entry.get("divine")), "words": words,
                "new_letters": new, "new_finals": finals, "letters_known": len(known),
            })
        missing = [c for c in ALPHABET if c not in known]
        print(f"{slug}: {len(cards)} cards, {len(known)} of 22 letters"
              + (f" (not yet: {' '.join(missing)})" if missing else "")
              + f", finals {' '.join(sorted(finals_seen)) or 'none'}")
        decks[slug] = {"title": deck["title"], "cards": cards}

    OUT.write_text(json.dumps({
        "sources": {
            "hebrew": "STEPBible TAHOT (Translators Amalgamated Hebrew OT), CC BY, STEPBible.org",
            "ESV": "ESV® Bible, © 2001 by Crossway. Used by permission. All rights reserved.",
        },
        "decks": decks,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
