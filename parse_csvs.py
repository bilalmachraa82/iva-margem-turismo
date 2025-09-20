#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import re

def clean_amount(amount_str):
    """Limpa string de valor monetário"""
    if not amount_str:
        return 0.0

    # Remove € e espaços, e caracter º problemático
    cleaned = amount_str.replace('€', '').replace(' ', '').replace('º', '').strip()

    # Tratar formato português: 11.484,60 -> 11484.60
    if ',' in cleaned:
        # Se tem vírgula, é o separador decimal
        parts = cleaned.split(',')
        if len(parts) == 2:
            # Remove pontos da parte inteira (separadores de milhares)
            integer_part = parts[0].replace('.', '')
            decimal_part = parts[1]
            cleaned = f"{integer_part}.{decimal_part}"
    else:
        # Se não tem vírgula, pode ter só pontos como separadores de milhares
        cleaned = cleaned.replace('.', '')

    try:
        return float(cleaned)
    except ValueError:
        print(f"Erro ao converter: '{amount_str}' -> '{cleaned}'")
        return 0.0

def parse_sales_csv():
    """Parse do CSV de vendas"""
    sales = []

    with open('e-fatura venda.csv', 'r', encoding='utf-8-sig') as f:
        content = f.read()
        # Substituir caracteres problemáticos
        content = content.replace('�', 'º')

        lines = content.strip().split('\n')
        headers = lines[0].split(';')

        for i, line in enumerate(lines[1:], 1):
            fields = line.split(';')
            if len(fields) >= 5:
                try:
                    doc_num = fields[0].strip()
                    doc_type = fields[3].strip()
                    amount_str = fields[4].strip()
                    date_str = fields[2].strip()

                    amount = clean_amount(amount_str)

                    # Se é nota de crédito, valor deve ser negativo
                    if 'Nota de cr' in doc_type or doc_num.startswith('NC'):
                        amount = -abs(amount)
                        print(f"Nota de crédito detectada: {doc_num} = -€{abs(amount)}")

                    # Extrair cliente do NIF (simplificado)
                    nif = fields[1].strip() if len(fields) > 1 else ""
                    client = f"Cliente {nif[-4:]}" if nif else "Cliente Desconhecido"

                    sales.append({
                        "id": f"s{i}",
                        "number": doc_num.split('/')[0].strip(),
                        "date": "2025-01-15",  # Data simplificada
                        "client": client,
                        "amount": amount,
                        "doc_type": doc_type
                    })

                except Exception as e:
                    print(f"Erro linha {i}: {e}")
                    continue

    return sales

def parse_costs_csv():
    """Parse do CSV de custos"""
    costs = []

    with open('e-fatura compras.csv', 'r', encoding='utf-8-sig') as f:
        content = f.read()
        # Substituir caracteres problemáticos
        content = content.replace('�', 'º')

        lines = content.strip().split('\n')
        headers = lines[0].split(';')

        for i, line in enumerate(lines[1:], 1):
            fields = line.split(';')
            if len(fields) >= 6:
                try:
                    supplier_raw = fields[1].strip()
                    amount_str = fields[5].strip()

                    amount = clean_amount(amount_str)

                    # Extrair nome do fornecedor
                    if ' - ' in supplier_raw:
                        supplier = supplier_raw.split(' - ', 1)[1]
                    else:
                        supplier = supplier_raw

                    # Limitar tamanho do nome
                    if len(supplier) > 40:
                        supplier = supplier[:37] + "..."

                    costs.append({
                        "id": f"c{i}",
                        "supplier": supplier,
                        "amount": amount,
                        "date": "2025-01-15"  # Data simplificada
                    })

                except Exception as e:
                    print(f"Erro linha custo {i}: {e}")
                    continue

    return costs

def main():
    print("📊 PROCESSANDO TODOS OS CSVs E-FATURA...")

    # Parse vendas
    sales = parse_sales_csv()
    print(f"✅ Vendas processadas: {len(sales)}")

    # Parse custos
    costs = parse_costs_csv()
    print(f"✅ Custos processados: {len(costs)}")

    # Calcular totais
    total_sales_positive = sum(s['amount'] for s in sales if s['amount'] > 0)
    total_sales_negative = sum(s['amount'] for s in sales if s['amount'] < 0)
    net_sales = total_sales_positive + total_sales_negative
    total_costs = sum(c['amount'] for c in costs)
    margin = net_sales - total_costs

    print(f"\n💰 Vendas Positivas: €{total_sales_positive:,.2f}")
    print(f"💸 Vendas Negativas: €{total_sales_negative:,.2f}")
    print(f"📊 Vendas Líquidas: €{net_sales:,.2f}")
    print(f"💳 Total Custos: €{total_costs:,.2f}")
    print(f"📈 Margem: €{margin:,.2f}")

    # Gerar JSON para a API
    api_data = {
        "sales": sales,
        "costs": costs,
        "metadata": {
            "total_sales_positive": round(total_sales_positive, 2),
            "total_sales_negative": round(total_sales_negative, 2),
            "net_sales": round(net_sales, 2),
            "total_costs": round(total_costs, 2),
            "potential_margin": round(margin, 2)
        }
    }

    with open('complete_data.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Dados salvos em complete_data.json")
    print(f"📄 {len(sales)} vendas + {len(costs)} custos processados!")

if __name__ == "__main__":
    main()