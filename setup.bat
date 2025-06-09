@echo off
echo =========================================
echo IVA Margem Turismo - Setup Windows
echo =========================================
echo.

cd backend

echo Criando ambiente virtual...
python -m venv venv

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo =========================================
echo INSTALACAO COMPLETA!
echo =========================================
echo.
echo Para executar o servidor:
echo   1. cd backend\app
echo   2. uvicorn main:app --reload
echo.
echo Depois abra no browser:
echo   http://localhost:8000
echo   http://localhost:8000/docs
echo.
pause