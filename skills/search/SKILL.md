# SearXNG Search

Privacy-respecting metasearch engine running locally via Docker.

## Usage

```bash
python3 skills/search/scripts/searx.py "your search query"
```

## Features

- Aggregates results from Google, Bing, DuckDuckGo, and more
- JSON API for easy integration
- No tracking, no logging
- Running on localhost:8888

## Endpoints

- Web UI: http://localhost:8888
- API: http://localhost:8888/search?q=query&format=json

## Docker Management

```bash
docker start searxng    # Start
docker stop searxng     # Stop  
docker logs searxng     # View logs
```