from http.server import BaseHTTPRequestHandler
import json
import base64

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
            vat_rate = request_data.get("vat_rate", 23)

            # Mock PDF content (basic)
            pdf_content = "Mock PDF content for IVA Margem Turismo Report"
            pdf_base64 = base64.b64encode(pdf_content.encode()).decode()

            response = {
                "success": True,
                "session_id": session_id,
                "filename": f"relatorio_iva_margem_{session_id[:8]}.pdf",
                "pdf_data": pdf_base64,
                "size": len(pdf_content),
                "generated_at": "2025-01-19T23:36:00Z"
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro ao gerar PDF: {str(e)}"
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()