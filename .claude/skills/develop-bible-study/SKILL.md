---
name: develop-bible-study
description: Walks through exegesis-then-hermeneutics before drafting a new study, commentary, or sermon file in docs/content/. Use when the user asks to start, research, outline, or draft a new Bible study, or asks how to properly study a passage before writing about it.
---

# Develop a Bible Study

This skill operationalizes the two-task method from Fee & Stuart, *How to Read the Bible for All Its Worth*: first **exegesis** (what the text meant, then-and-there), only then **hermeneutics** (what it means, here-and-now). It exists to enforce the principles already stated in [AGENTS.md](../../../AGENTS.md) — context before conclusions, word studies in the original languages, cited sources, dispensational reading of prophecy — as a concrete, repeatable workflow instead of good intentions.

**The one rule that governs everything below: do not draft application or theology before exegesis is done.** If you (the agent) notice yourself reaching for a conclusion, a cross-reference, or a "this means..." before you've established historical and literary context, stop and go back a phase.

## Before starting

Ask the user (if not already given): the primary passage or topic, and where it should land in `docs/content/`.

**Read [placement-and-tags.md](placement-and-tags.md) now, before drafting.** Sections are top level (`docs/content/<section>/<slug>.md` — no `studies/` wrapper, no `bible/`), named from the systematic-theology loci; tags carry the facets the directory can't (`method/`, `lang/`, `status/`, `audience/`, `person/`). That file has the section table, the two sections defined but not yet created, and the tag rules. Getting placement wrong is cheap to prevent and annoying to fix once the URL is published.

Create the state file for this study — see **State tracking** below — before doing any research. Update it as you complete each phase; this is what lets the study be picked back up in a later session without re-deriving where you left off.

## Phase 1 — Scope & classify

- Identify the primary passage(s) and any supporting cross-references already known.
- Identify the genre(s) involved (epistle, OT narrative, Acts/historical narrative, Gospel, parable, law, prophets, psalm, wisdom, apocalyptic/Revelation, or topical spanning several). Genre determines which questions in Phase 4 apply.
- Note this in the state file's `genre` field.

## Phase 2 — Exegesis: historical context

- Author, audience, date, and the historical/cultural occasion — what circumstance called this text into being?
- Geographic, political, or customary background relevant to understanding it (a denarius as a day's wage, the shape of a first-century cross, etc.) — these are exactly the kind of "cultural context" AGENTS.md asks for.
- Where useful, cite a Bible dictionary or reputable background source — record it in `resources_consulted`.

## Phase 3 — Exegesis: literary context

- Where does this passage sit in the book's argument or story? What comes immediately before and after, and why does the author move from one to the other?
- Identify the unit of thought (paragraph for prose, strophe/section for poetry) — don't exegete a verse in isolation from its paragraph.
- The governing question, asked of every unit: **"What's the point?"** — trace the author's own train of thought rather than importing one.

## Phase 4 — Exegesis: content, words, and genre lens

- Word studies: identify key theological or ambiguous terms, get the underlying Hebrew/Aramaic/Greek, gloss, and English pronunciation (per AGENTS.md). Use the Strong's/lexicon resources in [references/README.md](../../../references/README.md#word-study--original-language-tools).
- For a term that's load-bearing or contested (not every word needs this), work it through the fuller diachronic → synchronic → conclusion method in [word-study-method.md](word-study-method.md) rather than stopping at a bare gloss.
- **Before writing "the text says X" about an English word, check what X is translating.** `bible_interlinear <book> <ch> <v>` (or `query.py interlinear`) gives unfoldingWord ULT's word-level alignment to the Hebrew and Greek — the only link in this database between an English word and the original it renders, and the cheapest guard there is against building a point on a translator's choice. Two things to hold: the mapping is many-to-many by nature (Genesis 1:1's "the heavens" renders both אֵת and הַשָּׁמַיִם, since the object marker has no English of its own), and the Greek side is the UGNT, which differs from this project's default SBLGNT in roughly one verse in six — at John 1:34 it reads υἱός where SBLGNT has ἐκλεκτός, so confirm wording with `bible_verse` before resting a New Testament argument on it.
- Grammar/syntax points that affect meaning, only where they actually change the reading — don't pad with grammar for its own sake.
  - **Look grammar up rather than recalling it.** `bible_grammar <term>` searches the unfoldingWord Hebrew Grammar — 88 articles on what a *form* does as against what a word means: gentilic adjectives, the dual, construct chains, the cohortative. The lexicons here answer the second question; nothing answered the first until 2026-09-05, so grammar claims came from memory, which is the habit this skill exists to replace.
  - You can query this rather than eyeball it: `query.py syntax <book> <ch> <v>` (or the `bible_syntax` MCP tool) gives clause role (subject/object/indirect object), Hebrew construct state and verb conjugation (qatal/wayyiqtol/yiqtol), and resolved coreference — including **implicit subjects**, where the verb's subject sits verses earlier with no noun in between, and pronouns whose antecedent is annotated. Use it when the argument turns on who is acting on whom rather than on one word's meaning. Coverage is partial and a null means "not annotated," never "no such role" — see [references/README.md](../../../references/README.md#clause-syntax-and-coreference-macula).
- Apply the genre-specific lens:

  | Genre | Ask especially |
  |---|---|
  | Epistles | What problem/question in the original church occasioned this paragraph? Which claims does the author himself mark as universal ("in all the churches") vs local practice? |
  | OT narrative | Narrative *records* what happened, not necessarily what should happen — does the narrator (or the rest of Scripture) evaluate this as good or bad, or is that left implicit? Is this illustrating a principle taught explicitly elsewhere, or are you about to invent a new one from a character's behavior? |
  | Acts / historical precedent | Was this narrative's *intent* to establish a pattern, or is the detail incidental to a different primary point? A repeatable pattern is not automatically a binding norm for every believer. |
  | Gospels | Which Gospel, and what is that author's distinct emphasis/audience? Read it on its own terms before harmonizing with the others. Where does this sit on the kingdom's "already/not yet" horizon? |
  | Parables | What is the one (or few) main point the original hearers would have grasped? Who is Jesus needling — what's the provoking situation? Resist allegorizing incidental details. |
  | Law | Moral, civil, or ceremonial? What does the statute reveal about God's character even where the specific rule doesn't carry over under the New Covenant? |
  | Prophets | Read as covenant enforcement (blessing for faithfulness, judgment for breach) in the prophet's own historical setting *first*, before reading forward. |
  | Psalms | What type (lament, praise, thanksgiving, royal, wisdom, imprecatory)? A psalm is often prayer addressed to God, not a proposition addressed to us — let form shape expectation. |
  | Wisdom | Proverbs are generally-true observations, not unconditional promises. Hold Proverbs' hopeful realism against Job/Ecclesiastes' honest counterpoint rather than flattening one against the other. |
  | Revelation / apocalyptic | Identify the Old Testament imagery being drawn on before assigning a novel modern referent. Remember the original pastoral purpose to seven real churches sits alongside the future-oriented vision. Per AGENTS.md, lean dispensational here, but only after the imagery is grounded historically — don't skip straight to a end-times reading. |

## Phase 5 — Hermeneutics: then-and-now bridge

Only now, cross to application:

- What in this passage is tied to a particular historical/cultural circumstance, and what transcends it? (The classic test case: head coverings vs. the underlying principle of order/respect.)
- State the theological principle the text teaches or illustrates — in one or two sentences, in your own words.
- Cross-check: does this principle already appear taught explicitly elsewhere in Scripture? Don't build doctrine on an obscure narrative detail or an incidental remark alone — narratives illustrate, they rarely establish doctrine by themselves.
- **Where the principle just stated intersects a position documented in [statement-of-faith.md](../../../docs/content/about/statement-of-faith.md), check it's consistent — but only now, after the principle above is already derived, never earlier.** Most studies won't intersect it at all; the statement covers core doctrine, not every debated secondary topic, and silence is the normal case, not a gap to fill. This is a flag, not a filter: if the two genuinely conflict, say so to the user rather than quietly softening the conclusion to fit, or quietly leaving the conflict unmentioned. A real conflict is more likely a sign to revisit the exegesis above with fresh eyes than to distrust a settled, Scripture-derived conviction — but that judgment call belongs to the user, not to a silent edit either direction.
- Draft the contemporary application. Keep it distinguishable from the exegesis above — a reader should be able to tell what the text *said* from what you're *applying*.

## Phase 6 — Cross-reference & verify

- Gather cross-references with `bible_trace` (or `query.py trace <book> <ch> <v>`) — what this verse quotes, what quotes it, what it echoes, each carrying the method that established it and **the words the two verses actually share**. Treasury of Scripture Knowledge and the other inherited lists remain useful and are folded in as the tool's `leads` tier.
  - **Weigh the tiers as the tool labels them; never merge them.** A quotation in Greek (`quotation-greek`) or within the Hebrew Old Testament (`inner-biblical`) is a textual fact — both sides are the same language, so the quotation is literally the same words. `allusion-lemma` is shared rare vocabulary with no shared phrasing. `quotation-hebrew` is a 19th-century Hebraist's judgement rendered into Hebrew, so verify it in Greek before it carries any weight. `leads` are inherited cross-references: worth chasing, not evidence.
  - **`corroborated: false` on a strong link is the interesting case, not a weak one.** It means the connection is in the text and no reference list carries it — roughly one strong quotation in five. Those are the ones worth a sentence in the study.
  - **Silence means the method found nothing, not that there is nothing.** It finds quotation and vocabulary-level allusion, not paraphrase. Matthew 26:64 is the standing example: the Sanhedrin heard Psalm 110:1 and Daniel 7:13 and the high priest tore his robes, but Matthew paraphrases until barely three words survive intact, so only the `leads` tier carries it. When the tool is quiet and the connection still seems real, say so in your own words and cite the passage directly.
  - Run `bible_variants` on any Old Testament verse the study leans on, especially one a New Testament writer quotes — it reports where a Dead Sea Scroll reads something the Masoretic does not. Always quote its `extant_words` alongside: Deuteronomy 32:8's "sons of God" is legible but only two words of that verse survive, and a study should say so rather than cite it flat.
- Compare across the translations AGENTS.md specifies (Masoretic/LXX, ESV default, plus NLT/WEB/NASB/NIV as useful) and note where they diverge meaningfully.
  - **Ask which translation, if any, preserves the feature you found in the original — but only in that order.** Establish the sense from the Hebrew/Greek first; *then* check which English versions keep it visible. This is useful to a reader who doesn't read the original languages: telling them "the ESV shows this, the WEB doesn't" hands them something they can act on, and it's often the most practical fruit of a word study.
  - **The order is the whole guardrail, because run backwards this becomes translation-shopping** — scanning versions for the rendering that flatters a reading you already like, then citing that version as though it were evidence. It isn't; it's a witness to a translator's decision. If you notice yourself preferring a translation *because it agrees with you*, stop and go back to the text. The claim must stand on the Hebrew/Greek and be stated that way, with translations reported as observations about translations.
  - Corollary: **comparison never silently changes the study's base translation.** ESV remains the default for quotation per AGENTS.md even where another version renders a particular word better; if a different one is quoted for a specific purpose, say which and why, right there (AGENTS.md already requires naming the translation of every quote).
  - Expect the honest result to be mixed rather than a winner. A single version rarely preserves everything: in the Bread of Life study, the ESV keeps John's *esthiō*→*trōgō* shift at all four verses while losing the *menō* thread linking 6:27 to 6:56, and the ASV does exactly the reverse — which is a more useful thing to tell a reader ("read a second, more literal version alongside; expect each to be strong in different places") than crowning one translation.
  - Worth checking whenever a word is doing structural work: a deliberate mid-passage switch, a repetition that ties distant verses together, a rare or contested term, or a distinction the original marks and English tends to collapse (as English does with *kophinos*/*spyris*, both "basket"). Wooden-literal versions (ASV, YLT) are the likeliest to preserve such things and the least pleasant to read — which is the trade being made. All of ASV, YLT, WEB and BSB are queryable in `bible-text.db`; ESV/NIV/NKJV/CSB are in `study-notes.db` (see the commentary bullet below).
  - **YLT and NKJV stay comparison tools only** — AGENTS.md's "Biblical scholar principles" gives the full Fee & Stuart rationale. The structural-comparison use above is the legitimate one; neither gets quoted as a verse's meaning in a study's prose.
- **Consult commentaries last**, not first — use them to check your reading, not to form it. Cite any extra-biblical source used, per AGENTS.md.
  - You have real commentaries to consult, so do consult them: `study-notes.db` holds the ESV Study Bible, both Cultural Backgrounds Study Bibles, the NIV Biblical Theology Study Bible and the CSB Ancient Faith Study Bible — notes, book introductions, topical articles, and each edition's own verse text. Access pattern and the mandatory `immutable=1` URI form: [references/README.md](../../../references/README.md#study-notesdb-commercial-study-bible-commentary-external-not-in-this-repo-at-all). Query it with a `verse_start<=N AND verse_end>=N` window rather than an exact-verse match, since notes are attached to ranges.
  - **`note_type` splits that table into two different kinds of evidence, and the second is the underused one.** A `study_note` is the editors' commentary — a scholar's argued view, weighable against other scholars. A `footnote` is the translation committee's own record of a decision: *"Or X"*, *"Lit Y"*, *"Some mss omit Z"*. That is much closer to primary evidence — the translators telling you where the text is genuinely ambiguous, that they made a judgement call, and what the alternative was. **Pull `note_type='footnote'` for the passage as a matter of course, alongside the study notes — not only when something already looks contested.** They are worth reading wherever they exist: alternate renderings, wooden-literal glosses, manuscript variants, measurement and currency conversions, and notes on where a NT quotation departs from the OT it cites. Much of that is invisible in the running text and will not announce itself as a problem to go looking for; you find out the text was ambiguous *because* the footnote says so. The payoff is largest when a word is doing theological work, two translations diverge, or a variant is in play — there the footnote often names the divergence outright and saves reconstructing it from a lexicon and six parallel versions — but the habit is to read them, not to reach for them only after a difficulty surfaces. Song of Songs 8:6 is the standing example: the fork over whether <span dir="rtl">שַׁלְהֶבֶתְיָה</span> ends in the divine name or a superlative was worked out the long way, while the LSB's own footnotes at that verse state both options — "Or *A vehement flame*" and "The shortened form of Yahweh, found in poetry and praise (e.g. Hallelu*jah*)". The footnote corpus is now ~22,000 entries and the LSB supplies two-thirds of them.
  - Expect this step to *change* something. If commentaries confirm every single thing you already wrote and add nothing, you have probably skimmed them for agreement rather than read them for correction. Note explicitly in `resources_consulted` what each one confirmed versus contributed.
- Record every source touched in `resources_consulted` on the state file, with enough detail (author, work, translation) to reconstruct the citation later.

## Phase 7 — Draft

- Write the file per [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) frontmatter schema (`title`, `category`, `description`, `tags`, `draft: true`, `bible_references`), into the section chosen from [placement-and-tags.md](placement-and-tags.md).
- **Fill every placeholder** — that file's "Frontmatter failures worth checking" lists the five template values that once shipped intact on a published page, and why `zadok_year`/`gregorian_year` reach the timeline even on a draft.
- **Don't hand-write the provenance fields** (`date_created`, `date_modified`, `ai_provider_models`). Run `python3 utils/refresh_frontmatter_provenance.py` from the repo root **before committing**, and stage its edit alongside the study — it derives all three from git history, and running it after the commit instead can't converge. See "The provenance fields" in [placement-and-tags.md](placement-and-tags.md).
- **Always populate `primary_passage` and `bible_references`.** `references/build/commentary_index.py` reads these to auto-generate the "studies referencing this chapter" cross-links inside `docs/content/commentaries/<book>/`, keyed off exactly the passage(s) this study is centrally about (`primary_passage`, singular or `;`-separated for a multi-account passage like a Gospel parallel) versus what it merely cites in passing (`bible_references`). A study missing both is invisible to that index, not an error, but it means the cross-reference system silently under-reports — don't skip this field the way many of the pre-existing studies did.
- Structure: short hook → **Key Takeaways** → historical/literary context → walk-through with original-language notes → theological principle → discussion questions → **References & Recommended Reading**.
- **Key Takeaways** replaces the old flat "Key lessons" list with up to five subheadings **in this order**, each included only where the study earns it — don't force one to fill a slot. Rationale: [key-takeaways.md](../../../docs/content/about/key-takeaways.md). The section comes up front, before supporting detail — a reader should get the point even if they read no further.

  | Subheading | What goes in it |
  |---|---|
  | **Types & Prophecy** | Two distinct things, kept apart rather than blended. A **type** is an OT person/object/ritual patterning Christ or the gospel by *resemblance* (τύπος, e.g. Melchizedek); a **prophecy** is a direct verbal prediction the passage makes or fulfills (e.g. Psalm 110:4's sworn oracle). A study may have one, both, or neither. |
  | **Lessons about Jesus** | The direct Christological conclusions the exegesis established. |
  | **Memory verses** | 1–3 verses *already quoted and cited in the study's own body*, pointed back to — not new quotations introduced here. |
  | **Be Transformed** | Romans 12:2 made concrete: specific thoughts, attitudes, actions the study calls the reader to examine or change. Keep it as distinguishable from the exegesis as Phase 5 already requires. |
  | **Prayer** (last, deliberately) | A short response specific to this study's content, structured the way the Lord's Prayer study shows Jesus's model working — relationship and God's character first, request second. Not a generic devotional line. |
- Always give the translation used for any quotation (AGENTS.md). This applies per-quote, not just
  once for the study as a whole: when a lookup tool returns text, check which `work_id`/translation
  it actually came from before dropping it into prose, rather than assuming it's ESV because ESV is
  the site default. **Quoting WEB, ASV, or another named translation instead of ESV is a legitimate,
  deliberate choice** — WEB's "keep his charge" or ASV's more construct-visible phrasing can
  genuinely preserve something ESV's smoother rendering loses, the same way Phase 6's translation-
  comparison step already treats this as a feature, not a defect. The failure mode isn't using a
  different translation — it's doing so *silently*, so a paragraph reads as if it's continuing the
  study's stated-default ESV quotations when it's actually drifted to a different one word-for-word.
  Label every quote that isn't ESV, right where it appears (`(Genesis 8:20, WEB)`), not only in the
  References section's summary. A review-bible-study pass caught exactly this drift, uncaught
  across a whole section, in an earlier study on this site — see that skill's own findings format
  for what an unlabeled translation switch looks like once someone goes checking.
- **Scripture quote block format** (standardized across the site — see e.g. [as-the-snake-was-lifted.md](../../../docs/content/jesus/as-the-snake-was-lifted.md) or [bread-of-life-feeding-the-multitudes.md](../../../docs/content/jesus/bread-of-life-feeding-the-multitudes.md) as the reference examples). Any block quote of Bible text — not a short inline citation woven into a sentence — follows this exact shape:
  ```
  > ✝️ Book Chapter:Verse-Verse (TRANSLATION)
  >
  > N Verse text starts here, with each verse's number inlined into the
  > flowing prose (not one verse per line, not a separate list) N+1 continuing
  > straight into the next verse's text the same way.
  ```
  The `✝️ Reference (TRANSLATION)` line comes **first**, not after the quote — this is the one thing that most needs fixing when older drafts get it backwards (reference-after-with-an-em-dash is the wrong shape now, even for a single verse). Verse numbers are included even for a single-verse quote (`> ✝️ Psalm 110:4 (ESV)` / `> 4 The LORD has sworn...`). Multi-verse quotes stay in one continuous blockquote, numbers inlined, not split into separate quote blocks per verse. `validate-content.js` checks for this shape — see Phase 8.
- **Any mermaid diagram gets a width check — see [diagrams.md](diagrams.md).** The content column is ~560px, and mermaid scales an oversized diagram down whole, labels included, with no wrapping and no scrollbar to warn you. Seven `flowchart LR` nodes in a rank is 1769px, which renders its 16px text at 5px. Three columns is the ceiling; fold a longer chain into `subgraph` stages with `direction TB`. Shortening the labels does not work — the ~230px per column is padding, not text. Twelve diagrams on the site rendered under 50% before they were all rewritten on 2026-09-04, so this is the default outcome rather than an edge case — and since `validate-content.js` cannot measure width without a browser, this check is the only thing keeping the corpus clean.
- **Write toward [style-guide.md](style-guide.md)'s "Write toward this" section from the first draft, and re-run the whole guide after every substantive revision — not only before flipping `draft: false`.** The four positive rules there (every sentence adds a fact, a citation or a step; name the actor and show the mechanism; lead with the fact; let the citation carry the emphasis) prevent the whole class of AI-register tics; the diagnostic half of that page only catches instances after the event. **Revision is where the register is produced, not first drafting** — on `last-things/day-is-a-thousand-years.md` four narrated-argument constructions were cut in one pass and three more appeared in the next two revisions of the same paragraphs, written within the hour by the same agent that had just removed them. A green `npm run validate` is not evidence this pass happened: its four style checks cover `worth ___`, the "rather than" virtue contrast, bullet length and reader-reassurance, and nothing else on that page.
- If Phase 6's translation comparison turned up something a reader could act on, give it a short section of its own rather than burying it in a word study — but only where it earned one. "No English version preserves X, here's what you'd miss" is worth a reader's time; a table of trivial wording differences is padding.
- **Every study ends with a References & Recommended Reading section.** This is the reader-facing bibliography — distinct from the state file's `resources_consulted`, which is the working research trail. List every lexicon, commentary, dictionary, or background source actually drawn on, restricted/copyrighted ones included by name (e.g. TWOT, Cultural Backgrounds Study Bible, Fee & Stuart) — a citable work referenced with attribution and a reasonably-scoped quotation is a normal, fine thing to do in a public document; it isn't something to work around or leave unstated. What copyright actually constrains is quoting *too much* of one source (a full paragraph or note, not a sentence) or failing to attribute — not whether a restricted source can be named or cited at all. See [references/README.md](../../../references/README.md) for the tier-by-tier detail on what's safe to quote how.
- **Copyright guardrail.** There are *two* different permissions in play and they are not the same, so don't apply one rule to both:
  - **Bible text** is covered by each publisher's own stated allowance, which is generous enough that no study will approach the verse count. **The limit that actually binds is the percentage, not the verse count** — a short study that is mostly block-quoted Scripture with a little commentary around it can breach it at a couple of dozen verses. If a study is tripping this, it is usually too thin on its own contribution as well; fix that, not the quota. NASB is the exception with no blanket allowance at all — don't assume one.
  - **Commentary, study notes, introductions, articles, charts, maps** are separately copyrighted with **no blanket allowance** — the ESV Study Bible's own notice reserves all rights. Here "a sentence or two, always attributed" is the whole of what's available, and it applies to the locally-extracted Fee reference and the study-Bible notes in `study-notes.db` alike. Synthesize in your own words; never paste a full note or paragraph into a committed file.
  - **Attribution is a licence condition, not a courtesy.** Naming the translation inline satisfies scholarly convention but is *not* the copyright notice ESV/NIV/NKJV/CSB require. Those live on [docs/content/about/copyright.md](../../../docs/content/about/copyright.md) — if a study introduces a translation or major source not already listed there, add it in the same commit.
  - **Look the thresholds up, don't recall them** — they differ per publisher and are easy to misremember: [references/README.md](../../../references/README.md#two-different-permissions-dont-conflate-them).
  - None of this is a reason to avoid citing a source. A restricted work named with attribution and quoted at reasonable length is normal scholarship; what copyright constrains is *how much*, not *whether*.

## Phase 8 — Validate & review

- Run `npm run validate` (see [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md)) against the new file.
- Run `mkdocs build --strict` — it is the only check that resolves every internal link, and it fails
  the build on a broken one. `npm run validate` does not check links.

  ```bash
  uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin \
      --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects \
      mkdocs build --strict --site-dir /tmp/mkcheck
  ```

  Two things `--strict` cannot see, so check them by eye: links to `/timeline/` or `/genealogy/`
  (they point outside `docs_dir` to the Astro-served tools, so a wrong `../` depth fails silently),
  and image paths, which move with the file the same way links do.
- Re-run the index generators, from `references/build/`:
  `uv run python commentary_index.py` (picks up the new `primary_passage`/`bible_references`) and
  `uv run python section_index.py` (adds the study's card to its section landing page). Both skip
  `draft: true` files, so run them **after** flipping the draft flag, not before.
- This phase is a light self-check by the same agent who drafted the file — good for catching structural
  and frontmatter mistakes, not a substitute for an independent check. For a critical, adversarial audit
  (scripture re-verified against source, citations spot-checked, word studies re-derived, claims checked
  against a commentary not already cited, context coverage per how-to-read-the-bible.md, a style-guide
  pass), use the sibling **review-bible-study** skill before flipping `draft: false` on anything
  load-bearing.
- Once the user has reviewed it, flip `draft: false`.
- Mark the state file `status: published` — don't delete it; it's the record of how the conclusions were reached.

## State tracking

Every study-in-progress gets one structured-data file at `references/study-state/<slug>.yml`, copied from [study-state.template.yml](study-state.template.yml). It exists so a study can be resumed in a later session (or by a different agent) without re-deriving context, and so the exegesis trail — what was checked, what's still open — is never silently lost.

Update the relevant `stages.*` block and bump `last_updated` as each phase above completes. `open_questions` is for anything you're consciously deferring (a textual variant you didn't chase down, a cross-reference you couldn't confirm) — don't let it go silently unmentioned in the final draft's own notes.

**The state file is a record, not a verification.** It holds what you concluded, not proof the conclusion was right — and a wrong conclusion gets written into it with exactly the same confidence as a right one, usually *before* it reaches the draft. That makes checking a claim against your own notes worse than useless: the trail confirms the error instead of catching it, and does so in your own handwriting. This is not hypothetical — a `MAIN FINDING` block in one study's state file carried a bad citation into the published prose, and the error survived a self-check that consisted of re-reading. Anything load-bearing gets **re-queried from source**, never re-read from here. That is also why review-bible-study's Phase 3 says *re-derive, don't re-read*: it is the same rule pointed at a file someone has already finished.

## Companion files

- [placement-and-tags.md](placement-and-tags.md) — section taxonomy, tag facets, frontmatter traps (read before drafting)
- [word-study-method.md](word-study-method.md) — the fuller diachronic → synchronic → conclusion procedure (Phase 4)
- [style-guide.md](style-guide.md) — the prose pass (Phase 7)
- [diagrams.md](diagrams.md) — the mermaid width budget and the stage-folding pattern (Phase 7)
- [study-state.template.yml](study-state.template.yml) — state file schema

Source catalog and licence tiers: [references/README.md](../../../references/README.md), as AGENTS.md directs.

**Before concluding a text is unavailable, check the disk, not just the catalog.** The catalog can
lag what is actually checked out, and when it does, "not in this repo" is a confident wrong answer:
a study went to press asserting Tobit was unavailable while Tobit sat in
`references/open-data/scrollmapper-bible-databases-deuterocanonical/sources/en/book-of-tobit/`. Two
habits prevent it. Run `python3 references/check_sources.py` (from the repo root) — its **raw-only**
list is exactly the set of sources present on disk that `query.py` and the MCP tools *cannot* see,
so a `bible_verse` miss proves nothing about them. And remember `build.py` ingests six of the
open-data submodules and skips the rest; deuterocanonical and apocryphal books are skipped by
design, so they must be read as raw `sources/<lang>/<book>/` files.

**External material resolves through `$BIBLE_MEDIA_ROOT`**, not a hardcoded path — `study-notes.db`,
the patristics corpus and the TWOT scans all live there. Use `references/build/media_root.py` rather
than writing a `/Volumes/...` path into anything, and expect the volume to be unmounted sometimes;
say so plainly in the state file when it is, rather than quietly skipping verification. Prefer the `bible-references` MCP tools (`bible_word`, `bible_verse`, `bible_passage`, `bible_trace`, `bible_links`, `bible_variants`, `bible_parallel`, `bible_align`, `twot_root`, …) over shelling out to `query.py`/`twot_lookup.py` — same data, no text-parse round trip; the CLI is the fallback when the server isn't connected.

**A reference is not a universal address, and getting this wrong is silent.** Hebrew Joel 3:1 is English Joel 2:28 — the verse Acts 2 quotes. LXX Psalm 22 is English Psalm 23. The Masoretic and English traditions divide Daniel, Joel and Malachi differently, and the Septuagint renumbers nearly the whole psalter. Ask for a verse in one work's numbering and read it in another's and you get an unrelated verse with no error. `bible_verse` and `bible_passage` handle this internally, but a query you compose yourself does not: use `bible_parallel` to move a reference between two named works, or `bible_align` to see it as each scheme numbers it. Never assume `(book, chapter, verse)` carries across.
