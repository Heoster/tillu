# TILLU Deployment Guide - HuggingFace Spaces

Complete guide to deploy TILLU Gateway and Backend to HuggingFace Spaces.

## Prerequisites

1. **HuggingFace Account**: https://huggingface.co
2. **HuggingFace API Token**: https://huggingface.co/settings/tokens
3. **Python 3.8+** with `huggingface_hub` installed:
   ```bash
   pip install huggingface-hub
   ```

## Quick Start (5 minutes)

### Step 1: Get HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Select "Write" access
4. Copy the token

### Step 2: Deploy Spaces

```bash
# Set token (Windows CMD)
set HF_TOKEN=hf_your_token_here

# Or (Windows PowerShell)
$env:HF_TOKEN="hf_your_token_here"

# Or (Linux/Mac)
export HF_TOKEN=hf_your_token_here

# Deploy
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

### Step 3: Wait for Build

Spaces take 2-5 minutes to build. Check status at:
- Gateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- Backend: https://huggingface.co/spaces/tillu-AI/tillu-backend

### Step 4: Test Connection

Once built:

1. **Test Backend API**:
   ```bash
   curl https://tillu-ai-tillu-backend.hf.space/health
   ```
   Expected response:
   ```json
   {"status": "healthy", "version": "0.1.0", "environment": "huggingface-spaces"}
   ```

2. **Open Gateway UI**:
   - URL: https://tillu-ai-tillu-gateway.hf.space
   - In sidebar, enter backend URL: `https://tillu-ai-tillu-backend.hf.space`
   - Click "Test Connection"
   - Should see: ✅ Connected to TILLU backend

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HuggingFace Spaces                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Gateway (Streamlit)                           │  │
│  │  https://tillu-ai-tillu-gateway.hf.space             │  │
│  │                                                       │  │
│  │  - Chat Interface                                    │  │
│  │  - Memory Management                                │  │
│  │  - Tool Browser                                      │  │
│  │  - System Status                                     │  │
│  │                                                       │  │
│  │  Memory: ~100MB                                      │  │
│  │  Port: 8501 (Streamlit)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Backend (FastAPI)                             │  │
│  │  https://tillu-ai-tillu-backend.hf.space             │  │
│  │                                                       │  │
│  │  - Chat API                                          │  │
│  │  - Memory API                                        │  │
│  │  - Tools API                                         │  │
│  │  - Health Check                                      │  │
│  │                                                       │  │
│  │  Memory: ~50MB                                       │  │
│  │  Port: 7860 (HF Spaces default)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Details

### TILLU Gateway (Streamlit)

**Location**: `deployments/huggingface/tillu-gateway/`

**Files**:
- `streamlit_app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies (3 packages)
- `Dockerfile` - Docker configuration
- `README.md` - Space metadata

**Features**:
- 💬 Chat interface with TILLU backend
- 📝 Memory management (store & search)
- 🔧 Tool browser
- 📊 System status monitoring
- 🔗 API connection testing

**Configuration**:
- Port: 8501 (Streamlit default)
- Memory: ~100MB
- Build time: 2-3 minutes

### TILLU Backend (FastAPI)

**Location**: `deployments/huggingface/tillu-backend/`

**Files**:
- `app.py` - FastAPI application
- `requirements.txt` - Python dependencies (5 packages)
- `Dockerfile` - Docker configuration
- `README.md` - Space metadata

**Endpoints**:
- `GET /health` - Health check
- `GET /` - Root endpoint
- `POST /api/gateway/chat` - Chat endpoint
- `POST /api/memory/store` - Store memory
- `GET /api/memory/search` - Search memory
- `GET /api/gateway/tools` - List tools

**Configuration**:
- Port: 7860 (HuggingFace Spaces default)
- Memory: ~50MB
- Build time: 2-3 minutes

## Troubleshooting

### Space won't build

1. Check Space logs: Go to Space → "Logs" tab
2. Common issues:
   - Missing `Dockerfile`
   - Invalid `requirements.txt`
   - Syntax errors in Python files

**Solution**:
```bash
# Re-deploy
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

### Can't connect to backend

1. Verify backend is running:
   ```bash
   curl https://tillu-ai-tillu-backend.hf.space/health
   ```

2. Check gateway logs:
   - Go to Gateway Space → "Logs" tab
   - Look for connection errors

3. Verify backend URL in gateway settings:
   - Open gateway UI
   - Check sidebar for API URL
   - Should be: `https://tillu-ai-tillu-backend.hf.space`

### Slow responses

1. Check backend logs for errors
2. Verify network connectivity
3. Check HuggingFace Spaces status page

### Out of memory

HuggingFace Spaces free tier has:
- 2GB RAM
- 16GB storage

Current usage:
- Gateway: ~100MB
- Backend: ~50MB
- Total: ~150MB

Should be fine for normal use. If issues occur, upgrade to paid tier.

## Manual Deployment (Alternative)

If the script doesn't work, deploy manually:

### 1. Create Spaces

Go to https://huggingface.co/new-space and create:
- `tillu-AI/tillu-gateway` (SDK: Streamlit)
- `tillu-AI/tillu-backend` (SDK: Docker)

### 2. Clone Repos

```bash
git clone https://huggingface.co/spaces/tillu-AI/tillu-gateway
git clone https://huggingface.co/spaces/tillu-AI/tillu-backend
```

### 3. Copy Files

**For Gateway**:
```bash
cp deployments/huggingface/tillu-gateway/streamlit_app.py tillu-gateway/
cp deployments/huggingface/tillu-gateway/requirements.txt tillu-gateway/
cp deployments/huggingface/tillu-gateway/README.md tillu-gateway/
cp deployments/huggingface/tillu-gateway/Dockerfile tillu-gateway/
```

**For Backend**:
```bash
cp deployments/huggingface/tillu-backend/app.py tillu-backend/
cp deployments/huggingface/tillu-backend/requirements.txt tillu-backend/
cp deployments/huggingface/tillu-backend/README.md tillu-backend/
cp deployments/huggingface/tillu-backend/Dockerfile tillu-backend/
```

### 4. Push to HuggingFace

```bash
cd tillu-gateway
git add -A
git commit -m "Deploy TILLU Gateway"
git push

cd ../tillu-backend
git add -A
git commit -m "Deploy TILLU Backend"
git push
```

## Environment Variables

### Gateway

No required environment variables. Optional:
- `TILLU_API_URL` - Backend API URL (default: https://tillu-ai-tillu-backend.hf.space)

### Backend

No required environment variables. Optional:
- `LOG_LEVEL` - Logging level (default: INFO)

## Monitoring

### Check Space Status

1. Go to Space page
2. Click "Logs" tab
3. View real-time logs

### Check API Health

```bash
# Gateway health
curl https://tillu-ai-tillu-gateway.hf.space/_stcore/health

# Backend health
curl https://tillu-ai-tillu-backend.hf.space/health
```

### Monitor Usage

1. Go to Space settings
2. Check "Logs" for resource usage
3. Check "Settings" for storage usage

## Updating Spaces

To update a space after making changes:

```bash
# Update files
cp deployments/huggingface/tillu-gateway/streamlit_app.py tillu-gateway/
cp deployments/huggingface/tillu-backend/app.py tillu-backend/

# Push updates
cd tillu-gateway && git add -A && git commit -m "Update" && git push
cd ../tillu-backend && git add -A && git commit -m "Update" && git push
```

Or use the deployment script:
```bash
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

## Cost

**HuggingFace Spaces Free Tier**:
- 2 free spaces
- 2GB RAM per space
- 16GB storage per space
- CPU-only (no GPU)
- **Cost: $0/month**

**Upgrade to Paid** (if needed):
- $7/month per space (3GB RAM, 50GB storage)
- $15/month per space (16GB RAM, 100GB storage)
- GPU options available

## Support

### Documentation
- GitHub: https://github.com/Heoster/tillu
- Docs: `docs/` folder
- README: `README.md`

### Issues
- Check logs in Space settings
- Review this guide
- Check HuggingFace Spaces documentation

### Contact
- GitHub Issues: https://github.com/Heoster/tillu/issues

## Next Steps

1. ✅ Deploy spaces
2. ✅ Test connection
3. 📝 Add custom domain (optional)
4. 🔐 Add authentication (optional)
5. 📊 Monitor usage
6. 🚀 Share with users

---

**Last Updated**: 2026-05-11
**Status**: ✅ Production Ready
