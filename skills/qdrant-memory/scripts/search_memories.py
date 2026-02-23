#!/usr/bin/env python3
"""
search_memories.py - Semantic search across Qdrant memories
"""

import argparse
import json
import os
import sys

try:
    from qdrant_client import QdrantClient
    import requests
except ImportError:
    print("ERROR: Missing packages. Run: pip3 install qdrant-client requests")
    sys.exit(1)

COLLECTION_NAME = "kimi_memories"
EMBEDDING_MODEL = "snowflake-arctic-embed2"

def get_qdrant_client():
    url = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
    return QdrantClient(url=url)

def get_embedding(text: str) -> list:
    """Get embedding from Ollama."""
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        print(f"Embedding error: {e}")
    return None

def search_memories(user_id: str, query: str, limit: int = 10, collection: str = None):
    """Search memories using semantic similarity."""
    client = get_qdrant_client()
    
    collection_name = collection or COLLECTION_NAME
    
    # Get query embedding
    print(f"Searching for: '{query}'...")
    query_embedding = get_embedding(query)
    
    if query_embedding is None:
        print("ERROR: Failed to generate query embedding")
        return []
    
    # Search with user filter
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter={
            "must": [
                {"key": "user_id", "match": {"value": user_id}}
            ]
        },
        limit=limit
    )
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Search Qdrant memories")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--collection", help="Collection to search")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = search_memories(args.user_id, args.query, args.limit, args.collection)
    
    if args.json:
        output = [
            {
                "score": r.score,
                "text": r.payload.get("text", ""),
                "timestamp": r.payload.get("timestamp", ""),
                "id": r.id
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        print(f"\nFound {len(results)} memories:\n")
        for i, r in enumerate(results, 1):
            text = r.payload.get("text", "")
            ts = r.payload.get("timestamp", "unknown")
            score = r.score
            
            print(f"[{i}] Score: {score:.3f} | {ts}")
            print(f"    {text[:200]}{'...' if len(text) > 200 else ''}")
            print()

if __name__ == "__main__":
    main()