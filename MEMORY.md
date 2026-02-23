# MEMORY.md - Long-Term Memory

## User Preferences

- **Voice Response Rule**: When Anthony sends a voice message, respond with voice unless he explicitly requests text response.
- **Default TTS Voice**: `af_nova` (warm, natural female voice via Kokoro TTS)

## Telegram Settings

- **Streaming disabled**: Set `streaming: false` in `.channels.telegram` - `streaming: true` caused double messages (incremental updates appeared as separate Telegram messages)

## Communication

- **Primary Contact**: Anthony Lattanzio
- **Telegram**: 8570577057
- **Email**: antlatt@gmail.com, antlatt.openclaw@gmail.com
- **Timezone**: America/New_York (EST)

## Infrastructure

| Service | Address | Notes |
|---------|---------|-------|
| Redis | 192.168.1.206:6379 | Memory buffer |
| Qdrant | 192.168.1.202:6333 | Vector DB |
| Kokoro TTS | 192.168.1.204:8880 | Text-to-speech |
| Ollama (embeddings) | 192.168.1.207:11434 | Embeddings + qwen3:8b |
| SearXNG | localhost:8888 | Local search |

## Telegram Topics

Group ID: `-1003850499454`

| Topic | Thread ID |
|-------|-----------|
| daily-brief | 2 |
| crm | 4 |
| email | 7 |
| knowledge-base | 9 |
| video-ideas | 11 |
| earnings | 13 |
| cron-updates | 15 |
| financials | 17 |
| health | 19 |
| meta-analysis | 21 |
| security | 23 |
| social | 25 |
| general | 27 |
| website-rebuild | 80 |

## Accounts

- **GitHub**: antlatt-openclaw
- **Vercel**: antlattopenclaw-6650
- **Google**: antlatt.openclaw@gmail.com

## Agents

| Agent | Purpose |
|-------|---------|
| main | General assistant (this agent) |
| hallie | Coding specialist, background execution, spawns subagents |

---

*Update this file with significant learnings and preferences over time.*
## Knowledge Base (RAG)

- **Collections**: `kb_sources`, `kb_chunks`
- **Embeddings**: Gemini embedding-001 (768-dim)
- **Usage**: `python3 skills/knowledge-base/scripts/retrieve.py "query"`

## True-Recall Memory System

### Architecture
- **Capture**: Turns → Redis `mem:antlatt` (manual/hook staging)
- **Curation**: 2:30 AM cron (`qwen3:8b` extracts gems)
- **Storage**: Qdrant `true_recall` collection (1024-dim, `mxbai-embed-large`)
- **Retrieval**: On-demand search via `.projects/true-recall/tr-out/scripts/search_memories.py`

### Cron Schedule
| Time | Job |
|------|-----|
| 2:30 AM | True-Recall curator (processes Redis → Qdrant) |
| 3:00 AM | jarvis-memory backup |
| 3:30 AM | File archive |

### Key Files
- **Curator**: `.projects/true-recall/tr-process/curate_memories.py`
- **Search**: `.projects/true-recall/tr-out/scripts/search_memories.py`
- **Config**: `.projects/true-recall/.env`
- **Prompt**: `.projects/true-recall/curator_prompt.md`

### Usage
```bash
# Search memories
python3 .projects/true-recall/tr-out/scripts/search_memories.py "your query"

# Run curator manually
python3 .projects/true-recall/tr-process/curate_memories.py --user-id antlatt
```

