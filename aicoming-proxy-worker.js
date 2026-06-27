// CORS Proxy for aicoming.top API
// Deploy to Cloudflare Workers (free tier: 100k req/day)

const TARGET = 'https://api.aicoming.top';

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname + url.search;

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          'Access-Control-Max-Age': '86400',
        }
      });
    }

    // Forward request to aicoming
    const targetUrl = TARGET + path;
    const headers = new Headers(request.headers);
    headers.delete('Origin');

    const resp = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' ? request.body : undefined,
    });

    // Add CORS headers to response
    const corsHeaders = new Headers(resp.headers);
    corsHeaders.set('Access-Control-Allow-Origin', '*');
    corsHeaders.set('Access-Control-Expose-Headers', '*');

    return new Response(resp.body, {
      status: resp.status,
      statusText: resp.statusText,
      headers: corsHeaders,
    });
  }
};
