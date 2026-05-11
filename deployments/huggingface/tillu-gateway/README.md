# TILLU Gateway - HuggingFace Spaces

Streamlit-based web interface for TILLU backend, deployed on HuggingFace Spaces.

## Features

- 💬 **Chat Interface** - Conversational AI with TILLU
- 📝 **Memory Management** - Store and search semantic memories
- 🔧 **Tool Browser** - Explore available tools
- 📊 **System Status** - Monitor API health

## Deployment

### Option 1: Deploy to HuggingFace Spaces

1. Create a new Space on HuggingFace
2. Select "Streamlit" as the SDK
3. Upload this directory
4. Set environment variable: `TILLU_API_URL=<your-tillu-backend-url>`

### Option 2: Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then set the API URL in the sidebar to point to your TILLU backend.

## Configuration

Set these environment variables:

- `TILLU_API_URL` - URL of TILLU backend API (default: http://localhost:8000)

## Architecture

```
HuggingFace Spaces (Streamlit UI)
         ↓
    httpx client
         ↓
TILLU Backend API (FastAPI)
         ↓
Supabase + Redis + LLM Providers
```

## Memory Usage

- **Streamlit**: ~50MB
- **httpx**: ~5MB
- **Total**: ~100MB (well under HF free tier limit)

## Notes

- No heavy dependencies (no Playwright, CrewAI, Celery)
- Lightweight and fast
- Suitable for free tier deployment
- Requires TILLU backend to be running
