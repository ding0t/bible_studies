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


def walk_chain(people: dict, variant: dict, anchor: dict) -> dict:
    """Walk heir_id links from Adam forward, computing born/died years for this variant.

    Shem's birth year has two possible bases, differing by 2 years, and the choice
    propagates to every date below him -- see chronology_anchor.shem_birth_basis in
    docs/data/genealogy/index.json for both readings and why the default is Genesis 11:10.
    """
    base_tradition = variant["based_on"][0]
    overrides = {o["person_id"]: o["adopts_tradition"] for o in variant.get("overrides", [])}
    use_gen_11_10 = anchor.get("shem_birth_basis") == "gen_11_10"
    # The scenarios are all defined against the Masoretic chain, so a scenario-level Nahor
    # reading applies only to MT-based variants. Applying it to the LXX or SP would overwrite
    # those texts' own witness (179 and 79) and make them useless as independent comparisons.
    nahor_age = (
        anchor.get("nahor_age_at_terah_birth") if base_tradition == "mt" else None
    )

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
        if current_id == "shem" and use_gen_11_10:
            # Genesis 11:10: Arpachshad born 2 years after the Flood, Shem then 100.
            noah = computed.get("noah")
            if noah is not None:
                current_zadok_born = (
                    noah["zadok_year_born"] + 600 + 2 - t["age_at_heir_birth"]
                )
        zadok_died = current_zadok_born + t["lifespan_total"]
        computed[current_id] = {
            "tradition_used": tradition_key,
            "zadok_year_born": current_zadok_born,
            "zadok_year_died": zadok_died,
            "lifespan_years": t["lifespan_total"],
        }
        heir_id = t.get("heir_id")
        if heir_id is None:
            break
        step = t["age_at_heir_birth"]
        if current_id == "nahor" and nahor_age is not None:
            # Scenario-level reading of Nahor's age; see chronology_scenarios in index.json.
            step = nahor_age
        current_zadok_born = current_zadok_born + step
        current_id = heir_id

    return computed


def creation_epoch_bc(computed: dict, anchor: dict, variant: dict | None = None) -> int | None:
    """Derive this variant's creation date in BC from the shared downstream anchor.

    Zadok year 0 is creation and is absolute; the Gregorian equivalent is derived, so a
    variant with a longer Adam-to-Terah chain puts creation EARLIER, not the Flood later.
    Walking forward from Terah to the Exodus uses two figures that are interpretive choices
    rather than textual variants, so they live in index.json's chronology_anchor block
    alongside their scriptural basis.
    """
    terah = computed.get("terah")
    if terah is None:
        return None
    variant = variant or {}
    terah_to_abram = variant.get("terah_to_abram", anchor["terah_to_abram"])
    exodus_zadok = (
        terah["zadok_year_born"]
        + terah_to_abram
        + anchor["abram_birth_to_exodus"]
    )
    return exodus_zadok + anchor["anchor_exodus_bc"]


def apply_epoch(computed: dict, creation_bc: int) -> None:
    """Stamp gregorian_year_born/died onto every person, negative for BC.

    Sign convention is unchanged from the previous generator so downstream consumers
    (app/src/utils/calendarConvert.js, docs/data/events.json) keep working. The known
    off-by-one between that convention and true astronomical year numbering is tracked
    separately as defect GEN-2 and is deliberately NOT touched here.
    """
    for record in computed.values():
        record["gregorian_year_born"] = record["zadok_year_born"] - creation_bc
        record["gregorian_year_died"] = record["zadok_year_died"] - creation_bc


def main() -> None:
    people = load_people()
    validate(people)

    index = json.loads((GENEALOGY_DIR / "index.json").read_text(encoding="utf-8"))
    variants = index["timeline_variants"]
    scen_block = index["chronology_scenarios"]
    scenarios = scen_block["scenarios"]
    active_id = scen_block["active"]
    anchor = dict(scen_block["shared"], **scenarios[active_id])

    GENERATED_DIR.mkdir(exist_ok=True)
    summary_rows = []

    for variant_id, variant in variants.items():
        computed = walk_chain(people, variant, anchor)
        creation_bc = creation_epoch_bc(computed, anchor, variant)
        if creation_bc is not None:
            apply_epoch(computed, creation_bc)
        out_path = GENERATED_DIR / f"{variant_id}.json"
        out_path.write_text(
            json.dumps(
                {
                    "variant_id": variant_id,
                    "name": variant["name"],
                    "generated_by": "references/build/genealogy_chronology.py -- do not hand-edit",
                    "creation_bc": creation_bc,
                    "anchor_exodus_bc": anchor["anchor_exodus_bc"],
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
        flood_bc = (creation_bc - flood_year) if (creation_bc and flood_year) else None
        summary_rows.append(
            (variant_id, variant["name"], creation_bc, flood_year, flood_bc, terah_death)
        )

    print(f"Validated {len(people)} people across {len(SOURCE_FILES)} source file(s).")
    print(f"Generated {len(variants)} timeline variant(s) into {GENERATED_DIR.relative_to(REPO_ROOT)}/\n")
    print(f"Active scenario: {active_id} -- {scenarios[active_id]['name']}")
    print(f"  Exodus anchored at {anchor['anchor_exodus_bc']} BC; Nahor "
          f"{anchor['nahor_age_at_terah_birth']}; Terah+{anchor['terah_to_abram']} to Abram, "
          f"+{anchor['abram_birth_to_exodus']} to the Exodus\n")
    print(f"{'variant':<16}{'name':<30}{'creation':>10}{'flood (AM)':>12}{'flood BC':>10}{'terah died (AM)':>18}")
    for variant_id, name, creation_bc, flood_year, flood_bc, terah_death in summary_rows:
        print(f"{variant_id:<16}{name:<30}{str(creation_bc)+' BC':>10}"
              f"{str(flood_year):>12}{str(flood_bc)+' BC':>10}{str(terah_death):>18}")

    # Every tracked scenario, against the Masoretic chain, so the alternates stay visible
    # to anyone who runs this. Only the active one is written to the generated files.
    print("\nTracked scenarios (Masoretic variant):")
    print(f"  {'scenario':<24}{'Exodus':>9}{'Nahor':>7}{'creation':>11}{'AD 2026':>10}{'year 6000':>11}  status")
    mt_variant = variants["mt"]
    for sid, sc in scenarios.items():
        merged = dict(scen_block["shared"], **sc)
        computed = walk_chain(people, mt_variant, merged)
        cbc = creation_epoch_bc(computed, merged, mt_variant)
        print(f"  {sid:<24}{str(sc['anchor_exodus_bc'])+' BC':>9}"
              f"{sc['nahor_age_at_terah_birth']:>7}{str(cbc)+' BC':>11}"
              f"{'AM '+str(cbc+2025):>10}{'AD '+str(6000-cbc+1):>11}  {sc['status']}")


if __name__ == "__main__":
    main()
