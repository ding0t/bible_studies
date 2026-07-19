# References

Supporting material for developing studies in this repo — see the [develop-bible-study skill](../.claude/skills/develop-bible-study/SKILL.md) for the process this feeds into.

## Quick guide: which source, and is it safe to use freely?

| Need | Source | License tier | Use in a study how |
|---|---|---|---|
| Hebrew/Greek text, morphology, lemma, gloss | `open-data/morphhb`, `open-data/macula-greek`, `open-data/macula-hebrew`, `open-data/sblgnt` | open | Cite freely, quote at length if useful |
| Semantic domains (Louw-Nida / SDBH) | `open-data/macula-greek`, `open-data/macula-hebrew` | open (one field caveat — see [docs/content/resources/github.md](../docs/content/resources/github.md)) | Cite freely |
| English translations (KJV, ASV, WEB, BSB, etc.) | `open-data/scrollmapper-bible-databases`, eBible.org sources (`ebible-eng-web`, `ebible-grcbrent`, `ebible-heb`, `ebible-grc-tisch`) | open | Quote freely, name the translation |
| Cross-references | `open-data/scrollmapper-bible-databases` (OpenBible.info data), `open-data/stepbible-data` | open | Cite freely |
| Byzantine/TR Greek, BHSA syntax trees, Mounce dictionary | `restricted-data/*` | restricted-nc | Fine to use and cite now (site is non-commercial); flag if that ever changes |
| Fee & Stuart methodology, Stevens word-study method | Locally-synthesized into the skill files themselves | n/a | Already rewritten in our own words — cite the skill, not the source, for the *method*; don't reproduce the original PDFs' text |
| Cultural/historical background notes | Cultural Backgrounds Study Bible (`bible-text.db`'s `notes` table, `quotation-only`) | **quotation-only** | Quote a sentence with attribution; never reproduce a full note |

Everything below "open" and "restricted-nc" in that table is **not committed to this repo** — see the tier-by-tier notes further down.

## bible-text.db — the actual query interface

Most of the sources below are easiest to use through `references/build/bible-text.db`, not by grepping raw submodule files directly. Build it with:

```bash
cd references/build
uv sync
uv run python build.py
```

This is a **gitignored, fully regenerable build artifact** (`references/build/out/`, `references/build/cache/`) — never committed, rebuild it any time. `build.py` ingests every source below that has a `ingest_*` function: Bible text and morphology from the `open-data/` submodules, eBible.org translations fetched fresh into a cache, and (if the media volume is mounted) the Cultural Backgrounds Study Bible's notes. See `references/build/schema.sql` for the table definitions (`works`, `verses`, `morphology`, `notes`, `cross_references`, `literary_units`) — every row traces back to a `work_id` in `works`, which carries the license tier, so you can always check what you're allowed to do with a given row before citing it:

```sql
sqlite3 references/build/out/bible-text.db "SELECT work_id, license_tier FROM works;"
```

Example: look up a Greek word's lemma, Strong's number, and Louw-Nida domain for a specific verse —

```sql
SELECT surface_form, lemma, strongs_id, gloss, domain_code
FROM morphology WHERE work_id='macula-greek-sblgnt' AND book='Mark' AND chapter=5 AND verse=27;
```

Or pull a Cultural Backgrounds note for the same verse (only if you've built with that source available — see below):

```sql
SELECT text FROM notes WHERE work_id='cultural-backgrounds-niv' AND book='Mark' AND chapter=5 AND verse=27;
```

**There is currently no `export.py`** in this pipeline (referenced in `build.py`'s own docstring but not yet built) — tier-filtering to keep `quotation-only` and `restricted-nc` rows out of anything public is a manual discipline right now, not an enforced guarantee. Check `license_tier` yourself before copying a query result into a committed file.

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

For Hebrew *language learning* (as opposed to word-study lookup), see the existing [hebrew-studies/resources.md](../docs/content/hebrew-studies/resources.md).

## Cross-reference tools

- **Treasury of Scripture Knowledge (TSK)** — public domain (1836), the standard cross-reference set; available on Bible Hub and Blue Letter Bible per-verse.
- **Bible Gateway / Bible Hub parallel view** — quick multi-translation comparison, needed for the translation-comparison step in Phase 6 of the skill.

## Secondary/commentary sources (local-only, not committed)

These are commercially-sold or otherwise copyrighted works. None are committed to this repo — this is a public repo, and committing them would be redistribution, not personal use. Each one's source file lives only on the personal media volume that owns it. **The rule for using any of them in a study**: cite briefly with attribution (a sentence, a short quote), synthesize the substance in your own words, never reproduce a full paragraph or note verbatim into a file that gets committed here (see the copyright guardrail in the skill).

- *How to Read the Bible for All Its Worth* (Fee & Stuart, 4th ed.) — the methodology behind the develop-bible-study skill. Source PDF + a full local markdown extraction live next to each other on the media volume, for personal reference only.
- Gerald L. Stevens, "Word Study Guide — New Testament" (seminary course handout) — the methodology behind [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md). Source PDF at `/Volumes/media/bible/resources/NTWordStudyGuide.pdf`; the skill file is an original synthesis of the method, not a reproduction.
- *NIV Cultural Backgrounds Study Bible* and *NKJV Cultural Backgrounds Study Bible* (Zondervan, ed. John H. Walton & Craig S. Keener) — verse-by-verse historical/cultural notes. Source epubs at `/Volumes/media/bible/bibles/`, unzipped at `/Volumes/media/bible/local-only-build/unzipped/{niv,nkjv}-cultural-backgrounds-study-bible/`. **Has a proper extraction now** — `references/build/build.py`'s `ingest_cultural_backgrounds()` parses every note in the epub (keyed by verse-anchor IDs like `com41005025` for Mark 5:25) into `bible-text.db`'s `notes` table, `work_id='cultural-backgrounds-niv'`, `license_tier='quotation-only'`. Query it like any other note (see `bible-text.db` section above) rather than re-deriving the epub's anchor structure by hand. The NKJV edition isn't ingested by default (likely near-duplicate commentary paired with a different translation) — call `ingest_cultural_backgrounds(conn, edition='nkjv')` if it's ever actually needed.
- Any other commentary consulted for a study should be recorded per-study in that study's `resources_consulted` field, not duplicated here.
