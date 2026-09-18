"""Tests for source_catalog.py and references/sources.toml.

The catalog exists because three config surfaces -- license_map.yml, media_root.py and the
open-data/restricted-data directory split -- held overlapping facts and nothing checked them
against each other. These tests pin the properties that make it a single authority rather than a
fourth surface:

- it parses with the stdlib alone, so check_sources.py keeps working from a bare `python3`
- media_root.py and build.py genuinely read it, rather than keeping their own copies
- an unknown tier fails closed instead of granting permissive defaults
"""
import subprocess
import sys
from pathlib import Path

import pytest

import build
import media_root
import source_catalog as cat

REPO_ROOT = Path(__file__).resolve().parents[3]


# --- the constraint that chose TOML over YAML ------------------------------

def test_catalog_is_importable_without_third_party_packages():
    """check_sources.py is documented as runnable from a bare `python3` with no `uv sync`.

    PyYAML is not importable there; tomllib is. If source_catalog ever grows a third-party import,
    that script breaks in the one environment it is promised to work in -- so assert it in a
    subprocess with site-packages disabled rather than trusting the import list by eye.
    """
    result = subprocess.run(
        [sys.executable, "-S", "-c",
         "import sys; sys.path.insert(0, %r); import source_catalog; "
         "print(source_catalog.tier('open')['quote'])" % str(REPO_ROOT / "references" / "build")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "unlimited" in result.stdout


def test_check_sources_runs_on_bare_python():
    """The whole point of the above, end to end."""
    result = subprocess.run(
        [sys.executable, "-S", str(REPO_ROOT / "references" / "check_sources.py"), "--quiet"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# --- single authority: the other modules read it ---------------------------

def test_media_root_reads_the_catalog(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/elsewhere")
    assert media_root.media_root() == Path("/tmp/elsewhere")
    assert media_root.bibles_dir() == Path("/tmp/elsewhere/bibles")
    assert media_root.study_notes_db() == Path("/tmp/elsewhere/local-only-build/study-notes.db")


def test_media_root_env_var_name_comes_from_the_catalog():
    assert media_root.ENV_VAR == cat.media_env_var() == "BIBLE_MEDIA_ROOT"


def test_build_license_map_is_the_catalog_license_map():
    assert build.LICENSE_MAP == cat.license_map()


@pytest.mark.parametrize("license_string,expected", [
    ("Public Domain", "open"),
    ("Creative Commons: BY-NC 4.0", "restricted-nc"),
    ("GPL", "unknown"),
])
def test_known_licence_strings_keep_their_tier(license_string, expected):
    """Migrated verbatim from license_map.yml; these three span the three tiers it assigned."""
    assert cat.license_tier(license_string) == expected
    assert build.classify_license(license_string) == expected


# --- fail closed -----------------------------------------------------------

def test_unlisted_licence_falls_back_to_unknown():
    assert cat.license_tier("Totally Made Up Licence") == "unknown"
    assert build.classify_license(None) == "unknown"


def test_unknown_tier_is_not_quotable():
    t = cat.tier("unknown")
    assert t["quote"] == "none"
    assert t["commit_text"] is False


def test_quotation_only_is_not_committable():
    assert cat.tier("quotation-only")["commit_text"] is False


def test_unknown_tier_name_raises_rather_than_defaulting():
    """A typo must not silently grant quoting rights."""
    with pytest.raises(KeyError, match="unknown licence tier"):
        cat.tier("open-ish")


def test_unknown_database_name_raises():
    with pytest.raises(KeyError, match="no database"):
        cat.database("does-not-exist")


def test_unknown_media_subdir_raises():
    with pytest.raises(KeyError, match="no media subdir"):
        cat.media_subdir("nope")


# --- path resolution -------------------------------------------------------

def test_repo_database_resolves_inside_the_repo():
    db = cat.database("bible-text")
    assert db["resolved_path"] == REPO_ROOT / "references/build/out/bible-text.db"
    assert db["location"] == "repo"


def test_media_database_resolves_against_the_volume(monkeypatch):
    monkeypatch.setenv("BIBLE_MEDIA_ROOT", "/tmp/elsewhere")
    db = cat.database("study-notes")
    assert db["resolved_path"] == Path("/tmp/elsewhere/local-only-build/study-notes.db")
    assert db["location"] == "media"


def test_study_notes_db_is_never_inside_the_repo_tree():
    """The quotation-only tier's isolation is structural, not just a .gitignore line."""
    resolved = cat.database("study-notes")["resolved_path"]
    assert REPO_ROOT not in resolved.parents


def test_study_notes_connects_immutable():
    """Read-only network mount: no locking, no WAL sidecars written onto the share."""
    assert cat.database("study-notes")["connect"] == "immutable"
    assert cat.database("study-notes")["require_indexed"] is True


# --- internal consistency (the same rules check_sources enforces) ----------

def test_every_declared_tier_is_defined():
    defined = set(cat.tiers())
    for entry in cat.catalog()["databases"].values():
        assert entry["default_tier"] in defined
    for entry in cat.catalog()["source_trees"].values():
        assert entry["default_tier"] in defined
    for tier_name in cat.license_map().values():
        assert tier_name in defined


def test_source_trees_are_the_licence_boundary():
    trees = cat.source_trees()
    assert trees["open-data"]["default_tier"] == "open"
    assert trees["restricted-data"]["default_tier"] == "restricted-nc"
    for entry in trees.values():
        assert entry["resolved_path"].is_dir(), f"{entry['path']} missing"


def test_quote_allowance_names_its_tier():
    """It is stamped onto every study-notes record, so it has to be self-describing."""
    text = cat.quote_allowance("quotation-only")
    assert text.startswith("quotation-only:")
    assert "sentence or two" in text
