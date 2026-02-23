#!/bin/bash
# vercel-wrapper.sh - Run vercel with token from .env
TOKEN=$(grep VERCEL_TOKEN /root/.openclaw/antlatt-workspace/.env | cut -d'=' -f2)
vercel --token "$TOKEN" "$@"