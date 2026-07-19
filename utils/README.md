# utils/

One-off and occasional-use Python scripts for preparing the genealogy dataset (`docs/data/genealogy/*.json`). Stdlib only — no dependencies, no venv needed. Run with plain `python3` from the **repo root** (paths inside these scripts are relative to root, e.g. `docs/data/genealogy/antediluvian.json`).

```bash
python3 utils/validate_genealogy.py
```

- **`add_gender.py`**, **`add_hebrew_names.py`** — one-off enrichment passes over the genealogy era files (gender tags, Hebrew names/transliterations). Safe to re-run; both are keyed by person id, so re-running just re-applies the same mapping.
- **`validate_genealogy.py`** — sanity-checks the genealogy era files (referenced above). Run this after editing any `docs/data/genealogy/*.json` file by hand.
- **`lib/bible_books.py`** — shared Old/New Testament book-name list, imported by `archive/bible_md.py`.
- **`archive/`** — one-off migration scripts from past repo reorganizations (e.g. `restructure.py` hardcodes a specific old-path → new-path mapping from a since-completed move). Kept for historical reference; not meant to be re-run against the current tree, and will error or do nothing useful if you try.
