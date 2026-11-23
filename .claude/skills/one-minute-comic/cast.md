# One-minute comic: the cast catalogue

The catalogue behind section 3 of [SKILL.md](SKILL.md): every reserved figure, every generic role, and
every pose, scene, prop and panel option with the TOML that draws it. The rules for what a panel may
draw are in SKILL.md; this file is what there is to draw with. Open `cast.svg` beside it to choose by
eye, and re-run `python3 utils/build_comics.py --cast` after adding to `utils/lib/comic.py`.

## Reserved figures

Each is reserved once, in `FIGURES` in `utils/lib/comic.py`, and drawn the same way in every comic.

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
| `moses` | Moses | Dusty blue tunic, pale head cloth, grey hair and full beard (eighty, Exodus 7:7); carries the staff (Exodus 4:2) | those-called-gods |
| `daniel` | Daniel | Saffron courtier's tunic (Daniel 2:48), cream mantle | those-called-gods |
| `joseph` | Joseph, son of Jacob | Young and clean-shaven (Genesis 39:6; 41:14), a jade tunic and no outer garment, the one he left in her hand (39:12) | sexual-immorality |
| `magdalene` | Mary Magdalene | A plum-rose robe and a pale veil, a woman of means who provided for Jesus (Luke 8:2-3) | jesus-and-women |
| `david` | David | Burnt-orange tunic, cream mantle, auburn hair and a young man's short beard ("ruddy", 1 Samuel 16:12) | table |
| `nebuchadnezzar` | Nebuchadnezzar | Deep indigo robe, gold belt and collar, full beard, the tall rounded cap of a Neo-Babylonian king: background, not Scripture, so the comic's `note` says so | the-image-and-the-kingdoms |
| `balaam` | Balaam son of Beor | Charcoal tunic, ochre stole, grey hair, full beard (a fixed choice). His she-donkey is the `donkey` prop (`donkey_down` lying); a rider takes `stance = "sit"`, `dy = -0.208 * s`. The angel of the LORD is `angel_sword`, light with the drawn sword (Numbers 22:23) | the-donkey-and-her-prophet |
| `nathan` | Nathan the prophet | Olive tunic, dark brown stole, grey hair and full beard (a fixed choice; Scripture gives no detail), older than the king he rebukes (2 Samuel 12:1) | first-take-the-log-out |
| `melchizedek` | Melchizedek, king of Salem | Deep wine tunic, cream stole, grey hair and full beard, short hair (a fixed choice; Scripture does not describe his dress); no priest's head cloth, since his priesthood is not Levi's (Hebrews 7:6) | melchizedek-priesthood |
| `abram` | Abram | Sage green tunic, plain pale head cloth with no band (so it never reads as the priest's), grey hair and full beard (past seventy-five, Genesis 12:4); Abraham from Genesis 17:5, so tag him with the name the passage uses | melchizedek-priesthood |

## Generic roles

The roles anyone may fill, varied by `tone` so a crowd is not clones:

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
| `harlot` | Royal purple, a scarlet veil and a gold girdle, "arrayed in purple and scarlet, and adorned with gold" (Revelation 17:4); `holds = "cup"` for the golden cup. Babylon as John pictures her, a city (17:18): say so in the caption or `note`, and do not draw the beast or name the city |
| `egyptian` | An Egyptian woman of rank: pleated white linen, a black shoulder-length wig, a gold broad collar, bare-headed. Drawn for Potiphar's wife, whom Scripture leaves unnamed; the dress is period background, so the comic's `note` says so. `holds = "garment"` for Joseph's garment (Genesis 39:12) |
| `robed` | A white robe and pale stole, no head cloth: one clothed in the robe "made white in the blood of the Lamb" (Revelation 7:14). Brighter than the priest's linen, so it reads as a gift and not an office |

## Poses, panels and props

- `pose`: stand, point, open, praise, raise, shout, hold, grope, beg, fold, turn, heart, look_up.
  `stance`: stand, walk, kneel, sit, lie (laid on the ground, head toward `face`). `face`: "left" or "right". Poses also include `run` and `offer` (an arm held out
  with something in the hand).
- **`holds`** puts a prop in the near hand: `staff`, `scroll`, `stone`, `spear`, `jar`, `gift`,
  `loaf`, `lamp`, `yoke`, `robe` (a white robe held out, folded over the hand), `crown` (a gold
  victor's wreath, the στέφανος), `palm` (a palm branch, Revelation 7:9), `shofar` (a ram's-horn
  trumpet, Ezekiel 33:3), `cup` (the golden cup, Revelation 17:4), `supper_cup` (plain clay, the
  Last Supper's cup, Luke 22:20), `garment` (a cloth hanging from the fist, Genesis 39:12), and
  `load`, which goes on the back with the hand on its strap, for the heavy-laden (Matthew 11:28).
- **`eye = "beam"`** puts the δοκός of Matthew 7:3-5 in the figure's eye, a roof timber jutting
  forward past the frame (`beam = 1.25` lengthens it, `0.8` shortens it); **`eye = "speck"`** draws
  the κάρφος, too small to see, inside a faint red ring. Stand the beam-bearer so the timber clears
  the other figures' heads. Drawn only where the panel is Jesus' picture or says it lays that
  picture over a story (`first-take-the-log-out`, whose `note` says 2 Samuel 12 has no beam).
- `tag = "Peter"` is a nameplate under the feet; set a tagged figure on the left, since bottom-right
  collides with the reference tag. `name = "Simon"` overrides how the alt text names them.
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
  ground for `depth`, [Emphasis tools](#emphasis-tools)), cave (bare rock and a cave mouth, for Horeb, 1 Kings 19:9), eden
  (the garden: far trees, the river of Genesis 2:10, green ground; put the near trees in as
  `fruit_tree` props). `sky`: day, dawn, winter, dusk, night, storm.
- `in_cloud = true` on a cast entry sets a cloud at the figure's waist, for one taken up
  (Acts 1:9; Revelation 11:12); give it a negative `dy` to lift it.
- `aside` is a dashed note hung under the caption, in the site's confidence code: a reading, an
  inference, or what the text leaves unsaid ("Revelation names neither of them.").
- `props` stand in the scene rather than in a hand: `crosses` (three, with no figures on them),
  `tomb` (open, the stone rolled back), `cloud`, `ruin` (a wall cracking and falling), `breath` (gold
  currents for the breath of life), `gift`, `fire` (a charcoal fire), `rooster`,
  `vine` (a grapevine on a trellis, heavy with clusters, John 15:1-5), `lampstand` (a household
  stand with a clay lamp burning on it, Matthew 5:15), `golden_lampstand` (one of Revelation 1:12's
  seven, drawn as a single gold stand with one flame; John gives no shape, so say so in the comic's
  `note`; give `n = 7` with `x2` for the seven), `kophinos` (a small wicker basket), `spyris` (a large hamper), `loaf`, `sheep`, `load` (a corded
  bundle, set down), `yoke`, `statue` (Nebuchadnezzar's image, shared with the History Chart), `stone` (in flight), `chaff` (the image's metals blowing away, Daniel 2:35), `mountain`, `bed` (a figure lying on it takes `dy = -0.075`), `ark`, `tower`, `tablets`, `rainbow`, `well` (a stone parapet, Jacob's well), `shaft` and `spring` (for thought pictures), and `hull`, which runs from
  `x` to `x2` and takes `front = true` so it is drawn over the people standing in it. For judgment
  scenes: `bema` (a raised stone tribunal with steps; a figure on it takes `dy = -0.156 * s`),
  `throne` (a throne with the one seated on it drawn as light, since Revelation 4:2-3 and 20:11 give
  a presence and no form), `seat` (a seat at the throne's height in its white stone, for one seated "at the right hand of the throne", Hebrews 8:1; a figure on it takes `dy = -0.156 * s`), `books` (opened, Revelation 20:12), `crown` (a wreath laid down), and
  `refined`, the counterpart of `burning`: gold, silver and precious stones standing whole in the
  fire on the same foundation (1 Corinthians 3:12-14). Also `beam` (the timber of Matthew 7:5, laid down), `figleaves` (the sewn loincloths of
  Genesis 3:7, cast off on the ground), `fruit_tree` (a tree "good for food", Genesis 2:9, with
  round fruit of no species since Genesis names none; the forbidden tree is the same prop, because
  it looked like the others, 3:6), `thicket` (dense shrubs to hide in, Genesis 3:8; nobody is drawn
  behind it), `serpent` (Genesis 3:1, head raised; Genesis gives it no form before the curse of
  3:14, so the `note` says so), `idol` (a faceless stone god on a plinth with a smoking altar, Deuteronomy 32:17; 1 Corinthians 10:20), `wall` (a city wall with battlements for a watchman; a figure
  on it takes `dy = -0.303 * s`) and `hand` ("a hand was stretched out to me, and behold, a scroll",
  Ezekiel 2:9: an arm reaching down from above the frame, the scroll in the hand; give it a `y` well
  above the ground). Mounts: `colt` (the donkey's colt of the triumphal entry, the disciples' cloaks
  on its back, Mark 11:7; a rider takes `stance = "sit"`, `dy = -0.198 * s`), `white_horse`
  (Revelation 19:11, 14, unsaddled; a rider takes `dy = -0.308 * s`) and `diadems` (Revelation
  19:12's many crowns, set by `y` on a rider's head). `y` defaults to
  the ground line; `s` scales. **`n` with `x2` draws a counted row**, so twelve baskets are twelve;
  stack two rows for a heap that still counts.
  `face = "left"` turns a prop round, so a flock can walk toward its shepherd.
- `stance = "sit"` seats a figure cross-legged. A seated crowd at `s = 0.4` with a negative `dy`
  sits in the background, behind the speakers.
- `s = 0.8` on cast entries draws them smaller, which buys bubble room in a half-width panel under a
  two-line caption. `flashback = true` tints the panel sepia and rounds its corners.

## Layouts and page devices

- **Inline layout**: `layout = [[300, 1], [300, 2, 1]]`, each row its height and then the relative
  width of each panel. Add a named layout to `LAYOUTS` only when a second comic needs the same shape.
- **`headers = ["Their Lord", "His two witnesses"]`** puts a ribbon over each column of the first
  row, and `subheaders` a small italic line under each (the span of each day, in three-days).
  `first_column_past = true` colours the first column sepia, to match `flashback = true` on its
  panels.
- **A time gap** is a panel with `kind = "gap"`, `text` and `ref`, on its own short row (`[46, 1]`):
  no frame, a dotted rule across the page and the span on a ribbon. It is not counted or numbered.
- **A word thread** is a panel with `kind = "thread"`, `text` and `at` (fractions of the page width),
  on its own short row under a row of panels: a gold strip naming the word the panels above share,
  with a tick up to each.

## Bubble options

- **A voice with no figure** (heaven, an angel) takes `from = [x, y]` in place of a cast member;
  `style = "voice"` makes it gold and bold. A tail from above the frame is a straight line from the
  bubble to `from`; where the caption is in the way, narrow it (`caption_w`) and move `from` toward
  the panel's centre until the line clears the caption's edge (`why-we-need-saving` panels 1 and 3).
- **`style = "shout"`** for a crowd or an accusation, `"whisper"` for an aside; speech is the default.
  **`style = "text"`** is a square box with no tail, for a writer's words when no speaker stands in
  the panel (Hebrews 12:1-2 in `run-the-race`); it still takes `from` and is verified. Set text
  boxes in the upper half: low down they run into the reference tag and are clipped.
- **`*Starred words*`** are set bold and red. The stars are dropped for `--verify` and the alt text.
- **`fire`**: `style = "fire"` with `to = <cast id>` draws fire from a mouth (Revelation 11:5); an
  empty bubble with `picture = { what = "gift", n = 3 }` draws presents with no words.

## Emphasis tools

`python3 utils/build_comics.py --cast` also writes `emphasis.svg`: each tool below in one panel,
captioned with its TOML. `when-love-grows-cold` uses most of them.

| Tool | TOML | What it does | Use it for |
|---|---|---|---|
| Close shot | `shot = "close"` (`"medium"`, `"extreme"`), or `camera = { on = "<id>", zoom = 2.0, at = [x, y] }` | Moves in on one figure's head and shoulders; `at` is where the head lands | The one line a face would carry: Elijah's "I only am left". Frame the speaker off-centre with room on the side they face, and put the bubble there |
| Inset | `inset = { on = "<id>", zoom = 2.4, corner = "br", size = 0.38, marks = ["sigh"] }` | A close-up in a corner of a wide panel, ruled to the figure it enlarges | Where someone stands *and* what it does to them; the inset's `marks` show only in the close-up |
| Horizon and depth | Panel `scene = "vista"`, `horizon = 0.4`; cast `depth = 0..1` | Deeper figures stand nearer the horizon and shrink, with a haze between | A crowd larger than the panel. A low horizon gives a lone figure the sky |
| Pull back | A close shot, then a wide `vista` with the close-shot figure in front, `look = "silhouette"`, `s = 1.5` | The reader sees what the figure sees | The answer to a lonely line |
| Spotlight | `spotlight = "<id>"`, or `spotlight = { at = [x, y], r = 0.7 }` | Darkens the frame away from a figure, or a place where someone undrawn is | Someone alone; the thicket the man hides in |
| Focus lines | `burst = { on = "<id>", color = "gold" }` | Lines converging on a figure | The arrival or word the comic turns on. Gold for glory, ink for alarm |
| Grade | `grade = "warm"`, `"cold"`, `"dark"` | A colour over the whole panel | Night, dawn, a cold heart, when the text gives it |
| Look | cast `look = "cold"`, `"warm"`, `"radiant"`, `"silhouette"`, `"faded"` | Recolours one figure | Radiant for the Transfiguration (Matthew 17:2), faded for one leaving the story |
| Marks | cast `marks = ["sweat", "tears", "shock", "sigh", "question", "exclaim", "heart", "cold", "warm", "ember"]` | The marks cartoonists draw round a head | What a blank face cannot show |

The camera and inset move everything in the frame except bubbles, which are placed in the panel's
own coordinates, so `at` means the same with or without a shot.

## Extending the system

- **A new character, pose, scene or prop** goes into `utils/lib/comic.py` (`CAST`, `POSES`,
  `SCENES`, `_prop`) as data or one function, with its line here; `--cast` regenerates the sheet.
  **A new emphasis tool** goes in that file's emphasis section with a panel in `emphasis_sheet()`.
  Colours are named constants at the top of the file, never a stray hex in one comic.
- **A figure is drawn in its own units**, feet at (0, 0), facing right, about 105 units tall. A pose
  is the (elbow, hand) of the near and far arm in those units.
- Keep it stdlib-only, like every generator in `utils/`.
