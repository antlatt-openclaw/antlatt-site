---
name: true-recall-stager
description: "Auto-stage conversations to True-Recall Redis buffer on every response"
homepage: https://docs.openclaw.ai/automation/hooks#true-recall-stager
metadata:
  openclaw:
    emoji: 🧠
    events: ["message:sent"]
    requires: { config: ["workspace.dir"] }
---

# True-Recall Stager Hook

Automatically stages every conversation turn to the True-Recall Redis buffer when a message is sent.

## What It Does

After every AI response is sent to the user:

1. **Captures the exchange** - User message + AI response
2. **Stages to Redis** - Pushes to `tr-out:buffer:{user_id}` list
3. **Sets TTL** - 24 hour expiration on buffer

## Configuration

No configuration needed. The hook automatically:

- Uses Redis at `localhost:6379`
- Buffers to `tr-out:buffer:USER_ID`
- Filters out system metadata and thinking blocks
- Retains data for 24 hours

## Integration

Works with the True-Recall daily curator:

- Hook stages continuously to Redis
- Curator (qwen3) runs daily at 3 AM
- Curator reads 24h buffer, extracts gems, stores to Qdrant
- Buffer cleared after curation

## Requirements

- Redis running at `localhost:6379`
- `redis` Python package installed
- True-Recall scripts in `~/.openclaw/workspace/skills/true-recall-out/scripts/`
