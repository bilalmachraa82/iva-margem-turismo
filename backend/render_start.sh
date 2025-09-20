#!/bin/bash

echo "🚀 Iniciando aplicação IVA Margem Turismo no Render..."

# Verificar variáveis obrigatórias
if [ -z "$PORT" ]; then
    echo "❌ PORT não definida, usando 8000"
    export PORT=8000
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p uploads temp temp/sessions

# Iniciar aplicação
echo "🎯 Iniciando servidor..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
