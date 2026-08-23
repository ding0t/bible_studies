# Placement & tags

Which section a study goes in, and what it gets tagged. Shared by both skills:
[develop-bible-study](SKILL.md) uses it before drafting (getting this wrong is cheap to prevent and
annoying to fix once the URL is published), [review-bible-study](../review-bible-study/SKILL.md)
Phase 7 uses it as a checklist against a file that already exists.

Full definition: [our-taxonomy.md](../../../docs/content/about/our-taxonomy.md). This is the working
short version.

## Sections are top level

There is no `studies/` wrapper and no `bible/` — a study goes at `docs/content/<section>/<slug>.md`.
Named from the systematic-theology loci in plain English:

| Section | Locus | Takes |
|---|---|---|
| `scripture/` | Bibliology | Canon, manuscripts, textual criticism, translation, how to read it, biblical archaeology, extra-biblical texts |
| `god/` | Theology Proper | God's nature, Trinity, Holy Spirit, creation, revelation (incl. dreams and visions) |
| `jesus/` | Christology | Who Christ is and what he did; OT prophecy fulfilled in him |
| `sin/` | Hamartiology | The nature of sin and its particular forms |
| `spiritual-beings/` | Angelology & Demonology | Angels, demons, Satan, Nephilim, deliverance, discernment of spirits |
| `israel-and-church/` | Ecclesiology + the dispensational distinction | Covenants, Israel/Church, Hebrew roots |
| `last-things/` | Eschatology | Rapture, tribulation, millennium, judgment, ordering of events |
| `feasts/` | *Appointed times* | The feasts and calendars |
| `christian-life/` | Practical theology | Prayer, fasting, the disciplines |
| `commentaries/<nn>-<book>/` | — | Book studies and chapter notes, filed by book |
| `sermons/` | Homiletics | Sermon and teaching material |
| `resources/` | — | Guides to external material |

**Two sections are defined but not created**: `salvation/` (Soteriology — grace, redemption,
assurance, death) and `biblical-figures/` (biography). A section exists when it has content. **If a
study genuinely belongs to one of these, say so and create it** — that is the trigger the taxonomy is
waiting for, not a reason to file the study somewhere it doesn't fit. Creating one means adding the
directory, a line in `SUBJECT_DIRS` in `references/build/commentary_index.py`, a blurb in
`SECTION_BLURBS` in `section_index.py`, and an entry in `docs/content/.pages`.

**When a study could sit in two sections**, file it by what it is *most about* and tag the other
axis. Dewey's 200s are the tiebreaker — it has already adjudicated most of these (angels and demons
are 235, their own subject; apocrypha is 229; calendars and appointed times are 263). Don't invent a
new section to resolve a single awkward case.

**Some things are not subjects at all.** *Apologetics*, *typology*, *word study* and *archaeology*
are approaches, not topics — a study using them is filed by what it is about and carries the approach
as a tag. An apologetics study defending Scripture's reliability is `scripture/`; one arguing from
creation is `god/`; one on the resurrection is `jesus/`.

When reviewing, the failure to look for is a study parked in a section because that is where a
*related* study lives rather than because the subject fits.

## Tags carry every axis the directory can't

Five facets use a `/` prefix and render as a real hierarchy (`tags_hierarchy: true` in `mkdocs.yml`):

- `method/word-study`, `method/typology`, `method/archaeology`, `method/textual-criticism`
- `lang/hebrew`, `lang/greek`
- `status/investigation` — open inquiry, conclusions not settled
- `audience/teaching`
- `person/<name>` — a named individual the study is *about* (`person/peter`, `person/melchizedek`)

**Why `person/` exists.** Most Bible people share a name with a book, and a flat `matthew` tag cannot
tell a reader whether the page is about the tax collector or the Gospel. The site had exactly that
collision the moment `biblical-figures/` was created. So: **a book always gets the bare tag
(`matthew`, `john`, `james`), and a person always gets `person/`.** A page can carry both —
`biblical-figures/matthew.md` is about the man *and* cites his Gospel, so it tags `person/matthew`
and `matthew`. This is easy to miss on review because both tags are individually legitimate: check
which the *page* is about.

Use `person/` when the individual is a subject of the study, not merely mentioned. Where two people
share a name, disambiguate the way Scripture does, by patronymic: `person/james-son-of-zebedee` and
`person/james-son-of-alphaeus`, never a bare `person/james`. Where one person has two names, tag both
if the study argues the identification (`person/bartholomew` and `person/nathanael`).

Everything else is a plain topic tag: a book, a feast, a concept. Rules that matter:

- **Never tag what the section already says.** No `studies`, no `prophecy` on a `last-things/` page,
  no `sin` on a `sin/` page. It adds nothing and inflates the tag index.
- **No colons in tag values** — the facet separator is `/`, and a colon reads as a competing
  convention (`malachi-4:2` had to be renamed `malachi-4-2`).
- Lowercase, hyphenated, no spaces. `dead-sea-scrolls`, not `dead sea scrolls` or `Dead Sea Scrolls`.
- Prefer an existing tag to a near-synonym (`messianic` beside `messianic-prophecy`). Check
  [docs/content/tags.md](../../../docs/content/tags.md) — the rendered index is the live vocabulary.

## The provenance fields

Every hand-written page under `docs/content/` carries three provenance fields, at the end of the
frontmatter block:

```yaml
date_created: 2026-08-02
date_modified: 2026-08-23
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-sonnet-5
```

**Don't type these by hand — derive them.** Run `python3 utils/refresh_frontmatter_provenance.py`
from the repo root and it fills all three in from git history: first-commit date, last-commit
date, and every model named in a `Co-Authored-By` trailer on the commits that touched the file. It
follows renames, so the 2026-08 taxonomy migration doesn't reset an older study's `date_created`
to the day it was moved. Re-running is safe: it unions `ai_provider_models` with whatever is
already there rather than overwriting, so a model recorded by hand survives.

Two rules that follow from where the values come from:

- **Run it before you commit, and stage its edit with the content edit.** A file with uncommitted
  changes gets today's date, because today is when the commit you are about to make will land.
  Running it *after* committing cannot converge: stamping the dates is itself a change to every
  page, so the commit recording them moves each file's last-commit date one commit further on, and
  check 17 then flags the lot.
- **`ai_provider_models` entries are provider-qualified** — `anthropic/claude-opus-5`, not
  `Claude Opus 5` and not a bare `claude-opus-5`. `validate-content.js` check 17 warns on entries
  without the `provider/` prefix, on any of the three fields missing, and on a `date_modified`
  that has fallen behind the file's last commit.

The generated commentary cross-reference pages are deliberately exempt: they carry
`commentary-index:auto-start` and are rewritten on demand by `commentary_index.py`, so a
provenance record on them would describe a script run rather than authorship. The refresh script
and the validator both skip them on exactly that marker.

## Frontmatter failures worth checking

- The three provenance fields missing, or `date_modified` older than the file's last commit. The
  fix is always the same one command above; `npm run validate` from `app/` will tell you.
- `primary_passage` or `bible_references` missing — the study is then invisible to
  `commentary_index.py` and silently under-reports in the cross-reference index.
- Surviving template placeholders: `tag1`/`tag2`, `"Brief description of the page content"`,
  `bible_references: ["Genesis 1:1"]`, `zadok_year: 0`, `gregorian_year: -4004`. All five shipped
  intact on a real published file once — the effect was an empty published page cross-linked into
  Genesis 1's commentary and sitting at 4004 BC as the first entry on the prophetic timeline.
  `zadok_year`/`gregorian_year` are read by `app/scripts/build-events.js`, **which does not filter
  drafts**, so a bogus year reaches the timeline even on a `draft: true` file. Omit those two fields
  entirely unless the study is genuinely dated.
- `draft: false` on a file with no body, or with a `todo:` marker still in it.
