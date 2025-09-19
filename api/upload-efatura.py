from http.server import BaseHTTPRequestHandler
import json
import uuid
import csv
from io import StringIO

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

            # Extract file data
            vendas_content = request_data.get('vendas_content', '')
            compras_content = request_data.get('compras_content', '')

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Parse CSV data (simplified)
            sales = []
            costs = []

            # Parse vendas
            if vendas_content:
                csv_reader = csv.DictReader(StringIO(vendas_content), delimiter=';')
                for i, row in enumerate(csv_reader):
                    if i >= 50:  # Limit for demo
                        break
                    try:
                        sales.append({
                            "id": f"v{i+1}",
                            "number": row.get('Número', f"VND-{i+1:03d}"),
                            "amount": float(row.get('Valor', '0').replace(',', '.')),
                            "client": row.get('Cliente', 'Cliente Desconhecido'),
                            "date": row.get('Data', '2025-01-01')
                        })
                    except (ValueError, KeyError):
                        continue

            # Parse compras
            if compras_content:
                csv_reader = csv.DictReader(StringIO(compras_content), delimiter=';')
                for i, row in enumerate(csv_reader):
                    if i >= 200:  # Limit for demo
                        break
                    try:
                        costs.append({
                            "id": f"c{i+1}",
                            "supplier": row.get('Fornecedor', 'Fornecedor Desconhecido'),
                            "amount": float(row.get('Valor', '0').replace(',', '.')),
                            "date": row.get('Data', '2025-01-01')
                        })
                    except (ValueError, KeyError):
                        continue

            total_sales = sum(s['amount'] for s in sales)
            total_costs = sum(c['amount'] for c in costs)

            response = {
                "success": True,
                "session_id": session_id,
                "message": f"Ficheiros e-Fatura processados com sucesso",
                "summary": {
                    "sales_count": len(sales),
                    "costs_count": len(costs),
                    "total_sales": round(total_sales, 2),
                    "total_costs": round(total_costs, 2),
                    "potential_margin": round(total_sales - total_costs, 2)
                },
                "data": {
                    "sales": sales,
                    "costs": costs,
                    "associations": []
                }
            }

        except Exception as e:
            response = {
                "success": False,
                "error": f"Erro ao processar ficheiros: {str(e)}",
                "session_id": None
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()