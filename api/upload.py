from http.server import BaseHTTPRequestHandler
import json
import uuid

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

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Mock SAF-T processing response
            response = {
                "success": True,
                "session_id": session_id,
                "message": "Ficheiro SAF-T processado com sucesso",
                "summary": {
                    "sales_count": 26,
                    "costs_count": 157,
                    "total_sales": 24575.50,
                    "total_costs": 18945.25,
                    "potential_margin": 5630.25
                },
                "data": {
                    "sales": [
                        {"id": "s1", "number": "FT 2025/001", "amount": 1250.0, "client": "Hotel Tivoli", "date": "2025-01-15"},
                        {"id": "s2", "number": "FT 2025/002", "amount": 890.0, "client": "Restaurante Central", "date": "2025-01-16"}
                    ],
                    "costs": [
                        {"id": "c1", "supplier": "TAP Air Portugal", "amount": 800.0, "date": "2025-01-15"},
                        {"id": "c2", "supplier": "Hotel Partner", "amount": 450.0, "date": "2025-01-16"}
                    ],
                    "associations": []
                }
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro ao processar ficheiro SAF-T: {str(e)}",
                "session_id": None
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()