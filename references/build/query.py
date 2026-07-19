"""Convenience query CLI for bible-text.db -- built so a study session doesn't have
to hand-write SQL for the common lookups every time. Read-only; build.py owns writes.

Examples:
    uv run python query.py word --strongs G680
    uv run python query.py word --lemma dikaiosune
    uv run python query.py concordance G4982 --book Mark
    uv run python query.py domain 23.136
    uv run python query.py verse Mark 5 27
    uv run python query.py verse Mark 5 27 --translation KJV
    uv run python query.py works
"""
import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "out" / "bible-text.db"
DEFAULT_TRANSLATION_WORK_ID = "ebible-eng-web"  # WEB: public domain, full Bible, no permission caveats


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise SystemExit(f"{DB_PATH} not found -- run `uv run python build.py` first.")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_word(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """Every occurrence of a Strong's number or lemma, across the Greek/Hebrew morphology sources."""
    where, params = [], []
    if args.strongs:
        where.append("strongs_id = ?")
        params.append(args.strongs.lstrip("GH"))
    if args.lemma:
        where.append("lemma = ?")
        params.append(args.lemma)
    if not where:
        raise SystemExit("word: give --strongs or --lemma")
    if args.book:
        where.append("book = ?")
        params.append(args.book)
    rows = conn.execute(
        f"SELECT work_id, book, chapter, verse, surface_form, lemma, strongs_id, gloss, domain_code "
        f"FROM morphology WHERE {' AND '.join(where)} ORDER BY work_id, book, chapter, verse",
        params,
    ).fetchall()
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print(f"{r['work_id']:22} {r['book']} {r['chapter']}:{r['verse']:<4} {r['surface_form'] or '-':12} "
              f"lemma={r['lemma'] or '-':14} strongs={r['strongs_id'] or '-':8} domain={r['domain_code'] or '-':10} {r['gloss'] or ''}")


def cmd_concordance(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """Every occurrence of one Strong's number grouped by book -- the word-study-method.md
    'concord across the corpus' step, without hand-writing the GROUP BY each time."""
    strongs = args.strongs.lstrip("GH")
    where, params = ["strongs_id = ?"], [strongs]
    if args.book:
        where.append("book = ?")
        params.append(args.book)
    if args.work_id:
        where.append("work_id = ?")
        params.append(args.work_id)
    rows = conn.execute(
        f"SELECT work_id, book, chapter, verse, gloss FROM morphology WHERE {' AND '.join(where)} "
        f"ORDER BY work_id, book, chapter, verse",
        params,
    ).fetchall()
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
    """Every word sharing a Louw-Nida (Greek) or SDBH lexdomain (Hebrew) code -- the semantic-domain
    cross-check step in word-study-method.md."""
    rows = conn.execute(
        "SELECT DISTINCT work_id, lemma, gloss, strongs_id FROM morphology "
        "WHERE domain_code = ? OR domain_code LIKE ? OR domain_code LIKE ? "
        "ORDER BY work_id, lemma",
        (args.code, f"{args.code} %", f"% {args.code}%"),
    ).fetchall()
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print(f"{r['work_id']:22} {r['lemma'] or '-':16} strongs={r['strongs_id'] or '-':8} {r['gloss'] or ''}")


def cmd_verse(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """Translation text plus every morphology row for one verse -- the single most common
    per-verse lookup when drafting a study."""
    work_id = args.translation and (
        args.translation if args.translation.startswith(("scrollmapper-", "ebible-")) else f"scrollmapper-{args.translation}"
    ) or DEFAULT_TRANSLATION_WORK_ID
    verse_row = conn.execute(
        "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
        (work_id, args.book, args.chapter, args.verse),
    ).fetchone()
    print(f"{args.book} {args.chapter}:{args.verse} ({work_id})")
    print(f"  {verse_row['text'] if verse_row else '(not found for this work_id)'}")

    morph_rows = conn.execute(
        "SELECT work_id, word_position, surface_form, lemma, strongs_id, gloss, domain_code FROM morphology "
        "WHERE book=? AND chapter=? AND verse=? ORDER BY work_id, word_position",
        (args.book, args.chapter, args.verse),
    ).fetchall()
    last_work = None
    for r in morph_rows:
        if r["work_id"] != last_work:
            print(f"\n  -- {r['work_id']} --")
            last_work = r["work_id"]
        print(f"    {r['word_position']:2} {r['surface_form'] or '-':12} lemma={r['lemma'] or '-':14} "
              f"strongs={r['strongs_id'] or '-':8} domain={r['domain_code'] or '-':10} {r['gloss'] or ''}")

    notes = conn.execute(
        "SELECT work_id, text FROM notes WHERE book=? AND chapter=? AND verse=?",
        (args.book, args.chapter, args.verse),
    ).fetchall()
    for n in notes:
        print(f"\n  -- note ({n['work_id']}) --\n  {n['text']}")

    print(
        "\n  (For commercial study-Bible commentary -- ESV Study Bible, Cultural Backgrounds "
        "Study Bible, etc. -- query study-notes.db separately; see references/README.md. "
        "That data is quotation-only and deliberately not in this database.)"
    )


def cmd_works(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """List every ingested source and its license tier -- check before citing."""
    rows = conn.execute("SELECT work_id, title, license_tier, license FROM works ORDER BY license_tier, work_id").fetchall()
    for r in rows:
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

    p_works = sub.add_parser("works", help="List every ingested source and its license tier")
    p_works.set_defaults(func=cmd_works)

    args = parser.parse_args()
    conn = connect()
    try:
        args.func(conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
