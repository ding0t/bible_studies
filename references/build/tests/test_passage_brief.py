"""Tests for passage_brief.py.

The brief's job is to make a whole exegesis evidence set arrive at once, in a shape where the
things that fail silently cannot. So the tests concentrate on those:

- versification is always present and flagged when schemes disagree (Joel 2:28 / Joel 3:1)
- a translation only present in the commercial database is routed there, not reported missing
- an unreachable source leaves a *marked* gap, never a quiet empty section
- MACULA's Strong's spellings actually resolve to TWOT roots
"""
import pytest

import passage_brief as pb
import study_notes_query as snq
import twot_lookup

HAS_STUDY_NOTES = snq.availability()["available"]
needs_study_notes = pytest.mark.skipif(not HAS_STUDY_NOTES, reason="study-notes.db not mounted")


# --- versification: the silent failure the brief exists to surface ---------

def test_joel_2_28_is_flagged_as_renumbered():
    """English Joel 2:28 is Hebrew Joel 3:1 -- the verse Acts 2 quotes.

    Reading one scheme's text under the other's reference raises no error, so the brief has to
    say it out loud.
    """
    brief = pb.passage_brief("Joel", 2, 28, include=["addressing"])
    addressing = brief["addressing"]
    assert addressing["agree"] is False
    assert addressing["schemes"]["english"] == "Joel 2:28"
    assert addressing["schemes"]["masoretic"] == "Joel 3:1"
    assert "no error is raised" in addressing["warning"]


def test_agreeing_reference_carries_no_warning():
    brief = pb.passage_brief("John", 6, 34, include=["addressing"])
    assert brief["addressing"]["agree"] is True
    assert "warning" not in brief["addressing"]


def test_addressing_is_present_even_when_not_requested():
    """It is cheap and it is the section a reader most needs to not skip."""
    assert "addressing" in pb.SECTIONS
    brief = pb.passage_brief("John", 6, 34, include=["addressing", "text"])
    assert brief["addressing"]["schemes"]


# --- routing a translation to the database that holds it -------------------

@needs_study_notes
def test_esv_is_routed_to_study_notes():
    ids = pb._study_work_ids()
    assert pb.route_translation("ESV", ids) == ("study-notes", "esv-study-bible")
    assert pb.route_translation("esv-study-bible", ids) == ("study-notes", "esv-study-bible")


def test_open_translation_stays_on_bible_text():
    assert pb.route_translation("WEB", set()) == ("bible-text", "WEB")


@needs_study_notes
def test_brief_carries_both_open_and_commercial_text():
    """The WEB/ESV pair on John 6:34 is this repo's own worked example of why you check.

    WEB reads "Lord", ESV reads "Sir"; a study drafted from memory once used the former under an
    ESV attribution.
    """
    brief = pb.passage_brief("John", 6, 34, translations=["WEB", "ESV"], include=["text"])
    web = brief["text"]["WEB"]["verses"][0]["text"]
    esv = brief["text"]["ESV"]["verses"][0]["text"]
    assert "Lord" in web
    assert "Sir" in esv
    assert brief["text"]["ESV"]["tier"] == "quotation-only"


# --- Strong's normalisation ------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("H0430", "H430"),      # zero-padded
    ("b:H7225", "H7225"),   # MACULA particle prefix
    ("d:H8064", "H8064"),
    ("430", "H430"),        # bare
])
def test_macula_strongs_spellings_normalise(raw, expected):
    assert twot_lookup.normalize_strongs(raw)[0] == expected


def test_homograph_suffix_is_kept_as_a_fallback_not_silently_dropped():
    """H1254a and H1254b are different lexemes; TWOT does not carry the distinction.

    Collapsing them is a judgement, so it must be visible rather than automatic.
    """
    exact, fallback = twot_lookup.normalize_strongs("H1254a")
    assert exact == "H1254a"
    assert fallback == "H1254"
    entries = twot_lookup.lookup_strongs("H1254a")
    assert entries and all("matched_without_suffix" in e for e in entries)


def test_greek_strongs_is_rejected():
    with pytest.raises(ValueError, match="Hebrew/Aramaic only"):
        twot_lookup.normalize_strongs("G100")


def test_hebrew_passage_resolves_twot_roots():
    """Before normalisation this returned zero roots for Genesis 1:1 -- every id was a miss."""
    brief = pb.passage_brief("Gen", 1, 1, translations=["WEB"], include=["words"])
    roots = brief["words"]["twot_roots"]
    assert len(roots) >= 5, f"expected several roots, got {list(roots)}"
    assert "H430" in roots  # elohim


# --- degradation -----------------------------------------------------------

def test_unavailable_source_is_marked_not_silently_empty(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/definitely-not-mounted")
    brief = pb.passage_brief("John", 6, 34, translations=["WEB", "ESV"],
                             include=["addressing", "text", "notes"])
    assert brief["addressing"]["schemes"], "the open database must still answer"
    assert brief["diagnostics"]["unavailable_sources"]
    assert "do not fill it from memory" in brief["diagnostics"]["warning"]


def test_unknown_section_is_refused():
    out = pb.passage_brief("John", 6, 34, include=["nonsense"])
    assert "error" in out


# --- bounding --------------------------------------------------------------

def test_long_range_truncates_detail_and_says_so():
    brief = pb.passage_brief("Matt", 13, 1, 30, translations=["WEB"], include=["text", "words"])
    assert brief["diagnostics"]["truncated"] is True
    assert len(brief["diagnostics"]["detail_verses"]) == pb.MAX_DETAIL_VERSES
    assert "text covers the whole range" in brief["diagnostics"]["note"]
    assert len(brief["text"]["WEB"]["verses"]) == 30, "text should span the full range"


def test_single_verse_is_not_marked_truncated():
    brief = pb.passage_brief("John", 6, 34, translations=["WEB"], include=["text"])
    assert brief["diagnostics"]["truncated"] is False


def test_reference_string_reflects_the_span():
    assert pb.passage_brief("John", 6, 34, include=["addressing"])["reference"] == "John 6:34"
    assert pb.passage_brief("John", 6, 34, 40, include=["addressing"])["reference"] == "John 6:34-40"


# --- composition -----------------------------------------------------------

def test_brief_dispatches_only_through_the_batch_registry():
    """Every request the brief builds must be a tool research_batch knows.

    This is what keeps the brief from becoming a second implementation: it composes registered
    lookups rather than querying anything itself.
    """
    import research_batch as rb
    reqs = pb.build_requests("John", 6, 34, 40, ["WEB", "ESV"], ["esv-study-bible"],
                             pb.SECTIONS, {"esv-study-bible"})
    assert reqs
    for r in reqs:
        assert r["tool"] in rb.REGISTRY, f"{r['tool']} is not in the batch registry"


def test_variants_section_reports_absence_explicitly():
    brief = pb.passage_brief("John", 6, 34, include=["variants"])
    assert "note" in brief["textual_variants"]


def test_deut_32_8_variant_carries_extant_words():
    """A DSS reading must arrive with how much of the verse actually survives.

    Deuteronomy 32:8's "sons of God" is legible in only two words, and a study should say so
    rather than cite it flat.
    """
    brief = pb.passage_brief("Deut", 32, 8, include=["variants"])
    readings = brief["textual_variants"]["8"]["readings"]
    assert readings
    assert all("extant_words" in r for r in readings)
