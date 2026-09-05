---
title: "Reading the Original-Language Data"
category: "bible"
description: "What the Hebrew and Greek sources behind this site actually are, what an annotation layer like MACULA adds on top of a text, and what the vocabulary means — lemma, morphology, Strong's number, semantic domain, alignment — with one verse shown at every layer."
tags: ["lang/hebrew", "lang/greek", "method/textual-criticism", "sources", "data"]
draft: false
bible_references: ["Genesis 1:1", "John 1:1"]
date_created: 2026-09-05
date_modified: 2026-09-05
ai_provider_models:
  - anthropic/claude-opus-5
---

# Reading the original-language data

Studies on this site cite things like *"the lemma is <span dir="rtl">בָּרָא</span>, Strong's H1254,
parsed Vqp3ms, semantic domain 002002002005"*. That is precise and checkable, and it is also
impenetrable if nobody has said what any of it means.

Two different things get called "the Hebrew" or "the Greek", and separating them is most of the
confusion:

- **A text** is the words themselves — a manuscript, or a printed edition of one. The Westminster
  Leningrad Codex is a text.
- **An annotation layer** is what has been attached to each word of a text by later scholarship —
  its dictionary form, its parsing, its meaning, its place in the sentence. MACULA is an annotation
  layer.

You can have the same text with different layers, or the same layer applied to different texts. What
a study depends on is usually the layer, not the text, which is why the layer deserves naming.

## The texts

The full account of what each is *worth as a witness* — its strengths, its cautions, where it stands
in the manuscript tradition — belongs to [Bible Translations & Source
Texts](translations.md), which treats them one by one and explains the two columns in the middle of
this table: what **kind of edition** a text is, and whether **translation** stands anywhere in the
chain behind it. Both matter more than what language it is written in. A text can be in Hebrew and
still be a translation out of Greek. What the third column adds is narrower
and specific to this page: **every limitation of a text is inherited by the annotation built on it.**
A lemma attached to a single manuscript is a lemma for that manuscript's reading.

| Text | Kind of edition | Translation in its chain? | The limit the annotation inherits |
|---|---|---|---|
| **WLC** — Westminster Leningrad Codex | Diplomatic edition of one manuscript, about AD 1008 | **None** — Hebrew, in Hebrew | **One manuscript, not a reconstruction.** Where that scribe was idiosyncratic, so is every lemma and parse built on him. Its vowel points are Masoretic and medieval — centuries younger than the consonants they interpret — so a parsing that depends on vocalisation is resting on a later reading, not on the oldest layer of the text |
| **SBLGNT** — SBL Greek New Testament | Eclectic edition, 2010, compiled from earlier critical editions | **None** — Greek, in Greek. The default Greek in this site's database | **Eclectic: no single manuscript reads exactly this.** It is a reasoned synthesis of earlier critical editions, so the annotation describes an edition rather than any surviving copy |
| **Brenton Septuagint** | Edition of an **ancient translation**, Vaticanus-based, 1851 | **Yes, twice** — the Septuagint renders Hebrew into Greek before Christ; Brenton then renders that into English alongside it | **A translation, so it witnesses its Hebrew source at one remove** — and translators interpret. Brenton follows Vaticanus, one Septuagint tradition among several that diverge |
| **UHB / UGNT** | Derived texts — UHB from the WLC tradition, UGNT following the Bunning Heuristic Prototype | **None** in the texts themselves; the ULT aligned to them is an English translation | **UGNT is a heuristic text**, not a committee edition, and differs from SBLGNT in roughly one verse in six. Alignment data resolves against *it*, so check which Greek a wording came from |
| **Dead Sea Scrolls** | Manuscripts — actual surviving copies, not an edition | **None** — Hebrew, in Hebrew | **Neither complete nor uniform.** 31.8% of words carry an editorial mark, so a bracketed reading is a modern reconstruction; and the scrolls are textually plural — some proto-Masoretic, some behind the Septuagint, some independent. "The scrolls read X" is usually "one scroll reads X" |

The pattern across that column is worth naming, because it is the honest limit of everything on this
page: **annotation is only ever as good as the text it sits on, and none of these texts is neutral.**
A single medieval manuscript, a modern reconstruction, an ancient translation and a heap of fragments
each carry a different kind of uncertainty, and a study that leans hard on a word should say which
one it is standing on.

## The layers, and what MACULA is

**MACULA** is a set of open scholarly annotations published by Clear Bible, one for Hebrew and one
for Greek. It does not contain a Bible; it contains a row for every word of one, saying what that
word is. When a study on this site says "MACULA gives the domain as…", it means this dataset, not a
translation or a manuscript.

Everything below is a layer MACULA (or a comparable source) attaches to a word.

### Surface form

The word exactly as it stands in the text, inflected, with its vowel points and accents. Genesis
1:1's third word is <span dir="rtl">בָּרָ֣א</span>.

Surface forms are what you *read*, and they are nearly useless for searching: the same word appears
in dozens of inflected shapes, and Hebrew adds pointing that a plain search will not match.

### Lemma — and what "lemmatised" means

The **lemma** is the dictionary form of a word: the form you would look up. <span dir="rtl">בָּרָ֣א</span>
in the text has the lemma <span dir="rtl">בָּרָא</span> — *bara*, "to create".

To say a text is **lemmatised** is to say somebody has done that identification for every word in
it, and recorded it. That is the single most useful thing in this whole list, because it is what
makes a real word study possible. Without it you can search for a spelling; with it you can ask
*where else does this author use this word*, and get every occurrence regardless of how it was
inflected — which is the question a word study actually asks.

It is also a judgement, not a fact. Hebrew forms are frequently ambiguous, and a lemmatiser has to
choose. That is one reason this site keeps more than one source rather than trusting a single one.

### Strong's number

A number identifying a word in *Strong's Concordance* (1890) — H for Hebrew, G for Greek.
<span dir="rtl">בָּרָא</span> is H1254.

Strong's is old and its glosses are dated, but the *numbers* remain the common index that lets
different resources talk about the same word. Treat it as an identifier, not as a definition.

### Morphology — "parsing"

What grammatical form this particular occurrence is in, written as a code.
<span dir="rtl">בָּרָ֣א</span> is `Vqp3ms`: **V**erb, **q**al stem, **p**erfect, **3**rd person,
**m**asculine, **s**ingular. "He created."

This is what a grammar teacher means by **parsing** a word. It matters when an argument turns on the
form rather than the word — whether something is a command or a description, singular or plural, who
is acting on whom. For what a form *does*, as against what a word means, this project holds a Hebrew
reference grammar; the studies reach it with `bible_grammar`.

### Gloss

A very short English equivalent, for orientation only — <span dir="rtl">בָּרָא</span> is glossed
"he.created". A gloss is not a translation and not a definition; it is a label so you can tell which
word you are looking at.

### Semantic domain

A code placing the word in a category of meaning, from a scholarly classification — Louw-Nida for
Greek, SDBH for Hebrew. <span dir="rtl">רֵאשִׁית</span> ("beginning") carries `002003003004`; John
1:1's ἀρχή carries `67.65`.

This answers a question a dictionary cannot: *what other words mean something like this one*. Two
words with no shared letters can sit in the same domain, which is how you find a concept rather than
a spelling.

### Alignment

Which original word each English word is rendering. Not part of MACULA — it comes from
unfoldingWord's ULT, and it is the only dataset this site holds that links a translation to its
source word by word.

It matters because most study questions start from an English word, and therefore from a
translator's decision. Alignment turns "which Hebrew word is this?" from a guess into a lookup.

## Where the annotation comes from

The layers above did not appear from nowhere. Each is a project with a history, particular strengths
and real limits, and knowing which one a study leaned on tells you something about how much weight
the claim carries.

**A boundary worth keeping in mind:** this section is about the *annotation projects*. Whether a
given **text** is a good witness — how old the manuscript is, where it sits in the tradition, what
its editors chose — is a different question, answered in
[Bible Translations & Source Texts](translations.md). Where each of these is actually used, and how
it is queried, is on [About Our Datasets](../about/about-our-datasets.md).

### MACULA — Clear Bible

This site's main source for both Hebrew and Greek. Assembled rather than authored: MACULA Hebrew takes
the Westminster Leningrad Codex text released into the public domain by the **Groves Center**, adds
syntax trees developed by **Clear Bible** together with that same centre, and word-sense data from
the United Bible Societies' **MARBLE** project — the Semantic Dictionary of Biblical Hebrew. MACULA
Greek does the same over the Nestle 1904 text (transcribed by Diego Santos, morphology by Ulrik
Sandborg-Petersen) and the SBLGNT, with Louw & Nida's domains from MARBLE.

Clear Bible has changed names twice — Asia Bible Society, then Global Bible Initiative from 2014 to
2020 — which is why older citations of the same data look like different sources.

**Strengths.** Broad and consistent: morphology, lemma, gloss, semantic domain and clause syntax for
both testaments, in one shape, openly licensed (CC BY 4.0). The semantic domains are the part
no other source this site holds supplies, and they answer a question no dictionary does.

**Weaknesses.** It inherits every judgement of its sources, and those sources are not uniform — the
Greek side rests on two different editions. Syntax and coreference coverage is **partial**, so a
null means "not annotated", never "no such relation". And the domain codes come from MARBLE under a
grant to Clear specifically, so they are the one part to cite carefully rather than treat as plain
CC BY.

### Open Scriptures Hebrew Bible (morphhb)

The Westminster Leningrad Codex marked up in OSIS XML with lemma and morphology, maintained as an
open community project. Its own documentation notes that morphology was added progressively rather
than arriving complete.

**Strengths.** The most direct route to the WLC as a *text* with tagging attached, in a simple
format, and the source AGENTS.md points at for Hebrew word studies. Every word carries a stable id
so other datasets can attach to it.

**Weaknesses.** Text and tagging only — no syntax, no semantic domains. For anything beyond the word
itself you need MACULA.

### STEPBible — Tyndale House, Cambridge

Datasets from an established Biblical Studies research institute: Strong's-tagged texts, brief
Hebrew and Greek lexicons, morphology, and cross-references, CC BY 4.0.

**Strengths.** The broadest single source of the lot, covering lexicon and cross-reference needs
together, from scholars rather than a volunteer compilation. Attribution is a condition of STEPBible's own
licence, not a courtesy.

**Weaknesses.** Held but **not ingested** into this project's database, so it is read as raw files
rather than queried. Anyone concluding a word is unattested should remember that this source cannot
be seen by the query tools.

### BHSA — Eep Talstra Centre, VU Amsterdam

Decades of Hebrew linguistic analysis over the Biblia Hebraica Stuttgartensia, distributed in the
text-fabric format, from a university research centre built around exactly this work.

**Strengths.** Deeper syntactic analysis than any other source this site holds — full clause
hierarchy, not just clause role.

**Weaknesses.** **CC BY-NC**: non-commercial only, so it sits in `references/restricted-data/` and
would be off the table if this site ever monetised. Catalogued and licence-checked but not wired
into any query tool, because MACULA already covers subject, role, construct state and coreference.
It is reserved for an argument that specifically needs what MACULA cannot give.

### unfoldingWord — UHB, UGNT, ULT

A translation organisation's data rather than an academic corpus, and it shows in what it is good
at. The Hebrew Bible and Greek New Testament are tagged the same way as the others, but their reason
for existing is that the **ULT** English translation is aligned to them word by word.

**Strengths.** The alignment, which nothing else this site holds has. It is what turns "which Hebrew word is
this English word?" into a lookup.

**Weaknesses.** The Greek text is the *Bunning Heuristic Prototype*, not a committee edition like
NA28 or SBLGNT, and it differs from this project's default SBLGNT in roughly one verse in six — at
John 1:34 it reads Υἱὸς where SBLGNT has ἐκλεκτός. All four are **CC BY-SA**, the only ShareAlike
sources this site uses, which constrains what a derived dataset could be published under.

### Strong's numbers

James Strong's concordance of 1890, long out of copyright, digitised many times over.

**Strengths.** The universal index. Nearly every resource in this space, including all of the above,
carries Strong's numbers, which is what lets them be joined together at all.

**Weaknesses.** It is a Victorian concordance. Its glosses reflect the lexicography of its day, and
its numbering occasionally splits or merges what modern lexicons treat differently. Sound as an
identifier, unreliable as a definition — a distinction studies on this site are expected to keep.

## One verse, every layer

Genesis 1:1, as this site's database actually holds it:

| Position | Surface | Lemma | Strong's | Morphology | Gloss | Domain |
|---|---|---|---|---|---|---|
| 1 | <span dir="rtl">בְּ</span> | <span dir="rtl">בְּ</span> | H0871a | `R` (preposition) | in | — |
| 2 | <span dir="rtl">רֵאשִׁ֖ית</span> | <span dir="rtl">רֵאשִׁית</span> | H7225 | `Ncfsa` (noun, common, feminine, singular, absolute) | beginning | 002003003004 |
| 3 | <span dir="rtl">בָּרָ֣א</span> | <span dir="rtl">בָּרָא</span> | H1254 | `Vqp3ms` (verb, qal, perfect, 3ms) | he.created | 002002002005 |

Read across row 3 and the whole vocabulary is there at once: the word as written, the word as you
would look it up, its identifier, its grammatical form, a hint at its meaning, and its neighbourhood
of sense.

Note that the first word is a single letter. Hebrew attaches prepositions and articles directly to
the front of a word, and the annotation splits them out — which is why a count of "words" in Hebrew
depends on who is counting.

## Why any of this is in a study

Because it is the difference between a claim you can check and one you have to take on trust. When a
study says a word means something, the lemma says which word, the Strong's number lets you find it
in any other resource, the morphology says whether the form supports the reading, and the domain
says what company the word keeps.

Where those citations come from, how the database is built, and how it is queried is on
[About Our Datasets](../about/about-our-datasets.md).

## See also

- [Bible Translations & Source Texts](translations.md) — what each text is worth as a witness, and
  which English translations rest on which of them
- [About Our Datasets](../about/about-our-datasets.md) — the databases, the scripts that build them,
  and the tools that query them
- [Public Data Sources](../resources/public-data-sources.md) — the open datasets this material comes
  from, and others in the same space
