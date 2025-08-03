import sys
import os

# Thêm đường dẫn đến thư mục gốc của project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import weaviate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import từ thư mục src
from src.global_setting import WEAVIATE_URL, WEAVIATE_CLASS_NAME

def cleanup_cache():
    """Xóa cache files"""
    try:
        cache_file = os.path.join(project_root, "data/cache/pipeline_cache.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("✅ Deleted pipeline cache file")
        else:
            print("📝 Pipeline cache file not found")
            
        # Xóa index storage nếu còn tồn tại
        index_storage = os.path.join(project_root, "data/index_storage")
        if os.path.exists(index_storage):
            import shutil
            shutil.rmtree(index_storage)
            print("✅ Deleted index storage directory")
        else:
            print("📝 Index storage directory not found")
            
    except Exception as e:
        print(f"❌ Error cleaning cache: {e}")

def cleanup_weaviate():
    """Xóa collection trong Weaviate"""
    try:
        # Kết nối Weaviate
        client = weaviate.connect_to_local(host="localhost", port=8080)
        
        if not client.is_ready():
            print("❌ Weaviate is not ready")
            return False
        
        print(f"✓ Connected to Weaviate at {WEAVIATE_URL}")
        
        # Kiểm tra collection có tồn tại không
        if client.collections.exists(WEAVIATE_CLASS_NAME):
            print(f"🗑️ Deleting collection: {WEAVIATE_CLASS_NAME}")
            client.collections.delete(WEAVIATE_CLASS_NAME)
            print(f"✅ Successfully deleted collection: {WEAVIATE_CLASS_NAME}")
        else:
            print(f"📝 Collection {WEAVIATE_CLASS_NAME} not found")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning Weaviate: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_weaviate_collections():
    """Liệt kê tất cả collections trong Weaviate"""
    try:
        client = weaviate.connect_to_local(host="localhost", port=8080)
        
        if not client.is_ready():
            print("❌ Weaviate is not ready")
            return
        
        collections = client.collections.list_all()
        collection_names = [col.name for col in collections.values()]
        
        print(f"📋 Available collections in Weaviate:")
        for name in collection_names:
            collection = client.collections.get(name)
            count = len(list(collection.iterator()))
            print(f"  - {name}: {count} objects")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")

def main():
    print("🧹 RAG System Cleanup Utility")
    print("=" * 40)
    
    print("\nOptions:")
    print("1. Clean cache files only")
    print("2. Clean Weaviate collection only")
    print("3. Clean both cache and Weaviate")
    print("4. List Weaviate collections")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            print("\n🧹 Cleaning cache files...")
            cleanup_cache()
            
        elif choice == '2':
            print("\n🧹 Cleaning Weaviate collection...")
            cleanup_weaviate()
            
        elif choice == '3':
            print("\n🧹 Cleaning both cache and Weaviate...")
            cleanup_cache()
            cleanup_weaviate()
            
        elif choice == '4':
            print("\n📋 Listing Weaviate collections...")
            list_weaviate_collections()
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-5.")
            continue
        
        print("\n" + "-" * 40)

if __name__ == "__main__":
    main()
