# ✅ TILLU Deployment Checklist

## Pre-Deployment Verification

### Code Quality
- ✅ Gateway `streamlit_app.py` - No st.tabs() or st.container(height=)
- ✅ Gateway `Dockerfile` - Uses streamlit_app.py
- ✅ Backend `app.py` - FastAPI with mock endpoints
- ✅ Backend `Dockerfile` - Correct port 7860
- ✅ Old `app.py` - Deleted (was causing errors)
- ✅ Deployment script - `scripts/deploy_tillu_spaces.py`

### Configuration
- ✅ `.env.production` - Updated CORS origins for HF Spaces
- ✅ Gateway default URL - `https://tillu-ai-tillu-backend.hf.space`
- ✅ Backend health endpoint - `/health`
- ✅ CORS enabled - For cross-origin requests

### Documentation
- ✅ `docs/DEPLOYMENT_GUIDE.md` - Comprehensive guide
- ✅ `DEPLOY_NOW.md` - Quick start (5 steps)
- ✅ `DEPLOYMENT_READY.md` - Status and summary
- ✅ `DEPLOYMENT_CHECKLIST.md` - This file

---

## Deployment Steps

### Step 1: Prerequisites ✅
- [ ] HuggingFace account created
- [ ] HuggingFace API token generated (https://huggingface.co/settings/tokens)
- [ ] Python 3.8+ installed
- [ ] `huggingface_hub` installed: `pip install huggingface-hub`

### Step 2: Set Environment Variable
- [ ] Windows CMD: `set HF_TOKEN=hf_your_token_here`
- [ ] Windows PowerShell: `$env:HF_TOKEN="hf_your_token_here"`
- [ ] Linux/Mac: `export HF_TOKEN=hf_your_token_here`

### Step 3: Deploy Spaces
```bash
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```
- [ ] Script runs without errors
- [ ] Both spaces created/updated
- [ ] Files uploaded successfully

### Step 4: Wait for Build
- [ ] Gateway building: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- [ ] Backend building: https://huggingface.co/spaces/tillu-AI/tillu-backend
- [ ] Build time: 2-5 minutes

### Step 5: Verify Deployment
- [ ] Backend health check: `curl https://tillu-ai-tillu-backend.hf.space/health`
- [ ] Expected response: `{"status": "healthy", "version": "0.1.0", "environment": "huggingface-spaces"}`
- [ ] Gateway loads: https://tillu-ai-tillu-gateway.hf.space

### Step 6: Test Connection
- [ ] Open gateway UI
- [ ] In sidebar, verify API URL: `https://tillu-ai-tillu-backend.hf.space`
- [ ] Click "Test Connection"
- [ ] Should see: ✅ Connected to TILLU backend

### Step 7: Test Features
- [ ] Chat: Send a message
- [ ] Memory: Store and search a memory
- [ ] Tools: Browse available tools
- [ ] Status: Check system status

---

## Post-Deployment

### Monitoring
- [ ] Check Space logs regularly
- [ ] Monitor resource usage
- [ ] Set up alerts (if available)

### Maintenance
- [ ] Keep dependencies updated
- [ ] Monitor error logs
- [ ] Test regularly

### Scaling (if needed)
- [ ] Upgrade to paid tier
- [ ] Add more resources
- [ ] Optimize code

---

## Troubleshooting

### Space won't build
**Symptoms**: Space shows "Building" for >10 minutes or shows error
**Solution**:
1. Check Space logs
2. Verify all files uploaded
3. Re-deploy: `python scripts/deploy_tillu_spaces.py --token hf_your_token_here`

### Can't connect to backend
**Symptoms**: Gateway shows "❌ Connection failed"
**Solution**:
1. Verify backend is running: `curl https://tillu-ai-tillu-backend.hf.space/health`
2. Check gateway logs
3. Verify backend URL in gateway settings
4. Check CORS configuration

### Slow responses
**Symptoms**: Requests take >30 seconds
**Solution**:
1. Check backend logs for errors
2. Verify network connectivity
3. Check HuggingFace Spaces status
4. Optimize code if needed

### Out of memory
**Symptoms**: Space crashes or becomes unresponsive
**Solution**:
1. Check current usage in Space settings
2. Optimize code to reduce memory
3. Upgrade to paid tier if needed

---

## Rollback Plan

If deployment fails:

1. **Revert files**:
   ```bash
   git checkout deployments/huggingface/
   ```

2. **Re-deploy**:
   ```bash
   python scripts/deploy_tillu_spaces.py --token hf_your_token_here
   ```

3. **Manual deployment** (if script fails):
   - Clone spaces manually
   - Copy files manually
   - Push to HuggingFace

---

## Success Criteria

- ✅ Both spaces deployed
- ✅ Gateway loads without errors
- ✅ Backend responds to health check
- ✅ Gateway can connect to backend
- ✅ All features work (chat, memory, tools, status)
- ✅ No errors in logs
- ✅ Response time <5 seconds

---

## URLs

### Production
- **Gateway**: https://tillu-ai-tillu-gateway.hf.space
- **Backend**: https://tillu-ai-tillu-backend.hf.space
- **Backend API Docs**: https://tillu-ai-tillu-backend.hf.space/docs

### Management
- **Gateway Space**: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- **Backend Space**: https://huggingface.co/spaces/tillu-AI/tillu-backend
- **HF Settings**: https://huggingface.co/settings/tokens

---

## Support

### Documentation
- Deployment Guide: `docs/DEPLOYMENT_GUIDE.md`
- Quick Start: `DEPLOY_NOW.md`
- Status: `DEPLOYMENT_READY.md`

### Issues
- Check logs in Space settings
- Review troubleshooting section
- Check HuggingFace documentation

### Contact
- GitHub: https://github.com/Heoster/tillu
- Issues: https://github.com/Heoster/tillu/issues

---

## Sign-Off

- [ ] All checks passed
- [ ] Deployment successful
- [ ] Features verified
- [ ] Ready for production

**Deployed by**: _______________
**Date**: _______________
**Status**: ✅ PRODUCTION READY

---

**Last Updated**: 2026-05-11
**Version**: 1.0.0
