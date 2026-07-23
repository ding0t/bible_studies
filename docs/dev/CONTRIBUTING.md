# Contributing to Biblical Studies

Thank you for wanting to contribute! This guide covers the current site structure — it was split into two tools (mkdocs for content, Astro for the interactive timeline/genealogy) in mid-2026; if you find instructions elsewhere that describe a single Astro-powered site, they predate that split and are wrong.

## Site structure

- **Content** (studies, commentaries, resources) — plain markdown in `docs/content/`, built with [mkdocs-material](https://squidfunnel.github.io/mkdocs-material/). This is what you're editing for a new study.
- **Interactive tools** (timeline, genealogy viewer) — an Astro app in `app/`. Separate codebase, separate dev workflow; only touch this if you're changing the timeline/genealogy tools themselves, not writing content.
- Both get built and stitched together into one site by `.github/workflows/deploy.yml` on push to `main`.

## For study files

**Frontmatter and category conventions are documented in [`docs/CONTENT_GUIDE.md`](../CONTENT_GUIDE.md) — that's the authoritative reference, not this file.** The short version:

```markdown
---
title: "Your Study Title"
category: "prophecy"
description: "One-line summary of this study"
tags: ["end-times", "prophecy"]
draft: true
bible_references: ["Daniel 12:11", "Matthew 24:15"]
zadok_year: 5972
gregorian_year: 2026
---

# Your Study Title

Your content starts here in markdown...
```

Studies go under `docs/content/studies/<category-subfolder>/`. If you're using the [develop-bible-study skill](../../.claude/skills/develop-bible-study/SKILL.md) (recommended for anything beyond a quick note), it handles scoping, exegesis, word studies, and drafting for you, and requires every study to end with a **References & Recommended Reading** section.

**File naming:** lowercase, hyphen-separated, descriptive — `woman-issue-of-blood-faith-and-access.md`, not `study1.md` or `my_study_title.md` (underscores were the old convention; every current file uses hyphens).

**Categories** currently in use: `prophecy`, `theology`, `spiritual-disciplines`, `sins`, `feasts`, `sermons`, `hebrew-studies`, `dreams` / `dreams-visions`, `teaching-resources`, `deliverance`, `investigation`, `archeology`, `commentaries`, `other`. Any string works (the site auto-generates a label), but reuse an existing one where it fits.

## Local preview

**For content changes** (anything in `docs/content/`):

```bash
uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin --with mkdocs-git-revision-date-localized-plugin mkdocs serve
```

Serves with hot reload, typically at `http://localhost:8000/`.

**For timeline/genealogy tool changes** (anything in `app/`):

```bash
cd app
npm install
npm run dev
```

Dev server at `http://localhost:4321/`.

## Markdown formatting

Standard markdown, plus mkdocs-material extras already configured in `mkdocs.yml`:

- **Mermaid diagrams** — a fenced code block with `mermaid` as the language works directly:

  ````markdown
  ```mermaid
  flowchart LR
      A["Passover (Spring)"] -->|Fulfilled in| B["Christ's Crucifixion"]
  ```
  ````

- **Admonitions**: `> [!NOTE]`, `> [!WARNING]`, `> [!TIP]` render as callout boxes.
- **Task lists**: `- [x] done`, `- [ ] not done`.
- **Images**: see the path-counting rule in [`docs/CONTENT_GUIDE.md`](../CONTENT_GUIDE.md#images-and-assets) — relative paths depend on how deep your file is.

**Not available in study content:** React/JSX components (`<ProphecyComparison client:load />` and similar). That's an Astro-specific pattern that only works inside the `app/` codebase — it does not render in mkdocs-built markdown pages. If a study genuinely needs an interactive diagram, that would need to be a page built into the `app/` Astro tool, not a `docs/content/` markdown file.

## Validation

`npm run validate` (referenced in older docs) **no longer works** — `app/scripts/validate-content.js` hardcodes a path relative to `app/` that predates the mkdocs split and can't find `docs/content` anymore. Until that's fixed or replaced with an mkdocs-side check, validate a new study manually:

- Frontmatter starts on line 1, no blank line before the opening `---`.
- `title` is present and quoted if it contains a colon.
- Arrays (`tags`, `bible_references`) use quoted strings: `["tag1", "tag2"]`.
- `description` stays under ~200 characters.
- `draft: true` until reviewed.

## Process

1. Create/edit a file under `docs/content/studies/<category>/`.
2. Write frontmatter + content per `docs/CONTENT_GUIDE.md`.
3. Preview with `mkdocs serve`.
4. Leave `draft: true` until reviewed; a maintainer (or you, once satisfied) flips it to `false`.

## References and sources

See [`references/README.md`](../../references/README.md) for what data/lexicon/commentary sources this project has (open-license, restricted-license, and local-only copyrighted), and how to cite each appropriately — every study should end with a References & Recommended Reading section naming sources actually used, restricted/copyrighted ones included by name with attribution.
