"""Edersheim's list of the Old Testament passages the ancient synagogue read of the Messiah.

Alfred Edersheim, The Life and Times of Jesus the Messiah (1883), Appendix IX: 456 passages, each
with the Targum, Talmud or Midrash that applies it to the Messiah or to Messianic times. Public
domain (CCEL's text of the 1953 Eerdmans printing), kept on the media volume rather than in the
repo; sources.toml [profiles.edersheim] holds the path and the limits.

Edersheim writes one paragraph per passage, led by its reference in the Authorised Version's
numbering ('Gen. xlix. 10.', 'Ps. xxi. 1 (2 in the Hebrew)'), and a paragraph that opens 'Verse 7'
continues the chapter before it. This module indexes those paragraphs by English reference.
One is misfiled and left so: 'In the Midr. on Cant. ii. 13 it is said' belongs to Psalm 89, but
'In the Midr. on Eccl. i. 9' opens Ecclesiastes 1:9's own entry, and no rule tells them apart.

What it is evidence of: that a rabbinic source applies the verse to the Messiah. Not when. A
Targum or a midrash dates by its compilation, never by the rabbi it names (prophecy-method.md
section 6), and nearly all of them are later than the New Testament -- date each one before using it.

Usage:
    uv run python edersheim.py Gen 49 10
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache

import source_catalog

_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
_BOOKS = {
    "Gen": "Gen", "Ex": "Exod", "Exod": "Exod", "Lev": "Lev", "Num": "Num", "Numb": "Num",
    "Deut": "Deut", "Josh": "Josh", "Joshua": "Josh", "Judg": "Judg", "Ruth": "Ruth",
    "1 Sam": "1Sam", "2 Sam": "2Sam", "1 Kings": "1Kgs", "2 Kings": "2Kgs", "1 Chr": "1Chr",
    "Ps": "Ps", "Prov": "Prov", "Eccl": "Eccl", "Cant": "Song", "Is": "Isa", "Jer": "Jer",
    "Lam": "Lam", "Ezek": "Ezek", "Dan": "Dan", "Hos": "Hos", "Joel": "Joel", "Amos": "Amos",
    "Obadiah": "Obad", "Obad": "Obad", "Micah": "Mic", "Mic": "Mic", "Nahum": "Nah",
    "Habakkuk": "Hab", "Hab": "Hab", "Zephaniah": "Zeph", "Zeph": "Zeph", "Haggai": "Hag",
    "Hag": "Hag", "Zech": "Zech", "Malachi": "Mal", "Mal": "Mal",
}
_BOOK_ALT = "|".join(sorted((re.escape(b) for b in _BOOKS), key=len, reverse=True))
# 'Gen. xlix. 10', 'Gen iii. 15', 'Is. xi.', 'Ps. xxii. 7', 'chap. lix. 15', 'Cant. viii.1'
_REF = re.compile(rf"\b({_BOOK_ALT}|chap|Chap)\.?\s+([ivxlc]+)\.\s*(\d+)?(?:\s*[-,]\s*(\d+))?")
_VERSE = re.compile(r"^(?:On |In connection with |To |Of |Finally,? in |Similarly |The )?(?:the )?"
                    r"(?:last clause of |first clause of |second clause of )?[Vv]erses?\s+(\d+)"
                    r"(?:\s*(?:,|and|-)\s*(\d+))?")
_ORDINAL_VERSE = re.compile(r"^On the (\d+)(?:st|nd|rd|th) verse")
_ANAPHORIC = re.compile(r"^(?:Similarly,? |So |Again,? )?(?:this|the same) passage", re.I)


def _roman(numeral: str) -> int:
    total, prev = 0, 0
    for ch in reversed(numeral):
        value = _ROMAN[ch]
        total = total - value if value < prev else total + value
        prev = max(prev, value)
    return total


@lru_cache(maxsize=1)
def appendix_ix() -> list[dict]:
    """Appendix IX as paragraphs, each with the reference it is about (None for the preface)."""
    path = source_catalog.profile_location("edersheim")
    if path is None or not path.is_file():
        raise FileNotFoundError(
            f"Edersheim not found at {path}; it lives on the media volume "
            f"(${source_catalog.media_env_var()}), see sources.toml [profiles.edersheim]")
    text = path.read_text(encoding="utf-8")
    start = text.index("APPENDIX IX.\n")
    end = text.index("APPENDIX X.\n", start)
    paragraphs, current = [], []
    for raw in text[start:end].split("\n"):
        if raw.strip():
            current.append(raw.strip())
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))

    rows, book, chapter, apocrypha = [], None, None, False
    for index, para in enumerate(paragraphs):
        ref = None
        head = para[:120]
        # The list closes with the Apocrypha and a long extract from Sanhedrin; their references
        # are comparisons with passages already listed, not entries
        apocrypha = apocrypha or para.startswith("To the above passages we add some from the Apocryphal")
        if apocrypha:
            rows.append({"index": index, "book": None, "chapter": None, "verse_start": None,
                         "verse_end": None, "text": para})
            continue
        verse_only = _VERSE.match(head) or _ORDINAL_VERSE.match(head)
        explicit = _REF.search(head)
        anaphoric = _ANAPHORIC.match(head)
        if anaphoric and rows and rows[-1]["book"]:
            # 'Similarly, this passage is quoted in Yalkut on Ps. cxxi. 1': the Psalm is where the
            # quotation sits, the subject is still the previous paragraph's verse
            prev = rows[-1]
            ref = (prev["book"], prev["chapter"], prev["verse_start"], prev["verse_end"])
        elif verse_only and book and (not explicit or explicit.start() > verse_only.end()):
            first = int(verse_only.group(1))
            second = verse_only.group(2) if verse_only.re.groups > 1 else None
            last = int(second) if second else first
            ref = (book, chapter, first, last)
        elif explicit and explicit.start() < 60:
            name = explicit.group(1)
            if name.lower() != "chap":
                book = _BOOKS[name]
            chapter = _roman(explicit.group(2))
            first = int(explicit.group(3)) if explicit.group(3) else None
            last = int(explicit.group(4)) if explicit.group(4) else first
            ref = (book, chapter, first, last)
        rows.append({"index": index, "book": ref[0] if ref else None,
                     "chapter": ref[1] if ref else None,
                     "verse_start": ref[2] if ref else None,
                     "verse_end": ref[3] if ref else None, "text": para})
    return rows


def _cited(para: str, book: str, chapter: int, verse: int | None) -> bool:
    for m in _REF.finditer(para):
        if m.group(1).lower() == "chap" or _BOOKS[m.group(1)] != book or _roman(m.group(2)) != chapter:
            continue
        if verse is None or not m.group(3):
            return True
        first, last = int(m.group(3)), int(m.group(4) or m.group(3))
        if first <= verse <= max(first, last):
            return True
    return False


def lookup_edersheim(book: str, chapter: int, verse: int | None = None) -> dict[str, object]:
    """Edersheim's paragraphs on one Old Testament reference (English numbering), and the others
    that cite it in passing ('see our remarks on Gen. xlix. 10')."""
    rows = appendix_ix()
    about, mentioned = [], []
    for row in rows:
        if row["book"] == book and row["chapter"] == chapter and (
                verse is None or row["verse_start"] is None
                or row["verse_start"] <= verse <= max(row["verse_start"], row["verse_end"] or 0)):
            about.append(row)
        elif _cited(row["text"], book, chapter, verse):
            mentioned.append({k: row[k] for k in ("index", "book", "chapter", "verse_start")}
                             | {"text": row["text"][:400]})
    return {
        "reference": f"{book} {chapter}" + (f":{verse}" if verse else ""),
        "source": "Alfred Edersheim, The Life and Times of Jesus the Messiah (1883), Appendix IX",
        "license_tier": "open",
        "about": about,
        "mentioned_in": mentioned,
        "caution": ("Edersheim (1883) lists where a rabbinic text applies the verse to the Messiah; "
                    "his abbreviations are Ber. R. = Bereshith (Genesis) Rabbah, Sanh. = Talmud "
                    "Sanhedrin, Yalkut = Yalkut Shimoni (13th c.). Date each source by its "
                    "compilation before calling the reading early, and check his reading of it "
                    "against the source where Sefaria has it. Hebrew he printed is lost from "
                    "this text as {hebrew}."),
    }


if __name__ == "__main__":
    b, c = sys.argv[1], int(sys.argv[2])
    v = int(sys.argv[3]) if len(sys.argv) > 3 else None
    result = lookup_edersheim(b, c, v)
    for row in result["about"]:
        print(f"[{row['index']}] {row['book']} {row['chapter']}:{row['verse_start']}\n{row['text']}\n")
    for row in result["mentioned_in"]:
        print(f"  mentioned in [{row['index']}] {row['book']} {row['chapter']}:{row['verse_start']}: "
              f"{row['text'][:160]}")
