# Contributing to Biblical Studies

Thank you for wanting to contribute. This file is the short orientation; the detailed rules live in
the documents it points to, and those win where the two differ.

## How the site is built

- **One site, one build.** Every page is markdown in `docs/content/`, built by
  [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) and served from
  `the-way.lewy.au` on Cloudflare Workers. `.github/workflows/deploy.yml` builds and deploys on
  every push to `main` that touches `docs/`, `app/`, `mkdocs.yml` or `wrangler.jsonc`.
- **The interactive tools** are React components in `app/`, bundled by esbuild into
  `docs/content/assets/js/` before the mkdocs build, so mkdocs serves them as ordinary assets. There
  are three: the Prophetic Timeline (`timeline.md`, which also carries the genealogy: a row per
  person, a person panel and a family-tree view), the Scripture Links explorer (`references.md`),
  and the verse and word pop-ups that run on every page.
- **Chronology data** lives in `docs/data/`: `chronology.json` holds every dated event once, and
  `genealogy/` holds the people. Each fact is stored once and the other calendar is derived; see
  the "One set of chronology facts" note in [`AGENTS.md`](../../AGENTS.md) before editing either.

[`AGENTS.md`](../../AGENTS.md) (also loaded as `CLAUDE.md`) is the full description of the site,
its commands and its architecture.

## Writing a study

Use the **develop-bible-study** skill
([`.claude/skills/develop-bible-study/SKILL.md`](../../.claude/skills/develop-bible-study/SKILL.md))
for anything beyond a quick note. It works exegesis before hermeneutics, keeps a resumable state file
under `references/study-state/`, and drafts to the site's style guide. Three companion skills cover
an existing file: **review-bible-study** (is it true?), **read-bible-study** (can it be read?) and
**simplify-bible-study** (is it the right size?).

**Where it goes.** A study lives at `docs/content/<section>/<slug>.md`, in the section its subject
belongs to (`jesus/`, `last-things/`, `god/`, `feasts/`, and so on). There is no `studies/` folder.
[`placement-and-tags.md`](../../.claude/skills/develop-bible-study/placement-and-tags.md) lists the
sections and how to choose between two, and the tag vocabulary is on
[`tags.md`](../content/tags.md).

**File names** are lowercase and hyphen-separated: `woman-with-the-issue-of-blood.md`.

**Frontmatter** is documented in [`docs/CONTENT_GUIDE.md`](../CONTENT_GUIDE.md). The short
version:

```markdown
---
title: "Your Study Title"
category: "prophecy"
description: "One-line summary of this study"
tags: ["end-times", "method/word-study"]
draft: true
primary_passage: "Daniel 12:11"
bible_references: ["Daniel 12:11", "Matthew 24:15"]
---

# Your Study Title
```

Leave out `date_created`, `date_modified` and `ai_provider_models`: they are derived from git by
`python3 utils/refresh_frontmatter_provenance.py`, which you run before committing and stage with your
edit. Add `zadok_year` and `gregorian_year` only when the study is about a datable event, and take
both from the site's chronology (creation 3959 BC), never from memory.

**References** are written as plain text, never as links: "Genesis 7:11", not a Bible-site URL. Every
reference on a page opens a pop-up with the verse, so a link would hide it. Name the book every time,
except within a single citation ("Revelation 21:2, 9").

**Sources.** [`references/README.md`](../../references/README.md) lists what the project can
quote and how: open-licence texts, restricted ones, and copyrighted study Bibles that may be
checked freely but quoted only a sentence or two at a time. Verify every ESV quotation against
`study-notes.db`. Every study ends with a **References & Recommended Reading** section.

**Drafts.** Keep `draft: true` until the study has been reviewed. `hooks/draft_pages.py` keeps drafts
out of the published site, so a published page must not link to one.

## Markdown extras

Standard markdown, plus what `mkdocs.yml` enables:

- **Mermaid diagrams** in a fenced block with `mermaid` as the language. Keep them within the width
  the page can show; [`diagrams.md`](../../.claude/skills/develop-bible-study/diagrams.md) has the
  rules.
- **Admonitions** with mkdocs-material's syntax:

  ```markdown
  !!! note "Optional title"
      Indented body text.
  ```

  (GitHub's `> [!NOTE]` callout syntax is not enabled and renders as a plain quote.)
- **Task lists** (`- [x] done`), **footnotes** (`[^1]`), and collapsible blocks (`??? note`).
- **Hebrew and Aramaic** go in `<span dir="rtl">…</span>`, never inside `**bold**`: synthetic bold
  misplaces the vowel points.
- **Scripture block quotes** open with the reference and translation on their first line:
  `> ✝️ John 3:16 (ESV)`.
- **Images:** see [`docs/CONTENT_GUIDE.md`](../CONTENT_GUIDE.md#images-and-assets) for the path
  rules.

React components cannot be used inside a markdown page. A study that needs something interactive
needs a change to the tools in `app/`.

## Previewing

**Content** (anything in `docs/content/`), with hot reload at `http://localhost:8000/`:

```bash
uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects mkdocs serve
```

**Tools** (anything in `app/`). Build the bundles once, or keep them rebuilding while you work, and
run `mkdocs serve` alongside; the bundles land inside the docs folder, so a rebuild reloads the
page:

```bash
cd app
npm install
npm run build:tools   # once
npm run dev:tools     # or: rebuild on every change
```

Without a build, the timeline and Scripture Links pages render an empty box and no reference pops
up.

## Checking your work

- `npm run validate` (from `app/`) is the content linter: frontmatter, image paths, quote-block
  format, bold Hebrew, the style-guide checks, provenance, word budget and more. It is **not** run in
  CI, so run it by hand. Errors block; warnings are judgement calls explained in the script's
  comments.
- `npm test` (from `app/`) runs the tool and chronology tests. CI runs these on every deploy.
- After editing `docs/data/genealogy/`, run `python3 utils/validate_genealogy.py`.
- A strict build (`mkdocs build --strict`, with the plugins above) catches broken links, including a
  published page that links to a draft.

## Commits

Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`), a subject under 72
characters with no full stop. Run the provenance script before committing a content change and
include its edits in the same commit.
