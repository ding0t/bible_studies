---
title: "Our Taxonomy"
category: "other"
description: "How studies on this site are organised: the systematic-theology loci it's based on, the plain-English name used for each section, and the academic term behind it."
tags: ["taxonomy", "site-structure", "study-method"]
draft: false
---

# Our taxonomy

Studies here are filed by **subject**, using the standard divisions of systematic theology — the
same skeleton seminaries and theological libraries have used for centuries — with plain-English
names instead of the academic ones.

This page explains what each section holds, and gives the technical term behind each name so that
anyone coming from a formal theology background can see the mapping immediately.

!!! note "Status"

    This is the live structure as of August 2026. Everything previously under `studies/` and
    `bible/` was moved here, and the old URLs still resolve — every pre-migration address
    redirects to its new home, so old links and bookmarks keep working.

---

## What it's based on

Three sources, in descending order of how much weight they carry here.

**The systematic-theology *loci*.** The traditional division of Christian doctrine into topics —
Bibliology, Theology Proper, Christology, Hamartiology, Soteriology, Eschatology, and the rest. This
is the skeleton. It has the advantage of being genuinely comprehensive: it was built to cover the
whole of Christian doctrine, not to describe a particular collection of essays, so it has a slot
ready for subjects this site has not written about yet.

**The Dewey Decimal 200s.** A published, concrete encoding of those same loci, used as the tiebreaker
when a study could plausibly sit in two places. Dewey has already adjudicated most of the awkward
cases — that angels and demons are their own subject (235) rather than a subheading of theology
proper, that inter-testamental and apocryphal literature has its own slot (229) rather than being
split between "Bible" and "history", that religious calendars and appointed times belong together
(263). The numbers appear in the table below for reference. They are not used in URLs or filenames.

**Dispensational theology.** Per this site's [statement of faith](statement-of-faith.md), studies
here read Scripture dispensationally, and that changes one thing about the standard scheme: the
distinction between Israel and the Church is a major subject in its own right rather than a
footnote inside ecclesiology. It gets its own section below. The reference works behind this are
Lewis Sperry Chafer's *Systematic Theology* and Charles Ryrie's *Basic Theology*.

---

## The sections

| Our term | Academic term | Dewey | What belongs here |
|---|---|---|---|
| **Scripture** | Bibliology | 220, 229 | The Bible about itself: canon, manuscripts and textual criticism, translation, how to read it, biblical archaeology, extra-biblical and inter-testamental texts, apocrypha and pseudepigrapha |
| **God** | Theology Proper | 231 | God's nature and character, the Trinity, the Holy Spirit, creation, and how God reveals himself — including dreams, visions, and general revelation |
| **Jesus** | Christology | 232 | Who Christ is and what he did: incarnation, ministry, passion, resurrection, his offices as prophet, priest and king, and Old Testament prophecy fulfilled in him |
| **Sin** | Hamartiology | 233, 241.3 | The nature of sin and its particular forms — idolatry, sexual immorality, sorcery — and what Scripture says about temptation and repentance |
| **Salvation** | Soteriology | 234 | Grace, redemption, justification, assurance of salvation, and what happens at death |
| **Spiritual beings** | Angelology & Demonology | 235 | Angels, demons, Satan, the Nephilim, deliverance, and discernment of spirits |
| **Last things** | Eschatology | 236 | The rapture, the tribulation, the millennium, judgment, and the ordering of end-times events |
| **Israel and the Church** | Ecclesiology *(+ the dispensational distinction)* | 262 | The covenants, the relationship and distinction between Israel and the Church, and the Hebrew roots of Christian faith and practice |
| **Christian life** | Practical theology | 248 | Prayer, fasting, and the disciplines of walking with Christ |
| **Feasts** | *Appointed times* | 263 | The biblical feasts and calendars: their Old Testament instruction, their observance, and their fulfilment |
| **Biblical figures** | *(Biography)* | — | Studies of particular people in Scripture — the twelve disciples, the patriarchs, the prophets, the kings |
| **Sermons** | Homiletics | 251, 252 | Sermon notes, teaching material, and guidance on preparing to teach |
| **Resources** | — | — | Guides to external material: source catalogues, language-learning aids, and reference tools |

The last two sit alongside the studies rather than inside them, because they describe *how* material
is delivered or *where* it comes from rather than what subject it treats.

### These sections are top-level

Each section is a directory at the root of the site — `/jesus/`, `/last-things/`, `/sin/` — not
nested under a `studies/` wrapper. A container holding nearly every page on the site conveys nearly
nothing, and the extra path segment appears in every URL forever.

```
about/              biblical-figures/   christian-life/
commentaries/       feasts/             god/
israel-and-church/  jesus/              last-things/
resources/          salvation/          scripture/
sermons/            sin/                spiritual-beings/
```

Fifteen top-level entries sounds like a lot, but `navigation.prune` is enabled in `mkdocs.yml`, so
the sidebar only ever renders the branch you are actually in.

### Navigation order is deliberate

Left alone, `awesome-pages` sorts alphabetically, which would open the site on *biblical figures*
and scatter the doctrinal sequence. The loci have a teaching order — how we know (Scripture), who God
is, who Christ is, what is wrong, how it is fixed, how it ends — and a root `.pages` file preserves
it:

```yaml
nav:
  - index.md
  - scripture
  - god
  - jesus
  - spiritual-beings
  - sin
  - salvation
  - israel-and-church
  - last-things
  - feasts
  - christian-life
  - biblical-figures
  - commentaries
  - sermons
  - resources
  - about
```

### Reserved, not yet created

**Humanity** (Anthropology, Dewey 233) — the image of God, the constitution of the human person,
free will. The section is defined but not created, because there is not yet enough written to fill
it. Studies that touch on it are currently filed under **Salvation** or **Sin**. It will be split out
once two or more studies genuinely belong there rather than being placed there by default.

The same rule applies generally: a section exists when it has content, not in anticipation of it. An
empty section is worse than a slightly overloaded one, because it advertises something the site
doesn't have.

---

## The four content shapes

Subject says *where* a page is filed. Shape says *what kind of thing* it is. There are four.

### Single study

One passage or one question, worked through the
[develop-bible-study](https://github.com/ding0t/bible_studies) process: hook, Key Takeaways,
historical and literary context, word studies, theological principle, discussion questions,
references. One file, filed under its subject. The bulk of the site.

### Series

A subject small enough to be one topic and large enough to need several pages: a **directory
containing an `index.md`**, with the parts as sibling pages. The index carries the introduction and
links the parts in reading order. `god/dreams-and-visions/` is the working example.

This needs no special handling — `references/build/section_index.py` generates a card grid for any
directory that lacks an index page, and the navigation builds itself from the directory tree.

### Book study

A study of a whole biblical book, filed **by book rather than by subject**, living at
`commentaries/<nn>-<book>/index.md`. Dewey subdivides the 220s by book for the same reason: a
reader who wants to know what is in Proverbs navigates to Proverbs, not to a topic.

Genesis, Daniel and Proverbs already share a template, and it is close kin to
[Key Takeaways](key-takeaways.md):

| Section | Holds |
|---|---|
| About | Author, date, occasion |
| Memory verses | Verses worth committing, in the site's standard quote-block format |
| Attitudes | What the book teaches us to value, and what it warns against |
| Key Topics | The book's major themes |
| Types | Persons, objects, or events that pattern Christ or the gospel |
| Prophecies | Direct predictions the book makes or fulfils |
| References | Sources drawn on |
| *Chapters with linked studies* | **Generated** by `commentary_index.py` |

The generated chapter list sits between `<!-- commentary-index:auto-start -->` and
`<!-- commentary-index:auto-end -->`. Everything above those markers is hand-written and survives
regeneration. A book study that outgrows one page splits into sibling pages inside the same book
folder, the way `commentaries/20-proverbs/daily-reflections.md` does.

### Chapter note

A short, verse-anchored note at `commentaries/<nn>-<book>/chapter-<nnn>.md`. Mostly generated,
mostly stubs, and the surface the cross-reference index links into.

---

## What is deliberately *not* a directory

A study has more than one dimension, and only one of them can be a folder. Subject is the folder.
Everything else is a tag:

| Facet | Values |
|---|---|
| `method/` | `word-study`, `typology`, `archaeology`, `textual-criticism` |
| `lang/` | `hebrew`, `greek` |
| `status/` | `investigation` — open inquiry, conclusions not settled |
| `audience/` | `teaching` |
| `person/` | a named individual the study is *about* — `peter`, `melchizedek`, `judas-iscariot` |

The slash isn't decoration: mkdocs-material's tags plugin is configured with
`tags_hierarchy: true`, so `method/word-study` renders as a real parent-and-child grouping on the
[Tags](../tags.md) page rather than as a flat string. Add a value to a facet by using it; the
hierarchy builds itself.

`status: investigation` is worth singling out. Some material here is honest inquiry rather than
settled conclusion, and that distinction matters more to a reader than which folder it sits in. It is
a property of a study, not a place to put one.

`person/` exists to solve a collision that appeared as soon as [Biblical figures](../biblical-figures/index.md)
did. Most Bible people share a name with a book, so a flat `matthew` cannot tell you whether a page
is about the tax collector or the Gospel. The rule is simple: **the bare tag belongs to the book, the
`person/` tag to the human being.** A page about Matthew that also quotes Matthew carries both. Where
two figures share a name they are separated the way Scripture separates them, by father —
`person/james-son-of-zebedee` and `person/james-son-of-alphaeus`.

Tags do **not** repeat what the directory already says. A study in **Last things** is not tagged
`prophecy`; a study under `studies/` is not tagged `studies`.

---

## Passage-based access

Subject is not the only way in. Every study declares the passage it is about
(`primary_passage`) and the passages it cites (`bible_references`), and
`references/build/commentary_index.py` uses those to generate cross-links from every affected
chapter under [Commentaries](../commentaries/index.md). A reader who arrives at Deuteronomy 18
will find the studies treating it, regardless of which subject folder they were filed in.

This is the most reliable part of the system, because it is *derived* rather
than hand-maintained. Metadata that nothing renders drifts, quietly, until it is wrong everywhere.
Metadata that generates something visible stays correct because breaking it is immediately obvious.

---

## Known awkward cases

Two existing studies do not have an obviously right home, and it is more honest to name them than to
pretend the scheme is seamless:

- **Biblical Numerology** — it is about a pattern *in* the text, which argues for Scripture, but it
  is not about the text's transmission or canon like everything else there.
- **Genealogy and Times** — chronology from creation to Christ, which touches Scripture (dating),
  Biblical figures (the genealogies), and Last things (it feeds the prophetic timeline).

Both are filed by primary subject and tagged for the secondary one. Any taxonomy applied to real
material produces a few of these; the fix is a good tag, not a new folder.
