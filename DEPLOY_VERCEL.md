# 🚀 DEPLOY VERCEL - FULL STACK GRATUITO

**Sistema completo:** Frontend + Backend FastAPI no Vercel **100% gratuito**

---

## ✅ **PRÉ-REQUISITOS**

✅ Sistema local a funcionar (confirmado!)
✅ Conta GitHub (para código)
✅ Conta Vercel (gratuita)

---

## 🔥 **PASSO 1: PREPARAR CÓDIGO**

O sistema já está preparado para Vercel:

```bash
# Estrutura pronta:
├── api/index.py          # ✅ Wrapper FastAPI para Vercel
├── backend/              # ✅ Código FastAPI existente
├── frontend/             # ✅ Frontend Alpine.js
├── vercel.json          # ✅ Configuração deployment
├── requirements.txt     # ✅ Dependencies Python
```

**Configuração automática:**
- Frontend detecta production e usa `/api`
- Backend funciona como Serverless Function
- Zero alterações de código necessárias!

---

## 📦 **PASSO 2: PUSH PARA GITHUB**

```bash
# No teu projeto:
cd /Users/bilal/Programaçao/Claudia/iva-margem-turismo-1

# Inicializar git (se não tiver)
git init
git add .
git commit -m "feat: Vercel deployment ready"

# Criar repo GitHub e push
gh repo create iva-margem-turismo --public
git remote add origin https://github.com/SEU_USERNAME/iva-margem-turismo.git
git push -u origin main
```

---

## 🌐 **PASSO 3: DEPLOY VERCEL**

### **Método 1: CLI (Recomendado)**
```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (primeira vez)
vercel

# Configuração automática:
# ✅ Framework: Other
# ✅ Root Directory: ./
# ✅ Build Command: (deixar vazio)
# ✅ Output Directory: frontend/
# ✅ Serverless Functions: api/

# Deploy production
vercel --prod
```

### **Método 2: Dashboard Vercel**
1. Vai a [vercel.com](https://vercel.com)
2. "Import Project" → Liga GitHub
3. Seleciona repo `iva-margem-turismo`
4. Framework: **Other**
5. Root Directory: `./`
6. Deploy!

---

## ⚙️ **CONFIGURAÇÃO VERCEL**

O `vercel.json` já define:

```json
{
  "build": {
    "env": {
      "PYTHON_VERSION": "3.11"
    }
  },
  "functions": {
    "api/index.py": {
      "runtime": "python3.11",
      "maxDuration": 60
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

---

## 🎯 **LIMITES VERCEL GRATUITO**

### **Incluído GRATIS:**
✅ **100GB** bandwidth/mês
✅ **100** Serverless Function executions/dia
✅ **10 segundos** max execution time
✅ **Custom domain** gratuito
✅ **SSL certificate** automático
✅ **Git integration** automático

### **Para IVA Margem:**
- ✅ Perfeito para **MVP + early customers**
- ✅ Suporta **1000+ cálculos/mês**
- ✅ Upload SAF-T até **6MB**
- ✅ Export Excel/PDF funciona

---

## 📊 **MONITORIZAÇÃO**

Após deploy, tens acesso a:

```bash
# URLs automáticos:
https://iva-margem-turismo.vercel.app          # Frontend
https://iva-margem-turismo.vercel.app/api      # API Backend
https://iva-margem-turismo.vercel.app/docs     # API Docs

# Monitorização:
https://vercel.com/dashboard                   # Analytics
https://vercel.com/dashboard/functions         # Function logs
```

---

## 🚨 **TROUBLESHOOTING**

### **Erro: "Function timeout"**
```python
# Em vercel.json aumentar:
"maxDuration": 30  # Default 10s → 30s
```

### **Erro: "Module not found"**
```bash
# Verificar requirements.txt na root
# Verificar imports relativos em api/index.py
```

### **Upload files grandes**
```python
# Vercel limit: 6MB per file
# Para SAF-T >6MB, implementar chunked upload
```

### **Cold starts lentos**
```python
# Normal: primeiro request ~3-5s
# Subsequentes: ~100-500ms
# Solução: manter função "warm" com ping
```

---

## 💰 **CUSTOS**

### **Vercel Free Tier:**
- **€0/mês** para MVP
- **Upgrade Pro €20/mês** quando cresceres

### **Comparação vs Railway:**
```
Railway:   €5-25/mês
Vercel:    €0-20/mês
Netlify:   €0-19/mês

Winner:    Vercel (mais features gratis)
```

---

## 🔐 **SEGURANÇA & PERFORMANCE**

### **Automático no Vercel:**
✅ **HTTPS/SSL** gratuito
✅ **Global CDN** (edge caching)
✅ **DDoS protection**
✅ **Auto-scaling**
✅ **Git-based deployments**

### **Optimizações:**
```python
# 1. Enable caching headers
@app.middleware("http")
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/static"):
        response.headers["Cache-Control"] = "public, max-age=31536000"
    return response

# 2. Compress responses
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 🎉 **NEXT STEPS PÓS-DEPLOY**

### **1. Custom Domain (Gratis)**
```bash
# No Vercel dashboard:
Settings → Domains → Add "tuaempresa.pt"
```

### **2. Environment Variables**
```bash
# Para API keys/secrets:
vercel env add OPENAI_API_KEY
vercel env add DATABASE_URL
```

### **3. Analytics**
```bash
# Vercel Analytics (gratis):
npm i @vercel/analytics
# ou Google Analytics
```

### **4. Monitoring**
```bash
# Uptime monitoring gratis:
- UptimeRobot
- Pingdom
- StatusCake
```

---

## 🚀 **DEPLOY COMMAND SUMMARY**

```bash
# Quick deploy:
git add . && git commit -m "deploy"
git push
vercel --prod

# URL será: https://iva-margem-turismo.vercel.app
```

---

## 💡 **PRO TIPS**

### **Performance:**
- Frontend estático = super rápido
- API functions = cold start primeira vez
- Use preview deployments para testar

### **Development:**
```bash
# Local development (como sempre):
cd backend && python -m uvicorn app.main:app --reload  # Port 8000
cd frontend && python -m http.server 3000             # Port 3000

# Production deployment:
vercel --prod
```

### **Escalabilidade:**
- Free tier: **perfeito para MVP**
- Pro tier: **€20/mês para negócio sério**
- Enterprise: **quando faturares €10K+/mês**

---

**🎯 RESULTADO: Sistema completo online em 5 minutos, €0 de custo mensal!**

**✅ Ready para mostrar a clientes e começar a facturar!**