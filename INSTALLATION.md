# RAG Legal Consult System - Installation Guide

## Hướng dẫn cài đặt

### 1. Tạo môi trường ảo (khuyến nghị)
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Cài đặt dependencies

#### Cài đặt đầy đủ:
```bash
pip install -r requirements.txt
```

#### Cài đặt tối thiểu:
```bash
pip install -r requirements-minimal.txt
```

### 3. Cấu hình API Key
- Thay thế API key trong file `src/ingest_pipeline.py` và các file liên quan
- Hoặc tạo file `.env` với:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Chạy hệ thống

#### Xử lý dữ liệu (Vector hóa):
```bash
cd src
python ingest_pipeline.py
```

#### Chạy ứng dụng Streamlit:
```bash
cd streamlit
streamlit run app.py
```

### 5. Cấu trúc thư mục
```
project/
├── src/
│   ├── ingest_pipeline.py    # Xử lý và vector hóa dữ liệu
│   ├── global_setting.py     # Cấu hình đường dẫn
│   └── prompts.py           # Templates prompt
├── data/
│   ├── cache/               # Cache vector database
│   ├── ingestion_storage/   # Tài liệu gốc
│   └── index_storage/       # Index lưu trữ
├── streamlit/               # Web interface
└── requirements.txt         # Dependencies
```

### 6. Thêm dữ liệu mới
1. Thêm file vào `data/ingestion_storage/`
2. Cập nhật `FILES_PATH` trong `global_setting.py`
3. Chạy lại `python ingest_pipeline.py`

### Lưu ý:
- Đảm bảo có kết nối internet để sử dụng Gemini API
- File cache sẽ được cập nhật tự động, không ghi đè dữ liệu cũ
- Kiểm tra quota API key Gemini để tránh vượt giới hạn
