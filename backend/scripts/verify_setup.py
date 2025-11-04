"""
Verification script to test API endpoints
Run this after starting the server to verify everything works
"""

import asyncio
import httpx
import sys
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0


async def test_endpoint(client: httpx.AsyncClient, name: str, method: str, url: str, **kwargs) -> bool:
    """Test a single endpoint"""
    try:
        response = await client.request(method, url, **kwargs)
        status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
        print(f"{status} | {method} {url} | Status: {response.status_code}")
        return response.status_code < 400
    except Exception as e:
        print(f"❌ FAIL | {method} {url} | Error: {str(e)}")
        return False


async def main():
    """Run all verification tests"""
    print("=" * 70)
    print("Solar Site Analyzer API - Verification Tests")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}\n")
    
    results = []
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test 1: Health check
        print("1. Health Check Endpoint")
        results.append(await test_endpoint(
            client, "Health Check", "GET", f"{BASE_URL}/health"
        ))
        
        # Test 2: Root endpoint
        print("\n2. Root Endpoint")
        results.append(await test_endpoint(
            client, "Root", "GET", f"{BASE_URL}/"
        ))
        
        # Test 3: Get all sites
        print("\n3. GET /api/sites (List all sites)")
        results.append(await test_endpoint(
            client, "List Sites", "GET", f"{BASE_URL}/api/sites?limit=5"
        ))
        
        # Test 4: Get sites with filters
        print("\n4. GET /api/sites (With filters)")
        results.append(await test_endpoint(
            client, "Filtered Sites", "GET", 
            f"{BASE_URL}/api/sites?min_score=70&max_score=100&limit=10"
        ))
        
        # Test 5: Get specific site
        print("\n5. GET /api/sites/1 (Specific site)")
        results.append(await test_endpoint(
            client, "Site Detail", "GET", f"{BASE_URL}/api/sites/1"
        ))
        
        # Test 6: Get statistics
        print("\n6. GET /api/statistics")
        results.append(await test_endpoint(
            client, "Statistics", "GET", f"{BASE_URL}/api/statistics"
        ))
        
        # Test 7: Export as JSON
        print("\n7. GET /api/export (JSON format)")
        results.append(await test_endpoint(
            client, "Export JSON", "GET", 
            f"{BASE_URL}/api/export?format=json&min_score=80"
        ))
        
        # Test 8: Export as CSV
        print("\n8. GET /api/export (CSV format)")
        results.append(await test_endpoint(
            client, "Export CSV", "GET", 
            f"{BASE_URL}/api/export?format=csv&min_score=80"
        ))
        
        # Test 9: Custom analysis
        print("\n9. POST /api/analyze (Custom weights)")
        results.append(await test_endpoint(
            client, "Custom Analysis", "POST", f"{BASE_URL}/api/analyze",
            json={
                "weights": {
                    "solar": 0.4,
                    "area": 0.3,
                    "grid_distance": 0.15,
                    "slope": 0.1,
                    "infrastructure": 0.05
                }
            }
        ))
        
        # Test 10: API documentation
        print("\n10. API Documentation")
        results.append(await test_endpoint(
            client, "Swagger Docs", "GET", f"{BASE_URL}/docs"
        ))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! API is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
