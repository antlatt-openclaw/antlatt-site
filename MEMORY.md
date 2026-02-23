# MEMORY.md - Long-Term Memory

## User Preferences

- **Voice Response Rule**: When Anthony sends a voice message, respond with voice unless he explicitly requests text response.
- **Default TTS Voice**: `af_nova` (warm, natural female voice via Kokoro TTS)

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