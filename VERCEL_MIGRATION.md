# 🚀 Guia de Migração: Railway → Vercel + Neon

## Por que migrar?

- **Railway**: ~$5-20/mês
- **Vercel + Neon**: $0/mês (free tier generoso)
- **Performance**: CDN global, serverless auto-scaling

## Arquitetura Atual vs Nova

### Atual (Railway)
```
Railway (Backend FastAPI)
└── Armazenamento em memória
└── Arquivos temporários
```

### Nova (Vercel)
```
Vercel Functions (Backend FastAPI)
├── Option A: Memória + Temp files (como atual)
└── Option B: Neon PostgreSQL (futuro)
```

## Passo a Passo

### 1. Preparar Projeto

```bash
# Estrutura necessária
iva-margem-turismo/
├── api/
│   └── index.py          # ✅ Criado
├── backend/
│   └── app/              # Código existente
├── frontend/             # HTML/JS/CSS
├── vercel.json          # ✅ Criado
└── requirements.txt     # ✅ Criado
```

### 2. Ajustar Caminhos no Backend

No arquivo `backend/app/main.py`, adicione suporte para Vercel:

```python
# No início do arquivo
import os
from pathlib import Path

# Detectar ambiente
IS_VERCEL = os.environ.get('VERCEL')

# Ajustar path para temp files
if IS_VERCEL:
    TEMP_DIR = Path('/tmp')
else:
    TEMP_DIR = Path('temp')

# Garantir que diretório existe
TEMP_DIR.mkdir(exist_ok=True)
```

### 3. Deploy no Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Na raiz do projeto
cd /mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo

# Deploy
vercel

# Seguir prompts:
# - Link to existing project? No
# - What's your project name? iva-margem-turismo
# - Which directory? ./ (root)
# - Override settings? No
```

### 4. Configurar Frontend

Atualizar `frontend/index.html`:

```javascript
// Mudar de:
const apiUrl = 'http://localhost:8000';

// Para:
const apiUrl = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://iva-margem-turismo.vercel.app';
```

### 5. Variáveis de Ambiente (Opcional)

No dashboard Vercel:
- Settings → Environment Variables
- Adicionar se necessário:
  - `PYTHON_VERSION`: 3.11
  - `MAX_UPLOAD_SIZE`: 50MB

## Opção B: Com Neon (Persistência)

### 1. Criar conta Neon
- Ir para https://neon.tech
- Criar projeto free
- Copiar connection string

### 2. Adicionar ao projeto

```python
# backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
else:
    # Continuar com memória
    SessionLocal = None
```

### 3. Adicionar no Vercel
- Settings → Environment Variables
- `DATABASE_URL`: postgresql://...@ep-...neon.tech/...

## Vantagens da Migração

1. **Custo Zero** no free tier
2. **Deploy Automático** via GitHub
3. **CDN Global** (baixa latência)
4. **Serverless** (escala automática)
5. **HTTPS Grátis**
6. **Analytics** incluído

## Limitações Free Tier

### Vercel
- 100GB bandwidth/mês (suficiente)
- 100 horas serverless/mês (muito generoso)
- 12 segundos timeout (configuramos 60s)

### Neon (se usar)
- 0.5GB storage
- 1 projeto
- Branches ilimitados

## Comandos Úteis

```bash
# Deploy produção
vercel --prod

# Ver logs
vercel logs

# Rollback
vercel rollback

# Listar deployments
vercel ls
```

## Manter Railway Durante Transição

1. Manter Railway ativo inicialmente
2. Testar Vercel em staging
3. Migrar DNS quando estável
4. Cancelar Railway após 1 semana

## Resultado Final

- ✅ **Backend**: Vercel Functions (Python)
- ✅ **Frontend**: Vercel Static
- ✅ **Database**: Neon PostgreSQL (opcional)
- ✅ **Custo**: $0/mês
- ✅ **Performance**: Melhor que Railway