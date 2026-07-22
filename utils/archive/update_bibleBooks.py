#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Bible book names mapping
BIBLE_BOOKS = {
    '01': 'Genesis', '02': 'Exodus', '03': 'Leviticus', '04': 'Numbers',
    '05': 'Deuteronomy', '06': 'Joshua', '07': 'Judges', '08': 'Ruth',
    '09': '1 Samuel', '10': '2 Samuel', '11': '1 Kings', '12': '2 Kings',
    '13': '1 Chronicles', '14': '2 Chronicles', '15': 'Ezra', '16': 'Nehemiah',
    '17': 'Esther', '18': 'Job', '19': 'Psalms', '20': 'Proverbs',
    '21': 'Ecclesiastes', '22': 'Song of Solomon', '23': 'Isaiah', '24': 'Jeremiah',
    '25': 'Lamentations', '26': 'Ezekiel', '27': 'Daniel', '28': 'Hosea',
    '29': 'Joel', '30': 'Amos', '31': 'Obadiah', '32': 'Jonah',
    '33': 'Micah', '34': 'Nahum', '35': 'Habakkuk', '36': 'Zephaniah',
    '37': 'Haggai', '38': 'Zechariah', '39': 'Malachi', '40': 'Matthew',
    '41': 'Mark', '42': 'Luke', '43': 'John', '44': 'Acts',
    '45': 'Romans', '46': '1 Corinthians', '47': '2 Corinthians', '48': 'Galatians',
    '49': 'Ephesians', '50': 'Philippians', '51': 'Colossians',
    '52': '1 Thessalonians', '53': '2 Thessalonians', '54': '1 Timothy',
    '55': '2 Timothy', '56': 'Titus', '57': 'Philemon', '58': 'Hebrews',
    '59': 'James', '60': '1 Peter', '61': '2 Peter', '62': '1 John',
    '63': '2 John', '64': '3 John', '65': 'Jude', '66': 'Revelation'
}

def categorize_book(num):
    """Determine if book is OT, NT, or prophecy"""
    n = int(num)
    if n <= 39:
        if n in [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]:
            return 'prophecy'
        return 'other'
    else:
        if n == 66:
            return 'prophecy'
        return 'other'

def update_file(filepath):
    """Update a single bible book file with full frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract book number from filename
    match = re.match(r'(\d{2})_', os.path.basename(filepath))
    if not match:
        return False
    
    book_num = match.group(1)
    book_name = BIBLE_BOOKS.get(book_num, 'Bible')
    category = categorize_book(book_num)
    
    # Create title with number prefix for ordering
    title_with_num = f"{book_num} {book_name}"
    
    # Create new frontmatter
    is_ot = int(book_num) <= 39
    tags = ["bible", "ot" if is_ot else "nt"]
    if category == "prophecy":
        tags.insert(0, "prophecy")
    
    new_frontmatter = f"""---
title: "{title_with_num}"
category: "{category}"
description: "Study resources for the Book of {book_name}"
tags: {str(tags).replace("'", '"')}
draft: false
---"""
    
    # Replace old frontmatter
    new_content = re.sub(
        r'^---\n.*?\n---',
        new_frontmatter,
        content,
        count=1,
        flags=re.DOTALL
    )
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# Main execution - update both template and by_book directories
updated = 0
failed = 0

for template_dir in [
    Path("c:/Users/david/OneDrive/code/gh_ding0t/bible_end_times/docs/bible/templates"),
    Path("c:/Users/david/OneDrive/code/gh_ding0t/bible_end_times/docs/bible/by_book")
]:
    for filepath in sorted(template_dir.glob("*.md")):
        if filepath.name[0].isdigit():
            try:
                if update_file(str(filepath)):
                    updated += 1
                    print(f"✓ Updated {filepath.name}")
                else:
                    failed += 1
                    print(f"✗ Failed {filepath.name}")
            except Exception as e:
                failed += 1
                print(f"✗ Error in {filepath.name}: {e}")

print(f"\nCompleted: {updated} updated, {failed} failed")
