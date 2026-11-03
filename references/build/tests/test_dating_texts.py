"""docs/data/dating-texts.json quotes the verse behind every number the chronology uses.

Each quote must be the BSB's own wording of the verse it names, so a misremembered number ("the
four hundred and fortieth year") or a reference pointing at the wrong verse fails here. Whether
the site's dates agree with those numbers is chronology.test.js's half.
"""
import json
from pathlib import Path

import pytest

import query
from book_map import NUM_TO_OSIS
from commentary_index import parse_reference

REGISTER = Path(__file__).resolve().parents[3] / "docs" / "data" / "dating-texts.json"
QUOTES = [(text["id"], ref, words) for text in json.loads(REGISTER.read_text(encoding="utf-8"))["texts"]
          for ref, words in text["quotes"]]


@pytest.fixture(scope="module")
def conn():
    if not query.DB_PATH.exists():
        pytest.skip("bible-text.db not built")
    return query.connect()


@pytest.mark.parametrize("entry, ref, words", QUOTES, ids=[f"{e}:{r}" for e, r, _ in QUOTES])
def test_quote_is_the_bsb_wording_of_its_verse(conn, entry, ref, words):
    book_num, chapter, display = parse_reference(ref)
    verse = int(display.split(":", 1)[1])
    text = query.lookup_verse(conn, NUM_TO_OSIS[book_num], chapter, verse, translation="berean-bsb")["text"]
    assert words in text, f"{ref} (BSB) reads: {text}"
