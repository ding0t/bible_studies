import json

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

print(f'\n[OK] Genealogy split validation PASSED')
