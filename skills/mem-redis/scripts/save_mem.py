#!/usr/bin/env python3
"""
save_mem.py - Save conversation to Redis buffer
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

def save_conversation(user_id: str, conversation: list, session_id: str = None):
    """Save a full conversation to Redis buffer."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    
    if session_id is None:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    saved = 0
    for turn in conversation:
        entry = {
            "timestamp": turn.get("timestamp", datetime.now().isoformat()),
            "user_message": turn.get("user_message", ""),
            "ai_response": turn.get("ai_response", ""),
            "session_id": session_id,
            "hash": generate_hash(f"{turn.get('user_message', '')}{turn.get('ai_response', '')}")
        }
        r.rpush(key, json.dumps(entry))
        saved += 1
    
    count = r.llen(key)
    print(f"✓ Saved {saved} turns to Redis buffer ({count} total)")
    return count

def save_from_session(user_id: str, session_file: str = None):
    """Save from session transcript file if available."""
    # Check for today's session file
    today = datetime.now().strftime("%Y-%m-%d")
    if session_file is None:
        session_file = f"memory/{today}.md"
    
    if not os.path.exists(session_file):
        print(f"No session file found: {session_file}")
        return 0
    
    # Parse and save
    with open(session_file, 'r') as f:
        content = f.read()
    
    # Simple parsing - each turn separated by markers
    # Adjust parsing logic based on your session format
    conversation = []
    # Add parsing logic here
    
    return save_conversation(user_id, conversation)

def main():
    parser = argparse.ArgumentParser(description="Save conversation to Redis")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--session-file", help="Path to session transcript")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        # Interactive mode - read from stdin
        print("Enter conversation (JSON format, Ctrl+D to finish):")
        try:
            data = json.load(sys.stdin)
            if isinstance(data, list):
                save_conversation(args.user_id, data)
        except Exception as e:
            print(f"Error: {e}")
    else:
        save_from_session(args.user_id, args.session_file)

if __name__ == "__main__":
    main()