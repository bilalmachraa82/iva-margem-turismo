#!/usr/bin/env python3
"""
Quick test to verify backend API functionality using mock data
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_backend_api():
    """Test core backend functionality"""
    print("🧪 Testing backend API...")

    async with aiohttp.ClientSession() as session:
        # Test 1: Health check
        print("1. Health check...", end=" ")
        try:
            async with session.get(f"{BASE_URL}/") as resp:
                if resp.status == 200:
                    print("✅")
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

        # Test 2: Mock data endpoint
        print("2. Mock data loading...", end=" ")
        try:
            async with session.get(f"{BASE_URL}/api/mock-data") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    session_id = data.get("session_id")
                    if session_id:
                        print("✅")
                        print(f"   Session ID: {session_id}")
                        print(f"   Sales: {data.get('sales_count', 0)}")
                        print(f"   Costs: {data.get('costs_count', 0)}")
                    else:
                        print("❌ No session_id in response")
                        return False
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

        # Test 3: Get session data
        print("3. Session data retrieval...", end=" ")
        try:
            async with session.get(f"{BASE_URL}/api/session/{session_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "sales" in data and "costs" in data:
                        print("✅")
                        print(f"   Retrieved {len(data['sales'])} sales and {len(data['costs'])} costs")
                    else:
                        print("❌ Missing sales or costs in response")
                        return False
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

        # Test 4: Auto-match
        print("4. Auto-match algorithm...", end=" ")
        try:
            payload = {
                "session_id": session_id,
                "threshold": 60
            }
            async with session.post(f"{BASE_URL}/api/auto-match", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    matches = data.get("matches_found", 0)
                    print("✅")
                    print(f"   Found {matches} automatic matches")
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

        # Test 5: Calculate IVA
        print("5. IVA calculation...", end=" ")
        try:
            payload = {
                "session_id": session_id,
                "vat_rate": 23
            }
            async with session.post(f"{BASE_URL}/api/calculate", json=payload) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type', '')
                    if 'application/vnd.openxmlformats' in content_type:
                        excel_data = await resp.read()
                        print("✅")
                        print(f"   Excel file generated: {len(excel_data)} bytes")
                    else:
                        data = await resp.json()
                        print("✅")
                        print(f"   JSON response: {list(data.keys())}")
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

        # Test 6: Analytics endpoints
        print("6. Premium analytics...", end=" ")
        try:
            payload = {
                "session_id": session_id,
                "vat_rate": 23
            }

            # Test executive summary
            async with session.post(f"{BASE_URL}/api/analytics/executive-summary", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "executive_summary" in data:
                        print("✅")
                        print(f"   Analytics working with executive summary")
                    else:
                        print("❌ Missing executive_summary key")
                        return False
                else:
                    print(f"❌ HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ {e}")
            return False

    print("\n🎉 All backend tests passed! Backend is 100% functional!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_backend_api())
    if not success:
        exit(1)