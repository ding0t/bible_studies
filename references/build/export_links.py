"""Emit the reader-facing scripture-link index to docs/data/scripture-links.json.

Committed rather than generated in CI, because bible-text.db is a gitignored build artifact and
the deploy workflow cannot rebuild it. Same arrangement as commentary_index.py: a script writes
into committed content, and is re-run by hand when the underlying data changes.

Only STRONG links ship -- a reader should not be shown a borderline match with no way to weigh it.
Every text quoted is `open` tier. The Dead Sea Scrolls are restricted-nc, so a scroll's variant
lemma travels (one word, attributed) but its verse text does not.

Usage: uv run python export_links.py
"""
import collections
import json
import sqlite3
from datetime import date
from pathlib import Path

import quotations
import query
import versification

OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "scripture-links.json"
METHOD_OUT = OUT.with_name("link-method.json")
ENGLISH = "ebible-eng-web"
ORIGINAL = {"lxx": "ebible-grcbrent", "masoretic": "morphhb-wlc", "english": "sblgnt"}
METHOD_ORDER = ["quotation-greek", "inner-biblical", "quotation-crosslang", "allusion-lemma", "quotation-hebrew"]


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

    # `strong` is set by the build: a pair one of quotations.py's rules admits on its own measure.
    rows = conn.execute(
        "SELECT * FROM scripture_links WHERE strong ORDER BY link_type, from_book, "
        "from_chapter, from_verse, to_book, to_chapter, to_verse").fetchall()

    links = []
    for row in rows:
        kind = row["link_type"]
        source_scheme = "english" if kind in ("quotation-greek", "allusion-lemma", "quotation-crosslang") else "masoretic"
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
            "s": (round(row["idf_overlap"], 1) if kind == "allusion-lemma" else
                  round(row["lemma_score"]) if row["lemma_score"] is not None else row["alignment"]),
            "c": 1 if row["corroborated"] else 0,
            "b": row["basis"],
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

    # unfoldingWord's Translation Notes name the verse a quotation comes from. Where the derived
    # links have nothing for that pair, the note is a lead worth showing, marked as the editors'.
    linked = {(l["f"], l.get("te") or l["t"]) for l in links}
    noted: dict[str, list] = {}
    for row in conn.execute("SELECT DISTINCT from_book, from_chapter, from_verse, to_book, to_chapter, "
                            "to_verse_start FROM cross_references WHERE work_id='uw-tn-quotations'"):
        source = f"{row['from_book']} {row['from_chapter']}:{row['from_verse']}"
        target = f"{row['to_book']} {row['to_chapter']}:{row['to_verse_start']}"
        if (source, target) in linked:
            continue
        for key, ref in ((source, (row["from_book"], row["from_chapter"], row["from_verse"])),
                         (target, (row["to_book"], row["to_chapter"], row["to_verse_start"]))):
            if key not in texts:
                rendered = conn.execute("SELECT text FROM verses WHERE work_id=? AND book=? AND chapter=? AND verse=?",
                                        (ENGLISH, *ref)).fetchone()
                texts[key] = {"e": rendered["text"]} if rendered else {}
        noted.setdefault(source, []).append(target)

    write_method(conn, new_testament)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": date.today().isoformat(),
        "methodOrder": METHOD_ORDER,
        "texts": texts,
        "links": links,
        "leads": leads,
        "noted": noted,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = OUT.stat().st_size / 1e6
    print(f"scripture-links.json: {len(links)} links, {sum(len(v) for v in leads.values())} leads "
          f"across {len(leads)} verses, {len(texts)} verses of text, {size:.2f} MB")
    conn.close()
    return 0


def rules_of(link_type, basis):
    """The rules in a link's basis, as the method page names them. 'formula+phrases' is one rule."""
    prefix = {"quotation-greek": "greek", "inner-biblical": "hebrew"}.get(link_type)
    if prefix is None:
        return {link_type}
    parts = (basis or "").replace("formula+phrases", "formula").split("+")
    return {f"{prefix}-{p}" for p in parts if p}


def write_method(conn, new_testament):
    """What each method finds, how often it is confirmed, what it alone finds, and what it misses.

    Small enough to bundle (the page script imports it), so the method page's charts and the
    Scripture Links evidence view follow every rebuild of the links without being redrawn.
    """
    rows = conn.execute(
        "SELECT link_type, basis, from_book, from_chapter, from_verse, to_book, to_english_chapter, "
        "to_english_verse, to_chapter, to_verse, corroborated FROM scripture_links WHERE strong").fetchall()

    # One NT->OT connection is a quoting verse and an English-numbered target; several methods can
    # find the same one, and the overlap between them is what shows each method's own contribution.
    pairs: dict[tuple, dict] = {}
    ot_pairs: dict[tuple, dict] = {}
    rules: dict[str, dict] = {}
    for r in rows:
        for rule in rules_of(r["link_type"], r["basis"]):
            stat = rules.setdefault(rule, {"links": 0, "confirmed": 0})
            stat["links"] += 1
            stat["confirmed"] += r["corroborated"]
        if r["from_book"] in new_testament and r["to_english_chapter"]:
            key = ((r["from_book"], r["from_chapter"], r["from_verse"]),
                   (r["to_book"], r["to_english_chapter"], r["to_english_verse"]))
            entry = pairs.setdefault(key, {"rules": set(), "c": 0})
            entry["rules"] |= rules_of(r["link_type"], r["basis"])
            entry["c"] |= r["corroborated"]
        elif r["link_type"] == "inner-biblical":
            key = tuple(sorted([(r["from_book"], r["from_chapter"], r["from_verse"]),
                                (r["to_book"], r["to_chapter"], r["to_verse"])]))
            entry = ot_pairs.setdefault(key, {"rules": set(), "c": 0})
            entry["rules"] |= rules_of(r["link_type"], r["basis"])
            entry["c"] |= r["corroborated"]

    def overlap(connections):
        sets: dict[tuple, list] = {}
        for entry in connections.values():
            combo = tuple(sorted(entry["rules"]))
            tally = sets.setdefault(combo, [0, 0])
            tally[0] += 1
            tally[1] += entry["c"]
            if len(combo) == 1:
                rules[combo[0]]["alone"] = rules[combo[0]].get("alone", 0) + 1
        return sorted(({"rules": list(k), "links": v[0], "confirmed": v[1]} for k, v in sets.items()),
                      key=lambda s: -s["links"])

    def credit(found_by):
        for combo, n in found_by.items():
            if len(combo) == 1:
                rules[combo[0]]["keyAlone"] = rules[combo[0]].get("keyAlone", 0) + n
            for rule in combo:
                rules[rule]["key"] = rules[rule].get("key", 0) + n
        return sorted(({"rules": list(k), "n": n} for k, n in found_by.items()), key=lambda s: -s["n"])

    # Answer keys: the WEB translators' quotation footnotes and the Translation Notes, merged where
    # both name the same quotation. Matched as link_lab.hits_gold does -- the note's verse range,
    # one verse either side.
    keys = []
    for r in conn.execute("SELECT work_id, from_book, from_chapter, from_verse, to_book, to_chapter, "
                          "to_verse_start, COALESCE(to_verse_end, to_verse_start) AS to_end FROM cross_references "
                          "WHERE work_id IN ('web-crossrefs', 'uw-tn-quotations') ORDER BY work_id DESC"):
        if r["from_book"] not in new_testament:
            continue
        src = (r["from_book"], r["from_chapter"], r["from_verse"])
        if any(k["src"] == src and k["book"] == r["to_book"] and k["chapter"] == r["to_chapter"]
               and abs(k["start"] - r["to_verse_start"]) <= 1 for k in keys):
            continue
        keys.append({"src": src, "book": r["to_book"], "chapter": r["to_chapter"],
                     "start": r["to_verse_start"], "end": r["to_end"]})
    by_src = collections.defaultdict(list)
    for (src, tgt), entry in pairs.items():
        by_src[src].append((tgt, entry["rules"]))
    found_by: dict[tuple, int] = {}
    missed = []
    for k in keys:
        hit = set()
        for tgt, found in by_src.get(k["src"], ()):
            if tgt[0] == k["book"] and tgt[1] == k["chapter"] and k["start"] - 1 <= tgt[2] <= k["end"] + 1:
                hit |= found
        combo = tuple(sorted(hit))
        found_by[combo] = found_by.get(combo, 0) + 1
        if not hit:
            missed.append([f"{k['src'][0]} {k['src'][1]}:{k['src'][2]}", f"{k['book']} {k['chapter']}:{k['start']}"])

    # The Hebrew key: each verse of the sixteen known parallels, found when a strong link joins it to
    # any verse of its partner passage.
    ot_found: dict[tuple, int] = {}
    ot_missed = []
    by_verse = collections.defaultdict(list)
    for (a, b), entry in ot_pairs.items():
        by_verse[a].append((b, entry["rules"]))
        by_verse[b].append((a, entry["rules"]))
    for (ab, ac, a1, a2), (bb, bc, b1, b2) in quotations.KNOWN_OT:
        for v in range(a1, a2 + 1):
            hit = set()
            for other, found in by_verse.get((ab, ac, v), ()):
                if other[0] == bb and other[1] == bc and b1 <= other[2] <= b2:
                    hit |= found
            combo = tuple(sorted(hit))
            ot_found[combo] = ot_found.get(combo, 0) + 1
            if not hit:
                ot_missed.append([f"{ab} {ac}:{v}", f"{bb} {bc}"])

    # Confirmation by Greek alignment, every scored pair, strong or not: the curve the cut-off sits on.
    curve = [{"from": lo, "pairs": n, "confirmed": c} for lo, n, c in conn.execute(
        "SELECT MIN(alignment / 2 * 2, 40) AS lo, COUNT(*), SUM(corroborated) FROM scripture_links "
        "WHERE link_type='quotation-greek' GROUP BY lo ORDER BY lo")]

    # A random New Testament verse against a random Old Testament verse, confirmed by the same test
    # the links get (same verse, same chapter, within two verses): what chance agreement looks like.
    nt_verses = conn.execute("SELECT COUNT(*) FROM verses WHERE work_id='sblgnt'").fetchone()[0]
    ot_verses = {(b, c, v) for b, c, v in conn.execute(
        "SELECT book, chapter, verse FROM verses WHERE work_id=?", (ENGLISH,)) if b not in new_testament}
    windows: dict[tuple, set] = collections.defaultdict(set)
    for r in conn.execute("SELECT DISTINCT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse_start "
                          "FROM cross_references WHERE work_id != 'uw-tn-quotations'"):
        if r[0] in new_testament:
            for d in range(-2, 3):
                if (r[3], r[4], r[5] + d) in ot_verses:
                    windows[(r[0], r[1], r[2])].add((r[3], r[4], r[5] + d))
    baseline = sum(len(w) for w in windows.values()) / (nt_verses * len(ot_verses))

    payload = {
        "generated": date.today().isoformat(),
        "baseline": baseline,
        "curve": curve,
        "threshold": quotations.QUOTATION_ALIGNMENT,
        "rules": rules,
        "overlap": overlap(pairs),
        "otOverlap": overlap(ot_pairs),
        "key": {"total": len(keys), "foundBy": credit(found_by), "missed": missed},
        "otKey": {"total": sum(ot_found.values()), "foundBy": credit(ot_found), "missed": ot_missed},
    }
    METHOD_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"link-method.json: {len(rules)} rules, {len(pairs)} NT->OT connections, "
          f"key {len(keys) - len(missed)}/{len(keys)} found, Hebrew key "
          f"{sum(ot_found.values()) - len(ot_missed)}/{sum(ot_found.values())}")


if __name__ == "__main__":
    raise SystemExit(main())
