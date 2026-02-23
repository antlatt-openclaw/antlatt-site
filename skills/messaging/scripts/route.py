#!/usr/bin/env python3
"""
route.py - Route messages to specific Telegram topics
"""

import argparse
import json
import sys
from pathlib import Path

# Topic mapping
TOPIC_MAP = {
    "general": 27,          # https://t.me/c/3850499454/27
    "social": 25,           # https://t.me/c/3850499454/25
    "security": 23,         # https://t.me/c/3850499454/23
    "meta-analysis": 21,    # https://t.me/c/3850499454/21
    "health": 19,           # https://t.me/c/3850499454/19
    "financials": 17,       # https://t.me/c/3850499454/17
    "cron-updates": 15,     # https://t.me/c/3850499454/15
    "earnings": 13,         # https://t.me/c/3850499454/13
    "video-ideas": 11,      # https://t.me/c/3850499454/11
    "knowledge-base": 9,    # https://t.me/c/3850499454/9
    "email": 7,             # https://t.me/c/3850499454/7
    "crm": 4,               # https://t.me/c/3850499454/4
    "daily-brief": 2,       # https://t.me/c/3850499454/2
}

# Chat ID for topics (private group format: -100<numeric_id>)
CHAT_ID = "-1003850499454"  # Your Telegram group ID


def list_topics():
    """List all configured topics."""
    print("Configured Topics:")
    print("-" * 40)
    for topic, thread_id in TOPIC_MAP.items():
        status = f"ID: {thread_id}" if thread_id else "NOT CONFIGURED"
        print(f"  {topic:20} {status}")
    print()
    print("To get topic IDs:")
    print("  1. Open Telegram group with bot")
    print("  2. Create topics in group settings")
    print("  3. Update TOPIC_MAP in this file with thread_ids")


def route_message(topic: str, message: str, file: str = None):
    """Route a message to a specific topic."""
    if topic not in TOPIC_MAP:
        print(f"Error: Unknown topic '{topic}'")
        print(f"Available: {', '.join(TOPIC_MAP.keys())}")
        sys.exit(1)
    
    thread_id = TOPIC_MAP.get(topic)
    if not thread_id:
        print(f"Error: Topic '{topic}' not configured with thread_id")
        print("Update TOPIC_MAP in this script with actual thread_ids")
        sys.exit(1)
    
    # Build the command for message tool
    cmd = {
        "action": "send",
        "target": CHAT_ID,
        "threadId": thread_id,
        "message": message
    }
    
    if file:
        cmd["path"] = file
    
    # Output as JSON for calling from other scripts
    print(json.dumps(cmd))
    return cmd


def main():
    parser = argparse.ArgumentParser(description="Route messages to Telegram topics")
    parser.add_argument("--topic", "-t", help="Target topic name")
    parser.add_argument("--message", "-m", help="Message to send")
    parser.add_argument("--file", "-f", help="File to send")
    parser.add_argument("--list", "-l", action="store_true", help="List configured topics")
    
    args = parser.parse_args()
    
    if args.list:
        list_topics()
        return
    
    if not args.topic or not args.message:
        parser.print_help()
        return
    
    route_message(args.topic, args.message, args.file)


if __name__ == "__main__":
    main()