# References

Supporting material for developing studies in this repo — see the [develop-bible-study skill](../.claude/skills/develop-bible-study/SKILL.md) for the process this feeds into.

## open-data/ and restricted-data/

Git submodules of forked open-data repos (Bible texts, lexicons, morphology, cross-references) — see [docs/content/resources/github.md](../docs/content/resources/github.md) for the full master list, license findings, and why each one's there.

- **`open-data/`** — unconditionally open licenses only (CC BY, CC0, public domain). Safe regardless of this repo's visibility or commercial status.
- **`restricted-data/`** — usable now, but under non-commercial-only or similarly restricted terms. Fine to keep public as long as this site stays non-commercial; would need re-review if that ever changes. Never mix these into `open-data/` — the directory boundary *is* the audit boundary.

## study-state/

One structured-data file per study in progress, tracking exegesis/hermeneutics progress so work can resume across sessions. See [study-state.template.yml](../.claude/skills/develop-bible-study/study-state.template.yml) for the schema. Safe to commit — it's metadata (passages, stages, sources consulted), not copyrighted source text.

## Word study & original-language tools

For the Hebrew/Aramaic/Greek word studies AGENTS.md requires (original text + gloss + pronunciation), prefer the forked data in `open-data/` (`hebrew-lexicon`, `strongs`, `morphhb`, `stepbible-data`, `greek-resources`) for agent/offline use. For quick manual lookups:

- **[Blue Letter Bible](https://www.blueletterbible.org/)** — interlinear + Strong's-tagged lookup, Hebrew and Greek, free.
- **[STEP Bible](https://www.stepbible.org/)** (Tyndale House) — interlinear, lexicons, and original-language search, free.
- **[Bible Hub interlinear](https://biblehub.com/interlinear/)** — quick interlinear + Strong's cross-links.
- **Louw & Nida, *Greek-English Lexicon of the New Testament Based on Semantic Domains*** — groups Greek words by usage relationship rather than lexical root; the cross-check step in the fuller word-study method (see the [develop-bible-study word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md)) leans on this. Not held locally as data; consult in print or via a library/seminary access point.

For Hebrew *language learning* (as opposed to word-study lookup), see the existing [hebrew-studies/resources.md](../docs/content/hebrew-studies/resources.md).

## Cross-reference tools

- **Treasury of Scripture Knowledge (TSK)** — public domain (1836), the standard cross-reference set; available on Bible Hub and Blue Letter Bible per-verse.
- **Bible Gateway / Bible Hub parallel view** — quick multi-translation comparison, needed for the translation-comparison step in Phase 6 of the skill.

## Secondary/commentary sources

- *How to Read the Bible for All Its Worth* (Fee & Stuart, 4th ed.) — the methodology behind the develop-bible-study skill. **Not committed to this repo**: it's a commercially-sold, copyrighted work and this repo is public. A markdown extraction is kept locally next to the source PDF on the personal media volume it was extracted from, for the user's own reference — do not copy substantial passages from it into any file that gets committed here (see the copyright guardrail in the skill).
- Gerald L. Stevens, "Word Study Guide — New Testament" (seminary course handout) — the methodology behind [word-study-method.md](../.claude/skills/develop-bible-study/word-study-method.md). **Not committed to this repo**: course material, not public domain. Source PDF stays on the personal media volume (`/Volumes/media/bible/resources/NTWordStudyGuide.pdf`); the skill file is an original synthesis of the method, not a reproduction.
- Any other commentary consulted for a study should be recorded per-study in that study's `resources_consulted` field, not duplicated here.
