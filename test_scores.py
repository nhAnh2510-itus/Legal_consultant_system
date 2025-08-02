#!/usr/bin/env python3
# Test script để kiểm tra score similarity

import sys
import os
sys.path.append('.')

from query_system import query_vector_database

def test_similarity_scores():
    """Test với các câu hỏi khác nhau để xem score thay đổi như thế nào"""
    
    test_queries = [
        "Độ tuổi lao động tối thiểu là bao nhiêu?",  # Should have high score với test doc
        "Thời gian làm việc bình thường là bao nhiêu giờ?",  # Should match well
        "Nghỉ phép năm được mấy ngày?",  # Should match
        "Quy định về pizza và hamburger",  # Should have low score (irrelevant)
    ]
    
    print("🔬 Testing Similarity Scores")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        result = query_vector_database(query, top_k=3)
        
        if result and hasattr(result, 'source_nodes'):
            print(f"📊 Score Analysis:")
            for j, node in enumerate(result.source_nodes, 1):
                score = node.score
                relevance = "Excellent" if score > 0.8 else "Good" if score > 0.6 else "Fair" if score > 0.4 else "Poor"
                print(f"   {j}. Score: {score:.4f} ({relevance})")
                
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_similarity_scores()
