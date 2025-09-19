from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "message": "Test endpoint working!",
            "status": "ok",
            "path": self.path
        }

        self.wfile.write(json.dumps(response).encode('utf-8'))