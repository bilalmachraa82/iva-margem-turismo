#!/usr/bin/env python3
"""
Test different association scenarios to find the duplication issue
"""

import requests
import json

def test_manual_association():
    """Test manual association of all costs to all sales (worst case)"""
    print("=== TEST: Manual Association (All-to-All) ===")
    
    # Get mock data
    response = requests.get("http://localhost:8000/api/mock-data")
    data = response.json()
    session_id = data["session_id"]
    
    # Get all sale and cost IDs
    sale_ids = [s["id"] for s in data["sales"]]
    cost_ids = [c["id"] for c in data["costs"]]
    
    print(f"Session: {session_id}")
    print(f"Sales: {len(sale_ids)}, Costs: {len(cost_ids)}")
    
    # Associate ALL costs to ALL sales (this would be the duplication scenario)
    print("\nAssociating ALL costs to ALL sales...")
    assoc_response = requests.post("http://localhost:8000/api/associate", json={
        "session_id": session_id,
        "sale_ids": sale_ids,
        "cost_ids": cost_ids
    })
    
    if assoc_response.status_code == 200:
        result = assoc_response.json()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Associations made: {result.get('associations_made', 'N/A')}")
        
        # Now check the impact
        session_response = requests.get(f"http://localhost:8000/api/session/{session_id}")
        if session_response.status_code == 200:
            session_data = session_response.json()
            
            # Check costs
            costs = session_data["costs"]
            for i, cost in enumerate(costs[:5]):  # Show first 5
                num_links = len(cost.get("linked_sales", []))
                print(f"\nCost {i+1}: {cost['supplier']} - €{cost['amount']}")
                print(f"  Linked to {num_links} sales (out of {len(sale_ids)} total)")
            
            # Calculate theoretical duplication
            total_costs = sum(c["amount"] for c in data["costs"])
            print(f"\n=== DUPLICATION ANALYSIS ===")
            print(f"Original total costs: €{total_costs:,.2f}")
            print(f"If each cost is allocated to {len(sale_ids)} sales:")
            print(f"Total allocated (duplicated) amount: €{total_costs * len(sale_ids):,.2f}")
            print(f"Duplication factor: {len(sale_ids)}x")
            
            # Run calculation
            print("\nRunning calculation...")
            calc_response = requests.post("http://localhost:8000/api/calculate", json={
                "session_id": session_id,
                "vat_rate": 23
            })
            
            if calc_response.status_code == 200:
                print("✓ Calculation completed - check Excel for results")
            else:
                print(f"✗ Calculation failed: {calc_response.status_code}")

def test_auto_match_low_threshold():
    """Test auto-match with very low threshold"""
    print("\n\n=== TEST: Auto-Match with Low Threshold ===")
    
    # Get mock data
    response = requests.get("http://localhost:8000/api/mock-data")
    data = response.json()
    session_id = data["session_id"]
    
    print(f"Session: {session_id}")
    
    # Try auto-match with threshold 10%
    match_response = requests.post("http://localhost:8000/api/auto-match", json={
        "session_id": session_id,
        "threshold": 10.0,  # Very low threshold
        "max_matches": 200
    })
    
    if match_response.status_code == 200:
        result = match_response.json()
        print(f"Matches found: {result.get('matches_found', 0)}")
        
        # Show some matches
        matches = result.get('matches', [])
        if matches:
            print(f"\nShowing first 10 matches:")
            for match in matches[:10]:
                print(f"  Cost: {match['cost']}, Sale: {match['sale']}, Confidence: {match['confidence']}%")

def test_partial_association():
    """Test a more realistic partial association"""
    print("\n\n=== TEST: Partial Association ===")
    
    # Get mock data
    response = requests.get("http://localhost:8000/api/mock-data")
    data = response.json()
    session_id = data["session_id"]
    
    # Associate first 10 costs to first 5 sales
    sale_ids = [s["id"] for s in data["sales"][:5]]
    cost_ids = [c["id"] for c in data["costs"][:10]]
    
    print(f"Associating {len(cost_ids)} costs to {len(sale_ids)} sales")
    
    assoc_response = requests.post("http://localhost:8000/api/associate", json={
        "session_id": session_id,
        "sale_ids": sale_ids,
        "cost_ids": cost_ids
    })
    
    if assoc_response.status_code == 200:
        result = assoc_response.json()
        print(f"Associations made: {result.get('associations_made', 'N/A')}")

# Run tests
if __name__ == "__main__":
    test_manual_association()
    test_auto_match_low_threshold()
    test_partial_association()