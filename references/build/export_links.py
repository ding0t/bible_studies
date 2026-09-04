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

    # The tradition's own record, as a clearly subordinate tier. It exists because a derivation
    # from the texts cannot reach paraphrase: Matthew 26:64 draws on Daniel 7:13 and Psalm 110:1
    # and our method finds neither, yet the high priest tore his robes -- the Sanhedrin heard it,
    # and the cross-reference tradition has recorded it ever since. Showing "our method found
    # nothing here, the tradition says this" is more honest, and more useful, than showing nothing.
    #
    # English only. A lead is a pointer to chase, not evidence to examine in Greek, and carrying
    # the original text for every lead target would double the payload for no gain.
    #
    # The vote floor is 14 because that is what keeps the case that motivated the tier: Matthew
    # 26:64's leads are Daniel 7:13 at 25 votes and Psalm 110:1 at 15, and a floor of 20 would drop
    # the Psalm -- half of what the Sanhedrin heard. Calibrated against a case that can be checked,
    # like every other threshold here.
    new_testament = {r["book"] for r in conn.execute(
        "SELECT DISTINCT book FROM verses WHERE work_id='sblgnt'")}
    leads: dict[str, list] = {}
    for row in conn.execute(
            # DISTINCT because the upstream data stores every edge twice; without it the cap
            # fills with duplicates and pushes real leads out -- Psalm 110:1 vanished from
            # Matthew 26:64 that way, which is precisely the reference this tier exists to carry
            "SELECT DISTINCT from_book, from_chapter, from_verse, to_book, to_chapter, "
            "to_verse_start, votes FROM cross_references WHERE votes >= 14 "
            "ORDER BY from_book, from_chapter, from_verse, votes DESC"):
        source = f"{row['from_book']} {row['from_chapter']}:{row['from_verse']}"
        crosses_testament = (row["from_book"] in new_testament) != (row["to_book"] in new_testament)
        if not crosses_testament and source not in texts:
            continue          # keep the payload to quotation sites and verses we already carry
        bucket = leads.setdefault(source, [])
        if len(bucket) >= 4:
            continue
        target = f"{row['to_book']} {row['to_chapter']}:{row['to_verse_start']}"
        if target not in texts:
            rendered = conn.execute(
                "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                (ENGLISH, row["to_book"], row["to_chapter"], row["to_verse_start"])).fetchone()
            texts[target] = {"e": rendered["text"]} if rendered else {}
        if source not in texts:
            rendered = conn.execute(
                "SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                (ENGLISH, row["from_book"], row["from_chapter"], row["from_verse"])).fetchone()
            texts[source] = {"e": rendered["text"]} if rendered else {}
        bucket.append({"r": target, "v": row["votes"]})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": date.today().isoformat(),
        "methodOrder": METHOD_ORDER,
        "texts": texts,
        "links": links,
        "leads": leads,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = OUT.stat().st_size / 1e6
    print(f"scripture-links.json: {len(links)} links, {sum(len(v) for v in leads.values())} leads "
          f"across {len(leads)} verses, {len(texts)} verses of text, {size:.2f} MB")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
