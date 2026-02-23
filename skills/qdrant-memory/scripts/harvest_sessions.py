#!/usr/bin/env python3
"""
harvest_sessions.py - Extract and store memories from old session transcripts
"""

import os
import sys
import hashlib
import uuid
import json
import re
from datetime import datetime
from pathlib import Path

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

def find_session_files(workspace_path: str) -> list:
    """Find all session transcript files."""
    sessions = []
    
    # Check memory/ directory
    memory_path = Path(workspace_path) / "memory"
    if memory_path.exists():
        for f in memory_path.glob("*.md"):
            sessions.append(str(f))
    
    return sessions

def parse_session(filepath: str) -> list:
    """Parse a session file into turns."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    turns = []
    
    # Try different parsing patterns
    # Pattern 1: **User**: / **AI**:
    user_pattern = r'\*\*User\*\*:\s*(.+?)(?=\*\*AI\*\*:|\Z)'
    ai_pattern = r'\*\*AI\*\*:\s*(.+?)(?=\*\*User\*\*:|\Z)'
    
    user_msgs = re.findall(user_pattern, content, re.DOTALL)
    ai_msgs = re.findall(ai_pattern, content, re.DOTALL)
    
    for i, (user_msg, ai_msg) in enumerate(zip(user_msgs, ai_msgs)):
        turns.append({
            "turn": i + 1,
            "user_message": user_msg.strip(),
            "ai_response": ai_msg.strip(),
            "source_file": filepath
        })
    
    return turns

def harvest_session(user_id: str, filepath: str, max_turns: int = 50):
    """Harvest memories from a session file."""
    turns = parse_session(filepath)
    
    if not turns:
        print(f"No turns found in {filepath}")
        return 0
    
    client = get_qdrant_client()
    points = []
    
    for i, turn in enumerate(turns[:max_turns]):
        combined = f"User: {turn['user_message']}\nAI: {turn['ai_response']}"
        
        # Skip very short or empty turns
        if len(combined) < 50:
            continue
        
        embedding = get_embedding(combined)
        
        if embedding is None:
            continue
        
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}{filepath}{turn['turn']}"))
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "user_id": user_id,
                "user_message": turn["user_message"],
                "ai_response": turn["ai_response"],
                "source_file": filepath,
                "turn": turn["turn"],
                "harvested": datetime.now().isoformat()
            }
        )
        points.append(point)
        
        print(f"  Turn {turn['turn']}: {turn['user_message'][:40]}...")
    
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✓ Harvested {len(points)} turns from {filepath}")
    
    return len(points)

def harvest_all(user_id: str, workspace_path: str = None):
    """Harvest all session files."""
    if workspace_path is None:
        workspace_path = "/root/.openclaw/antlatt-workspace"
    
    sessions = find_session_files(workspace_path)
    
    if not sessions:
        print("No session files found")
        return 0
    
    print(f"Found {len(sessions)} session files")
    
    total = 0
    for session in sessions:
        total += harvest_session(user_id, session)
    
    print(f"\n✓ Total harvested: {total} turns")
    return total

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Harvest sessions to Qdrant")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--file", help="Specific file to harvest")
    parser.add_argument("--workspace", help="Workspace path")
    parser.add_argument("--all", action="store_true", help="Harvest all sessions")
    
    args = parser.parse_args()
    
    if args.file:
        harvest_session(args.user_id, args.file)
    elif args.all:
        harvest_all(args.user_id, args.workspace)
    else:
        print("Specify --file or --all")

if __name__ == "__main__":
    main()