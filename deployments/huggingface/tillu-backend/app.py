"""
TILLU Backend API - HuggingFace Spaces Deployment
Minimal FastAPI server for TILLU Gateway
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="TILLU Backend API",
    description="Personal AI Backend - HuggingFace Spaces Edition",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": "huggingface-spaces"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "TILLU Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

# Chat endpoint (mock)
@app.post("/api/gateway/chat")
async def chat(request: dict):
    """Chat endpoint - mock implementation"""
    message = request.get("message", "")
    return {
        "response": f"Echo: {message}",
        "status": "success"
    }

# Memory store endpoint (mock)
@app.post("/api/memory/store")
async def store_memory(request: dict):
    """Store memory endpoint - mock implementation"""
    return {
        "status": "success",
        "message": "Memory stored"
    }

# Memory search endpoint (mock)
@app.get("/api/memory/search")
async def search_memory(query: str, limit: int = 5):
    """Search memory endpoint - mock implementation"""
    return {
        "results": [],
        "query": query,
        "limit": limit
    }

# Tools endpoint (mock)
@app.get("/api/gateway/tools")
async def get_tools():
    """Get available tools - mock implementation"""
    return {
        "tools": [
            {
                "name": "Echo Tool",
                "description": "Echoes back the input",
                "parameters": {
                    "text": {"description": "Text to echo"}
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
