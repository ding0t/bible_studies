import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  // GitHub Pages configuration
  site: 'https://gh-ding0t.github.io/bible_end_times/',
  // Build to dist directory for GitHub Pages
  outDir: './dist',
  integrations: [react()],
  // Keep docs directory as source of content
  srcDir: './src',
  // Enable Content Layer API for collections
  experimental: {
    contentLayer: true
  },
  // Allow reading from docs for content collections
  vite: {
    ssr: {
      external: ['path']
    }
  }
});
