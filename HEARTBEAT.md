# HEARTBEAT.md

## True-Recall Status

The memory curation system runs automatically at 2:30 AM via cron:
- Reads conversation turns from Redis `mem:antlatt`
- Curates gems using qwen3:8b
- Stores to Qdrant `true_recall` collection
- Clears Redis buffer

## Response

- If there's something to report: respond with the alert
- If nothing needs attention: respond with ONLY "HEARTBEAT_OK"

---

**Note:** Turn staging to Redis currently requires manual calling or a hook mechanism.
The `memory-qdrant` plugin handles retrieval (`autoRecall: true`).