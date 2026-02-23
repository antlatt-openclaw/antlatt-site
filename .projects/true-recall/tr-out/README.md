# tr-out: Retrieval & Injection

**Purpose:** Retrieve contextual gems from Qdrant and provide to AI for enhanced responses.

---

## Components

### 1. Retrieval (`retrieval/search_memories.py`)

**Function:** Semantic search on curated gems in Qdrant

**Input:** User query (e.g., "What did I decide about the database?")

**Process:**
```
User query → Embedding (snowflake-arctic-embed2)
                ↓
         Semantic search in Qdrant
                ↓
         Find matching gems
                ↓
         Return gem + context + snippet
```

**Output:**
```json
{
  "gem": "User decided on Redis for caching layer",
  "context": "After evaluating tradeoffs between speed and persistence",
  "snippet": "[rob]: Redis or Postgres?\n[Kimi]: Redis for caching\n[rob]: I decided on Redis",
  "categories": ["decision", "technical"],
  "importance": "high",
  "score": 0.94,
  "timestamp": "2026-02-22T14:30:00",
  "date": "2026-02-22",
  "conversation_id": "uuid-here",
  "turn_range": "15-17"
}
```

**Temporal Fields from The Curator:**

| Field | Purpose | Example |
|-------|---------|---------|
| **timestamp** | Precise moment | 2026-02-22T14:30:00 |
| **date** | Day for grouping | 2026-02-22 |
| **conversation_id** | Full conversation | uuid |
| **turn_range** | Which turns | 15-17 |

**Usage:**
```bash
python3 retrieval/search_memories.py "database decision" --user-id USER_ID
```

**Temporal Retrieval Options:**
```bash
# Boost recent results
python3 retrieval/search_memories.py "database" --recency-boost

# Filter by date range
python3 retrieval/search_memories.py "decision" --after 2026-01-01 --before 2026-03-01

# Find versions of a preference
python3 retrieval/search_memories.py "database preference" --show-versions
```

---

### 2. Injection (Future)

**Purpose:** Automatically inject relevant context into AI responses

**Concept:**
```
User: "What should I use for caching?"
System: [searches Qdrant, finds Redis decision]
AI: "Based on your previous decision to use Redis for caching
     after evaluating tradeoffs, I'd recommend sticking with
     that choice for consistency..."
```

**Implementation Options:**

**Option A: OpenClaw Context Hook**
- Hook on `message:received`
- Search Qdrant for relevant context
- Inject into conversation context
- AI sees it naturally

**Option B: Pre-prompt Injection**
- Before each response generation
- Search Qdrant for relevant gems
- Add to system prompt
- AI responds with context

**Option C: On-demand Retrieval**
- Don't auto-inject
- User says "remember when..." or "what did I decide..."
- System searches and provides context
- User controls when to retrieve

**Current Status:** Not implemented. Retrieval works manually, auto-injection is future work.

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         tr-out                                │
│                  (Retrieval & Injection)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER QUERY                                                   │
│     │                                                        │
│     ▼                                                        │
│  ┌─────────────────────┐                                    │
│  │  search_memories.py │                                    │
│  │  (retrieval/)       │                                    │
│  │                     │                                    │
│  │  1. Embed query     │                                    │
│  │  2. Search Qdrant   │                                    │
│  │  3. Find gems       │                                    │
│  │  4. Return context  │                                    │
│  └─────────────────────┘                                    │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────┐                                    │
│  │  Gem with Context   │                                    │
│  │                     │                                    │
│  │  - gem: insight     │                                    │
│  │  - context: why     │                                    │
│  │  - snippet: source  │                                    │
│  └─────────────────────┘                                    │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────┐                                    │
│  │  [FUTURE] Injection │                                    │
│  │                     │                                    │
│  │  Auto-inject into   │                                    │
│  │  AI context or      │                                    │
│  │  provide on-demand  │                                    │
│  └─────────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage

### Manual Search

```bash
python3 tr-out/retrieval/search_memories.py "database decision" --user-id USER_ID
```

### Future Auto-Injection

```
User: "What should I use for caching?"
System: [searches Qdrant, finds Redis decision]
AI: "Based on your previous decision to use Redis for caching
     after evaluating tradeoffs, I'd recommend..."
```

---

## Qdrant Storage

Based on recent searches, tr-out can retrieve 5 True-Recall related memories from today's development session (2026-02-22):

| Memory | Importance | Available for Retrieval |
|--------|------------|------------------------|
| Mattermost vs Discord decision | MEDIUM | ✅ Yes |
| Redis buffer implementation | MEDIUM | ✅ Yes |
| True-Recall architecture | MEDIUM | ✅ Yes |
| System automation setup | MEDIUM | ✅ Yes |
| Curator prompt development | MEDIUM | ✅ Yes |

These memories are stored in Qdrant and available for semantic search via `retrieval/search_memories.py`.

## Temporal Retrieval

**The Curator** includes precise timestamps in every gem. tr-out uses these for intelligent retrieval:

### Timestamp Fields in Gems

| Field | Purpose | Example |
|-------|---------|---------|
| **timestamp** | Precise moment | 2026-02-22T14:30:00 |
| **date** | Day for grouping | 2026-02-22 |
| **conversation_id** | Full conversation | uuid |
| **turn_range** | Which turns | 15-17 |

### Temporal Retrieval Strategies

**1. Recency Weighting**
```python
# Boost recent results
score = semantic_similarity * recency_factor
recency_factor = 1.0 / (1 + days_ago/30)  # 30-day half-life
```

**2. Temporal Filtering**
```python
# Only search recent memories
search_memories(
    query="database decision",
    after="2026-01-01",      # Only 2026+
    before="2026-03-01"      # Before March
)
```

**3. Version Tracking**
```python
# Find when preferences changed
find_versions("database preference")
# Returns:
# - 2025-11-15: "User preferred Postgres"
# - 2026-02-22: "User switched to Redis"
```

**4. Temporal Decay**
```python
# Older gems fade unless reinforced
relevance = base_score * exp(-age_in_days / decay_constant)
# decay_constant = 90 days (3 month half-life)
```

### Why Temporal Matters

| Scenario | Without Timestamp | With Timestamp |
|----------|-------------------|----------------|
| "What did I decide?" | "You chose Redis" | "You chose Redis on Feb 22 (3 days ago)" |
| Preference change | "You prefer X" | "You preferred X until March, then switched to Y" |
| Outdated info | "Use this tool" | "This was recommended in 2025, may be outdated" |
| Recency bias | All results equal | Recent decisions weighted higher |

**Current Status:** Timestamps included in gems. Temporal retrieval strategies ⏳ Future enhancement.

## Relationship to Other Systems

### True-Recall is One Unified System

**tr-out is ONE HALF of True-Recall. tr-in is the OTHER HALF.**

They are not separate systems — they are the output and input sides of the same unified memory pipeline.

```
┌────────────────────────────────────────────────────────────────┐
│                      True-Recall                               │
│              (Unified Memory System)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│   │   tr-in  │ ───→ │ tr-process│ ───→ │  tr-out  │          │
│   │  INPUT   │      │  CURATE   │      │  OUTPUT  │          │
│   └──────────┘      └──────────┘      └──────────┘          │
│        │                  │                  │                 │
│        ▼                  ▼                  ▼                 │
│   Redis Buffer      The Curator         Qdrant               │
│   (24h hold)        (qwen3 LLM)         (true_recall)         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

- **tr-in**: Input side — receives raw conversation, filters noise, stages to Redis
- **tr-process**: The bridge — The Curator runs daily, extracts gems, stores to Qdrant
- **tr-out** (this folder): Output side — retrieves curated gems for AI context

### Key Differences from tr-in

| Aspect | tr-in | tr-out |
|--------|-------|--------|
| **Direction** | Ingestion | Retrieval |
| **Trigger** | Every message | On query |
| **Input** | Raw conversation | User question |
| **Process** | Filter → Stage → The Curator | Embed → Search → Return |
| **Output** | Curated gems | Contextual answer |
| **Storage** | Redis → Qdrant | Qdrant (read-only) |

### Predecessor: memory-qdrant Plugin (Replaced)

**The memory-qdrant plugin was a SEPARATE earlier attempt, NOT part of True-Recall.**

| Aspect | memory-qdrant Plugin | True-Recall (Unified) |
|--------|---------------------|----------------------|
| **Language** | TypeScript | Python |
| **Architecture** | Single plugin | Three-part pipeline (tr-in/process/out) |
| **Curation** | ❌ None (raw search) | ✅ LLM (The Curator) |
| **Timing** | Real-time | 24h delayed |
| **Collection** | `kimi_memories` | `true_recall` |
| **Injection** | Was automatic (now off) | Manual only (auto TBD) |
| **Status** | ❌ Disabled (Feb 21) | ✅ Active |

**History:**
- Feb 21: Built `memory-qdrant` TypeScript plugin — did dumb semantic search only
- Feb 21 21:36: Disabled `autoRecall` due to noise and lack of context awareness
- Feb 22: Built True-Recall as replacement — unified Python system with LLM curation

**Current:**
- `kimi_memories` — Legacy, 11,238 items, frozen (from disabled plugin)
- `true_recall` — Active, 4 gems, curated (this system)

### True-Recall is Separate from jarvis-memory

**True-Recall and jarvis-memory are TWO SEPARATE PROJECTS.**

| Project | Purpose | Location |
|---------|---------|----------|
| **jarvis-memory** | Python skill for OpenClaw with manual memory tools | `skills/jarvis-memory/` |
| **True-Recall** | Standalone Python system with automatic curation | `.projects/true-recall/` |

**Key differences:**
- jarvis-memory: Manual "save q", manual "q <topic>" — user controls everything
- True-Recall: Automatic staging → 24h curation → gem extraction — system handles everything

**No dependency:**
- True-Recall does NOT depend on jarvis-memory
- True-Recall does NOT extend jarvis-memory
- They are parallel memory systems with different approaches

---

## Scripts

### `search_memories.py` — Retrieval Script

**Location:** `tr-out/scripts/search_memories.py`

**Purpose:** Search for curated gems in the `true_recall` Qdrant collection

**Process:**
1. Embeds user query using mxbai-embed-large
2. Searches Qdrant for similar gems
3. Returns matching gems with context and metadata

**Usage:**
```bash
# Basic search
python3 search_memories.py "database decision" --user-id USER_ID

# With options
python3 search_memories.py \
  --user-id USER_ID \
  --limit 5 \
  --min-score 0.6 \
  "What did I decide about Redis?"
```

**Output format:**
```
💎 User decided to use Redis over Postgres for memory system caching

📋 Context: After discussing tradeoffs between persistence vs speed...

📝 Snippet: [rob]: Should I use Redis or Postgres?...

🏷️ Categories: decision, technical
⭐ Importance: high | Confidence: 0.95
📅 2026-02-22 @ 2026-02-22T14:30:00
🎯 Score: 0.748
```

**Parameters:**
- `query` (required): Search query text
- `--user-id`: Filter by user (default: "USER_ID")
- `--limit`: Max results (default: 5)
- `--min-score`: Minimum similarity threshold (default: 0.5)
- `--json`: Output as JSON instead of formatted text

---

## Status

| Feature | Status |
|---------|--------|
| Manual search | ✅ `tr-out/scripts/search_memories.py` |
| Qdrant retrieval | ✅ 4 gems in `true_recall` |
| Auto-injection | ⏳ Future — needs implementation |
| Context awareness | ⏳ Future — query + recent context |
| Proactive retrieval | ⏳ Future — hook-based |

### Gap: Auto-Injection Not Implemented

**The curated gems exist, but no automatic injection.**

Current state:
- User asks question → I respond (no memory lookup)
- User says "search q for X" → Manual search → User sees results
- No proactive "Based on your previous decision..." context

**Options to implement:**
1. **OpenClaw context hook** — Search `true_recall` before each response
2. **Pre-prompt injection** — Add relevant gems to system prompt
3. **Hybrid** — Keep manual, add opt-in auto mode

---

*Part of: True-Recall Unified Memory System*  
*Related: tr-in (Ingestion), tr-process (Curation)*  
*History: Replaced disabled memory-qdrant plugin (Feb 21)*