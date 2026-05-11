# HuggingFace Spaces Deployment Guide

## Overview

TILLU is now optimized for deployment on HuggingFace Spaces with a lightweight Streamlit interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HuggingFace Spaces                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Gateway (Streamlit)                           │  │
│  │  - Chat Interface                                    │  │
│  │  - Memory Management                                │  │
│  │  - Tool Browser                                      │  │
│  │  - System Status                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              TILLU Backend (FastAPI)                        │
│  - Conversational AI                                        │
│  - Memory Management                                        │
│  - Tool Execution                                           │
│  - Event Streaming                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Data & Services Layer                          │
│  - Supabase (PostgreSQL + pgvector)                         │
│  - Redis (Caching)                                          │
│  - LLM Providers (Groq, Cerebras, Together, etc.)          │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Steps

### Step 1: Deploy TILLU Backend

First, deploy the TILLU backend to Render or another service:

```bash
# Push to GitHub
git push origin main

# Deploy to Render
# - Create new Web Service
# - Connect GitHub repo
# - Set environment variables (see .env.production)
# - Deploy
```

Get the backend URL (e.g., `https://tillu-backend.onrender.com`)

### Step 2: Deploy TILLU Gateway to HuggingFace Spaces

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in details:
   - **Space name**: `tillu-gateway`
   - **License**: Apache 2.0
   - **SDK**: Streamlit
   - **Visibility**: Public
4. Click "Create Space"
5. In the Space settings, go to "Files and versions"
6. Upload files from `deployments/huggingface/tillu-gateway/`:
   - `app.py`
   - `requirements.txt`
   - `README.md`
7. Go to "Settings" → "Repository secrets"
8. Add secret: `TILLU_API_URL=<your-backend-url>`
9. Space will auto-deploy

### Step 3: Verify Deployment

1. Open the Space URL
2. In sidebar, enter your backend API URL
3. Click "Test Connection"
4. Should see "✅ Connected to TILLU backend"

## Environment Variables

### HuggingFace Spaces

- `TILLU_API_URL` - URL of TILLU backend (e.g., `https://tillu-backend.onrender.com`)

### TILLU Backend (.env.production)

```
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# LLM Providers (Free tier)
GROQ_API_KEY=your-groq-key
CEREBRAS_API_KEY=your-cerebras-key
TOGETHER_API_KEY=your-together-key
GOOGLE_API_KEY=your-google-key
OPENROUTER_API_KEY=your-openrouter-key
CLOUDFLARE_API_TOKEN=your-cf-token
CLOUDFLARE_ACCOUNT_ID=your-cf-account-id

# Redis
REDIS_URL=redis://your-redis-url

# YouTube (optional)
YOUTUBE_API_KEY=your-youtube-key

# Security
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=https://huggingface.co,https://your-domain.com

# Deployment
ENVIRONMENT=production
LOG_LEVEL=info
```

## Memory Optimization

### Removed Dependencies

- ❌ Playwright (browser automation) - 200MB+
- ❌ CrewAI (agent framework) - 100MB+
- ❌ Celery (task queue) - 50MB+
- ❌ APScheduler (scheduling) - 20MB+

### Kept Dependencies

- ✅ FastAPI (web framework) - 10MB
- ✅ LangChain (LLM orchestration) - 30MB
- ✅ Supabase (database client) - 5MB
- ✅ Redis (cache client) - 2MB
- ✅ Streamlit (UI) - 50MB

### Total Memory Usage

- **Backend**: ~150MB (well under 512MB limit)
- **Gateway**: ~100MB (well under HF free tier)
- **Combined**: ~250MB

## Monitoring

### Backend Health

Check backend status:
```bash
curl https://tillu-backend.onrender.com/health
```

Response:
```json
{
  "status": "running",
  "version": "0.1.0",
  "providers": {
    "groq": "available",
    "cerebras": "available",
    "together": "available"
  }
}
```

### Gateway Status

Check gateway in Streamlit UI:
- Go to "Status" tab
- See API connection status
- View system health metrics

## Troubleshooting

### Gateway can't connect to backend

1. Check backend URL in sidebar
2. Verify backend is running: `curl <backend-url>/health`
3. Check CORS settings in backend `.env`
4. Ensure `TILLU_API_URL` is set in HF Spaces secrets

### Out of memory errors

1. Check backend logs: `render.com/dashboard`
2. Verify no heavy dependencies are imported
3. Check Redis connection (may be consuming memory)
4. Consider upgrading to paid tier

### Slow responses

1. Check LLM provider status
2. Verify database connection
3. Check Redis cache hit rate
4. Monitor API response times in backend logs

## Scaling

### Horizontal Scaling

1. **Backend**: Deploy multiple instances on Render
   - Set up load balancer
   - Use Redis for session sharing

2. **Gateway**: Deploy multiple Spaces
   - Each Space is independent
   - All point to same backend

### Vertical Scaling

1. **Backend**: Upgrade Render plan
   - Free: 512MB RAM
   - Paid: 1GB+ RAM

2. **Gateway**: Upgrade HF Spaces
   - Free: 16GB storage, 2GB RAM
   - Paid: More resources

## Cost Analysis

### Free Tier (Current)

- **Backend (Render)**: $0/month (free tier)
- **Gateway (HF Spaces)**: $0/month (free tier)
- **Database (Supabase)**: $0/month (free tier)
- **LLM Providers**: $0/month (free tier)
- **Total**: $0/month

### Paid Tier (Optional)

- **Backend (Render)**: $7/month (starter)
- **Gateway (HF Spaces)**: $0/month (free)
- **Database (Supabase)**: $25/month (pro)
- **LLM Providers**: $0/month (free tier)
- **Total**: $32/month

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy gateway to HuggingFace Spaces
3. ⏳ Set up monitoring and alerts
4. ⏳ Configure custom domain
5. ⏳ Add authentication
6. ⏳ Set up CI/CD pipeline

## References

- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Render Docs](https://render.com/docs)
- [Supabase Docs](https://supabase.com/docs)
