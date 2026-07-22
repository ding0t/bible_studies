"""Strong's/BDB/TWOT number cross-reference, sourced entirely from our
already-forked, already-verified open-data/hebrew-lexicon submodule's
LexicalIndex.xml -- the Open Scriptures project's own unified numbering
cross-reference. This is a bare correspondence between numbering schemes
(which TWOT entry a given Strong's/BDB entry maps to), not TWOT's copyrighted
prose, so it lives in the open tier even though the TWOT commentary text
itself (sourced separately via OCR) cannot.
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[3]
LEXICAL_INDEX = REPO_ROOT / "references/open-data/hebrew-lexicon/LexicalIndex.xml"
OUT = Path(__file__).resolve().parent / "twot_strongs_map.json"


def local(tag: str) -> str:
    return tag.split("}")[-1]


def main():
    tree = ElementTree.parse(LEXICAL_INDEX)
    twot_to_entries = {}  # twot_number -> list of {strongs_id, bdb_id, lemma, xlit, gloss}

    for entry in tree.getroot().iter():
        if local(entry.tag) != "entry":
            continue
        w_el = next((c for c in entry if local(c.tag) == "w"), None)
        def_el = next((c for c in entry if local(c.tag) == "def"), None)
        xref_el = next((c for c in entry if local(c.tag) == "xref"), None)
        if w_el is None or xref_el is None:
            continue
        twot = xref_el.get("twot")
        if not twot or not re.match(r"^\d{1,4}[a-z]?$", twot):
            continue

        twot_to_entries.setdefault(twot, []).append({
            "strongs_id": f"H{xref_el.get('strong')}" if xref_el.get("strong") else None,
            "bdb_id": xref_el.get("bdb"),
            "lemma": w_el.text,
            "xlit": w_el.get("xlit"),
            "gloss": def_el.text if def_el is not None else None,
        })

    print(f"TWOT numbers found: {len(twot_to_entries)}")
    for k, v in list(twot_to_entries.items())[:5]:
        print(k, v)

    OUT.write_text(json.dumps(twot_to_entries, ensure_ascii=False, indent=1))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
