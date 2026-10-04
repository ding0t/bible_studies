---
title: "Genealogy and Times: From Creation to Christ"
category: "prophecy"
description: "Tracing the covenant line from Adam to Christ through Genesis 5 and 11's genealogies, comparing the Masoretic Text, Septuagint, and Samaritan Pentateuch, and asking what the names themselves are saying"
tags: ["genealogy", "chronology", "creation", "method/word-study", "method/textual-criticism"]
draft: false
primary_passage: "Genesis 5; Genesis 11:10-32"
bible_references: ["Genesis 3:15", "Genesis 5:1-32", "Genesis 11:10-32", "Genesis 12:4", "Luke 3:23-38", "Matthew 1:1-17", "Acts 7:4", "Romans 5:12-21", "1 Corinthians 15:22", "1 Corinthians 15:45"]
date_created: 2026-07-24
date_modified: 2026-10-04
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-opus-5.5
  - anthropic/claude-sonnet-5
---

# Genealogy and Times: From Creation to Christ

**The three surviving manuscript traditions put creation as much as 1,466 years apart. The gap is
patterned rather than random. A hundred years per patriarch, repeated down the list, which somebody
introduced deliberately.** Which somebody, and in which direction, is the question this page works
through.

Jesus's genealogy is recorded twice (Matthew 1, Luke 3), and Luke's runs all the way back to Adam.
Genesis 5 and 11:10-26 are the only places in the Old Testament that give a father's age at his
heir's birth generation after generation. Both are read here in all three witnesses. Those are the
Masoretic Text, the Hebrew that underlies most English Bibles; the Septuagint, the Greek translation
made by Jewish scholars around the third century BC and the version the New Testament writers most
often quote; and the Samaritan Pentateuch, preserved independently of both. The reasoning here feeds
[docs/data/genealogy](https://github.com/ding0t/bible_studies/tree/main/docs/data/genealogy)'s
structured files.

Two things are true at once, and neither collapses into the other. The genealogy is a real
chronological record, precise enough to argue over and
capable of being wrong in transmission — and it is also a theologically shaped document,
tracking a single promised line (Genesis 3:15's "seed of the woman") through named individuals
whose names themselves carry meaning. Getting the math right and hearing what the names say are
not competing projects.

**In one sentence:** Genesis 5 and 11 give a real chronology whose Masoretic numbers hold up best of the three witnesses, and the line they count carries God's promise by name from Adam to His Son Jesus, so you can trust the God who kept it one generation at a time to keep His promises to you.

## Study outline

- **How Genesis gives this data** — the fathering-age formula of Genesis 5 and 11, and where it stops.
- **The three witnesses** — the Masoretic, Septuagint and Samaritan numbers side by side, and the
  patterns in how they differ.
- **Case studies** — the second Cainan, Methuselah's death and the Flood, and Terah's age at Abram's
  departure.
- **Word studies** — which of the Genesis 5 names hold up in the lexicon.
- **Toward a most probable timeline** — why the site follows the Masoretic numbers, and the dates that
  result, and what stays open.
- **What this means for prophecy and Christ** — Matthew's and Luke's genealogies, and the promise
  carried through named people.
- **Annex: dating choices and open work** — the two data choices behind the dates, and the open items still tracked.

## How Genesis actually gives this data

Genesis 5 (Adam to Noah) and Genesis 11:10-26 (Shem to Terah) share a distinctive formula, repeated
once per patriarch: *he lived [age], and fathered [heir]; he lived [years] more after fathering
[heir], and had other sons and daughters; all his days were [total]*. That formula is what makes
three-way manuscript comparison possible at all — nowhere else in Scripture is this much
chronological data given about this many consecutive individuals. It also stops cold after Terah:
Genesis 11:26 gives his age, but from Abraham onward the text gives ages at specific named events
(Abraham 100 at Isaac's birth, Genesis 21:5; Isaac 60 at Jacob's, Genesis 25:26) rather than a
systematic per-generation formula. That is a real change in genre rather than a gap in the data. The
rest of this study's method compares an "age at heir's birth" figure across manuscripts. It cannot
apply past Terah, because Genesis stops giving one.

## The three witnesses

- **The Masoretic Text (MT)** — the one this site's own `zadok_year` numbering already assumes (see
  [The Zadok Calendar](../feasts/zadok-calendar.md) for the calendar side of that convention).
- **The Septuagint (LXX)**, in the Brenton edition, whose Genesis 5 and 11 numbers diverge from
  MT's in a patterned way (below).
- **The Samaritan Pentateuch (SP)** — the least commonly consulted of the three: it smooths the Terah
  puzzle MT and LXX read with Acts 7:4, and it corroborates MT's Methuselah result by an entirely
  different set of numbers (both below).

All figures below were queried directly from this repo's `references/build/bible-text.db`
(`morphhb-wlc` for MT, `ebible-grcbrent` for LXX, `scrollmapper-SP` for SP) and cross-checked by
computer against each tradition's own stated total (`age at heir's birth + years after = total
lifespan` — see `references/build/genealogy_chronology.py`, which fails loudly if a figure
doesn't add up). Every number here passed that check.

### Genesis 5: Adam to Noah

| Patriarch | MT (age / after / total) | LXX (age / after / total) | SP (age / after / total) |
| --- | --- | --- | --- |
| Adam | 130 / 800 / 930 | 230 / 700 / 930 | 130 / 800 / 930 |
| Seth | 105 / 807 / 912 | 205 / 707 / 912 | 105 / 807 / 912 |
| Enosh | 90 / 815 / 905 | 190 / 715 / 905 | 90 / 815 / 905 |
| Cainan (Kenan) | 70 / 840 / 910 | 170 / 740 / 910 | 70 / 840 / 910 |
| Mahalalel | 65 / 830 / 895 | 165 / 730 / 895 | 65 / 830 / 895 |
| Jared | 162 / 800 / 962 | 162 / 800 / 962 | **62 / 785 / 847** |
| Enoch | 65 / 300 / 365 (no death) | 165 / 200 / 365 (no death) | 65 / 300 / 365 (no death) |
| Methuselah | 187 / 782 / **969** | 167 / 802 / **969** | **67 / 653 / 720** |
| Lamech | 182 / 595 / **777** | 188 / 565 / **753** | **53 / 600 / 653** |
| Noah (age at Shem/Ham/Japheth) | 500 | 500 | 500 |

For six of these nine (Adam through Mahalalel, and Enoch) LXX adds exactly 100 years to the
age-at-heir-birth figure and subtracts the same 100 from years-after, so the *total* lifespan is
identical across MT, LXX, and SP every time. A constant offset six times over, with the total kept
each time, is a deliberate shift on someone's part. Copying errors do not produce it.

Jared, Methuselah, and Lamech break that pattern, each differently. Jared is untouched by the
LXX shift (MT and LXX agree exactly) but SP shortens both his age and his total. Methuselah keeps
his 969 total in MT and LXX, but LXX moves his fathering age *down* 20 years (167 for 187), and SP
shortens the total itself. Lamech is the strangest: all three traditions give a different total
(777 / 753 / 653), with no two agreeing against the third.

### Genesis 11:10-26: Shem to Terah

| Patriarch | MT | LXX | SP |
| --- | --- | --- | --- |
| Shem | 100 / 500 / 600 | 100 / 500 / 600 | 100 / 500 / 600 |
| Arphaxad | 35 / 403 / 438 | 135 / 400 / **535** | 135 / 303 / 438 |
| *(Cainan)* | — (absent) | 130 / 330 / 460 | — (absent) |
| Shelah | 30 / 403 / 433 | 130 / 330 / 460 | 130 / 303 / 433 |
| Eber | 34 / 430 / 464 | 134 / 270 / 404 | 134 / 270 / 404 |
| Peleg | 30 / 209 / 239 | 130 / 209 / 339 | 130 / 109 / 239 |
| Reu | 32 / 207 / 239 | 132 / 207 / 339 | 132 / 107 / 239 |
| Serug | 30 / 200 / 230 | 130 / 200 / 330 | 130 / 100 / 230 |
| Nahor | 29 / 119 / 148 | 179 / 125 / 304 | 79 / 69 / 148 |
| Terah | 70 / 135 / 205 | 70 / 135 / 205 | 70 / **75 / 145** |

A different, equally consistent pattern runs from Arphaxad through Serug: SP takes LXX's
higher age-at-heir-birth figure but keeps *MT's total*, by shortening years-after to compensate.
Five patriarchs (Arphaxad, Shelah, Peleg, Reu, Serug) do this identically, which is an editorial
signature. Eber breaks the run (SP just matches LXX outright, total included). Nahor breaks it a
third way (three different ages, though SP's total still matches MT's). And Terah —
the last one, and the most consequential — breaks it in the direction that matters most for
everything downstream.

## Case studies

### The Cainan question

Luke 3:36 names a Cainan between Arphaxad
and Shelah. MT and SP don't have him; LXX does, with his own full entry (130 years to Shelah's
birth, 330 more after, 460 total — Genesis 11:13 LXX).
This looks at first like Luke following the Greek tradition against the Hebrew, and this study
previously read it that way. The manuscript evidence points the other direction.

#### The case for a later insertion

**Luke's own text is contested.** The two earliest witnesses to this verse omit Cainan:
𝔓⁷⁵, the oldest extant manuscript of Luke, from the early third century, and the fifth-century
Codex Bezae. Every witness that has him is fourth-century or later, beginning with Codex
Vaticanus. Andrew Steinmann's survey (*JETS* 60/4, 2017) lists the sources with no knowledge of
Cainan in chronological order: the Samaritan Pentateuch (c. 100 BC), Josephus, Targum Onkelos,
Theophilus of Antioch, Julius Africanus, *Seder 'Olam Rabbah*, 𝔓⁷⁵, Targum Neofiti, Targum
Pseudo-Jonathan, and Codex Bezae.

**The Samaritan silence is the loudest.** Seven fathering ages in Genesis 11 are disputed, and SP
sides with LXX against MT in six of them (all but Nahor's). Its whole tendency in this passage is
toward the Greek numbers, and it still has no Cainan.

**The Septuagint contradicts itself.** 1 Chronicles 1:24
runs Arphaxad straight to Shelah with no Cainan, in the Masoretic Text *and* in Brenton's
Septuagint. A generation present in one Greek book and absent from the Greek parallel is a
generation with a transmission problem.

**The numbers give it away.** LXX Genesis 11:12-13 gives Cainan 130 years before Shelah's birth
and 330 after. Those are exactly the figures LXX gives Shelah before and after fathering Eber
in the next two verses. Nowhere else in Genesis 5 or 11, in MT, LXX or SP, does a father share
both numbers with his son. The entry reads as a duplicated block
with the name swapped.

**And the insertion has an obvious trigger.** Luke 3:37 names the antediluvian Cainan one line
below. A copyist's eye skipping from *Shelah* to a line ending in *Cainan* inserts the name at
3:36 without effort. No comparable mechanism explains an accidental deletion from 𝔓⁷⁵ and Bezae.

#### The contested counter, and the working position

Against all that: NA28 and UBS still print Cainan at Luke 3:36 unbracketed, Helen Jacobus (*JSP*
18, 2009) has argued he was original to the Hebrew, and one recent paper questions the
identification of the 𝔓⁷⁵ fragment itself. The question is contested rather than closed.

The working position here is that Cainan entered Luke by copying error in the third or fourth
century and was then harmonized into the Greek Genesis. For the arithmetic that means the LXX
chronology carries 130 years it should not, and the `lxx` variant in
`docs/data/genealogy/` inherits them.

### Methuselah: the name, the number, and the Flood

#### Two readings of the name

Methuselah's name (<span dir="rtl">מְתוּשֶׁלַח</span>) is ambiguous at the lexical level — not "one attested
reading and one folk etymology," but two real readings built from real roots. Read as *m'tei*
("men of") + *shelach* ("javelin," H7973), it's a plain warrior name with no theological
freight. Read as *mut* ("die," H4191) + *shalach* ("send," H7971), it becomes a sentence-name:
"his death shall send [it]." Both parse correctly; nothing in the lexicon settles which one the
name-giver intended.

#### The arithmetic in each tradition

What tips the scales toward the second reading is arithmetic rather than etymology. And the
arithmetic has to be run separately in each tradition, because the three chains put Methuselah's
death in three different places relative to the Flood. The Flood itself is fixed the same way in all
of them: Noah is six hundred when it comes (Genesis
7:6,
<span data-ref="Genesis 7:11">7:11</span>), so each tradition's Flood year is simply its
own Noah's birth year plus 600.

| Tradition | Methuselah born | dies | Flood | Result |
| --- | --- | --- | --- | --- |
| MT | AM 687 | AM 1656 | AM 1656 | dies in the Flood year |
| SP | AM 587 | AM 1307 | AM 1307 | dies in the Flood year |
| LXX | AM 1287 | AM 2256 | AM 2242 | outlives the Flood by 14 years |

MT lands it exactly. Adding the seven fathering-ages from Adam down to Enoch puts Methuselah's birth
at AM 687. His 969-year total carries him to AM 1656. That is the same year Noah turns 600. Nothing
in that sum was arranged to produce the result. It falls out of figures given one verse at a time
across Genesis 5. The longest life in the record ends in the year the judgment arrives.

SP reaches the same result by a different road. Its Jared fathers Enoch at 62 rather than 162,
which pulls Methuselah's birth 100 years back to AM 587, and its Methuselah totals 720 rather
than 969. Both ends move, and they move together: his death lands in AM 1307,
again the Flood year. Two traditions that disagree about nearly every number in the chapter
agree about this one relationship.

#### The Septuagint: Methuselah outlives the Flood

LXX alone breaks it, and by a specific 14 years. Its extra hundreds above Methuselah move his
birth and the Flood together, so they change nothing here. The 14 comes from the two fathering
ages after his birth: Methuselah fathers Lamech at 167 (MT 187) and Lamech fathers Noah at 188
(MT 182), a net 14 years less between Methuselah's birth and the Flood. His 969 years then carry
him to AM 2256 against a Flood at AM 2242. A man whose name may mean "his death shall send [judgment]" then outlives that
judgment by fourteen years. This is a real problem, long noted — but it belongs to the
Septuagint, not to the Hebrew, and it appears in the same tradition that carries the spurious
Cainan discussed [above](#the-cainan-question). If the eschatological reading of the name is
right, MT and SP both already agree with it, and the only witness that disagrees is the one with
an independent transmission problem in the same chain.

### Terah and Abram: a puzzle two different ways

This is the most consequential single data point in the whole survey, because it's not a
disagreement about a name's meaning — it's an internal tension inside the text of Genesis
itself, and MT and SP resolve it in two structurally different ways.

#### Two resolutions: the Masoretic 205 and the Samaritan 145

Genesis 11:26 states Terah was 70 when he fathered Abram (named first, alongside Nahor and Haran —
birth order not stated). But Genesis 12:4 has Abram leaving Haran at 75, and Acts 7:4
is explicit that this happened *after* Terah's
death. Under MT/LXX's stated 205-year total for Terah (born zadok year 1878 on MT's own numbers),
the plain "70 at Abram" reading puts Abram's departure at 1948+75=2023, a full 60 years *before*
Terah dies in 2083. That is a real contradiction with Acts 7:4. It is why the standard
harmonization reinterprets Genesis 11:26: Abram is listed first for his covenant importance and
was the youngest of the three sons, born when Terah was 130. Run it again: 1878+130=2008, +75=2083,
exactly Terah's death year.

SP's total for Terah is 145. Run the plain 70-year reading Genesis 11:26 states outright, with no
assumption about birth order, and 70 + 75 = 145 exactly. Terah's death and Abram's departure land
on the same year with no harmonizing move at all. MT's resolution reads past the plain sense of
one verse to save the numbers; SP's numbers already match it.

#### Contested: the study Bibles and this site's reading

**Which is original is contested, and the study Bibles lean the other way from this site.** The
NLT footnotes Genesis 11:32 "Some ancient versions read 145 years; compare 11:26 and 12:4" (*NLT
Life Application Study Bible*). The *ESV Study Bible* suggests Stephen "was following an
alternative text (represented today in the Samaritan Pentateuch)", and the *NIV Biblical Theology
Study Bible* says the 205 "may be due to a mistake by an early copyist." This site reads the same
fit as the mark of a harmonizing scribe, because a reading that removes a difficulty this neatly is
what a scribe produces, and follows the Masoretic 205; see
[Following the Masoretic numbers](#following-the-masoretic-numbers) below.

## Word studies: what the names actually say

Popular teaching sometimes strings the Genesis 5 names into a sentence. Seth (appointed), Enosh
(mortal man), Kenan (sorrow), Mahalalel (the Blessed God), Jared (shall come down), Enoch
(teaching), Methuselah (his death shall bring), Lamech (the despairing), Noah (rest/comfort). Read
together, that gives something like: *Man is appointed mortal sorrow, but the Blessed God shall come
down, teaching that his death shall bring the despairing rest.* That reads well. Whether it holds is
a question for the lexicon, name by name.

Querying this repo's own TWOT root data (`references/build/twot_lookup.py`) name by name, rather
than trusting the chain as a whole:

| Name | Verdict | What's actually attested |
| --- | --- | --- |
| Seth | **Solid** | "Appointed" — Genesis 4:25 states the wordplay itself; not reconstructed |
| Enosh | **Solid** | "Mortal man" — frailty-connoting, distinct from *adam*/*ish*, but inferred from usage elsewhere, not an in-text gloss |
| Kenan | *Speculative* | No TWOT root for the name at all; "sorrow" rests on an unconfirmed link to a different root |
| Mahalalel | **Solid** | "Praise of God" — transparent theophoric compound |
| Jared | **Solid** | "Descent" — direct nominal form of "to come down" |
| Enoch | **Solid**, imprecise popularly | "Dedicated/initiated" (same root as Proverbs 22:6) — "teaching" is a loose paraphrase |
| Methuselah | **Ambiguous, both real** | See above — not one solid reading and one invented one |
| Lamech | **Unknown** | No TWOT root exists; standard lexicons mark the derivation uncertain |
| Noah | **Solid**, needs precision | Genesis 5:29's own wordplay uses *nacham* ("comfort"), not *nuach* ("rest") — a real double sound-play, not a simple derivation |

So six of the nine names hold up on their own lexical merits. One, Methuselah, is a real and
motivated ambiguity rather than a coin-flip. Two, Kenan and Lamech, have no lexical footing for the
reading the popular chain wants from them. That doesn't wreck the pattern: six solid, theologically
resonant names out of nine (appointed, [frail] man, praise of God, shall come down, dedicated, comfort)
is still a real feature of the text. But claiming a complete nine-word sentence
requires filling two genuine gaps with unattested glosses. Rounding "suggestive" up to "complete" is
the temptation, and it is a real one.

## Toward a most probable timeline

### Following the Masoretic numbers

**Since 2026-09-28 this site follows the Masoretic Text for every number in Genesis 5 and 11,
Terah included.** The full case, with the confidence each part carries, is in
[The Flood and the King Lists](../god/flood-and-the-king-lists.md#why-this-site-follows-the-masoretic-numbers).
In brief:

- **Scripture's own test.** Only the eight in the ark survive the Flood (Genesis 7:23; 1 Peter
  3:20). The Septuagint as printed keeps Methuselah alive fourteen years past it, so it cannot be
  the original there. The Masoretic arithmetic lands his death in the Flood year exactly.
- **Scribal habits.** Andrew Steinmann's collation of every variant in Genesis (*JETS* 64/1, 2021)
  finds the fewest secondary readings in the Masoretic and the most in the Septuagint, with the
  Samaritan and Greek sharing enough secondary readings to mark them as one text type. When those
  two agree against the Hebrew they count once.
- **The patterns.** The Septuagint's +100 in Genesis 5 keeps every total unchanged, and the
  Samaritan has Jared, Methuselah and Lamech all die in its Flood year. Both look like editors
  solving problems. So does the shared +100 in Genesis 11, which thins out the crowd of long-lived
  ancestors the Hebrew leaves around Abraham.
- **Terah.** The Samaritan 145 reconciles Genesis 11:26 with Acts 7:4, which is the same
  harmonizing habit at work. The Masoretic 205 already satisfies Acts 7:4 once Abram, named first
  for his importance, is read as born when Terah was 130 ([above](#terah-and-abram-a-puzzle-two-different-ways)).

### Deriving the Gregorian dates

Zadok year 0 is Adam's creation, so each variant is anchored on one downstream point, the Exodus,
and its creation date falls out of its own chain length.

Computed results (`references/build/genealogy_chronology.py`, anchored on the Exodus at 1446 BC,
Terah to Abram per Acts 7:4, Abram's call to the Exodus per Galatians 3:17):

| Variant | Creation | Flood (zadok / Gregorian) | Terah's death (zadok / Gregorian) |
| --- | --- | --- | --- |
| MT | 3959 BC | 1656 / 2303 BC | 2083 / 1876 BC |
| LXX | 5425 BC | 2242 / 3183 BC | 3549 / 1876 BC |
| SP | 4200 BC | 1307 / 2893 BC | 2324 / 1876 BC |

The gap between MT's and LXX's Flood dates is now 880 years, and it runs the other way: the
Septuagint puts the Flood *before* Egypt's First Dynasty (c. 3100 BC), where the Masoretic puts it
some eight centuries after.
That holds only for the Septuagint as printed. Without the second Cainan, which
[the Cainan question](#the-cainan-question) above treats as an insertion, its Flood falls at
3053 BC, level with Egypt's First Dynasty, and with the Göttingen Septuagint's 79 for Nahor at 2953 BC,
after it. [The Flood and the King Lists](../god/flood-and-the-king-lists.md) weighs the three texts.
"The biblical timeline" is not a single settled number even before archaeology enters the
picture. All three variants agree on Terah's death because they share the anchor and the chain
from Terah forward; they diverge only above him, which is the whole point.

## What this means for prophecy and Christ

### Two genealogies, two different jobs

None of the above is only an arithmetic exercise. Two genealogies of Jesus survive (Matthew 1:1-17,
Luke 3:23-38), and they're doing visibly different jobs. Matthew's is explicitly structured,
"fourteen generations" three times over (Matthew 1:17), and to hit that count it compresses the
king-list of Judah, skipping three known kings between Joram and Uzziah (compare Matthew 1:8 with 1
Chronicles 3:11-12). That's not sloppiness; ancient genealogies routinely telescoped names for a
structuring purpose without being understood as lying about lineage. It also means Matthew's list,
unlike Genesis 5 and 11, was never trying to support a year count at all — it's making a royal,
covenantal argument (this is David's heir), not a chronological one. Luke's list runs the other
direction, all the way back past Abraham to "the son of Adam, the son of God" (Luke 3:38). That
ending is the argument. Luke is setting up the same connection Paul makes explicitly. Jesus is the
second Adam, undoing in obedience what the first Adam did in disobedience (Romans 5:12-21; 1
Corinthians 15:22, 45). The genealogy exists, in Luke's hands, to make a theological claim stick to
a real, traceable human line. It works precisely because that line is real.

### The promise carried through named people

That is the frame the chronological work sits inside. The line from Adam to Christ is tracked
because of a promise, not because a date is owed. Genesis 3:15 said the woman's seed would come, and
would matter. That promise runs through actual named people, whose own names turn out, more often
than not, to be saying something true about what is coming. Seth, *appointed*, in place of a
murdered brother. Enoch, *dedicated*, taken without dying, a preview that death isn't the last word
for those who walk with God (Hebrews 11:5). Noah, *comfort*, the one who carries the appointed line
through judgment rather than being consumed by it. Methuselah's own name may or may not have
predicted the Flood by its own arithmetic. The pattern around him does, on a larger scale, what the
whole genealogy does. It is a real record of real people, shaped by a real author, tracking a
promise. Twenty-some centuries after its last recorded chapter, that promise is still being kept.

The shape of the claim is settled: a single traceable line, named generation by generation,
carrying a promise from Eden to an empty tomb. The math was always in service of that.

## Annex: dating choices and open work

### Two choices behind the numbers

Two figures behind these numbers are choices rather than manuscript readings, and both are now
stated in `docs/data/genealogy/index.json` with their scriptural basis rather than buried in
code. Shem's birth is taken from Genesis 11:10 ("two years after the flood," Shem then 100)
rather than from Genesis 5:32's summary that Noah fathered three sons after his 500th year; the
two differ by 2 years and that slack propagates to every date below Shem. And the Samaritan
variant alone reads Terah's 70 in Genesis 11:26 plainly, because its own 145-year total already
puts Terah's death in Abram's 75th year; the Masoretic and Septuagint variants take Abram's birth
at Terah 130.

### What stays open

The manuscript question is settled for this site's purposes (above); the state file behind this
study (`references/study-state/genealogy-times.yml`) records the decision. The Exodus anchor
was settled on 2026-10-01: 1446 BC, from 1 Kings 6:1's 480 years counted back from Solomon's
fourth year, which puts Masoretic creation at 3959 BC. Ussher's 1491 BC, and the 4004 BC epoch it
produces, were used until then; `docs/data/genealogy/index.json` keeps both as tracked alternates.

[The Day is Near](day-is-near.md) used dsscalendar.org's creation epoch (~3925 BC) until
2026-10-01; the site's year-6000 arithmetic now lives in [A Day Is a Thousand
Years](day-is-a-thousand-years.md#six-days-of-history), on this line.

The genealogical reasoning above was worked out without `prophecy-events-times.md`'s external
archaeological anchors (Qarqar, Sennacherib, the Babylonian and Persian records), so that
anchor-based dating could not bias which manuscript readings looked more probable. Now that the
genealogical case stands on its own, linking the
two — checking where the Masoretic numbers land relative to Thiele's Qarqar-anchored
chronology for the divided monarchy, for instance — is the natural next step, and is tracked as open
work in the state file.

The span from the Exodus to Solomon's temple, where the genealogies stop and 1 Kings 6:1's 480
years take over, is the subject of a separate study, *Four Hundred and Eighty Years*, in draft.

## References & Recommended Reading

- Primary texts (queried directly via `references/build/query.py` against
  `references/build/bible-text.db`): `morphhb-wlc` (Westminster Leningrad Codex, MT),
  `ebible-grcbrent` (Brenton Septuagint, LXX), `scrollmapper-SP` (Samaritan Pentateuch)
- TWOT root/Strong's/gloss data (`twot_strongs_map.json`), queried via
  `references/build/twot_lookup.py`, for every word study above
- ***NLT Life Application Study Bible*** (Tyndale) — the textual note at Genesis 11:32 recording
  the 145-year reading for Terah and cross-referencing 11:26 and 12:4
- ***ESV Study Bible*** (Crossway) and ***NIV Biblical Theology Study Bible*** (Zondervan), notes on
  Genesis 11:32 — both favour the Samaritan 145 for Terah
- Andrew E. Steinmann, "Challenging the Authenticity of Cainan, Son of Arpachshad," *JETS* 60/4
  (2017): 697–711, and "A Comparison of the Text of Genesis in Three Traditions: Masoretic Text,
  Samaritan Pentateuch, Septuagint," *JETS* 64/1 (2021): 25–43
- Helen R. Jacobus, on Cainan as original to the Hebrew, *Journal for the Study of the
  Pseudepigrapha* 18 (2009)
- James C. VanderKam, *Calendars in the Dead Sea Scrolls: Measuring Time* — on the broader
  Second Temple textual environment these traditions come from
- [The Zadok Calendar](../feasts/zadok-calendar.md), [The Day is Near](day-is-near.md), and
  [Prophecy Events and Times](prophecy-events-times.md) — this site's other chronology studies,
  including the still-open creation-epoch discrepancy noted above
- `docs/data/genealogy/index.json`, `antediluvian.json`, `patriarchal.json` — the structured
  source data this study explains
- `references/build/genealogy_chronology.py` — the validator/generator computing the table
  above from that source data
- `references/study-state/genealogy-times.yml` — the full research trail, including items
  deferred rather than resolved in this draft
