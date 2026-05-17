# 📚 TILLU Documentation

Complete documentation for TILLU - Personal AI Backend

---

## 🚀 Quick Start

### Deploy to HuggingFace Spaces (5 minutes)

1. **Get HuggingFace Token**: https://huggingface.co/settings/tokens
2. **Deploy**:
   ```bash
   python scripts/deploy_tillu_spaces.py --token hf_your_token_here
   ```
3. **Wait**: 2-5 minutes for build
4. **Test**: https://tillu-ai-tillu-gateway.hf.space

See: [`DEPLOY_NOW.md`](../DEPLOY_NOW.md)

---

## 📖 Documentation Index

### Deployment
- **[DEPLOY_NOW.md](../DEPLOY_NOW.md)** - Quick start (5 steps, 5 minutes)
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Comprehensive guide
- **[MANUAL_DEPLOYMENT.md](../MANUAL_DEPLOYMENT.md)** - Step-by-step manual deployment
- **[DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md)** - Pre/post deployment checklist
- **[DEPLOYMENT_READY.md](../DEPLOYMENT_READY.md)** - Current status
- **[DEPLOYMENT_SUMMARY.md](../DEPLOYMENT_SUMMARY.md)** - Complete summary

### Architecture & Design
- **[WEAKPOINTS_REVIEW.md](WEAKPOINTS_REVIEW.md)** - Security audit and vulnerabilities
- **[TASK_8_COMPLETION.md](TASK_8_COMPLETION.md)** - Memory optimization details
- **[HF_SPACE_SETUP.md](HF_SPACE_SETUP.md)** - HuggingFace Spaces setup

### Configuration
- **[.env](../.env)** - Development environment variables
- **[.env.production](../.env.production)** - Production environment variables
- **[.env.example](../.env.example)** - Example environment variables

---

## 🏗️ Project Structure

```
tillu-backend/
├── app/                          # Main application
│   ├── api/                      # API endpoints
│   ├── chains/                   # LLM chains
│   ├── core/                     # Core logic
│   ├── models/                   # Data models
│   ├── providers/                # LLM providers
│   ├── security/                 # Security modules
│   ├── tools/                    # Tool implementations
│   ├── utils/                    # Utility functions
│   ├── config.py                 # Configuration
│   └── main.py                   # FastAPI app
├── deployments/                  # Deployment configurations
│   ├── huggingface/              # HuggingFace Spaces
│   │   ├── tillu-gateway/        # Streamlit UI
│   │   ├── tillu-backend/        # FastAPI backend
│   │   └── ...                   # Other spaces
│   ├── render/                   # Render deployment
│   └── fly/                      # Fly.io deployment
├── scripts/                      # Deployment & utility scripts
├── docs/                         # Documentation
├── supabase/                     # Database schema
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
└── README.md                     # Project README
```

---

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: Supabase (PostgreSQL + pgvector)
- **Cache**: Redis (Upstash)
- **Search**: SearXNG, Brave Search

### Frontend
- **UI**: Streamlit
- **HTTP Client**: httpx
- **Deployment**: HuggingFace Spaces

### LLM Providers (Free Tier)
- **Groq** - Fast inference
- **Cerebras** - Large models
- **Together AI** - Multiple models
- **OpenRouter** - Model aggregation
- **Google Gemini** - Google's models
- **HuggingFace** - Open source models
- **Cloudflare Workers AI** - Edge AI

### Infrastructure
- **Deployment**: HuggingFace Spaces (free tier)
- **Database**: Supabase
- **Cache**: Upstash Redis
- **Monitoring**: HuggingFace Spaces logs

---

## 🚀 Deployment Options

### Option 1: HuggingFace Spaces (Recommended)
- **Cost**: $0/month (free tier)
- **Setup time**: 5-15 minutes
- **Build time**: 2-5 minutes
- **Resources**: 2GB RAM, 16GB storage per space
- **Guide**: [`DEPLOY_NOW.md`](../DEPLOY_NOW.md)

### Option 2: Render
- **Cost**: $7-12/month
- **Setup time**: 10-20 minutes
- **Resources**: 512MB RAM (free tier)
- **Guide**: See `deployments/render/`

### Option 3: Fly.io
- **Cost**: $5-10/month
- **Setup time**: 10-20 minutes
- **Resources**: 256MB RAM (free tier)
- **Guide**: See `deployments/fly/`

---

## 🔐 Security

### Implemented Security Measures
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling
- ✅ Logging sanitization
- ✅ Connection pooling
- ✅ N+1 query prevention
- ✅ LLM fallback chains

See: [`WEAKPOINTS_REVIEW.md`](WEAKPOINTS_REVIEW.md)

---

## 📊 Features

### Chat Interface
- 💬 Real-time conversation with TILLU
- 📝 Message history
- 🔄 Streaming responses
- ⚡ Fast inference

### Memory Management
- 📝 Store memories (notes, events, insights, learnings)
- 🔍 Semantic search with pgvector
- 📊 Relevance scoring
- 🎯 Context-aware retrieval

### Tool Browser
- 🔧 List available tools
- 📖 View tool descriptions
- 📋 See tool parameters
- 🎯 Understand capabilities

### System Status
- 🟢 API health check
- 📈 Version information
- ⏱️ Uptime monitoring
- 📊 Detailed metrics

---

## 🛠️ Development

### Local Setup
```bash
# Clone repository
git clone https://github.com/Heoster/tillu.git
cd tillu-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
python -m uvicorn app.main:app --reload
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app
```

### Code Quality
```bash
# Lint
flake8 app/

# Format
black app/

# Type checking
mypy app/
```

---

## 📚 API Documentation

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "huggingface-spaces"
}
```

### Chat
```bash
POST /api/gateway/chat
Content-Type: application/json

{
  "message": "Hello TILLU"
}
```

### Memory
```bash
# Store memory
POST /api/memory/store
{
  "content": "Important note",
  "type": "note",
  "timestamp": "2026-05-11T12:00:00Z"
}

# Search memory
GET /api/memory/search?query=important&limit=5
```

### Tools
```bash
GET /api/gateway/tools
```

---

## 🐛 Troubleshooting

### Space won't build
- Check Space logs
- Verify all files uploaded
- Re-deploy

### Can't connect to backend
- Verify backend URL in gateway
- Check backend health: `curl https://tillu-ai-tillu-backend.hf.space/health`
- Check gateway logs

### Slow responses
- Check backend logs
- Verify network connectivity
- Check HuggingFace Spaces status

### Out of memory
- Check current usage
- Optimize code
- Upgrade to paid tier

See: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md#troubleshooting)

---

## 📞 Support

### Documentation
- GitHub: https://github.com/Heoster/tillu
- Docs: This folder
- README: `README.md`

### Issues
- GitHub Issues: https://github.com/Heoster/tillu/issues
- Check logs in Space settings
- Review troubleshooting sections

### Contact
- Email: tillu@tillu.ai
- GitHub: https://github.com/Heoster/tillu

---

## 📄 License

Apache 2.0 - See LICENSE file

---

## 🎯 Roadmap

### Current (v0.1.0)
- ✅ Basic chat interface
- ✅ Memory management
- ✅ Tool browser
- ✅ System status
- ✅ HuggingFace Spaces deployment

### Planned (v0.2.0)
- 🔄 Authentication
- 🔄 Rate limiting
- 🔄 Analytics
- 🔄 Performance optimization

### Future (v1.0.0)
- 🔮 Advanced features
- 🔮 Custom domain
- 🔮 Paid tier
- 🔮 Enterprise support

---

## 📊 Statistics

- **Lines of Code**: 5000+
- **Python Files**: 70+
- **Documentation**: 10+ guides
- **LLM Providers**: 7
- **Models**: 27+
- **Cost**: $0/month (free tier)
- **Build Time**: 2-5 minutes
- **Deployment Time**: 5-15 minutes

---

## 🙏 Acknowledgments

- FastAPI: https://fastapi.tiangolo.com
- Streamlit: https://streamlit.io
- Supabase: https://supabase.com
- HuggingFace: https://huggingface.co
- LangChain: https://langchain.com

---

## 📝 Changelog

### v0.1.0 (2026-05-11)
- Initial release
- HuggingFace Spaces deployment
- Chat interface
- Memory management
- Tool browser
- System status
- Security hardening
- Documentation

---

**Last Updated**: 2026-05-11
**Version**: 0.1.0
**Status**: ✅ Production Ready
