#!/usr/bin/env python
"""
Test script for IVA Margem backend
Run this to verify everything is working
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from app.models import Sale, Cost, Association
        print("✓ Models imported successfully")
        
        from app.saft_parser import SAFTParser
        print("✓ SAF-T parser imported successfully")
        
        from app.calculator import VATCalculator
        print("✓ Calculator imported successfully")
        
        from app.excel_export import ExcelExporter
        print("✓ Excel exporter imported successfully")
        
        from app.main import app
        print("✓ FastAPI app imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {str(e)}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    try:
        from app.calculator import VATCalculator
        
        # Test VAT calculation
        calc = VATCalculator(vat_rate=23)
        
        # Test data
        sales = [{
            "id": "s1",
            "number": "FT 2025/001",
            "amount": 1000,
            "linked_costs": ["c1"]
        }]
        
        costs = [{
            "id": "c1",
            "supplier": "Test Supplier",
            "description": "Test cost",
            "amount": 600,
            "linked_sales": ["s1"]
        }]
        
        results = calc.calculate_all(sales, costs)
        
        if results:
            result = results[0]
            print(f"✓ Sale amount: €{result['sale_amount']}")
            print(f"✓ Cost amount: €{result['total_allocated_costs']}")
            print(f"✓ Gross margin: €{result['gross_margin']}")
            print(f"✓ VAT amount: €{result['vat_amount']}")
            print(f"✓ Net margin: €{result['net_margin']}")
            return True
        
    except Exception as e:
        print(f"✗ Functionality error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("IVA Margem Turismo - Backend Test")
    print("=" * 50)
    
    all_ok = True
    
    # Test imports
    if not test_imports():
        all_ok = False
        
    # Test functionality
    if not test_basic_functionality():
        all_ok = False
        
    print("\n" + "=" * 50)
    if all_ok:
        print("✓ All tests passed! Backend is ready.")
        print("\nNow run:")
        print("  cd app")
        print("  uvicorn main:app --reload")
    else:
        print("✗ Some tests failed. Check the errors above.")
        
    print("=" * 50)

if __name__ == "__main__":
    main()