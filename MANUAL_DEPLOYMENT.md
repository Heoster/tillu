# 🚀 Manual Deployment to HuggingFace Spaces

If the automated script doesn't work, follow these manual steps to deploy TILLU to HuggingFace Spaces.

---

## Prerequisites

1. **HuggingFace Account**: https://huggingface.co
2. **HuggingFace API Token**: https://huggingface.co/settings/tokens
   - Click "New token"
   - Select "Write" access
   - Copy the token (starts with `hf_`)
3. **Git installed**: https://git-scm.com/download/win
4. **huggingface_hub CLI**: `pip install huggingface-hub`

---

## Step 1: Create Spaces on HuggingFace

### Create Gateway Space
1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Owner**: tillu-AI (or your username)
   - **Space name**: tillu-gateway
   - **License**: Apache 2.0
   - **SDK**: Streamlit
3. Click "Create space"

### Create Backend Space
1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Owner**: tillu-AI (or your username)
   - **Space name**: tillu-backend
   - **License**: Apache 2.0
   - **SDK**: Docker
3. Click "Create space"

---

## Step 2: Clone Spaces Locally

```bash
# Clone gateway
git clone https://huggingface.co/spaces/tillu-AI/tillu-gateway
cd tillu-gateway

# Clone backend (in another terminal)
git clone https://huggingface.co/spaces/tillu-AI/tillu-backend
cd tillu-backend
```

---

## Step 3: Copy Files to Gateway Space

```bash
# From tillu-backend repository root
cp deployments/huggingface/tillu-gateway/streamlit_app.py ../tillu-gateway/
cp deployments/huggingface/tillu-gateway/requirements.txt ../tillu-gateway/
cp deployments/huggingface/tillu-gateway/README.md ../tillu-gateway/
cp deployments/huggingface/tillu-gateway/Dockerfile ../tillu-gateway/
```

---

## Step 4: Copy Files to Backend Space

```bash
# From tillu-backend repository root
cp deployments/huggingface/tillu-backend/app.py ../tillu-backend/
cp deployments/huggingface/tillu-backend/requirements.txt ../tillu-backend/
cp deployments/huggingface/tillu-backend/README.md ../tillu-backend/
cp deployments/huggingface/tillu-backend/Dockerfile ../tillu-backend/
```

---

## Step 5: Push Gateway to HuggingFace

```bash
cd ../tillu-gateway

# Configure git (if not already done)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add all files
git add -A

# Commit
git commit -m "Deploy TILLU Gateway"

# Push to HuggingFace
git push
```

---

## Step 6: Push Backend to HuggingFace

```bash
cd ../tillu-backend

# Configure git (if not already done)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add all files
git add -A

# Commit
git commit -m "Deploy TILLU Backend"

# Push to HuggingFace
git push
```

---

## Step 7: Wait for Build

Both spaces will now build automatically. This takes 2-5 minutes.

**Check status**:
- Gateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- Backend: https://huggingface.co/spaces/tillu-AI/tillu-backend

Look for the "Building" status to change to "Running".

---

## Step 8: Verify Deployment

### Test Backend API

```bash
curl https://tillu-ai-tillu-backend.hf.space/health
```

Expected response:
```json
{"status": "healthy", "version": "0.1.0", "environment": "huggingface-spaces"}
```

### Open Gateway UI

1. Go to: https://tillu-ai-tillu-gateway.hf.space
2. Wait for it to load (may take 30 seconds on first load)
3. In the sidebar, verify API URL is set to: `https://tillu-ai-tillu-backend.hf.space`
4. Click "Test Connection"
5. Should see: ✅ Connected to TILLU backend

---

## Step 9: Test Features

### Chat
1. Click "💬 Chat" button
2. Type a message
3. Should get a response

### Memory
1. Click "📊 Memory" button
2. Enter some text in "Memory content"
3. Click "💾 Save Memory"
4. Should see: ✅ Memory saved

### Tools
1. Click "🔧 Tools" button
2. Should see list of available tools

### Status
1. Click "📈 Status" button
2. Should see API status and system info

---

## Troubleshooting

### Space won't build

**Symptoms**: Space shows "Building" for >10 minutes or shows error

**Solution**:
1. Check Space logs:
   - Go to Space page
   - Click "Logs" tab
   - Look for error messages
2. Common issues:
   - Missing `Dockerfile`
   - Invalid `requirements.txt`
   - Syntax errors in Python files
3. Fix and re-push:
   ```bash
   git add -A
   git commit -m "Fix build error"
   git push
   ```

### Can't connect to backend

**Symptoms**: Gateway shows "❌ Connection failed"

**Solution**:
1. Verify backend is running:
   ```bash
   curl https://tillu-ai-tillu-backend.hf.space/health
   ```
2. Check gateway logs:
   - Go to Gateway Space page
   - Click "Logs" tab
   - Look for connection errors
3. Verify backend URL in gateway:
   - Open gateway UI
   - Check sidebar for API URL
   - Should be: `https://tillu-ai-tillu-backend.hf.space`

### Git authentication fails

**Symptoms**: `fatal: Authentication failed`

**Solution**:
1. Use HuggingFace token for authentication:
   ```bash
   git config --global credential.helper store
   git clone https://huggingface.co/spaces/tillu-AI/tillu-gateway
   # When prompted for password, use your HF token
   ```
2. Or use SSH:
   - Set up SSH key: https://huggingface.co/docs/hub/security-git-ssh
   - Clone with SSH: `git clone git@huggingface.co:spaces/tillu-AI/tillu-gateway`

### Files not uploading

**Symptoms**: Files don't appear in Space after push

**Solution**:
1. Verify files are in the right directory:
   ```bash
   ls -la
   ```
2. Check git status:
   ```bash
   git status
   ```
3. Make sure files are added:
   ```bash
   git add -A
   git status  # Should show files as "Changes to be committed"
   ```
4. Commit and push:
   ```bash
   git commit -m "Add files"
   git push
   ```

---

## URLs

### Production
- **Gateway**: https://tillu-ai-tillu-gateway.hf.space
- **Backend**: https://tillu-ai-tillu-backend.hf.space
- **Backend API Docs**: https://tillu-ai-tillu-backend.hf.space/docs

### Management
- **Gateway Space**: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- **Backend Space**: https://huggingface.co/spaces/tillu-AI/tillu-backend

---

## Next Steps

1. ✅ Deploy spaces
2. ✅ Wait for build
3. ✅ Test connection
4. 📝 Share gateway URL with users
5. 📊 Monitor logs
6. 🔄 Update as needed

---

## Support

### Documentation
- Deployment Guide: `docs/DEPLOYMENT_GUIDE.md`
- Quick Start: `DEPLOY_NOW.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`

### Issues
- Check logs in Space settings
- Review troubleshooting section
- Check HuggingFace documentation: https://huggingface.co/docs/hub/spaces

### Contact
- GitHub: https://github.com/Heoster/tillu
- Issues: https://github.com/Heoster/tillu/issues

---

**Last Updated**: 2026-05-11
**Status**: ✅ Ready for Manual Deployment
