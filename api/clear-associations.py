from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}

            session_id = request_data.get("session_id", "demo-session-123")

            response = {
                "success": True,
                "session_id": session_id,
                "message": "Associações removidas com sucesso",
                "cleared_count": 5
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro ao limpar associações: {str(e)}"
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()