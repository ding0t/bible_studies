"""Emit the Greek word cards to docs/data/greek-cards.json, from docs/data/greek-cards.toml.

The Greek counterpart of export_hebrew_cards.py, rendered by hooks/greek_cards.py wherever a page
carries `<!-- greek-cards: <deck> -->`. Committed for the same reason: neither database is
reachable from the deploy workflow.

Nothing in the TOML ships unchecked:

- every Greek word must occur, accented exactly so, in the SBL Greek New Testament at the card's
  verse, or the export fails (a grave accent counts as the acute it stands for, since a grave is
  only an acute before another word). Its Strong's number comes from MACULA's tagging of the
  same verse. `…` in a card marks words left out between two that are there;
- the quotation must occur in the ESV of its verse in study-notes.db, or the export fails, and the
  quotation already in the JSON is kept, never assumed, when study-notes.db is unreachable;
- the transliteration (SBL style), syllables and stress are computed here from the Greek, and so are the
  letters each card introduces, so neither can disagree with the word printed.

Usage: uv run python export_greek_cards.py
"""
import json
import re
import sqlite3
import sys
import tomllib
import unicodedata
from pathlib import Path

import export_hebrew_cards as hc
import export_memory_verses as mv
import study_notes_query

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "docs" / "data" / "greek-cards.toml"
OUT = REPO / "docs" / "data" / "greek-cards.json"
BIBLE_TEXT = Path(__file__).resolve().parent / "out" / "bible-text.db"

ALPHABET = "αβγδεζηθικλμνξοπρστυφχψω"
GAP = "…"
_ACUTE, _GRAVE, _CIRCUMFLEX = "́", "̀", "͂"
_ROUGH, _DIAERESIS = "̔", "̈"
_SINGLE = {"α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "ē", "θ": "th", "ι": "i",
           "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ξ": "x", "ο": "o", "π": "p", "ρ": "r", "σ": "s",
           "ς": "s", "τ": "t", "υ": "y", "φ": "ph", "χ": "ch", "ψ": "ps", "ω": "ō"}
_DIPHTHONGS = {"αι": "ai", "ει": "ei", "οι": "oi", "υι": "ui", "αυ": "au", "ευ": "eu", "ηυ": "ēu", "ου": "ou"}
_VOWELS = set("αεηιουω")
# Clusters that can begin a Greek word stay together at the start of the next syllable.
_ONSETS = {"βλ", "βρ", "γλ", "γν", "γρ", "δρ", "θλ", "θν", "θρ", "κλ", "κμ", "κν", "κρ", "κτ", "μν", "πλ",
           "πν", "πρ", "πτ", "σβ", "σθ", "σκ", "σμ", "σπ", "στ", "σφ", "σχ", "τμ", "τρ", "φθ", "φλ", "φρ",
           "χθ", "χλ", "χρ", "σκλ", "σκρ", "σπλ", "στρ", "σφρ"}
_GAMMA_NASAL = set("γκξχ")
_MARKERS = re.compile(r"[⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍⸎⸏\[\]]")
_PUNCT = re.compile(r"[,.;·:!?“”‘’()—·;]")


def nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


def comparable(word: str) -> str:
    """The word as the verse text must contain it: graves read as acutes, elision marks kept."""
    return unicodedata.normalize("NFC", nfd(word).replace(_GRAVE, _ACUTE))


def bare(word: str) -> str:
    """Base letters only, lowercase, final sigma as sigma."""
    return "".join(c for c in nfd(word).lower() if c.isalpha() and unicodedata.category(c) != "Mn").replace("ς", "σ")


def units(word: str) -> list[dict]:
    """Letters grouped into sounds: a diphthong, a vowel or a consonant, each with its marks."""
    letters = []
    for c in nfd(word.lower()):
        if unicodedata.category(c) == "Mn":
            if letters:
                letters[-1]["marks"] += c
        elif c.isalpha():
            letters.append({"c": c, "marks": ""})
    out, i = [], 0
    while i < len(letters):
        a = letters[i]
        b = letters[i + 1] if i + 1 < len(letters) else None
        pair = a["c"] + b["c"] if b else ""
        if b and pair in _DIPHTHONGS and _DIAERESIS not in b["marks"]:
            out.append({"g": pair, "vowel": True, "marks": a["marks"] + b["marks"]})
            i += 2
        else:
            out.append({"g": a["c"], "vowel": a["c"] in _VOWELS, "marks": a["marks"]})
            i += 1
    return out


def roman(unit: dict, following: dict | None, first: bool) -> str:
    g = unit["g"]
    text = _DIPHTHONGS.get(g) or _SINGLE[g]
    if g == "γ" and following and following["g"] in _GAMMA_NASAL:
        text = "n"
    if g == "ρ" and first:
        text = "rh"
    if unit["vowel"] and first and _ROUGH in unit["marks"]:
        text = "h" + text
    return text


def syllables(word: str) -> tuple[list[str], int | None]:
    us = units(word)
    nuclei = [i for i, u in enumerate(us) if u["vowel"]]
    if not nuclei:
        return [word], None
    bounds = [0]
    for left, right in zip(nuclei, nuclei[1:]):
        between = [u["g"] for u in us[left + 1:right]]
        if not between:
            bounds.append(right)
        elif len(between) == 1:
            bounds.append(left + 1)
        else:
            keep = next((k for k in range(len(between)) if "".join(between[k:]) in _ONSETS), len(between) - 1)
            bounds.append(left + 1 + keep)
    bounds.append(len(us))
    out, stress = [], None
    for n, (a, b) in enumerate(zip(bounds, bounds[1:])):
        out.append("".join(roman(us[i], us[i + 1] if i + 1 < len(us) else None, i == 0)
                           for i in range(a, b)))
        if any(us[i]["vowel"] and set(us[i]["marks"]) & {_ACUTE, _GRAVE, _CIRCUMFLEX} for i in range(a, b)):
            stress = n if stress is None else stress
    return out, stress


def uncial(word: str) -> str:
    """The word as the majuscule manuscripts wrote it: capitals, no accents or breathings, and the
    lunate sigma (Ϲ) of the codices."""
    return "".join("Ϲ" if c in "σς" else c.upper() for c in bare(word))


def verse_words(db, ref: dict) -> list[str]:
    rows = db.execute("SELECT text FROM verses WHERE work_id='sblgnt' AND book=? AND chapter=? "
                      "AND verse BETWEEN ? AND ? ORDER BY verse",
                      (ref["osis"], ref["chapter"], ref["start"], ref["end"])).fetchall()
    if not rows:
        raise LookupError(f"{ref}: no SBLGNT text")
    text = _PUNCT.sub(" ", _MARKERS.sub("", " ".join(r[0] for r in rows)))
    return [comparable(w) for w in text.split()]


def strongs(db, ref: dict, word: str) -> str | None:
    rows = db.execute("SELECT surface_form, strongs_id FROM morphology WHERE work_id='macula-greek-sblgnt' "
                      "AND book=? AND chapter=? AND verse BETWEEN ? AND ?",
                      (ref["osis"], ref["chapter"], ref["start"], ref["end"])).fetchall()
    for surface, sid in rows:
        if surface and comparable(_PUNCT.sub("", surface)) == word and sid:
            return f"G{int(sid.split('+')[0])}"
    return None


def letters_in(words: list[str]) -> list[str]:
    seen = []
    for c in bare("".join(words)):
        if c in ALPHABET and c not in seen:
            seen.append(c)
    return seen


def main() -> None:
    source = tomllib.loads(SOURCE.read_text(encoding="utf-8"))
    previous = {}
    if OUT.exists():
        for deck in json.loads(OUT.read_text(encoding="utf-8"))["decks"].values():
            previous.update({(c["ref"], c["greek"]): c["quote"] for c in deck["cards"]})
    try:
        notes = study_notes_query.connect()
    except study_notes_query.SourceUnavailable as exc:
        print(f"ESV: study-notes.db unreachable ({exc}); keeping quotations already exported", file=sys.stderr)
        notes = None
    db = sqlite3.connect(f"file:{BIBLE_TEXT}?mode=ro", uri=True)

    decks = {}
    for slug, deck in source["deck"].items():
        known: set[str] = set()
        final_seen = False
        cards = []
        for entry in deck["card"]:
            ref = mv.parse_ref(entry["ref"])
            text = verse_words(db, ref)
            words = []
            for word in entry["greek"].split():
                if word == GAP:
                    words.append({"w": GAP, "t": [], "s": None, "strongs": None, "uncial": GAP})
                    continue
                if comparable(word) not in text:
                    raise LookupError(f"{entry['ref']}: {word} is not in the SBLGNT text of the verse")
                syl, stress = syllables(word)
                if word[0].isupper():
                    syl[0] = syl[0].capitalize()
                words.append({"w": word, "t": syl, "s": stress, "strongs": strongs(db, ref, comparable(word)),
                              "uncial": uncial(word)})

            greek = " ".join(w["w"] for w in words)
            quote_ref = entry.get("quote_ref", entry["ref"])
            quote = hc.esv_quote(notes, quote_ref, entry["quote"]) if notes else previous.get((entry["ref"], greek))
            if not quote:
                raise LookupError(f"{quote_ref}: no ESV to check the quotation against, and none exported before")

            letters = letters_in([w["w"] for w in words if w["w"] != GAP])
            new = [c for c in letters if c not in known]
            known.update(letters)
            final = "ς" in greek and not final_seen
            final_seen = final_seen or final
            cards.append({
                "greek": greek, "ref": entry["ref"], "name": entry["name"],
                "popular": entry.get("popular", ""), "meaning": entry["meaning"],
                "quote": quote, "quote_ref": quote_ref, "modern": entry["modern"], "words": words,
                "new_letters": new, "new_finals": ["ς"] if final else [], "letters_known": len(known),
            })
        missing = [c for c in ALPHABET if c not in known]
        print(f"{slug}: {len(cards)} cards, {len(known)} of 24 letters"
              + (f" (not yet: {' '.join(missing)})" if missing else "")
              + f", final sigma {'yes' if final_seen else 'no'}")
        decks[slug] = {"title": deck["title"], "cards": cards}

    OUT.write_text(json.dumps({
        "sources": {
            "greek": "SBL Greek New Testament (SBLGNT); Strong's numbers from MACULA Greek, CC BY 4.0",
            "ESV": "ESV® Bible, © 2001 by Crossway. Used by permission. All rights reserved.",
        },
        "decks": decks,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
