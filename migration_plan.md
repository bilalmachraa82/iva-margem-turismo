# 🚀 PLANO DE MIGRAÇÃO PROFISSIONAL - IVA MARGEM TURISMO
*Expert Migration Plan - 10+ Anos Experiência*

## 📊 ANÁLISE EXECUTIVA

### Estado Atual
- **Backend:** FastAPI 100% funcional com dados reais
- **Frontend:** Premium UI com DaisyUI + Alpine.js  
- **Database:** In-memory (necessita migração para PostgreSQL)
- **Infra:** Local development → Cloud migration pending

### Objetivos
1. Deploy produção com alta disponibilidade
2. Database persistente com backup automático
3. CI/CD pipeline automatizado
4. Monitorização e alertas
5. Escalabilidade horizontal

## 🏗️ ARQUITETURA TARGET

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUÇÃO                             │
├─────────────────────────────────────────────────────────┤
│ Frontend:  Vercel (Edge Network Global)                 │
│ Backend:   Railway (Container Platform)                 │
│ Database:  Neon PostgreSQL (Serverless)                │
│ Storage:   Cloudflare R2 (S3-compatible)              │
│ CDN:       Vercel Edge + Cloudflare                   │
│ Monitor:   Railway Analytics + Vercel Analytics        │
└─────────────────────────────────────────────────────────┘
```

## 📋 PLANO DETALHADO - 3 FASES

### FASE 1: PREPARAÇÃO E TESTES (3-4 horas)

#### 1.1 Database Migration
```sql
-- Neon PostgreSQL Schema
CREATE DATABASE iva_margem_turismo;

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_key VARCHAR(50) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '24 hours'
);

-- Indexes for performance
CREATE INDEX idx_sessions_key ON sessions(session_key);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Auto-cleanup old sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup every hour
SELECT cron.schedule('cleanup-sessions', '0 * * * *', 'SELECT cleanup_expired_sessions()');
```

#### 1.2 Backend Adaptations
```python
# database.py - New file
import os
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_key = Column(String(50), unique=True, index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

# Session manager
class SessionManager:
    def __init__(self, db: SessionLocal):
        self.db = db
    
    def create_session(self, data: dict) -> str:
        session_key = str(uuid.uuid4())[:8]
        db_session = SessionModel(
            session_key=session_key,
            data=data
        )
        self.db.add(db_session)
        self.db.commit()
        return session_key
    
    def get_session(self, session_key: str) -> dict:
        session = self.db.query(SessionModel).filter(
            SessionModel.session_key == session_key,
            SessionModel.expires_at > datetime.utcnow()
        ).first()
        return session.data if session else None
```

#### 1.3 Environment Configuration
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@neon.tech/iva_margem
REDIS_URL=redis://default:xxx@redis.railway.internal:6379
STORAGE_BACKEND=cloudflare_r2
R2_ACCESS_KEY=xxx
R2_SECRET_KEY=xxx
R2_BUCKET=iva-margem-files
SENTRY_DSN=https://xxx@sentry.io/xxx
ENVIRONMENT=production
```

### FASE 2: DEPLOYMENT (2-3 horas)

#### 2.1 Railway Backend Setup
```yaml
# railway.toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "backend"
type = "web"

[services.backend]
port = 8000

[[services.backend.envs]]
PYTHON_VERSION = "3.9"
```

#### 2.2 Vercel Frontend Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://iva-margem-backend.railway.app/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, s-maxage=86400"
        }
      ]
    }
  ]
}
```

#### 2.3 CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          cd backend
          pip install -r requirements.txt
          python -m pytest

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### FASE 3: OTIMIZAÇÃO E MONITORIZAÇÃO (2 horas)

#### 3.1 Performance Optimizations
```python
# Cache layer com Redis
import redis
from functools import lru_cache
import json

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def cache_result(key: str, data: dict, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(data))

def get_cached(key: str) -> dict:
    data = redis_client.get(key)
    return json.loads(data) if data else None

# Exemplo de uso
@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    # Check cache first
    cached = get_cached(f"session:{session_id}")
    if cached:
        return cached
    
    # Get from DB
    session = db.get_session(session_id)
    if session:
        cache_result(f"session:{session_id}", session, ttl=300)
    
    return session
```

#### 3.2 Monitoring Setup
```python
# monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development")
)

# Custom metrics
from prometheus_client import Counter, Histogram, generate_latest

upload_counter = Counter('saft_uploads_total', 'Total SAF-T uploads')
calculation_duration = Histogram('calculation_duration_seconds', 'VAT calculation duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### 3.3 Security Hardening
```python
# security.py
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_file(request: Request, file: UploadFile):
    # Validate file
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(400, "File too large")
    
    # Scan for malware (ClamAV integration)
    if not await scan_file(file):
        raise HTTPException(400, "File failed security scan")
    
    # Process file...
```

## 🔄 MIGRATION EXECUTION STEPS

### Step 1: Database Setup (30 min)
```bash
# 1. Create Neon project
neon create-project iva-margem-turismo --region eu-central-1

# 2. Get connection string
neon connection-string iva-margem-turismo

# 3. Run migrations
export DATABASE_URL="postgresql://..."
cd backend
python migrate_to_postgres.py
```

### Step 2: Backend Deployment (45 min)
```bash
# 1. Login to Railway
railway login

# 2. Create new project
railway init

# 3. Add PostgreSQL
railway add

# 4. Deploy
railway up

# 5. Set environment variables
railway variables set DATABASE_URL=$NEON_URL
railway variables set ENVIRONMENT=production
```

### Step 3: Frontend Deployment (30 min)
```bash
# 1. Update API URL in frontend
sed -i 's|http://localhost:8000|https://iva-margem-backend.railway.app|g' frontend/index.html

# 2. Deploy to Vercel
cd frontend
vercel --prod

# 3. Configure domain
vercel domains add iva-margem.com
```

### Step 4: Validation (30 min)
```bash
# Run smoke tests
python test_production.py

# Check metrics
curl https://iva-margem-backend.railway.app/metrics

# Monitor logs
railway logs -f
```

## 📊 SUCCESS METRICS

### Performance KPIs
- API Response Time: < 200ms (p95)
- Upload Processing: < 5s for 50MB file
- Excel Generation: < 3s
- Uptime: 99.9% SLA

### Business Metrics
- Concurrent Users: 100+
- Daily Uploads: 1000+
- Storage Usage: < 100GB/month
- Cost: < €50/month

## 🚨 ROLLBACK PLAN

```bash
# If deployment fails
railway rollback

# Restore database
neon restore --point-in-time "2024-01-09 10:00:00"

# Switch DNS back
vercel alias set old-deployment.vercel.app iva-margem.com
```

## 📝 POST-MIGRATION CHECKLIST

- [ ] All tests passing in production
- [ ] SSL certificates active
- [ ] Monitoring dashboards configured
- [ ] Backup automation verified
- [ ] Documentation updated
- [ ] Team trained on new deployment process
- [ ] Customer communication sent

## 🎯 TIMELINE

```
Day 1 (4h):
- 09:00-10:00: Database setup
- 10:00-12:00: Backend adaptations
- 14:00-16:00: Deployment preparation

Day 2 (3h):
- 09:00-11:00: Production deployment
- 11:00-12:00: Testing & validation

Day 3 (2h):
- 09:00-10:00: Monitoring setup
- 10:00-11:00: Performance tuning
```

---

**🏆 Com este plano, terás uma aplicação production-ready com:**
- ✅ Alta disponibilidade global
- ✅ Backup automático
- ✅ CI/CD completo
- ✅ Monitorização proativa
- ✅ Custo otimizado

**💡 Pronto para executar? Começamos pela Fase 1!**