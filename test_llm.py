#!/usr/bin/env python3
# Test script để thấy rõ LLM hoạt động

from query_system import query_vector_database

def test_llm_in_action():
    print("🔬 Testing LLM in RAG System")
    print("=" * 50)
    
    # Test query
    query = "Độ tuổi lao động tối thiểu là bao nhiêu?"
    
    print(f"📝 Question: {query}")
    print("\n🔄 RAG Process:")
    print("1. 🔍 Vector search in Weaviate (Embedding)")
    print("2. 📊 Retrieve top similar chunks") 
    print("3. 🤖 LLM generates answer from context")
    print("4. 📋 Return final response")
    
    print("\n" + "=" * 50)
    
    # Execute query
    result = query_vector_database(query, top_k=3)
    
    if result:
        print("\n✅ LLM successfully generated response from Weaviate context!")
    else:
        print("\n❌ Failed to get LLM response")

if __name__ == "__main__":
    test_llm_in_action()
