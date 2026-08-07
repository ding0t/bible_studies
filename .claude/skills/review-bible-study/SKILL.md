---
name: review-bible-study
description: Critically audits an existing study, commentary, or sermon file in docs/content/ -- scripture-quote accuracy, citation accuracy, word studies re-verified against source, claims cross-checked against a commentary, exegesis-context coverage per how-to-read-the-bible.md, taxonomy placement, frontmatter and tag correctness, and a style-guide pass. Use when the user asks to review, audit, fact-check, critique, double-check, or verify an already-drafted or already-published study -- as opposed to develop-bible-study, which builds a new one.
---

# Review a Bible Study

**develop-bible-study** builds a study forward, phase by phase, ending in the author's own light
validate pass (Phase 8). This skill does the opposite motion: it goes back over a file that already
exists and treats every claim in it as unverified until re-derived from source — not a re-read for
typos, an independent re-check. The two skills are complementary, not overlapping: use develop-bible-study
to write something new, this one to find out whether something already written actually holds up.

**The discipline that makes this worth doing separately from Phase 8:** don't fix issues inline as you
find them. A reviewer who edits as they go stops scrutinizing the sections already "fixed" as hard as
the sections still ahead — exactly the bias a second, independent pass exists to avoid. Record every
finding (see **Reporting** below), and only fix once the user has seen the complete list.

## Before starting

Get the target file (path or slug) from the user, or ask. Note whether it's `draft: true` or already
live (`draft: false`) — a live file failing this review is a higher-priority finding than a draft one.

Look for a companion state file at `references/study-state/<slug>.yml`. If it exists, this review adds
to its research trail, not replaces it. If it doesn't — most likely a study written before this skill
or the develop-bible-study skill existed — say so in the report; don't backfill a research trail for
phases that were never actually tracked as they happened.

## Phase 1 — Scripture accuracy

Every quoted verse gets re-queried from source, not read for plausibility.

- **ESV/NIV/NKJV/CSB**: `study-notes.db`'s `verses` table (verse text, not just commentary notes) — see
  [references/README.md](../../../references/README.md#study-notesdb-commercial-study-bible-commentary-external-not-in-this-repo-at-all)
  for the access pattern; the `immutable=1` URI form is mandatory, not optional, under the sandbox.
- **WEB/ASV/YLT/LXX/MT and other `bible-text.db` translations**: `query.py verse` or the `bible_verse`
  MCP tool.
- Check three things per quote, not just the wording: (1) the text matches verbatim, punctuation
  included; (2) the cited reference is the verse actually quoted — a right quote under a wrong
  reference is as bad as a wrong quote; (3) the translation labeled is the translation actually queried.
  A real example this repo has already hit: a study drafted from memory had John 6:34 as "Lord, give us
  this bread" where the ESV reads "Sir" — see AGENTS.md's own note on this.
- For claims that cite a verse without quoting it, spot-check a sample: pull the verse and confirm it
  actually says what's claimed, not just that a legitimate-looking reference was attached to the claim.

## Phase 2 — Reference & citation accuracy

- **Cross-references.** For each "see also" link between two passages, briefly verify the linked
  passage actually supports the stated relation. A plausible-sounding cross-reference that doesn't say
  what's claimed is a common failure mode, not a rare one.
- **Extra-biblical citations** — TWOT root numbers, Strong's numbers, lexicon glosses, named
  commentaries. Spot-check against the source directly: `twot_root`/`twot_strongs` for TWOT, `bible_word`
  for Strong's id and gloss. A wrong TWOT root number is a citation to something that doesn't say what's
  claimed, and reads exactly like a correct one until checked.
- **Internal links.** Confirm every relative markdown link's target file and anchor actually exist on
  disk. A link to a renamed file or a heading that's since moved fails silently for the reader — there's
  no build error anywhere in this pipeline that would catch it.
- **Copyright/quotation-length.** Rough-tally how much of the file is quoted Scripture from any one
  restricted-percentage translation against the caps in
  [references/README.md](../../../references/README.md#two-different-permissions-dont-conflate-them)
  (NIV 25%, ESV/CSB/NKJV 50%, of the quoting work), and confirm commentary quotations stay at a sentence
  or two rather than a full note.
- **Hebrew/Aramaic wrapped in markdown bold.** Run `npm run validate` (from `app/`) and treat any
  `Hebrew/Aramaic text is wrapped in markdown bold` error as a Critical finding, not a style nit —
  see [style-guide.md's "Hebrew/RTL text and markdown bold"](../develop-bible-study/style-guide.md#hebrewrtl-text-and-markdown-bold)
  for why this actually breaks rendering (synthetic bold misplaces Hebrew vowel points) rather than
  just reading oddly. The source markdown looks completely ordinary — re-reading the file, even
  carefully, will not catch this; only the automated check (or viewing the built page) will. This
  bug has shipped to `draft: false` studies before.

## Phase 3 — Word studies, critically

Re-derive, don't re-read. This is the same rigor [word-study-method.md](../develop-bible-study/word-study-method.md)
demands when a word study is first built — reapplied adversarially to one someone (possibly you, in an
earlier session) already wrote.

- For every original-language term the study leans real weight on, re-run the concordance
  (`bible_concordance` / `query.py concordance`) and confirm the occurrence count and reference list the
  study states are what the corpus actually returns right now. A miscounted or stale "only N
  occurrences" claim undermines exactly the kind of argument (*trōgō*, *kophinos*/*spyris*) this site's
  strongest studies are built on.
- **Root-fallacy check.** Flag any claim resting on "the word literally/originally means X" to establish
  present-tense usage in the passage, instead of on synchronic (contemporary) usage.
- Check the gloss, Strong's number, and semantic-domain code against `bible_word`/`bible_domain`
  directly, rather than trusting the study's own citation of them.
- Where the study claims "no English translation preserves this" or similar, spot-check at least two of
  the translations it names. A specific-sounding claim isn't the same as a checked one.
- **Syntax/coreference claims get re-run, not re-read.** If a study leans on an implicit-subject
  resolution, a pronoun disambiguation, an emphatic-pronoun reading, or a Hebrew construct-chain claim —
  the kind of finding the MACULA clause-syntax/coreference annotation in `bible-text.db` produces (see
  [references/README.md](../../../references/README.md#clause-syntax-and-coreference-macula)) — re-query
  it with `query.py syntax` / `bible_syntax` rather than trusting the study's transcription of what the
  annotation said. Remember a `NULL` there means *not annotated*, never *no such role* — don't flag a
  claim as unsupported just because a fresh query returns nothing; confirm whether the verse is covered
  at all before treating silence as contradiction.

## Phase 4 — Commentary cross-check

- From the study's `primary_passage`, query `study-notes.db` for a commentary the study's own
  **References & Recommended Reading** section does *not* already cite for that passage, if one covering
  it exists. The point is an independent check, not confirmation from a source the study already leaned
  on to reach its own conclusions.
- Compare the study's central claims — the stated theological principle, and the load-bearing
  exegetical moves it depends on — against what that commentary says. Report one of three outcomes per
  claim checked: **confirms**, **silent** (neither supports nor contradicts), or **complicates/contradicts**.
- A contradiction against a central claim is a **Critical** finding, not a footnote.

## Phase 5 — Context coverage

Run the file against the six questions on
[how-to-read-the-bible.md](../../../docs/content/scripture/how-to-read-the-bible.md), one at a time, marking
each **covered**, **partial**, or **missing**:

1. Genre identified, and the genre-appropriate lens actually applied (not just named in passing)?
2. Historical occasion — author, audience, date, circumstance — present?
3. Literary context — immediate before/after, the unit of thought — addressed?
4. Original-language check present wherever a word is doing real theological work? (Overlaps Phase 3
   above; the question here is *coverage*, Phase 3's is *correctness*.)
5. Cultural-vs-transcultural line drawn *explicitly*, not just assumed?
6. Is the theological principle stated or taught elsewhere in Scripture, rather than resting on one
   narrative detail or incidental remark alone?

A study can pass every check in Phases 1–4 — every quote and citation accurate — and still fail this
phase by skipping straight to application. That is precisely the failure mode
[how-to-read-the-bible.md](../../../docs/content/scripture/how-to-read-the-bible.md) and SKILL.md's "one
rule that governs everything" exist to catch, so don't skip this phase because the sourcing already
checked out clean.

## Phase 6 — Placement, frontmatter & tags

Cheap to check, and the failures are invisible from the page itself — they show up as a study missing
from an index, or a wrong entry on someone else's page. Definition:
[our-taxonomy.md](../../../docs/content/about/our-taxonomy.md).

**Placement.** Is the file in the section its subject actually belongs to? Sections are top level —
`docs/content/<section>/`, no `studies/` wrapper. Check especially for a study parked in a section
because that is where a *related* study lives rather than because the subject fits. If it genuinely
belongs in `salvation/` or `biblical-figures/` — the two sections defined but not yet created —
that is a finding worth raising, not a reason to leave it misfiled.

**Frontmatter.** Flag any of these:

- `primary_passage` or `bible_references` missing — the study is then invisible to
  `commentary_index.py` and silently under-reports in the cross-reference index.
- Surviving template placeholders: `tag1`/`tag2`, `"Brief description of the page content"`,
  `bible_references: ["Genesis 1:1"]`, `zadok_year: 0`, `gregorian_year: -4004`. All five shipped
  intact on a real published file once. Treat a bogus `gregorian_year` as **Major**: it plants a
  false entry on the prophetic timeline, and `build-events.js` does not filter drafts, so
  `draft: true` will not contain it.
- `draft: false` on a file with no body, or with a `todo:` marker still in it.

**Tags.** Against [docs/content/tags.md](../../../docs/content/tags.md), the live vocabulary:

- Tags that restate the section (`studies`; `prophecy` on a `last-things/` page; `sin` on a `sin/`
  page). Redundant, and they inflate the index.
- Facets written flat instead of prefixed — `word-study` rather than `method/word-study`,
  `hebrew` rather than `lang/hebrew`, `peter` rather than `person/peter`.
- A colon in a tag value: `/` is the facet separator and a colon competes with it.
- Uppercase, spaces, or a near-synonym of an existing tag (`messianic` beside `messianic-prophecy`).
- **A person tagged with a bare name that is also a book** — `matthew`, `john`, `james`, `daniel`,
  `ruth` and friends. The bare tag belongs to the *book*; a person takes `person/`. This one is easy
  to miss because both tags are individually legitimate: check which the *page* is about. A page
  genuinely covering both (a profile of Matthew that also cites his Gospel) correctly carries
  `person/matthew` **and** `matthew`. Also flag a bare `person/james`-style tag where two Bible
  figures share the name — it should be disambiguated by patronymic.

These are **Minor** findings unless a missing `primary_passage` or a false timeline year is involved,
which are **Major** — both corrupt a generated page elsewhere on the site.

## Phase 7 — Style guide pass

Run [style-guide.md](../develop-bible-study/style-guide.md) against the file: bare intensifiers, grader
adjectives, narrated-argument phrases, overused contrast rhythm, em-dash density, rule-of-three padding,
and — the brevity check — sentences that don't survive being deleted. Also confirm the section order
from develop-bible-study's Phase 7 (short hook → **Key Takeaways** → detail → … → References & Recommended
Reading). This phase produces
**Minor** findings only; a style issue is never as severe as a wrong Bible quote.

## Reporting

Findings, most severe first:

- **Critical** — wrong scripture text, a citation that doesn't say what's claimed, a broken translation
  label, a commentary that contradicts a central claim, or Hebrew/Aramaic text broken by markdown bold
  (see Phase 2). These block `draft: false` (or, for an already-live file, warrant fixing promptly).
- **Moderate** — a Phase 5 context gap (e.g., cultural-vs-transcultural never made explicit), a stale
  word-count claim that's directionally still true but numerically off, a cross-reference that's weaker
  than stated.
- **Minor** — style-guide hits, padding, structural nits.

Present the list to the user before fixing anything. Once they've seen it and said which to act on,
either fix directly or hand back to develop-bible-study's drafting phase for anything substantial enough
to need re-drafting rather than a line edit.

**Record the review.** Append a dated `review_<YYYY-MM-DD>` block to the study's state file
(`references/study-state/<slug>.yml`) summarizing what was checked and what was found — the same pattern
this repo already uses for post-publish revision entries. This makes the review itself a resumable,
citable event instead of a chat transcript that evaporates. If no state file exists, say so in the
report rather than fabricating a research trail for phases that were never actually tracked live.

## When to use this vs. develop-bible-study

- **develop-bible-study** — building a new study, from scoping through drafting to first publish.
- **review-bible-study** (this skill) — auditing a study that already exists, whether freshly drafted,
  long-published, or flagged by the user for a second look, with the same rigor but adversarial rather
  than generative.
