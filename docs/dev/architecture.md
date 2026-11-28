# Architecture

How the site is built and why, moved out of `AGENTS.md` on 2026-11-15 so the standing brief stays
short. `AGENTS.md` keeps the rules that break things if forgotten.

## Tech stack

- Environment: primary dev platform is macOS (previously Windows 11 + WSL2 — may still see references to that in older notes).
- Markup language: markdown
- Site generator: **mkdocs-material** serves all prose content (`docs/content/`, `docs_dir` in
  `mkdocs.yml`), the site home page, and **the interactive tools**. The Prophetic Timeline
  (`docs/content/timeline.md`) is an ordinary mkdocs page with a React bundle mounted into a
  `<div>`, so it inherits the site's sidebar, search, breadcrumbs and palette toggle. Since
  2026-10-01 it also carries the genealogy (a row per person, a person panel, a family-tree view);
  the separate Genealogy Viewer is gone and `/genealogy/` redirects to `/timeline/#view=family`.
  **Astro is gone** — there is one site build. `app/` is now just the React components
  (`app/src/components/chronology/` for the timeline), their utils, the build scripts and the tests;
  esbuild bundles the four entry points in `app/src/entries/` (the timeline, the Scripture Links
  explorer, the site-wide verse and word pop-ups, and the Hebrew word cards' on-screen practice)
  into `docs/content/assets/js/`.
- **One set of chronology facts.** `docs/data/chronology.json` holds every dated event once (anchor
  table, Genesis markers, milestones, the AD 33 sequence, life events), each tagged with the people
  it involves; the genealogy era files hold people, each storing ONE calendar (`zadok_year_*` for
  Genesis-dated people, `gregorian_year_*` from Salmon on). `app/src/utils/chronology.js`
  (`loadEvents`, `eventsForPerson`, `loadGenealogyPeople`) derives the other calendar and each
  person's events, and the epoch is set only in `chronology.json`. `utils/validate_genealogy.py`
  and `app/src/utils/chronology.test.js` fail on a duplicated calendar, an event list back in an
  era file, a lifespan that disagrees with its dates, or a timeline row that disagrees with
  Chronology Anchors. **Every verse a date rests on is in `docs/data/dating-texts.json`**: the
  BSB wording that states its number (`tests/test_dating_texts.py` checks it against the text),
  the site's reading, the events it dates and the intervals that reading implies, which
  `chronology.test.js` checks against the dates. It also fails on an event citing Scripture that no
  entry dates. Add the entry with the event. A known disagreement is a `tension`, reported rather
  than failed.
- **The site is served from `the-way.lewy.au` at its root** — a Cloudflare Workers Custom Domain,
  not `github.io/bible_studies` (stale and orphaned since the September 2026 migration; no longer
  built, no longer the custom domain, no longer even resolving there). Site-absolute URLs therefore
  carry no repo prefix. Getting this wrong is not cosmetic: it 404s the tools' JS bundles and kills
  them silently.

## Architecture

- **One site build.** esbuild writes both tool bundles into `docs/content/assets/js/` before the
  mkdocs build, so mkdocs treats them as ordinary assets and a single pass produces every page.
  This replaced a two-project split (mkdocs + Astro, stitched at deploy time) that let the halves
  disagree about the site root and silently 404 every tool asset in 2026-08. Keep it that way: a
  second build system is how that class of bug comes back.
- **The site is readable by AI assistants, and the gospel comes first.** `hooks/llms.py` writes
  `llms.txt` (opening with the home page's gospel section), a markdown copy of every page at its URL
  plus `index.md`, the FAQ's question list from each study's `questions:` frontmatter, and the study
  skills at `/skills/`. The **public connector** is an MCP server at `/mcp` (Streamable HTTP,
  stateless, read-only): `app/src/connector/`, bundled by `npm run build:worker` into
  `app/dist/worker.js`, the site Worker's `main`, which `wrangler.jsonc` runs only for `/mcp`. It
  reads the site's own built files through the ASSETS binding: `assets/lang/` from
  `export_connector.py`, the pop-up data, `assets/studies-index.json` and `assets/gospel.json` from
  the hook, `assets/search/` (the site search's index re-cut by the hook into per-word files, so
  `search_studies` reads the full text of every section a few words at a time), and the chronology bundled from `app/src/utils/chronology.js`. So it is never staler
  than the deploy, except the language data, which changes only when re-exported and published.
  `npm run test:connector` (CONNECTOR_SITE=<built site>) runs in CI after the mkdocs build. Serve
  open-tier data and the CC BY-NC scrolls only; study-notes.db and TWOT never leave this machine.
  [For AI Assistants](../content/about/for-ai-assistants.md) is the human-readable side.
- **Every Bible reference and Strong's tag on a page pops up.** `app/src/entries/popups.js`, loaded
  site-wide through `extra_javascript`, scans the rendered page (not the markdown) with
  `app/src/utils/scriptureRefs.js` and opens a card: the verse (WEB), its context, OpenBible
  cross-references and the studies that treat it; or, for a word, its lexicon entry, counts, every
  place a rare word occurs, and the studies that discuss it. So **references are written as plain
  text and never linked** — a link hides a reference from the scanner. Blue Letter Bible links were
  removed site-wide on 2026-09-27; keep one only as a deliberate send-off for follow-up study.
  The pop-up works alongside the prose, never instead of it. Quote what the argument stands on,
  since studies are read aloud and the pop-up shows the site's reading translation (the BSB,
  set once in `references/sources.toml` `[reading_translation]`), and cite what it only points to
  (develop-bible-study formatting.md).
  **Every reference names its book** except a continuation in the same citation ("(Revelation 21:2,
  9; 22:17)"). The pop-up resolves an older bare "(5:1)" from the paragraph, a table's column header,
  the quotation, the heading, then the page's `primary_passage` (which `hooks/popups.py` writes onto
  the page), but an edit that moves the reference before it repoints it silently. A
  Strong's tag also opens from the word in front of it and from that word's later mentions.
  Every other Greek or Hebrew word on the page, inflected forms and quoted sentences included,
  opens through the form index (`assets/popups/forms/`, every form in OSHB, MACULA Greek and the
  LXX lemmas mapped to its number). A form that belongs to two words links only when the page has
  tagged one of them, so an explicit tag always decides. Hebrew in running text is set in Noto
  Serif Hebrew at 1.2em (`hebrew.css`), and the script gives Hebrew and Greek words a `lang` so a
  screen reader voices them in the right language.
  A verse card switches between the reading translation, the Hebrew or Greek the BSB translates
  (the Berean Interlinear's text, table `interlinear_words`), the same word by word with a
  transliteration and the BSB's English under each word, and Brenton's Septuagint (OT) or
  Salkinson-Ginsburg's 1886 Hebrew (NT, labelled a translation); the reader's choice is remembered.
  In the BSB view each English word opens the word it renders, and a NT verse that quotes the
  Septuagint shows it with the shared words marked. Data: `assets/popups/original/<Book>/<c>.json`,
  in the BSB's numbering; every word opens its card with that occurrence's own parsing (MACULA).
  `data-ref="…"` and `data-strongs="…"` spans mark what the text cannot say on its own. The data is
  in two halves by where it can be built: `references/build/export_popups.py` writes the Bible
  text, cross-references and lexicon from `bible-text.db` into `docs/content/assets/popups/`
  (committed, since CI cannot rebuild the database; open-tier sources only, because it ships to the
  browser), and `hooks/popups.py` writes the study index from frontmatter and page text on every
  build, after `draft_pages.py`, so a draft never appears in a pop-up. Word counts match on the
  exact Strong's id, as `bible_concordance` does, so a pop-up agrees with the count a study was
  checked against. A word opened from a form on the page also gets that form's grammar in plain
  English (`parse/` + `grammar.json`, STEP's TEGMC/TEHMC), and a name gets who it is (TIPNR's
  individuals, family, and a link into the family tree where `genealogy_check.py` matches one) and
  its other testament's spelling (Jesse: H3448 in the OT, G2421 in the NT).
- **Content frontmatter is the integration point.** `app/scripts/build-events.js` reads
  `docs/content/**/*.md` frontmatter (as the first half of `build:tools`) to generate
  `docs/data/events.json`, which the timeline bundle imports at build time. `references/build/commentary_index.py` and `section_index.py` also read it to
  regenerate auto-sections of *other* committed markdown files, bounded by
  `<!-- *-index:auto-start/end -->` markers — hand-written prose outside those markers is preserved,
  so it's safe to re-run them after editing content.
- **`draft: true` is enforced by `hooks/draft_pages.py`, not by mkdocs.** MkDocs has no native
  draft support for ordinary pages (mkdocs-material's is blog-plugin only, and this site has no
  blog), so for a long time the flag was honoured *only* by this repo's own scripts —
  `section_index.py`, `commentary_index.py` and `generate_recent_updates.py` all hid drafts from
  their generated lists, while mkdocs went on building, publishing, nav-linking and search-indexing
  the page itself. Drafts therefore looked unpublished while being fully reachable; three were live
  on `the-way.lewy.au` that way before it was spotted (2026-09-01). The hook drops draft pages at
  `on_files` during `mkdocs build`/`gh-deploy` and keeps them under `mkdocs serve`, so local preview
  still works. Two consequences: a published page that links to a draft **builds clean under
  `mkdocs build --strict` and ships a dead link** — the draft is dropped, no warning is raised, and
  the link renders as a raw `href="<draft>.md"` that 404s on the live site (verified 2026-10-03 with
  `end-of-the-age.md`). Nothing catches it, so never link a draft from a published page: commit the
  linking edits in the same commit that flips the draft to `draft: false`. And a draft `index.md`
  takes its directory's landing page down with it, so finish a section index rather than drafting
  it. `build-events.js` still does **not** filter drafts, so a
  `draft: true` study with `gregorian_year` frontmatter can still plant a timeline entry.
- **Two SQLite pipelines under `references/`, deliberately isolated by trust tier**:
  `bible-text.db` (open/restricted-nc sources; gitignored but built *inside* the repo tree) vs.
  `study-notes.db` (commercial study-Bible commentary, `quotation-only`; built entirely *outside*
  the repo tree, on an external volume). Both are queried through the same `lookup_*` function
  pattern that `mcp_server.py` re-exposes — see [references/README.md](../../references/README.md) before
  adding a new source or query.
- **`references/open-data/` vs `references/restricted-data/` submodules partition by license
  tier** — the directory a source lives in *is* the license audit boundary; never move a source
  between them.
- **Four content skills:** new content goes through **develop-bible-study**
  (`.claude/skills/develop-bible-study/SKILL.md`), which tracks resumable per-study progress in
  `references/study-state/<slug>.yml`; an already-drafted or already-published file goes through
  **review-bible-study** (`.claude/skills/review-bible-study/SKILL.md`), which re-verifies quotes,
  citations, and word studies against source. Reach for review, not develop, when the ask is
  "audit / fact-check / critique" rather than "write". A third, **read-bible-study**
  (`.claude/skills/read-bible-study/SKILL.md`), answers the question neither of those does —
  *can it be read?* It restructures an existing file (headings, grouping, placement) under one
  governing rule, **change no sentence**, which is why its output needs no re-verification and
  why it cannot live inside review, whose whole job is to change what is wrong. Run it last, and
  in a different session from the one that drafted the file: judging your own composition order
  as a reader is the one thing the author cannot do. A fourth, **simplify-bible-study**
  (`.claude/skills/simplify-bible-study/SKILL.md`), shrinks a study under the rule **add
  nothing**: it names what the study is trying to say, maps every section against that, and
  recommends forking tangents into new studies, merging repeated points and tightening wordy
  passages, then applies what the author approves. It exists because every other pass adds words
  (`bride-of-christ.md` went from 4,362 to 14,393 in three weeks). Validator Check 23 warns when a
  study passes its `word_budget` (state file, default 4,000). The four answer *build it / is it
  true? / can it be read? / is it the right size?*
- **One-minute comics** (`.claude/skills/one-minute-comic/SKILL.md`) tell a study's point in three to
  six panels. A comic is data, `docs/data/comics/<slug>.toml`, drawn by `utils/build_comics.py` from
  the reusable cast, poses, scenes and layouts in `utils/lib/comic.py`; every bubble is the ESV's
  wording or marked "condensed" from the verses its panel names.
- **Youth pages** (`.claude/skills/youth-bible-study/SKILL.md`) cut a published study down for
  readers aged 8 to 16, under the rule **say nothing the study does not**. A youth page is data,
  `docs/data/youth/<slug>.toml`, which `hooks/youth.py` writes onto `docs/content/youth/<slug>.md`
  in a fixed shape (big idea, a four-panel comic with a phone layout, a tab per age band, a key
  word, a memory verse, a prayer). The full study is the leader's notes, and the page links to it.
- **Every study with a point and discussion questions gets a printable group sheet**
  (`hooks/study_sheet.py`): four A4 pages at 12 pt, two sheets double-sided, for a 40-minute
  group, in a collapsed block under the questions (a printer icon by the title jumps to it). It is assembled from the rendered study (the `**In one sentence:**`
  thesis, `primary_passage` in the reading translation, the first comic or drawn SVG, the Study outline, the
  questions, Be Transformed, the first memory verse, the prayer), so it says nothing the study
  does not. The sheet is the group's; **the study itself is the leader's notes** — one set of
  notes per study, with no separate leader's guide to drift from it. **The questions sit under the Study outline's steps** (the step whose section cites the
  same verses), and **the facet labels mark Be transformed**, which closes the sheet, and place the
  rest on the clock when a study has no outline (language and context → Discover, Christ and the
  hard part → Wrestle): two more reasons a study should carry an outline and its question set
  facet labels (Checks 22, 25). A **Two pages** option pours Open, the passage, each step with its
  questions, Be transformed and the point across one double-sided sheet. A study needs no change to get a sheet; a
  weak sheet is a sign of a missing thesis, outline or facet label. See
  [docs/dev/study-sheets.md](study-sheets.md).
- **Every study with a state file gets a "How this study was checked" panel**
  (`hooks/study_checks.py`), collapsed, before its References. It shows only what
  `references/study-state/<slug>.yml` records: dated review, read and simplify passes, the
  corrections and author questions the reviews list, and every `evidence:` entry by kind and in
  full. The build has no Bible databases, so nothing is replayed and the panel never says
  "verified". **Recording evidence and dating each pass's block is what the reader sees**, so a
  check left out of the state file is a check the page does not show.
- **A study series is a page with a `series:` frontmatter block** (`hooks/series.py`), listing
  studies from any section in the order a group takes them, one a week. A study keeps its one home
  in the taxonomy and only gets pointed at, so it can sit in several series; never move or copy a
  study into `series/`. The hook writes the weeks, the hub at `/series/` grouped by `cut`, and a
  "Week 2 of 7" line on each member study. A `planned` week, or a draft study, shows as *coming*
  and is never linked, which keeps Check 24's rule for links a hook writes. A series' `why` lines
  are descriptive; whether a series is worth running is the author's call. Field reference:
  [docs/CONTENT_GUIDE.md](../CONTENT_GUIDE.md#series).
- **The prophecies of Christ are a ledger rendered as a page** (`hooks/prophecies.py`), under
  Explore at `prophecies-of-christ.md`; the study that argues from it is
  `jesus/foretold-long-ago.md`.
  `docs/data/prophecies-of-christ.toml` is the authority; `references/build/export_prophecies.py`
  computes what needs the Bible databases or the dating tables (years written on both schemes,
  the year fulfilled, the Qumran copies) into `prophecies-of-christ.json`, and
  `utils/check_prophecies.py` fails `npm test` while that file is stale, so no count on
  either page is typed by hand. Markers on the ledger page place the measures table, each
  category's cards (`id="prophecy-<id>"`) and the New Testament's own predictions. A card leads
  with its takeaway (`predicts` beside `came_to_pass`, the years between on the arrow, and
  `still_to_come` beneath), then a labelled rule and the evidence. A ledger
  note's research leads ("lead:" on) are left off the page. The study is week 1 and the hub of the
  Prophecy and Jesus series (a `series:` block), and the charts are drawn from the same two files
  by `utils/build_jesus_graphics.py`. The same hook writes the ledger's explorer (three plates drawn
  at build time: a Sankey from Luke 24:44's Law, Prophets and Psalms through each subject to the New
  Testament book; a wheel of subjects; a grid of who brought each about against whether it was read
  beforehand), its filter bar (behaviour for both in `app/src/entries/prophecy-filter.js`, where each
  mark in a plate is a choice and the plates dim to the cards left showing, and each fact on a card is a choice too, through the same facet:value pairs (`_pivot`)) and the study's chance
  floor (its moments link to the
  ledger's cards), adds "Prophecies of Christ" to each
  generated commentary chapter page, and writes `assets/popups/prophecies.json`, which the verse
  pop-up reads to say a verse is a prophecy of Christ or a New Testament use of one.
- **An exemption in a checking tool carries its justification with it, or it is a hole.** Two of this
  repo's checks were defeated by an unrecorded exemption rather than by a missing check. The diagram
  sweep skipped `timeline` blocks because they "size themselves" — they do not, and five stayed
  unreadable through the pass built to catch exactly that. The `notes` table was empty in every
  build for months because nothing asserted a declared table has rows. So: `MAY_BE_EMPTY` in
  `references/build/tests/test_invariants.py` is a dict, not a set, and the value is the reason;
  a skipped case in `validate-content.js` gets a comment saying why. A reader who cannot see the
  reason cannot tell an exemption from an oversight, and neither can the next sweep.
- **`references/biblefacts/` is raw, unvetted input** — transcripts and notes captured from
  third-party teaching (currently Dead Sea Scrolls material). It is not part of either SQLite
  pipeline and is not covered by `references/README.md`'s license tiers. Treat it as a lead to
  chase down in a primary source, never as a citable reference in a study.
- **`utils/generate_recent_updates.py` derives "recently updated" purely from git log** (no
  hand-maintained date frontmatter field) and writes into four marker pairs: "New this month" and
  "Recently updated" on `docs/content/about/recent-updates.md`, and a teaser of each on the homepage
  (`docs/content/index.md`). It runs automatically in CI right before `mkdocs build`, so the page
  is fresh on every deploy without anyone needing to remember to regenerate it — unlike
  `commentary_index.py`/`section_index.py`, which are manual, this one isn't. **"New" means first
  published**: the commit that set `draft: false` (or the first commit, if the page was never a
  draft), never `date_created`, which would date a study drafted for weeks from its first draft.
  It also writes those dates to `docs/data/published.json` (committed), and `hooks/new_pages.py`
  reads that file to put a "New" line under a new page's title and material's `status: new` icon
  beside it in the nav, for the same 30-day window. The hook reads the file, never git, so
  `mkdocs serve` stays fast; run the script to refresh the badges locally.
- **`utils/refresh_frontmatter_provenance.py` is the other git-derived writer**, and unlike
  `generate_recent_updates.py` it is *manual* — it writes into the frontmatter of the ~168
  hand-written pages (`date_created`, `date_modified`, `ai_provider_models`), so running it in CI
  would mean CI rewriting committed source. `validate-content.js` check 17 closes the gap instead,
  warning when a page's `date_modified` has fallen behind its last commit. Scope is defined by the
  absence of `commentary-index:auto-start`: the ~789 generated cross-reference pages (724 of them
  `commentaries/<book>/chapter-NNN.md`, which `docs/overrides/` marks `noindex` and leaves out of
  `sitemap.xml`) are exempt,
  since a provenance record on a file a script writes on demand records the script run, not
  authorship. **It runs before a commit, not after** — a dirty file gets today's date, so staging
  its edit with the content edit makes the two agree; run after committing and it can never
  converge, because writing the dates is itself a change to every page.

## Standards

- Use UTF-8 encoding in scripts