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
from .calculator import VATCalculator
from .excel_export import ExcelExporter
from .validators import DataValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session storage (in-memory for simplicity)
sessions = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting IVA Margem Turismo API...")
    
    # Ensure required directories exist
    os.makedirs("temp", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # Clean old temp files
    clean_old_files()
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    

# Create FastAPI app
app = FastAPI(
    title="IVA Margem Turismo API",
    description="Sistema de cálculo de IVA sobre margem para agências de viagens",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:8080",  # Local development
        "https://iva-margem-turismo.vercel.app",  # Production frontend
        "https://*.vercel.app",  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def clean_old_files():
    """Clean temporary files older than 24 hours"""
    try:
        now = datetime.now()
        for folder in ['temp', 'uploads']:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if now - file_time > timedelta(hours=24):
                            os.remove(filepath)
                            logger.info(f"Removed old file: {filepath}")
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
        
        # Prepare response
        return UploadResponse(
            session_id=session_id,
            sales=data["sales"][:50],  # Limit to first 50 for response
            costs=data["costs"][:50],  # Limit to first 50 for response
            metadata=data["metadata"],
            summary={
                "total_sales": len(data["sales"]),
                "total_costs": len(data["costs"]),
                "sales_amount": sum(s["amount"] for s in data["sales"]),
                "costs_amount": sum(c["amount"] for c in data["costs"])
            }
        )
        
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
            
            # 1. Date proximity (max 40 points)
            date_diff = abs((sale_date - cost_date).days)
            if date_diff <= 7:
                date_score = 40 - (date_diff * 5)
                score += date_score
                reason_parts.append(f"Date proximity ({date_diff} days)")
            elif date_diff <= 30:
                date_score = 20 - (date_diff - 7) * 0.5
                score += date_score
                reason_parts.append(f"Date within month ({date_diff} days)")
                
            # 2. Value compatibility (max 30 points)
            if cost["amount"] < sale["amount"]:
                ratio = cost["amount"] / sale["amount"]
                if 0.1 <= ratio <= 0.8:  # Cost is 10-80% of sale
                    value_score = 30 * ratio
                    score += value_score
                    reason_parts.append(f"Value ratio {ratio:.1%}")
                    
            # 3. Description/client matching (max 30 points)
            cost_words = set(cost["description"].lower().split() + 
                           cost["supplier"].lower().split())
            sale_words = set(sale["client"].lower().split())
            
            # Remove common words
            common_words = cost_words.intersection(sale_words)
            common_words.discard("de")
            common_words.discard("da")
            common_words.discard("do")
            common_words.discard("e")
            
            if common_words:
                word_score = min(len(common_words) * 10, 30)
                score += word_score
                reason_parts.append(f"Keywords: {', '.join(common_words)}")
                
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
            {"id": "c1", "supplier": "Gms-Store Informação e Tecnologia S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-02-10", "amount": 2955.98, "vat_amount": 679.8754, "gross_total": 3635.8554, "document_number": "FT VD202509261AAA002/0000389 / JJ427H6B-0000389", "linked_sales": []},
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
            {"id": "c20", "supplier": "Parques de Sintra - Monte da Lua S A", "description": "Serviços diversos - Fornecimentos", "date": "2025-03-21", "amount": 35.0, "vat_amount": 8.05, "gross_total": 43.05, "document_number": "FTR 25001/9729 / JJ3X6VWM-9729", "linked_sales": []}
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