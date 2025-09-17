#!/usr/bin/env python3
"""
VAT Formula Validation Test
Specifically tests the corrected VAT calculation formula
"""
import sys
import os

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.calculator import VATCalculator


def test_vat_formula_correction():
    """Test that VAT formula has been corrected"""
    print("🧮 Testing VAT Formula Correction")
    print("=" * 40)

    # Test data
    test_sales = [
        {
            "id": "s1",
            "number": "FT 2025/1",
            "date": "2025-01-15",
            "client": "Test Client",
            "amount": 1000.0,
            "vat_amount": 230.0,
            "linked_costs": ["c1"]
        }
    ]

    test_costs = [
        {
            "id": "c1",
            "supplier": "Test Supplier",
            "description": "Test Cost",
            "amount": 600.0,
            "vat_amount": 138.0,
            "document_number": "FC 001",
            "date": "2025-01-10",
            "linked_sales": ["s1"]
        }
    ]

    # Initialize calculator
    calculator = VATCalculator(vat_rate=23.0)

    # Calculate
    results = calculator.calculate_all(test_sales, test_costs)

    if not results:
        print("❌ No calculation results generated")
        return False

    result = results[0]

    # Expected values
    expected_margin = 1000.0 - 600.0  # 400.0
    expected_vat_correct = 400.0 * 23 / 100  # 92.0 (CORRECT - Art. 308º)
    expected_vat_wrong = 400.0 * 23 / (100 + 23)  # ~74.8 (WRONG - VAT included method)

    actual_margin = result["gross_margin"]
    actual_vat = result["vat_amount"]

    print(f"📊 Test Results:")
    print(f"   Gross Margin: €{actual_margin:.2f} (expected: €{expected_margin:.2f})")
    print(f"   VAT Amount: €{actual_vat:.2f}")
    print()
    print(f"🔍 Formula Validation:")
    print(f"   ✅ CORRECT (Art. 308º): €{expected_vat_correct:.2f}")
    print(f"   ❌ WRONG (VAT included): €{expected_vat_wrong:.2f}")
    print()

    # Validate the correction
    margin_correct = abs(actual_margin - expected_margin) < 0.01
    vat_correct = abs(actual_vat - expected_vat_correct) < 0.01
    vat_not_wrong = abs(actual_vat - expected_vat_wrong) > 1.0

    if margin_correct and vat_correct and vat_not_wrong:
        print("✅ VAT formula has been CORRECTLY fixed!")
        print("   Formula used: Margem × Taxa / 100")
        print("   Compliance: CIVA Art. 308º - Regime Especial Agências de Viagens")
        return True
    else:
        print("❌ VAT formula is still INCORRECT!")
        if not vat_correct:
            print(f"   Expected VAT: €{expected_vat_correct:.2f}")
            print(f"   Actual VAT: €{actual_vat:.2f}")
            if abs(actual_vat - expected_vat_wrong) < 1.0:
                print("   ⚠️  Still using VAT included formula - CRITICAL ERROR!")
        return False


def test_negative_margin_handling():
    """Test handling of negative margins"""
    print("\n🔻 Testing Negative Margin Handling")
    print("=" * 40)

    # Test data with negative margin
    test_sales = [
        {
            "id": "s1",
            "number": "FT 2025/2",
            "date": "2025-01-15",
            "client": "Loss Client",
            "amount": 500.0,
            "vat_amount": 115.0,
            "linked_costs": ["c1"]
        }
    ]

    test_costs = [
        {
            "id": "c1",
            "supplier": "Expensive Supplier",
            "description": "High Cost",
            "amount": 800.0,
            "vat_amount": 184.0,
            "document_number": "FC 002",
            "date": "2025-01-10",
            "linked_sales": ["s1"]
        }
    ]

    calculator = VATCalculator(vat_rate=23.0)
    results = calculator.calculate_all(test_sales, test_costs)

    if not results:
        print("❌ No calculation results generated")
        return False

    result = results[0]
    margin = result["gross_margin"]
    vat = result["vat_amount"]

    print(f"📊 Negative Margin Test:")
    print(f"   Sale Amount: €500.00")
    print(f"   Cost Amount: €800.00")
    print(f"   Margin: €{margin:.2f}")
    print(f"   VAT on Margin: €{vat:.2f}")

    if margin < 0 and vat == 0:
        print("✅ Negative margins correctly handled (no VAT charged)")
        return True
    else:
        print("❌ Negative margin handling incorrect")
        return False


def test_multiple_scenarios():
    """Test various calculation scenarios"""
    print("\n🎯 Testing Multiple Scenarios")
    print("=" * 40)

    scenarios = [
        {
            "name": "High Margin Tourism Package",
            "sale_amount": 2000.0,
            "cost_amount": 1200.0,
            "expected_margin": 800.0,
            "expected_vat": 800.0 * 23 / 100
        },
        {
            "name": "Low Margin Flight Booking",
            "sale_amount": 500.0,
            "cost_amount": 450.0,
            "expected_margin": 50.0,
            "expected_vat": 50.0 * 23 / 100
        },
        {
            "name": "Premium Hotel Package",
            "sale_amount": 3500.0,
            "cost_amount": 2800.0,
            "expected_margin": 700.0,
            "expected_vat": 700.0 * 23 / 100
        }
    ]

    all_passed = True

    for i, scenario in enumerate(scenarios):
        test_sales = [{
            "id": f"s{i+1}",
            "number": f"FT 2025/{i+1}",
            "date": "2025-01-15",
            "client": f"Client {i+1}",
            "amount": scenario["sale_amount"],
            "vat_amount": scenario["sale_amount"] * 0.23,
            "linked_costs": [f"c{i+1}"]
        }]

        test_costs = [{
            "id": f"c{i+1}",
            "supplier": f"Supplier {i+1}",
            "description": scenario["name"],
            "amount": scenario["cost_amount"],
            "vat_amount": scenario["cost_amount"] * 0.23,
            "document_number": f"FC {i+1:03d}",
            "date": "2025-01-10",
            "linked_sales": [f"s{i+1}"]
        }]

        calculator = VATCalculator(vat_rate=23.0)
        results = calculator.calculate_all(test_sales, test_costs)

        if results:
            result = results[0]
            actual_margin = result["gross_margin"]
            actual_vat = result["vat_amount"]

            margin_ok = abs(actual_margin - scenario["expected_margin"]) < 0.01
            vat_ok = abs(actual_vat - scenario["expected_vat"]) < 0.01

            status = "✅" if (margin_ok and vat_ok) else "❌"
            print(f"{status} {scenario['name']}: Margin €{actual_margin:.2f}, VAT €{actual_vat:.2f}")

            if not (margin_ok and vat_ok):
                all_passed = False
        else:
            print(f"❌ {scenario['name']}: No results generated")
            all_passed = False

    return all_passed


def main():
    """Run all validation tests"""
    print("🧪 VAT Formula Validation Suite")
    print("Testing the corrected IVA calculation for Art. 308º CIVA")
    print("=" * 60)

    tests_passed = 0
    total_tests = 3

    # Run tests
    if test_vat_formula_correction():
        tests_passed += 1

    if test_negative_margin_handling():
        tests_passed += 1

    if test_multiple_scenarios():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Validation Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All VAT formula validations passed!")
        print("✅ System correctly implements CIVA Art. 308º")
        return True
    else:
        print("⚠️  VAT formula validation failed!")
        print("❌ CRITICAL: Review the calculator implementation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)