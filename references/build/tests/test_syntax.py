"""Syntax/coreference coverage checks for the MACULA columns in out/bible-text.db.

These guard two bugs that were both live during development and both of which fail *silently* --
returning plausible-looking empty results rather than raising:

1. The corpus-prefix mismatch. MACULA xml:ids carry a prefix ('n' Greek NT, 'o' Hebrew OT), but only
   Greek coreference pointers keep it -- Hebrew subjref/participantref drop it. Joined raw, every
   Hebrew coreference lookup returns zero rows, which reads as "the data doesn't cover this" instead
   of "the key is wrong."
2. Multi-valued pointers. subjref/referent/participantref hold a space-separated list whenever the
   reference is compound (a plural subject, a pronoun with several antecedents). Parsing the field as
   a single id silently discarded ~18k rows -- and specifically the plural subjects, which are
   exactly what someone asking "who is doing this verb" most often wants.

Row-count assertions are pinned to the TSV totals rather than to a floor, so a future ingest change
that drops rows fails here instead of degrading quietly.
"""
import sqlite3
from pathlib import Path

import pytest

import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"

GREEK = "macula-greek-sblgnt"
HEBREW = "macula-hebrew-wlc"

# Exact non-null counts in the source TSVs. Update only alongside a deliberate submodule bump.
EXPECTED = {
    GREEK: {"subject_ref": 16625, "referent": 14542, "syntactic_role": 46717},
    HEBREW: {"subject_ref": 42847, "referent": 51759, "state": 135965},
}


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


@pytest.mark.parametrize("work_id,column,expected",
                         [(w, c, n) for w, cols in EXPECTED.items() for c, n in cols.items()])
def test_syntax_column_counts(conn, work_id, column, expected):
    """Every annotated value in the TSV survives ingest -- no silent dropping."""
    got = conn.execute(
        f"SELECT COUNT({column}) FROM morphology WHERE work_id=?", (work_id,)
    ).fetchone()[0]
    assert got == expected, f"{work_id}.{column}: expected {expected} non-null rows, got {got}"


@pytest.mark.parametrize("work_id", [GREEK, HEBREW])
def test_node_ids_are_digits_only(conn, work_id):
    """node_id and pointers must be normalized, or cross-corpus joins silently miss."""
    bad = conn.execute(
        "SELECT node_id FROM morphology WHERE work_id=? AND node_id IS NOT NULL "
        "AND node_id GLOB '*[^0-9]*' LIMIT 5", (work_id,)
    ).fetchall()
    assert not bad, f"{work_id}: non-digit node_id values, e.g. {[r[0] for r in bad]}"


@pytest.mark.parametrize("work_id", [GREEK, HEBREW])
def test_pointers_resolve_to_real_words(conn, work_id):
    """Regression for bug 1: the vast majority of subject pointers must find their target.

    Not 100% -- a pointer can legitimately name a node outside the annotated corpus -- but a prefix
    mismatch drives this to zero, so anything below a high bar means the keys stopped matching.
    """
    total, resolved = conn.execute(
        "SELECT COUNT(*), SUM(EXISTS(SELECT 1 FROM morphology t "
        "                            WHERE t.work_id=m.work_id AND t.node_id=m.subject_ref)) "
        "FROM morphology m WHERE m.work_id=? AND m.subject_ref IS NOT NULL "
        "AND instr(m.subject_ref,' ')=0", (work_id,)
    ).fetchone()
    assert total > 1000, f"{work_id}: too few single-target subject pointers to be meaningful"
    assert resolved / total > 0.95, f"{work_id}: only {resolved}/{total} subject pointers resolve"


@pytest.mark.parametrize("work_id,minimum", [(GREEK, 1500), (HEBREW, 3500)])
def test_multi_target_pointers_are_preserved(conn, work_id, minimum):
    """Regression for bug 2: compound references must survive as space-separated lists."""
    count = conn.execute(
        "SELECT COUNT(*) FROM morphology WHERE work_id=? AND instr(subject_ref,' ')>0", (work_id,)
    ).fetchone()[0]
    assert count >= minimum, f"{work_id}: only {count} multi-target subject pointers (expected >={minimum})"


def test_lookup_syntax_resolves_implicit_subject_across_verses(conn):
    """The headline capability: a Greek verb with no stated subject resolves to an earlier verse.

    Mark 6:41's participles carry Jesus as their subject from Mark 6:30 -- eleven verses back, with
    no repeated noun in between. Morphology alone cannot answer this.
    """
    result = query.lookup_syntax(conn, "Mark", 6, 41, work_id=GREEK)
    verbs = [w for w in result["words"] if w["word_class"] == "verb" and w.get("subject")]
    assert verbs, "expected at least one verb with a resolved subject in Mark 6:41"

    subjects = [t for w in verbs for t in w["subject"]]
    assert all(isinstance(w["subject"], list) for w in verbs), "subject must always be a list"
    assert any(t["chapter"] == 6 and t["verse"] < 41 for t in subjects), \
        "expected an antecedent in an earlier verse, not only within 6:41"
    assert any("Jesus" in (t["gloss"] or "") for t in subjects), \
        f"expected Jesus as subject, got {[t['gloss'] for t in subjects]}"


def test_hebrew_state_and_conjugation_present(conn):
    """Hebrew-only fields that carry real exegetical weight: construct chains and conjugation."""
    row = conn.execute(
        "SELECT COUNT(DISTINCT state) states, COUNT(DISTINCT sub_type) types FROM morphology "
        "WHERE work_id=?", (HEBREW,)
    ).fetchone()
    assert row["states"] >= 3, "expected absolute/construct/determined in Hebrew state"
    conjugations = {r[0] for r in conn.execute(
        "SELECT DISTINCT sub_type FROM morphology WHERE work_id=? AND sub_type IS NOT NULL", (HEBREW,)
    )}
    for expected in ("qatal", "wayyiqtol", "yiqtol"):
        assert expected in conjugations, f"missing Hebrew conjugation '{expected}' in sub_type"


def test_no_syntax_on_translation_works(conn):
    """Syntax is original-language only -- an English work must not acquire these fields."""
    count = conn.execute(
        "SELECT COUNT(*) FROM morphology WHERE work_id NOT LIKE 'macula%' AND node_id IS NOT NULL"
    ).fetchone()[0]
    assert count == 0, f"{count} non-MACULA rows carry a node_id"


def test_lookup_syntax_warns_when_unannotated(conn):
    """An English-only reference must return a warning, not a bare empty list."""
    result = query.lookup_syntax(conn, "Gen", 1, 1, work_id="scrollmapper-KJV")
    assert result["words"] == []
    assert "warning" in result
