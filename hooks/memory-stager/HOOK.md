---
name: memory-stager
description: "Stage conversation turns to Redis for memory curation"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "events": ["message:received", "message:sent", "llm:output"],
        "requires": { "env": ["REDIS_HOST"] },
      },
  }
---

# Memory Stager Hook

Automatically stages conversation turns to Redis when messages are sent or received.

## What It Does

1. **On message:received** - Stages the user's message with a pending flag
2. **On message:sent** - Stages the AI response and updates the turn

## Output

Turns are stored in Redis under `mem:{user_id}` as JSON objects:

```json
{
  "timestamp": "2026-02-24T08:45:00",
  "user_message": "What's the weather?",
  "ai_response": "It's sunny today!",
  "session_id": "agent:main:main",
  "channel": "telegram"
}
```

## Configuration

Set environment variables in your `.env` or `memory_env`:

- `REDIS_HOST` - Redis server host (default: 192.168.1.206)
- `REDIS_PORT` - Redis server port (default: 6379)

## Requirements

- Redis server accessible from Gateway
- Python 3.x with `redis` package installed

## Disabling

```bash
openclaw hooks disable memory-stager
```