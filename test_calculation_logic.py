#!/usr/bin/env python3
"""
Test calculation logic to show proper cost allocation
"""

import sys
sys.path.append('backend')

from app.calculator import VATCalculator

# Example scenario: 3 sales, 5 costs with realistic associations
sales = [
    {"id": "s1", "number": "FT 2025/1", "amount": 1000.0, "linked_costs": ["c1", "c2"]},
    {"id": "s2", "number": "FT 2025/2", "amount": 2000.0, "linked_costs": ["c2", "c3", "c4"]},
    {"id": "s3", "number": "FT 2025/3", "amount": 1500.0, "linked_costs": ["c5"]}
]

costs = [
    {"id": "c1", "supplier": "Hotel Lisboa", "amount": 400.0, "linked_sales": ["s1"]},
    {"id": "c2", "supplier": "TAP Airlines", "amount": 600.0, "linked_sales": ["s1", "s2"]},  # Shared cost
    {"id": "c3", "supplier": "Restaurant Porto", "amount": 200.0, "linked_sales": ["s2"]},
    {"id": "c4", "supplier": "Bus Tour", "amount": 300.0, "linked_sales": ["s2"]},
    {"id": "c5", "supplier": "Hotel Algarve", "amount": 800.0, "linked_sales": ["s3"]}
]

# Create associations from the linked data
associations = []
for sale in sales:
    for cost_id in sale.get("linked_costs", []):
        associations.append({"sale_id": sale["id"], "cost_id": cost_id})

print("=== REALISTIC ASSOCIATION EXAMPLE ===\n")
print("Sales:")
for sale in sales:
    print(f"  {sale['number']}: €{sale['amount']:.2f}")
    print(f"    Linked costs: {sale['linked_costs']}")

print("\nCosts:")
for cost in costs:
    print(f"  {cost['supplier']}: €{cost['amount']:.2f}")
    print(f"    Linked to sales: {cost['linked_sales']}")

# Calculate with proper allocation
calc = VATCalculator(vat_rate=23)
result = calc.calculate_all(sales, costs, associations)

print("\n=== CALCULATION RESULTS ===")
print(f"Total Sales: €{result['totals']['sales']:.2f}")
print(f"Total Costs: €{result['totals']['costs']:.2f}")
print(f"Gross Margin: €{result['totals']['margin']:.2f}")
print(f"IVA on Margin (23%): €{result['totals']['vat']:.2f}")
print(f"Net Margin: €{result['totals']['net_margin']:.2f}")

print("\n=== DETAILED BREAKDOWN ===")
for sale_detail in result['sales_details']:
    sale = next(s for s in sales if s['id'] == sale_detail['id'])
    print(f"\n{sale['number']}:")
    print(f"  Revenue: €{sale_detail['amount']:.2f}")
    
    # Show allocated costs
    allocated_costs = []
    for cost_id in sale['linked_costs']:
        cost = next(c for c in costs if c['id'] == cost_id)
        num_linked_sales = len(cost['linked_sales'])
        allocated_amount = cost['amount'] / num_linked_sales
        allocated_costs.append({
            'supplier': cost['supplier'],
            'total': cost['amount'],
            'allocated': allocated_amount,
            'shared_with': num_linked_sales
        })
    
    if allocated_costs:
        print("  Costs:")
        for ac in allocated_costs:
            if ac['shared_with'] > 1:
                print(f"    - {ac['supplier']}: €{ac['allocated']:.2f} (€{ac['total']:.2f} ÷ {ac['shared_with']} sales)")
            else:
                print(f"    - {ac['supplier']}: €{ac['allocated']:.2f}")
        
        total_allocated = sum(ac['allocated'] for ac in allocated_costs)
        margin = sale_detail['amount'] - total_allocated
        print(f"  Total Costs: €{total_allocated:.2f}")
        print(f"  Margin: €{margin:.2f} ({margin/sale_detail['amount']*100:.1f}%)")
        print(f"  IVA: €{margin * 0.23:.2f}")
    else:
        print("  No costs associated")

print("\n=== PROBLEMATIC SCENARIO ===")
print("\nIf ALL costs were linked to ALL sales (unrealistic):")
# Calculate problematic scenario
bad_associations = []
for sale in sales:
    for cost in costs:
        bad_associations.append({"sale_id": sale["id"], "cost_id": cost["id"]})

bad_result = calc.calculate_all(sales, costs, bad_associations)
print(f"Total margin would be: €{bad_result['totals']['margin']:.2f}")
print(f"This is unrealistic because each cost is divided among all sales!")

print("\n=== KEY INSIGHTS ===")
print("1. Proper associations reflect real business relationships")
print("2. Shared costs (like TAP Airlines) are automatically split")
print("3. Each cost is counted only once in the total")
print("4. The calculation logic is correct - the issue is data quality")