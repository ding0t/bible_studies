---
name: youth-bible-study
description: Cuts a published study in docs/content/ down into a youth page for young readers aged 8 to 16 -- a big idea, a four-panel comic with large lettering and a phone layout, the passage to read together, a story with questions and an activity for ages 8-11 and for 12-16, a key word in the language the passage was written in, a memory verse and a prayer. Written as a TOML file in docs/data/youth/ and rendered onto docs/content/youth/<slug>.md by hooks/youth.py. Use when the user asks for a youth, kids', children's, teens' or young readers' version of a study, or a study for a Sunday school, youth group or family -- as opposed to simplify-bible-study, which shortens the study itself for adult readers.
---

# A study for young readers

A youth page is a full study told to children and teenagers. It lives under `youth/`, and the full
study stays its leader's notes: the page links to it and says so. The first is
`youth/woman-at-well.md` (`docs/data/youth/woman-at-well.toml`, comic `woman-at-well-youth.toml`).
The author judged its wording level "about right", so open it beside this file and match it.

## The rule: say nothing the study does not

Every claim on the page is the study's own, cut down and said in plain words. No new fact, reading,
application or illustration of a doctrine the study does not teach. A youth page that drifts from
its study gives a leader two sets of notes, and the full study is the only set (as with the group
sheet). If the young readers need something the study lacks, stop and tell the author; the fix
belongs in the study first.

What you add is only what the age needs: shorter sentences, an everyday picture of a thing the
study explains (a well is "a deep hole you let a jar down into"), the activity, and the comic.

## The shape is fixed

`hooks/youth.py` writes the page from the TOML in one order, so a youth page cannot grow the way a
study does. Every field is required.

| TOML | On the page | Comes from in the study |
|---|---|---|
| `study`, `ages` | "For young readers, ages 8–16. Leading a group? The full study is your notes." | The study's path under `docs/content/` |
| `big_idea` | The big idea box | `**In one sentence:**`, said to a 10-year-old, landing on "you" |
| `comic` | The comic (wide, and one panel per row on a phone) | The study's comic, redrawn (step 3) |
| `read` | "Read it together:" | `primary_passage`, trimmed to the verses the story tells |
| `[[band]]` × 2 | A tab per age band: `story`, `questions` (Talk about it), `activity` (Try this week) | The study's sections, discussion questions and Be Transformed |
| `[key_word]` | "Key word in Greek: πηγή" box | The study's central word study |
| `[memory_verse]` | Memory verse box | The verse the study turns on |
| `prayer` | `## Pray` | The study's prayer |

**TOML scoping:** every top-level key (`prayer` included) goes *above* the first `[table]`. A key
written after `[[band]]` belongs to the last band, and the build fails with `KeyError: 'prayer'`.

## 1. Check the study is ready

The study must be **published** (`draft: false`): the youth page links to it, and a published page
linking a draft is validator Check 24's error. It also needs an `**In one sentence:**` line,
facet-labelled discussion questions with a **Be transformed.** question, and a prayer. A study
missing one of those is not ready to cut down; tell the author which.

Read the whole study, its state file (`references/study-state/<slug>.yml`, for what is settled and
what is contested) and its comic TOML if it has one.

## 2. Write the TOML

**Both bands.** Write each band's story as a retelling of the passage in the study's order, ending
on the study's point. Name each verse in brackets so the pop-ups open it (John 4:14), and write
every reference with its book.

| | Ages 8–11 | Ages 12–16 |
|---|---|---|
| Story | ~175 words, four short paragraphs | ~300 words |
| Sentences | Short, one idea each, everyday words | Normal length; terms the study uses, glossed once |
| Quotation | Paraphrase, with the verse named | The BSB, quoted with "(BSB)", up to a sentence at a time |
| Original language | The key word only, in its own box | Up to two or three words the study's argument stands on, each as πηγή (*pēgē*, pay-GAY) |
| Questions | 3: **The language.**, **Christ.**, **Be transformed.** | 4: add **The text in its context.** or **The hard part.** |
| Activity | Something to draw, make or do with a drink, a walk, a meal | One habit for the week, often tied to the memory verse |

Questions keep the facet labels of `develop-bible-study/discussion-questions.md`, cut down from the
study's own set; the last is always **Be transformed.** Each is under 40 words and asks about the
reader's life, never for a fact they can read off the page.

Contested things: the 8–11 story leaves them out. The 12–16 story may name one only as the study
does ("some think… others…"). Neither band draws a contested reading as settled.

**The key word.** Take the study's central word study. Credit it to the writer's language, since the
speaker may have used another: Jesus most likely spoke Aramaic at the well, and John wrote his
Gospel in Greek, so `written = "John wrote his Gospel in Greek. The key word in this story is"`. For
the Old Testament, "…wrote in Hebrew". Never call it a "secret word". `say` is plain syllables
with the stress in capitals (pay-GAY). `strongs` is the number the study gives, checked with
`bible_word`. `note` gives one or two places the word occurs that the study itself cites.

**The memory verse** is the BSB (public domain, the site's reading translation), copied from
`bible_passage(..., work_id="berean-bsb")`, never from memory. Pick the verse the study's point
stands on; prefer one an 8-year-old can learn in a week (under 35 words).

**The prayer** is the study's prayer, made first person singular and simple: "Father, thank you
that your Son Jesus…", landing on what the reader asks for, and closing "In Jesus' name. Amen."
About 60 words.

**The header comment** names the study, says the TOML adds nothing to it, and records the date the
Bible text was checked and the comic's `--verify` command (see the pilot's header).

## 3. Draw the comic

Use the **one-minute-comic** skill, with these settings for young readers:

- **Four panels**: `layout = [[330, 1, 1], [330, 1, 1]]`. Keep the study comic's finding and drop
  the rest to four beats: the setting, the misunderstanding or problem, the answer, what the person
  did next.
- `lettering = 17` (larger text) and `phone = true`, which writes `<slug>-phone.svg` with one panel
  per row. The hook swaps the two by screen width.
- Slug `<study-slug>-youth`; the header names the parent comic.
- Every bubble is ESV wording, cut at a clause, `source = "esv"`, so `--verify` checks all of it. No
  Greek or Hebrew on the comic: thought pictures carry the ideas in English, and the page teaches
  the key word.

```bash
python3 utils/build_comics.py <slug>-youth
python3 utils/build_comics.py --verify <slug>-youth
qlmanage -t -s 1400 -o <scratchpad> docs/content/assets/img/comics/<slug>-youth.svg
qlmanage -t -s 1400 -o <scratchpad> docs/content/assets/img/comics/<slug>-youth-phone.svg
```

Look at both renders. At 17-point lettering a bubble that fit at 14.5 can cover a head; move it
with `at`.

## 4. The page and the links

`docs/content/youth/<slug>.md` is frontmatter, the H1 and the marker, nothing else:

```markdown
---
title: "<the study's title>"
category: "youth"
description: "<passage> for young readers aged 8-16: <the big idea in a phrase>."
tags: [<the study's topic tags>, "audience/youth"]
draft: false
primary_passage: "<the study's primary_passage>"
bible_references: [<the passages the youth page cites>]
---

# <the study's title>

<!-- youth: <slug> -->
```

In the full study, directly after its comic (or its opening paragraph), add one line:

```markdown
Teaching children or teenagers? [<Title> for young readers](../youth/<slug>.md) tells this story for ages 8 to 16, with its own comic.
```

## 5. Check and commit

```bash
python3 utils/build_comics.py --verify <slug>-youth
cd references/build && uv run python section_index.py && cd ../..
python3 utils/refresh_frontmatter_provenance.py
cd app && npm run validate && cd ..
uvx --with mkdocs-material --with mkdocs-awesome-pages-plugin --with mkdocs-git-revision-date-localized-plugin --with mkdocs-redirects --with segno mkdocs build --strict
```

Then open the page under `mkdocs serve` in Playwright webkit (the author reads in Safari) at desktop
width and at 390px. Check both tabs, the phone comic, and that every verse and the key word pop up.
`mkdocs serve` does not reload `hooks/youth.py`; restart it after a hook change.

Commit the TOML files, both SVGs, the youth page, the study's link line, the regenerated index
pages and the provenance edits together: `feat(youth): <title> for young readers`.

## Extending the system

The shape lives in `hooks/youth.py` and its styles in `series.css` (`.youth-for`, `.admonition.youth`,
`.comic-wide`/`.comic-phone`). A new field is a change to the hook and to every TOML in
`docs/data/youth/`, so add one only when the author asks for it on every page.
