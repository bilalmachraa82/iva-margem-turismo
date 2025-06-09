#!/usr/bin/env python3
"""
Deploy Simples para IVA Margem Turismo
"""
import os
import json
import subprocess

# Diretório do projeto
PROJECT_DIR = "/mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo"

# Tokens
VERCEL_TOKEN = "X9FONpQ2jSJIVvIZyltoBMAH"

def deploy_to_vercel():
    """Deploy simples para Vercel"""
    print("🚀 Deploy para Vercel...")
    
    # Criar vercel.json
    vercel_config = {
        "buildCommand": "cd backend && pip install -r requirements.txt",
        "outputDirectory": ".",
        "functions": {
            "backend/api/index.py": {
                "runtime": "python3.9"
            }
        },
        "rewrites": [
            {"source": "/api/(.*)", "destination": "/backend/api/index"},
            {"source": "/(.*)", "destination": "/frontend/$1"}
        ]
    }
    
    with open(f"{PROJECT_DIR}/vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    # Criar estrutura API
    os.makedirs(f"{PROJECT_DIR}/backend/api", exist_ok=True)
    
    # Criar handler API
    api_handler = """from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

# Handler para Vercel
handler = app
"""
    
    with open(f"{PROJECT_DIR}/backend/api/index.py", "w") as f:
        f.write(api_handler)
    
    # Deploy com Vercel CLI
    os.chdir(PROJECT_DIR)
    
    cmd = f"npx vercel --token {VERCEL_TOKEN} --yes --prod"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Deploy concluído!")
        print("🌐 URL: https://iva-margem-turismo.vercel.app")
    else:
        print(f"❌ Erro: {result.stderr}")

if __name__ == "__main__":
    deploy_to_vercel()