# Content File Guidelines

This guide helps you create valid markdown content files that work properly with the site.

## Quick Start

Every markdown file in `docs/content/` should follow this structure:

```markdown
---
title: "Your Study Title"
category: "prophecy"
description: "A brief description of the study"
tags: ["tag1", "tag2", "tag3"]
draft: false
---

# Your Content Here

Write your markdown content...
```

## Required Fields

### title (Required)
- Must be present and non-empty
- Should be a descriptive title for the study
- Use quotes for multi-word titles

```yaml
title: "The Feasts of the Lord"
```

## Recommended Fields

### category (Recommended)
- Groups studies together on the studies page
- If omitted, defaults to "other"
- Common categories: `prophecy`, `theology`, `spiritual-disciplines`, `sins`, `feasts`, `sermons`, etc.

```yaml
category: "prophecy"
```

### description (Recommended)
- Brief summary of the content
- Used for SEO and study cards
- Keep it under 200 characters

```yaml
description: "Understanding the biblical feasts and their prophetic significance"
```

### tags (Recommended)
- Array of strings for categorization
- Use quotes around each tag
- Helps with searching and filtering

```yaml
tags: ["feasts", "prophecy", "leviticus", "appointed-times"]
```

### draft (Recommended)
- Controls whether the study appears on the site
- `false` = published (default if omitted)
- `true` = hidden from public view

```yaml
draft: false
```

## Optional Fields

### bible_references
- Array of scripture references
- Displayed on study cards

```yaml
bible_references: ["Leviticus 23", "Colossians 2:16-17", "Hebrews 10:1"]
```

### year, zadok_year, gregorian_year
- Numeric fields for timeline integration

```yaml
year: 2024
zadok_year: 5999
gregorian_year: 2024
```

## Common Mistakes to Avoid

### ❌ Blank line before frontmatter

**WRONG:**
```markdown

---
title: "My Study"
---
```

**CORRECT:**
```markdown
---
title: "My Study"
---
```

The `---` must be on line 1 with no blank lines before it!

### ❌ Missing closing frontmatter delimiter

**WRONG:**
```markdown
---
title: "My Study"

# Content here
```

**CORRECT:**
```markdown
---
title: "My Study"
---

# Content here
```

### ❌ Unquoted strings with special characters

**WRONG:**
```yaml
title: My Study: Part 1
```

**CORRECT:**
```yaml
title: "My Study: Part 1"
```

### ❌ Unquoted array values

**WRONG:**
```yaml
tags: [prophecy, feasts, jesus]
```

**CORRECT:**
```yaml
tags: ["prophecy", "feasts", "jesus"]
```

## Images and Assets

When referencing images in your markdown files, use the correct relative paths:

### Correct Image Paths

The path depends on how deep your file is in the directory structure. Count the levels from your file to `docs/`, then add `assets/img/`:

**From `docs/content/sermons/file.md` (2 levels deep):**
```markdown
![Description](../../assets/img/image-name.jpg)
```

**From `docs/content/studies/prophecy/file.md` (3 levels deep):**
```markdown
![Description](../../../assets/img/image-name.jpg)
```

**Quick rule:** Count the directory separators from `docs/content/` to your file, then use that many `../` followed by `assets/img/`

### Image Directory Structure

All images should be placed in:

```text
docs/assets/img/
```

Example structure:

```text
docs/
├── assets/
│   └── img/
│       ├── larkin/
│       │   └── c07.jpg
│       └── hebrew-alphabet.png
└── content/
    └── studies/
        └── my-study.md
```

### Common Image Path Mistakes

❌ **WRONG:** `![Image](../img/photo.jpg)` (missing 'assets')
✅ **CORRECT:** Use proper relative path with `assets/img/`

❌ **WRONG:** `![Image](/img/photo.jpg)` (absolute path won't work)
✅ **CORRECT:** Use relative path like `../../assets/img/photo.jpg` or `../../../assets/img/photo.jpg`

❌ **WRONG:** `![Image](../../assets/img/photo.jpg)` (from 3 levels deep)
✅ **CORRECT:** `![Image](../../../assets/img/photo.jpg)` (count the levels!)

## Validation

Run the validation script to check your content files:

```bash
npm run validate
```

This will:
- Check for proper frontmatter structure
- Verify required fields are present
- Warn about missing recommended fields
- Identify common formatting issues

## What Happens with Invalid Files?

The site is designed to be resilient:

1. **Missing title**: Falls back to "Untitled Study" (but will be hidden from published list)
2. **Missing category**: Defaults to "other"
3. **Missing description**: Defaults to empty string
4. **Missing tags**: Defaults to empty array
5. **Missing draft**: Defaults to `false` (published)
6. **Invalid frontmatter structure**: File will be skipped entirely

However, it's best practice to provide all recommended fields for the best user experience.

## Categories

New categories are automatically supported! Just use any string value:

```yaml
category: "my-new-category"
```

The site will auto-generate a formatted label ("My New Category") and display it properly.

Common existing categories:
- `prophecy` - Prophecy fulfilled in Jesus
- `theology` - Theological studies
- `spiritual-disciplines` - Prayer, fasting, etc.
- `sins` - Sin and redemption
- `feasts` - Biblical feasts and seasons
- `sermons` - Sermon notes and presentations
- `hebrew-studies` - Hebrew language and culture
- `dreams` / `dreams-visions` - Dreams and visions
- `teaching-resources` - Teaching materials
- `deliverance` - Deliverance ministry
- `investigation` - Investigative studies
- `archeology` - Archaeological findings
- `commentaries` - Bible commentaries
- `other` - Miscellaneous studies

## Examples

### Minimal Valid File
```markdown
---
title: "My Simple Study"
---

Content goes here.
```

### Complete Example
```markdown
---
title: "The Day of Atonement: Yom Kippur"
category: "feasts"
description: "An in-depth study of the Day of Atonement and its fulfillment in Christ"
tags: ["feasts", "atonement", "leviticus", "jesus", "redemption"]
draft: false
bible_references: ["Leviticus 16", "Leviticus 23:27-32", "Hebrews 9:11-14"]
---

# The Day of Atonement

The Day of Atonement, known in Hebrew as **Yom Kippur**, is the holiest day of the year...
```

## Getting Help

If you encounter issues with content files:

1. Run `npm run validate` to identify problems
2. Check the console output when running `npm run dev`
3. Review this guide for common mistakes
4. Check that frontmatter starts on line 1
5. Ensure all strings with special characters are quoted
