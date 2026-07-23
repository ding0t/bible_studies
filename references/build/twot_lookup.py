"""Query library + CLI for twot_strongs_map.json (TWOT root -> Strong's/BDB/lemma/gloss).

Named twot_lookup.py, not twot.py, to avoid colliding with the twot/ package already in
this directory (the OCR/segmentation extraction pipeline) -- `import twot` would silently
resolve to that package instead of this module.

Same split as query.py: plain `lookup_*` functions return JSON-friendly data, `main()` is
a thin CLI wrapper, and mcp_server.py imports the same functions directly. This is a
reverse-lookup index over 6,925 TWOT roots (id/lemma/gloss only -- open-ish bare facts,
see references/README.md); it is NOT the copyrighted discussion prose, which isn't
committed to this repo at all.

CLI examples:
    uv run python twot_lookup.py root 1a
    uv run python twot_lookup.py strongs H1
    uv run python twot_lookup.py strongs 1          # H/G prefix optional, assumed Hebrew
    uv run python twot_lookup.py lemma אָב
"""
import argparse
import json
from functools import lru_cache
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parent / "twot" / "twot_strongs_map.json"


@lru_cache(maxsize=1)
def load_map() -> dict[str, list[dict]]:
    """Raw root -> [{strongs_id, bdb_id, lemma, xlit, gloss}, ...] map. Cached module-wide
    since it's loaded from a ~1MB JSON file -- an MCP server calling this repeatedly across
    tool calls should only pay the parse cost once."""
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"{MAP_PATH} not found -- see references/build/twot/build_twot_map.py.")
    with open(MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _indexes() -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Reverse indexes built once from load_map(): strongs_id -> entries (with root attached),
    lemma -> entries (with root attached). A handful of Strong's ids map to more than one TWOT
    root (sub-senses like 26b/26d under root 26) so both indexes fan out to lists, never a
    single dict."""
    by_strongs: dict[str, list[dict]] = {}
    by_lemma: dict[str, list[dict]] = {}
    for root, entries in load_map().items():
        for e in entries:
            enriched = {"root": root, **e}
            if e.get("strongs_id"):
                by_strongs.setdefault(e["strongs_id"], []).append(enriched)
            if e.get("lemma"):
                by_lemma.setdefault(e["lemma"], []).append(enriched)
    return by_strongs, by_lemma


def lookup_root(root: str) -> list[dict]:
    """Every Strong's/BDB entry under one TWOT root number, e.g. '1a'."""
    entries = load_map().get(root, [])
    return [{"root": root, **e} for e in entries]


def lookup_strongs(strongs_id: str) -> list[dict]:
    """TWOT root(s) for a Strong's Hebrew number. TWOT covers the Hebrew/Aramaic OT only,
    so a bare number or 'H'-prefixed number are treated the same; a 'G' prefix is rejected."""
    if strongs_id.upper().startswith("G"):
        raise ValueError("TWOT covers Hebrew/Aramaic only -- no Greek (G-prefixed) entries")
    normalized = "H" + strongs_id.lstrip("Hh")
    by_strongs, _ = _indexes()
    return by_strongs.get(normalized, [])


def lookup_lemma(lemma: str) -> list[dict]:
    """TWOT root(s) for an exact Hebrew lemma match, e.g. אָב."""
    _, by_lemma = _indexes()
    return by_lemma.get(lemma, [])


# ---------------------------------------------------------------------------
# CLI -- formats the same data the functions above return.
# ---------------------------------------------------------------------------

def _print_entries(entries: list[dict]) -> None:
    if not entries:
        print("No matches.")
        return
    for e in entries:
        print(f"root={e['root']:6} strongs={e.get('strongs_id') or '-':8} bdb={e.get('bdb_id') or '-':10} "
              f"{e.get('lemma') or '-':10} ({e.get('xlit') or '-'})  {e.get('gloss') or ''}")


def cmd_root(args: argparse.Namespace) -> None:
    _print_entries(lookup_root(args.root))


def cmd_strongs(args: argparse.Namespace) -> None:
    try:
        _print_entries(lookup_strongs(args.strongs))
    except ValueError as e:
        raise SystemExit(f"strongs: {e}")


def cmd_lemma(args: argparse.Namespace) -> None:
    _print_entries(lookup_lemma(args.lemma))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_root = sub.add_parser("root", help="Every entry under one TWOT root number")
    p_root.add_argument("root", help="e.g. 1a, 26b")
    p_root.set_defaults(func=cmd_root)

    p_strongs = sub.add_parser("strongs", help="TWOT root(s) for a Strong's Hebrew number")
    p_strongs.add_argument("strongs", help="e.g. H1 or 1 (H prefix optional)")
    p_strongs.set_defaults(func=cmd_strongs)

    p_lemma = sub.add_parser("lemma", help="TWOT root(s) for an exact Hebrew lemma")
    p_lemma.add_argument("lemma", help="e.g. אָב")
    p_lemma.set_defaults(func=cmd_lemma)

    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
