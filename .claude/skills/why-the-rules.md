# Why the rules exist

The skills state each rule once and keep at most a clause of the case behind it. This file holds
the case: the mistake in this corpus that the rule was written to stop. An agent doesn't need it to
follow a rule; read it when a rule seems arbitrary, before loosening one, or when writing about the
method for readers.

## Develop

### Develop state file

**The state file is a record, not a verification.** A `MAIN FINDING` block in one study's state
file carried a bad citation into the published prose, and the error survived a self-check that
consisted of re-reading the notes. The trail confirmed the error in the author's own hand.

### Develop revision

**Re-run the style guide after every revision.** On `day-is-a-thousand-years.md`, three
narrated-argument constructions reappeared within the hour in paragraphs the same agent had just
cleaned.

## Review

### Review phase 2

**Name the version.** Re-fetching `bride-of-christ.md`'s Mishnah through `references/build/sefaria.py`
with a named version found the study quoting *m. Ketubot* 5:2 as "to prepare herself with clothes
and jewelry". That is the William Davidson Edition's wording, and it is absent from Kulp's ("to
prepare herself for marriage"). The study had fetched from the web API, which serves Davidson by
default.

### Review phase 4

**Check the claim, not just its parts.** `last-things/day-is-a-thousand-years.md` asserted "Day
three's two events, in order, are the third millennium's two events, in order." Both lexical links
under it (*yabbashah*, *zera*) were verified in Phase 1 and re-derived in Phase 3, and both were
right. The ordering was wrong: Genesis day three runs land (Genesis 1:9-10) then seed (Genesis
1:11-12), while the millennium it was matched to has the promise of both together at Genesis 12:7
and reaches dry ground only at the Exodus, centuries later. It was caught while cutting the
sentence for style, which is luck, not method.

### Review siblings

**Compare the study with the site's other studies.** `rapture.md` had Noah removed before the flood
in one section and preserved through it in four others, while `olivet-discourse.md`, which it links
to, had settled the question the other way with lexical evidence. `day-is-near.md` prayed a reading
of Mark 13:32 that a sibling study exists to refute. Every one of those files had passed review on
its own.

### Review phase 8

**A green validate run is not a style pass.** *"Note what this is. It is not a mystical flourish;
it is an exegetical solution"* (an announcement stacked on a straw alternative, two tells in one
sentence) passed a full review of its file, because no regex matched it. The guide lists *"Notice
that…"*; a reviewer grepping for that literal missed its twin.

## Style guide

**Rule 5, define affirmatively, is a prohibition because detection failed.**
`christian-life/prayer-as-communion.md` carried 38 antithesis constructions (18 `, not ` and 20
`rather than` in 8,000 words, one every 210) after two full adversarial reviews and a clean
validate. The count went *up* between revisions: the agent that had just cut them wrote more within
the hour.

**Rule 6 has no symptom to search for.** The hedging vocabulary you would think to ban (*in some
sense*, *can be seen as*, *points toward*, *arguably*) appears in single figures across about 90
files. Every real instance was a sentence that was accurate, unhedged, and missing the name.

**Rule 7 came from a reader.** A reader tried reading `bride-of-christ.md` aloud to his wife and
stopped: "it sounds too vague and sparse… a sentence that has a lot of words but didn't have much
substance." Measured against Paul (WEB):

| | avg | median | ≥35 words | nominalisations | "you" |
|---|---|---|---|---|---|
| `bride-of-christ.md` | 25.0 | 22 | 24.8% | 25.6/1k | 9.2/1k |
| Ephesians 5 | 23.4 | 20 | 16.7% | 21.4/1k | 17.8/1k |
| Romans 12 | 20.2 | 10 | 15.0% | 19.8/1k | 32.1/1k |
| Philippians 4 | 17.4 | 15 | 7.4% | 14.8/1k | 48.6/1k |
| 1 Corinthians 13 | 18.0 | 13 | 6.7% | 3.6/1k | 0 |

1 Corinthians 13 has no "you" by design, and the lowest nominalisation rate; it is the most quoted
chapter Paul wrote.

**Rule 8's quotation half is the half that gets broken.** The repo once shipped an ESV "honored"
anglicised to "honoured". The capitalisation convention is measurable: across Psalms, Isaiah, John,
Romans and Hebrews, `He`/`Him`/`His` make up 63% of third-person masculine singular pronouns in the
NKJV, NASB, LSB and BSB, 52% in JPS, 39% in YLT, and 1-4% (sentence-initial capitals only) in every
translation that doesn't capitalise. Hebrew and Greek have no capitals, so the source settles
nothing.

**`worth ___` reached 48.** An audit of `docs/content/` found the other tell families at 0-3
instances each and this one at 48, because the guide listed three specimens ("Worth noting", "It's
worth asking whether", "One further point worth making") and writers avoiding those three still
wrote "it is worth being clear that". That is why the guide teaches shapes.

**The virtue contrast's other connectives.** *"Every cut-off here was set by measurement, not by
taste"* stood in `about/how-we-cross-reference.md` through a full review and a green validate: *not
by taste* charges an alternative nobody proposed, and the table beneath it already showed the fact.

**The hedging shapes came from one file.** `last-things/rapture.md` carried, at review, 29 "rather
than", 16 disclosure frames in 283 lines, "this is typology, not proof" four times, a 344-word
bullet, and "this study…" 19 times. Two of its four discussion questions asked the reader to grade
the page's handling of itself.

**The apologia posture triggers no check.** `about/why-ai-assisted-study.md` raised zero validator
warnings while being, top to bottom, a defence against an accusation nobody had made ("You deserve
to know that…").

**Narrated argument returns in revision.** See [Develop revision](#develop-revision): four instances
cut in one pass on `day-is-a-thousand-years.md`, three back within the next two revisions.

**`exactly` as emphasis.** A 2026-10-09 tidy of `numerology.md` cut it from 8 instances to 1.

## Read

**A guide of prohibitions produces prose that is defensible, not readable.**
`scribe-trained-for-the-kingdom.md` passed all twenty validator checks of the time with zero
findings and arrived as a wall: 17 sections, median 278 words, four over 400, the longest 669. A pass
that changed no prose (one summary line, eighteen sub-headings, one regrouping) took it to 28
sections, median 180, one over 400. Nothing in the toolchain could say the draft was hard to read.

## Diagrams

**The width budget was measured, not guessed.** On 2026-09-04, 29 mermaid blocks in 15 files were
measured; twelve rendered under 50% and all twelve were rewritten that day. The widest went from
3725px to 1178px.

| Was | Now | File |
|---|---|---|
| 3725 (15%) | 1178 (48%) | `about/about-our-datasets.md` |
| 3265 (17%) | 276 (100%) | `last-things/olivet-discourse.md` |
| 2084 (27%) | 558 (100%) | `about/site-architecture.md` |
| 1975 (29%) | 826 (68%) | `chronology/combined-timeline.md` |
| 1910 (29%) | 518 (100%) | `last-things/prophecy-chart.md` |
| 1638 (34%) | 269 (100%) | `israel-and-church/bride-of-christ.md` |
| 1407 (40%) | 276 (100%) | `last-things/rapture.md` |
| 1162 (48%) | 857 (66%) | `feasts/last-supper-four-cups.md` |

**`timeline` was exempted, and the exemption was the hole.** That sweep skipped `timeline` blocks
on the grounds that they "size themselves". They don't: the five on the site measured 1390–2790px
and rendered at 20–41%, and their per-section text colours (`.section-0 text{fill:black}`) left black
text on the dark theme. All five became `flowchart TD` on 2026-09-06:

| Was | Now | File |
|---|---|---|
| 2790 (20%) | 346 (100%) | `chronology/world-population-declares-gods-creation-and-biblical-truth.md` |
| 2390 (24%) | 346 (100%) | `chronology/combined-timeline.md` |
| 2190 (26%) | 552 (100%) | `last-things/rapture.md` |
| 1990 (28%) | 276 (100%) | `last-things/prophecy-chart.md` |
| 1390 (41%) | 249 (100%) | `last-things/day-is-near.md` |

**Why `about-our-datasets.md` stays at 48%.** Collapsing its two databases into one cluster reached
952px, but erased the trust-tier separation the page exists to state and moved TWOT into the
restricted tier, which the page's own "TWOT: one source, split across two tiers" section contradicts.
