import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const builds = await getCollection('builds');

  const searchIndex = builds.map(build => ({
    title: build.data.title,
    description: build.data.description,
    url: `/builds/${build.slug}/`,
    tags: build.data.tags || [],
    content: (build.body || '').toLowerCase().slice(0, 5000) // Truncate for performance
  }));

  return new Response(JSON.stringify(searchIndex), {
    headers: { 'Content-Type': 'application/json' }
  });
}