"""
Main FastAPI application for IVA Margem Turismo
API for VAT margin calculation for travel agencies
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import json
import shutil
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from contextlib import asynccontextmanager

# Import app modules
from .models import (
    Sale, Cost, Association, CalculationRequest, 
    AIMatchRequest, UnlinkRequest, UploadResponse,
    CalculationResult, AIMatchResult
)
from .saft_parser import SAFTParser
from .efatura_parser import EFaturaParser
from .calculator import VATCalculator
from .excel_export import ExcelExporter
from .validators import DataValidator
from .pdf_export_professional import generate_pdf_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session storage (in-memory for simplicity)
sessions = {}

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
    os.makedirs("temp", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # Clean old temp files
    clean_old_files()
    
    # Start periodic cleanup task
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

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_old_files():
    """Clean temporary files and sessions older than 24 hours"""
    try:
        now = datetime.now()
        
        # Clean old files
        cleaned_files = 0
        for folder in ['temp', 'uploads']:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if now - file_time > timedelta(hours=24):
                            os.remove(filepath)
                            cleaned_files += 1
                            logger.debug(f"Removed old file: {filepath}")
        
        # Clean old sessions
        cleaned_sessions = 0
        sessions_to_remove = []
        for session_id, session_data in sessions.items():
            created_at_str = session_data.get("created_at", "")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    if now - created_at > timedelta(hours=24):
                        sessions_to_remove.append(session_id)
                except:
                    # If can't parse date, mark for removal
                    sessions_to_remove.append(session_id)
        
        # Remove old sessions
        for session_id in sessions_to_remove:
            del sessions[session_id]
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
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions_active": len(sessions),
        "temp_files": len(os.listdir("temp")) if os.path.exists("temp") else 0
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
    temp_path = f"uploads/{session_id}_{file.filename}"
    
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
        
        # Store in session
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "data": data,
            "filename": file.filename
        }
        
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
            sales=data["sales"][:50],  # Limit to first 50 for response
            costs=data["costs"][:50],  # Limit to first 50 for response
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
        
        # Store in session
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "data": data,
            "filenames": {
                "vendas": vendas.filename,
                "compras": compras.filename
            }
        }
        
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
            sales=data["sales"][:50],  # Limit to first 50 for response
            costs=data["costs"][:50],  # Limit to first 50 for response
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
    if request.session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    session_data = sessions[request.session_id]["data"]
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
            
    return {
        "status": "success",
        "message": f"Created {associations_made} new associations",
        "associations_made": associations_made,
        "sales_updated": len(request.sale_ids),
        "costs_updated": len(request.cost_ids)
    }


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
}

@app.post("/api/auto-match")
async def auto_match(request: AIMatchRequest):
    """
    AI-powered automatic matching of sales and costs
    
    Uses date proximity, value compatibility and description matching
    """
    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    session_data = sessions[request.session_id]["data"]
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
                
        # Sort by score and take best match
        if best_matches:
            best_matches.sort(key=lambda x: x["score"], reverse=True)
            best = best_matches[0]
            
            # Create association
            cost["linked_sales"] = [best["sale"]["id"]]
            best["sale"]["linked_costs"] = best["sale"].get("linked_costs", []) + [cost["id"]]
            
            matches.append(AIMatchResult(
                cost=f"{cost['supplier']} - {cost['description'][:50]}",
                sale=f"{best['sale']['number']} - {best['sale']['client']}",
                confidence=best["score"],
                reason="; ".join(best["reasons"])
            ))
            
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
    if request.session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    session_data = sessions[request.session_id]["data"]
    
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
        
        # Initialize calculator
        calculator = VATCalculator(vat_rate=request.vat_rate)
        
        # Calculate VAT for all sales
        calculations = calculator.calculate_all(
            session_data["sales"], 
            session_data["costs"]
        )
        
        # Add metadata
        metadata = session_data.get("metadata", {})
        metadata["vat_rate"] = request.vat_rate
        metadata["calculation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate Excel report
        exporter = ExcelExporter()
        excel_path = exporter.generate(calculations, session_data, metadata)
        
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


@app.post("/api/export-pdf")
@app.options("/api/export-pdf")
async def export_pdf(request: Dict = None):
    """
    Generate PDF report with calculation results
    """
    # Handle OPTIONS request
    if request is None:
        return {"status": "ok"}
        
    try:
        # Validate request
        session_id = request.get("session_id")
        vat_rate = request.get("vat_rate", 23)
        final_results = request.get("results", {})
        
        if not session_id:
            # Create test session for PDF preview
            session_data = {
                "sales": [],
                "costs": [],
                "metadata": {}
            }
            calculations = []
        elif session_id not in sessions:
            raise HTTPException(404, "Session not found")
        else:
            session_data = sessions[session_id]["data"]
            
            # Initialize calculator
            calculator = VATCalculator(vat_rate=vat_rate)
            
            # Calculate VAT for all sales
            calculations = calculator.calculate_all(
                session_data["sales"], 
                session_data["costs"]
            )
        
        # Generate PDF
        logger.info(f"Generating PDF with {len(calculations)} calculations")
        logger.info(f"Session has {len(session_data.get('sales', []))} sales and {len(session_data.get('costs', []))} costs")
        logger.info(f"Final results: {final_results}")
        
        pdf_bytes = generate_pdf_report(
            session_data=session_data,
            calculation_results=calculations,
            vat_rate=vat_rate,
            final_results=final_results
        )
        
        # Return HTML that can be printed to PDF
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=pdf_bytes.decode('utf-8'),
            headers={
                "Content-Type": "text/html; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


@app.delete("/api/unlink")
async def unlink_items(request: UnlinkRequest):
    """Remove association between a sale and a cost"""
    
    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    session_data = sessions[request.session_id]["data"]
    
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
    
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    session = sessions[session_id]
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
    
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
        
    del sessions[session_id]
    
    return {
        "status": "success",
        "message": "Session deleted"
    }


@app.post("/api/validate")
async def validate_data(request: dict):
    """Validate session data for margin regime compliance"""
    
    if "session_id" not in request:
        raise HTTPException(400, "Session ID required")
    
    session_id = request["session_id"]
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    
    session_data = sessions[session_id]["data"]
    
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
    
    # Create mock session
    session_id = "demo-" + str(uuid.uuid4())[:4]
    
    # Dados reais extraídos do Excel modelo
    mock_data = {
        "sales": [
            {"id": "s1", "number": "NC E2025/2 / JJGSTD94-2", "date": "2025-03-12", "client": "Maria Santos - Empresarial - Cancellation", "amount": -375.0, "vat_amount": 0, "gross_total": -375.0, "linked_costs": []},
            {"id": "s2", "number": "FR E2025/7 / JJGWTD95-7", "date": "2025-03-01", "client": "Cliente Genérico - Premium International", "amount": 11484.6, "vat_amount": 0, "gross_total": 11484.6, "linked_costs": []},
            {"id": "s3", "number": "FT E2025/17 / JJGBTD9W-17", "date": "2025-02-28", "client": "João Silva - Particular - Domestic Trip", "amount": 400.0, "vat_amount": 0, "gross_total": 400.0, "linked_costs": []},
            {"id": "s4", "number": "FR E2025/6 / JJGWTD95-6", "date": "2025-02-28", "client": "Maria Santos - Empresarial - Domestic Trip", "amount": 750.0, "vat_amount": 0, "gross_total": 750.0, "linked_costs": []},
            {"id": "s5", "number": "NC E2025/1 / JJGSTD94-1", "date": "2025-02-28", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 420.0, "vat_amount": 0, "gross_total": 420.0, "linked_costs": []},
            {"id": "s6", "number": "FT E2025/14 / JJGBTD9W-14", "date": "2025-02-28", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 220.0, "vat_amount": 0, "gross_total": 220.0, "linked_costs": []},
            {"id": "s7", "number": "FT E2025/15 / JJGBTD9W-15", "date": "2025-02-28", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 200.0, "vat_amount": 0, "gross_total": 200.0, "linked_costs": []},
            {"id": "s8", "number": "FT E2025/16 / JJGBTD9W-16", "date": "2025-02-28", "client": "Cliente 5903 - Weekend Break", "amount": 1759.0, "vat_amount": 0, "gross_total": 1759.0, "linked_costs": []},
            {"id": "s9", "number": "FT E2025/12 / JJGBTD9W-12", "date": "2025-02-28", "client": "Cliente 1363 - Domestic Trip", "amount": 280.0, "vat_amount": 0, "gross_total": 280.0, "linked_costs": []},
            {"id": "s10", "number": "FT E2025/13 / JJGBTD9W-13", "date": "2025-02-28", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 420.0, "vat_amount": 0, "gross_total": 420.0, "linked_costs": []},
            {"id": "s11", "number": "FT E2025/11 / JJGBTD9W-11", "date": "2025-02-19", "client": "Cliente 6612 - Domestic Trip", "amount": 360.0, "vat_amount": 0, "gross_total": 360.0, "linked_costs": []},
            {"id": "s12", "number": "FT E2025/10 / JJGBTD9W-10", "date": "2025-02-19", "client": "Cliente 6612 - Domestic Trip", "amount": 945.0, "vat_amount": 0, "gross_total": 945.0, "linked_costs": []},
            {"id": "s13", "number": "FR E2025/5 / JJGWTD95-5", "date": "2025-02-11", "client": "Cliente 0015 - Domestic Trip", "amount": 351.78, "vat_amount": 0, "gross_total": 351.78, "linked_costs": []},
            {"id": "s14", "number": "FT E2025/7 / JJGBTD9W-7", "date": "2025-02-03", "client": "Cliente 1363 - Domestic Trip", "amount": 560.0, "vat_amount": 0, "gross_total": 560.0, "linked_costs": []},
            {"id": "s15", "number": "FT E2025/9 / JJGBTD9W-9", "date": "2025-02-03", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 161.0, "vat_amount": 0, "gross_total": 161.0, "linked_costs": []},
            {"id": "s16", "number": "FT E2025/8 / JJGBTD9W-8", "date": "2025-02-03", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 125.0, "vat_amount": 0, "gross_total": 125.0, "linked_costs": []},
            {"id": "s17", "number": "FR E2025/3 / JJGWTD95-3", "date": "2025-01-31", "client": "Cliente Genérico - Premium International", "amount": 12763.95, "vat_amount": 0, "gross_total": 12763.95, "linked_costs": []},
            {"id": "s18", "number": "FR E2025/4 / JJGWTD95-4", "date": "2025-01-31", "client": "Cliente Genérico - Domestic Trip", "amount": 109.94, "vat_amount": 0, "gross_total": 109.94, "linked_costs": []},
            {"id": "s19", "number": "FR E2025/2 / JJGWTD95-2", "date": "2025-01-09", "client": "Cliente Genérico - Domestic Trip", "amount": 335.0, "vat_amount": 0, "gross_total": 335.0, "linked_costs": []},
            {"id": "s20", "number": "FT E2025/2 / JJGBTD9W-2", "date": "2025-01-03", "client": "Cliente 1363 - Weekend Break", "amount": 1215.0, "vat_amount": 0, "gross_total": 1215.0, "linked_costs": []},
            {"id": "s21", "number": "FR E2025/1 / JJGWTD95-1", "date": "2025-01-03", "client": "Cliente Genérico - Domestic Trip", "amount": 492.66, "vat_amount": 0, "gross_total": 492.66, "linked_costs": []},
            {"id": "s22", "number": "FT E2025/1 / JJGBTD9W-1", "date": "2025-01-03", "client": "Cliente 7386 - Domestic Trip", "amount": 300.0, "vat_amount": 0, "gross_total": 300.0, "linked_costs": []},
            {"id": "s23", "number": "FT E2025/4 / JJGBTD9W-4", "date": "2025-01-03", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 161.0, "vat_amount": 0, "gross_total": 161.0, "linked_costs": []},
            {"id": "s24", "number": "FT E2025/5 / JJGBTD9W-5", "date": "2025-01-03", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 161.0, "vat_amount": 0, "gross_total": 161.0, "linked_costs": []},
            {"id": "s25", "number": "FT E2025/3 / JJGBTD9W-3", "date": "2025-01-03", "client": "Pedro Costa - Familiar - Domestic Trip", "amount": 406.0, "vat_amount": 0, "gross_total": 406.0, "linked_costs": []},
            {"id": "s26", "number": "FT E2025/6 / JJGBTD9W-6", "date": "2025-01-03", "client": "Cliente 7162 - Domestic Trip", "amount": 195.0, "vat_amount": 0, "gross_total": 195.0, "linked_costs": []}
        ],
        "costs": [
            {"id": "c1", "supplier": "Gms-Store Informa‹o e Tecnologia S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-10", "amount": 2955.98, "vat_amount": 679.8754, "gross_total": 3635.8554, "document_number": "FT VD202509261AAA002/0000389 / JJ427H6B-0000389", "linked_sales": []},
            {"id": "c2", "supplier": "Auto Taxis Andrafer Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-19", "amount": 5310.0, "vat_amount": 1221.3, "gross_total": 6531.3, "document_number": "FT AFT/254 / JFWB93T6-254", "linked_sales": []},
            {"id": "c3", "supplier": "Land Of Alandroal - Agricultura e Turismo, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-03", "amount": 1343.53, "vat_amount": 309.0119, "gross_total": 1652.5419, "document_number": "FR 1043200/1116 / JFCHC4D2-1116", "linked_sales": []},
            {"id": "c4", "supplier": "Tangomaos Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-03", "amount": 319.8, "vat_amount": 73.554, "gross_total": 393.354, "document_number": "FR 2025/3 / JJ7TVJ5Y-3", "linked_sales": []},
            {"id": "c5", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-12", "amount": 315.0, "vat_amount": 72.45, "gross_total": 387.45, "document_number": "FTR 25001/8055 / JJ3X6VWM-8055", "linked_sales": []},
            {"id": "c6", "supplier": "Ana Margarida Cruz Caldas da Costa", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-11", "amount": 307.5, "vat_amount": 70.72500000000001, "gross_total": 378.225, "document_number": "FR ATSIRE01FR/40 / JJXH4BMR-40", "linked_sales": []},
            {"id": "c7", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-11", "amount": 245.7, "vat_amount": 56.511, "gross_total": 302.21099999999996, "document_number": "FTR 25001/3794 / JJ3X6VWM-3794", "linked_sales": []},
            {"id": "c8", "supplier": "Paberesbares Actividades Hotelaria Lda", "description": "Alojamento - Estadia turística", "date": "2025-03-15", "amount": 278.0, "vat_amount": 63.940000000000005, "gross_total": 341.94, "document_number": "FR A2531/620 / JJ99KCD9-620", "linked_sales": []},
            {"id": "c9", "supplier": "Paberesbares Actividades Hotelaria Lda", "description": "Alojamento - Estadia turística", "date": "2025-01-07", "amount": 264.0, "vat_amount": 60.720000000000006, "gross_total": 324.71999999999997, "document_number": "FR A2531/67 / JJ99KCD9-67", "linked_sales": []},
            {"id": "c10", "supplier": "Mugasa Restaurante Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-24", "amount": 254.35, "vat_amount": 58.5005, "gross_total": 312.8505, "document_number": "FACBAR_CF-N 3/28121 / JFNDZ8WD-28121", "linked_sales": []},
            {"id": "c11", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-05", "amount": 140.0, "vat_amount": 32.2, "gross_total": 172.2, "document_number": "FTR 25001/6970 / JJ3X6VWM-6970", "linked_sales": []},
            {"id": "c12", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-18", "amount": 140.0, "vat_amount": 32.2, "gross_total": 172.2, "document_number": "FTR 25001/4721 / JJ3X6VWM-4721", "linked_sales": []},
            {"id": "c13", "supplier": "Amiroad, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-14", "amount": 450.0, "vat_amount": 103.5, "gross_total": 553.5, "document_number": "FA FA2025/287 / JJ4CSP54-287", "linked_sales": []},
            {"id": "c14", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-11", "amount": 123.14, "vat_amount": 28.322200000000002, "gross_total": 151.4622, "document_number": "FTR 25001/3795 / JJ3X6VWM-3795", "linked_sales": []},
            {"id": "c15", "supplier": "Acustica Suave Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-17", "amount": 114.0, "vat_amount": 26.220000000000002, "gross_total": 140.22, "document_number": "4 218/156 / JJP9V6H6-156", "linked_sales": []},
            {"id": "c16", "supplier": "Amiroad, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-20", "amount": 361.0, "vat_amount": 83.03, "gross_total": 444.03, "document_number": "FA FA2025/111 / JJ4CSP54-111", "linked_sales": []},
            {"id": "c17", "supplier": "Acustica Suave Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-14", "amount": 60.0, "vat_amount": 13.8, "gross_total": 73.8, "document_number": "4 218/150 / JJP9V6H6-150", "linked_sales": []},
            {"id": "c18", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-25", "amount": 52.0, "vat_amount": 11.96, "gross_total": 63.96, "document_number": "FTR 25001/10287 / JJ3X6VWM-10287", "linked_sales": []},
            {"id": "c19", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-26", "amount": 41.6, "vat_amount": 9.568000000000001, "gross_total": 51.168, "document_number": "FTR 25001/10491 / JJ3X6VWM-10491", "linked_sales": []},
            {"id": "c20", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 35.0, "vat_amount": 8.05, "gross_total": 43.05, "document_number": "FTR 25001/9729 / JJ3X6VWM-9729", "linked_sales": []},
            {"id": "c21", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-27", "amount": 35.0, "vat_amount": 8.05, "gross_total": 43.05, "document_number": "FTR 25001/2335 / JJ3X6VWM-2335", "linked_sales": []},
            {"id": "c22", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-16", "amount": 34.0, "vat_amount": 7.82, "gross_total": 41.82, "document_number": "FTR 25001/1406 / JJ3X6VWM-1406", "linked_sales": []},
            {"id": "c23", "supplier": "Nata da Nata Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-05", "amount": 42.15, "vat_amount": 9.6945, "gross_total": 51.8445, "document_number": "FS 012/30736 / JJRMMDH4-30736", "linked_sales": []},
            {"id": "c24", "supplier": "Manuel Castanheira Martinez Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 25.5, "vat_amount": 5.865, "gross_total": 31.365, "document_number": "FS 003/374749 / JF286D9F-374749", "linked_sales": []},
            {"id": "c25", "supplier": "Manuel Castanheira Martinez Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 24.5, "vat_amount": 5.635000000000001, "gross_total": 30.134999999999998, "document_number": "FS 003/367274 / JF286D9F-367274", "linked_sales": []},
            {"id": "c26", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-23", "amount": 17.05, "vat_amount": 3.9215000000000004, "gross_total": 20.9715, "document_number": "FR 25A/7357 / JJ4354HH-7357", "linked_sales": []},
            {"id": "c27", "supplier": "Luis Os—rio Sociedade Por Quotas, Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 16.0, "vat_amount": 3.68, "gross_total": 19.68, "document_number": "FS 25092/931 / JJS7VT82-931", "linked_sales": []},
            {"id": "c28", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-05", "amount": 14.65, "vat_amount": 3.3695000000000004, "gross_total": 18.0195, "document_number": "FR 25A/22640 / JJ4354HH-22640", "linked_sales": []},
            {"id": "c29", "supplier": "Ideias Circulares Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 12.15, "vat_amount": 2.7945, "gross_total": 14.9445, "document_number": "1 IDE23/41556 / JF9Y9PR9-41556", "linked_sales": []},
            {"id": "c30", "supplier": "Auto Taxis Ludovino Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-22", "amount": 40.0, "vat_amount": 9.200000000000001, "gross_total": 49.2, "document_number": "FR 202212/1299 / JFWXS6WS-1299", "linked_sales": []},
            {"id": "c31", "supplier": "Blueticket - Servios de Bilhetica S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-11", "amount": 10.7, "vat_amount": 2.461, "gross_total": 13.161, "document_number": "FS 0000000253/0001504595 / JFHXXF2G-0001504595", "linked_sales": []},
            {"id": "c32", "supplier": "Solar da Rua da Madalena Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 10.4, "vat_amount": 2.3920000000000003, "gross_total": 12.792, "document_number": "1 2301A1/41641 / JFRVGR7D-41641", "linked_sales": []},
            {"id": "c33", "supplier": "True Talented Company Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-09", "amount": 9.5, "vat_amount": 2.185, "gross_total": 11.685, "document_number": "TV T022/008522 / JF722DZX", "linked_sales": []},
            {"id": "c34", "supplier": "Nata da Nata Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-23", "amount": 15.4, "vat_amount": 3.5420000000000003, "gross_total": 18.942, "document_number": "FS 002/208129 / JJKWSCZX-208129", "linked_sales": []},
            {"id": "c35", "supplier": "Solar da Rua da Madalena Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 9.4, "vat_amount": 2.1620000000000004, "gross_total": 11.562, "document_number": "1 2301A1/42575 / JFRVGR7D-42575", "linked_sales": []},
            {"id": "c36", "supplier": "Vn‰ncio & Santos Unipessoal, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-24", "amount": 30.07, "vat_amount": 6.9161, "gross_total": 36.9861, "document_number": "FR T0002/120262 / JFSZFTRG-120262", "linked_sales": []},
            {"id": "c37", "supplier": "D R a - Produtos Regionais Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 13.5, "vat_amount": 3.105, "gross_total": 16.605, "document_number": "FS 6/32782 / JJZWRS68-32782", "linked_sales": []},
            {"id": "c38", "supplier": "Salsicharia Amarantina Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 13.5, "vat_amount": 3.105, "gross_total": 16.605, "document_number": "TV TV0124/770 / JJXPRDHG-770", "linked_sales": []},
            {"id": "c39", "supplier": "Prime Food, S.A.", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 13.3, "vat_amount": 3.059, "gross_total": 16.359, "document_number": "FS 022/3127407 / JFF2B6SN-3127407", "linked_sales": []},
            {"id": "c40", "supplier": "Ideias Circulares Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 8.1, "vat_amount": 1.863, "gross_total": 9.963, "document_number": "1 IDE23/42389 / JF9Y9PR9-42389", "linked_sales": []},
            {"id": "c41", "supplier": "Luis Os—rio Sociedade Por Quotas, Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 8.0, "vat_amount": 1.84, "gross_total": 9.84, "document_number": "FS 25092/967 / JJS7VT82-967", "linked_sales": []},
            {"id": "c42", "supplier": "Solar da Rua da Madalena Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-11", "amount": 7.8, "vat_amount": 1.794, "gross_total": 9.594, "document_number": "1 2301A1/40725 / JFRVGR7D-40725", "linked_sales": []},
            {"id": "c43", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 7.75, "vat_amount": 1.7825, "gross_total": 9.5325, "document_number": "FR 25A/32247 / JJ4354HH-32247", "linked_sales": []},
            {"id": "c44", "supplier": "Antiga Confeitaria Belem Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-19", "amount": 12.3, "vat_amount": 2.829, "gross_total": 15.129000000000001, "document_number": "FS 901/6842046 / JFSTT664-6842046", "linked_sales": []},
            {"id": "c45", "supplier": "Motivos Apressados Servios e Consultoria Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-24", "amount": 23.16, "vat_amount": 5.3268, "gross_total": 28.4868, "document_number": "FR T0001/2932 / JF8ZV758-2932", "linked_sales": []},
            {"id": "c46", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 6.2, "vat_amount": 1.4260000000000002, "gross_total": 7.626, "document_number": "FR 25A/18301 / JJ4354HH-18301", "linked_sales": []},
            {"id": "c47", "supplier": "Solar da Rua da Madalena Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 6.0, "vat_amount": 1.3800000000000001, "gross_total": 7.38, "document_number": "1 2301A1/40559 / JFRVGR7D-40559", "linked_sales": []},
            {"id": "c48", "supplier": "Casa do Alentejo", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 9.3, "vat_amount": 2.1390000000000002, "gross_total": 11.439, "document_number": "FS 101/522422 / JFSPZGMC-522422", "linked_sales": []},
            {"id": "c49", "supplier": "A Brasileira Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 9.1, "vat_amount": 2.093, "gross_total": 11.193, "document_number": "FS 45A2506/5663 / JJS8MXY8-5663", "linked_sales": []},
            {"id": "c50", "supplier": "Ideias Circulares Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 5.4, "vat_amount": 1.2420000000000002, "gross_total": 6.642, "document_number": "1 IDE23/43875 / JF9Y9PR9-43875", "linked_sales": []},
            {"id": "c51", "supplier": "Casa S‹o Miguel Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-11", "amount": 5.4, "vat_amount": 1.2420000000000002, "gross_total": 6.642, "document_number": "FS 25002/4252 / JJS36NN2-4252", "linked_sales": []},
            {"id": "c52", "supplier": "Moinhos Espinheira Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 8.0, "vat_amount": 1.84, "gross_total": 9.84, "document_number": "1 A/171005 / JFNXH8JF-171005", "linked_sales": []},
            {"id": "c53", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 4.65, "vat_amount": 1.0695000000000001, "gross_total": 5.7195, "document_number": "FR 25A/23689 / JJ4354HH-23689", "linked_sales": []},
            {"id": "c54", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-25", "amount": 14.25, "vat_amount": 3.2775000000000003, "gross_total": 17.5275, "document_number": "FTR 25001/10259 / JJ3X6VWM-10259", "linked_sales": []},
            {"id": "c55", "supplier": "Blueticket - Servios de Bilhetica S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 3.69, "vat_amount": 0.8487, "gross_total": 4.5386999999999995, "document_number": "FS 0000000253/0001579250 / JFHXXF2G-0001579250", "linked_sales": []},
            {"id": "c56", "supplier": "Terlinda Taxis Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-11", "amount": 12.0, "vat_amount": 2.7600000000000002, "gross_total": 14.76, "document_number": "FR 202213/876 / JFHC9MTJ-876", "linked_sales": []},
            {"id": "c57", "supplier": "Jotoservice - Servios Empresariais Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-24", "amount": 11.45, "vat_amount": 2.6334999999999997, "gross_total": 14.083499999999999, "document_number": "FR T0006/8346 / JJWZNG2W-8346", "linked_sales": []},
            {"id": "c58", "supplier": "Nata da Nata Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 5.6, "vat_amount": 1.288, "gross_total": 6.888, "document_number": "FS A25VSEVFO20/113168 / JFCHYSZK-113168", "linked_sales": []},
            {"id": "c59", "supplier": "Prime Food, S.A.", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 5.6, "vat_amount": 1.288, "gross_total": 6.888, "document_number": "FS 125/1612252 / JFFSBXVK-1612252", "linked_sales": []},
            {"id": "c60", "supplier": "Abcissa Festiva, Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-26", "amount": 11.06, "vat_amount": 2.5438, "gross_total": 13.6038, "document_number": "FR T0001/97306 / JFY853TK-97306", "linked_sales": []},
            {"id": "c61", "supplier": "Auto Taxis Central Vila Verde Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-10", "amount": 10.95, "vat_amount": 2.5185, "gross_total": 13.468499999999999, "document_number": "FR 202212/3613 / JFT58YCD-3613", "linked_sales": []},
            {"id": "c62", "supplier": "Angelo Rodrigo - Transporte de Passageiros Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-03", "amount": 10.96, "vat_amount": 2.5208000000000004, "gross_total": 13.4808, "document_number": "FR T0001/4405 / JFC32M2M-4405", "linked_sales": []},
            {"id": "c63", "supplier": "Weekendocean Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-25", "amount": 10.53, "vat_amount": 2.4219, "gross_total": 12.951899999999998, "document_number": "FR T0001/5897 / JFY6DWYJ-5897", "linked_sales": []},
            {"id": "c64", "supplier": "Cravo Popular - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-02", "amount": -3.9, "vat_amount": -0.897, "gross_total": -4.797, "document_number": "4 C25/1 / JJG3NXKT-1", "linked_sales": []},
            {"id": "c65", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 3.1, "vat_amount": 0.7130000000000001, "gross_total": 3.813, "document_number": "FR 25A/32651 / JJ4354HH-32651", "linked_sales": []},
            {"id": "c66", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 3.1, "vat_amount": 0.7130000000000001, "gross_total": 3.813, "document_number": "FR 25A/32311 / JJ4354HH-32311", "linked_sales": []},
            {"id": "c67", "supplier": "Francisco Espinheira e Cia Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 3.1, "vat_amount": 0.7130000000000001, "gross_total": 3.813, "document_number": "FS 22/442765 / JFZBK82H-442765", "linked_sales": []},
            {"id": "c68", "supplier": "Hbdrive Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 10.33, "vat_amount": 2.3759, "gross_total": 12.7059, "document_number": "FR T0001/3904 / JJFS7N2S-3904", "linked_sales": []},
            {"id": "c69", "supplier": "Ginginha Cima Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-17", "amount": 3.1, "vat_amount": 0.7130000000000001, "gross_total": 3.813, "document_number": "FR 25A/26787 / JJ4354HH-26787", "linked_sales": []},
            {"id": "c70", "supplier": "Adorable Parallel Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-13", "amount": 10.27, "vat_amount": 2.3621, "gross_total": 12.6321, "document_number": "FR T0005/10991 / JFM4CPRF-10991", "linked_sales": []},
            {"id": "c71", "supplier": "Herois D Inverno Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-26", "amount": 10.32, "vat_amount": 2.3736, "gross_total": 12.6936, "document_number": "FR T0005/63708 / JFMS8HC4-63708", "linked_sales": []},
            {"id": "c72", "supplier": "Particula Malabarista Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-17", "amount": 10.01, "vat_amount": 2.3023000000000002, "gross_total": 12.312299999999999, "document_number": "FR T0001/18559 / JFRXJ8PB-18559", "linked_sales": []},
            {"id": "c73", "supplier": "Expandsummer - Transportes Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-07", "amount": 9.96, "vat_amount": 2.2908000000000004, "gross_total": 12.250800000000002, "document_number": "FR T0004/8400 / JFSM6DG8-8400", "linked_sales": []},
            {"id": "c74", "supplier": "Solar da Rua da Madalena Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 3.0, "vat_amount": 0.6900000000000001, "gross_total": 3.69, "document_number": "1 2301A1/39285 / JFRVGR7D-39285", "linked_sales": []},
            {"id": "c75", "supplier": "Al-Baki Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-16", "amount": 9.73, "vat_amount": 2.2379000000000002, "gross_total": 11.9679, "document_number": "FR T0004/71068 / JFMRDD8P-71068", "linked_sales": []},
            {"id": "c76", "supplier": "Jotoservice - Servios Empresariais Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-14", "amount": 9.66, "vat_amount": 2.2218, "gross_total": 11.8818, "document_number": "FR T0006/7251 / JJWZNG2W-7251", "linked_sales": []},
            {"id": "c77", "supplier": "Habil Sintonia Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-09", "amount": 9.78, "vat_amount": 2.2494, "gross_total": 12.029399999999999, "document_number": "FR T0006/27421 / JJWHN7SW-27421", "linked_sales": []},
            {"id": "c78", "supplier": "Dormem Versos Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 9.74, "vat_amount": 2.2402, "gross_total": 11.9802, "document_number": "FR T0001/11216 / JFY6GDJG-11216", "linked_sales": []},
            {"id": "c79", "supplier": "Lufada Prometida Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-25", "amount": 9.61, "vat_amount": 2.2103, "gross_total": 11.8203, "document_number": "FR T0001/1188381 / JFG9XNR5-1188381", "linked_sales": []},
            {"id": "c80", "supplier": "Paulo Godinho Nunes Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-20", "amount": 9.29, "vat_amount": 2.1367, "gross_total": 11.426699999999999, "document_number": "FR T0005/6241 / JFMPCSD7-6241", "linked_sales": []},
            {"id": "c81", "supplier": "Alan Costa Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-22", "amount": 9.11, "vat_amount": 2.0953, "gross_total": 11.2053, "document_number": "FR T0001/4731 / JJ28NW5K-4731", "linked_sales": []},
            {"id": "c82", "supplier": "Grameen Mart Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-21", "amount": 8.95, "vat_amount": 2.0585, "gross_total": 11.0085, "document_number": "FR T0006/3428 / JJKCG75M-3428", "linked_sales": []},
            {"id": "c83", "supplier": "Ready To Go Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-26", "amount": 8.94, "vat_amount": 2.0562, "gross_total": 10.9962, "document_number": "FR T0004/9064 / JF4CWS58-9064", "linked_sales": []},
            {"id": "c84", "supplier": "Fluxo Recheado - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-19", "amount": 8.9, "vat_amount": 2.047, "gross_total": 10.947000000000001, "document_number": "FR T0001/24304 / JF7X5DSR-24304", "linked_sales": []},
            {"id": "c85", "supplier": "Yellow Cab Taxis Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-24", "amount": 8.44, "vat_amount": 1.9412, "gross_total": 10.3812, "document_number": "FR T0005/178716 / JFMR87VG-178716", "linked_sales": []},
            {"id": "c86", "supplier": "Nata da Nata Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 4.2, "vat_amount": 0.9660000000000001, "gross_total": 5.166, "document_number": "FS 002/255663 / JJKWSCZX-255663", "linked_sales": []},
            {"id": "c87", "supplier": "Obaydur Rahman Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-13", "amount": 8.33, "vat_amount": 1.9159000000000002, "gross_total": 10.2459, "document_number": "FR T0002/10529 / JF3HHXFP-10529", "linked_sales": []},
            {"id": "c88", "supplier": "Motivinvulgar Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-02", "amount": 8.39, "vat_amount": 1.9297000000000002, "gross_total": 10.319700000000001, "document_number": "FR T0001/21231 / JFPRDYGB-21231", "linked_sales": []},
            {"id": "c89", "supplier": "Raciocinio Ordenado - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-28", "amount": 8.34, "vat_amount": 1.9182000000000001, "gross_total": 10.2582, "document_number": "FR T0003/259119 / JFMSDWSM-259119", "linked_sales": []},
            {"id": "c90", "supplier": "Cravo Popular - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-07", "amount": -2.9, "vat_amount": -0.667, "gross_total": -3.5669999999999997, "document_number": "4 C25/2 / JJG3NXKT-2", "linked_sales": []},
            {"id": "c91", "supplier": "Kirti Parshad Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 8.05, "vat_amount": 1.8515000000000001, "gross_total": 9.9015, "document_number": "FR T0004/51005 / JFS8JXMY-51005", "linked_sales": []},
            {"id": "c92", "supplier": "Onda Libertina - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-09", "amount": 8.21, "vat_amount": 1.8883000000000003, "gross_total": 10.0983, "document_number": "FR T0001/19263 / JJFCZDS4-19263", "linked_sales": []},
            {"id": "c93", "supplier": "Elenco Unico Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 4.0, "vat_amount": 0.92, "gross_total": 4.92, "document_number": "FS 00002/604808 / JF27P3X3-604808", "linked_sales": []},
            {"id": "c94", "supplier": "Elenco Unico Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 4.0, "vat_amount": 0.92, "gross_total": 4.92, "document_number": "FS 00002/600510 / JF27P3X3-600510", "linked_sales": []},
            {"id": "c95", "supplier": "Mayara & Ribeiro Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-04", "amount": 7.99, "vat_amount": 1.8377000000000001, "gross_total": 9.8277, "document_number": "FR T0001/48175 / JFGKBDM5-48175", "linked_sales": []},
            {"id": "c96", "supplier": "Cravo Popular - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-30", "amount": 3.9, "vat_amount": 0.897, "gross_total": 4.797, "document_number": "1 B/44264 / JFWNH5R3-44264", "linked_sales": []},
            {"id": "c97", "supplier": "Multiplos Genu’nos Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-19", "amount": 7.7, "vat_amount": 1.7710000000000001, "gross_total": 9.471, "document_number": "FR T0005/22855 / JFM28GWR-22855", "linked_sales": []},
            {"id": "c98", "supplier": "Cravo Popular - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-14", "amount": -3.8, "vat_amount": -0.874, "gross_total": -4.6739999999999995, "document_number": "4 C25/4 / JJG3NXKT-4", "linked_sales": []},
            {"id": "c99", "supplier": "Vintage Conjugation - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-26", "amount": 7.74, "vat_amount": 1.7802000000000002, "gross_total": 9.5202, "document_number": "FR T0006/3838 / JJVXDKKX-3838", "linked_sales": []},
            {"id": "c100", "supplier": "Jasmine Symbol - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-05", "amount": 7.75, "vat_amount": 1.7825, "gross_total": 9.5325, "document_number": "FR T0002/4162 / JFRJ645V-4162", "linked_sales": []},
            {"id": "c101", "supplier": "Supreme Wishes - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-16", "amount": 7.67, "vat_amount": 1.7641, "gross_total": 9.434099999999999, "document_number": "FR T0003/13169 / JFSX5FPV-13169", "linked_sales": []},
            {"id": "c102", "supplier": "Turtle Mission Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-28", "amount": 7.49, "vat_amount": 1.7227000000000001, "gross_total": 9.2127, "document_number": "FR T0001/17999 / JFRC77TC-17999", "linked_sales": []},
            {"id": "c103", "supplier": "Obedientbutton - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-24", "amount": 7.49, "vat_amount": 1.7227000000000001, "gross_total": 9.2127, "document_number": "FR T0002/2950 / JFS5YJVP-2950", "linked_sales": []},
            {"id": "c104", "supplier": "Lufada Prometida Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 7.32, "vat_amount": 1.6836000000000002, "gross_total": 9.0036, "document_number": "FR T0001/1086442 / JFG9XNR5-1086442", "linked_sales": []},
            {"id": "c105", "supplier": "Marathon Factor Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-21", "amount": 7.16, "vat_amount": 1.6468, "gross_total": 8.8068, "document_number": "FR T0004/25478 / JF4HZ2CP-25478", "linked_sales": []},
            {"id": "c106", "supplier": "Competente Saturno Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-15", "amount": 7.02, "vat_amount": 1.6146, "gross_total": 8.634599999999999, "document_number": "FR T0003/12857 / JF7PJCW9-12857", "linked_sales": []},
            {"id": "c107", "supplier": "Autocoope Coop Taxis Lisboa Crl", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-02", "amount": 6.9, "vat_amount": 1.5870000000000002, "gross_total": 8.487, "document_number": "FR 3000141/34 / JJR5VFB3-34", "linked_sales": []},
            {"id": "c108", "supplier": "Flagrante Desafio - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-20", "amount": 6.91, "vat_amount": 1.5893000000000002, "gross_total": 8.4993, "document_number": "FR T0004/14916 / JFS2544G-14916", "linked_sales": []},
            {"id": "c109", "supplier": "Islam Sumon Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-25", "amount": 6.95, "vat_amount": 1.5985, "gross_total": 8.5485, "document_number": "FR T0006/657 / JJBGV8D8-657", "linked_sales": []},
            {"id": "c110", "supplier": "Bruno Daniel Lopes Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-17", "amount": 6.78, "vat_amount": 1.5594000000000001, "gross_total": 8.3394, "document_number": "FR T0002/8042 / JF744VX9-8042", "linked_sales": []},
            {"id": "c111", "supplier": "Circuito Refinado - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-12", "amount": 6.44, "vat_amount": 1.4812, "gross_total": 7.921200000000001, "document_number": "FR T0001/17789 / JFWSXJM3-17789", "linked_sales": []},
            {"id": "c112", "supplier": "Viliv Internacional, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 6.24, "vat_amount": 1.4352, "gross_total": 7.6752, "document_number": "FT BOLTRH002/116 / JJ2SMMSF-116", "linked_sales": []},
            {"id": "c113", "supplier": "Afonso e Torres Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-30", "amount": 3.0, "vat_amount": 0.6900000000000001, "gross_total": 3.69, "document_number": "1 A/143542 / JFTWHFV7-143542", "linked_sales": []},
            {"id": "c114", "supplier": "Audrina Autos, Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 5.97, "vat_amount": 1.3731, "gross_total": 7.3431, "document_number": "FR T0004/106044 / JFHTTX64-106044", "linked_sales": []},
            {"id": "c115", "supplier": "Rotas Acetinadas - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-15", "amount": 5.82, "vat_amount": 1.3386000000000002, "gross_total": 7.1586, "document_number": "FR T0001/55734 / JFDM6DPF-55734", "linked_sales": []},
            {"id": "c116", "supplier": "Horas Esperanosas Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-02", "amount": 5.82, "vat_amount": 1.3386000000000002, "gross_total": 7.1586, "document_number": "FR T0006/1023 / JJ9SRBPP-1023", "linked_sales": []},
            {"id": "c117", "supplier": "Grandiosa Miragem - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-11", "amount": 5.87, "vat_amount": 1.3501, "gross_total": 7.2201, "document_number": "FR T0004/4951 / JFST5BKB-4951", "linked_sales": []},
            {"id": "c118", "supplier": "Zodiaco Navegador Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-31", "amount": 5.86, "vat_amount": 1.3478, "gross_total": 7.207800000000001, "document_number": "FR T0001/2998 / JFCBM3FY-2998", "linked_sales": []},
            {"id": "c119", "supplier": "Happykey Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-30", "amount": 2.9, "vat_amount": 0.667, "gross_total": 3.5669999999999997, "document_number": "FS 002/541621 / JFTBYV4D-541621", "linked_sales": []},
            {"id": "c120", "supplier": "Pina Barbosa - Viagens Unipessoal Lda", "description": "Serviços turísticos - Excursões", "date": "2025-01-29", "amount": 5.64, "vat_amount": 1.2972, "gross_total": 6.9372, "document_number": "FR T0004/16374 / JFHKTTCY-16374", "linked_sales": []},
            {"id": "c121", "supplier": "Data Park Pt Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-08", "amount": 5.46, "vat_amount": 1.2558, "gross_total": 6.7158, "document_number": "FR T0001/125081 / JFYK6GZS-125081", "linked_sales": []},
            {"id": "c122", "supplier": "Ideia Ardente Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-17", "amount": 5.29, "vat_amount": 1.2167000000000001, "gross_total": 6.5067, "document_number": "FR T0002/11258 / JFSFYJ3N-11258", "linked_sales": []},
            {"id": "c123", "supplier": "Alma Poderosa - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-16", "amount": 5.34, "vat_amount": 1.2282, "gross_total": 6.5682, "document_number": "FR T0001/19396 / JFYT4BTF-19396", "linked_sales": []},
            {"id": "c124", "supplier": "L’rios Imaculados, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-20", "amount": 4.86, "vat_amount": 1.1178000000000001, "gross_total": 5.9778, "document_number": "FR T0006/18293 / JJKJF94T-18293", "linked_sales": []},
            {"id": "c125", "supplier": "Abdullah & Amir Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-19", "amount": 4.88, "vat_amount": 1.1224, "gross_total": 6.0024, "document_number": "FR T0003/43909 / JFSBS35P-43909", "linked_sales": []},
            {"id": "c126", "supplier": "Bussola da Cidade - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-10", "amount": 4.9, "vat_amount": 1.1270000000000002, "gross_total": 6.027, "document_number": "FR T0001/3826 / JFYFW59D-3826", "linked_sales": []},
            {"id": "c127", "supplier": "Thadeu Vingadas Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-10", "amount": 4.93, "vat_amount": 1.1339, "gross_total": 6.063899999999999, "document_number": "FR T0002/27333 / JFS3C9JW-27333", "linked_sales": []},
            {"id": "c128", "supplier": "Destinos & Manobras Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-08", "amount": 4.9, "vat_amount": 1.1270000000000002, "gross_total": 6.027, "document_number": "FR T0004/6701 / JFSG5MWP-6701", "linked_sales": []},
            {"id": "c129", "supplier": "Sabbir Ahmed Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-08", "amount": 4.9, "vat_amount": 1.1270000000000002, "gross_total": 6.027, "document_number": "FR T0004/12802 / JF7K7328-12802", "linked_sales": []},
            {"id": "c130", "supplier": "Grameen Mart Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-05", "amount": 4.9, "vat_amount": 1.1270000000000002, "gross_total": 6.027, "document_number": "FR T0006/2854 / JJKCG75M-2854", "linked_sales": []},
            {"id": "c131", "supplier": "Pedido Sublime - Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-19", "amount": 4.55, "vat_amount": 1.0465, "gross_total": 5.5965, "document_number": "FR T0001/2158 / JFP586ZM-2158", "linked_sales": []},
            {"id": "c132", "supplier": "Passos e Trajetorias - Transportes Unipessoal Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-21", "amount": 4.45, "vat_amount": 1.0235, "gross_total": 5.4735000000000005, "document_number": "FR T0004/54266 / JFSPF64T-54266", "linked_sales": []},
            {"id": "c133", "supplier": "Mello de Castro & Bastos Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-04", "amount": 4.48, "vat_amount": 1.0304000000000002, "gross_total": 5.510400000000001, "document_number": "FR T0001/102964 / JFW3R5JC-102964", "linked_sales": []},
            {"id": "c134", "supplier": "World Idols, Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-12", "amount": 3.92, "vat_amount": 0.9016000000000001, "gross_total": 4.8216, "document_number": "FR T0005/21751 / JFMFCKM8-21751", "linked_sales": []},
            {"id": "c135", "supplier": "Cravo Popular - Lda", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-03", "amount": -1.8, "vat_amount": -0.41400000000000003, "gross_total": -2.214, "document_number": "4 C25/3 / JJG3NXKT-3", "linked_sales": []},
            {"id": "c136", "supplier": "Margarida Nobre Nunes", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-31", "amount": 700.0, "vat_amount": 161.0, "gross_total": 861.0, "document_number": "FR ATSIRE01FR/11 / JJX9849Y-11", "linked_sales": []},
            {"id": "c137", "supplier": "Ana Margarida da Silva Calada", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-30", "amount": 300.0, "vat_amount": 69.0, "gross_total": 369.0, "document_number": "FR ATSIRE01FR/6 / JJM4F93R-6", "linked_sales": []},
            {"id": "c138", "supplier": "Bernardo Franco Rufino", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-29", "amount": 50.0, "vat_amount": 11.5, "gross_total": 61.5, "document_number": "FR ATSIRE01FR/26 / JJXP455H-26", "linked_sales": []},
            {"id": "c139", "supplier": "Funda‹o Cultursintra, Fp", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 50.0, "vat_amount": 11.5, "gross_total": 61.5, "document_number": "FT 0000000420/0001039087 / JFHKSVHS-0001039087", "linked_sales": []},
            {"id": "c140", "supplier": "Museus e Monumentos de Portugal e P E", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-18", "amount": 72.0, "vat_amount": 16.560000000000002, "gross_total": 88.56, "document_number": "SL W1-7/108556 / JJ6FW99Z-108556", "linked_sales": []},
            {"id": "c141", "supplier": "Fabrica da Igreja Paroquial da Freguesia de S Pedro", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-13", "amount": 12.0, "vat_amount": 2.7600000000000002, "gross_total": 14.76, "document_number": "FT 25010/482", "linked_sales": []},
            {"id": "c142", "supplier": "Cabido da Basilica Metropolitana de Evora", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-13", "amount": 8.0, "vat_amount": 1.84, "gross_total": 9.84, "document_number": "FS FS.2025/5688 / JJ9C2CK5-5688", "linked_sales": []},
            {"id": "c143", "supplier": "Jose Pedro Moreira Melo", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-11", "amount": 930.0, "vat_amount": 213.9, "gross_total": 1143.9, "document_number": "FR ATSIRE01FR/4 / JJMPJR67-4", "linked_sales": []},
            {"id": "c144", "supplier": "Assoc Comercial Porto", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-09", "amount": 88.0, "vat_amount": 20.240000000000002, "gross_total": 108.24, "document_number": "FT 10FR25/011988 / JJ4S7F3K-011988", "linked_sales": []},
            {"id": "c145", "supplier": "Mariana Fonseca da Silva Delgado", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-07", "amount": 150.0, "vat_amount": 34.5, "gross_total": 184.5, "document_number": "FR ATSIRE01FR/13 / JJXMPB7F-13", "linked_sales": []},
            {"id": "c146", "supplier": "Museus e Monumentos de Portugal e P E", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-05", "amount": 30.0, "vat_amount": 6.9, "gross_total": 36.9, "document_number": "SL W1-7/104825 / JJ6FW99Z-104825", "linked_sales": []},
            {"id": "c147", "supplier": "Rita Cid-Torres Portugal Azevedo", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-28", "amount": 210.0, "vat_amount": 48.300000000000004, "gross_total": 258.3, "document_number": "FR ATSIRE01FR/15 / JJXGCH5S-15", "linked_sales": []},
            {"id": "c148", "supplier": "Ana Margarida da Silva Calada", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-28", "amount": 100.0, "vat_amount": 23.0, "gross_total": 123.0, "document_number": "FR ATSIRE01FR/5 / JJM4F93R-5", "linked_sales": []},
            {"id": "c149", "supplier": "Margarida Nobre Nunes", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-27", "amount": 250.0, "vat_amount": 57.5, "gross_total": 307.5, "document_number": "FR ATSIRE01FR/9 / JJX9849Y-9", "linked_sales": []},
            {"id": "c150", "supplier": "Bernardo Franco Rufino", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-27", "amount": 50.0, "vat_amount": 11.5, "gross_total": 61.5, "document_number": "FR ATSIRE01FR/21 / JJXP455H-21", "linked_sales": []},
            {"id": "c151", "supplier": "Museus e Monumentos de Portugal e P E", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-22", "amount": 45.0, "vat_amount": 10.35, "gross_total": 55.35, "document_number": "SL W1-7/102143 / JJ6FW99Z-102143", "linked_sales": []},
            {"id": "c152", "supplier": "Funda‹o Cultursintra, Fp", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-11", "amount": 145.0, "vat_amount": 33.35, "gross_total": 178.35, "document_number": "FT 0000000420/0001000961 / JFHKSVHS-0001000961", "linked_sales": []},
            {"id": "c153", "supplier": "Mariana Fonseca da Silva Delgado", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-05", "amount": 115.0, "vat_amount": 26.450000000000003, "gross_total": 141.45, "document_number": "FR ATSIRE01FR/12 / JJXMPB7F-12", "linked_sales": []},
            {"id": "c154", "supplier": "Rita Cid-Torres Portugal Azevedo", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-04", "amount": 220.0, "vat_amount": 50.6, "gross_total": 270.6, "document_number": "FR ATSIRE01FR/12 / JJXGCH5S-12", "linked_sales": []},
            {"id": "c155", "supplier": "Margarida Nobre Nunes", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-01", "amount": 150.0, "vat_amount": 34.5, "gross_total": 184.5, "document_number": "FR ATSIRE01FR/8 / JJX9849Y-8", "linked_sales": []},
            {"id": "c156", "supplier": "Rita Cid-Torres Portugal Azevedo", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-03", "amount": 435.0, "vat_amount": 100.05000000000001, "gross_total": 535.05, "document_number": "FR ATSIRE01FR/9 / JJXGCH5S-9", "linked_sales": []},
            {"id": "c157", "supplier": "Mariana Fonseca da Silva Delgado", "description": "Serviços diversos - Fornecimentos", "date": "2025-01-03", "amount": 45.0, "vat_amount": 10.35, "gross_total": 55.35, "document_number": "FR ATSIRE01FR/11 / JJXMPB7F-11", "linked_sales": []},
        ],
        "metadata": {
            "company_name": "Agência de Viagens Excel Modelo Lda",
            "tax_registration": "999999990",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "currency": "EUR",
            "source": "Excel modelo convertido automaticamente"
        }
    }
    
    # Store in sessions
    sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "data": mock_data,
        "filename": "demo_data.xml"
    }
    
    return {
        "session_id": session_id,
        "message": "Mock data loaded successfully",
        "sales_count": len(mock_data["sales"]),
        "costs_count": len(mock_data["costs"]),
        "sales": mock_data["sales"],
        "costs": mock_data["costs"]
    }


# For Railway deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)