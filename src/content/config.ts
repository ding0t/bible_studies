import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const studies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../../docs/content' }),
  schema: z.object({
    title: z.string(),
    year: z.number().optional(),
    category: z.enum(['prophecy', 'theology', 'spiritual-disciplines', 'sins', 'feasts', 'sermons', 'hebrew-studies', 'dreams-visions', 'teaching-resources', 'deliverance', 'other']).optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().default(false),
    bible_references: z.array(z.string()).optional(),
    zadok_year: z.number().optional(),
    gregorian_year: z.number().optional(),
  })
});

export const collections = { studies };
