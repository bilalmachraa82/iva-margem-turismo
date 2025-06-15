@echo off
echo ================================================
echo   IVA MARGEM TURISMO - ARRANQUE WINDOWS
echo ================================================
echo.

echo [1] A iniciar backend (API)...
cd backend
start cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [2] Backend iniciado na porta 8000
echo.
echo [3] A abrir frontend no browser...
timeout /t 3 >nul
start "" "%CD%\..\frontend\index.html"

echo.
echo ================================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ================================================
echo.
echo URLs:
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Frontend: file:///%CD%\..\frontend\index.html
echo.
echo Para parar o servidor: Ctrl+C na janela do backend
echo.
pause