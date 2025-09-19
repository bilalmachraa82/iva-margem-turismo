"""
Vercel-optimized handler with graceful degradation
Removes heavy dependencies that might cause issues
"""

import os
import sys
from pathlib import Path

# Add backend to path
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

# Set environment flags for lighter mode
os.environ["VERCEL_DEPLOYMENT"] = "1"
os.environ["DISABLE_HEAVY_DEPENDENCIES"] = "1"

# Import with fallbacks
try:
    from app.main import app
    print("✅ FastAPI app loaded successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Create minimal app if main fails
    from fastapi import FastAPI
    app = FastAPI(title="IVA Margem Turismo - Serverless")

    @app.get("/")
    async def root():
        return {
            "message": "IVA Margem Turismo API",
            "status": "serverless",
            "mode": "degraded"
        }

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "mode": "serverless"}

# Export for Vercel
handler = app