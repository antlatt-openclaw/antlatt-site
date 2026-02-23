# Messaging Setup

Organized Telegram topics and communication style for the AI assistant.

## Telegram Topics

Create these topics in your Telegram chat with the bot (you can create topics in a group chat with the bot):

| Topic | Purpose | Content Type |
|-------|---------|--------------|
| `daily-brief` | Morning briefing | Calendar, meetings, daily summary |
| `crm` | Contact management | New contacts, follow-ups, relationship alerts |
| `email` | Email alerts | Urgent emails, email drafts |
| `knowledge-base` | KB ingestion | New sources added, search results |
| `video-ideas` | Content pipeline | Pitch approvals, research |
| `earnings` | Earnings reports | Company earnings summaries |
| `cron-updates` | System alerts | **Failures only** (no noise) |
| `financials` | Financial data | Sensitive, DM only |
| `health` | Health tracking | Food/symptom logs, analysis |
| `meta-analysis` | System health | Platform council reports |
| `security` | Security alerts | Injection attempts, config changes |
| `social` | Social metrics | YouTube/social performance |
| `general` | Default | Everything else |

### Rules

1. **One topic per content type** - Never cross-post
2. **No duplicate messages** - Each notification goes to exactly one place
3. **Send files directly** - Use actual files, not links
4. **Failures only for cron** - Don't alert on successful runs

## Communication Style

### Message Limits

- **Max 2 messages per task:**
  1. Acknowledgment (if needed)
  2. Result

- **No play-by-play:**
  - ❌ "Reading file..."
  - ❌ "Searching..."
  - ❌ "Found 3 results..."
  - ✅ Just deliver the results

### Response Format

```
# Good
✓ Ingested into knowledge base
  Sources: 1
  Chunks: 44

# Bad
Reading file...
Processing...
Chunking into 44 pieces...
Embedding...
Done! ✓ Ingested into knowledge base
```

## Routing Messages to Topics

Use the `message` tool with `threadId` parameter:

```bash
# Send to specific topic
python3 scripts/route.py --topic "crm" "New contact: John from Acme Corp"

# Or use the message tool directly
message(action="send", target="<chat_id>", threadId="<topic_id>", message="...")
```

## Acknowledgment Reactions

For groups, the bot auto-reacts with 👀 when it sees a message (configured in `messages.ackReactionScope`).

Current config: `group-mentions` - only reacts when mentioned in groups.

## Slack Integration

Skipped. Using Telegram only for now.