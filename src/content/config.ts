import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const studies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './docs/content' }),
  schema: z.object({
    // Title is the only truly required field, but provide a fallback
    title: z.string().catch('Untitled Study'),

    // Make all other fields optional with sensible defaults
    year: z.number().catch(undefined),
    category: z.string().default('other'),
    description: z.string().default(''),
    tags: z.array(z.string()).catch([]),
    draft: z.boolean().catch(false),
    bible_references: z.array(z.string()).catch([]),
    zadok_year: z.number().catch(undefined),
    gregorian_year: z.number().catch(undefined),

    // Allow marp and other unknown frontmatter fields without failing
  }).passthrough()
});

export const collections = { studies };
