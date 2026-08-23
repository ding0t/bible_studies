import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  // The site is served from the custom domain at its ROOT (GitHub Pages cname
  // the-way.lewy.au), not from github.io/bible_studies -- github.io 301s there. There is
  // deliberately no `base`: with one, every emitted asset URL carried a /bible_studies prefix,
  // so /bible_studies/_astro/*.js 404'd on the live domain and neither tool ever hydrated.
  site: 'https://the-way.lewy.au',
  outDir: './dist',
  srcDir: './src',
  integrations: [react()],
  vite: {
    ssr: { external: ['path'] },
  },
});
