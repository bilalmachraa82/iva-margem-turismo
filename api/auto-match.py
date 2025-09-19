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
            threshold = request_data.get("threshold", 60)

            # Mock auto-match results
            associations = [
                {
                    "sale_id": "s1",
                    "cost_ids": ["c1", "c2"],
                    "confidence": 85,
                    "reasoning": "Data próxima e correlação de valores"
                },
                {
                    "sale_id": "s2",
                    "cost_ids": ["c3"],
                    "confidence": 72,
                    "reasoning": "Cliente/fornecedor similar"
                }
            ]

            response = {
                "success": True,
                "session_id": session_id,
                "threshold": threshold,
                "associations": associations,
                "stats": {
                    "total_matches": len(associations),
                    "high_confidence": len([a for a in associations if a["confidence"] >= 80]),
                    "medium_confidence": len([a for a in associations if 60 <= a["confidence"] < 80]),
                    "low_confidence": len([a for a in associations if a["confidence"] < 60])
                }
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro no auto-match: {str(e)}"
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()