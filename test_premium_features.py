#!/usr/bin/env python3
"""
Test premium PDF features: company config and enhanced charts
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.company_config import CompanyConfigManager, apply_company_profile, COMPANY_PROFILES
from app.chart_generator import ProfessionalChartGenerator, generate_financial_charts
from app.pdf_export_premium import PremiumPDFGenerator
import tempfile
import json

def test_company_config():
    """Test company configuration system"""
    print("🏢 Testing Company Configuration...")

    # Test 1: Default configuration
    config_manager = CompanyConfigManager()
    company_info = config_manager.get_company_info()
    print(f"   ✅ Default company: {company_info.name}")
    print(f"   ✅ NIF: {company_info.nif}")
    print(f"   ✅ Full address: {company_info.get_full_address()}")

    # Test 2: Apply company profile
    print("   Testing company profiles...")
    for profile_name in COMPANY_PROFILES.keys():
        success = apply_company_profile(profile_name)
        if success:
            updated_info = config_manager.get_company_info()
            print(f"   ✅ Applied profile '{profile_name}': {updated_info.name}")
        else:
            print(f"   ❌ Failed to apply profile: {profile_name}")

    # Test 3: PDF header/footer data
    header_data = config_manager.get_pdf_header_data()
    footer_data = config_manager.get_pdf_footer_data()
    print(f"   ✅ PDF header data ready: {len(header_data)} fields")
    print(f"   ✅ PDF footer data ready: {len(footer_data)} fields")

    return True

def test_chart_generator():
    """Test professional chart generation"""
    print("📊 Testing Chart Generator...")

    # Sample financial data
    test_calculations = {
        "total_sales": 125450.0,
        "total_costs": 98230.0,
        "gross_margin": 27220.0,
        "vat_amount": 6260.6,
        "net_margin": 20959.4,
        "margin_percentage": 16.7,
        "normal_vat": 8500.0
    }

    generator = ProfessionalChartGenerator()

    # Test 1: Waterfall chart
    print("   Creating waterfall chart...", end=" ")
    try:
        waterfall_data = {
            "Total Vendas": test_calculations["total_sales"],
            "Total Custos": -test_calculations["total_costs"],
            "Margem Bruta": test_calculations["gross_margin"],
            "IVA s/ Margem": -test_calculations["vat_amount"],
            "Margem Líquida": test_calculations["net_margin"]
        }
        waterfall_chart = generator.create_waterfall_chart(waterfall_data)
        print(f"✅ Generated {len(waterfall_chart)} chars")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 2: Donut chart
    print("   Creating donut chart...", end=" ")
    try:
        donut_data = {
            "Custos Diretos": test_calculations["total_costs"],
            "IVA a Pagar": test_calculations["vat_amount"],
            "Margem Líquida": test_calculations["net_margin"]
        }
        donut_chart = generator.create_donut_chart(donut_data)
        print(f"✅ Generated {len(donut_chart)} chars")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 3: Comparison chart
    print("   Creating comparison chart...", end=" ")
    try:
        comparison_chart = generator.create_comparison_chart(
            test_calculations["normal_vat"],
            test_calculations["vat_amount"]
        )
        print(f"✅ Generated {len(comparison_chart)} chars")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 4: KPI dashboard
    print("   Creating KPI dashboard...", end=" ")
    try:
        kpi_data = {
            "total_sales": test_calculations["total_sales"],
            "total_costs": test_calculations["total_costs"],
            "gross_margin": test_calculations["gross_margin"],
            "vat_amount": test_calculations["vat_amount"],
            "net_margin": test_calculations["net_margin"],
            "margin_percentage": test_calculations["margin_percentage"]
        }
        kpi_dashboard = generator.create_kpi_dashboard(kpi_data)
        print(f"✅ Generated {len(kpi_dashboard)} chars")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 5: All charts at once
    print("   Testing complete chart generation...", end=" ")
    try:
        all_charts = generate_financial_charts(test_calculations)
        print(f"✅ Generated {len(all_charts)} chart types")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

def test_premium_pdf():
    """Test premium PDF generation"""
    print("📄 Testing Premium PDF Export...")

    # Sample data for PDF
    test_calculations = {
        "total_sales": 125450.0,
        "total_costs": 98230.0,
        "gross_margin": 27220.0,
        "vat_amount": 6260.6,
        "net_margin": 20959.4,
        "margin_percentage": 16.7,
        "normal_vat": 8500.0
    }

    test_associations = [
        {"sale_id": "s1", "cost_ids": ["c1", "c2"], "confidence": 85},
        {"sale_id": "s2", "cost_ids": ["c3"], "confidence": 92}
    ]

    test_sales = [
        {"id": "s1", "number": "FAT2025/001", "client": "Cliente Premium", "amount": 5500.0},
        {"id": "s2", "number": "FAT2025/002", "client": "Cliente Standard", "amount": 3200.0}
    ]

    test_costs = [
        {"id": "c1", "supplier": "Hotel Lisboa", "amount": 4200.0},
        {"id": "c2", "supplier": "Transfers Premium", "amount": 350.0},
        {"id": "c3", "supplier": "Restaurante Típico", "amount": 2100.0}
    ]

    # Test 1: Create premium PDF exporter
    print("   Initializing premium PDF exporter...", end=" ")
    try:
        exporter = PremiumPDFGenerator()
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 2: Generate complete premium PDF
    print("   Generating premium PDF...", end=" ")
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name

        exporter.generate_premium_report(
            calculations=test_calculations,
            sales=test_sales,
            costs=test_costs,
            associations=test_associations,
            output_path=pdf_path
        )

        # Check if file was created and has content
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            file_size = os.path.getsize(pdf_path)
            print(f"✅ Generated PDF: {file_size} bytes")
            print(f"   📁 Saved to: {pdf_path}")
            # Clean up
            os.unlink(pdf_path)
        else:
            print("❌ PDF file not created or empty")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

def main():
    """Run all premium feature tests"""
    print("🚀 Testing Premium PDF Features...")
    print("=" * 50)

    success = True

    # Test 1: Company configuration
    try:
        if not test_company_config():
            success = False
    except Exception as e:
        print(f"❌ Company config test failed: {e}")
        success = False

    print()

    # Test 2: Chart generation
    try:
        if not test_chart_generator():
            success = False
    except Exception as e:
        print(f"❌ Chart generator test failed: {e}")
        success = False

    print()

    # Test 3: Premium PDF
    try:
        if not test_premium_pdf():
            success = False
    except Exception as e:
        print(f"❌ Premium PDF test failed: {e}")
        success = False

    print()
    print("=" * 50)

    if success:
        print("🎉 All premium features working perfectly!")
        print("✅ Company configuration system ready")
        print("✅ Professional chart generation ready")
        print("✅ Premium PDF export ready")
        return True
    else:
        print("❌ Some tests failed - check errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)