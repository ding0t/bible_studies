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
- **Consult commentaries last**, not first — use them to check your reading, not to form it. Cite any extra-biblical source used, per AGENTS.md.
- Record every source touched in `resources_consulted` on the state file, with enough detail (author, work, translation) to reconstruct the citation later.

## Phase 7 — Draft

- Write the file per [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) frontmatter schema (`title`, `category`, `description`, `tags`, `draft: true`, `bible_references`).
- Structure: historical/literary context → walk-through with original-language notes → theological principle → application/discussion questions → **References & Recommended Reading**.
- Always give the translation used for any quotation (AGENTS.md).
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

See [references/README.md](../../../references/README.md) for the full source catalog this process leans on — open-license data (safe to cite freely), restricted-license data (usable now, non-commercial caveats), and local-only copyrighted references (Fee, Stevens, the Cultural Backgrounds Study Bible — cite briefly, never reproduce at length) — plus how to actually query most of it through `references/build/bible-text.db` instead of grepping raw source files.

For the fuller word-study procedure referenced in Phase 4, see [word-study-method.md](word-study-method.md).
