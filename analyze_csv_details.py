#!/usr/bin/env python3
"""Analyze CSV details to understand the data"""

import csv
import sys
sys.path.append('backend')

from app.efatura_parser import EFaturaParser

# Count lines in compras CSV
print("=== ANÁLISE DO CSV DE COMPRAS ===\n")

# Count raw lines
with open('e-fatura compras.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    print(f"Total de linhas no arquivo: {len(lines)}")
    print(f"Linha de cabeçalho: {lines[0].strip()[:100]}...")
    print(f"Linhas de dados: {len(lines) - 1}")

# Parse with the actual parser
with open('e-fatura venda.csv', 'rb') as f:
    vendas_content = f.read()

with open('e-fatura compras.csv', 'rb') as f:
    compras_content = f.read()

result = EFaturaParser.parse(vendas_content, compras_content)

print(f"\n=== RESULTADOS DO PARSER ===")
print(f"Vendas parseadas: {len(result['sales'])}")
print(f"Custos parseados: {len(result['costs'])}")

# Analyze costs by type
doc_types = {}
total_amount = 0
credit_notes = 0

for cost in result['costs']:
    doc_type = cost.get('description', '')
    if 'crédito' in doc_type.lower():
        credit_notes += 1
    
    if doc_type not in doc_types:
        doc_types[doc_type] = 0
    doc_types[doc_type] += 1
    
    total_amount += cost.get('amount', 0)

print(f"\n=== ANÁLISE DOS CUSTOS ===")
print(f"Total de documentos: {len(result['costs'])}")
print(f"Notas de crédito: {credit_notes}")
print(f"Valor total: €{total_amount:,.2f}")

print(f"\n=== TIPOS DE DOCUMENTOS ===")
for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
    print(f"{doc_type}: {count}")

# Show first 5 costs as sample
print(f"\n=== PRIMEIROS 5 CUSTOS ===")
for i, cost in enumerate(result['costs'][:5]):
    print(f"\nCusto {i+1}:")
    print(f"  Fornecedor: {cost.get('supplier', 'N/A')}")
    print(f"  Valor: €{cost.get('amount', 0):,.2f}")
    print(f"  Data: {cost.get('date', 'N/A')}")
    print(f"  Categoria: {cost.get('category', 'N/A')}")
    print(f"  Ícone: {cost.get('icon', 'N/A')}")

# Count unique suppliers
suppliers = set(cost.get('supplier', '') for cost in result['costs'])
print(f"\n=== ESTATÍSTICAS ===")
print(f"Fornecedores únicos: {len(suppliers)}")
print(f"Média por documento: €{total_amount/len(result['costs']):,.2f}")