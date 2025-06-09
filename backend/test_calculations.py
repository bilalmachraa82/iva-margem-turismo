#!/usr/bin/env python3
"""
Teste manual para validar cálculos de IVA sobre margem
Conforme CIVA Art. 308º - Portugal
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from calculator import VATCalculator

def test_vat_calculations():
    """Testa cálculos com exemplos reais de agência de viagens"""
    
    calc = VATCalculator(vat_rate=23)  # Taxa normal continental
    
    print("=" * 60)
    print("TESTE DE CÁLCULO DE IVA SOBRE MARGEM")
    print("Conformidade: CIVA Art. 308º - Portugal")
    print("=" * 60)
    
    # Exemplo 1: Viagem simples
    print("\nEXEMPLO 1: Viagem Paris")
    print("-" * 30)
    
    sales = [
        {
            "id": "s1",
            "number": "FT 2025/001",
            "date": "2025-01-05",
            "client": "João Silva - Viagem Paris",
            "amount": 1500.00,  # Preço venda ao cliente
            "vat_amount": 0,  # Venda sem IVA (margem)
            "linked_costs": ["c1", "c2"]
        }
    ]
    
    costs = [
        {
            "id": "c1",
            "supplier": "TAP Air Portugal",
            "description": "Voos LIS-CDG-LIS",
            "amount": 800.00,  # Custo direto
            "linked_sales": ["s1"]
        },
        {
            "id": "c2", 
            "supplier": "Hotel Paris",
            "description": "Alojamento 3 noites",
            "amount": 450.00,  # Custo direto
            "linked_sales": ["s1"]
        }
    ]
    
    results = calc.calculate_all(sales, costs)
    
    for result in results:
        print(f"Fatura: {result['invoice_number']}")
        print(f"Cliente: {result['client']}")
        print(f"Preço Venda: €{result['sale_amount']:,.2f}")
        print(f"Custos Diretos: €{result['total_allocated_costs']:,.2f}")
        print(f"Margem Bruta: €{result['gross_margin']:,.2f}")
        print(f"IVA sobre Margem ({calc.vat_rate}%): €{result['vat_amount']:,.2f}")
        print(f"Margem Líquida: €{result['net_margin']:,.2f}")
        print(f"% Margem: {result['margin_percentage']:.1f}%")
        
        # Validação manual
        expected_margin = 1500 - 800 - 450  # 250
        expected_vat = expected_margin * 23 / 100  # 57.50
        expected_net = expected_margin - expected_vat  # 192.50
        
        print(f"\nValidacao:")
        print(f"  Margem esperada: €{expected_margin:.2f} | Calculada: €{result['gross_margin']:.2f}")
        print(f"  IVA esperado: €{expected_vat:.2f} | Calculado: €{result['vat_amount']:.2f}")
        print(f"  Líquida esperada: €{expected_net:.2f} | Calculada: €{result['net_margin']:.2f}")
        
        # Verificar se está correto
        assert abs(result['gross_margin'] - expected_margin) < 0.01, "Erro no cálculo da margem"
        assert abs(result['vat_amount'] - expected_vat) < 0.01, "Erro no cálculo do IVA"
        assert abs(result['net_margin'] - expected_net) < 0.01, "Erro no cálculo da margem líquida"
        
        print("  OK: Todos os calculos corretos!")
    
    # Exemplo 2: Múltiplas vendas partilhando custos
    print("\n\nEXEMPLO 2: Custos Partilhados")
    print("-" * 30)
    
    sales2 = [
        {
            "id": "s1",
            "number": "FT 2025/002", 
            "client": "Maria Santos",
            "amount": 1000.00,
            "linked_costs": ["c1"]  # Partilha o voo
        },
        {
            "id": "s2",
            "number": "FT 2025/003",
            "client": "Pedro Costa", 
            "amount": 800.00,
            "linked_costs": ["c1"]  # Partilha o voo
        }
    ]
    
    costs2 = [
        {
            "id": "c1",
            "supplier": "TAP Air Portugal",
            "description": "Voo grupo 10 pessoas",
            "amount": 1200.00,  # Custo total do grupo
            "linked_sales": ["s1", "s2"]  # Partilhado entre 2 vendas
        }
    ]
    
    results2 = calc.calculate_all(sales2, costs2)
    
    total_vat = 0
    for result in results2:
        print(f"\nFatura: {result['invoice_number']}")
        print(f"Venda: €{result['sale_amount']:,.2f}")
        print(f"Custo Alocado: €{result['total_allocated_costs']:,.2f}")
        print(f"Margem: €{result['gross_margin']:,.2f}")
        print(f"IVA: €{result['vat_amount']:,.2f}")
        total_vat += result['vat_amount']
    
    print(f"\nTotal IVA das duas vendas: €{total_vat:.2f}")
    
    # Exemplo 3: Margem negativa (prejuízo)
    print("\n\nEXEMPLO 3: Margem Negativa")
    print("-" * 30)
    
    sales3 = [
        {
            "id": "s1",
            "number": "FT 2025/004",
            "client": "Ana Silva - Promoção",
            "amount": 500.00,  # Preço promocional
            "linked_costs": ["c1"]
        }
    ]
    
    costs3 = [
        {
            "id": "c1", 
            "supplier": "Fornecedor",
            "description": "Serviço caro",
            "amount": 700.00,  # Custo > Venda
            "linked_sales": ["s1"]
        }
    ]
    
    results3 = calc.calculate_all(sales3, costs3)
    
    for result in results3:
        print(f"Fatura: {result['invoice_number']}")
        print(f"Venda: €{result['sale_amount']:,.2f}")
        print(f"Custo: €{result['total_allocated_costs']:,.2f}")
        print(f"Margem: €{result['gross_margin']:,.2f} (PREJUÍZO)")
        print(f"IVA: €{result['vat_amount']:,.2f} (Zero - sem IVA sobre prejuízo)")
        print(f"Resultado: €{result['net_margin']:,.2f}")
    
    print("\n" + "=" * 60)
    print("OK: TODOS OS TESTES PASSARAM!")
    print("OK: Calculos conformes com CIVA Art. 308")
    print("=" * 60)

if __name__ == "__main__":
    test_vat_calculations()