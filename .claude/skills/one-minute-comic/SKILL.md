---
name: one-minute-comic
description: Draws a "one-minute comic" for a study in docs/content/ -- three to six panels with speech bubbles, a reusable cast (Jesus, the authorities, a crowd, the healed man, disciples, soldiers) and named story layouts, that tells the study's main point so a reader gets it in a minute. Written as a TOML file in docs/data/comics/ and rendered by utils/build_comics.py. Use when the user asks for a comic, a comic strip, a one-minute comic, speech bubbles, a cartoon of a passage, or "tell the main point as a story" -- as opposed to drawn-graphics.md's charts and imagery plates, which explain rather than narrate.
---

# The one-minute comic

A study is long; its point is one sentence. The one-minute comic carries that sentence as a story
a reader can take in before the first heading: who was there, what they said, what it showed. The
first is `jesus/you-are-gods.md` (`docs/data/comics/you-are-gods.toml`); open its SVG beside this
file when writing a new one.

Everything is reusable. The cast, poses, scenes, bubbles and layouts live in
`utils/lib/comic.py`; a comic is a TOML file of data that names them. A new comic is a new file and
nothing else, and a corrected line is one edit and a re-run.

```bash
python3 utils/build_comics.py <slug>         # docs/data/comics/<slug>.toml -> docs/content/assets/img/comics/<slug>.svg
python3 utils/build_comics.py --alt <slug>   # the alt text, every panel and every word, for the embed
python3 utils/build_comics.py --cast         # cast.svg beside this file: every cast member in every pose
qlmanage -t -s 1400 -o <scratchpad> docs/content/assets/img/comics/<slug>.svg   # render and look
```

## 1. Find the point, then the beats

Start from the study's `**In one sentence:**` line. If the study has none, run
simplify-bible-study's first step and name it; a comic cannot carry a point the study has not
settled. Then find the moments in the passage that *show* it: the beats. Most points fall into
one of the named layouts, chosen by what the story has to do:

| Layout | Panels | Story shape |
|---|---|---|
| `setting-exchange-reveal` | 1 / 2 / 1 | Set the scene, two lines of exchange, the reveal |
| `setting-exchange-evidence-verdict` | 1 / 2 / 1 / 1 | Scene, the charge and the answer, a flashback that proves it, the verdict (you-are-gods) |
| `contrast` | 2 / 1 | Two scenes side by side, then what they mean together |
| `six-beats` | 2 / 2 / 2 | A sequence of events |
| `three-acts` | 1 / 1 / 1 | Before, the turn, after |

A layout can also be given inline as rows, `layout = [[300, 1], [300, 2, 1]]`: each row is its
height, then the relative width of each panel. Add a layout to `LAYOUTS` only when a second comic
needs the same shape, and name it for the story it tells.

Five panels is the target and six the ceiling. A seventh beat is a second comic, or a sign the
point is two points.

## 2. Write the words

The bubbles are the comic. They are also the place a comic is most likely to say something
Scripture does not.

- **Every bubble is traceable to the verses in its panel's `ref`.** `source = "esv"` is the ESV's
  wording as printed, verified with `study_verse` against `study-notes.db`, never recalled.
  `source = "condensed"` is shortened from those verses; the panel's reference tag then reads
  "· condensed", and the footer says what that means. There is no third kind.
- **Condense; do not compose.** A condensed line keeps the speaker's own claim and drops words.
  It never makes a speaker say what the passage has someone else say. In John 10 it is the
  authorities who say "you, being a man, make yourself God" (John 10:33, ESV); Jesus says "I and
  the Father are one" (10:30) and "the Father is in me and I am in the Father" (10:38). So the
  charge goes in their bubble and Jesus answers in His own terms. A paraphrase like "Yes, I am
  God" puts a sentence in His mouth that the chapter does not, however true the doctrine is, and
  the study beside it would be the first thing to contradict it.
- **One idea per bubble, about twenty words at most.** Two bubbles per panel is comfortable; three
  is crowded. The reader should finish a panel in under ten seconds.
- **The caption carries setting, time and narration**: the feast, the season, "Earlier:" for a
  flashback. Narration is the study's voice and follows the style guide (affirmative, plain
  terms, divine pronouns capitalised). Quoted Scripture keeps its lowercase pronouns; condensed
  speech is our wording, so it capitalises.
- **`style = "shout"`** for a crowd or an accusation, `"whisper"` for an aside. Speech is the
  default.
- **`point`** is the closing line under THE POINT ribbon: the study's sentence, landed on the
  reader ("so you can..."), with its verse.

## 3. Cast the panels

Open `cast.svg` to choose by eye. Each cast member is a costume, so who is who reads from colour
and dress:

| `who` | Reads as |
|---|---|
| `jesus` | Off-white robe, red stole, a soft gold light behind Him |
| `authority` | Striped prayer shawl over the head with tassels (Numbers 15:38), a phylactery on the brow (Matthew 23:5) |
| `priest` | White, head cloth with a blue band |
| `man`, `woman` | The crowd: head cloth or veil, robes varied by `tone` |
| `disciple` | Brown stole, bare head |
| `beggar` | Ragged, patched tunic; use with `holds = "staff"` and `pose = "grope"` for the man born blind |
| `healed` | The same man, now with a mantle |
| `soldier` | Red tunic, helmet; `holds = "spear"` |
| `child` | Smaller, bare-headed |

- **Faces stay blank, everyone's.** drawn-graphics.md rules out drawing the face of Jesus; a cast
  where nobody has a face keeps Him from being the exception the eye looks for.
- `pose`: stand, point, open, praise, raise, shout, hold, grope, beg, fold, turn, heart.
  `stance`: stand, walk, kneel. `face`: "left" or "right". `holds`: stone, staff, scroll, spear,
  lamp.
- **A crowd is one entry**: `n = 3, x = 0.6, x2 = 0.9` spreads three figures, cycles a list of
  poses, varies their robes and staggers their depth. Give it an `id` for its bubbles.
- `x` and bubble `at = [x, y]` are fractions of the panel, so a comic survives a layout change.
  The renderer lifts a bubble that would cover its own speaker's head, and refuses to build when
  a bubble cannot clear both the speaker and the caption; move it sideways or shorten the caption.
- `scene`: colonnade, temple, synagogue, pool, hills, plain, room. `sky`: day, winter, dusk,
  night, storm. `flashback = true` tints the panel sepia and rounds its corners.
- `shows` is a short description of the panel for the alt text. Write what is drawn.

**Draw what the text gives.** A stone is in a hand because John 10:31 puts it there; it is winter
because John 10:22 says so. Atmosphere (a grey sky, columns) may be added and carries no claim. A
detail that would make a claim the text does not, such as lamps at the Feast of Dedication, waits
for a verse or stays out.

## 4. Build, look, fix

Render it and look at the PNG. Check every panel for: a bubble tail pointing at the right
speaker, text clear of the panel edge, a speaker's head uncovered, the reference tag readable.
The first comic needed three passes. When a fix belongs to the system (a wrap that orphans a word,
a pose that reads wrong), fix `comic.py` so every comic gets it, then re-render the others:
`python3 utils/build_comics.py` with no slug rebuilds them all.

## 5. Embed it

Directly after the study's `**In one sentence:**` paragraph, so the comic is the first thing a
reader sees after the thesis:

```markdown
[![<output of --alt>](../assets/img/comics/<slug>.svg)](../assets/img/comics/<slug>.svg)
```

Replace any `[` or `]` in the alt text with parentheses. Then run
`python3 utils/refresh_frontmatter_provenance.py` and `cd app && npm run validate`, and commit the
TOML, the SVG and the study together.

## Extending the system

- **A new character, pose, scene or prop** goes into `utils/lib/comic.py` (`CAST`, `POSES`,
  `SCENES`, `_prop`) as data or one function, then `--cast` regenerates the model sheet. Colours
  are named constants at the top of the file; never a stray hex in one comic.
- **A figure is drawn in its own units**, feet at (0, 0), facing right, about 105 units tall. A
  pose is the (elbow, hand) of the near and far arm in those units.
- Keep it stdlib-only, like every generator in `utils/`.
