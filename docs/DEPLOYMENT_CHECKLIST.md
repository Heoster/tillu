# TILLU Deployment Checklist

## Pre-Deployment

- [ ] All tests passing
- [ ] No import errors
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] Dependencies optimized (no heavy packages)
- [ ] Memory usage < 512MB
- [ ] Port binding to 0.0.0.0:8000

## Backend Deployment (Render)

### Setup

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Select Python runtime
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`

### Environment Variables

- [ ] `SUPABASE_URL` - Database URL
- [ ] `SUPABASE_KEY` - Anon key
- [ ] `GROQ_API_KEY` - Groq API key
- [ ] `CEREBRAS_API_KEY` - Cerebras API key
- [ ] `TOGETHER_API_KEY` - Together AI key
- [ ] `GOOGLE_API_KEY` - Google Gemini key
- [ ] `OPENROUTER_API_KEY` - OpenRouter key
- [ ] `CLOUDFLARE_API_TOKEN` - Cloudflare token
- [ ] `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID
- [ ] `REDIS_URL` - Redis connection URL
- [ ] `JWT_SECRET` - JWT signing secret
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `LOG_LEVEL` - Set to `info`

### Verification

- [ ] Service deployed successfully
- [ ] Health check passing: `GET /health`
- [ ] API responding: `GET /`
- [ ] No errors in logs
- [ ] Port 8000 is bound
- [ ] Memory usage < 512MB

## Gateway Deployment (HuggingFace Spaces)

### Setup

- [ ] Create HuggingFace account
- [ ] Create new Space
- [ ] Select Streamlit SDK
- [ ] Upload `deployments/huggingface/tillu-gateway/` files
- [ ] Add repository secret: `TILLU_API_URL`

### Files

- [ ] `app.py` - Streamlit application
- [ ] `requirements.txt` - Dependencies
- [ ] `README.md` - Documentation
- [ ] `Dockerfile` - Container config (optional)

### Verification

- [ ] Space deployed successfully
- [ ] Streamlit UI loads
- [ ] Can enter backend URL in sidebar
- [ ] "Test Connection" button works
- [ ] Shows "✅ Connected" message
- [ ] Chat interface functional
- [ ] Memory search working
- [ ] Tools browser showing tools

## Post-Deployment

### Monitoring

- [ ] Set up error tracking (Sentry)
- [ ] Monitor API response times
- [ ] Check memory usage daily
- [ ] Review logs for errors
- [ ] Monitor LLM provider status

### Security

- [ ] Verify CORS settings
- [ ] Check JWT validation
- [ ] Verify rate limiting
- [ ] Test authentication
- [ ] Review database permissions

### Performance

- [ ] Measure API latency
- [ ] Check cache hit rate
- [ ] Monitor database queries
- [ ] Verify LLM fallback chain
- [ ] Test under load

## Rollback Plan

If deployment fails:

1. [ ] Check error logs
2. [ ] Verify environment variables
3. [ ] Check database connectivity
4. [ ] Verify LLM provider keys
5. [ ] Rollback to previous version
6. [ ] Fix issues locally
7. [ ] Re-deploy

## Maintenance

### Weekly

- [ ] Check error logs
- [ ] Monitor memory usage
- [ ] Verify all providers working
- [ ] Test critical features

### Monthly

- [ ] Update dependencies
- [ ] Review security advisories
- [ ] Optimize slow queries
- [ ] Clean up old data

### Quarterly

- [ ] Performance audit
- [ ] Security audit
- [ ] Cost analysis
- [ ] Capacity planning

## Troubleshooting

### Backend won't start

```bash
# Check logs
render.com/dashboard

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Import errors
# - Port already in use
```

### Gateway can't connect

```bash
# Check backend URL
curl https://tillu-backend.onrender.com/health

# Check CORS
# Check firewall rules
# Check network connectivity
```

### Out of memory

```bash
# Check memory usage
# Remove heavy dependencies
# Upgrade to paid tier
# Optimize queries
```

### Slow responses

```bash
# Check LLM provider status
# Check database performance
# Check Redis cache
# Monitor network latency
```

## Success Criteria

- ✅ Backend API responding on port 8000
- ✅ Gateway UI accessible on HuggingFace Spaces
- ✅ Chat interface working
- ✅ Memory storage working
- ✅ Tool execution working
- ✅ Memory usage < 512MB
- ✅ Response time < 5 seconds
- ✅ No errors in logs
- ✅ All LLM providers available
- ✅ Database connected
- ✅ Redis connected
- ✅ JWT authentication working
- ✅ Rate limiting working
- ✅ CORS configured
- ✅ Monitoring active

## Deployment Complete! 🎉

Once all items are checked, TILLU is ready for production use.
