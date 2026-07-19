---
title: "Jewish Literature & Primary Sources"
category: "resources"
description: "Sefaria and other sources for Jewish literature (Mishnah, Talmud) relevant to understanding a passage's Second Temple / rabbinic background"
tags: ["resources", "jewish-literature", "mishnah", "talmud", "sefaria", "licensing"]
draft: true
---

# Jewish Literature & Primary Sources

Companion to [github.md](github.md) (open Bible data) — this page tracks sources for **Jewish literature outside the Bible itself**: the Mishnah, Talmud, and related rabbinic material that supplies historical/cultural background for a study (see the develop-bible-study skill's Phase 2), the way [the Last Supper study](../studies/feasts/last-supper-four-cups.md) leans on the Mishnah's Passover Seder structure.

## Sefaria

[Sefaria](https://www.sefaria.org) is a nonprofit digital library of Jewish texts — Tanakh, Mishnah, Talmud, Midrash, and centuries of commentary — with a public [API](https://developers.sefaria.org/reference/getting-started) (no key required) and a bulk data export, [Sefaria-Export](https://github.com/Sefaria/Sefaria-Export), hosted on public Google Cloud Storage.

**Licensing — check per text, per version, every time.** Sefaria's own summary: most of the underlying ancient/rabbinic texts are public domain (no living author to hold copyright), but *specific translations* range from CC0 through CC-BY, CC-BY-SA, to CC-BY-NC, and each version of a text carries its own license independently. The **default English translation Sefaria displays on its website is often CC-BY-NC** (e.g. the William Davidson Edition of the Mishnah/Talmud, a Koren/Steinsaltz translation) — don't assume the first thing you see is fully open. Query the version list before picking one to quote from.

Example — Mishnah Pesachim's available English translations:

| Version | License |
|---|---|
| Sefaria Community Translation | **CC0** |
| Mishnah Yomit by Dr. Joshua Kulp | CC-BY |
| The Mishna with Obadiah Bartenura (trans. Silverstein) | CC-BY |
| Eighteen Treatises from the Mishna (1845) | Public Domain |
| Open Mishnah | CC-BY-SA |
| William Davidson Edition (Sefaria's own default) | CC-BY-NC |

Prefer the CC0/CC-BY/public-domain options over the CC-BY-NC default when one exists — this site is non-commercial today, so CC-BY-NC is usable, but there's no reason to reach for the more restricted option when a fully open one says the same thing.

### Fetching a text

`references/build/sefaria.py` fetches and caches a specific text/version from the Sefaria-Export GCS bucket (no API key, no rate-limit concerns since it hits the static export rather than the live API):

```bash
cd references/build
uv run python sefaria.py --category "Mishnah/Seder Moed" --title "Mishnah Pesachim" \
  --language English --version "Sefaria Community Translation" --chapter 10 --section 7
```

This is deliberately **not** wired into `bible-text.db` — Mishnah/Talmud addressing (chapter + mishnah/daf, no verse) doesn't fit that schema's Bible-book/chapter/verse columns. It's a standalone fetch-and-cache helper; call `fetch_text()`/`get_section()` directly from Python for anything more involved than a one-off lookup. See `references/README.md` for how this fits alongside the other source-tracking tools.

### Not yet used, worth knowing about

Sefaria's library goes well beyond the Mishnah — Talmud Bavli/Yerushalmi, Midrash Rabbah, Targumim, Second Temple-period works, and centuries of commentary (Rashi, Ibn Ezra, Bartenura, etc.), all reachable the same way (fetch by category/title/language/version, check the license). Pull in what a specific study actually needs; there's no value in bulk-fetching the ~26GB export up front.
