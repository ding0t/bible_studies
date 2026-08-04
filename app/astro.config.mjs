import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://ding0t.github.io',
  base: '/bible_studies',
  outDir: './dist',
  srcDir: './src',
  integrations: [react()],
  vite: {
    ssr: { external: ['path'] },
  },
});
