import { defineCollection, z } from 'astro:content';

const builds = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    image: z.string().optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    // Series/Collection support
    series: z.object({
      name: z.string(),
      order: z.number(),
    }).optional(),
    // Parts for the PartsTable component
    parts: z.array(z.object({
      name: z.string(),
      model: z.string().optional(),
      price: z.number().optional(),
      link: z.string().optional(),
      affiliate: z.enum(['amazon', 'newegg']).optional()
    })).optional(),
    // Cost calculator options
    calculatorParts: z.array(z.object({
      name: z.string(),
      basePrice: z.number(),
      options: z.array(z.object({
        label: z.string(),
        value: z.string(),
        price: z.number()
      })).optional()
    })).optional(),
  }),
});

export const collections = { builds };