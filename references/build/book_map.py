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

# Full, lowercase-hyphenated book names for commentary directory naming (docs/content/bible/
# commentaries/<NN>-<slug>/), matching the convention already established by the four existing
# books (01-genesis, 19-psalms, 20-proverbs, 27-daniel). Same 1-66 numbering as NUM_TO_OSIS.
NUM_TO_SLUG = {
    1: "genesis", 2: "exodus", 3: "leviticus", 4: "numbers", 5: "deuteronomy",
    6: "joshua", 7: "judges", 8: "ruth", 9: "1-samuel", 10: "2-samuel",
    11: "1-kings", 12: "2-kings", 13: "1-chronicles", 14: "2-chronicles", 15: "ezra",
    16: "nehemiah", 17: "esther", 18: "job", 19: "psalms", 20: "proverbs",
    21: "ecclesiastes", 22: "song-of-solomon", 23: "isaiah", 24: "jeremiah", 25: "lamentations",
    26: "ezekiel", 27: "daniel", 28: "hosea", 29: "joel", 30: "amos",
    31: "obadiah", 32: "jonah", 33: "micah", 34: "nahum", 35: "habakkuk",
    36: "zephaniah", 37: "haggai", 38: "zechariah", 39: "malachi",
    40: "matthew", 41: "mark", 42: "luke", 43: "john", 44: "acts", 45: "romans",
    46: "1-corinthians", 47: "2-corinthians", 48: "galatians", 49: "ephesians", 50: "philippians",
    51: "colossians", 52: "1-thessalonians", 53: "2-thessalonians", 54: "1-timothy", 55: "2-timothy",
    56: "titus", 57: "philemon", 58: "hebrews", 59: "james", 60: "1-peter",
    61: "2-peter", 62: "1-john", 63: "2-john", 64: "3-john", 65: "jude", 66: "revelation",
}

# bible_references-style full names (as authors actually type them in frontmatter) -> book number.
# Deliberately permissive about singular/plural and "of John"-type suffixes that trip up
# SCROLLMAPPER_NAME_TO_OSIS (built for a different source's naming, not free-text frontmatter).
REFERENCE_NAME_TO_NUM = {name.replace("-", " ").title(): num for num, name in NUM_TO_SLUG.items()}
REFERENCE_NAME_TO_NUM.update({
    "Psalm": 19, "Psalms": 19, "Song of Songs": 22, "Revelation of John": 66,
    "1 Corinthians": 46, "2 Corinthians": 47, "1 Thessalonians": 52, "2 Thessalonians": 53,
    "1 Timothy": 54, "2 Timothy": 55, "1 Peter": 60, "2 Peter": 61,
    "1 John": 62, "2 John": 63, "3 John": 64, "1 Samuel": 9, "2 Samuel": 10,
    "1 Kings": 11, "2 Kings": 12, "1 Chronicles": 13, "2 Chronicles": 14,
})

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
