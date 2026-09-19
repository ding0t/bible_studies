# Structural readability — the positive counterpart

The reference page for **[read-bible-study](SKILL.md)**. That skill is the procedure;
this is the standard it applies.

[style-guide.md](../develop-bible-study/style-guide.md)'s "Structural readability" section lists five ways to structure
badly: bullets that are essays, the study talking about itself, the section recap, discussion
questions about the study's own method, the apologia posture. Every one is a prohibition.

Nothing there says how to structure *well*. This page is that counterpart, the way
[discussion-questions.md](../develop-bible-study/discussion-questions.md) is the counterpart to the prohibition on
method-questions.

## Why a separate page was needed

`scribe-trained-for-the-kingdom.md` passed **all twenty validator checks with zero findings** and
arrived as a wall: 17 sections, median 278 words, four of them over 400, the longest 669. A pass
that changed **no prose at all** — one summary line, eighteen sub-headings, one regrouping — took it
to 28 sections with a median of 180 words and one section over 400.

That is the whole lesson. A guide made of prohibitions produces prose that is *defensible* rather
than *readable*, because avoiding every listed failure is not the same as serving a reader. The
draft had nothing wrong with it. It was simply hard to read, and nothing in the toolchain could say
so.

Corpus audit behind the numbers below: 984 sections across 86 published files — p50 116 words, p75
225, p90 423, p95 545.

## The rules

**1. Give the reader the point before the evidence.** After the passage quote and before Key
Takeaways, one bold line stating what the study concludes:

> **In one sentence:** Jesus tells the Twelve they have been discipled into a scribal role that
> holds the whole Old and New revelation and is sent to spend it.

A reader who stops there should still have the answer. Check 14 already measures how long an
opening makes a reader wait; this is how you satisfy it deliberately rather than by luck.

**2. Aim at 250–400 words between headings.** That is roughly p75–p88 of this corpus, so it is
where the existing good sections already sit. Check 21 warns at 600 — the far tail, not the
target. A section past 400 words is usually two ideas that have not been separated yet.

**3. Name the content in the sub-heading, not the structure.** `### θησαυρός = storeroom` and
`### The 22 Matthew occurrences` tell a reader what is there. `### Analysis` and `### Background`
tell them nothing and make the table of contents useless.

**4. Let the structure mirror the subject's structure.** Three sequential sections on *storeroom*,
*brings out* and *new and old* became one parent — `## The householder's storeroom` — with three
sub-headings. Fewer top-level headings, and the shape of the page now shows that these are three
parts of one metaphor rather than three topics.

**5. Give a buried-but-important thing its own heading.** A paragraph marking a contested reading
as contested is doing the work AGENTS.md asks for, and it is invisible inside a 600-word run.
`### Confidence, marked` makes the honesty findable. Anything a reader would want to locate
deliberately needs a heading to locate it by.

**6. Never end a section on a table.** A table shows; it does not say. Precede it with the
one-sentence claim it supports and follow it with what it establishes. A reader who skims tables —
most do — should lose nothing.

**7. Open a section with its topic sentence, not with a citation.** *"Papias of Hierapolis names
him around AD 135…"* starts inside the evidence. *"The early church is unanimous that the tax
collector wrote this Gospel"* starts with the claim and then supports it.

**8. Write for two readers at once.** One wants the conclusion in thirty seconds; one wants the
word study. Headings and the one-sentence summary serve the first without costing the second
anything.

## Do this as a separate pass, not while drafting

This is the pass a drafting model is worst placed to do, and the reason is structural rather than
about effort.

A study is composed in the order its argument develops — for a one-verse study, usually the order
of the words in the verse. That order is correct *for composing* and it feels inevitable to whoever
composed it. Judging whether it is right *for reading* means arriving at the page as a stranger,
which the author cannot do and a second reader does for free.

So run it as a distinct step, after the draft is complete, asking only: where would a reader stop,
and can they find their way back in? Do not mix it with editing the prose. The pass that fixed
`scribe-trained-for-the-kingdom.md` changed zero sentences, which is exactly why it was safe.

## What this does not license

Readability is not an argument for rewriting the prose, and several plausible-sounding moves are
ruled out elsewhere in this skill:

- **Do not add bridge sentences** that announce what the next section will do. That is the
  `worth ___` narrating template (Check 10) and the study talking about itself.
- **Do not convert a reasoned paragraph into bullets** to make it look shorter. Check 12 exists
  because bullets that carry an argument become essays; prose that has become a list has usually
  lost its connective tissue.
- **Do not add a summary at the end of a section.** That is the section recap the style guide
  already prohibits. End on the last real point.
- **Do not name what a thing is not** in a heading. `### θησαυρός = storeroom, not just treasure`
  and `### New and old: time, not condition` are thesis-antithesis, ruled out at drafting by
  AGENTS.md's "define affirmatively". Write `### θησαυρός: the room, and what is kept in it`.

The safe operations are: add a heading, split at a natural break, regroup related sections under a
parent, move a table's context around it, and add the one-sentence summary. Everything else is
editing, and editing has its own rules on [style-guide.md](../develop-bible-study/style-guide.md).
