#!/usr/bin/env python3
"""
retrieve.py - Search and retrieve from knowledge base
"""

import argparse
import json
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.embeddings import embed_query
from lib.storage import search_chunks, get_source, get_stats


def retrieve(query: str, limit: int = 10, min_score: float = 0.3) -> list:
    """Retrieve relevant chunks for a query."""
    print(f"Searching: {query}")
    
    # Embed query
    query_embedding = embed_query(query)
    
    if not query_embedding:
        print("ERROR: Failed to embed query")
        return []
    
    # Search chunks
    chunks = search_chunks(query_embedding, limit=limit, min_score=min_score)
    
    # Enrich with source info
    results = []
    for chunk in chunks:
        source = get_source(chunk['source_id'])
        results.append({
            **chunk,
            "source_title": source.get('title', 'Unknown') if source else 'Unknown',
            "source_url": source.get('url', '') if source else '',
            "source_type": source.get('source_type', '') if source else ''
        })
    
    return results


def format_context(results: list, max_chars: int = 8000) -> str:
    """Format results as context for LLM."""
    context_parts = []
    total_chars = 0
    
    for i, r in enumerate(results, 1):
        excerpt = f"[{i}] From: {r['source_title']}\n{r['content']}\n"
        
        if total_chars + len(excerpt) > max_chars:
            break
        
        context_parts.append(excerpt)
        total_chars += len(excerpt)
    
    return "\n---\n".join(context_parts)


def main():
    parser = argparse.ArgumentParser(description="Search knowledge base")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Number of results")
    parser.add_argument("--min-score", "-m", type=float, default=0.3, help="Minimum similarity score")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--context", "-c", action="store_true", help="Format as LLM context")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats")
    
    args = parser.parse_args()
    
    # Stats mode
    if args.stats:
        stats = get_stats()
        print(f"Knowledge Base Stats:")
        print(f"  Sources: {stats.get('sources', 0)}")
        print(f"  Chunks: {stats.get('chunks', 0)}")
        return
    
    if not args.query:
        parser.print_help()
        return
    
    results = retrieve(args.query, limit=args.limit, min_score=args.min_score)
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.context:
        print(format_context(results))
        print(f"\n[{len(results)} sources retrieved]")
    else:
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} relevant chunks:\n")
        
        for i, r in enumerate(results, 1):
            score = r.get('score', 0)
            print(f"{i}. [{r['source_type']}] {r['source_title'][:50]}")
            print(f"   Score: {score:.3f}")
            print(f"   {r['content'][:200]}...")
            print()


if __name__ == "__main__":
    main()