#!/usr/bin/env python3
"""
init_private_court_docs.py - Initialize private documents collection
Optional collection for sensitive documents.
"""

import os
import sys

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance
except ImportError:
    print("ERROR: qdrant-client required. Run: pip3 install qdrant-client")
    sys.exit(1)

COLLECTION_NAME = "private_court_docs"
VECTOR_SIZE = 1024
DISTANCE = Distance.COSINE

def init_collection():
    url = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
    client = QdrantClient(url=url)
    
    collections = client.get_collections().collections
    existing = [c.name for c in collections]
    
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists")
        info = client.get_collection(COLLECTION_NAME)
        print(f"  Points: {info.points_count}")
        return
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=DISTANCE
        )
    )
    
    print(f"✓ Created collection '{COLLECTION_NAME}'")

if __name__ == "__main__":
    init_collection()