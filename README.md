# About

Personal bible studies on end times, prophecy, and biblical themes.

**Current Version:** [0.1.0](CHANGELOG.md) ([Release Notes](CHANGELOG.md#010---2026-01-11))

## Features

- 📅 **Interactive Timeline** with dual calendar views (Gregorian & Zadok)
- 📊 **Mermaid Diagrams** for prophecy visualizations
- 📖 **Bible Studies** organized by category, with a develop-bible-study skill that walks exegesis-then-hermeneutics before drafting
- 🔍 **Full Search Support** across all content
- 🗄️ **Queryable Bible-text database** (`references/build/`) — Hebrew/Greek morphology, Strong's, Louw-Nida/SDBH semantic domains, cross-references

## Site structure

One site build, from two source trees:

- **`docs/`** — the content site (studies, commentaries, resources), built with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/). This is where nearly all writing happens.
- **`app/`** — the React components behind the interactive tools (scripture links, timeline, genealogy).
  Separate npm project; esbuild bundles them into `docs/content/assets/js/` before the mkdocs build,
  so a single pass produces the whole site.

## Getting Started

### Content (studies, commentaries)

```bash
uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects mkdocs serve
```

Dev server (hot reload) at http://localhost:8000/.

### Interactive tools (timeline, genealogy)

```bash
cd app
npm install
npm run dev
```

Dev server at http://localhost:4321/.

### Bible-text database (word studies, cross-references)

```bash
cd references/build
uv sync
uv run python build.py       # builds references/build/out/bible-text.db
uv run python query.py --help
```

See [`references/README.md`](references/README.md) for what's in it and how to cite each source (open, restricted-non-commercial, or local-only copyrighted).

## Contributing

See [`docs/dev/CONTRIBUTING.md`](docs/dev/CONTRIBUTING.md) for guidelines on:
- Adding new studies
- Using frontmatter fields
- Creating diagrams with Mermaid
- Bible references and calendar years

## Project Structure

```text
docs/                    mkdocs content site
├── content/              studies, commentaries, resources (markdown + frontmatter)
│   └── studies/<category>/
├── assets/                images used by content
├── CONTENT_GUIDE.md       frontmatter schema, categories, image paths — the authoritative content reference
└── dev/CONTRIBUTING.md    contributor guide

app/                      React components for the interactive tools, bundled into the mkdocs site
├── src/
├── scripts/               build-time data prep (e.g. events.json from content frontmatter)
└── package.json

references/                data and tooling behind studies, not site content
├── open-data/              git submodules, unconditionally open-licensed sources
├── restricted-data/         git submodules, non-commercial-restricted sources
├── build/                  the bible-text.db pipeline (build.py, query.py) + study_notes/ (commercial
│                            study-Bible extraction, writes external to this repo — see references/README.md)
├── study-state/             per-study research/progress tracking (develop-bible-study skill)
└── README.md                what every source is, its license, and how to query/cite it

.claude/skills/develop-bible-study/  the exegesis-then-hermeneutics process for writing a new study

.github/workflows/deploy.yml   npm test + build:tools, then mkdocs build, deploys to GitHub Pages
```

## Licence

Two licences, because a repository of writing and a repository of code are not the same thing:

- **Writing** — the studies and other prose under `docs/content/` are [CC BY 4.0](LICENSE-CONTENT).
  Share and adapt them, commercially or not; credit the source and say if you changed anything.
- **Code** — `app/`, `references/build/`, `utils/`, `hooks/` and the build configuration are
  [MIT](LICENSE).

Neither covers third-party material. Quoted Scripture, lexicons, commentaries, the linguistic
datasets, and the submodules under `references/open-data/` and `references/restricted-data/` each
carry their own terms — see [about/copyright.md](docs/content/about/copyright.md) and
[references/README.md](references/README.md).
