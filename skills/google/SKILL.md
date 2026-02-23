# Google Workspace Integration

Gmail, Calendar, and Drive integration for your dedicated account.

## Setup

Credentials are stored in `.env`. First-time setup requires OAuth consent:

```bash
python3 skills/google/scripts/oauth_setup.py
```

This will:
1. Open a browser for Google login
2. Ask for consent
3. Save the refresh token to `.env`

## Capabilities

### Gmail
- `email` — Check recent emails
- `email sent` — View sent messages
- `email to: user@domain.com "subject" "body"` — Send email
- `email search: query` — Search emails

### Calendar
- `calendar` — Show today's events
- `calendar tomorrow` — Show tomorrow's events
- `calendar week` — Show week view

### Drive
- `drive list` — List files
- `drive search: query` — Search Drive

## Environment Variables

Set in `.env`:
- `GOOGLE_CLIENT_ID` — OAuth client ID
- `GOOGLE_CLIENT_SECRET` — OAuth client secret
- `GOOGLE_EMAIL` — Account email
- `GOOGLE_REFRESH_TOKEN` — Obtained via OAuth flow