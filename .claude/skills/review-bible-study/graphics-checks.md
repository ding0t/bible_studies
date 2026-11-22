# Review: comic and diagram checks

A study's comic and drawn plates make claims of their own, in poses, props, labels, legends and
spans, and a quotation can be word-perfect while the picture around it is wrong. Run these checks on
every comic in `docs/data/comics/` and every plate a study embeds. The comic is drawn by the
one-minute-comic skill and the plates follow
[drawn-graphics.md](../develop-bible-study/drawn-graphics.md); this page checks what they produce.

The list was first run on `docs/content/jesus/melchizedek-priesthood.md` (2026-11-22). Its
quotations all matched the ESV, and it still found 3 errors and 8 should-fixes, all in what the
graphics claimed around those quotations. Each check gives one example from that review.

Severity follows [SKILL.md](SKILL.md#reporting). A graphic that puts a reading in Scripture's mouth,
or draws something the text contradicts, is as serious as the same claim in prose.

**Status** says what a tool does today: *automated* (a command runs it), *automatable* (a tool
could do it, and none does yet) or *judgement* (a reader must).

## Comic

| # | Check | Status |
|---|---|---|
| 1 | Run `python3 utils/build_comics.py --verify` on every `source = "esv"` bubble. Required, even though it usually passes. | automated |
| 2 | Compare `python3 utils/build_comics.py --alt <slug>` with the alt text in the study's embed. | automatable |
| 3 | Render at 2800px and look at each panel alone. A 1400px view hid a priest behind a text box and Jesus's posture. | automatable: render and crop each panel |
| 4 | **Poses and props.** For each figure, ask whether the text gives the gesture, and whether the prop's catalogue meaning imports a reading. Melchizedek raising the Last Supper's cup suggested a communion reading Hebrews never makes. | judgement; a tool could list each panel's poses and props with their `cast.md` descriptions |
| 5 | **Posture.** Check seated, standing and enthroned figures against the text's own words. Jesus sat on the ground below the throne where Hebrews 8:1 has Him "seated at the right hand of the throne". | judgement |
| 6 | **Caption agency.** Whose act or words does each caption assign? "David writes an oath" gave David the LORD's oath (Psalm 110:4). | judgement |
| 7 | **Colour and costume collisions.** Compare a new figure's colours and `cast.md` wording against every generic role and reserved figure. Purple and gold on Melchizedek echoed the harlot of Revelation 17:4, and a banded head cloth on Abram read as a priest. | automatable: hue distance on the cast hex values, duplicate colour words in `cast.md` |
| 8 | **References cover claims.** Every claim in a caption and in the `point` has a verse that says it, and each panel's `ref` covers its caption. "Risen" needed Hebrews 7:16; "one sacrifice finished" needed Hebrews 7:27. | automatable: flag caption verses missing from the TOML header |
| 9 | **Hidden figures.** No figure is fully covered by a bubble or text box. | automatable from figure positions and bubble boxes |
| 10 | **The point.** Map the study's one-sentence point to the panels and name any part no panel draws. | judgement |
| 11 | **Foils.** Run the style guide's `X, not Y` check on the `note`, captions and `point`. "Background, not Scripture" was one. | automatable |

## Diagram

| # | Check | Status |
|---|---|---|
| 1 | Check every quotation word for word against `study_verse`. | automatable: extract the curly-quoted strings and their references from the generator |
| 2 | **The clause a quotation hangs on.** Re-read what condition the plate attaches to it. "Under the Law, Jesus 'would not be a priest at all'" replaced Hebrews 8:4's own "if he were on earth". | judgement |
| 3 | **Labels.** Is each column, row and banner label true of everything under it? A gold column headed "THE ORDER OF MELCHIZEDEK" made Melchizedek the subject of rows said only of Jesus. | judgement |
| 4 | **Era labels against dispensational boundaries.** Does "after X" imply X has ended? "AFTER THE LAW" put David outside the Law; Hebrews 7:28 says "later than the law". | judgement |
| 5 | **Spans.** Where does the text start and end each count? What other spans does it count between the same stations? Does a "not to scale" or "only span" note hold? The 430 years of Galatians 3:17 was drawn from Genesis 14 though it counts from the covenant of Genesis 15, and 1 Kings 6:1 counts a second span. | judgement; a tool could search for counted spans between the stations |
| 6 | **Legend honesty.** Does a legend item claim more than the text gives, and is anything inferred drawn solid? "The text dates it" stood where the text gives only the order. | judgement |
| 7 | **References on cards.** Does each card's reference cover every claim on it (each lineage link, "risen", "throne")? | judgement |
| 8 | **Attribution by grammar.** Does a sentence place the study's reading in the text's mouth? "Hebrews calls them copies, like a coin struck from a die" credited the study's picture to Hebrews 9:24. | judgement |
| 9 | Compare each plate's `<desc>` and the study's alt text against what the plate draws. | automatable: diff them |
| 10 | **Grammatical labels.** Check the morphology behind each one. ἀφωμοιωμένος is tagged V-RPM/P, middle or passive in form, so "passive" became "usually read as passive". | automatable against `bible_grammar` |
| 11 | **Placement.** Is each plate beside the prose it illustrates? | judgement |
| 12 | Confirm the SVG on disk matches the generator's current output. | automated: rerun the generator and diff |
