# Status API

A lightweight service that checks the health of antlatt.com infrastructure and exposes a JSON API for the Lab status page.

## Endpoints

- `GET /api/status` - Returns JSON with all service statuses
- `GET /api/status/live` - Simple health check

## Running

### Docker (recommended)

```bash
docker build -t status-api .
docker run -d --name status-api \
  -p 3001:3001 \
  -e QDRANT_URL=http://192.168.1.202:6333/collections \
  -e REDIS_HOST=192.168.1.206 \
  -e REDIS_PORT=6379 \
  -e OLLAMA_URL=http://192.168.1.207:11434/api/tags \
  status-api
```

### With docker-compose

```bash
docker-compose up -d
```

### Direct (development)

```bash
npm install
npm start
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3001 | API server port |
| `QDRANT_URL` | http://192.168.1.202:6333/collections | Qdrant health check endpoint |
| `REDIS_HOST` | 192.168.1.206 | Redis server host |
| `REDIS_PORT` | 6379 | Redis server port |
| `OLLAMA_URL` | http://192.168.1.207:11434/api/tags | Ollama health check endpoint |
| `WEBSITE_URL` | http://localhost:8080/ | Website health check URL |

## Integration with nginx

Add the contents of `nginx-proxy.conf` to your nginx server block to proxy `/api/` requests to this service.

## Response Format

```json
{
  "timestamp": "2024-02-24T14:44:00.000Z",
  "services": [
    {
      "name": "Qdrant",
      "description": "Vector Database",
      "status": "online",
      "responseTime": 15
    },
    {
      "name": "Redis",
      "description": "Cache & Memory Buffer",
      "status": "online",
      "responseTime": 3
    },
    {
      "name": "Ollama",
      "description": "LLM Inference",
      "status": "online",
      "responseTime": 8
    },
    {
      "name": "Website",
      "description": "This Site",
      "status": "online",
      "responseTime": 2
    }
  ],
  "summary": {
    "total": 4,
    "online": 4,
    "offline": 0,
    "status": "all-systems-go"
  }
}
```