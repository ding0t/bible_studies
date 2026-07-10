import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://gh-ding0t.github.io',
  base: '/bible_end_times',
  outDir: './dist',
  srcDir: './src',
  integrations: [react()],
  vite: {
    ssr: { external: ['path'] },
  },
});
