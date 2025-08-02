# Hướng dẫn chạy Weaviate với Docker

## 1. Chạy Weaviate container
```bash
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-transformers' \
  cr.weaviate.io/semitechnologies/weaviate:1.23.1
```

## 2. Kiểm tra Weaviate running
```bash
docker ps | grep weaviate
curl http://localhost:8080/v1/meta
```

## 3. Cài đặt dependencies
```bash
pip install weaviate-client==4.4.0
pip install llama-index-vector-stores-weaviate==0.1.9
```

## 4. Chạy ingestion pipeline
```bash
cd src
python ingest_pipeline.py
```

## 5. Test query system
```bash
python query_system.py
```

## Troubleshooting

### Nếu Weaviate không start:
```bash
docker stop weaviate
docker rm weaviate
docker run -d --name weaviate -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true cr.weaviate.io/semitechnologies/weaviate:1.23.1
```

### Kiểm tra logs:
```bash
docker logs weaviate
```

### Reset data:
```bash
docker stop weaviate
docker rm weaviate
# Chạy lại container mới
```
