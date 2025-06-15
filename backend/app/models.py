"""
Data models for IVA Margem Turismo
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Sale(BaseModel):
    """Sales invoice model"""
    id: str
    number: str
    date: str
    client: str
    amount: float = Field(description="Amount without VAT")
    vat_amount: float = Field(default=0)
    gross_total: float = Field(default=0)
    linked_costs: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "s1",
                "number": "FT 2025/001",
                "date": "2025-01-15",
                "client": "João Silva - Viagem Paris",
                "amount": 1200.00,
                "vat_amount": 276.00,
                "gross_total": 1476.00,
                "linked_costs": ["c1", "c2"]
            }
        }


class Cost(BaseModel):
    """Cost/purchase document model"""
    id: str
    supplier: str
    description: str
    date: str
    amount: float = Field(ge=0, description="Amount without VAT")
    vat_amount: float = Field(default=0, ge=0)
    gross_total: float = Field(default=0, ge=0)
    document_number: Optional[str] = None
    linked_sales: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "c1",
                "supplier": "Hotel Pestana",
                "description": "Alojamento 3 noites",
                "date": "2025-01-10",
                "amount": 450.00,
                "vat_amount": 103.50,
                "gross_total": 553.50,
                "linked_sales": ["s1"]
            }
        }


class Association(BaseModel):
    """Request model for associating sales and costs"""
    session_id: str
    sale_ids: List[str]
    cost_ids: List[str]


class CalculationRequest(BaseModel):
    """Request model for VAT calculation"""
    session_id: str
    vat_rate: float = Field(default=23.0, ge=0, le=100)


class AIMatchRequest(BaseModel):
    """Request model for AI auto-matching"""
    session_id: str
    threshold: float = Field(default=60.0, ge=0, le=100, description="Confidence threshold")
    max_matches: int = Field(default=50, ge=1, le=1000)


class UnlinkRequest(BaseModel):
    """Request model for unlinking associations"""
    session_id: str
    sale_id: str
    cost_id: str


class UploadResponse(BaseModel):
    """Response model for file upload"""
    session_id: str
    sales: List[Sale]
    costs: List[Cost]
    metadata: Dict[str, Any]
    summary: Dict[str, Any]  # Changed to Any to support mixed types


class CalculationResult(BaseModel):
    """Result model for VAT calculation"""
    invoice_number: str
    invoice_type: str
    date: str
    client: str
    sale_amount: float
    sale_vat: float
    total_allocated_costs: float
    gross_margin: float
    vat_rate: float
    vat_amount: float
    net_margin: float
    margin_percentage: float
    linked_costs: List[Dict[str, Any]]


class AIMatchResult(BaseModel):
    """Result model for AI matching"""
    cost: str
    sale: str
    confidence: float
    reason: str