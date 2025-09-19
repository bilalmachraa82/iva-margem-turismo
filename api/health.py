from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "uptime": "100%",
            "version": "1.0.0",
            "endpoints": {
                "GET": ["/api/", "/api/health", "/api/mock-data", "/api/test"],
                "POST": ["/api/calculate"]
            },
            "timestamp": "2025-01-19T23:36:00Z"
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))