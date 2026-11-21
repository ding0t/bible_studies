# Review: format checks

The format-specific half of review-bible-study Phase 8 ([SKILL.md](SKILL.md#phase-8--style-guide-pass)).
Run each check that applies to the study; the severity of each is given with it, and the phase's
overall severity rule in SKILL.md still governs.

**Check the discussion questions against
[discussion-questions.md](../develop-bible-study/discussion-questions.md)**, not only against
style-guide.md's prohibition. Two different findings live here. The prohibition catches a question
about the study's own method — including the disguised form, a question about evidence-weighting
technique rather than about the text. The facet table catches the commoner defect: a set that is
individually fine and collectively stale, because the study was restructured and the questions were
not re-read. Ask which facets the study now has — language, context, Christ, the hard part,
transformed — that no question touches, and whether the set's proportions match the study's own. A
study whose smallest section gets most of its questions has a set left over from an earlier draft.
Report as **Minor**, or **Moderate** where the questions no longer reflect what the study argues.

**If the study has a Key Takeaways → Be Transformed subsection, check it against
[key-takeaways.md](../../../docs/content/about/key-takeaways.md#be-transformed).** The default
shape is three labeled bullets — `**Think.**`, `**Attitude.**`, `**Do.**` — and a study that instead
has a prose paragraph, an unlabeled list, a different bullet count, or custom labels has drifted from
the site's convention unless the study genuinely can't be split three ways. A bullet with no
Scripture reference is Minor: each names the verse it stands on. This is the same failure
class as the discussion-questions check above: each shape is individually readable, so nothing looks
wrong until the corpus is read side by side. A 2026-09-19 audit found 6 of 29 published studies with
a Be Transformed subsection had drifted this way with no stated reason — this is corpus-wide drift,
not a rare exception, so check every study that has this subsection rather than only flagging one
that looks obviously off. Report as **Minor**.
Then check the content against
[be-transformed.md](../develop-bible-study/be-transformed.md)'s per-label tests: a Think that is
an instruction, an Attitude you could finish and tick off, or a Do that is a restatement, an inward
review with no next step, or an action with no verse behind it. A Do the passage itself supplies
(its command, its prayer, its model) is the target; when the passage offers one and the Do ignores
it, name it in the finding. Report as **Minor**.

**If the study has a Memory verses subsection, check it against
[key-takeaways.md](../../../docs/content/about/key-takeaways.md#memory-verses).** The standard shape
is a block quote with the reference written plainly, and no explanatory sentence after the verse
(a bare "See [section]" locator in a study with several parallel sections is the one exception).
The corpus still mixes shapes -- some studies use a bulleted `**Reference** -- "quote"` line, and a
few fold the citation into a paragraph -- so report a different shape as **Minor** (known corpus
cleanup). A reference linked to Blue Letter Bible or another Bible site is also **Minor**: the
site's pop-up opens every plain reference in place, and the links were removed on 2026-09-27; only a
deliberate send-off for follow-up study, saying so in its link text, keeps one. An explanatory
sentence tacked onto a verse is **Minor** as well, but flag it by name since it's the part of this
shape that's a genuine defect rather than a pending conversion.

**Check the balance between prose and pop-up** against [formatting.md](../develop-bible-study/formatting.md) ("The pop-up
works alongside the prose"). There are two findings, one in each direction. A section that argues
from a verse's wording while giving only its citation leaves the reader arguing from words they
cannot see. Nothing pops up when the study is read aloud, and the pop-up shows the reading translation (the BSB), so report
this as **Moderate**. A quotation or paraphrase the argument never uses, kept only to save a lookup,
is **Minor**; recommend simplify-bible-study.

**Measure any mermaid diagram in the file** against
[diagrams.md](../develop-bible-study/diagrams.md). A diagram wider than ~560px is scaled down whole
by the browser, labels with it, and the defect is invisible in the markdown — the source of a 3725px
diagram reads exactly like the source of a 400px one, so this is a finding no amount of careful
reading produces. Render it (`npx mmdc -i d.mmd -o d.svg` and read the `viewBox`) rather than
estimating from node count. The corpus was measured and cleared on 2026-09-04, so a diagram under
50% now is a regression rather than inherited debt.
Report as **Minor**, or **Moderate** under ~35%, where the labels are no longer legible at all and
the diagram is decoration.
