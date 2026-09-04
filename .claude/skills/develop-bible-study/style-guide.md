# Style guide: writing that doesn't sound AI-generated

Phase 7 of [SKILL.md](SKILL.md) links here. This isn't about content — the exegesis-before-hermeneutics
method, the word studies, the citation discipline all stay exactly as demanding as the rest of this
skill requires. It's about the surface of the prose: the tics that make a well-researched study *read*
like an LLM wrote it, which undercuts the reader's trust in the research underneath.

## Write toward this

**Four rules, and they are the whole guide.** Everything after this section is diagnostic — the
specific shapes prose takes when it drifts off these four, with corpus evidence behind each. Write
toward the four and the drift mostly doesn't happen; check against the tells and you only catch
instances, one at a time, forever. Use these from the first sentence of the first draft, not as a
pass at the end.

**1. Every sentence adds a fact, a citation, or a step in the argument.** This single rule subsumes
most of the page. An announcement adds none of the three. A restated conclusion adds none. A straw
contrast adds a fact about nobody. A grader adjective adds emphasis where evidence should go. If a
sentence carries only rhythm, it is already the defect — you never have to work out *which* tell it
is.

**2. Name the actor and show the mechanism.** *"Jubilees is doing exegesis here. It has a problem in
Genesis 2:17 — a sentence saying Adam will die in a day, and a narrative in which he lives 930 years
— and it solves the problem by taking the thousand-year day as the text's plain sense."* Not *"this
is an exegetical solution, not a mystical flourish."* Mechanisms are what you supply; categories are
what the reader concludes. When you find yourself asserting what kind of thing something is, show
how it works instead and delete the assertion.

**3. Lead with the fact.** Put the load-bearing thing in the first clause of the first sentence.
*"The Temple ran on it."* Whatever would have introduced it — how clear the evidence is, how
significant, what it demonstrates, that it is about to be demonstrated — is either unnecessary or
belongs after the fact rather than in front of it.

**4. Let the citation carry the emphasis.** A verse reference, a daf number, an occurrence count, a
manuscript variant and a date are each stronger than any adjective available to you. Reaching for
*decisive*, *striking* or *remarkable* is usually a sign of being short on evidence rather than short
on vocabulary — go and get the reference instead.

**Two tests, both cheap.** *Deletion*: cut the sentence, re-read the paragraph, and see whether any
fact, citation or step went with it. *Skim*: read the draft and notice what your eye slides past to
get to the content — that reflex **is** the finding, and it is exactly what the reader will do.

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

**This is a template with an open slot, exactly like `worth ___` below, and it has to be learned the
same way — by shape, not by specimen.**

> ⟨announcement that a point is arriving⟩ + ⟨the point⟩

The announcing half fills endlessly: *"Note what this is,"* *"Notice that…,"* *"What's happening
here is…,"* *"What it contains is…,"* *"What comes bundled with it is…,"* *"The thing to notice
is…,"* *"That matters, because…,"* *"This is precisely…,"* *"Credit where due,"* *"Against
overreading."* Cut the announcement and keep the point; it stands on its own. Say the observation,
don't narrate that an observation is arriving.

**It travels with a straw alternative.** Announcing a point opens a slot for a contrast, and the
contrast is generally against something nobody proposed:

> ⟨announcement⟩. It is not ⟨straw⟩; it is ⟨the real thing⟩.

*"Note what this is. It is not a mystical flourish; it is an exegetical solution."* Both halves are
overhead — no reader had suggested a mystical flourish, and the sentences that follow were going to
demonstrate the exegesis anyway. Replace the construction with the demonstration: show the mechanism
and the category takes care of itself. (*"Jubilees is doing exegesis here. It has a problem in
Genesis 2:17 — a sentence saying Adam will die in a day, and a narrative in which he lives 930
years — and it solves the problem by…"*)

**Where this is actually produced is revision, not first drafting.** The rule near the bottom of this
page — that throat-clearing gets added while tightening the transition around a sentence, "which is
exactly backwards" — bites hardest here. On `last-things/day-is-a-thousand-years.md`, four instances
were cut in one pass and **three more appeared in the next two revisions of the same paragraphs**,
each written within an hour of the cut, by a writer who had just finished removing them. Re-run this
section after every substantive rewrite, not only before `draft: false`.

**`npm run validate` will not catch any of it.** Its four style checks are `worth ___`, the "rather
than" virtue contrast, bullet length, and reader-reassurance address. Every announcement listed above
passes them clean, which is why a green validate run is not evidence this section was done.

### `worth ___` is a template, not a phrase

This one gets its own heading because it is the single tell that keeps getting through, and the
reason is worth understanding: **it is not a fixed phrase, it is a template with an open slot.**

> it is/it's **worth** ⟨being clear / noting / stating / saying / asking / flagging / remembering /
> pointing out / bearing in mind / a mention⟩ **that**…

Every other tell on this page is a near-fixed string, so knowing the string is enough to avoid it.
This one generates endlessly. An audit of `docs/content/` found the other eight families at 0-3
instances each and this one at **48** (`npm run validate` reports the live count) — not because the
rule was missing, but because the guide used to list three specimens ("Worth noting," "It's worth
asking whether," "One further point worth making") and a writer avoiding those three will still
happily produce *"it is worth being clear that."* Learn the shape, not the examples.

The cost is exactly what it looks like: the slot-filler verb is doing no work. *"Matthew's word for
Judas' response is worth noting. He 'changed his mind'…"* → *"Matthew's word for Judas' response:
he 'changed his mind'…"*

**Check for a doubled claim underneath it.** This construction attracts the *restated conclusion*
tell from the section below, because announcing a point and then making it invites saying it twice.
From a published study:

> Scripture never explains this, and it is worth being clear that no verse comments on it.

"Scripture never explains this" and "no verse comments on it" are one claim wearing two coats.
Fourteen words doing four words of work: *"Scripture never explains this."* When you cut a `worth
___`, re-read what's left on both sides of it — the redundancy is usually still sitting there.

**Where it earns its place.** Not every instance is filler, which is why the validator flags this at
warning level rather than as an error. *"Each proposal is worth stating and declining"*
(`biblical-figures/james-son-of-alphaeus.md`) tells the reader the shape of the next four paragraphs
— state each theory, then reject each — and deleting it loses that. The test is the same as
everywhere else on this page: **delete it and re-read.** If the paragraph still says everything it
said, it was filler. Roughly a third of the corpus instances survive that test; two thirds don't.

## The tell: narrating your own editorial virtue

The root of the section above, stated generally, because it generates more than one surface form:
**do the honest thing; don't also tell the reader you're doing it.** Disclosing a dependency, naming
a weakness in your own argument, admitting a text is difficult — all good. Commenting on the fact
that you disclosed it is the writer awarding himself marks. The disclosure already *is* the
disclosure.

Three shapes, all from published studies on this site:

**The virtue contrast** — the commonest, and the easiest to spot once named:

> ⟨did the honest thing⟩ **rather than** ⟨smoothing it over / letting it stand / hiding one /
> burying it / discovering it⟩

*"That's worth saying plainly rather than smoothing over."* / *"This site's own position, stated
plainly rather than smoothed into Larkin's chart."* / *"a textual difficulty rather than hiding
one."* The trailing clause names an alternative nobody proposed and the writer was never going to
take, so an ordinary act of reporting gets dressed up as courage. Cut the contrast, keep the fact:
*"That's worth saying plainly"* → *"Say it: …"*, then say it.

**The connective varies, and `rather than` is only the commonest one.** `not by`, `not from`,
`instead of` and a bare `not X — Y` build the same shape, and Check 11's regex sees none of them.
*"Every cut-off here was set by measurement, not by taste"* stood in `how-we-cross-reference.md`
through a full review and a green validate run: *not by taste* charges an alternative nobody
proposed, and the sentence carried no fact the corroboration table directly beneath it did not
already show. It was deleted rather than rewritten — usually the right move, because the contrast
tends to be the whole sentence. This is the `worth ___` lesson again: learn the shape, not the
specimens.

**The disclosure announcement** — a heading or lead-in advertising candour before delivering it:
*"One dependency to state plainly."* / *"I'll say plainly:"* / *"One honest complication belongs
here."* Name the thing, not your posture toward it. *"One dependency to state plainly."* → *"One
dependency."*

**The reader-benefit tail** — explaining what the reader gains from your having been forthcoming:

> The structural claim rests on it, **and a reader should know that rather than discover it.**

Fourteen words asserting that the preceding sentence was useful. Delete it; the sentence was already
useful. (This one stacks all three shapes at once — an announcement opening the paragraph, a virtue
contrast closing it, and a reader-benefit clause carrying the contrast. That is the usual way these
arrive: not singly, but reinforcing each other around a fact that needed none of them.)

**The test, and the real exception.** Instructions *to the reader* are not this tell. Rapture.md's
*"Note anything that doesn't fit cleanly, rather than smoothing it over"* tells the reader what to do
with their own study — the contrast is doing real work, because smoothing over is exactly the thing
they might otherwise do. The tell is when the subject of the virtue is **you, the writer**. Ask: *am
I telling the reader what to do, or telling them how well I did?*

`npm run validate` flags the virtue contrast at warning level (Check 11); the other two shapes are
too varied to detect mechanically, so they are on you.

## The tell: hedging as a reflex

The most damaging version of everything above, because it hides inside a real virtue. A study that
names its own weaknesses is doing exactly what this site asks. But once the habit sets in, every
caveat starts arriving pre-wrapped in an announcement that a caveat is coming, and the page becomes
a performance of honesty rather than a piece of honest work.

**The rule that matters: keep the caveat, cut the frame.** These are two separable things and only
one of them is the problem:

| | |
|---|---|
| **Caveat** — keep | "standard commentary treats ἐκ τῆς ὥρας as genuinely ambiguous between 'keep you from undergoing' and 'keep you through'" |
| **Frame** — cut | "but it's worth being direct about how contested the underlying Greek actually is" |

Do not fix this by deleting the honesty. The specific, checkable admission is the valuable part of
the sentence; the sentence announcing that an admission is imminent is pure overhead. Cutting the
wrong one makes the study worse.

Four shapes, all from `last-things/rapture.md`, which at review time carried **29** instances of
"rather than" and 16 disclosure frames in 283 lines:

**The disclosure wrapper.** *"Worth being direct about the sourcing here…"* / *"A counter-argument
worth engaging, not skipping past."* / *"A claim worth naming, and being direct about what can and
can't be checked."* Delete the sentence; start at the caveat.

**The trailing maxim** — an abstract general principle bolted onto a concrete choice to justify it:

> …naming real, live counter-arguments rather than hiding them, **because a conclusion that can't
> survive its own best objections isn't as strong as one that's been tested against them.**

The clause is unfalsifiable, true of all arguments everywhere, and tells the reader nothing about
the rapture. Related to the *vague hedge-tail* below, but worse: that one commits to nothing, this
one commits to a platitude.

**The repeated caveat.** Say a limitation once, where it applies. Rapture.md states "this is
typology, not proof" four separate times (lines 25, 100, 110, 128). Repetition doesn't make a
qualification more honest; after the second time it reads as anxiety, and a reader starts skimming
for where the actual claim resumes.

**The caveat cross-reference** — a caveat that cites another caveat elsewhere in the document to
establish a track record of caveating: *"the same way this study flags its patristic evidence below
rather than overclaiming it"* / *"per the caveat given there"* / *"Same verification limit as the
Pseudo-Ephraem citation above."* State the limit; don't build a citation network out of your own
modesty.

## Structural readability

Three failures that aren't about word choice at all, and that no grep will find.

**Bullets that are essays.** A bullet is a promise of brevity — breaking it is worse than never
having used one. Rapture.md has a single bullet of **344 words** (2 Thessalonians 2:6-7, the
restrainer) and another of 257. Anything past roughly 60 words wants to be a paragraph, a
sub-heading, or three bullets. If the content genuinely needs 300 words, it needs a heading.

**The study talking about itself.** *"This study argues…," "This site reads…," "this study flags…,"
"what this study can verify."* Rapture.md does this **19 times**. Occasional use is fine and
sometimes necessary — distinguishing this site's position from a source's is real work. As a habit
it turns a study about Scripture into a study about the study. Prefer stating the conclusion: *"This
site reads that as a promise to be kept from the hour itself"* → *"That reads best as a promise to be
kept from the hour itself."*

**The section recap.** The sentence-level *restated conclusion* below has a section-level twin: a
closing paragraph that re-lists what the preceding paragraphs just established. Rapture.md's "Taken
together: three men removed bodily…" recaps four paragraphs the reader has just finished. End on the
last real point.

**A note on discussion questions.** They are for the reader to think about *the subject*, never about
the study's own method. Two of rapture.md's four ask the reader to evaluate the page's handling of
itself — *"Did seeing those objections named change how persuasive the conclusion felt to you?"* /
*"Did that distinction change how you weighed that section…?"* — which solicits credit for the
caveats rather than provoking thought about Scripture. Ask about Enoch and Noah, not about your
own even-handedness.

## The tell: the apologia posture

Every other rule on this page works at the sentence. This one works at the whole document, which is
why it survives a careful line-by-line pass — `about/why-ai-assisted-study.md` triggered **zero**
validator warnings while being, from top to bottom, a defence against an accusation nobody had made.

**The governing principle: defending against an implied deception implies there is one.** A page that
works to reassure the reader that it is honest reads less trustworthy than one that simply states its
method, because the reassurance is evidence the author expected to be doubted. Disclosure already
made does not need to be re-earned in every paragraph.

**The reader-reassurance address** is the surface form, and it is unmistakable once named:

> I use AI to help research and draft the studies on this site. **You deserve to know that**, and to
> know exactly what that does and doesn't mean — so here it is in one page.

*"You deserve to know," "rest assured," "you can trust that," "I want to be clear with you," "let me
be clear."* All of them tell the reader how to feel about the disclosure instead of making it. Cut
the clause; the disclosure was the first sentence and it was already complete.

**The oath register.** Watch for promises escalated past the weight of the fact: *"one
non-negotiable,"* *"That gate does not move,"* *"Volume is not the goal and never has been,"*
*"Errors here are mine. Not the tool's."* Emphasis substituting for information. "A human reads every
line against the text before it is published" states the same policy and asks for no credit.

**Sections built out of denials.** A heading like *"What this is not,"* followed by four paragraphs
each beginning "It is not…," is the posture made structural. Denial concedes the accusation's frame.
Retitle to what the section actually establishes — *"Where it stops"* — and the same four paragraphs
become a statement of scope.

**The fix is a change of genre, not of wording: apologia → specification.** Ask what a methods
section in a paper would say. It would state what was done, what the known failure modes are, and
what controls were applied — with no sentence anywhere about the author's sincerity. Every fact on
the page survives that translation; only the posture doesn't.

**This is not an argument against disclosure or against caveats.** Say the true and awkward thing.
The rule is that saying it is sufficient — it does not also need defending, justifying, or
emotionally framed for the reader.

## The reading test that catches all of this

When reviewing a draft, notice what you **skim**. If your eye slides past a sentence to get to the
content, that sentence was overhead — and the reflex to skip it is better evidence than any rule on
this page, because it is the same thing the reader will do. Anything you find yourself discarding as
irrelevant while reading is a readability defect, not a neutral observation about your attention.

On rapture.md, an honest pass discarded: the whole five-step *Approach* section (process narration
that belongs in the study-state YAML — see the genre exception below, and note that it tells the
reader nothing about the rapture), the "Taken together" recap, *"and for good reason,"* every
disclosure wrapper, and two of the four discussion questions. That is the review, and it took one
read-through with attention paid to skipping.

### The genre exception

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
[melchizedek-priesthood.md](../../../docs/content/jesus/melchizedek-priesthood.md)) is
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
highlights, notably, importantly, that said`. None of these are banned outright — the test for each hit
is "does this word add information, or just add volume?" Delete the ones that fail that test; leave the
ones that pass it.

Grep separately for `worth` — as a template with an open slot it can't be caught by a word list, and
it is the tell most likely to still be in the draft. `npm run validate` also flags it (warning level,
Check 10), so a clean validate run is the faster way to find every instance.

## If you only remember one thing

Not the tell list — the four rules in [Write toward this](#write-toward-this). Every diagnostic on
this page exists because prose drifted off one of them, and the list will always lag the drift: each
new variant needs a new entry, which is why `worth ___` reached 48 instances in a corpus where the
rule was already written down. Writing toward "every sentence adds a fact, a citation, or a step"
makes the variants stop being generated in the first place.

## Why this is worth a pass of its own

AGENTS.md asks this project to read as careful, sourced, human scholarship — a study a reader can check
against the text and the citations, not prose to be taken on faith. Rhetorical padding doesn't make an
argument more rigorous; it just adds friction between the reader and the evidence already doing the
work. The fix is almost always subtraction, not rewriting: say the true thing once, plainly, and stop.
