"""Fifth extractor family: a Bible module held in a Microsoft Access (Jet 4.0) database.

The other four families all parse EPUB markup. This one does not parse markup at all -- it reads a
relational table -- which is why it needed a new family rather than a config entry in sources.py.
BibleShow-style `.bib` modules are Jet databases despite the extension, with a flat `Bible` table
(Book/Chapter/Verse/Scripture) and a parallel `Footnotes` table.

Read via the `mdb-export` CLI from mdbtools (`brew install mdbtools`) rather than a Python driver:
there is no maintained pure-Python reader for Jet 4.0, and shelling out to the standard tool is
less code and less risk than a bespoke parser for a proprietary binary format. If mdbtools is
missing the extractor says so plainly instead of failing three frames down.

Book numbering in these modules is the canonical 1-66 Protestant order, so `NUM_TO_OSIS` maps it
directly -- verified against the module's own `Structure` table (Gen=1, Ps=19, Song=22, Matt=40,
Rev=66) rather than assumed.
"""

from __future__ import annotations

import csv
import io
import re
import shutil
import subprocess
from pathlib import Path

from book_map import NUM_TO_OSIS
from study_notes.extractors.base import BaseExtractor
from study_notes.models import ExtractionResult, NoteRecord, VerseRecord

# Verse text carries presentation markup: <br> and empty padded <span>s for poetic lines, <i> for
# words supplied by the translators, <p> for paragraph starts. The other works in this database
# store plain text, so it all comes out -- the italics distinction is real but has nowhere to live
# in the `verses` schema, and inventing one for a single source would be worse than losing it.
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")

# An asterisk marks the word a footnote hangs off ("*formless"). The footnote itself is in the
# Footnotes table keyed by chapter.verse, so the marker carries no information here and comes out.
#
# It has to come out in two steps. Usually the asterisk follows a space and simply deletes. But the
# module sometimes parks it *between two elements* rather than inside one --
#   <span class='Isus'>...‘I am the</span>*<span class='Isus'>Christ,’...</span>
# -- so once tags are stripped the marker is the only thing separating two words, and deleting it
# outright yields "theChrist". Verified against the module: 15,320 asterisks follow a space or
# punctuation, 6 are glued to a letter, and none are textual content.
_MARKER_BETWEEN_WORDS = re.compile(r"(?<=[A-Za-z0-9])\*(?=[A-Za-z0-9])")
_MARKER = re.compile(r"\*")

# A pilcrow starts a new paragraph in the module's own display convention. Presentation, not text.
_PILCROW = re.compile(r"¶\s*")

# Footnote bodies arrive prefixed with their own reference, e.g. "1.2: Or <i>waste</i>". The
# chapter/verse are already columns, so the prefix is redundant and is stripped for consistency
# with how the EPUB families store note text.
_NOTE_PREFIX = re.compile(r"^\s*\d+[.:]\d+\s*:\s*")


def _clean(raw: str) -> str:
    text = raw.replace("<br>", " ").replace("<br/>", " ")
    text = _TAG.sub("", text)
    text = _MARKER_BETWEEN_WORDS.sub(" ", text)
    text = _MARKER.sub("", text)
    text = _PILCROW.sub("", text)
    return _WS.sub(" ", text).strip()


class JetBibleExtractor(BaseExtractor):
    """Reads a Jet/Access Bible module. Ignores `unzipped_root` -- there is nothing to unzip."""

    needs_unzip = False

    def _table(self, name: str) -> list[dict[str, str]]:
        if not shutil.which("mdb-export"):
            raise SystemExit(
                "mdb-export not found. This source is a Microsoft Access database and needs "
                "mdbtools:  brew install mdbtools"
            )
        proc = subprocess.run(
            ["mdb-export", str(self.config.epub_path), name],
            capture_output=True, text=True, check=True,
        )
        return list(csv.DictReader(io.StringIO(proc.stdout)))

    def extract(self) -> ExtractionResult:
        result = ExtractionResult()

        for row in self._table("Bible"):
            book = NUM_TO_OSIS.get(int(row["Book"]))
            text = _clean(row["Scripture"] or "")
            if book and text:
                result.verses.append(
                    VerseRecord(book=book, chapter=int(row["Chapter"]),
                                verse=int(row["Verse"]), text=text)
                )

        for row in self._table("Footnotes"):
            book = NUM_TO_OSIS.get(int(row["Book"]))
            body = _clean(_NOTE_PREFIX.sub("", row["Footnote"] or ""))
            if book and body:
                verse = int(row["Verse"])
                result.notes.append(
                    NoteRecord(book=book, chapter=int(row["Chapter"]), verse_start=verse,
                               verse_end=verse, note_type="footnote", text=body)
                )

        return result
