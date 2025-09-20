# 🚀 Deploy no Render - Guia Rápido

## Passo 1: Aceder ao Render
1. Vai a [render.com](https://render.com)
2. Cria conta com GitHub
3. Vai a Dashboard → New → Web Service

## Passo 2: Deploy Backend
**Nome**: `iva-margem-backend`
**Build Command**: `cd backend && pip install -r requirements.txt`
**Start Command**: `cd backend && ./render_start.sh`
> O backend cria `temp/sessions` automaticamente para partilhar dados entre workers, por isso podes manter `--workers 4` sem perdas de sessão.

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
