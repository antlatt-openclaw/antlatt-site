# Knowledge base library
from .config import *
from .extractors import extract_content, normalize_url, content_hash, detect_type
from .chunking import chunk_text
from .embeddings import embed_text, embed_batch, embed_query
from .storage import (
    init_collections, store_source, store_chunk,
    get_source, search_chunks, list_sources, delete_source, get_stats
)