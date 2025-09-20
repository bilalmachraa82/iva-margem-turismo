# 🚀 Deploy Manual no Render

## Passo 1: Criar Conta e Preparar
1. Acede a [render.com](https://render.com)
2. Cria conta com GitHub
3. Vai a Dashboard → New → Web Service

## Passo 2: Configurar Backend
**Nome**: `iva-margem-backend`  
**Repositório**: Seleciona o teu repo  
**Branch**: `main`  
**Build Command**: `cd backend && pip install -r requirements.txt`  
**Start Command**: `cd backend && ./render_start.sh`  

**Environment Variables**:
```
ENVIRONMENT=production
CORS_ORIGINS=https://iva-margem-frontend.onrender.com
ENABLE_PREMIUM_PDF=1
MAX_UPLOAD_SIZE_MB=50
SESSION_TIMEOUT_HOURS=24
```

## Passo 3: Configurar Frontend
**Nome**: `iva-margem-frontend`  
**Tipo**: Static Site  
**Build Command**: `echo "Frontend ready"`  
**Publish Directory**: `frontend`

## Passo 4: Configurar Base de Dados
**Nome**: `iva-margem-db`  
**Tipo**: PostgreSQL  
**Plano**: Starter (grátis)

## Passo 5: Testar
- Backend: `https://iva-margem-backend.onrender.com/api/health`
- Frontend: `https://iva-margem-frontend.onrender.com`

## 🛠️ Comandos Úteis para Debugging
```bash
# Ver logs
render logs iva-margem-backend

# Reiniciar serviço
render restart iva-margem-backend

# Escalar (se necessário)
render scale iva-margem-backend --type=standard
```