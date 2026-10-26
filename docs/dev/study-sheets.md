# Group study sheets

A four-page version of a study for a 40-minute small group or a study with a friend: two A4 sheets,
printed double-sided, flipped on the long edge, set at 12 pt for older eyes. `hooks/study_sheet.py` adds it to every study that has an
`**In one sentence:**` thesis and a `## Discussion questions` list (99 pages as of 2026-10-22), in a
collapsed "Group study sheet" block under the questions, with a Print button. A printer icon
beside the title opens the block and jumps to it, since a leader decides to print from the top.

## What goes on it

| Page | What is on it |
|---|---|
| 1 | Title, `primary_passage`; the point (the thesis); Open: the first `questions:` frontmatter entry, else "what comes to mind when you hear …"; Read it aloud: `primary_passage` in WEB; Look closer: say / meant then / means for us, to write in |
| 2 | The primary graphic, as large as the page allows (the first comic, else the first drawn SVG that is a diagram rather than a 100-unit feast emblem); the study in brief: the Study outline, beside a tall graphic, under a wide one, or with room for notes when there is no graphic |
| 3 | The questions under the Study outline's steps, in the outline's order, each step's badge carrying its share of Discover and Wrestle's minutes (12–35, by question count); a step with no questions keeps its heading. Unmatched questions go under "Talk it over". A study with no outline of two or more steps groups them by facet under Discover 12–25 and Wrestle 25–35 instead. Each question gets the same ruled space whatever its length |
| 4 | Be transformed 35–40: the study's Be transformed question with room to answer, then its think / attitude / do; Memory verse: the first one; Pray together: the study's prayer; notes; QR code and URL back to the full study |

**12 pt is the floor.** Everything read on the sheet is 12 pt, labels 10 pt and the footer 9 pt,
and nothing shrinks to make room; a long passage loses verses to "Also read" instead. The graphic
is the exception: its text is drawn into the SVG for the web (bubbles at 14.5 of 720 units), so a
comic scaled to a page's height prints it at about 7 pt.

Everything is lifted from the rendered page, so the sheet adds no claims and needs no
verification of its own. The passage is in WEB because it is printed at length; ESV appears only
where the study already quotes it (questions, memory verse), under the same notice as the memory
verse cards.

## Two pages: each step with its questions

A **Two pages** checkbox by the Print button swaps the four pages for one sheet printed
double-sided, for a leader who does not know the study well. It is offered when the Study outline
has two or more steps that link their sections (93 of 105 sheets on 2026-10-26), and the browser
remembers the choice. It reads as one run from top to bottom:

1. **Open** and **Read it aloud** (the reference only).
2. Each outline step, numbered, with its note and up to three key verses (the reference lines of
   the section's quote blocks, when the note cites none), followed straight away by the questions
   that belong to it. A step with no questions stands as a framing step.
3. **Talk it over**, for any question no step claims.
4. **Be transformed**: its question, then the think / attitude / do.
5. **The point**, last, then the QR code.

**A question belongs to the step whose sections cite the most of its references.** References
are counted, not verses, so a four-verse range does not outweigh three single verses, and a tie
goes to the earlier step, where the group meets the verse first. A bare "4:13" is read in the
book of `primary_passage`, except straight after another reference in the same citation, and a
whole chapter ("Matthew 24") covers all its verses. A step that links several sections covers
all of them. Outline lines may be "Name — note" or "Name. Note". A question that cites no verse
falls to "Talk it over". The four-page sheet's page 3 uses the same matching.

The hook writes the blocks in order onto page 1, and `ssFlow` pours what does not fit onto page 2,
keeping a heading with the question under it. Answer spaces start at two lines. If page 2
overruns, the key verses go, then the QR code, then the gaps close up, then the step notes, then
the answers drop to one line; anything dropped that fits again once a later step has made room is
put back. The room left over is shared equally among every answer on both pages.

## How it fits

All sizes are in sheet millimetres (`--mm`, as in `memory-verses.css`), so the on-screen sheet is a
scale model of the page. The block, not the sheet, is the size container, so a sheet's own type
and padding scale with it too (with the sheet as container they followed the viewport, and the
preview stopped matching paper). Page 1 is fitted in the browser by `ssFit` (inline in the hook) on
open and on Print. It moves trailing passages to an "Also read" line, then trims verses from the
end; on page 2 it drops the outline's annotations, then the outline; page 3 closes up its gaps,
then drops the steps with no questions; page 4 drops its notes, then gives Be transformed's
question one line to answer in. A word count cannot do this:
the thesis, the opener and the passage all compete for the same height. The hook cuts any passage
past 500 words before shipping it.

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
reproduces the Print button. Check for overflow with `scrollHeight > clientHeight` on each `.ss-sheet`,
`.ss-main` and `.ss-questions`, and that nothing on a page reaches its footer. `pdftoppm -gray` and `-mono` simulate greyscale
and black-only printers. At the 12 pt redesign (2026-10-25), all 104 sheets fitted their four pages, 37 with
verses moved to "Also read".

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
