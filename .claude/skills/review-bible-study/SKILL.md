---
name: review-bible-study
description: Critically audits an existing study, commentary, or sermon file in docs/content/ -- scripture-quote accuracy, citation accuracy, word studies re-verified against source, the study's own synthetic claims (correspondences, orderings, counts, arithmetic) verified independently, claims cross-checked against a commentary, exegesis-context coverage per how-to-read-the-bible.md, taxonomy placement, frontmatter and tag correctness, and a style-guide pass. Use when the user asks to review, audit, fact-check, critique, double-check, or verify an already-drafted or already-published study -- as opposed to develop-bible-study, which builds a new one.
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

## Phase 4 — The study's own claims

Phases 1–3 all check a claim against a **source**. This phase checks the claims that have no source:
the ones the study constructs itself, on top of correctly-quoted verses and correctly-derived word
studies. For any study whose distinctive contribution is a typological mapping, a chronology, or a
pattern argument, this is most of what the reader came for, and nothing above covers it.

**Extract them into a list, away from the prose, before checking any of them.** Two things make this
phase hard, and both defeat reading. A synthetic claim is usually the most rhetorically polished
sentence in its paragraph — it is where the writer landed the point — and polish reads as confidence.
And where the reviewer is also the author, re-reading supplies the relation that was *intended*
rather than the one that was *written*.

What to enumerate:

- **Correspondence claims** — "X answers to Y," "the same word appears in both," "these two events
  are those two events." Check the correspondence, not the things being corresponded. Both halves can
  be individually accurate and the relation between them still false.
- **Ordering and sequence claims** — "in order," "in the same order," "first … then." These fail
  silently, because a reader assumes anyone who wrote "in order" counted. Lay the two sequences out
  side by side and compare positions.
- **Quantity and frequency claims** — "six times in six verses," "four times," "the only place in
  Scripture," "never elsewhere." Re-run the count. Phase 3 covers this for original-language terms;
  the identical claim made about English words, books, events or people is not covered there.
- **Arithmetic** — dates, spans, totals, era conversions. Recompute; a wrong sum looks exactly like a
  right one.
- **Uniqueness and exhaustiveness** — "the only," "no other," "every," "always." Cheapest to write,
  most expensive to verify, and therefore usually written unverified.

**A false synthetic claim is Critical**, level with a misquoted verse. The study asserts it in its own
voice, so there is no source to carry the blame and nothing external for a reader to check it against.

**This is not hypothetical.** `last-things/day-is-a-thousand-years.md` asserted "Day three's two
events, in order, are the third millennium's two events, in order." Both lexical links underneath it
(*yabbashah*, *zera*) were verified in Phase 1 and re-derived in Phase 3, and both were correct. The
ordering was not: Genesis day three runs land (1:9-10) then seed (1:11-12), while the millennium it
was matched to has the promise of both together at Genesis 12:7 and reaches dry ground only at the
Exodus, centuries later. The sentence survived a complete review because every phase checked its
parts and no phase checked its claim. It was eventually caught while cutting the sentence for
*style* — which is luck, not method, and is why this phase exists.

## Phase 5 — Commentary cross-check

- From the study's `primary_passage`, query `study-notes.db` for a commentary the study's own
  **References & Recommended Reading** section does *not* already cite for that passage, if one covering
  it exists. The point is an independent check, not confirmation from a source the study already leaned
  on to reach its own conclusions.
- Compare the study's central claims — the stated theological principle, and the load-bearing
  exegetical moves it depends on — against what that commentary says. Report one of three outcomes per
  claim checked: **confirms**, **silent** (neither supports nor contradicts), or **complicates/contradicts**.
- A contradiction against a central claim is a **Critical** finding, not a footnote.

## Phase 6 — Context coverage

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

A study can pass every check in Phases 1–5 — every quote and citation accurate — and still fail this
phase by skipping straight to application. That is precisely the failure mode
[how-to-read-the-bible.md](../../../docs/content/scripture/how-to-read-the-bible.md) and SKILL.md's "one
rule that governs everything" exist to catch, so don't skip this phase because the sourcing already
checked out clean.

## Phase 7 — Placement, frontmatter & tags

Cheap to check, and the failures are invisible from the page itself — they show up as a study missing
from an index, or a wrong entry on someone else's page.

Audit the file against
[placement-and-tags.md](../develop-bible-study/placement-and-tags.md) — the same rules develop-bible-study
drafts to, applied backwards. Work through its three parts:

- **Placement.** Is the file in the section its subject actually belongs to, or parked where a
  *related* study lives? If it genuinely belongs in `salvation/` or `biblical-figures/` — defined but
  not yet created — raise that as a finding rather than leaving it misfiled.
- **Tags**, against [docs/content/tags.md](../../../docs/content/tags.md), the live vocabulary. The
  hits to look for: tags restating the section, facets written flat (`word-study` for
  `method/word-study`), colons, uppercase/spaces, near-synonyms, and a person carrying the bare name
  of a book.
- **Frontmatter**, per that file's "Frontmatter failures worth checking."

**Severity.** These are **Minor** by default, with two exceptions that are **Major** because they
corrupt a generated page elsewhere on the site: a missing `primary_passage`/`bible_references` (the
study goes silently under-reported in `commentary_index.py`'s cross-references), and a surviving
`gregorian_year: -4004` placeholder (plants a false entry on the prophetic timeline — and
`build-events.js` does not filter drafts, so `draft: true` will not contain it).

## Phase 8 — Style guide pass

Run [style-guide.md](../develop-bible-study/style-guide.md) against the file: bare intensifiers, grader
adjectives, narrated-argument phrases, overused contrast rhythm, em-dash density, rule-of-three padding,
and — the brevity check — sentences that don't survive being deleted. Also confirm the section order
from develop-bible-study's Phase 7 (short hook → **Key Takeaways** → detail → … → References & Recommended
Reading).

**Do the reading test, and do it before any grep.** style-guide.md's own instruction — notice what you
**skim** — is the check that catches this entire category, and it cannot be run from a terminal. Read
the prose start to finish and mark every sentence your eye slides past to get to the content. That
reflex *is* the finding; it is the same thing the reader will do.

**A clean `npm run validate` does not mean the file passed this phase.** Its style checks are four
narrow regexes — Check 10 `worth ___`, Check 11 the "rather than" virtue contrast, Check 12 bullet
length, Check 13 reader-reassurance address. The narrated-argument family, the apologia posture, the
restated conclusion and the straw-alternative contrast match none of them, and style-guide.md says so
outright: the shapes it cannot detect mechanically "are on you." Treating a green validate run as
coverage is exactly how *"Note what this is. It is not a mystical flourish; it is an exegetical
solution"* — an announcement stacked on a straw alternative, two tells in one sentence — passed a
full review of the file it was sitting in.

**Learn the shape, not the examples.** style-guide.md makes this point about `worth ___` and it
generalises to every tell on that page: a reviewer grepping the guide's literal specimens will miss
every variant of them. *"Notice that…"* is listed there; *"Note what this is"* is not, and they are
the same sentence.

Findings here are **Minor** one at a time; a style issue is never as severe as a wrong Bible quote.
Raise it as **Moderate** when the register is *pervasive* rather than local — style-guide.md exists
because prose that reads as machine-generated "undercuts the reader's trust in the research
underneath," and that damage scales with density, not with any single hit.

## Reporting

Findings, most severe first:

- **Critical** — wrong scripture text, a citation that doesn't say what's claimed, a broken translation
  label, a false synthetic claim the study makes in its own voice (Phase 4), a commentary that
  contradicts a central claim, or Hebrew/Aramaic text broken by markdown bold (see Phase 2). These
  block `draft: false` (or, for an already-live file, warrant fixing promptly).
- **Moderate** — a Phase 6 context gap (e.g., cultural-vs-transcultural never made explicit), a stale
  word-count claim that's directionally still true but numerically off, a cross-reference that's weaker
  than stated, or a pervasive style-register problem (Phase 8).
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
