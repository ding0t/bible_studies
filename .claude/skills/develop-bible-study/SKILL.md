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
- **Find what this site has already written on the passage.** For the primary passage's chapter
  (and any supporting chapter the study will lean on), list the existing studies:

  ```bash
  cd references/build
  uv run python cross_study_claims.py "John 4" --exclude <section>/<slug>.md
  ```

  `passage_brief` returns the same list as `existing_studies`, with `overlaps_passage` set when a
  study's own references cover the verses. Each study has a `role`: **primary** (the chapter is its
  `primary_passage`), **cited** (in its `bible_references`) or **prose** (named only in its prose,
  because older studies left the frontmatter empty). Record them in the state file's
  `sibling_studies`, each with a `use`:

  - `link` — it already covers ground this study needs; plan to point to it in one sentence
    instead of re-arguing it.
  - `build-on` — this study takes its conclusion further; plan to say so and link it.
  - `enrich` — this study is likely to find something that one lacks; revisit after drafting.
  - `none` — a passing mention only.

  This step records what other studies cover. It does not adopt their conclusions. Exegesis in
  Phases 2-5 still runs on the text, uncoerced, and Phase 6 is where the two get compared. A
  primary sibling on the same verses also raises a scope question for the author before research
  starts: is this a new study, or a revision of that one?

## Phase 2 — Exegesis: historical context

- Author, audience, date, and the historical/cultural occasion — what circumstance called this text into being?
- Geographic, political, or customary background relevant to understanding it (a denarius as a day's wage, the shape of a first-century cross, etc.) — these are exactly the kind of "cultural context" AGENTS.md asks for.
- **Settle who and where before writing a name.** `bible_names` (or `query.py names <name>`; `passage_brief` returns it as `names`) gives every *individual* the name can mean — "Zechariah" is 29 people — with parents, spouses, children, tribe and every verse naming them, from STEP's TIPNR. A family link marked (a), (d), (f) or (?) is an ancestor, a descendant people, a founder, or STEP's judgment on an ambiguous text: state it with that confidence, not flat. A place carries OpenBible's best modern identification with a score out of 1000 and the alternatives; a low score or a close runner-up means the site is disputed (Emmaus: six candidates, the best at 338), so say "probably" or name the rivals rather than the site.
- Where useful, cite a Bible dictionary or reputable background source — record it in `resources_consulted`.

## Phase 3 — Exegesis: literary context

- Where does this passage sit in the book's argument or story? What comes immediately before and after, and why does the author move from one to the other?
- Identify the unit of thought (paragraph for prose, strophe/section for poetry) — don't exegete a verse in isolation from its paragraph.
  - `bible_section` (or `query.py section`; `passage_brief` returns it as `structure`) gives the BSB's section the passage sits in and the passages its translators mark as parallel: Matthew 6:9 sits in "The Lord's Prayer" (6:5-15), parallel Luke 11:1-4. Use it as a first map and test it against your own reading of the unit, since the headings are editorial and the unit is your call. **Never quote a heading as though it were the text.**
  - **A parallel account is part of the literary context.** For a gospel passage, anything in Samuel–Kings–Chronicles, or a psalm with a historical title, read each parallel `bible_section` names in its own setting first, then ask what each writer does with the shared material. Blending them before that erases the differences that are often the point.
  - `bible_section` also carries STEP Bible's harmony of the gospels and OT parallels (work `step-lists`), and `bible_lists` (in `passage_brief` as `structure.lists`) adds the OT text an NT verse quotes, a name of God first used there, and a letter's part (salutation, thanksgiving, body). Where a study will argue from the ESV's wording, `study_esv_tags` shows which Hebrew or Greek word each English word renders: Genesis 16:13's "seeing" and "looks" are one word, *ro'i*. Both are editorial maps; the text decides.
- The governing question, asked of every unit: **"What's the point?"** — trace the author's own train of thought rather than importing one.

## Phase 4 — Exegesis: content, words, and genre lens

- Word studies: identify key theological or ambiguous terms, get the underlying Hebrew/Aramaic/Greek, gloss, and English pronunciation (per AGENTS.md). Use the Strong's/lexicon resources in [references/README.md](../../../references/README.md#word-study--original-language-tools).
- For a term that's load-bearing or contested (not every word needs this), work it through the fuller diachronic → synchronic → conclusion method in [word-study-method.md](word-study-method.md) rather than stopping at a bare gloss.
- **Before writing "the text says X" about an English word, check what X is translating.** `bible_interlinear` gives the ULT's word-level alignment and `interlinear="bsb"` the Berean Interlinear's (`passage_brief` returns both). They are independent committees: where they agree, the rendering does not hang on one; where they differ, that difference is worth a sentence. `bible_alignment_diff` lists exactly those words for a passage (Romans 3:25's ἱλαστήριον is "a propitiation" in the ULT and an "atoning sacrifice" in the BSB), and `passage_brief` returns it under `words.alignment_differences`; a difference is a lead to weigh, never a verdict. [docs/dev/alignment-disagreements.md](../../../docs/dev/alignment-disagreements.md) ranks the words the two disagree on most across the canon; if a study's key word is on it, say which rendering the study follows and why. The mapping is many-to-many (Genesis 1:1's "the heavens" renders both אֵת and הַשָּׁמַיִם). The ULT's Greek is the UGNT, not this project's default SBLGNT; they rarely differ by more than spelling, but do at Mark 16:8ff, the pericope adulterae, Luke 23:34 and John 1:34 (υἱός against ἐκλεκτός), so confirm with `bible_verse` which text a reading came from before resting a New Testament argument on its wording.
- Grammar/syntax points that affect meaning, only where they actually change the reading — don't pad with grammar for its own sake.
  - **Check a figure of speech against a second reader.** `bible_translation_notes <book> <ch> <v>` returns unfoldingWord's phrase-level notes (metaphor, metonymy, idiom, implied subject, passive voice), each quoting the original phrase. Use it after the exegesis, to see whether an editor reads a figure as you do. It checks a reading and never supplies one, and a verse with no note says nothing (CC BY-SA: quote briefly with attribution).
  - **Look grammar up rather than recalling it.** `bible_grammar <term>` searches the unfoldingWord Hebrew Grammar (88 articles on what a *form* does: gentilic adjectives, the dual, construct chains, the cohortative) and Greek Grammar (94: case endings and their paradigms, tense, voice, mood, the article); pass `language` to limit it. The tense articles state one view of aspect, which is debated, so mark it contested where an argument rests on it.
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

Each step's method, with the corpus examples behind it, is in [cross-references.md](cross-references.md).
Read it before this phase. The rules:

- **Gather cross-references with `bible_trace`** (or `query.py trace <book> <ch> <v>`): what the verse
  quotes, what quotes it and what it echoes, each with its method and the words the two verses share.
  **Weigh the tiers as the tool labels them and never merge them.** A strong link marked
  `corroborated: false` is the one worth a sentence; silence means the method found nothing, which
  is different from there being nothing.
- **Run `bible_variants` on any Old Testament verse the study leans on** and quote its
  `extant_words` with it. For a New Testament variant, read the translators' footnotes that
  `bible_verse` returns.
- **Settle every parallel account `review_gaps` reports**, in Phase 3 where you can: an unmentioned
  parallel is the omission a reader most often catches.
- **Compare translations only after the Hebrew or Greek has settled the sense.** Run the other way
  it is translation-shopping. The comparison never changes the study's base translation, and the
  honest result is usually mixed.
- **Consult commentaries last, to check the reading.** Read the translators' footnotes as a matter
  of course. No step of the argument rests on a study note alone, and a reading is contested only
  when the text gives reasons on both sides. Expect this step to change something.
- Record every source touched in `resources_consulted` on the state file, with enough detail (author, work, translation) to reconstruct the citation later.

### Check the study against its siblings, not only against sources

Run `cross_study_claims.py "<chapter>"` for each chapter in `sibling_studies`, and for any chapter
the research has added since. The method, the three questions to ask of each sibling and the
corpus failures behind them are in
[review-bible-study Phase 6](../review-bible-study/SKILL.md#check-the-study-against-its-siblings-not-only-against-sources).
Where two studies disagree, which one to fix is the author's call.

## Phase 7 — Draft

**Before writing any prose, say what the study is trying to say.** Put three things in the state
file:

1. `thesis`: the point in one sentence. It becomes the **In one sentence:** line.
2. `outline`: one line per planned section, saying what that section says. Every line must serve
   the thesis. That makes the outline the reader's mind map, and the page's Study outline when it
   needs one.
3. `word_budget`: 4,000 unless there's a reason to change it, and if there is, write the reason
   down.

Research that doesn't serve the thesis is a separate study. Write it down in `open_questions` as a
fork candidate and leave it out of this draft. Show the thesis and outline to the author before
drafting; changing them costs a minute at this point and a rewrite later.

- Write the file per [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) frontmatter schema (`title`, `category`, `description`, `tags`, `draft: true`, `bible_references`), into the section chosen from [placement-and-tags.md](placement-and-tags.md).
- **Fill every placeholder** — that file's "Frontmatter failures worth checking" lists the five template values that once shipped intact on a published page, and why `zadok_year`/`gregorian_year` reach the timeline even on a draft.
- **Don't hand-write the provenance fields** (`date_created`, `date_modified`, `ai_provider_models`). Run `python3 utils/refresh_frontmatter_provenance.py` from the repo root **before committing**, and stage its edit alongside the study — it derives all three from git history, and running it after the commit instead can't converge. See "The provenance fields" in [placement-and-tags.md](placement-and-tags.md).
- **Link to sibling studies instead of re-arguing them.** For each `sibling_studies` entry marked
  `link` or `build-on`, give the point a sentence and a relative link to that study, and spend the
  words on what this study adds. Never link a `draft: true` sibling from a page that will be
  published: the link ships as a 404 (validator Check 24).
- **Always populate `primary_passage` (what the study is centrally about; `;`-separated for a gospel parallel) and `bible_references` (what it cites in passing).** `commentary_index.py` builds the chapter pages' "studies referencing this chapter" lists from them, and a study with neither silently drops out.
- Structure: short hook → **Key Takeaways** → historical/literary context → walk-through with original-language notes → theological principle → discussion questions → an optional `## Annex:` → **References & Recommended Reading**.
- **A long study earns two more sections** ([structural-readability.md](../read-bible-study/structural-readability.md) rules 10-11): at 2,500+ words and 6+ `##` sections, a **Study outline** straight after Key Takeaways, with descriptive annotations only; and apparatus (source-weighting, correctives) in one `## Annex:` after Discussion questions and before References.
- **When the draft is finished, hand it to the read-bible-study skill**, in a different session where you can: judging the composition order as a reader is the one thing its author cannot do. Validator Check 21 catches only a 600-word unbroken run, so passing it is not evidence the pass was done.
- **Key Takeaways** has up to five subheadings **in this order**, each included only where the study earns it — don't force one to fill a slot. Rationale: [key-takeaways.md](../../../docs/content/about/key-takeaways.md). The section comes up front, before supporting detail — a reader should get the point even if they read no further.

  | Subheading | What goes in it |
  |---|---|
  | **Types & Prophecy** | Two distinct things, kept apart rather than blended. A **type** is an OT person/object/ritual/event patterning Christ, the gospel, or God's dealings with His people under it (1 Corinthians 10:6, 11; e.g. Lot's rescue patterning the church's) by *resemblance* (τύπος, e.g. Melchizedek); a **prophecy** is a direct verbal prediction the passage makes or fulfills (e.g. Psalm 110:4's sworn oracle). A study may have one, both, or neither. |
  | **Lessons about Jesus** | The direct Christological conclusions the exegesis established. |
  | **Memory verses** | 1–3 verses *already quoted and cited in the study's own body*, pointed back to — not new quotations introduced here. Block-quote shape with the reference written plainly (no link: every reference on the site opens the verse in a pop-up), no explanatory sentence after the verse. A bare "See [section]" locator is fine in a study with several parallel sections; an interpretive sentence is not — it belongs in Lessons about Jesus or the walk-through instead. |
  | **Be Transformed** | Romans 12:2 made concrete, as three labeled bullets — `**Think.**` (a thought or belief to correct), `**Attitude.**` (a posture to adopt), `**Do.**` (an action to take), each naming in parentheses the verse it stands on, from the study's own passages, so a reader of the printed sheet can open their Bible where the application comes from. This is the default shape, not one option among several; a different shape is a deliberate choice for a study whose application genuinely won't split three ways, not a fallback for when the three bullets are more work than a paragraph. Keep it as distinguishable from the exegesis as Phase 5 already requires. What makes each bullet good, and where the Do comes from (the passage's own command, prayer or model, done this week): [be-transformed.md](be-transformed.md). |
  | **Prayer** (last, deliberately) | A short response specific to this study's content, structured the way the Lord's Prayer study shows Jesus's model working — relationship and God's character first, request second. Not a generic devotional line. |
- **When you hand a draft back, hand back [human-review.md](human-review.md) with it.** Three things
  survive every automated pass — the antithesis construction, essay register in the applying
  sections, and writing around the theology instead of naming it. All three were found by the site's
  author correcting a study by hand after it had passed two adversarial reviews and a clean
  validate. Say which of the three you think the draft is weakest on.
- **Discussion questions cover a set of facets — see [discussion-questions.md](discussion-questions.md).**
  The set mirrors Key Takeaways: language, the text in its context, type/prophecy/Christ, the hard
  part, and one that lands on the reader personally. Include only the facets the study earned. That
  file also carries the rules, each from a specimen in this corpus, and the failure mode specific to
  this section: **question sets go stale silently after a restructure**, because each question stays
  individually defensible while the set stops matching the study.
- **Format the text by [formatting.md](formatting.md)**: label every quotation's translation where
  it appears; Scripture block quotes open `> ✝️ Reference (TRANSLATION)`; references are plain
  text, never linked, and always name their book; quote what the argument stands on and cite what
  it only points to; word studies in the shape `ἀρραβών (*arrabōn*, G728)`.
- **Propose a drawn graphic wherever prose carries something badly — see [drawn-graphics.md](drawn-graphics.md).** Four kinds: *sequence* (when: Larkin's dispensational charts), *relationship* (how things fit together), *pattern* (an object or place drawn to the text's measures, after Exodus 25:40) and *imagery* (a vividly described scene, dramatised, with every detail numbered against its verse). Pick the kind first; each has its own rules, and all four mark stated against inferred on the graphic itself.
- **Propose a one-minute comic** once the `**In one sentence:**` thesis is settled, for any study whose point happens in a scene with speakers: the **one-minute-comic** skill tells it in three to six panels, embedded right under the thesis.
- **Any mermaid diagram gets a width check — see [diagrams.md](diagrams.md).** The content column is ~560px and mermaid shrinks an oversized diagram whole, text included, without warning: three columns is the ceiling for `flowchart LR`; fold a longer chain into `subgraph` stages. The validator cannot measure width, so this check is the only guard.
- **Write toward [style-guide.md](style-guide.md)'s "Write toward this" from the first draft, and re-run the whole guide after every substantive revision.** Rule 5 (define affirmatively) is applied before drafting, because the antithesis family does not respond to detection. Revision is where the register comes back: on `day-is-a-thousand-years.md` three narrated-argument constructions reappeared within the hour in paragraphs the same agent had just cleaned. A green `npm run validate` covers four narrow regexes of that page, nothing more.
- If Phase 6's translation comparison turned up something a reader could act on, give it a short section of its own rather than burying it in a word study — but only where it earned one. "No English version preserves X, here's what you'd miss" is worth a reader's time; a table of trivial wording differences is padding.
- **End with References & Recommended Reading, and keep within copyright** — both in
  [formatting.md](formatting.md). The short version: name every source drawn on, restricted ones
  included; Bible text is limited by percentage, commentary to a sentence or two with attribution.

## Phase 8 — Validate & review

- Run `npm run validate` (see [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md)) against the new file.
- Run `mkdocs build --strict` — it is the only check that resolves every internal link, and it fails
  the build on a broken one. `npm run validate` does not check links.

  ```bash
  uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin \
      --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects --with segno \
      mkdocs build --strict --site-dir /tmp/mkcheck
  ```

  Check image paths by eye: they move with the file the same way links do. Link the family tree
  as the timeline's `#view=family`; `/genealogy/` is only a redirect.
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
- **Offer enrichment back to the siblings.** List for the author each `sibling_studies` entry where
  this study found something that study lacks: a word study, a correction, or a link back to this
  one. Say what each would add and where it would go. Don't edit the other study in this session:
  a change to a published study is its own change and gets its own review. Record what the author
  chose in the entry's `note`.
- Once the user has reviewed it, flip `draft: false`.
- Mark the state file `status: published` — don't delete it; it's the record of how the conclusions were reached.

## State tracking

Every study-in-progress gets one structured-data file at `references/study-state/<slug>.yml`, copied from [study-state.template.yml](study-state.template.yml). It exists so a study can be resumed in a later session (or by a different agent) without re-deriving context, and so the exegesis trail — what was checked, what's still open — is never silently lost.

Update the relevant `stages.*` block and bump `last_updated` as each phase above completes. `open_questions` is for anything you're consciously deferring (a textual variant you didn't chase down, a cross-reference you couldn't confirm) — don't let it go silently unmentioned in the final draft's own notes.

**The state file is a record, not a verification.** It holds what you concluded, not proof the conclusion was right — and a wrong conclusion gets written into it with exactly the same confidence as a right one, usually *before* it reaches the draft. That makes checking a claim against your own notes worse than useless: the trail confirms the error instead of catching it, and does so in your own handwriting. This is not hypothetical — a `MAIN FINDING` block in one study's state file carried a bad citation into the published prose, and the error survived a self-check that consisted of re-reading. Anything load-bearing gets **re-queried from source**, never re-read from here. That is also why review-bible-study's Phase 3 says *re-derive, don't re-read*: it is the same rule pointed at a file someone has already finished.

## Companion files

- [placement-and-tags.md](placement-and-tags.md) — section taxonomy, tag facets, frontmatter traps (read before drafting)
- [word-study-method.md](word-study-method.md) — the fuller diachronic → synchronic → conclusion procedure (Phase 4)
- [cross-references.md](cross-references.md) — cross-reference tiers, variants, translation comparison, commentaries and study notes (Phase 6)
- [formatting.md](formatting.md) — quote blocks, references, word tags, bibliography, copyright (Phase 7)
- [style-guide.md](style-guide.md) — the prose pass (Phase 7)
- [discussion-questions.md](discussion-questions.md) — the facets a question set covers (Phase 7)
- [human-review.md](human-review.md) — the three things only a human read-through catches (hand to the user with the draft)
- [diagrams.md](diagrams.md) — the mermaid width budget and the stage-folding pattern (Phase 7)
- [drawn-graphics.md](drawn-graphics.md) — the four kinds of drawn SVG and the rules for each (Phase 7)
- [study-state.template.yml](study-state.template.yml) — state file schema

Source catalog and licence tiers: [references/README.md](../../../references/README.md), as AGENTS.md directs.

Three source rules live in AGENTS.md and the `bible-references` server's own instructions, and
apply to every phase above: **a lookup miss is not absence** (run
`python3 references/check_sources.py` and read its raw-only list before saying a text is
unavailable); **a reference is not a universal address** (Hebrew Joel 3:1 is English Joel 2:28 —
use `bible_parallel` or `bible_align` for any query you compose yourself); and **external material
resolves through `$BIBLE_MEDIA_ROOT`**, which may be unmounted — say so in the state file rather
than skipping verification. Prefer the MCP tools over `query.py`; the CLI is the fallback.
