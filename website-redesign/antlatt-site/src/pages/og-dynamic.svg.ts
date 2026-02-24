// Dynamic OG Image for individual articles
import type { APIRoute } from 'astro';

const width = 1200;
const height = 630;

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const title = url.searchParams.get('title') || 'ANTLATT.COM';
  const description = url.searchParams.get('description') || '';
  
  // Truncate description if too long
  const maxDescLength = 100;
  const truncatedDesc = description.length > maxDescLength 
    ? description.slice(0, maxDescLength) + '...' 
    : description;

  const svg = `
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a0f"/>
      <stop offset="100%" style="stop-color:#12121a"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#6366f1"/>
      <stop offset="100%" style="stop-color:#22d3ee"/>
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="url(#bg)"/>
  
  <!-- Grid pattern -->
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#2a2a3a" stroke-width="0.5"/>
  </pattern>
  <rect width="100%" height="100%" fill="url(#grid)" opacity="0.5"/>
  
  <!-- Top accent bar -->
  <rect x="0" y="0" width="100%" height="4" fill="url(#accent)"/>
  
  <!-- Title -->
  <text x="60" y="300" font-family="Inter, system-ui, sans-serif" font-size="56" font-weight="800" fill="#e5e5e5">
    ${escapeXml(title).slice(0, 50)}
  </text>
  
  <!-- Description -->
  ${truncatedDesc ? `
  <text x="60" y="380" font-family="Inter, system-ui, sans-serif" font-size="24" fill="#8888a0">
    ${escapeXml(truncatedDesc).slice(0, 60)}
  </text>
  ` : ''}
  
  <!-- Site name -->
  <text x="60" y="570" font-family="Inter, system-ui, sans-serif" font-size="20" fill="#6366f1" font-weight="600">
    ANTLATT.COM
  </text>
  
  <!-- Decorative elements -->
  <circle cx="1100" cy="500" r="150" fill="#6366f1" opacity="0.05"/>
</svg>
`;

  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'public, max-age=3600'
    }
  });
};