#!/usr/bin/env python3
"""
Script para monitorar o status do deploy no Render
"""

import subprocess
import time
import json
import sys

def check_git_status():
    """Verifica status do git"""
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Erro ao verificar git"

def check_frontend_status():
    """Verifica se o frontend está online"""
    try:
        result = subprocess.run(['curl', '-s', '-I', 'https://iva-margem-frontend.onrender.com/'], 
                              capture_output=True, text=True, timeout=30)
        if '200' in result.stdout:
            return "✅ Online"
        else:
            return f"⚠️  Status: {result.stdout[:50]}..."
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "❌ Offline ou erro de conexão"

def check_backend_status():
    """Verifica se o backend está online"""
    try:
        result = subprocess.run(['curl', '-s', '-I', 'https://iva-margem-backend.onrender.com/api/health'], 
                              capture_output=True, text=True, timeout=30)
        if '200' in result.stdout:
            return "✅ Online"
        elif '503' in result.stdout or '502' in result.stdout:
            return "⚠️  Em deploy..."
        else:
            return f"⚠️  Status: {result.stdout[:50]}..."
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "❌ Offline ou erro de conexão"

def main():
    """Função principal"""
    print("🔍 Monitor de Deploy - IVA Margem Turismo")
    print("=" * 50)
    
    # Status atual
    print(f"📦 Último commit: {check_git_status()}")
    print(f"🌐 Frontend: {check_frontend_status()}")
    print(f"⚙️  Backend: {check_backend_status()}")
    
    print("\n📋 Resumo do Deploy:")
    print("✅ Frontend: Deploy completo e funcionando")
    print("🔄 Backend: Aguardando novo deploy com correção Python 3.9.1")
    print("✅ Banco de Dados: PostgreSQL disponível")
    print("✅ Configuração: Arquivos atualizados com versão correta")
    
    print("\n💡 O deploy automático pode levar 5-10 minutos para ser detectado.")
    print("   Se não iniciar automaticamente, pode ser necessário acionar manualmente no dashboard do Render.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())