---
title: "Open Bible Data on GitHub"
category: "resources"
description: "Master list of open-license Bible text, manuscript, lexicon, and cross-reference repositories we fork for use in this project, and why."
tags: ["resources", "github", "hebrew", "greek", "lexicon", "strongs", "manuscripts", "licensing"]
draft: true
---

# Open Bible Data on GitHub

Master list of external repositories we're forking (or considering forking) as open-data sources for study development — see the [develop-bible-study skill](https://github.com/ding0t/bible_studies/blob/main/.claude/skills/develop-bible-study/SKILL.md) for how this data gets used, and the note on our copyright approach in [references/README.md](https://github.com/ding0t/bible_studies/blob/main/references/README.md).

Sourced partly from [biblenerd/awesome-bible-developer-resources](https://github.com/biblenerd/awesome-bible-developer-resources), a curated list of Bible developer resources — good place to check first when we need a new data type.

**Rule we're following:** a repository's own license (MIT, CC0, etc.) only covers *their* code/compilation — it does not override the copyright status of third-party text they've bundled in (a Bible translation, a lexicon). Every entry below is checked for this specifically, because at least one candidate below gets it wrong.

**Status key**

- ✅ **Fork** — license confirmed fully open (CC BY, CC0, public domain), safe to fork into `references/open-data/` unconditionally
- 🟡 **Fork, restricted** — usable now under the license's terms, but not unconditionally open (e.g. non-commercial-only) — goes in `references/restricted-data/`, not `open-data/`. Fine to keep public as long as this site stays non-commercial; revisit if that ever changes.
- ⚠️ **Verify** — promising, but license isn't confirmed yet; don't fork until it is
- ❌ **Skip / partial only** — contains content we can't safely redistribute; do not fork wholesale

## Bibles & manuscripts

| Repo | What it is | License | Status | Our fork / submodule |
|---|---|---|---|---|
| [scrollmapper/bible_databases](https://github.com/scrollmapper/bible_databases) | 140 Bible versions + cross-reference databases (SQL/CSV/JSON) | Repo/schema: MIT. Per-translation copyright **not documented** | ✅ Forked, ⚠️ filter on use | [ding0t/bible_databases](https://github.com/ding0t/bible_databases) → `references/open-data/scrollmapper-bible-databases/`. **~12GB on disk** (GitHub's compressed-size estimate of ~4.2GB undersold it) — full repo, kept for the update path. Confirmed-safe translations: KJV, ASV, YLT, AKJV, Darby, Webster, BSB, LEB, NHEB, OEB, plus Greek (Byz, TR, StatResGNT), Latin Vulgate, Syriac Peshitta. Does **not** appear to include NIV/ESV/NASB — still verify the specific translation before citing it in a study. |
| [scrollmapper/bible_databases_deuterocanonical](https://github.com/scrollmapper/bible_databases_deuterocanonical) | Deuterocanonical, extra-biblical, and related texts | Not yet confirmed — verify per-text before citing | ✅ Forked | [ding0t/bible_databases_deuterocanonical](https://github.com/ding0t/bible_databases_deuterocanonical) → `references/open-data/scrollmapper-bible-databases-deuterocanonical/` |
| [openscriptures/morphhb](https://github.com/openscriptures/morphhb) | Westminster Leningrad Codex (WLC) + morphological/lemma tagging | WLC text: public domain. Tagging: CC BY 4.0 | ✅ Forked | [ding0t/morphhb](https://github.com/ding0t/morphhb) → `references/open-data/morphhb/`. The Hebrew original-language source AGENTS.md's word-study requirement points at. |
| [openscriptures/GreekResources](https://github.com/openscriptures/GreekResources) | Septuagint word-list/lemma/lookup tooling (NOT the LXX text itself — see notes) | CC BY 4.0 (confirmed in README) | ✅ Forked | [ding0t/GreekResources](https://github.com/ding0t/GreekResources) → `references/open-data/greek-resources/`. The repo's own maintainers deliberately exclude the actual Septuagint text because the CCAT source is restrictively licensed — good model to follow. Attribution: credit the Open Scriptures Septuagint Project. |
| [alshival/super_bible](https://github.com/alshival/super_bible) | CSV Bible text dumps, several English + Spanish versions, built for LLM training data | Repo claims **CC0-1.0** | ❌ Skip | Not forked. Includes a full **ESV** CSV (`super_bible_ESV.csv`). The ESV is a commercially copyrighted Crossway translation with a published permissions policy (free quotation up to 500 verses under conditions, not wholesale redistribution) — a CC0 declaration by this repo's maintainer doesn't and can't waive Crossway's copyright. If we want any of its clearly-public-domain files later, re-source them individually and verify each one, not via a blanket fork. |
| [javascripture/javascripture](https://github.com/javascripture/javascripture) | Bible data bundled with a JS project (`gh-pages/bibles`) | Not found in README | ⚠️ Verify | Not forked. Need to check the actual `bibles/` data files and their source before deciding. |
| [berean.bible](https://berean.bible/) (Berean Standard Bible / Berean Greek Bible) | Modern, readable English translation + Greek critical text | **CC0 — dedicated to the public domain, April 2023.** Confirmed on their terms page: "all uses are freely permitted," commercial use explicitly allowed. Only ask: don't call a modified derivative "Berean." | ✅ Covered, not separately forked | No single canonical GitHub source exists (BSB text is scattered across ~15 unofficial hobby repos). Already have it via `scrollmapper/bible_databases` above — a dedicated fork would be redundant. Revisit only if we need the canonical USFM form specifically (see `usfm-bible/examples.bsb`). |
| [unfoldingWord/hbo_uhb](https://git.door43.org/unfoldingWord/hbo_uhb) (UHB) | Lexically tagged, morphologically parsed Hebrew OT | CC BY-SA 4.0 (confirmed) | ⚠️ Blocked on mechanism | Hosted on Door43 (Gitea), not GitHub — `gh repo fork` doesn't cross platforms. Forking there needs a separate Door43 account and a different process than everything else in this doc. Holding off rather than half-doing the "fork for permanence" pattern; revisit if a study specifically needs UHB over `morphhb`. |
| [LogosBible/SBLGNT](https://github.com/LogosBible/SBLGNT) | SBL Greek New Testament, the standard academic critical text | CC BY 4.0 (confirmed — SBL & Logos Bible Software, copyright holders since 2010) | ✅ Forked | [ding0t/SBLGNT](https://github.com/ding0t/SBLGNT) → `references/open-data/sblgnt/`. Commercial use allowed. |
| [ETCBC/bhsa](https://github.com/ETCBC/bhsa) | Biblia Hebraica Stuttgartensia with deep linguistic/syntactic annotation (text-fabric format) | **CC BY-NC 4.0 — non-commercial only** (confirmed: "do not use the data for commercial applications without consent; contact the German Bible Society" for commercial use) | 🟡 Forked, restricted | [ding0t/bhsa](https://github.com/ding0t/bhsa) → `references/restricted-data/bhsa/`. Off the table if this site ever monetizes. |

## Lexicons & original language

| Repo | What it is | License | Status | Our fork / submodule |
|---|---|---|---|---|
| [openscriptures/HebrewLexicon](https://github.com/openscriptures/HebrewLexicon) | BDB (Brown-Driver-Briggs) outline linked to Strong's | CC BY 4.0 (BDB/Strong's underlying content itself is public domain) | ✅ Forked | [ding0t/HebrewLexicon](https://github.com/ding0t/HebrewLexicon) → `references/open-data/hebrew-lexicon/`. Primary Hebrew lexicon source for the develop-bible-study skill's word-study phase. |
| [openscriptures/strongs](https://github.com/openscriptures/strongs) | Strong's Dictionaries of Hebrew and Greek | No repo-level LICENSE, but confirmed via the data files themselves: Hebrew/Greek dictionary XML declares `Public Domain`; the JS/JSON compilation header declares `Copyright 2010, Open Scriptures. CC-BY-SA.` | ✅ Forked | [ding0t/strongs](https://github.com/ding0t/strongs) → `references/open-data/strongs/`. **Caveat:** the same XML also embeds TWOT (Theological Wordbook of the OT, Archer & Harris, Moody Publishers) entry *numbers* as cross-reference pointers — those numbers are explicitly marked `Copyright © 1980 by the Moody Bible Institute` in the header. Only bare TWOT reference numbers are present here (fine to keep/cite), not TWOT's actual descriptive text — don't merge in TWOT prose from elsewhere under the assumption it's covered by this same license. |
| [STEPBible/STEPBible-Data](https://github.com/STEPBible/STEPBible-Data) | Strong's-tagged texts, lexicons (incl. Tyndale brief Hebrew/Greek lexicons), morphology, TSK-style cross-references | CC BY 4.0 (confirmed in README) | ✅ Forked | [ding0t/STEPBible-Data](https://github.com/ding0t/STEPBible-Data) → `references/open-data/stepbible-data/`. Broadest single source — covers lexicon *and* cross-reference needs below in one place. Attribution required: credit "STEP Bible" linked to www.STEPBible.org. |
| [jcuenod/dictionary](https://github.com/jcuenod/dictionary) (Mounce's Concise Greek-English Dictionary) | William D. Mounce's concise NT Greek dictionary | **All-rights-reserved.** README states: "Copyright 1993 All Rights Reserved www.teknia.com/greek-dictionary" — free for non-commercial, non-revenue use provided the notice stays visible. Not a CC/PD license. | 🟡 Forked, restricted | [ding0t/dictionary](https://github.com/ding0t/dictionary) → `references/restricted-data/mounce-dictionary/`. The copyright notice must be kept visible wherever this data is used/displayed — that's a condition of the grant, not just a courtesy. |
| [Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek) | Per-word Greek NT (SBLGNT) morphology, lemma, gloss, and **Louw-Nida semantic domain codes** | CC BY 4.0 (Biblica, confirmed in `LICENSE.md`). Underlying sources (Nestle1904, SBLGNT, Berean Interlinear, Cherith glosses) are all PD or CC BY 4.0. **Caveat:** the Louw-Nida domain field (`@ln`, `@domain`) is drawn from UBS's MARBLE project "used with permission" **to Clear-Bible specifically** per their own license notes — not itself a blanket CC grant. Cite carefully, same spirit as the TWOT caveat on the `strongs` fork above. | ✅ Forked | [ding0t/macula-greek](https://github.com/ding0t/macula-greek) → `references/open-data/macula-greek/`. **~970MB.** The file that actually matters is the flat per-token TSV at `SBLGNT/tsv/macula-greek-SBLGNT.tsv` — turns the print-only Louw & Nida citation in the [develop-bible-study word-study-method](https://github.com/ding0t/bible_studies/blob/main/.claude/skills/develop-bible-study/word-study-method.md) into a queryable local source. |
| [Clear-Bible/macula-hebrew](https://github.com/Clear-Bible/macula-hebrew) | Per-word Hebrew OT (WLC) morphology, lemma, gloss, and **SDBH semantic domain codes** — the Hebrew-side equivalent of Louw-Nida, which is Greek-only | CC BY 4.0 (Biblica, confirmed in `LICENSE.md`) | ✅ Forked | [ding0t/macula-hebrew](https://github.com/ding0t/macula-hebrew) → `references/open-data/macula-hebrew/`. **~2.7GB** on disk (similar scale to `bible_databases` above). The flat TSV at `WLC/tsv/macula-hebrew.tsv` is **Git-LFS tracked** — `git-lfs` must be installed locally or the submodule checkout is just an LFS pointer stub, not real content. |
| [fhardison/hebrew-vocab-tools](https://github.com/fhardison/hebrew-vocab-tools) | Python query layer over `morphhb` + `HebrewLexicon` (both already forked above): lemma/Strong's/gloss lookups, plus paragraph/pericope chunking keyed to actual Masoretic markers (sof pasuq, samekh/pe) rather than modern chapter breaks | CC BY 4.0 (confirmed in README) | ✅ Forked | [ding0t/hebrew-vocab-tools](https://github.com/ding0t/hebrew-vocab-tools) → `references/open-data/hebrew-vocab-tools/`. Small (~9.5MB). Stagnant since 2022 but a finished, single-purpose tool — fine for this use. |

## Cross-references

| Repo | What it is | License | Status | Our fork / submodule |
|---|---|---|---|---|
| STEPBible-Data (above) | Includes TSK-style cross-reference data | CC BY 4.0 | ✅ Forked | See above — no separate source needed unless it turns out incomplete. |
| scrollmapper/bible_databases (above) | Includes cross-reference databases | MIT (schema) | ✅ Forked | See above — cross-ref tables come along with the Bible text fork. |

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
- **unfoldingWord Greek NT (UGNT), Literal Text (ULT), Simplified Text (UST)** — likely CC BY-SA 4.0 like `hbo_uhb` above, not individually confirmed yet
- **Open Bibles** (Bible Innovations) — aggregator of PD/CC translations, worth checking as a second source alongside scrollmapper
- **World English Bible (WEB)** — public domain by design; AGENTS.md already lists WEB as a preferred version, worth sourcing directly rather than only via scrollmapper
- **Abbott-Smith Manual Lexicon**, **Dodson Greek-English Lexicon**, **Liddell-Scott-Jones (LSJ)** — Greek lexicons, likely public domain (pre-1929 sources) but not confirmed per-repo

## Fork mechanics

Once a row above is ✅: fork under `ding0t` on GitHub, add as a git submodule at `references/open-data/<name>/`, and record the fork URL + submodule path in this table.

Once a row is 🟡: same fork/submodule process, but the target is `references/restricted-data/<name>/` instead — kept separate so the public/commercial-safety boundary stays a directory boundary, not something to remember. `references/open-data/` stays unconditionally-safe; `references/restricted-data/` is safe under current (non-commercial) use and needs a second look only if that ever changes.

See the [develop-bible-study skill](https://github.com/ding0t/bible_studies/blob/main/.claude/skills/develop-bible-study/SKILL.md) for how the resulting data gets used, and keep anything not ✅ or 🟡 out of `references/` entirely — that's what makes this repo safe to make public again (or to monetize, for the 🟡 tier) without a content audit.
