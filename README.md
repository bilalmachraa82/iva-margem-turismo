# IVA Margem Turismo - Backend

Sistema de cálculo de IVA sobre margem para agências de viagens.

## 🚀 Quick Start

### 1. Instalar dependências

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Executar o servidor

```bash
cd app
uvicorn main:app --reload
```

### 3. Testar

Abrir browser em:
- http://localhost:8000 - Status da API
- http://localhost:8000/docs - Documentação interativa
- http://localhost:8080/frontend/ - Interface com Dashboard Premium

## 📋 Funcionalidades

- ✅ Upload e parse de ficheiros SAF-T
- ✅ Associações many-to-many (custos ↔ vendas)
- ✅ Auto-associação inteligente com IA
- ✅ Cálculo preciso do IVA sobre margem
- ✅ Export Excel profissional com 5 folhas
- ✅ API RESTful completa
- ✅ Dashboard executivo premium com KPIs, cenários, waterfall e análise de outliers

## 🔧 Endpoints

- `POST /api/upload` - Upload ficheiro SAF-T
- `POST /api/associate` - Associar vendas e custos
- `POST /api/auto-match` - Auto-associação IA
- `POST /api/calculate` - Calcular e exportar Excel
- `GET /api/session/{id}` - Obter dados da sessão
- `DELETE /api/unlink` - Remover associações

## 📊 Estrutura Excel

1. **Resumo IVA Margem** - Cálculos principais
2. **Vendas Detalhadas** - Lista de vendas
3. **Custos Detalhados** - Lista de custos  
4. **Associações Detalhadas** - Mapa vendas-custos
5. **Totais e Estatísticas** - Sumário e análises

## 🎯 Fórmula IVA Margem

```
Margem = Venda - Custos
IVA = Margem × Taxa / (100 + Taxa)
Margem Líquida = Margem - IVA
```

## 🧪 Testes Recomendados

```bash
# Testes unitários do motor premium (não requer API a correr)
python test_premium_analytics.py

# Testes end-to-end (necessitam backend activo em http://localhost:8000)
python test_complete_system.py
python test_system_sync.py
```

## ⚙️ Variáveis de Ambiente Adicionais

| Variável | Descrição |
| --- | --- |
| `ENABLE_PREMIUM_PDF` | Define HTTP → PDF premium (`1` para activar). Requer dependências WeasyPrint instaladas no sistema. |
| `KV_REST_API_URL`, `KV_REST_API_TOKEN` | Credenciais Upstash KV para persistência serverless (opcional). |

## 🌐 Deploy

Pronto para Railway, Render ou Heroku.

---

**Powered by Accounting Advantage**
