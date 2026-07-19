"""Fetch/cache helper for Sefaria texts (Mishnah, Talmud, and other Jewish literature) via the
Sefaria-Export GCS bucket (https://github.com/Sefaria/Sefaria-Export) -- no API key needed.

Deliberately NOT wired into bible-text.db: Mishnah/Talmud addressing (chapter + mishnah/daf, no
verse) doesn't map onto that schema's book/chapter/verse columns, which assume the canonical
Bible's structure. This is a standalone cache + lookup, not a new ingest_* in build.py.

Every version of a Sefaria text carries its own license -- check `license_tier` before quoting.
Prefer a CC0/CC-BY/public-domain version over the CC-BY-NC "William Davidson Edition" that shows
up as Sefaria's own default English translation when one exists (Mishnah Pesachim has several
open options; see references/README.md and docs/content/resources/jewish-sources.md).

Usage:
    uv run python sefaria.py --category "Mishnah/Seder Moed" --title "Mishnah Pesachim" \
        --language English --version "Sefaria Community Translation" --chapter 10 --section 1
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent / "cache" / "sefaria"
BASE_URL = "https://storage.googleapis.com/sefaria-export/json"
_TAG_PATTERN = re.compile(r"<[^>]+>")


def fetch_text(category: str, title: str, language: str, version_title: str) -> dict:
    """category e.g. 'Mishnah/Seder Moed'; title e.g. 'Mishnah Pesachim'; language 'English' or
    'Hebrew'; version_title exactly as Sefaria names it, e.g. 'Sefaria Community Translation'."""
    cache_key = f"{category}__{title}__{language}__{version_title}".replace("/", "_")
    cache_path = CACHE_DIR / f"{cache_key}.json"
    if not cache_path.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = "/".join(urllib.parse.quote(p) for p in (*category.split("/"), title, language, f"{version_title}.json"))
        url = f"{BASE_URL}/{path}"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; bible_studies build script)"})
        with urllib.request.urlopen(request) as response:
            cache_path.write_bytes(response.read())
    return json.loads(cache_path.read_text(encoding="utf-8"))


def get_section(data: dict, chapter: int, section: int) -> str | None:
    """1-indexed chapter/section (matches how Sefaria refs are cited, e.g. 'Pesachim 10:1').
    Strips the source's inline HTML italics markup; returns None if out of range."""
    try:
        raw = data["text"][chapter - 1][section - 1]
    except IndexError:
        return None
    if not raw:
        return None
    return _TAG_PATTERN.sub("", raw).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--category", required=True, help="e.g. 'Mishnah/Seder Moed'")
    parser.add_argument("--title", required=True, help="e.g. 'Mishnah Pesachim'")
    parser.add_argument("--language", required=True, choices=["English", "Hebrew"])
    parser.add_argument("--version", required=True, dest="version_title", help="exact Sefaria versionTitle")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--section", type=int)
    args = parser.parse_args()

    data = fetch_text(args.category, args.title, args.language, args.version_title)
    print(f"{data.get('title')} -- {data.get('versionTitle')} ({data.get('language')}) -- license: {data.get('license')}")

    if args.chapter and args.section:
        text = get_section(data, args.chapter, args.section)
        print(f"\n{args.title} {args.chapter}:{args.section}\n{text}")
    elif args.chapter:
        for i, section in enumerate(data["text"][args.chapter - 1], start=1):
            clean = _TAG_PATTERN.sub("", section).strip() if section else ""
            print(f"\n{args.chapter}:{i}\n{clean}")


if __name__ == "__main__":
    main()
