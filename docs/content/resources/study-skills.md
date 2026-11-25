---
title: "The Study Skills"
category: "other"
description: "The written instructions the AI behind this site follows to build, check, structure and shorten a study, explained in plain words, with links to the full text of each."
tags: ["ai", "study-method", "getting-started"]
draft: false
date_created: 2026-11-24
date_modified: 2026-11-25
ai_provider_models:
  - anthropic/claude-opus-5.5
---

# The Study Skills

**In one sentence:** every study on this site is built, checked, shortened and arranged by an AI
following four written sets of instructions, called skills, and each one does a single job under a
single rule you can read for yourself.

A skill is a set of instructions an AI assistant loads before a task. The model chooses none of the
method here: the skills set it, and they are the same for every study. They are written to an AI, so
they read like a checklist. This page says what each one is for. The full text of each is linked
under it, and [Why the rules exist](https://the-way.lewy.au/skills/why-the-rules.md) gives the
mistake behind each rule.

## The four study skills

Each answers one question about a study, in this order:

| Skill | The question | Its rule |
|---|---|---|
| [Develop](#develop-build-the-study) | What does the passage say, and what does it mean for us? | Exegesis before application |
| [Review](#review-is-it-true) | Is every claim in it true? | Re-check every claim from its source |
| [Simplify](#simplify-is-it-the-right-size) | Is it the right size for its point? | Add nothing |
| [Read](#read-can-it-be-read) | Can a person follow it? | Change no sentence |

### Develop: build the study

Fee and Stuart's method from *How to Read the Bible for All Its Worth*, written as steps: first what
the text meant to its first readers, and only then what it means now. The assistant may draft no
application until the exegesis is done.

1. Set the passage, name its genre, and list what this site has already written on it.
2. The historical setting: author, audience, date and occasion.
3. The literary setting: what comes before and after, and the parallel accounts.
4. The words in Hebrew or Greek, the grammar where it changes the meaning, and the questions the
   genre asks (a proverb is read differently from a promise).
5. The bridge to today, checked against the [Statement of Faith](../about/statement-of-faith.md)
   only after the principle is drawn from the text.
6. Cross-references and translations, with commentaries consulted last.
7. The point in one sentence, an outline and a word budget, shown to the author before any drafting.
8. The site's automatic checks, then a hand-off to Review.

A working file beside each study records every step, so the work can be picked up later. Each study
shows that record in a "How this study was checked" panel above its references.

[Read the Develop skill](https://the-way.lewy.au/skills/develop-bible-study/SKILL.md) · its
[style guide](https://the-way.lewy.au/skills/develop-bible-study/style-guide.md),
[word-study method](https://the-way.lewy.au/skills/develop-bible-study/word-study-method.md) and,
for prophecy, [reading a prophecy forward](https://the-way.lewy.au/skills/develop-bible-study/prophecy-method.md)

### Review: is it true?

The reviewer treats every claim as unproven until it has been checked again from the source, and
fixes nothing until the whole list of findings is written. An assistant that edits as it reads stops
looking hard at the parts it has already tidied.

1. Every quotation of Scripture, against the printed translation.
2. Every citation, Strong's number, link and named source, including which edition was quoted.
3. Every word study, with its counts re-run.
4. The claims the study makes for itself: "these match", "in order", "only here", "every", and any
   arithmetic. Each part of such a claim can be true while the claim is false.
5. A commentary the study did not cite, to test its main reading.
6. Context: genre, setting, the passage around it, and the site's other studies on the same verses.
7. Placement, tags and frontmatter.
8. A pass over the prose with the style guide.

[Read the Review skill](https://the-way.lewy.au/skills/review-bible-study/SKILL.md)

### Simplify: is it the right size?

Every review finds something to add, so studies only grow. This skill is the pass that goes the other
way, and it may add nothing: no new fact, claim or citation. It writes the study's point in one
sentence, maps every section against that point, and proposes moving a side topic into a study of
its own, keeping a point made twice in one place, or shortening a wordy passage. The author approves
each move before any is made. The usual budget is 4,000 words, about 27 minutes read aloud.

[Read the Simplify skill](https://the-way.lewy.au/skills/simplify-bible-study/SKILL.md)

### Read: can it be read?

A study can pass every check and still arrive as a wall of text. This pass changes headings, grouping
and order, and no sentence. It runs last, in a separate session from the drafting, because the writer
of a study knows what each section means and so cannot see where a stranger gets lost. It reads the
study as a stranger first, then measures section lengths, restructures, and confirms with a script
that the sentences are unchanged.

[Read the Read skill](https://the-way.lewy.au/skills/read-bible-study/SKILL.md) · its
[structure rules](https://the-way.lewy.au/skills/read-bible-study/structural-readability.md)

## Two more

- **One-minute comic** draws a study's point as a short comic. Every speech bubble is Scripture as
  printed or shortened from it, and a character the text gives no words to says nothing.
- **Youth** cuts a published study down for readers aged 8 to 16 under the rule "say nothing the
  study does not".

Both depend on this site's own drawing tools, so their text is kept with the
[site's source](https://github.com/ding0t/bible_studies/tree/main/.claude/skills).

## Using them yourself

The skills call on this site's Bible database tools by name, so they run best in the
[workbench Getting Started sets up](getting-started.md). An assistant connected to the site's public
connector receives the four study skills as ready-made prompts
([For AI Assistants](../about/for-ai-assistants.md)). In an ordinary chat, the
[prompt card](guiding-ai-in-bible-study.md#the-prompt-card) carries their main rules in a form any
assistant can follow, and [Spot the Mistake](spot-the-mistake.md) gives practice in catching what
they catch.
