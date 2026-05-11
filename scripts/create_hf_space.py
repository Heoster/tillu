#!/usr/bin/env python3
"""
Create and push TILLU Gateway to HuggingFace Spaces via API
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo
import json

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
HF_USERNAME = "tillu-AI"
SPACE_NAME = "tillu-gateway"
SPACE_DESCRIPTION = "TILLU - Personal AI Backend Gateway. Streamlit interface for conversational AI, memory management, and tool execution."
SPACE_PRIVATE = False

# Paths
GATEWAY_DIR = Path(__file__).parent.parent / "deployments" / "huggingface" / "tillu-gateway"
FILES_TO_UPLOAD = [
    "app.py",
    "requirements.txt",
    "README.md",
    "Dockerfile"
]

def main():
    if not HF_TOKEN:
        print("❌ Error: HF_TOKEN environment variable not set")
        sys.exit(1)
    
    print("🚀 TILLU Gateway - HuggingFace Spaces Deployment")
    print("=" * 60)
    
    # Initialize API
    api = HfApi(token=HF_TOKEN)
    
    # Get user info
    try:
        user_info = api.whoami()
        print(f"✅ Authenticated as: {user_info['name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    # Create Space repo
    space_id = f"{HF_USERNAME}/{SPACE_NAME}"
    print(f"\n📦 Creating Space: {space_id}")
    
    try:
        repo_url = create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="streamlit",
            private=SPACE_PRIVATE,
            exist_ok=True,
            token=HF_TOKEN
        )
        print(f"✅ Space created/exists: {repo_url}")
    except Exception as e:
        print(f"❌ Failed to create Space: {e}")
        sys.exit(1)
    
    # Upload files
    print(f"\n📤 Uploading files...")
    
    for filename in FILES_TO_UPLOAD:
        filepath = GATEWAY_DIR / filename
        
        if not filepath.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            continue
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            api.upload_file(
                path_or_fileobj=file_content.encode("utf-8"),
                path_in_repo=filename,
                repo_id=space_id,
                repo_type="space",
                token=HF_TOKEN
            )
            print(f"✅ Uploaded: {filename}")
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")
            sys.exit(1)
    
    # Add secrets
    print(f"\n🔐 Adding secrets...")
    
    secrets = {
        "TILLU_API_URL": "https://tillu-backend.onrender.com"
    }
    
    try:
        for secret_name, secret_value in secrets.items():
            api.add_space_secret(
                repo_id=space_id,
                name=secret_name,
                value=secret_value,
                token=HF_TOKEN
            )
            print(f"✅ Added secret: {secret_name}")
    except Exception as e:
        print(f"⚠️  Could not add secrets via API: {e}")
        print(f"   Please add manually in Space settings:")
        for secret_name, secret_value in secrets.items():
            print(f"   - {secret_name} = {secret_value}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"\n🌐 Space URL: https://huggingface.co/spaces/{space_id}")
    print(f"\n📝 Next steps:")
    print(f"   1. Wait 2-3 minutes for Space to build")
    print(f"   2. Open the Space URL above")
    print(f"   3. Test connection in sidebar")
    print(f"   4. Should see '✅ Connected to TILLU backend'")
    print(f"\n💡 If connection fails:")
    print(f"   - Check backend is running: https://tillu-backend.onrender.com/health")
    print(f"   - Verify TILLU_API_URL secret is set")
    print(f"   - Check Space logs for errors")
    print("\n")

if __name__ == "__main__":
    main()
