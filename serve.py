# The mirrored site on this computer: python serve.py [port]
# /en and / give the page; /api/* answers with an empty result so the page carries on without the server behind it.
import http.server, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8798
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def do_GET(self):
        path = self.path.split('?')[0].split('#')[0]
        if path in ('/', '/en', '/en/', '/fr', '/fr/'):
            self.path = '/en.html'
        elif path.startswith('/api/'):
            body = json.dumps({'ok': True, 'slots': [], 'days': []}).encode()
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()
    def do_POST(self):
        body = b'{"ok":true}'
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 256      # the page asks for about a hundred files at once when it starts
Server(('127.0.0.1', PORT), H).serve_forever()
