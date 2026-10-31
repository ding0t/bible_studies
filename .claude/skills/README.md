# Skills: how to keep them right

A skill is instructions an agent follows literally, and nothing fails when one goes stale. These
rules keep them true to the repo and small enough to load.

`python3 utils/check_skills.py` checks the mechanical half on every `npm test`: frontmatter, links
and anchors, MCP tool names against `references/build/mcp_server.py`, and repo paths against the
disk. It also warns when a SKILL.md passes 5,000 words.

## Rules for writing a skill

1. **Each fact has one home.** A rule is written out once — in AGENTS.md, in the `bible-references`
   server's instructions, or in one skill — and everywhere else gets a one-line pointer to it.
   Copies drift: the sibling-study check and the versification rule were each in three or four
   places, and the copies had started to disagree in detail.
2. **State the rule; keep the history elsewhere.** "Until 2026-09-05 nothing answered this" belongs
   in a commit message or `references/README.md`. Keep one example from this corpus where it shows
   why the rule exists, and no more.
3. **SKILL.md is the workflow; detail goes in a companion file.** SKILL.md is loaded whole whenever
   the skill runs. Reference tables, specimens and format rules live beside it
   (`develop-bible-study/formatting.md`, `style-guide.md`) and are linked, one level deep.
4. **The description says what the skill does and when to use it**, and how it differs from its
   neighbours, in under 1,024 characters. It is all an agent sees when choosing a skill.
5. **Name tools, paths and sections exactly, in backticks.** That is what lets the checker find them
   when they move.
6. **An exemption in the checker carries its reason** (`NOT_TOOLS`, `ABSENT_PATHS` are dicts),
   per AGENTS.md.

## When to review them

The checker catches a renamed tool or a moved file. It cannot catch duplication, bloat, or a rule
that no longer matches practice. Read the skills through:

- after a toolchain change: a tool renamed, a section or directory moved, a validator check added;
- after the author corrects an agent's work by hand in a way a skill should have prevented;
- otherwise about once a month.

| Skill | Answers | Rule |
|---|---|---|
| develop-bible-study | build it | exegesis before hermeneutics |
| review-bible-study | is it true? | re-derive, don't re-read |
| read-bible-study | can it be read? | change no sentence |
| simplify-bible-study | is it the right size? | add nothing |
| youth-bible-study | can a child follow it? | say nothing the study does not |
| one-minute-comic | can it be told in a minute? | every bubble is the ESV or marked condensed |
