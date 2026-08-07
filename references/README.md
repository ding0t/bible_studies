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
| Clause syntax, coreference, Hebrew construct state / verb conjugation | `bible-text.db` `morphology` table (MACULA columns) — `query.py syntax` / `bible_syntax` | open | Cite freely; see the syntax section below for what the annotation does and doesn't cover |
| Byzantine/TR Greek, BHSA syntax trees, Mounce dictionary | `restricted-data/*` | restricted-nc | Fine to use and cite now (site is non-commercial); flag if that ever changes. **BHSA is not ingested** — see the syntax section below for why MACULA is the better first stop |
| Jewish literature (Mishnah, Talmud) for cultural/historical background | `references/build/sefaria.py` (Sefaria-Export) | varies per translation — check before quoting | Prefer a CC0/CC-BY/public-domain version; cite the specific version quoted |
| Early church fathers — post-apostolic tradition, what became of the apostles | `/Volumes/media/bible/reference/patristics/` (external, see below) | mixed: NPNF **open**, Apostolic Fathers Greek **unknown/restricted** | Quote NPNF freely with attribution; quote the Greek corpus briefly, never redistribute |
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

`references/build/mcp_server.py` exposes the same lookups as MCP tools (`bible_word`, `bible_concordance`, `bible_domain`, `bible_verse`, `bible_syntax`, `bible_passage`, `bible_crossref`, `bible_works`, `twot_root`, `twot_strongs`, `twot_lemma`), registered project-wide via `.mcp.json` at the repo root. It is a thin wrapper, not a second implementation: every tool calls a `lookup_*` function imported straight from `query.py` or `twot_lookup.py`, so the CLI and the MCP server can never return different answers to the same question, and both scripts keep working from the terminal (or from an agent's Bash tool as a fallback) whether or not the MCP server is configured. Adding a new lookup means adding one function to `query.py`/`twot_lookup.py` plus one `@mcp.tool()` wrapper — no query logic belongs in `mcp_server.py` itself. `study-notes.db` has no query library yet, so it isn't wired into the MCP server either; see the note in `mcp_server.py`'s own docstring before adding one, since that data's `quotation-only` tier needs tighter discipline (snippet-sized returns) than a straight passthrough would give it.

**There is currently no `export.py`** in this pipeline (referenced in `build.py`'s own docstring but not yet built) — tier-filtering to keep `restricted-nc` rows out of anything meant to go fully public (vs. "public but non-commercial," which is fine) is a manual discipline right now, not an enforced guarantee. Check `license_tier` yourself before copying a query result into a committed file.

## study-notes.db — commercial study-Bible commentary (external, not in this repo at all)

```bash
cd references/build
uv run python build_study_notes.py
```

Writes to `/Volumes/media/bible/local-only-build/study-notes.db` — never anywhere under `bible_studies/`. See `references/build/study_notes/schema.sql` for tables (`works`, `verses`, `introductions`, `notes`, `topical_articles`, `images`). Sources are registered declaratively in `references/build/study_notes/sources.py` — currently ESV Study Bible, NIV Cultural Backgrounds Study Bible, NKJV Cultural Backgrounds Study Bible, NIV Biblical Theology Study Bible, CSB Ancient Faith Study Bible, the NA28 Greek NT (from the NA28-ESV parallel), NLT Life Application Study Bible, NLT Christian Basics Bible, and NASB 1995/2020. **Adding another source that fits an existing extractor family is a config entry in `sources.py`, not new code** — check `extractors/__init__.py` before writing a new parser. Four families exist: `numeric_id` (shared `BBCCCVVV` verse ids — ESV/NIV/NKJV/NA28), `anchor_walker` (`start-BookName.C.V` anchors — CSB), `dotted_id` (`vs-BookAbbrev.C.V` anchors plus self-contained note/cref/textnote wrapper divs — the two NLT epubs), and `positional_verse` (no ids at all, verse boundaries recovered from chapter headers and inline verse-number markup — NASB, a plain calibre-converted reflow with none of the other three epubs' semantic markup).

Query it the same way as `bible-text.db`, but pointed at the external path **and opened with
`immutable=1`**:

```sql
sqlite3 "file:/Volumes/media/bible/local-only-build/study-notes.db?immutable=1" \
  "SELECT text FROM notes WHERE work_id='niv-cultural-backgrounds-study-bible' AND book='Mark' AND chapter=5 AND verse_start<=27 AND verse_end>=27;"
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
sqlite3 "file:/Volumes/media/bible/local-only-build/study-notes.db?immutable=1" \
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

Verified against the permission notices in the epubs themselves (`/Volumes/media/bible/bibles/`), not
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

Held at `/Volumes/media/bible/reference/patristics/`, with a `PROVENANCE.md` recording source, date
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
- Gerald L. Stevens, "Word Study Guide — New Testament" (seminary course handout) — the methodology behind [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md). Source PDF at `/Volumes/media/bible/resources/NTWordStudyGuide.pdf`; the skill file is an original synthesis of the method, not a reproduction.
- *ESV Study Bible* (Crossway, 2016), *NIV Cultural Backgrounds Study Bible* and *NKJV Cultural Backgrounds Study Bible* (Zondervan, ed. John H. Walton & Craig S. Keener), *NIV Biblical Theology Study Bible* (Zondervan), *CSB Ancient Faith Study Bible* (Holman), *NLT Life Application Study Bible, Third Edition* (Tyndale House, 2019) and *NLT Christian Basics Bible* (Tyndale House, ed. Mike Beaumont & Martin Manser, 2017) — all queryable via `study-notes.db` above.
- *NASB 1995 Update* and *NASB 2020 Text Edition* (The Lockman Foundation) — verse text only, no notes; queryable via `study-notes.db` for verification, but see the permissions table above before quoting directly (no stated threshold, unlike the study Bibles listed here).
- Any other commentary consulted for a study should be recorded per-study in that study's `resources_consulted` field *and* named in the study's own References section — not duplicated here.
