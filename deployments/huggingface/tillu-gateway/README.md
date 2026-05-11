---
title: TILLU Gateway
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: streamlit_app.py
pinned: false
license: apache-2.0
---

# TILLU Gateway - Personal AI Backend

Streamlit-based web interface for TILLU backend, deployed on HuggingFace Spaces.

## Features

- 💬 **Chat Interface** - Conversational AI with TILLU
- 📝 **Memory Management** - Store and search semantic memories
- 🔧 **Tool Browser** - Explore available tools
- 📊 **System Status** - Monitor API health

## Configuration

Set environment variable in Space settings:
- \TILLU_API_URL\ - URL of TILLU backend (default: http://localhost:8000)

## Architecture

\\\
HuggingFace Spaces (Streamlit UI)
         ↓
    httpx client
         ↓
TILLU Backend API (FastAPI)
         ↓
Supabase + Redis + LLM Providers
\\\

## Links

- [GitHub](https://github.com/Heoster/tillu)
- [Backend](https://tillu-backend.onrender.com)
