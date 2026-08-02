"""Extractor family for Tyndale's NLT Life Application Study Bible and NLT
Christian Basics Bible epubs -- a FOURTH markup convention alongside
anchor_walker's underscore-book-name scheme and numeric_id's BBCCCVVV scheme:
dotted 'vs-BookAbbrev.C.V' zero-width verse anchors, and self-contained
'<div class="StudyNote" id="BookAbbrev.C.V[-range][.letter]_StudyNote_...">'
-style wrapper divs for notes, cross-references, and textnotes (unlike the
other two families, a note here is not a flow-marker with trailing text --
the whole note lives inside its own div, so it's read directly rather than
via split_by_markers).

The two epubs share this same verse/note id scheme (confirmed against both,
not assumed) but differ in depth: LASB has per-verse StudyNotes and
NLT-Crefs, BookIntros, and topical Profiles/Charts; Christian Basics Bible
has only per-book topical Notes (essay-style, not per-verse), NLT-Textnotes,
BookIntros, and a few topical reference sections (BasicTruths, Glossary,
Articles). Presence of each is config-driven via SourceConfig.extra rather
than assumed, since which directories exist differs between the two.
"""
import re

from lxml import html as lxml_html

from study_notes.epub_utils import normalize_whitespace, split_by_markers
from study_notes.extractors.base import BaseExtractor
from study_notes.models import ExtractionResult, IntroductionRecord, NoteRecord, TopicalArticleRecord, VerseRecord

PARSER = lxml_html.HTMLParser(recover=True, encoding="utf-8")

VERSE_ID_RE = re.compile(r"^vs-([A-Za-z0-9]+)\.(\d+)\.(\d+)$")
REF_ID_RE = re.compile(r"^([A-Za-z0-9]+)\.(\d+)\.(\d+)(?:-(?:(\d+)\.)?(\d+))?")
TEXTNOTE_ID_RE = re.compile(r"^tn-([A-Za-z0-9]+)\.(\d+)\.(\d+)")
HREF_VERSE_RE = re.compile(r"#vs-([A-Za-z0-9]+)\.(\d+)\.(\d+)")

# Paragraph/span classes that are typesetting chrome or Tyndale's own reader
# aids (section outlines, chart/map/profile sidebar links, speaker labels in
# Song of Solomon) rather than translated Bible text -- confirmed against
# actual class names in both epubs' NLT/ verse files, not guessed.
VERSE_CHROME_CLASSES = {
    "chapter-number", "psa-theme", "psa-author", "outline-1", "outline-2", "outline-3",
    "outline-3-roman", "outline-blurb", "Chart-ref", "KeyMap-ref", "Map-ref", "Profile-ref",
    "Note-ref", "sos-speaker", "sos-speaker-no-space", "h1", "toc", "subhead", "cref-see", "vn",
}

# Per-topical-wrapper-class config: which paragraph/span carries the title,
# and which paragraph classes are chrome (nav links, redundant with the
# title, or print-edition-only page numbers) rather than article body.
_TOPICAL_WRAPPER_CONFIG = {
    "BasicTruth": {"title_classes": ["bm-bt-topic"], "skip_para_classes": {"bm-bt-topic"}},
    "GlossaryEntry": {"title_classes": ["bm-glossary-entry-head"], "skip_para_classes": set()},
    "Note": {"title_classes": ["note-head"], "skip_para_classes": {"note-head", "backlink-primary"}},
    "Reference": {"title_classes": ["bm-head", "_rh-book-name"], "skip_para_classes": {"bm-head"}},
    "Profile": {"title_classes": ["pro-name"],
                "skip_para_classes": {"pro-name", "pro-info", "artfile-pro", "pro-ref"}},
    "Chart": {"title_classes": ["chart-title"], "skip_para_classes": {"chart-title", "chart-ref"}},
}


def _flatten_inline(el, skip_classes: frozenset) -> str:
    """Concatenate an element's own text and its descendants', in document
    order, except the text (and descendants' text) of any element whose
    class is in skip_classes -- e.g. a note's leading '1:1-31' locator link,
    which repeats information already carried by the wrapper div's own id.
    Tail text (what follows a skipped element, still in the parent's flow)
    is kept; only the skipped element's own subtree is dropped. Same
    start/end skip-depth technique as epub_utils.split_by_markers, just
    without marker-splitting since a wrapper div here is one self-contained
    note, not a flow spanning multiple verses."""
    parts: list[str] = []
    skip_depth = 0

    def walk(e):
        nonlocal skip_depth
        cls = set((e.get("class") or "").split())
        is_skip = bool(cls & skip_classes)
        if is_skip:
            skip_depth += 1
        elif skip_depth == 0 and e.text:
            parts.append(e.text)
        for child in e:
            walk(child)
            if skip_depth == 0 and child.tail:
                parts.append(child.tail)
        if is_skip:
            skip_depth -= 1

    walk(el)
    return normalize_whitespace("".join(parts))


def _wrapper_paragraphs(div_el, skip_para_classes: frozenset, skip_inline_classes: frozenset = frozenset()) -> str:
    """A wrapper div's body as one string per <p>, blank-line joined -- the
    shape every note/cref/textnote/topical-article body shares, just with
    different per-kind chrome to exclude. Chart tables wrap each cell's text
    in its own <p> too, so selecting <p> alone (not also <td>) is what keeps
    a chart row from being counted twice."""
    paragraphs = []
    for p in div_el.xpath(".//p"):
        cls = set((p.get("class") or "").split())
        if cls & skip_para_classes:
            continue
        text = _flatten_inline(p, skip_inline_classes)
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _harvest_refs(div_el, book_abbrev_to_osis: dict) -> list[tuple[str, int, int]]:
    """Every '#vs-BookAbbrev.C.V' link inside a wrapper div, deduped in
    document order -- covers both a dedicated locator link (a Profile's
    pro-ref, a Note's 'Return to Genesis 1:26' backlink) and any inline
    verse links scattered through the body prose."""
    seen: set[tuple[str, int, int]] = set()
    refs: list[tuple[str, int, int]] = []
    for a in div_el.xpath(".//a[@href]"):
        m = HREF_VERSE_RE.search(a.get("href"))
        if not m:
            continue
        osis = book_abbrev_to_osis.get(m.group(1))
        if osis is None:
            continue
        key = (osis, int(m.group(2)), int(m.group(3)))
        if key not in seen:
            seen.add(key)
            refs.append(key)
    return refs


class DottedIdExtractor(BaseExtractor):
    def extract(self) -> ExtractionResult:
        result = ExtractionResult()
        self.book_abbrev_to_osis: dict = self.config.extra["book_abbrev_to_osis"]

        verse_dir = self.config.extra["verse_dir"]
        for f in sorted((self.root / verse_dir).glob("*.xhtml")) + sorted((self.root / verse_dir).glob("*.html")):
            self._extract_verses(self._parse(f), result)

        if study_notes_dir := self.config.extra.get("study_notes_dir"):
            for f in self._glob(study_notes_dir):
                self._extract_wrapper_notes(self._parse(f), "StudyNote", "study_note", result)

        if crefs_dir := self.config.extra.get("crefs_dir"):
            for f in self._glob(crefs_dir):
                self._extract_wrapper_notes(self._parse(f), "Cref", "cross_reference", result)

        if textnotes_dir := self.config.extra.get("textnotes_dir"):
            for f in self._glob(textnotes_dir):
                self._extract_textnotes(self._parse(f), result)

        if book_intro_dir := self.config.extra.get("book_intro_dir"):
            for f in self._glob(book_intro_dir):
                self._extract_book_intro(self._parse(f), result)

        for wrapper_class, topical_dir in self.config.extra.get("topical_wrapper_dirs", {}).items():
            for f in self._glob(topical_dir):
                self._extract_topical(self._parse(f), wrapper_class, result)

        return result

    def _glob(self, dirname: str) -> list:
        d = self.root / dirname
        if not d.exists():
            return []
        return sorted(d.glob("*.xhtml")) + sorted(d.glob("*.html"))

    def _parse(self, path):
        try:
            tree = lxml_html.parse(str(path), PARSER)
        except Exception:
            return None
        return tree.getroot()

    def _extract_verses(self, root_el, result: ExtractionResult) -> None:
        if root_el is None:
            return

        def is_marker(el):
            return el.tag == "a" and VERSE_ID_RE.match(el.get("id") or "") is not None

        def is_chrome(el):
            if el.tag == "a":
                return True
            cls = set((el.get("class") or "").split())
            return bool(cls & VERSE_CHROME_CLASSES)

        for marker, text in split_by_markers(root_el, is_marker, is_chrome):
            m = VERSE_ID_RE.match(marker.get("id"))
            book_abbrev, chapter, verse = m.groups()
            osis = self.book_abbrev_to_osis.get(book_abbrev)
            if osis is None or not text:
                continue
            result.verses.append(VerseRecord(osis, int(chapter), int(verse), text))

    def _extract_wrapper_notes(self, root_el, wrapper_class: str, note_type: str, result: ExtractionResult) -> None:
        if root_el is None:
            return
        skip_inline = {"note-ref"} if wrapper_class == "StudyNote" else {"cr-ref"}
        for div in root_el.xpath(f"//div[@class='{wrapper_class}']"):
            m = REF_ID_RE.match(div.get("id") or "")
            if not m:
                continue
            book_abbrev, chapter, v1, _c2, v2 = m.groups()
            osis = self.book_abbrev_to_osis.get(book_abbrev)
            if osis is None:
                continue
            text = _wrapper_paragraphs(div, frozenset(), frozenset(skip_inline))
            if not text:
                continue
            verse_end = int(v2) if v2 else int(v1)
            result.notes.append(NoteRecord(osis, int(chapter), int(v1), verse_end, note_type, text))

    def _extract_textnotes(self, root_el, result: ExtractionResult) -> None:
        if root_el is None:
            return
        for div in root_el.xpath("//div[@class='NLT-Textnote']"):
            m = TEXTNOTE_ID_RE.match(div.get("id") or "")
            if not m:
                continue
            book_abbrev, chapter, verse = m.groups()
            osis = self.book_abbrev_to_osis.get(book_abbrev)
            if osis is None:
                continue
            text = _wrapper_paragraphs(div, frozenset(), frozenset({"tn-marker", "tn-ref"}))
            if not text:
                continue
            result.notes.append(NoteRecord(osis, int(chapter), int(verse), int(verse), "footnote", text))

    def _extract_book_intro(self, root_el, result: ExtractionResult) -> None:
        if root_el is None:
            return
        for div in root_el.xpath("//div[contains(concat(' ', @class, ' '), ' BookIntro ')]"):
            m = re.match(r"^([A-Za-z0-9]+)_BookIntro", div.get("id") or "")
            if not m:
                continue
            osis = self.book_abbrev_to_osis.get(m.group(1))
            if osis is None:
                continue
            title_el = div.xpath(
                ".//*[contains(concat(' ', @class, ' '), ' _book ') or "
                "contains(concat(' ', @class, ' '), ' intro-book ')]"
            )
            book_name = title_el[0].text_content().strip() if title_el else osis
            text = _wrapper_paragraphs(div, frozenset({"_book", "intro-book", "intro-info-list", "artfile"}))
            if not text:
                continue
            result.introductions.append(IntroductionRecord(
                scope="book", book=osis, section_name=None,
                title=f"Introduction to {book_name}", text=text,
            ))

    def _extract_topical(self, root_el, wrapper_class: str, result: ExtractionResult) -> None:
        if root_el is None:
            return
        cfg = _TOPICAL_WRAPPER_CONFIG[wrapper_class]
        for div in root_el.xpath(f"//div[@class='{wrapper_class}']"):
            title = None
            for title_class in cfg["title_classes"]:
                title_el = div.xpath(f".//*[contains(concat(' ', @class, ' '), ' {title_class} ')]")
                if title_el:
                    title = title_el[0].text_content().strip()
                    break
            text = _wrapper_paragraphs(div, frozenset(cfg["skip_para_classes"]))
            if not title or not text:
                continue
            refs = _harvest_refs(div, self.book_abbrev_to_osis)
            result.topical_articles.append(TopicalArticleRecord(title=title, text=text, refs=refs))
