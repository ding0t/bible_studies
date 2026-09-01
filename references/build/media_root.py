"""Where the local-only reference material lives.

The commercial study-Bible EPUBs, the TWOT scans, the patristics corpus and the databases built
from them are deliberately **not** in this repository -- see references/README.md for the licence
tiers that decide what may live here and what may not. They sit on an external volume whose
location is a property of one machine, not of the project.

**This repository is public.** Its committed files should say what a source is and how much of it
may be quoted; they should not publish the layout of anyone's disks. So the location is read from
an environment variable instead of being hardcoded in a dozen scripts:

    export BIBLE_MEDIA_ROOT=/Volumes/media/bible

`DEFAULT_MEDIA_ROOT` keeps the previous behaviour when the variable is unset, so nothing breaks on
the machine this was built on -- but a second machine (or anyone who clones this) sets the variable
rather than editing source files. `.env` is gitignored and is a reasonable place to keep it.

Use `require_media_root()` (or one of the `require_*` helpers) in anything that will fail without
the volume: the external drive being unmounted is a routine occurrence, and several study-state
files record whole research sessions lost to it being silently absent. A clear message beats a
FileNotFoundError three call frames down.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "BIBLE_MEDIA_ROOT"
DEFAULT_MEDIA_ROOT = Path("/Volumes/media/bible")


def media_root() -> Path:
    """The external reference volume, from $BIBLE_MEDIA_ROOT or the default. Not checked to exist."""
    return Path(os.environ.get(ENV_VAR) or DEFAULT_MEDIA_ROOT).expanduser()


def require_media_root() -> Path:
    """As media_root(), but exit with a readable message if the volume is not mounted."""
    root = media_root()
    if not root.is_dir():
        source = f"${ENV_VAR}" if os.environ.get(ENV_VAR) else "the built-in default"
        raise SystemExit(
            f"External reference volume not found: {root} (from {source}).\n"
            f"Mount it, or point {ENV_VAR} at where it actually is. "
            f"See references/README.md for what lives there and why it is not in the repo."
        )
    return root


def local_only_build() -> Path:
    """Build output that must never land inside the repo tree (study-notes.db, OCR pages, …)."""
    return media_root() / "local-only-build"


def reference_dir() -> Path:
    """Source PDFs and the patristics corpus."""
    return media_root() / "reference"


def bibles_dir() -> Path:
    """The study-Bible EPUBs that build_study_notes.py extracts from."""
    return media_root() / "bibles"


def resources_dir() -> Path:
    """Secondary material -- course handouts, owned PDFs."""
    return media_root() / "resources"


def study_notes_db() -> Path:
    return local_only_build() / "study-notes.db"


def lexicon_restricted_db() -> Path:
    return local_only_build() / "lexicon-restricted.db"


def require_study_notes_db() -> Path:
    """The commercial study-Bible database, checked to exist. Used by query paths, not builders."""
    path = study_notes_db()
    if not path.is_file():
        require_media_root()  # gives the better message when the whole volume is missing
        raise SystemExit(
            f"study-notes.db not found at {path}.\n"
            f"Build it with `uv run python build_study_notes.py` from references/build."
        )
    return path
