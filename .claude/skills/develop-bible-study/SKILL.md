---
name: develop-bible-study
description: Walks through exegesis-then-hermeneutics before drafting a new study, commentary, or sermon file in docs/content/. Use when the user asks to start, research, outline, or draft a new Bible study, or asks how to properly study a passage before writing about it.
---

# Develop a Bible Study

This skill operationalizes the two-task method from Fee & Stuart, *How to Read the Bible for All Its Worth*: first **exegesis** (what the text meant, then-and-there), only then **hermeneutics** (what it means, here-and-now). It exists to enforce the principles already stated in [AGENTS.md](../../../AGENTS.md) — context before conclusions, word studies in the original languages, cited sources, dispensational reading of prophecy — as a concrete, repeatable workflow instead of good intentions.

**The one rule that governs everything below: do not draft application or theology before exegesis is done.** If you (the agent) notice yourself reaching for a conclusion, a cross-reference, or a "this means..." before you've established historical and literary context, stop and go back a phase.

## Before starting

Ask the user (if not already given): the primary passage or topic, and where it should land in `docs/content/` — see **Placement** below, and [docs/content/about/our-taxonomy.md](../../../docs/content/about/our-taxonomy.md) for the full definition.

Create the state file for this study — see **State tracking** below — before doing any research. Update it as you complete each phase; this is what lets the study be picked back up in a later session without re-deriving where you left off.

## Placement — which section, and what to tag

Full definition: [our-taxonomy.md](../../../docs/content/about/our-taxonomy.md). The short version, because getting this wrong is cheap to prevent and annoying to fix once the URL is published.

**Sections are top level.** There is no `studies/` wrapper and no `bible/` — a study goes at `docs/content/<section>/<slug>.md`. Named from the systematic-theology loci in plain English:

| Section | Locus | Takes |
|---|---|---|
| `scripture/` | Bibliology | Canon, manuscripts, textual criticism, translation, how to read it, biblical archaeology, extra-biblical texts |
| `god/` | Theology Proper | God's nature, Trinity, Holy Spirit, creation, revelation (incl. dreams and visions) |
| `jesus/` | Christology | Who Christ is and what he did; OT prophecy fulfilled in him |
| `sin/` | Hamartiology | The nature of sin and its particular forms |
| `spiritual-beings/` | Angelology & Demonology | Angels, demons, Satan, Nephilim, deliverance, discernment of spirits |
| `israel-and-church/` | Ecclesiology + the dispensational distinction | Covenants, Israel/Church, Hebrew roots |
| `last-things/` | Eschatology | Rapture, tribulation, millennium, judgment, ordering of events |
| `feasts/` | *Appointed times* | The feasts and calendars |
| `christian-life/` | Practical theology | Prayer, fasting, the disciplines |
| `commentaries/<nn>-<book>/` | — | Book studies and chapter notes, filed by book |
| `sermons/` | Homiletics | Sermon and teaching material |
| `resources/` | — | Guides to external material |

**Two sections are defined but not created**: `salvation/` (Soteriology — grace, redemption, assurance, death) and `biblical-figures/` (biography). A section exists when it has content. **If a study genuinely belongs to one of these, say so and create it** — that is the trigger the taxonomy is waiting for, not a reason to file the study somewhere it doesn't fit. Creating one means adding the directory, a line in `SUBJECT_DIRS` in `references/build/commentary_index.py`, a blurb in `SECTION_BLURBS` in `section_index.py`, and an entry in `docs/content/.pages`.

**When a study could sit in two sections**, file it by what it is *most about* and tag the other axis. Dewey's 200s are the tiebreaker — it has already adjudicated most of these (angels and demons are 235, their own subject; apocrypha is 229; calendars and appointed times are 263). Don't invent a new section to resolve a single awkward case.

**Some things are not subjects at all.** *Apologetics*, *typology*, *word study* and *archaeology* are approaches, not topics — a study using them is filed by what it is about and carries the approach as a tag. An apologetics study defending Scripture's reliability is `scripture/`; one arguing from creation is `god/`; one on the resurrection is `jesus/`.

**Tags carry every axis the directory can't.** Five facets use a `/` prefix and render as a real hierarchy (`tags_hierarchy: true` in `mkdocs.yml`):

- `method/word-study`, `method/typology`, `method/archaeology`, `method/textual-criticism`
- `lang/hebrew`, `lang/greek`
- `status/investigation` — open inquiry, conclusions not settled
- `audience/teaching`
- `person/<name>` — a named individual the study is *about* (`person/peter`, `person/melchizedek`)

**Why `person/` exists, and when to use it.** Most Bible people share a name with a book, and a flat
`matthew` tag cannot tell a reader whether the page is about the tax collector or the Gospel. The
site had exactly that collision the moment `biblical-figures/` was created. So: **a book always gets
the bare tag (`matthew`, `john`, `james`), and a person always gets `person/`.** A page can carry
both — `biblical-figures/matthew.md` is about the man *and* cites his Gospel, so it tags
`person/matthew` and `matthew`.

Use `person/` when the individual is a subject of the study, not merely mentioned. Where two people
share a name, disambiguate the way Scripture does, by patronymic:
`person/james-son-of-zebedee` and `person/james-son-of-alphaeus`, never a bare `person/james`.
Where one person has two names, tag both if the study argues the identification
(`person/bartholomew` and `person/nathanael`).

Everything else is a plain topic tag: a book, a feast, a concept. Rules that matter:

- **Never tag what the section already says.** No `studies`, no `prophecy` on a `last-things/` page, no `sin` on a `sin/` page. It adds nothing and inflates the tag index.
- **No colons in tag values** — the facet separator is `/`, and a colon reads as a competing convention (`malachi-4:2` had to be renamed `malachi-4-2`).
- Lowercase, hyphenated, no spaces. `dead-sea-scrolls`, not `dead sea scrolls` or `Dead Sea Scrolls`.
- Prefer an existing tag to a near-synonym. Check [docs/content/tags.md](../../../docs/content/tags.md) — the rendered index is the live vocabulary.

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
- Grammar/syntax points that affect meaning, only where they actually change the reading — don't pad with grammar for its own sake.
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
- Draft the contemporary application. Keep it distinguishable from the exegesis above — a reader should be able to tell what the text *said* from what you're *applying*.

## Phase 6 — Cross-reference & verify

- Gather cross-references (Treasury of Scripture Knowledge, parallel-passage tools — see references doc) for the key claims.
- Compare across the translations AGENTS.md specifies (Masoretic/LXX, ESV default, plus NLT/WEB/NASB/NIV as useful) and note where they diverge meaningfully.
  - **Ask which translation, if any, preserves the feature you found in the original — but only in that order.** Establish the sense from the Hebrew/Greek first; *then* check which English versions keep it visible. This is useful to a reader who doesn't read the original languages: telling them "the ESV shows this, the WEB doesn't" hands them something they can act on, and it's often the most practical fruit of a word study.
  - **The order is the whole guardrail, because run backwards this becomes translation-shopping** — scanning versions for the rendering that flatters a reading you already like, then citing that version as though it were evidence. It isn't; it's a witness to a translator's decision. If you notice yourself preferring a translation *because it agrees with you*, stop and go back to the text. The claim must stand on the Hebrew/Greek and be stated that way, with translations reported as observations about translations.
  - Corollary: **comparison never silently changes the study's base translation.** ESV remains the default for quotation per AGENTS.md even where another version renders a particular word better; if a different one is quoted for a specific purpose, say which and why, right there (AGENTS.md already requires naming the translation of every quote).
  - Expect the honest result to be mixed rather than a winner. A single version rarely preserves everything: in the Bread of Life study, the ESV keeps John's *esthiō*→*trōgō* shift at all four verses while losing the *menō* thread linking 6:27 to 6:56, and the ASV does exactly the reverse — which is a more useful thing to tell a reader ("read a second, more literal version alongside; expect each to be strong in different places") than crowning one translation.
  - Worth checking whenever a word is doing structural work: a deliberate mid-passage switch, a repetition that ties distant verses together, a rare or contested term, or a distinction the original marks and English tends to collapse (as English does with *kophinos*/*spyris*, both "basket"). Wooden-literal versions (ASV, YLT) are the likeliest to preserve such things and the least pleasant to read — which is the trade being made. All of ASV, YLT, WEB and BSB are queryable in `bible-text.db`; ESV/NIV/NKJV/CSB are in `study-notes.db` (see the commentary bullet below).
  - **YLT stays a comparison tool only.** Fee & Stuart — the methodology this whole skill operationalizes — hold up Young's Literal Translation by name as their own worst-case example of formal equivalence taken too far ("not a valid translation at all," of its 1 Cor 5:1 rendering). That critique is about YLT as a *reading* Bible; the structural-comparison use above is different and stays legitimate — but never quote YLT as a verse's meaning in a study's prose, only to show what a maximally literal rendering preserves. Same boundary on NKJV, which Fee & Stuart also name as worth avoiding for study (inherited the KJV's underlying Greek text): fine for verifying a quotation or reading its study-Bible notes in `study-notes.db`, never as a primary translation.
- **Consult commentaries last**, not first — use them to check your reading, not to form it. Cite any extra-biblical source used, per AGENTS.md.
  - You have real commentaries to consult, so do consult them: `study-notes.db` on the external media volume holds the ESV Study Bible, both Cultural Backgrounds Study Bibles, the NIV Biblical Theology Study Bible and the CSB Ancient Faith Study Bible — notes, book introductions, and topical articles, plus each edition's own **verse text** (so it is also where you verify an ESV/NIV/NKJV/CSB quotation rather than quoting from memory). Access pattern and the mandatory `immutable=1` URI form: [references/README.md](../../../references/README.md#study-notesdb-commercial-study-bible-commentary-external-not-in-this-repo-at-all). Query it with a `verse_start<=N AND verse_end>=N` window rather than an exact-verse match, since notes are attached to ranges.
  - Expect this step to *change* something. If commentaries confirm every single thing you already wrote and add nothing, you have probably skimmed them for agreement rather than read them for correction. Note explicitly in `resources_consulted` what each one confirmed versus contributed.
- Record every source touched in `resources_consulted` on the state file, with enough detail (author, work, translation) to reconstruct the citation later.

## Phase 7 — Draft

- Write the file per [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) frontmatter schema (`title`, `category`, `description`, `tags`, `draft: true`, `bible_references`), into the section chosen under **Placement** above.
- **Fill every placeholder.** The CONTENT_GUIDE template's example values are `tag1`/`tag2`, `"Brief description of the page content"`, `bible_references: ["Genesis 1:1"]`, `zadok_year: 0`, `gregorian_year: -4004`. A real file on this site shipped with all of those intact and `draft: false` — the effect was an empty published page cross-linked into Genesis 1's commentary and sitting at 4004 BC as the first entry on the prophetic timeline. `zadok_year`/`gregorian_year` are read by `app/scripts/build-events.js`, **which does not filter drafts**, so a bogus year reaches the timeline even on a draft. Omit those two fields entirely unless the study is genuinely dated.
- **Always populate `primary_passage` and `bible_references`.** `references/build/commentary_index.py` reads these to auto-generate the "studies referencing this chapter" cross-links inside `docs/content/commentaries/<book>/`, keyed off exactly the passage(s) this study is centrally about (`primary_passage`, singular or `;`-separated for a multi-account passage like a Gospel parallel) versus what it merely cites in passing (`bible_references`). A study missing both is invisible to that index, not an error, but it means the cross-reference system silently under-reports — don't skip this field the way many of the pre-existing studies did.
- Structure: short hook → **Key Takeaways** → historical/literary context → walk-through with original-language notes → theological principle → discussion questions → **References & Recommended Reading**.
- **Key Takeaways** (prototype, see [docs/content/about/key-takeaways.md](../../../docs/content/about/key-takeaways.md) for the full rationale) replaces the old flat "Key lessons" bullet list with up to five subheadings, in this order, each included only where the study actually earns it — don't force one to fill a slot: **Types & Prophecy** (two related but distinct things, kept apart rather than blended — a **type**, an OT person/object/ritual that patterns Christ or the gospel by *resemblance*, τύπος, e.g. Melchizedek; and a **prophecy**, a direct verbal prediction the passage makes or fulfills, e.g. Psalm 110:4's sworn oracle — a study may have one, both, or neither); **Lessons about Jesus** (the direct Christological conclusions the exegesis established); **Memory verses** (1-3 verses already quoted and cited in the study's own body, pointed back to — not new quotations introduced here); **Be Transformed** (Romans 12:2 made concrete — specific thoughts, attitudes, actions the study calls the reader to examine or change, kept as distinguishable from the exegesis as Phase 5's application already requires); **Prayer**, deliberately last (a short response specific to this study's actual content, structured the way the Lord's Prayer study shows Jesus's own model prayer working — relationship and God's character first, request second — not a generic devotional line). This section still comes up front, before supporting detail — a reader should get the point even if they read no further.
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
- **Before flipping to `draft: false`, run the prose through [style-guide.md](style-guide.md)** — a pass for the surface-level tics (bare intensifiers like "genuinely," narrated-argument phrases like "worth noting," overused contrast rhythms, em-dash overload) and for waffle — whole sentences that survive being deleted without losing any fact or step in the argument — that together make even well-researched content read as AI-generated and undercut the reader's trust in it.
- If Phase 6's translation comparison turned up something a reader could act on, give it a short section of its own rather than burying it in a word study — but only where it earned one. "No English version preserves X, here's what you'd miss" is worth a reader's time; a table of trivial wording differences is padding.
- **Every study ends with a References & Recommended Reading section.** This is the reader-facing bibliography — distinct from the state file's `resources_consulted`, which is the working research trail. List every lexicon, commentary, dictionary, or background source actually drawn on, restricted/copyrighted ones included by name (e.g. TWOT, Cultural Backgrounds Study Bible, Fee & Stuart) — a citable work referenced with attribution and a reasonably-scoped quotation is a normal, fine thing to do in a public document; it isn't something to work around or leave unstated. What copyright actually constrains is quoting *too much* of one source (a full paragraph or note, not a sentence) or failing to attribute — not whether a restricted source can be named or cited at all. See [references/README.md](../../../references/README.md) for the tier-by-tier detail on what's safe to quote how.
- **Copyright guardrail.** There are *two* different permissions in play and they are not the same, so don't apply one rule to both:
  - **Bible text** is covered by each publisher's own stated allowance, and it is generous: ESV, CSB and NKJV each permit **1,000 verses** without asking, NIV **500**. No study will come near those. **The limit that actually binds here is the percentage, not the verse count** — NIV caps quotation at 25% of the work it appears in, ESV/CSB/NKJV at 50%, and none of them permit a complete book. A short study that is mostly block-quoted Scripture with a little commentary around it can breach that at a couple of dozen verses. If a study is tripping this rule, it is usually too thin on its own contribution as well; fix that, not the quota. NASB is the exception — the Lockman Foundation's notice states no blanket allowance, so don't assume one.
  - **Commentary, study notes, introductions, articles, charts, maps** are separately copyrighted with **no blanket allowance at all** — the ESV Study Bible's own notice reserves all rights to its content. Here the "a sentence or two, always attributed" rule is the whole of what's available, and it applies to the locally-extracted Fee reference and the study-Bible notes in `study-notes.db` alike. Synthesize in your own words; never paste a full note or paragraph into a committed file.
  - **Attribution is a licence condition, not a courtesy.** Naming the translation inline satisfies scholarly convention but is *not* the copyright notice ESV/NIV/NKJV/CSB require. Those live on [docs/content/about/copyright.md](../../../docs/content/about/copyright.md) — if a study introduces a translation or major source not already listed there, add it in the same commit.
  - Exact thresholds, per translation, verified against the publishers' own notices: [references/README.md](../../../references/README.md#two-different-permissions-dont-conflate-them). Check there rather than recalling numbers — they differ per publisher and are easy to misremember.
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

## Essential references

See [references/README.md](../../../references/README.md) for the full source catalog this process leans on — open-license data (safe to cite freely), restricted-license data (usable now, non-commercial caveats), and local-only copyrighted references (Fee, Stevens, the Cultural Backgrounds Study Bible — cite briefly, never reproduce at length) — plus how to actually query most of it through `references/build/bible-text.db` instead of grepping raw source files. If the `bible-references` MCP server is connected (see the README's MCP section), prefer its tools (`bible_word`, `bible_verse`, `bible_passage`, `twot_root`, etc.) over shelling out to `query.py`/`twot_lookup.py` directly — same data, no bash-construct/text-parse round trip. The CLI scripts remain the fallback when it isn't configured.

For the fuller word-study procedure referenced in Phase 4, see [word-study-method.md](word-study-method.md). For the prose pass referenced in Phase 7, see [style-guide.md](style-guide.md).
