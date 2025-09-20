#!/usr/bin/env python3
"""
Deploy automático no Render usando MCP
"""

def deploy_backend(repo_url):
    """Cria backend service no Render"""
    print("🚀 Criando backend service...")
    
    # Configuração do backend
    backend_config = {
        "name": "iva-margem-backend",
        "runtime": "python",
        "repo": repo_url,
        "branch": "main",
        "buildCommand": "cd backend && pip install -r requirements.txt",
        "startCommand": "cd backend && ./render_start.sh",
        "region": "oregon",
        "plan": "starter",
        "envVars": [
            {"key": "ENVIRONMENT", "value": "production"},
            {"key": "CORS_ORIGINS", "value": "*"},
            {"key": "ENABLE_PREMIUM_PDF", "value": "1"},
            {"key": "MAX_UPLOAD_SIZE_MB", "value": "50"},
            {"key": "SESSION_TIMEOUT_HOURS", "value": "24"},
            {"key": "PORT", "value": "8000"}
        ]
    }
    
    return backend_config

def deploy_frontend(repo_url):
    """Cria frontend service no Render"""
    print("🚀 Criando frontend service...")
    
    # Configuração do frontend
    frontend_config = {
        "name": "iva-margem-frontend",
        "repo": repo_url,
        "branch": "main", 
        "buildCommand": "echo 'Frontend ready'",
        "publishPath": "frontend",
        "region": "oregon",
        "plan": "free"
    }
    
    return frontend_config

def deploy_database():
    """Cria PostgreSQL database"""
    print("🚀 Criando PostgreSQL database...")
    
    db_config = {
        "name": "iva-margem-db",
        "plan": "free",
        "region": "oregon",
        "version": 16
    }
    
    return db_config

def main():
    """Função principal"""
    print("🎯 DEPLOY AUTOMÁTICO NO RENDER")
    print("=" * 50)
    
    # Perguntar pelo repositório
    repo_url = input("📁 Qual é o URL do teu repositório GitHub? (ex: https://github.com/user/repo): ").strip()
    
    if not repo_url:
        print("❌ URL do repositório é obrigatório!")
        return
    
    print(f"\n✅ Repositório: {repo_url}")
    print("\n📋 Configurações que vou criar:")
    
    # Preparar configurações
    backend = deploy_backend(repo_url)
    frontend = deploy_frontend(repo_url)
    database = deploy_database()
    
    print("\n🚀 Backend:")
    for key, value in backend.items():
        if key != 'envVars':
            print(f"   {key}: {value}")
    
    print("\n🌐 Frontend:")
    for key, value in frontend.items():
        print(f"   {key}: {value}")
    
    print("\n🗄️ Database:")
    for key, value in database.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    print("📋 Copia estas configurações e confirma para prosseguir!")
    
    confirmar = input("\nQueres continuar com o deploy? (s/n): ")
    
    if confirmar.lower() == 's':
        print("\n🚀 Iniciando deploy automático...")
        print("Use os comandos MCP para criar os serviços:")
        print("\n1. Backend (Python Web Service):")
        print(f"   mcp_render2_create_web_service com os parâmetros acima")
        print("\n2. Frontend (Static Site):")  
        print(f"   mcp_render2_create_static_site com os parâmetros acima")
        print("\n3. Database (PostgreSQL):")
        print(f"   mcp_render2_create_postgres com os parâmetros acima")
    else:
        print("\n❌ Deploy cancelado.")

if __name__ == "__main__":
    main()