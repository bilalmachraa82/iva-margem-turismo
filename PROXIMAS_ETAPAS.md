# 📋 PRÓXIMAS ETAPAS - IVA Margem Turismo

## ✅ ESTADO ATUAL (100% Funcional)

### O que temos:
- ✅ Backend FastAPI funcionando com 157 custos + 26 vendas
- ✅ Frontend limpo e moderno (branco, minimalista)
- ✅ Associações many-to-many funcionando
- ✅ Cálculos IVA sobre margem corretos
- ✅ Export Excel completo
- ✅ Branding Accounting Advantage

### Como usar:
```bash
# Terminal 1 - Backend
cd backend
python3 -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd /mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo
python3 -m http.server 8080

# Navegador
http://localhost:8080/frontend/
```

---

## 🚀 FASE 1: QUICK WINS (1 semana)

### 1. Preview de Cálculos (2 dias)
```javascript
// Adicionar card que mostra em tempo real:
- Margem atual: €X
- IVA estimado: €Y  
- Economia vs regime normal: €Z
```

### 2. Indicadores Visuais (1 dia)
```css
/* Vendas com associações */
.has-associations {
  border-left: 4px solid green;
}

/* Badge com número */
.association-count {
  position: absolute;
  top: -8px;
  right: -8px;
}
```

### 3. Tooltips Informativos (1 dia)
```html
<i class="fas fa-info-circle" 
   title="IVA Margem: Paga IVA apenas sobre lucro">
</i>
```

### 4. Filtros Avançados (1 dia)
- Por data (date picker)
- Por valor (min/max)
- Por estado (associado/não)
- Por tipo documento

### 5. Exportar PDF (1 dia)
```python
pip install reportlab
# Gerar PDF além de Excel
```

---

## 🗄️ FASE 2: PERSISTÊNCIA (1 semana)

### 1. Guardar em Ficheiros JSON
```python
# Em vez de memória, guardar em:
data/
  sessions/
    {session_id}.json
  history/
    {user_email}_history.json
```

### 2. Histórico de Cálculos
- Últimos 50 cálculos
- Nome, data, resumo
- Possibilidade de reabrir

### 3. Templates de Associações
- Guardar padrões comuns
- "Hotel + Voo = Pacote"
- Reutilizar em novos cálculos

---

## 🔐 FASE 3: SEGURANÇA BÁSICA (1 semana)

### 1. Login Simples
```python
# Sem complicações - email/password
# Guardar em JSON encriptado
# Opcional no início
```

### 2. Validações
- Tamanho máximo ficheiro: 50MB
- Formato SAF-T válido
- Datas coerentes

### 3. Rate Limiting
- Max 100 requests/min
- Evitar DoS

---

## 🎯 FASE 4: MELHORIAS UX (2 semanas)

### 1. Drag & Drop Melhorado
- Arrastar custos para vendas
- Visual feedback
- Multi-seleção

### 2. Bulk Actions
- Associar múltiplas de uma vez
- Desassociar tudo
- Copiar associações

### 3. Dashboard Resumo
- KPIs principais
- Gráficos simples
- Timeline visual

### 4. Mobile Responsive
- Tabelas adaptativas
- Swipe actions
- Touch friendly

---

## 🚫 NÃO FAZER AGORA

### Evitar Complexidade:
- ❌ PostgreSQL (desnecessário para <1000 users)
- ❌ Autenticação OAuth/Social
- ❌ Multi-idioma
- ❌ API pública
- ❌ IA/ML complexo
- ❌ Microserviços

### Focar em:
- ✅ Funcionalidade que já temos
- ✅ Melhorias incrementais
- ✅ Feedback dos utilizadores
- ✅ Estabilidade

---

## 📊 MÉTRICAS DE SUCESSO

### Objetivos Fase 1:
- Preview reduz confusão em 80%
- Filtros poupam 50% tempo
- PDF evita abrir Excel

### Objetivos Fase 2:
- Zero perda de dados
- Histórico usado 3x/semana
- Templates poupam 30min/uso

### Objetivos Fase 3:
- Zero acessos não autorizados
- 100% ficheiros validados
- Zero crashes por DoS

---

## 🛠️ STACK TECNOLÓGICO

### Manter Simples:
```
Backend:  FastAPI + Python (✅)
Frontend: Alpine.js + Tailwind (✅)
Storage:  JSON files → PostgreSQL (futuro)
Auth:     Basic → JWT (futuro)
Deploy:   Railway + Vercel
```

### Dependências Novas:
```bash
# Fase 1
pip install reportlab  # PDF

# Fase 2  
# Nenhuma - usar JSON nativo

# Fase 3
pip install python-jose[cryptography]  # JWT
pip install slowapi  # Rate limiting
```

---

## 📅 CRONOGRAMA SUGERIDO

### Janeiro 2025:
- Semana 2: Quick Wins 1-3
- Semana 3: Quick Wins 4-5
- Semana 4: Testes com users

### Fevereiro 2025:
- Semana 1-2: Persistência
- Semana 3-4: Segurança básica

### Março 2025:
- Deploy produção
- Feedback e ajustes
- Planear v3.0

---

## 💡 NOTAS IMPORTANTES

1. **Cada feature deve ser independente** - não quebrar o que funciona
2. **Testar com dados reais** antes de implementar
3. **Documentar mudanças** no CLAUDE.md
4. **Backup antes de grandes mudanças**
5. **User feedback é rei** - ouvir contabilistas

---

## ✅ PRÓXIMO PASSO IMEDIATO

1. Confirmar que tudo funciona 100%
2. Fazer backup completo
3. Começar com Preview de Cálculos
4. Testar com 1 utilizador real
5. Iterar baseado em feedback

**Lembre-se: Better done than perfect! 🚀**