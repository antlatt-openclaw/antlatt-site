---
name: article-pipeline
description: Multi-agent article creation workflow. Use when creating new blog articles or content for antlatt.com. Triggers on "write article", "new article", "create content", "blog post". Coordinates Sarah (research), Caitlin (writing), and Renee (images) with staged review before deployment.
---

# Article Pipeline

Multi-agent workflow for creating polished blog articles with research, writing, and custom images.

## Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   Sarah     │ --> │   Caitlin   │ --> │   Renee     │ --> │  Vercel  │ --> │  Review  │ --> │  Local   │
│  (Research) │     │   (Write)   │     │  (Images)   │     │ (Auto)   │     │ (User)   │     │ (Approve)│
└─────────────┘     └─────────────┘     └─────────────┘     └──────────┘     └──────────┘     └──────────┘
```

**Key Change:** Articles auto-deploy to Vercel for live review, then require approval for local deployment.

## Agents & Roles

| Agent | Role | Model |
|-------|------|-------|
| **sarah** | Research - gather facts, web search, memory recall | glm-5:cloud |
| **caitlin** | Writing - draft article from research | glm-5:cloud |
| **renee** | Images - generate relevant visuals | glm-5:cloud + ComfyUI |
| **beatrice** | Deploy - implement on website | qwen3-coder-next:cloud |

## Process

### 1. Research (Sarah)

Spawn Sarah to gather information:

```
sessions_spawn(agentId="sarah", task="Research [TOPIC]...")
```

Sarah should:
- Use `memory_search` to find relevant context from MEMORY.md and past conversations
- Use `web_search` for current information and facts
- Compile sources, key points, and relevant context
- Save research to `drafts/[article-slug]/research.md`

### 2. Writing (Caitlin)

Spawn Caitlin to write the article:

```
sessions_spawn(agentId="caitlin", task="Write article about [TOPIC] based on research...")
```

Caitlin should:
- Read Sarah's research from `drafts/[article-slug]/research.md`
- Write engaging, technical-but-accessible content
- Use proper Astro/MDX frontmatter
- Include callout boxes, code blocks, and structure
- Save draft to `drafts/[article-slug]/article.mdx`
- **DO NOT** deploy to blog yet

### 3. Images (Renee)

Spawn Renee to generate visuals:

```
sessions_spawn(agentId="renee", task="Generate images for [TOPIC] article...")
```

Renee should:
- Read the article draft
- Identify appropriate image placements
- Generate hero image (1920x1080) and supporting images
- Match site aesthetic (dark theme, indigo #6366f1, cyan #22d3ee)
- Save to `public/images/blog/[slug]/`
- Update article draft with image references
- **DO NOT** deploy yet

### 4. Auto-Deploy to Vercel (Automatic)

After images are generated, **automatically deploy to Vercel** for live review:

```bash
# Copy article to blog folder
cp drafts/[slug]/article.mdx src/content/blog/[slug].mdx

# Build
npm run build

# Deploy to Vercel
cd /root/.openclaw/antlatt-workspace/website-redesign/antlatt-site
npx vercel --prod --yes
```

**Vercel Deployment Notes:**
- `.vercelignore` excludes `public/videos/` (12GB, exceeds Vercel's 100MB file limit)
- Videos are only served from local Docker container, not Vercel
- Project ID and Org ID are stored in `.vercel/project.json`
- If deployment fails, check `.vercelignore` includes large files

Get the live preview URL: `https://antlatt-site.vercel.app/blog/[slug]/`

### 5. Review (User)

Notify user with the live Vercel URL:

```
message(action="send", channel="telegram", to="8570577057", message="📝 Article ready for approval: [TITLE]\n\n📦 Live Preview: https://antlatt-site.vercel.app/blog/[slug]/\n\nReply 'approve' to deploy to antlatt.com\nReply 'deny' to remove from publication")
```

User response handling:
- "approve" / "approved" / "looks good" / "deploy it" → deploy to local
- "deny" / "reject" → remove from blog/ but keep draft in drafts/

### 6. Deploy to Local (After Approval Only)

After approval, deploy to local webserver:

```bash
# Article is already in src/content/blog/ from Vercel deploy
# Just rebuild local
npm run build
docker exec antlatt-site nginx -s reload
```

Confirm live URL: `https://antlatt.com/blog/[slug]/`

## Directory Structure

```
website-redesign/antlatt-site/
├── drafts/                          # Staged articles (not deployed)
│   └── [article-slug]/
│       ├── research.md              # Sarah's research notes
│       ├── article.mdx              # Caitlin's draft
│       └── images/                  # Renee's generated images (copy to public/)
├── src/content/blog/
│   └── [article-slug].mdx           # Published articles
└── public/images/blog/[slug]/       # Published images
```

## Article Frontmatter

```yaml
---
title: "Article Title"
description: "SEO-friendly description"
date: 2026-02-25
tags: ["tag1", "tag2"]
image: "/images/blog/[slug]/hero.webp"
---
```

Note: Use `date` (not `pubDate`) for the date field.

## Site Context

- **Framework**: Astro + Tailwind CSS v4
- **Build**: `npm run build`
- **Deploy**: `docker exec antlatt-site nginx -s reload`
- **URL**: https://antlatt.com
- **Design**: Dark theme, indigo (#6366f1) and cyan (#22d3ee) accents

## ComfyUI (Renee)

- **Endpoint**: 192.168.1.142:8188
- **Script**: `skills/comfyui/scripts/generate_image.py`
- **Models**: SDXL photorealistic, anime, Flux

## Pre-Check: Existing Article Detection

**CRITICAL: Before starting any article, check for existing content.**

```bash
# Check both blog/ and builds/ folders
ls src/content/blog/ | grep -i [slug-keywords]
ls src/content/builds/ | grep -i [slug-keywords]
```

If an article exists:
- **Skip the topic entirely** - do NOT create a duplicate
- Log the conflict: "Skipping [topic] - already exists at blog/[slug].mdx"
- Move to the next topic in the queue

This prevents wasted agent cycles on duplicate content.

## Quick Start

To create a new article:

```
User: "Write an article about [TOPIC]"

1. **Check for existing article** ← NEW STEP
   - If exists: skip topic, notify user
2. Create draft directory: drafts/[slug]/
3. Spawn Sarah for research
4. On completion, spawn Caitlin to write
5. On completion, spawn Renee for images
6. Auto-deploy to Vercel (no approval needed)
7. Notify user with live Vercel URL
8. On "approve" → deploy to antlatt.com
9. On "deny" → remove from blog/, keep draft
```

## Daily Cron (2 Articles)

The 2am cron job produces **two articles per night**:

1. **Check for existing articles first** - skip any topic that already has content
2. Find 2 distinct topics (that don't already exist!)
3. Execute full pipeline for article 1 → Vercel
4. Execute full pipeline for article 2 → Vercel
5. Notify with both Vercel URLs
6. User replies "approve 1" or "approve 2" individually
7. Each approval deploys that specific article to local

## Approval Words

The following words/phrases indicate approval:
- "approve" / "approved"
- "looks good" / "looks great"
- "deploy it" / "deploy"
- "ship it"
- "yes, deploy"

Any other response is treated as feedback to incorporate.