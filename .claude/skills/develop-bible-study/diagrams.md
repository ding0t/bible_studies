# Diagrams: mermaid that survives the content column

Phase 7 of [SKILL.md](SKILL.md) links here. This is the diagram equivalent of
[style-guide.md](style-guide.md): the content is your problem, but the *shape* has one rule that
matters more than every aesthetic judgement, and it is measurable.

## The width budget is ~560px, and going over it shrinks the text

Mermaid renders a diagram at its natural size and emits `width="100%"` with
`style="max-width: <natural>px"`. In a container narrower than that, the SVG scales down — **the
whole diagram, labels included**. There is no wrapping, no reflow, no horizontal scrollbar. A
too-wide diagram doesn't get cropped; it gets *small*.

The container is narrower than it looks. From the built theme's own CSS (`main.*.min.css`):

```
.md-grid          { max-width: 61rem }    /* 976px */
.md-sidebar       { width: 12.1rem }      /* 194px, twice — nav and TOC */
.md-content__inner{ margin: 0 .8rem }     /* 26px */
```

976 − 194 − 194 − 26 = **~563px** on a study page with a table of contents (any page with two or
more `##` headings, which is all of them). Pages without a TOC get ~750px. Budget to 560.

What that costs, measured:

| Diagram width | Renders at | 16px label becomes |
|---|---|---|
| 560 | 100% | 16px |
| 870 | 65% | 10px |
| 1769 | 32% | 5px |
| 3725 | 15% | 2px |

## The rule: three columns is the ceiling for `flowchart LR`

A column costs ~230px and **that floor is padding, not text** — so shortening labels does almost
nothing. Measured on `how-we-cross-reference.md`: cutting three-line labels to two and degrading
"Index every 4-word sequence" to "4-word run" moved the diagram 870px → 801px. Not worth the
precision. Four `LR` nodes in a rank is already over budget; seven is 1769px.

**Height is cheap and width is expensive.** Nothing gets scaled for being tall — the reader
scrolls, which they are doing anyway. Trade width for height every time.

## Fold a long chain into stages

Group the steps into at most three stages, stack the steps *inside* each stage, and **stack the
stages too** — `flowchart TD` with `direction TB` clusters is the narrowest form that still carries
the grouping:

```mermaid
flowchart TD
    subgraph prep["Prepare the texts"]
      direction TB
      A["Both texts, same language"] --> B["Normalise — accents and case removed"]
    end
    subgraph match["Find candidates"]
      direction TB
      D["Pairs sharing those sequences"] --> E["Score by local alignment, rarity and overlap"]
    end
    prep --> match
```

**Use `TD` for the outer direction unless you specifically want the stages side by side.** Same
seven steps, same three stages, on `how-we-cross-reference.md`: `LR` outer puts the stages in three
columns and costs 870px (65%); `TD` outer stacks them into one column at 346px, which renders at
full size. The labels stop needing `<br/>` at that width, too.

Two details make this work:

- **`direction TB` inside the subgraph** is what stacks the steps. Mermaid's docs warn that a
  subgraph's direction is ignored when its nodes link outside it — so **link stage-to-stage
  (`prep --> match`), not node-to-node across a boundary**. Both forms are already in this repo
  (`olivet-discourse.md:429` and `:882`), and stage-to-stage is the one that reliably keeps the
  inner direction. This is not a style preference: keeping the per-node edges on
  `about-our-datasets.md` and merely adding `direction TB` left the diagram at 2674px, because
  every `source --> btdb` edge voided the direction of the cluster the source sat in.
- **The stages should mean something.** If you can't name three stages, the diagram is a list and
  probably wants to be one. On `how-we-cross-reference.md` the three stages line up with the three
  choices the prose then explains, which is why the grouping reads as structure rather than as
  packing.

When the steps have no stages worth naming — which is most of the time — drop the subgraphs and use
a plain `TD` chain. Converting the linear chronologies on `olivet-discourse.md`, `rapture.md`,
`prophecy-chart.md` and `bride-of-christ.md` from `LR` to `TD` took all four from under 40% to
100%, changing nothing but the first line.

## Three more rules the corpus pass produced

- **`direction TB` only stacks nodes that are linked to each other.** A cluster holding a list of
  unconnected nodes lays them out in a *row* whatever its direction, because dagre has no rank
  relationship to work with. `about-our-datasets.md` is a catalog of sources with no internal
  edges, which is why it was the widest diagram on the site at 3725px. Give the list an explicit
  order with **invisible links** — `macula ~~~ sblgnt ~~~ wlc` — and it stacks.
- **Disconnected subgraphs sit side by side along the flow direction.** Three unlinked clusters in
  a `TD` chart form three columns; the same three in an `LR` chart stack vertically. When several
  parallel things each need their own box and nothing links them — the three gospel accounts on
  `last-supper-four-cups.md`, the three evidence tiers on `bride-of-christ.md` — **`LR` is the one
  that makes them narrow**, which is the opposite of the usual advice above.
- **Never put `<br/>` in a subgraph title.** Mermaid does not reserve height for a wrapped cluster
  label, so the second line renders *underneath* the first child node and is unreadable. Found by
  rendering; it is invisible in the source. Shorten the title or use `·` as a separator instead.

## Verify, don't estimate

Node count is a bad predictor — label length, subgraph titles and edge labels all move the number.
Render it:

```bash
cd "$TMPDIR" && npm init -y && npm i @mermaid-js/mermaid-cli
npx mmdc -i diagram.mmd -o out.svg -b white
grep -o 'viewBox="0 0 [0-9.]* [0-9.]*"' out.svg | head -1   # width height
```

Two environment traps, both hit on first use: mermaid-cli downloads Chromium from
`storage.googleapis.com` and *launches* it, and the sandbox blocks both (`ENOTFOUND`, then
`bootstrap_check_in ... Permission denied`). Run the install and the render with
`dangerouslyDisableSandbox`. There is no Chrome in `/Applications` to borrow.

## Keep the corpus clean

- **Do not use `timeline`.** Mermaid lays its sections out horizontally with nothing constraining the
  width, and it writes per-section text colours into the SVG, which ignores the dark-mode toggle. Use
  `flowchart TD`, and move a timeline's `title` into a lead-in sentence above the block.
- **Width is a constraint, not the goal.** When the only way under budget is a diagram that says
  something untrue, stop and take the shrink: `about/about-our-datasets.md` stays at 48% because
  every narrower form merged the trust tiers the page exists to separate.
- Fix the diagram in front of you when a study brings you to its file, and don't add a new wide one.
  `npm run validate` cannot measure width, so nothing catches this but you.

The 2026 width sweeps, file by file: [why-the-rules.md](../why-the-rules.md#diagrams).

## Drawn graphics

When mermaid cannot carry it, draw an SVG. [drawn-graphics.md](drawn-graphics.md) sets out the four
kinds (sequence, relationship, pattern and imagery), the rules they share (720 wide, one hand,
solid for stated and dashed for inferred, read data, render and look) and the rules for each kind.
