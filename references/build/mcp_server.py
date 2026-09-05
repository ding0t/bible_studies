"""MCP server exposing this repo's reference databases as tools for an agent session.

Every tool below is a thin wrapper around a `lookup_*`/`list_works` function imported
from query.py (bible-text.db) or twot_lookup.py (TWOT root map) -- no query logic lives in this
file. That's deliberate: query.py and twot_lookup.py are usable standalone from the CLI whether
or not this server is running (that's the fallback path for an agent without MCP configured,
and the normal path for you at the terminal); this file only adds a second, structured
front end over the exact same functions, so the two can never drift apart or disagree.

To add a resource's tools here: write its `lookup_*` functions in a plain library module
(pure functions returning JSON-friendly dicts/lists, a `connect()`/`load_*()` that raises
FileNotFoundError rather than SystemExit -- see query.py/twot_lookup.py for the pattern), then add
one `@mcp.tool()` wrapper per function below. Do not put SQL or JSON parsing in this file.

study-notes.db (external commercial commentary, quotation-only license tier) has no query
library yet, so it has no tools here either -- see references/README.md before adding one;
that data needs tighter discipline (snippet-sized returns, not raw notes) than the tiers
bible-text.db and TWOT are under.

Run directly for a quick check: `uv run python mcp_server.py` (stdio transport).
Registered with Claude Code via ../../.mcp.json.
"""
from mcp.server.fastmcp import FastMCP

import query
import twot_lookup

mcp = FastMCP(
    "bible-references",
    instructions=(
        "Tools over this repo's local Bible reference data: bible-text.db (translations, "
        "Greek/Hebrew morphology, Louw-Nida/SDBH semantic domains, cross-references) and the "
        "TWOT Strong's/BDB root map. Call bible_works first if you're about to quote a source "
        "publicly -- license_tier varies per work_id ('open' is safe to quote at length; "
        "'restricted-nc' and others are not). Default translation is WEB (public domain) "
        "unless a translation is specified."
    ),
)


# ---------------------------------------------------------------------------
# bible-text.db
# ---------------------------------------------------------------------------

@mcp.tool()
def bible_word(strongs: str | None = None, lemma: str | None = None, book: str | None = None) -> list[dict]:
    """Every occurrence of a Strong's number (e.g. 'G680', 'H1') or exact lemma across the
    ingested Greek/Hebrew morphology sources. Give strongs or lemma (or both); optionally
    restrict to one OSIS book code (e.g. 'Mark')."""
    conn = query.connect()
    try:
        return query.lookup_word(conn, strongs=strongs, lemma=lemma, book=book)
    finally:
        conn.close()


@mcp.tool()
def bible_concordance(strongs: str, book: str | None = None, work_id: str | None = None) -> list[dict]:
    """Every occurrence of one Strong's number, for tracing how a word is used across the
    whole corpus (or one book/source). This is the word-study 'concordance' step."""
    conn = query.connect()
    try:
        return query.lookup_concordance(conn, strongs, book=book, work_id=work_id)
    finally:
        conn.close()


@mcp.tool()
def bible_domain(code: str) -> list[dict]:
    """Every word sharing a Louw-Nida (Greek, e.g. '23.136') or SDBH (Hebrew) semantic
    domain code -- for the semantic-domain cross-check in a word study."""
    conn = query.connect()
    try:
        return query.lookup_domain(conn, code)
    finally:
        conn.close()


@mcp.tool()
def bible_verse(book: str, chapter: int, verse: int, translation: str | None = None) -> dict[str, object]:
    """Translation text, word-by-word morphology, and any translator/study notes for one
    verse. translation defaults to WEB; give a code like 'KJV', 'ASV', or 'ebible-heb'.
    For a range of verses, use bible_passage instead (cheaper -- no morphology noise)."""
    conn = query.connect()
    try:
        return query.lookup_verse(conn, book, chapter, verse, translation=translation)
    finally:
        conn.close()


@mcp.tool()
def bible_syntax(book: str, chapter: int, verse: int, work_id: str | None = None) -> dict[str, object]:
    """Clause-level syntax and coreference for one verse, from the MACULA annotation -- what
    morphology alone can't tell you: which word is subject vs object vs indirect object, what an
    implicit subject refers to, what a pronoun points back at, and for Hebrew whether a noun is in
    construct and which conjugation a verb is (qatal/wayyiqtol/yiqtol, in the sub_type field).

    Pointers are resolved to the word they name, across verse boundaries where the antecedent sits
    earlier. Hebrew OT and Greek NT only; a null field means 'not annotated', not 'no such role',
    so don't read absence off it. Use this after bible_verse when the argument turns on who is
    doing what to whom rather than on a single word's meaning."""
    conn = query.connect()
    try:
        return query.lookup_syntax(conn, book, chapter, verse, work_id=work_id)
    finally:
        conn.close()


@mcp.tool()
def bible_passage(book: str, chapter: int, verse_start: int, verse_end: int,
                   end_chapter: int | None = None, translation: str | None = None,
                   include_notes: bool = False) -> dict[str, object]:
    """Translation text for a verse range (a pericope), in one call instead of one
    bible_verse call per verse. If the range crosses a chapter boundary, set end_chapter
    (verse_end is then read in end_chapter); otherwise verse_start/verse_end are both
    within `chapter`. Text only unless include_notes=True."""
    conn = query.connect()
    try:
        return query.lookup_passage(
            conn, book, chapter, verse_start, verse_end,
            end_chapter=end_chapter, translation=translation, include_notes=include_notes,
        )
    finally:
        conn.close()


@mcp.tool()
def bible_crossref(book: str, chapter: int, verse: int, min_votes: int = 0, limit: int = 20,
                   from_scheme: str = "english") -> list[dict]:
    """Cross-references for one verse (OpenBible.info/TSK-style data), highest-voted first.
    Raise min_votes to drop low-confidence links. The data is numbered in the english scheme,
    so pass from_scheme='masoretic' or 'lxx' when your reference came off a Hebrew or
    Septuagint text -- otherwise Joel 3:1 returns the links for the wrong verse."""
    conn = query.connect()
    try:
        return query.lookup_crossref(conn, book, chapter, verse, min_votes=min_votes, limit=limit,
                                     from_scheme=from_scheme)
    finally:
        conn.close()


@mcp.tool()
def bible_parallel(book: str, chapter: int, verse: int, target: str, source: str | None = None) -> dict:
    """The same verse in another work, aligned by chapter AND verse.

    Use this rather than assuming a reference carries across, especially in the Psalms. The chapter
    shift is a scheme property (English Psalm 40 is LXX Psalm 39); the verse shift is not -- Hebrew
    and Greek count a psalm's superscription as verse 1 and most English editions don't, and which
    a given edition does varies by edition, so it is measured between the two works you name.
    English Psalm 40:6 is LXX Psalm 39:7, the verse Hebrews 10:5 quotes; without the verse step it
    resolves to 39:6 and returns the wrong text. `source` defaults to the WEB.
    """
    conn = query.connect()
    try:
        return query.lookup_parallel(conn, book, chapter, verse, source, target)
    finally:
        conn.close()


@mcp.tool()
def bible_links(book: str, chapter: int, verse: int, link_type: str | None = None,
                min_run: int = 0) -> dict:
    """Derived scripture links at one reference, both directions, grouped by class.

    Computed from the texts themselves rather than taken from a cross-reference list, so these find
    links such lists miss. The three classes are NOT equivalent evidence and must never be merged:

      quotation-greek   New Testament quoting the Septuagint. A textual fact -- both sides are the
                        same language, so the quotation is literally the same words.
      inner-biblical    the Hebrew Old Testament quoting itself (Kings//Chronicles, Kings//Isaiah,
                        the Decalogue). Equally textual, no translation in between.
      quotation-hebrew  a Hebrew New Testament matching the Hebrew Old Testament. CANDIDATES ONLY --
                        those are 19th-century translations, so a match means a Hebraist judged this
                        a quotation, which is informed opinion rather than evidence. Valuable
                        because it catches quotations the Greek misses, where the New Testament
                        follows the Hebrew rather than the Septuagint. Verify in Greek before using.

    Grade by `longest_run`: 8 or more reads as quotation, 4-5 is usually a shared formula.
    `corroborated` means openbible independently names the same passage; a strong run without it is
    a link the tradition missed, not a weak one. Give references as an English Bible numbers them.
    """
    conn = query.connect()
    try:
        return query.lookup_links(conn, book, chapter, verse, link_type=link_type, min_run=min_run)
    finally:
        conn.close()


@mcp.tool()
def study_gaps(study_path: str, limit: int = 10) -> dict:
    """What links to a study's passages that the study never mentions.

    Reads the study's own primary_passage and bible_references frontmatter, gathers quotation links
    (derived from the Greek) and openbible cross-references against those passages, subtracts every
    chapter the study already cites, and ranks what is left with quotations first. Use it during a
    review pass; a study with neither frontmatter field is invisible to it and reports so.

    The two kinds are not equivalent and are kept apart: a quotation at a strong run is a textual
    fact, a cross-reference is a lead worth chasing. `study_path` is repo-relative, e.g.
    docs/content/last-things/rapture.md
    """
    import sqlite3
    import study_gaps as gaps

    path = (gaps.REPO_ROOT / study_path).resolve()
    if not path.is_file():
        return {"error": f"no such study: {study_path}"}
    conn = sqlite3.connect(f"file:{gaps.DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        title, chapters, raw = gaps.study_references(path)
        if not chapters:
            return {"study": study_path, "title": title,
                    "warning": "no primary_passage or bible_references -- invisible to this check"}
        ranked = gaps.gaps_for(conn, chapters)
        for entry in ranked:
            entry["from"] = sorted(entry["from"])
        return {"study": study_path, "title": title, "cites_chapters": len(chapters),
                "cited_references": raw, "gap_count": len(ranked), "gaps": ranked[:limit]}
    finally:
        conn.close()


@mcp.tool()
def bible_interlinear(book: str, chapter: int, verse: int) -> dict:
    """Which original-language word each English word renders, for one verse.

    Reach for this whenever a study makes something turn on an English word -- before writing "the
    text says X", check what X is actually translating. Every other tool here describes one side or
    the other; this is the only one that links them, using unfoldingWord's ULT alignment against
    the UHB (Hebrew) and UGNT (Greek).

    The mapping is many-to-many and comes back that way. Genesis 1:1's "the heavens" renders both
    אֵת and הַשָּׁמַיִם, because the Hebrew object marker has no English of its own and the alignment
    encloses the phrase twice. Two rows sharing an English phrase is the data being honest, not a
    duplicate to filter out.

    Two cautions. ULT is one literal translation, so this answers "what does ULT render this with",
    not "what must this English word mean" -- for the word's own range use `bible_word`. And the
    Greek side is the UGNT, a Bunning Heuristic Prototype text rather than the SBLGNT the rest of
    this database uses: at John 1:34 they differ (υἱός against ἐκλεκτός), so check `bible_verse`
    before resting a New Testament argument on the wording here.
    """
    conn = query.connect()
    try:
        return query.lookup_interlinear(conn, book, chapter, verse)
    finally:
        conn.close()


@mcp.tool()
def bible_grammar(term: str, full: bool = False) -> list:
    """Biblical Hebrew grammar articles -- what a FORM does, as against what a word means.

    The lexicons reached through `bible_word` and `twot_root` say what a word means. This says what
    the morphology is doing: what a gentilic adjective is, how the dual differs from the plural,
    what the definite article does in a construct chain. develop-bible-study's Phase 4 asks for
    "grammar/syntax points that affect meaning" and this is where they come from -- previously they
    came from recall, which is exactly the habit this project exists to replace.

    Search by slug, title or phrase: "gentilic", "construct", "dual", "cohortative". Pass
    `full=True` for the complete article once you have found the right one; the default truncates so
    several can be scanned at once. Source is unfoldingWord's UHG, CC BY-SA 4.0.
    """
    conn = query.connect()
    try:
        return query.lookup_grammar(conn, term, full=full)
    finally:
        conn.close()


@mcp.tool()
def bible_variants(book: str, chapter: int, verse: int | None = None) -> dict:
    """Where the Dead Sea Scrolls read something the Masoretic text does not.

    Use it when a study rests on an Old Testament reading, especially one a New Testament writer
    quotes. Deuteronomy 32:8 is the standard case: 4Q37 reads "sons of God" where the Masoretic has
    "sons of Israel", and the Septuagint and New Testament follow the scroll.

    Compared at LEMMA level -- the scrolls' fuller spelling and their habit of writing a prefix as
    a separate word make 99% of verses "differ" on surface forms, which tells you nothing -- and
    only fully-extant scroll words count, since 46% of signs in this corpus are a modern editor's
    reconstruction. Reported one way only: a lemma the scroll has and the Masoretic lacks is a
    reading, while the reverse is nearly always damage.

    ALWAYS check `extant_words` before leaning on a row. It says how much of that verse survives:
    Deuteronomy 32:8's reading is legible but sits in a verse where only two words do, and a study
    should say so rather than cite it flat. Omit `verse` for a whole chapter.
    """
    conn = query.connect()
    try:
        return query.lookup_variants(conn, book, chapter, verse)
    finally:
        conn.close()


@mcp.tool()
def bible_trace(book: str, chapter: int, verse: int, translation: str | None = None) -> dict:
    """Everything the corpus knows about one verse, with the evidence for each connection shown.

    The tool to reach for when a study turns on where a verse comes from. Unlike a cross-reference
    list, every connection carries HOW it was established, how strongly, the linked verse in its
    original language, an English rendering, and the words the two verses actually share -- so a
    reader can judge the link rather than take it on trust.

    Connections are grouped by method and never merged into one score. quotation-greek and
    inner-biblical are textual facts, both sides being the same language. allusion-lemma is shared
    rare vocabulary with no shared phrasing. quotation-hebrew is a 19th-century translator's
    judgement and must be verified in Greek. `leads` holds crowd-assembled cross-references, which
    are worth chasing and are not evidence.

    Where a link lands on an Old Testament verse the Dead Sea Scrolls attest, any scroll reading
    the Masoretic lacks is attached, with how much of that verse survives.

    Matthew 21:5 is a good demonstration: it returns the Isaiah 62:11 quotation, the Zechariah 9:9
    echo, and a scroll variant -- which together show it to be a conflation of two passages.
    """
    conn = query.connect()
    try:
        return query.lookup_trace(conn, book, chapter, verse, translation)
    finally:
        conn.close()


@mcp.tool()
def bible_align(book: str, chapter: int, verse: int, from_scheme: str = "english") -> dict:
    """One reference as each versification scheme numbers it, with the works using each scheme.

    Run this before comparing a Hebrew or Greek verse against an English one. (book, chapter,
    verse) is not a universal address: Hebrew and LXX Joel 3:1 is English Joel 2:28 (the verse
    Acts 2 quotes), Hebrew Malachi 3:19 is English Malachi 4:1, and the LXX renumbers nearly the
    whole psalter, so English Psalm 23 is LXX Psalm 22. A null reference for a scheme means that
    scheme has no counterpart for the verse at all. from_scheme is the scheme YOUR reference is
    in -- 'english' unless you are reading a number off a Hebrew or Septuagint text.
    """
    conn = query.connect()
    try:
        return query.lookup_alignment(conn, book, chapter, verse, from_scheme)
    finally:
        conn.close()


@mcp.tool()
def bible_works() -> list[dict]:
    """Every ingested source (translation, lexicon, morphology set) with its license_tier.
    Check this before quoting a source at length in anything meant to be public -- only
    'open' tier is unrestricted; see references/README.md for what the other tiers allow."""
    conn = query.connect()
    try:
        return query.list_works(conn)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# TWOT root map
# ---------------------------------------------------------------------------

@mcp.tool()
def twot_root(root: str) -> list[dict]:
    """TWOT (Theological Wordbook of the Old Testament) entries under one root number,
    e.g. '1a'. Returns Strong's id, BDB id, lemma, transliteration, and gloss -- these
    bare facts are open-ish; the copyrighted discussion prose is not in this repo at all."""
    return twot_lookup.lookup_root(root)


@mcp.tool()
def twot_strongs(strongs_id: str) -> list[dict]:
    """TWOT root(s) for a Strong's Hebrew number (e.g. 'H1', or bare '1'). Hebrew/Aramaic
    OT only -- there is no TWOT coverage for Greek (G-prefixed) numbers. A handful of
    Strong's numbers map to more than one TWOT root (sub-senses); this can return several."""
    return twot_lookup.lookup_strongs(strongs_id)


@mcp.tool()
def twot_lemma(lemma: str) -> list[dict]:
    """TWOT root(s) for an exact Hebrew lemma match, e.g. 'אָב'."""
    return twot_lookup.lookup_lemma(lemma)


if __name__ == "__main__":
    mcp.run()
