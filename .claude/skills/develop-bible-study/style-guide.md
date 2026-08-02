# Style guide: writing that doesn't sound AI-generated

Phase 7 of [SKILL.md](SKILL.md) links here. This isn't about content — the exegesis-before-hermeneutics
method, the word studies, the citation discipline all stay exactly as demanding as the rest of this
skill requires. It's about the surface of the prose: the tics that make a well-researched study *read*
like an LLM wrote it, which undercuts the reader's trust in the research underneath. Run this pass after
a draft is otherwise done, not while first getting ideas down.

## The tell: words that assert confidence instead of earning it

Bare intensifiers — **genuinely, truly, actually, really, certainly, indeed, undeniably** — let a
sentence claim something while also pre-empting the reader's doubt about it, without adding any
information. "God's provision is genuinely abundant" claims nothing "God's provision is abundant"
doesn't; the extra word is there to sound more sure, not to be more sure. Cut it — don't swap in a
synonym, just delete it and read the sentence again. It's almost always stronger bare.

(This is not the same as *actually* used for real contrast — "it wasn't Moses who gave it; it was, in
fact, the Father, present tense" earns its emphasis because it's correcting a stated alternative. The
tell is the word doing work no contrast requires.)

Same instinct, different target — watch for grader adjectives applied to nearly everything: **decisive,
crucial, profound, striking, remarkable, powerful, rich, compelling.** If every claim in a study is
"decisive," none of them are. State the fact and let it carry its own weight; reserve a strong adjective
for the one place in the study that actually earns it by comparison to everything around it.

## The tell: narrating the argument instead of making it

Phrases like *"Credit where due,"* *"Against overreading,"* *"Worth noting,"* *"It's worth asking
whether,"* *"One further point worth making"* announce that a point is coming instead of just making it.
Cut the announcement; the point stands on its own. Same family: *"Notice that…,"* *"What's happening
here is…,"* *"This is precisely…"* — say the observation, don't narrate that an observation is arriving.

This is a genre distinction, not a blanket rule: the study-state YAML files under
`references/study-state/` are exactly the right place for process narration ("checked and deliberately
NOT added," "the honest result is mixed") — that's the research trail the state-tracking system exists
to keep. It just shouldn't leak into the reader-facing markdown file.

## The tell: sentences that don't survive being deleted

This is the brevity problem, and it's distinct from the word- and phrase-level tics above — a sentence
can be free of every banned word and still be waffle. The test: delete the sentence and read the
paragraph again. If nothing is lost — no fact, no citation, no step in the argument — it wasn't carrying
weight; it was carrying rhythm. Cut it.

Four recurring shapes this takes, all pulled from actual drafts of this study:

**The pure signpost**, announcing a section instead of starting it: *"Three more Old Testament threads
run straight into these accounts."* / *"One more verified detail."* / *"Two more explicit threads, both
outside John 6 but pointed at by it."* The heading or the next sentence already does this job — delete
the announcement and start with the content.

**The restated conclusion**, saying what the previous sentence just said, in vaguer words: *"Four
Gospel writers, two feedings, ten occurrences, not a single crossover in either direction. **Whatever
else the accounts do, they are not confused about which meal they describe.**"* The second sentence adds
nothing the first didn't already establish more precisely.

**The vague hedge-tail**, bolted onto a real fact to make it sound like it means more than it says:
*"The feeding of the 5,000 is the only miracle in all four Gospels — **which says something about how
central the early church took it to be.**"* "Says something about" commits to nothing; either state
what it says, or stop at the fact.

**The redundant triple**, saying one idea three times as if repetition were evidence: *"None of this is
stated in Scripture, **none of it is anything Mark or John does with the numbers**, and **no doctrine
here depends on it**."* Pick the strongest phrasing and cut the other two.

Watch for these especially in your own second and third drafts of a paragraph — the first pass usually
has the real sentence; the throat-clearing gets added while tightening the transition around it, which
is exactly backwards.

## The tell: rhetorical rhythm on autopilot

**The "Not X — Y" contrast.** Useful the first time in a section ("Not punished for being hungry —
punished for despising sufficiency"). Load-bearing the second time. A tic by the third — if a
section leans on it more than twice, cut back to the strongest instance and rewrite the rest plainly.

**Em-dash density.** One em-dash aside per sentence reads as controlled. Two pairs in one sentence, or
one pair in almost every sentence of a paragraph, reads as scaffolding holding up thoughts that were
never fully connected into prose. Try a period or a comma before reaching for another dash.

**Rule-of-three padding.** Lists of exactly three adjectives or examples, reached for out of rhythm
rather than because three is actually how many there are. If two examples make the point, stop at two;
if there's a fourth that actually adds something, keep it — don't trim a real fourth just to hit three.

**Summarizing what the paragraph you just wrote already said.** *"So, to sum up…"* / *"In short…"* right
after making the point. Trust the reader to have read the paragraph; end the section on the last real
point, not a recap of it.

## Hebrew/RTL text and markdown bold

Never wrap Hebrew or Aramaic text in markdown bold (`**...**`) — not even with a transliteration
nested inside as italics. It renders broken: browsers fake ("synthetic") a bold weight for scripts
the font stack has no real bold glyphs for, which is true of Hebrew niqqud (vowel points) in most
web font stacks, and synthetic bold reliably misplaces or drops combining marks. This has hit
published studies more than once — `**דֶּרֶךְ (*derek*, H1870...)**`-style spans are the recurring
shape of the mistake, and by the time it's caught the file is already `draft: false`.

The fix, already established elsewhere on this site
([why-ai-assisted-study.md](../../../docs/content/about/why-ai-assisted-study.md)'s
`<span dir="rtl">חֶסֶד</span>` example): wrap the Hebrew glyphs themselves in
`<span dir="rtl">...</span>`, left unbolded, and keep any bold on the surrounding English lead-in
text instead — `**Name and city.** Melchizedek — Hebrew מַלְכִּי־צֶדֶק (*malkî-ṣedeq*)...` (from
[melchizedek-priesthood.md](../../../docs/content/studies/theology/melchizedek-priesthood.md)) is
the working pattern: bold the English label, leave the Hebrew itself plain (a `dir="rtl"` span adds
correct directional isolation on top of that, worth adding whenever the Hebrew sits inline next to
Latin punctuation like a following parenthesis). Greek doesn't have this problem — bold-wrapping
Greek (`**ὁδός**`) is safe and common throughout this site's studies; this rule is specific to
Hebrew/Aramaic's RTL script and its combining vowel points.

`npm run validate` catches this automatically (Check 9 in `app/scripts/validate-content.js`, an
**error**-level finding) — run it before flipping `draft: false` rather than relying on a visual
re-read, since the broken markdown/HTML source looks completely unremarkable and the breakage only
shows up in the rendered page.

## A pre-publish check

Before a draft goes to `draft: false`, grep it for: `genuinely, truly, actually, really, certainly,
indeed, crucial, profound, compelling, delve, tapestry, boundless, unwavering, testament to, underscores,
highlights, notably, importantly`. None of these are banned outright — the test for each hit is "does
this word add information, or just add volume?" Delete the ones that fail that test; leave the ones
that pass it.

## Why this is worth a pass of its own

AGENTS.md asks this project to read as careful, sourced, human scholarship — a study a reader can check
against the text and the citations, not prose to be taken on faith. Rhetorical padding doesn't make an
argument more rigorous; it just adds friction between the reader and the evidence already doing the
work. The fix is almost always subtraction, not rewriting: say the true thing once, plainly, and stop.
