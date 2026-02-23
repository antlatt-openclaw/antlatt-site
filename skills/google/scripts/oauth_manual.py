#!/usr/bin/env python3
"""
oauth_manual.py - Manual OAuth setup for headless servers
Run this, open the URL in your browser, then paste the code.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

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
    sys.exit(1)

# All scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
]

TOKEN_PATH = Path("/root/.openclaw/antlatt-workspace/.google_token.json")


def get_client_config():
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }


def save_token(creds):
    TOKEN_PATH.write_text(creds.to_json())
    TOKEN_PATH.chmod(0o600)
    print(f"✓ Token saved to {TOKEN_PATH}")


def save_refresh_token(refresh_token):
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
    print("Google Workspace OAuth Setup (Manual Flow)")
    print("=" * 60)
    print(f"\nAccount: {os.environ.get('GOOGLE_EMAIL', 'unknown')}")
    
    client_config = get_client_config()
    
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n" + "=" * 60)
    print("STEP 1: Open this URL in your browser:")
    print("=" * 60)
    print(f"\n{auth_url}\n")
    print("=" * 60)
    print("STEP 2: Authorize the app, then paste the authorization code below:")
    print("=" * 60)
    
    auth_code = input("\nEnter code: ").strip()
    
    print("\nExchanging code for tokens...")
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        save_token(creds)
        save_refresh_token(creds.refresh_token)
        
        print("\n" + "=" * 60)
        print("✓ OAuth setup complete!")
        print("=" * 60)
        print("\nYou can now use:")
        print("  • Gmail: python3 skills/google/scripts/gmail.py --recent 5")
        print("  • Calendar: python3 skills/google/scripts/gcal.py --today")
        print("  • Drive: python3 skills/google/scripts/drive.py --list")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()