#!/usr/bin/env python3
"""
Teste final do sistema completo - Frontend e Backend
"""

import requests
import json
import time

def test_system_status():
    """Testar status completo do sistema"""
    
    frontend_url = "https://iva-margem-frontend.onrender.com"
    backend_url = "https://iva-margem-backend.onrender.com"
    
    print("🚀 Teste Final do Sistema")
    print("=" * 50)
    print(f"Frontend: {frontend_url}")
    print(f"Backend: {backend_url}")
    print("=" * 50)
    
    # Testar Frontend
    print("\n📱 Testando Frontend...")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend está acessível")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        else:
            print(f"❌ Frontend retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar frontend: {e}")
    
    # Testar Backend
    print("\n⚙️ Testando Backend...")
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend está saudável")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            print(f"   Sessões: {data.get('sessions_active', 0)}")
        else:
            print(f"❌ Backend retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar backend: {e}")
    
    # Testar CORS
    print("\n🌐 Testando CORS...")
    try:
        headers = {"Origin": frontend_url}
        response = requests.get(f"{backend_url}/api/health", headers=headers, timeout=10)
        cors_header = response.headers.get('access-control-allow-origin', 'NOT FOUND')
        print(f"✅ CORS Header: {cors_header}")
        
        if response.status_code == 200:
            print("✅ CORS está funcionando")
        else:
            print(f"❌ CORS falhou: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar CORS: {e}")
    
    # Testar endpoints do backend
    print("\n🔌 Testando Endpoints do Backend...")
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/mock-data", "Mock Data"),
        ("/api/companies", "Companies")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                if endpoint == "/api/mock-data":
                    data = response.json()
                    print(f"   Vendas: {len(data.get('vendas', []))}")
                    print(f"   Custos: {len(data.get('custos', []))}")
            else:
                print(f"⚠️ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Erro - {e}")
    
    print("\n🎉 Teste concluído!")
    print("\n💡 Para testar manualmente:")
    print("   1. Acesse: https://iva-margem-frontend.onrender.com")
    print("   2. Clique em 'Usar Dados de Demonstração'")
    print("   3. Verifique se os dados carregam sem erros")

if __name__ == "__main__":
    test_system_status()