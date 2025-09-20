#!/usr/bin/env python3
"""
Teste simples de conectividade frontend-backend
"""

import requests
import json

def test_cors_connectivity():
    """Testar se o CORS está funcionando entre frontend e backend"""
    
    backend_url = "https://iva-margem-backend.onrender.com"
    frontend_origin = "https://iva-margem-frontend.onrender.com"
    
    print("🧪 Testando conectividade CORS...")
    print(f"Backend: {backend_url}")
    print(f"Frontend: {frontend_origin}")
    print("=" * 50)
    
    # Testar health check com origin do frontend
    try:
        headers = {
            "Origin": frontend_origin,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{backend_url}/api/health", headers=headers)
        
        print(f"✅ Health Check: {response.status_code}")
        print(f"CORS Header: {response.headers.get('access-control-allow-origin', 'NOT FOUND')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status', 'unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
    
    # Testar mock data endpoint
    try:
        response = requests.get(f"{backend_url}/api/mock-data", headers=headers)
        
        print(f"\n✅ Mock Data: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Vendas: {len(data.get('vendas', []))} registros")
            print(f"Custos: {len(data.get('custos', []))} registros")
        
    except Exception as e:
        print(f"❌ Erro no mock data: {e}")
    
    print("\n🎯 Teste concluído!")

if __name__ == "__main__":
    test_cors_connectivity()