"""Book-name/code normalization to OSIS codes.

morphhb and sblgnt filenames already follow OSIS-compatible abbreviations
(Gen, Exod, ... 1Chr, Matt, ... Rev) so those are used as-is (stem of the
filename). scrollmapper's *_books tables use full English names, which need
mapping.
"""

SCROLLMAPPER_NAME_TO_OSIS = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "I Samuel": "1Sam", "II Samuel": "2Sam", "I Kings": "1Kgs", "II Kings": "2Kgs",
    "I Chronicles": "1Chr", "II Chronicles": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song of Solomon": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah",
    "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph",
    "Haggai": "Hag", "Zechariah": "Zech", "Malachi": "Mal",
    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Romans": "Rom", "I Corinthians": "1Cor", "II Corinthians": "2Cor",
    "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "I Thessalonians": "1Thess", "II Thessalonians": "2Thess", "I Timothy": "1Tim",
    "II Timothy": "2Tim", "Titus": "Titus", "Philemon": "Phlm", "Hebrews": "Heb",
    "James": "Jas", "I Peter": "1Pet", "II Peter": "2Pet", "I John": "1John",
    "II John": "2John", "III John": "3John", "Jude": "Jude", "Revelation of John": "Rev",
}

# scrollmapper's *_books tables use Roman-numeral prefixes ("I Samuel"), but its
# separate cross_references files (from openbible.info) use Arabic ("1 Samuel").
# Same repo, two conventions -- add the Arabic-numeral variants too rather than
# maintaining a second dict.
_ARABIC_VARIANTS = {
    "1 Samuel": "1Sam", "2 Samuel": "2Sam", "1 Kings": "1Kgs", "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr", "2 Chronicles": "2Chr", "1 Corinthians": "1Cor",
    "2 Corinthians": "2Cor", "1 Thessalonians": "1Thess", "2 Thessalonians": "2Thess",
    "1 Timothy": "1Tim", "2 Timothy": "2Tim", "1 Peter": "1Pet", "2 Peter": "2Pet",
    "1 John": "1John", "2 John": "2John", "3 John": "3John",
}
SCROLLMAPPER_NAME_TO_OSIS.update(_ARABIC_VARIANTS)

# macula-greek/macula-hebrew use USFM 3.0 book codes (their `ref` column, e.g.
# "MAT 1:1!1") rather than OSIS -- map to the same OSIS codes as everything else.
MACULA_USFM_TO_OSIS = {
    "GEN": "Gen", "EXO": "Exod", "LEV": "Lev", "NUM": "Num", "DEU": "Deut",
    "JOS": "Josh", "JDG": "Judg", "RUT": "Ruth", "1SA": "1Sam", "2SA": "2Sam",
    "1KI": "1Kgs", "2KI": "2Kgs", "1CH": "1Chr", "2CH": "2Chr", "EZR": "Ezra",
    "NEH": "Neh", "EST": "Esth", "JOB": "Job", "PSA": "Ps", "PRO": "Prov",
    "ECC": "Eccl", "SNG": "Song", "ISA": "Isa", "JER": "Jer", "LAM": "Lam",
    "EZK": "Ezek", "DAN": "Dan", "HOS": "Hos", "JOL": "Joel", "AMO": "Amos",
    "OBA": "Obad", "JON": "Jonah", "MIC": "Mic", "NAM": "Nah", "HAB": "Hab",
    "ZEP": "Zeph", "HAG": "Hag", "ZEC": "Zech", "MAL": "Mal",
    "MAT": "Matt", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts",
    "ROM": "Rom", "1CO": "1Cor", "2CO": "2Cor", "GAL": "Gal", "EPH": "Eph",
    "PHP": "Phil", "COL": "Col", "1TH": "1Thess", "2TH": "2Thess", "1TI": "1Tim",
    "2TI": "2Tim", "TIT": "Titus", "PHM": "Phlm", "HEB": "Heb", "JAS": "Jas",
    "1PE": "1Pet", "2PE": "2Pet", "1JN": "1John", "2JN": "2John", "3JN": "3John",
    "JUD": "Jude", "REV": "Rev",
}

# NIV/NKJV Cultural Backgrounds Study Bible epub verse-anchor IDs (e.g. "com41005025")
# use a 2-digit canonical book number (Gen=1 ... Mal=39, Matt=40 ... Rev=66) -- same
# numbering macula-greek's own xml:id scheme uses (John's ids start "n43...").
NUM_TO_OSIS = {
    1: "Gen", 2: "Exod", 3: "Lev", 4: "Num", 5: "Deut", 6: "Josh", 7: "Judg", 8: "Ruth",
    9: "1Sam", 10: "2Sam", 11: "1Kgs", 12: "2Kgs", 13: "1Chr", 14: "2Chr", 15: "Ezra",
    16: "Neh", 17: "Esth", 18: "Job", 19: "Ps", 20: "Prov", 21: "Eccl", 22: "Song",
    23: "Isa", 24: "Jer", 25: "Lam", 26: "Ezek", 27: "Dan", 28: "Hos", 29: "Joel",
    30: "Amos", 31: "Obad", 32: "Jonah", 33: "Mic", 34: "Nah", 35: "Hab", 36: "Zeph",
    37: "Hag", 38: "Zech", 39: "Mal",
    40: "Matt", 41: "Mark", 42: "Luke", 43: "John", 44: "Acts", 45: "Rom", 46: "1Cor",
    47: "2Cor", 48: "Gal", 49: "Eph", 50: "Phil", 51: "Col", 52: "1Thess", 53: "2Thess",
    54: "1Tim", 55: "2Tim", 56: "Titus", 57: "Phlm", 58: "Heb", 59: "Jas", 60: "1Pet",
    61: "2Pet", 62: "1John", 63: "2John", 64: "3John", 65: "Jude", 66: "Rev",
}

# Standard 66-book canonical order, used by the study-Bible EPUBs' "BBCCCVVV"
# numeric ids (e.g. id="v01001001" -> book 01 -> Genesis, chapter 1, verse 1).
_CANONICAL_ORDER = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph",
    "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb",
    "Jas", "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
]
BOOK_NUM_TO_OSIS = {f"{i+1:02d}": code for i, code in enumerate(_CANONICAL_ORDER)}

# CSB Ancient Faith Study Bible's "start-BookName.C.V" anchors use a THIRD
# naming convention: underscore before numbered-book digits ("1_Samuel"), and
# multi-word names concatenated with no separator ("SongofSongs"). Confirmed
# against the actual ids in the EPUB, not assumed -- don't extrapolate this
# pattern to other CSB-family products without checking.
CSB_NAME_TO_OSIS = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "1_Samuel": "1Sam", "2_Samuel": "2Sam", "1_Kings": "1Kgs", "2_Kings": "2Kgs",
    "1_Chronicles": "1Chr", "2_Chronicles": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "SongofSongs": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah",
    "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph",
    "Haggai": "Hag", "Zechariah": "Zech", "Malachi": "Mal",
    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Romans": "Rom", "1_Corinthians": "1Cor", "2_Corinthians": "2Cor",
    "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "1_Thessalonians": "1Thess", "2_Thessalonians": "2Thess", "1_Timothy": "1Tim",
    "2_Timothy": "2Tim", "Titus": "Titus", "Philemon": "Phlm", "Hebrews": "Heb",
    "James": "Jas", "1_Peter": "1Pet", "2_Peter": "2Pet", "1_John": "1John",
    "2_John": "2John", "3_John": "3John", "Jude": "Jude", "Revelation": "Rev",
}
