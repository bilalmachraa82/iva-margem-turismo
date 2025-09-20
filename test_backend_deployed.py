#!/usr/bin/env python3
"""
Script para testar o backend após deploy no Render
"""

import requests
import json
import time
import sys

def test_backend_health():
    """Testa se o backend está respondendo"""
    url = "https://iva-margem-backend.onrender.com/api/health"
    
    try:
        print("🧪 Testando health check do backend...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print("✅ Backend está respondendo!")
            print(f"Resposta: {response.text}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar ao backend: {e}")
        return False

def test_backend_api():
    """Testa endpoints principais do backend"""
    base_url = "https://iva-margem-backend.onrender.com/api"
    
    endpoints = [
        "/health",
        "/mock-data",
        "/companies"
    ]
    
    print("\n🧪 Testando endpoints do backend...")
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"⚠️  {endpoint}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Erro - {e}")

def main():
    """Função principal"""
    print("🚀 Testando Backend IVA Margem - Render Deploy")
    print("=" * 50)
    
    # Testar health check
    if test_backend_health():
        # Se health check passar, testar outros endpoints
        test_backend_api()
        print("\n✅ Testes completados!")
        return 0
    else:
        print("\n❌ Backend não está respondendo ainda.")
        print("💡 O deploy pode estar em andamento. Aguarde mais alguns minutos.")
        return 1

if __name__ == "__main__":
    sys.exit(main())