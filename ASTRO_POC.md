# Astro Migration Proof of Concept

## Overview

This proof of concept demonstrates how to migrate your Bible studies project from MkDocs to Astro with an interactive timeline feature.

## Project Structure

```
bible_end_times/
├── src/
│   ├── components/
│   │   └── TimelineComponent.jsx      # Interactive timeline with zoom
│   ├── layouts/
│   │   └── BaseLayout.jsx              # Main layout wrapper
│   ├── pages/
│   │   ├── index.astro                 # Timeline homepage
│   │   └── studies.astro               # Studies directory
│   └── styles/
│
├── docs/                                # UNCHANGED - your existing content
│   ├── bible/
│   ├── studies/
│   ├── dreams/
│   ├── slides/
│   └── ...
│
├── astro.config.mjs                    # Astro configuration
├── tsconfig.json                       # TypeScript configuration
└── package.json                        # Dependencies
```

## Key Features

### 1. Interactive Timeline Component
- **Location:** `src/components/TimelineComponent.jsx`
- **Features:**
  - Zoom in/out with smooth scaling
  - Click events to view narrative details
  - Year-based positioning
  - Responsive design
  - Client-side hydration with React

### 2. Flexible Content Loading
Your `/docs` directory remains unchanged. Future integration options:

**Option A: Direct Static Generation**
```js
// src/content/config.ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const prophecy = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './docs/studies' }),
  schema: z.object({
    title: z.string(),
    year: z.number().optional(),
  })
});
```

**Option B: Markdown Import**
```astro
---
// src/pages/studies/[slug].astro
import { getCollection } from 'astro:content';

const prophecyStudies = await getCollection('prophecy');
export const getStaticPaths = () => prophecyStudies.map(study => ({
  params: { slug: study.slug },
  props: { study }
}));

const { study } = Astro.props;
---
<BaseLayout title={study.data.title}>
  <study.Content />
</BaseLayout>
```

## Installation & Setup

### Prerequisites
- Node.js 18+ (you have v24)
- npm or yarn

### Steps

1. **Navigate to project**
   ```powershell
   cd "c:\Users\david\OneDrive\code\gh_ding0t\bible_end_times"
   ```

2. **Install dependencies** (if npm install succeeds)
   ```powershell
   npm install
   ```

3. **Run development server**
   ```powershell
   npm run dev
   ```
   Visit `http://localhost:3000`

4. **Build for production**
   ```powershell
   npm run build
   npm run preview
   ```

### If npm Install Has Issues

If network issues persist, try:

```powershell
# Use yarn instead
npm install -g yarn
yarn install

# Or try npm with registry override
npm install --registry https://registry.npmjs.org/

# Or build without sharp (image optimization)
npm install --omit=optional
```

## Current POC Files

✅ **Created:**
- `astro.config.mjs` - Astro configuration
- `tsconfig.json` - TypeScript setup
- `package.json` - Dependencies
- `src/components/TimelineComponent.jsx` - Interactive timeline
- `src/layouts/BaseLayout.jsx` - Page layout
- `src/pages/index.astro` - Home page with timeline
- `src/pages/studies.astro` - Studies index

## Next Steps After Installation

### 1. Integrate Your Content
```astro
---
// src/pages/prophecy-essentials.astro
import { readFileSync } from 'fs';
const content = readFileSync('../docs/studies/prophecy_events_times.md', 'utf-8');
---
```

### 2. Enhance Timeline Data
Modify `TIMELINE_EVENTS` in `TimelineComponent.jsx` to pull from your markdown frontmatter:

```jsx
// Auto-generate from docs
import glob from 'glob';
import matter from 'gray-matter';

const loadTimelineEvents = async () => {
  const files = glob.sync('../../docs/**/*.md');
  return files.map(file => {
    const { data } = matter(readFileSync(file));
    return {
      year: data.year,
      title: data.title,
      description: data.description,
      content: data.content
    };
  });
};
```

### 3. Add Advanced Features
- Dynamic content loading from `/docs`
- Search across all documents
- Related events linking
- Timeline filtering by category
- Export timeline as image/PDF

### 4. Theme Customization
The `BaseLayout.jsx` contains inline styles. Move to CSS modules:
```jsx
// src/styles/timeline.module.css
import styles from '../styles/timeline.module.css';
```

## Migration Path

### Phase 1: Basic Setup (Current)
- [x] Create Astro structure
- [x] Build timeline component
- [x] Setup page layouts

### Phase 2: Content Integration
- [ ] Load markdown from `/docs`
- [ ] Generate pages from markdown
- [ ] Add frontmatter to markdown files

### Phase 3: Enhancement
- [ ] Connect timeline to actual content
- [ ] Add search functionality
- [ ] Implement related content suggestions

### Phase 4: Deployment
- [ ] Configure GitHub Pages or hosting
- [ ] Setup CI/CD pipeline
- [ ] Performance optimization

## Technical Notes

### Why Astro?
- **Zero JS by default** - Static HTML, hydrate only interactive components
- **Island Architecture** - Timeline component hydrates independently
- **Fast builds** - Vite-based
- **Flexible content** - Works with markdown, MDX, APIs, databases
- **Modern DX** - TypeScript, component frameworks, hot reload

### Component Architecture

```
BaseLayout (Astro)
  ├─ Header (Static HTML)
  ├─ Navigation (Static HTML)
  ├─ TimelineComponent (React, Client-side)
  │  └─ State: zoom, selected event
  └─ Footer (Static HTML)
```

### Build Output

The final site is completely static HTML + minimal JavaScript:
```
dist/
├── index.html           # Home page
├── studies/index.html   # Studies page
└── _astro/
    └── TimelineComponent.*.js  # Only loaded on pages that need it
```

## PowerShell Notes

Since you're using PowerShell, some useful commands:

```powershell
# Start dev server in background
Start-Job -ScriptBlock { npm run dev }

# Check if port 3000 is available
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

# Kill process on port 3000 if stuck
Get-Process node | Stop-Process -Force
```

## Resources

- [Astro Documentation](https://docs.astro.build)
- [React in Astro](https://docs.astro.build/en/guides/integrations-guide/react/)
- [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Astro Deployment (GitHub Pages)](https://docs.astro.build/en/guides/deploy/github/)

## Summary

This POC provides:
1. ✅ Working Astro setup
2. ✅ Interactive timeline component with zoom/select
3. ✅ Page structure that can read from your `/docs`
4. ✅ React component for interactivity
5. ✅ Preservation of existing content location

The timeline can be expanded to:
- Load events from your markdown frontmatter
- Display full content when events are selected
- Filter by category (prophecy, dreams, feasts, etc.)
- Add timeline comparisons and relationships
