const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const MIME = { '.html':'text/html; charset=utf-8', '.css':'text/css', '.js':'application/javascript' };

http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  let fp = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
  fs.readFile(fp, (e, d) => {
    if (e) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
    res.end(d);
  });
}).listen(PORT, () => console.log(`Server: http://localhost:${PORT}`));
