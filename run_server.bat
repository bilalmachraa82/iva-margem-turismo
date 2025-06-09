@echo off
echo Iniciando servidor IVA Margem...
cd backend
call venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000