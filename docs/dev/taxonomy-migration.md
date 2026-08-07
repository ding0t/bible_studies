# Taxonomy migration plan

Moving `docs/content/` to the structure defined in
[Our Taxonomy](../content/about/our-taxonomy.md): subject sections at the top level, named from the
systematic-theology loci, with `studies/` and `bible/` dissolved.

**Not started.** This is the plan, not a record of work done.

---

## Scope

| | Count |
|---|---|
| Hand-written pages moving | 59 |
| Commentary pages moving (path only, content untouched) | 287 |
| Internal `.md` links in hand-written content | 238 |
| Internal `.md` links inside commentaries | 553 |
| Scripts needing edits | 2 |

**553 of the 791 links regenerate themselves.** They live inside
`<!-- commentary-index:auto-start/end -->` markers and are produced by `commentary_index.py` from
frontmatter. They are not hand-edited — the script is fixed, then re-run. This is the single biggest
thing that makes the migration tractable, and it is worth confirming before starting: a link at
`../../../studies/...` inside a commentary file should never be touched by hand.

---

## Phase 0 — do these first, no moves involved

Each is independently useful and carries no URL risk. Doing them first means the migration itself is
purely mechanical.

1. **Add `extra_css` to `mkdocs.yml`.** `docs/content/assets/stylesheets/enumerate-headings.css` and
   `hero-verses.css` exist but are never loaded — there is no `extra_css` key in the config at all.
   Unrelated to the migration; found while surveying.
2. **Enable the `tags` plugin**, so the facets below are worth maintaining. One line under `plugins:`.
3. **Normalise existing tags** — `doctrine` currently appears as two distinct values (trailing
   whitespace). Fix before re-faceting, so the before/after diff is readable.
4. **Decide `salvation/` and `biblical-figures/`.** Both are defined in the taxonomy but have zero
   files today. Per the taxonomy's own rule, do not create them until content exists — and do not
   list them in `.pages` until they do, or `awesome-pages` will point at nothing.

---

## Phase 1 — file moves

Use `git mv` throughout so history follows the file.

### scripture/ — Bibliology

| From | To |
|---|---|
| `bible/how-to-read-the-bible.md` | `scripture/how-to-read-the-bible.md` |
| `bible/translations.md` | `scripture/translations.md` |
| `studies/archeology/ancient-texts-manuscripts.md` | `scripture/ancient-texts-manuscripts.md` |
| `studies/archeology/archaeological-sites.md` | `scripture/archaeological-sites.md` |
| `studies/theology/numerology.md` | `scripture/numerology.md` ⚠️ |
| `resources/early-new-testament-manuscripts.md` | `scripture/early-new-testament-manuscripts.md` ⚠️ |

⚠️ = judgment call, see [Open questions](#open-questions).

### god/ — Theology Proper

| From | To |
|---|---|
| `studies/theology/creation-reveals-the-creator.md` | `god/creation-reveals-the-creator.md` |
| `studies/theology/dreams-and-visions/` *(whole tree, 5 files)* | `god/dreams-and-visions/` |

### jesus/ — Christology

| From | To |
|---|---|
| `studies/theology/melchizedek-priesthood.md` | `jesus/melchizedek-priesthood.md` |
| `studies/theology/the-way.md` | `jesus/the-way.md` |
| `studies/prophecy-fulfilled-in-jesus/as-the-snake-was-lifted.md` | `jesus/as-the-snake-was-lifted.md` |
| `studies/prophecy-fulfilled-in-jesus/bread-of-life-feeding-the-multitudes.md` | `jesus/bread-of-life-feeding-the-multitudes.md` |
| `studies/prophecy-fulfilled-in-jesus/woman-at-well.md` | `jesus/woman-at-well.md` |
| `studies/prophecy-fulfilled-in-jesus/woman-issue-of-blood-faith-and-access.md` | `jesus/woman-issue-of-blood-faith-and-access.md` |
| `studies/prophecy-fulfilled-in-jesus/woman-suffering-bleeding.md` | `jesus/woman-suffering-bleeding.md` |

### sin/ — Hamartiology

`studies/sins/{idolatry,sexual-immorality,sorcery}.md` → `sin/`

Note `sorcery.md` is `draft: true` pending review. It moves with the rest; the draft flag is
orthogonal.

### spiritual-beings/ — Angelology & Demonology

| From | To |
|---|---|
| `studies/prophecy/nephilim.md` | `spiritual-beings/nephilim.md` |
| `studies/spiritual-disciplines/test-the-spirits.md` | `spiritual-beings/test-the-spirits.md` ⚠️ |
| `investigation/deliverance/` *(3 files)* | `spiritual-beings/deliverance/` |

### last-things/ — Eschatology

`studies/prophecy/{day-is-near,prophecy-chart,prophecy-essentials,prophecy-events-times,rapture,trumpet}.md`
→ `last-things/`

Plus `studies/prophecy/genealogy-times.md` → `last-things/genealogy-times.md` ⚠️

### israel-and-church/ — Ecclesiology + the dispensational distinction

`studies/theology/{hebrew-roots,israel-and-the-church}.md` → `israel-and-church/`

### feasts/ — appointed times

`studies/feasts/{feasts,last-supper-four-cups,trumpets}.md` → `feasts/`

Plus `studies/prophecy/zadok-calendar.md` → `feasts/zadok-calendar.md`

### christian-life/ — practical theology

`studies/prayer/{lords-prayer,prayer-as-communion}.md` and
`studies/spiritual-disciplines/{be-prepared,fasting}.md` → `christian-life/`

### commentaries/

`bible/commentaries/` → `commentaries/` — the whole tree, 287 files, content untouched.

### sermons/

`studies/teaching-resources/{on-teaching,sermon-howto}.md` → `sermons/`

### resources/

`hebrew-studies/hebrew-alphabet.md` → `resources/hebrew-alphabet.md`;
`hebrew-studies/resources.md` merges into the existing `resources/index.md`.

### Containers that disappear

`studies/`, `studies/theology/`, `studies/archeology/`, `studies/prophecy-fulfilled-in-jesus/`,
`studies/prayer/`, `studies/spiritual-disciplines/`, `studies/teaching-resources/`,
`hebrew-studies/`, `investigation/`, `bible/`.

Their `index.md` files are **deleted, not moved** — `section_index.py` regenerates a landing page
for any directory that lacks one. Any hand-written intro prose on them worth keeping must be lifted
out first; check each before deleting.

---

## Phase 2 — script changes

### `references/build/commentary_index.py`

Five edits, all pinned to current line numbers:

| Line | Now | Becomes |
|---|---|---|
| 23 | `STUDIES_DIR = REPO_ROOT/"docs"/"content"/"studies"` | `CONTENT_DIR = REPO_ROOT/"docs"/"content"`, plus an explicit list of subject dirs to scan |
| 25 | `COMMENTARIES_DIR = .../"bible"/"commentaries"` | `.../"commentaries"` |
| 61 | `STUDIES_DIR.rglob("*.md")` | iterate the subject-dir list |
| 77 | `md_file.relative_to(STUDIES_DIR)` | `md_file.relative_to(CONTENT_DIR)` |
| 118 | `]({depth_prefix}studies/{e['rel_path']})` | `]({depth_prefix}{e['rel_path']})` — drop the hardcoded `studies/` |
| 198 | `render_auto_section(entries, "../../../")` | `"../../"` — one level shallower once `bible/` is gone |

The subject-dir list must be **explicit**, not "everything under `docs/content/`" — otherwise the
scan picks up `about/`, `commentaries/`, `resources/`, `sermons/` and `assets/` and starts
cross-referencing the site's own meta pages.

### `references/build/section_index.py`

`SECTION_BLURBS` is keyed by path (`"studies/prophecy"`, `"bible/commentaries"`, …). Every key needs
rewriting to the new names. It is the one hand-maintained piece in that script, and the blurbs
themselves are worth rewording at the same time, since several describe the old grouping.

### `app/scripts/build-events.js`

No code change needed — line 31 derives `category` from the parent directory name, so it picks up the
new names automatically. **But the values change** (`prophecy` → `last-things`, etc.). Check whether
the Astro timeline filters or colours by category before assuming this is free.

---

## Phase 3 — links

Order matters here.

1. **Fix and re-run `commentary_index.py`.** This regenerates all 553 commentary→study links at the
   new paths. Do this before hand-editing anything, so the hand-edit pass is only looking at the
   remaining 238.
2. **Rewrite the 238 hand-written links.** Mostly relative paths that get *shorter* — a study
   linking a sibling in the old `studies/theology/` may now be `../jesus/…` or a bare filename.
3. **Re-run `section_index.py`** to regenerate every landing page.
4. **Regenerate `utils/generate_recent_updates.py`** — it derives from git log and writes into
   `about/recent-updates.md` and `index.md`. It runs in CI anyway, but run it locally to confirm the
   moves do not produce 59 spurious "recently updated" entries. If they do, that is worth knowing
   before deploy, not after.

### Redirects

Add `mkdocs-redirects` and a `redirect_maps` entry for every moved page — all 59 hand-written pages,
plus the deleted container indexes (`studies/index.md`, `bible/index.md`, `hebrew-studies/index.md`,
`investigation/index.md`) so those do not 404.

The 287 commentary pages also change path. Whether they need redirects depends on whether anything
links to them externally; they are mostly generated stubs, so a blanket redirect for
`bible/commentaries/*` → `commentaries/*` is probably enough if the plugin supports the pattern —
otherwise skip them and accept the breakage on generated stubs.

---

## Phase 4 — tags

Only worth doing once the `tags` plugin is on (Phase 0).

**Delete outright** — the directory now says it, so the tag is pure noise:
`studies` (14 uses), `prophecy` (14), `eschatology`, `end-times`, `theology`, `sin`, `feasts`,
`sermons`, `bible`, `resources`, `deliverance`, `doctrine`.

**Re-prefix into facets:**

| Facet | From existing tags |
|---|---|
| `method:word-study` | `word-study` (17 uses) |
| `method:archaeology` | `archaeology` (4) |
| `method:textual-criticism` | `textual-criticism` (3) |
| `lang:hebrew` | `hebrew` (8) |
| `lang:greek` | `greek` (4) |
| `status:investigation` | the 3 files under `investigation/deliverance/` |
| `audience:teaching` | `teaching` (4) |

**Keep as plain topic tags** anything genuinely additive that the directory does not imply — book
names, named people, specific concepts (`garment-fringe`, `synoptics`, `uncleanness`).

---

## Verification

Run after each phase, not just at the end:

```bash
cd app && npm run validate          # frontmatter, image paths, quote-block format
uvx ... mkdocs build --strict       # --strict turns broken internal links into build failures
cd app && npm test && npm run build # build-events + timeline still build
```

`mkdocs build --strict` is the one that matters for a link migration — it is the only check that
actually resolves every internal link. It is not currently part of the deploy workflow
(`.github/workflows/deploy.yml` runs a plain `mkdocs build`), so run it by hand, and consider
adding `--strict` permanently once the tree is clean.

Manual spot-checks worth doing:

- A commentary chapter page with linked studies (e.g. `commentaries/43-john/chapter-014.md`) —
  confirm the regenerated links resolve at the new depth.
- The three book studies (Genesis, Daniel, Proverbs) — confirm hand-written prose above the
  auto-markers survived regeneration.
- `/timeline/` — confirm events still render after the category values change.

---

## Open questions

Four files have no single obviously-right home. Each is marked ⚠️ above; none blocks the migration.

1. **`numerology.md`** — about a pattern *in* the text, so `scripture/`, but everything else there is
   about transmission and canon.
2. **`genealogy-times.md`** — chronology creation→Christ. Touches `scripture/` (dating),
   `biblical-figures/` (the genealogies), `last-things/` (it feeds the prophetic timeline). Filed
   under `last-things/` on the strength of the timeline dependency.
3. **`test-the-spirits.md`** — discernment of spirits, so `spiritual-beings/`; but it is also a
   practice, so `christian-life/`. The sorcery study links it as a discernment test, which tips it.
4. **`early-new-testament-manuscripts.md`** — currently under `resources/` with
   `category: resources`, but its content is bibliology, not a guide to external tools.

All four are filed by primary subject and tagged for the secondary one, per the taxonomy page.

---

## Order of execution

Phases are ordered by risk, lowest first. Stop at any boundary and the site still builds.

1. **Phase 0** — config and tags. No moves, no risk, independently useful.
2. **Phase 2 script edits** — make them, do *not* run yet.
3. **Phase 1 moves**, one section at a time. `git mv`, validate, commit per section.
4. **Phase 3** — run the scripts, fix remaining links, add redirects.
5. **Phase 4** — tag re-facet.

The one-section-at-a-time discipline in step 3 matters: with a commit per section, a bad move is a
`git revert` rather than an archaeology exercise across 346 relocated files.
