# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## TTS (Kokoro)

- **Endpoint:** http://192.168.1.204:8880
- **Default voice:** `af_nova` (warm female voice)
- **Voices available:** 70+ voices across languages
- **API:** OpenAI-compatible (`/v1/audio/speech`)

### Voice Picks by Vibe

| Vibe | Voice | Notes |
|------|-------|-------|
| Warm default | `af_nova` | Friendly, natural |
| American male | `am_michael` | Deep, professional |
| British female | `bf_emma` | British accent |
| American female | `af_bella` | Younger, energetic |
| Calm female | `af_heart` | Softer, gentle |

### Other Infrastructure

| Service | Address |
|---------|---------|
| Redis | 192.168.1.206:6379 |
| Qdrant | 192.168.1.202:6333 |
| SearXNG | localhost:8888 |
| Kokoro TTS | 192.168.1.204:8880 |
| Ollama (embeddings) | 192.168.1.207:11434 |

## Skills

| Skill | Path | Description |
|-------|------|-------------|
| Knowledge Base | `skills/knowledge-base/` | RAG ingestion & retrieval |
| Humanize | `skills/humanize/` | AI content humanization |
| Messaging | `skills/messaging/` | Telegram topic routing |
| Memory (Redis) | `skills/mem-redis/` | Conversation memory buffer |
| Whisper | `skills/whisper/` | Groq transcription |
| TTS | `skills/tts/` | Kokoro voice synthesis |

---

Add whatever helps you do your job. This is your cheat sheet.