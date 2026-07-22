"""The only module that knows about study-notes.db's schema. Extractors never
touch SQL; they hand this an ExtractionResult and a SourceConfig."""
import sqlite3

from study_notes.extractors.base import SourceConfig
from study_notes.models import ExtractionResult


def write_work(conn: sqlite3.Connection, config: SourceConfig, result: ExtractionResult, ingested_at: str) -> None:
    conn.execute(
        "INSERT INTO works (work_id, title, publisher, year, source_id, source_path, "
        "ingested_at, license, license_tier, attribution) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (config.work_id, config.title, config.publisher, config.year, config.work_id,
         str(config.epub_path), ingested_at, config.extra.get("license"), config.license_tier,
         config.extra.get("attribution")),
    )

    conn.executemany(
        "INSERT INTO verses (work_id, book, chapter, verse, text) VALUES (?,?,?,?,?)",
        [(config.work_id, v.book, v.chapter, v.verse, v.text) for v in result.verses],
    )
    conn.executemany(
        "INSERT INTO notes (work_id, book, chapter, verse_start, verse_end, note_type, text) "
        "VALUES (?,?,?,?,?,?,?)",
        [(config.work_id, n.book, n.chapter, n.verse_start, n.verse_end, n.note_type, n.text)
         for n in result.notes],
    )
    conn.executemany(
        "INSERT INTO introductions (work_id, scope, book, section_name, title, text) VALUES (?,?,?,?,?,?)",
        [(config.work_id, i.scope, i.book, i.section_name, i.title, i.text) for i in result.introductions],
    )
    for a in result.topical_articles:
        cur = conn.execute(
            "INSERT INTO topical_articles (work_id, title, text) VALUES (?,?,?)",
            (config.work_id, a.title, a.text),
        )
        conn.executemany(
            "INSERT INTO topical_article_refs (article_id, book, chapter, verse) VALUES (?,?,?,?)",
            [(cur.lastrowid, book, chapter, verse) for book, chapter, verse in a.refs],
        )
    conn.executemany(
        "INSERT INTO images (work_id, figure_id, book, chapter, verse, context_type, file_path, "
        "caption, attribution, width, height) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [(config.work_id, im.figure_id, im.book, im.chapter, im.verse, im.context_type, im.file_path,
          im.caption, im.attribution, im.width, im.height) for im in result.images],
    )
    conn.commit()
