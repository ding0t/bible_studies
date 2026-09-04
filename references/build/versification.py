"""Which versification scheme a work follows, and how to move a reference between schemes.

(book, chapter, verse) is not a universal address. Three schemes sit in bible-text.db already,
and they disagree about whole chapters:

    Joel      masoretic 4 chapters, english 3  -- MT Joel 3:1 is EN Joel 2:28 (the verse Acts 2 quotes)
    Malachi   masoretic 3 chapters, english 4  -- MT Mal 3:19-24 is EN Mal 4:1-6
    Daniel    the 3/4 break falls three verses earlier in the masoretic than in english or lxx
    Psalms    the lxx renumbers almost the whole psalter -- "the LORD is my shepherd" is Ps 22

Comparing two works without accounting for that returns the wrong verse and no error, which is
what this module exists to prevent.

SCOPE -- read before extending. The rules below are CHAPTER-STRUCTURAL only: they are the places
where a chapter boundary moves, every one verified against the database rather than taken from a
reference table. Verse-level offsets *within* an aligned chapter are deliberately NOT modelled,
because the data says they aren't a property of the scheme at all. Hebrew and Greek count a
psalm's superscription as verse 1 and most English editions don't, but that is a per-digitisation
choice: scrollmapper-KJV counts them (differing from ebible-eng-web in 116 psalms) while WEB does
not. Encoding a single "english" rule for that would be confidently wrong for half the English
works in the database. Use psalm_superscription_risk() to detect it per work-pair instead.
"""

SCHEMES = ("masoretic", "lxx", "english")

# Works whose scheme is not the default. Everything else -- English translations, the Greek NT
# (whose versification is not in dispute), and openbible-crossrefs -- is 'english'.
_MASORETIC_WORKS = frozenset({
    "morphhb-wlc", "macula-hebrew-wlc",
    "scrollmapper-WLC", "scrollmapper-MapM", "scrollmapper-SP", "scrollmapper-HebModern",
})
_LXX_WORKS = frozenset({"ebible-grcbrent"})


def scheme_for_work(work_id: str) -> str:
    # Every Dead Sea Scroll work: Abegg's editors assigned the references against the Hebrew Bible,
    # so they follow the Masoretic division rather than an English one.
    if work_id.startswith("dss-") or work_id in _MASORETIC_WORKS:
        return "masoretic"
    if work_id in _LXX_WORKS:
        return "lxx"
    return "english"


# (book, chapter, verse_start, verse_end) -> (english_chapter, verse_delta), where a None target
# means "this passage has no counterpart in the english scheme at all". English is the hub: a
# masoretic->lxx lookup goes through it. Anything not listed here maps to itself.
# Hosea, Joel and Malachi are where the English tradition, not the Hebrew, is the outlier: the LXX
# keeps the Masoretic chapter division in all three (Brenton's Joel has four chapters, his Malachi
# three, and his Hosea 1 ends at verse 9 exactly as the WLC does), so these rules belong to both
# schemes rather than to the Hebrew alone.
#
# Hosea hid for longer than the other two, and the reason is worth recording: its gap is exactly
# two verses, which is the width of the superscription_offset() window below. The count-based scan
# that found Joel and Malachi looks for chapters whose verse counts diverge, and Hosea's do -- but
# any reference that landed wrong was then silently "corrected" by the title-shift heuristic, which
# cannot tell a two-verse chapter division from a two-line psalm heading. It surfaced as Romans
# 9:26 quoting Hosea 2:1 and resolving to English Hosea 2:-1, a verse number that cannot exist.
_HEBREW_CHAPTER_DIVISION = [
    ("Hos", 2, 1, 2, 1, 9),            # Hos 2:1-2      = EN Hos 1:10-11 (Rom 9:26 quotes 2:1)
    ("Hos", 2, 3, 25, 2, -2),          # Hos 2:3-25     = EN Hos 2:1-23
    ("Joel", 3, 1, 5, 2, 27),          # Joel 3:1-5     = EN Joel 2:28-32 (the verse Acts 2 quotes)
    ("Joel", 4, 1, 21, 3, 0),          # Joel 4         = EN Joel 3
    ("Mal", 3, 19, 24, 4, -18),        # Mal 3:19-24    = EN Mal 4:1-6
]

# Daniel divides its chapters differently in each direction, which is why neither "the LXX follows
# the Hebrew" nor "the LXX follows the English" is a safe generalisation. At the 3/4 break the LXX
# sides with English against the Masoretic; at 5/6 it sides with the Masoretic against English,
# where "Darius the Mede received the kingdom" closes chapter 5 in English but opens chapter 6 in
# both Hebrew and Greek.
_DANIEL_FIVE_SIX = [
    ("Dan", 6, 1, 1, 5, 30),           # Dan 6:1    = EN Dan 5:31
    ("Dan", 6, 2, 29, 6, -1),          # Dan 6:2-29 = EN Dan 6:1-28
]

_TO_ENGLISH: dict[str, list[tuple]] = {
    "masoretic": [
        *_HEBREW_CHAPTER_DIVISION,
        ("Dan", 3, 31, 33, 4, -30),    # MT Dan 3:31-33 = EN Dan 4:1-3
        ("Dan", 4, 1, 34, 4, 3),       # MT Dan 4:1-34  = EN Dan 4:4-37
        *_DANIEL_FIVE_SIX,
    ],
    "lxx": [
        *_HEBREW_CHAPTER_DIVISION,
        *_DANIEL_FIVE_SIX,
        # Proverbs turned out to be mostly identity after all. Brenton preserves the HEBREW verse
        # numbering and simply omits what the LXX lacks -- chapter 20 runs to verse 30 with 14-22
        # absent, chapter 31 begins at verse 10 -- so a shorter chapter is not a renumbered one.
        # Six New Testament quotations confirm it: the Greek match and openbible's english-scheme
        # cross-references independently name the same reference for all six (Prov 3:11, 3:12,
        # 11:31, 24:12, 25:21, 25:22). Only chapter 24's tail is genuinely relocated -- it carries
        # the Agur material the English prints as chapter 30.
        ("Prov", 24, 35, 62, None, 0),
        # Jeremiah is reordered, not merely renumbered: the LXX moves the oracles against the
        # nations to the middle of the book, so everything after them shifts. Chapter COUNTS are
        # identical at 52, which is why the count-based scan that found Joel and Malachi missed
        # this -- it surfaced instead as a quotation landing on the "wrong" chapter.
        #
        # Two blocks are mapped, each agreed on by two independent methods run against this
        # database. (a) Chapters 1-24 at offset 0: 16 of those chapters' verse counts match
        # English exactly and nothing contradicts it. (b) Chapters 33-51 at offset -7: 13 verse
        # counts match, and Hebrews 8:9/8:10/8:11 independently anchor LXX Jeremiah 38:32-34 to
        # English 31:32-34 (25, 25 and 9 shared English trigrams) -- verse numbers unchanged.
        #
        # Chapters 25-32 and 52 are the reordered oracles and the closing narrative. No offset
        # holds across them and no anchor lands in them, so they stay unmapped rather than
        # guessed. That is the block a published mapping table would close.
        # The relocated oracles. Each chapter names the nation it is against, and proper nouns
        # survive translation, so the Greek name and the English name identify the same chapter
        # without recourse to a published table. Verse deltas were then confirmed by matching
        # place names verse by verse: 15/16, 37/38, 40/41, 3/3 and 27/27 name hits respectively,
        # all at delta 0, each dominating the next-best delta by a wide margin.
        ("Jer", 25, 1, 13, 25, 0),        # the unshifted opening of the chapter
        ("Jer", 25, 14, 19, 49, 20),      # Elam: LXX 25:14 is verbatim EN 49:34, 25:19 is 49:39
        ("Jer", 25, 20, 20, None, 0),     # a displaced Elam superscription; EN 49:34 is taken
        ("Jer", 26, 1, 999, 46, 0),       # Egypt
        ("Jer", 27, 1, 999, 50, 0),       # Babylon
        ("Jer", 28, 1, 999, 51, 0),       # Babylon, continued
        ("Jer", 29, 1, 999, 47, 0),       # the Philistines
        # The composite chapter -- Edom, Damascus, Kedar, Ammon -- whose sub-oracles the LXX puts
        # in a different order from the English, so no single delta holds (best scored 6 of 16
        # against 4 for the runner-up). Internally reordered, and left unmapped.
        ("Jer", 30, 1, 999, None, 0),
        ("Jer", 31, 1, 999, 48, 0),       # Moab
        ("Jer", 32, 15, 38, 25, 0),       # the cup of wrath. Brenton keeps the Hebrew's own verse
                                          # numbers here, so this chapter runs 15-38, not 1-24
        *[("Jer", n, 1, 999, n - 7, 0) for n in range(33, 51)],
        # 51 splits: its tail is the word to Baruch, which English prints as its own chapter.
        # LXX 51:31 is verbatim EN 45:1 ("to Baruch the son of Neriah, when he wrote").
        ("Jer", 51, 1, 30, 44, 0),
        ("Jer", 51, 31, 35, 45, -30),
        # chapter 52 needs no rule: 28 of 29 name hits sit at delta 0
        ("Ps", 9, 22, 39, 10, -21),    # LXX Ps 9 is EN 9 + 10
        *[("Ps", n, 1, 999, n + 1, 0) for n in range(10, 113)],
        ("Ps", 113, 1, 8, 114, 0),     # LXX Ps 113 is EN 114 + 115
        ("Ps", 113, 9, 26, 115, -8),
        ("Ps", 114, 1, 9, 116, 0),     # LXX Ps 114 + 115 is EN 116
        ("Ps", 115, 1, 9, 116, 9),
        *[("Ps", n, 1, 999, n + 1, 0) for n in range(116, 146)],
        ("Ps", 146, 1, 11, 147, 0),    # LXX Ps 146 + 147 is EN 147
        ("Ps", 147, 1, 9, 147, 11),
        ("Ps", 151, 1, 999, None, 0),  # supernumerary -- no English counterpart
        # Daniel 3's Song of the Three (LXX 3:24-90) has no English counterpart, and Brenton's
        # verse division either side of it does not reconcile with the English chapter's 30
        # verses. Left unmapped rather than guessed: a wrong mapping here is worse than none.
    ],
}


# Chapters an english reference can name that simply do not exist in the other scheme, so the
# reverse lookup has nothing to return. Without this the fall-through would hand back an identity
# reference to a chapter that isn't there. Verified against the works in bible-text.db.
_ABSENT_CHAPTERS = {
    "lxx": {("Prov", 30)},   # the Agur material lives inside LXX Proverbs 24; there is no ch. 30
}


def to_english(scheme: str, book: str, chapter: int, verse: int) -> tuple[str, int, int] | None:
    """A reference in `scheme`, expressed in the english scheme. None when it has no counterpart."""
    if scheme not in SCHEMES:
        raise ValueError(f"unknown versification scheme: {scheme!r}")
    for rule_book, rule_chapter, start, end, to_chapter, delta in _TO_ENGLISH.get(scheme, ()):
        if book == rule_book and chapter == rule_chapter and start <= verse <= end:
            if to_chapter is None:
                return None
            return (book, to_chapter, verse + delta)
    return (book, chapter, verse)


def from_english(scheme: str, book: str, chapter: int, verse: int) -> tuple[str, int, int] | None:
    """The inverse. None when `scheme` has no counterpart for this english reference."""
    if scheme not in SCHEMES:
        raise ValueError(f"unknown versification scheme: {scheme!r}")
    if (book, chapter) in _ABSENT_CHAPTERS.get(scheme, ()):
        return None
    for rule_book, rule_chapter, start, end, to_chapter, delta in _TO_ENGLISH.get(scheme, ()):
        if to_chapter is None or book != rule_book or to_chapter != chapter:
            continue
        if start + delta <= verse <= end + delta:
            return (book, rule_chapter, verse - delta)
    # not the target of any rule -- but guard against handing back a reference this scheme
    # renumbers away from, e.g. english Ps 30 does not exist unshifted in the lxx
    for rule_book, rule_chapter, start, end, to_chapter, _ in _TO_ENGLISH.get(scheme, ()):
        if to_chapter is not None and book == rule_book and rule_chapter == chapter:
            return None
    return (book, chapter, verse)


def superscription_offset(source_count: int | None, target_count: int | None) -> int:
    """Verse shift between two works' numbering of the same chapter, from their verse counts.

    align() moves the chapter, which is a property of the scheme. This moves the verse, which is
    not: Hebrew and Greek count a psalm's superscription as verse 1 and most English editions do
    not, and which a given edition does is a per-digitisation choice -- scrollmapper-KJV counts
    them and differs from ebible-eng-web in 116 psalms. So it is measured between the two works in
    hand rather than encoded as a rule.

    One or two verses is a title. A larger gap means the target omits verses somewhere else
    entirely, where shifting the front would be the wrong correction, so nothing is applied.
    Validated against 60 New Testament quotations of the Psalms, anchored independently on the
    Greek and the English: it reproduces the true verse in every one.
    """
    if not source_count or not target_count:
        return 0
    difference = source_count - target_count
    return difference if 0 < abs(difference) <= 2 else 0


def align(book: str, chapter: int, verse: int, from_scheme: str, to_scheme: str):
    """Move one reference between schemes. None means the target scheme has no such verse."""
    if from_scheme == to_scheme:
        return (book, chapter, verse)
    english = to_english(from_scheme, book, chapter, verse)
    if english is None:
        return None
    return from_english(to_scheme, *english)
