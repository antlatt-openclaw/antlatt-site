#!/usr/bin/env python3
"""
gmail.py - Gmail operations
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = get_credentials()
    if not creds:
        return None
    return build('gmail', 'v1', credentials=creds)


def list_messages(service, query='in:inbox', max_results=10, label_ids=None):
    """List recent messages."""
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            labelIds=label_ids
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except HttpError as e:
        print(f"Error listing messages: {e}")
        return []


def get_message(service, msg_id):
    """Get full message details."""
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From', 'To', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        
        return {
            'id': msg_id,
            'threadId': msg.get('threadId'),
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', '(no subject)'),
            'date': headers.get('Date', ''),
            'snippet': msg.get('snippet', ''),
            'labelIds': msg.get('labelIds', [])
        }
    except HttpError as e:
        print(f"Error getting message: {e}")
        return None


def send_email(service, to, subject, body, cc=None, bcc=None):
    """Send an email."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc
    message['from'] = os.environ.get('GOOGLE_EMAIL', 'me')
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        print(f"✓ Email sent to {to}")
        print(f"  Message ID: {result['id']}")
        return result
    except HttpError as e:
        print(f"Error sending email: {e}")
        return None


def search_messages(service, query, max_results=10):
    """Search messages."""
    return list_messages(service, query=query, max_results=max_results)


def format_message(msg, include_snippet=True):
    """Format a message for display."""
    is_unread = 'UNREAD' in msg.get('labelIds', [])
    marker = "●" if is_unread else " "
    
    lines = [
        f"{marker} {msg['subject']}",
        f"  From: {msg['from']}",
        f"  Date: {msg['date']}",
    ]
    
    if include_snippet and msg.get('snippet'):
        snippet = msg['snippet'][:100]
        if len(msg['snippet']) > 100:
            snippet += "..."
        lines.append(f"  Preview: {snippet}")
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gmail operations")
    parser.add_argument("--recent", type=int, metavar="N", help="Show N recent emails")
    parser.add_argument("--sent", type=int, metavar="N", help="Show N sent emails")
    parser.add_argument("--search", metavar="QUERY", help="Search emails")
    parser.add_argument("--send-to", metavar="EMAIL", help="Recipient email")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    service = get_gmail_service()
    if not service:
        print("ERROR: Could not authenticate. Run oauth_setup.py first.")
        sys.exit(1)
    
    if args.recent:
        print(f"Recent {args.recent} emails:\n")
        messages = list_messages(service, 'in:inbox', max_results=args.recent)
        for msg_info in messages:
            msg = get_message(service, msg_info['id'])
            if msg:
                print(format_message(msg))
                print()
    
    elif args.sent:
        print(f"Recent {args.sent} sent emails:\n")
        messages = list_messages(service, 'in:sent', max_results=args.sent)
        for msg_info in messages:
            msg = get_message(service, msg_info['id'])
            if msg:
                print(format_message(msg))
                print()
    
    elif args.search:
        print(f"Search results for: {args.search}\n")
        messages = list_messages(service, args.search, max_results=10)
        for msg_info in messages:
            msg = get_message(service, msg_info['id'])
            if msg:
                print(format_message(msg))
                print()
    
    elif args.send_to and args.subject and args.body:
        send_email(service, args.send_to, args.subject, args.body)
    
    else:
        # Default: show recent inbox
        print("Recent inbox:\n")
        messages = list_messages(service, 'in:inbox', max_results=5)
        if not messages:
            print("No messages found.")
        for msg_info in messages:
            msg = get_message(service, msg_info['id'])
            if msg:
                print(format_message(msg))
                print()


if __name__ == "__main__":
    main()