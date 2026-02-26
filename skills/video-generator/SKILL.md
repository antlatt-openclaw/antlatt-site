---
name: video-generator
description: AI video production workflow using Remotion. Use when creating videos, short films, commercials, or motion graphics. Triggers on requests to make promotional videos, product demos, social media videos, animated explainers, or any programmatic video content. Produces polished motion graphics, not slideshows.
---

# Video Generator (Remotion)

Create professional motion graphics videos programmatically with React and Remotion.

## Implementation Steps

1. **Prerequisites check** — Verify Chrome dependencies installed, check for Firecrawl API key
2. **Brand data** — Scrape with Firecrawl OR fallback to reading source CSS/files
3. **Director's treatment** — Write vibe, camera style, emotional arc
4. **Visual direction** — Colors, fonts, brand feel, animation style
5. **Scene breakdown** — List every scene with description, duration, text, transitions
6. **Scaffold project** — `npx create-video@latest --blank --tailwind --no-skills my-video`
7. **Build scenes** — Each scene self-contained with own animation timing
8. **Test locally first** — Render a single frame to catch errors early
9. **Start studio for preview** — `npx remotion studio --host 0.0.0.0`
10. **Share preview URL** — Local network IP or tunnel if needed
11. **Iterate** — Edit source, re-render or refresh studio
12. **Final render** — Export to MP4 with H.264 codec
13. **Deploy** — Copy to web-accessible location

## Prerequisites

**System dependencies for Chrome headless (Linux):**
```bash
apt-get install -y libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
```

**Required environment variables:**
- `FIRECRAWL_API_KEY` — For brand scraping (optional, see alternatives below)

## Quick Start

```bash
# Scaffold project (may need interactive input)
npx --yes create-video@latest --blank --tailwind --no-skills my-video
cd my-video && npm install

# Add motion libraries
npm install lucide-react

# Fix scripts in package.json (replace any "bun" references with "npx remotion")

# Start dev server (bind to all interfaces for network access)
npx remotion studio --host 0.0.0.0

# For local network only, access directly at:
# http://YOUR_LOCAL_IP:3000
```

## Brand Data Without Firecrawl

If `FIRECRAWL_API_KEY` is not set or Firecrawl fails:

1. **Read site source code directly** — Check CSS for brand colors, fonts
2. **Use browser snapshot** — If browser tool is available, snapshot the site
3. **Fetch with web_fetch** — Get page content and extract key elements
4. **Check existing project files** — Read global.css, tailwind.config, layouts

Example fallback:
```bash
# Get brand colors from CSS
cat /path/to/project/src/styles/global.css | grep -E "color|font"
```

## Rendering

```bash
cd my-video
npx remotion render MyVideo out/video.mp4 --codec h264
```

**After rendering, copy to web-accessible location:**
```bash
# Check where your web server serves static files
cp out/video.mp4 /path/to/webserver/videos/video.mp4
```

## Common Remotion Gotchas

### Hook Usage
```tsx
// WRONG - useCurrentFrame returns frame number, not fps
const { fps } = useCurrentFrame();

// CORRECT - use useVideoConfig for fps
const frame = useCurrentFrame();
const { fps } = useVideoConfig();
```

### Scene Components Pattern
Keep scene components simple and self-contained. Each scene should handle its own animation timing:

```tsx
// Simple pattern - each scene starts animation from frame 0
const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const progress = spring({ frame, fps, damping: 20, stiffness: 100 });
  // ...
};

// In main composition, switch scenes by frame number
const SCENE_DURATION = 50;
const sceneIndex = Math.floor(frame / SCENE_DURATION);
```

### Server Networking
For local network access, always use `--host 0.0.0.0`:
```bash
npx remotion studio --host 0.0.0.0
```

## Motion Graphics Principles

### AVOID (Slideshow patterns)

- Fading to black between scenes
- Centered text on solid backgrounds
- Same transition for everything
- Linear/robotic animations
- Static screens
- Emoji icons — NEVER use emoji, always use Lucide React icons

### PURSUE (Motion graphics)

- Overlapping transitions (next starts BEFORE current ends)
- Layered compositions (background/midground/foreground)
- Spring physics for organic motion
- Varied timing (2-5s scenes, mixed rhythms)
- Continuous visual elements across scenes
- Custom transitions with clipPath, 3D transforms, morphs
- Lucide React for ALL icons — never emoji

## Transition Techniques

1. **Morph/Scale** - Element scales up to fill screen, becomes next scene's background
2. **Wipe** - Colored shape sweeps across, revealing next scene
3. **Zoom-through** - Camera pushes into element, emerges into new scene
4. **Clip-path reveal** - Circle/polygon grows from point to reveal
5. **Persistent anchor** - One element stays while surroundings change
6. **Directional flow** - Scene 1 exits right, Scene 2 enters from right
7. **Split/unfold** - Screen divides, panels slide apart
8. **Perspective flip** - Scene rotates on Y-axis in 3D

## Animation Timing Reference

```typescript
const springs = {
  snappy: { stiffness: 400, damping: 30 },
  bouncy: { stiffness: 300, damping: 15 },
  smooth: { stiffness: 120, damping: 25 },
};
```

## Visual Style Guidelines

### Typography
- One display font + one body font max
- Massive headlines, tight tracking
- Keep text SHORT (viewers can't pause)

### Colors
- Use brand colors as primary palette
- Simple, clean backgrounds — single dark tone or subtle gradient

### Layout
- Asymmetric layouts, off-center type
- Generous whitespace as design element

## Quality Tests

- **Mute test**: Story follows visually without sound?
- **Squint test**: Hierarchy visible when squinting?
- **Timing test**: Motion feels natural, not robotic?
- **Slideshow test**: Does NOT look like PowerPoint?

## Tunnel Management

**Note:** Cloudflare quick tunnels can be unreliable. Prefer direct local network access when possible.

```bash
# Start tunnel with cloudflared directly
cloudflared tunnel --url http://localhost:3000

# Better: Direct network access
npx remotion studio --host 0.0.0.0
# Then visit http://YOUR_SERVER_IP:3000
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome headless fails | Install system deps: `libnspr4 libnss3 libatk...` |
| `fps must be a number` | Use `useVideoConfig()` not `useCurrentFrame()` for fps |
| Server not reachable | Add `--host 0.0.0.0` flag |
| Tunnel keeps dropping | Use direct LAN IP instead |
| Video wrong content-type | Place in web server's static folder, not project dist |

## Project Structure

```
my-video/
├── src/
│   ├── Root.tsx           # Composition definitions
│   ├── index.ts           # Entry point
│   ├── MyVideo.tsx        # Main video component
│   └── scenes/            # Scene components (optional)
├── public/
│   └── images/            # Static assets
├── out/                   # Rendered output
├── remotion.config.ts
└── package.json
```