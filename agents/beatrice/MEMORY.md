# MEMORY.md - Long-Term Memory

## Primary Model

**ollama/qwen3-coder-next:cloud** - Use this for all website tasks.

## Project Location

```
/root/.openclaw/antlatt-workspace/website-redesign/antlatt-site/
```

## Key Commands

```bash
# Build site
cd /root/.openclaw/antlatt-workspace/website-redesign/antlatt-site
npm run build

# Reload nginx
docker exec antlatt-site nginx -s reload

# View logs
docker logs antlatt-site
```

## Component Structure

| Path | Purpose |
|------|---------|
| `src/layouts/` | Page layouts (BaseLayout, ArticleLayout) |
| `src/components/` | Reusable components |
| `src/pages/` | Route pages |
| `src/content/builds/` | Build article MDX files |
| `src/styles/global.css` | Global styles |
| `public/images/` | Static images |

## Security Rules

- **NEVER** expose internal IP addresses (192.168.x.x) on public pages
- Use environment variables for internal service URLs
- The lab page uses env vars: `QDRANT_URL`, `REDIS_URL`, `OLLAMA_URL`

## Deploy Process

1. Build: `npm run build`
2. Nginx reload: `docker exec antlatt-site nginx -s reload`
3. Test: `curl http://localhost:8080/`

The dist folder is bind-mounted, so builds are immediately live.

---

Update this file with important learnings about Anthony's website.
