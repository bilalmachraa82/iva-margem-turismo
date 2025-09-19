# Vercel Function wrapper for FastAPI
import os
import sys
from pathlib import Path

# Ensure backend package is importable when running on Vercel
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

try:
    from app.main import app
    # Vercel expects a function called 'handler'
    handler = app
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current path: {current_dir}")
    print(f"Backend path: {backend_path}")
    print(f"Sys path: {sys.path}")

    # Fallback simple handler for debugging
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"message": "API is running but backend import failed", "error": str(e)}

    handler = app
