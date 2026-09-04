"""Emit the reader-facing scripture-link index to docs/data/scripture-links.json.

Committed rather than generated in CI, because bible-text.db is a gitignored build artifact and
the deploy workflow cannot rebuild it. Same arrangement as commentary_index.py: a script writes
into committed content, and is re-run by hand when the underlying data changes.

Only STRONG links ship -- a reader should not be shown a borderline match with no way to weigh it.
Every text quoted is `open` tier. The Dead Sea Scrolls are restricted-nc, so a scroll's variant
lemma travels (one word, attributed) but its verse text does not.

Usage: uv run python export_links.py
"""
import json
import sqlite3
from datetime import date
from pathlib import Path

import quotations
import query
import versification

OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "scripture-links.json"
ENGLISH = "ebible-eng-web"
ORIGINAL = {"lxx": "ebible-grcbrent", "masoretic": "morphhb-wlc", "english": "sblgnt"}
METHOD_ORDER = ["quotation-greek", "inner-biblical", "allusion-lemma", "quotation-hebrew"]


def main() -> int:
    conn = query.connect()
    texts: dict[str, dict[str, str]] = {}

    def remember(scheme, book, chapter, verse, english_ref):
        """Store a verse's original and English text once, keyed by reference."""
        key = f"{book} {chapter}:{verse}"
        if key in texts:
            return key
        entry = {}
        original = conn.execute(
            "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
            (ORIGINAL[scheme], book, chapter, verse)).fetchone()
        if original:
            entry["o"] = original["text"]
        if english_ref:
            rendered = conn.execute(
                "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                (ENGLISH, *english_ref)).fetchone()
            if rendered:
                entry["e"] = rendered["text"]
        texts[key] = entry
        return key

    rows = conn.execute(
        "SELECT * FROM scripture_links WHERE (link_type='allusion-lemma' AND idf_overlap >= ?) "
        "OR (link_type != 'allusion-lemma' AND alignment >= ?) ORDER BY link_type, from_book, "
        "from_chapter, from_verse, to_book, to_chapter, to_verse",
        (quotations.ALLUSION_WEIGHT, quotations.QUOTATION_ALIGNMENT)).fetchall()

    links = []
    for row in rows:
        kind = row["link_type"]
        source_scheme = "english" if kind in ("quotation-greek", "allusion-lemma") else "masoretic"
        target_scheme = query.LINK_TARGET_SCHEME[kind]
        source = (row["from_book"], row["from_chapter"], row["from_verse"])
        target = (row["to_book"], row["to_chapter"], row["to_verse"])
        target_english = ((row["to_book"], row["to_english_chapter"], row["to_english_verse"])
                          if row["to_english_chapter"] else
                          versification.align(*target, target_scheme, "english"))

        source_key = remember(source_scheme, *source, versification.align(
            *source, source_scheme, "english"))
        target_key = remember(target_scheme, *target, target_english)
        entry = {
            "f": source_key, "t": target_key, "m": kind,
            "s": round(row["idf_overlap"], 1) if kind == "allusion-lemma" else row["alignment"],
            "c": 1 if row["corroborated"] else 0,
        }
        if target_english:
            english_key = f"{target_english[0]} {target_english[1]}:{target_english[2]}"
            if english_key != target_key:
                entry["te"] = english_key
        shared = query._shared_span(texts[source_key].get("o"), texts[target_key].get("o"),
                                    target_scheme in ("lxx", "english"))
        if shared:
            entry["sh"] = shared
        # a scroll's variant lemma travels; its verse text does not (restricted-nc)
        if target_english:
            masoretic = versification.align(*target_english, "english", "masoretic")
            if masoretic:
                variants = [{"w": r["work_id"].removeprefix("dss-"), "l": r["lemma"],
                             "n": r["extant_words"]}
                            for r in conn.execute(
                                "SELECT work_id, lemma, extant_words FROM dss_variants "
                                "WHERE book=? AND chapter=? AND verse=? ORDER BY extant_words DESC "
                                "LIMIT 4", masoretic)]
                if variants:
                    entry["v"] = variants
        links.append(entry)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": date.today().isoformat(),
        "methodOrder": METHOD_ORDER,
        "texts": texts,
        "links": links,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = OUT.stat().st_size / 1e6
    print(f"scripture-links.json: {len(links)} links, {len(texts)} verses, {size:.2f} MB")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
