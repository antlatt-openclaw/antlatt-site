# ANTLATT.COM

Personal website and blog featuring homelab builds, tech projects, and general geekery.

Built with [Astro](https://astro.build) and deployed on [Vercel](https://vercel.com).

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
/
├── public/
│   ├── images/          # Static images (builds, hero, etc.)
│   ├── videos/          # Video files (if any)
│   └── favicon.svg
├── src/
│   ├── components/      # Reusable Astro components
│   ├── content/         # MDX content (builds, blog posts)
│   ├── layouts/         # Page layouts
│   ├── pages/           # Route pages
│   └── styles/          # Global CSS
├── astro.config.mjs     # Astro configuration
└── package.json
```

## 📝 Content Management

Build posts are written in MDX format in `src/content/builds/`. Each post includes frontmatter with metadata:

```yaml
---
title: 'Your Build Title'
description: 'A brief description'
date: 2024-03-15
image: '/images/builds/your-build/thumbnail.webp'
tags: ['Tag1', 'Tag2']
featured: true
---
```

### Images

- Store images in `public/images/`
- Use WebP format for better compression
- Recommended max width: 1920px for hero images
- Thumbnails should be ~1200px or smaller

### Videos

Place videos in `public/videos/` and embed using the `VideoEmbed` component:

```astro
<VideoEmbed 
  src="/videos/your-video.mp4"
  title="Video Title"
  description="Optional description"
/>
```

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant vector DB URL | `http://localhost:6333` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `OLLAMA_URL` | Ollama LLM endpoint | `http://localhost:11434` |

## 🚢 Deployment

The site is configured for Vercel deployment. Push to main branch to deploy automatically.

### Manual Deployment

```bash
npm run build
# Deploy the ./dist folder to your hosting provider
```

## 🔧 Tech Stack

- **Framework:** [Astro](https://astro.build) v5.x
- **Styling:** Tailwind CSS
- **Content:** MDX
- **Deployment:** Vercel
- **Analytics:** Umami (self-hosted, optional)

## 📦 Key Features

- Responsive design
- Dark theme optimized
- RSS feed at `/rss.xml`
- Search functionality
- Newsletter integration (Buttondown)
- Contact form (Formspree)
- SEO optimized with Open Graph tags

## 🔗 Links

- **Live Site:** [antlatt.com](https://antlatt.com)
- **YouTube:** [youtube.com/@antlatt](https://youtube.com/@antlatt)
- **GitHub:** [github.com/antlatt-openclaw](https://github.com/antlatt-openclaw)

---

Built by [Anthony Lattanzio](mailto:antlatt@gmail.com)