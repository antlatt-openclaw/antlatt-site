#!/usr/bin/env python3
"""
google_auth.py - Shared authentication module for Google Workspace APIs
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Load environment
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")

def load_env():
    """Load environment variables from .env file."""
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

load_env()

# Try to import Google libs
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False
    print("WARNING: Google libs not installed. Run: pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# OAuth scopes
SCOPES = {
    'gmail': [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ],
    'calendar': [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ],
    'drive': [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
}

# Token storage
TOKEN_PATH = Path("/root/.openclaw/antlatt-workspace/.google_token.json")


def get_client_config():
    """Get OAuth client configuration."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
        return None
    
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }


def get_credentials(scopes=None):
    """Get valid Google OAuth credentials."""
    if not HAS_GOOGLE_LIBS:
        return None
    
    all_scopes = scopes or SCOPES['gmail'] + SCOPES['calendar'] + SCOPES['drive']
    
    creds = None
    
    # Try to load existing token
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), all_scopes)
        except Exception as e:
            print(f"Token load error: {e}")
            creds = None
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
        except Exception as e:
            print(f"Token refresh error: {e}")
            creds = None
    
    # If no valid creds, need to auth
    if not creds or not creds.valid:
        print("No valid credentials. Run: python3 skills/google/scripts/oauth_setup.py")
        return None
    
    return creds


def _save_token(creds):
    """Save credentials to token file."""
    TOKEN_PATH.write_text(creds.to_json())
    TOKEN_PATH.chmod(0o600)


def save_refresh_token(refresh_token):
    """Save refresh token to .env file."""
    # Read existing env
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().strip().split('\n')
    
    # Update or add refresh token
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


def create_credentials_from_refresh(refresh_token=None, scopes=None):
    """Create credentials from refresh token."""
    if not refresh_token:
        refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    
    if not refresh_token:
        return None
    
    client_config = get_client_config()
    if not client_config:
        return None
    
    all_scopes = scopes or SCOPES['gmail'] + SCOPES['calendar'] + SCOPES['drive']
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=client_config['installed']['token_uri'],
        client_id=client_config['installed']['client_id'],
        client_secret=client_config['installed']['client_secret'],
        scopes=all_scopes
    )
    
    # Refresh to get valid token
    creds.refresh(Request())
    
    return creds


if __name__ == "__main__":
    # Quick credential check
    creds = get_credentials()
    if creds:
        print("✓ Credentials valid")
        print(f"  Scopes: {len(creds.scopes)}")
    else:
        print("✗ Need to run OAuth setup")