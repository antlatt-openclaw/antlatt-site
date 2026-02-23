#!/usr/bin/env python3
"""
init_kimi_memories.py - Initialize main memories collection
"""

import os
import sys

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance
except ImportError:
    print("ERROR: qdrant-client required. Run: pip3 install qdrant-client")
    sys.exit(1)

COLLECTION_NAME = "kimi_memories"
VECTOR_SIZE = 1024  # snowflake-arctic-embed2
DISTANCE = Distance.COSINE

def init_collection():
    url = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
    client = QdrantClient(url=url)
    
    # Check if exists
    collections = client.get_collections().collections
    existing = [c.name for c in collections]
    
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists")
        # Get info
        info = client.get_collection(COLLECTION_NAME)
        print(f"  Points: {info.points_count}")
        print(f"  Vector size: {info.config.params.vectors.size}")
        return
    
    # Create collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=DISTANCE
        )
    )
    
    print(f"✓ Created collection '{COLLECTION_NAME}'")
    print(f"  Vector size: {VECTOR_SIZE}")
    print(f"  Distance: {DISTANCE}")

if __name__ == "__main__":
    init_collection()