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

**Land the line on what the doctrine makes of the reader, not on the status of the argument.** The
draft of `bride-of-christ.md` ended its thesis *"…which is what makes the waiting a confident one"*
— a verdict on an inference. The site's author added: *"And the remaining set the church in an
attitude of joyous hope."* Same doctrine, and now the sentence says what the church is *like*
because of it. This is [style-guide.md](../develop-bible-study/style-guide.md) rule 6 applied at the
one place a reader is guaranteed to look: finish *"so the church / so you ___"* and put the answer
in the line. Writing this summary is a safe operation for this pass, so it is the one sentence here
you are authorised to get right.

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

**9. An opening spends its words on the subject, never on the study's method.** The published
opening of `bride-of-christ.md` carried this, and the site's author cut it whole:

> So this study sorts the evidence into tiers and tells you which tier you are standing on. The
> doctrine is strong. It does not need the weak arguments, and it is better off without them.

The tiers are real and they are the best thing in that study. A reader still meets them, in the
section that does them. What the paragraph cost was the opening — the position where the reader
decides what the page is about — spent on the page instead of on Christ. Note that the same
sentences would be unremarkable in a methods note halfway down. **The style guide already
prohibits the study talking about itself as a *habit*; in the opening it is a placement fault, and
one instance is enough to do the damage.**

**This rule reports; it does not act.** Cutting those sentences is editing, and this pass changes
no sentence. Name it in the report, quote the paragraph, and say the opening is spent on method —
then leave it for the author or for a develop/review pass.

**10. A large study opens with a Study outline — a briefing, not a table of contents.** At
**5,000 words and 8 or more `##` sections**, a reader can no longer hold the shape of the page in
their head. That threshold is a corpus measurement: 9 of 77 content pages clear both bars, and the
second bar matters on its own — `world-population-declares-gods-creation.md` is 6,132 words in only
6 sections and does not need one, while `sorcery.md` is 5,810 words across 19 and does.

Put it directly after Key Takeaways, as a short bulleted list of the major sections. mkdocs-material
already renders a table of contents from the headings, so an outline that only repeats the headings
has bought nothing. What it adds is the three things a generated TOC structurally cannot do:

- **It annotates.** "This is the main takeaway of the study" is a judgment about what matters.
- **It groups.** Eight sequential components go on *one* line as a single idea, where the TOC is
  obliged to give eight equal rows.
- **It locates the reader.** "The first four are already done to you; the fifth is where you are
  standing now."

> ## Study outline
>
> This is quite a big study. Feel free to jump around.
>
> - [The bride of Christ in Scripture](#where-scripture-says-it-itself). Discussion on how
>   extensive the pattern is in Scripture.
> - **The eight components, a section each** — [1 Purchased](#1-purchased) · [2 Betrothed](#2-betrothed)
>   · … · [8 Homed](#8-homed). The first four are already done to you; the fifth is where you are
>   standing now.
> - [Annex: sources, word studies and cautions](#annex-sources-word-studies-and-cautions). Useful
>   material that helped build the body.

**Write descriptive annotations; leave evaluative ones to the author.** This is the rule that keeps
the section honest, and it is the one an agent will break. "Discussion on how extensive the pattern
is in Scripture" restates what the section does, and is yours to write. "This is the main takeaway
of the study, and most enjoyable" is a verdict on the study's own content — the site's author wrote
that line, and an agent producing it is inventing a judgment it has no standing to make. Where an
evaluative note would earn its place, leave the bullet descriptive and say so in the report. A page
of confected enthusiasm is worse than the generated TOC it was meant to improve on.

**Verify every anchor against a built page, never by deriving the slug.** The outline is the one
section made entirely of in-page links, and two ways of getting them wrong are silent: raw heading
text (`#Where Scripture Says It Itself`) renders as a link and goes nowhere, and non-ASCII is
stripped, so `### The Spirit as deposit: ἀρραβών` is `#the-spirit-as-deposit-arrabon` and not what
the Greek suggests. Build the site and diff the `href="#…"` set against the `id="…"` set.

**11. Apparatus goes in an annex, after the teaching.** Source-weighting, correctives, and a source
that underwrites several sections at once are all material a reader consults rather than reads
through. Left in sequence they sit between the teaching and the reader: `bride-of-christ.md` had
1,364 words of it between its spine and its body, and the reader crossed 48% of the page before
reaching what the study was for.

Move it to a single `## Annex:` section after the last teaching section and before Discussion
Questions, which belong with the teaching they examine — every other study in this corpus puts its
questions directly after its final teaching section. Three tests for whether something is apparatus:

- Would a reader who trusts the study skip it and lose nothing? (Song-of-Songs source-weighting.)
- Does it serve several sections at once, so filing it under one would strip the others?
  (Tobit witnesses to components 2, 7 and 8.)
- Is it about what the study does *not* rest on? (The popular-teaching corrective.)

**Load-bearing framing moves with its material; it is not deleted.** Dissolving a section orphans
the paragraph that introduced it. Move it to wherever its content went, and write at most one brief
line of new framing where a section genuinely needs one — then flag every such line in the report,
because a structural pass that quietly writes paragraphs is no longer a structural pass.

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
