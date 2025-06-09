#!/bin/bash
# Script corrigido para lançar backend em ambiente WSL
# Versão WSL-aware com fallbacks robustos

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warning() { echo -e "${YELLOW}⚠️${NC} $*"; }
error() { echo -e "${RED}❌${NC} $*"; }

# Detectar ambiente
detect_environment() {
    log "Detectando ambiente..."
    
    echo "Sistema: $(uname -s)"
    echo "Kernel: $(uname -r)"
    echo "Working dir: $(pwd)"
    
    # Verificar se é WSL
    if [[ "$(uname -r)" == *"microsoft"* ]]; then
        echo "🐧 Ambiente WSL detectado"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
        VENV_ACTIVATE="source venv/bin/activate"
        return 0
    else
        echo "🐧 Ambiente Linux nativo detectado"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
        VENV_ACTIVATE="source venv/bin/activate"
        return 0
    fi
}

# Verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."
    
    # Verificar Python3
    if ! command -v $PYTHON_CMD &> /dev/null; then
        error "$PYTHON_CMD não encontrado"
        error "Instale Python3: sudo apt update && sudo apt install python3"
        exit 1
    fi
    
    python_version=$($PYTHON_CMD --version)
    success "Python encontrado: $python_version"
    
    # Verificar se estamos na pasta correta
    if [[ ! -d "backend" ]]; then
        error "Pasta 'backend' não encontrada"
        error "Execute este script na raiz do projeto iva-margem-turismo"
        exit 1
    fi
    
    success "Pasta backend encontrada"
}

# Configurar ambiente virtual
setup_venv() {
    log "Configurando ambiente virtual..."
    
    cd backend
    
    # Criar venv se não existir
    if [[ ! -d "venv" ]]; then
        warning "Ambiente virtual não existe, criando..."
        $PYTHON_CMD -m venv venv
        success "Ambiente virtual criado"
    fi
    
    # Ativar ambiente virtual
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        success "Ambiente virtual ativado"
    else
        error "Arquivo de ativação não encontrado: venv/bin/activate"
        exit 1
    fi
    
    # Verificar pip no venv
    if ! command -v pip &> /dev/null; then
        warning "pip não encontrado no venv, instalando..."
        $PYTHON_CMD -m ensurepip --upgrade || {
            error "Falha ao instalar pip"
            exit 1
        }
    fi
    
    # Instalar dependências
    if [[ -f "requirements.txt" ]]; then
        log "Instalando dependências..."
        pip install -r requirements.txt
        success "Dependências instaladas"
    else
        warning "requirements.txt não encontrado"
    fi
}

# Verificar se servidor já está rodando
check_server() {
    log "Verificando se servidor já está ativo..."
    
    if curl -s -f http://localhost:8000/api/health > /dev/null 2>&1; then
        warning "Servidor já está rodando em http://localhost:8000"
        echo "Para parar: pkill -f 'uvicorn.*main:app'"
        return 1
    fi
    
    success "Porta 8000 disponível"
    return 0
}

# Iniciar servidor
start_server() {
    log "Iniciando servidor FastAPI..."
    
    cd app
    
    # Verificar se main.py existe
    if [[ ! -f "main.py" ]]; then
        error "main.py não encontrado em backend/app/"
        exit 1
    fi
    
    # Iniciar servidor
    log "Executando: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    success "🚀 Servidor iniciando..."
    success "📍 API: http://localhost:8000"
    success "📍 Docs: http://localhost:8000/docs"
    echo ""
    
    # Executar servidor (bloqueante)
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Função principal
main() {
    echo "🎯 IVA MARGEM TURISMO - BACKEND LAUNCHER (WSL)"
    echo "=" * 50
    
    detect_environment
    check_prerequisites
    
    if check_server; then
        setup_venv
        start_server
    fi
}

# Trap para cleanup
cleanup() {
    echo ""
    log "Parando servidor..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi