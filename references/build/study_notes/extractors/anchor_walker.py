"""Extractor family for study Bibles that mark verses with zero-width
'start-BookName.C.V' anchor spans and footnotes as separately-anchored
<aside> elements (id="fn.BookName.C.V.N") -- covers CSB Ancient Faith Study
Bible. Book introductions are their own structured <div class="introblock">
block per book, extracted whole (subsections flattened to markdown headers)
rather than split into a row per subsection, since "show me the introduction
to Job" should read as one coherent essay.
"""
import re

from lxml import html as lxml_html

from study_notes.epub_utils import export_image, split_by_markers
from study_notes.extractors.base import BaseExtractor
from study_notes.models import ExtractionResult, ImageRecord, IntroductionRecord, NoteRecord, VerseRecord

VERSE_ID_RE = re.compile(r"^start-([A-Za-z0-9_]+)\.(\d+)\.(\d+)$")
FOOTNOTE_ID_RE = re.compile(r"^fn\.([A-Za-z0-9_]+)\.(\d+)\.(\d+)\.(\d+)$")

PARSER = lxml_html.HTMLParser(recover=True, encoding="utf-8")

# maps introblock <p class="..."> styles to a markdown heading level, so a
# book intro's internal structure survives as one readable essay
_INTRO_HEADING_CLASSES = {"introbook": "#", "introhead": "##"}


class AnchorWalkerExtractor(BaseExtractor):
    """Reads config.extra['name_to_osis'] -- a book-name-to-OSIS mapping,
    since this family's ids use book names rather than numbers, and (per
    book_map.py) different products in this family may spell them differently."""

    def extract(self) -> ExtractionResult:
        self.name_to_osis: dict[str, str] = self.config.extra["name_to_osis"]
        result = ExtractionResult()
        for html_file in sorted(self.root.rglob("*.html")) + sorted(self.root.rglob("*.xhtml")):
            try:
                tree = lxml_html.parse(str(html_file), PARSER)
            except Exception:
                continue
            root_el = tree.getroot()
            if root_el is None:
                continue
            self._extract_verses(root_el, result)
            self._extract_footnotes(root_el, result)
            self._extract_introductions(root_el, result)
            self._extract_images(root_el, html_file, result)
        return result

    def _extract_verses(self, root_el, result: ExtractionResult) -> None:
        def is_verse_marker(el):
            return VERSE_ID_RE.match(el.get("id") or "") is not None

        def is_chrome(el):
            # <a> links (footnote refs) and the visible chapter/verse-number
            # labels are navigation chrome, not part of the verse itself
            cls = (el.get("class") or "").split()
            return el.tag == "a" or "chapternumber" in cls or "versenumber" in cls

        for marker, text in split_by_markers(root_el, is_verse_marker, is_chrome):
            book_name, chapter, verse = VERSE_ID_RE.match(marker.get("id")).groups()
            osis = self.name_to_osis.get(book_name)
            if osis is None or not text:
                continue
            result.verses.append(VerseRecord(osis, int(chapter), int(verse), text))

    def _extract_footnotes(self, root_el, result: ExtractionResult) -> None:
        for aside in root_el.xpath("//aside[@id]"):
            m = FOOTNOTE_ID_RE.match(aside.get("id"))
            if not m:
                continue
            book_name, chapter, verse, _n = m.groups()
            osis = self.name_to_osis.get(book_name)
            text = aside.text_content().strip()
            if osis is None or not text:
                continue
            result.notes.append(NoteRecord(osis, int(chapter), int(verse), int(verse), "footnote", text))

    def _extract_introductions(self, root_el, result: ExtractionResult) -> None:
        for block in root_el.xpath("//*[contains(concat(' ', @class, ' '), ' introblock ')]"):
            book_name = None
            title = None
            lines = []
            for p in block.xpath(".//p"):
                cls = (p.get("class") or "").strip()
                text = p.text_content().strip()
                if not text:
                    continue
                if cls == "introbook":
                    book_name, title = text, text
                elif cls in _INTRO_HEADING_CLASSES:
                    lines.append(f"{_INTRO_HEADING_CLASSES[cls]} {text}")
                elif cls == "preintro":
                    continue  # just says "Introduction to" -- redundant with the title
                else:
                    lines.append(text)
            if book_name is None:
                continue
            osis = self.name_to_osis.get(book_name.replace(" ", ""))  # introbook text has spaces, ids don't
            if osis is None:
                continue
            result.introductions.append(IntroductionRecord(
                scope="book", book=osis, section_name=None,
                title=title or f"Introduction to {book_name}",
                text="\n\n".join(lines),
            ))

    def _extract_images(self, root_el, html_file, result: ExtractionResult) -> None:
        for fig in root_el.xpath("//figure | //*[contains(concat(' ', @class, ' '), ' figure ')]"):
            img = fig.find(".//img")
            if img is None or not img.get("src"):
                continue
            src_path = (html_file.parent / img.get("src")).resolve()
            if not src_path.exists():
                continue
            caption_el = fig.xpath(".//figcaption | .//*[contains(concat(' ', @class, ' '), ' figcap ')]")
            result.images.append(ImageRecord(
                figure_id=fig.get("id"), book=None, chapter=None, verse=None,
                context_type="standalone",
                file_path=export_image(src_path, self.image_dir),
                caption=caption_el[0].text_content().strip() if caption_el else None,
                attribution=None,
                width=int(img.get("width")) if img.get("width", "").isdigit() else None,
                height=int(img.get("height")) if img.get("height", "").isdigit() else None,
            ))
