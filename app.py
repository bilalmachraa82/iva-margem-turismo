#!/usr/bin/env python3
"""
Render deployment entry point
Imports and exposes the FastAPI app from backend
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from app.main import app

# Export the app for Render
__all__ = ["app"]