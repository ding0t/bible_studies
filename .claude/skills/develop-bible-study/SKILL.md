---
name: develop-bible-study
description: Walks through exegesis-then-hermeneutics before drafting a new study, commentary, or sermon file in docs/content/. Use when the user asks to start, research, outline, or draft a new Bible study, or asks how to properly study a passage before writing about it.
---

# Develop a Bible Study

This skill operationalizes the two-task method from Fee & Stuart, *How to Read the Bible for All Its Worth*: first **exegesis** (what the text meant, then-and-there), only then **hermeneutics** (what it means, here-and-now). It exists to enforce the principles already stated in [AGENTS.md](../../../AGENTS.md) — context before conclusions, word studies in the original languages, cited sources, dispensational reading of prophecy — as a concrete, repeatable workflow instead of good intentions.

**The one rule that governs everything below: do not draft application or theology before exegesis is done.** If you (the agent) notice yourself reaching for a conclusion, a cross-reference, or a "this means..." before you've established historical and literary context, stop and go back a phase.

## Before starting

Ask the user (if not already given): the primary passage or topic, and where it should land in `docs/content/` (check `category` conventions in [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md)).

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
- For a term that's genuinely load-bearing or contested (not every word needs this), work it through the fuller diachronic → synchronic → conclusion method in [word-study-method.md](word-study-method.md) rather than stopping at a bare gloss.
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
  - **Ask which translation, if any, preserves the feature you found in the original — but only in that order.** Establish the sense from the Hebrew/Greek first; *then* check which English versions keep it visible. This is genuinely useful to a reader who doesn't read the original languages: telling them "the ESV shows this, the WEB doesn't" hands them something they can act on, and it's often the most practical fruit of a word study.
  - **The order is the whole guardrail, because run backwards this becomes translation-shopping** — scanning versions for the rendering that flatters a reading you already like, then citing that version as though it were evidence. It isn't; it's a witness to a translator's decision. If you notice yourself preferring a translation *because it agrees with you*, stop and go back to the text. The claim must stand on the Hebrew/Greek and be stated that way, with translations reported as observations about translations.
  - Corollary: **comparison never silently changes the study's base translation.** ESV remains the default for quotation per AGENTS.md even where another version renders a particular word better; if a different one is quoted for a specific purpose, say which and why, right there (AGENTS.md already requires naming the translation of every quote).
  - Expect the honest result to be mixed rather than a winner. A single version rarely preserves everything: in the Bread of Life study, the ESV keeps John's *esthiō*→*trōgō* shift at all four verses while losing the *menō* thread linking 6:27 to 6:56, and the ASV does exactly the reverse — which is a more useful thing to tell a reader ("read a second, more literal version alongside; expect each to be strong in different places") than crowning one translation.
  - Worth checking whenever a word is doing structural work: a deliberate mid-passage switch, a repetition that ties distant verses together, a rare or contested term, or a distinction the original marks and English tends to collapse (as English does with *kophinos*/*spyris*, both "basket"). Wooden-literal versions (ASV, YLT) are the likeliest to preserve such things and the least pleasant to read — which is the trade being made. All of ASV, YLT, WEB and BSB are queryable in `bible-text.db`; ESV/NIV/NKJV/CSB are in `study-notes.db` (see the commentary bullet below).
- **Consult commentaries last**, not first — use them to check your reading, not to form it. Cite any extra-biblical source used, per AGENTS.md.
  - You have real commentaries to consult, so do consult them: `study-notes.db` on the external media volume holds the ESV Study Bible, both Cultural Backgrounds Study Bibles, the NIV Biblical Theology Study Bible and the CSB Ancient Faith Study Bible — notes, book introductions, and topical articles, plus each edition's own **verse text** (so it is also where you verify an ESV/NIV/NKJV/CSB quotation rather than quoting from memory). Access pattern and the mandatory `immutable=1` URI form: [references/README.md](../../../references/README.md#study-notesdb-commercial-study-bible-commentary-external-not-in-this-repo-at-all). Query it with a `verse_start<=N AND verse_end>=N` window rather than an exact-verse match, since notes are attached to ranges.
  - Expect this step to *change* something. If commentaries confirm every single thing you already wrote and add nothing, you have probably skimmed them for agreement rather than read them for correction. Note explicitly in `resources_consulted` what each one confirmed versus contributed.
- Record every source touched in `resources_consulted` on the state file, with enough detail (author, work, translation) to reconstruct the citation later.

## Phase 7 — Draft

- Write the file per [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) frontmatter schema (`title`, `category`, `description`, `tags`, `draft: true`, `bible_references`).
- **Always populate `primary_passage` and `bible_references`.** `references/build/commentary_index.py` reads these to auto-generate the "studies referencing this chapter" cross-links inside `docs/content/bible/commentaries/<book>/`, keyed off exactly the passage(s) this study is centrally about (`primary_passage`, singular or `;`-separated for a multi-account passage like a Gospel parallel) versus what it merely cites in passing (`bible_references`). A study missing both is invisible to that index, not an error, but it means the cross-reference system silently under-reports — don't skip this field the way many of the pre-existing studies did.
- Structure: historical/literary context → walk-through with original-language notes → theological principle → application/discussion questions → **References & Recommended Reading**.
- Always give the translation used for any quotation (AGENTS.md).
- If Phase 6's translation comparison turned up something a reader could act on, give it a short section of its own rather than burying it in a word study — but only where it earned one. "No English version preserves X, here's what you'd miss" is worth a reader's time; a table of trivial wording differences is padding.
- **Every study ends with a References & Recommended Reading section.** This is the reader-facing bibliography — distinct from the state file's `resources_consulted`, which is the working research trail. List every lexicon, commentary, dictionary, or background source actually drawn on, restricted/copyrighted ones included by name (e.g. TWOT, Cultural Backgrounds Study Bible, Fee & Stuart) — a citable work referenced with attribution and a reasonably-scoped quotation is a normal, fine thing to do in a public document; it isn't something to work around or leave unstated. What copyright actually constrains is quoting *too much* of one source (a full paragraph or note, not a sentence) or failing to attribute — not whether a restricted source can be named or cited at all. See [references/README.md](../../../references/README.md) for the tier-by-tier detail on what's safe to quote how.
- **Copyright guardrail:** synthesize in your own words; keep any direct quotation from a commentary or reference work short (a sentence or two) and always attributed. Don't reproduce a full paragraph or note verbatim from a copyrighted source (e.g. the locally-extracted Fee reference, or a Cultural Backgrounds Study Bible note) into a file that gets committed here — the constraint is quotation *length*, not whether the source can be cited.

## Phase 8 — Validate & review

- Run `npm run validate` (see [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md)) against the new file.
- Once the user has reviewed it, flip `draft: false`.
- Mark the state file `status: published` — don't delete it; it's the record of how the conclusions were reached.

## State tracking

Every study-in-progress gets one structured-data file at `references/study-state/<slug>.yml`, copied from [study-state.template.yml](study-state.template.yml). It exists so a study can be resumed in a later session (or by a different agent) without re-deriving context, and so the exegesis trail — what was checked, what's still open — is never silently lost.

Update the relevant `stages.*` block and bump `last_updated` as each phase above completes. `open_questions` is for anything you're consciously deferring (a textual variant you didn't chase down, a cross-reference you couldn't confirm) — don't let it go silently unmentioned in the final draft's own notes.

## Essential references

See [references/README.md](../../../references/README.md) for the full source catalog this process leans on — open-license data (safe to cite freely), restricted-license data (usable now, non-commercial caveats), and local-only copyrighted references (Fee, Stevens, the Cultural Backgrounds Study Bible — cite briefly, never reproduce at length) — plus how to actually query most of it through `references/build/bible-text.db` instead of grepping raw source files. If the `bible-references` MCP server is connected (see the README's MCP section), prefer its tools (`bible_word`, `bible_verse`, `bible_passage`, `twot_root`, etc.) over shelling out to `query.py`/`twot_lookup.py` directly — same data, no bash-construct/text-parse round trip. The CLI scripts remain the fallback when it isn't configured.

For the fuller word-study procedure referenced in Phase 4, see [word-study-method.md](word-study-method.md).
