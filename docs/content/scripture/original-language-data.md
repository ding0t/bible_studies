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

Short descriptions here; what each one is *worth as a witness* — its strengths, its cautions, where
it stands in the manuscript tradition — belongs to
[Bible Translations & Source Texts](translations.md).

| Text | What it is |
|---|---|
| **WLC** — Westminster Leningrad Codex | The Hebrew Old Testament, in a digital edition of the Leningrad Codex, a complete manuscript written about AD 1008. This is the Hebrew behind almost every English Old Testament |
| **SBLGNT** — SBL Greek New Testament | A modern critical Greek New Testament, published 2010, openly licensed. The default Greek here |
| **Brenton Septuagint** | The Greek Old Testament: a pre-Christian translation of the Hebrew, and often the version New Testament authors quote |
| **UHB / UGNT** | unfoldingWord's Hebrew Bible and Greek New Testament — the texts their English translation is aligned to, word by word |
| **Dead Sea Scrolls** | Hebrew manuscripts a thousand years older than the Leningrad Codex, and fragmentary |

## The layers, and what MACULA is

**MACULA** is a set of open scholarly annotations published by Clear Bible, one for Hebrew and one
for Greek. It does not contain a Bible; it contains a row for every word of one, saying what that
word is. When a study here says "MACULA gives the domain as…", it means this dataset, not a
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
unfoldingWord's ULT, and it is the only thing here that links a translation to its source word by
word.

It matters because most study questions start from an English word, and therefore from a
translator's decision. Alignment turns "which Hebrew word is this?" from a guess into a lookup.

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
