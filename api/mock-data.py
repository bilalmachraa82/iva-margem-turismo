from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "session_id": "demo-session-123",
            "sales": [
                {"id": "s1", "number": "FT 2025/001", "amount": 1250.0, "client": "Hotel Tivoli", "date": "2025-01-15"},
                {"id": "s2", "number": "FT 2025/002", "amount": 890.0, "client": "Restaurante Central", "date": "2025-01-16"},
                {"id": "s3", "number": "FT 2025/003", "amount": 2100.0, "client": "TAP Corporate", "date": "2025-01-18"},
                {"id": "s4", "number": "FT 2025/004", "amount": 1450.0, "client": "Turismo de Lisboa", "date": "2025-01-20"},
                {"id": "s5", "number": "FT 2025/005", "amount": 780.0, "client": "Hotel Ritz", "date": "2025-01-22"}
            ],
            "costs": [
                {"id": "c1", "supplier": "TAP Air Portugal", "amount": 800.0, "date": "2025-01-15"},
                {"id": "c2", "supplier": "Hotel Partner", "amount": 450.0, "date": "2025-01-16"},
                {"id": "c3", "supplier": "Rent-a-Car", "amount": 320.0, "date": "2025-01-17"},
                {"id": "c4", "supplier": "Tour Operator", "amount": 1200.0, "date": "2025-01-18"},
                {"id": "c5", "supplier": "Restaurant Booking", "amount": 180.0, "date": "2025-01-19"},
                {"id": "c6", "supplier": "Transfer Service", "amount": 95.0, "date": "2025-01-20"}
            ],
            "associations": [],
            "metadata": {
                "total_sales": 6470.0,
                "total_costs": 3045.0,
                "potential_margin": 3425.0,
                "status": "ready"
            }
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))