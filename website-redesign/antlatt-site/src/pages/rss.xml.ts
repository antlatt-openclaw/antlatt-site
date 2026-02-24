import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const builds = await getCollection('builds');
  const site = (context.site?.toString() ?? 'https://antlatt.com').replace(/\/$/, '');
  
  // Sort by date descending
  const sortedBuilds = builds.sort((a, b) => 
    b.data.date.valueOf() - a.data.date.valueOf()
  );

  return rss({
    title: 'ANTLATT.COM',
    description: 'Tech stuff, general geekery, and whatever else catches my attention. Homelab builds, NAS setups, and more.',
    site: site,
    items: sortedBuilds.map((build) => ({
      title: build.data.title,
      pubDate: build.data.date,
      description: build.data.description,
      link: `/builds/${build.slug}/`,
      categories: build.data.tags,
    })),
    customData: `<language>en-us</language>
<lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
<atom:link href="${site}/rss.xml" rel="self" type="application/rss+xml"/>`,
    xmlns: {
      atom: 'http://www.w3.org/2005/Atom'
    }
  });
}