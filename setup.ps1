# Script para testar o backend
Write-Host "IVA Margem Turismo - Setup e Teste" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Verificar se estamos na pasta correta
$currentPath = Get-Location
Write-Host "Pasta atual: $currentPath" -ForegroundColor Yellow

# Entrar na pasta backend
Set-Location "backend"

# Criar ambiente virtual se não existir
if (-not (Test-Path "venv")) {
    Write-Host "`nCriando ambiente virtual..." -ForegroundColor Cyan
    python -m venv venv
}

# Ativar ambiente virtual
Write-Host "`nAtivando ambiente virtual..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Instalar dependências
Write-Host "`nInstalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

# Informações para o utilizador
Write-Host "`n======================================" -ForegroundColor Green
Write-Host "SETUP COMPLETO!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "`nPara executar o servidor:" -ForegroundColor Yellow
Write-Host "cd app" -ForegroundColor White
Write-Host "uvicorn main:app --reload" -ForegroundColor White
Write-Host "`nDepois abra:" -ForegroundColor Yellow
Write-Host "http://localhost:8000" -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor White