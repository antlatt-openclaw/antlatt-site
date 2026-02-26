// Infrastructure Status API Endpoint
// Returns real-time status of homelab services

import type { APIRoute } from 'astro';

interface ServiceStatus {
  name: string;
  description: string;
  status: 'online' | 'offline' | 'unknown';
  responseTime?: number;
  details?: string;
  error?: string;
}

const SERVICES = [
  { 
    name: 'Qdrant', 
    host: '192.168.1.202', 
    port: 6333,
    path: '/healthz',
    description: 'Vector Database'
  },
  { 
    name: 'Redis', 
    host: '192.168.1.206', 
    port: 6379,
    description: 'Cache & Memory Buffer'
  },
  { 
    name: 'Ollama', 
    host: '192.168.1.207', 
    port: 11434,
    path: '/api/tags',
    description: 'LLM Inference'
  },
  { 
    name: 'Website', 
    host: 'localhost', 
    port: 4321,
    path: '/',
    description: 'This Site'
  }
];

async function checkService(service: typeof SERVICES[0]): Promise<ServiceStatus> {
  const startTime = Date.now();
  
  try {
    const url = `http://${service.host}:${service.port}${service.path || '/'}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(url, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      }
    });
    
    clearTimeout(timeoutId);
    const responseTime = Date.now() - startTime;
    
    if (response.ok) {
      return {
        name: service.name,
        description: service.description,
        status: 'online',
        responseTime
      };
    } else {
      return {
        name: service.name,
        description: service.description,
        status: 'offline',
        responseTime,
        details: `HTTP ${response.status}`
      };
    }
  } catch (error) {
    const responseTime = Date.now() - startTime;
    return {
      name: service.name,
      description: service.description,
      status: 'offline',
      responseTime,
      error: error instanceof Error ? error.message : 'Connection failed'
    };
  }
}

export const GET: APIRoute = async () => {
  try {
    // Check all services concurrently
    const serviceResults = await Promise.all(
      SERVICES.map(service => checkService(service))
    );
    
    // Calculate summary
    const onlineCount = serviceResults.filter(s => s.status === 'online').length;
    const totalCount = serviceResults.length;
    
    let summaryStatus: 'all-systems-go' | 'partial' | 'major-outage';
    if (onlineCount === totalCount) {
      summaryStatus = 'all-systems-go';
    } else if (onlineCount === 0) {
      summaryStatus = 'major-outage';
    } else {
      summaryStatus = 'partial';
    }
    
    const response = {
      timestamp: new Date().toISOString(),
      services: serviceResults,
      summary: {
        status: summaryStatus,
        online: onlineCount,
        total: totalCount,
        uptime: 99.9 // Placeholder - would need historical data
      }
    };
    
    return new Response(JSON.stringify(response), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, max-age=0'
      }
    });
    
  } catch (error) {
    console.error('Status API error:', error);
    
    return new Response(JSON.stringify({
      timestamp: new Date().toISOString(),
      services: SERVICES.map(s => ({
        name: s.name,
        description: s.description,
        status: 'unknown' as const,
        error: 'API error'
      })),
      summary: {
        status: 'major-outage' as const,
        online: 0,
        total: SERVICES.length,
        uptime: 0
      }
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, max-age=0'
      }
    });
  }
};