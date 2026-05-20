const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const PROXY_TARGET = 'grsai.dakka.com.cn';

// 静态文件 + CORS 代理服务器
const server = http.createServer((req, res) => {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // 代理端点
  if (req.url === '/api/proxy' || req.url.startsWith('/api/proxy?')) {
    return handleProxy(req, res);
  }

  // 静态文件服务
  serveStatic(req, res);
});

function handleProxy(req, res) {
  const authHeader = req.headers['authorization'] || '';

  let targetPath = '/v1/api/generate';
  if (isGet && req.url.includes('id=')) {
    targetPath = '/v1/api/result' + req.url.substring(req.url.indexOf('?'));
  }

  const options = {
    hostname: PROXY_TARGET,
    port: 443,
    path: targetPath,
    method: req.method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': authHeader
    },
    rejectUnauthorized: false,
    timeout: 120000
  };

  const proxyReq = https.request(options, (proxyRes) => {
    let data = '';
    proxyRes.on('data', chunk => data += chunk);
    proxyRes.on('end', () => {
      console.log(`[${new Date().toLocaleTimeString()}] Proxy ${req.method} ${targetPath} → ${proxyRes.statusCode}`);
      res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json' });
      res.end(data);
    });
  });

  proxyReq.on('error', (err) => {
    console.error(`Proxy error: ${err.message}`);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: err.message, status: 'failed' }));
  });

  proxyReq.on('timeout', () => {
    proxyReq.destroy();
    res.writeHead(504, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Gateway timeout', status: 'failed' }));
  });

  if (req.method === 'POST') {
    // POST：收集完整 body 后再发送
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      proxyReq.write(body);
      proxyReq.end();
    });
  } else {
    // GET：无 body，直接发送
    proxyReq.end();
  }
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

function serveStatic(req, res) {
  let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath);

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔══════════════════════════════════════════╗
║  NanoBanana Pro · CORS 代理服务器已启动   ║
║  地址: http://localhost:${PORT}            ║
║  代理: /api/proxy → ${PROXY_TARGET}       ║
║  按 Ctrl+C 停止服务器                     ║
╚══════════════════════════════════════════╝
  `);
});
