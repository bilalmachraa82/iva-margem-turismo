"""
Main FastAPI application for IVA Margem Turismo
API for VAT margin calculation for travel agencies
Python 3.9.1 - Render deployment
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import uuid
import json
import shutil
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging
from contextlib import asynccontextmanager
import io
from pathlib import Path

# Import app modules
from .models import (
    Sale, Cost, Association, CalculationRequest,
    AIMatchRequest, UnlinkRequest, UploadResponse,
    CalculationResult, AIMatchResult, PeriodCalculateRequest,
    CompanyInfo, PDFExportRequest, ErrorDetail, ErrorResponse
)
from .saft_parser import SAFTParser
from .efatura_parser import EFaturaParser
from .calculator import VATCalculator
from .excel_export import ExcelExporter
from .validators import DataValidator
from .pdf_export_professional import generate_pdf_report as generate_professional_pdf_report
from .pdf_export_enhanced import generate_enhanced_pdf_report
from .pdf_export_premium import generate_premium_pdf_report
from .pdf_pipeline import render_pdf_from_html, resolve_company_payload, sanitize_company_name
from .period_calculator import PeriodVATCalculator
from .analytics import PremiumAnalytics, AdvancedKPICalculator
from .kv_store import kv
from .company_config import company_config, CompanyInfo, apply_company_profile, COMPANY_PROFILES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DISABLE_CHARTS = os.getenv("DISABLE_CHARTS") == "1"

if not DISABLE_CHARTS:
    try:  # pragma: no cover - diagnostic guard
        from .chart_generator import generate_financial_charts
    except Exception as exc:
        logger.warning("Chart generator indisponível (%s). A desativar gráficos opcionais.", exc)

        def generate_financial_charts(*args, **kwargs):  # type: ignore
            return {}
else:
    logger.info("Chart generator desativado (DISABLE_CHARTS=1).")

    def generate_financial_charts(*args, **kwargs):  # type: ignore
        return {}

# Runtime environment
IS_VERCEL = bool(os.getenv("VERCEL"))

# Directories (use /tmp on Vercel)
TEMP_DIR = Path('/tmp') if IS_VERCEL else Path('temp')
UPLOAD_DIR = TEMP_DIR / 'uploads'

# Session storage (in-memory fallback; KV used on Vercel when configured)
sessions = {}

SESSION_TTL_SECONDS = 24 * 3600

async def set_session_store(session_id: str, value: Dict) -> None:
    if IS_VERCEL and kv.enabled:
        await kv.set_json(f"session:{session_id}", value, ttl=SESSION_TTL_SECONDS)
    else:
        sessions[session_id] = value

async def get_session_store(session_id: str) -> Optional[Dict]:
    if IS_VERCEL and kv.enabled:
        return await kv.get_json(f"session:{session_id}")
    return sessions.get(session_id)

async def has_session_store(session_id: str) -> bool:
    rec = await get_session_store(session_id)
    return rec is not None

async def delete_session_store(session_id: str) -> None:
    if IS_VERCEL and kv.enabled:
        await kv.delete(f"session:{session_id}")
    else:
        sessions.pop(session_id, None)

async def clear_sessions_store() -> None:
    # Avoid global clears on KV to prevent cross-user data loss; no-op on Vercel
    if not (IS_VERCEL and kv.enabled):
        sessions.clear()

# Global reference to cleanup task
cleanup_task = None


async def periodic_cleanup():
    """Run cleanup every hour"""
    while True:
        try:
            await asyncio.sleep(3600)  # Wait 1 hour
            clean_old_files()
            logger.info("Periodic cleanup completed")
        except asyncio.CancelledError:
            logger.info("Periodic cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {str(e)}")
            # Continue running even if there's an error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global cleanup_task
    
    # Startup
    logger.info("Starting IVA Margem Turismo API...")
    
    # Ensure required directories exist
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clean old temp files
    clean_old_files()
    
    # Start periodic cleanup task (skip on Vercel serverless)
    if not IS_VERCEL:
        cleanup_task = asyncio.create_task(periodic_cleanup())
        logger.info("Started periodic cleanup task")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    
    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    

# Create FastAPI app
app = FastAPI(
    title="IVA Margem Turismo API",
    description="Sistema de cálculo de IVA sobre margem para agências de viagens",
    version="1.0.0",
    lifespan=lifespan
)

# Serve frontend statically in development to avoid CORS during local testing
try:
    FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
    if FRONTEND_DIR.exists():
        app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
        logger.info(f"Mounted frontend at /frontend from {FRONTEND_DIR}")
        # Dev convenience: redirect root to frontend index
        @app.get("/")
        async def root_index_redirect():
            return RedirectResponse(url="/frontend/index.html")
except Exception as _e:
    logger.warning(f"Could not mount frontend static dir: {_e}")

# Configure CORS with environment-based settings
def get_cors_origins():
    """Get allowed CORS origins from environment or defaults"""
    env_origins = os.getenv('CORS_ORIGINS', '')
    if env_origins:
        return env_origins.split(',')

    # Development defaults
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "*",  # dev fallback
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With"
    ],
    expose_headers=["Content-Disposition"],  # For file downloads
    max_age=600,  # Cache preflight for 10 minutes
)


# Enhanced error handling
def create_error_response(code: str, message: str, details: dict = None, request_id: str = None):
    """Create standardized error response"""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=ErrorDetail(code=code, message=message, details=details),
            request_id=request_id
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    request_id = str(uuid.uuid4())[:8]
    logger.warning(f"Validation error [{request_id}]: {exc.errors()}")

    details = {
        "errors": exc.errors(),
        "body": str(exc.body) if hasattr(exc, 'body') else None
    }

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid request data",
                details=details
            ),
            request_id=request_id
        ).dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with standardized format"""
    request_id = str(uuid.uuid4())[:8]

    # Map status codes to error codes
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        413: "FILE_TOO_LARGE",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR"
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=error_codes.get(exc.status_code, "HTTP_ERROR"),
                message=str(exc.detail),
                details={"status_code": exc.status_code}
            ),
            request_id=request_id
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = str(uuid.uuid4())[:8]
    logger.error(f"Unexpected error [{request_id}]: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details={"request_id": request_id}
            ),
            request_id=request_id
        ).dict()
    )


def clean_old_files():
    """Clean temporary files and sessions older than 24 hours"""
    try:
        now = datetime.now()
        
        # Clean old files
        cleaned_files = 0
        for folder in [TEMP_DIR, UPLOAD_DIR]:
            if folder.exists():
                for filename in os.listdir(folder):
                    filepath = folder / filename
                    if filepath.is_file():
                        file_time = datetime.fromtimestamp(filepath.stat().st_ctime)
                        if now - file_time > timedelta(hours=24):
                            try:
                                filepath.unlink()
                                cleaned_files += 1
                                logger.debug(f"Removed old file: {filepath}")
                            except Exception:
                                pass
        
        # Skip session cleanup on Vercel; rely on KV TTL. Local: cleanup in-memory sessions
        cleaned_sessions = 0
        if not (IS_VERCEL and kv.enabled):
            sessions_to_remove = []
            for session_id, session_data in sessions.items():
                created_at_str = session_data.get("created_at", "")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                        if now - created_at > timedelta(hours=24):
                            sessions_to_remove.append(session_id)
                    except Exception:
                        sessions_to_remove.append(session_id)
            for session_id in sessions_to_remove:
                sessions.pop(session_id, None)
                cleaned_sessions += 1

        if cleaned_files > 0 or cleaned_sessions > 0:
            logger.info(f"Cleanup completed: {cleaned_files} files, {cleaned_sessions} sessions removed")
            
    except Exception as e:
        logger.error(f"Error cleaning old files: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "API IVA Margem Turismo a funcionar!",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "upload_efatura": "/api/upload-efatura",
            "associate": "/api/associate",
            "calculate": "/api/calculate",
            "diagnostics": "/api/diagnostics/{session_id}",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    temp_files_count = 0
    try:
        temp_files_count = len(list(TEMP_DIR.iterdir())) if TEMP_DIR.exists() else 0
    except Exception:
        temp_files_count = 0
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions_active": None if (IS_VERCEL and kv.enabled) else len(sessions),
        "temp_files": temp_files_count
    }


@app.get("/api/diagnostics/{session_id}")
async def diagnostics(session_id: str, vat_rate: float = 23.0):
    """Run integrity checks and reconciliations for a session.

    - Verifies that sum of allocated costs across sales ~= total costs
    - Compares aggregate gross margin from per-sale calc vs (total sales - total costs)
    - Reports orphan costs / sales and association density
    """
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(session_id)
    data = session["data"]

    sales = data.get("sales", [])
    costs = data.get("costs", [])

    total_sales = sum(float(s.get("amount", 0) or 0) for s in sales if s.get("amount") is not None)
    total_costs = sum(float(c.get("amount", 0) or 0) for c in costs if c.get("amount") is not None)

    # Calculate using existing calculator
    calc = VATCalculator(vat_rate=vat_rate)
    calcs = calc.calculate_all(sales, costs)
    allocated_sum = sum(float(r.get("total_allocated_costs", 0) or 0) for r in calcs)
    gross_margin_sum = sum(float(r.get("gross_margin", 0) or 0) for r in calcs)

    expected_gross = total_sales - total_costs

    # Association stats
    sales_with_costs = [s for s in sales if len(s.get("linked_costs", [])) > 0]
    costs_with_sales = [c for c in costs if len(c.get("linked_sales", [])) > 0]
    orphan_sales = len(sales) - len(sales_with_costs)
    orphan_costs = len(costs) - len(costs_with_sales)
    total_links = sum(len(s.get("linked_costs", [])) for s in sales)
    avg_costs_per_sale = total_links / len(sales) if sales else 0
    avg_sales_per_cost = (sum(len(c.get("linked_sales", [])) for c in costs) / len(costs)) if costs else 0

    warnings = []
    if abs(allocated_sum - total_costs) > 0.01:
        warnings.append({
            "type": "allocation_mismatch",
            "message": f"Soma de custos alocados (€{allocated_sum:.2f}) difere do total de custos (€{total_costs:.2f})"
        })
    if orphan_costs > 0:
        warnings.append({"type": "orphan_costs", "count": orphan_costs})
    if orphan_sales > 0:
        warnings.append({"type": "sales_without_costs", "count": orphan_sales})
    if avg_costs_per_sale > 20 or avg_sales_per_cost > 20:
        warnings.append({
            "type": "mass_association",
            "message": "Densidade de associações muito elevada; verifique se não associou tudo com tudo"
        })

    return {
        "totals": {
            "sales": round(total_sales, 2),
            "costs": round(total_costs, 2),
            "expected_gross_margin": round(expected_gross, 2)
        },
        "calc": {
            "documents": len(calcs),
            "allocated_costs_sum": round(allocated_sum, 2),
            "gross_margin_sum": round(gross_margin_sum, 2)
        },
        "reconciliation": {
            "gross_margin_delta": round(gross_margin_sum - expected_gross, 2),
            "allocated_vs_costs_delta": round(allocated_sum - total_costs, 2)
        },
        "associations": {
            "sales_count": len(sales),
            "costs_count": len(costs),
            "orphan_sales": orphan_sales,
            "orphan_costs": orphan_costs,
            "avg_costs_per_sale": round(avg_costs_per_sale, 2),
            "avg_sales_per_cost": round(avg_sales_per_cost, 2)
        },
        "warnings": warnings
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_saft(file: UploadFile = File(...)):
    """
    Upload and parse SAF-T XML file
    
    - **file**: SAF-T XML file
    
    Returns parsed sales and costs data with a session ID
    """
    # Validate file
    file_content = await file.read()
    file_size = len(file_content)
    
    # Sanitize filename
    safe_filename = DataValidator.sanitize_filename(file.filename or "upload.xml")
    
    # Validate upload
    upload_errors = DataValidator.validate_file_upload(file_size, safe_filename)
    if upload_errors:
        raise HTTPException(400, f"Erro no ficheiro: {'; '.join(upload_errors)}")
    
    # Reset file pointer
    await file.seek(0)
        
    # Check file size (50MB limit)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    # Generate session ID
    session_id = str(uuid.uuid4())[:8]
    temp_path = str(UPLOAD_DIR / f"{session_id}_{safe_filename}")
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    os.remove(temp_path)
                    raise HTTPException(413, "File too large (max 50MB)")
                buffer.write(chunk)
                
        # Parse SAF-T file
        parser = SAFTParser()
        with open(temp_path, "rb") as f:
            content = f.read()
            
        data = parser.parse(content)
        
        # Clean up upload file
        os.remove(temp_path)
        
        # Store in session (KV on Vercel or in-memory locally)
        await set_session_store(session_id, {
            "created_at": datetime.now().isoformat(),
            "data": data,
            "filename": file.filename
        })
        
        # Validate parsed data
        validation_result = DataValidator.validate_margin_regime_data(
            data["sales"], 
            data["costs"]
        )
        
        # Combine all errors and warnings
        all_warnings = validation_result["warnings"] + data.get("parsing_warnings", [])
        all_errors = validation_result["errors"] + data.get("parsing_errors", [])
        
        # Log if there are issues
        if all_errors:
            logger.error(f"Upload {session_id} has {len(all_errors)} errors")
        if all_warnings:
            logger.warning(f"Upload {session_id} has {len(all_warnings)} warnings")
        
        # Prepare response
        response = UploadResponse(
            session_id=session_id,
            sales=data["sales"],
            costs=data["costs"],
            metadata=data["metadata"],
            summary={
                "total_sales": len(data["sales"]),
                "total_costs": len(data["costs"]),
                "sales_amount": sum(s["amount"] for s in data["sales"]),
                "costs_amount": sum(c["amount"] for c in data["costs"]),
                "errors": all_errors[:10],  # Limit errors shown
                "warnings": all_warnings[:10],  # Limit warnings shown
                "total_errors": len(all_errors),
                "total_warnings": len(all_warnings)
            }
        )
        
        return response
        
    except ValueError as e:
        # XML parsing error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(400, str(e))
    except Exception as e:
        # Other errors
        if os.path.exists(temp_path):
            os.remove(temp_path)
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(500, f"Error processing file: {str(e)}")


@app.post("/api/upload-efatura", response_model=UploadResponse)
async def upload_efatura_files(
    vendas: UploadFile = File(..., description="Ficheiro CSV de vendas do e-Fatura"),
    compras: UploadFile = File(..., description="Ficheiro CSV de compras do e-Fatura")
):
    # Limpa sessões anteriores (no-op em Vercel para evitar impacto cross-user)
    await clear_sessions_store()
    logger.info("Sessões anteriores limpas (ou ignoradas em Vercel) antes de novo upload.")
    """
    Upload e-Fatura CSV files (vendas and compras)
    
    Both files must be uploaded together for proper processing
    """
    # Validate file types
    for file, name in [(vendas, "vendas"), (compras, "compras")]:
        if not file.filename.endswith('.csv'):
            raise HTTPException(400, f"File {name} must be CSV format")
    
    # Generate session ID
    session_id = str(uuid.uuid4())[:8]
    
    try:
        # Read both files
        vendas_content = await vendas.read()
        compras_content = await compras.read()
        
        # Check file sizes (10MB limit for CSV)
        if len(vendas_content) > 10 * 1024 * 1024:
            raise HTTPException(413, "Vendas file too large (max 10MB)")
        if len(compras_content) > 10 * 1024 * 1024:
            raise HTTPException(413, "Compras file too large (max 10MB)")
        
        # Parse e-Fatura files
        parser = EFaturaParser()
        data = parser.parse(vendas_content, compras_content)
        
        # Store in session (KV on Vercel or in-memory locally)
        await set_session_store(session_id, {
            "created_at": datetime.now().isoformat(),
            "data": data,
            "filenames": {
                "vendas": vendas.filename,
                "compras": compras.filename
            }
        })
        
        # Validate parsed data
        validation_result = DataValidator.validate_margin_regime_data(
            data["sales"], 
            data["costs"]
        )
        
        # Combine all errors and warnings
        all_warnings = validation_result["warnings"] + data.get("parsing_warnings", [])
        all_errors = validation_result["errors"] + data.get("parsing_errors", [])
        
        # Log if there are issues
        if all_errors:
            logger.error(f"e-Fatura upload {session_id} has {len(all_errors)} errors")
        if all_warnings:
            logger.warning(f"e-Fatura upload {session_id} has {len(all_warnings)} warnings")
        
        # Prepare response
        response = UploadResponse(
            session_id=session_id,
            sales=data["sales"],
            costs=data["costs"],
            metadata=data["metadata"],
            summary={
                "total_sales": len(data["sales"]),
                "total_costs": len(data["costs"]),
                "sales_amount": sum(s["amount"] for s in data["sales"]),
                "costs_amount": sum(c["amount"] for c in data["costs"]),
                "errors": all_errors[:10],  # Limit errors shown
                "warnings": all_warnings[:10],  # Limit warnings shown
                "total_errors": len(all_errors),
                "total_warnings": len(all_warnings)
            }
        )
        
        return response
        
    except ValueError as e:
        # CSV parsing error
        raise HTTPException(400, str(e))
    except Exception as e:
        # Other errors
        logger.error(f"e-Fatura upload error: {str(e)}")
        raise HTTPException(500, f"Error processing files: {str(e)}")


@app.post("/api/associate")
async def associate_items(request: Association):
    """
    Associate sales with costs (many-to-many relationship)
    
    Multiple sales can be linked to multiple costs and vice versa
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]
    
    # Validate for mass associations
    warnings = []
    if len(request.sale_ids) > 10 and len(request.cost_ids) > 10:
        total_associations = len(request.sale_ids) * len(request.cost_ids)
        if total_associations > 100:
            logger.warning(f"Large association request: {len(request.sale_ids)} sales × {len(request.cost_ids)} costs = {total_associations} associations")
            warnings.append({
                "type": "mass_association",
                "message": f"Criando {total_associations} associações. Considere associar custos a vendas específicas relacionadas.",
                "severity": "high"
            })
    
    # Check for over-linked costs
    for cost_id in request.cost_ids:
        cost = next((c for c in session_data["costs"] if c["id"] == cost_id), None)
        if cost:
            existing_links = len(cost.get("linked_sales", []))
            new_total = existing_links + len(request.sale_ids)
            if new_total > 10:
                warnings.append({
                    "type": "over_linked_cost",
                    "cost_id": cost_id,
                    "supplier": cost.get("supplier", "Unknown"),
                    "total_links": new_total,
                    "message": f"Custo '{cost.get('supplier', 'Unknown')}' ficará ligado a {new_total} vendas"
                })
    
    associations_made = 0
    
    # Update sales with linked costs
    for sale in session_data["sales"]:
        if sale["id"] in request.sale_ids:
            before = len(sale.get("linked_costs", []))
            # Add new cost IDs, avoiding duplicates
            sale["linked_costs"] = list(set(sale.get("linked_costs", []) + request.cost_ids))
            associations_made += len(sale["linked_costs"]) - before
            
    # Update costs with linked sales
    for cost in session_data["costs"]:
        if cost["id"] in request.cost_ids:
            # Add new sale IDs, avoiding duplicates
            cost["linked_sales"] = list(set(cost.get("linked_sales", []) + request.sale_ids))
            
    response = {
        "status": "success" if not warnings else "warning",
        "message": f"Created {associations_made} new associations",
        "associations_made": associations_made,
        "sales_updated": len(request.sale_ids),
        "costs_updated": len(request.cost_ids)
    }
    
    if warnings:
        response["warnings"] = warnings
        
    return response


# Auto-match configuration
AUTO_MATCH_CONFIG = {
    "date_weight": 40,  # Weight for date proximity scoring
    "value_weight": 30,  # Weight for value ratio scoring
    "keyword_weight": 30,  # Weight for keyword matching
    "max_date_diff": 30,  # Maximum days difference to consider
    "min_value_ratio": 0.1,  # Minimum cost/sale ratio
    "max_value_ratio": 0.8,  # Maximum cost/sale ratio
    "stop_words": ["de", "da", "do", "e", "em", "para", "com", "lda", "sa", "unipessoal", "ltd", "inc"],
    "date_proximity_brackets": [
        (0, 7, 40),    # 0-7 days: max 40 points
        (8, 14, 30),   # 8-14 days: max 30 points
        (15, 30, 20),  # 15-30 days: max 20 points
    ],
    "min_keyword_length": 3,  # Minimum length for keyword to be considered
    "max_matches_per_cost": 5,  # Maximum number of sales to match per cost
    "category_match_bonus": 20,  # Bonus points for category matching
}

@app.post("/api/auto-match")
async def auto_match(request: AIMatchRequest):
    """
    AI-powered automatic matching of sales and costs
    
    Uses date proximity, value compatibility and description matching
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]
    sales = session_data["sales"]
    costs = session_data["costs"]
    
    matches = []
    
    # Get config (could be overridden by request in future)
    config = AUTO_MATCH_CONFIG.copy()
    
    # Auto-matching algorithm
    for cost in costs:
        # Skip if already has associations
        if len(cost.get("linked_sales", [])) > 0:
            continue
            
        best_matches = []
        
        # Parse cost date
        try:
            cost_date = datetime.strptime(cost["date"], "%Y-%m-%d")
        except:
            continue
            
        # Score each sale
        for sale in sales:
            try:
                sale_date = datetime.strptime(sale["date"], "%Y-%m-%d")
            except:
                continue
                
            # Calculate score based on multiple factors
            score = 0
            reason_parts = []
            
            # 1. Date proximity scoring
            date_diff = abs((sale_date - cost_date).days)
            date_score = 0
            
            # Check date proximity brackets
            for min_days, max_days, max_score in config["date_proximity_brackets"]:
                if min_days <= date_diff <= max_days:
                    # Linear interpolation within bracket
                    bracket_range = max_days - min_days
                    if bracket_range > 0:
                        date_score = max_score * (1 - (date_diff - min_days) / bracket_range)
                    else:
                        date_score = max_score
                    reason_parts.append(f"Date proximity ({date_diff} days)")
                    break
            
            # Skip if outside max date difference
            if date_diff > config["max_date_diff"]:
                continue
                
            score += date_score * (config["date_weight"] / 100)
                
            # 2. Value compatibility scoring
            if cost["amount"] < sale["amount"] and sale["amount"] > 0:
                ratio = cost["amount"] / sale["amount"]
                if config["min_value_ratio"] <= ratio <= config["max_value_ratio"]:
                    # Higher score for ratios closer to typical margins (20-40%)
                    if 0.2 <= ratio <= 0.4:
                        value_score = 1.0
                    else:
                        value_score = 0.5
                    score += value_score * config["value_weight"]
                    reason_parts.append(f"Value ratio {ratio:.1%}")
                    
            # 3. Description/client keyword matching
            # Extract and clean words
            cost_text = f"{cost.get('description', '')} {cost.get('supplier', '')}".lower()
            sale_text = f"{sale.get('client', '')} {sale.get('number', '')}".lower()
            
            # Tokenize and filter
            cost_words = set(word for word in cost_text.split() 
                           if len(word) >= config["min_keyword_length"] 
                           and word not in config["stop_words"])
            sale_words = set(word for word in sale_text.split() 
                           if len(word) >= config["min_keyword_length"] 
                           and word not in config["stop_words"])
            
            # Find common meaningful words
            common_words = cost_words.intersection(sale_words)
            
            if common_words:
                # Score based on number of matches (diminishing returns)
                keyword_score = min(len(common_words) / 3, 1.0)
                score += keyword_score * config["keyword_weight"]
                reason_parts.append(f"Keywords: {', '.join(list(common_words)[:5])}")
                
            # 4. Document type bonus
            if sale.get("invoice_type") == "FT" and cost["date"] < sale["date"]:
                score += 10
                reason_parts.append("Cost before invoice")
                
            if score >= request.threshold:
                best_matches.append({
                    "sale": sale,
                    "score": score,
                    "reasons": reason_parts
                })
                
        # Sort by score and take best matches (limited by max_matches_per_cost)
        if best_matches:
            best_matches.sort(key=lambda x: x["score"], reverse=True)
            
            # Take only top N matches per cost
            matches_to_add = best_matches[:config["max_matches_per_cost"]]
            
            # Create associations
            sale_ids = []
            for match in matches_to_add:
                sale = match["sale"]
                sale_ids.append(sale["id"])
                
                # Add cost to sale's linked costs
                if "linked_costs" not in sale:
                    sale["linked_costs"] = []
                if cost["id"] not in sale["linked_costs"]:
                    sale["linked_costs"].append(cost["id"])
                
                matches.append(AIMatchResult(
                    cost=f"{cost['supplier']} - {cost.get('description', '')[:50]}",
                    sale=f"{sale['number']} - {sale['client']}",
                    confidence=match["score"],
                    reason="; ".join(match["reasons"])
                ))
            
            # Update cost with all linked sales
            cost["linked_sales"] = sale_ids
            
            if len(matches) >= request.max_matches:
                break
                
    return {
        "status": "success",
        "matches_found": len(matches),
        "matches": matches,
        "message": f"Found {len(matches)} associations with confidence >= {request.threshold}%"
    }


@app.post("/api/calculate")
async def calculate_vat(request: CalculationRequest):
    """
    Calculate VAT on margin and generate Excel report
    
    Returns Excel file with complete calculations
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]
    
    try:
        # First, validate associations integrity
        integrity_errors = DataValidator.validate_associations_integrity(
            session_data["sales"],
            session_data["costs"]
        )
        
        # Log any integrity issues
        if integrity_errors:
            logger.warning(f"Found {len(integrity_errors)} integrity issues")
            for error in integrity_errors:
                if error["type"] == "error":
                    logger.error(f"Integrity error: {error['message']}")
                elif error["type"] == "warning":
                    logger.warning(f"Integrity warning: {error['message']}")
        
        # Initialize calculator with enhanced error handling
        calculator = VATCalculator(vat_rate=request.vat_rate)

        # Pre-validate data before calculation
        if not session_data.get("sales"):
            raise HTTPException(400, "No sales data found in session")
        if not session_data.get("costs"):
            logger.warning("No costs data found - calculating with zero costs")

        # Calculate VAT for all sales
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data.get("costs", [])
        )

        # Validate calculation results
        if not calculations:
            raise HTTPException(400, "No valid calculations generated")
        
        # Add metadata
        metadata = session_data.get("metadata", {})
        metadata["vat_rate"] = request.vat_rate
        metadata["calculation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate Excel report
        exporter = ExcelExporter()
        excel_path = exporter.generate(calculations, session_data, metadata, base_dir=TEMP_DIR)
        
        # Return file
        return FileResponse(
            excel_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f'iva_margem_{request.session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            headers={
                "Content-Disposition": f"attachment; filename=iva_margem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        raise HTTPException(500, f"Error calculating VAT: {str(e)}")


# -------------------------------------------------------------------------
# PREMIUM ANALYTICS ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/analytics/executive-summary")
async def get_executive_summary(request: CalculationRequest):
    """
    Generate C-Level executive summary with KPIs, drivers, and recommendations

    Returns executive dashboard suitable for Board presentation
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]

    try:
        # Initialize analytics engine
        analytics = PremiumAnalytics(vat_rate=request.vat_rate)

        # Calculate base results first
        calculator = VATCalculator(vat_rate=request.vat_rate)
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data["costs"]
        )

        # Generate executive summary
        executive_summary = analytics.generate_executive_summary(
            calculations, session_data
        )

        # Add metadata
        executive_summary["metadata"] = {
            "session_id": request.session_id,
            "vat_rate": request.vat_rate,
            "generated_at": datetime.now().isoformat(),
            "document_count": len(calculations),
            "calculation_engine": "PremiumAnalytics v1.0"
        }

        return JSONResponse(content=executive_summary)

    except Exception as e:
        logger.error(f"Executive summary error: {str(e)}")
        raise HTTPException(500, f"Error generating executive summary: {str(e)}")


@app.post("/api/analytics/waterfall")
async def get_waterfall_analysis(request: CalculationRequest):
    """
    Generate margin bridge/waterfall analysis for variance analysis

    Returns waterfall data suitable for bridge charts
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]

    try:
        # Initialize analytics
        analytics = PremiumAnalytics(vat_rate=request.vat_rate)

        # Calculate base results
        calculator = VATCalculator(vat_rate=request.vat_rate)
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data["costs"]
        )

        # Generate waterfall analysis
        waterfall_data = analytics.generate_waterfall_analysis(calculations)

        return JSONResponse(content={
            "waterfall_analysis": waterfall_data,
            "metadata": {
                "session_id": request.session_id,
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "margin_bridge"
            }
        })

    except Exception as e:
        logger.error(f"Waterfall analysis error: {str(e)}")
        raise HTTPException(500, f"Error generating waterfall analysis: {str(e)}")


@app.post("/api/analytics/scenarios")
async def get_scenario_analysis(request: CalculationRequest):
    """
    Generate stress test scenarios and sensitivity analysis

    Returns base/optimistic/pessimistic scenarios with VAT rate impacts
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]

    try:
        # Initialize analytics
        analytics = PremiumAnalytics(vat_rate=request.vat_rate)

        # Calculate base results
        calculator = VATCalculator(vat_rate=request.vat_rate)
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data["costs"]
        )

        # Generate scenario analysis
        scenarios = analytics.generate_scenario_analysis(calculations)

        return JSONResponse(content={
            "scenario_analysis": scenarios,
            "metadata": {
                "session_id": request.session_id,
                "base_vat_rate": request.vat_rate,
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "stress_test"
            }
        })

    except Exception as e:
        logger.error(f"Scenario analysis error: {str(e)}")
        raise HTTPException(500, f"Error generating scenario analysis: {str(e)}")


@app.post("/api/analytics/outliers")
async def get_outlier_analysis(request: CalculationRequest):
    """
    Identify statistical outliers in margins and revenues (percentile 95)

    Returns outlier documents requiring management attention
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]

    try:
        # Initialize analytics
        analytics = PremiumAnalytics(vat_rate=request.vat_rate)

        # Calculate base results
        calculator = VATCalculator(vat_rate=request.vat_rate)
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data["costs"]
        )

        # Identify outliers
        outliers = analytics.identify_outliers(calculations)

        return JSONResponse(content={
            "outlier_analysis": outliers,
            "metadata": {
                "session_id": request.session_id,
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "statistical_outliers",
                "percentile_threshold": 95
            }
        })

    except Exception as e:
        logger.error(f"Outlier analysis error: {str(e)}")
        raise HTTPException(500, f"Error generating outlier analysis: {str(e)}")


@app.get("/api/analytics/kpis/{session_id}")
async def get_advanced_kpis(session_id: str, vat_rate: float = 23.0):
    """
    Get advanced KPIs: ROIC, EVA, margin stability

    Returns sophisticated financial metrics for executive review
    """
    # Validate session
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(session_id)
    session_data = session["data"]

    try:
        # Calculate base results
        calculator = VATCalculator(vat_rate=vat_rate)
        calculations = calculator.calculate_all(
            session_data["sales"],
            session_data["costs"]
        )

        if not calculations:
            raise HTTPException(404, "No calculations available")

        # Calculate summary
        summary = calculator.calculate_summary(calculations)

        # Advanced KPIs
        invested_capital = summary["total_costs"]  # Simplified assumption
        cost_of_capital = 8.0  # Typical for travel agencies

        advanced_kpis = {
            "roic_simplified": AdvancedKPICalculator.calculate_roic_simplified(
                summary["total_net_margin"], invested_capital
            ),
            "eva_simplified": AdvancedKPICalculator.calculate_eva_simplified(
                summary["total_net_margin"], cost_of_capital, invested_capital
            ),
            "margin_stability": AdvancedKPICalculator.calculate_margin_stability(calculations),
            "baseline_metrics": {
                "net_margin": summary["total_net_margin"],
                "gross_margin": summary["total_gross_margin"],
                "margin_percentage": summary["average_margin_percentage"],
                "invested_capital": invested_capital
            }
        }

        return JSONResponse(content={
            "advanced_kpis": advanced_kpis,
            "metadata": {
                "session_id": session_id,
                "vat_rate": vat_rate,
                "generated_at": datetime.now().isoformat(),
                "kpi_version": "v1.0"
            }
        })

    except Exception as e:
        logger.error(f"Advanced KPIs error: {str(e)}")
        raise HTTPException(500, f"Error calculating advanced KPIs: {str(e)}")


@app.post("/api/export-pdf")
@app.options("/api/export-pdf")
async def export_pdf(request: PDFExportRequest = None):
    """
    Generate enhanced PDF report with calculation results and company info
    """
    # Handle OPTIONS request
    if request is None:
        return {"status": "ok"}
        
    try:
        # Validate request
        session_id = request.session_id if request else None
        vat_rate = request.vat_rate if request else 23
        final_results = request.results if request else {}
        company_info = request.company_info if request else None
        out_format = (request.format or 'html') if request else 'html'
        
        if not session_id:
            # Create test session for PDF preview
            session_data = {
                "sales": [],
                "costs": [],
                "metadata": {}
            }
            calculations = []
        elif not await has_session_store(session_id):
            raise HTTPException(404, "Session not found")
        else:
            session = await get_session_store(session_id)
            session_data = session["data"]
            
            # Initialize calculator
            calculator = VATCalculator(vat_rate=vat_rate)
            
            # Calculate VAT for all sales
            calculations = calculator.calculate_all(
                session_data["sales"], 
                session_data["costs"]
            )
        
        # Generate PDF / HTML content
        logger.info(f"Generating PDF with {len(calculations)} calculations")
        logger.info(f"Session has {len(session_data.get('sales', []))} sales and {len(session_data.get('costs', []))} costs")
        logger.info(f"Final results: {final_results}")

        # Resolve company metadata
        company_payload = resolve_company_payload(company_info, session_data)
        company_name = (
            company_payload.get('name')
            or session_data.get('metadata', {}).get('company_name')
            or 'Empresa'
        )
        safe_company = sanitize_company_name(company_name)
        filename = f"Relatório IVA sobre Margem - {safe_company}.pdf"

        saft_hash = None
        metadata = session_data.get('metadata') if isinstance(session_data, dict) else None
        if isinstance(metadata, dict):
            saft_hash = metadata.get('saft_hash')

        try:
            pdf_html_bytes = generate_enhanced_pdf_report(
                session_data=session_data,
                calculation_results=calculations,
                vat_rate=vat_rate,
                final_results=final_results or {},
                company_info=company_payload,
                saft_hash=saft_hash,
            )
            logger.info('Enhanced PDF report generated successfully.')
        except Exception as enhanced_error:  # pragma: no cover - fallback path
            logger.exception('Enhanced PDF generation failed. Falling back to professional template: %s', enhanced_error)
            pdf_html_bytes = generate_professional_pdf_report(
                session_data=session_data,
                calculation_results=calculations,
                vat_rate=vat_rate,
                final_results=final_results or {},
                company_info=company_payload,
            )

        html_content = pdf_html_bytes.decode('utf-8')

        if out_format.lower() == 'pdf':
            pdf_bin, renderer_name = render_pdf_from_html(
                html_content=html_content,
                session_data=session_data,
                calculations=calculations,
                vat_rate=vat_rate,
                final_results=final_results or {},
                company_payload=company_payload,
                safe_company=safe_company,
            )
            headers = {
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "X-Report-Renderer": renderer_name,
            }
            return StreamingResponse(io.BytesIO(pdf_bin), media_type='application/pdf', headers=headers)

        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Content-Disposition": f"inline; filename=\"{filename}\""
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


@app.delete("/api/unlink")
async def unlink_items(request: UnlinkRequest):
    """Remove association between a sale and a cost"""
    
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]
    
    # Find and update sale
    sale = next((s for s in session_data["sales"] if s["id"] == request.sale_id), None)
    if sale and request.cost_id in sale.get("linked_costs", []):
        sale["linked_costs"].remove(request.cost_id)
        
    # Find and update cost
    cost = next((c for c in session_data["costs"] if c["id"] == request.cost_id), None)
    if cost and request.sale_id in cost.get("linked_sales", []):
        cost["linked_sales"].remove(request.sale_id)
        
    return {
        "status": "success",
        "message": "Association removed"
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(session_id)
    data = session["data"]
    
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "filename": session.get("filename", ""),
        "sales": data["sales"],
        "costs": data["costs"],
        "metadata": data.get("metadata", {}),
        "summary": {
            "total_sales": len(data["sales"]),
            "total_costs": len(data["costs"]),
            "sales_with_costs": sum(1 for s in data["sales"] if len(s.get("linked_costs", [])) > 0),
            "costs_with_sales": sum(1 for c in data["costs"] if len(c.get("linked_sales", [])) > 0)
        }
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its data"""
    
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    await delete_session_store(session_id)
    
    return {
        "status": "success",
        "message": "Session deleted"
    }


@app.post("/api/clear-associations")
async def clear_associations(request: dict):
    """Clear all associations for a session"""
    
    if "session_id" not in request:
        raise HTTPException(400, "Session ID required")
    
    session_id = request["session_id"]
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(session_id)
    session_data = session["data"]
    
    # Clear all associations
    associations_cleared = 0
    
    # Clear linked costs from sales
    for sale in session_data["sales"]:
        if "linked_costs" in sale and sale["linked_costs"]:
            associations_cleared += len(sale["linked_costs"])
            sale["linked_costs"] = []
    
    # Clear linked sales from costs
    for cost in session_data["costs"]:
        if "linked_sales" in cost and cost["linked_sales"]:
            cost["linked_sales"] = []
    
    logger.info(f"Cleared {associations_cleared} associations for session {session_id}")
    
    return {
        "status": "success",
        "message": f"Cleared {associations_cleared} associations",
        "associations_cleared": associations_cleared
    }


@app.post("/api/validate")
async def validate_data(request: dict):
    """Validate session data for margin regime compliance"""
    
    if "session_id" not in request:
        raise HTTPException(400, "Session ID required")
    
    session_id = request["session_id"]
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    
    session = await get_session_store(session_id)
    session_data = session["data"]
    
    # Validate data
    validation = DataValidator.validate_margin_regime_data(
        session_data["sales"], 
        session_data["costs"]
    )
    
    return {
        "session_id": session_id,
        "validation": validation,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/mock-data")
async def get_mock_data():
    """Get mock data for testing without SAF-T file"""
    return await load_mock_data()

@app.post("/api/mock-data")
async def load_mock_data():
    """Get mock data for testing without SAF-T file"""
    
    # Create mock session
    session_id = "demo-" + str(uuid.uuid4())[:4]
    
    # Dados completos dos CSVs e-fatura (TODOS OS 26 SALES)
    import json
    import os

    # Carregar dados do arquivo completo
    api_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'api_sample_data.json')
    try:
        with open(api_data_path, 'r', encoding='utf-8') as f:
            complete_data = json.load(f)

        mock_data = {
            "sales": complete_data["sales"],
            "costs": complete_data["costs"],
            "metadata": complete_data["metadata"]
        }
    except (FileNotFoundError, KeyError) as e:
        print(f"⚠️ Erro carregando dados completos: {e}")
        # Retornar erro se não conseguir carregar dados completos
        return JSONResponse(
            status_code=500,
            content={
                "error": "Dados completos não disponíveis",
                "details": str(e),
                "message": "Sistema requer dados completos dos CSVs e-fatura"
            }
        )
    
    # Store in sessions
    sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "data": mock_data,
        "filename": "demo_data.xml"
    }
    
    # Store in session store for consistency with other endpoints
    await set_session_store(session_id, {
        "created_at": datetime.now().isoformat(),
        "data": mock_data,
        "filename": "demo_data.csv"
    })

    return {
        "session_id": session_id,
        "message": "Mock data loaded successfully",
        "sales_count": len(mock_data["sales"]),
        "costs_count": len(mock_data["costs"]),
        "sales": mock_data["sales"],
        "costs": mock_data["costs"]
    }


@app.post("/api/calculate-period")
async def calculate_period_vat(request: PeriodCalculateRequest):
    """
    Calculate VAT for a specific period with margin compensation
    Implements Portuguese VAT law requirements for travel agencies
    """
    from datetime import datetime
    from decimal import Decimal
    
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    
    session = await get_session_store(request.session_id)
    session_data = session["data"]
    
    try:
        # Parse dates
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(request.end_date, '%Y-%m-%d').date()
        
        # Initialize period calculator
        period_calc = PeriodVATCalculator(region=request.region)
        
        # Get associations from session data
        associations = []
        for sale in session_data["sales"]:
            for cost_id in sale.get("linked_costs", []):
                associations.append({
                    "sale_id": sale["id"],
                    "cost_id": cost_id
                })
        
        # Calculate period VAT
        result = period_calc.calculate_period_vat(
            sales=session_data["sales"],
            costs=session_data["costs"],
            associations=associations,
            start_date=start_date,
            end_date=end_date,
            previous_negative_margin=Decimal(str(request.previous_negative_margin))
        )
        
        # Add session info
        result['session_id'] = request.session_id
        result['calculation_type'] = 'period_based'
        
        # Log calculation
        logger.info(f"Period VAT calculation: {start_date} to {end_date}")
        logger.info(f"Gross margin: €{result['totals']['gross_margin']:.2f}")
        logger.info(f"VAT amount: €{result['totals']['vat_amount']:.2f}")
        logger.info(f"Carry forward: €{result['totals']['carry_forward']:.2f}")
        
        return result
        
    except ValueError as e:
        raise HTTPException(400, f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Period calculation error: {str(e)}")
        raise HTTPException(500, f"Calculation error: {str(e)}")


@app.post("/api/calculate-enhanced-period")
async def calculate_enhanced_period(request: PeriodCalculateRequest):
    """
    Calculate VAT on margin for enhanced period with new calculator
    Uses the improved calculator with better validation
    """
    # Validate session
    if not await has_session_store(request.session_id):
        raise HTTPException(404, "Session not found")
    session = await get_session_store(request.session_id)
    session_data = session["data"]

    try:
        # Initialize enhanced calculator
        calculator = VATCalculator(vat_rate=request.vat_rate)

        # Use new period calculation method
        period_result = calculator.calculate_by_period(
            session_data.get("sales", []),
            session_data.get("costs", []),
            request.period_start,
            request.period_end
        )

        # Add company info if available
        company_info = session_data.get("metadata", {}).get("company_info", {})
        period_result["company_info"] = company_info

        return {
            "success": True,
            "session_id": request.session_id,
            "period_result": period_result,
            "calculation_mode": "enhanced_period",
            "compliance": "CIVA Art. 308º - Regime Especial Agências Viagens"
        }

    except Exception as e:
        logger.error(f"Enhanced period calculation error: {str(e)}")
        raise HTTPException(500, f"Calculation failed: {str(e)}")


@app.post("/api/calculate-quarterly")
async def calculate_quarterly_vat(request: dict):
    """
    Calculate VAT for a specific quarter
    Convenience endpoint for quarterly calculations
    """
    # Validate request
    required_fields = ['session_id', 'year', 'quarter']
    for field in required_fields:
        if field not in request:
            raise HTTPException(400, f"Missing required field: {field}")
    
    session_id = request['session_id']
    year = request['year']
    quarter = request['quarter']
    region = request.get('region', 'continental')
    previous_negative = request.get('previous_negative_margin', 0.0)
    
    # Validate session
    if not await has_session_store(session_id):
        raise HTTPException(404, "Session not found")
    
    # Validate quarter
    if quarter not in [1, 2, 3, 4]:
        raise HTTPException(400, "Quarter must be 1, 2, 3, or 4")
    
    session = await get_session_store(session_id)
    session_data = session["data"]
    
    try:
        # Initialize period calculator
        period_calc = PeriodVATCalculator(region=region)
        
        # Get associations
        associations = []
        for sale in session_data["sales"]:
            for cost_id in sale.get("linked_costs", []):
                associations.append({
                    "sale_id": sale["id"],
                    "cost_id": cost_id
                })
        
        # Calculate quarterly VAT
        result = period_calc.calculate_quarterly_vat(
            year=year,
            quarter=quarter,
            sales=session_data["sales"],
            costs=session_data["costs"],
            associations=associations,
            previous_negative=Decimal(str(previous_negative))
        )
        
        # Generate Anexo O data
        anexo_o = period_calc.generate_anexo_o_data(result)
        result['anexo_o'] = anexo_o
        
        return result
        
    except Exception as e:
        logger.error(f"Quarterly calculation error: {str(e)}")
        raise HTTPException(500, f"Calculation error: {str(e)}")


# For Railway deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
