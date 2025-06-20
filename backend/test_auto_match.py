#!/usr/bin/env python3
"""
Test the auto-match functionality to see if it's creating duplicate associations
"""

import requests
import json

# Step 1: Get mock data
print("=== STEP 1: Loading mock data ===")
response = requests.get("http://localhost:8000/api/mock-data")
data = response.json()
session_id = data["session_id"]
print(f"Session ID: {session_id}")
print(f"Sales: {len(data['sales'])}, Costs: {len(data['costs'])}")

# Step 2: Run auto-match
print("\n=== STEP 2: Running auto-match ===")
match_response = requests.post("http://localhost:8000/api/auto-match", json={
    "session_id": session_id,
    "threshold": 60.0,
    "max_matches": 50
})

if match_response.status_code == 200:
    match_result = match_response.json()
    print(f"Status: {match_result.get('status', 'N/A')}")
    print(f"Message: {match_result.get('message', 'N/A')}")
    print(f"Total matches: {match_result.get('total_matches', 'N/A')}")
    
    # Print all keys to see what's available
    print("\nResponse keys:", list(match_result.keys()))
else:
    print(f"Auto-match failed: {match_response.status_code}")
    print(match_response.text)
    exit(1)

# Step 3: Get updated session data
print("\n=== STEP 3: Analyzing updated associations ===")
session_response = requests.get(f"http://localhost:8000/api/session/{session_id}")
if session_response.status_code == 200:
    session_data = session_response.json()
    sales = session_data["sales"]
    costs = session_data["costs"]
    
    # Analyze associations
    sales_with_costs = [s for s in sales if s.get("linked_costs", [])]
    costs_with_sales = [c for c in costs if c.get("linked_sales", [])]
    
    print(f"Sales with linked costs: {len(sales_with_costs)}")
    print(f"Costs with linked sales: {len(costs_with_sales)}")
    
    # Check for costs linked to many sales
    multi_linked_costs = []
    for cost in costs:
        num_links = len(cost.get("linked_sales", []))
        if num_links > 5:  # Flag costs linked to more than 5 sales
            multi_linked_costs.append((cost, num_links))
    
    if multi_linked_costs:
        print(f"\n⚠️ WARNING: Found {len(multi_linked_costs)} costs linked to MANY sales:")
        for cost, num_links in sorted(multi_linked_costs, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cost['id']} ({cost['supplier']}): €{cost['amount']} -> {num_links} sales!")
            print(f"    Linked to: {cost['linked_sales'][:5]}..." if len(cost['linked_sales']) > 5 else f"    Linked to: {cost['linked_sales']}")
    
    # Calculate impact
    total_cost_links = sum(len(c.get("linked_sales", [])) for c in costs)
    print(f"\nTotal cost-to-sale links: {total_cost_links}")
    print(f"Average links per cost: {total_cost_links / len(costs_with_sales) if costs_with_sales else 0:.2f}")
    
    # Check specific pattern
    costs_linked_to_all = [c for c in costs if len(c.get("linked_sales", [])) == 26]
    if costs_linked_to_all:
        print(f"\n🚨 CRITICAL: Found {len(costs_linked_to_all)} costs linked to ALL 26 sales!")
        for cost in costs_linked_to_all[:5]:
            print(f"  {cost['id']} ({cost['supplier']}): €{cost['amount']}")

# Step 4: Run calculation to see the impact
print("\n=== STEP 4: Running calculation ===")
calc_response = requests.post("http://localhost:8000/api/calculate", json={
    "session_id": session_id,
    "vat_rate": 23
})

if calc_response.status_code == 200:
    print("Calculation successful - Excel file generated")
else:
    print(f"Calculation failed: {calc_response.status_code}")