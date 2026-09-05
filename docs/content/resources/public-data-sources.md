---
title: "Public Data Sources"
category: "resources"
description: "A survey of the open Bible data that exists in this space — texts, manuscripts, lexicons, cross-references, alignment — what each source is, why it matters, how it is licensed, and which ones this site actually uses."
tags: ["github", "lang/hebrew", "lang/greek", "lexicon", "strongs", "manuscripts", "licensing"]
draft: false
date_created: 2026-09-05
date_modified: 2026-09-05
ai_provider_models:
  - anthropic/claude-opus-5
  - anthropic/claude-sonnet-5
---

# Public data sources

Open, machine-readable Bible data is unevenly good. Some of it is careful scholarship given away
under a permissive licence; some is a Bible translation someone re-licensed as their own without the
right to. This page is a survey of what exists, organised by what the data *is* — texts, lexicons,
cross-references, alignment, the fathers — with what each source is, why it is interesting, and how
it is licensed.

It is not a record of our plumbing. **Where a source is one this site actually uses, the row says so
and links to [About Our Datasets](../about/about-our-datasets.md)**, which is the single authority
on what we rely on, how it is built and how it is queried. Keeping the two apart is deliberate: they
were merged in substance for months, the same source was described on both, and the descriptions
drifted until one of them was wrong.

Much of the survey came from
[biblenerd/awesome-bible-developer-resources](https://github.com/biblenerd/awesome-bible-developer-resources),
a good first stop when a new kind of data is needed.

**One rule governs every licence below.** A repository's own licence (MIT, CC0)
covers *its* code and compilation only. It does not override the copyright of third-party text
bundled inside it — a Bible translation, a lexicon. At least one entry below gets this wrong, which
is why every one is checked separately.

**Used here?**

- ✅ **Used** — licence confirmed open, and this site relies on it. How it is built and queried is on [About Our Datasets](../about/about-our-datasets.md)
- 🟡 **Used, restricted** — usable under non-commercial terms, kept separate from the open sources so the boundary stays auditable
- ⚠️ **Unverified / not taken** — promising, but either the licence is unconfirmed or we have not needed it yet
- ❌ **Declined** — contains content that cannot safely be redistributed, or a licence claim that does not hold

## Bibles & manuscripts

| Source | What it is | Licence | Used here? | Why it matters |
|---|---|---|---|---|
| [scrollmapper/bible_databases](https://github.com/scrollmapper/bible_databases) | 140 Bible versions + cross-reference databases (SQL/CSV/JSON) | Repo/schema: MIT. Per-translation copyright **not documented** | ✅ Used, filtered | Confirmed-safe translations: KJV, ASV, YLT, AKJV, Darby, Webster, BSB, LEB, NHEB, OEB, plus Greek (Byz, TR, StatResGNT), Latin Vulgate, Syriac Peshitta. Does **not** appear to include NIV/ESV/NASB — still verify the specific translation before citing it in a study. |
| [scrollmapper/bible_databases_deuterocanonical](https://github.com/scrollmapper/bible_databases_deuterocanonical) | Deuterocanonical, extra-biblical, and related texts | Not yet confirmed — verify per-text before citing | ✅ Used | |
| [openscriptures/morphhb](https://github.com/openscriptures/morphhb) | Westminster Leningrad Codex (WLC) + morphological/lemma tagging | WLC text: public domain. Tagging: CC BY 4.0 | ✅ Used | The Hebrew original-language source AGENTS.md's word-study requirement points at. |
| [openscriptures/GreekResources](https://github.com/openscriptures/GreekResources) | Septuagint word-list/lemma/lookup tooling (NOT the LXX text itself — see notes) | CC BY 4.0 (confirmed in README) | ✅ Used | The repo's own maintainers deliberately exclude the actual Septuagint text because the CCAT source is restrictively licensed — good model to follow. Attribution: credit the Open Scriptures Septuagint Project. |
| [alshival/super_bible](https://github.com/alshival/super_bible) | CSV Bible text dumps, several English + Spanish versions, built for LLM training data | Repo claims **CC0-1.0** | ❌ Declined | Not forked. Includes a full **ESV** CSV (`super_bible_ESV.csv`). The ESV is a commercially copyrighted Crossway translation with a published permissions policy (free quotation up to 500 verses under conditions, not wholesale redistribution) — a CC0 declaration by this repo's maintainer doesn't and can't waive Crossway's copyright. If we want any of its clearly-public-domain files later, re-source them individually and verify each one, not via a blanket fork. |
| [javascripture/javascripture](https://github.com/javascripture/javascripture) | Bible data bundled with a JS project (`gh-pages/bibles`) | Not found in README | ⚠️ Unverified | Not forked. Need to check the actual `bibles/` data files and their source before deciding. |
| [berean.bible](https://berean.bible/) (Berean Standard Bible / Berean Greek Bible) | Modern, readable English translation + Greek critical text | **CC0 — dedicated to the public domain, April 2023.** Confirmed on their terms page: "all uses are freely permitted," commercial use explicitly allowed. Only ask: don't call a modified derivative "Berean." | ✅ Covered elsewhere | No single canonical GitHub source exists (BSB text is scattered across ~15 unofficial hobby repos). Already have it via `scrollmapper/bible_databases` above — a dedicated fork would be redundant. Revisit only if we need the canonical USFM form specifically (see `usfm-bible/examples.bsb`). |
| [unfoldingWord/hbo_uhb](https://git.door43.org/unfoldingWord/hbo_uhb) (UHB) | Hebrew OT in USFM with lemma, Strong's and morphology on every word | CC BY-SA 4.0 (confirmed in `LICENSE.md`, 2026-09-05) | ✅ Used | Reachable and small (~23MB). **On its own it adds little**: Genesis 1:1 gives `\w בְּ⁠רֵאשִׁ֖ית\|lemma="רֵאשִׁית" strong="b:H7225" x-morph="He,R:Ncfsa"`, which is lemma, prefixed Strong's and morphology we already hold twice over in `morphhb` and `macula-hebrew` off the same WLC text. Its actual value is being *the text ULT aligns to* — take it as the key to the alignment below, not as a third copy of the Hebrew. |
| [unfoldingWord/en_ult](https://git.door43.org/unfoldingWord/en_ult) (ULT) | Literal English translation carrying **word-level alignment to the Hebrew and Greek** | CC BY-SA 4.0 (confirmed in `LICENSE.md`, 2026-09-05) | ✅ Used | ~115MB. The one thing here nothing else supplies: every English word is wrapped in a `\zaln-s` marker naming the original word it renders, with its lemma, Strong's and morphology — *"In the beginning"* carries `x-content="בְּ⁠רֵאשִׁ֖ית"`. That turns "which Hebrew word is this English word?" from a judgement into a lookup, which is exactly what this site claims to do for cross-references. Needs `hbo_uhb` (and UGNT for the NT) to resolve against. |
| [unfoldingWord/el-x-koine_ugnt](https://git.door43.org/unfoldingWord/el-x-koine_ugnt) (UGNT) | Greek New Testament in USFM, lemma/Strong's/morphology per word — the Greek-side partner to UHB | CC BY-SA 4.0 (confirmed in `LICENSE.md`, 2026-09-05) | ✅ Used | ~20MB. **Its text is not the SBLGNT we already hold**, and that was measured rather than assumed: normalising both and comparing John verse by verse, 742 of 878 match and **136 differ** — 74 spelling-only, **62 with words added, removed or changed**. So ULT's alignment cannot be resolved against our SBLGNT; the `x-content` strings are UGNT wording. It also earns a place as a distinct witness: at John 1:34 it reads υἱός where SBLGNT has ἐκλεκτός, and at John 5:2 Βηθζαθά against Βηθεσδά. **Caution worth carrying:** UGNT follows the *Bunning Heuristic Prototype*, a text from the Center for New Testament Restoration rather than a committee edition like NA28 or SBLGNT, and its rationale is a document to read before leaning on it — the same distinction this page already draws for "majority by count". |
| [unfoldingWord/en_uhg](https://git.door43.org/unfoldingWord/en_uhg) (UHG) | Reference grammar of biblical Hebrew, 96 articles keyed to the same morphology codes | CC BY-SA 4.0 (confirmed in `LICENSE.md`, 2026-09-05) | ✅ Used | Tiny (~3MB), `.rst` files by category — *adjective_gentilic*, *definiteness*, *conjunction*. Fills a real gap rather than duplicating: this project holds lexicons (BDB, Strong's, TWOT) and morphology tags but **no grammar**, while develop-bible-study's Phase 4 asks for "grammar/syntax points that affect meaning." Currently that has to come from recall. |
| [LogosBible/SBLGNT](https://github.com/LogosBible/SBLGNT) | SBL Greek New Testament, the standard academic critical text | CC BY 4.0 (confirmed — SBL & Logos Bible Software, copyright holders since 2010) | ✅ Used | Commercial use allowed. |
| [ETCBC/bhsa](https://github.com/ETCBC/bhsa) | Biblia Hebraica Stuttgartensia with deep linguistic/syntactic annotation (text-fabric format) | **CC BY-NC 4.0 — non-commercial only** (confirmed: "do not use the data for commercial applications without consent; contact the German Bible Society" for commercial use) | 🟡 Used, restricted | Off the table if this site ever monetizes. |

## Lexicons & original language

| Source | What it is | Licence | Used here? | Why it matters |
|---|---|---|---|---|
| [openscriptures/HebrewLexicon](https://github.com/openscriptures/HebrewLexicon) | BDB (Brown-Driver-Briggs) outline linked to Strong's | CC BY 4.0 (BDB/Strong's underlying content itself is public domain) | ✅ Used | Primary Hebrew lexicon source for the develop-bible-study skill's word-study phase. |
| [openscriptures/strongs](https://github.com/openscriptures/strongs) | Strong's Dictionaries of Hebrew and Greek | No repo-level LICENSE, but confirmed via the data files themselves: Hebrew/Greek dictionary XML declares `Public Domain`; the JS/JSON compilation header declares `Copyright 2010, Open Scriptures. CC-BY-SA.` | ✅ Used | **Caveat:** the same XML also embeds TWOT (Theological Wordbook of the OT, Archer & Harris, Moody Publishers) entry *numbers* as cross-reference pointers — those numbers are explicitly marked `Copyright © 1980 by the Moody Bible Institute` in the header. Only bare TWOT reference numbers are present here (fine to keep/cite), not TWOT's actual descriptive text — don't merge in TWOT prose from elsewhere under the assumption it's covered by this same license. |
| [STEPBible/STEPBible-Data](https://github.com/STEPBible/STEPBible-Data) | Strong's-tagged texts, lexicons (incl. Tyndale brief Hebrew/Greek lexicons), morphology, TSK-style cross-references | CC BY 4.0 (confirmed in README) | ✅ Used | Broadest single source — covers lexicon *and* cross-reference needs below in one place. Attribution required: credit "STEP Bible" linked to www.STEPBible.org. |
| [jcuenod/dictionary](https://github.com/jcuenod/dictionary) (Mounce's Concise Greek-English Dictionary) | William D. Mounce's concise NT Greek dictionary | **All-rights-reserved.** README states: "Copyright 1993 All Rights Reserved www.teknia.com/greek-dictionary" — free for non-commercial, non-revenue use provided the notice stays visible. Not a CC/PD license. | 🟡 Used, restricted | The copyright notice must be kept visible wherever this data is used/displayed — that's a condition of the grant, not just a courtesy. |
| [Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek) | Per-word Greek NT (SBLGNT) morphology, lemma, gloss, and **Louw-Nida semantic domain codes** | CC BY 4.0 (Biblica, confirmed in `LICENSE.md`). Underlying sources (Nestle1904, SBLGNT, Berean Interlinear, Cherith glosses) are all PD or CC BY 4.0. **Caveat:** the Louw-Nida domain field (`@ln`, `@domain`) is drawn from UBS's MARBLE project "used with permission" **to Clear-Bible specifically** per their own license notes — not itself a blanket CC grant. Cite carefully, same spirit as the TWOT caveat on the `strongs` fork above. | ✅ Used | Turns the print-only Louw & Nida citation in the [develop-bible-study word-study-method](https://github.com/ding0t/bible_studies/blob/main/.claude/skills/develop-bible-study/word-study-method.md) into a queryable local source. |
| [Clear-Bible/macula-hebrew](https://github.com/Clear-Bible/macula-hebrew) | Per-word Hebrew OT (WLC) morphology, lemma, gloss, and **SDBH semantic domain codes** — the Hebrew-side equivalent of Louw-Nida, which is Greek-only | CC BY 4.0 (Biblica, confirmed in `LICENSE.md`) | ✅ Used | The flat TSV at `WLC/tsv/macula-hebrew.tsv` is **Git-LFS tracked** — `git-lfs` must be installed locally or the submodule checkout is just an LFS pointer stub, not real content. |
| [fhardison/hebrew-vocab-tools](https://github.com/fhardison/hebrew-vocab-tools) | Python query layer over `morphhb` + `HebrewLexicon` (both already forked above): lemma/Strong's/gloss lookups, plus paragraph/pericope chunking keyed to actual Masoretic markers (sof pasuq, samekh/pe) rather than modern chapter breaks | CC BY 4.0 (confirmed in README) | ✅ Used | Small (~9.5MB). Stagnant since 2022 but a finished, single-purpose tool — fine for this use. |

## Cross-references

| Source | What it is | Licence | Used here? | Why it matters |
|---|---|---|---|---|
| STEPBible-Data (above) | Includes TSK-style cross-reference data | CC BY 4.0 | ✅ Used | See above — no separate source needed unless it turns out incomplete. |
| scrollmapper/bible_databases (above) | Includes cross-reference databases | MIT (schema) | ✅ Used | See above — cross-ref tables come along with the Bible text fork. |

## Not pursuing

- [openscriptures/api](https://github.com/openscriptures/api) — archived, GPL-2.0, application code rather than data. No reason to fork for a static-content repo.
- [openscriptures/openscriptures](https://github.com/openscriptures/openscriptures), [openscriptures/openscriptures_site](https://github.com/openscriptures/openscriptures_site) — archived legacy code, not data.
- [scrollmapper/book_list](https://github.com/scrollmapper/book_list) — worth a look later if we need an index of what Scrollmapper's databases cover, not needed yet.
- [authenticwalk/mybibletoolbox-data](https://github.com/authenticwalk/mybibletoolbox-data) — ~3GB aggregator repackaging MACULA, UBS/SDGNT, TBTA, and eBible data as AI-context YAML/SQLite. **No repo-level LICENSE** despite mostly-clean per-file source/license metadata inside — not safe to fork wholesale. It's what led us to fork MACULA Greek/Hebrew directly (above) instead of going through this unlicensed proxy. Revisit only if a specific need arises that MACULA/SDGNT alone don't cover (e.g. TBTA's semantic-role parses — license unconfirmed).

## Backlog — from awesome-bible-developer-resources, not yet checked

Listed so nothing gets silently dropped; pull one of these in when a study actually needs it, and verify its license before forking (same process as everything above).

- **Open Hebrew Bible** — aligned historical codices
- **CATSS** — LXX morphological analysis and textual variants (watch for CCAT restrictions, same issue GreekResources deliberately worked around)
- **Perseus Digital Library** — ancient Greek texts with annotations
- **Codex Sinaiticus** (XML) — check license, British Library involvement suggests possible NC restriction
- **Open Greek New Testament (OGNT / CNTR)** — NA28-equivalent text
- **Robinson's Greek Texts** — Byzantine/Majority text
- **unfoldingWord Simplified Text (UST)** — likely CC BY-SA 4.0, not individually confirmed. (ULT and UGNT are both evaluated and tabled above.)
- **Open Bibles** (Bible Innovations) — aggregator of PD/CC translations, worth checking as a second source alongside scrollmapper
- **Abbott-Smith Manual Lexicon**, **Dodson Greek-English Lexicon**, **Liddell-Scott-Jones (LSJ)** — Greek lexicons, likely public domain (pre-1929 sources) but not confirmed per-repo

## Patristic originals (not GitHub — Internet Archive, stored outside this repo)

The church fathers are not on GitHub in any usable original-language form, so they come from the
Internet Archive instead: public-domain critical editions (CSEL, GCS, Migne) fetched as OCR text and
held on the media volume with the rest of the external reference material, never committed here.

The rule that governs them is the same one that governs translations of the Bible, and it was
learned the hard way: **an English translation can establish that a father discusses a passage and
what he argues, and can never establish what words he used.** A claim about a father's wording read
off ANF was published on this site and had to be retracted once the Latin was fetched. Seven
originals are now held — Victorinus, Eusebius (Greek, both halves of the *Church History*), Cyprian,
Irenaeus, Augustine and Tertullian — each pulled for a specific passage rather than collected. See
[references/README.md](https://github.com/ding0t/bible_studies/blob/main/references/README.md) for
the table of which claim each one answers, and the volume's own `PROVENANCE.md` for what was
verified present in each.

## eBible.org (not GitHub — fetched at build time, not forked)

[eBible.org](https://ebible.org/find/) is a plain file host, not a git repo, so the fork-under-`ding0t`-and-submodule mechanics below don't apply. Rather than vendoring raw USFM into this repo (one file dump per translation would sprawl, and there's no git history to pin against for reproducibility the way a submodule commit gives us), `references/build/build.py`'s `ingest_ebible()` downloads each translation's USFM zip on demand into a gitignored `references/build/cache/`, strips a couple of markup quirks the installed BibleOrgSys doesn't handle cleanly (see the function's own comments), and ingests straight into `bible-text.db`. Nothing here is pinned to a specific upstream revision — re-running the build re-fetches current content. Each source's license is checked individually (`ebible.org/find/show.php?id=<id>`) before adding; not everything listed there is public domain.

| eBible.org id | What it is | License | Notes |
|---|---|---|---|
| `eng-web` | World English Bible (WEB) — full Bible | Public Domain (confirmed on-page) | AGENTS.md's preferred WEB translation, previously not actually present (scrollmapper's bundle only has the unrelated older "Webster"/"RWebster" PD translations, despite a stray empty `WEB.db` stub suggesting otherwise). |
| `grcbrent` | Brenton Septuagint — actual Greek LXX text (verified by downloading and reading it directly, not just the license text — "Brenton" commonly implies his *English* translation, so this was worth checking) | Public Domain (confirmed on-page) | Fills a real gap: `GreekResources` above deliberately excludes LXX text because the CCAT source is restricted. `grclxx` (Orthodox Media Network) is a near-identical edition of the same text — skipped as redundant rather than forking both. |
| `grc-tisch` | Tischendorf 8th ed. Greek New Testament — a third distinct NT critical-text lineage alongside SBLGNT (CC BY 4.0, above) and Byzantine/TR (via scrollmapper, restricted-nc) | Public Domain (confirmed on-page) | |
| `heb` | Delitzsch — **his Hebrew New Testament**, bundled by eBible with a Hebrew Old Testament | Public Domain (confirmed on-page) | One of **two** Hebrew New Testaments here; `hebsg` below is the other. The bundle's OT half is the Hebrew Bible's own text, unpointed — *not* something Delitzsch translated, so read the work_id's "Hebrew Bible (OT+NT)" title as a container label rather than a claim about authorship. **Re-confirmed 2026-09-05 to be the same text as `scrollmapper-HebModern`** — 31,101 of 31,102 verses byte-identical — so the two work_ids are one text ingested twice, and this is the copy with a confirmed public-domain licence. What the two Hebrew New Testaments can and cannot settle is on [Bible Translations & Source Texts](../scripture/translations.md#hebrew-old-testament), not repeated here. |
| `hebsg` | Salkinson-Ginsburg Hebrew New Testament (1885, revised by Ginsburg 1886) | Public Domain (confirmed in eBible's catalog) | The second, independent Hebrew rendering of the Greek NT: Salkinson kept to vocabulary attested in the Tanakh and pointed his text, Delitzsch wrote unpointed in a more Mishnaic register, so the two differ in every verse. Both are 19th-century translations *from the Greek*. Why that matters, and the live question about its earliest printings, is on [Bible Translations & Source Texts](../scripture/translations.md#hebrew-old-testament). |

**Known data-quality caveats** (see `ingest_ebible()`'s own notes for full detail): some NT editions double-tag words (`\w` + non-standard `\ww`) or use USFM 3.0 `\w word|attr\w*` syntax the installed BibleOrgSys doesn't strip cleanly — handled with a regex pass before loading, verified against Rev 13:10 and John 3:16. LXX/deuterocanonical chapter-verse numbering can diverge from Masoretic/English versification (Psalms, Daniel, Esther especially) — don't assume `(book, chapter, verse)` lines up across works without checking.
