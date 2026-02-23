#!/usr/bin/env python3
"""
ingest.py - Ingest URLs and files into the knowledge base
"""

import argparse
import json
import os
import sys
import fcntl
from pathlib import Path
from datetime import datetime

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import LOCK_FILE, LOCK_TIMEOUT_MINUTES, EMBEDDING_DIM
from lib.extractors import extract_content, content_hash
from lib.chunking import chunk_text
from lib.embeddings import embed_batch
from lib.storage import (
    init_collections, store_source, store_chunk,
    get_source_by_hash, list_sources, delete_source, get_stats
)


def acquire_lock() -> bool:
    """Acquire ingestion lock. Returns True if acquired."""
    lock_path = Path(LOCK_FILE)
    
    # Check for stale lock
    if lock_path.exists():
        try:
            pid = int(lock_path.read_text().strip())
            # Check if PID is still running
            if not Path(f"/proc/{pid}").exists():
                lock_path.unlink()
            else:
                return False
        except:
            lock_path.unlink()
    
    # Acquire lock
    lock_path.write_text(str(os.getpid()))
    return True


def release_lock():
    """Release ingestion lock."""
    Path(LOCK_FILE).unlink(missing_ok=True)


def ingest_url(url: str, tags: list = None) -> dict:
    """Ingest a URL into the knowledge base."""
    print(f"Extracting: {url}")
    
    # Extract content
    result = extract_content(url=url)
    
    if result.get('error'):
        return {"success": False, "error": result['error']}
    
    content = result['content']
    title = result['title']
    source_type = result['source_type']
    normalized_url = result['normalized_url']
    
    # Generate content hash
    c_hash = content_hash(content)
    
    # Check for duplicate
    existing = get_source_by_hash(c_hash)
    if existing:
        return {"success": False, "error": "Duplicate content", "existing_id": existing['id']}
    
    print(f"Type: {source_type}, Chars: {len(content)}")
    
    # Store source
    source_id = store_source(
        url=normalized_url,
        title=title or url,
        source_type=source_type,
        raw_content=content,
        content_hash=c_hash,
        tags=tags or []
    )
    
    print(f"Source ID: {source_id}")
    
    # Chunk content
    chunks = chunk_text(content)
    print(f"Chunks: {len(chunks)}")
    
    # Generate embeddings in batches
    chunk_contents = [c['content'] for c in chunks]
    embeddings = embed_batch(chunk_contents)
    
    # Store chunks
    stored = 0
    for chunk, embedding in zip(chunks, embeddings):
        if embedding:
            store_chunk(
                source_id=source_id,
                chunk_index=chunk['chunk_index'],
                content=chunk['content'],
                embedding=embedding
            )
            stored += 1
    
    print(f"Stored {stored}/{len(chunks)} chunks with embeddings")
    
    return {
        "success": True,
        "source_id": source_id,
        "url": normalized_url,
        "title": title,
        "source_type": source_type,
        "content_chars": len(content),
        "chunks": len(chunks),
        "chunks_stored": stored
    }


def ingest_file(filepath: str, tags: list = None) -> dict:
    """Ingest a file into the knowledge base."""
    path = Path(filepath)
    
    if not path.exists():
        return {"success": False, "error": f"File not found: {filepath}"}
    
    print(f"Ingesting: {filepath}")
    
    # Extract content
    result = extract_content(filepath=filepath)
    
    if result.get('error'):
        return {"success": False, "error": result['error']}
    
    content = result['content']
    title = result['title'] or path.name
    source_type = result['source_type']
    
    # Generate content hash
    c_hash = content_hash(content)
    
    # Check for duplicate
    existing = get_source_by_hash(c_hash)
    if existing:
        return {"success": False, "error": "Duplicate content", "existing_id": existing['id']}
    
    print(f"Type: {source_type}, Chars: {len(content)}")
    
    # Store source
    source_id = store_source(
        url=f"file://{path.absolute()}",
        title=title,
        source_type=source_type,
        raw_content=content,
        content_hash=c_hash,
        tags=tags or []
    )
    
    # Chunk and embed
    chunks = chunk_text(content)
    chunk_contents = [c['content'] for c in chunks]
    embeddings = embed_batch(chunk_contents)
    
    stored = 0
    for chunk, embedding in zip(chunks, embeddings):
        if embedding:
            store_chunk(
                source_id=source_id,
                chunk_index=chunk['chunk_index'],
                content=chunk['content'],
                embedding=embedding
            )
            stored += 1
    
    return {
        "success": True,
        "source_id": source_id,
        "title": title,
        "source_type": source_type,
        "chunks": len(chunks),
        "chunks_stored": stored
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest content into knowledge base")
    parser.add_argument("source", nargs="?", help="URL or file path to ingest")
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--list", "-l", action="store_true", help="List sources")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats")
    parser.add_argument("--delete", "-d", help="Delete source by ID")
    parser.add_argument("--type", help="Filter by type when listing")
    parser.add_argument("--limit", "-n", type=int, default=50, help="Limit results")
    
    args = parser.parse_args()
    
    # Initialize collections
    init_collections()
    
    # List mode
    if args.list:
        sources = list_sources(limit=args.limit, source_type=args.type)
        if args.json:
            print(json.dumps(sources, indent=2))
        else:
            print(f"Sources ({len(sources)}):\n")
            for s in sources:
                print(f"  [{s['source_type']}] {s['title'][:60]}")
                print(f"    ID: {s['id']}")
                print(f"    URL: {s.get('url', 'N/A')}")
                print(f"    Tags: {s.get('tags', [])}")
                print()
        return
    
    # Stats mode
    if args.stats:
        stats = get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Knowledge Base Stats:")
            print(f"  Sources: {stats.get('sources', 0)}")
            print(f"  Chunks: {stats.get('chunks', 0)}")
        return
    
    # Delete mode
    if args.delete:
        delete_source(args.delete)
        print(f"Deleted source: {args.delete}")
        return
    
    # Ingest mode
    if not args.source:
        parser.print_help()
        return
    
    # Acquire lock
    if not acquire_lock():
        print("ERROR: Another ingestion is in progress")
        sys.exit(1)
    
    try:
        tags = args.tags.split(",") if args.tags else None
        
        # Detect URL vs file
        if args.source.startswith(("http://", "https://")):
            result = ingest_url(args.source, tags=tags)
        else:
            result = ingest_file(args.source, tags=tags)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result['success']:
                print(f"\n✓ Ingested successfully!")
                print(f"  Source ID: {result['source_id']}")
                print(f"  Chunks: {result['chunks_stored']}")
            else:
                print(f"\n✗ Error: {result['error']}")
                sys.exit(1)
    
    finally:
        release_lock()


if __name__ == "__main__":
    main()