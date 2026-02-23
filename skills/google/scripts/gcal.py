#!/usr/bin/env python3
"""
calendar.py - Google Calendar operations
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Load env
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

sys.path.insert(0, str(Path(__file__).parent))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Missing google-api-python-client")
    print("Run: pip3 install google-api-python-client")
    sys.exit(1)

from google_auth import get_credentials


def get_calendar_service():
    """Get authenticated Calendar service."""
    creds = get_credentials()
    if not creds:
        return None
    return build('calendar', 'v3', credentials=creds)


def get_events(service, start=None, end=None, max_results=20):
    """Get events in a time range."""
    if start is None:
        start = datetime.now().replace(hour=0, minute=0, second=0)
    if end is None:
        end = start + timedelta(days=1)
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except HttpError as e:
        print(f"Error getting events: {e}")
        return []


def format_event(event):
    """Format an event for display."""
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Get time
    if 'dateTime' in start:
        start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        time_str = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
    else:
        time_str = "All day"
    
    summary = event.get('summary', '(no title)')
    location = event.get('location', '')
    
    lines = [f"• {summary}", f"  {time_str}"]
    if location:
        lines.append(f"  📍 {location}")
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Calendar operations")
    parser.add_argument("--today", action="store_true", help="Today's events")
    parser.add_argument("--tomorrow", action="store_true", help="Tomorrow's events")
    parser.add_argument("--week", action="store_true", help="This week's events")
    parser.add_argument("--days", type=int, metavar="N", help="Next N days")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    service = get_calendar_service()
    if not service:
        print("ERROR: Could not authenticate. Run oauth_setup.py first.")
        sys.exit(1)
    
    tz = 'America/New_York'  # TODO: Get from user settings
    
    if args.today or (not any([args.tomorrow, args.week, args.days])):
        print("Today's events:\n")
        events = get_events(service)
        if not events:
            print("No events today.")
        for event in events:
            print(format_event(event))
            print()
    
    elif args.tomorrow:
        print("Tomorrow's events:\n")
        tomorrow = datetime.now() + timedelta(days=1)
        events = get_events(service, start=tomorrow.replace(hour=0, minute=0, second=0))
        if not events:
            print("No events tomorrow.")
        for event in events:
            print(format_event(event))
            print()
    
    elif args.week:
        print("This week's events:\n")
        start = datetime.now().replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=7)
        events = get_events(service, start=start, end=end)
        if not events:
            print("No events this week.")
        for event in events:
            print(format_event(event))
            print()
    
    elif args.days:
        print(f"Next {args.days} days:\n")
        start = datetime.now().replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=args.days)
        events = get_events(service, start=start, end=end)
        if not events:
            print(f"No events in the next {args.days} days.")
        for event in events:
            print(format_event(event))
            print()


if __name__ == "__main__":
    main()