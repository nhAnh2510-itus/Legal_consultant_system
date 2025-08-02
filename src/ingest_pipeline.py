import sys
import os

# Thêm đường dẫn đến thư mục gốc của project (thư mục cha của src)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Debug thông tin
print(f"Current file: {__file__}")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files path from global_setting: {os.path.join(project_root, 'data/ingestion_storage/luatlaodong.docx')}")

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI  # Sử dụng Google GenAI LLM
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import Settings
import google.generativeai as genai
import weaviate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import từ thư mục src
from global_setting import STORAGE_PATH, FILES_PATH, CACHE_FILE, WEAVIATE_URL, WEAVIATE_CLASS_NAME
from prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE

# Cấu hình API key từ environment variable
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

genai.configure(api_key=google_api_key)

# Thay vì sử dụng SummaryExtractor (tốn quota), hãy tắt nó đi tạm thời
google_llm = GoogleGenAI(
    model="models/gemini-1.5-flash", 
    api_key=google_api_key,
    temperature=0.1
)

def setup_weaviate_client():
    """Khởi tạo Weaviate client và tạo schema nếu chưa có"""
    try:
        # Sử dụng Weaviate client v4
        client = weaviate.connect_to_local(host="localhost", port=8080)
        
        # Kiểm tra kết nối
        if client.is_ready():
            print(f"✓ Weaviate connected successfully at {WEAVIATE_URL}")
        else:
            raise Exception("Weaviate is not ready")
        
        # Tạo collection nếu chưa có (v4 sử dụng collections thay vì classes)
        from weaviate.classes.config import Configure
        
        if not client.collections.exists(WEAVIATE_CLASS_NAME):
            client.collections.create(
                name=WEAVIATE_CLASS_NAME,
                description="Legal documents for RAG system",
                vectorizer_config=Configure.Vectorizer.none(),  # Chúng ta sẽ tự tạo vector
                properties=[
                    weaviate.classes.config.Property(
                        name="content",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="The main content of the document"
                    ),
                    weaviate.classes.config.Property(
                        name="filename", 
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Name of the source file"
                    ),
                    weaviate.classes.config.Property(
                        name="file_path",
                        data_type=weaviate.classes.config.DataType.TEXT, 
                        description="Path to the source file"
                    ),
                    weaviate.classes.config.Property(
                        name="chunk_id",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Unique identifier for this text chunk"
                    )
                ]
            )
            print(f"✓ Created Weaviate collection: {WEAVIATE_CLASS_NAME}")
        else:
            print(f"✓ Weaviate collection already exists: {WEAVIATE_CLASS_NAME}")
        
        return client
    
    except Exception as e:
        print(f"❌ Error connecting to Weaviate: {e}")
        print("Make sure Weaviate is running on Docker")
        return None

def ingest_documents():
    """Xử lý documents và lưu vào cả cache và Weaviate vector database"""
    
    print("🚀 Starting document ingestion process...")
    
    # 1. Setup Weaviate client
    weaviate_client = setup_weaviate_client()
    # weaviate_client = None  # Tạm thời tắt Weaviate để test nhanh
    
    # 2. Tạo đường dẫn tuyệt đối cho FILES_PATH
    absolute_files_path = []
    for file_path in FILES_PATH:
        if not os.path.isabs(file_path):
            # Nếu là đường dẫn tương đối, thêm project_root vào đầu
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
    
    # 4. Tạo đường dẫn tuyệt đối cho CACHE_FILE
    cache_file_path = os.path.join(project_root, CACHE_FILE) if not os.path.isabs(CACHE_FILE) else CACHE_FILE
    
    try:
        cached_hashes = IngestionCache.from_persist_path(cache_file_path)
        print("💾 Cache file found. Running using cache...")
        print(f"   Cache contains {len(cached_hashes._kvstore.data)} entries")
    except:
        cached_hashes = IngestionCache()
        print("💾 No cache file found. Running without cache...")
    
    # 5. Setup embedding model
    google_embedding = GoogleGenAIEmbedding(
        model_name="models/embedding-001",
        api_key=google_api_key
    )
    
    print("⚙️ Starting pipeline processing...")
    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=20
            ),
            # Tạm thời tắt SummaryExtractor để tránh vượt quota Gemini
            # SummaryExtractor(
            #     summaries=['self'], 
            #     prompt_template=CUSTORM_SUMMARY_EXTRACT_TEMPLATE,
            #     llm=google_llm  # Truyền Google LLM vào SummaryExtractor
            # ),
            google_embedding
        ],
        cache=cached_hashes
    )
    
    nodes = pipeline.run(documents=documents)
    print(f"✓ Processing completed. Generated {len(nodes)} nodes.")
    
    # 6. Lưu cache (cập nhật hoặc tạo mới)
    pipeline.cache.persist(cache_file_path)
    print(f"💾 Cache updated and saved to: {cache_file_path}")
    
    # 7. Lưu vào Weaviate nếu client khả dụng
    if weaviate_client:
        try:
            print("🔗 Setting up Weaviate vector store...")
            vector_store = WeaviateVectorStore(
                weaviate_client=weaviate_client,
                index_name=WEAVIATE_CLASS_NAME,
                text_key="content"
            )
            
            # Tạo storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Tạo VectorStoreIndex và insert data vào Weaviate
            print("📊 Creating vector index and inserting into Weaviate...")
            index = VectorStoreIndex(
                nodes=nodes,
                storage_context=storage_context,
                embed_model=google_embedding
            )
            
            print(f"✅ Successfully saved to Weaviate!")
            print(f"   - Data inserted into Weaviate collection: {WEAVIATE_CLASS_NAME}")
            
            # Kiểm tra số lượng objects trong Weaviate
            try:
                collection = weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
                count = len(list(collection.iterator()))
                print(f"   - Objects in Weaviate: {count}")
            except Exception as e:
                print(f"   - Could not get object count: {e}")
                
        except Exception as e:
            print(f"❌ Error saving to Weaviate: {e}")
            print("   Data was still saved to cache for later use.")
    else:
        print("⚠️ Weaviate not available. Data saved to cache only.")
    
    print("✅ Pipeline completed! Data processed and cached.")
    
    return nodes

# Chạy hàm
if __name__ == "__main__":
    try:
        nodes = ingest_documents()
        print(f"\n🎉 Success! Processed {len(nodes)} nodes into vector database.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

