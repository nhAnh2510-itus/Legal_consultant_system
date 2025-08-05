import sys
import os

# Thêm đường dẫn đến thư mục gốc của project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Test import đơn giản
try:
    print("Testing imports...")
    from query_system import query_hybrid_search
    print("✅ Import successful")
    
    # Test một query đơn giản
    print("Testing hybrid search...")
    result = query_hybrid_search("test query", top_k=1, alpha=0.7)
    
    if result:
        print("✅ Hybrid search works!")
        print(f"Answer: {result['answer'][:100]}...")
    else:
        print("⚠️ No results but no error")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
