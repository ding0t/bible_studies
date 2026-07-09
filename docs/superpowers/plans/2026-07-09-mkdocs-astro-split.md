# mkdocs + Astro Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the site so mkdocs-material serves all prose + the home page, while a slimmed Astro app serves only the interactive timeline and genealogy tools, all on one GitHub Pages site.

**Architecture:** mkdocs builds `docs/content/` to the site root. A build script scans study frontmatter into `docs/data/events.json`. Astro (moved to `app/`, base `/bible_end_times`) builds only `timeline.astro` + `genealogy.astro`; its `dist/` is copied over the mkdocs `site/`. One workflow builds and stitches both.

**Tech Stack:** mkdocs-material + mkdocs-awesome-pages-plugin (via `uvx`/global uv tool), Astro 5 + React 18 (npm, in `app/`), Node script with `gray-matter`, GitHub Actions.

## Global Constraints

- **Do not lose studies.** The 42 markdown files under `docs/content/` are the product. No task deletes, moves, or rewrites study prose. mkdocs points at them in place. Any deletion step touches only Astro plumbing, empty template stubs, or config.
- Astro base path is exactly `/bible_end_times` (matches Pages repo `bible_end_times`).
- Python tooling via `uvx mkdocs` / global uv tools — no per-repo Python venv (workspace convention).
- Node tooling via `npm`, all under `app/`.
- Conventional Commits; subject < 72 chars. Commit trailers as configured for this session.
- Frontmatter date fields are `zadok_year` and `gregorian_year` (numbers). There is no `year:` field.

---

### Task 0.1: Establish a clean, studies-safe baseline

**Files:**
- Modify: working tree (commit in-flight restructure)
- Delete: `src/layouts/BaseLayout.jsx`

**Interfaces:**
- Produces: a clean `git status` on `main` to branch/build from.

- [ ] **Step 1: Snapshot what is uncommitted**

Run:
```bash
git status --short > /tmp/split-status-before.txt
git diff --stat
```
Read the output. Confirm the changes are the content restructure already in progress (moves under `docs/content/`, new `src/` nav helpers), not accidental edits.

- [ ] **Step 2: Prove no study prose is being lost to deletions**

Run:
```bash
git status --short | grep '^ D\|^D ' | grep '\.md$'
```
Expected: only `docs/bible/templates/*.md` (empty book-stub scaffolds), `docs/content/meta/*.md`, and `docs/bible/*.md` (old duplicates now living under `docs/content/`). For any deleted path you do not recognize, run `git show HEAD:<path> | head -40` and confirm it is a stub/duplicate, not unique study content. **Stop and ask the user if any deleted file contains real study prose not present elsewhere.**

- [ ] **Step 3: Remove the duplicate layout**

Run:
```bash
git rm src/layouts/BaseLayout.jsx
```
Expected: `BaseLayout.jsx` deleted; `BaseLayout.astro` remains.

- [ ] **Step 4: Commit the baseline**

```bash
git add -A
git commit -m "chore: commit in-flight content restructure, drop duplicate layout"
```

- [ ] **Step 5: Verify clean tree**

Run: `git status --short`
Expected: empty output (clean working tree).

---

### Task 1.1: Stand up mkdocs on the existing content

**Files:**
- Modify: `mkdocs.yml`
- Create: `docs/content/home.md`

**Interfaces:**
- Produces: `uvx mkdocs build` emitting a `site/` with home + all study nav, no reference to Astro.

- [ ] **Step 1: Install the auto-nav plugin as a global uv tool**

Run:
```bash
uv tool install mkdocs-material --with mkdocs-awesome-pages-plugin
```
(If mkdocs-material is already a global tool, re-run to add the `--with` plugin.)
Expected: install succeeds; `uvx mkdocs --version` works.

- [ ] **Step 2: Rewrite `mkdocs.yml` to point at the content dir and auto-build nav**

Replace the top of `mkdocs.yml` (lines 1-33, through the `plugins:` block) with:
```yaml
site_name: Biblical Studies by ding0t
site_url: 'https://gh-ding0t.github.io/bible_end_times/'
repo_url: 'https://github.com/ding0t/bible_end_times'
docs_dir: docs/content

theme:
  name: material
  palette:
    scheme: default
    primary: blue
  features:
    - search.suggest
    - search.highlight
    - toc.follow
    - navigation.tracking
    - navigation.path
    - navigation.prune
    - navigation.top

plugins:
  - search
  - awesome-pages
```
Leave the existing `markdown_extensions:` block (tables, admonition, pymdownx.*, emoji) unchanged. Note: the `tags` plugin is removed (it required a `tags.md` page that was deleted); re-add later only if a tags index page is wanted.

- [ ] **Step 3: Create the home page that links to the interactive tools**

Create `docs/content/home.md`:
```markdown
---
title: Biblical Studies
---

# Biblical Studies by ding0t

Interactive exploration of Scripture and prophecy.

## Explore

- **[Prophetic Timeline](timeline/)** — key events across biblical history in both Gregorian and Zadok calendars.
- **[Genealogy Viewer](genealogy/)** — trace the lineage from Adam through Jesus.

## Studies

Browse the studies in the navigation, covering prophecy, feasts, theology, spiritual disciplines, and more.
```
Note: `home.md` is excluded from the Astro glob (`!home.md` in `src/content/config.ts`) — it is mkdocs-only, which is correct. Ensure mkdocs treats it as the landing page by making it the first nav item (awesome-pages honours a `nav:` order file if present; default is alphabetical). If home must be root `index`, rename to `docs/content/index.md` instead and adjust the link targets to `timeline/` and `genealogy/` unchanged.

- [ ] **Step 4: Build locally and verify**

Run:
```bash
uvx mkdocs build --strict 2>&1 | tail -30
```
Expected: build succeeds (warnings about the two `/timeline/` `/genealogy/` links resolving outside mkdocs are acceptable — those are served by Astro; if `--strict` fails only on those, drop `--strict` for this build). Confirm `site/index.html` exists and `site/studies/` contains the study pages.

- [ ] **Step 5: Spot-check a study renders**

Run:
```bash
ls site/studies/prophecy-fulfilled-in-jesus/woman-suffering-bleeding/
```
Expected: an `index.html` exists — the study survived and renders under mkdocs.

- [ ] **Step 6: Commit**

```bash
git add mkdocs.yml docs/content/home.md
git commit -m "feat(mkdocs): serve docs/content with auto nav and home page"
```

---

### Task 2.1: Events generator (TDD)

**Files:**
- Create: `app/scripts/build-events.js`
- Create: `app/scripts/build-events.test.js`
- Create fixtures: `app/scripts/__fixtures__/content/studies/prophecy/dated.md`, `app/scripts/__fixtures__/content/studies/prophecy/undated.md`
- Modify: `app/package.json` (add `gray-matter`, scripts) — created/moved in Task 2.2; if doing 2.1 first, add these to the current root `package.json` and they move with it.

**Interfaces:**
- Produces: `generateEvents(contentDir: string, base: string) => Event[]` where
  `Event = { slug, title, description, tags, category, zadok_year, gregorian_year, url }`.
  Exported from `app/scripts/build-events.js`. CLI entry writes the array to `docs/data/events.json`.

- [ ] **Step 1: Add the frontmatter parser dependency**

Run (from the directory holding the Astro `package.json`):
```bash
npm install gray-matter
```
Expected: `gray-matter` added to dependencies.

- [ ] **Step 2: Create fixtures**

Create `app/scripts/__fixtures__/content/studies/prophecy/dated.md`:
```markdown
---
title: "Dated Study"
description: "A study with dates"
tags: ["a", "b"]
zadok_year: 3988
gregorian_year: 32
---
Body text.
```
Create `app/scripts/__fixtures__/content/studies/prophecy/undated.md`:
```markdown
---
title: "Undated Study"
description: "No dates here"
tags: []
---
Body text.
```

- [ ] **Step 3: Write the failing test**

Create `app/scripts/build-events.test.js`:
```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { generateEvents } from './build-events.js';

const fixtureDir = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '__fixtures__/content'
);

test('includes only files with a year field', () => {
  const events = generateEvents(fixtureDir, '/bible_end_times');
  assert.equal(events.length, 1);
  assert.equal(events[0].title, 'Dated Study');
});

test('maps frontmatter and derives category, slug, url', () => {
  const [e] = generateEvents(fixtureDir, '/bible_end_times');
  assert.equal(e.slug, 'studies/prophecy/dated');
  assert.equal(e.category, 'prophecy');
  assert.equal(e.zadok_year, 3988);
  assert.equal(e.gregorian_year, 32);
  assert.deepEqual(e.tags, ['a', 'b']);
  assert.equal(e.url, '/bible_end_times/studies/prophecy/dated/');
});
```

- [ ] **Step 4: Run the test, verify it fails**

Run: `node --test app/scripts/build-events.test.js`
Expected: FAIL — `Cannot find module './build-events.js'` or `generateEvents is not a function`.

- [ ] **Step 5: Implement the generator**

Create `app/scripts/build-events.js`:
```javascript
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

export function generateEvents(contentDir, base) {
  return walk(contentDir)
    .map((file) => {
      const { data } = matter(fs.readFileSync(file, 'utf8'));
      if (data.zadok_year == null && data.gregorian_year == null) return null;
      const rel = path
        .relative(contentDir, file)
        .replace(/\\/g, '/')
        .replace(/\.md$/, '');
      return {
        slug: rel,
        title: data.title ?? 'Untitled Study',
        description: data.description ?? '',
        tags: data.tags ?? [],
        category: path.basename(path.dirname(rel)),
        zadok_year: data.zadok_year ?? null,
        gregorian_year: data.gregorian_year ?? null,
        url: `${base}/${rel}/`,
      };
    })
    .filter(Boolean)
    .sort((a, b) => (a.gregorian_year ?? 0) - (b.gregorian_year ?? 0));
}

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const contentDir = path.join(repoRoot, 'docs/content');
  const outFile = path.join(repoRoot, 'docs/data/events.json');
  const events = generateEvents(contentDir, '/bible_end_times');
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify(events, null, 2) + '\n');
  console.log(`Wrote ${events.length} events to ${outFile}`);
}
```

- [ ] **Step 6: Run the test, verify it passes**

Run: `node --test app/scripts/build-events.test.js`
Expected: PASS (2 tests).

- [ ] **Step 7: Generate the real events file and eyeball it**

Run:
```bash
node app/scripts/build-events.js
cat docs/data/events.json
```
Expected: 2 events (the two dated studies), each with `zadok_year`, `gregorian_year`, and a `url` under `/bible_end_times/studies/prophecy-fulfilled-in-jesus/...`.

- [ ] **Step 8: Commit**

```bash
git add app/scripts docs/data/events.json package.json package-lock.json
git commit -m "feat(timeline): generate events.json from study frontmatter"
```
(Paths adjust if `package.json` has already moved to `app/` — commit whichever `package.json`/lock changed.)

---

### Task 2.2: Relocate Astro into `app/`

**Files:**
- Move: `src/` → `app/src/`, `astro.config.mjs` → `app/astro.config.mjs`, `package.json` → `app/package.json`, `package-lock.json` → `app/package-lock.json`, `eslint`/`prettier` configs → `app/`
- Modify: `app/astro.config.mjs` (base + outDir), `app/src/components/GenealogyViewer.jsx` (data import paths)

**Interfaces:**
- Consumes: `app/scripts/build-events.js` from Task 2.1.
- Produces: `cd app && npm run build` emitting `app/dist/` with base `/bible_end_times`.

- [ ] **Step 1: Move the Astro project under `app/`**

Run:
```bash
mkdir -p app
git mv src app/src
git mv astro.config.mjs app/astro.config.mjs
git mv package.json app/package.json
git mv package-lock.json app/package-lock.json
git mv eslint.config.js app/eslint.config.js 2>/dev/null || true
git mv .prettierrc app/.prettierrc 2>/dev/null || true
```
If `scripts/` was created at repo root in Task 2.1 instead of `app/scripts/`, also `git mv scripts app/scripts`.
Expected: `app/` now holds the Astro project; repo root holds `docs/`, `mkdocs.yml`, `app/`.

- [ ] **Step 2: Fix the genealogy data import paths (now one level deeper)**

In `app/src/components/GenealogyViewer.jsx`, change the seven imports from `../../docs/data/genealogy/...` to `../../../docs/data/genealogy/...`:
```javascript
import genealogyIndex from '../../../docs/data/genealogy/index.json';
import antediluvian from '../../../docs/data/genealogy/antediluvian.json';
import patriarchal from '../../../docs/data/genealogy/patriarchal.json';
import conquestJudges from '../../../docs/data/genealogy/conquest-judges.json';
import dividedKingdom from '../../../docs/data/genealogy/divided-kingdom.json';
import exileReturn from '../../../docs/data/genealogy/exile-return.json';
import secondTemple from '../../../docs/data/genealogy/second-temple.json';
```

- [ ] **Step 3: Set base path and out dir in `app/astro.config.mjs`**

Replace the config with:
```javascript
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://gh-ding0t.github.io',
  base: '/bible_end_times',
  outDir: './dist',
  srcDir: './src',
  integrations: [react()],
  vite: {
    ssr: { external: ['path'] },
  },
});
```

- [ ] **Step 4: Wire the events generator into the build**

In `app/package.json`, add a `prebuild` script and an events script so `npm run build` regenerates events first:
```json
"scripts": {
  "dev": "astro dev",
  "prebuild": "node scripts/build-events.js",
  "build": "astro build",
  "build:events": "node scripts/build-events.js",
  "preview": "astro preview",
  "astro": "astro",
  "test": "node --test scripts/build-events.test.js && node src/utils/calendarConvert.test.js && node src/utils/bibleReference.test.js",
  "lint": "eslint src/",
  "lint:fix": "eslint src/ --fix",
  "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,astro,json,css}\"",
  "format:check": "prettier --check \"src/**/*.{js,jsx,ts,tsx,astro,json,css}\""
}
```
(The generator resolves `repoRoot` as two levels up from `app/scripts/`, so it correctly writes `docs/data/events.json` at the repo root.)

- [ ] **Step 5: Reinstall deps in the new location and build**

Run:
```bash
cd app && npm ci && npm run build 2>&1 | tail -30
```
Expected: `prebuild` writes events.json, then Astro builds `app/dist/` with pages under `/bible_end_times/`. Note it will still build the legacy content pages (index, studies, bible) — those are removed in Task 4.1; a successful build here is enough.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor(astro): relocate app to app/ with base path and events prebuild"
```

---

### Task 2.3: Rewire timeline to events.json; rename genealogy route

**Files:**
- Modify: `app/src/pages/timeline.astro`
- Rename: `app/src/pages/genealogy-viewer.astro` → `app/src/pages/genealogy.astro`

**Interfaces:**
- Consumes: `docs/data/events.json` (from Task 2.1), shape `{ slug, title, description, tags, category, zadok_year, gregorian_year, url }`.
- Produces: `/bible_end_times/timeline/` and `/bible_end_times/genealogy/` pages.

- [ ] **Step 1: Replace the timeline data source**

In `app/src/pages/timeline.astro`, replace the frontmatter (lines 1-20, the `getCollection` block) with a JSON import that passes the dual-calendar fields straight through:
```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import TimelineComponent from '../components/TimelineComponent.jsx';
import events from '../../../docs/data/events.json';

const timelineEvents = [...events].sort(
  (a, b) => (a.gregorian_year ?? 0) - (b.gregorian_year ?? 0)
);
---
```
Leave the `<BaseLayout>` / `<TimelineComponent client:load events={timelineEvents} />` markup below unchanged, EXCEPT update the genealogy link (was `/genealogy-viewer/`) to `/genealogy/` so it resolves under the new route (Astro prepends the base automatically for root-relative `href` via `import.meta.env.BASE_URL`; use `{import.meta.env.BASE_URL}genealogy/` to be safe).

- [ ] **Step 2: Rename the genealogy page to the clean route**

Run:
```bash
git mv app/src/pages/genealogy-viewer.astro app/src/pages/genealogy.astro
```

- [ ] **Step 3: Build and verify both routes exist with events**

Run:
```bash
cd app && npm run build 2>&1 | tail -15
ls dist/timeline/ dist/genealogy/
```
Expected: `dist/timeline/index.html` and `dist/genealogy/index.html` exist.

- [ ] **Step 4: Confirm the timeline actually has events (the original bug)**

Run:
```bash
grep -c "Dated Study\|Woman with the Issue" app/dist/timeline/index.html || true
```
Expected: a non-empty match — the timeline now renders the dated studies instead of being empty. (If the component renders events only client-side, instead open `npm run preview` and check the timeline shows the two dated events.)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "fix(timeline): read events.json with dual-calendar fields; rename genealogy route"
```

---

### Task 3.1: Unified deploy workflow

**Files:**
- Create: `.github/workflows/deploy.yml`
- Delete: `.github/workflows/astro_deploy.yml`, `.github/workflows/mkdocs_ci.yml`

**Interfaces:**
- Consumes: `uvx mkdocs build`, `app/` npm build, `app/scripts/build-events.js`.
- Produces: a `site/` containing mkdocs output plus Astro `/timeline/` and `/genealogy/`, deployed to Pages.

- [ ] **Step 1: Write the combined workflow**

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy site to GitHub Pages

on:
  push:
    branches: [main, master]
    paths:
      - 'docs/**'
      - 'app/**'
      - 'mkdocs.yml'
      - '.github/workflows/deploy.yml'
  workflow_dispatch:

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Build mkdocs content site
        run: uvx --with mkdocs-awesome-pages-plugin --from mkdocs-material mkdocs build --site-dir site

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: app/package-lock.json

      - name: Install app deps
        run: npm ci
        working-directory: app

      - name: Run tests
        run: npm test
        working-directory: app

      - name: Build Astro tools (runs events prebuild)
        run: npm run build
        working-directory: app

      - name: Stitch Astro output into the mkdocs site
        run: cp -r app/dist/* site/

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Remove the superseded workflows**

Run:
```bash
git rm .github/workflows/astro_deploy.yml .github/workflows/mkdocs_ci.yml
```
Expected: `marp_ci.yml` and the new `deploy.yml` remain.

- [ ] **Step 3: Commit and push to trigger deploy**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: single workflow builds mkdocs + Astro tools into one Pages site"
git push
```

- [ ] **Step 4: Verify the live site after the run**

After the Actions run completes, load and confirm each:
- `https://gh-ding0t.github.io/bible_end_times/` — mkdocs home
- `https://gh-ding0t.github.io/bible_end_times/studies/prophecy-fulfilled-in-jesus/woman-suffering-bleeding/` — a study
- `https://gh-ding0t.github.io/bible_end_times/timeline/` — timeline with the dated events
- `https://gh-ding0t.github.io/bible_end_times/genealogy/` — genealogy viewer

Expected: all four load; clicking a timeline event navigates to its mkdocs study page.

---

### Task 4.1: Delete retired Astro content code

**Files:**
- Delete: `app/src/content/config.ts`, `app/src/pages/index.astro`, `app/src/pages/bible.astro`, `app/src/pages/studies.astro`, `app/src/pages/studies/[...slug].astro`, `app/src/pages/[...slug].astro`, `app/src/components/SearchComponent.jsx`, `app/src/components/StudySidebar.astro`, `app/src/components/TableOfContents.astro`, `app/src/utils/contentTree.js`, `app/src/utils/categoryLabels.js`, all `docs/content/**/_category.json`
- Modify: `app/src/layouts/BaseLayout.astro` (drop content-collection nav)

**Interfaces:**
- Produces: an Astro app that builds only `timeline.astro` + `genealogy.astro`.

- [ ] **Step 1: Simplify BaseLayout to a static nav (no content collection)**

In `app/src/layouts/BaseLayout.astro`, remove the frontmatter's `getCollection`/`buildContentTree` block (lines 1-22) and replace with:
```astro
---
interface Props {
  title?: string;
}
const { title = 'Biblical Studies' } = Astro.props;
const base = import.meta.env.BASE_URL;
---
```
Then replace the `<nav>` `<ul>` contents (the `navSections.map` / `PINNED_LAST.map` block) with static links back to the mkdocs site and the two tools:
```astro
<ul>
  <li><a href={base}>Home</a></li>
  <li><a href={`${base}studies/`}>Studies</a></li>
  <li><a href={`${base}timeline/`}>Timeline</a></li>
  <li><a href={`${base}genealogy/`}>Genealogy</a></li>
</ul>
```

- [ ] **Step 2: Delete the retired content-rendering files**

Run:
```bash
git rm app/src/content/config.ts \
       app/src/pages/index.astro \
       app/src/pages/bible.astro \
       app/src/pages/studies.astro \
       "app/src/pages/studies/[...slug].astro" \
       "app/src/pages/[...slug].astro" \
       app/src/components/SearchComponent.jsx \
       app/src/components/StudySidebar.astro \
       app/src/components/TableOfContents.astro \
       app/src/utils/contentTree.js \
       app/src/utils/categoryLabels.js
git rm -r $(find docs/content -name _category.json)
```
Expected: files removed. `app/src/pages/` now contains only `timeline.astro` and `genealogy.astro`.

- [ ] **Step 3: Rebuild and confirm only the two tools build**

Run:
```bash
cd app && npm run build 2>&1 | tail -20
ls dist/
```
Expected: build succeeds; `dist/` contains `timeline/`, `genealogy/`, `_astro/` and no `studies/` or content index. No unresolved-import errors (all deleted files were unreferenced by the two remaining pages after Step 1).

- [ ] **Step 4: Run tests**

Run: `cd app && npm test`
Expected: PASS — events generator + calendar + bibleReference tests all green.

- [ ] **Step 5: Commit and push**

```bash
git add -A
git commit -m "refactor(astro): delete retired content pages, search, and nav helpers"
git push
```

- [ ] **Step 6: Final live verification**

Re-check the four URLs from Task 3.1 Step 4 after deploy. Expected: all still load; the Astro app is now purely the two tools.

---

## Notes for the implementer

- **Studies safety is the prime directive.** If any step appears to touch prose under `docs/content/`, stop — only config, `_category.json`, and Astro `src/` files should ever be deleted.
- The generator lives at `app/scripts/` (not repo-root `scripts/` as the spec sketched) so one `app/package.json` owns `gray-matter` and the `prebuild` hook — simpler CI, no second Node project. This is the one intentional deviation from the design doc.
- If `awesome-pages` global install is troublesome, fall back to an explicit `nav:` in `mkdocs.yml` listing the content sections; the rest of the plan is unaffected.
