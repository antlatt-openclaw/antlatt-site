#!/usr/bin/env python3
"""
daily_conversation_backup.py - Backup daily conversation logs
Reads from memory/YYYY-MM-DD.md and backs up to Qdrant.
"""

import os
import sys
import hashlib
import uuid
from datetime import datetime, timedelta

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
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

def parse_daily_file(filepath: str) -> list:
    """Parse daily markdown file into conversation turns."""
    turns = []
    
    if not os.path.exists(filepath):
        return turns
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Simple parsing - adjust based on your format
    # This expects format like:
    # **User**: message
    # **AI**: response
    
    import re
    pattern = r'\*\*User\*\*:\s*(.+?)(?=\*\*AI\*\*:|\Z)'
    ai_pattern = r'\*\*AI\*\*:\s*(.+?)(?=\*\*User\*\*:|\Z)'
    
    user_msgs = re.findall(pattern, content, re.DOTALL)
    ai_msgs = re.findall(ai_pattern, content, re.DOTALL)
    
    for i, (user_msg, ai_msg) in enumerate(zip(user_msgs, ai_msgs)):
        turns.append({
            "turn": i + 1,
            "user_message": user_msg.strip(),
            "ai_response": ai_msg.strip()
        })
    
    return turns

def backup_daily(user_id: str, date: str = None):
    """Backup a specific day's conversations."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    filepath = f"memory/{date}.md"
    turns = parse_daily_file(filepath)
    
    if not turns:
        print(f"No turns found for {date}")
        return 0
    
    client = get_qdrant_client()
    points = []
    
    for turn in turns:
        combined = f"User: {turn['user_message']}\nAI: {turn['ai_response']}"
        embedding = get_embedding(combined)
        
        if embedding is None:
            continue
        
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}{date}{turn['turn']}"))
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "user_id": user_id,
                "user_message": turn["user_message"],
                "ai_response": turn["ai_response"],
                "date": date,
                "turn": turn["turn"],
                "timestamp": datetime.now().isoformat(),
                "source": "daily_backup"
            }
        )
        points.append(point)
    
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✓ Backed up {len(points)} turns from {date}")
    
    return len(points)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup daily conversations")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--date", help="Date to backup (YYYY-MM-DD), defaults to today")
    parser.add_argument("--yesterday", action="store_true", help="Backup yesterday")
    
    args = parser.parse_args()
    
    date = args.date
    if args.yesterday:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    backup_daily(args.user_id, date)

if __name__ == "__main__":
    main()