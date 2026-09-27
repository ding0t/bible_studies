---
title: "Backlog"
category: "other"
description: "A public working list of study topics and research items still to be developed, organized by the site's own subject sections."
tags: ["backlog", "planning", "research", "development"]
draft: false
date_created: 2026-08-25
date_modified: 2026-09-27
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-opus-5.5
  - anthropic/claude-sonnet-5
---

# Backlog

A running, public list of study topics and research questions on the list to develop — some are
just a title, others already have working notes. Organized by the site's own
[subject sections](our-taxonomy.md), in their published order, so a section only appears here if
it currently has something queued.

Refer to an item by its number, e.g. "work on 4.3." Section 0 is work on the site itself rather
than a study topic.

## Quick reference

| Ref | Topic | Section |
|---|---|---|
| [0.3](#03-key-takeaways-the-remaining-two-parts) | Key Takeaways: the remaining two parts | Site features |
| [0.4](#04-new-studies-shown-apart-from-updated-ones) | New studies shown apart from updated ones | Site features |
| [0.5](#05-a-blog) | A blog | Site features |
| [0.6](#06-pop-up-follow-ups) | Pop-up follow-ups | Site features |
| [1.1](#11-extra-biblical-texts) | Extra-biblical texts | Scripture |
| [1.2](#12-typed-scripture-links) | Typed scripture links | Scripture |
| [2.1](#21-prophecy-and-jesus) | Prophecy and Jesus | Jesus |
| [2.3](#23-jesus-attitude-toward-women) | Jesus' attitude toward women | Jesus |
| [2.4](#24-the-feedings-and-the-hardened-hearts) | The feedings and the hardened hearts | Jesus |
| [4.2](#42-on-death) | On death | Salvation |
| [4.3](#43-faith) | Faith | Salvation |
| [5.1](#51-tribulation-perspectives) | Tribulation perspectives | Last things |
| [5.2](#52-end-times) | End times | Last things |
| [5.4](#54-the-olivet-discourse-regrouped-by-the-disciples-questions) | The Olivet Discourse, regrouped by the disciples' questions | Last things |
| [5.5](#55-the-age-to-come) | The age to come | Last things |
| [5.6](#56-they-were-given-white-robes) | They were given white robes | Last things |
| [6.1](#61-appointed-times-overarching) | Appointed times (overarching) | Feasts |
| [6.2](#62-individual-feast-studies) | Individual feast studies | Feasts |
| [8.1](#81-mirror-the-unfoldingword-sources) | Mirror the unfoldingWord sources | Sources & tooling |
| [9.1](#91-calling-good-evil-and-evil-good) | Calling good evil and evil good | Sin |
| [9.2](#92-sexual-immorality) | Sexual immorality | Sin |
| [10.2](#102-where-two-or-three-are-gathered) | Where two or three are gathered | Christian life |
| [10.3](#103-religion-and-the-way) | Religion and the Way | Christian life |
| [10.4](#104-i-stand-at-the-door-and-knock) | "I stand at the door and knock" | Christian life |

Finished items move to [Completed](#completed) at the foot of the page and keep their numbers, so
an old reference still points at the right thing.

---

## 0. Site features

Work on the site rather than a study. The verse and word pop-ups (0.1 and 0.2) are built; see
[Completed](#completed). Their data, exported from `bible-text.db` into
`docs/content/assets/popups/`, is also the natural source for the reader-facing lookup in
[1.2](#12-typed-scripture-links).

### 0.3 Key Takeaways: the remaining two parts

The first part is done: every Key Takeaways section now opens with one line saying it follows the
format, with a link to [Key Takeaways](key-takeaways.md) (2026-09-27, 50 studies).

- **Refresh the format page's example.** [Key Takeaways](key-takeaways.md) names the Melchizedek
  study as where the format was first built out, and draws its type example from it. The
  2026-09-25/26 studies ([Know the Truth](../christian-life/know-the-truth.md),
  [The Restrainer](../last-things/the-restrainer.md)) now show the format better: pick one as the
  worked example.
- **Point each prayer to the prayer study.** Add one line above each `### Prayer` heading linking to
  [Prayer: Communion and the Habit It Sustains](../christian-life/prayer-as-communion.md), the same
  way the Key Takeaways line was normalised: one fixed wording, applied by script, relative link
  adjusted per file.

### 0.4 New studies shown apart from updated ones

Updates happen daily, so a new study gets lost among them. Readers, and the author, should be able
to see what is new this month.

- **The data is already there.** `date_created` is in every hand-written page's frontmatter,
  derived from git by `refresh_frontmatter_provenance.py`.
- **One catch:** `date_created` is the first commit, and a study forked or drafted weeks before it
  is published would count as old on the day it goes live. "New" should mean *first published*:
  the commit that set `draft: false`. `generate_recent_updates.py` already reads git log and can find
  that commit.
- **Ideas to choose from:**
    - a "New this month" list above "Recently updated" on the
      [Recent updates](recent-updates.md) page, and a matching block in the homepage teaser;
    - a small "New" badge on a page for 30 days after publication, added by the build hook;
    - a "New studies" feed once the blog (0.5) exists.

### 0.5 A blog

A place for shorter posts alongside the studies, built on mkdocs-material's own blog plugin.

- **Setup:** the `blog` plugin is part of mkdocs-material, so no new dependency. Add it to
  `plugins:` in `mkdocs.yml`, create `docs/content/blog/index.md` and a `posts/` folder, and give
  it a nav entry through awesome-pages.
- **Drafts:** the blog plugin honours `draft: true` on posts by itself. Check that
  `hooks/draft_pages.py` does not also act on posts, or they will be handled twice.
- **Docs to update:** AGENTS.md says "this site has no blog" in its note on draft handling; that
  line changes when this lands.
- **Deploy:** posts live under `docs/`, so the existing path filter already deploys them.
- **Decide first:** categories, authors, whether posts get the Key Takeaways shape (probably not),
  and whether a post can be the first draft of a study.

### 0.6 Pop-up follow-ups

What the pop-ups (0.1 and 0.2) left undone.

- **Strong's numbers on untagged words.** A word gets a word card only when its Strong's number is
  written beside it. The studies carry about 380 tagged words, and many of the 433 Hebrew words
  written in `<span dir="rtl">` have no number yet. A sweep adds the number, verified with
  `bible_word`, in the existing `(*transliteration*, H/G number)` shape.
- **Hebrew meanings.** The word card shows STEPBible's short gloss. TBESH's fuller "Meaning" column
  is left out because its header credits Online Bible's abridged BDB and asks that permission be
  sought. Ask Online Bible, or leave it out for good.
- **Counts in the studies against the cards.** A study's "only here" or "N times" now sits on the
  same page as a card showing the concordance's number. A one-off pass comparing every stated count
  with the exported data would find the stale ones (see validator checks 18-19).

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

1. **Gap detector.** *Built:* `references/build/study_gaps.py` and the `review_gaps` MCP tool. For a study, take `primary_passage` + `bible_references`, pull typed edges,
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

75 of 134 hand-written pages now carry `primary_passage` and 80 carry `bible_references` (up from
46 and 49 of 102; counted 2026-09-27). Every step
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

### 2.3 Jesus' attitude toward women

How Jesus treats women across the Gospels, against the norms of his day — not yet scoped beyond
that.

### 2.4 The feedings and the hardened hearts

Expand [The Bread of Life](../jesus/bread-of-life-feeding-the-multitudes.md) with Mark's reading
of the two feedings (the five thousand and the four thousand) — a revision of that study rather than
a new one.

- **The gap.** The study treats the rebuke in the boat over the loaves (Mark 8:14-21) but never
  Mark 6:52. There, after Jesus walks on the water, Mark gives the disciples' astonishment (6:51) its cause: "for
  they did not understand about the loaves, but their hearts were hardened" (Mark 6:52, ESV).
- **The thread.** Both scenes are in the boat, and both tie the disciples' failure to the loaves. In
  the first they are straining against the wind when Jesus comes to them on the water (Mark 6:48).
  In the second they are arguing over having no bread, and Jesus asks, "Are your hearts
  hardened?" (Mark 8:17, ESV) and makes them count the baskets from both feedings. Matthew's parallel calls them "you of little faith"
  (Matthew 16:8), which links this item to [4.3](#43-faith).

## 4. Salvation

### 4.2 On death

For those in Christ, we are immediately with Christ in spirit/soul, though our bodies are yet to
be resurrected.

Notes to work through:

- "Went to be with the Lord"
- "Risen"
- "Today you will be with me" — Jesus to the thief on the cross (Luke 23:43)
- Moses and Elijah with Jesus at the Transfiguration
- The parable of the rich man speaking with Abraham and Lazarus (Luke 16:19-31)

**In progress:** *At Home with the Lord* (`last-things/at-home-with-the-lord.md`) is drafted
(2 Corinthians 5:1-8, the believer with Christ between death and resurrection). Still to fold in
from the notes above: the thief on the cross, Moses and Elijah at the Transfiguration, and Luke 16.

### 4.3 Faith

What the Bible means by faith, across both Testaments.

- **Where the study should land:** faith is not a work of our own strength. Faith "like a grain of
  mustard seed" is enough (Matthew 17:20; Luke 17:6), because what matters is **who** the faith is
  in. That is what Jesus meant when He called His disciples "you of little faith", as when Peter
  began to sink after walking on the water (Matthew 14:31). ὀλιγόπιστος (*oligopistos*, G3640)
  occurs five times, all on Jesus' lips: Matthew 6:30, 8:26, 14:31, 16:8 and Luke 12:28.
- **Words:** Hebrew <span dir="rtl">אָמַן</span> (*ʾaman*, H539), whose hiphil is "believed" at
  Genesis 15:6, and its noun <span dir="rtl">אֱמוּנָה</span> (*ʾemunah*, H530, faithfulness); Greek
  πίστις (*pistis*, G4102) and πιστεύω (*pisteuō*, G4100). The Hebrew root carries firmness and
  reliability, which is why "faith" and "faithfulness" share it.
- **Anchor texts:** Genesis 15:6 (Abraham believed, and it was counted to him as righteousness);
  Habakkuk 2:4, which the New Testament quotes three times (Romans 1:17, Galatians 3:11,
  Hebrews 10:38); and Hebrews 11, read as that chapter's own definition (11:1) followed by its
  examples.
- **Questions to work through:** faith and works in Romans 4 beside James 2; whether faith is itself
  a gift (Ephesians 2:8-9, where the grammar is debated); faith as trust in a Person.
- **Links:** [Assurance of Salvation](../salvation/assurance-of-salvation.md) and
  [Know the Truth](../christian-life/know-the-truth.md).

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

### 5.4 The Olivet Discourse, regrouped by the disciples' questions

[The Olivet Discourse](../last-things/olivet-discourse.md) was cut back and given an outline on
2026-09-26, and it still does not leave the reader thinking "that is what Jesus was saying".

- **Group by the questions asked.** Matthew 24:3 puts three to Jesus: when will "these things" (the
  temple's fall, 24:2) be, what will be the sign of His coming, and what will be the sign of the
  close of the age. Arranged under those three, each answer can be read against the question it
  answers. Luke 21:7 has only the temple question, which is part of why the parallels differ.
- **Or group by the events answered.** The temple's fall; the time of distress; the coming of the
  Son of Man; the hour no one knows. Either way, the reader should reach the end able to say which
  part of the discourse answers which question.
- **Which skill:** if the sentences can stay, this is **read-bible-study** (regroup, change no
  sentence). If the argument itself needs re-ordering, it is a redraft through
  **develop-bible-study**. Decide after one read against the question grouping.
- **The problem is finding your place, and the content is good.** It is hard to tell which part of
  the discourse sits where. The 2026-09-26 edits may have helped, so re-read before starting.
- **Example: the flight to the mountains.** It is not clear when "let those who are in Judea flee to
  the mountains" (Matthew 24:16, ESV) happens: the temple's destruction and the persecution of the
  first Christians, the tribulation, or both. Luke's parallel ties it to "Jerusalem surrounded by
  armies" (Luke 21:20, ESV); Matthew and Mark tie it to Daniel's abomination of desolation. The
  regrouped study should say which question the instruction answers, and mark the reading as
  contested where it is.
- **One full exegesis of "one taken, one left".** Matthew 24:40-41 is worked through in three
  places: [The Olivet Discourse](../last-things/olivet-discourse.md) has its own section, the
  [rapture study](../last-things/rapture.md) defers to that, and the draft *One Taken, One Left*
  (`last-things/one-taken-one-left.md`) is a full study of it. Keep the full exegesis in one of
  them, most naturally the dedicated study, and have the other two point to it. The draft cannot be
  linked until it is published. The readings must also agree; the open question is recorded in
  `references/study-state/readability-sweep-2026-09.yml` under `author_questions`.


### 5.5 The age to come

What the New Testament means by "the age to come", and how it relates to the millennium and the
eternal state.

- **Texts:** Matthew 12:32 ("this age or the age to come"); Ephesians 1:21; Hebrews 6:5 ("the powers
  of the age to come"); Mark 10:30 and Luke 18:30 (eternal life "in the age to come"); Luke 20:34-35.
  Verify each wording against the ESV before quoting.
- **Word:** αἰών (*aiōn*, G165), and the phrase ὁ αἰὼν ὁ μέλλων.
- **Background:** the Jewish two-age frame, "this world" and "the world to come" (*ʿolam ha-ba*),
  as in the Mishnah's "all Israel has a share in the world to come" (m. Sanhedrin 10:1). Cite from a
  primary source.
- **Links:** [A Day Is a Thousand Years](../last-things/day-is-a-thousand-years.md) (the seventh
  day as the millennium), and the Olivet Discourse's "close of the age" (Matthew 24:3).

### 5.6 They were given white robes

White garments on God's people run through Scripture, explicitly and significantly, and Revelation
returns to them repeatedly. The study should gather every occurrence and ask what the robes mean,
who wears them, and whether they are God's gift.

- **Where they appear:** Revelation 3:4-5 and 3:18 (the promise to those who conquer, and the
  counsel to Laodicea); 6:11 (the martyrs under the altar); 7:9 and 7:13-14 (the great multitude,
  who "washed their robes and made them white in the blood of the Lamb"); 19:8 and 19:14 (the
  Bride's fine linen, and the armies of heaven). Behind them: Isaiah 1:18, Zechariah 3:3-5 (Joshua's
  filthy garments taken away and clean ones given), Daniel 7:9 and 12:10, and Isaiah 61:10
  ("garments of salvation").
- **The Transfiguration parallel:** Jesus' clothes became white as light (Matthew 17:2, Mark 9:3,
  Luke 9:29), and the angels at the tomb and the Ascension are dressed in white (Mark 16:5,
  Acts 1:10). Ask whether the saints' robes share in His glory.
- **Who wears them:** the martyrs of 6:11, the multitude "out of the great tribulation" (7:14) and
  the Bride of 19:8 may be different groups. That matters for this site's reading of the
  tribulation and the Church, so mark which identifications are contested.
- **Gift or deeds?** The robes are *given* (6:11, the verb ἐδόθη, a divine passive), *washed* in
  the Lamb's blood (7:14), and the Bride's linen is *granted* her yet is "the righteous deeds of the
  saints" (19:8). Hold the three together: imputed righteousness (Zechariah 3, Isaiah 61:10) and the
  fruit it produces. Name the doctrines.
- **Words:** στολή (*stolē*, "robe"), λευκός (*leukos*, "white"), λευκαίνω (*leukainō*, "make
  white", 7:14) and βύσσινος (*byssinos*, "fine linen", 19:8). Count occurrences with the
  concordance before claiming any.
- **Does it tie in with [The Wife of the Lamb](../israel-and-church/wife-of-the-lamb.md)?** Almost
  certainly at 19:7-8, where the Bride is clothed in fine linen at the marriage of the Lamb. Test
  whether the white robes of 3:5, 6:11 and 7:14 are the same clothing, and say how far the link holds.
- **Other links:** [The Bride of Christ](../israel-and-church/bride-of-christ.md), and
  [The Rapture of the Church](../last-things/rapture.md), which places the Bema and the linen.

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
- [ ] Firstfruits — drafted, in review (`feasts/firstfruits.md`)
- [ ] Weeks / Pentecost (Shavuot)
- [x] Trumpets (Yom Teruah) — [published](../feasts/trumpets.md)
- [ ] Day of Atonement (Yom Kippur)
- [ ] Tabernacles (Sukkot)

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

## 9. Sin

### 9.1 Calling good evil and evil good

Tracing the prevalent sin of calling what is good evil, and what the Bible says of it.

- when someone condemns another of wrongdoing who has called out sin - such as murder
- when sin is legalised as not only ok, but as good, and those who speak against it are in the wrong
- when preaching Christ is considered as wrongdoing

### 9.2 Sexual immorality

The current study is very light.

- the bible is clear what is sexual sin
- why is it sin
- the impact on the individual: sin against one's own body
- defiling the image of the bride of Christ?

## 10. Christian life

### 10.2 Where two or three are gathered

> ✝️ [Matthew 18:20 (ESV)](https://www.blueletterbible.org/esv/mat/18/20)
>
> 20 For where two or three are gathered in my name, there am I among them.

This verse is often quoted as though Jesus needs at least two people present to be with them, or to
make prayer effective. The study should teach what Jesus actually said.

- **Context first:** 18:20 closes a paragraph about a brother who sins (18:15-20): go to him alone,
  then with one or two others, then tell it to the church. "Two or three" echoes the law's
  requirement of two or three witnesses (Deuteronomy 19:15, which Jesus quotes at 18:16). The
  promise of His presence stands behind the church's judgement in that process.
- **Word study:** συνάγω (*synagō*, "gather", the root of *synagogue*) and "in my name".
- **Cultural background:** the Jewish saying that the Divine Presence rests on even two who study
  the law together (m. Avot 3:2, 3:6). Jesus' promise has the same shape, with Himself in that
  place. Cite from a primary source.
- **Pastoral landing:** a believer praying or worshipping alone is not alone. Jesus promised to be
  with His disciples always (Matthew 28:20), and the Spirit dwells in each believer (1 Corinthians
  6:19). The call to meet together (Hebrews 10:24-25) stands alongside that. The study should say
  both.

### 10.3 Religion and the Way

We are called to know Jesus, who is the truth, and so to have assurance of life in Him. Religion as
self-effort offers a moral code to live by instead.

- **Self-effort and pride:** works as a trap that feeds pride, in the self and in one's religion
  (Ephesians 2:8-9; Luke 18:9-14, the Pharisee and the tax collector).
- **What God desires:** a broken and contrite heart (Psalm 51:17); also Isaiah 66:2 and
  Micah 6:6-8.
- **Handle the word carefully.** James uses θρησκεία (*thrēskeia*, "religion") positively: pure
  religion is to visit orphans and widows and keep oneself unstained from the world (James 1:27).
  So the study cannot rest on the English word "religion". It has to say affirmatively what God asks
  for.
- **Links:** [The Way](../jesus/the-way.md) (the name the first believers took),
  [Assurance of Salvation](../salvation/assurance-of-salvation.md),
  [Know the Truth](../christian-life/know-the-truth.md), and 10.4.

### 10.4 "I stand at the door and knock"

> ✝️ [Revelation 3:20 (ESV)](https://www.blueletterbible.org/esv/rev/3/20)
>
> 20 Behold, I stand at the door and knock. If anyone hears my voice and opens the door, I will come
> in to him and eat with him, and he with me.

A study on Jesus seeking His people. He is not meant to stand outside, and the answer is a contrite
heart that opens the door.

- **Context first:** the verse is addressed to a church, Laodicea (Revelation 3:14-22), whose members
  thought themselves rich and needing nothing (3:17). It is most often preached as an invitation to
  the unconverted. Set out both uses and say which the text supports; the context favours a call to
  a complacent church first.
- **Word and background:** δειπνέω (*deipneō*, "eat, dine"), a shared evening meal as fellowship;
  and Laodicea's lukewarm water supply, which the letter's "neither cold nor hot" draws on.
- **Links:** 10.3 (religion and a contrite heart), and [The Way](../jesus/the-way.md).

## Completed

Kept here so that an old reference like "work on 3.1" still resolves.

| Ref | Item | Now |
|---|---|---|
| 2.2 | Priest of the order of Melchizedek | [Jesus, Priest in the Order of Melchizedek](../jesus/melchizedek-priesthood.md) |
| 3.1 | Nephilim | [The Nephilim](../spiritual-beings/nephilim.md) |
| 4.1 | Assurance of salvation | [Assurance of Salvation](../salvation/assurance-of-salvation.md) |
| 5.3 | The last trumpet | [The Trumpet Call of God](../last-things/trumpet.md) |
| 7.1 | Twelve disciples | [The Twelve: Disciples and Apostles](../biblical-figures/twelve-apostles.md), with a page per apostle |
| 10.1 | Know the truth | [Know the Truth](../christian-life/know-the-truth.md) |
| 0.1 | Scripture pop-up on a verse reference | Every reference on the site opens the verse, its context, cross-references and the studies that treat it, 2026-09-27. Blue Letter Bible links removed |
| 0.2 | Word-study pop-up on an original-language word | Every Strong's tag, and the word in front of it, opens a word card: lexicon, counts, where it occurs, renderings, and the studies that discuss it, 2026-09-27. Follow-ups in [0.6](#06-pop-up-follow-ups) |
| 0.3 (part) | Normalise the Key Takeaways opening line | Done across 50 studies, 2026-09-27 |
