import glob
import json

# Fields the genealogy viewer reads off a person. Split by where they come from, because the
# viewer's three worst bugs to date all came from assuming this data is uniform when it is not:
#
#   * a children id naming someone with no record (fixed f655c51)
#   * major_events absent on all 20 antediluvian/patriarchal figures, which crashed the detail
#     panel the moment one of them was selected (fixed 4d7c5e0)
#   * year fields absent for a person the active chronology variant doesn't cover, which turned
#     the gantt chart's axis bounds into NaN and rendered an empty chart (fixed e6c0f67)
#
# So: REQUIRED is what every person must carry; VARIANT_SUPPLIED comes from the generated variant
# files rather than the era files and is checked per variant; OPTIONAL is genuinely era-dependent
# and reported as coverage, not as a problem. Add to these lists when a component starts reading a
# new field -- that is the point of them.
REQUIRED_FIELDS = ['id', 'name', 'parent_id', 'children', 'tags', 'bible_references', 'lineages']
VARIANT_SUPPLIED = ['gregorian_year_born', 'gregorian_year_died', 'lifespan_years']
OPTIONAL_FIELDS = ['major_events', 'name_hebrew', 'name_meaning', 'name_transliteration']

# Load all era files
files = [
    'docs/data/genealogy/antediluvian.json',
    'docs/data/genealogy/patriarchal.json',
    'docs/data/genealogy/conquest-judges.json',
    'docs/data/genealogy/divided-kingdom.json',
    'docs/data/genealogy/exile-return.json',
    'docs/data/genealogy/second-temple.json'
]

total_people = 0
people_ids = set()
parent_links = []
child_links = []
all_people = {}

# Non-zero only for genuine data errors -- a missing required field. The dangling-link and
# coverage reports are warnings: a children list naming someone outside the covenant line, or an
# era with no major_events, is legitimate content that components must simply guard against.
exit_code = 0

print("Era File Summary:")
print("-" * 50)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    filename = file.split('/')[-1]
    print(f'[OK] {filename:30} {len(data["people"]):2} people')
    
    for person in data['people']:
        total_people += 1
        people_ids.add(person['id'])
        all_people[person['id']] = person
        if person['parent_id']:
            parent_links.append((person['id'], person['parent_id']))
        for child_id in person.get('children', []):
            child_links.append((person['id'], child_id))

print("-" * 50)
print(f'Total people: {total_people}')
print(f'Unique person IDs: {len(people_ids)}')

# Check parent links
missing_parents = []
for child_id, parent_id in parent_links:
    if parent_id not in people_ids:
        missing_parents.append((child_id, parent_id))

if missing_parents:
    print(f'\n[WARN] Warning: {len(missing_parents)} broken parent links')
    for child, parent in missing_parents[:5]:
        print(f'  {child} -> {parent} (missing)')
else:
    print('\n[OK] All parent-child links valid')

# Check children lists. This ran only in the parent_id direction until 2026-08-23, and the gap
# was not cosmetic: 37 children ids named nobody in the dataset, and because the tree viewer
# resolved each id to a person object without checking the result, an unresolved id became an
# undefined array element that threw on render. The viewer expands noah and abraham by default
# and both have unresolved children, so the whole component crashed on load.
#
# A dangling child id is legitimate content, not necessarily a mistake -- Noah's line names Ham
# and Japheth while only Shem's descendants are recorded -- so this is a warning. The viewer now
# filters unresolved ids out and shows the branches it does have.
missing_children = []
for parent_id, child_id in child_links:
    if child_id not in people_ids:
        missing_children.append((parent_id, child_id))

if missing_children:
    print(f'\n[WARN] Warning: {len(missing_children)} children ids with no person record')
    for parent, child in missing_children[:5]:
        print(f'  {parent} -> {child} (missing)')
    if len(missing_children) > 5:
        print(f'  ... and {len(missing_children) - 5} more')
else:
    print('[OK] All children ids resolve to a person')

# Check required fields. These are the ones the viewer reads without a guard being reasonable --
# a person with no name or no children list is a data error, not an era difference.
missing_required = [
    (pid, f) for pid, person in sorted(all_people.items())
    for f in REQUIRED_FIELDS if f not in person
]
if missing_required:
    print(f'\n[FAIL] {len(missing_required)} missing required field(s)')
    for pid, f in missing_required[:10]:
        print(f'  {pid} has no {f}')
    exit_code = 1
else:
    print(f'[OK] All {total_people} people carry every required field')

# Report optional-field coverage. Not a failure: major_events is genuinely absent for the
# antediluvian and patriarchal figures. It is here so the non-uniformity is visible on the page
# rather than discovered when a component reads one of these without a guard.
print('\n[INFO] Optional field coverage (absence is legitimate; guard these in components)')
for f in OPTIONAL_FIELDS:
    have = sum(1 for person in all_people.values() if f in person)
    if have < total_people:
        print(f'  {f:<22} {have:>2}/{total_people}  absent on {total_people - have}')

# Check chronology-variant coverage. The era files carry no years for the antediluvian and
# patriarchal figures; those come from docs/data/genealogy/generated/<variant>.json, merged in by
# mergePeopleWithVariant. A person the active variant does not cover therefore reaches the viewer
# with *undefined* year fields -- which is not null, so a `!== null` guard lets it through, and
# one undefined in Math.min() makes the gantt chart's whole axis NaN.
print('\n[INFO] Chronology-variant year coverage')
needs_variant = sorted(
    pid for pid, person in all_people.items()
    if any(f not in person for f in VARIANT_SUPPLIED)
)
for path in sorted(glob.glob('docs/data/genealogy/generated/*.json')):
    variant = json.load(open(path, encoding='utf-8'))
    covered = variant.get('people', {})
    gaps = [pid for pid in needs_variant if pid not in covered]
    name = path.split('/')[-1].replace('.json', '')
    if gaps:
        print(f'  [WARN] {name:<16} no years for: {", ".join(gaps)}')
    else:
        print(f'  [OK]   {name:<16} covers all {len(needs_variant)} people who need it')

if exit_code:
    print('\n[FAIL] Genealogy validation FAILED')
else:
    print('\n[OK] Genealogy split validation PASSED')
raise SystemExit(exit_code)
