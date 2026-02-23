# Deploy Skills

CLI tools for deploying projects to GitHub and Vercel.

## Vercel

```bash
# Deploy current directory
vercel --token $VERCEL_TOKEN

# Deploy to production
vercel --token $VERCEL_TOKEN --prod

# List deployments
vercel --token $VERCEL_TOKEN list

# View project info
vercel --token $VERCEL_TOKEN inspect <url>
```

## GitHub CLI

```bash
# Authenticate (one-time)
gh auth login

# Create repo
gh repo create <name> --private

# Push
gh repo push

# Create PR
gh pr create --title "Title" --body "Description"
```

## Environment

Credentials stored in `.env`:
- `VERCEL_TOKEN` — Vercel API token
- `GITHUB_TOKEN` — GitHub personal access token (via gh auth)