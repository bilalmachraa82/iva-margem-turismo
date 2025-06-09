# Mock data endpoints for testing

Add these endpoints to main.py for quick testing:

```python
@app.get("/api/mock-data")
async def get_mock_data():
    """Get mock data for testing without SAF-T file"""
    
    # Create mock session
    session_id = "demo-" + str(uuid.uuid4())[:4]
    
    mock_data = {
        "sales": [
            {"id": "s1", "number": "FT E2025/1 / JJGBTD9W-1", "date": "2025-01-05", "client": "João Silva - Viagem Paris", "amount": 300.00, "vat_amount": 56.10, "gross_total": 356.10, "linked_costs": []},
            {"id": "s2", "number": "FT E2025/2 / JJGBTD9W-2", "date": "2025-01-08", "client": "Maria Santos - Tour Europa", "amount": 1215.00, "vat_amount": 227.20, "gross_total": 1442.20, "linked_costs": []},
            {"id": "s3", "number": "FT E2025/3 / JJGBTD9W-3", "date": "2025-01-10", "client": "Pedro Costa - Escapada Lisboa", "amount": 406.00, "vat_amount": 75.92, "gross_total": 481.92, "linked_costs": []},
            {"id": "s4", "number": "FR E2025/1 / JJGWTD95-1", "date": "2025-01-12", "client": "Ana Ferreira - Cruzeiro Douro", "amount": 492.66, "vat_amount": 92.12, "gross_total": 584.78, "linked_costs": []},
            {"id": "s5", "number": "FR E2025/3 / JJGWTD95-3", "date": "2025-01-18", "client": "Sofia Rodrigues - América Tour", "amount": 12763.95, "vat_amount": 2386.75, "gross_total": 15150.70, "linked_costs": []},
            {"id": "s6", "number": "FT E2025/16 / JJGBTD9W-16", "date": "2025-01-20", "client": "Miguel Alves - Tailândia", "amount": 1759.00, "vat_amount": 328.92, "gross_total": 2087.92, "linked_costs": []},
            {"id": "s7", "number": "NC E2025/1 / JJGSTD94-1", "date": "2025-01-22", "client": "Correção - João Silva", "amount": -420.00, "vat_amount": -78.54, "gross_total": -498.54, "linked_costs": []}
        ],
        "costs": [
            {"id": "c1", "supplier": "Hotel Pestana Porto", "description": "Alojamento 3 noites Twin", "date": "2025-01-03", "amount": 450.00, "vat_amount": 58.50, "gross_total": 508.50, "document_number": "FT 2025/123", "linked_sales": []},
            {"id": "c2", "supplier": "TAP Air Portugal", "description": "Voos LIS-CDG-LIS Classe Y", "date": "2025-01-02", "amount": 890.00, "vat_amount": 115.70, "gross_total": 1005.70, "document_number": "E-TKT-456", "linked_sales": []},
            {"id": "c3", "supplier": "Europcar", "description": "Aluguer VW Golf 5 dias", "date": "2025-01-06", "amount": 350.00, "vat_amount": 45.50, "gross_total": 395.50, "document_number": "RES-789", "linked_sales": []},
            {"id": "c4", "supplier": "Paris Tours SARL", "description": "City tour + Versailles", "date": "2025-01-04", "amount": 280.00, "vat_amount": 56.00, "gross_total": 336.00, "document_number": "INV-001", "linked_sales": []},
            {"id": "c5", "supplier": "Douro Azul", "description": "Cruzeiro 2 dias Régua-Pinhão", "date": "2025-01-11", "amount": 1200.00, "vat_amount": 276.00, "gross_total": 1476.00, "document_number": "FT 2025/456", "linked_sales": []},
            {"id": "c6", "supplier": "American Express Travel", "description": "Pacote USA 15 dias all-inclusive", "date": "2025-01-16", "amount": 8500.00, "vat_amount": 1105.00, "gross_total": 9605.00, "document_number": "AMX-789", "linked_sales": []},
            {"id": "c7", "supplier": "Thai Airways", "description": "Voos LIS-BKK-LIS Business", "date": "2025-01-17", "amount": 2200.00, "vat_amount": 286.00, "gross_total": 2486.00, "document_number": "TG-456", "linked_sales": []}
        ],
        "metadata": {
            "company_name": "Agência de Viagens Demo Lda",
            "tax_registration": "123456789",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "currency": "EUR"
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
        "costs_count": len(mock_data["costs"])
    }
```

## How to use:

1. Call GET /api/mock-data to get a session with test data
2. Use the returned session_id for other endpoints
3. Test associations, calculations, etc.