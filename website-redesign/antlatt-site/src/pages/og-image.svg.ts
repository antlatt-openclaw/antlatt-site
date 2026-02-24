// Default OG Image for the site
// Returns a simple SVG as OG image
import type { APIRoute } from 'astro';

const width = 1200;
const height = 630;

export const GET: APIRoute = async () => {
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
  
  <!-- Accent line -->
  <rect x="60" y="240" width="200" height="4" fill="url(#accent)" rx="2"/>
  
  <!-- Title -->
  <text x="60" y="320" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="800" fill="#e5e5e5">
    ANTLATT
  </text>
  <text x="60" y="400" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="800" fill="url(#accent)">
    .COM
  </text>
  
  <!-- Tagline -->
  <text x="60" y="480" font-family="Inter, system-ui, sans-serif" font-size="28" fill="#8888a0">
    Tech stuff, general geekery, and whatever else catches my attention.
  </text>
  
  <!-- Decorative elements -->
  <circle cx="1000" cy="200" r="80" fill="#6366f1" opacity="0.1"/>
  <circle cx="1050" cy="450" r="120" fill="#22d3ee" opacity="0.05"/>
</svg>
`;

  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'public, max-age=31536000, immutable'
    }
  });
};