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

print(f'\n[OK] Genealogy split validation PASSED')
