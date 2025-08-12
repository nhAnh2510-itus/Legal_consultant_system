"""
Simple FastAPI for Legal RAG System
Chỉ sử dụng query_hybrid_search với chỉ số mặc định và trả về answer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import time

# Import existing query functions
try:
    from query_system import query_hybrid_search
    QUERY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import query_system: {e}")
    QUERY_AVAILABLE = False

# FastAPI app
app = FastAPI(
    title="Legal RAG API",
    description="Simple API for legal document search - chỉ trả về answer",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Câu hỏi tìm kiếm")

class SearchResponse(BaseModel):
    query: str
    answer: str
    processing_time: float
    status: str = "success"

# Routes
@app.get("/")
async def root():
    return {
        "message": "Legal RAG API - Simple Version",
        "status": "running" if QUERY_AVAILABLE else "limited",
        "docs": "/docs",
        "description": "Chỉ sử dụng query_hybrid_search với chỉ số mặc định"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy" if QUERY_AVAILABLE else "degraded",
        "query_system_available": QUERY_AVAILABLE,
        "search_method": "query_hybrid_search with default params"
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Main search endpoint - chỉ sử dụng query_hybrid_search và trả về answer"""
    start_time = time.time()
    
    if not QUERY_AVAILABLE:
        processing_time = time.time() - start_time
        return SearchResponse(
            query=request.query,
            answer="Hệ thống tìm kiếm không khả dụng. Vui lòng kiểm tra cấu hình.",
            processing_time=processing_time,
            status="error"
        )
    
    try:
        # Sử dụng query_hybrid_search với các chỉ số mặc định
        response = query_hybrid_search(
            query_text=request.query,
            top_k=5,  # Mặc định
            alpha=0.6  # Mặc định từ query_system.py
        )
        
        processing_time = time.time() - start_time
        
        if response is None:
            return SearchResponse(
                query=request.query,
                answer="Không thể kết nối đến cơ sở dữ liệu. Vui lòng kiểm tra Weaviate đang chạy tại http://localhost:8080",
                processing_time=processing_time,
                status="error"
            )
        
        # Chỉ lấy answer từ response
        answer = response.get('answer', 'Không tìm thấy thông tin liên quan đến câu hỏi của bạn.')
        
        return SearchResponse(
            query=request.query,
            answer=answer,
            processing_time=processing_time,
            status="success"
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return SearchResponse(
            query=request.query,
            answer=f"Lỗi trong quá trình tìm kiếm: {str(e)}",
            processing_time=processing_time,
            status="error"
        )

@app.get("/test")
async def test():
    """Test endpoint để kiểm tra query_hybrid_search"""
    if not QUERY_AVAILABLE:
        return {"error": "Query system not available"}
    
    try:
        result = query_hybrid_search("thời gian làm việc", top_k=2, alpha=0.6)
        return {
            "status": "success",
            "result_type": type(result).__name__,
            "has_answer": 'answer' in result if result else False,
            "test_query": "thời gian làm việc"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Legal RAG API...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Search endpoint: POST http://localhost:8000/search")
    print("💡 Chỉ sử dụng query_hybrid_search với top_k=5, alpha=0.6")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
