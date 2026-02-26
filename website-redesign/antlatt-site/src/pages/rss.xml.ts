import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const [builds, blog] = await Promise.all([
    getCollection('builds'),
    getCollection('blog', ({ data }) => !data.draft),
  ]);
  
  const site = (context.site?.toString() ?? 'https://antlatt.com').replace(/\/$/, '');
  
  // Map builds to RSS items
  const buildItems = builds.map((build) => ({
    title: build.data.title,
    pubDate: build.data.date,
    description: build.data.description,
    link: `/builds/${build.slug}/`,
    categories: build.data.tags,
  }));
  
  // Map blog posts to RSS items
  const blogItems = blog.map((post) => ({
    title: post.data.title,
    pubDate: post.data.date,
    description: post.data.description,
    link: `/blog/${post.slug}/`,
    categories: post.data.tags,
  }));
  
  // Combine and sort by date descending
  const allItems = [...buildItems, ...blogItems].sort((a, b) => 
    b.pubDate.valueOf() - a.pubDate.valueOf()
  );

  return rss({
    title: 'ANTLATT.COM',
    description: 'Tech stuff, general geekery, and whatever else catches my attention. Homelab builds, NAS setups, and more.',
    site: site,
    items: allItems,
    customData: `<language>en-us</language>
<lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
<atom:link href="${site}/rss.xml" rel="self" type="application/rss+xml"/>`,
    xmlns: {
      atom: 'http://www.w3.org/2005/Atom'
    }
  });
}