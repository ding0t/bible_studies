import json
import os

# Hebrew names and meanings reference
HEBREW_NAMES = {
    "adam": {
        "hebrew": "אָדָם",
        "transliteration": "Adam",
        "meaning": "Man, mankind; from 'adamah' (earth/ground)"
    },
    "eve": {
        "hebrew": "חַוָּה",
        "transliteration": "Chavah",
        "meaning": "Life; she gives life (mother of all living)"
    },
    "cain": {
        "hebrew": "קַיִן",
        "transliteration": "Qayin",
        "meaning": "Acquisition, possession; related to 'kanah' (to obtain)"
    },
    "abel": {
        "hebrew": "הָבֶל",
        "transliteration": "Hevel",
        "meaning": "Breath, vapor, emptiness; transience of life"
    },
    "seth": {
        "hebrew": "שֵׁת",
        "transliteration": "Shet",
        "meaning": "Appointed, placed; from 'shith' (to put, place)"
    },
    "enosh": {
        "hebrew": "אֱנוֹשׁ",
        "transliteration": "Enosh",
        "meaning": "Man, mortal man; from 'anash' (to be weak, mortal)"
    },
    "cainan": {
        "hebrew": "קֵינָן",
        "transliteration": "Qenan",
        "meaning": "Possessor; variant of Cain"
    },
    "mahalalel": {
        "hebrew": "מַהֲלַלְאֵל",
        "transliteration": "Mahalalel",
        "meaning": "Praise of God; from 'hallal' (praise) and 'El' (God)"
    },
    "jared": {
        "hebrew": "יָרֶד",
        "transliteration": "Yared",
        "meaning": "Descend; from 'yarad' (to descend)"
    },
    "enoch": {
        "hebrew": "חֲנוֹךְ",
        "transliteration": "Chanoch",
        "meaning": "Initiated, dedicated; from 'chanach' (to train, dedicate)"
    },
    "methuselah": {
        "hebrew": "מְתוּשֶׁלַח",
        "transliteration": "Metushelach",
        "meaning": "Man of the javelin; or 'when he dies, it shall be sent' (prophetic of flood)"
    },
    "lamech": {
        "hebrew": "לֶמֶךְ",
        "transliteration": "Lemech",
        "meaning": "Powerful, strong; possibly related to 'lamak' (to be weak) - ironic"
    },
    "noah": {
        "hebrew": "נֹחַ",
        "transliteration": "Noah",
        "meaning": "Rest, comfort; from 'nacham' (to comfort, rest)"
    },
    "shem": {
        "hebrew": "שֵׁם",
        "transliteration": "Shem",
        "meaning": "Name, renown; from 'shem' (name, fame)"
    },
    "abraham": {
        "hebrew": "אַבְרָהָם",
        "transliteration": "Avraham",
        "meaning": "Father of multitude; from 'av' (father) and 'hamon' (multitude)"
    },
    "sarah": {
        "hebrew": "שָׂרָה",
        "transliteration": "Sarah",
        "meaning": "Princess; from 'sar' (prince, ruler)"
    },
    "isaac": {
        "hebrew": "יִצְחָק",
        "transliteration": "Yitzhak",
        "meaning": "He laughs; from 'tzachak' (to laugh)"
    },
    "rebekah": {
        "hebrew": "רִבְקָה",
        "transliteration": "Rivka",
        "meaning": "To bind, join; possibly from 'ribka' (to tie, bind)"
    },
    "jacob": {
        "hebrew": "יַעֲקֹב",
        "transliteration": "Yaakov",
        "meaning": "Heel-grabber, supplanter; from 'akev' (heel) and 'akab' (to supplant)"
    },
    "rachel": {
        "hebrew": "רָחֵל",
        "transliteration": "Rachel",
        "meaning": "Ewe (female sheep); from 'rachel' (ewe, gentleness)"
    },
    "leah": {
        "hebrew": "לֵאָה",
        "transliteration": "Leah",
        "meaning": "Weary, tired; possibly from 'la'ah' (to be weary)"
    },
    "judah": {
        "hebrew": "יְהוּדָה",
        "transliteration": "Yehudah",
        "meaning": "Praise of the Lord; from 'yadah' (to praise) and 'Yah' (God)"
    },
    "perez": {
        "hebrew": "פֶּרֶץ",
        "transliteration": "Perez",
        "meaning": "Breaking forth; from 'paraz' (to break out, break through)"
    },
    "tamar": {
        "hebrew": "תָּמָר",
        "transliteration": "Tamar",
        "meaning": "Palm tree; from 'tamar' (palm tree, upright, graceful)"
    },
    "david": {
        "hebrew": "דָּוִד",
        "transliteration": "David",
        "meaning": "Beloved; from 'dod' (beloved, uncle) or 'david' (friend)"
    },
    "bathsheba": {
        "hebrew": "בַּת־שֶׁבַע",
        "transliteration": "Bat-Sheva",
        "meaning": "Daughter of the oath; from 'bat' (daughter) and 'sheba' (oath)"
    },
    "solomon": {
        "hebrew": "שְׁלֹמֹה",
        "transliteration": "Shlomo",
        "meaning": "Peaceful; from 'shalom' (peace)"
    },
    "jesus": {
        "hebrew": "יֵשׁוּעַ",
        "transliteration": "Yeshua",
        "meaning": "The Lord is salvation; from 'yasha' (to save) and 'Yah' (God)"
    },
    "mary": {
        "hebrew": "מִרְיָם",
        "transliteration": "Miryam",
        "meaning": "Rebellion, star of the sea; possibly from 'marah' (bitter) or Latin 'mare' (sea)"
    },
    "joseph": {
        "hebrew": "יוֹסֵף",
        "transliteration": "Yosef",
        "meaning": "He shall add; from 'yasaf' (to add, increase)"
    }
}

def add_hebrew_names_to_genealogy():
    """Add Hebrew names and meanings to all genealogy files"""
    genealogy_dir = 'src/data/genealogy'
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
            
            if person_id in HEBREW_NAMES:
                name_info = HEBREW_NAMES[person_id]
                person['name_hebrew'] = name_info['hebrew']
                person['name_transliteration'] = name_info['transliteration']
                person['name_meaning'] = name_info['meaning']
                updated_count += 1
            else:
                # Add empty fields for those without Hebrew data yet
                person['name_hebrew'] = ""
                person['name_transliteration'] = person['name']
                person['name_meaning'] = ""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Updated {filename}: {updated_count} people with Hebrew names")

if __name__ == '__main__':
    add_hebrew_names_to_genealogy()
    print("\n✓ Hebrew names added to all genealogy files")
