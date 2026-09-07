# Human review: the three things to read for

The agent skills check what can be checked mechanically — quotations against source, counts
re-derived, links resolved, claims re-run as SQL. This page is the other half: **the three things
that survive every automated pass and only a human reading notices.**

They were identified the way findings should be, from a real corpus. Each one is something the
author of this site corrected by hand across a study that had already passed two full adversarial
reviews and a clean `npm run validate`.

Read the draft once, straight through, and mark these three. Nothing else is as valuable.

---

## 1 · The antithesis construction

**What to look for:** `X, not Y` · `X — not Y` · `X rather than Y` · `not only X but Y`.

**The test:** delete the negative half. If the positive half still says everything, the contrast was
rhythm, and it goes.

**Why it matters:** it defines a thing by what it is not, so the reader receives the wrong version
first and has to discard it. Once, for a contrast a reader genuinely arrives holding, that is useful.
Every third sentence, it *adds fluff and destroys confidence* — the prose starts to sound like it is
arguing with an absent opponent instead of telling you what is true.

**The fix is upstream.** Detection does not work on this one — the count went *up* between
revisions of the same file, written by the same agent that had just cut them. It is now
[rule 5](style-guide.md#write-toward-this), a structural prohibition applied before drafting:
define affirmatively, and where a contrast feels necessary supply a concrete example, a count or a
citation instead of a foil. If you are commissioning the work, say so in the prompt.

**Calibration:** `prayer-as-communion.md` had 38 in 8,000 words, one every 210, after two reviews.
Assume any agent draft is over budget until counted:

```bash
f=docs/content/<study>.md
echo "$(grep -o ', not ' $f | wc -l) comma-form, $(grep -o 'rather than' $f | wc -l) rather-than"
```

## 2 · Essay register where devotional register belongs

**What to look for:** the analytical voice surviving into the parts of the study a reader is meant
to *use* — Key Takeaways, Be Transformed, the prayer, the application.

**The test:** could this sentence be spoken to someone? A prayer that reads like a paragraph about
prayer has not finished.

**The split is structural, not global.** Exegesis, word studies and evidence *should* be analytical;
that is where precision lives. It is the closing and applying sections that drift.

| Drifted | Landed |
|---|---|
| a sentence built on a hinge | a plain imperative |
| "the practical guard against a prayer life that silts up" | "pray as you walk, and before a meeting" |
| "let them know you better this year than last" | "let them know you better" |

## 3 · Is the theology addressed, or only described?

**The one the author of this site rates highest**, and the hardest to see, because nothing in the
sentence is wrong. What is wrong is what is absent, and an absence does not grep.

**The test, and it is a positive one:** for each section, finish the sentence *"this shows that God
___"*. If the study never prints that answer — if the reader has to assemble it from the exegesis —
the theology has been described rather than addressed.

Three follow-ups once you are looking:

- **Is the doctrine named?** Adoption, atonement, propitiation, justification. If the study
  paraphrases around a word the tradition already has, ask what the paraphrase gained.
- **Is the person named?** "Your Son Jesus", not "your Son". A prayer that closes on "Amen" alone.
- **Does it reach the reader?** A doctrine that never gets to *"so you may…"* stopped short. Key
  Takeaways, Be Transformed and the prayer are where to check.

**What this is not.** Not licence to overclaim. Where a reading is genuinely contested the study
should say so and give both sides, and this corpus does that well — keep it. The target is the
*unmarked* middle, where the prose is careful enough that a reader cannot tell whether they are
being told a settled thing or a disputed one. Marked uncertainty is precision.

**Why it is worth reading for rather than searching for.** The hedging vocabulary you would expect —
*in some sense*, *can be seen as*, *arguably* — was measured across this corpus at single figures in
~90 files. There is no phrase to catch. Every real instance was accurate, unhedged prose with the
name left out.

---

## Why these three and not a longer list

Because a longer list does not get used. [style-guide.md](style-guide.md) carries the full diagnostic
set for the agent to work through; this page is what a human should hold in their head on one
read-through.

The pattern behind all three is the same, and it is worth naming: **an agent drafting this material
drifts toward sounding careful.** The antithesis sounds balanced. The essay register sounds rigorous.
The unnamed theology sounds measured. All three trade authority for the appearance of it, and all
three are subtraction problems — say the true thing once, plainly, and name it.
