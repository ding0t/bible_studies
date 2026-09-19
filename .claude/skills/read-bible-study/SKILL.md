---
name: read-bible-study
description: Restructures an existing study, commentary, or sermon file in docs/content/ so a human can actually read it -- sub-headings that name their content, a one-line thesis before the evidence, related sections regrouped, tables given their context, an unbroken 600-word run broken up. Changes no sentence: structure, headings and placement only. Use when the user asks to make a study more readable, scannable, easier to follow, better structured, less of a wall of text, or asks for a readability or structure pass -- as opposed to review-bible-study, which checks whether the content is true, and develop-bible-study, which writes it.
---

# Make a Bible Study Readable

**develop-bible-study** writes a study. **review-bible-study** asks whether it is true. This skill
asks the third question: **can it be read?**

That is a separate pass because it has the opposite governing constraint to the other two.

> **Change no sentence.** Not one word of prose is added, cut or reworded. Headings, section
> grouping, placement and one summary line — nothing else.

Everything safe about this pass follows from that rule. A restructure that touches no prose cannot
introduce a theological error, a misquotation or a stale count, which is why its output can be
accepted without re-running a verification pass. The moment you start rewriting sentences you are
doing review-bible-study's job with none of its checks, and the result needs a full audit before it
can ship.

## Why this is not a phase of the other two skills

**It cannot be the author's own pass.** A study is composed in the order its argument develops —
for a one-verse study, usually the order of the words in the verse. That order is right for
composing and feels inevitable to whoever composed it. Judging whether it serves a *reader* means
arriving at the page as a stranger, which the author cannot do. Run this in a session that did not
write the draft wherever possible; that asymmetry is the whole mechanism.

**It cannot be review-bible-study's pass either.** That skill's posture is adversarial: find what
is wrong and change it. This one's safety is that it changes nothing. One skill cannot hold both
rules, and bundling them is how a structural pass acquires an editing licence it should not have.

**The cost is different.** review-bible-study re-queries every quotation against source. This pass
needs no source lookups at all. Bundled, you cannot fix a heading without paying for a full audit.

## What this pass does NOT do

Say this plainly in the report, because a clean structural pass reads like approval and is not:

**This pass verifies nothing.** It does not check a quotation, a citation, a count, a word study or
a doctrinal position. A study can be perfectly structured and wrong throughout. If the file has not
been through **review-bible-study**, say so in the report; do not let a green readability pass stand
in for an audit it never performed.

## Before starting

Get the target file (path or slug), or ask. Note whether it is `draft: true` or live.

If the user asked for a corpus sweep rather than one file, see **Corpus mode** below.

## Phase 1 — Read it as a stranger, before any measurement

Read the file start to finish, as a reader who has not seen it before and wants the point.

Mark, as you go:

- **Where you would stop.** Not where it gets difficult — where you would put it down. That reflex
  is the finding; it is what the reader will do.
- **Where you lost the thread** and had to scroll back to recover what a section was about.
- **What you skimmed**, and what you were skimming *toward*. A reader skimming toward something
  means the thing they wanted was buried.
- **Where you could not tell what a section contained** from its heading.

Do this before running any tool. The measurements below will tell you a section is 700 words; only
reading tells you that the 700 words are two ideas that were never separated.

## Phase 2 — Measure

```bash
cd app && npm run validate        # Check 21 flags any unbroken prose run over 600 words
```

Check 21 excludes tables, lists, block quotes and code, so a section already broken by
sub-headings never fires. **600 words is the far tail, not the target** — p96 of a corpus audit of
984 sections. Passing Check 21 is not evidence this pass was done; the aspiration is 250–400 words
between headings, which is p75–p88 of what this corpus already does well.

Cross-check the reading from Phase 1 against the numbers. Where they disagree, the reading wins: a
dense 500-word section that reads cleanly is fine, and a 300-word section a reader abandons is not.

## Phase 3 — Restructure

Apply [structural-readability.md](structural-readability.md). In short:

1. A one-line **In one sentence:** thesis after the passage quote, before Key Takeaways.
2. Aim at 250–400 words between headings.
3. Sub-headings name their **content**, not their function — `### The 22 Matthew occurrences`, not
   `### Analysis`.
4. Let structure mirror the subject: three sections on one metaphor become one parent with three
   sub-headings.
5. Give a buried-but-important thing its own heading — a contested reading marked as contested is
   invisible inside a 600-word run.
6. Never end a section on a table. Lead in with the claim, follow with what it establishes.
7. Open a section with its topic sentence, not a citation.
8. Serve the thirty-second reader and the word-study reader at once.

**The safe operations, exhaustively:** add a heading; split at a natural break; regroup related
sections under a parent; move a table's surrounding context; add the one-line summary. Anything
else is editing.

Read structural-readability.md's **"What this does not license"** before you start. Bridge
sentences, bulleting a reasoned paragraph, closing summaries and headings built out of what a thing
is not are all ruled out by rules this repo already holds — and all of them feel like readability
improvements while you are making them.

## Phase 4 — Verify you changed nothing but structure

This is the check that makes the pass trustworthy. Run it every time.

```bash
# Every non-heading prose line, before and after, must be identical as a set.
git show HEAD:<path> | grep -v '^#' | grep -v '^\s*$' | sort > /tmp/before.txt
grep -v '^#' <path> | grep -v '^\s*$' | sort > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

Three lines may legitimately appear in that diff and nothing else:

- the **In one sentence:** line you added
- an `ai_provider_models` entry, if you are recording your own provenance
- `date_modified`, which `refresh_frontmatter_provenance.py` rewrites

**Any other line is a prose change you did not intend** — revert it. A deletion (`<`) is always a
mistake here: the pass has no operation that removes a sentence.

Then:

```bash
cd app && npm run validate                          # Check 21 clean, no new warnings
python3 utils/refresh_frontmatter_provenance.py     # before committing, per AGENTS.md
```

## Phase 5 — Report

Lead with the measurements, because they are the honest summary of what changed:

- sections before → after, median section length before → after, sections over 400 words before →
  after
- the prose-line diff result, stated explicitly: *no sentence changed*
- **whether this file has been through review-bible-study**, and if not, that this pass says
  nothing about whether it is accurate

Then list what you could not fix without rewriting prose, as findings for review-bible-study or the
author: a section that needs a topic sentence it does not have, a heading whose content genuinely
has no single subject, a table with no claim to lead it. Do not fix these here.

## Corpus mode

For a sweep rather than one file:

```bash
cd app && npm run validate 2>&1 | grep -A1 "unbroken prose"
```

Nothing else in the toolchain owns these. `develop-bible-study` only touches new content, and
`review-bible-study` would make you pay for a full audit to split a section.

Work them worst-first, one file per pass, with the Phase 4 check on each. Do not batch several
files into one commit: the prose-identity check is per-file, and a batched diff hides a prose
change in the noise.

A live file (`draft: false`) that a reader is currently meeting outranks a draft.

## When to use this vs. the other two

- **develop-bible-study** — writing a new study. Its Phase 7 points here for the structure pass.
- **review-bible-study** — is the content true? Quotes, citations, word studies, claims, doctrine.
- **read-bible-study** (this skill) — can it be read? Structure only, no sentence changed, verifies
  nothing.

A new study normally wants all three: develop writes it, review checks it, this makes it readable.
Run this one last, and in a different session from the one that drafted it.
