"""
NanoBananaPro CORS 代理服务器
同时提供：
1. 静态文件服务（托管 index.html）
2. /api/proxy 代理端点（转发到 grsai.dakka.com.cn，解决跨域问题）
"""
import http.server
import urllib.request
import urllib.error
import json
import os
import sys

PROXY_TARGET = "https://grsai.dakka.com.cn"
PORT = 8080

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/proxy':
            self.handle_proxy()
        else:
            super().do_POST()

    def do_GET(self):
        if self.path.startswith('/api/proxy?'):
            self.handle_proxy_get()
        else:
            super().do_GET()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')

    def handle_proxy(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        # 读取原始请求的 Authorization 头
        auth_header = self.headers.get('Authorization', '')

        target_url = PROXY_TARGET + '/v1/api/generate'

        req = urllib.request.Request(
            target_url,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
            },
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                response_data = resp.read()
                self.send_response(resp.status)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e), 'status': 'failed'}).encode())

    def handle_proxy_get(self):
        import urllib.parse
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        task_id = query_params.get('id', [None])[0]
        auth_header = self.headers.get('Authorization', '')

        target_url = PROXY_TARGET + '/v1/api/result'
        if task_id:
            target_url += '?id=' + urllib.parse.quote(task_id)

        req = urllib.request.Request(
            target_url,
            headers={'Authorization': auth_header},
            method='GET'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_data = resp.read()
                self.send_response(resp.status)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e), 'status': 'failed'}).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

if __name__ == '__main__':
    # 切换到脚本所在目录（即 index.html 所在目录）
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f"""
╔══════════════════════════════════════════╗
║  NanoBanana Pro · CORS 代理服务器已启动   ║
║  地址: http://localhost:{PORT}            ║
║  代理: /api/proxy → grsai.dakka.com.cn   ║
║  按 Ctrl+C 停止服务器                     ║
╚══════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止。")
        server.server_close()
