#!/usr/bin/env python3
"""
Test script to analyze potential cost duplication in IVA Margem Turismo calculations
"""

import json
from app.calculator import VATCalculator

# Test data with many-to-many associations
test_sales = [
    {
        "id": "s1",
        "number": "FT 2025/001",
        "date": "2025-01-15",
        "client": "Client A",
        "amount": 1000.0,
        "vat_amount": 0,
        "linked_costs": ["c1", "c2"]  # Sale 1 linked to Cost 1 and Cost 2
    },
    {
        "id": "s2",
        "number": "FT 2025/002",
        "date": "2025-01-16",
        "client": "Client B",
        "amount": 2000.0,
        "vat_amount": 0,
        "linked_costs": ["c1", "c3"]  # Sale 2 also linked to Cost 1 (shared) and Cost 3
    }
]

test_costs = [
    {
        "id": "c1",
        "supplier": "Supplier X",
        "description": "Shared service",
        "date": "2025-01-10",
        "amount": 600.0,
        "vat_amount": 0,
        "linked_sales": ["s1", "s2"]  # Cost 1 is shared between Sale 1 and Sale 2
    },
    {
        "id": "c2",
        "supplier": "Supplier Y",
        "description": "Service for S1",
        "date": "2025-01-11",
        "amount": 200.0,
        "vat_amount": 0,
        "linked_sales": ["s1"]  # Cost 2 only for Sale 1
    },
    {
        "id": "c3",
        "supplier": "Supplier Z",
        "description": "Service for S2",
        "date": "2025-01-12",
        "amount": 800.0,
        "vat_amount": 0,
        "linked_sales": ["s2"]  # Cost 3 only for Sale 2
    }
]

# Initialize calculator
calculator = VATCalculator(vat_rate=23)

# Run calculations
print("=== Testing Cost Allocation Logic ===\n")
calculations = calculator.calculate_all(test_sales, test_costs)

# Analyze results
print("SALES:")
for sale in test_sales:
    print(f"- {sale['number']}: €{sale['amount']} linked to costs: {sale['linked_costs']}")

print("\nCOSTS:")
for cost in test_costs:
    print(f"- {cost['id']} ({cost['supplier']}): €{cost['amount']} linked to sales: {cost['linked_sales']}")

print("\nCALCULATION RESULTS:")
total_allocated_costs = 0
for calc in calculations:
    print(f"\n{calc['invoice_number']}:")
    print(f"  Sale amount: €{calc['sale_amount']}")
    print(f"  Total allocated costs: €{calc['total_allocated_costs']}")
    print(f"  Gross margin: €{calc['gross_margin']}")
    print(f"  Linked costs:")
    for cost in calc['linked_costs']:
        print(f"    - {cost['cost_id']} ({cost['supplier']}): €{cost['total_amount']} allocated €{cost['allocated_amount']} (shared with {cost['shared_with']} sales)")
        total_allocated_costs += cost['allocated_amount']

print(f"\n=== ANALYSIS ===")
print(f"Total original costs: €{sum(c['amount'] for c in test_costs)}")
print(f"Total allocated costs across all sales: €{round(total_allocated_costs, 2)}")
print(f"Total sales: €{sum(s['amount'] for s in test_sales)}")
print(f"Total gross margin: €{sum(c['gross_margin'] for c in calculations)}")

# Check if costs are duplicated
original_total = sum(c['amount'] for c in test_costs)
allocated_total = round(total_allocated_costs, 2)

if allocated_total > original_total:
    print(f"\n⚠️ WARNING: Costs appear to be DUPLICATED!")
    print(f"   Original costs: €{original_total}")
    print(f"   Allocated costs: €{allocated_total}")
    print(f"   Duplication: €{allocated_total - original_total}")
elif allocated_total < original_total:
    print(f"\n✓ No duplication detected, but some costs may be unallocated")
    print(f"   Unallocated: €{original_total - allocated_total}")
else:
    print(f"\n✓ Perfect allocation - no duplication or missing costs")

# Validation errors
if hasattr(calculator, 'validation_errors') and calculator.validation_errors:
    print("\nVALIDATION ERRORS:")
    for error in calculator.validation_errors:
        print(f"  [{error['type']}] {error.get('sale', 'N/A')}: {error['message']}")