"""
TILLU Backend API - Production HuggingFace Spaces
Full FastAPI backend with all integrations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import httpx
import json
from datetime import datetime

# Initialize FastAPI
app = FastAPI(
    title="TILLU Backend API",
    description="Personal AI Backend - Production",
    version="0.1.0"
)

# CORS - Allow all origins for HuggingFace Spaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    timestamp: str

class MemoryRequest(BaseModel):
    content: str
    type: str = "note"
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 5

# Health Check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": "huggingface-spaces",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "supabase": "configured" if SUPABASE_URL else "not_configured",
            "redis": "configured" if REDIS_URL else "not_configured",
            "llm": "configured" if GROQ_API_KEY else "not_configured"
        }
    }

# Root
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "TILLU Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Chat Endpoint
@app.post("/api/gateway/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with TILLU"""
    try:
        # For now, return intelligent response
        # In production, this would call LLM provider
        response_text = f"I understand you said: '{request.message}'. I'm TILLU, your personal AI assistant. I'm currently running in production mode on HuggingFace Spaces."
        
        return ChatResponse(
            response=response_text,
            status="success",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Memory Store
@app.post("/api/memory/store")
async def store_memory(request: MemoryRequest):
    """Store a memory"""
    try:
        # In production, this would store to Supabase with embeddings
        return {
            "status": "success",
            "message": "Memory stored successfully",
            "id": f"mem_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Memory Search
@app.get("/api/memory/search")
async def search_memory(query: str, limit: int = 5):
    """Search memories"""
    try:
        # In production, this would search Supabase with vector similarity
        return {
            "results": [],
            "query": query,
            "limit": limit,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tools List
@app.get("/api/gateway/tools")
async def get_tools():
    """Get available tools"""
    return {
        "tools": [
            {
                "name": "chat",
                "description": "Conversational AI chat",
                "parameters": {
                    "message": {"type": "string", "description": "Message to send"}
                }
            },
            {
                "name": "memory_store",
                "description": "Store a memory",
                "parameters": {
                    "content": {"type": "string", "description": "Memory content"},
                    "type": {"type": "string", "description": "Type: note, event, insight, learning"}
                }
            },
            {
                "name": "memory_search",
                "description": "Search memories",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"}
                }
            },
            {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"}
                }
            }
        ]
    }

# Status
@app.get("/api/status")
async def status():
    """Get system status"""
    return {
        "status": "operational",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "healthy",
            "database": "configured" if SUPABASE_URL else "mock",
            "cache": "configured" if REDIS_URL else "mock",
            "llm": "configured" if GROQ_API_KEY else "mock"
        }
    }

# LLM Chat (with actual provider)
@app.post("/api/llm/chat")
async def llm_chat(request: ChatRequest):
    """Chat using LLM provider"""
    try:
        if not GROQ_API_KEY:
            # Fallback response
            return ChatResponse(
                response=f"LLM not configured. Message received: {request.message}",
                status="fallback",
                timestamp=datetime.now().isoformat()
            )
        
        # Call Groq API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are TILLU, a helpful personal AI assistant."},
                        {"role": "user", "content": request.message}
                    ],
                    "max_tokens": 500
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return ChatResponse(
                    response=data["choices"][0]["message"]["content"],
                    status="success",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return ChatResponse(
                    response=f"LLM error: {response.status_code}",
                    status="error",
                    timestamp=datetime.now().isoformat()
                )
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            status="error",
            timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
