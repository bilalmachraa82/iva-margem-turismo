#!/usr/bin/env python3
"""Analyze sales CSV to compare with costs"""

import csv
import sys
sys.path.append('backend')

from app.efatura_parser import EFaturaParser

print("=== ANÁLISE COMPLETA VENDAS VS CUSTOS ===\n")

# Parse both files
with open('e-fatura venda.csv', 'rb') as f:
    vendas_content = f.read()

with open('e-fatura compras.csv', 'rb') as f:
    compras_content = f.read()

result = EFaturaParser.parse(vendas_content, compras_content)

# Analyze sales
total_sales = 0
sales_by_type = {}
credit_notes_sales = 0

print("=== ANÁLISE DAS VENDAS ===")
print(f"Total de documentos de venda: {len(result['sales'])}")

for sale in result['sales']:
    amount = sale.get('amount', 0)
    total_sales += amount
    
    doc_type = sale.get('doc_type', 'Unknown')
    if doc_type not in sales_by_type:
        sales_by_type[doc_type] = {'count': 0, 'total': 0}
    
    sales_by_type[doc_type]['count'] += 1
    sales_by_type[doc_type]['total'] += amount
    
    if 'crédito' in doc_type.lower():
        credit_notes_sales += 1

print(f"\nTipos de documentos de venda:")
for doc_type, data in sales_by_type.items():
    print(f"  {doc_type}: {data['count']} docs, €{data['total']:,.2f}")

print(f"\nTotal de vendas: €{total_sales:,.2f}")
print(f"Notas de crédito: {credit_notes_sales}")

# Analyze costs
total_costs = 0
costs_by_type = {}
credit_notes_costs = 0

print("\n=== ANÁLISE DOS CUSTOS ===")
print(f"Total de documentos de compra: {len(result['costs'])}")

for cost in result['costs']:
    amount = cost.get('amount', 0)
    total_costs += amount
    
    desc = cost.get('description', 'Unknown')
    if desc not in costs_by_type:
        costs_by_type[desc] = {'count': 0, 'total': 0}
    
    costs_by_type[desc]['count'] += 1
    costs_by_type[desc]['total'] += amount
    
    if 'crédito' in desc.lower():
        credit_notes_costs += 1

print(f"\nTipos de documentos de compra:")
for doc_type, data in sorted(costs_by_type.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"  {doc_type}: {data['count']} docs, €{data['total']:,.2f}")

print(f"\nTotal de custos: €{total_costs:,.2f}")
print(f"Notas de crédito: {credit_notes_costs}")

# Calculate margin
print("\n=== COMPARAÇÃO VENDAS VS CUSTOS ===")
print(f"Total Vendas: €{total_sales:,.2f}")
print(f"Total Custos: €{total_costs:,.2f}")
margin = total_sales - total_costs
margin_percent = (margin / total_sales * 100) if total_sales > 0 else 0
print(f"Margem Bruta: €{margin:,.2f} ({margin_percent:.1f}%)")

if margin < 0:
    print("\n⚠️ ALERTA: Os custos são maiores que as vendas!")
    print(f"   Déficit: €{abs(margin):,.2f}")
else:
    print("\n✅ Margem positiva")

# Show some sales details
print("\n=== DETALHES DAS VENDAS ===")
for i, sale in enumerate(result['sales'][:10]):
    print(f"\nVenda {i+1}:")
    print(f"  Número: {sale.get('number', 'N/A')}")
    print(f"  Cliente: {sale.get('client', 'N/A')}")
    print(f"  Valor: €{sale.get('amount', 0):,.2f}")
    print(f"  Data: {sale.get('date', 'N/A')}")
    print(f"  Tipo: {sale.get('doc_type', 'N/A')}")

# Date range analysis
print("\n=== ANÁLISE TEMPORAL ===")
sales_dates = [s.get('date', '') for s in result['sales'] if s.get('date')]
costs_dates = [c.get('date', '') for c in result['costs'] if c.get('date')]

if sales_dates:
    print(f"Vendas: {min(sales_dates)} a {max(sales_dates)}")
if costs_dates:
    print(f"Custos: {min(costs_dates)} a {max(costs_dates)}")