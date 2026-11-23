---
name: one-minute-comic
description: Draws a "one-minute comic" for a study in docs/content/ -- three to six panels with speech bubbles, a reusable cast (Jesus, the authorities, a crowd, the healed man, disciples, soldiers) and named story layouts, that tells the study's main point so a reader gets it in a minute. Written as a TOML file in docs/data/comics/ and rendered by utils/build_comics.py. Use when the user asks for a comic, a comic strip, a one-minute comic, speech bubbles, a cartoon of a passage, or "tell the main point as a story" -- as opposed to drawn-graphics.md's charts and imagery plates, which explain rather than narrate.
---

# The one-minute comic

A study's point is one sentence. The one-minute comic tells that sentence as a story a reader takes
in before the first heading: who was there, what they said, what it showed. Open the nearest
existing comic beside this file: `you-are-gods` (an exchange and a verdict), `peter` (a life in six
beats), `bread-of-life` (two events compared), `two-witnesses` (one story echoing another, almost
wordless).

A comic is a TOML file in `docs/data/comics/` naming parts that live in `utils/lib/comic.py`, so a
corrected line is one edit and a re-run. What there is to draw with (cast, poses, scenes, props,
layout devices, bubble options, emphasis tools) is catalogued in [cast.md](cast.md); this file holds
the rules.

```bash
python3 utils/build_comics.py <slug>         # docs/data/comics/<slug>.toml -> docs/content/assets/img/comics/<slug>.svg
python3 utils/build_comics.py --alt <slug>   # the alt text, every panel and every word, for the embed
python3 utils/build_comics.py --cast         # cast.svg and emphasis.svg beside this file
python3 utils/build_comics.py --draft <slug> # render despite layout faults and list them
python3 utils/build_comics.py --verify <slug># every source = "esv" bubble checked against the ESV of its panel's ref
qlmanage -t -s 1400 -o <scratchpad> docs/content/assets/img/comics/<slug>.svg   # render and look
```

## 1. Read the study for the comic

Read the whole study first. Each part feeds one part of the comic:

| In the study | Becomes in the comic |
|---|---|
| `**In one sentence:**` | What the comic shows. **Its grammar picks the layout**: "X, then Y" is a sequence; "X and Y compared" is `contrast` or `two-tables`; a type and its fulfilment is `echo`; a life is `call-pairs-mission` |
| The passage's words, and who speaks them | The bubbles (section 2). Who has *no* recorded words is a finding too |
| "What X shows about God", Be Transformed | `point`, landed on the reader ("so you…") with its verse |
| "Contested", "this study holds" | What needs a dashed `aside`. An identification the text does not make is never drawn as fact |
| Word studies and stated numbers | Visual details: a distinction the Greek keeps is two different objects; a count is drawn as that many |
| Setting the study cites (season, terrain, feast) | Scene, sky and caption, each with its verse in the TOML header comment |
| Tradition, study-Bible opinion, other readings | Left out. A minute holds the text and the point |

A study with no `**In one sentence:**` line needs one first (simplify-bible-study, Phase 1).

## 1a. Find the beats

The beats are the moments that *show* the point. Choose a layout by what the story has to do:

| Layout | Panels | Story shape |
|---|---|---|
| `setting-exchange-reveal` | 1 / 2 / 1 | Scene, two lines of exchange, the reveal |
| `setting-exchange-evidence-verdict` | 1 / 2 / 1 / 1 | Scene, charge and answer, a flashback that proves it, the verdict (you-are-gods) |
| `two-tables` | 2 / 1 / 3:1 | Two events side by side, what was said, the reckoning, a silent beat (bread-of-life) |
| `echo` | 1:2 × 4, with `headers` | One story beside another, beat for beat (two-witnesses) |
| `day-by-day` | 3 × 2, then a tally | Days as columns, each night above its daylight, then a counting strip (three-days) |
| `call-pairs-mission` | 1 / 2 / 2 / 1 | A life: the call, a high and a low, a fall and a return, the mission (peter) |
| `contrast` | 2 / 1 | Two scenes, then what they mean together |
| `six-beats` | 2 / 2 / 2 | A sequence |
| `three-acts` | 1 / 1 / 1 | Before, the turn, after |

**Five beats is the target and six the ceiling**; count beats, not panels (an `echo` row is one beat
drawn twice). A seventh beat is a second comic, or a sign the point is two points.

- **A doctrine has no single scene**: tell its first story, then cross to the reader in the text's
  own picture. `why-we-need-saving` draws Genesis 2-3 in three beats, turns with "And every one of us
  since." to Isaiah 53:6's straying sheep, and lands on Romans 5:8. The crossing panel is a picture a
  verse paints, with that verse in a text box. Layout `[[300, 1], [300, 1, 1], [300, 1, 1]]`.
- **A comic can replace a diagram** whose boxes are moments in a story (`three-days` replaced a
  mermaid flowchart). It must carry every claim and confidence mark the diagram made.
- **A time gap** holds apart two scenes the text separates ("A thousand years", Revelation 20:5, 7,
  in `judgment-seat-of-christ`). Only for a span the text states.
- **A word thread** shows the text joining two scenes: `they-were-given-white-robes` runs one under
  Mark 9:3 and Revelation 7:14, the only New Testament uses of λευκαίνω. Verify the word with
  `bible_concordance` and record it in the TOML header; a thread is a claim about the text.

## 2. Write the words

The bubbles are the comic, and the likeliest place for it to say something Scripture does not.

- **Every bubble is traceable to its panel's `ref`.** `source = "esv"` is the ESV as printed,
  verified with `study_verse`, never recalled. `source = "condensed"` is shortened from those
  verses; its tag reads "· condensed". There is no third kind.
- **Condense; never compose.** A condensed line keeps the speaker's own claim and drops words, and
  never gives a speaker what the passage gives someone else. In John 10 the authorities say "you,
  being a man, make yourself God" (John 10:33, ESV), and Jesus answers in His own terms: "I and the
  Father are one" (John 10:30). "Yes, I am God" would put a sentence in His mouth the chapter
  doesn't, however true the doctrine.
- **Where the text records no words, write none.** Revelation 11:3-13 gives the witnesses no speech,
  so the comic draws what it gives: fire from their mouths (Revelation 11:5), presents exchanged
  (Revelation 11:10). Say so in the `note`. A bubble written for a silent character is the one error
  a reader cannot check.
- **A speaker the comic may not draw speaks from where they are.** Adam and Eve are reserved for
  after Genesis 3:21, so the man answers "I hid myself" (Genesis 3:10) from the `thicket`, with a
  spotlight on it. Say in the `note` who is not drawn and why.
- **Run `--verify` before embedding.** It fails on any ESV bubble not found in its panel's `ref`, so
  the `ref` is the bubble's evidence: widen it if a line comes from outside. Read each condensed line
  it lists against its verses.
- **One idea per bubble, about twenty words at most**, two bubbles a panel (three is crowded), and
  under ten seconds a panel.
- **The caption carries setting, time and narration** ("Earlier:" for a flashback). Narration is the
  study's voice and follows the style guide. Quoted Scripture keeps lowercase pronouns; condensed
  speech is our wording, so it capitalises.
- **`*Starred words*`** mark the word a line turns on: one phrase per bubble at most, and only words
  the study's point rests on.
- **`point`** is the closing line under THE POINT ribbon: the study's sentence, landed on the reader,
  with its verse.

## 3. Cast the panels

### Reserved figures

A biblical figure is drawn the same in every comic, so a reader who met Peter once knows him again.
Each is reserved once, in `FIGURES` in `utils/lib/comic.py`, and listed in
[cast.md](cast.md#reserved-figures).

- **Reserve only a figure the text names.** The two witnesses are unnamed and contested, so they are
  the generic `witness`, never Moses and Elijah; put the reading in an `aside`.
- **Reserve a figure the first time a comic needs them**: a `FIGURES` entry with `study` and `why`,
  naming the Scripture behind any detail of dress (John the Baptist's camel hair, Matthew 3:4) and
  deciding once each choice Scripture leaves open. Add a row to cast.md and re-run `--cast`.
- **A costume never changes**, no two reserved figures share a tunic colour, and no generic role
  wears one (check the robe lists in `CAST`).
- **Name a figure the first time they appear** with `tag`, using the passage's name: Simon in John
  1:42, Peter after.

### What a panel may draw

- **Faces stay blank, everyone's**, so Jesus is never the exception the eye looks for
  ([drawn-graphics.md](../develop-bible-study/drawn-graphics.md)).
- **Never draw the crucifixion's figures.** `crosses` stand empty; caption and verse carry it.
- **A thought picture draws only what the thinker's own words say**, captioned with their word
  (`woman-at-well`).
- **Draw what the text gives.** A stone is in a hand because John 10:31 puts it there; it is winter
  because John 10:22 says so. Atmosphere (a grey sky, columns) carries no claim. A detail that would
  claim something (lamps at the Feast of Dedication) waits for a verse.
- **When two scenes are compared, draw the difference the text gives, and only that.** Both feedings
  are in a "desolate place" (Mark 6:35; 8:4), so bread-of-life draws green grass near Passover
  against bare ground, the lake against the Decapolis, twelve κόφινοι against seven σπυρίδες.
- **Let the text's own echoes show.** Peter's denial and restoration are both by an ἀνθρακιά (John
  18:18; 21:9, its only uses), so they are a mirrored pair. Verify an echo with `bible_concordance`
  and record it in the TOML header.
- `shows` describes the panel for the alt text: write what is drawn.

## 3a. Emphasis: make the key beat land

One of the five beats carries the point; emphasis tells the eye which. The tools are in
[cast.md](cast.md#emphasis-tools), and each follows the rule that the picture says nothing the text
does not:

- **A mark is an emotion the text gives.** Elijah sweats because "he was afraid" (1 Kings 19:3); a
  disciple has a question mark because "some doubted" (Matthew 28:17). Name the verse in the header.
- **One emphasis per beat, on the beat that carries the point.** `when-love-grows-cold` gives the
  close shot to the lonely line, the pull-back to God's answer, the gold to the risen Jesus.
- **A crowd too large to draw says so** in its `aside` ("Drawn: a few dozen of the seven thousand.");
  every count that can be drawn is.
- **Colour that makes a claim needs a verse**: a `cold` look only on someone the text says it of.
- **Close shots of Jesus stay at `medium`**: a close shot of His blank face draws the eye to what the
  cast is built not to show.

## 4. Build, look, fix

Render and look at the PNG. In every panel: each tail points at its speaker, text clears the edge,
no speaker's head is covered, the reference tag is readable. Keep a `note` to two lines. A fix that
belongs to the system (a wrap that orphans a word, a pose that reads wrong) goes in `comic.py`; then
`python3 utils/build_comics.py` with no slug rebuilds every comic.

## 5. Embed it

Directly after the study's `**In one sentence:**` paragraph (or its opening paragraph):

```markdown
[![<output of --alt>](../assets/img/comics/<slug>.svg)](../assets/img/comics/<slug>.svg)
```

Replace any `[` or `]` in the alt text with parentheses. Run
`python3 utils/refresh_frontmatter_provenance.py` and `cd app && npm run validate`, and commit the
TOML, the SVG and the study together. To extend the system itself, see
[cast.md](cast.md#extending-the-system).
