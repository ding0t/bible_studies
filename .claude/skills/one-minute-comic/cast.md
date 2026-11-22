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
  ground for `depth`, SKILL.md section 3a), cave (bare rock and a cave mouth, for Horeb, 1 Kings 19:9), eden
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
