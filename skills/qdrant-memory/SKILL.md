# qdrant-memory - Long-Term Semantic Memory

Persistent vector storage using Qdrant. Enables semantic search across all conversations.

## Architecture

```
Redis Buffer (daily) → Qdrant (permanent)
        ↓
  Daily files (.md) → Archive
```

## Collections

| Collection | Purpose |
|------------|---------|
| `kimi_memories` | Conversation memories |
| `kimi_kb` | Knowledge base entries |
| `private_court_docs` | Sensitive documents (optional) |

## Scripts

| Script | Purpose |
|--------|---------|
| `init_*.py` | Initialize Qdrant collections |
| `q_save.py` | Save to Qdrant with embeddings |
| `search_memories.py` | Semantic search |
| `auto_store.py` | Automatic embedding + store |
| `daily_conversation_backup.py` | Backup daily logs |
| `harvest_sessions.py` | Extract from old sessions |

## Usage

```bash
# Save to Qdrant
python3 skills/qdrant-memory/scripts/q_save.py --user-id antlatt --text "Important thing to remember"

# Search memories
python3 skills/qdrant-memory/scripts/search_memories.py --user-id antlatt --query "what did we discuss about projects?"
```