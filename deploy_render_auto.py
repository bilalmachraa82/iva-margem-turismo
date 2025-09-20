#!/usr/bin/env python3
"""
Script automático para deploy no Render
"""

import os
import json
import subprocess
import time
from pathlib import Path

def print_step(step, message):
    print(f"\n🚀 {step}: {message}")
    print("=" * 60)

def run_command(command, cwd=None):
    """Executa comando e retorna output"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Erro: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return None

def prepare_backend():
    """Prepara o backend para deploy"""
    print_step("1", "Preparando Backend para Deploy")
    
    # Verificar se requirements.txt está atualizado
    backend_dir = Path("backend")
    if not (backend_dir / "requirements.txt").exists():
        print("❌ requirements.txt não encontrado!")
        return False
    
    # Verificar se render_start.sh é executável
    start_script = backend_dir / "render_start.sh"
    if start_script.exists():
        os.chmod(start_script, 0o755)
        print("✅ Script de arranque configurado")
    
    # Testar import do backend
    print("🧪 Testando backend...")
    test_result = run_command("python3 -c \"from app.main import app; print('✅ Backend OK')\"", cwd="backend")
    if test_result:
        print("✅ Backend testado com sucesso")
        return True
    else:
        print("❌ Falha no teste do backend")
        return False

def prepare_frontend():
    """Prepara o frontend para deploy"""
    print_step("2", "Preparando Frontend para Deploy")
    
    frontend_dir = Path("frontend")
    if not (frontend_dir / "index.html").exists():
        print("❌ index.html não encontrado!")
        return False
    
    print("✅ Frontend pronto")
    return True

def create_render_config():
    """Cria configuração atualizada para o Render"""
    print_step("3", "Criando Configuração do Render")
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "iva-margem-backend",
                "env": "python",
                "buildCommand": "cd backend && pip install -r requirements.txt",
                "startCommand": "cd backend && ./render_start.sh",
                "healthCheckPath": "/api/health",
                "envVars": [
                    {"key": "ENVIRONMENT", "value": "production"},
                    {"key": "CORS_ORIGINS", "value": "*"},
                    {"key": "ENABLE_PREMIUM_PDF", "value": "1"},
                    {"key": "MAX_UPLOAD_SIZE_MB", "value": "50"},
                    {"key": "SESSION_TIMEOUT_HOURS", "value": "24"},
                    {"key": "PORT", "value": "8000"},
                    {"key": "PYTHON_VERSION", "value": "3.9.1"}
                ]
            },
            {
                "type": "web",
                "name": "iva-margem-frontend", 
                "env": "static",
                "buildCommand": "echo 'Frontend ready'",
                "staticPublishPath": "frontend",
                "headers": [
                    {
                        "path": "/*",
                        "name": "Access-Control-Allow-Origin",
                        "value": "*"
                    }
                ]
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        f.write("# Render Configuration - Auto-generated\n")
        f.write("services:\n")
        
        # Backend service
        f.write("  - type: web\n")
        f.write("    name: iva-margem-backend\n")
        f.write("    env: python\n")
        f.write("    buildCommand: cd backend && pip install -r requirements.txt\n")
        f.write("    startCommand: cd backend && ./render_start.sh\n")
        f.write("    healthCheckPath: /api/health\n")
        f.write("    envVars:\n")
        f.write("      - key: ENVIRONMENT\n")
        f.write("        value: production\n")
        f.write("      - key: CORS_ORIGINS\n")
        f.write("        value: *\n")
        f.write("      - key: ENABLE_PREMIUM_PDF\n")
        f.write("        value: \"1\"\n")
        f.write("      - key: MAX_UPLOAD_SIZE_MB\n")
        f.write("        value: \"50\"\n")
        f.write("      - key: SESSION_TIMEOUT_HOURS\n")
        f.write("        value: \"24\"\n")
        f.write("      - key: PORT\n")
        f.write("        value: \"8000\"\n")
        f.write("      - key: PYTHON_VERSION\n")
        f.write("        value: \"3.9.1\"\n\n")
        
        # Frontend service
        f.write("  - type: web\n")
        f.write("    name: iva-margem-frontend\n")
        f.write("    env: static\n")
        f.write("    buildCommand: echo 'Frontend ready'\n")
        f.write("    staticPublishPath: frontend\n")
    
    print("✅ Configuração render.yaml criada")
    return True

def create_deployment_guide():
    """Cria guia de deployment detalhado"""
    print_step("4", "Criando Guia de Deployment")
    
    guide_content = """# 🚀 Deploy no Render - Guia Rápido

## Passo 1: Aceder ao Render
1. Vai a [render.com](https://render.com)
2. Cria conta com GitHub
3. Vai a Dashboard → New → Web Service

## Passo 2: Deploy Backend
**Nome**: `iva-margem-backend`
**Build Command**: `cd backend && pip install -r requirements.txt`
**Start Command**: `cd backend && ./render_start.sh`

## Passo 3: Deploy Frontend  
**Nome**: `iva-margem-frontend`
**Tipo**: Static Site
**Publish Directory**: `frontend`

## URLs Previstas:
- Backend: `https://iva-margem-backend.onrender.com`
- Frontend: `https://iva-margem-frontend.onrender.com`

## Testar:
```bash
curl https://iva-margem-backend.onrender.com/api/health
```
"""
    
    with open("DEPLOY_RENDER_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Guia de deployment criado")

def main():
    """Função principal"""
    print("🚀 Iniciando preparação para deploy no Render")
    print("=" * 60)
    
    # Preparar componentes
    if not prepare_backend():
        return False
    
    if not prepare_frontend():
        return False
    
    if not create_render_config():
        return False
    
    create_deployment_guide()
    
    print_step("✅", "Preparação completa!")
    print("\n📋 Próximos passos:")
    print("1. Acede a https://render.com")
    print("2. Conecta o teu repositório GitHub")
    print("3. Usa o ficheiro render.yaml criado")
    print("4. Faz deploy! 🎯")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)