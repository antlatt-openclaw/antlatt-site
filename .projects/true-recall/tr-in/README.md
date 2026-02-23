# Grok Prompt: Build The Curator System Prompt

**Your Task:** Create a comprehensive system prompt for "The Curator" — an AI agent that evaluates 24 hours of conversation and extracts contextual gems for long-term memory storage.

---

## Background: True-Recall System

**True-Recall** is a unified memory system with three components:
- **tr-in**: Captures conversation, filters noise, stages to Redis
- **The Curator** (tr-in/curator/): Reads 24h from Redis, extracts gems, stores to Qdrant
- **tr-out**: Retrieves gems from Qdrant for AI context injection

**The Problem with Current Memory Systems:**
- Line-by-line: Loses context ("User chose Redis" — but why?)
- Full dump: Unsearchable (24h of banter + 1 gem)
- Extracted facts: Lossy ("User prefers Redis" — when?)

**The Solution:** Contextual gems with timestamps

---

## The Curator's Role

**The Curator** is an AI agent (qwen3:4b-instruct) that:
1. Reads 24 hours of conversation from Redis as a single narrative
2. Evaluates holistically (not line-by-line)
3. Identifies "gems" — insights, decisions, solutions worth remembering
4. Extracts each gem with full temporal and contextual metadata
5. Stores to Qdrant for long-term retrieval

**Why "The Curator":**
Like a museum curator selecting pieces for an exhibit — discerning judgment about what matters, preserving context and meaning, creating a collection of value.

---

## Input Format

The Curator receives 24 hours of conversation as a JSON array:

```json
[
  {
    "user_id": "USER_ID",
    "user_message": "Should I use Redis or Postgres for caching?",
    "ai_response": "For short-term caching, Redis is faster. Postgres is better for persistence.",
    "turn": 15,
    "timestamp": "2026-02-22T14:28:00",
    "date": "2026-02-22",
    "conversation_id": "abc-123"
  },
  {
    "user_id": "USER_ID",
    "user_message": "I decided on Redis. Speed matters more for this use case.",
    "ai_response": "Good choice. Redis will handle the caching layer efficiently.",
    "turn": 16,
    "timestamp": "2026-02-22T14:30:00",
    "date": "2026-02-22",
    "conversation_id": "abc-123"
  }
]
```

**Key Points:**
- Each entry is one conversation turn (user message + AI response)
- Timestamps are ISO 8601 format with timezone
- Turn numbers show sequence within conversation
- Multiple conversations may be interleaved (different conversation_ids)

---

## Output Format

The Curator outputs an array of gems, each with full temporal and contextual metadata:

```json
[
  {
    "gem": "User decided to use Redis over Postgres for memory system caching",
    "context": "After discussing tradeoffs between persistence vs speed for short-term storage, user prioritized speed",
    "snippet": "USER: Should I use Redis or Postgres?\n[Kimi]: For caching, Redis is faster. Postgres is better for persistence.\nUSER: I decided on Redis. Speed matters more for this use case.",
    "categories": ["decision", "technical", "architecture"],
    "importance": "high",
    "confidence": 0.94,
    "timestamp": "2026-02-22T14:30:00",
    "date": "2026-02-22",
    "conversation_id": "abc-123",
    "turn_range": "15-16",
    "source_turns": [15, 16]
  }
]
```

### Required Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| **gem** | string | Core insight/decision | ✅ |
| **context** | string | Why it matters, surrounding circumstances | ✅ |
| **snippet** | string | ±2 turns of raw conversation | ✅ |
| **categories** | array | Classification tags | ✅ |
| **importance** | string | high/medium/low | ✅ |
| **confidence** | float | 0.0-1.0, AI certainty | ✅ |
| **timestamp** | string | ISO 8601 datetime | ✅ |
| **date** | string | YYYY-MM-DD | ✅ |
| **conversation_id** | string | UUID of source conversation | ✅ |
| **turn_range** | string | "start-end" format | ✅ |
| **source_turns** | array | List of turn numbers | ✅ |

### Temporal Field Details

**timestamp (ISO 8601):**
- Format: `YYYY-MM-DDTHH:MM:SS` (e.g., 2026-02-22T14:30:00)
- Precision: Minute-level (seconds optional)
- Timezone: UTC or local with offset
- Source: From the last turn in the gem's turn_range

**date (YYYY-MM-DD):**
- Format: `YYYY-MM-DD` (e.g., 2026-02-22)
- Purpose: Grouping and filtering by day
- Source: Extracted from timestamp

**conversation_id (UUID):**
- Format: Standard UUID string
- Purpose: Link back to full conversation if needed
- Source: From conversation metadata

**turn_range (string):**
- Format: `"start-end"` (e.g., "15-16", "42-45")
- Purpose: Human-readable range reference
- Source: Min and max turn numbers in snippet

**source_turns (array):**
- Format: `[15, 16]` or `[42, 43, 44, 45]`
- Purpose: Exact turn numbers for precise retrieval
- Source: All turns included in snippet

---

## What Makes a Gem

### Criteria for Extraction

**Extract if the conversation contains:**

1. **Decisions** - User chose X over Y
   - "I decided on Redis"
   - "Let's go with Mattermost"
   - "I'm switching to Linux"

2. **Technical Solutions** - How to solve a problem
   - "Use Python's asyncio for this"
   - "The fix is to increase the timeout"
   - "Deploy with Docker Compose"

3. **Preferences** - What user likes/dislikes
   - "I prefer dark mode"
   - "I hate popups"
   - "Local > cloud for me"

4. **Projects** - What user is working on
   - "Building a memory system"
   - "Setting up True-Recall"
   - "Working on the website"

5. **Knowledge** - Facts user learned or stated
   - "Redis has 24h TTL support"
   - "Qdrant uses cosine similarity"
   - "OpenClaw hooks are event-driven"

### Do NOT Extract

**Skip if:**

- **Trivial acknowledgments** - "ok", "thanks", "got it"
- **System metadata** - JSON blocks, sender IDs
- **Thinking blocks** - AI reasoning, thought processes
- **Test messages** - "test", "ping", "testing"
- **Banter** - Casual chat without decisions or insights
- **Repeated info** - Already captured in previous gem

### Quality Thresholds

| Metric | Minimum | Target | Notes |
|--------|---------|--------|-------|
| **Confidence** | 0.6 | 0.8+ | AI certainty this is worth remembering |
| **Importance** | medium | high | How significant is this gem? |
| **Context** | present | detailed | Enough to understand the gem |
| **Snippet** | 1 turn | 2-3 turns | Surrounding conversation |
| **Timestamp** | required | precise | ISO 8601 with timezone |

---

## The Curator's Evaluation Process

### Step 1: Read as Narrative

Read all 24 hours of conversation as a single story. Don't evaluate turn-by-turn. Look for:
- Arcs (how did we get from A to B?)
- Decisions (what did the user choose?)
- Insights (what did we learn?)
- Patterns (repeated themes or preferences)

### Step 2: Identify Gems

For each potential gem, ask:

1. **Is this worth remembering in 6 months?**
   - Yes → Continue
   - No → Skip

2. **Does this have context?**
   - Can I explain WHY this matters?
   - Is there surrounding conversation that explains it?

3. **Is this a duplicate?**
   - Was this already captured in a previous gem?
   - Is this just restating something already known?

4. **What's the confidence?**
   - High (0.8+): Clear decision or insight
   - Medium (0.6-0.8): Likely worth remembering
   - Low (<0.6): Probably skip

5. **Can I extract a precise timestamp?**
   - Must identify the exact moment the decision/insight occurred
   - Use the timestamp from the final turn in the gem's range
   - Format: ISO 8601 (2026-02-22T14:30:00)

### Step 3: Extract with Context and Timestamp

For each approved gem:

1. **Write the gem statement**
   - Clear, concise statement of the insight/decision
   - Example: "User decided to use Redis over Postgres for caching"

2. **Summarize the context**
   - Why did this decision happen?
   - What was the user trying to solve?
   - Example: "After discussing tradeoffs between persistence vs speed"

3. **Capture the snippet**
   - Include ±2 turns of raw conversation
   - Shows the actual dialogue that led to the gem
   - Example: "USER: Should I use Redis...\n[Kimi]: For caching...\nUSER: I decided on Redis"

4. **Extract precise timestamp**
   - Identify the exact moment the gem was formed
   - Use timestamp from the last turn in the gem's range
   - Include date, conversation_id, turn_range, source_turns

5. **Add metadata**
   - Categories: ["decision", "technical"]
   - Importance: "high"
   - Confidence: 0.94
   - Timestamp: "2026-02-22T14:30:00"
   - Date: "2026-02-22"
   - Conversation ID: "abc-123"
   - Turn Range: "15-16"
   - Source Turns: [15, 16]

### Step 4: Store to Qdrant

Each gem becomes a point in Qdrant with:
- **Vector:** Embedding of gem + context
- **Payload:** Full gem object with all metadata including timestamp
- **ID:** Deterministic hash (for deduplication)

### Step 5: Clear Redis Buffer

After successful curation:
- All processed turns removed from Redis
- Buffer ready for next 24 hours
- Gems safely stored in Qdrant with timestamps

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         tr-in                                 │
│                  (Ingestion & Curation)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER MESSAGE                                                 │
│     │                                                        │
│     ▼                                                        │
│  ┌─────────────────────┐                                    │
│  │  OpenClaw Gateway   │                                    │
│  │                     │                                    │
│  │  AI generates       │                                    │
│  │  response           │                                    │
│  └──────────┬──────────┘                                    │
│             │                                                │
│             │ message:sent                                   │
│             ▼                                                │
│  ┌─────────────────────┐                                    │
│  │  Hook captures      │                                    │
│  │  (tr-in/hook/)      │                                    │
│  └──────────┬──────────┘                                    │
│             │                                                │
│             ▼                                                │
│  ┌─────────────────────┐                                    │
│  │  stage_turn.py      │                                    │
│  │  (tr-in/staging/)   │                                    │
│  │                     │                                    │
│  │  Filters:           │                                    │
│  │  - System metadata  │                                    │
│  │  - Thinking blocks  │                                    │
│  │  - Trivial msgs     │                                    │
│  └──────────┬──────────┘                                    │
│             │                                                │
│             ▼                                                │
│  ┌─────────────────────┐                                    │
│  │  Redis Buffer       │                                    │
│  │  (24h hold)           │                                    │
│  │                     │                                    │
│  │  tr-out:buffer:USER_ID  │                                    │
│  └────────┬──────────────┘                                    │
│           │                                                  │
│           │ Daily @ 3 AM (cron)                              │
│           ▼                                                  │
│  ┌─────────────────────┐                                    │
│  │  The Curator        │                                    │
│  │  (tr-in/curator/)   │                                    │
│  │                     │                                    │
│  │  qwen3:4b-instruct  │                                    │
│  │                     │                                    │
│  │  1. Read 24h as     │                                    │
│  │     single narrative│                                    │
│  │  2. Identify gems   │                                    │
│  │  3. Extract with    │                                    │
│  │     timestamps      │                                    │
│  │  4. Store to Qdrant │                                    │
│  └──────────┬──────────┘                                    │
│             │                                                │
│             ▼                                                │
│  ┌─────────────────────┐                                    │
│  │  Qdrant             │                                    │
│  │  (Long-term)          │                                    │
│  │                     │                                    │
│  │  kimi_memories      │                                    │
│  │  collection         │                                    │
│  └─────────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Scripts

### `stage_turn.py` — Staging Script

**Location:** `skills/true-recall-out/scripts/stage_turn.py`

**Purpose:** Capture conversation turns and stage them to Redis buffer

**Called by:** OpenClaw `message:sent` hook

**Process:**
1. Receives user message + AI response
2. Creates structured turn object with metadata
3. Filters out system metadata and noise
4. Pushes to Redis list with 48-hour TTL

**Usage:**
```bash
python3 stage_turn.py \
  --user-id USER_ID \
  --user-msg "Hello" \
  --ai-response "Hi there" \
  --turn 1
```

**Redis Key:** `tr_out_buffer:{user_id}` (e.g., `mem:USER_ID`)

**Fields stored:**
- `user_id`: User identifier
- `user_message`: What user said
- `ai_response`: What AI responded
- `turn`: Turn number in conversation
- `timestamp`: ISO 8601 datetime
- `date`: YYYY-MM-DD for grouping
- `conversation_id`: Unique conversation UUID
- `status`: "staged" (pending curation)

---

## Key Principles

1. **I do nothing** — Just chat, system handles everything
2. **Event-driven** — Hook fires automatically on `message:sent`
3. **Filtered staging** — System metadata and noise removed at entry
4. **Holistic curation** — The Curator reads 24h as narrative, extracts gems
5. **Temporal awareness** — Every gem includes precise timestamp
6. **Contextual storage** — Gems stored with surrounding context
7. **Semantic retrieval** — Search finds relevant gems with meaning

---

## Relationship to Other Systems

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

### True-Recall is One Unified System

**tr-in is ONE HALF of True-Recall. tr-out is the OTHER HALF.**

They are not separate systems — they are the input and output sides of the same unified memory pipeline.

They are not separate systems — they are the input and output sides of the same unified memory pipeline.

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

- **tr-in** (this folder): Input side — receives raw conversation, filters noise, stages to Redis
- **tr-process**: The bridge — The Curator runs daily, extracts gems, stores to Qdrant
- **tr-out**: Output side — retrieves curated gems for AI context

### Predecessor: memory-qdrant Plugin (Replaced)

**The memory-qdrant plugin was a SEPARATE earlier attempt, NOT part of True-Recall.**

| Aspect | memory-qdrant Plugin | True-Recall (Unified) |
|--------|---------------------|----------------------|
| **Language** | TypeScript | Python |
| **Architecture** | Single plugin | Three-part pipeline (tr-in/process/out) |
| **Curation** | ❌ None (raw search) | ✅ LLM (The Curator) |
| **Timing** | Real-time | 24h delayed |
| **Collection** | `kimi_memories` | `true_recall` |
| **Status** | ❌ Disabled (Feb 21) | ✅ Active |

**History:**
- Feb 21: Built `memory-qdrant` TypeScript plugin — did dumb semantic search only
- Feb 21 21:36: Disabled `autoRecall` due to noise and lack of context awareness
- Feb 22: Built True-Recall as replacement — unified Python system with LLM curation

**Current:** Plugin still exists but is disabled. True-Recall (tr-in + tr-process + tr-out) is the active system.

---

## Status

| Component | Status |
|-----------|--------|
| Staging Script | ✅ `skills/true-recall-out/scripts/stage_turn.py` |
| Redis Buffer | ✅ `mem:USER_ID` at localhost:6379 |
| The Curator | ✅ `tr-process/curate_memories.py` |
| Cron | ✅ Daily at 3:30 AM |
| Log File | ✅ `/var/log/true-recall-curator.log` |

---

*Last Updated: 2026-02-22 11:25 CST*  
*Status: Fully Operational — 4 gems curated and stored*