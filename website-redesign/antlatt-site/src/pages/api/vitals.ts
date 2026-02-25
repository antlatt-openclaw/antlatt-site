// Web Vitals API Endpoint
// Receives Core Web Vitals metrics and stores them

import type { APIRoute } from 'astro';

interface WebVitalMetric {
  name: 'LCP' | 'FID' | 'CLS' | 'INP' | 'TTFB' | 'FCP';
  value: number;
  id: string;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  navigationType: string;
  page: string;
  timestamp: string;
  userAgent?: string;
}

// Rating thresholds based on Google's Core Web Vitals
const THRESHOLDS: Record<string, { good: number; poor: number }> = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  INP: { good: 200, poor: 500 },
  TTFB: { good: 800, poor: 1800 },
  FCP: { good: 1800, poor: 3000 },
};

// Simple in-memory storage (will reset on server restart)
// For persistent storage, connect to Redis or use a database
const metricsStore: Map<string, WebVitalMetric[]> = new Map();
const MAX_METRICS_PER_TYPE = 1000;

// Initialize stores
Object.keys(THRESHOLDS).forEach(name => {
  metricsStore.set(name, []);
});

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json() as WebVitalMetric;
    
    // Validate the metric
    if (!body.name || typeof body.value !== 'number' || !body.page) {
      return new Response(JSON.stringify({ error: 'Invalid metric data' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Validate metric name
    if (!THRESHOLDS[body.name]) {
      return new Response(JSON.stringify({ error: 'Unknown metric type' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Enrich the metric
    const metric: WebVitalMetric = {
      ...body,
      timestamp: body.timestamp || new Date().toISOString(),
      userAgent: request.headers.get('user-agent')?.slice(0, 200) || undefined,
    };
    
    // Store in memory
    const metrics = metricsStore.get(metric.name) || [];
    metrics.unshift(metric);
    
    // Keep only the most recent metrics
    if (metrics.length > MAX_METRICS_PER_TYPE) {
      metrics.length = MAX_METRICS_PER_TYPE;
    }
    metricsStore.set(metric.name, metrics);
    
    // Try to log to Redis if available (non-blocking)
    tryLogToRedis(metric);
    
    return new Response(JSON.stringify({ 
      success: true, 
      metric: {
        name: metric.name,
        value: metric.value,
        rating: metric.rating
      }
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Web vitals API error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// GET endpoint to retrieve metrics for the admin dashboard
export const GET: APIRoute = async ({ url }) => {
  const metricName = url.searchParams.get('metric');
  const since = url.searchParams.get('since'); // ISO timestamp
  
  try {
    const results: any = {
      timestamp: new Date().toISOString(),
      metrics: {}
    };
    
    const metricTypes = metricName && THRESHOLDS[metricName] 
      ? [metricName] 
      : Object.keys(THRESHOLDS);
    
    for (const name of metricTypes) {
      let metrics = metricsStore.get(name) || [];
      
      // Filter by timestamp if provided
      if (since) {
        const sinceDate = new Date(since);
        metrics = metrics.filter(m => new Date(m.timestamp) > sinceDate);
      }
      
      // Calculate statistics
      if (metrics.length > 0) {
        const values = metrics.map(m => m.value);
        const sum = values.reduce((a, b) => a + b, 0);
        const avg = sum / values.length;
        const sorted = [...values].sort((a, b) => a - b);
        const p50 = sorted[Math.floor(sorted.length * 0.5)];
        const p75 = sorted[Math.floor(sorted.length * 0.75)];
        const p95 = sorted[Math.floor(sorted.length * 0.95)];
        
        const thresholds = THRESHOLDS[name];
        const goodCount = values.filter(v => v <= thresholds.good).length;
        const poorCount = values.filter(v => v > thresholds.poor).length;
        
        results.metrics[name] = {
          count: metrics.length,
          average: Math.round(avg * 100) / 100,
          p50: Math.round(p50 * 100) / 100,
          p75: Math.round(p75 * 100) / 100,
          p95: Math.round(p95 * 100) / 100,
          goodPercentage: Math.round((goodCount / metrics.length) * 100),
          poorPercentage: Math.round((poorCount / metrics.length) * 100),
          thresholds,
          recent: metrics.slice(0, 50).map(m => ({
            value: m.value,
            rating: m.rating,
            page: m.page,
            timestamp: m.timestamp
          }))
        };
      } else {
        results.metrics[name] = {
          count: 0,
          average: null,
          recent: []
        };
      }
    }
    
    return new Response(JSON.stringify(results), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, max-age=0'
      }
    });
    
  } catch (error) {
    console.error('Failed to retrieve metrics:', error);
    return new Response(JSON.stringify({ error: 'Failed to retrieve metrics' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// Attempt to log to Redis (non-blocking, silent failure)
async function tryLogToRedis(metric: WebVitalMetric): Promise<void> {
  // This is a placeholder for Redis logging
  // When running on a server with Redis access, you can implement this
  // For now, metrics are stored in memory and will persist until server restart
  // 
  // Example Redis implementation:
  // const redis = new Redis('redis://192.168.1.206:6379');
  // await redis.lpush(`webvitals:${metric.name}`, JSON.stringify(metric));
  // await redis.ltrim(`webvitals:${metric.name}`, 0, 999);
  
  // Alternative: Write to a JSON file for persistence
  // This works in most Astro deployment scenarios
  const fs = await import('fs/promises');
  const path = await import('path');
  
  try {
    const dataDir = path.join(process.cwd(), 'data');
    const filePath = path.join(dataDir, `webvitals-${metric.name}.json`);
    
    // Ensure data directory exists
    try {
      await fs.mkdir(dataDir, { recursive: true });
    } catch {}
    
    // Read existing data
    let existing: WebVitalMetric[] = [];
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      existing = JSON.parse(content);
    } catch {}
    
    // Add new metric and keep last 1000
    existing.unshift(metric);
    if (existing.length > 1000) {
      existing = existing.slice(0, 1000);
    }
    
    // Write back
    await fs.writeFile(filePath, JSON.stringify(existing, null, 2));
  } catch (err) {
    // Silent failure - in-memory storage is still available
    console.debug('Could not persist metric to file:', err);
  }
}