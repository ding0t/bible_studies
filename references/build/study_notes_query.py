#!/usr/bin/env python3
"""Query library + CLI for study-notes.db (commercial study-Bible commentary, quotation-only).

Same contract as query.py: every lookup is a plain `lookup_*` function taking a connection and
returning JSON-friendly data, with no printing and no argparse. `main()` is a thin CLI over those
functions; `mcp_server.py` imports the same functions and wraps them as MCP tools. Two front ends,
one source of truth. Read-only -- build_study_notes.py owns writes.

Why this module exists, recorded because the reasoning is load-bearing
----------------------------------------------------------------------
study-notes.db had no query library and therefore no MCP tools, so agents needing an ESV note
hand-rolled sqlite3 against it. It lives on a network share (see media_root.py), and a hand-rolled
query is overwhelmingly likely to be a survey query -- `count(*)`, `SELECT DISTINCT work_id` --
which full-scans a 116 MB file across SMB. Measured on 2026-09-18: `count(distinct work_id) FROM
verses` took **97 seconds**, `count(*) FROM notes` took 64. The indexed form of the same lookup
takes **0.1 s**. One agent read that latency as the volume being "hung", reported it unavailable,
and proposed drafting from memory instead -- which is the failure this repo already has a scar
from (a study rendered John 6:34 as "Lord, give us this bread"; the ESV reads "Sir").

So the point of this module is not convenience. It is that the only reachable query shapes are the
indexed ones, and that an absent volume reports itself as absent instead of looking slow.

    idx_sn_verses_ref (book, chapter, verse)
    idx_notes_ref     (book, chapter, verse_start, verse_end)
    idx_intro_book    (book)

`_require_indexed()` enforces that on the two large tables. `introductions` (213 rows) and
`topical_articles` (1,992) are small enough that a scan is cheap, so they are exempt -- and per
this repo's rule that an exemption carries its justification or it is a hole, that is the
justification, restated at each call site.

Licence discipline
------------------
Every work here is `quotation-only`. That tier governs how much may be **reproduced in a committed
file** -- a sentence or two with attribution -- and NOT whether it may be looked up. AGENTS.md is
explicit about this, and getting it backwards would defeat the module's main purpose: verifying a
quotation requires reading the whole verse.

So the caps below are deliberately generous enough to verify against, and the discipline is
carried by `quote_allowance` and `attribution` riding on every returned record rather than by
withholding text. Truncation, when it happens, is always declared (`truncated`, `full_length`) so
a caller can never mistake a clipped note for a whole one.

NOTE_CHARS default of 1500 keeps the great majority of notes whole (mean note length 267 chars),
while bounding the outliers -- the longest note in the database is 18,405 characters.

CLI examples:
    uv run python study_notes_query.py verse John 6 34 --work esv-study-bible
    uv run python study_notes_query.py note John 6 34
    uv run python study_notes_query.py intro Matt
    uv run python study_notes_query.py article "Passover"
    uv run python study_notes_query.py works
    uv run python study_notes_query.py status
"""
import argparse
import sqlite3

import media_root
import source_catalog
from book_map import NUM_TO_OSIS

_ALL_OSIS_BOOKS = set(NUM_TO_OSIS.values())
_DB = "study-notes"

# Reproduction limit for the quotation-only tier, applied per record. See the module docstring:
# this bounds outliers so a single call cannot return an entire chapter's commentary, and it is
# NOT a restriction on lookup -- verse text is never truncated, because verifying a quotation
# against a clipped verse is worse than not verifying it.
NOTE_CHARS = 1500
MAX_ROWS = 50

# Tier and its reproduction limit come from references/sources.toml, so this module cannot drift
# from what the catalog says the licence permits. See source_catalog.quote_allowance().
DEFAULT_TIER = source_catalog.database(_DB)["default_tier"]
QUOTE_ALLOWANCE = source_catalog.quote_allowance(DEFAULT_TIER)


class SourceUnavailable(Exception):
    """The database or the volume holding it is not reachable.

    Carries a remedy, because the failure this module exists to prevent was an agent guessing at
    the cause of an unreachable source rather than being told it.
    """

    def __init__(self, reason: str, remedy: str):
        super().__init__(reason)
        self.reason = reason
        self.remedy = remedy

    def as_dict(self) -> dict:
        return {"available": False, "reason": self.reason, "remedy": self.remedy}


def db_path():
    return source_catalog.database(_DB)["resolved_path"]


def availability() -> dict:
    """Whether the database is reachable, as data rather than as an exception.

    Call this instead of inferring availability from a slow or failed query -- the distinction
    between 'absent' and 'slow' is exactly what was lost in the incident above.
    """
    root = media_root.media_root()
    path = db_path()
    if not root.is_dir():
        return {
            "available": False,
            "reason": f"External reference volume not mounted: {root}",
            "remedy": "Mount it, or point $BIBLE_MEDIA_ROOT at where it actually is.",
            "path": str(path),
        }
    if not path.is_file():
        return {
            "available": False,
            "reason": f"study-notes.db not found at {path}",
            "remedy": "Build it: `uv run python build_study_notes.py` from references/build.",
            "path": str(path),
        }
    return {"available": True, "path": str(path)}


def connect() -> sqlite3.Connection:
    """Open a read-only connection, raising SourceUnavailable (not SystemExit) so the MCP server,
    a test or another script can turn it into a structured answer.

    `immutable=1` rather than `mode=ro`: it promises the file will not change underneath us, which
    lets SQLite skip locking and the WAL/shm sidecar files entirely. On a network share that is
    both faster (measured 0.07s vs 0.11s on an indexed lookup) and avoids writing lock files onto
    a read-only mount -- the review skill already calls this form mandatory under the sandbox.
    """
    status = availability()
    if not status["available"]:
        raise SourceUnavailable(status["reason"], status["remedy"])
    mode = source_catalog.database(_DB)["connect"]  # 'immutable' per the catalog
    conn = sqlite3.connect(f"file:{db_path()}?{'immutable=1' if mode == 'immutable' else 'mode=ro'}",
                           uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _require_indexed(book: str, chapter: int | None = None, *, need_chapter: bool = True) -> None:
    """Refuse a query that would scan `notes` or `verses`.

    Raises ValueError naming the index that should have been used, rather than running a query
    that takes a minute and reads as a hung volume.
    """
    if not book:
        raise ValueError(
            "book is required -- an unfiltered query scans the whole table (~60-100s over SMB). "
            "Use idx_notes_ref / idx_sn_verses_ref by passing at least book and chapter."
        )
    if book not in _ALL_OSIS_BOOKS:
        raise ValueError(
            f"{book!r} is not an OSIS book code. study-notes.db uses the same codes as "
            f"bible-text.db (Matt, 1Cor, Ps, Joel)."
        )
    if need_chapter and chapter is None:
        raise ValueError(
            f"chapter is required for {book} -- book alone still scans a large slice. "
            f"Pass a chapter to use the index."
        )


def _work_meta(conn: sqlite3.Connection) -> dict[str, dict]:
    return {
        r["work_id"]: {
            "title": r["title"],
            "publisher": r["publisher"],
            "attribution": r["attribution"],
            "tier": r["license_tier"],
        }
        for r in conn.execute(
            "SELECT work_id, title, publisher, attribution, license_tier FROM works"
        )
    }


def _stamp(record: dict, meta: dict[str, dict]) -> dict:
    """Attach licence and attribution to a record.

    Every returned record carries its own tier. The alternative -- a separate `works` lookup the
    caller is instructed to make first -- is an instruction rather than a guarantee, and an
    instruction is the thing that gets skipped when it matters.
    """
    info = meta.get(record.get("work_id"), {})
    record["tier"] = info.get("tier", DEFAULT_TIER)
    record["attribution"] = info.get("attribution")
    record["work_title"] = info.get("title")
    record["quote_allowance"] = QUOTE_ALLOWANCE
    return record


def _clip(text: str, limit: int | None) -> tuple[str, bool, int]:
    full = len(text or "")
    if limit is None or full <= limit:
        return text, False, full
    return text[:limit].rstrip() + "…", True, full


def lookup_verse(conn: sqlite3.Connection, book: str, chapter: int, verse: int,
                 work_id: str | None = None) -> list[dict]:
    """One verse's text from the commercial translations (ESV, NIV, NKJV, CSB, NASB, LSB, NA28).

    This is the quotation-verification path: bible-text.db has none of these translations, so a
    study quoting the ESV can only be checked here. Verse text is never truncated -- see module
    docstring.
    """
    _require_indexed(book, chapter)
    sql = ("SELECT work_id, book, chapter, verse, text FROM verses "
           "WHERE book=? AND chapter=? AND verse=?")
    params: list = [book, chapter, verse]
    if work_id:
        sql += " AND work_id=?"
        params.append(work_id)
    sql += " ORDER BY work_id"
    meta = _work_meta(conn)
    return [_stamp(dict(r), meta) for r in conn.execute(sql, params)]


def lookup_note(conn: sqlite3.Connection, book: str, chapter: int, verse: int | None = None,
                work_id: str | None = None, note_type: str | None = None,
                max_chars: int | None = NOTE_CHARS, limit: int = MAX_ROWS) -> list[dict]:
    """Study notes whose verse span covers the reference.

    A note is stored against a span (`verse_start`..`verse_end`), so a verse is often covered by
    more than one: the ESV Study Bible covers John 6:10 both with its note on 6:1-15 (the feeding
    as a messianic sign) and with the one on 6:10-11 (the crowd's size). Both are returned, which
    is usually what you want -- the span note carries the argument, the verse note the detail.
    Omit `verse` for the whole chapter.

    An empty result is a real answer, not a failure: the ESV has no note on John 6:34, though
    three other works do. Do not read it as the source being unavailable -- call availability()
    for that.
    """
    _require_indexed(book, chapter)
    sql = ("SELECT work_id, book, chapter, verse_start, verse_end, note_type, text FROM notes "
           "WHERE book=? AND chapter=?")
    params: list = [book, chapter]
    if verse is not None:
        sql += " AND verse_start<=? AND verse_end>=?"
        params += [verse, verse]
    if work_id:
        sql += " AND work_id=?"
        params.append(work_id)
    if note_type:
        sql += " AND note_type=?"
        params.append(note_type)
    sql += " ORDER BY verse_start, work_id LIMIT ?"
    params.append(limit)

    meta = _work_meta(conn)
    out = []
    for row in conn.execute(sql, params):
        rec = dict(row)
        rec["text"], rec["truncated"], rec["full_length"] = _clip(rec["text"], max_chars)
        out.append(_stamp(rec, meta))
    return out


def lookup_intro(conn: sqlite3.Connection, book: str, work_id: str | None = None,
                 max_chars: int | None = NOTE_CHARS) -> list[dict]:
    """Book and section introductions -- authorship, date, audience, structure.

    Exempt from _require_indexed's chapter rule: `introductions` holds 213 rows in total, so even
    a full scan of it is trivially cheap. idx_intro_book still covers the book filter.
    """
    if book and book not in _ALL_OSIS_BOOKS:
        raise ValueError(f"{book!r} is not an OSIS book code.")
    sql = "SELECT work_id, scope, book, section_name, title, text FROM introductions WHERE book=?"
    params: list = [book]
    if work_id:
        sql += " AND work_id=?"
        params.append(work_id)
    sql += " ORDER BY work_id, scope"
    meta = _work_meta(conn)
    out = []
    for row in conn.execute(sql, params):
        rec = dict(row)
        rec["text"], rec["truncated"], rec["full_length"] = _clip(rec["text"], max_chars)
        out.append(_stamp(rec, meta))
    return out


def lookup_article(conn: sqlite3.Connection, term: str | None = None, book: str | None = None,
                   chapter: int | None = None, max_chars: int | None = NOTE_CHARS,
                   limit: int = MAX_ROWS) -> list[dict]:
    """Topical articles, by title match and/or by the passage they are attached to.

    Exempt from the chapter rule for the same reason as lookup_intro: `topical_articles` holds
    1,992 rows, and a LIKE over its titles is cheap. The passage filter joins through
    topical_article_refs, which is indexed by nothing but is only 15,326 rows.
    """
    if book and book not in _ALL_OSIS_BOOKS:
        raise ValueError(f"{book!r} is not an OSIS book code.")
    if not term and not book:
        raise ValueError("pass a term, a book, or both -- an unfiltered article list is not useful.")

    sql = "SELECT DISTINCT a.id, a.work_id, a.title, a.text FROM topical_articles a"
    params: list = []
    if book:
        sql += " JOIN topical_article_refs r ON r.article_id = a.id AND r.book = ?"
        params.append(book)
        if chapter is not None:
            sql += " AND r.chapter = ?"
            params.append(chapter)
    if term:
        sql += " WHERE a.title LIKE ?" if "WHERE" not in sql else " AND a.title LIKE ?"
        params.append(f"%{term}%")
    sql += " ORDER BY a.title LIMIT ?"
    params.append(limit)

    meta = _work_meta(conn)
    out = []
    for row in conn.execute(sql, params):
        rec = dict(row)
        rec["text"], rec["truncated"], rec["full_length"] = _clip(rec["text"], max_chars)
        out.append(_stamp(rec, meta))
    return out


def list_works(conn: sqlite3.Connection, with_counts: bool = False) -> list[dict]:
    """Every work in study-notes.db with its tier and attribution. Instant: `works` has 11 rows.

    `with_counts` adds per-work note/verse totals and is **off by default because it scans both
    large tables** -- ~90s over SMB, the exact cost this module exists to avoid. The first draft of
    this function did the counts unconditionally and hung the CLI on its own smoke test, which is a
    fair demonstration that the scan guard has to apply to this module's own queries and not only
    to the ones it accepts from callers. Turn it on deliberately, from the terminal, when you
    actually want an inventory; never on an agent's default path.
    """
    rows = conn.execute(
        "SELECT work_id, title, publisher, year, license_tier, attribution FROM works "
        "ORDER BY work_id"
    ).fetchall()
    out = [dict(r) | {"quote_allowance": QUOTE_ALLOWANCE} for r in rows]
    if with_counts:
        for rec in out:
            rec["notes"] = conn.execute(
                "SELECT COUNT(*) FROM notes WHERE work_id=?", (rec["work_id"],)
            ).fetchone()[0]
            rec["verses"] = conn.execute(
                "SELECT COUNT(*) FROM verses WHERE work_id=?", (rec["work_id"],)
            ).fetchone()[0]
    return out


# ---------------------------------------------------------------------------
# CLI -- formats the same data the functions above return.
# ---------------------------------------------------------------------------

def _print_records(records: list[dict], body_key: str = "text") -> None:
    if not records:
        print("(no results)")
        return
    for r in records:
        ref = r.get("title") or f"{r.get('book','')} {r.get('chapter','')}".strip()
        if r.get("verse_start") is not None:
            ref = f"{r['book']} {r['chapter']}:{r['verse_start']}"
            if r["verse_end"] != r["verse_start"]:
                ref += f"-{r['verse_end']}"
        elif r.get("verse") is not None:
            ref = f"{r['book']} {r['chapter']}:{r['verse']}"
        flag = f"  [truncated, full {r['full_length']} chars]" if r.get("truncated") else ""
        print(f"\n{r['work_id']:38} {ref}{flag}")
        print(f"  {r.get(body_key,'')}")


def cmd_verse(conn, args):
    _print_records(lookup_verse(conn, args.book, args.chapter, args.verse, args.work))


def cmd_note(conn, args):
    _print_records(lookup_note(conn, args.book, args.chapter, args.verse, args.work, args.type))


def cmd_intro(conn, args):
    _print_records(lookup_intro(conn, args.book, args.work))


def cmd_article(conn, args):
    _print_records(lookup_article(conn, args.term, args.book, args.chapter))


def cmd_works(conn, args):
    for r in list_works(conn, with_counts=args.counts):
        line = f"{r['license_tier']:16} {r['work_id']:38} {(r['title'] or '')[:34]}"
        if args.counts:
            line += f"  notes={r['notes']:>6} verses={r['verses']:>6}"
        print(line)


def cmd_status(conn, args):  # conn unused: status must work when connect() would fail
    status = availability()
    print("available" if status["available"] else "UNAVAILABLE")
    for k in ("path", "reason", "remedy"):
        if status.get(k):
            print(f"  {k}: {status[k]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_v = sub.add_parser("verse", help="Verse text from a commercial translation (ESV, NIV, …)")
    p_v.add_argument("book"); p_v.add_argument("chapter", type=int); p_v.add_argument("verse", type=int)
    p_v.add_argument("--work", help="work_id, e.g. esv-study-bible")
    p_v.set_defaults(func=cmd_verse)

    p_n = sub.add_parser("note", help="Study notes covering a verse")
    p_n.add_argument("book"); p_n.add_argument("chapter", type=int)
    p_n.add_argument("verse", type=int, nargs="?")
    p_n.add_argument("--work"); p_n.add_argument("--type",
                                                 choices=["study_note", "footnote", "cross_reference"])
    p_n.set_defaults(func=cmd_note)

    p_i = sub.add_parser("intro", help="Book/section introductions")
    p_i.add_argument("book"); p_i.add_argument("--work")
    p_i.set_defaults(func=cmd_intro)

    p_a = sub.add_parser("article", help="Topical articles by title and/or passage")
    p_a.add_argument("term", nargs="?"); p_a.add_argument("--book"); p_a.add_argument("--chapter", type=int)
    p_a.set_defaults(func=cmd_article)

    p_w = sub.add_parser("works", help="Every work with its tier and attribution")
    p_w.add_argument("--counts", action="store_true",
                     help="also count notes/verses per work -- scans both large tables, ~90s over SMB")
    p_w.set_defaults(func=cmd_works)
    sub.add_parser("status", help="Is the database reachable?").set_defaults(func=cmd_status)

    args = parser.parse_args()
    if args.command == "status":
        return cmd_status(None, args)
    try:
        conn = connect()
    except SourceUnavailable as e:
        raise SystemExit(f"{e.reason}\n{e.remedy}")
    try:
        args.func(conn, args)
    except ValueError as e:
        raise SystemExit(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
