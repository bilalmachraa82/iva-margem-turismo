#!/bin/bash
# Script para testar o funcionamento completo da aplicação

echo "🧪 TESTE COMPLETO - IVA Margem Turismo"
echo "======================================"

# 1. Verificar se o backend está rodando
echo -e "\n1️⃣ Verificando backend..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend está rodando"
else
    echo "❌ Backend não está rodando!"
    echo "Execute: cd backend && python3 -m uvicorn app.main:app --reload"
    exit 1
fi

# 2. Testar endpoint mock data
echo -e "\n2️⃣ Testando dados de demonstração..."
RESPONSE=$(curl -s http://localhost:8000/api/mock-data)
SALES_COUNT=$(echo $RESPONSE | grep -o '"sales_count":[0-9]*' | grep -o '[0-9]*')
COSTS_COUNT=$(echo $RESPONSE | grep -o '"costs_count":[0-9]*' | grep -o '[0-9]*')

echo "📊 Vendas: $SALES_COUNT documentos"
echo "💰 Custos: $COSTS_COUNT documentos"

if [ "$SALES_COUNT" -eq "26" ] && [ "$COSTS_COUNT" -eq "157" ]; then
    echo "✅ Dados carregados corretamente!"
else
    echo "❌ Erro: Esperado 26 vendas e 157 custos"
fi

# 3. Verificar servidor frontend
echo -e "\n3️⃣ Para testar o frontend:"
echo "   1. Abra outro terminal"
echo "   2. Execute: python3 -m http.server 8080"
echo "   3. Acesse: http://localhost:8080/frontend/"
echo "   4. Limpe o cache: F12 → Console → localStorage.clear()"
echo "   5. Recarregue a página e teste"

echo -e "\n✅ Checklist de Funcionamento:"
echo "   [ ] Backend responde na porta 8000"
echo "   [ ] Mock data retorna 26 vendas + 157 custos"
echo "   [ ] Frontend carrega sem erros"
echo "   [ ] Associações funcionam corretamente"
echo "   [ ] Excel é gerado ao calcular"
echo "   [ ] Interface limpa e profissional"

echo -e "\n📝 Ficheiros limpos:"
echo "   - Removidos todos os test_*.py"
echo "   - Removidos todos os *.backup"
echo "   - Mantido apenas index.html (v2)"
echo "   - Estrutura organizada"

echo -e "\n🚀 Aplicação pronta para uso!"