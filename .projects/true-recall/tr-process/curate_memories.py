#!/usr/bin/env python3
"""
True-Recall Curator: Holistic Gem Extraction

Reads 24 hours of conversation from Redis, processes as narrative,
extracts contextual gems using qwen3, stores to Qdrant with mxbai embeddings.

Usage:
    python curate_memories.py --user-id antlatt
    python curate_memories.py --user-id antlatt --hours 48
    python curate_memories.py --user-id antlatt --dry-run
"""

import json
import argparse
import os
import sys
from datetime import datetime, timedelta
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
    import redis
    import requests
except ImportError as e:
    print(f"ERROR: Missing packages. Run: pip3 install redis requests")
    sys.exit(1)

# Configuration (from environment or defaults)
REDIS_HOST = os.environ.get("REDIS_HOST", "192.168.1.206")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))

QDRANT_URL = os.environ.get("QDRANT_URL", "http://192.168.1.202:6333")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "true_recall")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.1.207:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "mxbai-embed-large")
CURATOR_MODEL = os.environ.get("CURATOR_MODEL", "qwen3:8b")

# Load curator prompt (relative to script location)
CURATOR_PROMPT_PATH = os.path.join(PROJECT_DIR, "curator_prompt.md")


def load_curator_prompt() -> str:
    """Load the curator system prompt."""
    try:
        with open(CURATOR_PROMPT_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Curator prompt not found at {CURATOR_PROMPT_PATH}")


def get_redis_client() -> redis.Redis:
    """Get Redis connection."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )


def get_staged_turns(user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
    """Get all staged turns from Redis for a user."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    
    # Get all items from the list
    items = r.lrange(key, 0, -1)
    
    turns = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    for item in items:
        try:
            turn = json.loads(item)
            # Filter by timestamp if present
            if 'timestamp' in turn and hours:
                try:
                    turn_time = datetime.fromisoformat(turn['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
                    if turn_time < cutoff:
                        continue
                except ValueError:
                    pass
            turns.append(turn)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Skipping invalid turn: {e}")
            continue
    
    # Sort by turn number if present
    turns.sort(key=lambda x: x.get('turn', 0))
    return turns


def extract_gems_with_curator(turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Use qwen3 to extract gems from conversation turns."""
    if not turns:
        return []
    
    prompt = load_curator_prompt()
    
    # Build the conversation input
    conversation_json = json.dumps(turns, indent=2)
    
    print(f"📝 Sending {len(turns)} turns to curator ({CURATOR_MODEL})...")
    
    # Call Ollama with native system prompt
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": CURATOR_MODEL,
            "system": prompt,
            "prompt": f"## Input Conversation\n\n```json\n{conversation_json}\n```\n\n## Output\n",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4000
            }
        },
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Curation failed: {response.text}")
    
    result = response.json()
    output = result.get('response', '').strip()
    
    # Extract JSON from output (handle markdown code blocks)
    if '```json' in output:
        output = output.split('```json')[1].split('```')[0].strip()
    elif '```' in output:
        output = output.split('```')[1].split('```')[0].strip()
    
    try:
        gems = json.loads(output)
        if not isinstance(gems, list):
            print(f"Warning: Curator returned non-list, wrapping: {type(gems)}")
            gems = [gems] if gems else []
        return gems
    except json.JSONDecodeError as e:
        print(f"Error parsing curator output: {e}")
        print(f"Raw output: {output[:500]}...")
        return []


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


def store_gem_to_qdrant(gem: Dict[str, Any], user_id: str) -> bool:
    """Store a gem to Qdrant with embedding."""
    # Create embedding from gem text
    embedding_text = f"{gem['gem']} {gem['context']} {gem['snippet']}"
    print(f"  🔢 Generating embedding...")
    vector = get_embedding(embedding_text)
    
    # Prepare payload
    payload = {
        "user_id": user_id,
        **gem
    }
    
    # Generate deterministic integer ID (Qdrant requires integer or UUID)
    import hashlib
    hash_bytes = hashlib.sha256(
        f"{user_id}:{gem.get('conversation_id', 'unknown')}:{gem.get('turn_range', '0')}".encode()
    ).digest()[:8]
    gem_id = int.from_bytes(hash_bytes, byteorder='big') % (2**63)  # Ensure positive int64
    
    # Store to Qdrant
    response = requests.put(
        f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points",
        json={
            "points": [{
                "id": gem_id,
                "vector": vector,
                "payload": payload
            }]
        }
    )
    
    return response.status_code == 200


def clear_staged_turns(user_id: str) -> bool:
    """Clear the Redis buffer after successful curation."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    return r.delete(key) > 0


def main():
    parser = argparse.ArgumentParser(description="True-Recall Curator")
    parser.add_argument("--user-id", default=os.environ.get("USER_ID", "antlatt"), help="User ID to process")
    parser.add_argument("--hours", type=int, default=24, help="Hours of history to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't store or clear, just preview")
    args = parser.parse_args()
    
    print(f"🔍 True-Recall Curator for {args.user_id}")
    print(f"⏰ Processing last {args.hours} hours")
    print(f"🧠 Embedding model: {EMBEDDING_MODEL}")
    print(f"🎨 Curator model: {CURATOR_MODEL}")
    print(f"💎 Target collection: {QDRANT_COLLECTION}")
    print(f"📊 Qdrant: {QDRANT_URL}")
    print(f"📦 Redis: {REDIS_HOST}:{REDIS_PORT}")
    print()
    
    # Get staged turns
    print("📥 Fetching conversation turns from Redis...")
    turns = get_staged_turns(args.user_id, args.hours)
    print(f"✅ Found {len(turns)} turns")
    
    if not turns:
        print("⚠️ No turns to process. Exiting.")
        return
    
    # Extract gems
    print("\n🧠 Extracting gems with The Curator...")
    gems = extract_gems_with_curator(turns)
    print(f"✅ Extracted {len(gems)} gems")
    
    if not gems:
        print("⚠️ No gems extracted. Clearing buffer and exiting.")
        if not args.dry_run:
            clear_staged_turns(args.user_id)
        return
    
    # Preview gems
    print("\n💎 Preview of extracted gems:")
    for i, gem in enumerate(gems[:3], 1):
        print(f"\n--- Gem {i} ---")
        print(f"Gem: {gem.get('gem', 'N/A')[:100]}...")
        print(f"Categories: {gem.get('categories', [])}")
        print(f"Importance: {gem.get('importance', 'N/A')}")
        print(f"Confidence: {gem.get('confidence', 'N/A')}")
    
    if len(gems) > 3:
        print(f"\n... and {len(gems) - 3} more gems")
    
    if args.dry_run:
        print("\n🏃 DRY RUN: Not storing or clearing.")
        return
    
    # Store gems
    print("\n💾 Storing gems to Qdrant...")
    stored = 0
    for gem in gems:
        if store_gem_to_qdrant(gem, args.user_id):
            stored += 1
            print(f"  ✅ Stored: {gem.get('gem', 'N/A')[:50]}...")
        else:
            print(f"  ⚠️ Failed to store gem: {gem.get('gem', 'N/A')[:50]}...")
    
    print(f"\n✅ Stored {stored}/{len(gems)} gems")
    
    # Clear buffer
    print("\n🧹 Clearing Redis buffer...")
    if clear_staged_turns(args.user_id):
        print("✅ Buffer cleared")
    else:
        print("⚠️ Buffer was empty or already cleared")
    
    print("\n🎉 Curation complete!")


if __name__ == "__main__":
    main()