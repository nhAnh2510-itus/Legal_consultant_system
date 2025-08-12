"""
Test script for Legal RAG API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test the API endpoints"""
    
    print("🧪 Testing Legal RAG API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test stats
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"✅ Stats: {response.json()}")
    except Exception as e:
        print(f"❌ Stats failed: {e}")
    
    # Test hybrid search
    try:
        search_data = {
            "query": "thời gian làm việc",
            "top_k": 3,
            "use_hybrid": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/hybrid-search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hybrid search successful:")
            print(f"   Query: {result['query']}")
            print(f"   Results: {result['total_results']}")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            
            for i, res in enumerate(result['results'][:2]):
                print(f"   Result {i+1}: {res['source']} (score: {res['score']:.2f})")
                print(f"     Content: {res['content'][:100]}...")
        else:
            print(f"❌ Hybrid search failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Hybrid search error: {e}")

if __name__ == "__main__":
    test_api()
