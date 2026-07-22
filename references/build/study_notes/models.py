"""Intermediate representation for study-Bible extraction.

Every extractor (regardless of which EPUB family it handles) produces these
same records. Nothing downstream -- the writer, the schema -- knows or cares
which publisher's markup produced them. This is the seam that keeps adding a
5th study Bible from touching any existing code: write a new extractor that
yields these types, register it, done.
"""
from dataclasses import dataclass, field


@dataclass
class VerseRecord:
    book: str            # OSIS code
    chapter: int
    verse: int
    text: str


@dataclass
class NoteRecord:
    book: str
    chapter: int
    verse_start: int
    verse_end: int        # equal to verse_start for a single-verse note
    note_type: str         # 'footnote' | 'study_note' | 'cross_reference'
    text: str


@dataclass
class IntroductionRecord:
    scope: str             # 'book' | 'section' | 'testament' | 'whole-bible'
    book: str | None       # OSIS code, None unless scope == 'book'
    section_name: str | None
    title: str
    text: str               # full essay, subsection headers preserved as markdown


@dataclass
class TopicalArticleRecord:
    title: str
    text: str
    refs: list[tuple[str, int, int]] = field(default_factory=list)  # (book, chapter, verse)


@dataclass
class ImageRecord:
    figure_id: str | None
    book: str | None
    chapter: int | None
    verse: int | None
    context_type: str      # 'introduction' | 'note' | 'topical_article' | 'standalone'
    file_path: str          # path to the extracted image file, relative to the work's image dir
    caption: str | None
    attribution: str | None
    width: int | None
    height: int | None


@dataclass
class ExtractionResult:
    verses: list[VerseRecord] = field(default_factory=list)
    notes: list[NoteRecord] = field(default_factory=list)
    introductions: list[IntroductionRecord] = field(default_factory=list)
    topical_articles: list[TopicalArticleRecord] = field(default_factory=list)
    images: list[ImageRecord] = field(default_factory=list)
