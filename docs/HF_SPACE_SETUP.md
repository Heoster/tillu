# HuggingFace Spaces Setup - Quick Guide

## Create the Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in the form:
   - **Space name**: `tillu-gateway`
   - **License**: Apache 2.0
   - **SDK**: Streamlit
   - **Visibility**: Public
4. Click **"Create Space"**

## Upload Files

1. In the Space, go to **"Files and versions"**
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from `deployments/huggingface/tillu-gateway/`:
   - `app.py`
   - `requirements.txt`
   - `README.md`

Or use Git:

```bash
# Clone the Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/tillu-gateway
cd tillu-gateway

# Copy files
cp ../../deployments/huggingface/tillu-gateway/* .

# Push
git add .
git commit -m "Initial commit"
git push
```

## Configure Environment

1. Go to Space **"Settings"**
2. Click **"Repository secrets"**
3. Add secret:
   - **Name**: `TILLU_API_URL`
   - **Value**: `https://tillu-backend.onrender.com` (or your backend URL)
4. Click **"Add secret"**

## Deploy

The Space will auto-deploy when files are uploaded. Wait 2-3 minutes for deployment.

## Verify

1. Open the Space URL
2. In sidebar, verify the API URL is set
3. Click **"Test Connection"**
4. Should see **"✅ Connected to TILLU backend"**

## Troubleshooting

### Space won't load
- Check logs: Space → "Logs"
- Verify `requirements.txt` is valid
- Check `app.py` for syntax errors

### Can't connect to backend
- Verify `TILLU_API_URL` is set in secrets
- Check backend is running: `curl https://tillu-backend.onrender.com/health`
- Check CORS settings in backend

### Out of memory
- Space has 16GB storage, 2GB RAM (free tier)
- Current usage: ~100MB
- Should be fine

## Next Steps

1. ✅ Create Space
2. ✅ Upload files
3. ✅ Configure environment
4. ✅ Verify connection
5. ⏳ Share Space URL
6. ⏳ Add to documentation

## Space URL

Once deployed, your Space will be at:
```
https://huggingface.co/spaces/YOUR_USERNAME/tillu-gateway
```

Share this URL with users to access TILLU!
