#!/usr/bin/env python3
"""
q_save.py - Save memory to Qdrant with embeddings
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    import requests
except ImportError as e:
    print(f"ERROR: Missing packages. Run: pip3 install qdrant-client requests")
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

import uuid

def generate_id(content: str) -> str:
    """Generate deterministic UUID from content hash."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, content))

def check_duplicate(client: QdrantClient, user_id: str, content_hash: str) -> bool:
    """Check if this exact content already exists for this user."""
    try:
        # Search for existing point with same hash
        results = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                "must": [
                    {"key": "user_id", "match": {"value": user_id}},
                    {"key": "content_hash", "match": {"value": content_hash}}
                ]
            },
            limit=1
        )
        return len(results[0]) > 0
    except:
        return False

def save_memory(user_id: str, text: str, metadata: dict = None):
    """Save a memory to Qdrant."""
    client = get_qdrant_client()
    
    # Generate content hash for deduplication
    content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    
    # Check for duplicates
    if check_duplicate(client, user_id, content_hash):
        print(f"⚠ Duplicate memory, skipping")
        return None
    
    # Get embedding
    print(f"Generating embedding for: {text[:50]}...")
    embedding = get_embedding(text)
    
    if embedding is None:
        print("ERROR: Failed to generate embedding")
        return None
    
    # Create point
    point_id = generate_id(f"{user_id}{text}{datetime.now().isoformat()}")
    
    payload = {
        "user_id": user_id,
        "text": text,
        "content_hash": content_hash,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    point = PointStruct(
        id=point_id,
        vector=embedding,
        payload=payload
    )
    
    # Upsert
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    
    print(f"✓ Memory saved to Qdrant")
    print(f"  ID: {point_id[:16]}...")
    
    return point_id

def main():
    global COLLECTION_NAME
    
    parser = argparse.ArgumentParser(description="Save memory to Qdrant")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--text", required=True, help="Memory text")
    parser.add_argument("--collection", default=COLLECTION_NAME, help="Collection name")
    parser.add_argument("--metadata", default="{}", help="JSON metadata")
    
    args = parser.parse_args()
    
    COLLECTION_NAME = args.collection
    
    try:
        metadata = json.loads(args.metadata)
    except:
        metadata = {}
    
    save_memory(args.user_id, args.text, metadata)

if __name__ == "__main__":
    main()