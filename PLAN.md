# Website Redesign Plan — antlatt.com

## Overview

**Goal:** Complete redesign — modern stack, new copy, dark tech aesthetic

**Stack:** Astro (content-focused, MDX, lightning fast, Vercel-ready)

**Design:** Dark tech portfolio/magazine hybrid — clean grids, code aesthetics, typography-forward

**Timeline:** No rush — quality over speed

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Framework | Astro 5.x | Content collections, MDX, island architecture |
| Styling | Tailwind CSS | Fast, flexible, dark mode built-in |
| Typography | Inter + JetBrains Mono | Clean UI + code aesthetic |
| Hosting | Vercel | Already set up, edge functions if needed |
| Content | MDX + Content Collections | Articles as markdown with components |
| Animations | Motion One | Subtle, performant |

---

## Site Structure

```
/
├── Home                    # Hero + featured builds + latest posts
├── Builds/                 # All project builds
│   ├── nas-build/         # 10G 20TB Plex NAS
│   ├── arcade-build/      # Ultimate Arcade1Up
│   ├── server-rack/       # Unraid Master Build
│   ├── pihole/            # Pi-hole Network Ad Blocker
│   └── network-gear/      # Consolidated: Mikrotik + Nanobeam + US-24
├── DeepFakes/             # Deepfake detection/explanation
├── About/                 # Who is Anthony?
└── Contact/               # Links to social/email
```

**Removed:**
- YouTube Clone (drop)
- cloud.antlatt.com link (inactive)
- jitsi.antlatt.com link (inactive)
- ElevenLabs widget (drop)
- Zack's PC (time-sensitive, outdated)

---

## Design System

### Color Palette (Dark Tech)

```
Background:     #0a0a0f   (near black)
Surface:        #12121a   (cards, panels)
Surface Hover:  #1a1a25
Border:         #2a2a3a
Text Primary:   #e5e5e5
Text Secondary: #8888a0
Accent:         #6366f1   (indigo)
Accent Hover:   #818cf8
Code/Syntax:    #22d3ee   (cyan)
Success:        #22c55e
Warning:        #f59e0b
```

### Typography

```
Headings:      Inter (600-800 weight)
Body:          Inter (400 weight)
Code:          JetBrains Mono
Article Body:  18px / 1.7 line-height
```

### Components

- **Card** — Image + title + excerpt + tags + date
- **Hero** — Full-width gradient + headline + CTA
- **Article** — MDX with custom components (code blocks, callouts, image galleries)
- **Navigation** — Sticky header, minimal
- **Footer** — Socials, copyright, minimal

---

## Content Pipeline

### Articles to Rewrite

| Article | Priority | Notes |
|---------|----------|-------|
| NAS Build | High | Flagship content, add updates |
| Arcade Build | High | Great visuals, modernize copy |
| Server Rack | High | Core infrastructure piece |
| Pi-hole | Medium | Still relevant, condense |
| Network Gear | Medium | Consolidate 3 into 1 guide |
| DeepFakes | Medium | Recent, review/expand |

### New Content Ideas

- **About page** — Who is Anthony? Background, skills, philosophy
- **Homelab overview** — Current setup (ties into True-Recall, Qdrant, Redis, etc.)
- **OpenClaw integration** — Your AI assistant project
- **Self-hosting philosophy** — Why you run your own infrastructure

---

## Milestones

### Milestone 1: Foundation
- [ ] Initialize Astro project in `website-redesign/`
- [ ] Set up Tailwind + dark theme
- [ ] Create base layouts (home, article, page)
- [ ] Build core components (Card, Hero, Nav, Footer)
- [ ] Set up content collections for builds

### Milestone 2: Content Migration
- [ ] Create MDX files for each article
- [ ] Copy over images (organized by article)
- [ ] Write new copy for NAS Build
- [ ] Write new copy for Arcade Build
- [ ] Write new copy for Server Rack

### Milestone 3: Polish & Features
- [ ] Add code syntax highlighting
- [ ] Add image galleries/lightbox
- [ ] Add table of contents for long articles
- [ ] Responsive design (mobile-first)
- [ ] SEO optimization (meta, sitemap, RSS)

### Milestone 4: Launch
- [ ] Build About page
- [ ] Build Contact page
- [ ] Final design review
- [ ] Deploy to Vercel
- [ ] Point antlatt.com domain
- [ ] Archive old site

---

## File Structure

```
website-redesign/
├── src/
│   ├── components/
│   │   ├── Card.astro
│   │   ├── Hero.astro
│   │   ├── Navigation.astro
│   │   ├── Footer.astro
│   │   ├── CodeBlock.astro
│   │   └── ImageGallery.astro
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   └── ArticleLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── about.astro
│   │   ├── contact.astro
│   │   └── builds/
│   │       └── [...slug].astro
│   ├── content/
│   │   └── builds/
│   │       ├── nas-build.mdx
│   │       ├── arcade-build.mdx
│   │       ├── server-rack.mdx
│   │       ├── pihole.mdx
│   │       └── network-gear.mdx
│   └── styles/
│       └── global.css
├── public/
│   └── images/
│       └── builds/
│           ├── nas/
│           ├── arcade/
│           └── ...
├── astro.config.mjs
├── tailwind.config.mjs
└── package.json
```

---

## Next Steps

1. **Initialize Astro project** — `npm create astro@latest`
2. **Tailwind setup** — Dark theme configuration
3. **Build first component** — Card component as proof of concept
4. **Migrate first article** — NAS Build with new copy
5. **Iterate** — One article at a time, polish design

---

*Created: 2026-02-23*
*Status: Planning complete, ready for implementation*