#!/usr/bin/env python3
"""
hb_append.py - Append single turn to Redis buffer
Called during heartbeat to accumulate conversation turns.
"""

import argparse
import json
import hashlib
import os
import sys
from datetime import datetime

try:
    import redis
except ImportError:
    print("ERROR: redis package required. Run: pip3 install redis")
    sys.exit(1)

def get_redis_client():
    host = os.environ.get("REDIS_HOST", "192.168.1.206")
    port = int(os.environ.get("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, decode_responses=True)

def generate_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def append_turn(user_id: str, user_msg: str, ai_response: str, metadata: dict = None):
    """Append a conversation turn to Redis buffer."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    
    turn = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_msg,
        "ai_response": ai_response,
        "hash": generate_hash(f"{user_msg}{ai_response}"),
        "metadata": metadata or {}
    }
    
    # Push to list (right side)
    r.rpush(key, json.dumps(turn))
    
    # Get current buffer size
    count = r.llen(key)
    print(f"✓ Turn saved to Redis buffer ({count} total)")
    return count

def main():
    parser = argparse.ArgumentParser(description="Append turn to Redis buffer")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--user-msg", required=True, help="User message")
    parser.add_argument("--ai-response", required=True, help="AI response")
    parser.add_argument("--metadata", default="{}", help="JSON metadata")
    
    args = parser.parse_args()
    
    try:
        metadata = json.loads(args.metadata)
    except:
        metadata = {}
    
    append_turn(args.user_id, args.user_msg, args.ai_response, metadata)

if __name__ == "__main__":
    main()