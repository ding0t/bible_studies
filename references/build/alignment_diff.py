"""Where the ULT and the Berean Interlinear render the same original word differently.

Both word-align an English translation to the Hebrew or Greek behind it, and they are independent
committees working from different base texts. Where they agree, a study's point does not hang on
one translator's choice. Where they differ, the difference is worth a sentence: it is the list of
words a study should look at before resting an argument on an English term.

The two tables are not directly comparable row by row. Strong's numbers are written differently
(the ULT's 'c:d:H0776', 'G13440' for G1344; the Berean's 'H776'), and USFM's nested frames spread
one English phrase across several original words ('by' and 'grace' both sit on χάριτι AND on the
article before it). So the comparison is keyed on the original word itself -- its letters with
accents, vowel points and punctuation removed, plus which occurrence of it in the passage -- and
an English side is its content words, with the small words that carry no rendering choice dropped.

Two kinds of finding, kept apart:

* `differ`: both translations render the same original word with content words, and share none.
  'void' for 'empty' at Genesis 1:2 is a different word, not an error; a reader decides whether it
  matters for the passage.
* `text_differs`: an original word one base text has and the other lacks (Psalm 51's title, which
  the Berean numbers as verse 1 and the ULT does not; a verse boundary that falls elsewhere). Checked
  against each side's own base text, not its alignment: the ULT hangs 'God' on the article before
  θεόν, so the Berean having no row for that article says nothing about the text.

A word one side leaves with no English of its own, or only function words, is skipped. That is
the nesting artefact above, and reporting it would bury the real differences.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

STOP = frozenset(
    "a an the of and or to in on at by for from with as is are was were be been being am it its "
    "that this these those he him his she her they them their you your we us our i me my not no "
    "but so if then than there who whom whose which what shall will would may might can could "
    "do does did has have had into upon unto over".split())


def original_key(word: str) -> str:
    """The word's letters only: Hebrew points, accents and maqaf and Greek accents and breathings
    are marks or punctuation, so removing every non-letter reduces both texts to comparable forms."""
    stripped = "".join(c for c in unicodedata.normalize("NFD", word)
                       if unicodedata.category(c).startswith("L"))
    return unicodedata.normalize("NFC", stripped).lower().replace("ς", "σ")


def text_keys(verses: list[list[str]]) -> set[tuple[str, int]]:
    """(word, occurrence in the passage) for every word of a base text, verse by verse in order.
    `verses` is each verse's words as written; maqaf-joined Hebrew must already be split."""
    seen: Counter = Counter()
    keys = set()
    for words in verses:
        for w in words:
            k = original_key(w)
            if k:
                seen[k] += 1
                keys.add((k, seen[k]))
    return keys


def split_words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s־]+", text) if w]


def english_content(text: str) -> list[str]:
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower().replace("’", "'"))
    return [w for w in words if w not in STOP]


def agree(a: list[str], b: list[str]) -> bool:
    """Two renderings agree when a content word of one equals one of the other, or shares its first
    five letters with it: justified/justify, righteous/righteousness."""
    return any(x == y or (len(x) >= 5 and len(y) >= 5 and x[:5] == y[:5]) for x in a for y in b)


def words_of(rows_by_verse: list[list[dict]], offsets: list[Counter],
             verse_numbers: list[int]) -> dict[tuple[str, int], dict]:
    """Group alignment rows by the original word they enclose. `occurrence` counts within a verse,
    so each verse's rows are shifted by how many times the word came in the verses before it."""
    words: dict[tuple[str, int], dict] = {}
    for rows, before, verse in zip(rows_by_verse, offsets, verse_numbers):
        for r in rows:
            k = original_key(r["content"])
            if not k:
                continue
            w = words.setdefault((k, before[k] + (r["occurrence"] or 1)),
                                 {"content": r["content"], "english": [], "verse": verse, "strong": None})
            w["english"].append(r["english"])
            w["strong"] = w["strong"] or r.get("strong")
    return words


def compare(ult_rows: list[list[dict]], bsb_rows: list[list[dict]], ult_text: list[list[str]],
            bsb_text: list[list[str]], verse_numbers: list[int], tally: list | None = None) -> dict[str, object]:
    """Each list argument holds one entry per verse of the passage, in order; `verse_numbers`
    names them, so a finding says where it sits. Pass a list as `tally` to have every compared
    word appended to it as (Berean Strong's, agreed, ULT English, Berean English) -- the canon-wide
    ranking in alignment_ranking.py totals those."""
    def before(text: list[list[str]]) -> list[Counter]:
        out, running = [], Counter()
        for words in text:
            out.append(Counter(running))
            running.update(k for k in (original_key(w) for w in words) if k)
        return out

    ult = words_of(ult_rows, before(ult_text), verse_numbers)
    bsb = words_of(bsb_rows, before(bsb_text), verse_numbers)
    ult_has, bsb_has = text_keys(ult_text), text_keys(bsb_text)
    differences, agreed, text_differs = [], 0, []
    for key, u in ult.items():
        b = bsb.get(key)
        if b is None:
            if key not in bsb_has and english_content(" ".join(u["english"])):
                text_differs.append({"kind": "ULT only", "verse": u["verse"], "original": u["content"],
                                     "english": " / ".join(dict.fromkeys(u["english"]))})
            continue
        u_words, b_words = english_content(" ".join(u["english"])), english_content(" ".join(b["english"]))
        if not (u_words and b_words):
            continue
        same = agree(u_words, b_words)
        if tally is not None:
            tally.append((b["strong"], same, " ".join(dict.fromkeys(u_words)), " ".join(dict.fromkeys(b_words))))
        if same:
            agreed += 1
        else:
            differences.append({"verse": u["verse"], "original": u["content"],
                                "ult": " / ".join(dict.fromkeys(u["english"])),
                                "bsb": " / ".join(dict.fromkeys(b["english"]))})
    for key, b in bsb.items():
        if key not in ult and key not in ult_has and english_content(" ".join(b["english"])):
            text_differs.append({"kind": "Berean only", "verse": b["verse"], "original": b["content"],
                                 "english": " / ".join(dict.fromkeys(b["english"]))})
    return {"agreed": agreed, "differences": differences, "text_differs": text_differs}
