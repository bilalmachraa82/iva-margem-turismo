#!/usr/bin/env python3
"""
Entry point para Render deployment
Redireciona para o app principal no diretório backend
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Mudar para o diretório backend
os.chdir(backend_dir)

# Importar e executar o app
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)