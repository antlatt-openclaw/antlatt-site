#!/usr/bin/env python3
"""
drive.py - Google Drive operations
"""

import os
import sys
from pathlib import Path

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


def get_drive_service():
    """Get authenticated Drive service."""
    creds = get_credentials()
    if not creds:
        return None
    return build('drive', 'v3', credentials=creds)


def list_files(service, page_size=20, query=None):
    """List files in Drive."""
    try:
        q = query or "trashed = false"
        results = service.files().list(
            pageSize=page_size,
            q=q,
            fields="files(id, name, mimeType, modifiedTime, size)",
            orderBy="modifiedTime desc"
        ).execute()
        
        return results.get('files', [])
    except HttpError as e:
        print(f"Error listing files: {e}")
        return []


def search_files(service, query, page_size=20):
    """Search for files."""
    q = f"name contains '{query}' and trashed = false"
    return list_files(service, page_size=page_size, query=q)


def format_file(f):
    """Format a file for display."""
    name = f.get('name', 'Unknown')
    mime = f.get('mimeType', 'unknown')
    modified = f.get('modifiedTime', '')[:10]
    size = f.get('size', '?')
    
    # Get type icon
    if 'folder' in mime:
        icon = '📁'
    elif 'document' in mime:
        icon = '📄'
    elif 'spreadsheet' in mime:
        icon = '📊'
    elif 'presentation' in mime:
        icon = '📽️'
    else:
        icon = '📎'
    
    return f"{icon} {name} ({modified})"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Drive operations")
    parser.add_argument("--list", "-l", action="store_true", help="List recent files")
    parser.add_argument("--search", "-s", metavar="QUERY", help="Search files")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    service = get_drive_service()
    if not service:
        print("ERROR: Could not authenticate. Run oauth_setup.py first.")
        sys.exit(1)
    
    if args.search:
        print(f"Search results for: {args.search}\n")
        files = search_files(service, args.search, page_size=args.limit)
    else:
        print("Recent files:\n")
        files = list_files(service, page_size=args.limit)
    
    if not files:
        print("No files found.")
    else:
        for f in files:
            print(format_file(f))


if __name__ == "__main__":
    main()