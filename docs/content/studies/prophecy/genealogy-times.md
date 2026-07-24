---
title: "Genealogy and Times: From Creation to Christ"
category: "prophecy"
description: "Tracing the covenant line from Adam to Christ through Genesis 5 and 11's genealogies, comparing the Masoretic Text, Septuagint, and Samaritan Pentateuch, closing the Exodus-to-Solomon gap with the priestly and Davidic genealogies, and asking what the names themselves are saying"
tags: ["studies", "genealogy", "chronology", "prophecy", "creation", "word-study", "textual-criticism"]
draft: false
primary_passage: "Genesis 5; Genesis 11:10-32"
bible_references: ["Genesis 3:15", "Genesis 5:1-32", "Genesis 11:10-32", "Genesis 12:4", "Numbers 1:7", "Joshua 14:7-10", "Judges 3-16", "1 Samuel 4:18", "1 Samuel 13:1", "2 Samuel 5:4-5", "1 Kings 6:1", "1 Chronicles 6:35-38", "Ezra 7:1-5", "Ruth 4:18-22", "Luke 3:23-38", "Matthew 1:1-17", "Acts 7:4", "Acts 13:19-21", "Romans 5:12-21", "1 Corinthians 15:22", "1 Corinthians 15:45"]
---

# Genealogy and Times: From Creation to Christ

Jesus's genealogy is recorded twice (Matthew 1, Luke 3), and Luke's runs all the way back to
Adam. That claim is only as strong as the data behind it, so this study does the work directly:
it reads Genesis 5 and 11:10-26 — the only two places in the Old Testament that give a
father's age at his heir's birth, not just a name — in all three surviving textual witnesses
(the Masoretic Text, the Septuagint, and the Samaritan Pentateuch), pulled straight from this
site's own primary-source database rather than from secondary comparison tables. The raw data
and the reasoning documented here feed
[docs/data/genealogy](https://github.com/ding0t/bible_studies/tree/main/docs/data/genealogy)'s
structured files; this page is where the *why* behind those numbers lives.

Two things are true at once, and this study tries to hold both without collapsing either into
the other: the genealogy is a real chronological record, precise enough to argue over and
capable of being wrong in transmission — and it is also a theologically shaped document,
tracking a single promised line (Genesis 3:15's "seed of the woman") through named individuals
whose names themselves carry meaning. Getting the math right and hearing what the names say are
not competing projects.

## How Genesis actually gives this data

Genesis 5 (Adam to Noah) and Genesis 11:10-26 (Shem to Terah) share a distinctive formula,
repeated once per patriarch: *he lived [age], and fathered [heir]; he lived [years] more after
fathering [heir], and had other sons and daughters; all his days were [total]*. That formula is
what makes three-way manuscript comparison possible at all — nowhere else in Scripture is this
much chronological data given about this many consecutive individuals. It also stops cold after
Terah: Genesis 11:26 gives his age, but from Abraham onward the text gives ages at specific
named events (Abraham 100 at Isaac's birth, Genesis 21:5; Isaac 60 at Jacob's, Genesis 25:26)
rather than a systematic per-generation formula. That's a real change in genre, not a gap in the
data — the rest of this study's method (comparing an "age at heir's birth" figure across
manuscripts) simply doesn't apply past Terah, because Genesis stops giving one.

## The three witnesses

- **The Masoretic Text (MT)** — the standard Hebrew text underlying most English translations,
  and the one this site's own `zadok_year` numbering already assumes (see
  [The Zadok Calendar](zadok-calendar.md) for the calendar side of that convention).
- **The Septuagint (LXX)**, in the Brenton edition — the pre-Christian Greek translation, whose
  Genesis 5 and 11 numbers diverge from MT's in a strikingly patterned way (below).
- **The Samaritan Pentateuch (SP)** — preserved independently by the Samaritan community, and
  the least commonly consulted of the three, but not the least interesting: it resolves two real
  problems that MT and LXX both leave open (see Methuselah and Terah below).

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

The pattern for six of these nine (Adam through Mahalalel, and Enoch) is remarkably clean: LXX
adds exactly 100 years to the age-at-heir-birth figure and subtracts the same 100 from
years-after, so the *total* lifespan is identical across MT, LXX, and SP every time. That's a
systematic shift, almost certainly deliberate on someone's part, not manuscript noise — noise
doesn't reproduce a constant offset nine times running with a matching total.

Jared, Methuselah, and Lamech break that pattern, each differently. Jared is untouched by the
LXX shift (MT and LXX agree exactly) but SP shortens both his age and his total. Methuselah gets
the standard MT/LXX same-total treatment (969 both) but SP shortens the *total*, not just the
split. Lamech is the strangest: all three traditions give a genuinely different total (777 / 753
/ 653) — no clean two-agree-one-differs pattern at all.

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

A different, equally consistent pattern shows up from Shelah through Serug: SP takes LXX's
higher age-at-heir-birth figure but keeps *MT's total*, by shortening years-after to compensate.
Four consecutive patriarchs do this identically — that's a real editorial signature, not
coincidence. Eber breaks it (SP just matches LXX outright, total included). Nahor breaks it a
third way (three genuinely different ages, though SP's total still matches MT's). And Terah —
the last one, and the most consequential — breaks it in the direction that matters most for
everything downstream.

## Case studies

### The Cainan question

[Luke 3:36 (ESV)](https://www.blueletterbible.org/esv/Luk/3/36) names a Cainan between Arphaxad
and Shelah. MT and SP don't have him; LXX does, with his own full entry (130 years to Shelah's
birth, 330 more after, 460 total — [Genesis 11:13 LXX](https://www.blueletterbible.org/esv/Gen/11/13)).
Luke is following LXX here, not MT. That's not a contradiction to explain away — it's evidence
Luke's genealogy is textually dependent on the Greek tradition at this specific point, which
matters for anyone using Luke's list to reconstruct an exact year count: if Cainan is a real
generation MT and SP dropped, any MT-based total from Adam to Christ is short by roughly this
generation's span; if he's a later Greek-tradition addition, LXX's own total (already the
longest of the three by a wide margin) inherits an extra generation MT/SP never had. Neither
option is resolved by more counting — it's a text-critical question, not a math one.

### Methuselah: the name, the number, and the Flood

Methuselah's name (מְתוּשֶׁלַח) is genuinely ambiguous at the lexical level — not "one attested
reading and one folk etymology," but two real readings built from real roots. Read as *m'tei*
("men of") + *shelach* ("javelin," H7973), it's a plain warrior name with no theological
freight. Read as *mut* ("die," H4191) + *shalach* ("send," H7971), it becomes a sentence-name:
"his death shall send [it]." Both parse correctly; nothing in the lexicon settles which one the
name-giver intended.

What tips the scales toward the second reading isn't etymology, it's arithmetic — and this is
exactly where the textual traditions disagree most sharply. MT and LXX both total Methuselah's
life at 969 years (the longest in the record), but via different splits. Run that 969 forward on
either tradition's own numbers for Lamech and Noah, and Methuselah is still alive more than a
decade *after* the Flood begins — a long-noted, real problem, not an invented one. If the name
really does mean "his death shall send [judgment]," a man who outlives the judgment his own name
predicted is an awkward result. SP alone avoids it: its total for Methuselah is 720, not 969 —
short enough that his death lands in the very year of the Flood. If the eschatological reading
of the name is right, SP is the one tradition where the name and the math actually agree without
further harmonizing.

### Terah and Abram: a puzzle two different ways

This is the most consequential single data point in the whole survey, because it's not a
disagreement about a name's meaning — it's an internal tension inside the text of Genesis
itself, and MT and SP resolve it in two structurally different ways.

Genesis 11:26 states Terah was 70 when he fathered Abram (named first, alongside Nahor and
Haran — birth order not stated). But Genesis 12:4 has Abram leaving Haran at 75, and
[Acts 7:4 (ESV)](https://www.blueletterbible.org/esv/Act/7/4) is explicit that this happened
*after* Terah's death. Under MT/LXX's stated 205-year total for Terah (born 1876 zadok on MT's
own numbers), the plain "70 at Abram" reading puts Abram's departure at zadok year 1946+75=2021
— a full 60 years *before* Terah actually dies at 2081. That's a real contradiction with Acts
7:4, not a rounding issue, and it's why the standard harmonization reinterprets Genesis 11:26:
Abram is listed first by covenant significance, not birth order, and was actually the youngest
of the three sons, born when Terah was 130 (1876+130=2006; +75=2081 — now it lines up exactly
with Terah's actual death year).

SP's total for Terah is 145, not 205. Run the *same plain 70-year reading* Genesis 11:26 states
outright — no reinterpretation, no assumption about birth order — and 70 + 75 = 145 exactly.
Terah's death and Abram's departure land on the same year without any harmonizing move at all.
Both resolutions work internally. MT/LXX's requires reading past the plain sense of one verse to
save the numbers; SP's numbers already match the plain sense of that same verse. That asymmetry
is worth sitting with rather than picking whichever number is more familiar.

## Word studies: what the names actually say

Popular teaching sometimes strings the Genesis 5 names into a sentence — Seth (appointed),
Enosh (mortal man), Kenan (sorrow), Mahalalel (the Blessed God), Jared (shall come down), Enoch
(teaching), Methuselah (his death shall bring), Lamech (the despairing), Noah (rest/comfort) —
read together as something like: *Man is appointed mortal sorrow, but the Blessed God shall come
down, teaching that his death shall bring the despairing rest.* It's a striking claim, and worth
checking against the lexicon rather than repeating on the strength of how well it reads.

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
| Lamech | **Unknown** | No TWOT root exists; standard lexicons mark the derivation genuinely uncertain |
| Noah | **Solid**, needs precision | Genesis 5:29's own wordplay uses *nacham* ("comfort"), not *nuach* ("rest") — a real double sound-play, not a simple derivation |

So: six of nine names hold up on their own lexical merits, one (Methuselah) is a real, motivated
ambiguity rather than a coin-flip, and two (Kenan, Lamech) have no lexical footing for the
reading the popular chain wants from them. That's worth saying plainly rather than smoothing
over. It doesn't wreck the pattern — six solid, theologically resonant names in a row
(appointed, [frail] man, praise of God, shall come down, dedicated, comfort) is still a real
feature of the text, not manufactured. But claiming a complete nine-word sentence requires
filling two genuine gaps with unattested glosses, and the temptation to do that — to round
"suggestive" up to "complete" — is itself worth naming as a temptation, not just quietly
resisting it.

## Toward a most probable timeline

Three real manuscript traditions and a fourth option — synthesizing rather than simply picking
one — are laid out in `docs/data/genealogy/index.json`'s `timeline_variants`. This study's
working position, `harmonized_v1`, takes MT as the base (matching this site's existing
`zadok_year` convention and `docs/data/events.json`) and adopts SP's reading in exactly two
places:

1. **Methuselah** — because SP is the only tradition where his death doesn't survive the Flood
   his own (possible) name predicts.
2. **Terah** — because SP's total resolves the Abram-departure puzzle without requiring Genesis
   11:26 to be read against its own stated birth-order.

Both substitutions share the same justification: they're adopted *because* they resolve a
demonstrable internal problem in the base reading, not merely because SP is available, older in
places, or shorter. That's a deliberate filter. SP has other divergences — the Shelah-through-
Serug redistribution pattern, the three-way split at Nahor — that this study does *not* adopt
into `harmonized_v1`, because nothing about those specific numbers resolves a contradiction the
way Methuselah and Terah's do. Adopting a reading only where it earns its keep, and leaving the
rest alone, is the whole point of naming this a *proposed synthesis* rather than just crowning
one manuscript the winner.

Computed results (`references/build/genealogy_chronology.py`, zadok year 0 = 4004 BC = Adam's
creation in every variant):

| Variant | Flood (zadok / Gregorian) | Terah's death (zadok / Gregorian) |
| --- | --- | --- |
| MT | 1656 / 2348 BC | 2081 / 1923 BC |
| LXX | 2242 / 1762 BC | 3547 / 457 BC |
| SP | 1307 / 2697 BC | 2322 / 1682 BC |
| **harmonized_v1** | **1536 / 2468 BC** | **1901 / 2103 BC** |

The gap between MT's and LXX's Flood dates alone is 586 years — a reminder that "the biblical
timeline" is not a single settled number even before archaeology enters the picture. This is
presented as the working answer, not the final one — the state file behind this study
(`references/study-state/genealogy-times.yml`) tracks it as `harmonized_v1`, open to revision if
a better-justified case for a different substitution turns up.

**One outstanding item, deliberately not smoothed over yet:** [The Day is
Near](day-is-near.md#when-is-the-year-6000) uses a different creation epoch again (~3925 BC)
than any of the four variants above. Reconciling that is future work, tracked but not resolved
here.

## The Exodus-to-Solomon gap: genealogy as a check on the Judges chronology

Genealogical age-data stops at Terah. From here to Solomon, the chronological evidence changes
character entirely: instead of a systematic formula, Scripture gives one summary figure
([1 Kings 6:1](https://www.blueletterbible.org/esv/1Ki/6/1): 480 years from the Exodus to
Solomon's 4th year) and a long list of individual judges' and oppressors' reign-lengths in
between. Those two kinds of evidence don't agree with each other on a naive reading, and two
different genealogies — one priestly, one royal — turn out to pull in opposite directions on
how to resolve it.

### The problem: the numbers don't add up to 480

Summing every individually-stated figure in Judges, in the order given:

| Event | Years | Verse |
| --- | --- | --- |
| Cushan-Rishathaim oppression | 8 | [Judges 3:8](https://www.blueletterbible.org/esv/Jdg/3/8) |
| Othniel / land's rest | 40 | [Judges 3:11](https://www.blueletterbible.org/esv/Jdg/3/11) |
| Eglon (Moab) oppression | 18 | [Judges 3:14](https://www.blueletterbible.org/esv/Jdg/3/14) |
| Ehud / land's rest | 80 | [Judges 3:30](https://www.blueletterbible.org/esv/Jdg/3/30) |
| Jabin (Canaan) oppression | 20 | [Judges 4:3](https://www.blueletterbible.org/esv/Jdg/4/3) |
| Deborah/Barak / land's rest | 40 | [Judges 5:31](https://www.blueletterbible.org/esv/Jdg/5/31) |
| Midian oppression | 7 | [Judges 6:1](https://www.blueletterbible.org/esv/Jdg/6/1) |
| Gideon / land's rest | 40 | [Judges 8:28](https://www.blueletterbible.org/esv/Jdg/8/28) |
| Abimelech | 3 | [Judges 9:22](https://www.blueletterbible.org/esv/Jdg/9/22) |
| Tola | 23 | [Judges 10:2](https://www.blueletterbible.org/esv/Jdg/10/2) |
| Jair | 22 | [Judges 10:3](https://www.blueletterbible.org/esv/Jdg/10/3) |
| Ammon oppression (east, Gilead) | 18 | [Judges 10:8](https://www.blueletterbible.org/esv/Jdg/10/8) |
| Jephthah | 6 | [Judges 12:7](https://www.blueletterbible.org/esv/Jdg/12/7) |
| Ibzan | 7 | [Judges 12:9](https://www.blueletterbible.org/esv/Jdg/12/9) |
| Elon | 10 | [Judges 12:11](https://www.blueletterbible.org/esv/Jdg/12/11) |
| Abdon | 8 | [Judges 12:14](https://www.blueletterbible.org/esv/Jdg/12/14) |
| Philistine oppression (west) | 40 | [Judges 13:1](https://www.blueletterbible.org/esv/Jdg/13/1) |
| Samson (during the Philistine oppression) | 20 | [Judges 15:20](https://www.blueletterbible.org/esv/Jdg/15/20); [16:31](https://www.blueletterbible.org/esv/Jdg/16/31) |

That's **410 years** for Judges proper. Add the wilderness wandering (40, fixed), roughly 7
years for Joshua's conquest (derived from [Joshua 14:7,
10](https://www.blueletterbible.org/esv/Jos/14/7): Caleb was 40 at the spies' mission, 85 "45
years" later, and 38 of those 45 were the imposed wilderness delay, leaving ~7 for the conquest
itself), Eli's 40 years judging Israel
([1 Samuel 4:18](https://www.blueletterbible.org/esv/1Sa/4/18)), an unspecified stretch of
Samuel's own ministry before the monarchy, Saul's reign, David's 40
([2 Samuel 5:4-5](https://www.blueletterbible.org/esv/2Sa/5/4)), and Solomon's 4 years to the
temple, and the sequential total comfortably exceeds 480 before Samuel's own years are even
counted — by at least 100 years, likely more. **This is a long-recognized problem, not a new
one**, and it has a name in the scholarly literature: the "Judges chronology problem."

Saul's own reign-length can't even be read off the Hebrew text as it stands: [1 Samuel
13:1](https://www.blueletterbible.org/esv/1Sa/13/1) reads, transliterated, "Saul was a son of a
year when he began to reign, and two years he reigned over Israel" — a well-known textual
lacuna, not a translation choice. A number has dropped out of the Masoretic transmission at
Saul's age, and "two years" for his whole reign is implausibly short given everything the text
elsewhere attributes to it. The traditional 40-year figure comes not from Samuel but from
[Acts 13:21 (ESV)](https://www.blueletterbible.org/esv/Act/13/21), where Paul states it plainly:
God "gave them Saul... for forty years." Worth knowing when that number is used: it's patching a
real gap in the Hebrew manuscript tradition, not resolving an ambiguity within it.

### The textual basis for overlap — this isn't invented

The standard resolution treats several of these judgeships as **regional rather than national**,
and therefore overlapping in time rather than strictly sequential. That's not a modern
harmonizer's convenience — the text says so directly. [Judges 10:7-9
(ESV)](https://www.blueletterbible.org/esv/Jdg/10/7) states that God "sold them into the hand of
the Philistines and into the hand of the Ammonites" **in the same breath**, with the Ammonite
oppression explicitly located "beyond the Jordan... in Gilead" (east) for 18 years, while
Philistine pressure came from the west. Jephthah, Ibzan, Elon, and Abdon's combined 31 years
belong to the eastern/Gilead side of that same double-oppression; Samson's 20 years explicitly
take place "in the days of the Philistines" ([Judges 15:20](https://www.blueletterbible.org/esv/Jdg/15/20))
— he judges *during* the 40-year Philistine oppression, not after ending it, and 1 Samuel's own
narrative shows Philistine dominance continuing well past Samson's death, through Eli's era and
into Samuel's early ministry. None of this requires inventing an overlap the text doesn't
support; it requires taking the text's own geography seriously instead of defaulting to a single
linear national timeline the book of Judges never actually claims to be giving.

### Genealogy check #1: the priestly line — broadly consistent with ~480 years

The high priestly line from Aaron to Zadok (David and Solomon's priest) is given twice,
independently: [1 Chronicles 6:35-38](https://www.blueletterbible.org/esv/1Ch/6/35) and
[Ezra 7:1-5](https://www.blueletterbible.org/esv/Ezr/7/1) (tracing Ezra's own ancestry back to
Aaron), and the two lists agree exactly: Aaron → Eleazar → Phinehas → Abishua → Bukki → Uzzi →
Zerahiah → Meraioth → Amariah → Ahitub → Zadok. That's **10 generational steps** from Aaron
(who dies in the wilderness, so effectively at the Exodus end-point) to Zadok (serving at the
very end of David's reign and the start of Solomon's). Over roughly 400-480 years, that's
40-48 years per generation — on the high side for a strict father-to-son succession, but not
implausible for a priestly office where a man might not become high priest, or father his own
heir, particularly young. This genealogy doesn't *prove* 480 years, but it doesn't strain against
it either.

### Genealogy check #2: the Davidic line — in real tension with 480 years

[Ruth 4:18-22](https://www.blueletterbible.org/esv/Rut/4/18) gives David's own ancestry from
Judah's son Perez: Perez → Hezron → Ram → Amminadab → **Nahshon** → Salmon → Boaz → Obed →
Jesse → David. Nahshon isn't a random name — [Numbers 1:7
(ESV)](https://www.blueletterbible.org/esv/Num/1/7) names him as the tribal leader of Judah
during the wilderness census, firmly placing him in the Exodus generation. From Nahshon to
David is only **5 generational gaps** (Nahshon-Salmon-Boaz-Obed-Jesse-David). Spread across the
same 400-480 year span the priestly line tolerates, that's 80-96 years per generation —
not plausible for ordinary human fathering, by a wide margin.

This doesn't mean Ruth's genealogy is wrong; it means it's very likely **telescoped** — skipping
generations the way ancient genealogies regularly do (this site's own Matthew 1:17 discussion
above is a directly comparable case: three known kings dropped to hit a structuring number).
Telescoping in an official succession line, especially one this short, is a well-attested
biblical pattern, not a special plea invented to save this one case.

### Where this leaves the reconstruction

Two genealogical checks, pointing in different directions, is the honest state of the evidence
— not a failure of the method. The priestly line is compatible with something close to 1 Kings
6:1's 480 years; the royal line, taken at face value, is not, and all but requires accepting that
Ruth's list omits names. Put together with the judges-overlap evidence above, the most defensible
reading is: **1 Kings 6:1's 480 years is plausible as a real total**, achieved by real regional
overlap among the judges (textually supported, not invented) rather than strict national
sequence, while Ruth's five-generation genealogy for David almost certainly telescopes rather
than recording every link — the same kind of compression this study already had to reckon with
in Matthew's genealogy, just applied one book earlier. Nothing here fixes an exact year-by-year
allocation of which judge overlaps which by how much; that level of precision isn't recoverable
from what the text actually states, and claiming otherwise would overshoot the evidence in the
same way summing the numbers naively does.

## What this means for prophecy and Christ

None of the above is only an arithmetic exercise. Two genealogies of Jesus survive
(Matthew 1:1-17, Luke 3:23-38), and they're doing visibly different jobs. Matthew's is
explicitly structured — "fourteen generations" three times over (Matthew 1:17) — and to hit that
count it compresses the king-list of Judah, skipping three known kings between Joram and
Uzziah (compare Matthew 1:8 with 1 Chronicles 3:11-12). That's not sloppiness; ancient
genealogies routinely telescoped names for a structuring purpose without being understood as
lying about lineage. It also means Matthew's list, unlike Genesis 5 and 11, was never trying to
support a year count at all — it's making a royal, covenantal argument (this is David's heir),
not a chronological one. Luke's list runs the other direction, all the way back past Abraham to
"the son of Adam, the son of God" (Luke 3:38) — and that ending is the argument. Luke is setting
up the same connection Paul makes explicitly: Jesus as the second Adam, undoing in obedience
what the first Adam did in disobedience (Romans 5:12-21; 1 Corinthians 15:22, 45). The genealogy
exists, in Luke's hands, to make a theological claim stick to a real, traceable human line — not
in spite of it being real, but because it is.

That's the frame this study's chronological work sits inside. The line from Adam to Christ isn't
being tracked because a date is owed; it's being tracked because Genesis 3:15's promise — that
the woman's seed would come, and would matter — runs through actual named people whose own names
turn out, more often than not, to be saying something true about what's coming. Seth,
*appointed*, in place of a murdered brother. Enoch, *dedicated*, taken without dying, a preview
that death isn't the last word for those who walk with God (Hebrews 11:5). Noah, *comfort*, the
one who carries the appointed line through judgment rather than being consumed by it. Whether or
not Methuselah's own name predicted the Flood by its own arithmetic, the pattern around him
does the same thing on a larger scale that the whole genealogy does: a real record of real
people, shaped by a real author, tracking a promise that is still, twenty-some centuries after
its last recorded chapter, being kept.

The specific date question — whether creation was 6540, 5960, or 5308 years before Christ on
this study's three witnesses, or something closer to the 5940-year figure `harmonized_v1`
implies — stays open, and honestly reported as open above. What doesn't stay open is the shape
of the claim: a single traceable line, named generation by generation, carrying a promise from
Eden to an empty tomb. The math was always in service of that; it was never the point on its
own.

## Israel and the Church, and the anchors this study deliberately deferred

This study intentionally did not pull in `prophecy-events-times.md`'s external archaeological
anchors (Qarqar, Sennacherib, the Babylonian and Persian records) while working out the
genealogical reasoning above, so that anchor-based dating wouldn't quietly bias which manuscript
readings looked more "probable." Now that the genealogical case stands on its own, linking the
two — checking where `harmonized_v1`'s numbers land relative to Thiele's Qarqar-anchored
chronology for the divided monarchy, for instance — is the natural next step, tracked as open
work in this study's state file rather than done here.

## References & Recommended Reading

- Primary texts (queried directly via `references/build/query.py` against
  `references/build/bible-text.db`): `morphhb-wlc` (Westminster Leningrad Codex, MT),
  `ebible-grcbrent` (Brenton Septuagint, LXX), `scrollmapper-SP` (Samaritan Pentateuch)
- TWOT root/Strong's/gloss data (`twot_strongs_map.json`), queried via
  `references/build/twot_lookup.py`, for every word study above
- James C. VanderKam, *Calendars in the Dead Sea Scrolls: Measuring Time* — on the broader
  Second Temple textual environment these traditions come from
- [The Zadok Calendar](zadok-calendar.md), [The Day is Near](day-is-near.md), and
  [Prophecy Events and Times](prophecy-events-times.md) — this site's other chronology studies,
  including the still-open creation-epoch discrepancy noted above
- `docs/data/genealogy/index.json`, `antediluvian.json`, `patriarchal.json` — the structured
  source data this study explains
- `references/build/genealogy_chronology.py` — the validator/generator computing the table
  above from that source data
- `references/study-state/genealogy-times.yml` — the full research trail, including items
  deferred rather than resolved in this draft
