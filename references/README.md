# References

Supporting material for developing studies in this repo — see the [develop-bible-study skill](../.claude/skills/develop-bible-study/SKILL.md) for the process this feeds into.

**Two separate databases, two separate safety postures — don't confuse them:**

- **`references/build/bible-text.db`** — Bible text, morphology, cross-references. Sources are open or restricted-nc. Gitignored build artifact, lives *inside* this repo's directory tree at `references/build/out/`.
- **`references/build/study_notes/` → `study-notes.db`** — commercial study-Bible commentary (ESV Study Bible, Cultural Backgrounds Study Bible, etc.). Every source here is `quotation-only`. Built and stored **entirely outside this repo's directory tree**, on the external reference volume (`$BIBLE_MEDIA_ROOT/local-only-build/study-notes.db`, see **External material and `BIBLE_MEDIA_ROOT`** below) — not just gitignored, actually not present anywhere under `bible_studies/`. This is deliberate: `quotation-only` data gets the stronger isolation, not just a `.gitignore` line. If you're ever tempted to add a new commercial-study-Bible extraction, **use this system, not a new one** — see the section below before writing new extraction code.

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
| Dead Sea Scrolls (biblical) | `restricted-data/dss` | restricted-nc | Cite with attribution; never reproduce wholesale |
| Clause syntax, coreference, Hebrew construct state / verb conjugation | `bible-text.db` `morphology` table (MACULA columns) — `query.py syntax` / `bible_syntax` | open | Cite freely; see the syntax section below for what the annotation does and doesn't cover |
| Hebrew paragraph/pericope divisions (samekh/pe markers) for concordance chunking | `open-data/hebrew-vocab-tools` — ingested as work `hebrew-vocab-tools-pericopes` | open (CC BY 4.0) | Cite freely with attribution; used by [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md) for Hebrew concordance grouping |
| Byzantine/TR Greek, BHSA syntax trees, Mounce dictionary | `restricted-data/*` | restricted-nc | Fine to use and cite now (site is non-commercial); flag if that ever changes. **BHSA is not ingested** — see the syntax section below for why MACULA is the better first stop |
| Jewish literature (Mishnah, Talmud) for cultural/historical background | `references/build/sefaria.py` (Sefaria-Export) | varies per translation — check before quoting | Prefer a CC0/CC-BY/public-domain version; cite the specific version quoted |
| Deuterocanonical / extra-biblical books (Tobit, 1-2 Maccabees, Sirach, 1 Enoch, Jubilees…) | `open-data/scrollmapper-bible-databases-deuterocanonical` — **raw files only**, `sources/<lang>/<book>/<book>.{json,md}`. `build.py` deliberately skips these books, so they are **not** in `bible-text.db` and not reachable from `query.py` or the MCP tools | text: public domain by age (the English is the KJV Apocrypha rendering); the dataset itself carries no license file | Quote the text with attribution, naming it as the KJV Apocrypha. Cite as an **extra-biblical historical witness**, never as Scripture — and note the upstream README's framing of these books as "perfectly valid scripture" is not this site's position |
| Early church fathers — post-apostolic tradition, what became of the apostles | `$BIBLE_MEDIA_ROOT/reference/patristics/` (external, see below) | mixed: NPNF **open**, Apostolic Fathers Greek **unknown/restricted** | Quote NPNF freely with attribution; quote the Greek corpus briefly, never redistribute |
| Fee & Stuart methodology, Stevens word-study method | Locally-synthesized into the skill files themselves | n/a | Already rewritten in our own words — cite the skill, not the source, for the *method*; don't reproduce the original PDFs' text |
| TWOT word-study entries | `references/build/twot/twot_strongs_map.json` (committed) for id/lemma/gloss; full discussion prose is local-only, uncommitted OCR work | ids/glosses: open-ish (bare facts); prose: quotation-only | Cite the TWOT root number and gloss freely; quote a sentence of discussion with attribution, don't reproduce a whole entry |
| Commercial study Bibles and translations (ESV Study Bible, both Cultural Backgrounds Study Bibles, NIV Biblical Theology, CSB Ancient Faith, NLT Life Application, NLT Christian Basics, NASB 1995/2020, **LSB 2021**, NA28 Greek NT) | `study-notes.db` (external, see above) | **quotation-only** | Quote a sentence or two with attribution in a study's References section; never reproduce a full note. Per-work caps differ and are recorded in the db's `works.license` column — **read that column, don't recall the number**. The LSB's is the strictest: 1,000 verses / 50% of the quoting work, no complete book |

Everything except "open" and "restricted-nc" in that table is **not committed to this repo**.

### Keeping this table honest: `check_sources.py`

This table is what the develop- and review-bible-study skills consult before concluding a source is
unavailable, so when it falls behind what is actually on disk it produces confident wrong answers.
That has happened twice: `scrollmapper-bible-databases-deuterocanonical` was added as a submodule
and never documented, so a study asserted Tobit was unavailable while Tobit sat in
`references/open-data/`; and `hebrew-vocab-tools` was ingested into `bible-text.db` and cited by the
word-study skill while appearing nowhere here.

```bash
python3 references/check_sources.py          # from the repo root
python3 references/check_sources.py --quiet  # only problems
```

It reports two things. **Undocumented** (exit 1) is a directory under `open-data/` or
`restricted-data/` that this file never mentions — add a row. **raw-only** is a source that *is*
documented but that `build.py` does not ingest, so `query.py` and the MCP tools cannot see it and it
must be read as raw files; that list is currently `greek-resources`, `hebrew-lexicon`,
`scrollmapper-bible-databases-deuterocanonical`, `stepbible-data`, `strongs`, `bhsa` and
`mounce-dictionary`. Which ingests exist is read out of `build.py` itself, so adding one updates the
check for free.

### External material and `BIBLE_MEDIA_ROOT`

**This repository is public.** Committed files should say what a source is and how much of it may be
quoted; they should not publish the layout of anyone's disks. The commercial study-Bible EPUBs, the
TWOT scans, the patristics corpus and the databases built from them live on an external volume whose
location is a property of one machine, so every script resolves it through an environment variable
rather than a hardcoded path:

```bash
export BIBLE_MEDIA_ROOT=/Volumes/media/bible   # the default if unset; .env is gitignored
```

`references/build/media_root.py` is the single place that resolves it, and supplies
`local_only_build()`, `reference_dir()`, `bibles_dir()`, `resources_dir()`, `study_notes_db()` and
`lexicon_restricted_db()`. Anything that will fail without the volume should call
`require_media_root()` or `require_study_notes_db()` — the drive being unmounted is routine, and
several study-state files record whole research sessions spent unaware it was silently absent.

Paths in this file are written as `$BIBLE_MEDIA_ROOT/...` for that reason. Historical records —
`references/study-state/*.yml` and `references/build/twot/PLAN_derivative_structure.md` — keep the
absolute paths they were written with, because they are an audit trail of what happened, not
configuration.

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

### `(book, chapter, verse)` is not an identity — two ways it fails

The schema treated the reference tuple as if it were a key. It is not, and the two failures are independent:

1. **Not unique within a work.** Nothing enforced one row per reference, and it wasn't true: upstream scrollmapper ships each verse many times over (ASV: 217,714 rows for 31,102 references) with the copies differing in whitespace, so 28,674 references carried two or three rows across 38 works — and `lookup_verse`'s `fetchone()` returned whichever SQLite reached first. Fixed at ingest (normalize whitespace; where copies still differ keep the one with the most words, since the disagreements are lost word separators) and now enforced by `idx_verses_unique`. It also un-inflated KJV Psalm 119 from 198 verses to 176.
2. **Not an identity across works.** Uniqueness within a work says nothing about whether the same tuple means the same verse in another one. It often doesn't — see below.

### Two works that look like Semitic originals and are not

- **`ebible-hebsg`** is the Salkinson-Ginsburg Hebrew New Testament (1885/86) — two Hebraists, Isaac Salkinson and Christian David Ginsburg, and the edition most often meant when "two Hebrew scholars" comes up. It is nonetheless a **translation from the Greek**, distinguished from Delitzsch by confining itself to vocabulary attested in the Tanakh. Held here precisely so the two can be read against each other; neither attests a Hebrew original.
- **`ebible-heb`** is titled "Delitzsch Hebrew Bible (OT+NT)" and carries a full Hebrew New Testament — 1,071 verses in Matthew alone. That is Franz Delitzsch's **19th-century translation of the Greek into Hebrew**, not an ancient witness. It is not evidence of a Hebrew original and must never be cited as such.
- **The Syriac Peshitta** sits on disk at `open-data/scrollmapper-bible-databases/sources/syr/Peshitta/` (public domain, **not ingested**). It is New Testament only — every OT row is empty — and it is a **translation from Greek**, its standard form dating to the early 5th century. Its proper use is versional evidence in textual criticism: a Peshitta reading attests what Greek text its translator had. "Peshitta primacy", the claim that the Aramaic precedes the Greek, is a fringe position and a Hebrew Roots staple; see [the site's own position](../docs/content/israel-and-church/hebrew-roots.md) before leaning on it.

**Provenance note on `ebible-hebsg`, recorded 2026-09-03.** Ken Johnson (Bible Facts) argues that the *original* Salkinson-Ginsburg carries readings in 1-2 Thessalonians that later editions removed to conform it to the Received Text, and that those readings are attested in earlier Hebrew manuscripts. Whether our copy — eBible's edition, USFM dated 2025-05-07 — is unedited in that sense is unresolved. Pinning what it actually reads now, so a specific claim can be checked in one line later rather than re-derived:

- **2 Thessalonians 2:6** — <span dir="rtl">וְכֵן יְדַעְתֶּם אֶת־אֲשֶׁר יַעַצְרֶנּוּ עַתָּה לְמַעַן יִגָּלֶה בְּעִתּוֹ׃</span>
- **2 Thessalonians 2:7** — <span dir="rtl">כִּי סוֹד הַפֶּשַׁע כְּבָר הֵחֵל לְהוֹצִיא פְעֻלָּתוֹ אֶפֶס הָעֹצֵר יַעַצְרֶנּוּ עַד אֲשֶׁר יוּסַר מִתּוֹךְ הַמְּסִילָּה׃</span>

Two features of verse 7 are worth having on record. Salkinson names an explicit personal restrainer, <span dir="rtl">הָעֹצֵר יַעַצְרֶנּוּ</span> ("the restrainer will restrain him"), where Delitzsch is vague. And he closes <span dir="rtl">מִתּוֹךְ הַמְּסִילָּה</span>, "out of the midst of the highway" — <span dir="rtl">הַמְּסִילָּה</span> has no counterpart in the Greek, which reads only ἐκ μέσου, "out of the midst". That is a genuine plus against the Greek; whether it reflects an earlier Hebrew reading or a translator supplying an idiom (a bare <span dir="rtl">מִתּוֹךְ</span> reads awkwardly in Hebrew) is exactly the open question, and 2 Thessalonians 2:7 carries weight in [the rapture study](../docs/content/last-things/rapture.md), so settle it before citing it.

The genuinely ancient Aramaic in this repo is **biblical Aramaic in the Old Testament** — Daniel 2:4b–7:28 and Ezra 4:8–6:18, 7:12–26 — carried by the WLC with full MACULA morphology (Daniel 2 alone has 1,321 tagged words). That is primary-source Aramaic, and it is queryable now.

### Scripture links — the first table this repo derives rather than ingests

`scripture_links` holds three classes of derived link, computed at build time by `quotations.py`. Nothing upstream supplies them, so nothing upstream will fail if they degrade — `tests/test_quotations.py` is the only thing standing between a silent regression and a wrong citation.

| class | sides | pairs (alignment ≥18) | what a match means |
|---|---|---|---|
| `quotation-greek` | `sblgnt` → `ebible-grcbrent` | 140 | **Textual fact.** Author and translator wrote the same language, so the quotation is literally the same words |
| `inner-biblical` | `morphhb-wlc` ↔ itself | 822 | **Textual fact.** The Hebrew Old Testament quoting itself — Kings//Chronicles, Kings//Isaiah, the Decalogue. No translation in between |
| `quotation-hebrew` | `ebible-heb` → `morphhb-wlc` | 49 | **Candidates only.** Delitzsch is a 19th-century translation, so a match says a Hebraist judged this a quotation. Verify in Greek |
| `allusion-lemma` | `macula-greek-sblgnt` → `lxx-lemmas` | 103 | **Shared rare vocabulary**, no shared phrasing required. Scored on `idf_overlap`, not alignment |

**They are never merged into one score.** A quotation in Greek and a Victorian translator's judgement are not the same kind of evidence, and the schema keeps them apart so a caller has to choose.

The Hebrew class earns its place by being *complementary*: it recovers 81% of the Greek-found quotations on its own, and finds 19 the Greek run misses — including **Matthew 21:5 quoting Zechariah 9:9**, where Matthew follows the Hebrew more closely than the Septuagint and the Greek match goes weak.

`inner-biblical` rediscovers the canonical parallels without being told they exist: 2 Kings 19 ↔ Isaiah 37 (23 verses), Deuteronomy 5 ↔ Exodus 20, 2 Samuel 22 ↔ Psalm 18, Psalm 14 ↔ Psalm 53. The most-linked book pairs are Kings/Chronicles and Kings/Isaiah — exactly the known synoptic relationships.

**One trap, recorded because it produced a confidently wrong answer.** The WLC marks morpheme boundaries with `/` and the Hebrew New Testaments mark nothing, so splitting on the separator compares `["ו","יהי"]` against `["ויהי"]` — which can never match. Splitting scored **12%** recall; joining scores **81%**. `normalise_hebrew` joins.

**Method.** An n-gram inverted index for recall, then four graded measures on what survives. Not a whole-string edit distance: quotation is a *local* phenomenon, so overall similarity is swamped by the material two verses don't share, and 7,939 × 22,948 alignments is not a computation anyone runs.

| measure | what it says |
|---|---|
| `alignment` | **the primary measure.** Smith-Waterman local alignment, which tolerates the insertions and omissions that adapted quotation always carries |
| `longest_run` | longest contiguous shared token run. Kept because it is checkable — a reader can go and count nine verbatim words — but it breaks at the first edit |
| `containment` | share of the quoting verse's 4-grams that are shared |
| `idf_overlap` | shared n-grams weighted by rarity, so a shared "and it came to pass" stops counting like a shared rare phrase |
| `corroborated` | a cross-reference list independently names the same passage — openbible's, or the WEB's own translator footnotes |

**Both thresholds are measured, not asserted.** Auditing every pair against the two lists (unrelated provenance, English scheme) locates the cliff, and alignment separates far more sharply than a contiguous run:

| alignment | corroborated | | verbatim run | corroborated |
|---|---|---|---|---|
| 20–29 | **86%** | | 12+ | 85% |
| 15–19 | 55% | | 8–11 | 79% |
| 10–14 | 14% | | 4–5 | 11% |

So the threshold is **alignment ≥ 18**: 140 pairs at 84%, against the old run ≥ 8's 138 at 80%. Similar volume, better precision — and it recovers quotations a contiguous run missed **outright**, every one of them independently corroborated:

| | run | alignment |
|---|---|---|
| **Matthew 1:23 → Isaiah 7:14** (*"the virgin shall conceive"*) | 5 | 24 |
| **Luke 4:18 → Isaiah 61:1** (Luke omits a clause) | 6 | 25 |
| **Acts 13:41 → Habakkuk 1:5** | 7 | 33 |

That is the case for local alignment in one table: adapted quotation is the normal case, and a run of contiguous words breaks at the first edit. **A strong alignment that no list carries is a quotation the cross-reference tradition missed, not a weak result** — the point of deriving this at all, and a test asserts those keep existing.

**Two witnesses, and only two.** `corroborated` checks both `openbible-crossrefs` (830,866 rows, crowd-voted, CC-BY) and `web-crossrefs` (424 rows, the WEB translators' own footnotes, public domain, parsed from the raw USFM because BibleOrgSys drops notes at ingest). The second is tiny but independent, and sits almost entirely on New Testament quotations of the Old — exactly where these links are scored. **Scrollmapper's `cross_references.txt` is not a third witness:** its header reads `#www.openbible.info CC-BY`, so it and `openbible-crossrefs` are one source counted twice. Checking a link against a list that shares provenance with the list already checked corroborates nothing.

Matthew 11:10 is the case that shows why a second witness is worth having: both lists carry the Malachi 3:1 half of its conflated quotation, neither carries the Exodus 23:20 half, and the derived link finds it on nine verbatim Greek words. `tests/test_crossrefs.py` asserts that stays true.

Every candidate above two shared 4-grams is stored; there is deliberately **no per-verse cap**. Capping at the best few discarded 27% of qualifying pairs and, because ties broke on set iteration order, returned a different set on each run.

**`query.py trace` — one verse, every connection, with the evidence shown.** The composite entry point, and the reason the classes were kept apart rather than merged. For a reference it returns each connection with *how* it was established, how strongly, the linked verse in its **original language**, an English rendering, and the words the two verses actually share.

```
$ uv run python query.py trace Heb 10 5

Heb 10:5
    διὸ εἰσερχόμενος εἰς τὸν κόσμον λέγει· Θυσίαν καὶ προσφορὰν οὐκ ἠθέλησας, σῶμα δὲ κατηρτίσω μοι·
    ... but you prepared a body for me.

  ── QUOTATION  (Greek on both sides -- a textual fact)

    quotes Ps 39:7 = Ps 40:6   strength 18  [corroborated]
        shared: Θυσίαν καὶ προσφορὰν οὐκ ἠθέλησας, σῶμα δὲ κατηρτίσω μοι·
        Sacrifice and offering you didn't desire. You have opened my ears.
```

The whole thesis is visible in one output: the Greek New Testament and the Greek Old Testament share those words exactly, while the English Old Testament reads *"you have opened my ears"* — because it translates the Hebrew.

The `shared` span is the part no cross-reference list carries. A list asserts a connection; this shows the words the claim rests on, sliced from the original text rather than the normalised form, so it can be quoted.

Two further behaviours worth knowing:

- **Conflations surface whole.** `trace Matt 21:5` returns the Isaiah 62:11 quotation *and* the Zechariah 9:9 echo, because grouping by method shows every half rather than picking one best match. Matthew is drawing on two passages and the output says so.
- **Scroll readings attach to the quoted verse.** Where a link lands on an Old Testament verse the Dead Sea Scrolls attest, any reading the Masoretic lacks is shown with it — so a study sees whether the verse a New Testament writer quoted is textually disputed without having to think to ask.

Crowd-assembled cross-references are returned under `leads`, never mixed into `connections`. Merging consensus with a textual fact is precisely what the design refuses to do.

**Rare-lemma allusion, and the source that unblocked it.** The Septuagint's *text* was here from the start but not its lemmas, which blocked every lemma-level question about the Old Testament in the language the New Testament authors read it in. CCAT's morphological database is restrictively licensed — which is why our own `greek-resources` fork ships without it — but the Open Scriptures Septuagint Project's **lemma files are a separate work, CC BY 4.0**, carrying only a key and a lemma and none of CCAT's text. They had been sitting in `open-data/greek-resources/LxxLemmas/` unused: 59 books, **616,548 lemmatised words**, the deuterocanon included.

That makes the cross-language bridge unnecessary rather than merely difficult. The Septuagint and the Greek New Testament **share a lemma inventory covering 96% of New Testament tokens**, so a lemma is a lemma and both sides are simply Greek. Where two passages share several lemmas that are rare across the whole corpus, that is evidence even with no shared phrasing:

| | |
|---|---|
| Random New Testament / Septuagint verse pairs corroborated by a cross-reference | **0.3%** |
| Pairs above the rarity threshold | **52%** |

A 173× enrichment. It reaches what quotation matching structurally cannot — Revelation 21:20's jewels against Ezekiel 28:13, which share no phrasing at all — and because the lemma files cover the deuterocanon it surfaces links no cross-reference list carries: **Paul at the Areopagus against Wisdom 13:10**, **Hebrews 11:5 against Sirach 44:16**. That bears directly on backlog item 1.1 on extra-biblical texts.

Two things to know before using it. The word ORDER in the lemma files is CCAT/Rahlfs's, not Brenton's — they agree on word count in 73% of verses and on position in 47% — so `word_position` indexes that source's own sequence and **must not be joined positionally to `ebible-grcbrent`**. And both sides must normalise through the same function: the lemma files keep final sigma where `normalise_greek` converts it, and joining them raw made νόμος and ἔλεος appear absent from the Septuagint, which is impossible on its face and is how the bug announced itself.

**Why this is done in Greek, and cannot be done in English.** The obvious shortcut is to match an English New Testament against its own English Old Testament and skip the alignment work entirely. It was measured against the Greek-derived results as ground truth, and it does not hold up:

| translation | recall of Greek-found quotations | pairs emitted |
|---|---|---|
| KJV | 57% | 4,822 |
| WEB | 53% | 1,534 |
| ASV | 52% | 3,948 |
| Darby | 49% | 3,833 |
| LEB / Rotherham | 45% | 1,592 / 3,887 |
| **YLT** | **29%** | 1,739 |

Half the quotations lost, and ten to thirty times the noise against 138 strong Greek pairs. Note that **the most wooden translation does worst** — literalness is not the variable.

The reason is structural rather than a matter of translation philosophy. An English New Testament renders Greek; an English Old Testament renders Hebrew. The two halves are translated as separate books from different source languages, so a quotation and its source only overlap verbatim where the translators happened to converge — usually on famous passages. The failures are not where you would guess:

| | Greek run | English run |
|---|---|---|
| Hebrews 8:9 → Jeremiah 31:32 | 23 | 22 |
| Romans 10:18 → Psalm 19:4 | 17 | 7 |
| Acts 8:33 → Isaiah 53:8 | 20 | 3 |
| **Galatians 4:27 → Isaiah 54:1** | **23** | **0** |

Galatians 4:27 quotes Isaiah 54:1 across 23 verbatim Greek tokens and shares *nothing* with the WEB's Isaiah. In Greek the New Testament author and the Septuagint translator were writing the same language and the quotation is literally the same words; in English you are comparing two independent translations of two different source texts.

So links are derived in Greek and *displayed* in English — which is what `to_english_chapter` / `to_english_verse` are for.

```bash
uv run python query.py quotations Heb 10 5              # -> LXX Ps 39:7 = Ps 40:6, run 9
uv run python query.py quotations Ps 95 8               # the reverse: who quotes this passage
uv run python query.py quotations Isa 37 4              # -> 2 Kings 19:4, inner-biblical, run 22
uv run python query.py quotations Zech 9 9 --type quotation-hebrew
uv run python study_gaps.py docs/content/jesus/the-way.md
```

`study_gaps.py` is the payoff: it reads a study's own `primary_passage`/`bible_references`, gathers quotation links and cross-references against those passages, subtracts every chapter the study already cites, and ranks what is left with quotations first. The two kinds are never merged into one score — a quotation at a strong run is a textual fact, a cross-reference is a lead. A study with neither frontmatter field is invisible to it and says so.

### A negative result: the Septuagint as a cross-language bridge

Worth recording so it isn't re-derived. The standard technique for detecting *translated* reuse is to bridge the languages with a lexicon learned from a parallel corpus — and this repo has one hiding in plain sight, since the Hebrew Old Testament and the Greek Septuagint are the same text already verse-aligned by reference.

Learning it works. From 22,761 aligned verses, verse-level co-occurrence scored by Dice yields correct equivalences with no external dictionary — <span dir="rtl">חסד</span> → ἔλεος, <span dir="rtl">תורה</span> → νόμος, <span dir="rtl">ברית</span> → διαθήκη, <span dir="rtl">רוח</span> → πνεῦμα. 2,107 Hebrew lemmas covered.

**Using it to find Hebrew-OT/Greek-NT allusions does not work.** Scored against the 140 known quotations as ground truth:

| | median bridge overlap |
|---|---|
| known quotation pairs | 0.168 |
| random verse pairs | 0.067 |

A 2.5× ratio on medians, but the distributions overlap so heavily that only **9% of known quotations** clear the 99th percentile of random pairs. A method that cannot separate a quotation it already knows about from noise will not find allusions.

**Using it for translation-choice analysis is promising but not ready.** It does surface real collapses — where the Septuagint renders several Hebrew words with one Greek one:

| Greek | Hebrew collapsed into it |
|---|---|
| φόβος | <span dir="rtl">אימה יראה פחד</span> — three distinct fear-words |
| μόσχον | <span dir="rtl">עגל פר שור</span> — calf, bull, ox |
| αἷμα | <span dir="rtl">דם זרק שפך</span> — the sacrificial blood vocabulary |

But the same output contains obvious artifacts (καί "collapsing" six Hebrew function words; Δανιηλ pulling in Aramaic particles), because Dice on verse-level co-occurrence conflates *translation equivalence* with *appearing in the same verse*. Separating those needs real statistical word alignment rather than co-occurrence, and much of the curated version of this question is already answered better by Louw-Nida and SDBH.

**What would change the calculus:** a lemmatised Septuagint. Lemma-to-lemma alignment is far cleaner than lemma-to-inflected-surface, and it is the same missing source that blocks cross-testament rare-lemma allusion. Both stalled classes have one unlock.

### `biblefacts/` — third-party teaching, unvetted

Transcripts and notes captured from Ken Johnson (Bible Facts). **Not** part of either SQLite pipeline and **not** covered by the license tiers above. AGENTS.md is the rule: a lead to chase down in a primary source, never a citable reference in a study.

[textual-heritage-kenjohnson.md](biblefacts/textual-heritage-kenjohnson.md) is the exception in form — a worked summary rather than a raw dump, covering his Old and New Testament transmission lines with both diagrams redrawn, a claim-by-claim assessment, and the leads that have since been chased to a source. Read it before taking any transmission-history claim from that channel into a study: several of its claims check out against this repo's own data, several do not, and the file says which is which.

### Dead Sea Scrolls — `restricted-data/dss`

ETCBC's Text-Fabric edition of **Martin Abegg's** transcriptions (with James E. Bowley and Edward M. Cook), converted by Jarod Jacobs, Martijn Naaijer and Dirk Roorda. **CC BY-NC 4.0** — stated in the data's own feature metadata, not merely the repo README — so it sits in `restricted-data/` and every row lands in the `restricted-nc` tier. Cite it; don't reproduce it at length.

- **262 scrolls, 11,910 verses, 212,374 tagged words**, across **36 of the 39** Old Testament books. Absent: **Esther** (famously unattested at Qumran), Nehemiah and 1 Chronicles.
- **One work per scroll** (`dss-1Qisaa`, `dss-4Q37`, …), because a scroll *is* a witness and they disagree. Isaiah 53:5 survives in both 1Qisaa and 1Q8 and they do not read alike — 1Qisaa has the fuller orthography. Query all witnesses to a verse with `work_id LIKE 'dss-%'`.
- **References follow the Masoretic division**, since that is what Abegg's editors aligned to. So Psalm 22:17 here is English Psalm 22:16 — use `query.py parallel` rather than assuming.
- Where the editors could not assign a canonical book they put a scroll designation in the book field. Those are unidentified fragments and are **not** ingested.

**Read the brackets before resting an argument on a reading.** `verses.text` keeps the `full` transcription including editorial marks — `[ ]` reconstruction, `#` and `?` damaged or uncertain letters. The bracket notation marks 31.8% of biblical words, but the per-sign annotation underneath tells a far starker story: **46% of signs in this corpus are a modern editor's reconstruction, and only 33% of biblical words are free of any reconstructed or uncertain letter.** `morphology.extant` carries that per word — two-thirds of the biblical Dead Sea Scrolls is, letter by letter, editorial. A scroll reading that differs from the Masoretic while sitting inside brackets is an editor's reconstruction, not manuscript evidence, and a corpus that hid that distinction would be actively misleading for the textual criticism it exists to serve. `morphology.surface_form` carries the clean `glyph` form for tokenizing and lemma queries.

**Variant readings.** `dss_variants` records where a scroll reads a lemma the Masoretic verse does not — 1,874 readings across 1,202 verses from 135 scrolls, derived at build time.

Comparing at **lemma** level rather than surface level is the whole difference between signal and noise. 1QIsaa spells more fully than the Masoretic and the scrolls habitually write a prefix as its own word, so on surface forms **99%** of comparable verses "differ" and the output is worthless. At lemma level both disappear and the figure falls to 28%, leaving readings.

Two disciplines are built in. Only **fully-extant** scroll words count, since a differing word that is partly reconstructed is a hole in the leather. And the comparison runs **one way only**: a lemma the scroll has and the Masoretic lacks is a reading, while the reverse is nearly always damage, and recording it would manufacture omissions out of gaps.

`extant_words` says how much of the verse survives, and it is there to be *weighed*, not filtered on. An earlier cut requiring five surviving words silently discarded **Deuteronomy 32:8 in 4Q37** — the best-known variant in the corpus — because only four survive there, though <span dir="rtl">בני אלוהים</span> is among them, whole. What matters is whether the differing word is legible, not whether its neighbours are.

```bash
uv run python query.py variants Deut 32 8    # -> 4Q37 reads אלהים (2 words survive)
uv run python query.py variants Isa 2 20     # -> 1Qisaa reads חפרפרה (13 survive)
uv run python query.py variants Isa 53       # a whole chapter
```

Two readings this makes checkable in-repo for the first time:

| Reference | Scrolls | Masoretic |
|---|---|---|
| Deuteronomy 32:8 | `dss-4Q37` — <span dir="rtl">בני אלוהים</span>, "sons of God", the reading the Septuagint follows | <span dir="rtl">בני ישראל</span>, "sons of Israel" |
| Psalm 22:17 (English 22:16) | `dss-5/6hev1b` — <span dir="rtl">כארו</span> | <span dir="rtl">כארי</span>, "like a lion" |

Reading the corpus needs the `text-fabric` package, which `references/build` now depends on; `build.py`'s `ingest_dss` is the only place that touches it.

### Versification — `(book, chapter, verse)` is not a universal address

Three schemes live in `bible-text.db`, and `works.versification` says which one each work uses (`masoretic`, 6 works; `lxx`, 1; `english`, 44). They disagree about **whole chapters**, so comparing across them without aligning returns the wrong verse and no error:

| Book | What differs |
|---|---|
| Joel | Hebrew **and LXX** have 4 chapters, English 3 — Joel 3:1 in both is **English Joel 2:28**, the verse Acts 2 quotes |
| Malachi | Hebrew and LXX have 3 chapters, English 4 — Malachi 3:19–24 is English 4:1–6 |
| Daniel | Divides differently in each direction, so no generalisation about "the LXX follows X" is safe. At **3/4** the LXX sides with English against the Masoretic (MT 3:31–33 is English 4:1–3). At **5/6** it sides with the Masoretic against English — "Darius the Mede received the kingdom" closes English chapter 5 but opens chapter 6 in both Hebrew and Greek |
| Psalms | The LXX renumbers nearly the whole psalter — English Psalm 23 is **LXX Psalm 22** — and adds Psalm 151 |
| Proverbs | Mostly identity. Brenton preserves the **Hebrew** verse numbering and omits what the LXX lacks (chapter 20 runs to verse 30 with 14–22 absent; chapter 31 opens at verse 10), so a shorter chapter here is not a renumbered one. Only chapter 24's tail is relocated — it carries the Agur material English prints as chapter 30, and there is no LXX chapter 30 at all |
| Jeremiah | Reordered, and the chapter *count* matches at 52, so a count-based check sees nothing. Now fully mapped except chapter 30 — see the table below |

**LXX Jeremiah in detail.** The book was derived chapter by chapter from this database, not from a published table: each relocated chapter names the nation it is against, and proper nouns survive translation, so the Greek and English names identify the same chapter independently. Verse deltas were then confirmed by matching place names verse by verse.

| LXX | English | How it was confirmed |
|---|---|---|
| 1–24 | same | 16 chapters' verse counts match exactly; nothing contradicts |
| 25:1–13 | 25:1–13 | 5 of 5 name hits at delta 0 |
| 25:14–19 | 49:34–39 | Elam. LXX 25:14 is verbatim English 49:34; 25:19 is 49:39 |
| 25:20 | — | a displaced Elam superscription; English 49:34 is already taken |
| 26 | 46 | Egypt, 15 of 16 name hits at delta 0 |
| 27 | 50 | Babylon, 37 of 38 |
| 28 | 51 | Babylon continued, 40 of 41 |
| 29 | 47 | the Philistines, 3 of 3 |
| 30 | — | Edom, Damascus, Kedar and Ammon, whose sub-oracles the LXX orders differently *within* the chapter, so no single delta holds. **Unmapped** |
| 31 | 48 | Moab, 27 of 27 |
| 32:15–38 | 25:15–38 | the cup of wrath. Brenton keeps the Hebrew verse numbers here, so this chapter runs 15–38 |
| 33–50 | 26–43 | offset −7; 13 verse counts match, and Hebrews 8:9–11 anchors LXX 38:32–34 to English 31:32–34 |
| 51:1–30 | 44:1–30 | same offset |
| 51:31–35 | 45:1–5 | the word to Baruch, which English prints as its own chapter. LXX 51:31 is verbatim English 45:1 |
| 52 | 52 | 28 of 29 name hits at delta 0 |

Two smaller cleanups belong to the same family. Verse text from eBible sources had BibleOrgSys's style markers (`¶ ¦ § ₁₂`) in 47% of WEB verses and 24% of the LXX; they are stripped at ingest, while Greek ano teleia and Hebrew sof pasuq are deliberately kept. And a translation code now resolves against `works` rather than by assuming `scrollmapper-{code}` — five codes live under a different prefix, WEB among them, so `lookup_verse(..., 'WEB')` had been returning nothing at all.

One known oddity left alone: `scrollmapper-MapM` stores Joshua 21:36–37 as `—`, that edition's placeholder for verses the Leningrad Codex omits. Faithful to the source, but it is text, not an absence.

Align with `versification.align()`, or from the command line / MCP:

```bash
uv run python query.py align Joel 2 28     # -> masoretic Joel 3:1, lxx Joel 3:1, english Joel 2:28
```

`lookup_verse` does this for you: it reads the reference in the requested work's scheme and fetches morphology and notes at whatever that verse is called in *theirs*, reporting the shift under `aligned_references`. Before this existed, asking for English Joel 3:1 returned English text with the morphology of Hebrew Joel 3:1 — a different verse — attached.

That last point generalises: **Brenton preserves the Hebrew verse numbers throughout and simply omits verses the LXX lacks**, which is why the edition shows 278 verse-number gaps. A short chapter is an omission, not a renumbering — the two look identical in a verse count and are completely different for alignment.

**Not modelled:** verse-level offsets *within* an aligned chapter, chiefly the psalm superscription counted as verse 1 in Hebrew and Greek. That is a per-digitisation choice rather than a property of the scheme — `scrollmapper-KJV` counts superscriptions and differs from `ebible-eng-web` in 116 psalms — so a single rule would be wrong for half the English works here. Compare psalm verse counts between two works before trusting a verse number.

### The Septuagint in `bible-text.db` — what's there, and where it doesn't line up

The LXX is the Brenton edition (`work_id` `ebible-grcbrent`, open tier). Two protocanonical books sit where the Greek canon puts them rather than where a USFM book code would suggest, and both were silently dropped as "deuterocanonical" until 2026-09-02:

- **Daniel** ships as *Greek* Daniel (`DNG`, not `DAN`). That text is **Theodotion**, not the Old Greek — identifiable at Daniel 1:3, which reads Ἀσφανὲζ where the Old Greek has Ἀβιεσδρί. Theodotion is the form the New Testament generally quotes, so it's the one worth having. Say which Greek Daniel you mean when you cite it.
- **Esther** ships as *Greek* Esther (`ESG`). Its six additions ride on **lettered** sub-verses (1:1b–1s, 3:13a–g, 4:17a–x, 5:1a–2b, 8:12a–u, 10:3a–k) precisely so the numeric verses keep the Hebrew numbering, so only the numeric ones are ingested and the additions are not in the database. Read them from `references/build/cache/grcbrent/43-ESGgrcbrent.usfm`; storing them would need a schema change, since `verses.verse` is `INTEGER`.
- **Nehemiah** has no file at all: it is the back half of **2 Esdras**, living inside `EZR` at chapters 11–23. `ingest_ebible` splits it back out, so `Neh` 1–13 queries normally.

Versification does **not** line up with the Masoretic everywhere, so don't assume `(book, chapter, verse)` means the same thing across works:

| Where | What differs |
|---|---|
| Daniel 3 | Theodotion inserts the Prayer of Azariah and the Song of the Three after 3:23 — 95 verses against the WLC's 33 |
| Daniel 4 | The chapter break falls three verses later: Greek Daniel 4:1–3 **is** WLC Daniel 3:31–33, so Greek 4:*n* = WLC 4:*n*−3 |
| Daniel 1–2, 5–12 | Align verse-for-verse with the WLC — including **9:24–27**, the Seventy Weeks |
| Nehemiah 3, 11, 12 | Shorter than the WLC (37/27/41 against 38/36/47); the other ten chapters match exactly |
| Esther 1 | Starts at **verse 2**. Addition A's opening carries a plain numeric `1`, which would land Mordecai's dream on `Esth 1:1` — an address that reads "in the days of Ahasuerus" in every other work. The Greek of the Masoretic 1:1 is on the lettered `1:1s`, out of reach, so verse 1 is dropped rather than filed under a reference meaning something else |
| Esther 4, 9 | The Greek abbreviates: 16 and 30 verses against the WLC's 17 and 32 |
| Esther 2, 3, 5, 6, 7, 8, 10 | Align verse-for-verse with the WLC |

`references/build/tests/test_lxx_coverage.py` pins all of the above.

For convenient lookups instead of hand-writing SQL each time, see `references/build/query.py` (word lookup, concordance, verse-range passages, cross-references, notes, clause syntax) — run `uv run python query.py --help`. `references/build/twot_lookup.py` is the equivalent for `twot_strongs_map.json` (root/Strong's/lemma reverse lookup) — run `uv run python twot_lookup.py --help`.

Example (raw SQL, if you need something the query script doesn't cover): a Greek word's lemma, Strong's number, and Louw-Nida domain for a specific verse —

```sql
SELECT surface_form, lemma, strongs_id, gloss, domain_code
FROM morphology WHERE work_id='macula-greek-sblgnt' AND book='Mark' AND chapter=5 AND verse=27;
```

### Clause syntax and coreference (MACULA)

Morphology answers "what is this word." Syntax answers "who is doing what to whom," which is where a
lot of exegetical arguments actually live. That data was sitting unused in the MACULA TSVs for a long
time — `build.py` loaded the word-level columns and dropped the rest. It now loads them into
`morphology` too, so no new table or source is involved:

| Column | Source | What it gives you |
|---|---|---|
| `word_class` | `class` | Part of speech. ~100% coverage both corpora |
| `syntactic_role` | `role` | **Greek only**: `s` subject, `v` verb, `o` object, `io` indirect object, `adv` adverbial, `p` predicate, `vc` copula. 33% |
| `sub_type` | `type` | Greek: common/proper/personal/demonstrative. **Hebrew: doubles as verb conjugation** — `qatal`, `wayyiqtol`, `yiqtol`, `participle active`. 33% / 73% |
| `state` | `state` | **Hebrew only**: `absolute` / `construct` / `determined` — i.e. construct chains. 28% |
| `subject_ref` | `subjref` | The node this verb's subject is. Pays off on **implicit subjects**, where the inflection carries the subject and no noun appears nearby |
| `referent` | `referent` (Gk) / `participantref` (Heb) | What a pronoun or participant points back at |
| `frame` | `frame` | Verbal argument frame, e.g. `A0:n40001018011`. Compound string — parse before joining |
| `node_id` | `xml:id` | MACULA's word id, **normalized to digits** — the key the two pointer columns join against |

```bash
uv run python query.py syntax Mark 6 41 --work-id macula-greek-sblgnt
```

Pointers are resolved to the words they name, across verse boundaries. Mark 6:41's four participles
(`λαβών`/`ἀναβλέψας`/`εὐλόγησεν`/`ἐδίδου`) all resolve their subject to **Jesus at Mark 6:30** — eleven
verses earlier, with no repeated noun in between. There is no way to get that from morphology.

Two traps, both of which fail *silently* and are covered by `tests/test_syntax.py`:

- **Pointer keys don't match the ids as shipped.** Every `xml:id` carries a corpus prefix (`n` Greek,
  `o` Hebrew), but only Greek *pointers* keep it — Hebrew `subjref` drops it (`o010010050061` vs
  `010010050021`). Joined raw, Hebrew coreference returns zero rows, which reads as missing data
  rather than a bad key. Hence digits-only normalization on both sides.
- **Pointers are multi-valued.** A plural subject or a pronoun with several antecedents holds a
  *space-separated list*. Treating the field as one id silently discarded ~18k rows — precisely the
  plural subjects most worth asking about. Split on whitespace; `lookup_syntax` always returns a
  list, even for one target.

A `NULL` here means **not annotated, not "no such role"** — coverage is partial by design, so never
argue from absence. And note the `frame`/pointer node ids are MACULA's own, not Strong's numbers.

**Why not BHSA?** `restricted-data/bhsa` (ETCBC) is the deeper OT syntax resource — full clause and
phrase hierarchy where MACULA gives a flatter word-level annotation. It is deliberately **not
ingested**: it's 1.6 GB of Text-Fabric `.tf` files needing the `text-fabric` package to read, and it
is `restricted-nc` where the MACULA columns are plain CC BY. Since MACULA already covers subject,
role, construct state, conjugation and coreference for both testaments at zero new dependency and a
freer licence, it is the right first stop. Reach for BHSA when an argument genuinely needs clause
*hierarchy* — subordination, embedding, clause typing — and record it as `restricted-nc` when you do.

### MCP server (for agent sessions)

`references/build/mcp_server.py` exposes the same lookups as MCP tools (`bible_word`, `bible_concordance`, `bible_domain`, `bible_verse`, `bible_syntax`, `bible_passage`, `bible_crossref`, `bible_align`, `bible_parallel`, `bible_quotations`, `study_gaps`, `bible_works`, `twot_root`, `twot_strongs`, `twot_lemma`), registered project-wide via `.mcp.json` at the repo root. It is a thin wrapper, not a second implementation: every tool calls a `lookup_*` function imported straight from `query.py` or `twot_lookup.py`, so the CLI and the MCP server can never return different answers to the same question, and both scripts keep working from the terminal (or from an agent's Bash tool as a fallback) whether or not the MCP server is configured. Adding a new lookup means adding one function to `query.py`/`twot_lookup.py` plus one `@mcp.tool()` wrapper — no query logic belongs in `mcp_server.py` itself. `study-notes.db` has no query library yet, so it isn't wired into the MCP server either; see the note in `mcp_server.py`'s own docstring before adding one, since that data's `quotation-only` tier needs tighter discipline (snippet-sized returns) than a straight passthrough would give it.

**There is currently no `export.py`** in this pipeline (referenced in `build.py`'s own docstring but not yet built) — tier-filtering to keep `restricted-nc` rows out of anything meant to go fully public (vs. "public but non-commercial," which is fine) is a manual discipline right now, not an enforced guarantee. Check `license_tier` yourself before copying a query result into a committed file.

## study-notes.db — commercial study-Bible commentary (external, not in this repo at all)

```bash
cd references/build
uv run python build_study_notes.py
```

Writes to `$BIBLE_MEDIA_ROOT/local-only-build/study-notes.db` — never anywhere under `bible_studies/`. See `references/build/study_notes/schema.sql` for tables (`works`, `verses`, `introductions`, `notes`, `topical_articles`, `images`). Sources are registered declaratively in `references/build/study_notes/sources.py` — currently ESV Study Bible, NIV Cultural Backgrounds Study Bible, NKJV Cultural Backgrounds Study Bible, NIV Biblical Theology Study Bible, CSB Ancient Faith Study Bible, the NA28 Greek NT (from the NA28-ESV parallel), NLT Life Application Study Bible, NLT Christian Basics Bible, NASB 1995/2020, and the Legacy Standard Bible (2021). **Adding another source that fits an existing extractor family is a config entry in `sources.py`, not new code** — check `extractors/__init__.py` before writing a new parser. Five families exist: `numeric_id` (shared `BBCCCVVV` verse ids — ESV/NIV/NKJV/NA28), `anchor_walker` (`start-BookName.C.V` anchors — CSB), `dotted_id` (`vs-BookAbbrev.C.V` anchors plus self-contained note/cref/textnote wrapper divs — the two NLT epubs), `positional_verse` (no ids at all, verse boundaries recovered from chapter headers and inline verse-number markup — NASB, a plain calibre-converted reflow with none of the other three epubs' semantic markup), and `jet_bible` (**not an EPUB at all** — a Microsoft Access/Jet database with flat `Bible` and `Footnotes` tables, as BibleShow-style `.bib` modules use; read via `mdb-export` from mdbtools, `brew install mdbtools`). A source whose extractor sets `needs_unzip = False` is handed its own file path instead of an unzipped tree.

Query it the same way as `bible-text.db`, but pointed at the external path **and opened with
`immutable=1`**:

```sql
sqlite3 "file:$BIBLE_MEDIA_ROOT/local-only-build/study-notes.db?immutable=1" \
  "SELECT text FROM notes WHERE work_id='niv-cultural-backgrounds-study-bible' AND book='Mark' AND chapter=5 AND verse_start<=27 AND verse_end>=27;"
```

**`note_type` holds two different kinds of evidence — don't query them as one.** A `study_note`
(~54,000) is the editors' commentary: a scholar's argued view, to be weighed against other scholars
and quoted with attribution. A `footnote` (~22,000, two-thirds of them the LSB's) is the *translation
committee's own record of a decision* — "Or X", "Lit Y", "Some mss omit Z", a measurement conversion,
a note that a NT quotation departs from the OT it cites. That is much closer to primary evidence, and
it is the half that had no method behind it until 2026-09: neither skill mentioned footnotes and no
study had ever cited one. Both skills now say to pull them for a passage as a matter of course.

```sql
-- the translators' own notes at one verse, across every work that has them
sqlite3 "file:$BIBLE_MEDIA_ROOT/local-only-build/study-notes.db?immutable=1" \
  "SELECT work_id, text FROM notes WHERE note_type='footnote'
     AND book='Song' AND chapter=8 AND verse_start<=6 AND verse_end>=6;"
```

`immutable=1` is not optional cosmetics — **without it this fails under the agent sandbox** with
`Error: in prepare, access permission denied (3)`, which looks like a missing-file or bad-schema error
and is neither. The volume is readable, but SQLite's locking layer wants POSIX advisory locks (and the
freedom to create `-wal`/`-shm`/`-journal` siblings) that the sandbox declines to grant out there.
`immutable=1` promises SQLite the file won't change underneath it, so it skips locking and journalling
altogether and just reads. `?mode=ro` is **not** sufficient — read-only still takes a shared lock.
(`nolock=1` also works, but `immutable=1` states the intent better for a read-only reference DB.)

So there is nothing to fix in the sandbox configuration and no reason to disable it for these
lookups — use this URI form and it works as an ordinary sandboxed read. The same applies to
`lexicon-restricted.db` beside it. In Python: `sqlite3.connect(f"file:{path}?immutable=1", uri=True)`.

**Verse text, not just notes.** It's easy to read this section as covering study-Bible *commentary*
only. The `verses` table also holds each edition's full Bible text — including the **ESV**
(`work_id='esv-study-bible'`), NIV, NKJV, CSB, NLT (`nlt-life-application-study-bible` /
`nlt-christian-basics-bible`), and NASB (`nasb-1995` / `nasb-2020`), none of which are in
`bible-text.db`. This is the place to verify an ESV quotation instead of trusting recall:

```sql
sqlite3 "file:$BIBLE_MEDIA_ROOT/local-only-build/study-notes.db?immutable=1" \
  "SELECT book||' '||chapter||':'||verse, text FROM verses WHERE work_id='esv-study-bible' AND book='John' AND chapter=6 AND verse BETWEEN 26 AND 27;"
```

`quotation-only` means: fine — expected, even — to quote a sentence or two with attribution in a study's own References section (see the skill's Phase 7). Not fine: bulk-exporting this database's contents, or reproducing a full note/article verbatim into a committed file.

### Two different permissions, don't conflate them

These editions contain two legally distinct things, and the rules are not the same for both:

1. **The Bible text** — governed by the publisher's own permission notice, which grants a generous,
   explicit allowance with no need to ask.
2. **The study notes, introductions, articles, charts and maps** — separately copyrighted, with **no
   blanket allowance at all**. The ESV Study Bible's notice is explicit: "Crossway reserves all
   rights for all of the content of the ESV Study Bible." For these, a short attributed quotation
   under fair use is the whole of what's available — which is where "a sentence or two" belongs.

Verified against the permission notices in the epubs themselves (`$BIBLE_MEDIA_ROOT/bibles/`), not
from memory — the numbers are easy to misremember and one of these is commonly misquoted:

| Translation | Verses without asking | Must not exceed | Also |
|---|---|---|---|
| **ESV** (Crossway) | **1,000** (250 for audio) | 50% of your work; never a complete book | Copyright notice required on the title/copyright page |
| **CSB** (Holman) | **1,000** | 50% of your work; never a complete book | Credit line required |
| **NKJV** (Thomas Nelson) | **1,000** (printed) | 50% of a complete book *and* 50% of your work | Quotations must conform exactly to the NKJV text |
| **NIV** (Zondervan/Biblica) | **500** | 25% of your work; never a complete book | Copyright notice required; separate easier terms for church bulletins |
| **NLT** (Tyndale House) | **500** | 25% of your work; never a complete book | Copyright notice required on the copyright/title page; "NLT" initials alone suffice in nonsalable media (bulletins, newsletters) |
| **NASB** (Lockman) | **none stated in this edition** | — | The epub's notice says quotation/reprint requests "must be directed to and approved in writing by The Lockman Foundation." Don't assume a threshold; check lockman.org |
| **NA28 Greek** (Deutsche Bibelgesellschaft) | none stated | — | "Used by permission" to Crossway for that parallel edition; that grant isn't ours to inherit |

**For this repo the binding constraint is the percentage, not the verse count.** No single study is
going to approach 500 verses, so the verse ceilings are practically irrelevant. The 25%/50% test is
not: a short page that is mostly block-quoted Scripture can breach it at a couple of dozen verses.
If a study is mostly quotation with a little commentary, that's the rule it trips — and it's a sign
the study is thin anyway. Note also the ESV's 50% is measured against *the work in which they are
quoted*; whether that means one page or the whole site is not something this README can settle, so
keep individual studies comfortably clear of it rather than relying on a favourable reading.
**NASB is not covered by this reasoning at all** — there's no percentage or verse ceiling to stay
clear of because there's no stated allowance in the first place; treat `nasb-1995`/`nasb-2020` as
verify-only (checking a quotation you already have some other reason to trust) rather than a source
to quote from directly the way ESV/CSB/NKJV/NIV/NLT can be.

**Attribution is an obligation, not a courtesy.** ESV, CSB, NKJV, NIV and NLT all require a copyright
notice where their text is quoted. Naming the translation inline — "(ESV)" after a quote, as
AGENTS.md already requires — satisfies scholarly convention but is *not* the notice these licences
ask for. The site carries the required notices on
[docs/content/about/copyright.md](../docs/content/about/copyright.md); add to it if a study
introduces a translation not already listed there.

## open-data/ and restricted-data/

Git submodules of forked open-data repos (Bible texts, lexicons, morphology, cross-references) — see [docs/content/resources/github.md](../docs/content/resources/github.md) for the full master list, license findings, and why each one's there. Also see that doc's **eBible.org section** for translations fetched at build time rather than forked (not git-hosted, so the submodule pattern doesn't apply).

- **`open-data/`** — unconditionally open licenses only (CC BY, CC0, public domain). Safe regardless of this repo's visibility or commercial status.
- **`restricted-data/`** — usable now, but under non-commercial-only or similarly restricted terms. Fine to keep public as long as this site stays non-commercial; would need re-review if that ever changes. Never mix these into `open-data/` — the directory boundary *is* the audit boundary.

## study-state/

One structured-data file per study in progress, tracking exegesis/hermeneutics progress so work can resume across sessions. See [study-state.template.yml](../.claude/skills/develop-bible-study/study-state.template.yml) for the schema. Safe to commit — it's metadata (passages, stages, sources consulted), not copyrighted source text. **Always fill in `resources_consulted`** as you go — that's what makes a study's reasoning traceable later, for any source tier.

## Patristic texts (external, not in this repo)

Held at `$BIBLE_MEDIA_ROOT/reference/patristics/`, with a `PROVENANCE.md` recording source, date
retrieved, and licence tier per item. Added 2026-08-08 while reviewing the Twelve Apostles study set,
which had been written with patristic claims recalled from memory rather than checked — exactly the
failure mode the review skill exists to catch. Reader-facing companion page, with the reliability
grading rather than the file paths: [docs/content/resources/patristic-sources.md](../docs/content/resources/patristic-sources.md).

- **`eusebius-npnf2-01-church-history.txt`** — *Nicene and Post-Nicene Fathers* Series 2 Vol. 1
  (Schaff & Wace, eds.; trans./annotated by A. C. McGiffert, 1890), from
  [CCEL](https://ccel.org/ccel/schaff/npnf201). **Licence tier: open** (published 1890, public domain
  by age) — quote at length and cite freely. This is the go-to for Hist. eccl. 3.1 (Origen on the
  apostles' mission fields), 1.13 (Abgar/Thaddaeus), and 3.39 (Papias). **McGiffert's footnotes are
  the most valuable part**: they date and grade each tradition instead of repeating it, and they
  caught a real overstatement in this repo's own Thomas study (India is a *late* tradition; Parthia
  is the early one).
- **`apostolic-fathers-greek/`** (15 files) — 1-2 Clement, the Ignatian epistles, Polycarp, Didache,
  Barnabas, Shepherd of Hermas, Martyrdom of Polycarp, Diognetus, in Greek, from
  [jtauber/apostolic-fathers](https://github.com/jtauber/apostolic-fathers) (corrected Kirsopp Lake
  text). **Licence tier: unknown — treat as restricted.** The underlying Lake text is public domain
  by age, but the repository states no licence covering its corrections, so these files are *not*
  committed here and must not be redistributed. Brief quotation with attribution is fine. Beyond the
  apostles, the Didache and Ignatius are directly relevant to early-church-practice and Hebrew-roots
  studies.

- **`ante-nicene-fathers/`** (`anf01.txt` … `anf10.txt`, ~35 MB) — *Ante-Nicene Fathers* Vols. 1-10
  (Roberts & Donaldson, eds.; Coxe's American edition), from
  [CCEL](https://ccel.org/ccel/s/schaff/anf01). **Licence tier: open** — public domain by age, marked
  as such by CCEL. The two volumes that earn their place immediately: **anf01** has **Irenaeus**
  (*Against Heresies* 3.1.1 on Matthew writing among the Hebrews and John publishing at Ephesus;
  3.3.4 on Irenaeus having seen Polycarp), and **anf08** has the **New Testament apocrypha** including
  the *Acts of Thomas*. Also inside: Justin Martyr (anf01), Clement of Alexandria (anf02), Tertullian
  (anf03-04), Hippolytus and Cyprian (anf05), Lactantius (anf07), and the Diatessaron and Gospel of
  Peter (anf09). `anf10` is the index volume and is legitimately tiny (28 KB, image-only on CCEL) —
  not a failed download.

**Fetching more from CCEL.** The plain text lives at `/ccel/s/schaff/<id>/cache/<id>.txt`. The
`/ccel/schaff/<id>.txt` landing page **returns HTML with a 200**, so a naive fetch looks like it
worked until you read the file — check for `<!DOCTYPE` before trusting it. `ccel.org` and
`www.ccel.org` are in the sandbox network allowlist in `.claude/settings.json`.

**Nothing is currently outstanding.** Every patristic claim on the site has been verified against
primary text.

## Word study & original-language tools

For the Hebrew/Aramaic/Greek word studies AGENTS.md requires (original text + gloss + pronunciation), prefer the forked data in `open-data/` (`hebrew-lexicon`, `strongs`, `morphhb`, `stepbible-data`, `greek-resources`) for agent/offline use — queried via `bible-text.db` above. For quick manual lookups:

- **[Blue Letter Bible](https://www.blueletterbible.org/)** — interlinear + Strong's-tagged lookup, Hebrew and Greek, free.
- **[STEP Bible](https://www.stepbible.org/)** (Tyndale House) — interlinear, lexicons, and original-language search, free.
- **[Bible Hub interlinear](https://biblehub.com/interlinear/)** — quick interlinear + Strong's cross-links.
- **[PrecepAustin](https://www.preceptaustin.org/greek_word_study)** — Bruce Hurt's verse-by-verse word-study compilation site; useful as one more cross-check pass and as a pointer into public-domain classics (Vine's, Robertson's *Word Pictures*, Vincent's *Word Studies*) it curates per-word. It's the author's own synthesis, not raw lexical data, so treat it like a named commentary: cite with attribution, don't bulk-borrow. Its own explicit caution is worth repeating here — "every lexicon is at least in part a product of the lexicon writer's systematic bias," including Thayer's — a reason to cross-check a load-bearing gloss against more than one lexicon (Louw-Nida/SDBH below, TWOT, BDAG) rather than settling on the first one that supports a reading.
- **Louw & Nida, *Greek-English Lexicon of the New Testament Based on Semantic Domains*** (Greek) and **SDBH, *Semantic Dictionary of Biblical Hebrew*** (Hebrew) — group words by usage relationship rather than lexical root; the cross-check step in the fuller word-study method (see the [develop-bible-study word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md)) leans on these. Available as local data via `open-data/macula-greek` (`@ln`/`@domain`) and `open-data/macula-hebrew` (`@sdbh`/`@lexdomain`) — see [docs/content/resources/github.md](../docs/content/resources/github.md) for the license caveat on the Greek domain field specifically.
- **TWOT** (*Theological Wordbook of the Old Testament*, Archer, Harris & Waltke, Moody Publishers) — the standard companion to Strong's/BDB for Hebrew root theology. `references/build/twot/twot_strongs_map.json` **is committed** and gives a `TWOT root → {strongs_id, bdb_id, lemma, xlit, gloss}` reverse-lookup usable right now. The fuller OCR/segmentation extraction of TWOT's actual discussion prose (`references/build/twot/`) is **not committed** and must not be — TWOT has no open license, unlike the bare Strong's numbers/glosses in the map above (same distinction as the caveat already on the `strongs` fork in [docs/content/resources/github.md](../docs/content/resources/github.md)).
- **Trench, *Synonyms of the New Testament*** (1880) and **Girdlestone, *Synonyms of the Old Testament*** (1897) — public domain, and the gap the other resources on this list don't cover: distinguishing *between* two near-synonyms rather than defining one word in isolation. Reach for these specifically when a study's argument turns on why the text uses one word and not a close alternative — the same kind of finding as this site's own *kophinos*/*spyris* distinction in the Bread of Life study, which Trench-style comparison would have been the traditional way to reach. Free full text on [archive.org](https://archive.org) and [Perseus](http://www.perseus.tufts.edu/).
- **Moulton & Milligan, *The Vocabulary of the Greek Testament*** (1930) — documentary papyri (private letters, receipts, contracts) rather than literary Greek, showing how a word was used in *ordinary* first-century speech. A useful check against reading a term as more technical or "special" than it actually was outside a theological text — public domain, free on archive.org.

For Hebrew *language learning* (as opposed to word-study lookup), see the existing [hebrew-studies/resources.md](../docs/content/hebrew-studies/resources.md).

## Cross-reference tools

- **Treasury of Scripture Knowledge (TSK)** — public domain (1836), the standard cross-reference set; available on Bible Hub and Blue Letter Bible per-verse.
- **Bible Gateway / Bible Hub parallel view** — quick multi-translation comparison, needed for the translation-comparison step in Phase 6 of the skill.

## Secondary/commentary sources (local-only, not committed)

These are commercially-sold or otherwise copyrighted works. The **source files themselves** aren't committed to this repo — this is a public repo, and committing an entire copyrighted work would be redistribution, not personal use. Most are queryable through `study-notes.db` above rather than by hand.

That doesn't mean these sources can't be *cited*. **They should be** — citing a restricted or copyrighted source by name, with attribution and a reasonably short quotation, is a normal and expected thing to do in a public study, not something to avoid. What copyright actually constrains: quoting *too much* of one source (a full paragraph or note, not a sentence or two) into a committed file, or citing without attribution. Every study should end with a **References & Recommended Reading** section (see the skill's Phase 7) naming every source actually drawn on — restricted/copyrighted ones by name included — so a reader can go find the fuller discussion themselves.

- *How to Read the Bible for All Its Worth* (Fee & Stuart, 4th ed.) — the methodology behind the develop-bible-study skill. Source PDF + a full local markdown extraction live next to each other on the media volume, for personal reference only. The site's own public write-up of these principles, for readers rather than for the skill tooling, is [docs/content/bible/how-to-read-the-bible.md](../docs/content/bible/how-to-read-the-bible.md) — currently a draft stub, not yet fleshed out.
- Gerald L. Stevens, "Word Study Guide — New Testament" (seminary course handout) — the methodology behind [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md). Source PDF at `$BIBLE_MEDIA_ROOT/resources/NTWordStudyGuide.pdf`; the skill file is an original synthesis of the method, not a reproduction.
- *ESV Study Bible* (Crossway, 2016), *NIV Cultural Backgrounds Study Bible* and *NKJV Cultural Backgrounds Study Bible* (Zondervan, ed. John H. Walton & Craig S. Keener), *NIV Biblical Theology Study Bible* (Zondervan), *CSB Ancient Faith Study Bible* (Holman), *NLT Life Application Study Bible, Third Edition* (Tyndale House, 2019) and *NLT Christian Basics Bible* (Tyndale House, ed. Mike Beaumont & Martin Manser, 2017) — all queryable via `study-notes.db` above.
- *NASB 1995 Update* and *NASB 2020 Text Edition* (The Lockman Foundation) — verse text only, no notes; queryable via `study-notes.db` for verification, but see the permissions table above before quoting directly (no stated threshold, unlike the study Bibles listed here).
- Any other commentary consulted for a study should be recorded per-study in that study's `resources_consulted` field *and* named in the study's own References section — not duplicated here.
