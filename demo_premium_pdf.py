#!/usr/bin/env python3
"""
Generate a demo premium PDF with enhanced charts and company branding
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.company_config import apply_company_profile, company_config
from app.chart_generator import generate_financial_charts
from app.pdf_export_premium import generate_premium_pdf_report
import tempfile

def create_demo_premium_pdf():
    """Create a demo premium PDF with all new features"""

    print("🎨 Generating Premium PDF Demo...")

    # Apply a premium company profile
    print("   Setting up premium company profile...")
    apply_company_profile("agencia_premium")
    company_info = company_config.get_company_info()
    print(f"   Company: {company_info.name}")
    print(f"   Theme: {company_info.primary_color}")

    # Sample realistic financial data
    calculations = {
        "total_sales": 285450.75,
        "total_costs": 198320.40,
        "gross_margin": 87130.35,
        "vat_amount": 20040.0,
        "net_margin": 67090.35,
        "margin_percentage": 23.5,
        "normal_vat": 28500.0
    }

    # Sample sales data
    sales = [
        {"id": "s1", "number": "FAT2025/001", "client": "Luxury Tours Premium", "amount": 12500.0, "date": "2025-01-15"},
        {"id": "s2", "number": "FAT2025/002", "client": "Corporate Travel Solutions", "amount": 8750.0, "date": "2025-01-16"},
        {"id": "s3", "number": "FAT2025/003", "client": "Elite Destination Services", "amount": 15200.0, "date": "2025-01-17"},
        {"id": "s4", "number": "FAT2025/004", "client": "VIP Experience Group", "amount": 9800.0, "date": "2025-01-18"},
        {"id": "s5", "number": "FAT2025/005", "client": "Premium Holidays International", "amount": 18900.0, "date": "2025-01-19"}
    ]

    # Sample costs data
    costs = [
        {"id": "c1", "supplier": "Four Seasons Hotel", "amount": 8500.0, "date": "2025-01-15"},
        {"id": "c2", "supplier": "Michelin Star Restaurant", "amount": 2200.0, "date": "2025-01-15"},
        {"id": "c3", "supplier": "Private Jet Charter", "amount": 15000.0, "date": "2025-01-16"},
        {"id": "c4", "supplier": "Luxury Car Service", "amount": 1800.0, "date": "2025-01-17"},
        {"id": "c5", "supplier": "Exclusive Wine Tour", "amount": 3500.0, "date": "2025-01-18"}
    ]

    # Sample associations
    associations = [
        {"sale_id": "s1", "cost_ids": ["c1", "c2"], "confidence": 95},
        {"sale_id": "s2", "cost_ids": ["c3"], "confidence": 88},
        {"sale_id": "s3", "cost_ids": ["c4", "c5"], "confidence": 92}
    ]

    # Generate premium charts
    print("   Generating professional charts...")
    try:
        charts = generate_financial_charts(calculations, {
            "primary": company_info.primary_color,
            "secondary": company_info.secondary_color,
            "accent": company_info.accent_color
        })
        print(f"   ✅ Generated {len(charts)} premium charts")
    except Exception as e:
        print(f"   ❌ Chart generation failed: {e}")
        return False

    # Generate premium PDF
    print("   Creating premium PDF report...")
    try:
        output_path = f"/Users/bilal/Programaçao/Claudia/iva-margem-turismo-1/Premium_Demo_{company_info.name.replace(' ', '_')}.pdf"

        generated_path = generate_premium_pdf_report(
            calculations=calculations,
            sales_data=sales,
            costs_data=costs,
            company_info=company_info,
            filename=output_path
        )

        file_size = os.path.getsize(generated_path)
        output_path = generated_path
        print(f"   ✅ Premium PDF generated: {file_size:,} bytes")
        print(f"   📁 Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        return False

def main():
    """Main demo function"""
    print("🚀 Premium PDF Demo - Industry Best Practices")
    print("=" * 60)

    success = create_demo_premium_pdf()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Premium PDF demo completed successfully!")
        print("✨ Features demonstrated:")
        print("   • Professional company branding")
        print("   • Industry-standard financial charts")
        print("   • Enhanced visual design")
        print("   • Customizable color schemes")
        print("   • Executive-quality presentation")
    else:
        print("❌ Demo failed - check errors above")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)