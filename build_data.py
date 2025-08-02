import sys
import os

# Thêm đường dẫn đến thư mục gốc của project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.google import GoogleGenerativeAI
import weaviate
import google.generativeai as genai

# Import từ thư mục src
from src.global_setting import (
    STORAGE_PATH, FILES_PATH, CACHE_FILE, 
    WEAVIATE_URL, WEAVIATE_CLASS_NAME, WEAVIATE_INDEX_NAME, INDEX_STORAGE
)
from src.prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE

# Cấu hình API key cho Gemini
genai.configure(api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag")

def setup_weaviate_client():
    """Khởi tạo Weaviate client và tạo schema nếu chưa có"""
    try:
        client = weaviate.Client(WEAVIATE_URL)
        
        # Kiểm tra kết nối
        if client.is_ready():
            print(f"✓ Weaviate connected successfully at {WEAVIATE_URL}")
        else:
            raise Exception("Weaviate is not ready")
        
        # Tạo schema nếu chưa có
        schema = {
            "class": WEAVIATE_CLASS_NAME,
            "description": "Legal documents for RAG system",
            "vectorizer": "none",  # Chúng ta sẽ tự tạo vector
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The main content of the document"
                },
                {
                    "name": "filename",
                    "dataType": ["string"],
                    "description": "Name of the source file"
                },
                {
                    "name": "file_path",
                    "dataType": ["string"],
                    "description": "Path to the source file"
                },
                {
                    "name": "chunk_id",
                    "dataType": ["string"],
                    "description": "Unique identifier for this text chunk"
                },
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "Summary of the content (if available)"
                }
            ]
        }
        
        # Kiểm tra xem class đã tồn tại chưa
        existing_schema = client.schema.get()
        class_exists = any(cls['class'] == WEAVIATE_CLASS_NAME for cls in existing_schema.get('classes', []))
        
        if not class_exists:
            client.schema.create_class(schema)
            print(f"✓ Created Weaviate class: {WEAVIATE_CLASS_NAME}")
        else:
            print(f"✓ Weaviate class already exists: {WEAVIATE_CLASS_NAME}")
        
        return client
    
    except Exception as e:
        print(f"❌ Error connecting to Weaviate: {e}")
        print("Make sure Weaviate is running on Docker:")
        print("docker run -d --name weaviate -p 8080:8080 -e QUERY_DEFAULTS_LIMIT=25 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' cr.weaviate.io/semitechnologies/weaviate:1.23.1")
        raise

def build_vector_database():
    """Xây dựng vector database từ documents và lưu vào Weaviate"""
    
    print("🚀 Starting Vector Database Build Process...")
    
    # 1. Khởi tạo Weaviate client
    weaviate_client = setup_weaviate_client()
    
    # 2. Tạo đường dẫn tuyệt đối cho FILES_PATH
    absolute_files_path = []
    for file_path in FILES_PATH:
        if not os.path.isabs(file_path):
            absolute_path = os.path.join(project_root, file_path)
        else:
            absolute_path = file_path
        absolute_files_path.append(absolute_path)
    
    print(f"📁 Loading files from: {absolute_files_path}")
    
    # 3. Load documents
    documents = SimpleDirectoryReader(
        input_files=absolute_files_path,
        filename_as_id=True
    ).load_data()
    
    print(f"📄 Loaded {len(documents)} documents:")
    for doc in documents:
        print(f"  - {doc.id_}")
    
    # 4. Thiết lập cache
    cache_file_path = os.path.join(project_root, CACHE_FILE) if not os.path.isabs(CACHE_FILE) else CACHE_FILE
    
    try:
        cached_hashes = IngestionCache.from_persist_path(cache_file_path)
        print("💾 Cache file found. Running with cache...")
        print(f"   Cache contains {len(cached_hashes._kvstore.data)} entries")
    except:
        cached_hashes = IngestionCache()
        print("💾 No cache file found. Creating new cache...")
    
    # 5. Thiết lập LLM và Embedding
    gemini_llm = GoogleGenerativeAI(
        model="gemini-1.5-flash", 
        api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag",
        temperature=0.1
    )
    
    gemini_embedding = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag"
    )
    
    # 6. Tạo pipeline xử lý
    print("⚙️ Setting up ingestion pipeline...")
    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=20
            ),
            SummaryExtractor(
                summaries=['self'], 
                prompt_template=CUSTORM_SUMMARY_EXTRACT_TEMPLATE,
                llm=gemini_llm
            ),
            gemini_embedding
        ],
        cache=cached_hashes
    )
    
    # 7. Xử lý documents thành nodes
    print("🔄 Processing documents...")
    nodes = pipeline.run(documents=documents)
    print(f"✓ Generated {len(nodes)} nodes")
    
    # 8. Lưu cache
    pipeline.cache.persist(cache_file_path)
    print(f"💾 Cache saved to: {cache_file_path}")
    
    # 9. Thiết lập Weaviate Vector Store
    print("🔗 Setting up Weaviate vector store...")
    vector_store = WeaviateVectorStore(
        weaviate_client=weaviate_client,
        index_name=WEAVIATE_CLASS_NAME,
        text_key="content"
    )
    
    # 10. Tạo storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 11. Tạo VectorStoreIndex và lưu vào Weaviate
    print("📊 Creating vector index and inserting into Weaviate...")
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=gemini_embedding
    )
    
    # 12. Lưu index để sử dụng sau
    index_storage_path = os.path.join(project_root, INDEX_STORAGE)
    os.makedirs(index_storage_path, exist_ok=True)
    index.storage_context.persist(persist_dir=index_storage_path)
    
    print(f"✅ Vector database build completed!")
    print(f"   - Total nodes: {len(nodes)}")
    print(f"   - Weaviate class: {WEAVIATE_CLASS_NAME}")
    print(f"   - Index saved to: {index_storage_path}")
    
    # 13. Kiểm tra dữ liệu trong Weaviate
    try:
        result = weaviate_client.query.aggregate(WEAVIATE_CLASS_NAME).with_meta_count().do()
        count = result['data']['Aggregate'][WEAVIATE_CLASS_NAME][0]['meta']['count']
        print(f"   - Objects in Weaviate: {count}")
    except Exception as e:
        print(f"   - Could not get object count: {e}")
    
    return index

if __name__ == "__main__":
    try:
        index = build_vector_database()
        print("\n🎉 Success! Vector database is ready for queries.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
