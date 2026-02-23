# mem-redis - Redis Buffer Memory Skill

Fast short-term memory buffer using Redis. Accumulates conversation turns and persists across sessions.

## Commands

- `save mem` — Save current conversation to Redis buffer
- `save q` — Flush buffer to Qdrant for semantic search
- `q <topic>` — Semantic search across all memories

## Scripts

| Script | Purpose |
|--------|---------|
| `hb_append.py` | Append single turn to Redis (heartbeat) |
| `save_mem.py` | Save full conversation to Redis |
| `mem_retrieve.py` | Get recent memories from Redis |
| `search_mem.py` | Search Redis buffer |
| `cron_backup.py` | Daily Redis → Qdrant flush |

## Environment

Set in `.memory_env`:
- `REDIS_HOST` — Redis server IP
- `REDIS_PORT` — Redis port (default 6379)
- `USER_ID` — Your user identifier

## Usage

```bash
# Save conversation
python3 skills/mem-redis/scripts/save_mem.py --user-id antlatt

# Retrieve recent
python3 skills/mem-redis/scripts/mem_retrieve.py --user-id antlatt --limit 10
```