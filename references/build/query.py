"""Query library + CLI for bible-text.db.

Every lookup lives in a plain `lookup_*`/`list_works` function that takes a connection
and returns JSON-friendly data (dicts/lists) -- no printing, no argparse. `main()` below
is a thin CLI wrapper around those functions for interactive/terminal use. `mcp_server.py`
imports the same functions directly and exposes them as MCP tools, so the CLI and the MCP
server are two front ends over one source of truth; neither duplicates query logic, and the
CLI keeps working standalone whether or not the MCP server is configured. Read-only;
build.py owns writes.

CLI examples:
    uv run python query.py word --strongs G680
    uv run python query.py word --lemma dikaiosune
    uv run python query.py concordance G4982 --book Mark
    uv run python query.py domain 23.136
    uv run python query.py verse Mark 5 27
    uv run python query.py verse Mark 5 27 --translation KJV
    uv run python query.py passage Mark 5 21 43
    uv run python query.py passage Mark 4 35 20 --end-chapter 5
    uv run python query.py crossref Mark 5 27
    uv run python query.py works
"""
import argparse
import sqlite3
from pathlib import Path

import quotations
import versification
from book_map import NUM_TO_OSIS

DB_PATH = Path(__file__).resolve().parent / "out" / "bible-text.db"
DEFAULT_TRANSLATION_WORK_ID = "ebible-eng-web"  # WEB: public domain, full Bible, no permission caveats
_ALL_OSIS_BOOKS = set(NUM_TO_OSIS.values())


def connect() -> sqlite3.Connection:
    """Open a read-only connection. Raises FileNotFoundError (not SystemExit) so callers
    other than the CLI -- the MCP server, a test, another script -- can catch it instead
    of the process being killed."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"{DB_PATH} not found -- run `uv run python build.py` first.")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _resolve_work_id(conn: sqlite3.Connection, translation: str | None) -> str:
    """A translation code or work_id -> the work_id actually in the database.

    Resolved against `works` rather than by string convention. Guessing "scrollmapper-{code}"
    silently returned nothing for the five codes that live under a different prefix -- WEB among
    them, which is this repo's default English text: every lookup_verse(..., 'WEB') came back
    empty while the text sat in ebible-eng-web.
    """
    if not translation:
        return DEFAULT_TRANSLATION_WORK_ID
    if conn.execute("SELECT 1 FROM works WHERE work_id=?", (translation,)).fetchone():
        return translation
    # by translation_code, preferring a work that actually carries verses, then an open licence
    rows = conn.execute(
        "SELECT w.work_id FROM works w LEFT JOIN verses v ON v.work_id = w.work_id "
        "WHERE w.translation_code = ? COLLATE NOCASE "
        "GROUP BY w.work_id ORDER BY COUNT(v.rowid) = 0, w.license_tier != 'open', w.work_id",
        (translation,),
    ).fetchall()
    if rows:
        return rows[0]["work_id"]
    return f"scrollmapper-{translation}"  # unknown: let _empty_result_reason explain it


# ---------------------------------------------------------------------------
# Lookup functions -- shared by the CLI below and mcp_server.py.
# ---------------------------------------------------------------------------

def _empty_result_reason(conn: sqlite3.Connection, work_id: str, book: str,
                          chapter: int | None = None, verse: int | None = None,
                          from_scheme: str = "english") -> str:
    """A found-nothing verse/passage lookup looks identical whether the caller typo'd the book
    code or the translation genuinely doesn't cover that book (e.g. an NT-only Greek text, or --
    what this was written for -- ingest_ebible silently dropping 22 books from WEB/Delitzsch/
    Tischendorf/Brenton before the BOS_CODE_TO_USFM fix). Give the caller enough to tell those
    apart instead of a bare empty list that reads the same either way."""
    if book not in _ALL_OSIS_BOOKS:
        return f"'{book}' isn't a recognized OSIS book code (expected e.g. Gen, 1Kgs, Matt, 1Cor, Rev)."
    has_any = conn.execute(
        "SELECT 1 FROM verses WHERE work_id=? AND book=? LIMIT 1", (work_id, book),
    ).fetchone()
    if not has_any:
        return (f"{work_id} has no verses for {book} at all -- this translation may not cover "
                f"that book (check bible_works), or try a different translation.")
    # The commonest cause of a miss in a book the work DOES carry is a versification mismatch, and
    # "check the reference" sends the caller looking for a typo that isn't there. uw-uhb numbers
    # verses the ULT's way and morphhb-wlc the Hebrew way, so Joel 2:28 is a real verse in one and
    # absent from the other; say which number to ask for instead of implying user error.
    if chapter is not None and verse is not None:
        target_scheme = _work_scheme(conn, work_id)
        if target_scheme == "masoretic" and from_scheme == "english":
            stated = _stated_alt_ref(conn, book, chapter, verse)
            if stated and conn.execute(
                "SELECT 1 FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                (work_id, book, stated["alt_chapter"], stated["alt_verse"]),
            ).fetchone():
                return (f"{work_id} uses masoretic versification. UHB records that "
                        f"{book} {chapter}:{verse} is {book} {stated['alt_chapter']}:"
                        f"{stated['alt_verse']} in Hebrew numbering -- ask for that reference.")
        if target_scheme != from_scheme:
            ref = versification.align(book, chapter, verse, from_scheme, target_scheme)
            if ref is not None:
                a_book, a_chapter, a_verse = ref
                exists = conn.execute(
                    "SELECT 1 FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                    (work_id, a_book, a_chapter, a_verse),
                ).fetchone()
                if exists:
                    return (f"{work_id} uses {target_scheme} versification, where "
                            f"{book} {chapter}:{verse} ({from_scheme}) is "
                            f"{a_book} {a_chapter}:{a_verse}. Ask for that reference, or use "
                            f"`query.py parallel` -- it resolves work-to-work and also applies "
                            f"the psalm-superscription offset, which `align` (scheme-to-scheme) "
                            f"does not.")
    return f"{book} exists in {work_id}, but not at the chapter/verse given -- check the reference."

# Strong's numbers are stored bare (schema.sql explains why), so G1242 and H1242 are the same
# string in the table -- diatheke and boqer, "covenant" and "morning". A prefixed query therefore
# has to filter by the work's language or it silently mixes the testaments' numbering. The
# collision was always there; adding 566k Strong's-tagged Septuagint rows made it loud.
_STRONGS_LANGUAGES = {"G": ("grc",), "H": ("heb", "hbo")}


def _strongs_filter(strongs: str) -> tuple[str, list]:
    """(WHERE clause, params) restricting a Strong's lookup to the language its prefix names.

    Returned as a bare clause for the caller's `where` list rather than as SQL to append, because
    appending it after the other clauses while inserting its parameters before them binds every
    placeholder to the wrong value -- 'Matt' went to the language subquery and 'grc' to `book = ?`,
    and the lookup silently returned nothing. Clause and params have to move together.
    """
    languages = _STRONGS_LANGUAGES.get(strongs[:1].upper()) if strongs[:1].isalpha() else None
    if not languages:
        return "", []
    placeholders = ",".join("?" * len(languages))
    return (f"work_id IN (SELECT work_id FROM works WHERE language IN ({placeholders}))",
            list(languages))


def lookup_word(conn: sqlite3.Connection, strongs: str | None = None, lemma: str | None = None,
                 book: str | None = None) -> list[dict]:
    """Every occurrence of a Strong's number or lemma, across the Greek/Hebrew morphology sources."""
    if not strongs and not lemma:
        raise ValueError("word lookup needs strongs or lemma")
    where, params = [], []
    if strongs:
        where.append("strongs_id = ?")
        params.append(strongs.lstrip("GH"))
        language_clause, language_params = _strongs_filter(strongs)
        if language_clause:
            where.append(language_clause)
            params.extend(language_params)
    if lemma:
        where.append("lemma = ?")
        params.append(lemma)
    if book:
        where.append("book = ?")
        params.append(book)
    rows = conn.execute(
        f"SELECT work_id, book, chapter, verse, surface_form, lemma, strongs_id, gloss, domain_code "
        f"FROM morphology WHERE {' AND '.join(where)} ORDER BY work_id, book, chapter, verse",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def lookup_concordance(conn: sqlite3.Connection, strongs: str, book: str | None = None,
                        work_id: str | None = None) -> list[dict]:
    """Every occurrence of one Strong's number -- the word-study-method.md 'concord across
    the corpus' step, without hand-writing the GROUP BY each time."""
    where, params = ["strongs_id = ?"], [strongs.lstrip("GH")]
    language_clause, language_params = _strongs_filter(strongs)
    if language_clause:
        where.append(language_clause)
        params.extend(language_params)
    if book:
        where.append("book = ?")
        params.append(book)
    if work_id:
        where.append("work_id = ?")
        params.append(work_id)
    rows = conn.execute(
        f"SELECT work_id, book, chapter, verse, gloss FROM morphology "
        f"WHERE {' AND '.join(where)} ORDER BY work_id, book, chapter, verse",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def lookup_domain(conn: sqlite3.Connection, code: str) -> list[dict]:
    """Every word sharing a Louw-Nida (Greek) or SDBH lexdomain (Hebrew) code -- the
    semantic-domain cross-check step in word-study-method.md."""
    rows = conn.execute(
        "SELECT DISTINCT work_id, lemma, gloss, strongs_id FROM morphology "
        "WHERE domain_code = ? OR domain_code LIKE ? OR domain_code LIKE ? "
        "ORDER BY work_id, lemma",
        (code, f"{code} %", f"% {code}%"),
    ).fetchall()
    return [dict(r) for r in rows]


def lookup_syntax(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                   work_id: str | None = None) -> dict[str, object]:
    """Clause-level syntax and coreference for one verse, from the MACULA annotation.

    Answers the questions morphology alone can't: which word is the subject, which the object, what
    an implicit subject actually refers to, what a pronoun points back at, and (Hebrew) whether a
    noun is in construct and which conjugation a verb is.

    Each word's subject_ref/referent pointer is resolved to the word it names -- including across
    verses, which is the common case for a pronoun or an implicit subject whose antecedent sits in an
    earlier verse. An unresolved pointer means the target is outside this corpus's annotation, not
    that the reference is broken.
    """
    rows = conn.execute(
        "SELECT work_id, word_position, surface_form, lemma, gloss, node_id, word_class, "
        "syntactic_role, sub_type, state, frame, subject_ref, referent FROM morphology "
        "WHERE book=? AND chapter=? AND verse=? AND node_id IS NOT NULL "
        + ("AND work_id=? " if work_id else "")
        + "ORDER BY work_id, word_position",
        (book, chapter, verse, work_id) if work_id else (book, chapter, verse),
    ).fetchall()

    words = [dict(r) for r in rows]
    # Pointers are space-separated and may name several nodes (a plural subject, a pronoun with more
    # than one antecedent), so every pointer resolves to a *list*, even when it holds one id.
    wanted = {
        (w["work_id"], node)
        for w in words for p in ("subject_ref", "referent") if w[p] for node in w[p].split()
    }
    targets: dict[tuple[str, str], dict] = {}
    for wid, node in wanted:
        hit = conn.execute(
            "SELECT book, chapter, verse, surface_form, gloss FROM morphology "
            "WHERE work_id=? AND node_id=? LIMIT 1", (wid, node),
        ).fetchone()
        if hit:
            targets[(wid, node)] = dict(hit)

    for w in words:
        for pointer, label in (("subject_ref", "subject"), ("referent", "refers_to")):
            if not w[pointer]:
                continue
            nodes = w[pointer].split()
            found = [targets[(w["work_id"], n)] for n in nodes if (w["work_id"], n) in targets]
            w[label] = found
            if len(found) < len(nodes):
                w[f"{label}_unresolved"] = len(nodes) - len(found)

    result: dict[str, object] = {
        "book": book, "chapter": chapter, "verse": verse, "words": words,
    }
    if not words:
        result["warning"] = (
            "No MACULA syntax rows for this verse. MACULA covers the Hebrew OT (macula-hebrew-wlc) "
            "and Greek NT (macula-greek-sblgnt) only -- there is no syntax annotation for English "
            "translations. If the reference is inside that range, the verse may simply be unannotated."
        )
    return result


def _work_scheme(conn: sqlite3.Connection, work_id: str) -> str:
    row = conn.execute("SELECT versification FROM works WHERE work_id=?", (work_id,)).fetchone()
    return row["versification"] if row else "english"


def _aligned_refs(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                   from_scheme: str) -> dict[str, tuple[str, int, int]]:
    """This reference expressed in every versification scheme present in the database. A scheme is
    absent from the result when it has no counterpart for the verse (LXX Psalm 151, say)."""
    schemes = [r[0] for r in conn.execute("SELECT DISTINCT versification FROM works")]
    resolved = {}
    for scheme in schemes:
        ref = versification.align(book, chapter, verse, from_scheme, scheme)
        if ref is not None:
            resolved[scheme] = ref
    return resolved


def _stated_alt_ref(conn: sqlite3.Connection, book: str, chapter: int, verse: int):
    """The Hebrew reference UHB itself records for this verse, or None.

    Preferred over `versification.align()` wherever it exists, because the verse is stated per verse
    by the source rather than inferred from two works' verse counts, and the chapter is checked
    against the WLC text rather than assumed. `source` says which: 'explicit' and 'verse+verified'
    are both checked, 'verse+unverified' is not. Measured against morphhb-wlc it lands
    on the right verse for 2,014 of 2,027 rows, where align() alone manages 173 -- and it is the only
    thing here that gets English Jonah 1:17 to Hebrew 2:1 or English Job 41:2 to Hebrew 40:26.
    """
    row = conn.execute(
        "SELECT alt_chapter, alt_verse, source FROM versification_map "
        "WHERE book=? AND chapter=? AND verse=? LIMIT 1", (book, chapter, verse),
    ).fetchone()
    return dict(row) if row else None


def _stated_english_ref(conn: sqlite3.Connection, book: str, chapter: int, verse: int):
    """The reverse: given a Hebrew (masoretic) reference, the English number UHB gives it."""
    row = conn.execute(
        "SELECT chapter, verse FROM versification_map "
        "WHERE book=? AND alt_chapter=? AND alt_verse=? LIMIT 1", (book, chapter, verse),
    ).fetchone()
    return dict(row) if row else None


def lookup_verse(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                  translation: str | None = None) -> dict[str, object]:
    """Translation text plus every morphology row and note for one verse -- the single most
    common per-verse lookup when drafting a study."""
    work_id = _resolve_work_id(conn, translation)
    scheme = _work_scheme(conn, work_id)
    verse_row = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
        (work_id, book, chapter, verse),
    ).fetchone()

    # The reference is read in the requested work's own scheme, so morphology and notes have to be
    # fetched at whatever that verse is called in THEIR scheme. Querying them at the caller's
    # numbers silently pairs an English verse with a different Hebrew one: ask for Joel 3:1 in an
    # English work and the unaligned query returns the morphology of Hebrew Joel 3:1, which is
    # English Joel 2:28 -- the Acts 2 verse, not the one asked for.
    aligned = _aligned_refs(conn, book, chapter, verse, scheme)
    morph_rows, notes = [], []
    for other_scheme, (a_book, a_chapter, a_verse) in aligned.items():
        morph_rows += conn.execute(
            "SELECT m.work_id, m.word_position, m.surface_form, m.lemma, m.strongs_id, m.gloss, "
            "m.domain_code FROM morphology m JOIN works w ON w.work_id = m.work_id "
            "WHERE w.versification=? AND m.book=? AND m.chapter=? AND m.verse=? "
            "ORDER BY m.work_id, m.word_position",
            (other_scheme, a_book, a_chapter, a_verse),
        ).fetchall()
        notes += conn.execute(
            "SELECT n.work_id, n.text FROM notes n JOIN works w ON w.work_id = n.work_id "
            "WHERE w.versification=? AND n.book=? AND n.chapter=? AND n.verse=?",
            (other_scheme, a_book, a_chapter, a_verse),
        ).fetchall()

    result = {
        "book": book, "chapter": chapter, "verse": verse, "work_id": work_id,
        "versification": scheme,
        "text": verse_row["text"] if verse_row else None,
        "morphology": [dict(r) for r in morph_rows],
        "notes": [dict(r) for r in notes],
    }
    # only worth reporting when the reference actually moves
    realigned = {s: r for s, r in aligned.items() if s != scheme and r != (book, chapter, verse)}
    if realigned:
        result["aligned_references"] = {
            s: f"{b} {c}:{v}" for s, (b, c, v) in realigned.items()
        }
    # A stated mapping beats an inferred one, and disagreements are worth showing rather than
    # silently preferring one -- they mark the verses where the scheme map is wrong.
    stated = _stated_alt_ref(conn, book, chapter, verse) if scheme == "english" else None
    if stated:
        result["stated_hebrew_reference"] = (
            f"{book} {stated['alt_chapter']}:{stated['alt_verse']}")
        result["stated_hebrew_source"] = stated["source"]
    if verse_row is None:
        result["warning"] = _empty_result_reason(conn, work_id, book, chapter, verse)
    return result


def lookup_passage(conn: sqlite3.Connection, book: str, chapter: int, verse_start: int, verse_end: int,
                    end_chapter: int | None = None, translation: str | None = None,
                    include_notes: bool = False) -> dict[str, object]:
    """Translation text for a verse range -- for studying a pericope without N separate
    verse lookups. Text only unless include_notes is set, to keep the common case cheap."""
    end_chapter = end_chapter or chapter
    work_id = _resolve_work_id(conn, translation)
    rows = conn.execute(
        "SELECT chapter, verse, text FROM verses WHERE work_id=? AND book=? AND "
        "(chapter > ? OR (chapter = ? AND verse >= ?)) AND "
        "(chapter < ? OR (chapter = ? AND verse <= ?)) "
        "ORDER BY chapter, verse",
        (work_id, book, chapter, chapter, verse_start, end_chapter, end_chapter, verse_end),
    ).fetchall()
    result = {
        "book": book, "start_chapter": chapter, "start_verse": verse_start,
        "end_chapter": end_chapter, "end_verse": verse_end, "work_id": work_id,
        "verses": [dict(r) for r in rows],
    }
    if not rows:
        result["warning"] = _empty_result_reason(conn, work_id, book)
    if include_notes:
        notes = conn.execute(
            "SELECT work_id, chapter, verse, text FROM notes WHERE book=? AND "
            "(chapter > ? OR (chapter = ? AND verse >= ?)) AND "
            "(chapter < ? OR (chapter = ? AND verse <= ?)) "
            "ORDER BY chapter, verse",
            (book, chapter, chapter, verse_start, end_chapter, end_chapter, verse_end),
        ).fetchall()
        result["notes"] = [dict(r) for r in notes]
    return result


def lookup_crossref(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                     min_votes: int = 0, limit: int = 20, from_scheme: str = "english") -> list[dict]:
    """Cross-references for one verse (OpenBible.info / TSK-style data), highest-voted
    first -- the Phase 6 'gather cross-references' step without hand SQL.

    The cross-reference data is numbered in the english scheme, so a reference read off a Hebrew
    or Septuagint text has to be aligned first: pass from_scheme='masoretic' for Joel 3:1 out of
    the WLC and you get the links for english Joel 2:28, which is the verse it actually is.
    """
    aligned = versification.align(book, chapter, verse, from_scheme, "english")
    if aligned is None:
        return []
    book, chapter, verse = aligned
    rows = conn.execute(
        "SELECT DISTINCT to_book, to_chapter, to_verse_start, to_verse_end, votes, work_id "
        "FROM cross_references WHERE from_book=? AND from_chapter=? AND from_verse=? AND votes >= ? "
        "ORDER BY votes DESC LIMIT ?",
        (book, chapter, verse, min_votes, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def _chapter_verse_count(conn: sqlite3.Connection, work_id: str, book: str, chapter: int) -> int | None:
    row = conn.execute(
        "SELECT COUNT(*) n FROM verses WHERE work_id=? AND book=? AND chapter=?", (work_id, book, chapter)
    ).fetchone()
    return row["n"] or None


def lookup_parallel(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                     source: str | None = None, target: str | None = None) -> dict[str, object]:
    """The same verse in another work, aligned in both directions a reference can move.

    versification.align() handles the chapter, which is a property of the scheme. The verse needs
    a second step it cannot do: Hebrew and Greek count a psalm's superscription as verse 1 and most
    English editions don't, and whether a given edition does is a per-digitisation choice rather
    than a scheme rule -- scrollmapper-KJV counts them, ebible-eng-web doesn't. So the offset is
    MEASURED between the two works actually named, from the verse counts already in the database.

    Validated against 60 New Testament quotations of the Psalms, anchored independently on both the
    Greek (NT against the LXX) and the English (NT against an English psalter): the measured offset
    reproduces the true verse in every one. Without it, Hebrews 10:5's source resolved to LXX Psalm
    39:6 when the verse it quotes is 39:7.
    """
    src = _resolve_work_id(conn, source)
    tgt = _resolve_work_id(conn, target)
    aligned = versification.align(book, chapter, verse,
                                  _work_scheme(conn, src), _work_scheme(conn, tgt))
    result: dict[str, object] = {
        "source": f"{book} {chapter}:{verse}", "source_work": src, "target_work": tgt,
    }
    if aligned is None:
        result["warning"] = f"{tgt} has no counterpart for {book} {chapter}:{verse}"
        return result
    a_book, a_chapter, a_verse = aligned

    src_n = _chapter_verse_count(conn, src, book, chapter)
    tgt_n = _chapter_verse_count(conn, tgt, a_book, a_chapter)
    offset = versification.superscription_offset(src_n, tgt_n)
    if offset:
        result["verse_offset"] = offset
    a_verse -= offset

    row = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
        (tgt, a_book, a_chapter, a_verse),
    ).fetchone()
    result["target"] = f"{a_book} {a_chapter}:{a_verse}"
    result["text"] = row["text"] if row else None
    if row is None:
        result["warning"] = _empty_result_reason(conn, tgt, a_book)
    return result


# Which scheme each class's to_* references are numbered in, so a query reference can be aligned
# into it before lookup. Callers give a reference as an English Bible numbers it.
LINK_TARGET_SCHEME = {
    "quotation-greek": "lxx",
    "inner-biblical": "masoretic",
    "quotation-hebrew": "masoretic",
    "allusion-lemma": "lxx",
}


def lookup_links(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                  link_type: str | None = None, min_run: int = 0,
                  from_scheme: str = "english") -> dict[str, object]:
    """Every derived link at one reference, in both directions, grouped by class.

    The classes are not equivalent evidence and are never merged:

      quotation-greek   the New Testament quoting the Septuagint. A textual fact -- author and
                        translator were writing the same language.
      inner-biblical    the Hebrew Old Testament quoting itself. Equally textual, and with no
                        translation standing between the two sides.
      quotation-hebrew  a Hebrew New Testament matching the Hebrew Old Testament. CANDIDATES: those
                        are 19th-century translations, so a match means a Hebraist judged this to be
                        a quotation. It catches quotations the Greek misses, where the New Testament
                        follows the Hebrew rather than the Septuagint -- verify in Greek before
                        relying on one.
      allusion-lemma    shared RARE vocabulary between the Septuagint and the Greek New Testament,
                        with no shared phrasing required. Scored on `idf_overlap` (summed rarity),
                        not on alignment, which is 0 for this class by construction. It reaches
                        what quotation matching cannot -- Revelation 21:20's jewels against Ezekiel
                        28:13 -- and because the lemma files cover the deuterocanon it surfaces
                        allusions to Wisdom and Sirach that no cross-reference list carries.

    Grade by `longest_run`, the longest contiguous shared token run; 8 or more reads as quotation.
    `corroborated` means a cross-reference list -- openbible's, or the WEB translators' own
    footnotes -- independently names the same passage, and a
    strong run WITHOUT it is a link the tradition missed rather than a weak result.
    """
    wanted = [link_type] if link_type else list(LINK_TARGET_SCHEME)
    out: dict[str, list] = {}
    into: dict[str, list] = {}
    aligned_as: dict[str, str] = {}

    for kind in wanted:
        out[kind] = [dict(r) for r in conn.execute(
            "SELECT to_book, to_chapter, to_verse, to_english_chapter, to_english_verse, "
            "shared_ngrams, containment, longest_run, alignment, idf_overlap, corroborated "
            "FROM scripture_links "
            "WHERE link_type=? AND from_book=? AND from_chapter=? AND from_verse=? AND longest_run>=? "
            "ORDER BY alignment DESC, idf_overlap DESC, to_book, to_chapter, to_verse",
            (kind, book, chapter, verse, min_run))]

        target = versification.align(book, chapter, verse, from_scheme, LINK_TARGET_SCHEME[kind])
        if target is None:
            into[kind] = []
            continue
        aligned_as[kind] = f"{target[0]} {target[1]}:{target[2]}"
        into[kind] = [dict(r) for r in conn.execute(
            "SELECT from_book, from_chapter, from_verse, shared_ngrams, containment, longest_run, "
            "alignment, idf_overlap, corroborated FROM scripture_links "
            "WHERE link_type=? AND to_book=? AND to_chapter=? AND to_verse=? AND longest_run>=? "
            "ORDER BY alignment DESC, idf_overlap DESC, from_book, from_chapter, from_verse",
            (kind, *target, min_run))]

    return {
        "reference": f"{book} {chapter}:{verse}",
        "aligned_as": aligned_as,
        "quotation_run_threshold": quotations.QUOTATION_RUN,
        "links_from": {k: v for k, v in out.items() if v},
        "links_to": {k: v for k, v in into.items() if v},
    }


def lookup_interlinear(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                        from_scheme: str = "english") -> dict[str, object]:
    """Which original-language word each English word renders, from unfoldingWord's ULT alignment.

    The gap this fills: everything else here describes the two sides separately. `verse` gives a
    translation, `word` gives a lemma's occurrences, `syntax` gives clause roles -- but none of them
    says *this English word renders that Hebrew word*, which is the question a reader actually asks
    when a study makes something turn on a term.

    The mapping is many-to-many and is reported as it stands. Genesis 1:1's "the heavens" renders
    both אֵת and הַשָּׁמַיִם, because the object marker has no English of its own and the alignment
    encloses the phrase twice. Flattening that to one row per English phrase would invent a
    precision the data does not have, so both rows come back.

    Numbered in the English scheme, since ULT is an English translation; pass `from_scheme` if your
    reference is masoretic or lxx.
    """
    reference = versification.align(book, chapter, verse, from_scheme, "english")
    if reference is None:
        return {"reference": f"{book} {chapter}:{verse}", "rows": [],
                "warning": "no English-scheme counterpart for this reference"}
    e_book, e_chapter, e_verse = reference
    rows = [dict(r) for r in conn.execute(
        "SELECT english, content, lemma, strong, morph, occurrence FROM word_alignment "
        "WHERE book=? AND chapter=? AND verse=? ORDER BY rowid",
        (e_book, e_chapter, e_verse))]
    text = conn.execute(
        "SELECT text FROM verses WHERE work_id='uw-ult' AND book=? AND chapter=? AND verse=?",
        (e_book, e_chapter, e_verse)).fetchone()
    return {"reference": f"{e_book} {e_chapter}:{e_verse}", "text": text[0] if text else None,
            "rows": rows}


def lookup_grammar(conn: sqlite3.Connection, term: str, full: bool = False) -> list[dict[str, object]]:
    """Search the unfoldingWord Hebrew Grammar by slug, title or body.

    The lexicons in this database say what a word means. This says what a *form* does -- what a
    gentilic adjective is, what the definite article does to a construct chain -- which
    develop-bible-study's Phase 4 asks for ("grammar/syntax points that affect meaning") and which
    nothing here could previously answer without recall.

    Matched loosely on purpose: a morphology code like `Ncfsa` is not what anyone types, so slug and
    title are searched first and the body only if that finds nothing.
    """
    needle = f"%{term.lower().replace(' ', '_')}%"
    rows = [dict(r) for r in conn.execute(
        "SELECT slug, title, body FROM grammar_articles WHERE lower(slug) LIKE ? OR lower(title) LIKE ? "
        "ORDER BY length(slug)", (needle, f"%{term.lower()}%"))]
    if not rows:
        rows = [dict(r) for r in conn.execute(
            "SELECT slug, title, body FROM grammar_articles WHERE lower(body) LIKE ? ORDER BY length(slug) LIMIT 8",
            (f"%{term.lower()}%",))]
    if not full:
        for r in rows:
            body = str(r["body"])
            r["body"] = body[:600] + ("…" if len(body) > 600 else "")
    return rows


def lookup_variants(conn: sqlite3.Connection, book: str, chapter: int, verse: int | None = None,
                     from_scheme: str = "english") -> dict[str, object]:
    """Where the Dead Sea Scrolls read something the Masoretic text does not.

    Compared at lemma level, because the scrolls' fuller spelling and their habit of writing a
    prefix as a separate word make 99% of verses "differ" on surface forms and tell you nothing.
    Only fully-extant scroll words count: 46% of signs in this corpus are a modern editor's
    reconstruction, so a differing word that is not extant is damage rather than a reading.

    Reported one way only. A lemma the scroll has and the Masoretic lacks is a reading; a lemma the
    Masoretic has and the scroll lacks is nearly always a hole in the leather, and reporting it
    would invent omissions. Pass a whole chapter by leaving `verse` unset.

    This is what makes the claim that the scrolls side with the New Testament against the Masoretic
    checkable rather than something taken on report -- but check `extant_words` before leaning on
    any single row. A reading from a verse where six words survive carries less than one from
    twenty.
    """
    reference = versification.align(book, chapter, verse or 1, from_scheme, "masoretic")
    if reference is None:
        return {"reference": f"{book} {chapter}", "readings": [],
                "warning": "no Masoretic counterpart for this reference"}
    sql = ("SELECT work_id, book, chapter, verse, lemma, extant_words FROM dss_variants "
           "WHERE book=? AND chapter=?")
    params: list = [reference[0], reference[1]]
    if verse is not None:
        sql += " AND verse=?"
        params.append(reference[2])
    sql += " ORDER BY verse, extant_words DESC, work_id, lemma"
    rows = [dict(r) for r in conn.execute(sql, params)]
    return {
        "reference": f"{reference[0]} {reference[1]}" + (f":{reference[2]}" if verse else ""),
        "scheme": "masoretic",
        "readings": rows,
        "scrolls": sorted({r["work_id"] for r in rows}),
    }


# The witness to quote for each scheme when showing a link's original-language text.
ORIGINAL_WORK = {"lxx": "ebible-grcbrent", "masoretic": "morphhb-wlc", "english": "sblgnt"}
ENGLISH_WORK = "ebible-eng-web"


def _verse_text(conn: sqlite3.Connection, work_id: str, book: str, chapter: int,
                 verse: int) -> str | None:
    row = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
        (work_id, book, chapter, verse)).fetchone()
    return row["text"] if row else None


def _shared_span(left: str | None, right: str | None, greek: bool) -> str | None:
    """The longest run of words the two verses actually share, in their ORIGINAL spelling.

    The point of the whole exercise. A cross-reference list asserts that two verses are connected;
    this shows the reader the words on which the claim rests, so they can judge it rather than
    trust it. Matching runs on the normalised forms -- accents and pointing removed -- but the span
    returned is sliced out of the original text, because that is what a study quotes.
    """
    if not left or not right:
        return None
    normalise = quotations.normalise_greek if greek else quotations.normalise_hebrew
    left_words, right_words = left.split(), right.split()
    left_keys = [(normalise(w) or [""])[0] for w in left_words]
    right_keys = {(normalise(w) or [""])[0] for w in right_words}

    best_start = best_length = 0
    start = length = 0
    for index, key in enumerate(left_keys):
        if key and key in right_keys:
            if length == 0:
                start = index
            length += 1
            if length > best_length:
                best_start, best_length = start, length
        else:
            length = 0
    if best_length < 2:
        return None
    return " ".join(left_words[best_start:best_start + best_length])


def lookup_trace(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                  translation: str | None = None) -> dict[str, object]:
    """Everything the corpus knows about one verse, with the evidence for each connection shown.

    A cross-reference list gives you a list of references. This gives you, for each connection: how
    it was established, how strongly, the linked verse in its ORIGINAL language, an English
    rendering, and -- the part no reference list carries -- the words the two verses actually share.
    A reader can then judge the link instead of taking it on trust.

    Connections are grouped by how they were established and ordered by what that is worth, never
    merged into one relevance score:

      quotation-greek / inner-biblical   textual fact -- same language on both sides
      allusion-lemma                     shared rare vocabulary, no shared phrasing
      quotation-hebrew                   a 19th-century translator's judgement; verify in Greek
      cross-references                   crowd-assembled and inherited; leads, not evidence

    Where a link lands on an Old Testament verse the Dead Sea Scrolls also attest, any scroll
    reading the Masoretic lacks is attached to it -- so a study can see at once whether the verse a
    New Testament writer quoted is textually disputed.
    """
    scheme = _work_scheme(conn, _resolve_work_id(conn, translation))
    english_ref = versification.align(book, chapter, verse, scheme, "english") or (book, chapter, verse)
    result: dict[str, object] = {
        "reference": f"{book} {chapter}:{verse}",
        "english": _verse_text(conn, ENGLISH_WORK, *english_ref),
        "connections": [],
        "leads": [],
    }
    for work in ("sblgnt", "morphhb-wlc"):
        original = _verse_text(conn, work, book, chapter, verse)
        if original:
            result["original"] = original
            result["original_work"] = work
            break

    links = lookup_links(conn, book, chapter, verse, from_scheme=scheme)
    order = ["quotation-greek", "inner-biblical", "allusion-lemma", "quotation-hebrew"]
    for kind in order:
        for direction, rows in (("quotes", links["links_from"].get(kind, [])),
                                 ("quoted by", links["links_to"].get(kind, []))):
            for row in rows:
                if direction == "quotes":
                    target = (row["to_book"], row["to_chapter"], row["to_verse"])
                    target_scheme = LINK_TARGET_SCHEME[kind]
                    # use the stored english reference rather than re-aligning: it already carries
                    # the measured verse offset, and align() alone puts Hebrews 10:5's source at
                    # Psalm 40:7 when the verse it quotes is 40:6
                    stored_english = ((row["to_book"], row["to_english_chapter"],
                                       row["to_english_verse"])
                                      if row["to_english_chapter"] else None)
                else:
                    target = (row["from_book"], row["from_chapter"], row["from_verse"])
                    target_scheme = "english" if kind in ("quotation-greek", "allusion-lemma") else "masoretic"
                    stored_english = None
                greek = target_scheme in ("lxx", "english")
                original = _verse_text(conn, ORIGINAL_WORK[target_scheme], *target)
                to_english = stored_english or versification.align(*target, target_scheme, "english")
                entry = {
                    "method": kind,
                    "direction": direction,
                    "reference": f"{target[0]} {target[1]}:{target[2]}",
                    "scheme": target_scheme,
                    "english_reference": f"{to_english[0]} {to_english[1]}:{to_english[2]}" if to_english else None,
                    "original": original,
                    "english": _verse_text(conn, ENGLISH_WORK, *to_english) if to_english else None,
                    "shared": _shared_span(result.get("original"), original, greek),
                    "strength": (row["idf_overlap"] if kind == "allusion-lemma" else row["alignment"]),
                    "corroborated": bool(row["corroborated"]),
                }
                if to_english and target_scheme in ("lxx", "masoretic"):
                    masoretic = versification.align(*to_english, "english", "masoretic")
                    if masoretic:
                        entry["scroll_readings"] = [dict(r) for r in conn.execute(
                            "SELECT work_id, lemma, extant_words FROM dss_variants "
                            "WHERE book=? AND chapter=? AND verse=?", masoretic)]
                result["connections"].append(entry)

    for row in lookup_crossref(conn, *english_ref, min_votes=8, limit=12):
        result["leads"].append({
            "reference": f"{row['to_book']} {row['to_chapter']}:{row['to_verse_start']}",
            "votes": row["votes"],
            "english": _verse_text(conn, ENGLISH_WORK, row["to_book"], row["to_chapter"],
                                   row["to_verse_start"]),
        })
    return result


def lookup_alignment(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                      from_scheme: str = "english") -> dict[str, object]:
    """One reference expressed in every versification scheme in the database, with the works that
    use each. The check to run before comparing a Hebrew or Greek verse against an English one."""
    refs = _aligned_refs(conn, book, chapter, verse, from_scheme)
    schemes = {}
    for scheme in versification.SCHEMES:
        works = [r["work_id"] for r in conn.execute(
            "SELECT work_id FROM works WHERE versification=? ORDER BY work_id", (scheme,))]
        if not works:
            continue
        ref = refs.get(scheme)
        schemes[scheme] = {
            "reference": f"{ref[0]} {ref[1]}:{ref[2]}" if ref else None,
            "work_count": len(works),
            "example_works": works[:4],
        }
    return {"query": f"{book} {chapter}:{verse}", "from_scheme": from_scheme, "schemes": schemes}


def list_works(conn: sqlite3.Connection) -> list[dict]:
    """Every ingested source and its license tier -- check before citing."""
    rows = conn.execute(
        "SELECT work_id, title, license_tier, license FROM works ORDER BY license_tier, work_id"
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CLI -- formats the same data the functions above return.
# ---------------------------------------------------------------------------

def cmd_word(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    try:
        rows = lookup_word(conn, strongs=args.strongs, lemma=args.lemma, book=args.book)
    except ValueError as e:
        raise SystemExit(f"word: {e} (give --strongs or --lemma)")
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print(f"{r['work_id']:22} {r['book']} {r['chapter']}:{r['verse']:<4} {r['surface_form'] or '-':12} "
              f"lemma={r['lemma'] or '-':14} strongs={r['strongs_id'] or '-':8} domain={r['domain_code'] or '-':10} {r['gloss'] or ''}")


def cmd_concordance(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = lookup_concordance(conn, args.strongs, book=args.book, work_id=args.work_id)
    if not rows:
        print("No matches.")
        return
    last_book = None
    for r in rows:
        if r["book"] != last_book:
            print(f"\n-- {r['book']} ({r['work_id']}) --")
            last_book = r["book"]
        print(f"  {r['chapter']}:{r['verse']:<4} {r['gloss'] or ''}")
    print(f"\n{len(rows)} occurrence(s).")


def cmd_domain(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = lookup_domain(conn, args.code)
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print(f"{r['work_id']:22} {r['lemma'] or '-':16} strongs={r['strongs_id'] or '-':8} {r['gloss'] or ''}")


def cmd_verse(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    result = lookup_verse(conn, args.book, args.chapter, args.verse, translation=args.translation)
    print(f"{result['book']} {result['chapter']}:{result['verse']} ({result['work_id']})")
    print(f"  {result['text'] or '(not found for this work_id)'}")
    if result.get("warning"):
        print(f"  WARNING: {result['warning']}")
    # lookup_verse resolves this so the morphology below comes from the right verse, but it was
    # never shown. Worth printing: it is the only signal that the same reference names a different
    # verse in another work here (uw-uhb is numbered the ULT's way, morphhb-wlc the Hebrew way),
    # which otherwise fails silently when two Hebrew works are compared by reference.
    if result.get("aligned_references"):
        others = ", ".join(f"{s} {r}" for s, r in sorted(result["aligned_references"].items()))
        print(f"  NOTE: this verse is numbered differently elsewhere -- {others}. "
              f"Works in another scheme must be queried at their own number.")
    if result.get("stated_hebrew_reference"):
        stated = result["stated_hebrew_reference"]
        inferred = (result.get("aligned_references") or {}).get("masoretic")
        if inferred and inferred != stated:
            print(f"  NOTE: UHB states the Hebrew reference is {stated} "
                  f"({result['stated_hebrew_source']}), against {inferred} from the scheme map. "
                  f"Prefer the stated one.")
        elif not inferred:
            print(f"  NOTE: UHB states the Hebrew reference is {stated} "
                  f"({result['stated_hebrew_source']}); the scheme map reports no shift.")

    last_work = None
    for r in result["morphology"]:
        if r["work_id"] != last_work:
            print(f"\n  -- {r['work_id']} --")
            last_work = r["work_id"]
        print(f"    {r['word_position']:2} {r['surface_form'] or '-':12} lemma={r['lemma'] or '-':14} "
              f"strongs={r['strongs_id'] or '-':8} domain={r['domain_code'] or '-':10} {r['gloss'] or ''}")

    for n in result["notes"]:
        print(f"\n  -- note ({n['work_id']}) --\n  {n['text']}")

    print(
        "\n  (For commercial study-Bible commentary -- ESV Study Bible, Cultural Backgrounds "
        "Study Bible, etc. -- query study-notes.db separately; see references/README.md. "
        "That data is quotation-only and deliberately not in this database.)"
    )


ROLE_LABELS = {
    "s": "subject", "v": "verb", "o": "object", "io": "indirect-obj",
    "adv": "adverbial", "p": "predicate", "vc": "copula",
}


def cmd_syntax(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    result = lookup_syntax(conn, args.book, args.chapter, args.verse, work_id=args.work_id)
    print(f"{result['book']} {result['chapter']}:{result['verse']} -- syntax")
    if result.get("warning"):
        print(f"  WARNING: {result['warning']}")
        return

    last_work = None
    for w in result["words"]:
        if w["work_id"] != last_work:
            print(f"\n  -- {w['work_id']} --")
            last_work = w["work_id"]
        role = ROLE_LABELS.get(w["syntactic_role"], w["syntactic_role"]) or "-"
        bits = f"class={w['word_class'] or '-':7} role={role:12}"
        if w["sub_type"]:
            bits += f" type={w['sub_type']:18}"
        if w["state"]:
            bits += f" state={w['state']}"
        print(f"    {w['word_position']:2} {w['surface_form'] or '-':14} {bits}  {w['gloss'] or ''}")
        for label in ("subject", "refers_to"):
            for t in w.get(label) or []:
                print(f"       -> {label}: {t['surface_form'] or '-'} ({t['gloss'] or '-'}) "
                      f"@ {t['book']} {t['chapter']}:{t['verse']}")
            if w.get(f"{label}_unresolved"):
                print(f"       -> {label}: {w[f'{label}_unresolved']} pointer(s) outside "
                      "the annotated corpus")


def cmd_passage(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    result = lookup_passage(
        conn, args.book, args.chapter, args.verse_start, args.verse_end,
        end_chapter=args.end_chapter, translation=args.translation, include_notes=args.notes,
    )
    end_chapter = result["end_chapter"]
    if not result["verses"]:
        print(f"No verses found for {args.book} {args.chapter}:{args.verse_start}-{end_chapter}:{args.verse_end} ({result['work_id']}).")
        print(f"  WARNING: {result['warning']}")
        return
    print(f"{args.book} {args.chapter}:{args.verse_start}-{end_chapter}:{args.verse_end} ({result['work_id']})")
    last_chapter = None
    for r in result["verses"]:
        if r["chapter"] != last_chapter:
            print(f"\n  -- ch. {r['chapter']} --")
            last_chapter = r["chapter"]
        print(f"  {r['verse']:<4} {r['text']}")

    for n in result.get("notes", []):
        print(f"\n  -- note {n['chapter']}:{n['verse']} ({n['work_id']}) --\n  {n['text']}")


METHOD_LABEL = {
    "quotation-greek": ("quotation", "Greek on both sides -- a textual fact"),
    "inner-biblical": ("quotation", "Hebrew on both sides -- a textual fact"),
    "allusion-lemma": ("allusion", "shared rare vocabulary, no shared phrasing"),
    "quotation-hebrew": ("candidate", "a 19th-century Hebrew NT's judgement -- verify in Greek"),
}


def _wrap(text: str, width: int = 92, indent: str = "        ") -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width, initial_indent=indent, subsequent_indent=indent))


def cmd_trace(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    r = lookup_trace(conn, args.book, args.chapter, args.verse, args.translation)
    print(f"\n{r['reference']}")
    if r.get("original"):
        print(_wrap(r["original"], indent="    "))
    if r.get("english"):
        print(_wrap(r["english"], indent="    "))

    if not r["connections"]:
        print("\n  no derived connection at this verse")
    seen_method = None
    for c in r["connections"]:
        kind, why = METHOD_LABEL[c["method"]]
        if c["method"] != seen_method:
            seen_method = c["method"]
            print(f"\n  ── {kind.upper()}  ({why})")
        verb = {"quotation-greek": ("quotes", "quoted by"),
                "inner-biblical": ("quotes", "quoted by"),
                "allusion-lemma": ("echoes", "echoed by"),
                "quotation-hebrew": ("may quote", "may be quoted by")}[c["method"]]
        direction = verb[0] if c["direction"] == "quotes" else verb[1]
        eng = f" = {c['english_reference']}" if c["english_reference"] != c["reference"] else ""
        mark = "corroborated" if c["corroborated"] else "not in any reference list"
        print(f"\n    {direction} {c['reference']}{eng}   strength {c['strength']}  [{mark}]")
        if c["shared"]:
            print(f"        shared: {c['shared']}")
        if c["original"]:
            print(_wrap(c["original"]))
        if c["english"]:
            print(_wrap(c["english"]))
        for v in c.get("scroll_readings") or []:
            print(f"        scroll variant: {v['work_id']} reads {v['lemma']} "
                  f"({v['extant_words']} words of that verse survive)")

    if args.leads and r["leads"]:
        print("\n  ── LEADS  (crowd-assembled cross-references -- worth chasing, not evidence)")
        for lead in r["leads"]:
            print(f"    {lead['reference']:14} {lead['votes']:4} votes")


def cmd_interlinear(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    r = lookup_interlinear(conn, args.book, args.chapter, args.verse)
    print(f"{r['reference']} (ULT, aligned to UHB/UGNT)\n")
    if r.get("warning"):
        print(f"  {r['warning']}")
        return
    if r.get("text"):
        print(f"  {r['text']}\n")
    if not r["rows"]:
        print("  no alignment recorded for this verse")
        return
    for row in r["rows"]:
        strong = row["strong"] or ""
        print(f"  {str(row['english'])[:34]:36} <- {row['content']}")
        print(f"  {'':36}    {str(row['lemma'] or ''):16} {strong:12} {row['morph'] or ''}")


def cmd_grammar(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = lookup_grammar(conn, args.term, full=args.full)
    if not rows:
        print(f"no grammar article matching {args.term!r}")
        return
    for row in rows[: 1 if args.full else 6]:
        print(f"\n  {row['title']}  ({row['slug']})")
        for line in str(row["body"]).splitlines():
            if line.strip():
                print(f"    {line}")


def cmd_variants(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    r = lookup_variants(conn, args.book, args.chapter, args.verse)
    print(f"{r['reference']} (masoretic numbering)\n")
    if not r["readings"]:
        print("  no scroll reading here that the Masoretic lacks")
        if r.get("warning"):
            print(f"  {r['warning']}")
        return
    current = None
    for row in r["readings"]:
        ref = f"{row['book']} {row['chapter']}:{row['verse']}"
        if ref != current:
            current = ref
            print(f"  {ref}")
        print(f"     {row['work_id']:14} reads {row['lemma']:14} "
              f"({row['extant_words']} words of the verse survive)")
    print("\n  lemma-level, fully-extant scroll words only; weigh by how much of the verse survives")


def cmd_quotations(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    r = lookup_links(conn, args.book, args.chapter, args.verse,
                     link_type=args.type, min_run=args.min_run)
    print(f"{r['reference']}\n")
    labels = {"quotation-greek": "quotes (Greek, New Testament -> Septuagint)",
              "inner-biblical": "quotes (Hebrew, within the Old Testament)",
              "quotation-hebrew": "matches a Hebrew New Testament -- CANDIDATES, verify in Greek",
              "allusion-lemma": "shares rare vocabulary with (allusion, not quotation)"}
    for kind, rows in r["links_from"].items():
        print(f"  {labels[kind]}:")
        for q in rows:
            eng = (f" = {q['to_book']} {q['to_english_chapter']}:{q['to_english_verse']}"
                   if q["to_english_chapter"] else "")
            strength = (f"rarity={q['idf_overlap']:5.1f}" if kind == "allusion-lemma"
                        else f"align={q['alignment']:3d} run={q['longest_run']:2d}")
            print(f"   {'*' if q['corroborated'] else ' '} {q['to_book']} {q['to_chapter']}:"
                  f"{q['to_verse']}{eng}   {strength} containment={q['containment']:.2f}")
    for kind, rows in r["links_to"].items():
        print(f"  quoted by ({kind}):")
        for q in rows:
            print(f"   {'*' if q['corroborated'] else ' '} {q['from_book']} {q['from_chapter']}:"
                  f"{q['from_verse']}   align={q['alignment']:3d} run={q['longest_run']:2d}"
                  f" containment={q['containment']:.2f}")
    if not r["links_from"] and not r["links_to"]:
        print("  no link found")
    else:
        print("\n  * corroborated by an independent cross-reference list")


def cmd_parallel(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    r = lookup_parallel(conn, args.book, args.chapter, args.verse, args.source, args.target)
    shift = f"  (verse offset {r['verse_offset']:+d})" if "verse_offset" in r else ""
    print(f"{r['source']} ({r['source_work']})  ->  {r.get('target', '--')} ({r['target_work']}){shift}\n")
    if r.get("text"):
        print(f"  {r['text']}")
    if r.get("warning"):
        print(f"  warning: {r['warning']}")


def cmd_align(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    result = lookup_alignment(conn, args.book, args.chapter, args.verse, args.from_scheme)
    print(f"{result['query']} (given as {result['from_scheme']})\n")
    for scheme, info in result["schemes"].items():
        ref = info["reference"] or "-- no counterpart --"
        print(f"  {scheme:<10} {ref:<16} {info['work_count']} works, e.g. {', '.join(info['example_works'])}")


def cmd_crossref(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = lookup_crossref(conn, args.book, args.chapter, args.verse, min_votes=args.min_votes,
                           limit=args.limit, from_scheme=args.from_scheme)
    if not rows:
        print("No cross-references found.")
        return
    for r in rows:
        verse_range = (
            f"{r['to_verse_start']}" if r["to_verse_start"] == r["to_verse_end"]
            else f"{r['to_verse_start']}-{r['to_verse_end']}"
        )
        print(f"{r['to_book']} {r['to_chapter']}:{verse_range:8} votes={r['votes']:<4} ({r['work_id']})")


def cmd_works(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    for r in list_works(conn):
        print(f"{r['license_tier']:14} {r['work_id']:30} {r['title'] or ''}  ({r['license'] or 'no license recorded'})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_word = sub.add_parser("word", help="Look up a Strong's number or lemma")
    p_word.add_argument("--strongs", help="e.g. G680 or H5060 (G/H prefix optional)")
    p_word.add_argument("--lemma", help="exact lemma match, e.g. σῴζω")
    p_word.add_argument("--book", help="restrict to one OSIS book code, e.g. Mark")
    p_word.set_defaults(func=cmd_word)

    p_conc = sub.add_parser("concordance", help="Every occurrence of a Strong's number, grouped by book")
    p_conc.add_argument("strongs", help="e.g. G4982 or H2930")
    p_conc.add_argument("--book", help="restrict to one OSIS book code")
    p_conc.add_argument("--work-id", help="restrict to one source, e.g. macula-greek-sblgnt")
    p_conc.set_defaults(func=cmd_concordance)

    p_dom = sub.add_parser("domain", help="Every word sharing a Louw-Nida/SDBH domain code")
    p_dom.add_argument("code", help="e.g. 23.136")
    p_dom.set_defaults(func=cmd_domain)

    p_verse = sub.add_parser("verse", help="Translation text + morphology + notes for one verse")
    p_verse.add_argument("book", help="OSIS book code, e.g. Mark")
    p_verse.add_argument("chapter", type=int)
    p_verse.add_argument("verse", type=int)
    p_verse.add_argument("--translation", help="e.g. KJV, ASV, ebible-heb (default: WEB)")
    p_verse.set_defaults(func=cmd_verse)

    p_syntax = sub.add_parser(
        "syntax", help="Clause-level syntax + coreference for one verse (MACULA Hebrew/Greek only)")
    p_syntax.add_argument("book", help="OSIS book code, e.g. Mark")
    p_syntax.add_argument("chapter", type=int)
    p_syntax.add_argument("verse", type=int)
    p_syntax.add_argument("--work-id", dest="work_id",
                          help="restrict to one corpus, e.g. macula-greek-sblgnt")
    p_syntax.set_defaults(func=cmd_syntax)

    p_passage = sub.add_parser("passage", help="Translation text for a verse range")
    p_passage.add_argument("book", help="OSIS book code, e.g. Mark")
    p_passage.add_argument("chapter", type=int, help="start chapter")
    p_passage.add_argument("verse_start", type=int)
    p_passage.add_argument("verse_end", type=int, help="end verse (in --end-chapter, if given, else in `chapter`)")
    p_passage.add_argument("--end-chapter", type=int, help="if the passage spans chapters (default: same as `chapter`)")
    p_passage.add_argument("--translation", help="e.g. KJV, ASV, ebible-heb (default: WEB)")
    p_passage.add_argument("--notes", action="store_true", help="include translator/study notes in range")
    p_passage.set_defaults(func=cmd_passage)

    p_xref = sub.add_parser("crossref", help="Cross-references for one verse, highest-voted first")
    p_xref.add_argument("book", help="OSIS book code, e.g. Mark")
    p_xref.add_argument("chapter", type=int)
    p_xref.add_argument("verse", type=int)
    p_xref.add_argument("--min-votes", type=int, default=0, help="filter out low-confidence links")
    p_xref.add_argument("--limit", type=int, default=20)
    p_xref.add_argument("--from-scheme", default="english", choices=versification.SCHEMES,
                        help="scheme the reference is given in (default: english)")
    p_xref.set_defaults(func=cmd_crossref)

    p_trace = sub.add_parser("trace", help="Everything linking to a verse, with the evidence shown")
    p_trace.add_argument("book", help="OSIS book code, e.g. Heb")
    p_trace.add_argument("chapter", type=int)
    p_trace.add_argument("verse", type=int)
    p_trace.add_argument("--translation", help="scheme the reference is given in (default: English)")
    p_trace.add_argument("--leads", action="store_true",
                         help="also show crowd-assembled cross-references")
    p_trace.set_defaults(func=cmd_trace)

    p_inter = sub.add_parser("interlinear", help="Which original word each English word renders (ULT alignment)")
    p_inter.add_argument("book", help="OSIS book code, e.g. Gen")
    p_inter.add_argument("chapter", type=int)
    p_inter.add_argument("verse", type=int)
    p_inter.set_defaults(func=cmd_interlinear)

    p_gram = sub.add_parser("grammar", help="Hebrew grammar articles (unfoldingWord UHG)")
    p_gram.add_argument("term", help="a slug, title or phrase -- e.g. gentilic, construct, dual")
    p_gram.add_argument("--full", action="store_true", help="print the first match in full")
    p_gram.set_defaults(func=cmd_grammar)

    p_var = sub.add_parser("variants", help="Scroll readings the Masoretic text does not carry")
    p_var.add_argument("book", help="OSIS book code, e.g. Isa")
    p_var.add_argument("chapter", type=int)
    p_var.add_argument("verse", type=int, nargs="?", help="omit for the whole chapter")
    p_var.set_defaults(func=cmd_variants)

    p_quot = sub.add_parser("quotations", help="What this verse quotes, and who quotes it")
    p_quot.add_argument("book", help="OSIS book code, e.g. Heb")
    p_quot.add_argument("chapter", type=int)
    p_quot.add_argument("verse", type=int)
    p_quot.add_argument("--min-run", type=int, default=0,
                        help="drop pairs below this verbatim token run (8 = quotation)")
    p_quot.add_argument("--type", choices=sorted(LINK_TARGET_SCHEME),
                        help="restrict to one link class (default: all three)")
    p_quot.set_defaults(func=cmd_quotations)

    p_par = sub.add_parser("parallel", help="The same verse in another work, chapter- and verse-aligned")
    p_par.add_argument("book", help="OSIS book code, e.g. Ps")
    p_par.add_argument("chapter", type=int)
    p_par.add_argument("verse", type=int)
    p_par.add_argument("--source", help="translation the reference is given in (default: WEB)")
    p_par.add_argument("--target", required=True, help="translation to find it in")
    p_par.set_defaults(func=cmd_parallel)

    p_align = sub.add_parser("align", help="One reference as each versification scheme numbers it")
    p_align.add_argument("book", help="OSIS book code, e.g. Joel")
    p_align.add_argument("chapter", type=int)
    p_align.add_argument("verse", type=int)
    p_align.add_argument("--from-scheme", default="english", choices=versification.SCHEMES,
                         help="scheme the reference is given in (default: english)")
    p_align.set_defaults(func=cmd_align)

    p_works = sub.add_parser("works", help="List every ingested source and its license tier")
    p_works.set_defaults(func=cmd_works)

    args = parser.parse_args()
    try:
        conn = connect()
    except FileNotFoundError as e:
        raise SystemExit(str(e))
    try:
        args.func(conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
