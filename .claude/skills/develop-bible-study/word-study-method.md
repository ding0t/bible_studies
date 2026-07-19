# Word study method

An operationalized version of the diachronic → synchronic → conclusion method for original-language word studies, adapted from Gerald L. Stevens' seminary word-study handout ("Word Study Guide — New Testament"). The handout is course material, not public domain — it is **not committed to this repo**; the source PDF stays on the personal media volume it was extracted from, alongside the Fee extraction (see [references/README.md](../../../references/README.md#secondary-commentary-sources)). What follows is a synthesis of the method in our own words, not a reproduction of the handout's text.

Phase 4 of [SKILL.md](SKILL.md) links here. Use the full method below for words that are genuinely load-bearing or ambiguous in context (Paul's "righteousness" in Rom. 1:17, "flesh" in Rom. 8, etc.) — not for every noun that happens to have a Strong's number. For a routine term, the lighter treatment already in Phase 4 (Strong's number, gloss, pronunciation) is sufficient; reaching for the full apparatus below on a word whose meaning isn't actually in question is padding, not rigor.

## Step 1 — Diachronic: how the word arrived here

Trace the word's usage *through time*, in order: Classical Greek, then the Septuagint (LXX — the Greek OT Paul and the early church actually read), then other Hellenistic Jewish literature (apocrypha, pseudepigrapha, rabbinic sources, Qumran/Dead Sea Scrolls). The goal is a *range* of attested meanings, not a single "root meaning."

**Root fallacy guardrail:** a word's ancient or etymological root is not its present-tense meaning. If a conclusion leans on "the root word literally means X" as though that settles usage in the passage at hand, that's the error this step exists to catch — flag it and go back to usage evidence instead.

## Step 2 — Synchronic: how the word was actually used

This carries the most weight in the study, and itself narrows in three passes:

**2A. Across the New Testament.** Concord the word — by its Greek/Hebrew lexical number, not the English gloss, since translators vary the English word used for the same original term (and occasionally supply an English word with no corresponding original-language term at all). Group occurrences by author/corpus rather than treating the NT as one undifferentiated pool:

1. Matthew
2. Mark
3. Lukan (Luke, Acts)
4. Johannine (John, 1–3 John, Revelation)
5. Pauline (Romans–2 Timothy)
6. Hebrews
7. James
8. Petrine (1–2 Peter)
9. Jude

Sort occurrences into meaning-subcategories as they emerge (don't force every instance into a category decided in advance — an occurrence that doesn't fit is itself a finding). Cross-check the concordance work against a semantic-domain lexicon — Louw & Nida for Greek, SDBH (Semantic Dictionary of Biblical Hebrew) for Hebrew — which groups words by usage relationship rather than lexical root and often surfaces a contextual nuance a straight concordance search misses. Both are now available as local data, not just print: `references/open-data/macula-greek/SBLGNT/tsv/macula-greek-SBLGNT.tsv` and `references/open-data/macula-hebrew/WLC/tsv/macula-hebrew.tsv` carry a per-word `domain`/`ln` (Greek) or SDBH (Hebrew) column alongside lemma, Strong's number, morphology, and gloss — see [references/README.md](../../../references/README.md#word-study--original-language-tools). For Hebrew concordance/chunking specifically, `references/open-data/hebrew-vocab-tools/` adds paragraph- and pericope-level grouping keyed to the Masoretic text's own markers.

**2B. Across this author's other writings.** Narrow to the passage's own author (or corpus, if the author wrote more than one book). Note where this author's usage tracks the wider NT pattern from 2A and where it doesn't — an author-specific nuance here is often exegetically significant.

**2C. In this passage.** Heaviest weight of all three passes. Grammar, syntax, sentence flow, genre, and where this sits in the author's argument up to this point govern which sense from the established range is actually in play here.

## Step 3 — Conclusion

- State the established range of meaning for the word.
- Note continuity/discontinuity between that range and this specific occurrence — is this a standard use, or is the author doing something distinctive with it?
- Choose the option that best fits this context, and say why the alternatives were set aside. Don't just list the options and stop short of a call — Phase 4 exists to feed a reading, not a lexicon dump.

## Recording

Capture the term in the study-state file's `content_word_studies.terms` entry (see [study-state.template.yml](study-state.template.yml)). Beyond `word`, `language`, `transliteration`, `strongs_id`, and `gloss`, use the `range_of_meanings` and `notes` fields for what Steps 1–3 above turn up — enough that a later session (or a different agent) can see the reasoning, not just the final gloss.
