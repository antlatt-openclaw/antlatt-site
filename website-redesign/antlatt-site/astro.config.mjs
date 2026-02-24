// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import mdx from '@astrojs/mdx';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://antlatt.com',
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [mdx(), sitemap()],
  output: 'static',
  build: {
    assets: 'assets'
  },
  image: {
    // Enable responsive images with multiple formats
    service: {
      entrypoint: 'astro/assets/services/sharp',
      config: {
        limitInputPixels: false
      }
    },
    // Define default breakpoints for responsive images
    domains: []
  }
});