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
            sale_id = request_data.get("sale_id")
            cost_ids = request_data.get("cost_ids", [])

            response = {
                "success": True,
                "session_id": session_id,
                "message": f"Associação criada: venda {sale_id} com {len(cost_ids)} custos",
                "association": {
                    "sale_id": sale_id,
                    "cost_ids": cost_ids,
                    "timestamp": "2025-01-19T23:36:00Z"
                }
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro ao criar associação: {str(e)}"
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()