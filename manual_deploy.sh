#!/bin/bash

# 🚀 Script de Deploy Manual no Render
# Este script vai abrir o browser com os links corretos para deploy

echo "🚀 DEPLOY MANUAL NO RENDER"
echo "=========================="
echo ""
echo "📋 INSTRUÇÕES PASSO A PASSO:"
echo ""
echo "1. 🌐 Abre o Render: https://render.com"
echo "2. 👤 Faz login com GitHub"
echo "3. ➕ Clica em 'New' → 'Web Service'"
echo ""
echo "🔧 CONFIGURAÇÃO DO BACKEND:"
echo "   📛 Nome: iva-margem-backend"
echo "   🔧 Build Command: cd backend && pip install -r requirements.txt"
echo "   🚀 Start Command: cd backend && ./render_start.sh"
echo "   🏥 Health Check: /api/health"
echo ""
echo "🔧 CONFIGURAÇÃO DO FRONTEND:"
echo "   📛 Nome: iva-margem-frontend"
echo "   📁 Tipo: Static Site"
echo "   📂 Publish Directory: frontend"
echo ""
echo "🔗 URLS ESPERADAS:"
echo "   Backend: https://iva-margem-backend.onrender.com"
echo "   Frontend: https://iva-margem-frontend.onrender.com"
echo ""
echo "🧪 TESTAR APÓS DEPLOY:"
echo "   curl https://iva-margem-backend.onrender.com/api/health"
echo ""
echo "📁 Ficheiros preparados:"
echo "   ✅ render.yaml"
echo "   ✅ backend/render_start.sh"
echo "   ✅ DEPLOY_RENDER_GUIDE.md"
echo ""
echo "Abrir o Render no browser? (s/n)"
read -r resposta

if [[ "$resposta" == "s" ]]; then
    echo "🌐 A abrir o Render..."
    
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "https://render.com"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open "https://render.com"
    else
        echo "Por favor, abre manualmente: https://render.com"
    fi
fi

echo ""
echo "🎯 Boa sorte com o deploy! 🚀"
echo "📖 Consulta DEPLOY_RENDER_GUIDE.md para mais detalhes"