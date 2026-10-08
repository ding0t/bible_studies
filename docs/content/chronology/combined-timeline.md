---
title: "The Combined Timeline: One Line, Two Zones"
category: "prophecy"
description: "Creation to the present on a single line, showing where the biblical timeline is rigid and where it stretches — the manuscript variants diverge by 1,646 years at creation and converge on Abraham to the year."
tags: ["genealogy", "creation", "method/textual-criticism", "status/investigation"]
draft: false
primary_passage: "Genesis 11:10-32"
bible_references: ["Genesis 5:1-32", "Genesis 7:11", "Genesis 11:10-32", "Genesis 12:4", "Exodus 12:40-41", "1 Kings 6:1", "Acts 7:4", "Galatians 3:17"]
date_created: 2026-08-22
date_modified: 2026-10-08
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-opus-5.5
---

# The Combined Timeline: One Line, Two Zones

**The four manuscript traditions disagree about creation by 1,646 years and agree about Abraham to the year.** That single fact is the shape of biblical chronology. Everything above Abraham stretches; everything below him is fixed.

Two other pages hold the detail. [Genealogy and Times](genealogy-times.md) works through the manuscript evidence for the stretch above Abraham. [Chronology Anchors](chronology-anchors.md) lists the forty-one datable events below him. This page puts them on one line.

## Key Takeaways

*(This section follows the [Key Takeaways](../about/key-takeaways.md) format — see that page for what each part is for.)*

### Lessons about Jesus

The timeline converges twice, and both convergences point the same way. Every manuscript tradition, however far apart it places creation, agrees on when Abraham was born — because all of them are measured back from the Exodus, and the Exodus is measured back from a temple whose builder is dated by an eclipse. Then the whole rail runs forward to a Friday in AD 33 that two independent chains reach on their own: Daniel's seventy weeks counted in prophetic years from a Persian decree, and Luke's note of the fifteenth year of a Roman emperor. A promise made to one childless man in Ur and a prophecy given in Babylon both terminate in the same week.

### Prayer

Father, you did not give us a timeline; you gave us a genealogy, a set of intervals and a Son who came in the fullness of time. Thank you that the parts we can count check out, and that the parts we cannot are still yours. Keep me from mistaking a number I have worked out for a certainty you have promised, and let the study of when you acted deepen my trust that you did. Amen.

## Why the timeline has two zones

Every dated event in Scripture ultimately hangs on one extra-biblical peg: a solar eclipse recorded by Assyrian scribes on 15 June 763 BC, which converts their eponym list from a relative sequence into an absolute one. From there, synchronisms fix Solomon's fourth year, 1 Kings 6:1's 480 years fix the Exodus, and Scripture's own intervals — Abram 75 at the call (Genesis 12:4), the 430 years of Galatians 3:17, Terah's age at Abram's birth from Acts 7:4 — carry the count back to Terah.

Above Terah the method changes completely. Genesis 5 and 11 give a father's age at his heir's birth for nineteen consecutive generations, ten from Adam to Noah and nine from Shem to Terah, and nowhere else does Scripture supply that. But those are exactly the figures the manuscript traditions disagree about, so the count above Abraham is only as firm as the text you read it from.

```mermaid
flowchart LR
    subgraph E["ELASTIC — the count varies by manuscript"]
        direction TB
        A["Creation<br/>3959-5425 BC<br/>depending on the tradition"] --> B["The Flood"] --> C["Babel"]
    end
    subgraph R["RIGID — the dates are fixed by anchors"]
        direction TB
        D["Abraham<br/>1951 BC<br/>all traditions agree"] --> F["Exodus"] --> G["Solomon's temple"] --> H["Exile and return"] --> I["Christ"]
    end
    E --> R
    J["763 BC eclipse<br/>Assyrian eponym list"] -.->|"anchors everything<br/>by working backward"| R
```

## The spine

The order of events is certain even where their dates are not. No manuscript tradition disputes any of this sequence.

The spine — order first, dates second.

```mermaid
flowchart TD
    subgraph elastic["Elastic — the order is firm, the dates are not"]
      direction TB
      A["Creation<br/>Adam and Eve"] --> B["The Flood<br/>eight survive, six of childbearing age"]
      B --> C["Babel<br/>the seventy clans scatter"]
    end
    subgraph hinge["The hinge"]
      direction TB
      D["Abraham<br/>every tradition agrees on 1951 BC"]
    end
    subgraph rigid["Rigid — anchored to datable events"]
      direction TB
      E["Exodus<br/>Israel leaves Egypt"] --> F["Solomon<br/>the first temple begun"]
      F --> G["Exile<br/>Jerusalem falls, then the return"]
      G --> H["Antiochus<br/>the temple desecrated and rededicated"]
      H --> I["Christ<br/>crucified and raised"]
    end
    subgraph since["Since"]
      direction TB
      J["The church age<br/>running now"]
    end
    elastic --> hinge
    hinge --> rigid
    rigid --> since
```

## The elastic zone: creation to Abraham

Anno Mundi year and Gregorian date both move here, and they move together. Figures are from this repo's own generator under the active epoch scenario, `a_prime` (the Exodus at 1446 BC).

| Event | Masoretic (the site's working chronology) | Septuagint | Samaritan |
|---|---|---|---|
| Creation | AM 0 · 3959 BC | AM 0 · 5425 BC | AM 0 · 4200 BC |
| Enoch born | AM 622 · 3337 BC | AM 1122 · 4303 BC | AM 522 · 3678 BC |
| Noah born | AM 1056 · 2903 BC | AM 1642 · 3783 BC | AM 707 · 3493 BC |
| The Flood (Genesis 7:11) | AM 1656 · 2303 BC | AM 2242 · 3183 BC | AM 1307 · 2893 BC |
| Peleg born | AM 1757 · 2202 BC | AM 2773 · 2652 BC | AM 1708 · 2492 BC |
| Terah born | AM 1878 · 2081 BC | AM 3344 · 2081 BC | AM 2179 · 2021 BC |
| **Abram born** | **AM 2008 · 1951 BC** | **AM 3474 · 1951 BC** | **AM 2249 · 1951 BC** |

The site follows the Masoretic numbers. The reasons, and the confidence each carries, are set out
in [The Flood and the King Lists](flood-and-the-king-lists.md#why-this-site-follows-the-masoretic-numbers).
Until 2026-09-28 a fourth path, `harmonized_v1`, took the Samaritan age for Terah; it has been
retired.

The stretch itself is what varies. Measured in years from creation to Abraham's birth:

```mermaid
xychart-beta
    title "Length of the elastic zone — creation to Abraham, in years"
    x-axis ["Masoretic", "Samaritan", "Septuagint"]
    y-axis "years" 0 --> 3600
    bar [2008, 2249, 3474]
```

The Septuagint's chain is half as long again as the Samaritan's, and about three-quarters longer than the Masoretic's. Which of them preserves the older figures is a text-critical question, not an arithmetical one, and [Genealogy and Times](genealogy-times.md) works through the evidence — including the finding that the Samaritan Pentateuch sides with the Masoretic Text six times to nil in Genesis 5 and with the Septuagint six times to nil in Genesis 11, which is why the two chapters cannot be decided as one block.

## The hinge: why they all agree about Abraham

Every tradition puts Abram's birth at 1951 BC, to the year. That is not a coincidence and it is not evidence that the traditions agree — it is the anchoring working as designed. The chain from Abraham forward to the Exodus uses figures all three manuscript traditions share: Abram 75 at the call (Genesis 12:4), 430 years from the call to the Exodus (Galatians 3:17), and Terah's age at Abram's birth derived from Acts 7:4. So fixing the Exodus fixes Abraham, and every variant inherits that date whatever it does above him. One link is contested: the Septuagint and Samaritan texts of Exodus 12:40 count the 430 years across Canaan and Egypt, as this line does, while the Hebrew can be read as 430 years in Egypt alone. That long reading would put Abram's birth 215 years earlier, in 2166 BC; [Why Not 4004 BC?](why-not-4004-bc.md#how-long-was-israel-in-egypt) weighs the two.

Terah is the last person for whom Genesis supplies an age at his heir's birth, so he is where the two methods meet. The Masoretic and Septuagint also converge on his birth year. The Samaritan puts it 60 years later because it reads Genesis 11:26's seventy plainly, which its own 145-year Terah allows.

## The rigid zone: Abraham to now

Below the hinge the Gregorian dates stop moving. The manuscript question has no purchase here, because these dates come from contemporary documents and astronomy rather than from genealogy. The Anno Mundi figures follow from the Exodus: 1 Kings 6:1's 480 years counted back from Solomon's fourth year put it at 1446 BC, which is AM 2513 on the Masoretic chain.

| Event | Date | AM |
|---|---|---|
| Exodus | 1446 BC | 2513 |
| Solomon's temple begun | 966 BC | 2993 |
| Jerusalem falls | 586 BC | 3373 |
| Cyrus's decree | 538 BC | 3421 |
| Second temple completed | 515 BC | 3444 |
| Temple rededicated | 164 BC | 3795 |
| Crucifixion and Resurrection | AD 33 | 3991 |
| Today | AD 2026 | 5984 |

Until 2026-10-01 the site used Ussher's 1491 BC Exodus and creation at 4004 BC, which put every AM figure above 45 years higher. Ussher reached that Exodus from a temple date of 1012 BC, which he got by adding the kings' reigns end to end. The Assyrian synchronisms fix the temple at 966 BC, so the site moved to the 1446 BC Exodus. [Why Not 4004 BC?](why-not-4004-bc.md) traces where Ussher's forty-six years came from.

Forty-one events with their evidence, tiers and error bars are in [Chronology Anchors](chronology-anchors.md). Thirty-one of them carry an error bar of a year or less.

## What is settled and what is open

**Settled.** The order of events, throughout. The Gregorian dates below Abraham, to within a year for most of them. The crucifixion at Friday 3 April AD 33. The sabbatical cycle, anchored on three attested sabbatical years whose intervals are exact multiples of seven. The epoch, since 2026-10-01: the Masoretic chain on the 1446 BC Exodus (`a_prime`), with the three alternates recorded in `docs/data/genealogy/index.json` and set out in [The Zadok Calendar](../feasts/zadok-calendar.md#where-year-0-sits).

**Open, and tracked rather than guessed.** Which manuscript tradition preserves the older figures in Genesis 5 and 11 — the evidence splits by chapter.

The manuscript question and the epoch are independent. Nothing about choosing a manuscript tradition settles the epoch, and nothing about the epoch touches the manuscript evidence.

## Discussion questions

1. The traditions disagree about creation by more than sixteen centuries and agree about Abraham to the year. Does that make you more or less confident in the parts of the chronology that can be checked?
2. Genesis gives a father's age at his heir's birth for nineteen generations and then stops at Terah. Why might the text supply that much detail for the early period and none afterward?
3. Everything datable in Scripture ultimately hangs on an eclipse recorded by scribes who had no interest in the Bible. What do you make of God's providence running through a record like that?
4. The order of events is certain throughout while the dates are not. Which of the two does the biblical narrative actually depend on?

## References & Recommended Reading

- [Genealogy and Times](genealogy-times.md) — the manuscript evidence for the elastic zone, and the three timeline variants.
- [Chronology Anchors](chronology-anchors.md) — the forty-one datable events below Abraham, with tiers and error bars.
- [The Zadok Calendar](../feasts/zadok-calendar.md) — the calendar these Anno Mundi years are counted in, and the four epoch scenarios.
- [A Day Is a Thousand Years](../last-things/day-is-a-thousand-years.md) — the millennial-week reading, and why the epoch question bears on it.
- `docs/data/genealogy/` — the source data. Per-tradition textual facts in `antediluvian.json` and `patriarchal.json`, anchoring decisions in `index.json`, and derived years in `generated/`, all produced by `references/build/genealogy_chronology.py`.
- **ESV Bible** (Crossway) — all scripture verified against `study-notes.db`.
