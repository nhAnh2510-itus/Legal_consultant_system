import sys
import os

# Thêm đường dẫn đến thư mục gốc của project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from query_system import query_hybrid_search
import time

def test_hybrid_search_simple():
    """Test đơn giản cho hybrid search"""
    
    # Các câu hỏi test
    test_queries = [
        "Thời gian làm việc bình thường là bao nhiêu giờ?", 
        "Nghỉ phép năm được mấy ngày?",
        "Quyền và nghĩa vụ của người lao động là gì?",
        "Những đối tượng nào áp dụng Bộ luật Lao động?",
        "Các hành vi nào bị nghiêm cấm trong lĩnh vực lao động theo Bộ luật?"
    ]
    
    print("� Testing Hybrid Search")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = query_hybrid_search(query, top_k=7, alpha=0.5)
            search_time = time.time() - start_time
            
            if result:
                print(f"⏱️ Time: {search_time:.2f}s")
                print(f"📋 Answer: {result['answer']}")
                # print(f"📊 Found {len(result['sources'])} sources")
                
                # In ra scores của sources
                # for j, source in enumerate(result['sources'], 1):
                #     print(f"   {j}. Score: {source['score']:.4f}")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    print("� RAG System - Hybrid Search Test")
    print("=" * 50)
    
    test_hybrid_search_simple()
    
    print("\n✅ Testing completed!")
