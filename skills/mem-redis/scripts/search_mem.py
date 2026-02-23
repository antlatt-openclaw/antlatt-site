#!/usr/bin/env python3
"""
search_mem.py - Search Redis buffer for keyword matches
"""

import argparse
import json
import os
import sys
import re

try:
    import redis
except ImportError:
    print("ERROR: redis package required. Run: pip3 install redis")
    sys.exit(1)

def get_redis_client():
    host = os.environ.get("REDIS_HOST", "192.168.1.206")
    port = int(os.environ.get("REDIS_PORT", 6379))
    return redis.Redis(host=host, port=port, decode_responses=True)

def search_redis(user_id: str, query: str, limit: int = 20):
    """Search Redis buffer for keyword matches."""
    r = get_redis_client()
    key = f"mem:{user_id}"
    
    # Get all items (Redis doesn't support native search)
    total = r.llen(key)
    items = r.lrange(key, 0, -1)
    
    results = []
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for item in items:
        mem = json.loads(item)
        user_msg = mem.get("user_message", "").lower()
        ai_msg = mem.get("ai_response", "").lower()
        
        # Score based on matches
        score = 0
        if query_lower in user_msg or query_lower in ai_msg:
            score = 100  # Exact phrase match
        else:
            # Word-level matches
            user_words = set(user_msg.split())
            ai_words = set(ai_msg.split())
            word_matches = len(query_words & (user_words | ai_words))
            score = word_matches * 10
        
        if score > 0:
            mem["_score"] = score
            results.append(mem)
    
    # Sort by score
    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    
    return results[:limit], len(results)

def main():
    parser = argparse.ArgumentParser(description="Search Redis buffer")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results, total = search_redis(args.user_id, args.query, args.limit)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {total} matches for '{args.query}'\n")
        for i, mem in enumerate(results, 1):
            ts = mem.get("timestamp", "unknown")
            user_msg = mem.get("user_message", "")[:150]
            ai_msg = mem.get("ai_response", "")[:150]
            score = mem.get("_score", 0)
            print(f"[{i}] Score: {score} | {ts}")
            print(f"    User: {user_msg}{'...' if len(user_msg) == 150 else ''}")
            print(f"    AI: {ai_msg}{'...' if len(ai_msg) == 150 else ''}")
            print()

if __name__ == "__main__":
    main()