/**
 * Status API Server
 * 
 * Tiny Express server that checks infrastructure health and exposes /api/status
 * Runs on port 3001 (configurable via PORT env var)
 * 
 * Endpoints:
 *   GET /api/status      - JSON with all service statuses
 *   GET /api/status/live - Simple health check for the API itself
 */

import express from 'express';
import net from 'net';

const app = express();
const PORT = process.env.PORT || 3001;

// Service configuration - use environment variables or defaults
const SERVICES = {
  qdrant: {
    name: 'Qdrant',
    description: 'Vector Database',
    url: process.env.QDRANT_URL || 'http://192.168.1.202:6333/collections',
    timeout: 5000
  },
  redis: {
    name: 'Redis',
    description: 'Cache & Memory Buffer',
    host: process.env.REDIS_HOST || '192.168.1.206',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    timeout: 5000
  },
  ollama: {
    name: 'Ollama',
    description: 'LLM Inference',
    url: process.env.OLLAMA_URL || 'http://192.168.1.207:11434/api/tags',
    timeout: 5000
  },
  website: {
    name: 'Website',
    description: 'This Site',
    url: process.env.WEBSITE_URL || 'http://localhost:8080/',
    timeout: 5000
  }
};

/**
 * Check a generic HTTP service
 */
async function checkHttpService(name, description, url, timeoutMs) {
  const start = Date.now();
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    
    const response = await fetch(url, {
      method: 'GET',
      signal: controller.signal
    });
    clearTimeout(timeout);
    
    return {
      name,
      description,
      status: response.ok || response.status === 401 ? 'online' : 'offline',
      responseTime: Date.now() - start,
      details: response.status === 401 ? 'Auth required (service up)' : undefined
    };
  } catch (error) {
    return {
      name,
      description,
      status: 'offline',
      responseTime: Date.now() - start,
      error: error.name === 'AbortError' ? 'Timeout' : error.message
    };
  }
}

/**
 * Check Redis directly via TCP connection
 * Redis doesn't speak HTTP, so we use a raw socket
 */
async function checkRedis(name, description, host, port, timeoutMs) {
  const start = Date.now();
  
  return new Promise((resolve) => {
    const socket = new net.Socket();
    const timeout = setTimeout(() => {
      socket.destroy();
      resolve({
        name,
        description,
        status: 'offline',
        responseTime: Date.now() - start,
        error: 'Timeout'
      });
    }, timeoutMs);
    
    socket.connect(port, host, () => {
      clearTimeout(timeout);
      // Send PING command
      socket.write('*1\r\n$4\r\nPING\r\n');
    });
    
    socket.on('data', (data) => {
      clearTimeout(timeout);
      const response = data.toString();
      socket.destroy();
      resolve({
        name,
        description,
        status: response.includes('+PONG') || response.includes('NOAUTH') ? 'online' : 'offline',
        responseTime: Date.now() - start,
        details: response.includes('NOAUTH') ? 'Auth required (service up)' : undefined
      });
    });
    
    socket.on('error', (error) => {
      clearTimeout(timeout);
      resolve({
        name,
        description,
        status: 'offline',
        responseTime: Date.now() - start,
        error: error.message
      });
    });
  });
}

/**
 * Main status check - runs all service checks in parallel
 */
async function checkAllServices() {
  const [qdrant, ollama, website, redis] = await Promise.all([
    checkHttpService(
      SERVICES.qdrant.name,
      SERVICES.qdrant.description,
      SERVICES.qdrant.url,
      SERVICES.qdrant.timeout
    ),
    checkHttpService(
      SERVICES.ollama.name,
      SERVICES.ollama.description,
      SERVICES.ollama.url,
      SERVICES.ollama.timeout
    ),
    checkHttpService(
      SERVICES.website.name,
      SERVICES.website.description,
      SERVICES.website.url,
      SERVICES.website.timeout
    ),
    checkRedis(
      SERVICES.redis.name,
      SERVICES.redis.description,
      SERVICES.redis.host,
      SERVICES.redis.port,
      SERVICES.redis.timeout
    )
  ]);
  
  return [qdrant, redis, ollama, website];
}

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Health check endpoint
app.get('/api/status/live', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Main status endpoint
app.get('/api/status', async (req, res) => {
  try {
    const services = await checkAllServices();
    const onlineCount = services.filter(s => s.status === 'online').length;
    
    res.json({
      timestamp: new Date().toISOString(),
      services,
      summary: {
        total: services.length,
        online: onlineCount,
        offline: services.length - onlineCount,
        status: onlineCount === services.length ? 'all-systems-go' :
                onlineCount > 0 ? 'partial' : 'major-outage'
      }
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to check services',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Status API running on port ${PORT}`);
  console.log(`  GET http://localhost:${PORT}/api/status`);
  console.log(`  GET http://localhost:${PORT}/api/status/live`);
  console.log('\nService endpoints:');
  console.log(`  Qdrant: ${SERVICES.qdrant.url}`);
  console.log(`  Redis:  ${SERVICES.redis.host}:${SERVICES.redis.port}`);
  console.log(`  Ollama: ${SERVICES.ollama.url}`);
  console.log(`  Website: ${SERVICES.website.url}`);
});