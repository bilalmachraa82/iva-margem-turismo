#!/usr/bin/env python3
"""
Debug script to test associations between sales and costs
Tests the full flow: load data -> associate -> calculate -> verify results
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_associations():
    print("🔍 Testing Association Logic...")
    
    # Step 1: Load mock data
    print("\n1️⃣ Loading mock data...")
    response = requests.get(f"{API_URL}/api/mock-data")
    if response.status_code != 200:
        print(f"❌ Error loading mock data: {response.status_code}")
        return
    
    data = response.json()
    session_id = data["session_id"]
    print(f"✅ Session created: {session_id}")
    print(f"📊 Loaded {len(data['sales'])} sales and {len(data['costs'])} costs")
    
    # Get first sale and all costs
    first_sale = data['sales'][0]
    all_cost_ids = [cost['id'] for cost in data['costs']]
    
    print(f"\n📋 First sale: {first_sale['number']} - €{first_sale['amount']}")
    print(f"💰 Total costs available: €{sum(cost['amount'] for cost in data['costs'])}")
    
    # Step 2: Associate first sale with ALL costs
    print(f"\n2️⃣ Associating sale {first_sale['id']} with ALL {len(all_cost_ids)} costs...")
    
    association_request = {
        "session_id": session_id,
        "sale_ids": [first_sale['id']],
        "cost_ids": all_cost_ids
    }
    
    response = requests.post(
        f"{API_URL}/api/associate",
        json=association_request
    )
    
    if response.status_code != 200:
        print(f"❌ Error associating: {response.text}")
        return
        
    result = response.json()
    print(f"✅ Associations created: {result['associations_made']}")
    
    # Step 3: Verify associations were saved
    print("\n3️⃣ Verifying associations...")
    response = requests.get(f"{API_URL}/api/session/{session_id}")
    if response.status_code != 200:
        print(f"❌ Error getting session: {response.status_code}")
        return
        
    updated_data = response.json()
    updated_sale = next(s for s in updated_data['sales'] if s['id'] == first_sale['id'])
    
    print(f"✅ Sale now has {len(updated_sale['linked_costs'])} linked costs")
    print(f"   Linked cost IDs: {updated_sale['linked_costs'][:5]}... (showing first 5)")
    
    # Step 4: Calculate VAT
    print("\n4️⃣ Calculating VAT with associations...")
    
    calc_request = {
        "session_id": session_id,
        "vat_rate": 23
    }
    
    response = requests.post(
        f"{API_URL}/api/calculate",
        json=calc_request
    )
    
    if response.status_code != 200:
        print(f"❌ Error calculating: {response.status_code}")
        return
        
    # The response is an Excel file, so we can't parse it directly
    print(f"✅ Calculation completed - Excel file generated ({len(response.content)} bytes)")
    
    # Step 5: Test calculation logic directly
    print("\n5️⃣ Testing calculation logic directly...")
    
    # Import and test the calculator directly
    sys.path.insert(0, '/mnt/c/Users/Bilal/Documents/aiparati/claudia/iva-margem-turismo/backend')
    from app.calculator import VATCalculator
    
    calculator = VATCalculator(vat_rate=23)
    
    # Test with one sale that has all costs
    test_sale = updated_sale.copy()
    test_costs = updated_data['costs']
    
    # Calculate for this specific sale
    results = calculator.calculate_all([test_sale], test_costs)
    
    if results:
        result = results[0]
        print(f"\n📊 Calculation Result:")
        print(f"   Sale Amount: €{result['sale_amount']}")
        print(f"   Allocated Costs: €{result['total_allocated_costs']}")
        print(f"   Gross Margin: €{result['gross_margin']}")
        print(f"   VAT (23%): €{result['vat_amount']}")
        print(f"   Net Margin: €{result['net_margin']}")
        print(f"   Margin %: {result['margin_percentage']}%")
        print(f"   Linked Costs Count: {result['cost_count']}")
        
        # Check if it's working correctly
        if result['total_allocated_costs'] == 0:
            print("\n❌ PROBLEM: No costs were allocated!")
            print("   This means associations are not being considered in calculations")
        elif result['cost_count'] != len(all_cost_ids):
            print(f"\n⚠️ WARNING: Only {result['cost_count']} costs were considered, expected {len(all_cost_ids)}")
        else:
            print("\n✅ SUCCESS: All costs were properly allocated!")
            
    # Step 6: Test with different scenarios
    print("\n6️⃣ Testing edge cases...")
    
    # Test 1: One sale with one cost
    print("\nTest 1: One sale with one cost")
    test_sale_1 = {"id": "s1", "amount": 1000, "linked_costs": ["c1"]}
    test_cost_1 = {"id": "c1", "amount": 600, "linked_sales": ["s1"]}
    
    results_1 = calculator.calculate_all([test_sale_1], [test_cost_1])
    if results_1:
        r1 = results_1[0]
        print(f"   Sale: €1000, Cost: €600")
        print(f"   Expected Margin: €400, Actual: €{r1['gross_margin']}")
        print(f"   Expected VAT: €92, Actual: €{r1['vat_amount']}")
        
    # Test 2: One cost shared between two sales
    print("\nTest 2: One cost shared between two sales")
    test_sales_2 = [
        {"id": "s1", "amount": 1000, "linked_costs": ["c1"]},
        {"id": "s2", "amount": 1000, "linked_costs": ["c1"]}
    ]
    test_cost_2 = {"id": "c1", "amount": 600, "linked_sales": ["s1", "s2"]}
    
    results_2 = calculator.calculate_all(test_sales_2, [test_cost_2])
    if len(results_2) == 2:
        print(f"   Cost €600 shared between 2 sales")
        print(f"   Sale 1 allocated cost: €{results_2[0]['total_allocated_costs']} (expected €300)")
        print(f"   Sale 2 allocated cost: €{results_2[1]['total_allocated_costs']} (expected €300)")
        
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_associations()