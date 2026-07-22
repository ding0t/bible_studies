-- lexicon-restricted.db: quotation-only lexicon/reference works (starting
-- with TWOT). Sibling to study-notes.db's local-only master -- never
-- committed, lives entirely outside the git repo.

CREATE TABLE works (
    work_id TEXT PRIMARY KEY,
    title TEXT, publisher TEXT, year INTEGER,
    source_path TEXT, ingested_at TEXT,
    license TEXT, license_tier TEXT NOT NULL,
    attribution TEXT
);

CREATE TABLE entries (
    work_id TEXT NOT NULL REFERENCES works(work_id),
    key TEXT NOT NULL,              -- TWOT MAIN root number, e.g. '6' -- the citation scheme other works use
    lemma TEXT,                      -- Hebrew, from our verified hebrew-lexicon data, NOT OCR
    transliteration TEXT,             -- from verified data, NOT OCR
    strongs_ids TEXT,                 -- JSON list, e.g. '["H1"]' -- from verified data, aggregated across all sub-entries
    bdb_id TEXT,                      -- from verified data
    short_gloss TEXT,                  -- from verified data (LexicalIndex.xml's own brief def)
    main_text TEXT,                     -- discussion prose only (Bibliography/initials split out below), from OCR
    bibliography TEXT,                   -- from OCR, split out via the 'Bibliography:' marker
    contributor_initials TEXT,            -- e.g. 'JBP' -- from OCR, split out via the confirmed-initials roster
    source_pages TEXT,                     -- JSON list of 0-indexed PDF page numbers, for provenance/spot-checking
    extraction_source TEXT,                 -- which OCR source + segmentation strategy won this entry,
                                              -- e.g. 'colsplit', 'colsplit-blockwalk' -- for review prioritization
    boundary_text TEXT,                      -- literal ~80 raw chars where segmentation decided this entry
                                               -- starts -- lets a reviewer see the actual matched evidence
                                               -- (or a running-header lookalike/wrong match) directly, not
                                               -- just the final cleaned text
    text_confidence TEXT,                   -- 'verified' | 'suspect' | 'unverified' | 'not-found' | 'manual'
    manually_corrected INTEGER DEFAULT 0,     -- 1 once a human has confirmed/fixed main_text via the
                                               -- <<<N>>> review-file marker workflow -- takes precedence
                                               -- over automated re-extraction
    derivative_heading TEXT                    -- 'derivatives' | 'assumed-root' | NULL (no derivatives list
                                                 -- located, or none exists) -- which of TWOT's two distinct
                                                 -- list-introduction conventions this root uses. 'derivatives'
                                                 -- means the root HAS independent meaning of its own (its main_text
                                                 -- above is generally about the root itself); 'assumed-root'
                                                 -- ("Assumed root of the following.") means the root is a pure
                                                 -- grammatical construct with no meaning of its own, so main_text
                                                 -- is naturally about whichever derivative is substantive, not the
                                                 -- root as such. From derivative_structure.py, not OCR.
);
CREATE INDEX idx_entries_key ON entries(key);
CREATE INDEX idx_entries_strongs ON entries(strongs_ids);

CREATE TABLE derivatives (
    work_id TEXT NOT NULL REFERENCES works(work_id),
    parent_key TEXT NOT NULL REFERENCES entries(key),  -- the main root, e.g. '6'
    key TEXT NOT NULL,               -- the sub-entry, e.g. '6a' -- 100% populated from verified data,
                                       -- independent of whether the parent's main_text was ever found
    lemma TEXT, transliteration TEXT,  -- from verified hebrew-lexicon data, NOT OCR
    strongs_ids TEXT,                   -- JSON list
    bdb_id TEXT,
    gloss TEXT,                           -- from verified data (LexicalIndex.xml's brief def)
    main_text TEXT,                        -- VERBATIM TWOT text for this derivative's own list-item line
                                             -- (plus any attached note beyond it), from the PDF's embedded
                                             -- text layer (derivative_structure.py) -- deliberately richer
                                             -- than lemma/transliteration/gloss above (which come from
                                             -- verified but terse hebrew-lexicon data): TWOT's own printed
                                             -- phrasing can carry a fuller gloss, an inline citation, or a
                                             -- usage note the verified data doesn't. NULLABLE -- only null
                                             -- when the derivative's own list block couldn't be located at
                                             -- all (see combine_sources.py's coverage numbers), not merely
                                             -- because it lacked an attached note beyond the bare list line
    source_pages TEXT                       -- JSON list of 0-indexed PDF pages, mirrors entries.source_pages
);
CREATE INDEX idx_derivatives_parent ON derivatives(parent_key);
CREATE INDEX idx_derivatives_key ON derivatives(key);

-- TWOT prints exactly one running head per page, in the outer top margin,
-- naming the HIGHEST TWOT root number that begins on that page (a "last
-- headword" guide-word convention -- confirmed directly against 5
-- consecutive pages, including cases where the named root doesn't start
-- until deep in the page). Independent of body-text matching, so useful
-- specifically as a cross-check when body-text segmentation itself is what's
-- failing (see combine_sources.py's page-header cross-check, added after
-- this signal caught roots 2 and 3 landing on wrong boundaries that neither
-- OCR nor embedded-text body matching alone had flagged).
CREATE TABLE page_headers (
    page INTEGER PRIMARY KEY,          -- 0-indexed PDF page number
    header_root TEXT,                   -- root number read from the header, or NULL if unparsable
    embedded_reading TEXT,               -- raw header text from the PDF's embedded text layer (derivative_structure.py)
    ocr_reading TEXT,                     -- raw header-zone text from an OCR source, for cross-validation --
                                            -- NULL when no OCR candidate was found near this page's start
                                            -- (expected: OCR's column-concatenated text only lets this catch
                                            -- headers printed on the left/even-page side reliably, see
                                            -- combine_sources.py)
    confidence TEXT                        -- 'verified' (embedded+OCR agree) | 'suspect' (disagree) |
                                             -- 'embedded-only' (no OCR candidate to cross-check against)
);
