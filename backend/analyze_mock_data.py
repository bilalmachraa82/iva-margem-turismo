#!/usr/bin/env python3
"""
Analyze the mock data to check for cost duplication issues
"""

import requests
import json

# Get mock data from API
response = requests.get("http://localhost:8000/api/mock-data")
if response.status_code != 200:
    print(f"Error fetching mock data: {response.status_code}")
    exit(1)

data = response.json()
session_id = data["session_id"]
sales = data["sales"]
costs = data["costs"]

print(f"=== MOCK DATA ANALYSIS ===")
print(f"Session ID: {session_id}")
print(f"Total sales: {len(sales)}")
print(f"Total costs: {len(costs)}")

# Check for pre-existing associations
sales_with_costs = [s for s in sales if s.get("linked_costs", [])]
costs_with_sales = [c for c in costs if c.get("linked_sales", [])]

print(f"\nSales with linked costs: {len(sales_with_costs)}")
print(f"Costs with linked sales: {len(costs_with_sales)}")

# Analyze associations
if sales_with_costs:
    print("\nSALES WITH ASSOCIATIONS:")
    for sale in sales_with_costs:
        print(f"  {sale['number']}: linked to {len(sale['linked_costs'])} costs: {sale['linked_costs']}")

if costs_with_sales:
    print("\nCOSTS WITH ASSOCIATIONS:")
    total_links = 0
    for cost in costs_with_sales:
        num_links = len(cost['linked_sales'])
        total_links += num_links
        print(f"  {cost['id']} ({cost['supplier']}): linked to {num_links} sales: {cost['linked_sales']}")
    
    print(f"\nTotal cost-to-sale links: {total_links}")
    print(f"Average sales per cost: {total_links / len(costs_with_sales):.2f}")

# Check for potential duplication scenarios
print("\n=== CHECKING FOR DUPLICATION SCENARIOS ===")

# Find costs linked to multiple sales
multi_linked_costs = [c for c in costs if len(c.get("linked_sales", [])) > 1]
if multi_linked_costs:
    print(f"\nCosts linked to MULTIPLE sales: {len(multi_linked_costs)}")
    for cost in multi_linked_costs:
        print(f"  {cost['id']} ({cost['supplier']}): €{cost['amount']} -> {len(cost['linked_sales'])} sales")

# Calculate total amounts
total_sales_amount = sum(s["amount"] for s in sales)
total_costs_amount = sum(c["amount"] for c in costs)

print(f"\n=== TOTALS ===")
print(f"Total sales amount: €{total_sales_amount:,.2f}")
print(f"Total costs amount: €{total_costs_amount:,.2f}")
print(f"Expected gross margin: €{total_sales_amount - total_costs_amount:,.2f}")
print(f"Expected margin %: {((total_sales_amount - total_costs_amount) / total_sales_amount * 100):.2f}%")

# Now test a calculation
print("\n=== TESTING CALCULATION ===")
calc_response = requests.post("http://localhost:8000/api/calculate", json={
    "session_id": session_id,
    "vat_rate": 23
})

if calc_response.status_code == 200:
    print("Calculation successful - Excel file generated")
    # The response is an Excel file, so we can't easily analyze it here
    print("Check the generated Excel file for detailed results")
else:
    print(f"Calculation failed: {calc_response.status_code}")
    print(calc_response.text)