CACHE_FILE = "data/cache/pipeline_cache.json"
CONVERSATION_FILE = "data/cache/chat_history.json" 
STORAGE_PATH = "data/ingestion_storage/"
FILES_PATH = [
    "data/ingestion_storage/luatlaodong.docx", 
    "data/ingestion_storage/test_document.txt",
    "data/ingestion_storage/test_rag_system.txt"
]
INDEX_STORAGE = "data/index_storage"
SCORES_FILE = "data/user_storage/scores.json"

# Weaviate Configuration
WEAVIATE_URL = "http://localhost:8080"
WEAVIATE_CLASS_NAME = "LegalDocument"
WEAVIATE_INDEX_NAME = "legal_docs_index"