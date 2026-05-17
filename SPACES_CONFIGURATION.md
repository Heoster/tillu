# 🌐 TILLU AI — HuggingFace Spaces Configuration

**Status**: ✅ Configured with correct URLs  
**Date**: 2026-05-11  
**Updated**: Environment variables fixed

---

## 📊 Spaces Overview

### ✅ Working Spaces (Production Ready)

#### 1. **TILLU Gateway** (Streamlit)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- **Purpose**: Main user interface
- **Features**: Chat, Memory, Tools, Status
- **Implementation**: `deployments/huggingface/tillu-gateway/streamlit_app.py`
- **Status**: ✅ Deployed and working

#### 2. **TILLU Embedding** (Gradio)
- **URL**: https://tillu-ai-tillu-ai.hf.space
- **Purpose**: Semantic embeddings API
- **Features**: 768-dim embeddings, emotion detection, similarity scoring
- **Implementation**: `deployments/huggingface/embedding-space.py`
- **Models**:
  - `sentence-transformers/all-mpnet-base-v2` (embeddings)
  - `j-hartmann/emotion-english-distilroberta-base` (emotion)
- **Status**: ✅ Deployed and working

#### 3. **TILLU WebSearch** (FastAPI)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-websearch
- **Purpose**: Web search + content scraping + AI summarization
- **Features**:
  - Search: SearXNG → DDG → Google → Bing → Groq fallback
  - Scraping: Playwright + BeautifulSoup
  - Summarization: Groq 70B
  - Rate limiting: 120 req/60s
  - Language detection: Hindi/English
- **Implementation**: `deployments/huggingface/websearch-space/main.py`
- **Endpoints**:
  - `POST /search` - Basic search
  - `POST /search-and-scrape` - Search + content extraction
  - `POST /intelligence` - Full JARVIS mode
  - `POST /scrape` - Standalone URL scraping
  - `GET /stats` - Service statistics
- **Status**: ✅ Deployed and working

#### 4. **TILLU AI** (Gradio)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-ai
- **Purpose**: Main AI interface
- **Status**: ✅ Deployed and working

---

### ⚠️ Placeholder Spaces (Need Implementation)

#### 1. **TILLU Search** (SearXNG)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-search
- **Purpose**: Meta-search engine
- **Status**: ❌ Placeholder (use WebSearch instead)
- **Fix**: Deploy SearXNG Docker image

#### 2. **TILLU Engine** (n8n)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-engine
- **Purpose**: Workflow automation
- **Status**: ❌ Placeholder (needs n8n + workflows)
- **Fix**: Deploy n8n with WF-01 + WF-02
- **Workflows**:
  - WF-01: Message Router (webhook-based)
  - WF-02: Morning Intelligence Brief (scheduled)

#### 3. **TILLU Daemon** (Background Tasks)
- **URL**: https://huggingface.co/spaces/tillu-AI/tillu-daemon
- **Purpose**: 16 async background loops
- **Status**: ❌ Placeholder (needs daemon implementation)
- **Fix**: Deploy FastAPI + daemon loops
- **Loops**: 16 concurrent async tasks

---

## 🔗 Environment Variables (Updated)

### Correct URLs in `.env`

```bash
# EMBEDDING SPACE (Working)
HF_EMBEDDING_SPACE_URL=https://tillu-ai-tillu-ai.hf.space

# SEARCH SPACES (Working)
WEBSEARCH_URL=https://huggingface.co/spaces/tillu-AI/tillu-websearch
SEARXNG_URL=https://codeex123-tillu-searxng.hf.space

# ENGINE (Placeholder - needs n8n)
N8N_WEBHOOK_URL=https://tillu-ai-tillu-engine.hf.space/webhook
N8N_URL=https://tillu-ai-tillu-engine.hf.space

# DAEMON (Placeholder - needs implementation)
# No specific URL yet - runs as background service
```

---

## 🔄 Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HuggingFace Spaces                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Gateway (Streamlit)                           │  │
│  │  https://huggingface.co/spaces/tillu-AI/tillu-gateway│  │
│  │  - Chat Interface                                    │  │
│  │  - Memory Management                                │  │
│  │  - Tool Browser                                      │  │
│  │  - System Status                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Embedding (Gradio)                            │  │
│  │  https://tillu-ai-tillu-ai.hf.space                  │  │
│  │  - Semantic embeddings (768-dim)                     │  │
│  │  - Emotion detection                                 │  │
│  │  - Similarity scoring                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU WebSearch (FastAPI)                           │  │
│  │  https://huggingface.co/spaces/tillu-AI/tillu-websearch
│  │  - Web search (SearXNG + fallbacks)                  │  │
│  │  - Content scraping (Playwright)                     │  │
│  │  - AI summarization (Groq 70B)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Engine (n8n) [PLACEHOLDER]                    │  │
│  │  https://huggingface.co/spaces/tillu-AI/tillu-engine │  │
│  │  - Message router (WF-01)                            │  │
│  │  - Morning brief (WF-02)                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓ httpx                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TILLU Daemon (FastAPI) [PLACEHOLDER]                │  │
│  │  https://huggingface.co/spaces/tillu-AI/tillu-daemon │  │
│  │  - 16 async background loops                         │  │
│  │  - Event publishing (Redis)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓ httpx
┌─────────────────────────────────────────────────────────────┐
│              TILLU Backend (Render)                         │
│  https://tillu-backend.onrender.com                         │
│                                                             │
│  - Conversational AI                                        │
│  - Memory Management                                        │
│  - Tool Execution                                           │
│  - Event Streaming                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Data & Services Layer                          │
│  - Supabase (PostgreSQL + pgvector)                         │
│  - Redis (Caching + Pub/Sub)                                │
│  - LLM Providers (7 providers, 27 models)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 How Each Space Works

### 1. Gateway (Streamlit)
```
User → Streamlit UI → httpx → Backend API
                   ↓
            Embedding Space (for vectors)
            WebSearch Space (for search)
            Engine Space (for workflows)
```

### 2. Embedding (Gradio)
```
Text Input → Sentence-Transformers → 768-dim Vector
          ↓
    Emotion Detection (7 classes)
    Similarity Scoring
    Language Detection
```

### 3. WebSearch (FastAPI)
```
Query → SearXNG (primary)
     ↓ (if fails)
     DDG JSON (fallback 1)
     ↓ (if fails)
     DDG HTML (fallback 2)
     ↓ (if fails)
     Google Lite (fallback 3)
     ↓ (if fails)
     Bing (fallback 4)
     ↓ (if fails)
     Groq Knowledge (last resort)
     
Results → Scraping (Playwright) → Content Extraction → AI Summarization
```

### 4. Engine (n8n) [PLACEHOLDER]
```
Message → Webhook → Normalize Input
                 ↓
         Parallel Processing:
         - Fetch Recent Memory
         - Semantic Memory Search
         - Classify Intent
         - Detect Emotion
                 ↓
         Brain Router (select chain)
                 ↓
         Execute Chain (LangChain)
                 ↓
         Personality Compiler
                 ↓
         Response + Async Tasks:
         - Store Memory
         - Embed + Index
         - Self-Critique
```

### 5. Daemon (FastAPI) [PLACEHOLDER]
```
16 Concurrent Loops:
1. Heartbeat (60s)
2. Financial Watcher (15m)
3. Web Change Detector (30m)
4. News Urgency Scanner (10m)
5. Pattern Recognition (1h)
6. Context Pre-Computer (1h)
7. Rate Limit Tracker (5m)
8. Free Tier Governor (1h)
9. Goal Probability Engine (6h)
10. Emotion Trend Tracker (30m)
11. Relationship Monitor (6h)
12. Email Monitor (30m)
13. Calendar Monitor (1h)
14. Memory Consolidation (24h)
15. Personality Evolution (7d)
16. Ambient Monitoring (30m)

All loops → Redis Pub/Sub → Events
```

---

## 📋 Configuration Checklist

### Environment Variables
- [x] `HF_EMBEDDING_SPACE_URL` = `https://tillu-ai-tillu-ai.hf.space`
- [x] `WEBSEARCH_URL` = `https://huggingface.co/spaces/tillu-AI/tillu-websearch`
- [x] `SEARXNG_URL` = `https://codeex123-tillu-searxng.hf.space`
- [x] `N8N_WEBHOOK_URL` = `https://tillu-ai-tillu-engine.hf.space/webhook`
- [x] `N8N_URL` = `https://tillu-ai-tillu-engine.hf.space`

### Space Deployments
- [x] Gateway (Streamlit) - Working
- [x] Embedding (Gradio) - Working
- [x] WebSearch (FastAPI) - Working
- [ ] Engine (n8n) - Needs deployment
- [ ] Daemon (FastAPI) - Needs deployment
- [ ] Search (SearXNG) - Needs deployment

### Testing
- [ ] Test Gateway: Visit https://huggingface.co/spaces/tillu-AI/tillu-gateway
- [ ] Test Embedding: `curl https://tillu-ai-tillu-ai.hf.space/health`
- [ ] Test WebSearch: `curl https://huggingface.co/spaces/tillu-AI/tillu-websearch/health`
- [ ] Test Engine: `curl https://huggingface.co/spaces/tillu-AI/tillu-engine/health`
- [ ] Test Daemon: `curl https://huggingface.co/spaces/tillu-AI/tillu-daemon/health`

---

## 🚀 Deployment Instructions

### For Working Spaces (No Action Needed)
- Gateway, Embedding, WebSearch are already deployed
- Just verify they're accessible

### For Placeholder Spaces (Need Deployment)

#### Deploy Engine (n8n)
```bash
cd deployments/huggingface/n8n-space
# Deploy Docker image
# Import workflows:
#   - n8n/workflows/message-router.json
#   - n8n/workflows/morning-intelligence-brief.json
```

#### Deploy Daemon
```bash
cd deployments/huggingface/daemon-space
# Deploy Docker image
# Uses: daemon/core.py + daemon/hf_runner.py
```

#### Deploy Search (SearXNG)
```bash
cd deployments/huggingface/searxng-space
# Deploy SearXNG Docker image
```

---

## 📞 Support

### Quick Links
- Gateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- Embedding: https://tillu-ai-tillu-ai.hf.space
- WebSearch: https://huggingface.co/spaces/tillu-AI/tillu-websearch
- GitHub: https://github.com/Heoster/tillu

### Troubleshooting
- Check `.env` for correct URLs
- Verify space is "Running" status
- Check space logs for errors
- Test connectivity: `curl <space-url>/health`

---

## 📝 Files Reference

### Configuration
- `.env` - Environment variables (updated)
- `app/config.py` - Configuration settings

### Implementations
- `deployments/huggingface/tillu-gateway/streamlit_app.py` - Gateway UI
- `deployments/huggingface/embedding-space.py` - Embedding API
- `deployments/huggingface/websearch-space/main.py` - WebSearch API
- `deployments/huggingface/n8n-space/Dockerfile` - Engine (n8n)
- `deployments/huggingface/daemon-space/` - Daemon (FastAPI)

### Workflows
- `n8n/workflows/message-router.json` - WF-01
- `n8n/workflows/morning-intelligence-brief.json` - WF-02

### Daemon
- `daemon/core.py` - 16 async loops
- `daemon/hf_runner.py` - FastAPI + daemon runner

---

**Status**: ✅ Configuration complete  
**Last Updated**: 2026-05-11  
**Version**: 1.0.0

