---
name: one-minute-comic
description: Draws a "one-minute comic" for a study in docs/content/ -- three to six panels with speech bubbles, a reusable cast (Jesus, the authorities, a crowd, the healed man, disciples, soldiers) and named story layouts, that tells the study's main point so a reader gets it in a minute. Written as a TOML file in docs/data/comics/ and rendered by utils/build_comics.py. Use when the user asks for a comic, a comic strip, a one-minute comic, speech bubbles, a cartoon of a passage, or "tell the main point as a story" -- as opposed to drawn-graphics.md's charts and imagery plates, which explain rather than narrate.
---

# The one-minute comic

A study is long; its point is one sentence. The one-minute comic carries that sentence as a story
a reader can take in before the first heading: who was there, what they said, what it showed. The
first is `jesus/you-are-gods.md` (`docs/data/comics/you-are-gods.toml`), and `biblical-figures/peter.md`
(`peter.toml`) shows a life told in six beats; open one beside this file when writing a new one.

Everything is reusable. The cast, poses, scenes, bubbles and layouts live in
`utils/lib/comic.py`; a comic is a TOML file of data that names them. A new comic is a new file and
nothing else, and a corrected line is one edit and a re-run.

```bash
python3 utils/build_comics.py <slug>         # docs/data/comics/<slug>.toml -> docs/content/assets/img/comics/<slug>.svg
python3 utils/build_comics.py --alt <slug>   # the alt text, every panel and every word, for the embed
python3 utils/build_comics.py --cast         # cast.svg beside this file: every cast member in every pose
python3 utils/build_comics.py --draft <slug> # render despite layout faults and list them, to see what to move
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
| `two-tables` | 2 / 1 / 3:1 | Two events side by side, what was said about them, the reckoning, a silent beat (bread-of-life) |
| `call-pairs-mission` | 1 / 2 / 2 / 1 | A life: the call, a high and a low, a fall and a return, the mission it reached (peter) |
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

### Reserved figures

A biblical figure is drawn the same way in every comic on the site, so a reader who met Peter in one
comic knows him in the next. Each is reserved once, in `FIGURES` in `utils/lib/comic.py`:

| `who` | Figure | Reads as | Introduced in |
|---|---|---|---|
| `jesus` | Jesus | Off-white robe, red stole, long hair and a full beard (Isaiah 50:6), a soft gold light behind Him | you-are-gods |
| `peter` | Simon Peter | Broad-built; deep teal fisherman's tunic, rope belt, sienna outer garment (John 21:7), grey-flecked hair | peter |
| `andrew` | Andrew | Peter's rope belt; mustard tunic, grey cloak | peter |

- **Reserve a figure the first time a comic needs them**, never in advance: add a `FIGURES` entry
  with `study` (the page that introduces them) and `why`, which names the Scripture behind any
  detail of dress (John the Baptist's camel hair and leather belt, Matthew 3:4) and records every
  choice Scripture leaves open, so it is decided once. Add a row to this table and re-run `--cast`.
- **Once reserved, a costume does not change.** A recoloured Peter is a different man to the reader.
- **No two reserved figures share a tunic colour, and no generic role wears one.** Check the
  generic robe lists in `CAST` before choosing.
- **Name a figure the first time they appear** in a comic with `tag = "Peter"` (a nameplate under
  the feet). Use the name the passage uses: Simon in John 1:42, Peter after. A tag on a figure in the
  bottom-right corner collides with the panel's reference tag; set them on the left.
- `name = "Simon"` on a cast entry overrides how the alt text names them for that panel.

### Generic cast

Open `cast.svg` to choose by eye. The roles anyone may fill, varied by `tone` so a crowd is not
clones:

| `who` | Reads as |
|---|---|
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
  The renderer lifts a bubble that would cover its own speaker's head; when the caption or the
  panel top is in the way, it sets the bubble beside the head instead. It refuses to build when a
  bubble runs past the panel edge or overlaps another bubble; `--draft` shows you the panel.
- **`style = "memory"`** is a thought-cloud that trails small circles to its speaker, for what a
  speaker remembers, and `picture = { what = "kophinos", n = 12 }` draws the memory inside it. The
  disciples answering "Twelve." and "Seven." in the boat show the baskets they mean.
- **A beat panel**: a narrow panel (`[340, 3, 1]`) holding one figure and one line lets the line
  land in silence. "Do you not yet understand?" is its own panel in bread-of-life.
- **A half-width panel holds two short bubbles side by side.** Keep each under about 40 characters,
  or put the setting line in the caption and give the panel one bubble. Peter's panel 2 does this:
  the caption carries Jesus' question, the bubble Peter's answer.
- `scene`: colonnade, temple, synagogue, pool, hills, plain, room, shore (lake and a fishing
  boat), courtyard (walled, a lit doorway), street, grassland (spring grass above the lake), decapolis
  (dry ground, a Greek city on the ridge), hall (inside a synagogue), lake (open water; put people
  in a boat with the `hull` prop). `sky`: day, dawn, winter, dusk, night, storm.
- `props` stand in the scene rather than in a hand: `fire` (a charcoal fire), `rooster`,
  `kophinos` (a small wicker basket), `spyris` (a large hamper), `loaf`, and `hull`, which runs from
  `x` to `x2` and takes `front = true` so it is drawn over the people standing in it. `y` defaults to
  the ground line; `s` scales. **`n` with `x2` draws a counted row**, so twelve baskets are twelve;
  stack two rows for a heap that still counts.
- `stance = "sit"` seats a figure cross-legged. A seated crowd at `s = 0.4` with a negative `dy`
  sits in the background, behind the speakers.
- `s = 0.8` on cast entries draws them smaller, which buys bubble room in a half-width panel under a
  two-line caption. `flashback = true` tints the panel sepia and rounds its corners.
- `shows` is a short description of the panel for the alt text. Write what is drawn.

**When two scenes are compared, draw the difference the text gives, and only that.** Both
feedings happen in a "desolate place" (Mark 6:35; 8:4), so the bread-of-life comic does not draw
one barren and one lush for drama. It draws what differs: green grass near Passover against bare
ground after three days, Galilee's lake against the Decapolis' Greek city, twelve κόφινοι against
seven σπυρίδες. The TOML header records each source.

**Draw what the text gives, and let the text's own echoes show.** Peter's denial and restoration
both happen by an ἀνθρακιά, a charcoal fire, a word the New Testament uses only at John 18:18 and
21:9, so the comic draws them as a mirrored pair. Verify an echo like that with
`bible_concordance` before building a panel on it, and record it in the TOML's header comment.

 A stone is in a hand because John 10:31 puts it there; it is winter
because John 10:22 says so. Atmosphere (a grey sky, columns) may be added and carries no claim. A
detail that would make a claim the text does not, such as lamps at the Feast of Dedication, waits
for a verse or stays out.

## 4. Build, look, fix

Render it and look at the PNG. Check every panel for: a bubble tail pointing at the right
speaker, text clear of the panel edge, a speaker's head uncovered, the reference tag readable.
The first comic needed three passes, the second six. When a fix belongs to the system (a wrap that orphans a word,
a pose that reads wrong), fix `comic.py` so every comic gets it, then re-render the others:
`python3 utils/build_comics.py` with no slug rebuilds them all.

## 5. Embed it

Directly after the study's `**In one sentence:**` paragraph (or its opening paragraph, if it has
none), so the comic is the first thing a reader sees after the thesis:

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
