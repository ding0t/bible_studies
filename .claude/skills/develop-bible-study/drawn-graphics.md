# Drawn graphics: sequence, relationship, pattern, imagery

Phase 7 of [SKILL.md](SKILL.md) links here. [diagrams.md](diagrams.md) covers mermaid; this file
covers the SVGs drawn by the stdlib generators in `utils/`. The author rates these highly. Propose
one whenever a study has something prose carries badly: an order of events, how things fit
together, an object Scripture specifies, or a scene it describes in detail.

Pick the kind before drawing. Each answers a different question and has its own rules.

| Kind | Answers | Examples on the site |
|---|---|---|
| **Sequence** | *When?* Events on a line of time, spans, the order of a series | `seven-thousand-years`, `seventy-weeks`, `two-stages-of-his-coming`, `end-of-the-ages`, `after-the-thousand-years`, the tribulation charts |
| **Relationship** | *How does it fit together?* Nesting, correspondence, comparison, one thing inside or beside another | `weeks-within-weeks`, `eighth-day`, `six-days-three-ages`, `taken-before-judgment`, Larkin's "Jew, Gentile and Church" |
| **Pattern** | *What was it?* An object or place drawn as the text specifies it, to its measures | `sanctuary-lampstand`, `sanctuary-ark`, `sanctuary-incense-altar`, `new-jerusalem`, `new-jerusalem-scale` |
| **Imagery** | *What did they see?* A scene the text describes vividly, dramatised, with every detail in place | `tribulation/sea-to-blood`, `tribulation/four-horsemen` |

**Sequence** charts descend from Clarence Larkin's dispensational charts (*Dispensational Truth*,
1918; expanded 1920). **Pattern** takes its name from Scripture: Moses was to make the lampstand
"after the pattern for them, which is being shown you on the mountain" (Exodus 25:40, ESV), the
<span dir="rtl">תַּבְנִית</span> (*tavnit*, H8403) of Exodus 25:9. **Imagery** stands in the line of
the illuminated Apocalypse manuscripts and Dürer's Apocalypse woodcuts (1498): the vision drawn so
a reader feels its weight. A graphic can mix kinds. `six-days-three-ages` is a relationship drawn
along a line of time. Name the dominant kind and follow its rules.

## Rules every kind shares

- **Portrait, 720 units wide**, so 13-15 unit lettering still reads at the ~560px content column.
  Let height grow. The width budget in [diagrams.md](diagrams.md) applies to drawn SVGs too.
- **One hand.** Draw with `utils/lib/larkin.py`: parchment, ink, the ruled double border, the
  serif, the credit line. A new colour goes into the generator as a named constant, never as a
  stray hex in one shape.
- **Mark the confidence on the graphic.** A solid outline is what the text states or dates; a dashed
  one is inference, tradition or a modern construction. A contested point shows both readings. A
  graphic without the code reads as more certain than the study it sits in.
- **Read data, never retype it.** Dates come from `docs/data/chronology.json`, counts from the
  `evidence:` entries in the study's state file. A graphic that copies a number by hand drifts from
  its source.
- **Render and look.** `qlmanage -t -s 1400 -o <dir> <file>.svg` on macOS. Every graphic so far
  needed at least one pass for a label colliding with a line, text running past the border, or a
  shape escaping its panel (clip with a `clipPath`).
- **Embed with a link to the file**, `[![alt](path)](path)`, so the reader can open it full size.
  Write the alt text, and the `<desc>` inside the SVG, as a description of what the graphic says,
  including every numbered detail.
- **Generate, don't hand-draw.** Each graphic is a function in a `utils/build_*_graphics.py`
  script, so a corrected reference is one edit and a re-run.

## Sequence

- Time runs one way across the graphic, at a constant scale where the text gives the numbers.
- Spans the text counts (1,260 days, seven years, a thousand years) get a red span bar. Spans that
  are inferred are dashed.
- Placement by order alone, such as an event placed because it comes after another in Revelation, is
  dashed. Placement the text dates ("immediately after the tribulation") is solid.

## Relationship

- Show the thing the prose cannot: what nests inside what, what corresponds to what, where two
  readings divide. `weeks-within-weeks` forks at the 49- or 50-year question because that is the
  point where the sources part.
- Keep parallel items at one size and one alignment so the eye compares them. The eighth day is the
  same gold square in every row.
- Name each correspondence's source in the row or panel. A type the text names (1 Peter 3:20-21)
  is solid; a pattern the study reads into several texts is dashed.

## Pattern

- **Draw to the text's measures and counts.** Cubits, stadia, the number of branches, gates, cups or
  stones are counted in the generator from a list, never placed by eye.
- **Say where the text is silent.** The lampstand's height and base are not given, so they are
  dashed, with the tradition that supplies them named (b. *Menachot* 28b). A key at the side
  separates "stated: drawn solid" from "not stated: dashed, or a tradition named".
- **State scale honestly.** If something is drawn enlarged to be visible (the New Jerusalem's
  144-cubit wall against 12,000 stadia), the plate says so and gives the true ratio.
- **Show the second witness where one exists.** Zechariah's lampstand beside the Tabernacle's; the
  tribes on the gates from Ezekiel 48:31-34, labelled as Ezekiel's.

## Imagery

This kind is for the passages that are meant to be seen: the sea turned to blood, the New
Jerusalem coming down, the four horsemen, the throne room of Revelation 4, the sixth seal's sky
rolled up like a scroll, Ezekiel's river rising from ankle to swimming depth. Draw them with drama,
and make the detail the drama. The reader should be able to check every element against the verse.

- **Every detail is in the text, and the plate says where.** Number the details in the scene and
  give each a key line that quotes the verse with its reference (`sea-to-blood` does this with five
  callouts). If a reader could ask "where does it say that?", the element needs a callout or it
  goes.
- **Atmosphere may be added and never carries a claim.** Sky, light, waves, smoke and depth make the
  scene felt. Keep them neutral: a darkened sky in a judgment scene is mood, but a darkened sun is
  a claim and needs a verse (Revelation 8:12).
- **Draw the text's numbers exactly.** "A third of the ships" is two wrecks among six; "every living
  thing" is every creature drawn dead. Twelve gates are twelve, three to a side. Count them from a
  list in the generator.
- **Draw what the text names and nothing it does not.** The second bowl names no ships, so the plate
  shows none and says so. Where the text is silent on a place or arrangement that the drawing must
  still decide (which third of the sea, where the wrecks lie), mark it with a dashed line and a
  "Not stated" key line.
- **Keep John's comparisons visible.** Revelation says "something like a great mountain" and "like
  the blood of a corpse" (ὡς, *hōs*, G5613). Note the "like" in the key so the picture does not
  turn a comparison into a description.
- **Put the source beside the vision when the vision echoes it.** The second trumpet and second
  bowl replay Egypt's first plague (Exodus 7:20-21), so the plate sets the Nile beside the bowl, at
  one size. The New Jerusalem's river belongs beside Ezekiel 47:1-12. The echo is often the point
  of the passage.
- **Show escalation as Scripture measures it.** One river, then a third of the sea, then the whole
  sea. A strip that compares the reach often teaches more than the scene.
- **End on the theology.** Close the plate with the line in the passage that says what the scene
  shows about God: in `sea-to-blood` the angel of the waters, "Just are you, O Holy One"
  (Revelation 16:5, ESV).
- **Do not draw the face of God the Father or of Jesus.** Use the images the text itself gives: the
  throne, light, the rainbow like an emerald (Revelation 4:3), the Lamb standing as though slain
  (Revelation 5:6), a voice or a sound. Angels can be shown by what they do (a trumpet, a bowl
  poured out) without a figure. People in a scene are small, unindividuated figures. This is the
  default; the author can set it differently for a particular plate.
- **Drama techniques that render everywhere:** `linearGradient` and `radialGradient` for sky, glow
  and depth; layered paths at partial opacity for fire and smoke; repeated wave paths for water.
  Avoid `filter` effects unless the render check shows them working, and keep a plate under about
  150 KB. No raster images, no external fonts.
- **A contested figure stays faceless and carries its dispute on the plate.** The first horseman
  may be conquest, a false christ or Christ; `four-horsemen` draws him as a silhouette like the
  others and puts the readings in a dashed note beside him. Draw what the text gives him, a bow
  and a crown, and say what it leaves out (no arrows are named).
- **Composition.** One focal point per scene. The scene first, with its numbered key directly
  below, then any comparison panels, then the closing verse. Callout circles sit on the scene edge
  or in open space, never over a detail they would hide.
