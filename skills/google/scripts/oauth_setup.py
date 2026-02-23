#!/usr/bin/env python3
"""
oauth_setup.py - One-time OAuth setup for Google Workspace APIs
Run this once to authorize access and get a refresh token.
"""

import os
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Load env
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: Missing Google libraries")
    print("Run: pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# All scopes we need
SCOPES = [
    # Gmail
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    # Calendar
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    # Drive
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
]

TOKEN_PATH = Path("/root/.openclaw/antlatt-workspace/.google_token.json")


def get_client_config():
    """Get OAuth client configuration from environment."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("ERROR: Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env")
        sys.exit(1)
    
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }


def save_token(creds):
    """Save credentials to token file."""
    TOKEN_PATH.write_text(creds.to_json())
    TOKEN_PATH.chmod(0o600)
    print(f"✓ Token saved to {TOKEN_PATH}")


def save_refresh_token(refresh_token):
    """Save refresh token to .env file."""
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().strip().split('\n')
    
    found = False
    for i, line in enumerate(lines):
        if line.startswith('GOOGLE_REFRESH_TOKEN='):
            lines[i] = f'GOOGLE_REFRESH_TOKEN={refresh_token}'
            found = True
            break
    
    if not found:
        lines.append(f'GOOGLE_REFRESH_TOKEN={refresh_token}')
    
    ENV_PATH.write_text('\n'.join(lines) + '\n')
    print(f"✓ Refresh token saved to {ENV_PATH}")


def main():
    print("=" * 60)
    print("Google Workspace OAuth Setup")
    print("=" * 60)
    print(f"\nAccount: {os.environ.get('GOOGLE_EMAIL', 'unknown')}")
    print(f"\nScopes to authorize:")
    for scope in SCOPES:
        print(f"  • {scope.split('/')[-1]}")
    print()
    
    client_config = get_client_config()
    
    # Check for existing token
    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            print("Found existing token file.")
        except Exception as e:
            print(f"Token file invalid: {e}")
            creds = None
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        try:
            creds.refresh(Request())
            save_token(creds)
            print("✓ Token refreshed!")
            return
        except Exception as e:
            print(f"Refresh failed: {e}")
            creds = None
    
    # Need new auth
    if not creds or not creds.valid:
        print("\nStarting OAuth flow...")
        print("A browser window will open for you to authorize access.\n")
        
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
        
        save_token(creds)
        save_refresh_token(creds.refresh_token)
        
        print("\n" + "=" * 60)
        print("✓ OAuth setup complete!")
        print("=" * 60)
        print("\nYou can now use Google Workspace features:")
        print("  • Gmail: send, read, search emails")
        print("  • Calendar: view and create events")
        print("  • Drive: list and search files")


if __name__ == "__main__":
    main()