"""Extractor family for plain calibre-converted reflow epubs with no
per-verse ids at all -- covers the NASB 1995/2020 epubs (The Lockman
Foundation), and presumably any similarly bare commercial epub conversion.
Verse boundaries are recovered positionally: an ALL-CAPS '<p class="head">
BOOK NAME</p>' announces a chapter (confirmed one chapter per split file,
not split mid-chapter, across both NASB editions), and a verse number is
whichever <b>/<sup> element's own direct text is a bare digit -- the first
verse of a chapter is <b>, the rest are <sup>, but both share that "own text
is just digits" signature, which is what's actually matched rather than the
specific tag/class (calibre's exact tag choice isn't a reliable contract).

Deliberately verse-text only. The same files also carry translators' notes,
but as a bracketed '[... ]' aside dropped inline in the flow wherever a
footnote falls -- sometimes after a lettered <a id="fNN"> anchor (prose
books), sometimes with no anchor at all, just the literal brackets (Psalms'
poetry layout, confirmed by checking Psalm 23 specifically after an
anchor-only skip left its brackets leaking into verse text) -- rather than
one note per verse as a self-contained element. Lower value, high
fragility, out of scope for this pass; the bracket-text state machine below
exists only to keep that aside from leaking into verse text, not to
capture it, and matches on the literal '[' / ']' characters themselves
since that's the one thing both forms share.
"""
import re

from lxml import etree
from lxml import html as lxml_html

from study_notes.epub_utils import normalize_whitespace
from study_notes.extractors.base import BaseExtractor
from study_notes.models import ExtractionResult, VerseRecord

PARSER = lxml_html.HTMLParser(recover=True, encoding="utf-8")

HEAD_RE = re.compile(r"^(.+?)\s+(\d+)\s*$")


class PositionalVerseExtractor(BaseExtractor):
    def extract(self) -> ExtractionResult:
        result = ExtractionResult()
        header_to_osis: dict = self.config.extra["header_to_osis"]
        text_dir = self.config.extra.get("text_dir", "text")

        for html_file in sorted((self.root / text_dir).glob("*.html")):
            try:
                tree = lxml_html.parse(str(html_file), PARSER)
            except Exception:
                continue
            root_el = tree.getroot()
            if root_el is None:
                continue
            self._extract_file(root_el, header_to_osis, result)

        return result

    def _extract_file(self, root_el, header_to_osis: dict, result: ExtractionResult) -> None:
        head_el = root_el.xpath("//p[@class='head']")
        if not head_el:
            return
        m = HEAD_RE.match((head_el[0].text or "").strip())
        if not m:
            return
        osis = header_to_osis.get(m.group(1).strip().upper())
        if osis is None:
            return
        chapter = int(m.group(2))

        verse = None
        buffer: list[str] = []
        in_footnote_zone = False

        def flush():
            if verse is not None:
                text = normalize_whitespace("".join(buffer))
                if text:
                    result.verses.append(VerseRecord(osis, chapter, verse, text))
            buffer.clear()

        def append_text(chunk):
            nonlocal in_footnote_zone
            while chunk:
                if in_footnote_zone:
                    idx = chunk.find("]")
                    if idx == -1:
                        return
                    chunk = chunk[idx + 1:]
                    in_footnote_zone = False
                else:
                    idx = chunk.find("[")
                    if idx == -1:
                        buffer.append(chunk)
                        return
                    buffer.append(chunk[:idx])
                    chunk = chunk[idx + 1:]
                    in_footnote_zone = True

        for action, el in etree.iterwalk(root_el, events=("start", "end")):
            if action == "start":
                own_text = (el.text or "").strip()
                if el.tag in ("b", "sup") and own_text.isdigit():
                    flush()
                    verse = int(own_text)
                    in_footnote_zone = False
                    continue
                if el.tag == "a":
                    continue  # footnote-ref letters, "[Books]" nav -- chrome, never content
                if el.tag == "sup" and len(own_text) == 1 and own_text.isalpha():
                    continue  # bare footnote-ref letter -- poetry sections skip the <a> wrapper
                if el.text:
                    append_text(el.text)
            elif action == "end":
                if el.tail:
                    append_text(el.tail)
        flush()
