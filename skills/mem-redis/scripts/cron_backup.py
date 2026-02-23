#!/usr/bin/env python3
"""
cron_backup.py - Daily Redis → Qdrant flush
Run via cron at 3:00 AM to move Redis buffer to Qdrant.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

try:
    import redis
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
except ImportError as e:
    print(f"ERROR: Missing packages. Run: pip3 install redis qdrant-client")
    sys.exit(1)

COLLECTION_NAME = "kimi_memories"
VECTOR_SIZE = 1024  # snowflake-arctic-embed2

def get_redis_client():
    host = os.environ.get("REDIS_HOST", "192.168.1.206")
    port = int(os.environ.get("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, decode_responses=True)

def get_qdrant_client():
    url = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
    return QdrantClient(url=url)

def get_embedding(text: str) -> list:
    """Get embedding from Ollama."""
    import requests
    
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": "snowflake-arctic-embed2", "prompt": text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        print(f"Embedding error: {e}")
    return None

def generate_id(content: str) -> str:
    """Generate unique ID from content hash."""
    return hashlib.sha256(content.encode()).hexdigest()

def backup_redis_to_qdrant(user_id: str, clear_after: bool = True):
    """Move all Redis memories to Qdrant."""
    r = get_redis_client()
    qdrant = get_qdrant_client()
    
    redis_key = f"mem:{user_id}"
    total = r.llen(redis_key)
    
    if total == 0:
        print(f"No memories to backup for {user_id}")
        return 0
    
    print(f"Backing up {total} memories for {user_id}...")
    
    # Get all items
    items = r.lrange(redis_key, 0, -1)
    
    points = []
    errors = 0
    
    for item in items:
        mem = json.loads(item)
        
        # Create combined text for embedding
        combined = f"{mem.get('user_message', '')} {mem.get('ai_response', '')}"
        
        # Get embedding
        embedding = get_embedding(combined)
        
        if embedding is None:
            print(f"  Skipping memory (no embedding): {mem.get('timestamp')}")
            errors += 1
            continue
        
        # Create point
        point_id = generate_id(combined)
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "user_id": user_id,
                "timestamp": mem.get("timestamp", ""),
                "user_message": mem.get("user_message", ""),
                "ai_response": mem.get("ai_response", ""),
                "session_id": mem.get("session_id", ""),
                "backup_date": datetime.now().isoformat()
            }
        )
        points.append(point)
    
    if points:
        # Upsert to Qdrant
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✓ Backed up {len(points)} memories to Qdrant")
        
        if errors:
            print(f"  {errors} memories skipped (embedding errors)")
    
    # Clear Redis buffer after successful backup
    if clear_after and len(points) > 0:
        r.delete(redis_key)
        print(f"✓ Cleared Redis buffer for {user_id}")
    
    return len(points)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Redis to Qdrant")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--no-clear", action="store_true", help="Don't clear Redis after backup")
    
    args = parser.parse_args()
    
    backup_redis_to_qdrant(args.user_id, clear_after=not args.no_clear)

if __name__ == "__main__":
    main()