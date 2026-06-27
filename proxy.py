"""
CreateMaster CORS Proxy · 本地 CORS 代理
运行方式：python proxy.py
然后在网站上填入代理地址：http://localhost:9901
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, json, ssl

TARGET = 'https://api.aicoming.top'
PORT = 9901

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors_headers()
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        target_url = TARGET + self.path
        print(f'[PROXY] POST {target_url[:60]}...')

        try:
            # Forward headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.headers.get('Authorization', '')
            }
            req = urllib.request.Request(target_url, data=body, method='POST',
                                        headers={k: v for k, v in headers.items() if v})
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                resp_body = resp.read()
                self._cors_headers()
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                self.wfile.write(resp_body)
                print(f'[PROXY] OK: {len(resp_body)} bytes')
        except urllib.error.HTTPError as e:
            self._cors_headers()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
            print(f'[PROXY] HTTP {e.code}')
        except Exception as e:
            self._cors_headers()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            err = {'error': str(e)}
            self.wfile.write(json.dumps(err).encode())
            print(f'[PROXY] Error: {e}')

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def log_message(self, format, *args):
        print(f'[PROXY] {args[0]} {args[1]}')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'════════════════════════════════════════════')
    print(f'  CreateMaster CORS Proxy 正在运行')
    print(f'  代理地址：http://localhost:{PORT}')
    print(f'  用法：打开网站 → ⚙ 代理设置 → 填入以上地址')
    print(f'  按 Ctrl+C 停止')
    print(f'════════════════════════════════════════════')
    server.serve_forever()
