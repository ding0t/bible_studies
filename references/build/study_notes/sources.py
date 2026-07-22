"""Declarative registry of study-Bible EPUBs. Adding a 5th source that fits
an existing family (numeric_id or anchor_walker) means adding one entry here
-- no code changes. A genuinely new markup convention needs a new extractor
module registered in extractors/__init__.py, but still configured here.
"""
from pathlib import Path

from book_map import CSB_NAME_TO_OSIS, SCROLLMAPPER_NAME_TO_OSIS
from study_notes.extractors.base import SourceConfig

BIBLES_DIR = Path("/Volumes/media/bible/bibles")

SOURCES = [
    SourceConfig(
        work_id="csb-ancient-faith-study-bible",
        epub_path=BIBLES_DIR / "CSB Ancient Faith Study Bible.epub",
        title="CSB Ancient Faith Study Bible",
        publisher="Holman Bible Publishers", year=2019,
        license_tier="quotation-only",
        extractor="anchor_walker",
        extra={"name_to_osis": CSB_NAME_TO_OSIS,
               "license": "Copyrighted, commercial study Bible", "attribution": "CSB Ancient Faith Study Bible"},
    ),
    SourceConfig(
        work_id="esv-study-bible",
        epub_path=BIBLES_DIR / "ESV Study Bible - Crossway - 2016.epub",
        title="ESV Study Bible",
        publisher="Crossway", year=2016,
        license_tier="quotation-only",
        extractor="numeric_id",
        extra={
            "note_kinds": [
                {"id_prefix": "n", "note_type": "study_note"},
                {"id_prefix": "f", "note_type": "footnote"},
            ],
            "intro_file_glob": "*.intros.xhtml",
            "intro_name_to_osis": SCROLLMAPPER_NAME_TO_OSIS,  # "Genesis", "2 Samuel" -- same Arabic-numeral style
            "license": "Copyrighted, commercial study Bible", "attribution": "ESV Study Bible, Crossway",
        },
    ),
    SourceConfig(
        work_id="niv-biblical-theology-study-bible",
        epub_path=BIBLES_DIR / "NIV Biblical Theology Study Bible - Zondervan - 2018.epub",
        title="NIV Biblical Theology Study Bible",
        publisher="Zondervan", year=2018,
        license_tier="quotation-only",
        extractor="numeric_id",
        extra={
            "note_kinds": [{"id_prefix": "com", "note_type": "study_note"}],
            "has_sidebar_articles": True,
            "license": "Copyrighted, commercial study Bible", "attribution": "NIV Biblical Theology Study Bible, Zondervan",
        },
    ),
    SourceConfig(
        work_id="nkjv-cultural-backgrounds-study-bible",
        epub_path=BIBLES_DIR / "NKJV Cultural Backgrounds Study Bible - Zondervan - 2017.epub",
        title="NKJV Cultural Backgrounds Study Bible",
        publisher="Zondervan", year=2017,
        license_tier="quotation-only",
        extractor="numeric_id",
        extra={
            "note_kinds": [{"id_prefix": "com", "note_type": "study_note"}],
            "has_sidebar_articles": True,
            "license": "Copyrighted, commercial study Bible", "attribution": "NKJV Cultural Backgrounds Study Bible, Zondervan",
        },
    ),
    SourceConfig(
        work_id="na28-greek-nt",
        epub_path=BIBLES_DIR / "Greek-English Parallel New Testament - NA28-ESV.epub",
        title="NA28 Greek New Testament (from the NA28-ESV Parallel New Testament)",
        publisher="Deutsche Bibelgesellschaft (German Bible Society) / Crossway", year=2015,
        license_tier="quotation-only",
        extractor="numeric_id",
        extra={
            "verse_source": "greek_span",
            "note_kinds": [],  # the paired ESV apparatus here duplicates esv-study-bible's own; skip it
            "license": "Copyrighted, Deutsche Bibelgesellschaft (NA28 critical text)",
            "attribution": "Novum Testamentum Graece, 28th edition (NA28), Deutsche Bibelgesellschaft",
        },
    ),
    SourceConfig(
        work_id="niv-cultural-backgrounds-study-bible",
        epub_path=BIBLES_DIR / "NIV Cultural Backgrounds Study Bible - Zondervan - 2016.epub",
        title="NIV Cultural Backgrounds Study Bible",
        publisher="Zondervan", year=2016,
        license_tier="quotation-only",
        extractor="numeric_id",
        extra={
            "note_kinds": [{"id_prefix": "com", "note_type": "study_note"}],
            "has_sidebar_articles": True,
            "license": "Copyrighted, commercial study Bible", "attribution": "NIV Cultural Backgrounds Study Bible, Zondervan",
        },
    ),
]
