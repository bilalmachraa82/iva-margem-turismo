# Vercel Function wrapper for FastAPI
from app.main import app

# Vercel expects a function called 'handler'
handler = app