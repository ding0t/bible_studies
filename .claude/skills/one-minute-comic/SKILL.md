---
name: one-minute-comic
description: Draws a "one-minute comic" for a study in docs/content/ -- three to six panels with speech bubbles, a reusable cast (Jesus, the authorities, a crowd, the healed man, disciples, soldiers) and named story layouts, that tells the study's main point so a reader gets it in a minute. Written as a TOML file in docs/data/comics/ and rendered by utils/build_comics.py. Use when the user asks for a comic, a comic strip, a one-minute comic, speech bubbles, a cartoon of a passage, or "tell the main point as a story" -- as opposed to drawn-graphics.md's charts and imagery plates, which explain rather than narrate.
---

# The one-minute comic

A study is long; its point is one sentence. The one-minute comic carries that sentence as a story
a reader can take in before the first heading: who was there, what they said, what it showed. The
first is `jesus/you-are-gods.md` (`docs/data/comics/you-are-gods.toml`), and `biblical-figures/peter.md`
(`peter.toml`) shows a life told in six beats, `bread-of-life` two events compared, and
`two-witnesses` one story echoing another with almost no words; open the nearest beside this file
when writing a new one.

Everything is reusable. The cast, poses, scenes, bubbles and layouts live in
`utils/lib/comic.py`; a comic is a TOML file of data that names them. A new comic is a new file and
nothing else, and a corrected line is one edit and a re-run.

```bash
python3 utils/build_comics.py <slug>         # docs/data/comics/<slug>.toml -> docs/content/assets/img/comics/<slug>.svg
python3 utils/build_comics.py --alt <slug>   # the alt text, every panel and every word, for the embed
python3 utils/build_comics.py --cast         # cast.svg beside this file: every cast member in every pose
python3 utils/build_comics.py --draft <slug> # render despite layout faults and list them, to see what to move
python3 utils/build_comics.py --verify <slug># every source = "esv" bubble checked against the ESV of its panel's ref
qlmanage -t -s 1400 -o <scratchpad> docs/content/assets/img/comics/<slug>.svg   # render and look
```

## 1. Read the study for the comic

Read the whole study before choosing a panel. Each part of a study feeds one part of the comic:

| In the study | Becomes in the comic |
|---|---|
| `**In one sentence:**` | What the comic shows. **The sentence's grammar picks the layout**: "X, then Y" is a sequence; "X and Y compared" is `contrast` or `two-tables`; "X follows Y" or a type and its fulfilment is `echo`; a person's life is `call-pairs-mission` |
| The passage's own words, and who speaks them | The bubbles (section 2). Note who has *no* recorded words; that is a finding, too |
| "What X shows about God", Be Transformed | `point`, landed on the reader ("so you…") with its verse |
| A confidence table, "contested", "this study holds" | What may be drawn as settled and what needs a dashed `aside`. An identification the text does not make (a name, a temple, a place) is never drawn as fact |
| Word studies (κόφινος/σπυρίς, ἀνθρακιά) and stated numbers | Visual details: a distinction the Greek keeps is drawn as two different objects, a count is drawn as that many |
| Setting details the study cites (season, terrain, feast) | Scene, sky and caption, each with its verse in the TOML header comment |
| Tradition, study-Bible opinions, the case for other readings | Leave out. A minute holds the text and the study's point, never the debate |

If the study has no `**In one sentence:**` line, run simplify-bible-study's first step and name it;
a comic cannot carry a point the study has not settled.

## 1a. Find the beats

Find the moments in the passage that *show* the point: the beats. Most points fall into one of
the named layouts, chosen by what the story has to do:

| Layout | Panels | Story shape |
|---|---|---|
| `setting-exchange-reveal` | 1 / 2 / 1 | Set the scene, two lines of exchange, the reveal |
| `setting-exchange-evidence-verdict` | 1 / 2 / 1 / 1 | Scene, the charge and the answer, a flashback that proves it, the verdict (you-are-gods) |
| `two-tables` | 2 / 1 / 3:1 | Two events side by side, what was said about them, the reckoning, a silent beat (bread-of-life) |
| `echo` | 1:2 × 4, with `headers` | One story beside another, beat for beat: a type and its fulfilment, a servant's life following the Lord's (two-witnesses) |
| `day-by-day` | 3 × 2, then a tally | Days as columns, each night above its daylight as the Hebrew day runs from sunset, then a counting strip (three-days) |
| `call-pairs-mission` | 1 / 2 / 2 / 1 | A life: the call, a high and a low, a fall and a return, the mission it reached (peter) |
| `contrast` | 2 / 1 | Two scenes side by side, then what they mean together |
| `six-beats` | 2 / 2 / 2 | A sequence of events |
| `three-acts` | 1 / 1 / 1 | Before, the turn, after |

A layout can also be given inline as rows, `layout = [[300, 1], [300, 2, 1]]`: each row is its
height, then the relative width of each panel. Add a layout to `LAYOUTS` only when a second comic
needs the same shape, and name it for the story it tells.

Five beats is the target and six the ceiling; count beats, not panels. In an `echo` each row
is one beat drawn twice, so four rows are eight panels and four beats. A seventh beat is a second
comic, or a sign the point is two points.

**A comic can replace a diagram inside a study**, not only open it. `three-days` replaces a mermaid
flowchart in "The week as the Hebrew calendar counts it" and is embedded where the flowchart was. A
diagram whose boxes are moments in a story (who was where, what happened, what it counts as) is a
comic waiting to be drawn; one whose boxes are concepts is not. The comic must still carry every
claim the diagram made, and the confidence marks with them.

`headers = ["Their Lord", "His two witnesses"]` puts a ribbon over each column of the first row,
and `subheaders` a line of small italic under each ribbon (the span of each day, in three-days);
`first_column_past = true` colours the first sepia, to match `flashback = true` on its panels, so
the column that has already happened reads as the past.

**A time gap** is a panel with `kind = "gap"`, `text` and `ref`, given its own short row in the
layout (`[46, 1]`): no frame, a dotted rule across the page and the span on a ribbon. It is not
counted or numbered as a panel. `judgment-seat-of-christ` puts "A thousand years" (Revelation 20:5,
7) between the crowns cast before the throne and the great white throne, so two scenes the eye would
read as adjacent are held apart by the distance the text puts between them. Use it only for a span
the text states.

**A word thread** is a panel with `kind = "thread"`, `text` and `at` (fractions of the page width),
on its own short row under a row of panels: a gold strip naming the word the panels above share,
with a tick up to each. `they-were-given-white-robes` runs one under Mark 9:3 and Revelation 7:14,
the only two New Testament uses of λευκαίνω, so the reader sees the text joining the two scenes and
not the artist. Verify the word with `bible_concordance` and record it in the TOML header; a thread
is a claim about the text, held to the same standard as a bubble.

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
- **Where the text records no words, write none.** Revelation 11:3-13 gives the two witnesses and
  the crowd no speech at all; the only words are heaven's, "Come up here!" (11:12). So the comic
  puts what the text gives in the bubble's place: fire from the witnesses' mouths
  (`style = "fire"`, `to = <cast id>`, Revelation 11:5), a bubble of presents with no words
  (`text = ""`, `picture = { what = "gift", n = 3 }`, 11:10). Say so in the comic's `note`. A
  bubble written for a silent character is the one error a reader cannot check.
- **A voice with no figure** (heaven, an angel, a voice from the tomb) takes `from = [x, y]`, a
  place in the panel or above it, in place of a cast member; `style = "voice"` makes it gold and
  bold. Aim the `from` so the tail does not cross the caption.
- **Run `--verify` before embedding.** It looks up every `source = "esv"` bubble in the ESV text of
  the verses its panel's `ref` names and fails on any bubble it cannot find there, then lists the
  condensed ones for you to read against their verses. A `ref` is therefore the bubble's evidence:
  if a quoted line comes from a verse outside it, widen the `ref`.
- **One idea per bubble, about twenty words at most.** Two bubbles per panel is comfortable; three
  is crowded. The reader should finish a panel in under ten seconds.
- **The caption carries setting, time and narration**: the feast, the season, "Earlier:" for a
  flashback. Narration is the study's voice and follows the style guide (affirmative, plain
  terms, divine pronouns capitalised). Quoted Scripture keeps its lowercase pronouns; condensed
  speech is our wording, so it capitalises.
- **`*Starred words*` are the key words**, set bold and red the way a letterer leans on the word a
  line turns on: "the love of many will \*grow cold\*." One phrase per bubble at most, and only the
  words the study's point rests on. The stars are dropped for `--verify` and the alt text, so an
  ESV bubble with stars still checks as the ESV's wording.
- **`style = "shout"`** for a crowd or an accusation, `"whisper"` for an aside. Speech is the
  default. **`style = "text"`** is a square box with no tail, for a writer's words when no speaker
  stands in the panel (Hebrews 12:1-2, Isaiah 40:29 in `run-the-race`); it still takes `from` and
  is checked by `--verify` like any ESV bubble.
- **`holds`** on a cast entry puts a prop in the near hand: `staff`, `scroll`, `stone`, `spear`,
  `jar`, `gift`, `loaf`, `lamp`, `yoke`, `robe` (a white robe held out, folded over the hand),
  `crown` (a gold victor's wreath, the στέφανος), `palm` (a palm branch, Revelation 7:9), `shofar`
  (a ram's-horn trumpet, Ezekiel 33:3), and `load`, which goes on the back with the hand on its
  strap, for the heavy-laden (Matthew 11:28). Poses include `run` and `offer` (an arm held out
  with something in the hand).
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
| `pilate` | Pontius Pilate | Tan tunic, red military cloak, clean-shaven in the Roman manner | two-witnesses |
| `john` | John, son of Zebedee | Deep blue tunic, cream mantle, the fishermen's rope belt | test-the-spirits |
| `paul` | Paul | Rust tunic, charcoal travelling cloak, leather belt | test-the-spirits |
| `elijah` | Elijah | Coarse brown hair garment, dark leather belt (2 Kings 1:8), dark cloak (1 Kings 19:13), full beard, short hair | when-love-grows-cold |
| `james` | James, son of Zebedee | Deep forest-green tunic, sand mantle, the fishermen's rope belt | they-were-given-white-robes |
| `adam`, `eve` | Adam and Eve | Mottled hide tunics, knee-length for Adam, full-length for Eve: the "garments of skins" (Genesis 3:21). Drawn only after 3:21 | they-were-given-white-robes |
| `ezekiel` | Ezekiel | A priest's pale head cloth (Ezekiel 1:3) over a muted violet tunic, full beard | ezekiels-commission |

- **Reserve only a figure the text names.** The two witnesses are unnamed in Revelation 11 and
  contested in the study, so they are the generic `witness` (sackcloth), never a reserved Moses
  and Elijah; drawing them as Moses and Elijah would assert on the picture what the study marks as
  its reading. Put the reading in an `aside`.
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
| `witness` | Sackcloth (coarse, dark goat's hair), for a prophet in mourning dress (Revelation 11:3) |
| `child` | Smaller, bare-headed |
| `bride` | Bright white linen and a white veil: the Bride as Revelation pictures God's people (19:7-8). Say in the caption that it is John's picture |
| `robed` | A white robe and pale stole, no head cloth: one clothed in the robe "made white in the blood of the Lamb" (Revelation 7:14). Brighter than the priest's linen, so it reads as a gift and not an office |

- **Faces stay blank, everyone's.** drawn-graphics.md rules out drawing the face of Jesus; a cast
  where nobody has a face keeps Him from being the exception the eye looks for.
- `pose`: stand, point, open, praise, raise, shout, hold, grope, beg, fold, turn, heart, look_up.
  `stance`: stand, walk, kneel, sit, lie (laid on the ground, head toward `face`). `face`: "left" or "right". `holds`: stone, staff, scroll, spear,
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
- **`style = "thought"`** is the same cloud for what a speaker *has in mind*, and a picture inside it
  can carry a `caption` (the word they use) and an `h` for a tall drawing. `woman-at-well` is the
  specimen: John 4 says "well" with two words, so the woman thinks of a `shaft` captioned
  "φρέαρ: a shaft" (4:11) and Jesus of a `spring` captioned "πηγή: a spring" (4:14). **A thought
  picture draws only what the thinker's own words in the panel say**, captioned with the word they
  use; a thought the text does not voice is a bubble written for a silent character. Where the
  picture carries a reading (she "still pictures the shaft" at 4:15), the panel's `aside` says so.
- **Never draw the crucifixion's figures.** `crosses` draws the three crosses on the rise with no
  one on them; the caption and the verse carry what happened there.
- **`badge = { text = "Night 1", tone = "night" }`** labels what a panel counts as, bottom-left;
  tones are `night`, `day` and `muted` (dashed: present but not counted). A reference tag that would
  collide with it steps up a line.
- **`kind = "tally"`** is a counting strip in place of a scene: `marks` lists `sun` (`fill = "part"`
  or `"full"`) and `moon` icons with labels, `{ sunset = true }` puts a divider between days, and
  `style = "dashed"` draws a mark the count needs that the text does not give, in red with a "?".
  Its `caption` sits beside the strip.
- **`numbers = false`** hides the panel numbers when columns or headers already give the reading
  order, which also lets captions use the full panel width (narrow panels need it).
- **A beat panel**: a narrow panel (`[340, 3, 1]`) holding one figure and one line lets the line
  land in silence. "Do you not yet understand?" is its own panel in bread-of-life.
- **A half-width panel holds two short bubbles side by side.** Keep each under about 40 characters,
  or put the setting line in the caption and give the panel one bubble. Peter's panel 2 does this:
  the caption carries Jesus' question, the bubble Peter's answer.
- `scene`: colonnade, temple, synagogue, pool, hills, plain, room, shore (lake and a fishing
  boat), courtyard (walled, a lit doorway), street, grassland (spring grass above the lake), decapolis
  (dry ground, a Greek city on the ridge), hall (inside a synagogue), lake (open water; put people
  in a boat with the `hull` prop). vista (open land to a horizon the panel sets with `horizon`; the
  ground for `depth`, section 3a), cave (bare rock and a cave mouth, for Horeb, 1 Kings 19:9). `sky`: day, dawn, winter, dusk, night, storm.
- `in_cloud = true` on a cast entry sets a cloud at the figure's waist, for one taken up
  (Acts 1:9; Revelation 11:12); give it a negative `dy` to lift it.
- `aside` is a dashed note hung under the caption, in the site's confidence code: a reading, an
  inference, or what the text leaves unsaid ("Revelation names neither of them.").
- `props` stand in the scene rather than in a hand: `crosses` (three, with no figures on them),
  `tomb` (open, the stone rolled back), `cloud`, `ruin` (a wall cracking and falling), `breath` (gold
  currents for the breath of life), `gift`, `fire` (a charcoal fire), `rooster`,
  `vine` (a grapevine on a trellis, heavy with clusters, John 15:1-5), `kophinos` (a small wicker basket), `spyris` (a large hamper), `loaf`, `sheep`, `load` (a corded
  bundle, set down), `yoke`, `well` (a stone parapet, Jacob's well), `shaft` and `spring` (for thought pictures), and `hull`, which runs from
  `x` to `x2` and takes `front = true` so it is drawn over the people standing in it. For judgment
  scenes: `bema` (a raised stone tribunal with steps; a figure on it takes `dy = -0.156 * s`),
  `throne` (a throne with the one seated on it drawn as light, since Revelation 4:2-3 and 20:11 give
  a presence and no form), `books` (opened, Revelation 20:12), `crown` (a wreath laid down), and
  `refined`, the counterpart of `burning`: gold, silver and precious stones standing whole in the
  fire on the same foundation (1 Corinthians 3:12-14). Also `figleaves` (the sewn loincloths of
  Genesis 3:7, cast off on the ground), `wall` (a city wall with battlements for a watchman; a figure
  on it takes `dy = -0.303 * s`) and `hand` ("a hand was stretched out to me, and behold, a scroll",
  Ezekiel 2:9: an arm reaching down from above the frame, the scroll in the hand; give it a `y` well
  above the ground). `y` defaults to
  the ground line; `s` scales. **`n` with `x2` draws a counted row**, so twelve baskets are twelve;
  stack two rows for a heap that still counts.
  `face = "left"` turns a prop round, so a flock can walk toward its shepherd.
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

## 3a. Emphasis: make the key beat land

A comic tells its point in five beats, and one of them carries it. Emphasis is how the reader's eye
is told which. `python3 utils/build_comics.py --cast` also writes `emphasis.svg` beside this file:
every tool below in one panel each, captioned with the TOML that draws it. Open it to choose by eye.
`when-love-grows-cold` uses most of them and is the specimen.

| Tool | TOML | What it does | Use it for |
|---|---|---|---|
| Close shot | `shot = "close"` (`"medium"`, `"extreme"`), or `camera = { on = "<id>", zoom = 2.0, at = [x, y] }` | Moves the camera in on one figure's head and shoulders; `at` is where the head lands in the frame | The one line a face would carry: Elijah's "I only am left". Frame the speaker off-centre with room on the side they face, and put the bubble there |
| Inset | `inset = { on = "<id>", zoom = 2.4, corner = "br", size = 0.38, marks = ["sigh"] }` | A close-up set into a corner of a wide panel, ruled to the figure it enlarges | Where someone stands *and* what it does to them, in one glance; the inset's `marks` show only in the close-up |
| Horizon and depth | Panel `scene = "vista"`, `horizon = 0.4`; cast `depth = 0..1` | Figures deeper in the picture stand nearer the horizon and shrink in proportion; a haze in the horizon's colour falls between far and near | A crowd that is more than the panel can hold (the seven thousand). A low horizon gives a lone figure the sky; a high one fills the frame with land and people |
| Pull back | A close shot, then a wide `vista` panel; the close-shot figure in the foreground with `look = "silhouette"`, `s = 1.5` | The reveal: the reader sees what the figure sees | The answer to a lonely line, the size of what God has done |
| Spotlight | `spotlight = "<id>"` | Darkens the frame away from one figure | Someone alone, or the one figure the panel is about |
| Focus lines | `burst = { on = "<id>", color = "gold" }` | Lines converging on a figure, stopping short of it | The arrival or word the comic turns on. Gold for glory; ink for alarm |
| Grade | `grade = "warm"`, `"cold"`, `"dark"` | Lays a colour over the whole panel | The temperature of the moment, when the text gives it (night, dawn, a cold heart) |
| Look | cast `look = "cold"`, `"warm"`, `"radiant"`, `"silhouette"`, `"faded"` | Recolours one figure | Cold for love cooling, warm for the faithful, radiant for His glory at the Transfiguration (Matthew 17:2), faded for one leaving the story, silhouette for the figure the camera looks past |
| Marks | cast `marks = ["sweat", "tears", "shock", "sigh", "question", "exclaim", "heart", "cold", "warm", "ember"]` | The marks cartoonists draw round a head | What a blank face cannot show |

Rules, each for the same reason as section 1's: the picture must not say what the text does not.

- **A mark is an emotion the text gives.** Elijah sweats because "he was afraid" (1 Kings 19:3); a
  disciple carries a question mark because "some doubted" (Matthew 28:17). No text, no mark. Name the
  verse in the TOML header.
- **One emphasis per beat, on the beat that carries the point.** A comic in which every panel zooms,
  glows and bursts has emphasised nothing. `when-love-grows-cold` gives the close shot to the lonely
  line, the pull-back to God's answer, and the gold to the risen Jesus.
- **A crowd too large to draw says so.** Seven thousand cannot be drawn; the panel's `aside` reads
  "Drawn: a few dozen of the seven thousand." Section 1's rule that a count is drawn as that many
  still governs every count that can be.
- **Colour that makes a claim needs a verse.** A `cold` look on a figure says that person's love has
  cooled; draw it only on someone the text says it of, or in a picture of Jesus' own words about
  "many".
- **Close shots of Jesus stay at `medium`.** The faces are blank by rule (drawn-graphics.md); a close
  shot of His blank face draws the eye to exactly what the cast is built not to show.
- The camera and inset move everything in the frame, bubbles excepted: bubbles are placed in the
  panel's own coordinates after the camera, so `at` means the same thing with or without a shot.

## 4. Build, look, fix

Render it and look at the PNG. Check every panel for: a bubble tail pointing at the right
speaker, text clear of the panel edge, a speaker's head uncovered, the reference tag readable.
The first comic needed three passes, the second six; with `--draft` and the automatic placement,
the fourth needed three. When a fix belongs to the system (a wrap that orphans a word,
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
  `SCENES`, `_prop`) as data or one function, then `--cast` regenerates the model sheet. **A new
  emphasis tool** (a shot, a look, a mark) goes in the emphasis section of the same file and gets a
  panel in `emphasis_sheet()`, so the sheet stays the full catalogue. Colours
  are named constants at the top of the file; never a stray hex in one comic.
- **A figure is drawn in its own units**, feet at (0, 0), facing right, about 105 units tall. A
  pose is the (elbow, hand) of the near and far arm in those units.
- Keep it stdlib-only, like every generator in `utils/`.
