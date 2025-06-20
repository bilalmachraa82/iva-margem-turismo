#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to parse and analyze e-fatura compras.csv file
Provides detailed statistics about the CSV contents
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter
import locale
import os

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

def parse_portuguese_date(date_str):
    """Parse Portuguese date format DD/MM/YYYY"""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except:
        return None

def parse_portuguese_amount(amount_str):
    """Parse Portuguese amount format (e.g., '1.234,56 €')"""
    try:
        # Remove currency symbol and spaces
        cleaned = amount_str.replace('€', '').strip()
        # Replace Portuguese decimal separator
        cleaned = cleaned.replace('.', '').replace(',', '.')
        return float(cleaned)
    except:
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
        'negative_amounts': 0,
        'duplicates': [],
        'encoding_issues': 0,
        'raw_samples': []
    }
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                # Read all lines to check for encoding issues
                lines = file.readlines()
                stats['total_rows'] = len(lines)
                
                # Reset file position
                file.seek(0)
                
                # Parse CSV
                csv_reader = csv.DictReader(file, delimiter=';')
                
                # Check if we have headers
                if csv_reader.fieldnames:
                    stats['header_rows'] = 1
                    # Fix potential encoding issues in field names
                    fieldnames = []
                    for field in csv_reader.fieldnames:
                        # Common encoding fixes
                        field = field.replace('Emissão', 'Emissão')
                        field = field.replace('Nº', 'Nº')
                        field = field.replace('Comunicação', 'Comunicação')
                        field = field.replace('Situação', 'Situação')
                        fieldnames.append(field)
                    print(f"Headers found: {fieldnames}")
                
                # Track seen invoices for duplicate detection
                seen_invoices = {}
                
                for row_num, row in enumerate(csv_reader, start=2):
                    # Check if row is empty
                    if not any(row.values()):
                        stats['empty_rows'] += 1
                        continue
                    
                    stats['data_rows'] += 1
                    
                    # Save first few rows as samples
                    if len(stats['raw_samples']) < 5:
                        stats['raw_samples'].append(row)
                    
                    # Extract supplier info
                    supplier = row.get('Emitente', '')
                    if supplier:
                        stats['unique_suppliers'].add(supplier)
                        stats['supplier_counts'][supplier] += 1
                    
                    # Document type
                    doc_type = row.get('Tipo', '')
                    if doc_type:
                        stats['document_types'][doc_type] += 1
                    
                    # Sector
                    sector = row.get('Setor', '')
                    if sector:
                        stats['sectors'][sector] += 1
                    
                    # Parse date - try different field names due to encoding
                    date_str = row.get('Data Emissão', '') or row.get('Data Emiss�o', '')
                    if date_str:
                        date_obj = parse_portuguese_date(date_str)
                        if date_obj:
                            if stats['date_range']['min'] is None or date_obj < stats['date_range']['min']:
                                stats['date_range']['min'] = date_obj
                            if stats['date_range']['max'] is None or date_obj > stats['date_range']['max']:
                                stats['date_range']['max'] = date_obj
                    
                    # Parse amounts
                    total_amount = parse_portuguese_amount(row.get('Total', '0'))
                    vat_amount = parse_portuguese_amount(row.get('IVA', '0'))
                    
                    stats['total_amount'] += total_amount
                    stats['total_vat'] += vat_amount
                    
                    if total_amount < 0:
                        stats['negative_amounts'] += 1
                    
                    # Check for duplicates based on unique fields
                    invoice_num = row.get('Nº Fatura / ATCUD', '') or row.get('N� Fatura / ATCUD', '')
                    invoice_key = f"{supplier}|{invoice_num}|{total_amount}"
                    if invoice_key in seen_invoices:
                        stats['duplicates'].append({
                            'row': row_num,
                            'supplier': supplier,
                            'invoice': invoice_num,
                            'amount': total_amount,
                            'original_row': seen_invoices[invoice_key]
                        })
                    else:
                        seen_invoices[invoice_key] = row_num
                
                print(f"\nSuccessfully parsed with {encoding} encoding")
                
                # Debug: Show sample raw data
                if stats['raw_samples']:
                    print("\nSample raw data (first row):")
                    for key, value in stats['raw_samples'][0].items():
                        print(f"  {key}: {value}")
                
                return stats
                
        except UnicodeDecodeError:
            print(f"Failed with {encoding} encoding, trying next...")
            continue
        except Exception as e:
            print(f"Error with {encoding}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    raise Exception("Could not parse file with any encoding")

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
    
    print(f"\n2. SUPPLIERS:")
    print(f"   - Unique suppliers: {len(stats['unique_suppliers'])}")
    print(f"   - Top 10 suppliers by frequency:")
    top_suppliers = sorted(stats['supplier_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    for supplier, count in top_suppliers:
        print(f"     • {supplier}: {count} invoices")
    
    print(f"\n3. DOCUMENT TYPES:")
    for doc_type, count in stats['document_types'].most_common():
        print(f"   - {doc_type}: {count}")
    
    print(f"\n4. SECTORS:")
    for sector, count in stats['sectors'].most_common():
        sector_name = sector if sector else "(No sector)"
        print(f"   - {sector_name}: {count}")
    
    print(f"\n5. DATE RANGE:")
    if stats['date_range']['min'] and stats['date_range']['max']:
        print(f"   - From: {stats['date_range']['min'].strftime('%d/%m/%Y')}")
        print(f"   - To: {stats['date_range']['max'].strftime('%d/%m/%Y')}")
        days_diff = (stats['date_range']['max'] - stats['date_range']['min']).days
        print(f"   - Period: {days_diff} days")
    
    print(f"\n6. FINANCIAL SUMMARY:")
    print(f"   - Total amount: €{stats['total_amount']:,.2f}")
    print(f"   - Total VAT: €{stats['total_vat']:,.2f}")
    print(f"   - Average per invoice: €{stats['total_amount']/stats['data_rows']:,.2f}")
    print(f"   - Negative amounts (credit notes): {stats['negative_amounts']}")
    
    print(f"\n7. DATA QUALITY:")
    print(f"   - Duplicate entries found: {len(stats['duplicates'])}")
    if stats['duplicates']:
        print("   - Duplicate details:")
        for dup in stats['duplicates'][:5]:  # Show first 5 duplicates
            print(f"     • Row {dup['row']}: {dup['supplier']} - {dup['invoice']} (€{dup['amount']:.2f})")
            print(f"       Duplicate of row {dup['original_row']}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: Found {stats['data_rows']} cost entries from {len(stats['unique_suppliers'])} unique suppliers")
    print("="*80)

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
        
        # Create a simple parser function for importing into the app
        print("\n\nSAMPLE PARSER FUNCTION FOR APP INTEGRATION:")
        print("-" * 60)
        print("""
def parse_efatura_csv(file_path):
    '''Parse e-fatura CSV and return cost documents'''
    costs = []
    
    with open(file_path, 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        for row in csv_reader:
            # Skip empty rows
            if not any(row.values()):
                continue
            
            # Parse supplier
            supplier_info = row.get('Emitente', '').split(' - ', 1)
            supplier_nif = supplier_info[0] if supplier_info else ''
            supplier_name = supplier_info[1] if len(supplier_info) > 1 else row.get('Emitente', '')
            
            # Parse amounts
            total = parse_portuguese_amount(row.get('Total', '0'))
            vat = parse_portuguese_amount(row.get('IVA', '0'))
            
            # Create cost document
            cost = {
                'supplier_nif': supplier_nif,
                'supplier_name': supplier_name,
                'document_number': row.get('Nº Fatura / ATCUD', '').split(' / ')[0],
                'document_type': row.get('Tipo', ''),
                'date': parse_portuguese_date(row.get('Data Emissão', '')),
                'total_amount': total,
                'vat_amount': vat,
                'taxable_amount': parse_portuguese_amount(row.get('Base Tributável', '0')),
                'sector': row.get('Setor', ''),
                'status': row.get('Situação', '')
            }
            
            costs.append(cost)
    
    return costs
""")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()