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


class PeriodCalculateRequest(BaseModel):
    """Request model for period-based VAT calculation"""
    session_id: str
    vat_rate: float = 23.0
    period_start: str  # YYYY-MM-DD format
    period_end: str    # YYYY-MM-DD format
    start_date: str    # YYYY-MM-DD format - required for compatibility
    end_date: str      # YYYY-MM-DD format - required for compatibility
    region: str = "continental"  # continental, madeira, azores
    previous_negative_margin: float = 0.0


class CompanyInfoPayload(BaseModel):
    """Company information payload shared between frontend and backend"""
    name: Optional[str] = Field(default=None, description="Company name")
    nif: Optional[str] = Field(default=None, description="Tax identification number")
    cae: Optional[str] = Field(default=None, description="CAE code")
    address: Optional[str] = Field(default=None, description="Company address")
    city: Optional[str] = Field(default=None, description="City")
    postal_code: Optional[str] = Field(default=None, description="Postal code")
    country: Optional[str] = Field(default=None, description="Country")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    website: Optional[str] = Field(default=None, description="Website")


class CompanyInfoUpdate(CompanyInfoPayload):
    """Partial update model for company information"""

    class Config:
        extra = 'allow'


class PDFExportRequest(BaseModel):
    """Enhanced request model for PDF export with company info"""
    session_id: Optional[str] = None
    vat_rate: float = Field(default=23.0, ge=0, le=100)
    results: Optional[Dict[str, Any]] = None
    company_info: Optional[CompanyInfoPayload] = None
    format: Optional[str] = Field(default='html', description="'html' (preview) or 'pdf' (binary)")


class ErrorDetail(BaseModel):
    """Standard error detail structure"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    """Standard error response structure"""
    error: ErrorDetail
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid session ID format",
                    "details": {"field": "session_id", "value": "invalid-id"},
                    "timestamp": "2025-01-09T12:00:00"
                },
                "request_id": "req_123456"
            }
        }
