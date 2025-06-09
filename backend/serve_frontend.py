#!/usr/bin/env python3
"""
Servidor para desenvolvimento que serve frontend e redireciona API
Resolve problemas de CORS
"""
import http.server
import socketserver
import urllib.parse
import urllib.request
import json

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Se for requisição API, fazer proxy
        if self.path.startswith('/api/'):
            try:
                # Fazer request para o backend
                backend_url = f'http://localhost:8000{self.path}'
                with urllib.request.urlopen(backend_url) as response:
                    data = response.read()
                
                # Enviar resposta
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Servir arquivos estáticos
            super().do_GET()
    
    def do_POST(self):
        # Proxy para POST requests
        if self.path.startswith('/api/'):
            try:
                # Ler body da requisição
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Fazer request para o backend
                backend_url = f'http://localhost:8000{self.path}'
                req = urllib.request.Request(backend_url, data=post_data, method='POST')
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                
                # Enviar resposta
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(500, str(e))

if __name__ == '__main__':
    PORT = 8080
    Handler = ProxyHandler
    
    print(f"🚀 Servidor de desenvolvimento iniciado!")
    print(f"📁 Frontend: http://localhost:{PORT}/frontend/")
    print(f"🧪 Teste: http://localhost:{PORT}/backend/test_frontend.html")
    print(f"🔄 API Proxy: http://localhost:{PORT}/api/*")
    print(f"✨ CORS resolvido automaticamente!")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()