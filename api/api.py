from http.server import BaseHTTPRequestHandler
import json
import uuid
import csv
import base64
from io import StringIO
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        path = self.path.split('?')[0]  # Remove query parameters

        if path == '/api/api':
            self._handle_main_api()
        elif path == '/api/api/mock-data':
            self._handle_mock_data()
        elif path == '/api/api/health':
            self._handle_health()
        elif path.startswith('/api/api/session/'):
            session_id = path.split('/')[-1]
            self._handle_session_get(session_id)
        else:
            self._handle_not_found(path)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        path = self.path.split('?')[0]

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
        else:
            request_data = {}

        if path == '/api/api/upload-efatura':
            self._handle_upload_efatura(request_data)
        elif path == '/api/api/upload':
            self._handle_upload_saft(request_data)
        elif path == '/api/api/associate':
            self._handle_associate(request_data)
        elif path == '/api/api/auto-match':
            self._handle_auto_match(request_data)
        elif path == '/api/api/clear-associations':
            self._handle_clear_associations(request_data)
        elif path == '/api/api/calculate':
            self._handle_calculate(request_data)
        elif path == '/api/api/calculate-period':
            self._handle_calculate_period(request_data)
        elif path == '/api/api/export-pdf':
            self._handle_export_pdf(request_data)
        else:
            self._handle_not_found(path)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _handle_main_api(self):
        response = {
            "message": "IVA Margem Turismo API está online!",
            "status": "success",
            "version": "1.0.0",
            "endpoints": [
                "GET /api/api/mock-data",
                "GET /api/api/health",
                "POST /api/api/calculate"
            ]
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_mock_data(self):
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

    def _handle_health(self):
        response = {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "uptime": "100%",
            "version": "1.0.0",
            "endpoints": {
                "GET": ["/api/api/", "/api/api/health", "/api/api/mock-data"],
                "POST": ["/api/api/calculate", "/api/api/upload-efatura"]
            },
            "timestamp": "2025-01-19T23:36:00Z"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_calculate(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        vat_rate = request_data.get("vat_rate", 23)

        # Mock calculation
        total_sales = 6470.0
        total_costs = 3045.0
        gross_margin = total_sales - total_costs
        vat_amount = gross_margin * vat_rate / 100
        net_margin = gross_margin - vat_amount

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

    def _handle_upload_efatura(self, request_data):
        vendas_content = request_data.get('vendas_content', '')
        compras_content = request_data.get('compras_content', '')
        session_id = str(uuid.uuid4())

        response = {
            "success": True,
            "session_id": session_id,
            "message": "Ficheiros e-Fatura processados com sucesso",
            "summary": {
                "sales_count": 5,
                "costs_count": 6,
                "total_sales": 6470.0,
                "total_costs": 3045.0,
                "potential_margin": 3425.0
            }
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_associate(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        sale_id = request_data.get("sale_id")
        cost_ids = request_data.get("cost_ids", [])

        response = {
            "success": True,
            "session_id": session_id,
            "message": f"Associação criada: venda {sale_id} com {len(cost_ids)} custos"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_auto_match(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        threshold = request_data.get("threshold", 60)

        associations = [
            {"sale_id": "s1", "cost_ids": ["c1", "c2"], "confidence": 85},
            {"sale_id": "s2", "cost_ids": ["c3"], "confidence": 72}
        ]

        response = {
            "success": True,
            "session_id": session_id,
            "associations": associations,
            "stats": {"total_matches": len(associations)}
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_clear_associations(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        response = {
            "success": True,
            "session_id": session_id,
            "message": "Associações removidas com sucesso"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_calculate_period(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        period = request_data.get("period", "monthly")
        vat_rate = request_data.get("vat_rate", 23)

        response = {
            "success": True,
            "session_id": session_id,
            "period": period,
            "vat_rate": vat_rate,
            "summary": {
                "total_sales": 6470.0,
                "total_costs": 3045.0,
                "gross_margin": 3425.0,
                "vat_amount": 787.75,
                "net_margin": 2637.25
            }
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_export_pdf(self, request_data):
        session_id = request_data.get("session_id", "demo-session-123")
        pdf_content = "Mock PDF content"
        pdf_base64 = base64.b64encode(pdf_content.encode()).decode()

        response = {
            "success": True,
            "session_id": session_id,
            "filename": f"relatorio_iva_margem_{session_id[:8]}.pdf",
            "pdf_data": pdf_base64
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_upload_saft(self, request_data):
        session_id = str(uuid.uuid4())
        response = {
            "success": True,
            "session_id": session_id,
            "message": "Ficheiro SAF-T processado com sucesso"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_session_get(self, session_id):
        response = {
            "success": True,
            "session_id": session_id,
            "status": "active",
            "data": {
                "sales": [{"id": "s1", "amount": 1250.0}],
                "costs": [{"id": "c1", "amount": 800.0}],
                "associations": []
            }
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_not_found(self, path):
        response = {
            "error": "Endpoint not found",
            "path": path,
            "available_endpoints": [
                "GET /api/api/mock-data",
                "POST /api/api/calculate"
            ]
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))