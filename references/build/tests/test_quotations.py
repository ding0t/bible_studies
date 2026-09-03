"""New Testament quotations of the Septuagint, derived by quotations.py.

This is the first table the repo computes for itself rather than ingesting, so the risk is
different: nothing upstream will fail loudly if the derivation silently degrades. These pin the
method's behaviour, the specific quotations it must find, and the properties the generator has to
keep -- determinism above all, because it feeds content and a re-run that differs makes a diff
unreviewable.
"""
import sqlite3
from pathlib import Path

import pytest

import quotations
import query

DB_PATH = Path(__file__).parent.parent / "out" / "bible-text.db"


@pytest.fixture(scope="module")
def conn():
    if not DB_PATH.exists():
        pytest.skip(f"{DB_PATH} not built -- run `uv run python build.py` first")
    connection = query.connect()
    yield connection
    connection.close()


# --- the method ------------------------------------------------------------------------------

def test_accents_are_stripped_before_matching():
    """Brenton (1851) and the SBLGNT accent differently, so unnormalised surface forms fail to
    match on identical words -- which would sink the whole approach."""
    brenton = quotations.normalise("Πνεῦμα Κυρίου ἐπʼ ἐμὲ, οὗ εἵνεκε ἔχρισέν με")
    sblgnt = quotations.normalise("Πνεῦμα κυρίου ἐπʼ ἐμέ, οὗ εἵνεκεν ἔχρισέν με")
    assert brenton[:4] == sblgnt[:4]


def test_longest_shared_run_measures_a_contiguous_span():
    assert quotations.longest_shared_run(list("abcd"), list("xabc")) == 3
    assert quotations.longest_shared_run(list("abcd"), list("axcx")) == 1
    assert quotations.longest_shared_run(list("abc"), list("xyz")) == 0


def test_generator_output_is_deterministic():
    """Candidates are ranked without reference to how the index iterated. The earlier version took
    the best four per verse, which broke ties on set iteration order and returned a different set
    each run -- while discarding 27% of qualifying pairs."""
    source = [("Isa", 61, 1, "Πνεῦμα Κυρίου ἐπʼ ἐμὲ οὗ εἵνεκε ἔχρισέν με εὐαγγελίσασθαι πτωχοῖς"),
              ("Ps", 39, 7, "Θυσίαν καὶ προσφορὰν οὐκ ἠθέλησας σῶμα δὲ κατηρτίσω μοι")]
    quoting = [("Luke", 4, 18, "Πνεῦμα κυρίου ἐπʼ ἐμέ οὗ εἵνεκεν ἔχρισέν με εὐαγγελίσασθαι πτωχοῖς")]
    tokens, index = quotations.build_index(source)
    runs = [list(quotations.find_quotations(quoting, tokens, index)) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert runs[0], "expected Luke 4:18 to match Isaiah 61:1"


# --- what the corpus must contain ---------------------------------------------------------------

@pytest.mark.parametrize("nt,ot,least_alignment", [
    (("Heb", 10, 5), ("Ps", 40, 6), 18),     # "a body you have prepared for me"
    (("Acts", 8, 33), ("Isa", 53, 8), 30),   # the Ethiopian's scroll
    (("Heb", 3, 15), ("Ps", 95, 8), 25),
    (("Gal", 4, 27), ("Isa", 54, 1), 40),
    (("Rom", 10, 18), ("Ps", 19, 4), 25),
    (("Heb", 8, 9), ("Jer", 31, 32), 30),    # the new covenant, LXX Jeremiah 38
    # the ones a contiguous run misses outright, recovered by local alignment
    (("Matt", 1, 23), ("Isa", 7, 14), 18),   # the virgin shall conceive -- run of only 5
    (("Luke", 4, 18), ("Isa", 61, 1), 18),   # Luke omits a clause -- run of only 6
    (("Acts", 13, 41), ("Hab", 1, 5), 25),   # run of only 7
])
def test_known_quotations_are_found_with_the_right_english_reference(conn, nt, ot, least_alignment):
    """The English reference is stored alongside, so a caller need not re-align -- and it has to be
    right at the verse, not just the chapter. Hebrews 10:5's source is Psalm 40:6, not 40:7."""
    result = query.lookup_links(conn, *nt, link_type="quotation-greek")
    matches = [q for q in result["links_from"].get("quotation-greek", [])
               if q["to_book"] == ot[0] and q["to_english_chapter"] == ot[1]
               and q["to_english_verse"] == ot[2]]
    assert matches, f"{nt} -> {ot} not found"
    assert max(q["alignment"] for q in matches) >= least_alignment


def test_reverse_direction_finds_who_quotes_a_passage(conn):
    """An Old Testament reference is given as an English Bible numbers it and aligned into the
    Septuagint's own numbering before lookup."""
    result = query.lookup_links(conn, "Ps", 95, 8, link_type="quotation-greek")
    assert result["aligned_as"]["quotation-greek"] == "Ps 94:8"
    quoters = {(q["from_book"], q["from_chapter"]) for q in result["links_to"]["quotation-greek"]}
    assert ("Heb", 3) in quoters


def test_strength_grading_separates_quotation_from_formula(conn):
    """The audit that set the threshold: corroboration by openbible's independent cross-references
    is several times higher at a strong alignment than a weak one. If that separation collapses,
    the grading has stopped meaning anything and the threshold is arbitrary again."""
    def corroboration(low, high):
        return conn.execute(
            "SELECT AVG(corroborated) r FROM scripture_links WHERE link_type='quotation-greek' "
            "AND alignment BETWEEN ? AND ?", (low, high)).fetchone()["r"]
    assert corroboration(20, 9999) > 0.75
    assert corroboration(10, 14) < 0.25


def test_local_alignment_outranks_a_contiguous_run(conn):
    """Why alignment is the primary measure. These are real quotations that adapt their source, so
    the run breaks at the edit and scores under the old threshold of 8 -- while aligning well above
    the new one. Matthew 1:23 quoting Isaiah 7:14 is the starkest: a run of 5."""
    for (nt_book, nt_ch, nt_v), (ot_book, ot_ch) in [
        (("Matt", 1, 23), ("Isa", 7)), (("Luke", 4, 18), ("Isa", 61)),
        (("Acts", 13, 41), ("Hab", 1)),
    ]:
        row = conn.execute(
            "SELECT longest_run, alignment, corroborated FROM scripture_links "
            "WHERE link_type='quotation-greek' AND from_book=? AND from_chapter=? AND from_verse=? "
            "AND to_book=? AND to_english_chapter=?",
            (nt_book, nt_ch, nt_v, ot_book, ot_ch)).fetchone()
        assert row, f"{nt_book} {nt_ch}:{nt_v} -> {ot_book} {ot_ch} missing"
        assert row["longest_run"] < quotations.QUOTATION_RUN
        assert row["alignment"] >= quotations.QUOTATION_ALIGNMENT
        assert row["corroborated"], "an independent source should back these"


def test_idf_weighting_discounts_common_phrasing(conn):
    """A shared 'and it came to pass' must not score like a shared rare phrase."""
    rare, common = conn.execute(
        "SELECT AVG(CASE WHEN corroborated THEN idf_overlap END), "
        "       AVG(CASE WHEN NOT corroborated THEN idf_overlap END) "
        "FROM scripture_links WHERE link_type='quotation-greek'").fetchone()
    assert rare > common


def test_uncorroborated_strong_quotations_exist(conn):
    """The value-add. A strong verbatim run that no cross-reference list carries is a quotation the
    tradition missed -- if this ever hits zero, the method has stopped adding anything."""
    n = conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='quotation-greek' "
        "AND alignment >= ? AND corroborated = 0", (quotations.QUOTATION_ALIGNMENT,)).fetchone()["n"]
    assert n > 10


def test_no_pair_points_at_an_unmapped_passage_with_an_english_reference(conn):
    """LXX Jeremiah 30 and the Proverbs 24 tail have no English counterpart. Those pairs must carry
    a NULL rather than an invented reference."""
    bad = conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='quotation-greek' "
        "AND to_english_chapter IS NOT NULL "
        "AND ((to_book='Jer' AND to_chapter=30) OR (to_book='Prov' AND to_chapter=24 AND to_verse>=35))"
    ).fetchone()["n"]
    assert bad == 0


# --- the gap detector -------------------------------------------------------------------------

def test_gap_detector_finds_a_real_omission(conn):
    """The gate the backlog sets: if it doesn't change a study, the rest isn't worth building.
    'The Way' cites Hebrews 3 and never Psalm 95 -- which Hebrews 3 quotes three times."""
    import study_gaps

    path = study_gaps.REPO_ROOT / "docs/content/jesus/the-way.md"
    if not path.is_file():
        pytest.skip("study not present")
    _, chapters, _ = study_gaps.study_references(path)
    assert ("Heb", 3) in chapters and ("Ps", 95) not in chapters
    ranked = study_gaps.gaps_for(conn, chapters)
    top = ranked[0]
    assert (top["book"], top["chapter"]) == ("Ps", 95)
    assert top["quotation"] >= 3


def test_gap_detector_never_reports_a_chapter_the_study_already_cites(conn):
    import study_gaps

    path = study_gaps.REPO_ROOT / "docs/content/last-things/rapture.md"
    if not path.is_file():
        pytest.skip("study not present")
    _, chapters, _ = study_gaps.study_references(path)
    reported = {(e["book"], e["chapter"]) for e in study_gaps.gaps_for(conn, chapters)}
    assert not (reported & chapters)


def test_gap_detector_ranks_quotations_above_bare_cross_references(conn):
    """The two kinds are not equivalent evidence and must not be merged into one score."""
    import study_gaps

    path = study_gaps.REPO_ROOT / "docs/content/last-things/rapture.md"
    if not path.is_file():
        pytest.skip("study not present")
    _, chapters, _ = study_gaps.study_references(path)
    ranked = study_gaps.gaps_for(conn, chapters)
    first_without = next(i for i, e in enumerate(ranked) if not e["quotation"])
    assert all(e["quotation"] for e in ranked[:first_without])


# --- inner-biblical: the Hebrew Old Testament quoting itself -----------------------------------
# Same language, same corpus, no translation between the two sides -- as strong as the Greek class.
# The method has to rediscover the canonical parallels without being told they exist.

@pytest.mark.parametrize("a,b,least,label", [
    (("2Kgs", 19), ("Isa", 37), 8, "the Hezekiah narrative, duplicated in Kings and Isaiah"),
    (("2Kgs", 18), ("Isa", 36), 4, "the same narrative, earlier"),
    (("Deut", 5), ("Exod", 20), 3, "the Decalogue"),
    (("2Chr", 25), ("2Kgs", 14), 1, "the thistle and the cedar"),
])
def test_inner_biblical_finds_the_canonical_parallels(conn, a, b, least, label):
    n = conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='inner-biblical' "
        "AND ((from_book=? AND from_chapter=? AND to_book=? AND to_chapter=?) "
        "  OR (from_book=? AND from_chapter=? AND to_book=? AND to_chapter=?))",
        (*a, *b, *b, *a)).fetchone()["n"]
    assert n >= least, label


def test_inner_biblical_excludes_a_verse_resembling_its_own_neighbours(conn):
    """Continuous prose repeats itself locally; that is style, not citation."""
    bad = conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='inner-biblical' "
        "AND from_book = to_book AND ABS(from_chapter - to_chapter) <= 1").fetchone()["n"]
    assert bad == 0


def test_inner_biblical_stores_each_pair_once(conn):
    """The relation is symmetric. Storing both directions would double every count downstream."""
    rows = conn.execute(
        "SELECT from_book, from_chapter, from_verse, to_book, to_chapter, to_verse "
        "FROM scripture_links WHERE link_type='inner-biblical'").fetchall()
    keys = {tuple(sorted([(r[0], r[1], r[2]), (r[3], r[4], r[5])])) for r in rows}
    assert len(keys) == len(rows)


# --- the Hebrew New Testament class: candidates, and complementary --------------------------

def test_hebrew_class_catches_a_quotation_the_greek_misses(conn):
    """Matthew 21:5 quotes Zechariah 9:9 -- Matthew there follows the Hebrew more closely than the
    Septuagint, so the Greek run is weak and the Hebrew New Testament catches it. That complementary
    reach is the whole reason this class exists."""
    hebrew = conn.execute(
        "SELECT alignment FROM scripture_links WHERE link_type='quotation-hebrew' "
        "AND from_book='Matt' AND from_chapter=21 AND to_book='Zech' AND to_chapter=9").fetchone()
    assert hebrew and hebrew["alignment"] >= quotations.QUOTATION_ALIGNMENT
    greek = conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='quotation-greek' "
        "AND from_book='Matt' AND from_chapter=21 AND to_book='Zech' "
        "AND alignment >= ?", (quotations.QUOTATION_ALIGNMENT,)).fetchone()
    assert greek["n"] == 0


def test_hebrew_normalisation_joins_morphemes_rather_than_splitting(conn):
    """The WLC marks morpheme boundaries and the Hebrew New Testaments do not, so splitting on the
    separator compares tokens that can never match. It scored 12% recall against the Greek-derived
    quotations; joining scores 81%."""
    assert quotations.normalise_hebrew("וַ/יְהִ֖י") == quotations.normalise_hebrew("ויהי")
    assert conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='quotation-hebrew'"
    ).fetchone()["n"] > 40


def test_classes_are_stored_separately_and_never_merged(conn):
    """The discipline the backlog sets: a quotation in Greek is a textual fact, a Hebrew New
    Testament match is a translator's judgement, and nothing may collapse them into one score."""
    kinds = {r["link_type"] for r in conn.execute("SELECT DISTINCT link_type FROM scripture_links")}
    assert kinds == {"quotation-greek", "inner-biblical", "quotation-hebrew", "allusion-lemma"}


# --- rare-lemma allusion: the Septuagint against the Greek New Testament -----------------------
# Same language and a shared lemma inventory, so no bridge is needed. Scored on rarity rather than
# alignment (which is 0 for this class by construction), because an allusion need share no phrasing.

def test_lxx_lemmas_are_ingested_and_openly_licensed(conn):
    """The gap this closed: the Septuagint's text was here but not its lemmas. CCAT's morphological
    database is restrictively licensed -- these lemma files are a separate CC BY 4.0 work carrying
    only a key and a lemma, and they were sitting unused in open-data/."""
    work = conn.execute("SELECT license_tier, notes FROM works WHERE work_id='lxx-lemmas'").fetchone()
    assert work and work["license_tier"] == "open"
    assert conn.execute(
        "SELECT COUNT(*) n FROM morphology WHERE work_id='lxx-lemmas'").fetchone()["n"] > 500000


def test_lxx_and_nt_share_a_lemma_inventory(conn):
    """What makes the bridge unnecessary. Both sides normalise through the same function -- the
    lemma files keep final sigma where normalise_greek converts it, and joining them unnormalised
    made nomos and eleos appear ABSENT from the Septuagint, which is impossible on its face."""
    lxx = {r["lemma"] for r in conn.execute(
        "SELECT DISTINCT lemma FROM morphology WHERE work_id='lxx-lemmas'")}
    for probe in ("νομοσ", "ελεοσ", "διαθηκη", "πνευμα"):
        assert probe in lxx, f"{probe} missing from the Septuagint lemma set"


def test_allusion_class_reaches_past_quotation(conn):
    """Revelation 21:20's jewels against Ezekiel 28:13 -- shared rare vocabulary, no shared
    phrasing, so quotation matching cannot see it at all."""
    row = conn.execute(
        "SELECT idf_overlap, alignment FROM scripture_links WHERE link_type='allusion-lemma' "
        "AND from_book='Rev' AND from_chapter=21 AND to_book='Ezek' AND to_chapter=28").fetchone()
    assert row and row["idf_overlap"] >= quotations.ALLUSION_WEIGHT
    assert row["alignment"] == 0, "allusion is not scored on alignment"
    assert conn.execute(
        "SELECT COUNT(*) n FROM scripture_links WHERE link_type='quotation-greek' "
        "AND from_book='Rev' AND from_chapter=21 AND to_book='Ezek'").fetchone()["n"] == 0


def test_allusion_reaches_the_deuterocanon(conn):
    """The lemma files cover Wisdom and Sirach, so allusions no cross-reference list carries become
    visible -- Paul at the Areopagus against Wisdom 13:10, Hebrews 11:5 against Sirach 44:16. That
    bears directly on the extra-biblical-texts item in the backlog."""
    books = {r["to_book"] for r in conn.execute(
        "SELECT DISTINCT to_book FROM scripture_links WHERE link_type='allusion-lemma'")}
    assert books & {"Wis", "Sir"}, "expected deuterocanonical allusions"


def test_allusion_is_far_above_the_random_baseline(conn):
    """Corroboration for random New Testament / Septuagint verse pairs is 0.3%; for this class it
    is around half. If that enrichment collapses, the rarity threshold has stopped discriminating."""
    rate = conn.execute(
        "SELECT AVG(corroborated) r FROM scripture_links WHERE link_type='allusion-lemma'"
    ).fetchone()["r"]
    assert rate > 0.3
