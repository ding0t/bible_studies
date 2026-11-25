---
name: review-bible-study
description: Critically audits an existing study, commentary, or sermon file in docs/content/ -- scripture-quote accuracy, citation accuracy, word studies re-verified against source, the study's own synthetic claims (correspondences, orderings, counts, arithmetic) verified independently, claims cross-checked against a commentary, exegesis-context coverage per how-to-read-the-bible.md, consistency with statement-of-faith.md, taxonomy placement, frontmatter and tag correctness, and a style-guide pass. Use when the user asks to review, audit, fact-check, critique, double-check, or verify an already-drafted or already-published study -- as opposed to develop-bible-study, which builds a new one.
---

# Review a Bible Study

This skill goes back over a file that already exists and treats every claim in it as unverified
until it is re-derived from source. develop-bible-study builds a study; this one finds out whether
it holds up.

**Don't fix anything while reviewing.** A reviewer who edits as they go stops scrutinising the
sections already fixed. Record every finding (see **Reporting**) and fix only after the user has
seen the whole list.

## Before starting

Get the target file from the user. Note whether it is `draft: true` or live (`draft: false`): a live
file failing review is the higher priority.

Look for `references/study-state/<slug>.yml`. If it exists, this review adds to its trail. If it
doesn't, say so in the report, and don't backfill a trail for phases nobody tracked.

## Phase 1 — Scripture accuracy

Re-query every quoted verse from source.

- **ESV/NIV/NKJV/CSB**: `study-notes.db`'s `verses` table, via `study_verse` or the access pattern in
  [references/README.md](../../../references/README.md#study-notesdb-commercial-study-bible-commentary-external-not-in-this-repo-at-all)
  (the `immutable=1` URI form is mandatory under the sandbox).
- **WEB/BSB/ASV/YLT/LXX/MT** and the other `bible-text.db` translations: `bible_verse` or
  `query.py verse`. The BSB is `berean-bsb`.
- **A reference is not a universal address** (AGENTS.md): move it with `bible_parallel` before
  calling a quotation wrong against another work's "same verse".
- Check three things per quote: the text matches verbatim, punctuation included; the reference is
  the verse actually quoted; the translation labelled is the one queried. (John 6:34's "Lord" for
  the ESV's "Sir" is the standing example.)
- For verses cited without quotation, spot-check a sample: does the verse say what is claimed?

## Phase 2 — Reference & citation accuracy

- **Cross-references.** Check that each linked passage supports the stated relation. A
  plausible-sounding one that doesn't is common.
- **Extra-biblical citations.** Spot-check TWOT roots (`twot_root`, `twot_strongs`), Strong's ids and
  glosses (`bible_word`) and named commentaries against the source. A wrong number reads exactly
  like a right one.
- **What each reference and Strong's tag opens.** Each opens a pop-up, so a wrong one is a wrong
  citation shown to the reader. A reference without its book ("(21:2)", "v. 20" outside a
  continuation like "(Revelation 21:2, 9)") resolves against whatever precedes it
  ([formatting.md](../develop-bible-study/formatting.md)). A word with no Strong's number gets no
  card; `references/build/strongs_suggest.py <file>` lists them. Report a misresolving reference or
  wrong number at the severity of the citation it amounts to, and a missing number as **Minor**.
- **Internal links.** Confirm every relative link's file and anchor exist. Nothing in the build
  catches a moved heading.
- **Quotation length.** Tally quoted Scripture per restricted translation against the caps in
  [references/README.md](../../../references/README.md#two-different-permissions-dont-conflate-them)
  (NIV 25%, ESV/CSB/NKJV 50% of the quoting work), and keep commentary quotations to a sentence or two.
- **Named version.** "The Mishnah" or "Sefaria" is not checkable. Sefaria's default Mishnah English
  is the CC-BY-NC William Davidson Edition, which `references/build/sefaria.py` and
  [references/README.md](../../../references/README.md) avoid; re-fetch through the script with a
  named version and compare. Wrong version and wrong words travel together.
- **"Not available" may mean unqueryable.** Before accepting that a text could not be checked, run
  `python3 references/check_sources.py` and read its **raw-only** list. An **UNDOCUMENTED** result is
  a finding: the fix is a row in references/README.md.
- **External material resolves through `$BIBLE_MEDIA_ROOT`** (`references/build/media_root.py`). If a
  study says verification was skipped because the volume was offline, check whether that is still
  true before repeating it.
- **Hebrew/Aramaic in markdown bold** is **Critical**: it misplaces the vowel points
  ([style-guide.md](../develop-bible-study/style-guide.md#hebrewrtl-text-and-markdown-bold)).
  `npm run validate` (from `app/`) reports it.

## Phase 3 — Word studies, critically

Re-derive, don't re-read: [word-study-method.md](../develop-bible-study/word-study-method.md),
applied adversarially.

- **Counts.** Re-run `bible_concordance` for every term the study leans on and confirm the stated
  count and list. For a bare frequency, pass `count_only=True`. Each tagged word's pop-up shows its
  count too, so a wrong one is contradicted on the page; check against the concordance, never the
  card, which is an export (`references/build/export_popups.py`) that can lag. Say which is stale.
- **Disputed renderings.** Run `uv run python alignment_ranking.py --study docs/content/<study>.md`
  (from `references/build`). For an `interpretive` word the study must say which rendering it follows
  and why. A word with no entry in `docs/data/word-renderings.toml` is a finding: settle it from the
  word's uses, the Septuagint and the New Testament, then the ESV, and propose an entry.
  A `decided` entry shows on the word's card; re-run `alignment_ranking.py` after editing the file.
- **Translators' footnotes.** Pull `note_type='footnote'` for the `primary_passage` and read them
  all. An *"Or X"*, *"Lit Y"* or *"Some mss omit Z"* the study never mentions, where it argues from
  the other reading, is an undisclosed fork: **Moderate** if the argument turns on it, **Minor** if
  incidental.
- **Root fallacy.** Flag "literally/originally means X" used to set the meaning in the passage.
- **Glosses and domains.** Check against `bible_word` and `bible_domain` directly.
- **"No translation preserves this."** Spot-check at least two of the translations named.
- **Syntax and coreference.** Re-query an implicit subject, pronoun antecedent or construct chain
  with `bible_syntax`. A `NULL` means not annotated; confirm the verse is covered before treating
  silence as contradiction.

## Phase 4 — The study's own claims

Phases 1–3 check claims against a source. This phase checks the claims the study constructs itself:
for a typology, chronology or pattern argument, most of what the reader came for.

**Extract them into a list, away from the prose, before checking any.** A synthetic claim is usually
the most polished sentence in its paragraph, and an author re-reading supplies the relation intended
in place of the one written.

- **Identity and family** ("Zechariah son of Jehoiada", "Emmaus, seven miles west"): check against
  `bible_names`. A link TIPNR marks (a)/(d)/(f)/(?), or a site scored low or with close rivals, is
  contested; stated flat, it is overclaimed.
- **Correspondence** ("X answers to Y"): check the relation. Both halves can be accurate and the
  relation false.
- **Ordering** ("in order", "first … then"): lay the two sequences side by side and compare positions.
- **Quantity** ("four times", "the only place"): re-run the count, for English words, books, events
  and people as well as original-language terms.
- **Arithmetic** (dates, spans, era conversions): recompute.
- **Uniqueness** ("the only", "no other", "every"): usually written unverified.

**A false synthetic claim is Critical**: the study asserts it in its own voice, with no source to
check it against. `day-is-a-thousand-years.md`'s "day three's two events, in order" survived a full
review because every phase checked its parts and none its claim
([why-the-rules.md](../why-the-rules.md#review-phase-4)).

## Phase 5 — Commentary cross-check

- Query `study-notes.db` for a commentary on the `primary_passage` that the study's References do
  not already cite.
- Compare the central claims (the principle and the exegetical moves under it) and report each as
  **confirms**, **silent** or **complicates/contradicts**.
- A contradiction sends you back to the text. Weigh the commentary's reasons against the passage: if
  the text supports the objection, it is **Critical**; if the study's exegesis answers it, report
  the disagreement and recommend no change. Never recommend "contested" only because a study Bible
  reads it differently.
- Report any exegetical step that rests on a study note alone, and recommend grounding it in the text
  or dropping it ([cross-references.md](../develop-bible-study/cross-references.md#commentaries-and-study-notes)).

## Phase 6 — Context coverage

Mark each of the six questions on
[how-to-read-the-bible.md](../../../docs/content/scripture/how-to-read-the-bible.md) **covered**,
**partial** or **missing**:

1. Genre identified, and its lens applied? For a prediction, check each fulfilment claim against
   [prophecy-method.md](../develop-bible-study/prophecy-method.md): the New Testament use labelled, and every ledger cell sourced.
2. Historical occasion (author, audience, date, circumstance)?
3. Literary context (before and after, the unit of thought)?
4. Original-language check wherever a word does theological work? (Coverage; Phase 3 is correctness.)
5. Cultural-vs-transcultural line drawn explicitly?
6. The principle taught elsewhere in Scripture, beyond one narrative detail?

Mark a seventh separately:

7. **Statement-of-faith consistency.** Where the principle meets a position in
   [statement-of-faith.md](../../../docs/content/about/statement-of-faith.md), is it consistent?
   **Missing** is the usual result. Report a conflict as a tension for the author; never suggest
   rewriting the study or the statement.

A study can pass Phases 1–5 and fail here by skipping straight to application. Don't skip this phase
because the sourcing checked out.

**Then the mechanical half.** Run the `review_gaps` MCP tool with the study's path (the `study_*`
tools are about study Bibles). CLI fallback: `cd references/build && uv run python study_gaps.py
<path>`. Weigh its kinds differently:

- **quotation**: a textual fact. A study that treats a passage and never names what it quotes has a
  gap (Hebrews 3 without Psalm 95).
- **parallel**: the BSB translators' judgment that another passage tells the same story. Report an
  unnamed parallel unless the study has a reason to stay with one account.
- **hebrew-candidate**: a 19th-century translator's judgment; check it in Greek.
- **crossref**: a lead only.

A long gap list is normal. Report what bears on the argument, and say why. A study with neither
`primary_passage` nor `bible_references` is invisible to this check and to the commentary index;
that is its own finding.

### Check the study against its siblings, not only against sources

Every check above compares a claim to a source; this one compares it to the site's other studies,
where the corpus has contradicted itself while each file passed review alone
([why-the-rules.md](../why-the-rules.md#review-siblings)).

```bash
cd references/build
uv run python cross_study_claims.py --min-studies 4                         # the shared surface
uv run python cross_study_claims.py "John 4" --exclude jesus/woman-at-well.md  # one chapter's siblings
```

Run it for each chapter the study leans on. Each sibling has a role: **primary** (its
`primary_passage`), **cited** (its `bible_references`) or **prose**. Start with the primary ones and
ask:

1. **Do they agree?** Where they don't, which to fix is the user's call.
2. **Does this study re-argue a sibling's ground without linking it?** That should be one sentence
   and a link. A primary sibling on the same verses that is never mentioned is a finding.
3. **Could either enrich the other?** Report both directions as suggestions, and never edit the
   sibling in this review.

If the state file has `sibling_studies`, check that each marked `link` or `build-on` is linked, and
that no link points to a `draft: true` page (validator Check 24).

## Phase 7 — Placement, frontmatter & tags

Audit against [placement-and-tags.md](../develop-bible-study/placement-and-tags.md):

- **Placement.** Is the file in its subject's section, or parked beside a related study? Older
  studies may predate `salvation/` and `biblical-figures/`.
- **Tags**, against [docs/content/tags.md](../../../docs/content/tags.md): a tag restating the
  section, a flat facet (`word-study` for `method/word-study`), colons, uppercase or spaces,
  near-synonyms, a person tagged with a book's bare name.
- **Frontmatter**, per that file's "Frontmatter failures worth checking" and "The provenance
  fields". A missing or stale provenance field is fixed by running
  `python3 utils/refresh_frontmatter_provenance.py`, never by hand.

**Minor** by default. Two are **Major** because they corrupt a page elsewhere: a missing
`primary_passage`/`bible_references` (the commentary index under-reports it), and a surviving
`gregorian_year: -4004` placeholder (a false timeline entry, which `build-events.js` plants even for
a draft).

## Phase 8 — Style guide pass

**Do the reading test first, before any grep.** Read the prose start to finish and mark every
sentence your eye slides past ([style-guide.md](../develop-bible-study/style-guide.md#the-reading-test-that-catches-all-of-this)).
Then run the guide's tells: bare intensifiers, grader adjectives, narrated argument, contrast rhythm,
em-dash density, rule-of-three padding, and sentences that don't survive deletion. Confirm the
section order in develop-bible-study Phase 7.

**A clean `npm run validate` is not a pass.** Its style checks are four narrow regexes (Checks 10–13),
and the narrated argument, the apologia posture and the straw alternative match none of them. **Learn
the shape, not the specimens**: *"Notice that…"* is listed and *"Note what this is"* is not, and they
are the same sentence ([why-the-rules.md](../why-the-rules.md#review-phase-8)).

**Three tells need a human** ([human-review.md](../develop-bible-study/human-review.md)): the
antithesis construction (count it; one every 210 words is the observed drift), essay register in
Key Takeaways, prayer and application, and writing around the theology. Count the first, report the
other two, and hand the page to the user.

**Then the format checks** in [format-checks.md](format-checks.md) that apply, and
[graphics-checks.md](graphics-checks.md) if the study has a comic or drawn plates.

Style findings are **Minor** one at a time, and **Moderate** when the register is pervasive.

## Reporting

Findings, most severe first:

- **Critical**: wrong Scripture text, a citation that doesn't say what's claimed, a wrong translation
  label, a false synthetic claim (Phase 4), a commentary contradicting a central claim that the text
  supports, Hebrew broken by bold, or a conflict with a marked-essential section of the statement of
  faith (Scripture's authority, the Trinity, salvation/justification). These block `draft: false`, or
  need a prompt fix on a live page.
- **Moderate**: a Phase 6 context gap, a statement-of-faith conflict outside those sections, a count
  that is directionally right but numerically off, a cross-reference weaker than stated, a conclusion
  contradicting a sibling, pervasive style register.
- **Minor**: style hits, padding, structural nits, a sibling's ground re-argued without a link, a
  primary sibling never linked.

**Suggestions for other studies** go in their own list after the findings, naming each study and the
section the addition would go in.

**Report the size**: the study's word count, its budget (`word_budget` in the state file, or 4,000),
and the net words the fixes would add. Where a fix pushes it over budget, pair it with a cut or name
a fork candidate for **simplify-bible-study**.

Present the list before fixing anything. Once the user has chosen, fix directly, or hand anything
needing a redraft to develop-bible-study.

**Record the review**: append a dated `review_<YYYY-MM-DD>` block to the state file, saying what was
checked and found. With no state file, say so rather than fabricate a trail.
