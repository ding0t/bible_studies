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


def _resolve_work_id(translation: str | None) -> str:
    if not translation:
        return DEFAULT_TRANSLATION_WORK_ID
    if translation.startswith(("scrollmapper-", "ebible-")):
        return translation
    return f"scrollmapper-{translation}"


# ---------------------------------------------------------------------------
# Lookup functions -- shared by the CLI below and mcp_server.py.
# ---------------------------------------------------------------------------

def _empty_result_reason(conn: sqlite3.Connection, work_id: str, book: str) -> str:
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
    return f"{book} exists in {work_id}, but not at the chapter/verse given -- check the reference."

def lookup_word(conn: sqlite3.Connection, strongs: str | None = None, lemma: str | None = None,
                 book: str | None = None) -> list[dict]:
    """Every occurrence of a Strong's number or lemma, across the Greek/Hebrew morphology sources."""
    if not strongs and not lemma:
        raise ValueError("word lookup needs strongs or lemma")
    where, params = [], []
    if strongs:
        where.append("strongs_id = ?")
        params.append(strongs.lstrip("GH"))
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
    if book:
        where.append("book = ?")
        params.append(book)
    if work_id:
        where.append("work_id = ?")
        params.append(work_id)
    rows = conn.execute(
        f"SELECT work_id, book, chapter, verse, gloss FROM morphology WHERE {' AND '.join(where)} "
        f"ORDER BY work_id, book, chapter, verse",
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


def lookup_verse(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                  translation: str | None = None) -> dict[str, object]:
    """Translation text plus every morphology row and note for one verse -- the single most
    common per-verse lookup when drafting a study."""
    work_id = _resolve_work_id(translation)
    verse_row = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
        (work_id, book, chapter, verse),
    ).fetchone()
    morph_rows = conn.execute(
        "SELECT work_id, word_position, surface_form, lemma, strongs_id, gloss, domain_code FROM morphology "
        "WHERE book=? AND chapter=? AND verse=? ORDER BY work_id, word_position",
        (book, chapter, verse),
    ).fetchall()
    notes = conn.execute(
        "SELECT work_id, text FROM notes WHERE book=? AND chapter=? AND verse=?",
        (book, chapter, verse),
    ).fetchall()
    result = {
        "book": book, "chapter": chapter, "verse": verse, "work_id": work_id,
        "text": verse_row["text"] if verse_row else None,
        "morphology": [dict(r) for r in morph_rows],
        "notes": [dict(r) for r in notes],
    }
    if verse_row is None:
        result["warning"] = _empty_result_reason(conn, work_id, book)
    return result


def lookup_passage(conn: sqlite3.Connection, book: str, chapter: int, verse_start: int, verse_end: int,
                    end_chapter: int | None = None, translation: str | None = None,
                    include_notes: bool = False) -> dict[str, object]:
    """Translation text for a verse range -- for studying a pericope without N separate
    verse lookups. Text only unless include_notes is set, to keep the common case cheap."""
    end_chapter = end_chapter or chapter
    work_id = _resolve_work_id(translation)
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
                     min_votes: int = 0, limit: int = 20) -> list[dict]:
    """Cross-references for one verse (OpenBible.info / TSK-style data), highest-voted
    first -- the Phase 6 'gather cross-references' step without hand SQL."""
    rows = conn.execute(
        "SELECT DISTINCT to_book, to_chapter, to_verse_start, to_verse_end, votes, work_id "
        "FROM cross_references WHERE from_book=? AND from_chapter=? AND from_verse=? AND votes >= ? "
        "ORDER BY votes DESC LIMIT ?",
        (book, chapter, verse, min_votes, limit),
    ).fetchall()
    return [dict(r) for r in rows]


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


def cmd_crossref(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rows = lookup_crossref(conn, args.book, args.chapter, args.verse, min_votes=args.min_votes, limit=args.limit)
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
    p_xref.set_defaults(func=cmd_crossref)

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
