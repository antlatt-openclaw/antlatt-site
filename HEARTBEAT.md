# HEARTBEAT.md

## Memory Buffer (Every Heartbeat)

Save conversation turns to Redis buffer for persistence:

```bash
source /root/.openclaw/antlatt-workspace/.memory_env && python3 /root/.openclaw/antlatt-workspace/skills/mem-redis/scripts/save_mem.py --user-id antlatt
```

## Response

- If there's something to report: respond with the alert
- If nothing needs attention: respond with ONLY "HEARTBEAT_OK" (no quotes, no markdown)