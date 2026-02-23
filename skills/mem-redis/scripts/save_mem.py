#!/usr/bin/env python3
"""
save_mem.py - Save conversation turn to Redis buffer for True-Recall

Called by HEARTBEAT.md to stage conversation turns for the daily curator.
Format matches True-Recall's expected schema.
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import redis
except ImportError:
    print("ERROR: redis package required. Run: pip3 install redis")
    sys.exit(1)

# Redis config from environment
REDIS_HOST = os.environ.get("REDIS_HOST", "192.168.1.206")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
BUFFER_KEY = "mem:{user_id}"
RETENTION_HOURS = 24


def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def get_turn_number(user_id: str) -> int:
    """Get next turn number from Redis counter."""
    r = get_redis_client()
    counter_key = f"mem:counter:{user_id}"
    return r.incr(counter_key)


def should_skip_message(user_msg: str, ai_response: str) -> bool:
    """Filter out system metadata, thinking blocks, and noise."""
    
    # Skip empty messages
    if not user_msg or not user_msg.strip():
        return True
    
    # Skip system metadata blocks
    if 'Conversation info (untrusted metadata):' in user_msg:
        return True
    if '"sender_id": "openclaw-control-ui"' in user_msg:
        return True
    if '"message_id":' in user_msg and '"sender_id":' in user_msg:
        return True
    if '```json' in user_msg and 'sender_id' in user_msg:
        return True
    
    # Skip thinking blocks
    if user_msg.startswith('[thinking:') or '[thinking:' in user_msg[:50]:
        return True
    if ai_response.startswith('[thinking:') or '[thinking:' in ai_response[:50]:
        return True
    if 'Thought:' in user_msg[:20] or 'Reasoning:' in user_msg[:20]:
        return True
    
    # Skip pure acknowledgments
    ack_phrases = ['got it', 'done', 'ok', 'okay', 'sure', 'will do', 'noted', 'thanks', 'thank you']
    user_msg_lower = user_msg.lower().strip()
    if len(user_msg.split()) <= 3 and any(p in user_msg_lower for p in ack_phrases):
        return True
    
    # Skip test messages
    test_phrases = ['test message', 'ping', 'testing', 'this is a test', 'heartbeat']
    if any(p in user_msg_lower for p in test_phrases):
        return True
    
    return False


def save_turn(user_id: str, user_msg: str, ai_response: str, conversation_id: str = None) -> bool:
    """Save a single conversation turn to Redis buffer."""
    
    # Skip noise
    if should_skip_message(user_msg, ai_response):
        print(f"  Skipped (filtered)")
        return False
    
    r = get_redis_client()
    
    # Get turn number
    turn = get_turn_number(user_id)
    
    # Generate conversation_id if not provided
    if conversation_id is None:
        conversation_id = datetime.now().strftime("%Y%m%d")
    
    now = datetime.now()
    
    entry = {
        "user_id": user_id,
        "user_message": user_msg,
        "ai_response": ai_response,
        "turn": turn,
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "conversation_id": conversation_id
    }
    
    key = BUFFER_KEY.format(user_id=user_id)
    r.rpush(key, json.dumps(entry))
    r.expire(key, RETENTION_HOURS * 3600)
    
    print(f"  Saved turn {turn} to Redis ({user_id})")
    return True


def save_from_transcript(user_id: str, transcript_path: str):
    """Save from a session transcript file (legacy support)."""
    if not os.path.exists(transcript_path):
        print(f"  No transcript found: {transcript_path}")
        return 0
    
    with open(transcript_path, 'r') as f:
        lines = f.readlines()
    
    # Parse transcript - this is a placeholder for actual parsing logic
    # You'd implement based on your transcript format
    saved = 0
    # ... parsing logic ...
    
    return saved


def main():
    parser = argparse.ArgumentParser(description="Save conversation turn to Redis for True-Recall")
    parser.add_argument("--user-id", default=os.environ.get("USER_ID", "antlatt"), help="User identifier")
    parser.add_argument("--user-msg", help="User message to save")
    parser.add_argument("--ai-response", help="AI response to save")
    parser.add_argument("--conversation-id", help="Optional conversation ID")
    parser.add_argument("--transcript", help="Path to transcript file (legacy mode)")
    
    args = parser.parse_args()
    
    if args.transcript:
        # Legacy mode: save from transcript
        save_from_transcript(args.user_id, args.transcript)
    elif args.user_msg and args.ai_response:
        # Direct mode: save a single turn
        save_turn(args.user_id, args.user_msg, args.ai_response, args.conversation_id)
    else:
        # Heartbeat mode: no-op for now (would need session context)
        print("  No turn data provided, skipping")
    
    sys.exit(0)


if __name__ == "__main__":
    main()