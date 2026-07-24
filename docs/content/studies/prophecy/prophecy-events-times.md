---
title: "Prophecy Events and Times"
category: "prophecy"
description: "How prophetic time is measured -- the 360-day prophetic year and the day-year principle -- and how the ancient Hebrew calendar and Ussher's chronology line up major biblical events"
tags: ["studies", "end-times", "prophecy", "timeline", "calendar", "chronology", "eschatology"]
draft: false
bible_references: ["Genesis 7:11", "Genesis 8:3-4", "Daniel 9:24-27", "Ezekiel 4:6", "Revelation 11:2-3", "Revelation 12:6", "Revelation 13:5"]
---

# Prophecy, calendar, and the times of fulfilled events

[The Day is Near](day-is-near.md) makes the theological case that "a day is as a thousand years"
([2 Peter 3:8](https://www.blueletterbible.org/esv/2Pe/3/8)) and lands on roughly 6000 years of
ordinary history before a seventh, sabbath-rest millennium. This study is the working-out of that
construct: what calendar the Bible's own prophecies actually run on, how that calendar compares to
the ancient Hebrew calendar in wider use, and where major biblical events fall once you try to date
them against it.

## Interpreting Bible prophecy

1. **Bible prophecy uses a 360-day year.** The Flood lasted "five months"
   ([Genesis 7:11](https://www.blueletterbible.org/esv/Gen/7/11);
   [Genesis 8:3-4](https://www.blueletterbible.org/esv/Gen/8/3-4)) and
   that same span is elsewhere counted as 150 days — five 30-day months. Revelation counts the same
   period three different ways and gets the same number every time: 42 months
   ([Revelation 11:2](https://www.blueletterbible.org/esv/Rev/11/2)), "time, and times, and half a
   time" i.e. 3.5 years ([Revelation 12:14](https://www.blueletterbible.org/esv/Rev/12/14)), and
   1,260 days ([Revelation 11:3](https://www.blueletterbible.org/esv/Rev/11/3);
   [Revelation 12:6](https://www.blueletterbible.org/esv/Rev/12/6)) — which only reconciles if a
   prophetic year is a fixed 360 days (12 x 30), not the 365.25-day solar year.
2. **Watch for a day standing in for a year.** Daniel's seventy weeks (
   [Daniel 9:24-27](https://www.blueletterbible.org/esv/Dan/9/24-27)) are weeks of years, not
   days — the same day-for-a-year principle God states explicitly to Ezekiel
   ([Ezekiel 4:6](https://www.blueletterbible.org/esv/Eze/4/6)).

## On calendars

Two calendars are worth comparing when dating biblical events:

- **The Zadok/Essene calendar** — a 364-day solar calendar (12 x 30 days plus 4 Tekufah days),
  already covered in depth in [The Zadok Calendar](zadok-calendar.md). This is the calendar behind
  this site's own `zadok_year` dating.
- **The standard rabbinic (lunisolar) calendar** — the one most Jewish and Christian sources mean by
  "the Hebrew calendar" today. Per [Hebrew4Christians' calendar
  overview](https://www.hebrew4christians.com/Holidays/Calendar/calendar.html): it runs on two
  year-starts at once — a **religious year beginning in Nisan** (spring, tied to the Exodus) and a
  **civil year beginning in Tishri** (fall) — with months measured by the ~29.5-day lunar cycle.
  A new month (**Rosh Chodesh**, "head of the month") is marked liturgically at each new moon; see
  that site's own [Rosh Chodesh](https://www.hebrew4christians.com/Holidays/Rosh_Chodesh/rosh_chodesh.html)
  and [Rosh Chodashim](https://www.hebrew4christians.com/Holidays/Spring_Holidays/Rosh_Chodashim/rosh_chodashim.html)
  pages for more on the new-moon reckoning and the Nisan-1 "biblical new year" question specifically.
  To resync the 354-day lunar year with the 365-day solar year, a leap month (**Adar II**) is
  inserted seven times in every 19-year cycle. The individual feast pages linked from that same
  overview (Passover, Shavu'ot, Sukkot, and so on) duplicate what's already covered in
  [Feasts](../feasts/feasts.md), so aren't re-linked here.

The lunisolar calendar's drifting month lengths are exactly why the Zadok calendar's defenders
prefer it for prophetic arithmetic (see zadok-calendar.md's "Why I use it") — a fixed 360/364-day
scheme gives clean, repeatable math; a lunisolar one needs a leap-month correction folded in first.

## Aligning major events to a timeline

The dates below follow **James Ussher's 17th-century chronology** ([*Annals of the World*,
1650s](https://en.wikipedia.org/wiki/Ussher_chronology)) — the same one already anchoring
`docs/data/events.json` behind this site's [Prophetic Timeline](../../../timeline/) tool, which
places Creation at 4004 BC (`zadok_year` 0). Using that same zero-point (`zadok_year` =
`gregorian_year` + 4004), Ussher's other anchor dates line up as follows:

| Event | Gregorian Date | Zadok Year | Bible Reference | Basis |
| --- | --- | --- | --- | --- |
| Creation | 4004 BC | 0 | [Genesis 1](https://www.blueletterbible.org/esv/Gen/1/1) | Ussher's chronology; this site's `events.json` zero-point |
| The Flood | 2349 BC | 1655 | [Genesis 7:11](https://www.blueletterbible.org/esv/Gen/7/11) (Noah's 600th year) | Ussher's chronology |
| The Exodus | 1491 BC | 2513 | [Exodus 12:40-41](https://www.blueletterbible.org/esv/Exo/12/40-41) | Ussher's chronology |
| Solomon's Temple founded | 1012 BC | 2992 | [1 Kings 6:1, 37](https://www.blueletterbible.org/esv/1Ki/6/1) (4th year of Solomon, 480 years after the Exodus) | Ussher's chronology |
| Birth of Jesus | c. 5 BC | c. 3999 | [Matthew 2:1](https://www.blueletterbible.org/esv/Mat/2/1); [Luke 2](https://www.blueletterbible.org/esv/Luk/2/1) | Ussher's chronology (he placed the nativity before Herod's death, which Josephus dates to 4 BC) |
| Crucifixion | AD 32 | 4036 | See [The Day is Near](day-is-near.md) | This site's own dating; matches `events.json`'s entries for c. AD 32-33 |
| Restoration of Israel | 14 May 1948 | c. 5952 | — | Israel's Declaration of Independence |

**Caution on the "Zadok Year" column:** these are Ussher's Gregorian/BC-AD dates run through a
simple `+4004` conversion for illustration, not an independently sourced Zadok-calendar date for
each event — nothing in this repo currently derives a Zadok-calendar date for the Flood, Exodus, or
Nativity from first principles. Ussher's own chronology is also one reconstruction among several;
it isn't the scholarly consensus (the more common "early date" Exodus in evangelical scholarship, for
example, is usually placed nearer 1446 BC using Thiele's chronology for the divided monarchy rather
than Ussher's own 1012 BC anchor for Solomon's 4th year — a real, unresolved disagreement between
two internally-consistent systems, not a rounding error).

**Open item:** [The Day is Near](day-is-near.md#when-is-the-year-6000)'s own timeline chart implies
a *different* creation epoch (roughly 3925 BC, for its "AD 75 = year 4000" and "AD 2075 = year
6000" markers to work) than the 4004 BC used here and in `events.json`. That ~79-year gap between
the two hasn't been reconciled yet — worth resolving before leaning further weight on either page's
numbers.

## Israel and the Church

The identity of Israel and the Church is a related but separate theological question from anything
above — see [Israel and the Church](../theology/israel-and-the-church.md) for that discussion.

## References

- Ussher chronology overview: [Wikipedia](https://en.wikipedia.org/wiki/Ussher_chronology)
- [Hebrew4Christians: The Hebrew Calendar](https://www.hebrew4christians.com/Holidays/Calendar/calendar.html)
