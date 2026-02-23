#!/usr/bin/env python3
"""
searx.py - Search using local SearXNG instance
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests

# Load env
ENV_PATH = Path("/root/.openclaw/antlatt-workspace/.env")
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8888")


def search(query: str, engines: list = None, categories: list = None, 
           pageno: int = 1, time_range: str = None, safesearch: int = 0):
    """Perform a search via SearXNG API."""
    
    params = {
        "q": query,
        "format": "json",
        "pageno": pageno,
        "safesearch": safesearch
    }
    
    if engines:
        params["engines"] = ",".join(engines)
    
    if categories:
        params["categories"] = ",".join(categories)
    
    if time_range:
        params["time_range"] = time_range  # day, week, month, year
    
    url = f"{SEARXNG_URL}/search?{urlencode(params)}"
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Search error: {e}")
        return None


def format_results(data: dict, max_results: int = 10) -> str:
    """Format search results for display."""
    
    if not data:
        return "No results or search failed."
    
    results = data.get("results", [])[:max_results]
    
    if not results:
        return "No results found."
    
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")[:150]
        engine = r.get("engine", "unknown")
        
        lines.append(f"{i}. {title}")
        lines.append(f"   {url}")
        if snippet:
            lines.append(f"   {snippet}...")
        lines.append(f"   [{engine}]")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search via SearXNG")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--engines", "-e", help="Comma-separated engines (google,bing,ddg)")
    parser.add_argument("--category", "-c", help="Category (general,images,news)")
    parser.add_argument("--time", "-t", help="Time range (day,week,month,year)")
    parser.add_argument("--results", "-n", type=int, default=10, help="Number of results")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    parser.add_argument("--urls", "-u", action="store_true", help="Only show URLs")
    
    args = parser.parse_args()
    
    engines = args.engines.split(",") if args.engines else None
    categories = [args.category] if args.category else None
    
    data = search(
        query=args.query,
        engines=engines,
        categories=categories,
        time_range=args.time
    )
    
    if args.json:
        print(json.dumps(data, indent=2))
    elif args.urls:
        if data:
            for r in data.get("results", [])[:args.results]:
                print(r.get("url", ""))
    else:
        print(f"Searching: {args.query}\n")
        print(format_results(data, args.results))


if __name__ == "__main__":
    main()