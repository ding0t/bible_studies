# References

Supporting material for developing studies in this repo — see the [develop-bible-study skill](../.claude/skills/develop-bible-study/SKILL.md) for the process this feeds into.

**Two separate databases, two separate safety postures — don't confuse them:**

- **`references/build/bible-text.db`** — Bible text, morphology, cross-references. Sources are open or restricted-nc. Gitignored build artifact, lives *inside* this repo's directory tree at `references/build/out/`.
- **`references/build/study_notes/` → `study-notes.db`** — commercial study-Bible commentary (ESV Study Bible, Cultural Backgrounds Study Bible, etc.). Every source here is `quotation-only`. Built and stored **entirely outside this repo's directory tree**, on the personal media volume (`/Volumes/media/bible/local-only-build/study-notes.db`) — not just gitignored, actually not present anywhere under `bible_studies/`. This is deliberate: `quotation-only` data gets the stronger isolation, not just a `.gitignore` line. If you're ever tempted to add a new commercial-study-Bible extraction, **use this system, not a new one** — see the section below before writing new extraction code.

A third script, `references/build/commentary_index.py`, is different in kind from the two databases above — it doesn't ingest any external source. It scans this repo's own `docs/content/studies/**/*.md` frontmatter (`primary_passage`, `bible_references`) and maintains an auto-generated cross-reference section inside `docs/content/bible/commentaries/<NN>-<book>/` (a chapter file and a book `index.md` per referenced book/chapter), so a reader looking at a commentary page can see which studies actually treat that passage. It writes directly into committed content — run it after adding or editing a study's reference frontmatter (`uv run python commentary_index.py`). It's idempotent and only ever touches the content between `<!-- commentary-index:auto-start -->` / `...auto-end -->` markers, so hand-written commentary prose around that section is never overwritten. See the develop-bible-study skill's Phase 7 for why every study should populate `primary_passage`/`bible_references` — a study missing both is simply invisible to this index, not an error.

A fourth, `references/build/sefaria.py`, fetches Jewish literature (Mishnah, Talmud, etc.) from [Sefaria](https://www.sefaria.org)'s public [Sefaria-Export](https://github.com/Sefaria/Sefaria-Export) data — used to verify/quote the Mishnah Pesachim citations in the Last Supper study directly against primary text instead of secondary summaries. See [docs/content/resources/jewish-sources.md](../docs/content/resources/jewish-sources.md) for licensing detail (varies by translation — check before quoting) and usage. Fetch-and-cache only, like `ingest_ebible()`; deliberately not a `bible-text.db` table since Mishnah/Talmud addressing doesn't fit that schema's Bible book/chapter/verse columns.

A fifth, `references/build/section_index.py`, fixes a real site bug rather than adding a source: `mkdocs-awesome-pages-plugin` falls through to the first alphabetical leaf page whenever a nav section has no `index.md` (e.g. clicking "Studies" landed on whatever the first archaeology study happened to be). It scans every `docs/content/` directory and generates a card-grid landing page for any directory that's missing one — a category's live studies, or a section's subsections — filtering `draft: true` automatically since the site is public. Same delimited auto-section pattern (`<!-- section-index:auto-start -->`/`...auto-end -->`) as `commentary_index.py`; safe to add hand-written intro prose around the generated grid. Run it after adding a new study or a new top-level content section (`uv run python section_index.py`).

## Quick guide: which source, and is it safe to use freely?

| Need | Source | License tier | Use in a study how |
|---|---|---|---|
| Hebrew/Greek text, morphology, lemma, gloss | `open-data/morphhb`, `open-data/macula-greek`, `open-data/macula-hebrew`, `open-data/sblgnt` | open | Cite freely, quote at length if useful |
| Semantic domains (Louw-Nida / SDBH) | `open-data/macula-greek`, `open-data/macula-hebrew` | open (one field caveat — see [docs/content/resources/github.md](../docs/content/resources/github.md)) | Cite freely |
| English translations (KJV, ASV, WEB, BSB, etc.) | `open-data/scrollmapper-bible-databases`, eBible.org sources (`ebible-eng-web`, `ebible-grcbrent`, `ebible-heb`, `ebible-grc-tisch`) | open | Quote freely, name the translation |
| Cross-references | `open-data/scrollmapper-bible-databases` (OpenBible.info data), `open-data/stepbible-data` | open | Cite freely |
| Byzantine/TR Greek, BHSA syntax trees, Mounce dictionary | `restricted-data/*` | restricted-nc | Fine to use and cite now (site is non-commercial); flag if that ever changes |
| Jewish literature (Mishnah, Talmud) for cultural/historical background | `references/build/sefaria.py` (Sefaria-Export) | varies per translation — check before quoting | Prefer a CC0/CC-BY/public-domain version; cite the specific version quoted |
| Fee & Stuart methodology, Stevens word-study method | Locally-synthesized into the skill files themselves | n/a | Already rewritten in our own words — cite the skill, not the source, for the *method*; don't reproduce the original PDFs' text |
| TWOT word-study entries | `references/build/twot/twot_strongs_map.json` (committed) for id/lemma/gloss; full discussion prose is local-only, uncommitted OCR work | ids/glosses: open-ish (bare facts); prose: quotation-only | Cite the TWOT root number and gloss freely; quote a sentence of discussion with attribution, don't reproduce a whole entry |
| Commercial study-Bible commentary (ESV Study Bible, Cultural Backgrounds Study Bible, NIV Biblical Theology Study Bible, CSB Ancient Faith Study Bible, NA28 Greek NT) | `study-notes.db` (external, see above) | **quotation-only** | Quote a sentence or two with attribution in a study's References section; never reproduce a full note |

Everything except "open" and "restricted-nc" in that table is **not committed to this repo**.

## bible-text.db — text, morphology, cross-references

```bash
cd references/build
uv sync
uv run python build.py
```

Gitignored, fully regenerable (`references/build/out/`, `references/build/cache/`). Ingests every `open-data/` submodule plus eBible.org translations fetched fresh into a cache. See `references/build/schema.sql` for tables (`works`, `verses`, `morphology`, `notes`, `cross_references`, `literary_units`) — every row traces to a `work_id` in `works`, which carries `license_tier`, so check that before citing a row:

```sql
sqlite3 references/build/out/bible-text.db "SELECT work_id, license_tier FROM works;"
```

For convenient lookups instead of hand-writing SQL each time, see `references/build/query.py` (word lookup, concordance, cross-references, notes) — run `uv run python query.py --help`.

Example (raw SQL, if you need something the query script doesn't cover): a Greek word's lemma, Strong's number, and Louw-Nida domain for a specific verse —

```sql
SELECT surface_form, lemma, strongs_id, gloss, domain_code
FROM morphology WHERE work_id='macula-greek-sblgnt' AND book='Mark' AND chapter=5 AND verse=27;
```

**There is currently no `export.py`** in this pipeline (referenced in `build.py`'s own docstring but not yet built) — tier-filtering to keep `restricted-nc` rows out of anything meant to go fully public (vs. "public but non-commercial," which is fine) is a manual discipline right now, not an enforced guarantee. Check `license_tier` yourself before copying a query result into a committed file.

## study-notes.db — commercial study-Bible commentary (external, not in this repo at all)

```bash
cd references/build
uv run python build_study_notes.py
```

Writes to `/Volumes/media/bible/local-only-build/study-notes.db` — never anywhere under `bible_studies/`. See `references/build/study_notes/schema.sql` for tables (`works`, `verses`, `introductions`, `notes`, `topical_articles`, `images`). Sources are registered declaratively in `references/build/study_notes/sources.py` — currently ESV Study Bible, NIV Cultural Backgrounds Study Bible, NKJV Cultural Backgrounds Study Bible, NIV Biblical Theology Study Bible, CSB Ancient Faith Study Bible, and the NA28 Greek NT (from the NA28-ESV parallel). **Adding a 6th source that fits an existing extractor family is a config entry in `sources.py`, not new code** — check `extractors/__init__.py` before writing a new parser.

Query it the same way as `bible-text.db`, just pointed at the external path:

```sql
sqlite3 /Volumes/media/bible/local-only-build/study-notes.db \
  "SELECT text FROM notes WHERE work_id='niv-cultural-backgrounds-study-bible' AND book='Mark' AND chapter=5 AND verse_start<=27 AND verse_end>=27;"
```

`quotation-only` means: fine — expected, even — to quote a sentence or two with attribution in a study's own References section (see the skill's Phase 7). Not fine: bulk-exporting this database's contents, or reproducing a full note/article verbatim into a committed file.

## open-data/ and restricted-data/

Git submodules of forked open-data repos (Bible texts, lexicons, morphology, cross-references) — see [docs/content/resources/github.md](../docs/content/resources/github.md) for the full master list, license findings, and why each one's there. Also see that doc's **eBible.org section** for translations fetched at build time rather than forked (not git-hosted, so the submodule pattern doesn't apply).

- **`open-data/`** — unconditionally open licenses only (CC BY, CC0, public domain). Safe regardless of this repo's visibility or commercial status.
- **`restricted-data/`** — usable now, but under non-commercial-only or similarly restricted terms. Fine to keep public as long as this site stays non-commercial; would need re-review if that ever changes. Never mix these into `open-data/` — the directory boundary *is* the audit boundary.

## study-state/

One structured-data file per study in progress, tracking exegesis/hermeneutics progress so work can resume across sessions. See [study-state.template.yml](../.claude/skills/develop-bible-study/study-state.template.yml) for the schema. Safe to commit — it's metadata (passages, stages, sources consulted), not copyrighted source text. **Always fill in `resources_consulted`** as you go — that's what makes a study's reasoning traceable later, for any source tier.

## Word study & original-language tools

For the Hebrew/Aramaic/Greek word studies AGENTS.md requires (original text + gloss + pronunciation), prefer the forked data in `open-data/` (`hebrew-lexicon`, `strongs`, `morphhb`, `stepbible-data`, `greek-resources`) for agent/offline use — queried via `bible-text.db` above. For quick manual lookups:

- **[Blue Letter Bible](https://www.blueletterbible.org/)** — interlinear + Strong's-tagged lookup, Hebrew and Greek, free.
- **[STEP Bible](https://www.stepbible.org/)** (Tyndale House) — interlinear, lexicons, and original-language search, free.
- **[Bible Hub interlinear](https://biblehub.com/interlinear/)** — quick interlinear + Strong's cross-links.
- **Louw & Nida, *Greek-English Lexicon of the New Testament Based on Semantic Domains*** (Greek) and **SDBH, *Semantic Dictionary of Biblical Hebrew*** (Hebrew) — group words by usage relationship rather than lexical root; the cross-check step in the fuller word-study method (see the [develop-bible-study word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md)) leans on these. Available as local data via `open-data/macula-greek` (`@ln`/`@domain`) and `open-data/macula-hebrew` (`@sdbh`/`@lexdomain`) — see [docs/content/resources/github.md](../docs/content/resources/github.md) for the license caveat on the Greek domain field specifically.
- **TWOT** (*Theological Wordbook of the Old Testament*, Archer, Harris & Waltke, Moody Publishers) — the standard companion to Strong's/BDB for Hebrew root theology. `references/build/twot/twot_strongs_map.json` **is committed** and gives a `TWOT root → {strongs_id, bdb_id, lemma, xlit, gloss}` reverse-lookup usable right now. The fuller OCR/segmentation extraction of TWOT's actual discussion prose (`references/build/twot/`) is **not committed** and must not be — TWOT has no open license, unlike the bare Strong's numbers/glosses in the map above (same distinction as the caveat already on the `strongs` fork in [docs/content/resources/github.md](../docs/content/resources/github.md)).

For Hebrew *language learning* (as opposed to word-study lookup), see the existing [hebrew-studies/resources.md](../docs/content/hebrew-studies/resources.md).

## Cross-reference tools

- **Treasury of Scripture Knowledge (TSK)** — public domain (1836), the standard cross-reference set; available on Bible Hub and Blue Letter Bible per-verse.
- **Bible Gateway / Bible Hub parallel view** — quick multi-translation comparison, needed for the translation-comparison step in Phase 6 of the skill.

## Secondary/commentary sources (local-only, not committed)

These are commercially-sold or otherwise copyrighted works. The **source files themselves** aren't committed to this repo — this is a public repo, and committing an entire copyrighted work would be redistribution, not personal use. Most are queryable through `study-notes.db` above rather than by hand.

That doesn't mean these sources can't be *cited*. **They should be** — citing a restricted or copyrighted source by name, with attribution and a reasonably short quotation, is a normal and expected thing to do in a public study, not something to avoid. What copyright actually constrains: quoting *too much* of one source (a full paragraph or note, not a sentence or two) into a committed file, or citing without attribution. Every study should end with a **References & Recommended Reading** section (see the skill's Phase 7) naming every source actually drawn on — restricted/copyrighted ones by name included — so a reader can go find the fuller discussion themselves.

- *How to Read the Bible for All Its Worth* (Fee & Stuart, 4th ed.) — the methodology behind the develop-bible-study skill. Source PDF + a full local markdown extraction live next to each other on the media volume, for personal reference only. The site's own public write-up of these principles, for readers rather than for the skill tooling, is [docs/content/bible/how-to-read-the-bible.md](../docs/content/bible/how-to-read-the-bible.md) — currently a draft stub, not yet fleshed out.
- Gerald L. Stevens, "Word Study Guide — New Testament" (seminary course handout) — the methodology behind [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md). Source PDF at `/Volumes/media/bible/resources/NTWordStudyGuide.pdf`; the skill file is an original synthesis of the method, not a reproduction.
- *ESV Study Bible* (Crossway, 2016), *NIV Cultural Backgrounds Study Bible* and *NKJV Cultural Backgrounds Study Bible* (Zondervan, ed. John H. Walton & Craig S. Keener), *NIV Biblical Theology Study Bible* (Zondervan), *CSB Ancient Faith Study Bible* (Holman) — all queryable via `study-notes.db` above.
- Any other commentary consulted for a study should be recorded per-study in that study's `resources_consulted` field *and* named in the study's own References section — not duplicated here.
