#!/usr/bin/env python3
"""Reader for references/sources.toml -- the single authority for source locations, licence tiers
and reproduction limits.

Everything that needs to know where a source lives or what may be quoted from it goes through
here: media_root.py for off-repo paths, build.py for the licence-string mapping,
study_notes_query.py for the quotation allowance, check_sources.py for drift. Do not parse
sources.toml anywhere else -- the point of the file is that the three facts it holds can no longer
disagree with each other, and a second parser reintroduces exactly that.

**stdlib only, deliberately.** references/check_sources.py is documented as runnable from a bare
`python3` with no `uv sync`, and PyYAML is not importable there. `tomllib` is, which is why the
catalog is TOML. Keep this module importable from the bare interpreter: no third-party imports,
ever. There is a test asserting it.

Usage:
    import source_catalog as cat
    cat.tier("quotation-only")["quote"]      # 'sentence-or-two-with-attribution'
    cat.database("study-notes")["connect"]   # 'immutable'
    cat.media_subdir("local_only_build")     # Path, honouring $BIBLE_MEDIA_ROOT
    cat.license_tier("Public Domain")        # 'open'
"""
from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH = REPO_ROOT / "references" / "sources.toml"

UNKNOWN_TIER = "unknown"  # fail-closed default; see the [license_map] comments in sources.toml


@lru_cache(maxsize=1)
def catalog() -> dict:
    """The parsed catalog. Cached -- it is read many times per process and never changes."""
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(f"{CATALOG_PATH} not found -- the source catalog is required.")
    with open(CATALOG_PATH, "rb") as f:
        return tomllib.load(f)


def tiers() -> dict[str, dict]:
    return catalog()["tiers"]


def tier(name: str) -> dict:
    """One tier's policy. Raises on an unknown name rather than returning a permissive default --
    a typo must not silently grant quoting rights."""
    try:
        return catalog()["tiers"][name]
    except KeyError:
        raise KeyError(
            f"unknown licence tier {name!r}; sources.toml defines {sorted(catalog()['tiers'])}"
        ) from None


def quote_allowance(tier_name: str) -> str:
    """A one-line statement of what may be reproduced, for stamping onto returned records.

    This is what makes tier awareness a property of the data rather than of the agent's
    diligence -- see study_notes_query._stamp.
    """
    t = tier(tier_name)
    return f"{tier_name}: {t['description']}"


def license_tier(license_string: str) -> str:
    """A source's self-reported licence string -> our tier. Fail-closed to 'unknown'."""
    return catalog()["license_map"].get(license_string, UNKNOWN_TIER)


def license_map() -> dict[str, str]:
    return dict(catalog()["license_map"])


# --- locations -------------------------------------------------------------

def media_root() -> Path:
    """The external reference volume, from the env var named in the catalog. Not checked to exist."""
    media = catalog()["media"]
    return Path(os.environ.get(media["env_var"]) or media["default_root"]).expanduser()


def media_env_var() -> str:
    return catalog()["media"]["env_var"]


def media_subdir(key: str) -> Path:
    """A named subdirectory of the external volume, e.g. 'local_only_build', 'bibles'."""
    subdirs = catalog()["media"]["subdirs"]
    try:
        return media_root() / subdirs[key]
    except KeyError:
        raise KeyError(f"no media subdir {key!r}; catalog defines {sorted(subdirs)}") from None


def database(name: str) -> dict:
    """One database's entry, with `resolved_path` added.

    A `path` starting with a ${media.*} placeholder resolves against the external volume; anything
    else is repo-relative. Keeping that rule here means no caller has to know which is which.
    """
    try:
        entry = dict(catalog()["databases"][name])
    except KeyError:
        raise KeyError(
            f"no database {name!r}; catalog defines {sorted(catalog()['databases'])}"
        ) from None
    entry["resolved_path"] = _resolve_path(entry["path"])
    return entry


def _resolve_path(spec: str) -> Path:
    if spec.startswith("${media."):
        key, _, rest = spec[len("${media."):].partition("}")
        return media_subdir(key) / rest.lstrip("/")
    return REPO_ROOT / spec


def source_trees() -> dict[str, dict]:
    """The open-data/ and restricted-data/ trees. The directory a source sits in IS the licence
    audit boundary -- this describes it, it does not replace it."""
    return {
        name: dict(entry) | {"resolved_path": REPO_ROOT / entry["path"]}
        for name, entry in catalog()["source_trees"].items()
    }


def raw_only() -> list[str]:
    """Sources present on disk but not ingested, so query.py and the MCP tools cannot see them.

    Their absence from a query is not evidence of their absence from the repo.
    """
    return list(catalog()["ingest"]["raw_only"])


def summary() -> str:
    """One-screen human view of the catalog, for `python3 references/build/source_catalog.py`."""
    lines = [f"source catalog v{catalog()['meta']['version']} ({CATALOG_PATH})", ""]
    lines.append("tiers:")
    for name, t in tiers().items():
        commit = "committable" if t["commit_text"] else "NOT committable"
        lines.append(f"  {name:18} quote={t['quote']:32} {commit}")
    lines.append("")
    lines.append(f"media root: {media_root()}  (${media_env_var()})")
    for key in catalog()["media"]["subdirs"]:
        path = media_subdir(key)
        lines.append(f"  {key:18} {path}  {'ok' if path.is_dir() else 'MISSING'}")
    lines.append("")
    lines.append("databases:")
    for name in catalog()["databases"]:
        db = database(name)
        state = "ok" if db["resolved_path"].is_file() else "not built"
        lines.append(f"  {name:14} {db['default_tier']:16} {state:10} {db['resolved_path']}")
    lines.append("")
    lines.append(f"raw-only (present, not ingested): {len(raw_only())}")
    for path in raw_only():
        lines.append(f"  {path}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
