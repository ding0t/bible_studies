# Finding the quotations the links miss: research, 2026-10-19

[What the Scripture Links Reveal](../content/scripture/what-the-links-reveal.md) showed well-known
quotations absent from the derived links: James 2:8, Romans 1:17, John 10:34 ("you are gods"), Matthew
24:15, the Chronicler's psalm, Obadiah and Jeremiah 49. This note records what was tested to recover
them. The experiments live in `references/build/link_lab.py` (not part of the build); each section names
its subcommand.

## Answer keys

Precision and recall need keys with no connection to the method.

| Key | What it is | Size | Used for |
|---|---|---|---|
| WEB footnotes (`web-crossrefs`) | the translators' notes marking New Testament quotations | 423 NT→OT references | recall |
| unfoldingWord Translation Notes | notes filed under the `writing-quotations` article, with the OT verse named or linked | 213 NT→OT references (154 shared with WEB) | second recall key |
| openbible cross-references | crowd-voted, English scheme | 830,866 | precision, by score bin, as the original thresholds were set |
| known Old Testament parallels | sixteen passages (`KNOWN_OT` in the lab) | 266 verses | Hebrew recall |

**The baseline is low.** Today's strong Greek links (alignment 18) find 17% of the WEB-footnoted
quotations and 18% of the Translation Notes ones. Many footnotes are allusions no word method will
find, so the ceiling is well under 100%, but the gap is real.

## Greek: New Testament to Septuagint (`compare`, `model`, `fp`)

| Technique | Links | Corroborated | WEB recall |
|---|---|---|---|
| surface 4-grams + alignment ≥ 18 (today) | 140 | 82% | 17.0% |
| lemma / Strong's keys, rarity-weighted alignment ≥ 32 | 122 | 77% | 14.2% |
| **phrase fingerprints**: ≥ 3 three-word phrases each found in one LXX verse | 158 | 87% | 22.0% |
| **combined model** (logistic, cross-validated) at p ≥ 0.8 | 228 | 83% | 29.6% |
| combined model at p ≥ 0.9 | 187 | 86% | 25.1% |

- **Lemma keys alone are no better at equal precision**, but they recover specific short quotations
  (James 2:8 scores 20, John 1:23 20.5, Romans 1:17 17) and reach Malachi 3:1. MACULA's Strong's
  numbers unify suppletive verbs (εἶπεν and λέγω both 2036). The LXX lemma file numbers the article
  3801 where MACULA uses 3588; `KEY_FIX` maps it.
- **Phrase fingerprints are the best single signal.** A run of common words can be unique as a phrase.
  John 10:34 shares four everyday words with Psalm 82:6 (LXX 81:6), *ἐγὼ εἶπα θεοί ἐστε*, which no
  rarity method sees; the phrase occurs in one Septuagint verse, and that uniqueness is the evidence.
- **Citation formulas are a prior.** γράφω, γραφή, πληρόω and ῥηθέν in the verse or the one before lower
  the bar safely: two unique phrases plus a formula is 81% corroborated, and recovers John 10:34,
  Matthew 4:7 and 4:10, and Romans 1:17.
- **The combined model** weighs surface alignment, lemma alignment, rare-word weight, the fingerprint
  counts, the formula, and verse lengths, learned against openbible and tested against the WEB key.
  At the same precision as today it finds about 60-70% more. A linear model still underrates a short
  verse that is all quotation, so the formula rule should sit beside it.

## Hebrew: the Old Testament quoting itself (`ot`, `otg`)

Surface matching fails on spelling: 1 Chronicles 16:8 and Psalm 105:1 are the same seven words, but
one is spelled with a vowel letter (<span dir="rtl">עלילתיו</span> / <span dir="rtl">עלילותיו</span>),
so they score 12. MACULA's Hebrew lemmas (prefixes split, spelling normalised) remove the problem.

| Technique, whole Old Testament | Links | Corroborated | Known-parallel verses (of 266) |
|---|---|---|---|
| surface trigrams, alignment ≥ 18 (today) | 822 | 59% | 68 |
| lemma keys, rarity-weighted ≥ 36 | 1,549 | 62% | 116 |
| **weighted ≥ 36, or a run of ≥ 22 on the diagonal** | 2,054 | 61% | 211 |

**Passage chaining** is the plagiarism-detection idea that matters here: borrowed passages come as
runs, verse after verse on the same diagonal. A weak pair whose neighbours also match is part of a
borrowing. Within the known passages the weighted lemma method finds 252 of 266 verses; the global
rule above keeps precision at today's level and still triples recall.

## Across the languages (`twl`)

Some quotations follow the Hebrew where the Septuagint differs (Matthew 2:15 and Hosea 11:1; John 19:37
and Zechariah 12:10), and no Greek-to-Greek method can find them. unfoldingWord's **Translation Words
Links** tag Hebrew and Greek words with shared concepts, a ready-made bridge. Ranking every Old Testament
verse by concept alignment:

- **Matthew 24:15 → Daniel 12:11 ranks 1st** (abomination, desolate, holy place). No word method found it.
- **Matthew 12:18 → Isaiah 42:1 ranks 1st.** Matthew 26:64 → Daniel 7:13 ranks 26th.
- Short or thinly tagged verses fail; Psalm 82:6's *elohim* is tagged "god" and John 10:34's θεοί
  "falsegod", so the bridge breaks exactly where the meaning is contested.

Concept tags are a useful extra feature, too sparse to stand alone.

## Recommendations

1. **Hebrew:** switch the inner-biblical class to MACULA lemma keys with rarity weighting and
   diagonal chaining. Clear win: same precision, three times the known parallels.
2. **Greek:** add phrase fingerprints and the citation-formula rule; rank with the combined model.
   Keep the classes separate, as now, and keep every component score on the row.
3. **Answer keys:** ingest unfoldingWord Translation Notes (CC BY-SA 4.0, open tier) as a second
   quotation key, and as explicit "quoted here" leads on the Scripture Links page.
4. **Cross-language:** ingest Translation Words Links as a concept bridge. Next experiment: a
   Greek↔Hebrew Strong's lexicon learned from Septuagint–Masoretic verse pairs (IBM Model 1 style),
   for the Hebrew-following quotations the concept tags miss.
5. **Sources:**
   - The `lxx-lemmas` Septuagint already carries Old Greek and Theodotion Daniel, both Joshua and
     Judges texts, and both Tobits. Match against it, not only Brenton.
   - Note Brenton's Psalm 13:3 interpolation in the method page.
   - A public-domain Greek 1 Enoch would let Jude 14 be found.
6. **Not yet:** multilingual sentence embeddings. They would catch paraphrase, but they bring a large
   model dependency and an opaque score. Revisit if 1–4 leave a clear gap.
7. **Not measured at all:** New Testament to New Testament. The Synoptic parallels, Jude and 2 Peter,
   and 1 Timothy 5:18 citing Luke 10:7 need a class of their own.

## Built in, 2026-10-20

Recommendations 1, 2 and 4 (as a class of its own), and the Translation Notes from 3, went into the
build. Each rule then had to hold up on the whole Bible, not just the lab:

| Rule | Strong links | Corroborated |
|---|---|---|
| Greek, every rule | 246 (was 140) | 84% (was 82%) |
| unique phrases alone | 57 | 79% |
| citation formula + phrases alone | 24 | 83% |
| Hebrew lemmas, chaining | 2,054 (was 822) | 46% (was 45%) |
| crosslang | 48 | 88% |

Two first versions were noise and were tightened before shipping:

- **Formula by lemma** (γράφω, πληρόω) admitted Colossians 1:9's "be filled" and Revelation's "write".
  Formula by citing form (γέγραπται, ἡ γραφή, πληρωθῇ, ῥηθέν), with Revelation exempt (its "it is
  written" is the book of life), took the rule from 56% to 83%.
- **Hebrew surface matches the lemmas do not confirm** were regnal and ritual formulas at 16%; they now
  need lemma confirmation.

A Psalms-only rule surfaced on the way: the verse-shift correction for psalm titles had been applied to
every book, mapping LXX Micah 5:1 to English 5:3. It now applies to Psalms only (build.py, query.py).

Found since by the method page's answer-key chart: Romans 4:3 cites Genesis 15:6 by formula but shares only one unique phrase, because "credited to him for righteousness" also stands in LXX Psalm 105:31 (106:31). A formula rule taking one phrase plus alignment 14 would recover it; untested for noise.

Still open: Matthew 24:15 (the concept bridge found it; no shipped rule does), Joel 3:16 and Amos 1:2, New
Testament to New Testament, and a Greek 1 Enoch for Jude 14.
