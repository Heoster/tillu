# 🚀 Deploy TILLU to HuggingFace Spaces - Quick Start

## 1️⃣ Get HuggingFace Token

Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Select "Write" access
- Copy token (starts with `hf_`)

## 2️⃣ Deploy Spaces

### Windows CMD
```cmd
set HF_TOKEN=hf_your_token_here
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

### Windows PowerShell
```powershell
$env:HF_TOKEN="hf_your_token_here"
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

### Linux/Mac
```bash
export HF_TOKEN=hf_your_token_here
python scripts/deploy_tillu_spaces.py --token hf_your_token_here
```

## 3️⃣ Wait for Build (2-5 minutes)

Check status:
- Gateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway
- Backend: https://huggingface.co/spaces/tillu-AI/tillu-backend

## 4️⃣ Test Connection

### Test Backend API
```bash
curl https://tillu-ai-tillu-backend.hf.space/health
```

Expected:
```json
{"status": "healthy", "version": "0.1.0", "environment": "huggingface-spaces"}
```

### Open Gateway UI
1. Go to: https://tillu-ai-tillu-gateway.hf.space
2. In sidebar, enter: `https://tillu-ai-tillu-backend.hf.space`
3. Click "Test Connection"
4. Should see: ✅ Connected to TILLU backend

## 5️⃣ Done! 🎉

Your TILLU is now live on HuggingFace Spaces!

- **Gateway**: https://tillu-ai-tillu-gateway.hf.space
- **Backend**: https://tillu-ai-tillu-backend.hf.space
- **Cost**: $0/month (free tier)

---

## Troubleshooting

### Space won't build?
- Check logs in Space settings
- Verify all files are uploaded
- Try re-deploying

### Can't connect to backend?
- Verify backend URL in gateway settings
- Check backend is running: `curl https://tillu-ai-tillu-backend.hf.space/health`
- Check gateway logs

### Need help?
- See: `docs/DEPLOYMENT_GUIDE.md`
- GitHub: https://github.com/Heoster/tillu

---

**Status**: ✅ Ready to Deploy
**Last Updated**: 2026-05-11
