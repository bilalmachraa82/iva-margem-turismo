from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        path = self.path

        if path == '/api/' or path == '/api' or path == '/':
            response = {
                "message": "IVA Margem Turismo API está online!",
                "status": "success",
                "version": "1.0.0",
                "endpoints": [
                    "GET /api/mock-data",
                    "GET /api/health"
                ]
            }
        elif path == '/api/mock-data':
            response = {
                "session_id": "demo-session-123",
                "sales": [
                    {"id": "s1", "number": "FT 2025/001", "amount": 1250.0, "client": "Hotel Tivoli"},
                    {"id": "s2", "number": "FT 2025/002", "amount": 890.0, "client": "Restaurante Central"}
                ],
                "costs": [
                    {"id": "c1", "supplier": "TAP Air Portugal", "amount": 800.0},
                    {"id": "c2", "supplier": "Hotel Partner", "amount": 450.0}
                ],
                "metadata": {
                    "total_sales": 2140.0,
                    "total_costs": 1250.0,
                    "potential_margin": 890.0
                }
            }
        elif path == '/api/health':
            response = {
                "status": "healthy",
                "message": "API funcionando correctamente"
            }
        else:
            response = {
                "error": "Endpoint not found",
                "path": path
            }

        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
        else:
            request_data = {}

        path = self.path

        if path == '/api/calculate':
            vat_rate = request_data.get("vat_rate", 23)
            total_sales = 2140.0
            total_costs = 1250.0
            gross_margin = total_sales - total_costs
            vat_amount = gross_margin * vat_rate / 100
            net_margin = gross_margin - vat_amount

            response = {
                "session_id": "demo-session-123",
                "vat_rate": vat_rate,
                "summary": {
                    "total_sales": total_sales,
                    "total_costs": total_costs,
                    "gross_margin": gross_margin,
                    "vat_amount": vat_amount,
                    "net_margin": net_margin
                }
            }
        else:
            response = {
                "success": True,
                "message": "POST processed"
            }

        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
