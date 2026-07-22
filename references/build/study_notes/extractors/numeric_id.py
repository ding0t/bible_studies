"""Extractor family for study Bibles using the shared 'BBCCCVVV' numeric id
scheme (id="v01001001" for verses, id="com01001001" / id="n01001026" etc. for
notes) -- covers ESV Study Bible, NIV Biblical Theology Study Bible, and NKJV
Cultural Backgrounds Study Bible, despite their differing file layouts,
because the ids themselves are self-describing: we don't need to know which
file a book's content lives in, just scan everything and let the id say what
it is.

Per-source differences (which note kinds exist, what prefix each uses) are
supplied via SourceConfig.extra['note_kinds'] rather than hardcoded here --
that's what makes this one module cover three publishers' different note
structures (ESV: separate study-note/footnote/cross-ref files; NIV/NKJV:
a single interleaved commentary stream) without three copies of this class.
"""
import re

from lxml import html as lxml_html

from book_map import BOOK_NUM_TO_OSIS
from study_notes.epub_utils import export_image, normalize_whitespace, split_by_markers
from study_notes.extractors.base import BaseExtractor
from study_notes.models import (
    ExtractionResult, ImageRecord, IntroductionRecord, NoteRecord, TopicalArticleRecord, VerseRecord,
)

VERSE_ID_RE = re.compile(r"^v(\d{2})(\d{3})(\d{3})$")
BCCV_ANYWHERE_RE = re.compile(r"(\d{2})(\d{3})(\d{3})")

PARSER = lxml_html.HTMLParser(recover=True, encoding="utf-8")


def _note_id_re(prefix: str) -> re.Pattern:
    return re.compile(rf"^{re.escape(prefix)}(\d{{2}})(\d{{3}})(\d{{3}})(?:-(\d{{2}})(\d{{3}})(\d{{3}}))?$")


class NumericIdExtractor(BaseExtractor):
    def extract(self) -> ExtractionResult:
        result = ExtractionResult()
        note_kinds = self.config.extra.get("note_kinds", [])

        for html_file in sorted(self.root.rglob("*.xhtml")) + sorted(self.root.rglob("*.html")):
            try:
                tree = lxml_html.parse(str(html_file), PARSER)
            except Exception:
                continue
            root_el = tree.getroot()
            if root_el is None:
                continue

            if self.config.extra.get("verse_source") == "greek_span":
                self._extract_verses_greek_span(root_el, result)
            else:
                self._extract_verses(root_el, result)
            for kind in note_kinds:
                self._extract_notes(root_el, kind["id_prefix"], kind["note_type"], result)
            self._extract_images(root_el, html_file, result)
            if self.config.extra.get("has_sidebar_articles"):
                self._extract_topical_articles(root_el, result)
            if self.config.extra.get("intro_file_glob") and html_file.match(self.config.extra["intro_file_glob"]):
                self._extract_introductions(root_el, result)

        return result

    def _extract_verses(self, root_el, result: ExtractionResult) -> None:
        def is_verse_marker(el):
            return VERSE_ID_RE.match(el.get("id") or "") is not None

        _CHROME_CLASSES = {"heading", "chapter-num", "verse-num", "book-name"}

        def is_chrome(el):
            # inline <a> links within verse text are always footnote/cross-ref/
            # study-note reference markers, never real scripture content; these
            # classes are section headings and chapter/verse-number labels that
            # sometimes reuse a verse's own id (ESV puts id="v01001001" on a
            # heading <p> that precedes the actual, unanchored verse-1 paragraph)
            cls = set((el.get("class") or "").split())
            return el.tag == "a" or bool(cls & _CHROME_CLASSES)

        for marker, text in split_by_markers(root_el, is_verse_marker, is_chrome):
            m = VERSE_ID_RE.match(marker.get("id"))
            book_num, chapter, verse = m.groups()
            osis = BOOK_NUM_TO_OSIS.get(book_num)
            if osis is None or not text:
                continue
            result.verses.append(VerseRecord(osis, int(chapter), int(verse), text))

    def _extract_verses_greek_span(self, root_el, result: ExtractionResult) -> None:
        """For parallel Greek/English editions where a verse's id sometimes
        lands on a heading paragraph rather than the verse's own paragraph
        (same quirk as ESV's English text -- see _extract_verses), and Greek
        and English paragraphs both fall in the same marker-to-marker span, so
        the generic split_by_markers flow-splitting approach would mix the two
        languages together. Instead: walk in document order, track the current
        (book, chapter, verse) from whichever v-id or bare verse-number span
        was seen most recently, and pull text only from span.greek-text --
        everything else (the paired English, cross-refs, footnotes) is ignored
        outright rather than extracted and discarded, since we already have
        this edition's English apparatus from the study Bible it's paired with.
        """
        book_num = chapter = verse = None
        current_key = None   # (osis, chapter, verse) for whatever we're currently accumulating
        buffer: list[str] = []

        def flush():
            if current_key is not None:
                text = normalize_whitespace(" ".join(buffer))
                if text:
                    result.verses.append(VerseRecord(current_key[0], current_key[1], current_key[2], text))
            buffer.clear()

        for el in root_el.iter():
            el_id = el.get("id") or ""
            m = VERSE_ID_RE.match(el_id)
            if m:
                book_num, chapter, verse = m.groups()
                chapter, verse = int(chapter), int(verse)
                continue
            cls = (el.get("class") or "").split()
            if "greek-verse-num" in cls and book_num is not None:
                num_text = (el.text or "").strip()
                if num_text.isdigit():
                    verse = int(num_text)
                continue
            if "greek-text" in cls and book_num is not None:
                osis = BOOK_NUM_TO_OSIS.get(book_num)
                if not osis:
                    continue
                key = (osis, chapter, verse)
                if key != current_key:
                    # poetic/hymnic passages (1 Tim 3:16, Col 1:16, Rev doxologies)
                    # split one verse across several greek-text spans (one per
                    # stich) with no new marker in between -- concatenate rather
                    # than emit a row per span
                    flush()
                    current_key = key
                buffer.append(el.text_content())
        flush()

    def _extract_notes(self, root_el, prefix: str, note_type: str, result: ExtractionResult) -> None:
        note_re = _note_id_re(prefix)

        def is_note_marker(el):
            return note_re.match(el.get("id") or "") is not None

        for marker, text in split_by_markers(root_el, is_note_marker):
            m = note_re.match(marker.get("id"))
            book_num, c1, v1, _, c2, v2 = m.groups()
            osis = BOOK_NUM_TO_OSIS.get(book_num)
            if osis is None or not text:
                continue
            v_end = int(v2) if v2 else int(v1)
            c_end_verse = int(v_end)
            result.notes.append(NoteRecord(osis, int(c1), int(v1), c_end_verse, note_type, text))

    def _extract_images(self, root_el, html_file, result: ExtractionResult) -> None:
        self._extract_images_figure_pattern(root_el, html_file, result)
        self._extract_images_object_pattern(root_el, html_file, result)

    def _extract_images_figure_pattern(self, root_el, html_file, result: ExtractionResult) -> None:
        """NIV/NKJV: <div class="figure"><p class="fig"><img/></p><p class="figcap">...<p class="figatr">..."""
        for fig in root_el.xpath("//*[contains(concat(' ', @class, ' '), ' figure ')]"):
            img = fig.find(".//img")
            if img is None or not img.get("src"):
                continue
            src_path = (html_file.parent / img.get("src")).resolve()
            if not src_path.exists():
                continue
            caption_el = fig.xpath(".//*[contains(concat(' ', @class, ' '), ' figcap ')]")
            attr_el = fig.xpath(".//*[contains(concat(' ', @class, ' '), ' figatr ')]")
            result.images.append(ImageRecord(
                figure_id=fig.get("id"),
                book=None, chapter=None, verse=None,   # nearest-verse linking is a v2 refinement
                context_type="note",
                file_path=export_image(src_path, self.image_dir),
                caption=caption_el[0].text_content().strip() if caption_el else None,
                attribution=attr_el[0].text_content().strip() if attr_el else None,
                width=int(img.get("width")) if img.get("width", "").isdigit() else None,
                height=int(img.get("height")) if img.get("height", "").isdigit() else None,
            ))

    def _extract_images_object_pattern(self, root_el, html_file, result: ExtractionResult) -> None:
        """ESV: <div class="object map"><h3>title</h3><p class="era">date</p>
        <p class="caption">...</p><p class="image"><img/></p></div> -- also covers
        class="object chart"/"object illustration" etc, any 'object' variant."""
        for obj in root_el.xpath("//*[contains(concat(' ', @class, ' '), ' object ')]"):
            img = obj.find(".//img")
            if img is None or not img.get("src"):
                continue
            src_path = (html_file.parent / img.get("src")).resolve()
            if not src_path.exists():
                continue
            caption_el = obj.xpath(".//*[contains(concat(' ', @class, ' '), ' caption ')]")
            title_el = obj.xpath(".//h3")
            caption = caption_el[0].text_content().strip() if caption_el else None
            title = title_el[0].text_content().strip() if title_el else None
            result.images.append(ImageRecord(
                figure_id=obj.get("id"), book=None, chapter=None, verse=None,
                context_type="note",
                file_path=export_image(src_path, self.image_dir),
                caption=f"{title}: {caption}" if title and caption else (title or caption),
                attribution=None,
                width=int(img.get("width")) if img.get("width", "").isdigit() else None,
                height=int(img.get("height")) if img.get("height", "").isdigit() else None,
            ))

    def _extract_topical_articles(self, root_el, result: ExtractionResult) -> None:
        """Sidebar divs come in two flavors in this family: pure image wrappers
        (already handled by _extract_images, which finds the nested div.figure
        regardless of its sidebar parent) and real topical essays (p.sbh title +
        p.sbaft/p.sb body paragraphs). Skip the former here by checking for a
        nested figure; skip p.sbo ("go to index") and p.sb1t (running-header
        chrome) paragraphs; anchor to a verse only if the id actually encodes one
        (front-matter essays often don't)."""
        for sidebar in root_el.xpath("//*[contains(concat(' ', @class, ' '), ' sidebar ')]"):
            # NOTE: don't skip based on containing a div.figure -- nearly every
            # article sidebar also wraps a decorative rule-line image, so that's
            # not a reliable "this is image-only" signal. Presence of a p.sbh
            # title is: pure-image sidebars never have one.
            title_el = sidebar.xpath(".//*[contains(concat(' ', @class, ' '), ' sbh ')]")
            if not title_el:
                continue
            title = title_el[0].text_content().strip()

            body_paras = sidebar.xpath(
                ".//p[contains(concat(' ', @class, ' '), ' sbaft ') or "
                "(contains(concat(' ', @class, ' '), ' sb ') and not(contains(@class, 'sb1')) "
                "and not(contains(@class, 'sbh')) and not(contains(@class, 'sbo')))]"
            )
            text = "\n\n".join(p.text_content().strip() for p in body_paras if p.text_content().strip())
            if not title or not text:
                continue

            refs = []
            id_match = BCCV_ANYWHERE_RE.search(sidebar.get("id") or "")
            if id_match:
                book_num, chapter, verse = id_match.groups()
                osis = BOOK_NUM_TO_OSIS.get(book_num)
                if osis:
                    refs.append((osis, int(chapter), int(verse)))

            result.topical_articles.append(TopicalArticleRecord(title=title, text=text, refs=refs))

    def _extract_introductions(self, root_el, result: ExtractionResult) -> None:
        """ESV: dedicated per-book *.intros.xhtml files -- <h1 class="book-title">
        names the book, <h2 class="intro-heading"> subsections, <p class="normal">
        body paragraphs, flattened to one essay per book with headers as markdown."""
        book_title_el = root_el.xpath("//h1[contains(concat(' ', @class, ' '), ' book-title ')]")
        if not book_title_el:
            return
        book_name = book_title_el[0].text_content().strip()
        # most are a single book ("Genesis", "2 Samuel" -- Arabic numeral, per the
        # actual ids checked); some are combined-book essays ("1-2 Samuel") that
        # don't map to one OSIS code -- keep those as a named section instead
        osis = self.config.extra["intro_name_to_osis"].get(book_name)
        scope = "book" if osis else "section"

        top_h1 = root_el.xpath("//h1[not(contains(concat(' ', @class, ' '), ' book-title '))]")
        title = top_h1[0].text_content().strip() if top_h1 else f"Introduction to {book_name}"

        lines = []
        for el in root_el.xpath("//h2 | //p[contains(concat(' ', @class, ' '), ' normal ')]"):
            text = el.text_content().strip()
            if not text:
                continue
            if el.tag == "h2":
                lines.append(f"## {text}")
            else:
                lines.append(text)

        result.introductions.append(IntroductionRecord(
            scope=scope, book=osis, section_name=None if osis else book_name,
            title=title, text="\n\n".join(lines),
        ))
