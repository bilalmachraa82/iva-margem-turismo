# 🚀 COMO LANÇAR A APLICAÇÃO (FORMA SIMPLES)

## Para Windows (PowerShell ou CMD):

### 1️⃣ Abrir Terminal no diretório do projeto:
```
cd C:\Users\Bilal\Documents\aiparati\claudia\iva-margem-turismo
```

### 2️⃣ Iniciar o Backend:
```cmd
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Deve aparecer: `Uvicorn running on http://0.0.0.0:8000`

### 3️⃣ Abrir o Frontend:
- Abrir o ficheiro diretamente no navegador:
  `C:\Users\Bilal\Documents\aiparati\claudia\iva-margem-turismo\frontend\index.html`

### 4️⃣ Testar:
1. No frontend, clicar em "Usar dados de demonstração"
2. Selecionar vendas e custos
3. Clicar em "Associar Selecionados"
4. Clicar em "Calcular e Exportar"

---

## 🔧 Se houver problemas:

### Porta já em uso:
```cmd
# Verificar o que está a usar a porta 8000:
netstat -ano | findstr :8000

# Matar o processo (substituir PID pelo número encontrado):
taskkill /F /PID [PID]
```

### Ambiente virtual não ativa:
```cmd
# Recriar ambiente:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### API não responde:
- Verificar se o backend mostra erros no terminal
- Tentar: http://localhost:8000/docs

---

## 📝 Notas Importantes:

1. **NÃO usar WSL** para executar o servidor (problemas de rede)
2. **Usar CMD ou PowerShell nativo** do Windows
3. **Um terminal para backend, browser para frontend**
4. **Manter simples** - sem scripts, sem automação

---

## ✅ Checklist de Sucesso:

- [ ] Backend mostra: "Application startup complete"
- [ ] http://localhost:8000/docs abre no browser
- [ ] Frontend carrega sem erros
- [ ] Botão "Usar dados de demonstração" funciona
- [ ] Excel é gerado ao calcular

Se tudo isto funcionar, a aplicação está 100% operacional! 🎉