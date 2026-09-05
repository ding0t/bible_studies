---
title: "Backlog"
category: "other"
description: "A public working list of study topics and research items still to be developed, organized by the site's own subject sections."
tags: ["backlog", "planning", "research", "development"]
draft: false
date_created: 2026-08-25
date_modified: 2026-09-05
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-sonnet-5
---

# Backlog

A running, public list of study topics and research questions on the list to develop — some are
just a title, others already have working notes. Organized by the site's own
[subject sections](our-taxonomy.md), in their published order, so a section only appears here if
it currently has something queued.

Refer to an item by its number, e.g. "work on 4.1."

## Quick reference

| Ref | Topic | Section |
|---|---|---|
| [1.1](#11-extra-biblical-texts) | Extra-biblical texts | Scripture |
| [1.2](#12-typed-scripture-links) | Typed scripture links | Scripture |
| [2.1](#21-prophecy-and-jesus) | Prophecy and Jesus | Jesus |
| [2.2](#22-priest-of-the-order-of-melchizedek) | Priest of the order of Melchizedek | Jesus |
| [2.3](#23-jesus-attitude-toward-women) | Jesus' attitude toward women | Jesus |
| [3.1](#31-nephilim) | Nephilim | Spiritual beings |
| [4.1](#41-assurance-of-salvation) | Assurance of salvation | Salvation |
| [4.2](#42-on-death) | On death | Salvation |
| [5.1](#51-tribulation-perspectives) | Tribulation perspectives | Last things |
| [5.2](#52-end-times) | End times | Last things |
| [5.3](#53-the-last-trumpet) | The last trumpet | Last things |
| [6.1](#61-appointed-times-overarching) | Appointed times (overarching) | Feasts |
| [6.2](#62-individual-feast-studies) | Individual feast studies | Feasts |
| [7.1](#71-twelve-disciples) | Twelve disciples | Biblical figures |
| [8.1](#81-mirror-the-unfoldingword-sources) | Mirror the unfoldingWord sources | Sources & tooling |

---

## 1. Scripture

### 1.1 Extra-biblical texts

- Which texts, from when, and why they're of interest
- Which ones are referenced in the Bible
- Which ones are deuterocanonical, and what that means
- Other known texts from Jewish heritage (across the patriarchs)
- Gad the Seer, etc.
- Dead Sea Scrolls
- Early church fathers

### 1.2 Typed scripture links

Scripture links to Scripture, and this site should be able to show that without borrowing anyone
else's theology to do it. The goal is **not** a graph database of other people's cross-references —
that data is already ingested and largely commoditised. The goal is to **type** the links by how
they can be established, keep the objective classes separate from the opinion-based ones, and join
them to the studies we've actually written, which is the one thing no other site can compute.

**Already done — don't re-acquire.** The OpenBible.info set is in `bible-text.db` as
`openbible-crossrefs` (via the `scrollmapper-bible-databases` submodule, `build.py`'s
`ingest_scrollmapper_crossrefs`): 415,433 distinct directed edges, votes from −31 to 1,268, 28,956
distinct source verses. It's agent-only today — `query.py crossref` and the MCP `bible_crossref`
tool, at Phase 6 of develop-bible-study. No reader ever sees it. The only reader-facing scripture
linking is `commentary_index.py`, which maps chapters to the studies citing them.

#### Edge classes, ordered by how objectively each can be established

The ordering is the point. An edge's class travels with it, and classes are **never summed into a
single "strength" score** — that is exactly how one tradition's reading gets laundered as data.

1. **Quotation** — the New Testament quoting the Old, verbatim or near enough. The most objective
   class, and the one to build first: it is a *textual* judgement, not a theological one. Computable
   as Greek n-gram overlap between `sblgnt` and the Brenton LXX (`ebible-grcbrent`), both already
   ingested and both `open` tier. Worked example: Luke 4:18 reads
   `Πνεῦμα κυρίου ἐπʼ ἐμέ, οὗ εἵνεκεν ἔχρισέν με εὐαγγελίσασθαι πτωχοῖς` against LXX Isaiah 61:1
   `Πνεῦμα Κυρίου ἐπʼ ἐμὲ, οὗ εἵνεκε ἔχρισέν με, εὐαγγελίσασθαι πτωχοῖς` — near-verbatim.
    - **The distinctive value-add is recording which text the quotation follows.** We hold the
      Masoretic (`morphhb-wlc`, `macula-hebrew-wlc`) *and* the LXX *and* the Greek NT, so a
      quotation edge can carry its Vorlage. That Luke follows the LXX rather than the Hebrew is a
      real exegetical fact a study can use, and it isn't in any cross-reference list.
    - **LXX coverage: resolved, and we already had the text.** The Brenton edition looked as
      though it lacked Daniel, Esther and Nehemiah. It doesn't — the Greek canon just puts two of
      them somewhere a USFM book code doesn't reveal, and the ingest was dropping them as
      "deuterocanonical". Daniel ships as *Greek* Daniel (`DNG`, and it's **Theodotion** — the form
      the NT generally quotes, confirmed at 1:3's Ἀσφανὲζ against the Old Greek's Ἀβιεσδρί), and
      Nehemiah is the back half of 2 Esdras inside `EZR` chapters 11–23. Both are now ingested.
    - **Daniel 9:24–27 aligns verse-for-verse with the WLC**, as do Daniel 1–2 and 5–12. Only
      chapters 3 and 4 diverge, and they are one problem seen twice: Theodotion inserts the Song of
      the Three after 3:23, and the chapter break then lands three verses late, so Greek Daniel
      4:1–3 *is* WLC Daniel 3:31–33. Never compare those two chapters verse-for-verse.
    - **Greek Esther is in too.** Its six additions ride on *lettered* sub-verses (1:1b–1s,
      3:13a–g, 4:17a–x, 5:1a–2b, 8:12a–u, 10:3a–k) exactly so the numeric verses keep the Hebrew
      numbering, so ingesting the numeric verses aligns eight of ten chapters with the WLC. The
      additions themselves aren't in the database — `verses.verse` is `INTEGER` — and Esther 1
      starts at verse 2, because Addition A's opening carries a plain numeric `1` that would
      otherwise put Mordecai's dream at an address reading "in the days of Ahasuerus" everywhere
      else. The LXX now holds all 39 protocanonical OT books.
2. **Rare-lemma allusion** — two passages sharing a lemma that occurs only a handful of times in
   the canon. Objectively gradeable by corpus frequency, and it surfaces allusions crowd-voting
   misses. We have the lemmas already: `macula-hebrew-wlc` (475,911 words), `morphhb-wlc` (376,712),
   `macula-greek-sblgnt` (137,741).
    - **Works within a testament; blocked across one.** Hebrew and Greek lemmas don't join, and
      Strong's H/G numbering doesn't bridge them. The pivot would be a lemmatised LXX, which we
      don't have — Brenton is text-only. STEPBible's TAHOT/TAGNT files (`open-data/stepbible-data`,
      CC-BY, currently raw-only) are the first place to look for that bridge. Until then,
      cross-testament allusion is out of scope — and it's the case that matters most for a
      promise-to-fulfilment reading, so it's the open question to resolve first.
3. **Semantic-domain proximity** — Louw-Nida and SDBH domains, already sitting in
   `morphology.domain_code`. This is how to get "theme links" without inventing a theme taxonomy.
4. **Curated typological / dispensational links** — hand-authored in our own frontmatter. The
   smallest class and the only one that is our own scholarship rather than someone else's data.
   Always attributed as a reading, never presented as a computed fact.
5. **Crowd cross-reference (OpenBible votes)** — kept, but ranked last and always labelled. Its
   votes are consensus from a largely covenantal user base and will confidently weight
   Israel-equals-church links this site doesn't hold; it's also KJV-versified, so expect drift at
   the Psalm superscriptions, Joel 2/3 and Malachi 3/4. Useful as a lead to chase, not as evidence.

#### Source data — state of play

Cleared, in the order they were found — each one blocked something in the edge classes above:

- **SBLGNT word separators.** All 7,939 verses were stored run-together (`Ἐνἀρχῇἦνὁλόγος`), because
  the XML encodes the separator implicitly. Without it the Greek NT cannot be tokenised at all, so
  the quotation class was dead on arrival. The reconstruction now reproduces the publisher's own
  text edition exactly.
- **The LXX's "missing" books.** Daniel, Esther and Nehemiah were on disk all along — Daniel as
  Greek Daniel (Theodotion), Nehemiah inside 2 Esdras, Esther with its additions on lettered
  sub-verses — and were being dropped as deuterocanonical. All 39 protocanonical OT books now.
- **Duplicate verse rows.** 28,674 references carried two or three rows across 38 works, because
  upstream ships each verse many times with differing whitespace. Now deduplicated at ingest and
  enforced by a unique index.
- **Versification.** `(book, chapter, verse)` means different things in different works. Joel,
  Malachi, Daniel, Psalms, Proverbs and Jeremiah all disagree across schemes; `works.versification`
  and `versification.py` now carry it, and the lookups align automatically.
- **Style markers and translation-code resolution.** BibleOrgSys markers reached 47% of WEB verses;
  and `WEB` resolved to a work that does not exist, so the default English lookup returned nothing.

- **The LXX's own versification**, now derived rather than deferred. Jeremiah is reordered with an
  identical chapter count, so it hides from any count-based check; it was found by a quotation
  landing on the wrong chapter and then mapped chapter by chapter from the text itself — each
  relocated chapter names the nation it is against, and proper nouns survive translation. Only
  Jeremiah 30 resists, its sub-oracles being reordered *within* the chapter. The same pass turned
  up two more chapter breaks nobody had noticed: Daniel 5/6 (where the LXX sides with the Hebrew,
  having sided with the English at 3/4) and LXX Jeremiah 51's tail, which English prints as its
  own chapter 45.

Still open, both needing a source rather than a fix:

- **A lemmatised LXX.** Deriving one from the annotated Greek NT covers **55.3%** of LXX tokens —
  useful for confirming a specific lemma, but not enough for the rare-lemma allusion class, which
  rests on corpus frequency and would be computing rarity against a broken denominator. Cross-
  testament allusion stays out of scope until a real lemmatised LXX lands.
Proverbs turned out to be mappable after all, once it was clear that Brenton preserves the Hebrew
verse numbering and merely omits what the LXX lacks — a short chapter is an omission, not a
renumbering. Six New Testament quotations confirm it, the Greek match and openbible's
english-scheme cross-references independently naming the same reference for each.

Quotation hits that cannot be expressed as English references are down to **2 of 968 (0.2%)** —
both weak two-gram hits in Jeremiah 30, the one chapter whose sub-oracles the LXX reorders
internally.

#### One constraint on the generator

**Threshold, never top-N, and sort deterministically.** The prototype capped candidates per verse
at the best four, which looked harmless and was not: a score tie straddled that cut for 58 of 541
verses, so which candidates survived depended on set iteration order and changed between runs, and
the cap discarded 27% of qualifying pairs outright — including 32 quotations strong enough to carry
an eight-token verbatim run. Keeping everything above the threshold and letting the grading rank it
gives byte-identical output across runs and more real signal. This matters because the generator
writes into committed content: a re-run that produces a different set makes every diff unreviewable
and lets a cited edge vanish under someone's feet.

#### Deliverables, in order — each one gated on the last proving out

1. **Gap detector.** For a study, take `primary_passage` + `bible_references`, pull typed edges,
   subtract what the study already cites, and report what the tradition connects that we never
   mention. A `query.py` subcommand plus an MCP wrapper, consumed by review-bible-study. No
   database, no visualisation, plain text output.
2. **Test it on real studies** before building anything else. If it doesn't change a study, the
   rest of this item isn't worth building.
3. **Scripture-derived related studies.** Two studies are related when their passage sets are
   densely linked — *even when they share no tag and never cite each other*. Emit a "Related by
   passage" block through the same `<!-- ...auto-start/end -->` mechanism `commentary_index.py`
   already uses. This is the integrated-message claim made concrete.
4. **A reader-facing reference lookup** — see below.

#### Surfacing it

If this proves out it shouldn't stay buried in an agent tool. But the right surface is **not a
second search box**: mkdocs-material's search already indexes prose and a competing one is a UX
problem. What's genuinely missing is a **reference resolver** — enter or click *Isaiah 61:1* and get
(a) which studies treat it, (b) its typed links, each labelled by class. Site search can't do that,
because it indexes words rather than references.

- Build it the way the timeline and genealogy already work: a static JSON index emitted at build
  time (the `build-events.js` pattern), mounted as a React page from `app/src/entries/`. No server.
- **Scope the shipped index to our own passages and their immediate neighbourhood**, not 415k edges.
- **Licence constraint:** any verse text rendered in the browser must be WEB or another `open` work.
  ESV/NIV/NKJV/CSB live in `study-notes.db` under `quotation-only` and never ship to the client.

#### Prerequisite

Only 46 of 102 content pages carry `primary_passage` and 49 carry `bible_references`. Every step
above is bounded by that coverage, so filling it in is the cheapest first move — and it improves the
existing commentary index immediately.

#### Explicitly not doing

- A force-directed whole-canon graph. 415k edges renders as a hairball, and OpenBible already
  publishes the arc diagram.
- A graph database. At this scale SQLite with an `edge_type` column is sufficient; a graph store
  would have to earn its place later.
- A hand-built theme taxonomy, when semantic domains and the existing tag facets already exist.

## 2. Jesus

### 2.1 Prophecy and Jesus

- Nature
- Birth and lineage
- Childhood
- Ministry
- Passion
- Work — redemption
- Prophet, priest, king
- Future

### 2.2 Priest of the order of Melchizedek

Christ's priesthood as a distinct order from the Levitical one (Genesis 14, Psalm 110,
Hebrews 5-7) — not yet scoped beyond that.

### 2.3 Jesus' attitude toward women

How Jesus treats women across the Gospels, against the norms of his day — not yet scoped beyond
that.

## 3. Spiritual beings

### 3.1 Nephilim

- What they are
- Other biblical references that are related — e.g. the Rephaim
- Did they survive the flood?
    - Not by strength — Genesis 6-7 is clear that all flesh outside the ark perished
    - Possibly by genetic pollution recurring after the flood (cf. Numbers 13:33, Deuteronomy
      2-3, 2 Samuel 21) — worth investigating rather than assuming
- Are they still around?
- What extra-biblical Jewish tradition says about the Nephilim — e.g. the Book of Enoch's
  account, the most extensive we have. It's held by New Testament authors (Jude quotes it
  directly) as generally true but not as Scripture.

## 4. Salvation

### 4.1 Assurance of salvation

The question and assurance of salvation: there is no other name by which we may be saved
(Acts 4:12), and it is not by our works (Ephesians 2:8-9).

### 4.2 On death

For those in Christ, we are immediately with Christ in spirit/soul, though our bodies are yet to
be resurrected.

Notes to work through:

- "Went to be with the Lord"
- "Risen"
- "Today you will be with me" — Jesus to the thief on the cross (Luke 23:43)
- Moses and Elijah with Jesus at the Transfiguration
- The parable of the rich man speaking with Abraham and Lazarus (Luke 16:19-31)

Verses to gather and compare as the study takes shape — not started yet.

## 5. Last things

### 5.1 Tribulation perspectives

**Pre-tribulation**

- [Missler on the rapture, part I](https://www.youtube.com/watch?v=-lVcN9vsCbQ)
- [Missler on the rapture, part II](https://www.youtube.com/watch?v=wdufyUUfRmk)

**Post-tribulation**

- [The Last Days, Vol. 2 (PDF)](https://faithconnector.s3.amazonaws.com/teachingfaith/files/The_Last_Days_Vol_2_Updated/the_last_days_vol_2_updated_6-22-23_(1).pdf)

### 5.2 End times

- Ordered events
- Signs
- How God removes his people from judgment

**Psalm 83 war**

- Objective is the destruction of Israel
- Who —
- References: [Not the Gog-Magog War (PDF)](https://faithconnector.s3.amazonaws.com/teachingfaith/files/The_Last_Days_Volume_11/not_the_gog-magog_war.pdf), [Tents of Edom (PDF)](https://faithconnector.s3.amazonaws.com/teachingfaith/files/The_Last_Days_Volume_11/tents_of_edom.pdf)

**Ezekiel 38 war**

- Objective is the plundering of Israel
- Who —

### 5.3 The last trumpet

Meaning of the last trumpet in 1 Corinthians 15 and 1 Thessalonians 4.

## 6. Feasts

### 6.1 Appointed times (overarching)

- The seasons — spring and fall feasts, and the pattern of the Leviticus 23 sequence
- The meaning of each feast
- Where each has already been fulfilled (first coming) vs. what's still awaited (second coming)
- Plan: one overarching study covering the whole appointed-times pattern, then a dedicated study
  per feast (6.2)

### 6.2 Individual feast studies

- [ ] Passover (Pesach)
- [ ] Unleavened Bread
- [ ] Firstfruits
- [ ] Weeks / Pentecost (Shavuot)
- [ ] Trumpets (Yom Teruah)
- [ ] Day of Atonement (Yom Kippur)
- [ ] Tabernacles (Sukkot)

## 7. Biblical figures

### 7.1 Twelve disciples

- Name and meaning
- Calling order
- Background
- Significance
- Key verse
- Takeaway / lesson

## 8. Sources & tooling

Not study topics — work on the material the studies rest on.

### 8.1 Mirror the unfoldingWord sources

The four unfoldingWord submodules (`uw-uhb`, `uw-ugnt`, `uw-ult`, `uw-uhg`) point at
[Door43](https://git.door43.org/unfoldingWord) directly. Every other source in
`references/open-data/` is forked to `ding0t/*` first, so the project survives an upstream
disappearing; these four are the exception, because GitHub auth was not working on the machine that
added them on 2026-09-05.

Auth has since been fixed, so the only thing left is the doing. Pinned submodule commits already
protect against upstream *changing* — the gap is Door43 going away entirely.

**Licensing is not a blocker.** All four are CC BY-SA 4.0, which permits redistributing the
unmodified work provided unfoldingWord's trademark and licence file stay intact. A verbatim mirror
does exactly that.

Per repo — `hbo_uhb`, `el-x-koine_ugnt`, `en_ult`, `en_uhg`:

1. `git clone --mirror https://git.door43.org/unfoldingWord/<name>.git` — a full clone, since the
   submodules here are `--depth 1` and cannot push complete history
2. `gh repo create ding0t/<name> --public` — matching the visibility of the existing forks
3. `git push --mirror https://github.com/ding0t/<name>.git`

Then repoint the four URLs in `.gitmodules`, run `git submodule sync`, and correct the three places
that currently say these are not mirrored: the permanence note on
[Public Data Sources](../resources/public-data-sources.md), the unfoldingWord section of
`references/README.md`, and `references/study-state/unfoldingword-wireup.yml`.

Roughly 140MB in total; `en_ult` is nearly all of it and `en_uhg` is 3.6MB.
