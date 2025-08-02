# Environment Setup Guide

## Quick Start

### 1. Setup Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the System

```bash
# Ingest documents
python src/ingest_pipeline.py

# Query system
python query_system.py
```

## Security Notes

✅ **What we did:**
- ✅ Moved API key to `.env` file
- ✅ Added `.env` to `.gitignore`
- ✅ Created `.env.example` template
- ✅ Used `python-dotenv` for environment loading
- ✅ Added error handling for missing keys

❌ **Never do this:**
- ❌ Hardcode API keys in source code
- ❌ Commit `.env` files to git
- ❌ Share API keys in plain text
- ❌ Use the same API key for different environments

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |
| `WEAVIATE_URL` | Weaviate database URL | Optional (default: localhost:8080) |
| `WEAVIATE_CLASS_NAME` | Collection name in Weaviate | Optional (default: LegalDocument) |

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"
1. Check if `.env` file exists
2. Check if API key is set in `.env`
3. Make sure `.env` is in project root directory

### Error: "Invalid API key"
1. Verify your API key is correct
2. Check if API key has proper permissions
3. Try generating a new API key

---
**🔒 Your API key is now secure!** 🛡️
