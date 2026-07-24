"""Walks the Genesis 5 / Genesis 11 genealogy chain (Adam through Terah) and computes
zadok_year/gregorian_year born-and-died for every person, once per named timeline_variant
in docs/data/genealogy/index.json (mt, lxx, sp, harmonized_v1, ...).

This is the generator half of a source-of-truth split: antediluvian.json and the first ten
records of patriarchal.json hold only raw per-tradition textual facts (age_at_heir_birth,
years_after, lifespan_total, verse citations) -- never a hand-typed cumulative year. Nobody
edits a year number by hand; this script derives every one of them by walking heir_id links
from Adam (zadok_year 0) forward, so a corrected citation in the source JSON automatically
propagates to every downstream year on the next run.

Also serves as the validator: asserts age_at_heir_birth + years_after == lifespan_total for
every tradition entry on every person, and fails loudly (nonzero exit) if anything doesn't
add up -- this is what would have caught a mistranscribed Hebrew/Greek number before it ever
reached a generated file.

Usage: uv run python genealogy_chronology.py
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GENEALOGY_DIR = REPO_ROOT / "docs" / "data" / "genealogy"
GENERATED_DIR = GENEALOGY_DIR / "generated"

SOURCE_FILES = ["antediluvian.json", "patriarchal.json"]


def load_people() -> dict:
    """Merge all people from SOURCE_FILES into one id-keyed dict."""
    people = {}
    for filename in SOURCE_FILES:
        data = json.loads((GENEALOGY_DIR / filename).read_text(encoding="utf-8"))
        for person in data["people"]:
            people[person["id"]] = person
    return people


def validate(people: dict) -> None:
    errors = []
    for pid, person in people.items():
        for trad, t in person.get("traditions", {}).items():
            if "age_at_heir_birth" not in t:
                continue  # e.g. Shelah/Eber/etc. entries with no further heir tracked
            expected = t["age_at_heir_birth"] + t["years_after"]
            if expected != t["lifespan_total"]:
                errors.append(
                    f"{pid} [{trad}]: age_at_heir_birth ({t['age_at_heir_birth']}) + "
                    f"years_after ({t['years_after']}) = {expected}, but lifespan_total "
                    f"states {t['lifespan_total']}"
                )
    if errors:
        print(f"VALIDATION FAILED -- {len(errors)} arithmetic mismatch(es):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)


def resolve_tradition(person: dict, base_tradition: str, overrides: dict) -> tuple[str, dict] | None:
    """Which tradition's data to use for this person under this variant, honoring overrides."""
    tradition_key = overrides.get(person["id"], base_tradition)
    traditions = person.get("traditions", {})
    if tradition_key not in traditions:
        return None
    return tradition_key, traditions[tradition_key]


def walk_chain(people: dict, variant: dict) -> dict:
    """Walk heir_id links from Adam forward, computing born/died years for this variant."""
    base_tradition = variant["based_on"][0]
    overrides = {o["person_id"]: o["adopts_tradition"] for o in variant.get("overrides", [])}

    computed = {}
    current_id = "adam"
    current_zadok_born = 0

    while current_id is not None:
        person = people.get(current_id)
        if person is None:
            break
        resolved = resolve_tradition(person, base_tradition, overrides)
        if resolved is None:
            # Person exists but has no chronology data under this variant/tradition
            # (e.g. Cainan under 'mt' or 'sp') -- chain simply doesn't include them.
            break
        tradition_key, t = resolved
        zadok_died = current_zadok_born + t["lifespan_total"]
        computed[current_id] = {
            "tradition_used": tradition_key,
            "zadok_year_born": current_zadok_born,
            "gregorian_year_born": current_zadok_born - 4004,
            "zadok_year_died": zadok_died,
            "gregorian_year_died": zadok_died - 4004,
            "lifespan_years": t["lifespan_total"],
        }
        heir_id = t.get("heir_id")
        if heir_id is None:
            break
        current_zadok_born = current_zadok_born + t["age_at_heir_birth"]
        current_id = heir_id

    return computed


def main() -> None:
    people = load_people()
    validate(people)

    index = json.loads((GENEALOGY_DIR / "index.json").read_text(encoding="utf-8"))
    variants = index["timeline_variants"]

    GENERATED_DIR.mkdir(exist_ok=True)
    summary_rows = []

    for variant_id, variant in variants.items():
        computed = walk_chain(people, variant)
        out_path = GENERATED_DIR / f"{variant_id}.json"
        out_path.write_text(
            json.dumps(
                {
                    "variant_id": variant_id,
                    "name": variant["name"],
                    "generated_by": "references/build/genealogy_chronology.py -- do not hand-edit",
                    "people": computed,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        flood_year = computed.get("noah", {}).get("zadok_year_born", None)
        if flood_year is not None:
            flood_year += 600  # Noah was 600 at the Flood (Genesis 7:11), all traditions agree
        terah_death = computed.get("terah", {}).get("zadok_year_died")
        summary_rows.append((variant_id, variant["name"], flood_year, terah_death))

    print(f"Validated {len(people)} people across {len(SOURCE_FILES)} source file(s).")
    print(f"Generated {len(variants)} timeline variant(s) into {GENERATED_DIR.relative_to(REPO_ROOT)}/\n")
    print(f"{'variant':<16}{'name':<32}{'flood (zadok)':<16}{'terah death (zadok)'}")
    for variant_id, name, flood_year, terah_death in summary_rows:
        print(f"{variant_id:<16}{name:<32}{str(flood_year):<16}{terah_death}")


if __name__ == "__main__":
    main()
