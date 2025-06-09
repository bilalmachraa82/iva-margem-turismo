# 🚀 IVA MARGEM TURISMO - Claude Code Documentation

**Projeto:** Sistema de Cálculo de IVA sobre Margem para Agências de Viagens  
**Status:** Backend 100% funcional | Frontend premium em desenvolvimento  
**Ambiente:** WSL + Windsurf IDE | Deploy: Railway + Vercel  
**Última atualização:** 2025-01-09

---

## 📋 VISÃO GERAL DO PROJETO

Sistema completo para cálculo de IVA sobre margem conforme CIVA Art. 308º, com:
- **Backend:** FastAPI + Python (100% funcional)
- **Frontend:** Alpine.js + Tailwind CSS (upgrade premium planejado)
- **Excel Export:** Multi-folhas com cálculos automáticos
- **Auto-Associação:** Algoritmo de scoring para associar vendas-custos
- **API:** RESTful completa com documentação automática

### 🎯 Fórmula Fiscal Crítica
```python
# ✅ CORRETO - Regime de Margem (CIVA Art. 308º)
IVA = Margem × Taxa / 100

# ❌ ERRADO - Fórmula IVA Incluído (não aplicável)
IVA = Margem × Taxa / (100 + Taxa)
```

---

## 🖥️ AMBIENTE DE DESENVOLVIMENTO

### WSL + Windsurf Setup
```bash
# Verificar ambiente
echo "Sistema: $(uname -a)"
echo "Python: $(which python3)"
echo "Pip: $(which pip3)"
echo "Working dir: $(pwd)"

# Comandos WSL-específicos
PYTHON_CMD="python3"
PIP_CMD="pip3"
VENV_ACTIVATE="source venv/bin/activate"
```

### Estrutura de Pastas
```
iva-margem-turismo/
├── backend/                 # FastAPI backend (FUNCIONAL)
│   ├── app/
│   │   ├── main.py         # API endpoints + mock data
│   │   ├── calculator.py   # Cálculos IVA margem
│   │   ├── excel_export.py # Geração Excel 5 folhas
│   │   ├── models.py       # Pydantic models
│   │   └── saft_parser.py  # Parser XML SAF-T
│   ├── requirements.txt    # Dependencies
│   ├── server.log         # Logs de execução
│   └── venv/              # Virtual environment
├── frontend/               # Frontend Alpine.js (UPGRADE PENDING)
│   ├── index.html         # Interface completa
│   ├── css/
│   ├── js/
│   └── assets/
├── LESSONS_LEARNED.md      # Erros críticos e soluções
├── FRONTEND_PLAN.md        # Plano upgrade premium
└── CLAUDE.md              # Este arquivo
```

---

## 🚀 QUICK START (WSL)

### 1. Iniciar Backend
```bash
cd /mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo/backend
source venv/bin/activate
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificar se iniciou
curl http://localhost:8000/docs
```

### 2. Testar API
- **Docs:** http://localhost:8000/docs
- **Status:** http://localhost:8000/
- **Mock Data:** http://localhost:8000/api/mock-data

### 3. Frontend
```bash
# Abrir no navegador
file:///mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo/frontend/index.html
```

---

## 📊 DADOS REAIS DO PROJETO

### Estatísticas Atuais
- **Vendas:** 26 documentos (Excel modelo)
- **Custos:** 157 documentos (Excel modelo) 
- **Margem Média:** ~14.5% (realista para turismo)
- **Fórmula:** IVA = Margem × 23 / 100

### Mock Data Location
```python
# backend/app/main.py (linha ~200)
mock_data = {
    "sales": [
        {"id": "s1", "number": "NC E2025/2", "amount": -375.0, ...},
        # 26 vendas reais do Excel modelo
    ],
    "costs": [
        {"id": "c1", "supplier": "Gms-Store", "amount": 2955.98, ...},
        # 157 custos reais do Excel modelo
    ]
}
```

---

## 🎨 PLANO UPGRADE PREMIUM (EM PROGRESSO)

### Bibliotecas Modernas Selecionadas

#### Frontend UI (Escolha Final: DaisyUI)
```html
<!-- CDN Setup -->
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet">
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Componentes Premium -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">IVA Margem</h2>
    <div class="stats shadow">
      <div class="stat">
        <div class="stat-title">Total Vendas</div>
        <div class="stat-value text-primary">€125,450</div>
      </div>
    </div>
  </div>
</div>
```

#### Gráficos (Tremor + Chart.js)
```html
<!-- Tremor para dashboards -->
<script src="https://cdn.jsdelivr.net/npm/@tremor/react@latest"></script>

<!-- Chart.js para Excel-style charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0"></script>
```

#### Animações (Framer Motion Web)
```html
<script src="https://cdn.jsdelivr.net/npm/framer-motion@10.18.0/dist/framer-motion.js"></script>
```

### Excel Export Premium
```python
# Bibliotecas avançadas para Excel
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9  # Para formatação avançada
pip install pandas==2.1.3      # Para manipulação dados

# Features premium:
# - Gráficos embebidos
# - Formatação condicional
# - Validação de dados
# - Dashboards Excel
# - Exportação para Power BI
```

---

## 🔧 ENDPOINTS API

### Core Endpoints
```python
POST /api/upload          # Upload SAF-T XML
POST /api/mock-data       # Carregar dados demo
POST /api/associate       # Associar vendas-custos
POST /api/auto-match      # Auto-associação IA
POST /api/calculate       # Calcular + export Excel
GET  /api/session/{id}    # Obter dados sessão
DELETE /api/unlink        # Remover associações
```

### Estrutura Request/Response
```python
# Auto-match request
{
    "session_id": "uuid",
    "threshold": 60  # 0-100, confiança mínima
}

# Calculate request  
{
    "session_id": "uuid",
    "vat_rate": 23  # Taxa IVA
}
```

---

## 🧮 LÓGICA DE CÁLCULOS

### Algoritmo Auto-Associação
```python
def calculate_similarity(sale, cost):
    score = 0
    
    # Data proximity (40%)
    date_diff = abs((sale_date - cost_date).days)
    if date_diff <= 7: score += 40
    elif date_diff <= 30: score += 20
    
    # Client/supplier match (30%)
    if sale.client.lower() in cost.supplier.lower():
        score += 30
    
    # Amount correlation (30%)
    amount_ratio = min(sale.amount, cost.amount) / max(sale.amount, cost.amount)
    score += amount_ratio * 30
    
    return score
```

### Cálculo IVA Margem
```python
class MarginCalculator:
    def __init__(self, vat_rate=23):
        self.vat_rate = vat_rate
    
    def calculate_vat_on_margin(self, sales, costs, associations):
        """Calcula IVA sobre margem conforme CIVA Art. 308º"""
        total_margin = 0
        
        for sale in sales:
            sale_costs = self.get_linked_costs(sale, costs, associations)
            margin = sale.amount - sum(cost.amount for cost in sale_costs)
            
            if margin > 0:  # Só calcular IVA sobre margem positiva
                total_margin += margin
        
        vat_amount = total_margin * self.vat_rate / 100
        return {
            "gross_margin": total_margin,
            "vat_amount": vat_amount,
            "net_margin": total_margin - vat_amount
        }
```

---

## 📱 FRONTEND FEATURES

### Funcionalidades Implementadas
- ✅ Upload drag & drop SAF-T
- ✅ Interface associações many-to-many
- ✅ Auto-match com feedback confiança
- ✅ Cálculos tempo real
- ✅ Export Excel automático
- ✅ Notificações toast elegantes
- ✅ Responsive mobile-first
- ✅ Progress tracking
- ✅ Session persistence

### Upgrade Premium Pendente
```html
<!-- Componentes DaisyUI -->
<div class="drawer lg:drawer-open">
  <div class="drawer-content">
    <!-- Main dashboard -->
    <div class="stats stats-vertical lg:stats-horizontal shadow">
      <div class="stat">
        <div class="stat-figure text-primary">
          <i class="fas fa-chart-line text-3xl"></i>
        </div>
        <div class="stat-title">Total Vendas</div>
        <div class="stat-value text-primary">€125K</div>
        <div class="stat-desc">↗︎ 400 (22%)</div>
      </div>
    </div>
  </div>
</div>
```

---

## 🎯 TAREFAS COMUNS

### Atualizar Mock Data
```python
# Localização: backend/app/main.py
# Substituir mock_data = {...} pelos dados reais

# Validar dados antes
python3 validate_final_data.py
```

### Adicionar Nova Funcionalidade
```python
# 1. Criar endpoint em main.py
@app.post("/api/nova-feature")
async def nova_feature(data: NovaFeatureRequest):
    # Implementação
    return {"result": "success"}

# 2. Adicionar model em models.py
class NovaFeatureRequest(BaseModel):
    session_id: str
    parametros: dict

# 3. Atualizar frontend (index.html)
async novaFeature() {
    const response = await fetch(`${this.apiUrl}/api/nova-feature`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({...})
    });
}
```

### Deploy Railway
```bash
# Backend
cd backend
railway login
railway link [projeto-existente]
railway up

# Variáveis ambiente
railway variables set PYTHON_VERSION=3.11
railway variables set PORT=8000
```

### Deploy Vercel (Frontend)
```bash
# Atualizar apiUrl no index.html
const apiUrl = 'https://seu-backend.railway.app'

# Deploy
cd frontend
vercel --prod
```

---

## ⚠️ ERROS CRÍTICOS E SOLUÇÕES

### WSL Environment Issues
```bash
# ❌ Erro comum
python script.py  # Falha em WSL

# ✅ Solução
python3 script.py

# ❌ Caminho Windows em WSL
C:\Users\Bilal\...

# ✅ Caminho WSL
/mnt/c/Users/Bilal/...
```

### Fórmula IVA Incorreta
```python
# ❌ ERRO CRÍTICO
vat = margin * rate / (100 + rate)  # Fórmula IVA incluído

# ✅ CORRETO
vat = margin * rate / 100  # Regime margem CIVA Art. 308º
```

### Dados Mock Irrealistas
```python
# ❌ Problema
margins = [-228%, 37%]  # Irrealista

# ✅ Solução
margins = [8%, 14.5%, 22%]  # Realista para turismo
```

---

## 🔍 DEBUGGING

### Verificar Estado API
```bash
# Health check
curl http://localhost:8000/

# Obter sessão
curl http://localhost:8000/api/session/[session-id]

# Logs
tail -f backend/server.log
```

### Frontend Debug
```javascript
// Console browser
console.log('App state:', this.$data);
console.log('Sales:', this.sales);
console.log('Selected:', this.selectedSales);
```

### Validar Cálculos
```python
# Teste manual
from app.calculator import MarginCalculator
calc = MarginCalculator(vat_rate=23)
result = calc.calculate_vat_on_margin(sales, costs, associations)
print(f"Margem: €{result['gross_margin']:.2f}")
print(f"IVA: €{result['vat_amount']:.2f}")
```

---

## 📋 DEPLOYMENT CHECKLIST

### Pre-Deploy
- [ ] ✅ Todos os testes passam
- [ ] ✅ Mock data substituído por dados reais
- [ ] ✅ Frontend apiUrl atualizado
- [ ] ✅ Requirements.txt atualizado
- [ ] ✅ Variáveis ambiente configuradas

### Railway Backend
- [ ] ✅ Projeto criado e linkado
- [ ] ✅ PORT=8000 configurado
- [ ] ✅ CORS configurado para frontend domain
- [ ] ✅ Logs monitorizados

### Vercel Frontend
- [ ] ✅ Build settings corretos
- [ ] ✅ API URLs atualizados
- [ ] ✅ CDN assets otimizados
- [ ] ✅ Domain personalizado (opcional)

---

## 🔄 DESENVOLVIMENTO ATIVO

### Estado Atual (2025-01-09)
- ✅ Backend 100% funcional
- ✅ Dados reais do Excel integrados
- ✅ API documentada e testada
- 🔄 Frontend upgrade premium em progresso
- 📋 Deploy planejado para Railway + Vercel

### Próximos Passos
1. **Implementar DaisyUI components** (priority: high)
2. **Adicionar Tremor dashboards** (priority: medium)
3. **Upgrade Excel export** (priority: medium)
4. **Deploy e testes produção** (priority: high)

---

## 🤝 CONVENÇÕES DE CÓDIGO

### Python (Backend)
```python
# Type hints obrigatórios
def calculate_margin(sales: List[Sale], costs: List[Cost]) -> Dict[str, float]:
    pass

# Docstrings para funções públicas
def process_saft_file(file_path: str) -> Dict[str, Any]:
    """
    Processa ficheiro SAF-T e extrai vendas/custos
    
    Args:
        file_path: Caminho para ficheiro XML
        
    Returns:
        Dict com sales, costs e metadata
    """
```

### JavaScript (Frontend)
```javascript
// Alpine.js naming
function ivaApp() {
    return {
        // Camel case para properties
        selectedSales: [],
        totalCosts: 0,
        
        // Camel case para methods
        calculateMargin() {},
        uploadFile() {}
    }
}

// API calls sempre async/await
async uploadFile(file) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return data;
    } catch (error) {
        this.showError('Erro no upload');
    }
}
```

---

## 🔗 RECURSOS ÚTEIS

### Documentação Oficial
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Alpine.js Guide](https://alpinejs.dev/start-here)
- [DaisyUI Components](https://daisyui.com/components/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### APIs Relacionadas
- [CIVA Artigo 308º](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/civa_rep/Pages/iva308.aspx)
- [SAF-T Portugal](https://www.gov.pt/pagina/saf-t)

### Deploy Platforms
- [Railway Deploy Guide](https://railway.app/help)
- [Vercel Documentation](https://vercel.com/docs)

---

## 📞 SUPORTE

### Logs Importantes
```bash
# Backend logs
tail -f backend/server.log

# Browser console (Frontend)
F12 -> Console

# Network requests
F12 -> Network -> Filter XHR
```

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| Backend não inicia | Verificar virtual environment ativo |
| CORS errors | Adicionar frontend domain ao CORS |
| Upload falha | Verificar size limits e file format |
| Cálculos incorretos | Validar fórmula IVA margem |
| WSL command not found | Usar python3/pip3 em vez de python/pip |

---

**🎯 Este projeto representa conhecimento profundo em fiscalidade portuguesa e desenvolvimento full-stack moderno. A arquitetura many-to-many para associações vendas-custos é o core técnico mais complexo.**

**🚀 Ready for production deployment with premium UI upgrade.**