# Vercel Function wrapper for FastAPI
import os
import sys
from pathlib import Path

# Ensure backend package is importable when running on Vercel
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from app.main import app

# Vercel expects a function called 'handler'
handler = app
