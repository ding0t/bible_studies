"""commentary_index.py turns frontmatter references into commentary chapter pages.

Written after "Jude 12" in a study's bible_references was read as Jude chapter 12, and five pages
for chapters Jude does not have shipped on the site. Nothing failed: the pages built, linked and
looked like any other chapter page.
"""
import sqlite3
from pathlib import Path

import pytest

from book_map import NUM_TO_OSIS
from commentary_index import CHAPTER_COUNTS, COMMENTARIES_DIR, parse_reference

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.mark.parametrize("ref, expected", [
    ("Jude 12", (65, 1, "1:12")),
    ("Jude 3-4", (65, 1, "1:3-4")),
    ("Jude 1:3-4", (65, 1, "1:3-4")),
    ("Jude 1", (65, 1, "1")),
    ("3 John 9-11", (64, 1, "1:9-11")),
    ("Philemon 10", (57, 1, "1:10")),
    ("Obadiah 15", (31, 1, "1:15")),
    ("Mark 5:25-34", (41, 5, "5:25-34")),
    ("Leviticus 23", (3, 23, "23")),
])
def test_parses_references(ref, expected):
    assert parse_reference(ref) == expected


@pytest.mark.parametrize("ref", ["Leviticus 23-25", "Jude 2:1", "Psalm 151", "Malachi 5"])
def test_rejects_ranges_across_chapters_and_chapters_a_book_lacks(ref):
    assert parse_reference(ref) is None


def test_no_chapter_page_past_the_end_of_its_book():
    stray = []
    for book_num, count in CHAPTER_COUNTS.items():
        for book_dir in COMMENTARIES_DIR.glob(f"{book_num:02d}-*"):
            for page in book_dir.glob("chapter-*.md"):
                if int(page.stem.split("-", 1)[1]) > count:
                    stray.append(str(page.relative_to(COMMENTARIES_DIR)))
    assert not stray, f"chapter pages for chapters these books do not have: {stray}"


def test_chapter_counts_match_the_web():
    if not DB_PATH.exists():
        pytest.skip("out/bible-text.db not built")
    conn = sqlite3.connect(f"file:{DB_PATH}?immutable=1", uri=True)
    in_db = dict(conn.execute(
        "SELECT book, MAX(chapter) FROM verses WHERE work_id = 'ebible-eng-web' GROUP BY book"))
    conn.close()
    assert {num: in_db.get(NUM_TO_OSIS[num]) for num in CHAPTER_COUNTS} == CHAPTER_COUNTS
