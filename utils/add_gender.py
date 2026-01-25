import json
import os

# Gender mapping for all people
GENDER_MAP = {
    # Antediluvian
    "adam": "male",
    "eve": "female",
    "cain": "male",
    "abel": "male",
    "seth": "male",
    "enosh": "male",
    "cainan": "male",
    "mahalalel": "male",
    "jared": "male",
    "enoch": "male",
    "methuselah": "male",
    "lamech": "male",
    "noah": "male",
    
    # Patriarchal
    "shem": "male",
    "arphaxad": "male",
    "shelah": "male",
    "eber": "male",
    "peleg": "male",
    "reu": "male",
    "serug": "male",
    "nahor": "male",
    "terah": "male",
    "abraham": "male",
    "sarah": "female",
    "isaac": "male",
    "rebekah": "female",
    "jacob": "male",
    "rachel": "female",
    "judah": "male",
    "leah": "female",
    "perez": "male",
    "tamar": "female",
    
    # Conquest/Judges
    "hezron": "male",
    "ram": "male",
    "amminadab": "male",
    "nahshon": "male",
    "elisheba": "female",
    "salmon": "male",
    "rahab": "female",
    "boaz": "male",
    "ruth": "female",
    "obed": "male",
    "jesse": "male",
    "david": "male",
    "bathsheba": "female",
    "solomon": "male",
    
    # Divided Kingdom
    "rehoboam": "male",
    "abijah": "male",
    "asa": "male",
    "jehoshaphat": "male",
    "jehoram": "male",
    "ahaziah": "male",
    "joast": "male",
    "amaziah": "male",
    "uzziah": "male",
    "jotham": "male",
    "ahaz": "male",
    "hezekiah": "male",
    "manasseh": "male",
    "amon": "male",
    "josiah": "male",
    
    # Exile/Return
    "jehoiakim": "male",
    "jehoiachin": "male",
    "shealtiel": "male",
    "zerubbabel": "male",
    
    # Second Temple
    "abiud": "male",
    "eliakim_3": "male",
    "azor": "male",
    "sadoc": "male",
    "achim": "male",
    "eliud": "male",
    "eleazar_2": "male",
    "matthan": "male",
    "jacob_2": "male",
    "joseph": "male",
    "mary": "female",
    "jesus": "male",
}

def add_gender_to_genealogy():
    """Add gender field to all genealogy files"""
    genealogy_dir = 'docs/data/genealogy'
    era_files = [
        'antediluvian.json',
        'patriarchal.json',
        'conquest-judges.json',
        'divided-kingdom.json',
        'exile-return.json',
        'second-temple.json'
    ]
    
    for filename in era_files:
        filepath = os.path.join(genealogy_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        for person in data['people']:
            person_id = person['id']
            
            if person_id in GENDER_MAP:
                person['gender'] = GENDER_MAP[person_id]
                updated_count += 1
            else:
                # Default to unknown if not in map
                person['gender'] = 'unknown'
                print(f"  Warning: {person_id} not in gender map")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Updated {filename}: {updated_count} people with gender")

if __name__ == '__main__':
    add_gender_to_genealogy()
    print("\n✓ Gender added to all genealogy files")
