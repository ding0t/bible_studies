"""Strong's numbers a study could add so its word studies open a pop-up card.

The site's pop-up (app/src/entries/popups.js) opens a word study from a Strong's tag and from the
Greek or Hebrew word written just before it: `ἀρραβών (*arrabōn*, G728)`. A word glossed with a
transliteration but no number, `κατέχω (*katechō*)`, gets no card. Once a page has tagged a word,
the pop-up links that word's later mentions on the same page too, so only the untagged ones are
reported here.

Each untagged glossed word is looked up in MACULA's surface forms and lemmas (bible-text.db). A
word that resolves to exactly one Strong's number is a suggestion; one that resolves to several
lists them, because only the author knows which is meant. Nothing is written: a wrong number opens
the wrong card with no error, so every suggestion is for the author to accept.

A word named bare, with no gloss at all -- `The New Testament never uses δαιμονίζομαι of a Christian`
-- gets no card either, unless the page tags it somewhere. These are reported too, with the number
another page already tags that word with where there is one, since that is the author's own reading
and outranks MACULA's. Only a lone word counts: a run of two or more is a quotation, whose articles
and conjunctions nobody means to study, and a block quotation is skipped whole.

Phrases are reported but not resolved, since which word in a phrase carries the gloss is a reading
decision. So is a gloss written outside parentheses (`<span dir="rtl">מַרְאֶה</span> *mar'eh*`),
which the pop-up cannot connect to its number.

Usage:  uv run python strongs_suggest.py docs/content/last-things/the-restrainer.md
        uv run python strongs_suggest.py --all
"""
import argparse
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "out" / "bible-text.db"
REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "docs" / "content"

SCRIPT = "̀-ͯͰ-Ͽἀ-῿֐-׿יִ-ﭏ"
LETTER = "Ά-Ͽἀ-῿א-תיִ-ﭏ"
WORD = f"[{SCRIPT}]*[{LETTER}][{SCRIPT}]*"
# The word, any closing markup around it, then an opening parenthesis.
GLOSSED = re.compile(rf"({WORD}(?:\s+{WORD})*)((?:</span>|\*\*)?\s*)\(([^()]*)\)")
# The English leads and the word opens its own gloss: `**remains** (μένω, *menō*, G3306)`.
OPENED = re.compile(rf"\((?:\*\*)?({WORD})(?:\*\*)?,([^()]*)\)")
RUN = re.compile(rf"{WORD}(?:\s+{WORD})*")
DATA_STRONGS = re.compile(rf'<span[^>]* data-strongs="([^"]*)"[^>]*>({WORD})</span>')
LINK_TEXT = re.compile(r"\[[^\]]*\]\([^)]*\)")
UNBRACKETED = re.compile(rf'<span dir="rtl">({WORD})</span>\s*\*[^*\s][^*]*\*')
STRONGS = re.compile(r"(?<![\w-])([HG])0*(\d{1,4})[a-z]?(?![\w-])")
STRONGS_MAX = {"H": 8674, "G": 5624}


def word_key(word: str) -> str:
    """The pop-up's wordKey (app/src/utils/scriptureRefs.js), plus meteg, which MACULA and the
    studies write inconsistently."""
    stripped = re.sub(r"[̀-֑ͯ-ֽ֯;·]", "", unicodedata.normalize("NFD", word))
    return unicodedata.normalize("NFC", stripped).lower().replace("ς", "σ")


def tag_in(text: str) -> str | None:
    for prefix, number in STRONGS.findall(text):
        if 1 <= int(number) <= STRONGS_MAX[prefix]:
            return f"{prefix}{int(number)}"
    return None


def load_index(conn: sqlite3.Connection) -> tuple[dict[str, set[str]], dict[str, str]]:
    forms: dict[str, set[str]] = defaultdict(set)
    lemmas: dict[str, str] = {}
    rows = conn.execute(
        "SELECT work_id, surface_form, lemma, strongs_id FROM morphology "
        "WHERE work_id LIKE 'macula-%' AND strongs_id IS NOT NULL AND strongs_id NOT LIKE '%+%'"
    )
    for work, surface, lemma, number in rows:
        # MACULA writes 0 for a word it gives no Strong's number (ἄμωμον, Ἀρνί).
        if not number.lstrip("0"):
            continue
        sid = ("G" if "greek" in work else "H") + number.lstrip("0")
        lemmas.setdefault(sid, lemma or "")
        for form in (surface, lemma):
            if form:
                forms[word_key(form)].add(sid)
    return forms, lemmas


def body_of(path: Path) -> str:
    """The markdown a reader sees, with removed spans blanked rather than cut so offsets still map
    to line numbers."""
    text = path.read_text(encoding="utf-8")
    blank = lambda m: re.sub(r"[^\n]", " ", m.group())
    text = re.sub(r"\A---\n.*?\n---\n", blank, text, flags=re.S)
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    # The pop-up does not scan headings, so a number there tags nothing.
    return re.sub(r"^#{1,6} .*$", blank, text, flags=re.M)


def site_tags(pages: list[Path]) -> dict[str, set[str]]:
    """Every number each word is tagged with anywhere on the site."""
    site: dict[str, set[str]] = defaultdict(set)
    for page in pages:
        for key, number in tags_on(body_of(page)):
            site[key].add(number)
    return site


def tags_on(body: str) -> list[tuple[str, str]]:
    found = []
    for m in GLOSSED.finditer(body):
        number = tag_in(m.group(3))
        if number and len(m.group(1).split()) == 1:
            found.append((word_key(m.group(1)), number))
    for m in OPENED.finditer(body):
        if number := tag_in(m.group(2)):
            found.append((word_key(m.group(1)), number))
    for m in DATA_STRONGS.finditer(body):
        if number := tag_in(m.group(1)):
            found.append((word_key(m.group(2)), number))
    return found


def scan(
    path: Path, forms: dict[str, set[str]], lemmas: dict[str, str], site: dict[str, set[str]] | None = None
) -> dict[str, list]:
    body = body_of(path)
    line_of = lambda offset: body.count("\n", 0, offset) + 1
    tagged = {key for key, _ in tags_on(body)}
    untagged = []
    covered = [(m.start(1), m.end(1)) for m in GLOSSED.finditer(body)]
    covered += [m.span() for m in re.finditer(r"\([^()]*\)", body) if tag_in(m.group())]
    covered += [m.span() for m in DATA_STRONGS.finditer(body)]
    covered += [m.span() for m in LINK_TEXT.finditer(body)]
    for m in GLOSSED.finditer(body):
        run, gloss = m.group(1), m.group(3)
        # A gloss whose first item holds a number is a domain code or a citation, and one whose number follows
        # within the sentence -- `ἡρμοσάμην (*hērmosamēn*), from ἁρμόζω (*harmozō*, G718)` -- is
        # an inflected form the lemma after it already tags.
        if not tag_in(gloss) and not re.search(r"\d", gloss.split(",")[0]):
            untagged.append((line_of(m.start()), run, gloss.strip(), body[m.end(): m.end() + 150]))

    report = {"suggest": [], "ambiguous": [], "unknown": [], "phrase": [], "unbracketed": [], "bare": []}
    seen = set()
    for line, run, gloss, after in untagged:
        key = word_key(run)
        if key in tagged or key in seen:
            continue
        seen.add(key)
        if len(run.split()) > 1:
            report["phrase"].append((line, run, gloss))
            continue
        ids = sorted(forms.get(key, ()), key=lambda s: (s[0], int(re.sub(r"\D", "", s))))
        if len(ids) == 1 and re.search(rf"(?<![\w-]){ids[0]}(?!\d)", after):
            continue
        entry = (line, run, gloss, [(sid, lemmas.get(sid, "")) for sid in ids])
        report["suggest" if len(ids) == 1 else "ambiguous" if ids else "unknown"].append(entry)
    for m in UNBRACKETED.finditer(body):
        report["unbracketed"].append((line_of(m.start()), m.group(1), ""))

    for m in RUN.finditer(body):
        word, key = m.group(), word_key(m.group())
        if " " in word or key in tagged or key in seen or any(a <= m.start() < b for a, b in covered):
            continue
        if body[body.rfind("\n", 0, m.start()) + 1:].lstrip().startswith(">"):
            continue
        seen.add(key)
        ids = sorted((site or {}).get(key) or forms.get(key, ()), key=lambda s: (s[0], int(re.sub(r"\D", "", s))))
        # An inflected form the next clause tags by its lemma: `μαντευομένη, from μαντεύομαι (…, G3132)`.
        if len(ids) == 1 and re.search(rf"(?<![\w-]){ids[0]}(?!\d)", body[m.end(): m.end() + 150]):
            continue
        source = "site" if (site or {}).get(key) else "macula" if ids else ""
        report["bare"].append((line_of(m.start()), word, source, [(sid, lemmas.get(sid, "")) for sid in ids]))
    return report


def print_report(path: Path, report: dict[str, list]) -> None:
    print(f"\n{path.relative_to(REPO_ROOT)}")
    labels = {
        "suggest": "add the number",
        "ambiguous": "several numbers -- pick the one meant",
        "unknown": "not in MACULA -- tag by hand if it is a word study",
        "phrase": "phrase -- tag the word the gloss is about, if any",
        "unbracketed": "gloss outside parentheses -- write `word (*translit*, H123)`",
        "bare": "named with no gloss and never tagged here -- gloss it, or `<span data-strongs=\"G123\">`",
    }
    for kind, label in labels.items():
        if not report[kind]:
            continue
        print(f"  {label}:")
        for line, run, gloss, *ids in report[kind]:
            found = ", ".join(f"{sid} {lemma}" for sid, lemma in ids[0]) if ids else ""
            print(f"    {line:>5}  {' '.join(run.split())}  ({gloss[:40]})  {found}".rstrip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--all", action="store_true", help="every hand-written page, summarised")
    args = parser.parse_args()
    if not DB_PATH.exists():
        print(f"{DB_PATH} not built -- run `uv run python build.py`", file=sys.stderr)
        return 1
    forms, lemmas = load_index(sqlite3.connect(DB_PATH))
    pages = [
        p for p in sorted(CONTENT_DIR.rglob("*.md"))
        if "commentary-index:auto-start" not in p.read_text(encoding="utf-8")
    ]
    site = site_tags(pages)

    if args.all:
        kinds = ("suggest", "ambiguous", "unknown", "phrase", "unbracketed", "bare")
        print(f"{'page':60} suggest ambiguous unknown phrase unbracketed    bare")
        for page in pages:
            report = scan(page, forms, lemmas, site)
            counts = [len(report[k]) for k in kinds]
            if any(counts):
                print(f"{str(page.relative_to(CONTENT_DIR)):60} " + " ".join(f"{c:>7}" for c in counts))
        return 0

    for path in args.paths:
        print_report(path.resolve(), scan(path.resolve(), forms, lemmas, site))
    return 0


if __name__ == "__main__":
    sys.exit(main())
