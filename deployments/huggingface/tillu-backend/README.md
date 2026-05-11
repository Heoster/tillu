---
title: TILLU Backend API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# TILLU Backend API - HuggingFace Spaces

FastAPI-based backend for TILLU personal AI system, deployed on HuggingFace Spaces.

## Features

- 🚀 FastAPI REST API
- 💬 Chat endpoint
- 📝 Memory management
- 🔧 Tool execution
- 📊 Health monitoring

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/gateway/chat` - Chat with TILLU
- `POST /api/memory/store` - Store memory
- `GET /api/memory/search` - Search memories
- `GET /api/gateway/tools` - List tools

## Usage

```bash
# Health check
curl https://tillu-ai-tillu-backend.hf.space/health

# Chat
curl -X POST https://tillu-ai-tillu-backend.hf.space/api/gateway/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello TILLU"}'
```

## Links

- [Gateway](https://huggingface.co/spaces/tillu-AI/tillu-gateway)
- [GitHub](https://github.com/Heoster/tillu)
