#!/usr/bin/env python3
"""
True-Recall Memory Search

Search for contextual gems in the true_recall collection.
Uses mxbai-embed-large for query embedding.

Usage:
    python search_memories.py "What did I decide about Redis?"
    python search_memories.py --user-id antlatt --limit 5 "database decision"
"""

import json
import argparse
import os
import sys
from typing import List, Dict, Any

# Load environment from .env file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ENV_FILE = os.path.join(PROJECT_DIR, ".env")

def load_env():
    """Load environment variables from .env file."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

load_env()

try:
    import requests
except ImportError as e:
    print(f"ERROR: Missing packages. Run: pip3 install requests")
    sys.exit(1)

# Configuration (from environment or defaults)
QDRANT_URL = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "true_recall")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.1.207:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "mxbai-embed-large")


def get_embedding(text: str) -> List[float]:
    """Get embedding vector from Ollama using mxbai-embed-large."""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Embedding failed: {response.text}")
    
    return response.json()['embedding']


def search_memories(
    query: str,
    user_id: str = None,
    limit: int = 5,
    min_score: float = 0.5
) -> List[Dict[str, Any]]:
    """Search for gems in Qdrant."""
    # Get query embedding
    query_vector = get_embedding(query)
    
    # Build filter
    filter_dict = None
    if user_id:
        filter_dict = {
            "must": [
                {"key": "user_id", "match": {"value": user_id}}
            ]
        }
    
    # Search Qdrant
    response = requests.post(
        f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search",
        json={
            "vector": query_vector,
            "limit": limit,
            "with_payload": True,
            "filter": filter_dict,
            "score_threshold": min_score
        }
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Search failed: {response.text}")
    
    results = response.json()['result']
    
    # Format results
    gems = []
    for result in results:
        gem = result['payload']
        gem['score'] = result['score']
        gems.append(gem)
    
    return gems


def format_gem(gem: Dict[str, Any]) -> str:
    """Format a gem for display."""
    lines = [
        f"💎 {gem.get('gem', 'N/A')}",
        f"",
        f"📋 Context: {gem.get('context', 'N/A')}",
        f"",
        f"📝 Snippet: {gem.get('snippet', 'N/A')[:200]}...",
        f"",
        f"🏷️ Categories: {', '.join(gem.get('categories', []))}",
        f"⭐ Importance: {gem.get('importance', 'N/A')} | Confidence: {gem.get('confidence', 'N/A')}",
        f"📅 {gem.get('date', 'N/A')} @ {gem.get('timestamp', 'N/A')}",
        f"🎯 Score: {gem.get('score', 'N/A'):.3f}",
        f"---"
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search True-Recall memories")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--user-id", default=os.environ.get("USER_ID", "antlatt"), help="User ID to search for")
    parser.add_argument("--limit", type=int, default=5, help="Number of results")
    parser.add_argument("--min-score", type=float, default=0.5, help="Minimum similarity score")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    print(f"🔍 Searching: '{args.query}'")
    print(f"👤 User: {args.user_id}")
    print(f"📊 Limit: {args.limit}, Min score: {args.min_score}")
    print(f"🧠 Embedding: {EMBEDDING_MODEL}")
    print(f"💎 Collection: {QDRANT_COLLECTION}")
    print()
    
    try:
        gems = search_memories(
            query=args.query,
            user_id=args.user_id,
            limit=args.limit,
            min_score=args.min_score
        )
        
        if args.json:
            print(json.dumps(gems, indent=2))
        else:
            if not gems:
                print("❌ No memories found matching your query.")
            else:
                print(f"✅ Found {len(gems)} gem(s):\n")
                for gem in gems:
                    print(format_gem(gem))
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()