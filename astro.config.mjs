import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
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
