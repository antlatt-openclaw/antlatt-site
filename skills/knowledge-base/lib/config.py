#!/usr/bin/env python3
"""
config.py - Knowledge base configuration
"""

import os
from pathlib import Path

# Load .env
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Qdrant
QDRANT_URL = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
SOURCES_COLLECTION = "kb_sources"
CHUNKS_COLLECTION = "kb_chunks"

# Embeddings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "gemini-embedding-001"  # or text-embedding-3-small
EMBEDDING_DIM = 768  # 1536 for OpenAI

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# Quality thresholds
MIN_CONTENT_CHARS = 20
MIN_ARTICLE_CHARS = 500
MIN_PROSE_RATIO = 0.15
MIN_PROSE_LINE_LEN = 80
MAX_CONTENT_CHARS = 200000

# Dedup
TRACKING_PARAMS = [
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "igshid", "ref", "s", "t", "src", "source", "_ga", "mc_eid"
]

# Concurrency
LOCK_FILE = "/tmp/kb_ingest.lock"
LOCK_TIMEOUT_MINUTES = 15

# Retry
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]

# Embedding cache
EMBEDDING_CACHE_SIZE = 1000