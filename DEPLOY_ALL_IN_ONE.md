# 🚀 All-in-One TILLU Deployment

Complete deployment guide - deploy spaces AND set all environment variables in one command.

---

## ⚡ Quick Start (One Command)

```bash
# Get your HuggingFace token: https://huggingface.co/settings/tokens
# Then run:
python scripts/deploy_tillu_complete.py --token hf_your_token_here
```

This will:
1. ✅ Deploy TILLU Gateway (Streamlit UI)
2. ✅ Deploy TILLU Backend (FastAPI)
3. ✅ Set ALL environment variables for backend
4. ✅ Configure gateway with backend URL

**Time**: 5-10 minutes  
**Cost**: $0/month (free tier)  

---

## Prerequisites

### 1. HuggingFace Account
- Sign up: https://huggingface.co/join
- Get token: https://huggingface.co/settings/tokens
  - Click "New token"
  - Select "Write" access
  - Copy the token

### 2. Install Requirements
```bash
pip install huggingface-hub
```

---

## Step-by-Step Deployment

### Step 1: Get HuggingFace Token (2 minutes)

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "TILLU Deployment"
4. Role: "Write"
5. Click "Generate token"
6. Copy token (starts with `hf_`)

### Step 2: Run Complete Deployment (5 minutes)

```bash
# Windows CMD
python scripts/deploy_tillu_complete.py --token hf_your_token_here

# Windows PowerShell
python scripts/deploy_tillu_complete.py --token hf_your_token_here

# Linux/Mac
python scripts/deploy_tillu_complete.py --token hf_your_token_here
```

### Step 3: Wait for Build (2-5 minutes)

The script will output:
```
✅ Logged in as: your-username

============================================================
TILLU COMPLETE DEPLOYMENT
============================================================

📍 PHASE 1: Deploying Spaces
============================================================

📦 Deploying: TILLU Gateway
   Repo: tillu-AI/tillu-gateway
   ✅ Space exists

📤 Uploading files...
  📤 Uploading streamlit_app.py... ✅
  📤 Uploading requirements.txt... ✅
  📤 Uploading README.md... ✅
  📤 Uploading Dockerfile... ✅

📊 Files: 4/4 uploaded

📦 Deploying: TILLU Backend
   Repo: tillu-AI/tillu-backend
   ✅ Space exists

📤 Uploading files...
  📤 Uploading app.py... ✅
  📤 Uploading requirements.txt... ✅
  📤 Uploading README.md... ✅
  📤 Uploading Dockerfile... ✅

📊 Files: 4/4 uploaded

============================================================
🔐 PHASE 2: Setting Environment Variables
============================================================

📄 Reading from: .env.hf-spaces
📋 Found 45 secrets

🔐 Setting secrets for tillu-AI/tillu-backend...
  ✅ APP_ENV
  ✅ DEBUG
  ✅ SECRET_KEY
  ✅ CORS_ORIGINS
  ✅ SUPABASE_URL
  ✅ SUPABASE_KEY
  ...
  
📊 Secrets: 45 set

🔐 Setting secrets for TILLU Gateway...
  ✅ TILLU_API_URL
  
📊 Secrets: 1 set

============================================================
✅ DEPLOYMENT COMPLETE!
============================================================

🌐 Space URLs:
   • TILLU Gateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway
   • TILLU Backend: https://huggingface.co/spaces/tillu-AI/tillu-backend

🚀 Next Steps:
   1. Wait 2-5 minutes for spaces to build
   2. Test backend: curl https://tillu-ai-tillu-backend.hf.space/health
   3. Open gateway: https://tillu-ai-tillu-gateway.hf.space
   4. Test connection in gateway UI
```

### Step 4: Verify Deployment (2 minutes)

```bash
# Test backend health
curl https://tillu-ai-tillu-backend.hf.space/health

# Expected response:
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "huggingface-spaces"
}
```

### Step 5: Test Gateway (2 minutes)

1. Open: https://tillu-ai-tillu-gateway.hf.space
2. In sidebar, verify API URL: `https://tillu-ai-tillu-backend.hf.space`
3. Click "Test Connection"
4. Should see: ✅ Connected to TILLU backend

---

## What Gets Deployed

### TILLU Gateway (Streamlit UI)
- **Files**: 4 (streamlit_app.py, requirements.txt, README.md, Dockerfile)
- **Port**: 8501
- **Memory**: ~100MB
- **Features**: Chat, Memory, Tools, Status

### TILLU Backend (FastAPI)
- **Files**: 4 (app.py, requirements.txt, README.md, Dockerfile)
- **Port**: 7860
- **Memory**: ~50MB
- **Endpoints**: /health, /api/gateway/chat, /api/memory/*, /api/gateway/tools

### Environment Variables
- **Total**: 45+ secrets
- **Categories**: App, Database, Cache, LLM Providers, Services
- **Security**: Encrypted at rest by HuggingFace

---

## Environment Variables Set

### Application (5)
```
APP_ENV, DEBUG, LOG_LEVEL, SECRET_KEY, CORS_ORIGINS
```

### Database (6)
```
SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, etc.
```

### Cache (3)
```
REDIS_URL, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN
```

### LLM Providers (6 - Free Tier)
```
GROQ_API_KEY, CEREBRAS_API_KEY, GOOGLE_API_KEY, 
OPENROUTER_API_KEY, TOGETHER_API_KEY, HF_TOKEN
```

### Services (20+)
```
Search, News, Google, N8N, Financial, etc.
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HuggingFace Spaces                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Gateway (Streamlit)                           │  │
│  │  https://tillu-ai-tillu-gateway.hf.space             │  │
│  │  Port: 8501 | Memory: ~100MB                         │  │
│  │  Secrets: 1 (TILLU_API_URL)                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Backend (FastAPI)                             │  │
│  │  https://tillu-ai-tillu-backend.hf.space             │  │
│  │  Port: 7860 | Memory: ~50MB                          │  │
│  │  Secrets: 45+ (All environment variables)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │Supabase │          │  Redis  │          │   LLM   │
   │(Postgres)│          │(Upstash)│          │Providers│
   └─────────┘          └─────────┘          └─────────┘
```

---

## Alternative: Individual Commands

### Deploy Only (No Secrets)
```bash
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

### Set Secrets Only
```bash
python scripts/set_hf_secrets.py --token hf_your_token_here --space tillu-AI/tillu-backend
```

### Manual Deployment
See: `MANUAL_DEPLOYMENT.md`

---

## Troubleshooting

### Build Fails
1. Check logs: https://huggingface.co/spaces/tillu-AI/tillu-backend/logs
2. Verify all files uploaded
3. Re-run deployment script

### Secrets Not Set
1. Check: https://huggingface.co/spaces/tillu-AI/tillu-backend/settings
2. Verify HF token has "Write" access
3. Run secrets script separately:
   ```bash
   python scripts/set_hf_secrets.py --token hf_your_token_here --space tillu-AI/tillu-backend
   ```

### Connection Fails
1. Verify backend is running: `curl https://tillu-ai-tillu-backend.hf.space/health`
2. Check CORS_ORIGINS includes gateway URL
3. Check gateway has TILLU_API_URL secret set

### Out of Memory
- Free tier: 2GB RAM per space
- Current usage: ~150MB total
- Should be fine for normal use

---

## Cost Breakdown

| Service | Cost | Tier |
|---------|------|------|
| HuggingFace Spaces (2) | $0/month | Free |
| Supabase | $0/month | Free |
| Upstash Redis | $0/month | Free |
| LLM Providers | $0/month | Free tier |
| **Total** | **$0/month** | **Free** |

---

## URLs

### Production
- **Gateway**: https://tillu-ai-tillu-gateway.hf.space
- **Backend**: https://tillu-ai-tillu-backend.hf.space
- **Backend API Docs**: https://tillu-ai-tillu-backend.hf.space/docs

### Management
- **Gateway Space**: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- **Backend Space**: https://huggingface.co/spaces/tillu-AI/tillu-backend
- **Gateway Settings**: https://huggingface.co/spaces/tillu-AI/tillu-gateway/settings
- **Backend Settings**: https://huggingface.co/spaces/tillu-AI/tillu-backend/settings
- **Gateway Logs**: https://huggingface.co/spaces/tillu-AI/tillu-gateway/logs
- **Backend Logs**: https://huggingface.co/spaces/tillu-AI/tillu-backend/logs

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Get token | 2 min | ⏳ |
| Run script | 5 min | ⏳ |
| Build | 2-5 min | ⏳ |
| Test | 2 min | ⏳ |
| **Total** | **10-15 min** | ✅ |

---

## Support

### Documentation
- **All-in-One Guide**: This file
- **Quick Start**: `DEPLOY_NOW.md`
- **Manual**: `MANUAL_DEPLOYMENT.md`
- **Secrets**: `SET_SECRETS_NOW.md`
- **Full Guide**: `docs/DEPLOYMENT_GUIDE.md`

### Scripts
- **Complete**: `scripts/deploy_tillu_complete.py` (this script)
- **Spaces only**: `scripts/deploy_tillu_spaces.py`
- **Secrets only**: `scripts/set_hf_secrets.py`

### Issues
- GitHub: https://github.com/Heoster/tillu/issues
- Check logs in Space settings
- Review troubleshooting section

---

## Success Checklist

After running the script, verify:
- [ ] Both spaces show in HuggingFace dashboard
- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Gateway loads at URL
- [ ] Gateway shows "✅ Connected to TILLU backend"
- [ ] Chat works in gateway
- [ ] Memory features work
- [ ] Tools are visible
- [ ] Status shows all systems healthy

---

## What's Different from Separate Scripts?

### Before (Multiple Commands)
```bash
# Deploy spaces
python scripts/deploy_tillu_spaces.py --token hf_token

# Then manually set secrets in UI
# Takes 15-30 minutes
```

### Now (One Command)
```bash
# Deploy everything
python scripts/deploy_tillu_complete.py --token hf_token
# Done! Takes 5-10 minutes
```

---

## 🎉 Ready to Deploy?

```bash
python scripts/deploy_tillu_complete.py --token hf_your_token_here
```

**That's it!** Everything is deployed and configured automatically.

---

**Last Updated**: 2026-05-11  
**Version**: 1.0.0  
**Status**: ✅ Ready  
**Time**: 10-15 minutes  
**Cost**: $0/month
