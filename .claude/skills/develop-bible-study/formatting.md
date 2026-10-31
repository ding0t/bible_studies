# Formatting: quotations, references, word tags, sources

The mechanical rules a study's text follows, drafted to in develop-bible-study Phase 7 and checked
against in review-bible-study. `npm run validate` enforces the quote-block shape (Checks 1–9); the
rest is on the writer.

## Label every quotation's translation, where it appears

Give the translation for every quotation (AGENTS.md), per quote, not once for the study. When a
lookup tool returns text, check which `work_id` it came from before dropping it into prose rather
than assuming ESV because ESV is the default. **Quoting WEB, ASV or another named translation is a
legitimate choice** where it preserves something the ESV's smoother rendering loses. The failure is
doing it *silently*, so a paragraph reads as continuing the ESV when it has drifted word for word to
another version. Label every non-ESV quote in place (`(Genesis 8:20, WEB)`), not only in References.
A review-bible-study pass caught exactly this drift across a whole section of an earlier study.

## Scripture quote block

Any block quote of Bible text (not a short inline citation) takes this shape. Reference examples:
[as-the-snake-was-lifted.md](../../../docs/content/jesus/as-the-snake-was-lifted.md),
[bread-of-life-feeding-the-multitudes.md](../../../docs/content/jesus/bread-of-life-feeding-the-multitudes.md).

```
> ✝️ Book Chapter:Verse-Verse (TRANSLATION)
>
> N Verse text starts here, with each verse's number inlined into the
> flowing prose N+1 continuing straight into the next verse's text.
```

The `✝️ Reference (TRANSLATION)` line comes **first**; reference-after-with-an-em-dash is the old,
wrong shape. Verse numbers appear even for a single verse (`> 4 The LORD has sworn...`). A
multi-verse quote stays one continuous block quote.

## References: plain text, never linked, always with the book

**Write references as plain text — `(Romans 8:28, ESV)` after a quotation, `(Romans 8:28)` for a
bare citation — and do not link them.** The pop-up script (`app/src/entries/popups.js`) finds every
reference on the rendered page; a link hides it. Two markers cover what plain text cannot say:
`<span data-ref="Genesis 7:11">7:11</span>` for a partial reference, and
`<span data-strongs="H7657">Seventy</span>` for an English word standing in for the original. Link
to Blue Letter Bible only as a deliberate send-off for follow-up study, with link text saying so.

**Every reference names its book: `(Revelation 21:2)`, never `(21:2)`, `v. 20` or `at 4:16`.** The
one exception is a continuation in the same citation: `(Revelation 21:2, 9; 22:17)`. A bare
reference resolves against whatever came before it, and an edit that moves that sends it somewhere
else without warning: in `bride-of-christ.md` a rewritten opening made "(21:2)" open Isaiah 21:2 on
the live site. A listener to a study read aloud cannot scroll back for the book either.

## The pop-up works alongside the prose, never instead of it

- **Quote every verse the argument rests on**, in the translation it argues from. The pop-up shows
  the reading translation (the BSB), so an argument from ESV wording has to show the ESV words.
  Nothing pops up when a study is read aloud (style-guide.md rule 7) or printed.
- **Give a verse you only point to a bare citation.** Don't quote or paraphrase it to save the
  reader a lookup; the pop-up does that.

## Word tags

**Keep each word study's script, transliteration and Strong's number in the prose, in one shape:
`ἀρραβών (*arrabōn*, G728)`, `<span dir="rtl">גֹּאֵל</span> (*goel*, H1350)`.** Inside the
parentheses: transliteration, pronunciation if given, number, then gloss —
`(*Petros*, PET-ross, G4074, "a rock")`. The number is what makes the pop-up card certain; without
it the form index guesses and leaves an ambiguous form unlinked. Tag the first mention in the body,
never a heading (headings are not scanned). An Aramaic form with no Strong's entry (כֵּיפָא
*kepha*) keeps the shape with no number. `references/build/strongs_suggest.py <file>` lists glossed
words still missing a number.

The card already shows the gloss, the counts and every place a rare word occurs, so don't restate
those as lists. State the count or the "only here" the argument needs, verified with
`bible_concordance` and recorded as `evidence:`. The card counts on the exact Strong's id, as
`bible_concordance` does, so a stated count that disagrees is contradicted on the same page.

Never wrap Hebrew or Aramaic in markdown bold (style-guide.md, "Hebrew/RTL text"; Check 9).

## References & Recommended Reading

Every study ends with this reader-facing bibliography, distinct from the state file's
`resources_consulted`. List every lexicon, commentary, dictionary or background source drawn on,
restricted ones included by name (TWOT, Cultural Backgrounds Study Bible, Fee & Stuart). Naming and
briefly quoting a restricted work with attribution is normal scholarship.

## Copyright

Two different permissions; don't apply one rule to both.

- **Bible text** is covered by each publisher's allowance. **The limit that binds is the
  percentage of the quoting work, not the verse count** — a short study that is mostly block-quoted
  Scripture can breach it at a couple of dozen verses, and is usually too thin on its own
  contribution as well. NASB has no blanket allowance.
- **Commentary, study notes, introductions, articles, charts, maps** have **no blanket allowance**.
  "A sentence or two, always attributed" is the whole of what's available, for `study-notes.db` and
  the Fee extract alike. Synthesize in your own words; never paste a full note into a committed file.
- **Attribution is a licence condition.** The notices ESV/NIV/NKJV/CSB require live on
  [copyright.md](../../../docs/content/about/copyright.md); a study that introduces a translation or
  major source not listed there adds it in the same commit.
- **Look the thresholds up, don't recall them:**
  [references/README.md](../../../references/README.md#two-different-permissions-dont-conflate-them).
