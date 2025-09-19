from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
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

        # Simple VAT calculation
        session_id = request_data.get("session_id", "demo-session-123")
        vat_rate = request_data.get("vat_rate", 23)

        # Mock calculation with realistic data
        total_sales = 6470.0
        total_costs = 3045.0
        gross_margin = total_sales - total_costs  # 3425.0
        vat_amount = gross_margin * vat_rate / 100  # 787.75
        net_margin = gross_margin - vat_amount     # 2637.25

        response = {
            "success": True,
            "session_id": session_id,
            "vat_rate": vat_rate,
            "summary": {
                "total_sales": total_sales,
                "total_costs": total_costs,
                "gross_margin": gross_margin,
                "vat_amount": round(vat_amount, 2),
                "net_margin": round(net_margin, 2),
                "effective_rate": round((vat_amount / gross_margin * 100) if gross_margin > 0 else 0, 2)
            },
            "formula": "IVA = Margem × Taxa / 100 (CIVA Art. 308º)",
            "calculated_at": "2025-01-19T23:36:00Z"
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()