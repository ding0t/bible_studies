# Design: mkdocs + Astro split

**Date:** 2026-07-09
**Status:** Approved
**Repo:** bible_studies (bible_end_times on GitHub Pages)

## Problem

The repo migrated from mkdocs to a custom Astro app. Astro rebuilt — and now hand-maintains — navigation, table of contents, search, and layout, all of which mkdocs-material provided for free (~half of ~5650 LOC in `src/`). The only Astro-exclusive value is two interactive React tools: the prophetic timeline and the genealogy viewer.

Two systems currently coexist in the repo: `mkdocs.yml` and a deprecated `mkdocs_ci.yml` still sit alongside the live `astro_deploy.yml`. The working tree is dirty mid-restructure. The timeline is additionally **broken**: only two study files carry temporal data (`zadok_year`/`gregorian_year`), but `timeline.astro` filters on a `year:` field no file has, and drops the zadok/gregorian fields — so it renders zero events.

## Goal

Split responsibilities so each system does what it is best at, on one GitHub Pages site:

- **mkdocs-material** owns all prose content and the site home page.
- **Astro** owns exactly two interactive tools, mounted at `/timeline/` and `/genealogy/`.

Get the repo to a clean, committed state so Bible study authoring can resume — drop a markdown file, it appears in nav.

## Non-goals

- No redesign of the timeline or genealogy UI.
- No new studies content in this work.
- No change to the marp slides pipeline (`docs/slides/`, `marp_ci.yml`) — left as-is.

## Target end state

- One Pages site, one URL: `https://gh-ding0t.github.io/bible_end_times/`
- Home page and all prose served by mkdocs at the site root.
- Timeline and genealogy served by Astro at `/timeline/` and `/genealogy/`.
- One deploy workflow builds both and stitches the output.

```
gh-ding0t.github.io/bible_end_times/
  /                <- mkdocs home (index.md)
  /studies/...     <- mkdocs prose
  /bible/...       <- mkdocs prose
  /timeline/       <- Astro app
  /genealogy/      <- Astro app
```

## Repo layout (target)

```
docs/
  content/          # markdown — mkdocs docs_dir (Astro content collection retired)
  data/
    genealogy.json  # already standalone, consumed by GenealogyViewer
    events.json     # GENERATED from content frontmatter
  slides/           # marp, untouched
  superpowers/specs/
app/                # Astro sub-app, moved out of repo-root src/
  src/
    components/     # TimelineComponent, GenealogyViewer + their deps
    pages/          # timeline.astro, genealogy.astro (only these two)
    utils/          # calendarConvert, bibleReference (+ tests), accessibility
    styles/colors.js
    layouts/BaseLayout.astro
  astro.config.mjs  # base: '/bible_end_times'
  package.json
scripts/
  build-events.js   # scan docs/content frontmatter -> docs/data/events.json
mkdocs.yml
.github/workflows/
  deploy.yml        # replaces astro_deploy.yml + mkdocs_ci.yml
  marp_ci.yml       # kept
```

Note: Astro moves from repo-root `src/` into `app/`. This isolates the sub-app so mkdocs config at the repo root is unambiguous and the two build systems do not share a `src/`.

## Components

### mkdocs content site

- `docs_dir` = `docs/content`.
- Home page: `docs/content/home.md` (or `index.md`) becomes the site root landing — prose plus links to `/timeline/` and `/genealogy/`.
- Navigation: **mkdocs-awesome-pages-plugin** builds nav automatically from the directory tree, so adding a study file requires no nav edit. Added as a global uv tool (`uv tool install` alongside mkdocs-material, matching the workspace `uvx mkdocs` convention).
- `mkdocs.yml` cleaned up: real `site_url`, `repo_url`, theme, plugins (search, awesome-pages). Remove commented-out legacy nav.
- Retire the Astro-era `_category.json` files (they encoded nav for Astro, not mkdocs).

### Events generator — `scripts/build-events.js`

- **What it does:** produces the timeline's data file from study frontmatter, keeping a single source of truth in the markdown.
- **Input:** `docs/content/**/*.md`.
- **Dependency:** `gray-matter` for frontmatter parsing (one dependency; do not hand-roll YAML).
- **Filter:** keep files with `zadok_year` OR `gregorian_year` present.
- **Output:** `docs/data/events.json` — an array of:
  ```json
  {
    "slug": "prophecy-fulfilled-in-jesus/woman-suffering-bleeding",
    "title": "...",
    "description": "...",
    "tags": ["..."],
    "category": "prophecy-fulfilled-in-jesus",
    "zadok_year": 3988,
    "gregorian_year": 32,
    "url": "/bible_end_times/studies/prophecy-fulfilled-in-jesus/woman-suffering-bleeding/"
  }
  ```
  - `category` derived from the top study subdirectory.
  - `url` points at the mkdocs page for that study, so clicking a timeline event opens the study. The URL base prefix (`/bible_end_times`) is a constant in the script.
- **Interface:** `node scripts/build-events.js`; also an `npm run build:events` script; runs in CI before the Astro build.
- **Testing:** unit test against a small fixture directory — asserts a known set of markdown files produces the expected `events.json`. This is real business logic (frontmatter parsing, filtering, URL derivation) and is worth testing.

### Astro app — `app/`

- Two pages only: `timeline.astro`, `genealogy.astro`.
- `timeline.astro` reads `docs/data/events.json` (import at build time) instead of `getCollection('studies')`, and passes `zadok_year` + `gregorian_year` through to `TimelineComponent` so the dual-calendar view works. This fixes the current empty-timeline bug.
- `genealogy.astro` unchanged in behavior — already reads `docs/data/genealogy.json`.
- `astro.config.mjs`: `site: 'https://gh-ding0t.github.io'`, `base: '/bible_end_times'`. Pages emit to `/bible_end_times/timeline/` and `/bible_end_times/genealogy/`.
- `BaseLayout.astro` kept as the shell for the two pages; the duplicate `BaseLayout.jsx` is deleted.

### Deploy workflow — `deploy.yml`

Single job:

1. `uvx mkdocs build` → `site/`
2. `npm ci` in `app/`
3. `node scripts/build-events.js` → `docs/data/events.json`
4. `cd app && npm run build` (base `/bible_end_times`) → `app/dist/{timeline,genealogy,_astro,...}`
5. copy `app/dist/*` into `site/`
6. upload `site/` to Pages, deploy

Path safety: mkdocs must own no `/timeline` or `/genealogy` page, so the copy in step 5 does not collide. Trigger on push to `main`/`master` touching `docs/**`, `app/**`, `mkdocs.yml`, `scripts/**`, or the workflow itself.

## Data flow

```
study .md (zadok_year/gregorian_year in frontmatter)
   |
   |-- mkdocs build --------------------> site/studies/.../  (the readable study page)
   |
   '-- build-events.js --> events.json --> Astro timeline --> site/timeline/
                                                                  |
                          click event --> url --> back to the mkdocs study page
genealogy.json --> Astro genealogy --> site/genealogy/
```

## What gets deleted (enabled by the split)

- `src/content/config.ts` (content collection)
- `src/pages/index.astro`, `src/pages/bible.astro`, `src/pages/studies.astro`
- `src/pages/studies/[...slug].astro`, `src/pages/[...slug].astro`
- `src/components/SearchComponent.jsx` (mkdocs-material search replaces it)
- `src/components/StudySidebar.astro`, `src/components/TableOfContents.astro` (mkdocs nav/TOC)
- `src/utils/contentTree.js`, `src/utils/categoryLabels.js`
- `src/layouts/BaseLayout.jsx` (duplicate of `.astro`)
- all `docs/content/**/_category.json`
- `.github/workflows/mkdocs_ci.yml` (deprecated; superseded by `deploy.yml`)

**Kept:** `TimelineComponent.jsx`, `GenealogyViewer.jsx`, `BibleReference.jsx`, `ErrorBoundary.jsx`, `calendarConvert.js` (+test), `bibleReference.js` (+test), `accessibility.js`, `colors.js`, `BaseLayout.astro`.

## Early cleanup (Phase 0 — before split work)

The repo is mid-restructure and must not be evaluated or branched from while dirty.

1. Get to a known-good committed baseline: review the in-flight staged + unstaged moves/deletes, commit (or stash) them so `git status` is clean.
2. Confirm the 66 deleted `docs/bible/templates/*.md` files are an intentional deletion; commit it.
3. Delete the duplicate `src/layouts/BaseLayout.jsx`.

## Phasing

- **P0 — Cleanup:** commit the in-flight restructure, confirm template deletions, remove dup `BaseLayout.jsx`. Clean `git status`.
- **P1 — Stand up mkdocs:** set `docs_dir`, add awesome-pages, write `mkdocs.yml`, create `docs/content/home.md`, build locally with `uvx mkdocs build`, verify nav and pages.
- **P2 — Timeline data + Astro move:** write `scripts/build-events.js` + its test, move Astro `src/` → `app/`, set `base`, rewire `timeline.astro` to `events.json` with dual-calendar pass-through, build `app/` locally and verify subpaths.
- **P3 — Unified deploy:** write `deploy.yml`, remove `astro_deploy.yml` + `mkdocs_ci.yml`, deploy, verify `/`, `/studies/...`, `/timeline/`, `/genealogy/` live.
- **P4 — Delete retired code:** remove the files in "What gets deleted", confirm builds still pass.

## Testing

- Keep `calendarConvert.test.js` and `bibleReference.test.js` (moved with the utils into `app/`).
- Add `scripts/build-events.test` (fixture → expected `events.json`).
- Manual verification each phase: local `uvx mkdocs build` and `npm run build`, then the live Pages URLs after P3.

## Risks / open points

- **awesome-pages as a global uv tool:** if installing it globally proves awkward, fall back to an explicit `nav:` in `mkdocs.yml` (more maintenance, but no plugin). Decide during P1.
- **Astro `base` and cross-links:** timeline/genealogy links back to mkdocs pages must use the `/bible_end_times` prefix; centralize the prefix as one constant in `build-events.js` and in the Astro config to avoid drift.
- **Frontmatter coverage:** only two studies currently have dates. The timeline will be sparse until more studies gain `zadok_year`/`gregorian_year`. This is expected and is authoring work, not a split defect.
