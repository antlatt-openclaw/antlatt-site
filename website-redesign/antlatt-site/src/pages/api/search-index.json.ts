import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const [builds, blog] = await Promise.all([
    getCollection('builds'),
    getCollection('blog', ({ data }) => !data.draft),
  ]);

  // Index builds
  const buildIndex = builds.map(build => ({
    title: build.data.title,
    description: build.data.description,
    url: `/builds/${build.slug}/`,
    tags: build.data.tags || [],
    date: build.data.date.toISOString(),
    type: 'build',
    content: (build.body || '').toLowerCase().slice(0, 5000) // Truncate for performance
  }));
  
  // Index blog posts
  const blogIndex = blog.map(post => ({
    title: post.data.title,
    description: post.data.description,
    url: `/blog/${post.slug}/`,
    tags: post.data.tags || [],
    date: post.data.date.toISOString(),
    type: 'blog',
    content: (post.body || '').toLowerCase().slice(0, 5000) // Truncate for performance
  }));
  
  // Combine and sort by date descending
  const searchIndex = [...buildIndex, ...blogIndex].sort((a, b) => 
    new Date(b.date).valueOf() - new Date(a.date).valueOf()
  );

  return new Response(JSON.stringify(searchIndex), {
    headers: { 'Content-Type': 'application/json' }
  });
}