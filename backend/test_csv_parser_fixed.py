#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed test script to parse and analyze e-fatura compras.csv file
Properly handles Portuguese CSV format and encoding
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter
import os

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

def parse_portuguese_date(date_str):
    """Parse Portuguese date format DD/MM/YYYY"""
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except:
        return None

def parse_portuguese_amount(amount_str):
    """Parse Portuguese amount format (e.g., '1.234,56 €' or '1.234,56 €')"""
    try:
        # Remove currency symbol and spaces
        cleaned = amount_str.replace('€', '').replace('�', '').strip()
        # Replace thousand separator and decimal separator
        cleaned = cleaned.replace('.', '').replace(',', '.')
        return float(cleaned)
    except Exception as e:
        print(f"Error parsing amount '{amount_str}': {e}")
        return 0.0

def analyze_csv_file(file_path):
    """Analyze the e-fatura CSV file and return detailed statistics"""
    
    stats = {
        'total_rows': 0,
        'header_rows': 0,
        'data_rows': 0,
        'empty_rows': 0,
        'unique_suppliers': set(),
        'supplier_counts': defaultdict(int),
        'document_types': Counter(),
        'sectors': Counter(),
        'date_range': {'min': None, 'max': None},
        'total_amount': 0.0,
        'total_vat': 0.0,
        'total_base': 0.0,
        'negative_amounts': 0,
        'credit_notes': [],
        'duplicates': [],
        'sample_data': []
    }
    
    # Open with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as file:
        # Count total lines
        lines = file.readlines()
        stats['total_rows'] = len(lines)
        
        # Reset to beginning
        file.seek(0)
        
        # Read header to understand column positions
        header_line = file.readline().strip()
        headers = header_line.split(';')
        print(f"Column headers ({len(headers)} columns):")
        for i, h in enumerate(headers):
            print(f"  [{i}] {h}")
        
        stats['header_rows'] = 1
        
        # Process data rows
        for line_num, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line:
                stats['empty_rows'] += 1
                continue
                
            # Split by semicolon
            fields = line.split(';')
            
            if len(fields) < 11:  # Should have at least 11 columns
                print(f"Warning: Line {line_num} has only {len(fields)} fields")
                continue
                
            stats['data_rows'] += 1
            
            # Extract data by position (0-indexed)
            sector = fields[0] if len(fields) > 0 else ''
            supplier = fields[1] if len(fields) > 1 else ''
            invoice_num = fields[2] if len(fields) > 2 else ''
            doc_type = fields[3] if len(fields) > 3 else ''
            date_str = fields[4] if len(fields) > 4 else ''
            total_str = fields[5] if len(fields) > 5 else ''
            vat_str = fields[6] if len(fields) > 6 else ''
            base_str = fields[7] if len(fields) > 7 else ''
            status = fields[8] if len(fields) > 8 else ''
            
            # Save sample data
            if len(stats['sample_data']) < 5:
                stats['sample_data'].append({
                    'line': line_num,
                    'supplier': supplier,
                    'invoice': invoice_num,
                    'type': doc_type,
                    'date': date_str,
                    'total': total_str,
                    'vat': vat_str,
                    'status': status
                })
            
            # Process supplier
            if supplier:
                stats['unique_suppliers'].add(supplier)
                stats['supplier_counts'][supplier] += 1
            
            # Document type
            if doc_type:
                stats['document_types'][doc_type] += 1
                if 'cr�dito' in doc_type.lower() or 'crédito' in doc_type.lower():
                    stats['credit_notes'].append({
                        'line': line_num,
                        'supplier': supplier,
                        'invoice': invoice_num,
                        'amount': total_str
                    })
            
            # Sector
            if sector:
                stats['sectors'][sector] += 1
            
            # Parse date
            if date_str:
                date_obj = parse_portuguese_date(date_str)
                if date_obj:
                    if stats['date_range']['min'] is None or date_obj < stats['date_range']['min']:
                        stats['date_range']['min'] = date_obj
                    if stats['date_range']['max'] is None or date_obj > stats['date_range']['max']:
                        stats['date_range']['max'] = date_obj
            
            # Parse amounts
            total_amount = parse_portuguese_amount(total_str)
            vat_amount = parse_portuguese_amount(vat_str)
            base_amount = parse_portuguese_amount(base_str)
            
            stats['total_amount'] += total_amount
            stats['total_vat'] += vat_amount
            stats['total_base'] += base_amount
            
            if total_amount < 0:
                stats['negative_amounts'] += 1
    
    return stats

def print_statistics(stats):
    """Print detailed statistics about the CSV file"""
    
    print("\n" + "="*80)
    print("E-FATURA COMPRAS.CSV - DETAILED ANALYSIS")
    print("="*80)
    
    print(f"\n1. FILE STRUCTURE:")
    print(f"   - Total rows in file: {stats['total_rows']}")
    print(f"   - Header rows: {stats['header_rows']}")
    print(f"   - Data rows: {stats['data_rows']}")
    print(f"   - Empty rows: {stats['empty_rows']}")
    print(f"   - Actual cost entries: {stats['data_rows']}")
    
    print(f"\n2. SAMPLE DATA (first 5 entries):")
    for sample in stats['sample_data']:
        print(f"   Line {sample['line']}:")
        print(f"     - Supplier: {sample['supplier']}")
        print(f"     - Invoice: {sample['invoice']}")
        print(f"     - Type: {sample['type']}")
        print(f"     - Date: {sample['date']}")
        print(f"     - Total: {sample['total']}")
        print(f"     - VAT: {sample['vat']}")
        print()
    
    print(f"\n3. SUPPLIERS:")
    print(f"   - Unique suppliers: {len(stats['unique_suppliers'])}")
    print(f"   - Top 10 suppliers by frequency:")
    top_suppliers = sorted(stats['supplier_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    for supplier, count in top_suppliers:
        print(f"     • {supplier}: {count} invoices")
    
    print(f"\n4. DOCUMENT TYPES:")
    for doc_type, count in stats['document_types'].most_common():
        print(f"   - {doc_type}: {count}")
    
    print(f"\n5. SECTORS:")
    for sector, count in stats['sectors'].most_common():
        sector_name = sector if sector else "(No sector)"
        print(f"   - {sector_name}: {count}")
    
    print(f"\n6. DATE RANGE:")
    if stats['date_range']['min'] and stats['date_range']['max']:
        print(f"   - From: {stats['date_range']['min'].strftime('%d/%m/%Y')}")
        print(f"   - To: {stats['date_range']['max'].strftime('%d/%m/%Y')}")
        days_diff = (stats['date_range']['max'] - stats['date_range']['min']).days
        print(f"   - Period: {days_diff} days")
    
    print(f"\n7. FINANCIAL SUMMARY:")
    print(f"   - Total amount: €{stats['total_amount']:,.2f}")
    print(f"   - Total VAT: €{stats['total_vat']:,.2f}")
    print(f"   - Total base: €{stats['total_base']:,.2f}")
    if stats['data_rows'] > 0:
        print(f"   - Average per invoice: €{stats['total_amount']/stats['data_rows']:,.2f}")
    print(f"   - Negative amounts: {stats['negative_amounts']}")
    print(f"   - Credit notes found: {len(stats['credit_notes'])}")
    
    if stats['credit_notes']:
        print(f"\n8. CREDIT NOTES:")
        for cn in stats['credit_notes'][:5]:  # Show first 5
            print(f"   - Line {cn['line']}: {cn['supplier']} - {cn['invoice']} ({cn['amount']})")
    
    print("\n" + "="*80)
    print(f"SUMMARY: Found {stats['data_rows']} cost entries from {len(stats['unique_suppliers'])} unique suppliers")
    print(f"Total costs: €{stats['total_amount']:,.2f} (VAT: €{stats['total_vat']:,.2f})")
    print("="*80)

def create_parser_function():
    """Create a parser function for the backend integration"""
    
    print("\n\nPARSER FUNCTION FOR BACKEND INTEGRATION:")
    print("-" * 60)
    print("""
import csv
from datetime import datetime

def parse_efatura_csv(file_path):
    '''Parse e-fatura CSV and return cost documents'''
    
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
    
    costs = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        # Skip header
        header = file.readline()
        
        # Process data rows
        for line in file:
            fields = line.strip().split(';')
            
            if len(fields) < 11:
                continue
            
            # Extract supplier info
            supplier_full = fields[1]
            supplier_parts = supplier_full.split(' - ', 1)
            supplier_nif = supplier_parts[0] if supplier_parts else ''
            supplier_name = supplier_parts[1] if len(supplier_parts) > 1 else supplier_full
            
            # Extract invoice number
            invoice_full = fields[2]
            invoice_parts = invoice_full.split(' / ')
            invoice_number = invoice_parts[0] if invoice_parts else invoice_full
            
            # Create cost document
            cost = {
                'id': f'c{len(costs)+1}',
                'supplier_nif': supplier_nif,
                'supplier': supplier_name,
                'supplier_full': supplier_full,
                'number': invoice_number,
                'document_type': fields[3],
                'date': parse_date(fields[4]),
                'amount': parse_amount(fields[5]),
                'vat_amount': parse_amount(fields[6]),
                'base_amount': parse_amount(fields[7]),
                'sector': fields[0],
                'status': fields[8] if len(fields) > 8 else 'Registado'
            }
            
            # Only add if amount is positive (skip credit notes for costs)
            if cost['amount'] > 0:
                costs.append(cost)
    
    return costs

# Usage example:
# costs = parse_efatura_csv('/path/to/e-fatura compras.csv')
# print(f"Loaded {len(costs)} cost documents")
""")
    print("-" * 60)

def main():
    """Main function to run the analysis"""
    
    # File path
    file_path = "/mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo/e-fatura compras.csv"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    print(f"Analyzing file: {file_path}")
    print(f"File size: {os.path.getsize(file_path):,} bytes")
    
    try:
        # Analyze the CSV file
        stats = analyze_csv_file(file_path)
        
        # Print statistics
        print_statistics(stats)
        
        # Create parser function
        create_parser_function()
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()