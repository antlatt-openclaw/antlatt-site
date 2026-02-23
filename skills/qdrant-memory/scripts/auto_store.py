#!/usr/bin/env python3
"""
auto_store.py - Automatic embedding and storage
Analyzes conversation turns and automatically stores significant memories.
"""

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Optional, List

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    import requests
except ImportError:
    print("ERROR: Missing packages. Run: pip3 install qdrant-client requests")
    sys.exit(1)

COLLECTION_NAME = "kimi_memories"
EMBEDDING_MODEL = "snowflake-arctic-embed2"

# Keywords that indicate important memories
SIGNIFICANCE_KEYWORDS = [
    "remember", "important", "don't forget", "note", "save",
    "my name is", "i am", "i work", "my project", "i prefer",
    "birthday", "anniversary", "deadline", "meeting"
]

def get_qdrant_client():
    url = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
    return QdrantClient(url=url)

def get_embedding(text: str) -> Optional[list]:
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

def is_significant(user_msg: str, ai_response: str) -> bool:
    """Determine if a turn is worth remembering."""
    combined = (user_msg + " " + ai_response).lower()
    
    for keyword in SIGNIFICANCE_KEYWORDS:
        if keyword in combined:
            return True
    
    # Long conversations might be significant
    if len(combined) > 500:
        return True
    
    return False

def auto_store(user_id: str, user_msg: str, ai_response: str, force: bool = False):
    """Automatically decide and store if significant."""
    
    if not force and not is_significant(user_msg, ai_response):
        return None
    
    client = get_qdrant_client()
    
    # Create combined text
    combined = f"User: {user_msg}\nAI: {ai_response}"
    
    # Generate 3 embeddings as per blueprint
    user_embedding = get_embedding(user_msg)
    ai_embedding = get_embedding(ai_response)
    combined_embedding = get_embedding(combined)
    
    if not combined_embedding:
        print("ERROR: Failed to generate embeddings")
        return None
    
    # Use combined embedding for storage
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}{combined}{datetime.now().isoformat()}"))
    
    point = PointStruct(
        id=point_id,
        vector=combined_embedding,
        payload={
            "user_id": user_id,
            "user_message": user_msg,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "has_user_embedding": user_embedding is not None,
            "has_ai_embedding": ai_embedding is not None
        }
    )
    
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    
    print(f"✓ Auto-stored memory: {user_msg[:50]}...")
    return point_id

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-store memories")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--user-msg", required=True, help="User message")
    parser.add_argument("--ai-response", required=True, help="AI response")
    parser.add_argument("--force", action="store_true", help="Force storage")
    
    args = parser.parse_args()
    
    auto_store(args.user_id, args.user_msg, args.ai_response, args.force)

if __name__ == "__main__":
    main()