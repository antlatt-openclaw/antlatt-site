# Knowledge Base - RAG System

Personal knowledge base with retrieval-augmented generation.

## Commands

```bash
# Ingest content
python3 skills/knowledge-base/scripts/ingest.py <url_or_file>

# Search/retrieve
python3 skills/knowledge-base/scripts/retrieve.py "your query"

# List sources
python3 skills/knowledge-base/scripts/ingest.py --list

# Delete source
python3 skills/knowledge-base/scripts/ingest.py --delete <source_id>
```

## Supported Sources

- Web articles (with fallback extraction chain)
- YouTube videos (transcripts)
- Twitter/X posts
- PDFs
- Plain text files

## Architecture

- **Storage**: Qdrant at 192.168.1.202:6333
- **Collections**: `kb_sources`, `kb_chunks`
- **Embeddings**: Gemini embedding-001 (768d) or OpenAI text-embedding-3-small
- **Chunking**: 800 chars, 200 overlap, sentence-boundary splits

## Extraction Fallback Chain

1. Twitter/X → FxTwitter API → X API → web scrape
2. YouTube → transcript API → yt-dlp
3. Articles → Readability → Firecrawl → Playwright → raw fetch

## Quality Gates

- Min 20 chars, 500+ for articles
- 15% prose lines (80+ chars) for non-tweets
- Error page detection
- Dedup by URL + content hash