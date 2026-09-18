#!/usr/bin/env python3
"""Assemble the standard exegesis evidence set for a passage in one call.

What it replaces
----------------
Working a passage means the same dozen-plus lookups every time: the text in a couple of
translations, the interlinear, the cross-references, any Dead Sea Scroll divergence, the TWOT
roots behind the Hebrew, the study notes. Gathering them one call at a time is slow, easy to do
half of, and easy to do in an order that hides a problem until late.

This runs them through research_batch (so: one connection per database, a wall-clock budget,
per-request status) and reshapes the answers into the order the develop-bible-study skill works
in -- addressing, then historical context, then text, then words, then cross-references.

Why versification comes first and is never optional
---------------------------------------------------
**A reference is not a universal address, and getting it wrong is silent.** Hebrew Joel 3:1 is
English Joel 2:28 -- the verse Acts 2 quotes. LXX Psalm 22 is English Psalm 23. The Masoretic and
English traditions divide Daniel, Joel and Malachi differently, and the Septuagint renumbers
nearly the whole psalter. Ask for a verse in one work's numbering and read it in another's and you
get an unrelated verse with **no error raised**.

lookup_verse and lookup_passage handle this internally, but a brief that assembles several sources
around one reference is exactly where a mismatch would go unnoticed -- so `addressing` is computed
unconditionally, put first, and flagged when the schemes disagree. That flag is the single most
useful line in the output for an Old Testament passage, and it costs one indexed lookup.

Bounded on purpose
------------------
A twenty-verse passage with full per-verse detail would be unreadable and slow. Text covers the
whole range; per-verse detail (interlinear, variants, trace, notes) covers at most
MAX_DETAIL_VERSES, and the brief says so rather than silently truncating.
"""
from __future__ import annotations

import research_batch
import study_notes_query
import twot_lookup

DEFAULT_TRANSLATIONS = ["WEB"]            # public domain; safe to quote at length
DEFAULT_STUDY_WORKS = ["esv-study-bible"]  # the quotation-verification path
MAX_DETAIL_VERSES = 12
MAX_TWOT_LOOKUPS = 25
SECTIONS = ("addressing", "historical", "text", "words", "crossrefs", "variants", "notes")


def _study_work_ids() -> set[str]:
    """work_ids that live in study-notes.db, so a translation name can be routed to the right db.

    Resolved against the database rather than by string convention, for the same reason
    query._resolve_work_id is: guessing a prefix silently returns nothing.
    """
    try:
        conn = study_notes_query.connect()
    except study_notes_query.SourceUnavailable:
        return set()
    try:
        return {w["work_id"] for w in study_notes_query.list_works(conn)}
    finally:
        conn.close()


_ALIASES = {
    "ESV": "esv-study-bible", "NIV": "niv-biblical-theology-study-bible",
    "NKJV": "nkjv-cultural-backgrounds-study-bible", "CSB": "csb-ancient-faith-study-bible",
    "NASB": "nasb-2020", "LSB": "lsb-2021", "NA28": "na28-greek-nt",
}


def route_translation(name: str, study_ids: set[str]) -> tuple[str, str]:
    """(source, work_id) for a translation name.

    ESV/NIV/NKJV/CSB/NASB/LSB exist ONLY in study-notes.db -- bible-text.db has none of them --
    so a caller asking for "ESV" must be sent there rather than getting an empty result from the
    open database and concluding the verse is missing.
    """
    if name in study_ids:
        return "study-notes", name
    upper = name.upper()
    if upper in _ALIASES and _ALIASES[upper] in study_ids:
        return "study-notes", _ALIASES[upper]
    return "bible-text", name


def _verse_span(chapter: int, verse_start: int, verse_end: int | None) -> list[int]:
    end = verse_start if verse_end is None else verse_end
    return list(range(verse_start, max(verse_start, end) + 1))


def build_requests(book: str, chapter: int, verse_start: int, verse_end: int | None,
                   translations: list[str], study_works: list[str],
                   include: tuple[str, ...], study_ids: set[str]) -> list[dict]:
    verses = _verse_span(chapter, verse_start, verse_end)[:MAX_DETAIL_VERSES]
    end = verse_start if verse_end is None else verse_end
    reqs: list[dict] = []

    if "addressing" in include:
        reqs.append({"id": "addressing", "tool": "bible_align",
                     "args": {"book": book, "chapter": chapter, "verse": verse_start}})

    if "historical" in include:
        for work in study_works:
            reqs.append({"id": f"intro:{work}", "tool": "study_intro",
                         "args": {"book": book, "work_id": work}})

    if "text" in include:
        for name in translations:
            source, work_id = route_translation(name, study_ids)
            if source == "bible-text":
                reqs.append({"id": f"text:{name}", "tool": "bible_passage",
                             "args": {"book": book, "chapter": chapter, "verse_start": verse_start,
                                      "verse_end": end, "translation": work_id}})
            else:
                for v in verses:
                    reqs.append({"id": f"text:{name}:{v}", "tool": "study_verse",
                                 "args": {"book": book, "chapter": chapter, "verse": v,
                                          "work_id": work_id}})

    if "words" in include:
        for v in verses:
            reqs.append({"id": f"interlinear:{v}", "tool": "bible_interlinear",
                         "args": {"book": book, "chapter": chapter, "verse": v}})

    if "crossrefs" in include:
        for v in verses:
            reqs.append({"id": f"trace:{v}", "tool": "bible_trace",
                         "args": {"book": book, "chapter": chapter, "verse": v}})

    if "variants" in include:
        for v in verses:
            reqs.append({"id": f"variants:{v}", "tool": "bible_variants",
                         "args": {"book": book, "chapter": chapter, "verse": v}})

    if "notes" in include:
        for work in study_works:
            for v in verses:
                reqs.append({"id": f"note:{work}:{v}", "tool": "study_note",
                             "args": {"book": book, "chapter": chapter, "verse": v,
                                      "work_id": work}})
    return reqs


def _ok(results: dict, rid: str):
    record = results.get(rid)
    return record["result"] if record and record["status"] == "ok" else None


def _addressing(results: dict) -> dict:
    """Versification, with an explicit flag when the schemes disagree."""
    align = _ok(results, "addressing")
    if not align:
        return {"available": False,
                "note": "versification alignment unavailable -- do not assume the reference "
                        "carries between works"}
    refs = {name: data.get("reference") for name, data in (align.get("schemes") or {}).items()}
    distinct = {r for r in refs.values() if r}
    out = {"schemes": refs, "agree": len(distinct) <= 1}
    if len(distinct) > 1:
        out["warning"] = (
            f"This reference is numbered differently across traditions ({', '.join(sorted(distinct))}). "
            f"Quoting one scheme's text under another's reference is silent -- no error is raised. "
            f"Use bible_parallel to move the reference between two named works."
        )
    return out


def _hebrew_strongs(results: dict, verses: list[int]) -> list[str]:
    """Distinct Hebrew Strong's ids in the interlinear, normalised for TWOT.

    MACULA writes them prefixed and zero-padded (`b:H7225`, `H0430`), which TWOT's index does not
    use. twot_lookup.normalize_strongs does the conversion; deduping on the normalised key stops
    `H0430` and `H430` counting as two lookups.
    """
    seen: list[str] = []
    for v in verses:
        data = _ok(results, f"interlinear:{v}") or {}
        for row in data.get("rows") or []:
            raw = (row.get("strong") or "").strip()
            if not raw:
                continue
            try:
                key, _ = twot_lookup.normalize_strongs(raw)
            except ValueError:
                continue  # Greek, or no number in it -- TWOT has nothing to say either way
            if key not in seen:
                seen.append(key)
    return seen[:MAX_TWOT_LOOKUPS]


def passage_brief(book: str, chapter: int, verse_start: int, verse_end: int | None = None,
                  translations: list[str] | None = None, study_works: list[str] | None = None,
                  include: list[str] | None = None,
                  budget_seconds: float = 60.0) -> dict:
    """The standard evidence set for a passage, in exegesis order.

    Sections: addressing (versification, always), historical (book introductions), text,
    words (interlinear + TWOT roots for Hebrew), crossrefs, variants, notes.
    """
    translations = list(translations or DEFAULT_TRANSLATIONS)
    study_works = list(study_works or DEFAULT_STUDY_WORKS)
    include = tuple(include or SECTIONS)
    unknown = [s for s in include if s not in SECTIONS]
    if unknown:
        return {"error": f"unknown section(s) {unknown}; known: {list(SECTIONS)}"}

    all_verses = _verse_span(chapter, verse_start, verse_end)
    verses = all_verses[:MAX_DETAIL_VERSES]
    study_ids = _study_work_ids()

    reqs = build_requests(book, chapter, verse_start, verse_end, translations, study_works,
                          include, study_ids)
    batch = research_batch.run_batch(reqs, budget_seconds=budget_seconds)
    results = batch["results"]

    # TWOT depends on the interlinear, so it is a second pass rather than part of the first batch.
    twot: dict = {}
    if "words" in include:
        strongs = _hebrew_strongs(results, verses)
        if strongs:
            second = research_batch.run_batch(
                [{"id": f"twot:{s}", "tool": "twot_strongs", "args": {"strongs_id": s}}
                 for s in strongs],
                budget_seconds=max(5.0, batch["summary"]["budget_seconds"]
                                   - batch["summary"]["elapsed_seconds"]),
            )
            for s in strongs:
                roots = _ok(second["results"], f"twot:{s}")
                if roots:
                    twot[s] = roots

    ref = f"{book} {chapter}:{verse_start}"
    if verse_end and verse_end != verse_start:
        ref += f"-{verse_end}"

    brief: dict = {"reference": ref, "sections": list(include)}

    if "addressing" in include:
        brief["addressing"] = _addressing(results)
    if "historical" in include:
        brief["historical_context"] = {
            work: _ok(results, f"intro:{work}") or [] for work in study_works
        }
    if "text" in include:
        text: dict = {}
        for name in translations:
            source, work_id = route_translation(name, study_ids)
            if source == "bible-text":
                text[name] = _ok(results, f"text:{name}")
            else:
                rows = [r for v in verses for r in (_ok(results, f"text:{name}:{v}") or [])]
                text[name] = {"work_id": work_id, "tier": "quotation-only", "verses": rows}
        brief["text"] = text
    if "words" in include:
        brief["words"] = {
            "interlinear": {str(v): _ok(results, f"interlinear:{v}") for v in verses},
            "twot_roots": twot,
        }
    if "crossrefs" in include:
        brief["cross_references"] = {str(v): _ok(results, f"trace:{v}") for v in verses}
    if "variants" in include:
        found = {str(v): data for v in verses
                 if (data := _ok(results, f"variants:{v}")) and data.get("readings")}
        brief["textual_variants"] = found or {
            "note": "no Dead Sea Scroll divergence recorded for these verses"}
    if "notes" in include:
        brief["study_notes"] = {
            work: {str(v): _ok(results, f"note:{work}:{v}") or [] for v in verses}
            for work in study_works
        }

    unavailable = sorted({r.get("source") or r.get("tool")
                          for r in results.values() if r["status"] == "unavailable"})
    brief["diagnostics"] = {
        "requests": batch["summary"],
        "detail_verses": verses,
        "truncated": len(all_verses) > len(verses),
        "unavailable_sources": unavailable,
    }
    if brief["diagnostics"]["truncated"]:
        brief["diagnostics"]["note"] = (
            f"per-verse detail covers the first {MAX_DETAIL_VERSES} of {len(all_verses)} verses; "
            f"text covers the whole range. Request a narrower span for detail on the rest.")
    if unavailable:
        brief["diagnostics"]["warning"] = (
            "Some sources could not be reached; their sections are empty. That is a gap in this "
            "brief, not evidence about the text -- do not fill it from memory.")
    return brief


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("book"); parser.add_argument("chapter", type=int)
    parser.add_argument("verse_start", type=int)
    parser.add_argument("verse_end", type=int, nargs="?")
    parser.add_argument("--translations", nargs="*", default=None)
    parser.add_argument("--study-works", nargs="*", default=None)
    parser.add_argument("--include", nargs="*", default=None, choices=SECTIONS)
    parser.add_argument("--budget", type=float, default=60.0)
    args = parser.parse_args()
    print(json.dumps(passage_brief(args.book, args.chapter, args.verse_start, args.verse_end,
                                   args.translations, args.study_works, args.include,
                                   args.budget), indent=2, default=str))
