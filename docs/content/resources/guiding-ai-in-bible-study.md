---
title: "Guiding AI in Bible Study"
category: "other"
description: "Seven habits for studying the Bible with an AI chat assistant, each learned from a mistake the AI behind this site actually made, and a prompt card to paste at the start of a conversation."
tags: ["ai", "study-method", "getting-started"]
draft: false
date_created: 2026-11-23
date_modified: 2026-11-23
ai_provider_models:
  - anthropic/claude-opus-5.5
---

# Guiding AI in Bible Study

**In one sentence:** an AI assistant writes a fluent answer whether or not it is true, so ask it for
things you can check: the verse as printed in a named translation, the Hebrew or Greek word with its
number, a count it actually made, the case against your view, and a list of what it could not verify.

An AI helps research and draft every study on this site. Each habit below became a written rule after
that AI made the mistake here, in a study that was then corrected. The mistakes are typical of these
tools, so the rules work in any chat assistant, with or without the
[workbench this site uses](getting-started.md). [AI in These Studies](../about/why-ai-assisted-study.md)
explains why the site uses AI at all and where its usefulness ends.

## Study outline

- [Make it quote, and name the translation](#make-it-quote-and-name-the-translation): a remembered
  verse looks exactly like a checked one
- [Name the edition of every other source](#name-the-edition-of-every-other-source): the wrong
  edition brings the wrong words
- [Ask for counts it made](#ask-for-counts-it-made): an empty search is an answer
- [Check the claim as well as its parts](#check-the-claim-as-well-as-its-parts): true pieces can
  make a false whole
- [Ask for the case against you](#ask-for-the-case-against-you): the assistant leans toward agreeing
- [Check in a fresh conversation](#check-in-a-fresh-conversation): re-reading its own notes confirms
  its own errors
- [Ask for plain sentences](#ask-for-plain-sentences): fluent prose can say very little
- [The prompt card](#the-prompt-card): all seven, ready to paste

## Make it quote, and name the translation

**What happened here.** A study drafted from the assistant's memory quoted John 6:34 as "Lord, give
us this bread". The ESV has "Sir". The wrong word sat in a quotation mark beside a verse reference and
read as checked.

An assistant reproduces familiar verses from what it absorbed in training, which mixes translations
and paraphrases freely. It will name a translation it did not use.

**Ask:** "Quote the verse exactly as it is printed in the ESV. If you cannot look it up, say so, and
I will check it myself." Then check it. A verse takes ten seconds to look up, and every reference on
this site opens in a pop-up for the same reason.

## Name the edition of every other source

**What happened here.** A study quoted the Mishnah (*m. Ketubot* 5:2) on a bride preparing herself
"with clothes and jewelry". Re-fetching it from a named translation, Kulp's, gave "to prepare herself
for marriage". The first wording belonged to a different English edition, the one a website served by
default. The wrong edition and the wrong words arrived together.

The same happens with church fathers, Josephus, lexicons and commentaries, which all exist in several
translations and editions.

**Ask:** "Which edition and translation is that quotation from, and where can I read it?" An
assistant that cannot name one is quoting from memory.

## Ask for counts it made

**What happened here.** While writing on the Olivet Discourse, the author wanted to link Matthew
24:35 ("heaven and earth will pass away") with Revelation 21:1 by their shared verb. A search of the
Greek came back empty: παρέρχομαι (*parerchomai*, par-ER-kho-my, G3928) never occurs in
Revelation. An assistant answering from impression would have offered a link that sounded right.

Claims such as "this word occurs six times", "the only place in Scripture" and "always means" are
the easiest for an assistant to write and the hardest for a reader to check.

**Ask:** "Give me the Greek or Hebrew word with its Strong's number, how many times it occurs, and
whether you counted or estimated." A free concordance such as the Blue Letter Bible or STEP Bible
lets you check the count by its Strong's number.

## Check the claim as well as its parts

**What happened here.** A study claimed that day three of creation and the third millennium of
history held the same two events "in order". Both word links underneath the claim were correct and
had been checked twice. The order was wrong: Genesis 1:9-10 has dry land and then Genesis 1:11-12
has seed, while the history it was matched with has the promise of land and seed together (Genesis
12:7) and reaches dry ground at the Exodus, centuries later. The claim survived a full review because
every check looked at its parts. It was caught by luck while the sentence was being shortened.

An assistant writes its own conclusions in its most confident sentences: "these two events are
those two events", "in the same order", "this answers to that".

**Ask:** "Lay the two lists side by side, item by item, and show me where each one matches." A
correspondence that holds survives being written out as a table.

## Ask for the case against you

**What happened here.** The author has come to passages sure of what they said, asked for the
counter-evidence, and watched the idea fall over. An assistant asked leadingly ("show me how this
verse teaches X") builds the case it was asked for, confidently.

"The one who states his case first seems right, until the other comes and examines him" (Proverbs
18:17, ESV).

**Ask:** "Make the strongest case against my reading from the text, its context and the original
language. Then tell me which parts of my reading survive, and mark what is settled and what is
contested." Contested means the text gives reasons on both sides; a study Bible disagreeing is a
reason to look, and the text decides.

## Check in a fresh conversation

**What happened here.** A wrong citation in the assistant's working notes went into a published
study, and the assistant's self-check passed it, because the check was re-reading those same notes.
Another study described Noah as removed before the flood in one section and kept through it in four
others; a sibling study it linked to had already settled the question. Each page passed review on
its own.

An assistant that drafted an answer reads it back as it meant it. Within one conversation it also
favours what it said earlier.

**Ask**, in a new conversation, with only the answer pasted in: "Check every quotation, reference
and count in this against the sources, and list what you could not verify as unverified." For a
larger question, ask how the answer fits the other passages on the same subject.

## Ask for plain sentences

**What happened here.** A reader tried one of these studies aloud and stopped partway: "a sentence
that has a lot of words but didn't have much substance." Another study, after two full reviews,
still carried 38 "this, not that" constructions in 8,000 words. The assistant that had just removed
them wrote new ones within the hour.

Assistants produce a recognisable register: long sentences, foils nobody proposed, hedges such as
"in some sense", and sentences that announce a point is coming. Each one sounds careful and holds
the point back.

**Ask:** "Write short sentences. Name the person, the doctrine and the verse. Say what a thing is
by giving an example or a citation, and leave out what it isn't." Then read the answer aloud. If a
sentence can go without losing a fact, a reference or a step of the argument, cut it.

## The prompt card

Paste this at the start of a conversation, then ask your question.

```text
Help me study the Bible. Follow these rules for the whole conversation.

1. Quote Scripture exactly as printed in a named translation (default ESV). If you
   cannot look a verse up, say so; never quote from memory as though you had checked.
2. Name the edition and translation of any other source you quote, and where to read it.
3. For a Hebrew or Greek word, give the word, its transliteration and pronunciation,
   and its Strong's number. For any count ("occurs N times", "the only place"), say
   whether you counted it or are estimating.
4. Study the passage in its own setting first: who wrote it, to whom, why, and what
   comes before and after. Only then say what it means for me.
5. When you claim two things correspond or happen in the same order, lay them side by
   side so I can see each match.
6. When I state a view, give the strongest case against it from the text before you
   agree. Mark what is settled and what is contested, and give the case on both sides
   of anything contested.
7. Give a reference, with its book named, for every claim.
8. Write plainly: short sentences, no padding, no announcing a point before making
   it. Say what a thing is with an example or a citation.
9. End each answer with a list of anything you could not verify.

You are a research assistant. You have no spiritual authority, and Scripture is the
judge of everything you say.
```

The rules ask the assistant for things you can check. They make it easier to check its answer, and
the checking is still yours, as the Bereans checked Paul himself: "examining the Scriptures daily to
see if these things were so" (Acts 17:11, ESV).

## Going further

- **[Getting Started](getting-started.md)** sets up the workbench this site is built with: the
  Hebrew and Greek texts in a database an assistant can query, so a quotation or a count comes from
  a row you can see.
- **The skills** are the full instructions the site's assistant follows, served as plain text:
  [develop](https://the-way.lewy.au/skills/develop-bible-study/SKILL.md) a study,
  [review](https://the-way.lewy.au/skills/review-bible-study/SKILL.md) one,
  [read](https://the-way.lewy.au/skills/read-bible-study/SKILL.md) one for structure, and
  [simplify](https://the-way.lewy.au/skills/simplify-bible-study/SKILL.md) one.
  [Why the rules exist](https://the-way.lewy.au/skills/why-the-rules.md) holds every mistake behind
  them, including the ones on this page.
- **[For AI Assistants](../about/for-ai-assistants.md)** is what this site tells an assistant a
  reader points at it, and how to connect one to the site's data.
