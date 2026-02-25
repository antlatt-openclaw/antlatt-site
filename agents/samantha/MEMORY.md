# MEMORY.md - Long-Term Memory

## Primary Model

**ollama/qwen3-coder-next:cloud** - Use this for all coding tasks.

## Projects

| Project | Path | Description |
|---------|------|-------------|
| antlatt-site | `/root/.openclaw/antlatt-workspace/website-redesign/antlatt-site/` | Astro website |
| OpenClaw workspace | `/root/.openclaw/antlatt-workspace/` | Main workspace |

## Infrastructure

| Service | Address | Notes |
|---------|---------|-------|
| Redis | 192.168.1.206:6379 | Memory buffer |
| Qdrant | 192.168.1.202:6333 | Vector DB |
| Ollama | 192.168.1.207:11434 | LLM inference |
| ComfyUI | 192.168.1.142:8188 | Image generation |
| Kokoro TTS | 192.168.1.204:8880 | Text-to-speech |

## Coding Conventions

- Commit changes after completing tasks
- Test builds before deployment
- Use `docker exec antlatt-site nginx -s reload` after site changes
- Never expose internal IPs (192.168.x.x) on public pages

---

Update this file with important learnings about Anthony's codebase and preferences.
