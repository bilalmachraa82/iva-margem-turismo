#!/bin/bash
# Script robusto para lançar a aplicação IVA Margem Turismo
# Aplicando lições aprendidas

set -euo pipefail  # Strict mode

# Configuração
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKEND_DIR="$SCRIPT_DIR/backend"
readonly FRONTEND_FILE="$SCRIPT_DIR/frontend/index.html"
readonly SERVER_PORT=8000
readonly SERVER_HOST="localhost"

# Funções utilitárias
log() { echo "[$(date +'%H:%M:%S')] $*"; }
error() { log "❌ ERRO: $*" >&2; }
success() { log "✅ $*"; }

# Verificar dependências
check_dependencies() {
    log "🔍 Verificando dependências..."
    
    [ -d "$BACKEND_DIR" ] || { error "Backend não encontrado: $BACKEND_DIR"; exit 1; }
    [ -f "$FRONTEND_FILE" ] || { error "Frontend não encontrado: $FRONTEND_FILE"; exit 1; }
    
    cd "$BACKEND_DIR"
    [ -f "requirements.txt" ] || { error "requirements.txt não encontrado"; exit 1; }
    
    success "Dependências verificadas"
}

# Verificar se servidor está ativo
is_server_running() {
    curl -s -f "http://$SERVER_HOST:$SERVER_PORT/docs" > /dev/null 2>&1
}

# Iniciar servidor backend
start_backend() {
    log "🚀 Iniciando servidor backend..."
    
    cd "$BACKEND_DIR"
    
    # Verificar se já está rodando
    if is_server_running; then
        success "Servidor já está ativo"
        return 0
    fi
    
    # Ativar ambiente virtual
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log "Ambiente virtual Linux ativado"
    elif [ -f "venv/Scripts/activate.bat" ]; then
        log "Ambiente Windows detectado"
        # Para WSL com Windows, usar cmd.exe
        if command -v cmd.exe > /dev/null; then
            log "Usando cmd.exe para ativar ambiente virtual..."
        else
            error "Ambiente Windows detectado mas cmd.exe não disponível"
            exit 1
        fi
    else
        error "Ambiente virtual não encontrado"
        log "Execute primeiro: python -m venv venv && pip install -r requirements.txt"
        exit 1
    fi
    
    # Iniciar servidor
    log "Iniciando uvicorn..."
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $SERVER_PORT > server.log 2>&1 &
    local server_pid=$!
    
    # Aguardar inicialização (máximo 30 segundos)
    log "⏳ Aguardando servidor inicializar..."
    for i in {1..30}; do
        if is_server_running; then
            success "Servidor iniciado (PID: $server_pid, Porta: $SERVER_PORT)"
            echo $server_pid > server.pid
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    # Se chegou aqui, falhou
    error "Servidor não iniciou em 30 segundos"
    error "Log do servidor:"
    cat server.log
    kill $server_pid 2>/dev/null || true
    exit 1
}

# Abrir frontend
open_frontend() {
    log "🌐 Abrindo frontend..."
    
    local frontend_url="file://$FRONTEND_FILE"
    
    # Detectar SO e abrir navegador
    if command -v xdg-open > /dev/null; then
        xdg-open "$frontend_url"
    elif command -v open > /dev/null; then
        open "$frontend_url"
    elif command -v cmd.exe > /dev/null; then
        # Para WSL, usar cmd.exe do Windows
        cmd.exe /c "start \"\" \"$frontend_url\""
    else
        log "⚠️  Não foi possível abrir automaticamente"
        log "   Abra manualmente no navegador:"
        log "   $frontend_url"
        return 1
    fi
    
    success "Frontend aberto no navegador"
}

# Função principal
main() {
    log "🎯 Iniciando IVA Margem Turismo..."
    log "Aplicando lições aprendidas para lançamento robusto..."
    
    check_dependencies
    start_backend
    sleep 2  # Dar tempo para servidor estabilizar
    open_frontend
    
    success "🎉 Aplicação iniciada com sucesso!"
    log ""
    log "📍 URLs importantes:"
    log "   Backend API: http://$SERVER_HOST:$SERVER_PORT"
    log "   Documentação: http://$SERVER_HOST:$SERVER_PORT/docs"
    log "   Frontend: file://$FRONTEND_FILE"
    log ""
    log "🔧 Para parar o servidor:"
    log "   kill \$(cat $BACKEND_DIR/server.pid)"
    log ""
    log "📊 Para monitorar:"
    log "   tail -f $BACKEND_DIR/server.log"
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi