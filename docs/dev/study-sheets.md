# Group study sheets

A one-sheet version of a study for a 40-minute small group or a study with a friend: A4, printed
double-sided, flipped on the long edge. `hooks/study_sheet.py` adds it to every study that has an
`**In one sentence:**` thesis and a `## Discussion questions` list (99 pages as of 2026-10-22), in a
collapsed "Group study sheet" block under the questions, with a Print button. A printer icon
beside the title opens the block and jumps to it, since a leader decides to print from the top.

## What goes on it

| Side 1 | Side 2 |
|---|---|
| Title, `primary_passage` | The timed plan: Open 0–5, Read 5–12, Discover 12–25, Wrestle 25–35, Respond 35–40 |
| The point (the thesis) | The questions, grouped on the plan by facet label, each with ruled space |
| Open: the first `questions:` frontmatter entry, else "what comes to mind when you hear …" | This week: Be Transformed's think / attitude / do |
| Read it aloud: `primary_passage` in WEB | Memory verse: the first one |
| Look closer: say / meant then / means for us, to write in | Pray together: the study's prayer |
| The primary graphic: the first comic, else the first drawn SVG | QR code and URL back to the full study |
| The study in brief: the Study outline | |

Everything is lifted from the rendered page, so the sheet adds no claims and needs no
verification of its own. The passage is in WEB because it is printed at length; ESV appears only
where the study already quotes it (questions, memory verse), under the same notice as the memory
verse cards.

## How it fits

All sizes are in sheet millimetres (`--mm`, as in `memory-verses.css`), so the on-screen sheet is a
scale model of the page. Side 1 is fitted in the browser by `ssFit` (inline in the hook) on open
and on Print. It steps the passage type down, moves trailing passages to an "Also read" line, then
trims verses from the end, and it tightens the outline column before dropping it. A word count
cannot do this: the thesis, the opener and the outline all compete for the same height. The hook
cuts any passage past 900 words before shipping it.

Hooking `on_post_page`, after the search plugin indexes the page, keeps the sheet's copy of the
questions out of site search. Print media follows `html.ss-on`, which only the reader sets, by
clicking the block's summary or the Print button: with it, the page prints as the sheet (from the
button or the browser's own Print); without it, the study prints with no sheet. Two things rule
out simpler keys. Safari fires `afterprint` before it lays out the print, so a class the button
sets and `afterprint` clears is gone in time to print the study; and mkdocs-material opens every
`<details>` while printing, so `details[open]` would print the sheet in place of the study.
Safari also keeps its default margins under the named `@page study-sheet` and shrinks the sheet
to fit them, so `ssOn` adds an unnamed `@page { size: A4; margin: 0 }` alongside the class.

**Black & white** (a checkbox by the Print button) drops the tints, makes labels black, outlines the
badges and greys the graphic, for black-only and toner printers. The default colours are also
chosen to hold up when a colour sheet is printed in greyscale.

## Checking a change

Build to a scratch directory, serve it, and print with Playwright. `page.pdf()` with
`prefer_css_page_size=True` after opening the block, calling `ssOn(true)` and `ssFit`
reproduces the Print button. Check for overflow with `scrollHeight > clientHeight` on `.ss-main`,
`.ss-side` and `.ss-questions` under print media. `pdftoppm -gray` and `-mono` simulate greyscale
and black-only printers. At the prototype, all 99 sheets fitted.

## The study is the leader's notes

There is one set of notes per study, and it is the study itself. The sheet is what the group holds;
the leader holds the full study, with its depth: the word studies, the context, the case on both
sides of what is contested. No separate leader's guide is written, so there is no second
document to drift out of step with the study. Anything a leader needs that the sheet lacks belongs
in the study, where every reader gets it.

## Not done yet

- **A one-to-one variant**: three questions, more weight on Respond, a "next week I'll ask you
  about…" line.
- **Series booklets**: a cover, then one sheet per week, for a study series (`hooks/series.py`;
  the `series:` frontmatter already lists the weeks in order).
- Studies with seven or more questions get as little as one ruled line on some; the sheet has no
  rule yet for choosing which to keep.
