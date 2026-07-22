"""Low-level EPUB mechanics shared by every extractor family.

An EPUB is just a zip file. These helpers handle unzipping, image export, and
the one non-trivial algorithm every family needs (splitting a document's text
by marker elements) -- the parts that have nothing to do with any particular
publisher's specific class names or id schemes. Extractor families own their
own marker-matching logic in their own modules, but call back into
split_by_markers() rather than re-solving text-flattening themselves.
"""
import re
import zipfile
from collections.abc import Callable
from pathlib import Path

from lxml import etree

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """Collapse source pretty-printing whitespace (newlines/indentation from
    the HTML, not deliberate content) to single spaces. Shared so every
    extractor's text ends up consistently formatted, not just split_by_markers'."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def split_by_markers(
    root: etree._Element,
    is_marker: Callable[[etree._Element], bool],
    skip_subtree: Callable[[etree._Element], bool] | None = None,
) -> list[tuple[etree._Element, str]]:
    """Walk `root` in document order and split its full text content at every
    element for which is_marker(el) is True. Returns [(marker_element, text)],
    where `text` is everything in the document between this marker and the
    next one (or the end of the document), regardless of how deeply the
    intervening content is nested in the tree.

    A marker's own direct text is never included (a marker denotes a
    position -- e.g. a zero-width anchor span, or a verse-number label
    wrapping the id -- not content). skip_subtree(el), if given, excludes an
    entire element's text AND all of its descendants' text (but not the tail
    that follows it) -- e.g. inline footnote-reference links, which are
    navigation chrome, not part of the verse itself.

    This is the one genuinely tricky bit of flattening semantically-marked-up
    HTML back into plain verse/note text -- get it right once here rather
    than per-extractor. Uses start/end tree events so text and tail content
    both land in correct reading order even across nested tags.
    """
    segments: list[tuple[etree._Element, str]] = []
    current_marker: etree._Element | None = None
    buffer: list[str] = []
    skip_depth = 0

    def flush():
        if current_marker is not None:
            segments.append((current_marker, normalize_whitespace("".join(buffer))))
        buffer.clear()

    for action, el in etree.iterwalk(root, events=("start", "end")):
        is_skip_root = skip_subtree(el) if skip_subtree else False
        if action == "start":
            if is_marker(el):
                flush()
                current_marker = el
            if is_skip_root:
                skip_depth += 1
            elif skip_depth == 0 and el.text and not is_marker(el):
                buffer.append(el.text)
        elif action == "end":
            if is_skip_root:
                skip_depth -= 1
            if skip_depth == 0 and el.tail:
                buffer.append(el.tail)
    flush()
    return segments


def unzip_epub(epub_path: Path, dest_dir: Path) -> Path:
    """Unzip once, reuse across runs -- these are large files (up to 140MB)."""
    if dest_dir.exists() and any(dest_dir.iterdir()):
        return dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(epub_path) as zf:
        zf.extractall(dest_dir)
    return dest_dir


def export_image(src_path: Path, work_image_dir: Path) -> str:
    """Copy an image out of the unzipped EPUB tree into the work's own image
    directory (flat, by filename) and return the path stored in the DB, as a
    string relative to work_image_dir."""
    work_image_dir.mkdir(parents=True, exist_ok=True)
    dest = work_image_dir / src_path.name
    if not dest.exists():
        dest.write_bytes(src_path.read_bytes())
    return src_path.name


def parse_bccv(id_str: str, prefix: str) -> tuple[str, int, int] | None:
    """Parse a 'PREFIX + BBCCCVVV' id (e.g. 'v01001001') into (book_num, chapter, verse).
    Returns None if id_str doesn't match. Book number -> OSIS code is the
    caller's job (via book_map), since numbering schemes are shared across
    these publishers but this function shouldn't assume a specific book list."""
    if not id_str.startswith(prefix):
        return None
    digits = id_str[len(prefix):]
    if len(digits) != 8 or not digits.isdigit():
        return None
    book_num, chapter, verse = digits[0:2], digits[2:5], digits[5:8]
    return book_num, int(chapter), int(verse)
