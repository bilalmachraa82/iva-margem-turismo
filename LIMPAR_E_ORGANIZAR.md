# 🧹 LIMPEZA E ORGANIZAÇÃO DO PROJETO

## 📁 FICHEIROS A MANTER

### Backend (/backend)
✅ **app/** - Código principal
  - main.py - API endpoints
  - calculator.py - Lógica de cálculo
  - excel_export.py - Geração Excel
  - models.py - Modelos de dados
  - saft_parser.py - Parser XML

✅ **requirements.txt** - Dependências Python
✅ **temp/** - Pasta para ficheiros temporários
✅ **uploads/** - Pasta para uploads SAF-T

### Frontend (/frontend)
✅ **index_v2.html** - Interface principal (USAR ESTE!)
✅ **assets/** - Imagens e recursos
✅ **css/** - Estilos (se existir)
✅ **js/** - Scripts (se existir)

### Raiz (/)
✅ **README.md** - Documentação principal
✅ **CLAUDE.md** - Instruções para Claude
✅ **launch_app.sh** - Script de lançamento

## 🗑️ FICHEIROS A REMOVER

### Frontend
❌ **index.html** - Versão antiga (substituída por index_v2.html)
❌ **test_associations.html** - Apenas para testes

### Backend
❌ **test_*.py** - Ficheiros de teste temporários
❌ **check_*.py** - Scripts de verificação
❌ ***.backup** - Ficheiros backup
❌ **get-pip.py** - Não necessário
❌ **serve_frontend.py** - Temporário
❌ **clear_cache.html** - Temporário
❌ **test_frontend.html** - Temporário

### Raiz
❌ **MOCK_DATA.md** - Dados já integrados
❌ **excel_mock_converted.json** - Já integrado no main.py
❌ **UPDATE_FRONTEND.md** - Info temporária
❌ **SOLUCAO_7_DOCUMENTOS.md** - Problema resolvido

## 🔧 PROBLEMA: Só aparecem 7 documentos no index_v2.html

### Causa
Cache do localStorage com dados antigos

### Solução Imediata
1. Abrir o navegador
2. Pressionar F12 → Console
3. Executar:
```javascript
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### Verificação
```javascript
// No console, após carregar dados demo:
console.log('Sales:', Alpine.$data(document.querySelector('[x-data]')).sales.length);
console.log('Costs:', Alpine.$data(document.querySelector('[x-data]')).costs.length);
```

## 🚀 COMO USAR A APLICAÇÃO

### 1. Iniciar Backend
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Iniciar Servidor Frontend
```bash
cd /mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo
python3 -m http.server 8080
```

### 3. Aceder à Aplicação
```
http://localhost:8080/frontend/index_v2.html
```

### 4. Testar
1. Clicar "Usar Dados de Demonstração"
2. Verificar: 26 vendas + 157 custos
3. Associar vendas com custos
4. Gerar Excel

## 📋 PRÓXIMAS ETAPAS

### Fase 1: Estabilização (Esta Semana)
1. ✅ Limpar ficheiros desnecessários
2. ✅ Resolver cache localStorage
3. ✅ Documentar uso correto
4. ⏳ Testar fluxo completo

### Fase 2: Melhorias Quick Win (Próxima Semana)
1. 📊 Preview de cálculos em tempo real
2. 🎨 Indicadores visuais de associações
3. 💡 Tooltips explicativos
4. 🔍 Filtros avançados

### Fase 3: Features Novas (Depois)
1. 💾 Persistência com ficheiros JSON
2. 📄 Export PDF
3. ↩️ Undo/Redo
4. 📱 Melhorias mobile

## ✅ CHECKLIST DE FUNCIONAMENTO

- [ ] Backend inicia sem erros
- [ ] Frontend carrega corretamente
- [ ] Dados demo mostram 26 vendas + 157 custos
- [ ] Associações funcionam
- [ ] Excel é gerado com cálculos corretos
- [ ] Interface é limpa e profissional

## 🆘 PROBLEMAS COMUNS

### "Command not found"
```bash
# Usar python3 em vez de python
python3 script.py
```

### "CORS error"
```bash
# Usar servidor HTTP em vez de file://
python3 -m http.server 8080
```

### "Só vejo 7 documentos"
```javascript
// Limpar cache do navegador
localStorage.clear();
location.reload();
```