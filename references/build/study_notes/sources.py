"""Declarative registry of study-Bible EPUBs. Adding a source that fits an
existing family (numeric_id, anchor_walker, dotted_id, positional_verse)
means adding one entry here -- no code changes. A genuinely new markup
convention needs a new extractor module registered in extractors/__init__.py,
but still configured here.
"""
from pathlib import Path

from book_map import CSB_NAME_TO_OSIS, NASB_HEADER_TO_OSIS, SCROLLMAPPER_NAME_TO_OSIS, TYNDALE_ABBREV_TO_OSIS
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
    SourceConfig(
        work_id="nlt-life-application-study-bible",
        epub_path=BIBLES_DIR / "NLT Life Application Study Bible, Third Ed - Tyndale House Publishers, Inc.epub",
        title="NLT Life Application Study Bible, Third Edition",
        publisher="Tyndale House Publishers", year=2019,
        license_tier="quotation-only",
        extractor="dotted_id",
        extra={
            "book_abbrev_to_osis": TYNDALE_ABBREV_TO_OSIS,
            "verse_dir": "NLT",
            "study_notes_dir": "StudyNotes",
            "crefs_dir": "NLT-Crefs",
            "textnotes_dir": "NLT-Textnotes",
            "book_intro_dir": "BookIntros",
            "topical_wrapper_dirs": {"Profile": "Profiles", "Chart": "Charts"},
            "license": "NLT text: quotable up to 500 verses / 25% of a work with credit line, per "
                       "Tyndale's standard permission notice (verified in this epub's own copyright "
                       "page). Life Application notes/Bible helps: separately copyrighted, all rights "
                       "reserved -- quotation-only, same as this repo's other study-Bible commentary.",
            "attribution": "NLT Life Application Study Bible, Third Edition, Tyndale House Publishers",
        },
    ),
    SourceConfig(
        work_id="nlt-christian-basics-bible",
        epub_path=BIBLES_DIR / "NLT Bible - Christian Basics Bible.epub",
        title="NLT Christian Basics Bible",
        publisher="Tyndale House Publishers", year=2017,
        license_tier="quotation-only",
        extractor="dotted_id",
        extra={
            "book_abbrev_to_osis": TYNDALE_ABBREV_TO_OSIS,
            "verse_dir": "NLT",
            "textnotes_dir": "NLT-Textnotes",
            "book_intro_dir": "BookIntros",
            "topical_wrapper_dirs": {
                "BasicTruth": "BasicTruths", "GlossaryEntry": "Glossary",
                "Note": "Notes", "Reference": "Articles",
            },
            "license": "NLT text: quotable up to 500 verses / 25% of a work with credit line, per "
                       "Tyndale's standard permission notice (verified in this epub's own copyright "
                       "page, identical wording to the Life Application Study Bible above). Features/Bible "
                       "helps (Beaumont & Manser, 2017): separately copyrighted, all rights reserved.",
            "attribution": "NLT Christian Basics Bible, Tyndale House Publishers",
        },
    ),
    SourceConfig(
        work_id="nasb-1995",
        epub_path=BIBLES_DIR / "New American Standard Bible - The Lockman Foundation - NASB 1995.epub",
        title="New American Standard Bible, 1995 Update",
        publisher="The Lockman Foundation", year=1995,
        license_tier="quotation-only",
        extractor="positional_verse",
        extra={
            "header_to_osis": NASB_HEADER_TO_OSIS,
            "license": "No stated verse threshold in this edition (unlike ESV/CSB/NKJV/NIV/NLT above) -- "
                       "its own copyright page says quotation/reprint requests 'must be directed to and "
                       "approved in writing by The Lockman Foundation.' Loaded here for the same "
                       "verify-a-quotation-against-source use as every other quotation-only work in this "
                       "db, not as a blanket license to quote at will; don't assume a safe-harbor verse "
                       "count the way the other translations here have one.",
            "attribution": "New American Standard Bible, 1995 Update, The Lockman Foundation",
        },
    ),
    SourceConfig(
        work_id="nasb-2020",
        epub_path=BIBLES_DIR / "New American Standard Bible - The Lockman Foundation - NASB 2020.epub",
        title="New American Standard Bible, 2020 Text Edition",
        publisher="The Lockman Foundation", year=2020,
        license_tier="quotation-only",
        extractor="positional_verse",
        extra={
            "header_to_osis": NASB_HEADER_TO_OSIS,
            "license": "Same no-stated-threshold caveat as nasb-1995 above -- see that entry.",
            "attribution": "New American Standard Bible, 2020 Text Edition, The Lockman Foundation",
        },
    ),
]
