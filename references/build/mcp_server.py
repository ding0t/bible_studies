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
def bible_crossref(book: str, chapter: int, verse: int, min_votes: int = 0, limit: int = 20) -> list[dict]:
    """Cross-references for one verse (OpenBible.info/TSK-style data), highest-voted first.
    Raise min_votes to drop low-confidence links."""
    conn = query.connect()
    try:
        return query.lookup_crossref(conn, book, chapter, verse, min_votes=min_votes, limit=limit)
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
