import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function getStaticPaths() {
  const builds = await getCollection('builds');
  const allTags = [...new Set(builds.flatMap(b => b.data.tags || []))];
  
  return allTags.map(tag => ({
    params: { tag: tag.toLowerCase().replace(/\s+/g, '-') },
    props: { tag },
  }));
}

export async function GET(context: APIContext) {
  const tag = context.props.tag as string;
  const builds = await getCollection('builds');
  
  const tagBuilds = builds
    .filter(b => b.data.tags?.includes(tag))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  return rss({
    title: `ANTLATT.COM - ${tag}`,
    description: `Builds and projects tagged with "${tag}"`,
    site: context.site ?? 'https://antlatt.com',
    items: tagBuilds.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      description: post.data.description,
      link: `/builds/${post.slug}/`,
    })),
    customData: `<language>en-us</language>
<category>${tag}</category>`,
  });
}