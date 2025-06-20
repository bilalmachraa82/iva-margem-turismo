#!/usr/bin/env python3
"""Test e-Fatura parser with real CSV files"""

import sys
sys.path.append('backend')

from app.efatura_parser import EFaturaParser

# Read the CSV files
with open('e-fatura venda.csv', 'rb') as f:
    vendas_content = f.read()

with open('e-fatura compras.csv', 'rb') as f:
    compras_content = f.read()

# Test the parser
result = EFaturaParser.parse(vendas_content, compras_content)

print(f"Sales parsed: {len(result['sales'])}")
print(f"Costs parsed: {len(result['costs'])}")
print(f"Parsing errors: {len(result['parsing_errors'])}")

if result['parsing_errors']:
    print("\nErrors:")
    for error in result['parsing_errors']:
        print(f"  - {error}")

if result['sales']:
    print("\nFirst sale:")
    sale = result['sales'][0]
    for key, value in sale.items():
        print(f"  {key}: {value}")

if result['costs']:
    print("\nFirst cost:")
    cost = result['costs'][0]
    for key, value in cost.items():
        print(f"  {key}: {value}")