# Commands

The full command reference, moved out of `AGENTS.md` on 2026-11-15 so the standing brief stays short.
`AGENTS.md` keeps the everyday few.

**Content site** (`docs/content/` — mkdocs-material, where nearly all writing happens):

```bash
uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects --with segno mkdocs serve
```

Hot-reload dev server at http://localhost:8000/. `docs_dir` is `docs/content` (see `mkdocs.yml`).

**Interactive tools** (`app/` — React components bundled into the mkdocs site, separate npm project):

```bash
cd app
npm install
npm run build:tools  # events.json + esbuild -> docs/content/assets/js/{timeline,references,
                     # popups,hebrew-cards}.js (gitignored). Run before `mkdocs serve`, or the tool
                     # pages render an empty div and no reference on any page pops up.
npm run dev:tools    # same, unminified, with esbuild --watch. Pair with `mkdocs serve`: the
                     # bundles land inside docs_dir, so a rebuild triggers a page reload.
npm test             # build-events, calendarConvert, bibleReference, chronology, cardReview
npm run lint         # eslint src/  (npm run format for prettier)
```

The tools style themselves from ten `--color-*` CSS variables with light-mode fallbacks (the
`theme` object in each component). `docs/content/assets/stylesheets/tools.css` maps those onto
mkdocs-material's own variables, which is what makes the timeline follow the site's
dark-mode toggle without any component change. Add a colour there, not as a hex in a component.

The suites are plain `node:test` files, so a single one runs directly — `node --test
scripts/build-events.test.js`, or `node src/utils/chronology.test.js` for the `src/utils/` ones
(each is executable on its own; that's why `npm test` mixes both invocation styles).

`npm run validate` (`app/scripts/validate-content.js`, run from `app/`) is the content linter, and
**it is not wired into CI** — the deploy workflow runs `npm test` only, so validate has to be run
by hand after editing content. It applies 26 checks in nine groups:

- **Checks 1–9, structural**: frontmatter (required fields, tag quoting, draft status), image paths,
  scripture quote blocks opening with `> ✝️ Reference (TRANSLATION)` as their first line (the
  develop-bible-study skill's formatting.md), and Hebrew/Aramaic text never wrapped in markdown
  bold (synthetic bold misplaces niqqud — use `<span dir="rtl">`).
- **Checks 10–13, style-guide enforcement**: the `worth ___` narrating template, "virtue contrast"
  (`rather than` + a straw alternative), bullets over 100 words, and reader-reassurance address.
  These are deliberately **warnings, not errors** — each has a legitimate use the regex can't
  distinguish, and the thresholds were tuned against a corpus audit to keep false positives near
  zero. Read the comments above each check before tightening one; the rationale is recorded there.
  See `.claude/skills/develop-bible-study/style-guide.md` for the prose rules these partially
  mechanize.
- **Checks 14–17**: how long a study's opening makes a reader wait for its point (words to the
  first bold thesis, block-quote share of the opening, unglossed terms of art), and the provenance
  frontmatter — missing fields, a `date_modified` behind the file's last commit, or an
  `ai_provider_models` entry that isn't provider-qualified. Also warnings.
- **Check 20, prose that cannot be read aloud** — sentence-length median and long tail, measured
  against Pauline chapters so Paul himself would pass. **Check 21, an unbroken prose run** over
  600 words under one heading, where a reader has nowhere to stop (tables, lists and quotes
  excluded, so a section with sub-headings never fires). 600 is the far tail — p96 of a 984-section
  corpus audit; the 250-400 word target lives in
  [structural-readability.md](../../.claude/skills/read-bible-study/structural-readability.md), the
  standard the **read-bible-study** skill applies and the positive counterpart to style-guide.md's
  prohibitions. Both warnings. **Check 22, a study with no `## Study outline`** — 2,500+
  words *and* 6+ top-level sections, which is 38 of 113 content pages (lowered from 5,000/8 on
  2026-09-25 so readers get the mind map early). mkdocs renders a table of contents already; what it cannot do is annotate a section,
  group a run of eight into one line, or tell the reader which part they are standing in — see
  structural-readability.md rule 10, including the rule that an agent writes *descriptive*
  annotations and leaves evaluative ones to the author. Warning, because whether a page is
  navigable is a judgment about its argument that a word count cannot make.
- **Check 23, a study over its word budget** — `word_budget` in
  `references/study-state/<slug>.yml`, else 4,000 words (about 27 minutes read aloud; References and
  the Study outline are not counted, since both are consulted rather than read). Warning;
  the fix is the **simplify-bible-study** skill's recommendation, or a raised budget with its
  reason recorded in the state file.
- **Check 24, a published page linking to a draft** — an **error**. `hooks/draft_pages.py` drops
  drafts from the build without a warning, so the link ships as a 404 that `mkdocs build --strict`
  cannot see. Fix it by removing the link or by publishing the target in the same commit. Image
  lines (alt text) are excluded from the prose measurements in Checks 20-23: alt text is
  described for a screen reader and never read aloud.
- **Check 25, discussion questions without facet labels** — a question with no bold facet label
  (**The language.**, **The text in its context.**, **Christ.**, **The hard part.**,
  **Be transformed.**), or a set with no **Be transformed.** question. Warning; the format and the
  reference specimen (`hurt-by-the-church.md`) are in
  `.claude/skills/develop-bible-study/discussion-questions.md`.
- **Check 26, a Bible reference without its book** — a stand-alone "(5:27)" or "at 4:16" with no
  book in its sentence. A book named in words there counts ("both in Job (1:6; 2:1)"), as the
  pop-up reads it, and only the first of a bare run is reported. Quotations, headings, alt text,
  inline code, non-biblical works (1 Enoch, the Mishnah, Tobit) and table cells under a header or
  row naming the book are skipped, each reason recorded at `bareReferences`. Warning; the fix is
  the book chosen from what the paragraph discusses, never copied from the nearest earlier
  reference. The 2026-11-15 sweep brought the site to zero.
- **Checks 18–19, claims that go stale silently.** An exhaustiveness claim ("only occurrence",
  "nowhere else") sharing a line with Greek or Hebrew characters — the cheapest sentence in a study
  to write and the most expensive to verify, so routinely written unverified; one shipped saying
  βύσσινος "clothes nobody else in the book" when Babylon wears it six verses earlier. And a
  directional reference whose anchor points the other way ("see [X](#x) above" when `#x` is below).
  Reordering a study breaks those in bulk and *nothing else can see it* — the anchor still resolves,
  so `mkdocs build --strict` passes and the reader is simply sent the wrong way. Neither check can
  verify the claim; both ask.

**Bible-text database** (`references/build/` — `uv`-managed Python, ≥3.14):

```bash
cd references/build
uv sync
uv run python build.py             # builds out/bible-text.db (gitignored, regenerable)
uv run pytest                      # completeness / query-diagnostics / syntax checks against out/bible-text.db
uv run pytest tests/test_syntax.py # single suite (pythonpath is set in pyproject.toml — run from references/build)
uv run python query.py --help      # word / concordance / verse / passage / cross-ref / align / parallel / scripture-link lookups
uv run python study_gaps.py docs/content/<study>.md   # what links to a study's passages that it never cites
                                                      # (MCP tool for the same thing: review_gaps)
uv run python strongs_suggest.py docs/content/<study>.md  # glossed Greek/Hebrew words with no Strong's number, and the number
                                                          # MACULA gives each -- reports, never writes (--all for the corpus)
uv run python twot_lookup.py --help
uv run pytest tests/test_invariants.py                # every declared table has rows -- the guard the empty `notes` table needed
uv run python study_structure.py <path>               # section-by-section prose measurements for the read-bible-study skill
uv run python study_structure.py <path> --verify-against HEAD  # prove a restructure changed no sentence
uv run python study_structure.py                      # corpus: studies ranked by their worst unbroken prose run
uv run python verify_claims.py                        # re-run the SQL behind studies' recorded counts, compare to `expect:`
uv run python verify_claims.py --evidence             # also replay `evidence:` blocks -- tool calls with expected answers
uv run python verify_claims.py <slug> --only-evidence # just one study's evidence
uv run python cross_study_claims.py --min-studies 4   # chapters several studies treat; add a chapter to see what each says
                                                      # ("John 4" --exclude <slug>.md: the siblings a new study should link or build on)
uv run python commentary_index.py  # regenerate auto cross-ref pages — run after editing a study's bible_references/primary_passage
uv run python section_index.py     # regenerate category landing pages — run after adding a study or new content section
uv run python build_study_notes.py # commercial study-Bible db, writes outside this repo — see references/README.md
uv run python export_popups.py     # verse + word pop-up data -> docs/content/assets/popups/ (committed; re-run when bible-text.db changes)
uv run python export_harmony.py    # STEP's harmony of the gospels -> docs/data/gospel-harmony.json (committed), the timeline's
                                   # "Also told in"; re-run after build.py's STEP_APP_COMMIT moves
uv run python step_chronology_check.py  # this site's dates against STEP's chronology (Hebrew_200_15); reports, never edits.
                                        # STEP's AM is not this site's AM: it compares AM only inside Genesis
uv run python build_study_notes.py --esv-tags  # add STEP's TTESV ESV word tags to the existing study-notes.db
uv run python export_connector.py --publish  # the connector's Hebrew/Greek data -> docs/content/assets/lang/ (130 MB,
                                             # gitignored) and the `lang-data` release the deploy downloads
uv run python export_memory_verses.py  # docs/data/memory-verses.toml -> .json for the printable cards (hooks/memory_verses.py);
                                       # re-run after adding a verse -- needs study-notes.db for the ESV
uv run python export_songbook.py   # docs/data/songbook.toml -> songbook-words.json, each song's full WEB text
                                   # for the Songbook (hooks/songbook.py); re-run after adding a song
uv run python export_prophecies.py # prophecies-of-christ.toml -> .json: years written and fulfilled, Qumran
                                   # copies, for the reference page (hooks/prophecies.py) and the jesus/
                                   # charts; re-run after editing the ledger (check_prophecies.py fails if stale)
```

**Source catalog drift check** (run from the repo root, stdlib only):

```bash
python3 references/check_sources.py   # every source on disk documented, the three docs describing
                                      # the patristics corpus still in agreement, and sources.toml
                                      # still matching what build.py actually ingests?
python3 references/build/source_catalog.py   # print the catalog: tiers, locations, raw-only list
python3 utils/check_skills.py                 # skills still match the repo: links, anchors, MCP tool names,
                                              # paths (runs in npm test); rules in .claude/skills/README.md
```

**`references/sources.toml` is the single authority** for where each source lives, what licence
tier it sits in, and how much of it may be reproduced. `media_root.py`, `build.py`,
`study_notes_query.py` and `check_sources.py` all read it through
`references/build/source_catalog.py` — don't parse it anywhere else, and don't reintroduce a
second place where a location or a tier is decided. It is TOML rather than YAML because
`check_sources.py` must run from a bare `python3` with no `uv sync`, where `tomllib` is importable
and PyYAML is not. (`license_map.yml` was folded into it on 2026-09-18.)

Exits non-zero on an undocumented source or on catalog drift. Its **raw-only** list is the one to know before saying a
text is unavailable: those sources are present but not ingested by `build.py`, so `query.py` and the
MCP tools cannot see them (this is why a study once asserted Tobit wasn't in the repo while it sat in
`references/open-data/`). The Septuagint spans two works: `ebible-grcbrent` (Brenton: the Hebrew
canon and fourteen deuterocanonical books, Tobit to the Prayer of Manasseh) and `swete-lxx` (the
Odes, Psalms of Solomon and Psalm 151, which Brenton lacks). Only the *English* deuterocanon is
raw-only. External material — `study-notes.db`, patristics, TWOT scans — resolves
through **`$BIBLE_MEDIA_ROOT`** via `references/build/media_root.py`, never a hardcoded path, because
this repo is public.

`references/build/mcp_server.py` (registered via `.mcp.json`) exposes the same `query.py`/
`twot_lookup.py`/`study_notes_query.py` lookups as MCP tools — it's a thin wrapper, not a
second implementation. **Before leaning on a source, call `source_profile`.** Every work in the database carries a
profile in `references/sources.toml` — `kind`, `edition`, `era`, `purpose`, `strengths`,
`limits` — so you can find out that Young's Literal is a cross-check and never a quotation
source, or that the Delitzsch Hebrew New Testament is a 19th-century translation rather than a
Semitic original, without having read this file. The prose these were distilled from is
[docs/content/scripture/translations.md](../content/scripture/translations.md).

**Record what you verify as `evidence:` in the study's state file.** `claims:` only takes SQL
returning one number, which is why only a handful of studies ever grew one; `evidence:` takes
any tool call from `research_batch.REGISTRY` plus what its answer must contain, so a quotation's
wording, a gloss or a root number becomes re-checkable. `evidence_draft` turns lookups you have
just made into entries to paste. Replay with `verify_claims.py --evidence`. An entry whose
source is unreachable reports as **unverified**, never as failed — could-not-test and wrong are
different facts and must read differently.

**Beginning work on a passage? Call `passage_brief` first** — one call returns
versification, the book introduction, the BSB section the passage sits in and its parallel
accounts (`structure`), the text in each translation you name (open and commercial alike, each
routed to the database that holds it), the ULT and BSB interlinears, TWOT roots for the Hebrew,
cross-references, Dead Sea Scroll divergence, the translators' footnotes naming which editions read
a variant, every person and place the passage names (`names`, one entry per individual), study
notes, and the studies on this site that already treat the chapter (`existing_studies`), in the
order the develop skill works in. Its `addressing` section is always computed and flags a
reference that is numbered differently across traditions — Hebrew Joel 3:1 is English Joel
2:28, and reading one under the other raises no error.

**Gospel or a passage with a parallel? `bible_lists` and `study_esv_tags`.** STEP Bible's
curated lists (`reference_lists`, work `step-lists`): the harmony of the gospels, OT parallels, the
names of God, NT quotations of the OT, miracles, prophets and each NT letter's parts. The harmony's
pairs also sit in `parallel_passages`, so `bible_section` and `review_gaps` see them.
`study_esv_tags` is an ESV interlinear (STEP's TTESV word positions over the ESV 2016 text in
study-notes.db): which English word renders which Hebrew or Greek word, for checking, never quoting.

**For other multi-lookup work, use `research_batch_run`**: it dispatches to the same library functions over one connection per
database rather than reopening for each call (measured 9x faster across twelve
study-notes.db lookups), enforces a wall-clock budget that can actually interrupt a slow
query, and reports each request's status separately — one unreachable source never fails
the batch. An `unavailable` result says how to fix it; it is never licence to answer from
memory.

**Genealogy data** (`utils/` — stdlib-only, run from repo root):

```bash
python3 utils/validate_genealogy.py       # run after hand-editing docs/data/genealogy/*.json. Exits
                                          # non-zero only on a missing REQUIRED field; dangling
                                          # child ids, optional-field gaps and per-variant year
                                          # coverage are reported as warnings, because that
                                          # non-uniformity is legitimate content the components
                                          # must guard against rather than a data error.
python3 utils/generate_recent_updates.py  # regenerate New this month / Recently Updated (page + homepage), docs/data/published.json and the RSS feed docs/content/feed.xml from git log; runs automatically in CI, so a manual run is only needed to preview locally
python3 utils/refresh_frontmatter_provenance.py  # fill date_created/date_modified/ai_provider_models on hand-written pages from git history -- run BEFORE committing a new or revised page and stage its edit with yours (--check reports drift without writing)
```

**Deploy**: `.github/workflows/deploy.yml` runs `utils/generate_recent_updates.py`, then `npm ci`
+ `npm test` + `npm run build:tools` in `app/` (**before** the mkdocs build — `build:tools` writes
the React bundle into `docs/content/assets/js/`, which mkdocs then copies like any other asset),
then `mkdocs build --site-dir site`, and deploys to **Cloudflare Workers** (`wrangler deploy`, via
`cloudflare/wrangler-action@v3` — pinned to `wranglerVersion: '4'`, since the action's unpinned
default silently installs an old Wrangler that can't read an assets-only `wrangler.jsonc`) on push
to `main`. One build produces the whole site; there is no stitch step. This replaced a GitHub Pages
deploy in September 2026 — same domain, same build, only the last step changed. See
[docs/dev/cloudflare-migration.md](cloudflare-migration.md) for the full migration record.
It is **path-filtered to `docs/**`, `app/**`, `mkdocs.yml`, `wrangler.jsonc`, and the workflow
file** — a commit touching only `references/` or `utils/` deploys nothing. If such a change needs
to reach the live site (e.g. re-running `commentary_index.py` wrote into `docs/content/`, or you
want a fresh recent-updates page), either include the `docs/` edit in the same commit or trigger
the workflow manually (`workflow_dispatch`).

