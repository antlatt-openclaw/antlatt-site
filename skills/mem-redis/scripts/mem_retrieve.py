#!/usr/bin/env python3
"""
mem_retrieve.py - Retrieve recent memories from Redis buffer
"""

import argparse
import json
import os
import sys

try:
    import redis
except ImportError:
    print("ERROR: redis package required. Run: pip3 install redis")
    sys.exit(1)

def get_redis_client():
    host = os.environ.get("REDIS_HOST", "192.168.1.206")
    port = int(os.environ.get("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, decode_responses=True)

def retrieve_memories(user_id: str, limit: int = 10, offset: int = 0):
    """Retrieve recent memories from Redis."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    
    total = r.llen(key)
    
    # Get most recent (from end)
    start = max(0, total - limit - offset)
    end = total - 1 - offset
    
    if start > end:
        return [], 0
    
    items = r.lrange(key, start, end)
    memories = [json.loads(item) for item in items]
    
    return memories, total

def main():
    parser = argparse.ArgumentParser(description="Retrieve memories from Redis")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--limit", type=int, default=10, help="Number of memories")
    parser.add_argument("--offset", type=int, default=0, help="Offset from end")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    memories, total = retrieve_memories(args.user_id, args.limit, args.offset)
    
    if args.json:
        print(json.dumps(memories, indent=2))
    else:
        print(f"Redis Buffer: {total} total memories\n")
        for i, mem in enumerate(memories, 1):
            ts = mem.get("timestamp", "unknown")
            user_msg = mem.get("user_message", "")[:100]
            ai_msg = mem.get("ai_response", "")[:100]
            print(f"[{i}] {ts}")
            print(f"    User: {user_msg}{'...' if len(user_msg) == 100 else ''}")
            print(f"    AI: {ai_msg}{'...' if len(ai_msg) == 100 else ''}")
            print()

if __name__ == "__main__":
    main()