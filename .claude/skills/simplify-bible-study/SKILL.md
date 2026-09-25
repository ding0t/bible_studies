---
name: simplify-bible-study
description: Cuts an existing study, commentary, or sermon file in docs/content/ back to what it is trying to say -- names the one-sentence point, maps every section against it, then recommends forking tangents into their own studies, merging points made more than once, and tightening wordy passages, and applies what the author approves. Adds nothing. Use when a study is over its word budget (validator Check 23), when the user says a study is too long, wordy, repetitive, bloated, or hard to follow, or asks to simplify, shorten, split, or trim one -- as opposed to read-bible-study, which restructures without changing a sentence, and review-bible-study, which checks whether the content is true.
---

# Simplify a Bible Study

The four content skills each do one thing to a study:

| Skill | Does | Rule |
|---|---|---|
| develop-bible-study | builds it | exegesis before hermeneutics |
| review-bible-study | corrects it | re-derive from source |
| read-bible-study | rearranges it | change no sentence |
| **simplify-bible-study** | **shrinks it** | **add nothing** |

Every review pass finds something to add, so studies only grow. `bride-of-christ.md` went from
4,362 words to 14,393 in three weeks; `prayer-as-communion.md` from 463 to 10,084. A reader who
tried reading the bride study aloud stopped when it was a third of its current length. This skill
is the pass that goes the other way.

## The rule: add nothing

No new fact, claim, citation or argument. You may:

- **delete** a sentence, paragraph or section;
- **move** text verbatim, within the study or into a new study;
- **shorten** a sentence, keeping every fact and citation in it;
- write **one pointer line** where forked content used to be, and the **Study outline**.

Because of that rule, the only things a reviewer needs to recheck are the sentences you shortened.
List every one in the report.

## Phase 1: What is this study trying to say?

Write the point in one sentence, without looking at the file. If the study already has an
**In one sentence:** line, compare the two.

If you can't write it, or yours and the file's disagree, stop and tell the author. A study that
doesn't know its point can't be simplified, only shortened, and deciding the point is the
author's call.

## Phase 2: Map it

Give every `##` and `###` section one line in a table:

| Section | Words | What it says, in one line | Serves the point? |
|---|---|---|---|

Mark each **serves**, **supports** (needed by a section that serves) or **tangent** (true and
interesting, but the point stands without it). Then note every idea that shows up in more than one
section, with where each copy is.

The map is also the reader's mind map. The **serves** rows, in order, are the draft of the
`## Study outline` (structural-readability.md rule 10). If the study needs one and has none, add it.

## Phase 3: Recommend. Change nothing yet.

Get the budget from `word_budget` in `references/study-state/<slug>.yml`. If there isn't one, it's
**4,000 words**: about 27 minutes read aloud, one sitting with a family or small group. Count words
the way Check 23 does, with tables, block quotes, code and headings left out.

Recommend moves of three kinds, each with the words it saves:

1. **Fork.** A tangent with its own point becomes its own study. Give it a working title, its own
   one-sentence point, and the sections that move. Several tangents on one subject make one fork,
   not several.
2. **Merge.** An idea made in two or more places stays in the one where it does the most work. The
   other places lose it, or point to it in a clause.
3. **Tighten.** Wordy passages, judged by [style-guide.md](../develop-bible-study/style-guide.md)'s
   deletion test: cut the sentence and see whether a fact, a citation or a step in the argument
   went with it. Start with openings, section closers and transitions, where padding collects.

Total the savings and show the projected length against the budget. Forks usually close most of
the gap. If the study is still over budget after every move you believe in, say so and give the
reason. An author may set a higher budget; record it in the state file with the reason.

Present this to the author and wait. Which tangents are worth their own study is their call.

## Phase 4: Apply what was approved

- **Forks.** Create `docs/content/<section>/<new-slug>.md` with `draft: true` and a state file
  whose `stages` notes say where the text came from (file and commit). Move the text verbatim. Its
  word studies and quotations were verified where they came from, so don't redraft them here. The
  new study goes through develop-bible-study later to get its own opening and Key Takeaways.
- **The pointer.** A published page that links to a draft fails `mkdocs build --strict`, so leave
  the link out until the fork is published. Until then the pointer is plain text, or nothing.
  Record the pending link in the parent's state file under `open_questions`.
- **Merges and tightening.** Edit in place.
- Fix anything that pointed at removed text: in-page anchors, "see above" references, Key
  Takeaways entries, memory verses and discussion questions. Questions go stale silently when the
  section they examined leaves (see discussion-questions.md).

## Phase 5: Verify

```bash
cd references/build
uv run python study_structure.py <path> --verify-against HEAD
```

`removed` lists your cuts. `added_unexpected` must hold only the sentences you shortened, the
pointer lines and the outline. Anything else there is a new sentence, and the rule forbids it.

Then run `npm run validate` from `app/` and `mkdocs build --strict` (command in develop-bible-study
Phase 8).

## Phase 6: Report

- Words before and after, and the budget.
- The one-sentence point.
- Each fork: its new path and its point.
- **Every shortened sentence, old and new side by side.** This is the only part of the pass that
  needs a second reader.
- Append a dated `simplify_<YYYY-MM-DD>` block to the state file.

Run review-bible-study before simplifying, not after. Simplify only deletes and shortens verified
text, so the result doesn't need a fresh audit. Run read-bible-study afterwards if the remaining
sections need regrouping.
