#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Fatura Import Summary
Shows exactly what will be imported from the CSV file
"""

import csv
from datetime import datetime
import sys

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except:
        return None

def parse_amount(amount_str):
    try:
        cleaned = amount_str.replace('€', '').replace('�', '').strip()
        cleaned = cleaned.replace('.', '').replace(',', '.')
        return float(cleaned)
    except:
        return 0.0

def parse_efatura_csv(file_path):
    '''Parse e-fatura CSV and return cost documents'''
    costs = []
    credit_notes = []
    skipped = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        # Skip header
        header = file.readline()
        
        # Process data rows
        line_num = 1
        for line in file:
            line_num += 1
            fields = line.strip().split(';')
            
            if len(fields) < 11:
                skipped.append(f"Line {line_num}: Not enough fields ({len(fields)})")
                continue
            
            # Extract data
            supplier_full = fields[1]
            supplier_parts = supplier_full.split(' - ', 1)
            supplier_nif = supplier_parts[0] if supplier_parts else ''
            supplier_name = supplier_parts[1] if len(supplier_parts) > 1 else supplier_full
            
            invoice_full = fields[2]
            invoice_parts = invoice_full.split(' / ')
            invoice_number = invoice_parts[0] if invoice_parts else invoice_full
            
            doc_type = fields[3]
            amount = parse_amount(fields[5])
            
            # Create document
            doc = {
                'line': line_num,
                'id': f'c{len(costs)+len(credit_notes)+1}',
                'supplier_nif': supplier_nif,
                'supplier': supplier_name,
                'supplier_full': supplier_full,
                'number': invoice_number,
                'document_type': doc_type,
                'date': parse_date(fields[4]),
                'amount': amount,
                'vat_amount': parse_amount(fields[6]),
                'base_amount': parse_amount(fields[7]),
                'sector': fields[0],
                'status': fields[8] if len(fields) > 8 else 'Registado'
            }
            
            # Categorize by type
            if 'cr�dito' in doc_type.lower() or 'crédito' in doc_type.lower():
                credit_notes.append(doc)
            elif amount > 0:
                costs.append(doc)
            else:
                skipped.append(f"Line {line_num}: Zero or negative amount ({amount})")
    
    return costs, credit_notes, skipped

def main():
    file_path = "/mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo/e-fatura compras.csv"
    
    print("="*80)
    print("E-FATURA CSV IMPORT SUMMARY")
    print("="*80)
    
    costs, credit_notes, skipped = parse_efatura_csv(file_path)
    
    print(f"\n📊 IMPORT STATISTICS:")
    print(f"   ✅ Cost documents to import: {len(costs)}")
    print(f"   📝 Credit notes found: {len(credit_notes)}")
    print(f"   ⚠️  Skipped entries: {len(skipped)}")
    print(f"   📄 Total processed: {len(costs) + len(credit_notes) + len(skipped)}")
    
    # Financial summary
    total_costs = sum(c['amount'] for c in costs)
    total_vat = sum(c['vat_amount'] for c in costs)
    total_credits = sum(c['amount'] for c in credit_notes)
    
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   Total costs amount: €{total_costs:,.2f}")
    print(f"   Total VAT: €{total_vat:,.2f}")
    print(f"   Total credit notes: €{total_credits:,.2f}")
    print(f"   Net amount: €{total_costs - total_credits:,.2f}")
    
    # Date range
    if costs:
        dates = [c['date'] for c in costs if c['date']]
        if dates:
            print(f"\n📅 DATE RANGE:")
            print(f"   From: {min(dates).strftime('%d/%m/%Y')}")
            print(f"   To: {max(dates).strftime('%d/%m/%Y')}")
    
    # Top suppliers
    print(f"\n🏢 TOP 10 SUPPLIERS BY AMOUNT:")
    supplier_totals = {}
    for cost in costs:
        supplier = cost['supplier_full']
        supplier_totals[supplier] = supplier_totals.get(supplier, 0) + cost['amount']
    
    top_suppliers = sorted(supplier_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    for supplier, total in top_suppliers:
        print(f"   {supplier}: €{total:,.2f}")
    
    # Document types
    print(f"\n📋 DOCUMENT TYPES:")
    doc_types = {}
    for cost in costs:
        dt = cost['document_type']
        doc_types[dt] = doc_types.get(dt, 0) + 1
    
    for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {doc_type}: {count}")
    
    # Show credit notes
    if credit_notes:
        print(f"\n💳 CREDIT NOTES DETAIL:")
        for cn in credit_notes:
            print(f"   Line {cn['line']}: {cn['supplier']} - {cn['number']} - €{cn['amount']:,.2f}")
    
    # Show skipped
    if skipped:
        print(f"\n⚠️  SKIPPED ENTRIES:")
        for skip in skipped[:5]:  # Show first 5
            print(f"   {skip}")
        if len(skipped) > 5:
            print(f"   ... and {len(skipped)-5} more")
    
    print("\n" + "="*80)
    print(f"✅ READY TO IMPORT: {len(costs)} cost documents totaling €{total_costs:,.2f}")
    print("="*80)
    
    # Sample data for verification
    print("\n📄 SAMPLE DATA (first 5 costs):")
    for i, cost in enumerate(costs[:5]):
        print(f"\n{i+1}. {cost['supplier_full']}")
        print(f"   Invoice: {cost['number']}")
        print(f"   Date: {cost['date'].strftime('%d/%m/%Y') if cost['date'] else 'N/A'}")
        print(f"   Amount: €{cost['amount']:,.2f} (VAT: €{cost['vat_amount']:,.2f})")
        print(f"   Type: {cost['document_type']}")

if __name__ == "__main__":
    main()