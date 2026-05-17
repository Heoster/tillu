# 🔧 TILLU AI — Fix HuggingFace Spaces Deployment

**Status**: Fixing placeholder spaces with actual implementations  
**Date**: 2026-05-11

---

## 📋 Problem Analysis

The following spaces have placeholder/fake implementations and need to be replaced with actual working code:

1. ❌ **tillu-search** - Placeholder (needs WebSearch implementation)
2. ❌ **tillu-engine** - Placeholder (needs n8n integration)
3. ❌ **tillu-embedding** - Placeholder (needs actual embedding model)
4. ❌ **tillu-daemon** - Placeholder (needs 16 async loops)

**Actual Implementations Already Exist**:
- ✅ **tillu-websearch** - `https://huggingface.co/spaces/tillu-AI/tillu-websearch` (FastAPI + SearXNG)
- ✅ **tillu-ai** - Main AI space
- ✅ **tillu-gateway** - Streamlit UI (working)
- ✅ **tillu-embedding** - `https://tillu-ai-tillu-ai.hf.space` (Gradio + sentence-transformers)

---

## 🔗 Correct Space URLs

### Primary Spaces (Working)
```
Gateway (Streamlit):
  https://huggingface.co/spaces/tillu-AI/tillu-gateway

Embedding (Gradio):
  https://tillu-ai-tillu-ai.hf.space
  OR
  https://huggingface.co/spaces/tillu-AI/tillu-embedding

WebSearch (FastAPI):
  https://huggingface.co/spaces/tillu-AI/tillu-websearch

Main AI (Gradio):
  https://huggingface.co/spaces/tillu-AI/tillu-ai
```

### Secondary Spaces (Need Fixing)
```
Engine (n8n):
  https://huggingface.co/spaces/tillu-AI/tillu-engine
  (Currently: placeholder)
  (Should be: n8n instance with WF-01 + WF-02)

Daemon (Background Tasks):
  https://huggingface.co/spaces/tillu-AI/tillu-daemon
  (Currently: placeholder)
  (Should be: FastAPI + 16 async loops)

Search (SearXNG):
  https://huggingface.co/spaces/tillu-AI/tillu-search
  (Currently: placeholder)
  (Should be: SearXNG instance)
```

---

## ✅ Solution: Update Environment Variables

The `.env` file already has the correct URLs for the working spaces:

```bash
# CORRECT URLS (Already in .env)
HF_EMBEDDING_SPACE_URL=https://tillu-ai-tillu-ai.hf.space
SEARXNG_URL=https://codeex123-tillu-searxng.hf.space
WEBSEARCH_URL=https://tillu-AI-tillu-websearch.hf.space
N8N_WEBHOOK_URL=https://tillu-ai-tillu-engine.hf.space/webhook
N8N_URL=https://tillu-ai-tillu-engine.hf.space
```

---

## 🚀 Fix Strategy

### Option 1: Use Existing Working Spaces (Recommended)
The actual implementations are already deployed. Just update the deployment configuration to point to them:

```bash
# Update .env to use working spaces
HF_EMBEDDING_SPACE_URL=https://tillu-ai-tillu-ai.hf.space
WEBSEARCH_URL=https://huggingface.co/spaces/tillu-AI/tillu-websearch
SEARXNG_URL=https://codeex123-tillu-searxng.hf.space
```

### Option 2: Deploy Actual Implementations
Replace placeholder spaces with real code:

1. **tillu-search** → Deploy SearXNG instance
2. **tillu-engine** → Deploy n8n with workflows
3. **tillu-daemon** → Deploy FastAPI + daemon loops
4. **tillu-embedding** → Deploy Gradio + models

---

## 📝 Implementation Files

### 1. WebSearch Space (Already Working)
**File**: `deployments/huggingface/websearch-space/main.py`
**Features**:
- SearXNG integration
- 5-engine fallback chain (SearXNG → DDG → Google → Bing → Groq)
- Content scraping (Playwright + BeautifulSoup)
- AI summarization (Groq 70B)
- Rate limiting (120 req/60s)
- Language detection (Hindi/English)

**Endpoints**:
- `POST /search` - Basic search
- `POST /search-and-scrape` - Search + content extraction
- `POST /intelligence` - Full JARVIS mode (search + scrape + summarize)
- `POST /scrape` - Standalone URL scraping
- `GET /stats` - Service statistics

### 2. Engine Space (n8n)
**File**: `n8n/workflows/message-router.json` + `morning-intelligence-brief.json`
**Features**:
- Message router with intent classification
- Parallel memory fetching + semantic search
- Emotion detection + stress level
- Chain selection (empathy/research/react_agent/analysis/conversational)
- Personality compiler
- Async memory storage + embedding

**Workflows**:
- WF-01: Message Router (webhook-based)
- WF-02: Morning Intelligence Brief (scheduled daily 07:00)

### 3. Daemon Space
**File**: `daemon/core.py`
**Features**:
- 16 concurrent async loops
- Self-restart on exception
- State tracking in database
- Redis pub/sub for events
- Exponential backoff for errors

**Loops**:
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

### 4. Embedding Space (Already Working)
**File**: `deployments/huggingface/embedding-space.py`
**Features**:
- Sentence embeddings (768-dim)
- Emotion detection (7 classes)
- Language detection (Hindi/English)
- Similarity scoring
- Batch processing

**Models**:
- `sentence-transformers/all-mpnet-base-v2` (768-dim)
- `j-hartmann/emotion-english-distilroberta-base` (emotion)
- Unicode script analysis (language detection)

---

## 🔄 Integration Points

### Search Tools
```python
# app/tools/search_tools.py
WebSearchTool → POST /search
IntelligenceTool → POST /intelligence
ScrapePageTool → POST /scrape
```

### Research Agent
```python
# app/langgraph/research_agent.py
7-node LangGraph workflow:
PLAN → SEARCH → SCRAPE → EXTRACT → SYNTHESIZE → CRITIQUE → STORE
```

### Gateway Integration
```python
# app/api/gateway.py
/api/v1/message → n8n WF-01 webhook
/api/v1/stream → Redis SSE events
```

### Daemon Integration
```python
# daemon/hf_runner.py
FastAPI health server (port 7860)
+ 16 async daemon loops
```

---

## 📊 Deployment Status

| Space | Type | Status | URL | Implementation |
|-------|------|--------|-----|-----------------|
| **Gateway** | Streamlit | ✅ Working | https://huggingface.co/spaces/tillu-AI/tillu-gateway | `tillu-gateway/streamlit_app.py` |
| **Embedding** | Gradio | ✅ Working | https://tillu-ai-tillu-ai.hf.space | `embedding-space.py` |
| **WebSearch** | FastAPI | ✅ Working | https://huggingface.co/spaces/tillu-AI/tillu-websearch | `websearch-space/main.py` |
| **AI** | Gradio | ✅ Working | https://huggingface.co/spaces/tillu-AI/tillu-ai | Main AI space |
| **Search** | SearXNG | ❌ Placeholder | https://huggingface.co/spaces/tillu-AI/tillu-search | Needs SearXNG |
| **Engine** | n8n | ❌ Placeholder | https://huggingface.co/spaces/tillu-AI/tillu-engine | Needs n8n + workflows |
| **Daemon** | FastAPI | ❌ Placeholder | https://huggingface.co/spaces/tillu-AI/tillu-daemon | Needs `daemon/core.py` |

---

## 🔧 How to Fix

### Step 1: Update Environment Variables
```bash
# Update .env to use working spaces
HF_EMBEDDING_SPACE_URL=https://tillu-ai-tillu-ai.hf.space
WEBSEARCH_URL=https://huggingface.co/spaces/tillu-AI/tillu-websearch
SEARXNG_URL=https://codeex123-tillu-searxng.hf.space
N8N_WEBHOOK_URL=https://tillu-ai-tillu-engine.hf.space/webhook
N8N_URL=https://tillu-ai-tillu-engine.hf.space
```

### Step 2: Deploy Actual Implementations

#### For tillu-search (SearXNG)
```bash
cd deployments/huggingface/searxng-space
# Deploy SearXNG Docker image
```

#### For tillu-engine (n8n)
```bash
cd deployments/huggingface/n8n-space
# Deploy n8n with workflows
# Import: n8n/workflows/message-router.json
# Import: n8n/workflows/morning-intelligence-brief.json
```

#### For tillu-daemon (Background Tasks)
```bash
cd deployments/huggingface/daemon-space
# Deploy FastAPI + daemon loops
# Uses: daemon/core.py + daemon/hf_runner.py
```

### Step 3: Verify Deployments
```bash
# Test each space
curl https://huggingface.co/spaces/tillu-AI/tillu-gateway/health
curl https://tillu-ai-tillu-ai.hf.space/health
curl https://huggingface.co/spaces/tillu-AI/tillu-websearch/health
curl https://huggingface.co/spaces/tillu-AI/tillu-engine/health
curl https://huggingface.co/spaces/tillu-AI/tillu-daemon/health
```

---

## 📚 Reference Files

### Search Implementation
- `deployments/huggingface/websearch-space/main.py` (600+ lines)
- `app/tools/search_tools.py` (WebSearchTool, IntelligenceTool, ScrapePageTool)

### Engine Implementation
- `n8n/workflows/message-router.json` (WF-01)
- `n8n/workflows/morning-intelligence-brief.json` (WF-02)
- `deployments/huggingface/n8n-space/Dockerfile`

### Daemon Implementation
- `daemon/core.py` (16 loops)
- `daemon/hf_runner.py` (FastAPI + daemon runner)
- `deployments/huggingface/daemon-space/requirements.txt`

### Embedding Implementation
- `deployments/huggingface/embedding-space.py` (Gradio UI)
- `deployments/huggingface/requirements.txt` (dependencies)

### Gateway Implementation
- `deployments/huggingface/tillu-gateway/streamlit_app.py` (Streamlit UI)
- `app/api/gateway.py` (FastAPI endpoints)

---

## ✅ Verification Checklist

- [ ] Update `.env` with correct space URLs
- [ ] Test WebSearch space: `curl https://huggingface.co/spaces/tillu-AI/tillu-websearch/health`
- [ ] Test Embedding space: `curl https://tillu-ai-tillu-ai.hf.space/health`
- [ ] Test Gateway space: Visit https://huggingface.co/spaces/tillu-AI/tillu-gateway
- [ ] Deploy SearXNG to tillu-search
- [ ] Deploy n8n to tillu-engine with workflows
- [ ] Deploy daemon to tillu-daemon
- [ ] Test message routing: Send message to n8n webhook
- [ ] Test daemon loops: Check Redis events
- [ ] Verify all integrations working

---

## 🎯 Next Steps

1. **Immediate**: Update `.env` with correct URLs
2. **Short-term**: Deploy actual implementations to placeholder spaces
3. **Verification**: Test all integrations
4. **Monitoring**: Check logs and metrics

---

**Status**: Ready to fix  
**Last Updated**: 2026-05-11  
**Version**: 1.0.0

