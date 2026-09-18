# Plan — research & review MCP server, v2

**Date:** 2026-09-18
**Status:** Phases 1–3 shipped 2026-09-18. Phases 4–5 proposed.
**Scope:** `references/build/` — extend the existing `bible-references` MCP server into the
research/review substrate the two content skills actually need.

---

## Why now

The trigger was a diagnostic failure, and it is worth recording precisely because the fix is
architectural rather than a bug fix.

An agent needed an ESV study note. `study-notes.db` has **no MCP tool**, so it hand-rolled
`sqlite3` over the SMB mount and wrote survey queries — `count(*)`, `SELECT DISTINCT work_id`.
Those full-scan a 116 MB file across a ~25 MB/s network share. They took **64–97 seconds**. The
agent concluded the NAS was "hung", reported the volume unavailable three times, and proposed to
draft the study from memory instead.

Nothing was wrong with the volume. The indexed form of the same lookup returns in **0.1 s**:

| Query | Plan | Time |
|---|---|---|
| `notes WHERE book/chapter` | `SEARCH … USING INDEX idx_notes_ref` | 0.10 s |
| `verses WHERE book/chapter/verse` | `SEARCH … USING INDEX idx_sn_verses_ref` | 0.07 s |
| `count(distinct work_id) FROM verses` | `SCAN verses` | 97 s |
| `count(*) FROM notes` | `SCAN notes` | 64 s |

Three defects, none of them in the data:

1. **A source with no tool gets accessed badly.** The gap *is* the bug.
2. **Slow is indistinguishable from broken.** No deadline, no diagnostic — so an agent guesses,
   and guesses wrong in the expensive direction.
3. **Falling back to memory is the worst outcome available**, and it is the one an agent reaches
   for when a source looks unavailable. This repo already has the scar: a study drafted from
   memory rendered John 6:34 as "Lord, give us this bread" where the ESV reads **"Sir"**. The
   source that catches that is `study-notes.db` — the one just declared unavailable.

Meanwhile the existing 20 tools over `bible-text.db` worked fine throughout. The difference is
entirely *tool coverage*, not data health.

## What exists today

- `references/build/mcp_server.py` — 20 tools, registered via `.mcp.json`. Sound architecture:
  every tool is a thin wrapper over a `lookup_*` in `query.py`/`twot_lookup.py`, with SQL kept out
  of the server so CLI and MCP cannot drift. **Keep this rule.**
- `references/build/verify_claims.py` — claims-as-SQL with an `expect:` value, re-run against the
  db. This is already the repeatability idea, in embryo, and it works.
- `references/study-state/<slug>.yml` — durable per-study research record. Already the queue
  concept in embryo.
- Config split three ways: `license_map.yml` (license string → tier), `media_root.py`
  (`$BIBLE_MEDIA_ROOT`), and the `open-data/` vs `restricted-data/` directory convention.

Two adoption signals worth naming: only **9 of 43** state files use `claims:`, and only **53 of
68** subject files populate reference frontmatter. Both are cases where the right thing is
available but costs more effort than the wrong thing. That is a tooling problem, and it is the
same shape as the one above.

---

## Design principles

These are the load-bearing decisions; everything below follows from them.

**P1 — A source without a tool is an incident waiting to happen.** Every source an agent is told
to consult gets a first-class tool. If the tier makes raw access unwise, that is an argument for a
*narrower* tool, never for no tool.

**P2 — Make the wrong query unrepresentable.** The 97 s scan should not be *discouraged*; it
should be impossible to express. Tools take `(work_id, book, chapter, verse)` — the index
signature. No free-form SQL reaches the network-mounted db.

**P3 — Every result carries its own licence.** Today `license_tier` needs a *separate*
`bible_works` call, and the server's instructions say "call it first if you're about to quote" —
an instruction, not a guarantee, and instructions are what get skipped at 2am. Stamp `tier` and
`quote_allowance` onto every returned record. Authoritative awareness should be a property of the
data, not of the agent's diligence.

**P4 — Degrade loudly and specifically.** Never hang, never raise a bare `FileNotFoundError`.
Return `{available: false, reason: "...", remedy: "..."}`. An agent that is *told* "volume not
mounted; set $BIBLE_MEDIA_ROOT" behaves correctly. An agent that waits 97 s invents a story.

**P5 — Deadlines, always.** Every tool takes a budget and returns partial results plus a
diagnostic on expiry. "Slow" must be reportable as *slow*, distinct from *broken*.

**P6 — The state file is the queue.** Do not invent a second durable store. `study-state/*.yml`
already holds the research trail; make it executable rather than replacing it.

---

## Phase 1 — `study_notes_query.py` + tools

The highest-value phase by a wide margin, and independently shippable.

New library `references/build/study_notes_query.py`, following the `query.py` pattern exactly
(pure functions, JSON-friendly returns, `connect()` raising rather than `SystemExit`). Verified
schema:

```
works(work_id, title, publisher, year, license, license_tier, attribution, …)
verses(work_id, book, chapter, verse, text)                 idx_sn_verses_ref(book,chapter,verse)
notes(work_id, book, chapter, verse_start, verse_end, note_type, text)
                                                            idx_notes_ref(book,chapter,verse_start,verse_end)
introductions(work_id, scope, book, section_name, title, text)   idx_intro_book(book)
topical_articles(id, work_id, title, text) + topical_article_refs(article_id, book, chapter, verse)
images(work_id, figure_id, book, chapter, verse, context_type, file_path, caption, attribution, …)
```

11 works; notes by work: `nlt-life-application` 28,712 · `niv-biblical-theology` 16,988 ·
**`esv-study-bible` 16,133** · `lsb-2021` 14,865 · `niv-cultural-backgrounds` 10,286 ·
`nkjv-cultural-backgrounds` 10,263 · `csb-ancient-faith` 7,069 · `nlt-christian-basics` 4,889.

**Connection policy:** `file:…?immutable=1`, not `mode=ro`. Measured faster (0.07 s vs 0.11 s),
and it avoids WAL/lock-file writes on a network share entirely. The review skill already calls
this form "mandatory, not optional, under the sandbox" — Phase 1 makes that the only form
reachable.

Tools:

| Tool | Purpose |
|---|---|
| `study_note(book, chapter, verse, work_id=None)` | Notes whose span covers the verse. Indexed. |
| `study_verse(book, chapter, verse, work_id)` | ESV/NIV/NKJV/CSB/NASB/LSB verse text — the quotation-verification path. |
| `study_intro(book, work_id=None)` | Book/section introductions. |
| `study_article(query, book=None)` | Topical articles via `topical_article_refs`. |
| `study_works()` | The 11 works with tier + quote allowance. |

**Snippet discipline, enforced in code.** `quotation-only` means a sentence or two with
attribution. So: a per-call character cap, truncation marked explicitly (`truncated: true`,
`full_length: N`), a max row count, and every record stamped with `attribution` and
`quote_allowance`. The cap is a property of the tool, not a line in a skill file. Record the
chosen cap and its reasoning in the module docstring — per the repo's own rule that an exemption
or threshold carries its justification with it, or it is a hole.

**Guard against the scan.** Any lookup lacking an indexable predicate raises a structured error
naming the index it should have used. This is P2 made concrete, and it is the specific fix for
the incident above.

Tests in `references/build/tests/test_study_notes_query.py`: John 6:34 returns "Sir" (the
regression that motivated all of this); every query plan is `SEARCH`, never `SCAN` — assert via
`EXPLAIN QUERY PLAN`, which makes P2 a test rather than a convention; truncation marks itself;
unavailable volume returns the structured refusal rather than raising.

> **Gate:** the review skill's Phase 1 can verify an ESV quotation end-to-end through MCP alone,
> with no hand-written SQL anywhere in the transcript.

## Phase 2 — `sources.toml`, one config  ✅ shipped

Shipped as **TOML, not YAML**: `check_sources.py` is documented as runnable from a bare
`python3` with no `uv sync`, and PyYAML is not importable there while `tomllib` is. Using
YAML would have forced a dependency into the one script promised to need none.

Single authority for **location, tier, and permission**, replacing the three-way split.

```yaml
tiers:
  open:            { quote: unlimited,  commit_text: true  }
  restricted-nc:   { quote: short,      commit_text: true,  note: non-commercial only }
  quotation-only:  { quote: sentence-or-two-with-attribution, commit_text: false }

databases:
  bible-text:
    path: references/build/out/bible-text.db      # repo-relative, gitignored artifact
    default_tier: open                             # per-work tier lives in works.license_tier
  study-notes:
    path: ${BIBLE_MEDIA_ROOT}/local-only-build/study-notes.db
    default_tier: quotation-only
    connect: immutable
    network: true                                  # → deadlines, scan guard, degradation apply

raw_only:            # present on disk, NOT ingested — query.py/MCP cannot see these
  - references/open-data/hebrew-lexicon
  - references/open-data/stepbible-data
  # …
```

`media_root.py` and `license_map.yml` become readers of this rather than parallel sources of
truth. `check_sources.py` gains a drift check against it.

The `raw_only` block earns its place: a study once asserted Tobit was not in the repo while it sat
in `references/open-data/`. Expose it as a `sources_status()` tool so "not ingested" is a
queryable fact and never an inference.

**Do not** move a source between `open-data/` and `restricted-data/` — that directory split *is*
the licence audit boundary. `sources.yml` describes it; it does not replace it.

## Phase 3 — `research_batch`, the queue  ✅ shipped

One call, many typed lookups, one round-trip.

```jsonc
{ "requests": [
    {"id": "v1",  "tool": "bible_verse",   "args": {"book":"John","chapter":6,"verse":34}},
    {"id": "esv", "tool": "study_verse",   "args": {"book":"John","chapter":6,"verse":34,"work_id":"esv-study-bible"}},
    {"id": "int", "tool": "bible_interlinear", "args": {"book":"John","chapter":6,"verse":34}}
  ],
  "budget_seconds": 30 }
```

Returns results keyed by `id`, each tier-stamped, each independently marked
`ok | unavailable | timed_out`. **Partial success is a first-class outcome** — one unavailable
source must never fail the batch, because that is precisely the pressure that pushes an agent
toward memory.

Two properties worth having: dedupe identical requests within a batch, and open each db connection
once per batch rather than once per lookup — on a network share that is most of the cost.

## Phase 4 — `passage_brief`, the innovation

The single biggest reduction in agent effort. One call assembles the standard evidence set for a
passage that the develop skill currently gathers in a dozen-plus separate calls:

- verse text in requested translations (open tier at length; `quotation-only` as stamped snippets)
- interlinear alignment + morphology
- `bible_trace` cross-references with shared wording
- `bible_variants` (DSS divergence, with `extant_words` — Deut 32:8 is legible in only two words,
  and a study should say so)
- TWOT roots for Hebrew lemmas present
- study notes, snippet-capped, per work
- **versification alignment**, unconditionally

That last is not a convenience. Hebrew Joel 3:1 is English Joel 2:28 — the verse Acts 2 quotes;
LXX Psalm 22 is English Psalm 23. Ask in one scheme, read in another, and you get an unrelated
verse **with no error raised**. `bible_verse`/`bible_passage` handle this internally today, but a
composed query does not. Folding alignment into the brief closes the class.

Shape the return as the skill's exegesis order, so the brief reads as the section it will become.

## Phase 5 — repeatable ledger

Generalise `verify_claims.py` from SQL-with-`expect` to *any tool call with an expected result*.
The state file gains an `evidence:` block:

```yaml
evidence:
  - id: john-6-34-esv
    tool: study_verse
    args: {book: John, chapter: 6, verse: 34, work_id: esv-study-bible}
    expect_contains: "Sir, give us this bread always"
    checked: 2026-09-18
```

Then `uv run python verify_claims.py --evidence` replays every study's evidence and reports drift.
This gives all three of the asked-for properties at once — queued, batched (it *is* a batch), and
repeatable — on top of a mechanism already proven in this repo, and without a second store.

It also addresses the adoption number: 9 of 43 state files use `claims:` today because writing SQL
by hand is work. A tool call the agent already made, recorded automatically, is nearly free.

---

## Sequencing & risk

| Phase | Depends on | Est. | Ship alone? |
|---|---|---|---|
| 1 — study-notes tools | — | ~half day | **shipped 2026-09-18** |
| 2 — `sources.toml` | — | ~half day | **shipped 2026-09-18** |
| 3 — `research_batch` | 1, 2 | ~half day | **shipped 2026-09-18** |
| 4 — `passage_brief` | 3 | ~1 day | yes |
| 5 — evidence ledger | 3 | ~half day | yes |

Phases 1 and 2 are independent; either can go first. **Phase 1 first** — it removes the live
failure mode.

Risks:

- **Scope creep into a second server.** The repo's own architecture note warns that a second build
  system is how the 2026-08 asset-404 class of bug returns. One server, one query-library pattern.
- **Snippet caps drifting into over-quotation.** Cap in code with a recorded rationale; assert it
  in a test.
- **Tool-count sprawl.** 20 → ~28. Past ~30 an agent starts picking wrongly. Phase 4 is the
  mitigation: `passage_brief` should become the *default* entry point, with the granular tools as
  follow-ups. Revisit consolidation if the count grows again.
- ~~**`sources.toml` becoming a fourth source of truth**~~ — closed: `media_root.py` and
  `build.py` read it (asserted by `test_source_catalog.py`), and `license_map.yml` was
  deleted after a verified-identical migration rather than left alongside.

## Explicitly out of scope

- Any change to the `open-data/` / `restricted-data/` split.
- Committing more `quotation-only` text than the tier allows — the tooling makes lookup easy; it
  does not widen what may be reproduced.
- Exposing raw `notes` rows wholesale, even internally. Snippets or nothing.
- Fixing the SMB1 negotiation (`smbutil statshares` reports `SMBV_NEG_SMB1_ENABLED`). Real, worth
  chasing on the NAS, but it is a throughput matter and does not block any phase — with indexed
  queries the current share is already sub-second.
