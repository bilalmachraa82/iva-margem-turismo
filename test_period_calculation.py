#!/usr/bin/env python3
"""
Test period-based VAT calculation with compensation
"""

import sys
sys.path.append('backend')

from datetime import date
from decimal import Decimal
from app.period_calculator import PeriodVATCalculator

# Test scenario: Q4/2024 (costs) and Q1/2025 (sales)
# This matches the real data scenario

# Simulated Q4/2024 - Only costs
q4_sales = []
q4_costs = [
    {"id": "c1", "supplier": "Hotel Lisboa", "amount": 15000.0, "date": "2024-10-15", "linked_sales": []},
    {"id": "c2", "supplier": "TAP Airlines", "amount": 20000.0, "date": "2024-11-20", "linked_sales": []},
    {"id": "c3", "supplier": "Restaurant Porto", "amount": 10225.09, "date": "2024-12-10", "linked_sales": []},
]

# Simulated Q1/2025 - Only sales
q1_sales = [
    {"id": "s1", "number": "FT 2025/1", "amount": 15000.0, "date": "2025-01-15", "linked_costs": []},
    {"id": "s2", "number": "FT 2025/2", "amount": 12000.0, "date": "2025-02-20", "linked_costs": []},
    {"id": "s3", "number": "FT 2025/3", "amount": 7950.93, "date": "2025-03-10", "linked_costs": []},
]
q1_costs = []

print("=== TESTE CÁLCULO IVA POR PERÍODO ===\n")

# Initialize calculator
calc = PeriodVATCalculator(region='continental')

print("1. Q4/2024 - Período com apenas custos")
print("="*50)

# Calculate Q4/2024
q4_result = calc.calculate_period_vat(
    sales=q4_sales,
    costs=q4_costs,
    associations=[],
    start_date=date(2024, 10, 1),
    end_date=date(2024, 12, 31),
    previous_negative_margin=Decimal('0')
)

print(f"Vendas: €{q4_result['totals']['sales']:,.2f}")
print(f"Custos: €{q4_result['totals']['costs']:,.2f}")
print(f"Margem Bruta: €{q4_result['totals']['gross_margin']:,.2f}")
print(f"Margem Negativa Anterior: €{q4_result['totals']['previous_negative']:,.2f}")
print(f"Margem Compensada: €{q4_result['totals']['compensated_margin']:,.2f}")
print(f"Base Tributável: €{q4_result['totals']['vat_base']:,.2f}")
print(f"IVA a Pagar: €{q4_result['totals']['vat_amount']:,.2f}")
print(f"Margem Negativa a Transportar: €{q4_result['totals']['carry_forward']:,.2f}")

print("\n2. Q1/2025 - Período com apenas vendas + compensação")
print("="*50)

# Calculate Q1/2025 with compensation
q1_result = calc.calculate_period_vat(
    sales=q1_sales,
    costs=q1_costs,
    associations=[],
    start_date=date(2025, 1, 1),
    end_date=date(2025, 3, 31),
    previous_negative_margin=abs(Decimal(str(q4_result['totals']['carry_forward'])))
)

print(f"Vendas: €{q1_result['totals']['sales']:,.2f}")
print(f"Custos: €{q1_result['totals']['costs']:,.2f}")
print(f"Margem Bruta: €{q1_result['totals']['gross_margin']:,.2f}")
print(f"Margem Negativa Anterior: €{q1_result['totals']['previous_negative']:,.2f}")
print(f"Margem Compensada: €{q1_result['totals']['compensated_margin']:,.2f}")
print(f"Base Tributável: €{q1_result['totals']['vat_base']:,.2f}")
print(f"IVA a Pagar: €{q1_result['totals']['vat_amount']:,.2f}")
print(f"Margem Negativa a Transportar: €{q1_result['totals']['carry_forward']:,.2f}")

print("\n3. COMPARAÇÃO: Cálculo por Transação vs Por Período")
print("="*50)

# Wrong calculation (by transaction)
total_sales = sum(s['amount'] for s in q1_sales)
vat_by_transaction = Decimal(str(total_sales)) * Decimal('0.23')

print(f"❌ Por Transação (ERRADO):")
print(f"   IVA = Vendas Q1 × 23% = €{total_sales:,.2f} × 23% = €{vat_by_transaction:,.2f}")

print(f"\n✅ Por Período com Compensação (CORRETO):")
print(f"   Q4: Margem = -€45,225.09 (transporta)")
print(f"   Q1: Margem = €34,950.93")
print(f"   Margem Compensada = €34,950.93 - €45,225.09 = -€10,274.16")
print(f"   IVA = €0.00 (margem ainda negativa)")

print(f"\n💰 DIFERENÇA: €{vat_by_transaction:,.2f} de IVA poupado!")

print("\n4. Simulação Q2/2025 - Continuação da compensação")
print("="*50)

# Simulate Q2/2025 with positive margin
q2_sales = [
    {"id": "s4", "number": "FT 2025/4", "amount": 25000.0, "date": "2025-04-15", "linked_costs": []},
]
q2_costs = [
    {"id": "c4", "supplier": "Hotel Algarve", "amount": 5000.0, "date": "2025-04-10", "linked_sales": []},
]

q2_result = calc.calculate_period_vat(
    sales=q2_sales,
    costs=q2_costs,
    associations=[],
    start_date=date(2025, 4, 1),
    end_date=date(2025, 6, 30),
    previous_negative_margin=abs(Decimal(str(q1_result['totals']['carry_forward'])))
)

print(f"Margem Q2: €{q2_result['totals']['gross_margin']:,.2f}")
print(f"Margem Negativa Q1: €{q2_result['totals']['previous_negative']:,.2f}")
print(f"Margem Compensada: €{q2_result['totals']['compensated_margin']:,.2f}")
print(f"IVA a Pagar: €{q2_result['totals']['vat_amount']:,.2f}")

print("\n=== RESUMO FINAL ===")
print(f"Q4/2024: IVA = €0.00 (margem -€45,225.09)")
print(f"Q1/2025: IVA = €0.00 (margem -€10,274.16 após compensação)")
print(f"Q2/2025: IVA = €{q2_result['totals']['vat_amount']:,.2f} (finalmente positivo)")
print(f"\nEste é o cálculo correto segundo a lei portuguesa!")