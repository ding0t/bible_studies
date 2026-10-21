"""Emit the original-language data the public connector serves to docs/content/assets/lang/.

The connector (app/src/connector/, mounted at /mcp by the site's Worker) answers an AI assistant's
questions about the Hebrew and Greek under a passage. It reads these files as static assets, so
it needs no database at request time, and they are committed for the same reason as
export_popups.py's: CI cannot rebuild bible-text.db. Re-run by hand when the database changes.

Every source here may be shared: the open tier, and the CC BY-NC Dead Sea Scrolls readings, served
free of charge with attribution (the author's decision, 2026-10-21). Nothing from study-notes.db,
TWOT or an `unknown`-tier work is read.

- chapters/<Book>/<n>.json   one file per English chapter. For each verse: WEB, BSB and ULT text;
                             the original (SBLGNT, or the WLC under its Masoretic number) and, for
                             the Old Testament, the Septuagint (Brenton); every original word with
                             MACULA's lemma, Strong's number, morphology, gloss, semantic domain and
                             syntax, its implicit subject and its referent resolved to the words they
                             point at; the ULT's English-to-original alignment; the unfoldingWord
                             notes (Qere, translator decisions); Dead Sea Scroll readings the
                             Masoretic lacks, with how much of the verse survives; the verse's
                             Masoretic and Septuagint numbers where they differ; and the scripture
                             links query.lookup_trace finds, with the words the two verses share.
- words/<H|G><nn>.json       Strong's numbers in files of a hundred, like the pop-up lexicon: every
                             occurrence (English references) and the ULT's commonest renderings.
                             The gloss and transliteration stay in assets/popups/words/.
- grammar.json               the unfoldingWord Hebrew Grammar articles.

Usage: uv run python export_connector.py [--publish]

--publish packs the output as lang.tgz and uploads it to the `lang-data` GitHub release, which the
deploy workflow downloads before the site build. Run it after a re-export that should go live.
"""
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import query
import versification

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs" / "content" / "assets" / "lang"
ENGLISH = {"web": "ebible-eng-web", "bsb": "scrollmapper-BSB", "ult": "uw-ult"}
MACULA = ("macula-greek-sblgnt", "macula-hebrew-wlc")
RENDERINGS = 8
WORD_FIELDS = ["surface", "strongs", "lemma", "morph", "gloss", "domain", "class", "role",
               "type", "state", "subject", "referent"]


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def strongs_id(raw: str | None, greek: bool) -> str | None:
    """'G37670' (ULT: four digits and a sense digit), 'c:H8085', '3767', '1537+4053' -> 'G3767'."""
    if not raw:
        return None
    raw = raw.split(":")[-1].split("+")[0]
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    if raw[:1] == "G" and len(digits) == 5:
        digits = digits[:4]
    prefix = "G" if (raw[:1] == "G" or (raw[:1] != "H" and greek)) else "H"
    return f"{prefix}{int(digits)}"


def english_ref(book, chapter, verse, scheme) -> tuple[str, int, int]:
    return versification.align(book, chapter, verse, scheme, "english") or (book, chapter, verse)


def ref_text(ref) -> str:
    return f"{ref[0]} {ref[1]}:{ref[2]}"


def main() -> None:
    conn = query.connect()
    shutil.rmtree(OUT, ignore_errors=True)

    chapters: dict[tuple[str, int], dict[str, dict]] = defaultdict(lambda: defaultdict(dict))
    order: list[tuple[str, int]] = []
    for row in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id=? "
                            "ORDER BY rowid", (ENGLISH["web"],)):
        key = (row["book"], row["chapter"])
        if key not in chapters:
            order.append(key)
        chapters[key][str(row["verse"])]["web"] = row["text"].strip()
    old_testament = {b for b, _ in order[:order.index(("Matt", 1))]}

    for name in ("bsb", "ult"):
        for row in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id=?",
                                (ENGLISH[name],)):
            verse = chapters.get((row["book"], row["chapter"]), {}).get(str(row["verse"]))
            if verse is not None:
                verse[name] = row["text"].strip()

    def verse_at(ref):
        return chapters.get((ref[0], ref[1]), {}).get(str(ref[2]))

    for work, scheme, field in (("sblgnt", "english", "orig"), ("morphhb-wlc", "masoretic", "orig"),
                                ("ebible-grcbrent", "lxx", "lxx")):
        for row in conn.execute("SELECT book, chapter, verse, text FROM verses WHERE work_id=?", (work,)):
            ref = english_ref(row["book"], row["chapter"], row["verse"], scheme)
            verse = verse_at(ref)
            if verse is None:
                continue
            verse[field] = row["text"].strip()
            if scheme != "english" and (row["chapter"], row["verse"]) != ref[1:]:
                verse.setdefault("numbering", {})[scheme] = ref_text((row["book"], row["chapter"], row["verse"]))

    # Words first pass: every MACULA word by node id, so a pointer to a subject or referent
    # resolves to the word it names, wherever in the chapter (or the verse before) it sits.
    nodes: dict[str, tuple] = {}
    rows = conn.execute(
        f"""SELECT work_id, book, chapter, verse, word_position, surface_form, strongs_id, morph_code,
                   lemma, gloss, domain_code, node_id, word_class, syntactic_role, sub_type, state,
                   subject_ref, referent
            FROM morphology WHERE work_id IN ({",".join("?" * len(MACULA))})
            ORDER BY work_id, book, chapter, verse, word_position""", MACULA).fetchall()
    for r in rows:
        greek = r["work_id"].startswith("macula-greek")
        ref = english_ref(r["book"], r["chapter"], r["verse"], "english" if greek else "masoretic")
        nodes[re.sub(r"\D", "", r["node_id"] or "")] = (r["surface_form"], r["gloss"], ref_text(ref))

    def resolve(pointers: str | None):
        if not pointers:
            return None
        found = [nodes.get(re.sub(r"\D", "", p)) for p in pointers.split()]
        return [list(f) for f in found if f] or None

    occurrences: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        greek = r["work_id"].startswith("macula-greek")
        ref = english_ref(r["book"], r["chapter"], r["verse"], "english" if greek else "masoretic")
        verse = verse_at(ref)
        sid = strongs_id(r["strongs_id"], greek)
        if sid and (not occurrences[sid] or occurrences[sid][-1] != ref_text(ref)):
            occurrences[sid].append(ref_text(ref))
        if verse is None:
            continue
        verse.setdefault("words", []).append([
            r["surface_form"], sid, r["lemma"], r["morph_code"], r["gloss"], r["domain_code"],
            r["word_class"], r["syntactic_role"], r["sub_type"], r["state"],
            resolve(r["subject_ref"]), resolve(r["referent"]),
        ])

    renderings: dict[str, Counter] = defaultdict(Counter)
    for r in conn.execute("SELECT book, chapter, verse, english, content, lemma, strong "
                          "FROM word_alignment ORDER BY rowid"):
        greek = (r["strong"] or "").lstrip("c:").startswith("G") or r["book"] not in old_testament
        sid = strongs_id(r["strong"], greek)
        verse = verse_at((r["book"], r["chapter"], r["verse"]))
        if verse is not None:
            verse.setdefault("align", []).append([r["english"], r["content"], sid, r["lemma"]])
        if sid:
            renderings[sid][r["english"].lower()] += 1

    for r in conn.execute("SELECT work_id, book, chapter, verse, note_type, text FROM notes"):
        scheme = versification.scheme_for_work(r["work_id"])
        verse = verse_at(english_ref(r["book"], r["chapter"], r["verse"], scheme))
        if verse is not None:
            verse.setdefault("notes", []).append([r["work_id"], r["note_type"], r["text"]])

    for r in conn.execute("SELECT work_id, book, chapter, verse, lemma, extant_words FROM dss_variants"):
        verse = verse_at(english_ref(r["book"], r["chapter"], r["verse"], "masoretic"))
        if verse is not None:
            verse.setdefault("scrolls", []).append([r["work_id"].removeprefix("dss-"), r["lemma"],
                                                    r["extant_words"]])

    # Links, through the same lookup_trace the research tools use, for every verse that has one.
    linked = set()
    for r in conn.execute("SELECT link_type, from_book, from_chapter, from_verse, to_book, "
                          "to_english_chapter, to_english_verse FROM scripture_links"):
        from_scheme = "english" if r["link_type"] in ("quotation-greek", "allusion-lemma",
                                                      "quotation-crosslang") else "masoretic"
        linked.add(english_ref(r["from_book"], r["from_chapter"], r["from_verse"], from_scheme))
        if r["to_english_chapter"]:
            linked.add((r["to_book"], r["to_english_chapter"], r["to_english_verse"]))
    for ref in sorted(linked):
        verse = verse_at(ref)
        if verse is None:
            continue
        if ref[0] in old_testament:
            masoretic = versification.align(*ref, "english", "masoretic") or ref
            trace = query.lookup_trace(conn, *masoretic, translation="morphhb-wlc")
        else:
            trace = query.lookup_trace(conn, *ref)
        if trace["connections"]:
            verse["links"] = [
                {k: c.get(k) for k in ("method", "direction", "english_reference", "reference",
                                       "scheme", "original", "shared", "strength", "corroborated",
                                       "scroll_readings") if c.get(k) not in (None, [])}
                for c in trace["connections"]
            ]

    for (book, chapter), verses in chapters.items():
        dump(OUT / "chapters" / book / f"{chapter}.json",
             {"book": book, "chapter": chapter, "ot": book in old_testament,
              "word_fields": WORD_FIELDS, "verses": verses})

    buckets: dict[str, dict] = defaultdict(dict)
    for sid in set(occurrences) | set(renderings):
        n = int(sid[1:])
        buckets[f"{sid[0]}{n // 100:02d}"][str(n)] = {
            "occurrences": occurrences.get(sid, []),
            "renderings": renderings[sid].most_common(RENDERINGS) if sid in renderings else [],
        }
    for name, data in buckets.items():
        dump(OUT / "words" / f"{name}.json", data)

    dump(OUT / "grammar.json", [
        {"slug": r["slug"], "title": r["title"], "body": r["body"]}
        for r in conn.execute("SELECT slug, title, body FROM grammar_articles ORDER BY title")])
    dump(OUT / "books.json", [[book, chapter, len(chapters[(book, chapter)])] for book, chapter in order])
    print(f"{len(chapters)} chapters, {len(buckets)} word files, {len(linked)} linked verses -> {OUT}")


def publish() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "lang.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(OUT, arcname="lang")
        exists = subprocess.run(["gh", "release", "view", "lang-data"], capture_output=True).returncode == 0
        if not exists:
            subprocess.run(["gh", "release", "create", "lang-data", "--title", "Original-language data",
                            "--notes", "The public connector's data, written by "
                            "references/build/export_connector.py. Downloaded by the deploy workflow."],
                           check=True)
        subprocess.run(["gh", "release", "upload", "lang-data", str(archive), "--clobber"], check=True)
        print(f"published {archive.stat().st_size // 1_000_000} MB to release lang-data")


if __name__ == "__main__":
    main()
    if "--publish" in sys.argv:
        publish()
