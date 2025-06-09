#!/usr/bin/env python3
"""
Validação completa dos dados mock e cálculos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from calculator import VATCalculator

def validate_mock_data():
    """Analisa os dados mock e identifica problemas"""
    
    print("=" * 70)
    print("VALIDACAO COMPLETA DOS DADOS MOCK")
    print("=" * 70)
    
    # Dados mock originais
    sales = [
        {"id": "s1", "number": "FT E2025/1", "date": "2025-01-05", "client": "João Silva - Viagem Paris", "amount": 300.00, "vat_amount": 56.10, "linked_costs": []},
        {"id": "s2", "number": "FT E2025/2", "date": "2025-01-08", "client": "Maria Santos - Tour Europa", "amount": 1215.00, "vat_amount": 227.20, "linked_costs": []},
        {"id": "s3", "number": "FT E2025/3", "date": "2025-01-10", "client": "Pedro Costa - Escapada Lisboa", "amount": 406.00, "vat_amount": 75.92, "linked_costs": []},
        {"id": "s4", "number": "FR E2025/1", "date": "2025-01-12", "client": "Ana Ferreira - Cruzeiro Douro", "amount": 492.66, "vat_amount": 92.12, "linked_costs": []},
        {"id": "s5", "number": "FR E2025/3", "date": "2025-01-18", "client": "Sofia Rodrigues - América Tour", "amount": 12763.95, "vat_amount": 2386.75, "linked_costs": []},
        {"id": "s6", "number": "FT E2025/16", "date": "2025-01-20", "client": "Miguel Alves - Tailândia", "amount": 1759.00, "vat_amount": 328.92, "linked_costs": []},
        {"id": "s7", "number": "NC E2025/1", "date": "2025-01-22", "client": "Correção - João Silva", "amount": -420.00, "vat_amount": -78.54, "linked_costs": []}
    ]
    
    costs = [
        {"id": "c1", "supplier": "Hotel Pestana Porto", "description": "Alojamento 3 noites Twin", "date": "2025-01-03", "amount": 450.00, "vat_amount": 58.50, "linked_sales": []},
        {"id": "c2", "supplier": "TAP Air Portugal", "description": "Voos LIS-CDG-LIS Classe Y", "date": "2025-01-02", "amount": 890.00, "vat_amount": 115.70, "linked_sales": []},
        {"id": "c3", "supplier": "Europcar", "description": "Aluguer VW Golf 5 dias", "date": "2025-01-06", "amount": 350.00, "vat_amount": 45.50, "linked_sales": []},
        {"id": "c4", "supplier": "Paris Tours SARL", "description": "City tour + Versailles", "date": "2025-01-04", "amount": 280.00, "vat_amount": 56.00, "linked_sales": []},
        {"id": "c5", "supplier": "Douro Azul", "description": "Cruzeiro 2 dias Régua-Pinhão", "date": "2025-01-11", "amount": 1200.00, "vat_amount": 276.00, "linked_sales": []},
        {"id": "c6", "supplier": "American Express Travel", "description": "Pacote USA 15 dias all-inclusive", "date": "2025-01-16", "amount": 8500.00, "vat_amount": 1105.00, "linked_sales": []},
        {"id": "c7", "supplier": "Thai Airways", "description": "Voos LIS-BKK-LIS Business", "date": "2025-01-17", "amount": 2200.00, "vat_amount": 286.00, "linked_sales": []}
    ]
    
    print("\n1. PROBLEMAS IDENTIFICADOS NOS DADOS MOCK:")
    print("-" * 50)
    
    # Problema 1: Vendas já têm IVA
    print("PROBLEMA 1: Vendas já incluem IVA")
    print("No regime de margem, as vendas NÃO devem ter IVA separado!")
    print("O IVA é calculado sobre a margem, não sobre a venda.")
    
    print("\nVendas com IVA incorreto:")
    for sale in sales:
        if sale['vat_amount'] != 0:
            expected_total = sale['amount'] + sale['vat_amount']
            print(f"  {sale['number']}: €{sale['amount']:.2f} + IVA €{sale['vat_amount']:.2f} = €{expected_total:.2f}")
            print(f"    DEVERIA SER: Total vendido ao cliente = €{expected_total:.2f} (sem IVA separado)")
    
    # Problema 2: Custos com taxas de IVA inconsistentes
    print(f"\nPROBLEMA 2: Custos com taxas de IVA inconsistentes")
    print("Verificando taxas de IVA nos custos...")
    
    for cost in costs:
        if cost['vat_amount'] > 0:
            vat_rate = (cost['vat_amount'] / cost['amount']) * 100
            print(f"  {cost['supplier']}: Taxa IVA = {vat_rate:.1f}%")
            if abs(vat_rate - 23) > 2 and abs(vat_rate - 13) > 2 and abs(vat_rate - 6) > 2:
                print(f"    AVISO: Taxa incomum: {vat_rate:.1f}%")
    
    print(f"\n2. DADOS CORRIGIDOS PARA REGIME DE MARGEM:")
    print("-" * 50)
    
    # Corrigir vendas - remover IVA e usar valor total
    sales_corrected = []
    for sale in sales.copy():
        sale_corrected = sale.copy()
        # No regime de margem, o valor da venda é o total cobrado ao cliente
        sale_corrected['amount'] = sale['amount'] + sale['vat_amount']
        sale_corrected['vat_amount'] = 0  # IVA será calculado sobre margem
        sale_corrected['gross_total'] = sale_corrected['amount']
        sales_corrected.append(sale_corrected)
    
    print("Vendas corrigidas:")
    for i, (original, corrected) in enumerate(zip(sales, sales_corrected)):
        print(f"  {corrected['number']}:")
        print(f"    Antes: €{original['amount']:.2f} + IVA €{original['vat_amount']:.2f}")
        print(f"    Depois: €{corrected['amount']:.2f} (total cobrado ao cliente)")
    
    print(f"\n3. TESTE COM DADOS CORRIGIDOS:")
    print("-" * 50)
    
    # Exemplo prático: João Silva - Viagem Paris
    print("EXEMPLO: João Silva - Viagem Paris")
    
    # Corrigir associações para exemplo
    sales_corrected[0]['linked_costs'] = ['c2', 'c4']  # Voo + Tour
    costs[1]['linked_sales'] = ['s1']  # TAP
    costs[3]['linked_sales'] = ['s1']  # Paris Tours
    
    calc = VATCalculator(vat_rate=23)
    results = calc.calculate_all([sales_corrected[0]], costs)
    
    for result in results:
        print(f"\nCliente: {result['client']}")
        print(f"Valor cobrado ao cliente: €{result['sale_amount']:,.2f}")
        print(f"Custos diretos:")
        
        total_costs = 0
        for linked_cost in result['linked_costs']:
            print(f"  - {linked_cost['supplier']}: €{linked_cost['allocated_amount']:,.2f}")
            total_costs += linked_cost['allocated_amount']
        
        print(f"Total custos: €{total_costs:,.2f}")
        print(f"Margem bruta: €{result['gross_margin']:,.2f}")
        print(f"IVA sobre margem (23%): €{result['vat_amount']:,.2f}")
        print(f"Margem líquida: €{result['net_margin']:,.2f}")
        print(f"% Margem: {result['margin_percentage']:.1f}%")
        
        # Validação manual
        manual_margin = result['sale_amount'] - total_costs
        manual_vat = manual_margin * 23 / 100
        manual_net = manual_margin - manual_vat
        
        print(f"\nValidacao manual:")
        print(f"  Margem: €{result['sale_amount']:,.2f} - €{total_costs:,.2f} = €{manual_margin:,.2f}")
        print(f"  IVA: €{manual_margin:,.2f} × 23% = €{manual_vat:,.2f}")
        print(f"  Líquida: €{manual_margin:,.2f} - €{manual_vat:,.2f} = €{manual_net:,.2f}")
        
        if abs(result['gross_margin'] - manual_margin) < 0.01:
            print("  OK: Calculos corretos!")
        else:
            print("  ERRO nos calculos!")
    
    print(f"\n4. RECOMENDAÇÕES:")
    print("-" * 50)
    print("1. Corrigir dados mock para usar valores corretos do regime de margem")
    print("2. Remover vat_amount das vendas (deve ser sempre 0)")
    print("3. Usar gross_total como valor cobrado ao cliente")
    print("4. Documentar claramente que é regime especial de margem")
    print("5. Adicionar validações para evitar dados incorretos")
    
    return sales_corrected, costs

if __name__ == "__main__":
    validate_mock_data()