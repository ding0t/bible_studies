---
name: develop-bible-study
description: Walks through exegesis-then-hermeneutics before drafting a new study, commentary, or sermon file in docs/content/. Use when the user asks to start, research, outline, or draft a new Bible study, or asks how to properly study a passage before writing about it.
---

# Develop a Bible Study

Fee & Stuart's two tasks (*How to Read the Bible for All Its Worth*), as a workflow: first
**exegesis** (what the text meant, then and there), then **hermeneutics** (what it means, here and
now).

**The one rule: draft no application or theology until the exegesis is done.** If you reach for a
conclusion, a cross-reference or a "this means..." before the historical and literary context is
settled, go back a phase.

## Before starting

Get the primary passage or topic, and where it lands in `docs/content/`. **Read
[placement-and-tags.md](placement-and-tags.md) before drafting**: sections are top level, named from
the systematic-theology loci, and tags carry the facets the directory can't.

Create the state file (see **State tracking**) before any research, and update it as each phase
completes.

## Phase 1 — Scope & classify

- Identify the primary passage(s), the known cross-references, and the genre (epistle, OT narrative,
  Acts, Gospel, parable, law, prophets, psalm, wisdom, apocalyptic, or topical). Record the genre in
  the state file's `genre`.
- **Find what the site has already written on the passage**, for the primary chapter and any
  supporting chapter the study leans on:

  ```bash
  cd references/build
  uv run python cross_study_claims.py "John 4" --exclude <section>/<slug>.md
  ```

  (`passage_brief` returns the same list as `existing_studies`.) Record each in `sibling_studies`
  with a `use`: `link` (it covers ground this study needs; point to it in a sentence), `build-on`
  (this study takes its conclusion further), `enrich` (this study may find something it lacks) or
  `none`. This records coverage; it adopts no conclusion, and Phase 6 does the comparing. A primary
  sibling on the same verses raises a question for the author first: new study, or a revision?

## Phase 2 — Exegesis: historical context

- Author, audience, date, and the occasion that called the text into being.
- Geographic, political and customary background (a denarius as a day's wage).
- **Settle who and where before writing a name.** `bible_names` gives every individual a name can
  mean, with family and verses, and a place's best identification with a score out of 1000. A family
  link marked (a), (d), (f) or (?), or a low-scoring or closely contested site, is stated with that
  confidence ("probably", or name the rivals).
- Record any background source in `resources_consulted`.

## Phase 3 — Exegesis: literary context

- Where does the passage sit in the book's argument or story, and why does the author move into it
  and out of it? Exegete the paragraph (or strophe), never a verse alone. The governing question:
  **"What's the point?"**
- `bible_section` gives the BSB's section and the passages marked parallel; test it against your own
  reading of the unit. **Never quote a heading as Scripture.**
- **A parallel account is literary context.** For a gospel passage, Samuel–Kings–Chronicles, or a
  psalm with a historical title, read each parallel in its own setting first, and ask what each
  writer does with the shared material before blending them.
- `bible_lists` (in `passage_brief` as `structure.lists`) adds STEP's harmony, the OT text an NT
  verse quotes, and a letter's parts; `study_esv_tags` shows which Hebrew or Greek word each ESV word
  renders. Both are maps; the text decides.

## Phase 4 — Exegesis: content, words, and genre lens

- **Word studies**: the Hebrew, Aramaic or Greek, gloss and pronunciation, for each key or ambiguous
  term. For a load-bearing or contested one, work [word-study-method.md](word-study-method.md).
- **Check what an English word translates before arguing from it.** `bible_interlinear` gives the
  ULT's alignment and `interlinear="bsb"` the Berean's; `bible_alignment_diff` lists where they
  differ, a lead to weigh. If the key word is ranked in
  [alignment-disagreements.md](../../../docs/dev/alignment-disagreements.md), say which rendering the
  study follows and why. The ULT's Greek is the UGNT; at Mark 16:8ff, the pericope adulterae, Luke
  23:34 and John 1:34 it differs from the SBLGNT, so confirm the text with `bible_verse`.
- **Grammar only where it changes the reading.** Look it up with `bible_grammar` (unfoldingWord's
  Hebrew and Greek grammars; mark aspect contested where an argument rests on it). Check a figure of
  speech against `bible_translation_notes` after your own reading: it checks, never supplies, and a
  verse with no note says nothing. Use `bible_syntax` when the argument turns on who acts on whom
  (clause roles, construct state, implicit subjects); a null means not annotated
  ([references/README.md](../../../references/README.md#clause-syntax-and-coreference-macula)).
- **Apply the genre lens:**

  | Genre | Ask especially |
  |---|---|
  | Epistles | What occasioned the paragraph? Which claims does the author mark universal ("in all the churches"), and which are local practice? |
  | OT narrative | Narrative records what happened. Does the narrator, or the rest of Scripture, evaluate it? Is a principle taught elsewhere being illustrated, or are you inventing one from a character's behaviour? |
  | Acts | Was a pattern the narrative's intent, or incidental? A repeatable pattern is not automatically binding. |
  | Gospels | Which Gospel, with what emphasis and audience? Read it on its own terms before harmonising. Where does it sit on the kingdom's already/not yet? |
  | Parables | The one or few points the first hearers grasped, and who Jesus is needling. Don't allegorise incidental details. |
  | Law | Moral, civil or ceremonial? What does it reveal of God's character where the rule doesn't carry over? |
  | Prophets | Covenant enforcement in the prophet's own setting first, before reading forward. |
  | Psalms | Which type? A psalm is often prayer addressed to God; let form shape expectation. |
  | Wisdom | Proverbs observe what is generally true. Hold them against Job and Ecclesiastes. |
  | Revelation / apocalyptic | Ground the OT imagery and the pastoral purpose to seven real churches first; then lean dispensational (AGENTS.md). |

## Phase 5 — Hermeneutics: then-and-now bridge

- What is tied to its historical circumstance, and what transcends it? (Head coverings and the
  principle of order beneath them.)
- State the principle in one or two sentences, and check that Scripture teaches it explicitly
  elsewhere: narrative illustrates and rarely establishes doctrine alone.
- **Only now**, where the principle meets a position in
  [statement-of-faith.md](../../../docs/content/about/statement-of-faith.md), check it is
  consistent. Silence is the normal case. A real conflict goes to the user, never into a quiet
  edit either way; it more often means the exegesis needs fresh eyes.
- Draft the application, distinguishable from the exegesis: a reader should tell what the text said
  from what you are applying.

## Phase 6 — Cross-reference & verify

The method, with the corpus examples behind it, is in [cross-references.md](cross-references.md).
Read it before this phase.

- **Gather cross-references with `bible_trace`**, and weigh its tiers as labelled, never merged. A
  strong link marked `corroborated: false` is worth a sentence; silence means the method found
  nothing.
- **Run `bible_variants`** on every OT verse the study leans on, and quote its `extant_words`. For an
  NT variant, read the footnotes `bible_verse` returns.
- **Settle every parallel `review_gaps` reports**, in Phase 3 where you can.
- **Compare translations only after the original has settled the sense**, and never change the base
  translation for it.
- **Consult commentaries last, to check the reading.** No step rests on a study note alone, and a
  reading is contested only when the text gives reasons on both sides.
- Record every source in `resources_consulted`, enough to rebuild the citation.
- **Check against the siblings**: run `cross_study_claims.py` for each chapter in `sibling_studies`
  and any added since, by
  [review-bible-study's sibling check](../review-bible-study/SKILL.md#check-the-study-against-its-siblings-not-only-against-sources).
  Which of two disagreeing studies to fix is the author's call.

## Phase 7 — Draft

**First say what the study is trying to say**, in the state file:

1. `thesis`: one sentence. It becomes the **In one sentence:** line.
2. `outline`: one line per planned section, each serving the thesis. It is the reader's mind map,
   and the page's Study outline when it needs one.
3. `word_budget`: 4,000, or another figure with its reason.

Research that doesn't serve the thesis is a fork candidate in `open_questions`, left out of this
draft. Show the thesis and outline to the author before drafting.

**Frontmatter** ([docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md); section from
[placement-and-tags.md](placement-and-tags.md)):

- `draft: true`, and every placeholder filled (that file's "Frontmatter failures worth checking").
- `primary_passage` (`;`-separated for a gospel parallel) and `bible_references`, always: the
  commentary index is built from them.
- Never hand-write `date_created`, `date_modified` or `ai_provider_models`. Run
  `python3 utils/refresh_frontmatter_provenance.py` before committing and stage its edit.

**Shape**: short hook → **Key Takeaways** → historical/literary context → walk-through with
original-language notes → theological principle → discussion questions → optional `## Annex:` →
**References & Recommended Reading**. At 2,500+ words and 6+ `##` sections, add a **Study outline**
after Key Takeaways and put apparatus in one `## Annex:`
([structural-readability.md](../read-bible-study/structural-readability.md) rules 10-11).

**Key Takeaways** comes first so a reader gets the point without reading further. Up to five
subheadings, **in this order**, each only where the study earns it
([key-takeaways.md](../../../docs/content/about/key-takeaways.md)):

| Subheading | What goes in it |
|---|---|
| **Types & Prophecy** | Kept apart. A **type** patterns Christ or the gospel by resemblance (τύπος; 1 Corinthians 10:6, 11; Melchizedek); a **prophecy** is a verbal prediction (Psalm 110:4). |
| **Lessons about Jesus** | The Christological conclusions the exegesis established. |
| **Memory verses** | 1–3 verses already quoted in the body, as block quotes with plain references and no explanatory sentence: an interpretive one belongs in Lessons about Jesus (a bare "See [section]" locator is fine). |
| **Be Transformed** | Romans 12:2 as `**Think.**`, `**Attitude.**`, `**Do.**`, each naming its verse from the study's passages. The default shape; another is a deliberate choice for an application that won't split three ways ([be-transformed.md](be-transformed.md)). |
| **Prayer** (last) | Specific to this study, on the Lord's Prayer's model: God's character and relationship first, request second. |

**The rest of the draft:**

- **Siblings.** For each `link` or `build-on` sibling, a sentence and a relative link; spend the
  words on what this study adds. Never link a `draft: true` page from a published one (Check 24).
- **Discussion questions** cover the facets in
  [discussion-questions.md](discussion-questions.md), mirroring Key Takeaways, only those earned.
  Sets go stale silently after a restructure.
- **Format** by [formatting.md](formatting.md): every quotation's translation labelled, Scripture
  blocks opening `> ✝️ Reference (TRANSLATION)`, plain-text references naming their book, word tags
  as `ἀρραβών (*arrabōn*, G728)`, and copyright limits.
- **Prose** toward [style-guide.md](style-guide.md#write-toward-this) from the first draft (rule 5,
  define affirmatively, before drafting), and the whole guide again after every substantive revision:
  revision is where the register comes back ([why-the-rules.md](../why-the-rules.md#develop-revision)).
- **Graphics.** Propose a drawn graphic where prose carries something badly
  ([drawn-graphics.md](drawn-graphics.md): sequence, relationship, pattern, imagery); a
  **one-minute-comic** once the thesis is settled, for a point that happens in a scene with speakers;
  and give any mermaid diagram the width check in [diagrams.md](diagrams.md).
- **A translation finding a reader can act on** ("no English version preserves X") earns its own
  short section; a table of trivial differences is padding.

**Hand it on.** Send the finished draft to **read-bible-study**, in a different session where you
can: its author can't judge the composition order as a reader. Hand the user
[human-review.md](human-review.md) with it, and say which of its three tells the draft is weakest on.

## Phase 8 — Validate & review

- `npm run validate` (from `app/`) against the file, then `mkdocs build --strict`, the only check
  that resolves links:

  ```bash
  uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin \
      --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects --with segno \
      mkdocs build --strict --site-dir /tmp/mkcheck
  ```

  Check image paths by eye. Link the family tree as the timeline's `#view=family`.
- After flipping `draft: false`, re-run `uv run python commentary_index.py` and
  `uv run python section_index.py` from `references/build/` (both skip drafts).
- This phase is the author's self-check. Before publishing anything load-bearing, run
  **review-bible-study**.
- **Offer enrichment back** to each sibling this study found something for, saying what and where.
  Don't edit the other study here; record the author's choice in the entry's `note`.
- Once the user has reviewed it, flip `draft: false` and mark the state file `status: published`.

## State tracking

Each study in progress has `references/study-state/<slug>.yml`, copied from
[study-state.template.yml](study-state.template.yml), so it can be resumed without re-deriving.
Update its `stages.*` block and `last_updated` as each phase completes. `open_questions` holds what
you defer.

**The state file is a record, not a verification.** A wrong conclusion is written into it with the
same confidence as a right one, so re-query anything load-bearing from source, never re-read it from
here ([why-the-rules.md](../why-the-rules.md#develop-state-file)).

## Companion files

- [placement-and-tags.md](placement-and-tags.md) — sections, tags, frontmatter traps (before drafting)
- [word-study-method.md](word-study-method.md) — diachronic → synchronic → conclusion (Phase 4)
- [cross-references.md](cross-references.md) — cross-references, variants, translations, commentaries (Phase 6)
- [formatting.md](formatting.md), [style-guide.md](style-guide.md),
  [discussion-questions.md](discussion-questions.md), [be-transformed.md](be-transformed.md),
  [diagrams.md](diagrams.md), [drawn-graphics.md](drawn-graphics.md) (Phase 7)
- [human-review.md](human-review.md) — the three things only a human catches (with the draft)
- [study-state.template.yml](study-state.template.yml) — the state file schema

The source rules that apply to every phase (a lookup miss is not absence; a reference is not a
universal address; external material resolves through `$BIBLE_MEDIA_ROOT`) are in AGENTS.md and
the `bible-references` server's instructions. Prefer the MCP tools; `query.py` is the fallback.
