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

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.google import GoogleGenerativeAI  # Sử dụng Google GenerativeAI thay vì Gemini deprecated
from llama_index.core import Settings
import google.generativeai as genai

# Import từ thư mục src
from global_setting import STORAGE_PATH, FILES_PATH, CACHE_FILE
from prompts import CUSTORM_SUMMARY_EXTRACT_TEMPLATE

# Cấu hình API key cho Gemini
genai.configure(api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag")

# Thay vì sử dụng SummaryExtractor (tốn quota), hãy tắt nó đi tạm thời
# gemini_llm = GoogleGenerativeAI(
#     model="gemini-1.5-flash", 
#     api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag",
#     temperature=0.1
# )

def ingest_documents():
    # Load documents, easy but we can't move data or share for another device.
    # Because document id is root file name when our input is a folder.
    
    # Tạo đường dẫn tuyệt đối cho FILES_PATH
    absolute_files_path = []
    for file_path in FILES_PATH:
        if not os.path.isabs(file_path):
            # Nếu là đường dẫn tương đối, thêm project_root vào đầu
            absolute_path = os.path.join(project_root, file_path)
        else:
            absolute_path = file_path
        absolute_files_path.append(absolute_path)
    
    print(f"Loading files from: {absolute_files_path}")
    
    documents = SimpleDirectoryReader(
        input_files=absolute_files_path,
        filename_as_id=True
    ).load_data()
    
    for doc in documents:
        print(doc.id_)
    
    # Tạo đường dẫn tuyệt đối cho CACHE_FILE
    cache_file_path = os.path.join(project_root, CACHE_FILE) if not os.path.isabs(CACHE_FILE) else CACHE_FILE
    
    try:
        cached_hashes = IngestionCache.from_persist_path(cache_file_path)
        print("Cache file found. Running using cache...")
        print(f"Cache contains {len(cached_hashes._kvstore.data)} entries")
    except:
        cached_hashes = ""
        print("No cache file found. Running without cache...")
    
    print("Starting pipeline processing...")
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
            #     llm=gemini_llm  # Truyền Gemini LLM vào SummaryExtractor
            # ),
            GeminiEmbedding(
                model_name="models/embedding-001",
                api_key="AIzaSyBzNVYfLf77NhGDCTlflkd9WC9doqa-5ag"
            )
        ],
        cache=cached_hashes
    )
    
    nodes = pipeline.run(documents=documents)
    print(f"Processing completed. Generated {len(nodes)} nodes.")
    
    # Lưu cache (cập nhật hoặc tạo mới)
    pipeline.cache.persist(cache_file_path)
    print(f"Cache updated and saved to: {cache_file_path}")
    
    return nodes

# Chạy hàm
ingest_documents()