---
title: "Backlog"
category: "other"
description: "A public working list of study topics and research items still to be developed, organized by the site's own subject sections."
tags: ["backlog", "planning", "research", "development"]
draft: false
date_created: 2026-08-25
date_modified: 2026-10-09
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-opus-5.5
  - anthropic/claude-sonnet-5
  - anthropic/claude-sonnet-5.5
---

# Backlog

A running, public list of study topics and research questions on the list to develop — some are
just a title, others already have working notes. Organized by the site's own
[subject sections](our-taxonomy.md), in their published order, so a section only appears here if
it currently has something queued.

Refer to an item by its number, e.g. "work on 4.3." Section 0 is work on the site itself rather
than a study topic.

## new

Add new items here. They get a number and move into their section.

## Quick reference

| Ref | Topic | Section |
|---|---|---|
| [0.3](#03-key-takeaways-the-remaining-two-parts) | Key Takeaways: the remaining two parts | Site features |
| [0.5](#05-a-blog) | A blog | Site features |
| [0.6](#06-pop-up-follow-ups) | Pop-up follow-ups | Site features |
| [0.7](#07-review-the-older-studies) | Review the older studies | Site features |
| [0.9](#09-drafts-awaiting-publication) | Drafts awaiting publication | Site features |
| [1.1](#11-extra-biblical-texts) | Extra-biblical texts | Scripture |
| [1.2](#12-typed-scripture-links) | Typed scripture links | Scripture |
| [1.3](#13-learning-hebrew) | Learning Hebrew | Scripture |
| [2.1](#21-prophecy-and-jesus) | Prophecy and Jesus | Jesus |
| [2.3](#23-jesus-attitude-toward-women) | Jesus' attitude toward women | Jesus |
| [2.4](#24-the-feedings-and-the-hardened-hearts) | The feedings and the hardened hearts | Jesus |
| [2.5](#25-the-heavenly-pattern) | The heavenly pattern (series) | Jesus |
| [4.2](#42-on-death) | On death | Salvation |
| [5.1](#51-tribulation-perspectives) | Tribulation perspectives | Last things |
| [5.2](#52-end-times) | End times | Last things |
| [5.6](#56-they-were-given-white-robes) | They were given white robes | Last things |
| [5.7](#57-heaven-and-earth-by-fire) | Heaven and earth by fire | Last things |
| [8.1](#81-mirror-the-unfoldingword-sources) | Mirror the unfoldingWord sources | Sources & tooling |
| [8.2](#82-chronology-follow-ups) | Chronology follow-ups | Sources & tooling |
| [9.1](#91-calling-good-evil-and-evil-good) | Calling good evil and evil good | Sin |
| [9.2](#92-sexual-immorality) | Sexual immorality | Sin |
| [10.3](#103-religion-and-the-way) | Religion and the Way | Christian life |
| [10.4](#104-i-stand-at-the-door-and-knock) | "I stand at the door and knock" | Christian life |
| [10.6](#106-run-the-race) | Run the race | Christian life |

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
- **A "New studies" feed**, left over from 0.4. `docs/data/published.json` already holds every
  page's first-published date, so the feed needs no new git work.
- **Decide first:** categories, authors, whether posts get the Key Takeaways shape (probably not),
  and whether a post can be the first draft of a study.

### 0.6 Pop-up follow-ups

What the pop-ups (0.1 and 0.2) left undone.

- **Strong's numbers on untagged words.** A word gets a word card only when its Strong's number is
  written beside it. The 2026-09-27 sweep added the 198 numbers MACULA resolves to a single entry,
  so what is left needs a reader's judgement. `references/build/strongs_suggest.py --all` lists it:
  34 words with more than one candidate number (חֶסֶד, pronouns), 40 not in MACULA, and 64 phrases
  where the gloss may belong to one word. The 7 in this page are left for the author.
- **Every reference names its book.** develop-bible-study now requires `(Revelation 21:2)`, never a
  bare `(21:2)`, except a continuation within the same citation (`(Revelation 21:2, 9; 22:17)`).
  912 stand-alone bare references across 46 pages were written before the rule. The pop-up resolves
  them from the nearest earlier reference, and an edit that moves that reference repoints them with
  no error: `bride-of-christ.md`'s (21:2) opened Isaiah 21:2 after a rewrite cut the sentence naming
  Revelation 19:7. The 2026-09-27 audit caught only resolutions to a verse that does not exist or
  with another book named just before, so a wrong book with a real verse can still be hiding. The
  sweep adds the book to each, checked against its paragraph rather than taken from the resolver.
- **A validator warning for a bare reference.** Once the sweep is done, a `validate-content.js`
  check warns on a chapter-and-verse with no book that is not a continuation in the same citation,
  so new text cannot drift back.
- **Pronunciation: prose, card, or neither.** AGENTS.md asks for "the English pronunciation of a
  word" alongside the original text, but most studies give only the transliteration, and the word
  card shows the transliteration without a pronunciation. The studies that do give one use the
  house shape `(*Petros*, PET-ross, G4074)`. Decide whether to keep the rule and add pronunciations
  where they are missing, move pronunciation into the card (STEPBible's lexicon would have to
  supply it), or drop the requirement from AGENTS.md.
- **Iscariot's derivation in `biblical-figures/judas-iscariot.md`.** The page cites Strong's H377 for
  the "man of Kerioth" reading, and that is what Strong's G2469 says ("probably H0377 and H07149").
  But H377 is the verb "to be a man", while the Hebrew the page writes, <span dir="rtl">אִישׁ</span>
  *ish*, is the noun "man", H376. Decide whether the page notes that Strong's points at the verb.
- **Hebrew meanings.** The word card shows STEPBible's short gloss. TBESH's fuller "Meaning" column
  is left out because its header credits Online Bible's abridged BDB and asks that permission be
  sought. Ask Online Bible, or leave it out for good.
- **Counts in the studies against the cards.** A study's "only here" or "N times" now sits on the
  same page as a card showing the concordance's number. A one-off pass comparing every stated count
  with the exported data would find the stale ones (see validator checks 18-19).

### 0.7 Review the older studies

About 70 hand-written studies are live, and 19 have had a review-bible-study pass since
2026-09-24 (The Rapture of the Church on 2026-09-28, Genealogy and Times on 2026-09-30,
Melchizedek on 2026-10-02 after its rewrite). Nearly every page lists `anthropic/claude-opus-5.5` in its provenance, but that
records the site-wide sweeps (pop-ups, Key Takeaways) rather than reviews. A review counts when it
is recorded as a dated `review_` block in the study's state file. Work through the list in batches
of about four, and record each review in the state file.

- **Priority 1: changed or published since 2026-09-24 with no review since.** Silent doctrinal or
  chronology drift is the risk here.
  - [Chronology Anchors](../chronology/chronology-anchors.md): 4,600 words the timeline rests on.
    Reviewed 2026-08-22 alongside Combined Timeline (that day's edits only), then restructured
    2026-09-20 without review. Reviewed again 2026-10-01; findings await the author.
  - [At Home with the Lord](../last-things/at-home-with-the-lord.md) (reviewed and fixed 2026-10-04),
    [Taken Before Judgment](../last-things/taken-before-judgment.md) (reviewed and fixed 2026-10-04),
    [Six Days of History](../last-things/six-days-of-history.md) and
    [A Thousand Years in Your Sight](../last-things/a-thousand-years-in-your-sight.md): published
    2026-09-27 without a review.
  - [One Taken, One Left](../last-things/one-taken-one-left.md): reviewed and fixed 2026-10-04; previously never reviewed. The Olivet and
    rapture studies both point readers to it.
  - [The Olivet Discourse](../last-things/olivet-discourse.md): regrouped 2026-09-28. Last reviewed
    2026-09-04.
  - [The Bride of Christ](../israel-and-church/bride-of-christ.md): 10,000 words, heavily edited
    since its 2026-09-23 review.
- **Priority 2: long, and never reviewed by any model.**
  - [Bible Translations & Source Texts](../scripture/translations.md): the `source_profile` data was distilled from it,
    so an error here reaches every study's choice of translation.
  - [Ancient Texts and Manuscripts](../scripture/ancient-texts-manuscripts.md) and
    [Biblical Numerology](../scripture/numerology.md).
  - [The Woman at the Well](../jesus/woman-at-well.md) and
    [The Woman Who Touched the Fringe](../jesus/woman-with-the-issue-of-blood.md).
  - [Paul](../biblical-figures/paul.md) and the ten short apostle pages.
  - [Fasting](../christian-life/fasting.md) was rewritten and reviewed 2026-10-01, so it drops off
    this list.
- **Priority 3: reviewed before 2026-09-24 and stable since.** The Way, The Trumpet Call of God, The Twelve, Assurance of Salvation, The Last Supper's Four Cups, Three Days
  and Three Nights, The Lord's Prayer, Prayer as Communion.
- **Not reviews.** [Sin and Sexual Immorality](../sin/sexual-immorality.md) (28 words) and
  [Sin and Idolatry](../sin/idolatry.md) (185 words) are stubs and need a develop pass. For the first, see
  [9.2](#92-sexual-immorality). The pride study links to Idolatry.

### 0.9 Drafts awaiting publication

Files with `draft: true`, which the build drops. Each needs its remaining passes and a decision to
publish. This list names them by file path and links none, because a published page may not link a draft
(validator Check 24).

- Run the Race (`christian-life/run-the-race.md`): 5,534 words; see [10.6](#106-run-the-race).
- Great Commission (`christian-life/great-commission.md`): 3,289 words.
- Supplication: Begging, Turned Upward (`christian-life/supplication.md`): 589 words, a stub.
- How God Answers Prayer (`christian-life/how-god-answers-prayer.md`): 1,314 words. Publishing it
  restores the altar page's link in [2.5](#25-the-heavenly-pattern).
- Psalm 118 on the Road to Gethsemane (`jesus/psalm-118-road-to-gethsemane.md`): 1,449 words.
- The Rapture in the Early Church (`last-things/rapture-in-the-early-church.md`) (3,443 words) and
  Meet the Lord in the Air (`last-things/meet-the-lord-in-the-air.md`) (3,138 words).
- Four Hundred and Eighty Years (`chronology/four-hundred-and-eighty-years.md`): 1,393 words,
  forked from Genealogy and Times; see [8.2](#82-chronology-follow-ups).

### 0.10 Cut the AI register

A tidy of [Biblical Numerology](../scripture/numerology.md) on 2026-10-09 took its em-dashes from
109 to 64, "rather than" from 7 to 0, ", not" from 9 to 1 and "exactly" from 8 to 1, and the study
lost 437 words with nothing of substance gone. The pages below carry the same markers most densely.
They were counted on 2026-10-09 in prose only (quotations, tables and References excluded) and
scored per 1,000 words, one point per em-dash and four per contrast or intensifier. Numerology now
scores 6, Hebrew Roots and Israel's Regathering about 3. Each count is a pointer to read the page:
a contrast stays where the reader arrives holding the wrong version.

**Progress.** A review-bible-study Phase 8 pass was applied on 2026-10-09 to Bible Prophecy
Essentials, The Trumpet Call of God, Prophecy Events and Times, Dreams and Visions, What Creation
Declares, Genealogy and Times, Christians and Deliverance Ministry, The Day No One Knows,
Assurance of Salvation, The Woman Who Touched the Fringe, Bread of Life, Israel and the Church,
Bible Translations & Source Texts, The Day Is Near, The Twelve and its six apostle pages. All but
Bible Translations (22, its remaining contrasts are real distinctions between translations) and
Thomas (18) now score under 13. Content questions those passes raised are not yet resolved; a
review-bible-study pass should take them up. Still to do: the reference and about pages below.

- **Contrast-heavy** ("X, not Y", "rather than"), which the style guide's "define affirmatively"
  rule governs:
  - [Bible Prophecy Essentials](../last-things/prophecy-essentials.md): 15 "rather than", 15 ", not"
  - [The Trumpet Call of God](../last-things/trumpet.md): 16 "rather than"
  - [Prophecy Events and Times](../last-things/prophecy-events-times.md): 17 ", not", 70 em-dashes
  - [Dreams and Visions](../god/dreams-and-visions/index.md): 11 "rather than", 10 ", not"
  - [What Creation Declares](../god/creation-reveals-the-creator.md): 10 "rather than",
    11 ", not"
  - [Genealogy and Times](../chronology/genealogy-times.md): 11 "rather than", 7 "exactly"; pair
    with its word-budget item in [8.2](#82-chronology-follow-ups)
- **Em-dash-heavy** (about 11-16 per 1,000 words):
  - [The Twelve](../biblical-figures/twelve-apostles.md) (the highest-scoring study, also 9
    "rather than", 9 ", not", 7 "exactly") and the six short apostle pages that score with it:
    Bartholomew, Thomas, Matthew, Simon the Zealot, Thaddaeus and Judas Iscariot. Tidy them as
    one batch.
  - [Christians and Deliverance Ministry](../spiritual-beings/deliverance/christians-and-deliverance.md)
  - [The Day No One Knows](../jesus/the-day-no-one-knows.md)
  - [Assurance of Salvation](../salvation/assurance-of-salvation.md)
  - [Bread of Life](../jesus/bread-of-life-feeding-the-multitudes.md)
  - [The Woman Who Touched the Fringe](../jesus/woman-with-the-issue-of-blood.md)
  - [Israel and the Church](../israel-and-church/israel-and-the-church.md)
  - [Bible Translations & Source Texts](../scripture/translations.md): also 17 "rather than"
  - [The Day Is Near](../last-things/day-is-near.md)
- **Count both dash forms.** Many pages write the dash as an ASCII " -- ", which a count of "—"
  alone misses.
- **Reference and about pages**, lower priority: [Public Data Sources](../resources/public-data-sources.md)
  (the densest page on the site), [Key Takeaways](key-takeaways.md),
  [Reading the Original-Language Data](../scripture/original-language-data.md),
  [Patristic Sources](../resources/patristic-sources.md) and the [Glossary](../glossary.md), where
  many dashes separate a term from its definition and should stay.
- **The author's own:** [Statement of Faith](statement-of-faith.md) has 21 ", not". It records
  settled conviction, so any change to it is the author's call.

### 0.11 Content questions from the 0.10 pass

The style passes in [0.10](#010-cut-the-ai-register) changed wording only. Along the way they
found these content questions, none yet checked against source. Each needs verifying (quotations
against study-notes.db, Greek and Hebrew against bible-text.db) before it is fixed. Items marked
*author* need new wording or a judgment only the author can make.

**Across many of the 19 pages**

- Pronouns for God and Jesus are lowercase in the studies' own prose (style-guide rule 8). The
  0.10 pass capitalised only the lines it touched; each page needs one full sweep, leaving
  quotations alone. Worst: Bread of Life (about 30), The Woman Who Touched the Fringe, The Day Is
  Near, Bible Prophecy Essentials and all seven apostle pages.
- Prayers that never name Jesus or close "In Jesus' name. Amen.": The Trumpet Call of God, The Day
  No One Knows, The Woman Who Touched the Fringe and all seven apostle pages.
- *Author:* no sentence saying what the passage shows about God, or no "so you…" landing:
  Prophecy Events and Times, Christians and Deliverance Ministry (neither has Key Takeaways), The
  Trumpet Call of God ("Then and now"), Genealogy and Times (closing section), What Creation
  Declares (science section), The Woman Who Touched the Fringe ("Theological principle"), The
  Twelve ("Theological principle", election unnamed), Simon the Zealot, Bible Prophecy Essentials
  (God keeps His word).

**Bible Prophecy Essentials**

- 2 Samuel 5:2 is called "Nathan's word to David"; in 5:1-2 the tribes at Hebron quote the LORD.
  Nathan's oracle is 2 Samuel 7.
- The LXX is said to predate any crucifixion of a Jew by about two centuries. Alexander Jannaeus
  crucified Jewish opponents about 88 BC (Josephus, *Antiquities* 13.380).
- Brenton's edition is called "translated some two centuries before Christ"; Brenton is 1844.
- "A claim no other ancient religious text makes at the same scale" is uncited; "Both Testaments
  treat…" cites only Matthew 24:5.
- The frontmatter `description` keeps "genuine… rather than assumed".

**The Trumpet Call of God**

- "The dead in Christ" is attributed to 1 Corinthians 15 (it is 1 Thessalonians 4:16), and
  "incorruptible" is KJV/NKJV; the ESV has "imperishable".
- The third trumpet is tabled as water-to-blood; Revelation 8:11 has wormwood.
- The Revelation 11:18 ellipsis drops "rewarding your servants", which weakens "judgment only".
- Exodus 19:13 makes the Sinai trumpet a summons.
- "All three judgment cycles" names two; "a fourth" (Revelation 6:8) belongs to the fourth seal
  only; "a single, sustained blast" against Numbers 10:3's "both are blown".

**Prophecy Events and Times**

- The Luke 23:45 ἐκλιπόντος reading is called "later manuscripts"; it is in P75, Sinaiticus and
  Vaticanus and is the NA28 text.
- Anderson dated the Triumphal Entry itself to 6 April AD 32, not "days before".
- It says it takes no side on the Exodus date, then that the site works to 1446 BC.
- A References entry cites an "open discrepancy noted above" that the study never discusses.
- Herod's death in 4 BC is stated as fixed; the 1 BC date has defenders.

**Dreams and Visions**

- Jeremiah 23:32 is called the chapter's closing verdict (the chapter runs to v.40), and the Baal
  comparison misreads v.27.
- "Every dream… protects his life" does not fit Matthew 1:20-21.
- The Acts 10:17 quotation has no translation label.
- Heading "a hierarchy, not a flat category" is an antithesis; renaming it means updating the
  Study outline link.

**What Creation Declares**

- The prayer quotes Hebrews 1:3 as "the exact imprint of your nature"; the ESV has "his".
- "Biologists once assumed the 'simplest' living cell must be complex": probably "simple".
- "At the close of Romans 11:35" probably means Romans 11.
- *Author:* Discussion question 3 asks the reader to judge the study's fairness and needs replacing.

**Genealogy and Times**

- The Samaritan Pentateuch's Methuselah is counted as independent support for the Masoretic Text in
  two places and as an editor's fix in a third.

**Christians and Deliverance Ministry**

- The empty-house argument does not say what the danger is to a believer, whose place the study
  says the Holy Spirit fills.
- "Every occurrence" does not fit John 10:21; deliverance is placed "at conversion" in one place
  and "at the cross" in another; the κολαφίζω caveat is stated twice.
- A block-quoted line may be the site's own words.

**The Day No One Knows**

- A textual-note paragraph sits under the Prayer heading.
- "Lessons about Jesus" repeats a later paragraph almost word for word.
- The "birth-pangs checklist" has no citation (Matthew 24:6-8).
- "No question of incarnational limitation" after the resurrection rests on an unstated
  state-of-exaltation distinction.

**Assurance of Salvation**

- 2 Timothy 1:12 is spliced to end "entrusted to" him; the ESV reads "entrusted to me".
- John 20:31's evangelistic aim is stated as settled; the *pisteusēte*/*pisteuēte* variant is
  contested.
- The council's condemnation of Jesus is cited to Acts 4; it comes from the Gospels.

**The Woman Who Touched the Fringe**

- It says three times that this is the only place Jesus calls a woman "Daughter"; Matthew 9:22
  and Luke 8:48 do too, and Luke 23:28 has "Daughters of Jerusalem".
- Mark 6:56 has the sick touching the κράσπεδον, against "the detail is not Mark's interest" and
  "the one place in Mark where someone touches Jesus first" (see also Mark 3:10).

**Bread of Life**

- Mark 6:39 is bolded as "lie down"; the ESV has "sit down" (ἀνακλῖναι, recline). The Psalm 23
  argument leans on it.
- ἐπιούσιος is called "the rarest word in the New Testament"; it occurs twice.
- ESV wording under a WEB block quote (1 Kings 17); five quotations near the end have no
  translation label.
- "Abundant" in the closing against "sufficient, never abundant" earlier; one claim made twice.
- Be Transformed labels use `**Think:**`, against the site's `**Think.**`.

**Israel and the Church**

- The καινός/νέος distinction is overstated: Colossians 3:10 uses νέος for the "new self" that
  Ephesians 4:24 calls καινός.

**Bible Translations & Source Texts**

- "Four Hebrew words" lists three (Song of Songs 8:6); "only the LSB prints the name" while WEB,
  ASV and YLT do too; "three committees footnote" shows two.
- The link to the Hebrew New Testaments points at `#hebrew-old-testament`. The same wrong anchor
  is on [Public Data Sources](../resources/public-data-sources.md) and possibly the Glossary.

**The Day Is Near**

- James 5:7's μακροθυμέω is defined as patience and *hypomonē* as endurance, yet Be Transformed
  and the prayer call 5:7 "endurance"; "James uses both… at 5:8 and 5:11" reads as if 5:8 has
  *hypomonē*.

**The Twelve and the apostle pages**

- "Nine of the Twelve never speak" and "Six never speak" contradict each other, and neither count
  fits.
- Matthew and Simon "four places apart" holds only in Mark (The Twelve, Matthew, Simon the Zealot).
- "Four independent lists" is not marked contested; the pages disagree on whether Simon belonged to
  the Zealot party.
- Thomas speaks four times in John, not three.
- Thaddaeus is called tenth in the Synoptic lists; Luke has him eleventh. The Jude argument rests
  on "son of James" where the Greek has a bare genitive, "Judas of James".
- Judas Iscariot: the explanation "he was a thief" is in John 12:6, the first mention, not the
  second; the *metamelomai*/*metanoeō* contrast is stated as settled despite Matthew 21:29, 32.
- Bartholomew: "Come and see" is Philip's invitation, not Jesus'.
- Simon the Zealot: "Both men were standing there" (Matthew 22:15-22) is not in the text.
- Matthew: "everyone else in his profession" overstates Luke 5:29.

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

### 1.3 Learning Hebrew

- **Memory verses in Hebrew.** A few key verses to learn in the original, like Genesis 1:1, which
  [Verses Quoted Well](../scripture/verses-quoted-well.md) already gives with its Hebrew and
  pronunciation.
- **The aleph-bet.** Expand the material on [Hebrew Learning
  Resources](../resources/hebrew-learning-resources.md): the first week, the words, and the link to
  the videos. Make sure there is material on the basics, such as learning the alphabet.

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
  (Matthew 16:8), which links this item to [Faith](../salvation/faith.md#why-did-you-doubt).

### 2.5 The heavenly pattern

A series at `jesus/the-heavenly-pattern/` on the furnishings God told Moses to make "after the
pattern for them, which is being shown you on the mountain" (Exodus 25:40, ESV). There is one page
per furnishing. Each follows the furnishing from Sinai through Solomon's temple and the prophets to
Christ and the heavenly sanctuary. Each ends with a table that sorts the connections by how firmly
Scripture makes them: stated in the New Testament, echoed there, inferred, or later tradition.
Hebrews sets the limit: "Of these things we cannot now speak in detail" (Hebrews 9:5, ESV).

Each page gets a plate drawn by `utils/sanctuary_plates.py`. The plate is built from a facts table
that tags every detail as given, inferred or unstated. Unstated details are drawn dashed, with the
tradition that supplies them named.

**Started.** Published, reviewed and corrected, each with its plate: [The
Lampstand](../jesus/the-heavenly-pattern/lampstand.md) and the series
[index](../jesus/the-heavenly-pattern/index.md) (2026-09-28), [The Ark of the
Covenant](../jesus/the-heavenly-pattern/ark.md) and [The Golden Altar of
Incense](../jesus/the-heavenly-pattern/incense-altar.md) (2026-09-29). The lampstand's Revelation 11
material became its own study, [The Two Witnesses](../last-things/two-witnesses.md). Still worth doing:
a read-bible-study pass on each in a fresh session, and restoring the altar page's link to How God
Answers Prayer once that study is published.

The remaining pages, in the order suggested. Figures marked *(verified)* were checked against the
text or the concordance when the series was planned; the rest still need checking.

- **Index: "According to the pattern."**
    - *Tabnit* (<span dir="rtl">תַּבְנִית</span>, H8403) names God's pattern for the sanctuary
      (Exodus 25:9, 40; 1 Chronicles 28:11-19). It also names the carved "likeness" God forbids
      (Deuteronomy 4:16-18), the Damascus altar Ahaz had copied (2 Kings 16:10), and the forms of
      creeping things drawn on the temple walls (Ezekiel 8:10) *(verified)*.
    - The Greek words for copy: *typos*, *hypodeigma*, *skia* and *antitypa* (Acts 7:44; Hebrews
      8:5; 9:23-24).
    - A plate of the whole plan. God gives the instructions from the inside out, starting with the
      ark (Exodus 25:10), while a worshipper comes in from the gate. The plate shows both routes,
      with metals keyed: bronze outside, gold inside, silver under the frames.
    - Two cubits: Ezekiel's longer one (Ezekiel 43:13) and "cubits of the old standard" (2 Chronicles
      3:3).
- **The ark and the mercy seat.** Published as [The Ark of the Covenant](../jesus/the-heavenly-pattern/ark.md); planning notes kept below.
    - At Sinai: 2½ × 1½ × 1½ cubits (Exodus 25:10). The poles were never to be removed (Exodus
      25:15). God says, "There I will meet with you" (Exodus 25:22). The mercy seat's thickness is
      not given.
    - Solomon's cherubim (1 Kings 6:23-27), with the poles still visible (1 Kings 8:8).
    - What was in the ark. Hebrews 9:4 puts the manna jar, Aaron's rod and the tablets inside it.
      1 Kings 8:9 says there was nothing in it but the tablets *(verified)*.
    - Jeremiah 3:16 says the ark "will not come to mind… nor will another be made." The ark is
      nowhere in Ezekiel *(verified)*. John sees it in heaven (Revelation 11:19).
    - *Hilastērion* is the Septuagint's word for the mercy seat. It also names the ledges of
      Ezekiel's altar (Ezekiel 43:14, 17, 20) *(verified)*. Paul calls Christ the *hilastērion*
      (Romans 3:25), and Hebrews 9:5 uses the word for the mercy seat.
    - The veil: Exodus 26:31; Matthew 27:51; Hebrews 10:20.
- **The table and the bread of the Presence.**
    - At Sinai: 2 × 1 × 1½ cubits (Exodus 25:23). Twelve loaves, set out every Sabbath (Leviticus
      24:5-9) *(verified)*. *Ma'arakhot* can mean rows or stacks, and the plate has to flag which.
    - David eats the bread (1 Samuel 21:6), and Jesus cites it (Matthew 12:3-4).
    - Solomon's ten tables (2 Chronicles 4:8) and David's silver tables (1 Chronicles 28:16)
      *(verified)*.
    - Ezekiel's wooden altar is "the table that is before Yahweh" (Ezekiel 41:22) *(verified)*.
    - John 6:35 as an echo.
    - The lampstand page's note that the lamps lit the table (Numbers 8:2; Exodus 26:35) connects
      the two pages.
- **The altar of incense.** Published as [The Golden Altar of Incense](../jesus/the-heavenly-pattern/incense-altar.md); planning notes kept below.
    - At Sinai: 1 × 1 × 2 cubits, before the veil, with its horns touched with blood once a year
      (Exodus 30:1-10).
    - Hebrews 9:4's *thymiatērion* is the Septuagint's word for a censer (2 Chronicles 26:19;
      Ezekiel 8:11) *(verified)*. That is why the KJV has "golden censer." The page should argue it
      both ways.
    - Later: Uzziah (2 Chronicles 26), Zechariah's service (Luke 1:9-11), Psalm 141:2, and the golden
      altar before the throne (Revelation 5:8; 8:3-5).
- **The bronze altar.**
    - Three sizes: 5 × 5 × 3 cubits at Sinai (Exodus 27:1); 20 × 20 × 10 under Solomon (2 Chronicles
      4:1) *(verified)*; Ezekiel's stepped altar, with a 12 × 12 hearth, a 14 × 14 ledge and steps
      facing east (Ezekiel 43:13-17) *(verified)*.
    - Ahaz's copied altar (2 Kings 16:10-16). "We have an altar" (Hebrews 13:10). The souls under
      the altar (Revelation 6:9), and which altar that is.
    - Plate: all three altars at one scale.
- **The basin and the bronze sea.**
    - At Sinai the basin has no measurements. It was made from the mirrors of the ministering women
      (Exodus 38:8), for washing hands and feet "that they not die" (Exodus 30:18-21) *(verified)*.
    - Solomon's sea: 10 cubits across, 30 around and 5 high, standing on twelve oxen (1 Kings
      7:23-25) *(verified)*.
    - Two differences between Kings and Chronicles. The sea holds 2,000 baths (1 Kings 7:26) or
      3,000 (2 Chronicles 4:5), and has gourds (1 Kings 7:24) or oxen (2 Chronicles 4:3) under the
      brim *(verified)*.
    - Ten basins on wheeled stands (1 Kings 7:27-39). The sea "was for the priests to wash in"
      (2 Chronicles 4:6).
    - There is no basin in Ezekiel *(verified)*; a river flows from under the threshold instead
      (Ezekiel 47:1).
    - John 13:10. The sea of glass (Revelation 4:6; 15:2) and "the sea was no more" (Revelation
      21:1). Whether the sea of glass answers to the basin is contested.
- **The house, from tent to city.**
    - The tent's frames are 10 cubits tall and 1½ wide, 20 on each side, making 30 cubits (Exodus
      26:16-25) *(verified)*. The width depends on how the corner frames are read, and the plate can
      show the working.
    - The silver sockets came from the atonement money (Exodus 30:11-16; 38:25-27).
    - The Most Holy Place over time: a 10-cubit square (reconstructed), Solomon's 20-cubit cube
      (1 Kings 6:20), Ezekiel's 20-cubit square (Ezekiel 41:4), and the city's cube (Revelation
      21:16). The page links to [The New Jerusalem](../last-things/new-jerusalem.md) rather than
      repeating it.
- **Optional: the high priest's garments** (Exodus 28). The breastpiece stones lead into the city's
  foundations (Exodus 28:17-21; Revelation 21:19-20). *Podērēs*, the robe of Revelation 1:13, is
  already worked out on the lampstand page.

**Settle first.** Ezekiel's temple has sacrifices (Ezekiel 43:18-27). A dispensational reading has
to say what they are in a future temple, and the [statement of faith](statement-of-faith.md) is
silent. The author needs to decide before the Ezekiel sections of the altar and house pages are
written.

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

**In progress:** [At Home with the Lord](../last-things/at-home-with-the-lord.md) is published
(2 Corinthians 5:1-8, the believer with Christ between death and resurrection), and the body that
follows is [We Shall All Be Changed](../last-things/we-shall-all-be-changed.md) (5.8). Still to fold in
from the notes above: the thief on the cross, Moses and Elijah at the Transfiguration, and Luke 16.

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
- **Not the resurrection body.** [We Shall All Be Changed](../last-things/we-shall-all-be-changed.md#the-white-robes-are-a-different-gift)
  notes that the robes of 6:11 are given to souls not yet raised, so they cannot be the body of
  1 Corinthians 15. Both are clothing (ἐνδύω, "put on", 1 Corinthians 15:53-54) and both are God's
  gift; this study says what the robes are.

### 5.7 Heaven and earth by fire

What happens after the thousand years: Satan's release, the fire from heaven, the great white
throne, and the passing of the present heaven and earth by fire before the new heaven and new earth.
No study works through it.
[Heaven and Earth Will Pass Away](../last-things/heaven-and-earth-will-pass-away.md) (spun off from
the Olivet Discourse, published 2026-09-28) places it in two paragraphs ("Where it falls") and stops there.

- **Texts:** 2 Peter 3:7-13 read alongside Revelation 20:7–21:1; Isaiah 65:17 and 66:22; Isaiah
  51:6; Hebrews 1:10-12 (Psalm 102:25-27); Hebrews 12:26-28 (Haggai 2:6); Romans 8:18-25. Verify
  each wording against the ESV before quoting.
- **Order of events:** does the fire of 2 Peter 3:10-12 fall at the same point as Revelation 20:9
  (fire on Gog and Magog) and 20:11 ("earth and sky fled away"), or are they separate? Say where the
  text settles the sequence and where it is inferred.
- **Renewal or replacement:** the open question the sibling draft records. The textual problem at
  2 Peter 3:10 ("will be found", "will be burned up", "will not be found") bears on it, and so does
  καινός (*kainos*, G2537) against νέος (*neos*) for "new". Count and check the lexica before
  claiming a distinction.
- **The day of the Lord as a period:** the dispensational reading that it opens with the thief-like
  coming and closes with the dissolution a thousand years later. Check it against the
  [statement of faith](statement-of-faith.md#end-times), and give the amillennial case.
- **Links:** [A Day Is a Thousand Years](../last-things/day-is-a-thousand-years.md) (2 Peter 3:7,
  the seventh day and the eighth), [The Wife of the Lamb](../israel-and-church/wife-of-the-lamb.md)
  (Revelation 21), and [The End of the Age](../last-things/end-of-the-age.md) (5.5, completed).

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

### 8.2 Chronology follow-ups

Left over from moving the site's chronology to the Masoretic numbers on 2026-09-28 (see
[The Flood and the King Lists](../chronology/flood-and-the-king-lists.md#why-this-site-follows-the-masoretic-numbers)).

- **Terah's birth year.** [Genealogy and Times](../chronology/genealogy-times.md) works Terah's
  puzzle from 1876 BC; the generator (`references/build/genealogy_chronology.py`) uses 1878. Find
  which is right and make the other agree.
- **Stale source paths.** Existing references in `docs/data/chronology.json` point at
  `studies/prophecy/...`, which no longer exists. Repoint them at the current pages.
- **Steinmann's count.** The Flood study cites 467 secondary readings in the Septuagint
  (Steinmann, *JETS* 64/1, 2021, pp. 26, 29, 34); his own prose says 468 once (p. 33). Note the
  discrepancy in the study or confirm which figure his table supports.
- **Genealogy and Times:** simplified, restructured and given its Study outline on 2026-09-30. The
  file is still 4,825 words, so re-run validator Check 23 and either trim further or record a
  raised `word_budget` and its reason in the state file.
- **The Flood study skipped two passes.** It was published straight after its develop pass. Run
  read-bible-study (in a fresh session) and review-bible-study on it.

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

> ✝️ Revelation 3:20 (ESV)
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
- **Links:** 10.3 (religion and a contrite heart), [The Way](../jesus/the-way.md), and
  [Faith](../salvation/faith.md#the-door-every-morning), which reads the verse as the door faith opens.

### 10.6 Run the race

**Drafted** as `christian-life/run-the-race.md` (still a draft, so not linked until it is
published). Check the draft against these notes before it is published.

We come to Christ at His invitation, for rest. His burden is light, far lighter than the burden of
salvation through works (Matthew 11:28-30). So why do Christians grow weary? How do we run the race
with endurance (Hebrews 12:1), set our faces like flint (Isaiah 50:7), and press on to take hold of
that for which Christ took hold of us (Philippians 3:12)?

- **What keeps us running:** meeting together and encouraging each other; prayer, as communion and
  daily bread; living on the word.
- **What does not:** doing works to be seen as pious; fasting to earn life; taking in all the news
  and troubles of the world, the cares of life that choke the seed. In short, everything that took
  the word away in the parable of the sower.
- **Proverbs:** guard your heart and mind (Proverbs 4:23), and trust Him.

## Completed

Kept here so that an old reference like "work on 3.1" still resolves.

| Ref | Item | Now |
|---|---|---|
| 2.2 | Priest of the order of Melchizedek | [Jesus, Priest in the Order of Melchizedek](../jesus/melchizedek-priesthood.md); rewritten 2026-10-02 to say what a priest is and what "the order" means before the evidence |
| 3.1 | Nephilim | [The Nephilim](../spiritual-beings/nephilim.md) |
| 4.1 | Assurance of salvation | [Assurance of Salvation](../salvation/assurance-of-salvation.md) |
| 4.3 | Faith | [Faith](../salvation/faith.md) |
| 5.3 | The last trumpet | [The Trumpet Call of God](../last-things/trumpet.md) |
| 7.1 | Twelve disciples | [The Twelve: Disciples and Apostles](../biblical-figures/twelve-apostles.md), with a page per apostle |
| 10.1 | Know the truth | [Know the Truth](../christian-life/know-the-truth.md) |
| 0.1 | Scripture pop-up on a verse reference | Every reference on the site opens the verse, its context, cross-references and the studies that treat it, 2026-09-27. Blue Letter Bible links removed |
| 0.2 | Word-study pop-up on an original-language word | Every Strong's tag, and the word in front of it, opens a word card: lexicon, counts, where it occurs, renderings, and the studies that discuss it, 2026-09-27. Follow-ups in [0.6](#06-pop-up-follow-ups) |
| 0.3 (part) | Normalise the Key Takeaways opening line | Done across 50 studies, 2026-09-27 |
| 0.4 | New studies shown apart from updated ones | [New this month](recent-updates.md#new) on Recent updates and the homepage, dated from the commit that took each page out of draft, and a "New" line under the title and icon in the nav for 30 days, 2026-09-28. The feed idea moved to [0.5](#05-a-blog) |
| 5.4 | The Olivet Discourse, regrouped by the disciples' questions | [The Olivet Discourse](../last-things/olivet-discourse.md) regrouped under the question each part answers, a section on which question the flight to the mountains answers (marked contested), and "one taken, one left" pointed at [One Taken, One Left](../last-things/one-taken-one-left.md) from both it and the rapture study, 2026-09-28 |
| 5.8 | We will all be changed, raised imperishable | [We Shall All Be Changed](../last-things/we-shall-all-be-changed.md) (1 Corinthians 15:35-58), linked from At Home with the Lord (4.2); the white robes of 5.6 treated as a separate gift, 2026-09-28 |
| 10.5 | In humility | [In Humility](../christian-life/humility.md) (Philippians 2:1-11), rooted in dependence on God; its counterpart [Pride](../sin/pride.md), with "You are gods" and the Isaiah 14 / Ezekiel 28 question marked contested, 2026-09-28 |
| 10.2 | Where two or three are gathered | [Where Two or Three Are Gathered](../israel-and-church/where-two-or-three-are-gathered.md) (Matthew 18:15-20), filed under the church because the passage is about the church dealing with a brother's sin; gives a verdict on each church use of the verse, with prayer alone and together, 2026-10-01 |
| new | Commonly misquoted scripture | [Verses Often Misquoted](../scripture/verses-often-misquoted.md): 1 Peter 3:15, Matthew 18:20, John 8:32, 1 Corinthians 15:44, Mark 9:29 and "demonized" (Mark 5:15), each linked to its study, 2026-10-01 |
| new | Well used scripture | [Verses Quoted Well](../scripture/verses-quoted-well.md): Genesis 1:1 (with the Hebrew and pronunciation), John 3:16 and Hebrews 11:1, 2026-10-01 |
| 6.1 | Appointed times (overarching) | [The Appointed Times](../feasts/feasts.md), linking each feast to its own study; the Feasts section ordered by the calendar, 2026-10-02 |
| 6.2 | Individual feast studies | [Passover](../feasts/passover.md), [Unleavened Bread](../feasts/unleavened-bread.md), [Firstfruits](../feasts/firstfruits.md), [Weeks](../feasts/weeks.md), [Trumpets](../feasts/trumpets.md), [Day of Atonement](../feasts/day-of-atonement.md) and [Tabernacles](../feasts/tabernacles.md), all published by 2026-10-02 |
| 6.3 | The Lord's Supper | [The Lord's Supper: Do This in Remembrance of Me](../feasts/lords-supper.md), with two graphics; the [four-cups study](../feasts/last-supper-four-cups.md) now points its general communion material there, 2026-10-02 |
| new | Edits to Verses Often Misquoted | [Verses Often Misquoted](../scripture/verses-often-misquoted.md) opens on common church sayings, adds "Did God actually say?" (the garden, the wilderness, the church), "Take up your cross" and a link to How to Read the Bible, 2026-10-02 |
| 5.5 | The age to come | The age to come in [A New Heaven and a New Earth](../last-things/new-heaven-and-new-earth.md#the-age-to-come); the line between the ages in [The End of the Age](../last-things/end-of-the-age.md) (Matthew's συντέλεια, opened at the cross and closed at the return), with cross-links and a scope line on each, and the Zadok calendar's 49- or 50-year jubilee question, 2026-10-03 |
| 10.7 | Forgiveness | [Forgive Us Our Debts](../christian-life/forgiveness.md), on Matthew 6:14-15: God's forgiveness paid and offered to all and received by those who repent, releasing a debt to God (Mark 11:25) and forgiving the one who repents (Luke 17:3-4), the offender who keeps on, Matthew 6:15 used as a weapon, and what forgiveness is not, 2026-10-04 |
| 5.9 | The tribulation period | [The Tribulation: Daniel's Seventieth Week, Year by Year](../last-things/tribulation.md): what the week is for, the seals, trumpets and bowls in order, the midpoint, and where the church, Israel and the tribulation saints are, with four charts, 2026-10-03 |
| 10.8 | Fasting: a rewrite | [Fasting](../christian-life/fasting.md) rewritten so "When to fast" no longer reads as deliverance ministry (2 Corinthians 10:4's strongholds are arguments), then reviewed, 2026-10-01 |
| new | Hurt by the Church | [Hurt by the Church: Wolves, Weeds and the Good Shepherd](../christian-life/hurt-by-the-church.md), published with its review and a readability pass, 2026-10-04 |
| 0.8 | Fixes found by reviews | [Christians and Deliverance Ministry](../spiritual-beings/deliverance/christians-and-deliverance.md) now quotes John 10:20-21 correctly (δαιμόνιον ἔχει in 10:20, the participle in 10:21) and treats κολαφίζω as suggestive rather than decisive; [As the Snake Was Lifted Up](../jesus/as-the-snake-was-lifted.md) marks the οὕτως reading contested; Paul added to the Biblical Figures sidebar, 2026-10-04 |
