#!/usr/bin/env python3
"""
Deploy TILLU Gateway and Backend to HuggingFace Spaces
Usage: python scripts/deploy_tillu_spaces.py --token YOUR_HF_TOKEN
"""

import os
import sys
import argparse
import pathlib
import time
from huggingface_hub import HfApi

def main():
    parser = argparse.ArgumentParser(description="Deploy TILLU spaces to HuggingFace")
    parser.add_argument("--token", help="HuggingFace API token")
    args = parser.parse_args()
    
    # Get token from argument or environment
    hf_token = args.token or os.getenv("HF_TOKEN")
    
    if not hf_token:
        print("❌ ERROR: HF_TOKEN not provided")
        print("Usage: python scripts/deploy_tillu_spaces.py --token YOUR_HF_TOKEN")
        print("Or set environment variable: set HF_TOKEN=your_token_here")
        sys.exit(1)
    
    # Initialize API
    api = HfApi(token=hf_token)
    
    # Get user info
    try:
        user = api.whoami()
        print(f"✅ Logged in as: {user['name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    base_path = pathlib.Path(__file__).parent.parent
    
    # Define spaces to deploy
    spaces = [
        {
            "name": "TILLU Gateway",
            "repo_id": "tillu-AI/tillu-gateway",
            "local_path": base_path / "deployments" / "huggingface" / "tillu-gateway",
            "files": ["streamlit_app.py", "requirements.txt", "README.md", "Dockerfile"]
        },
        {
            "name": "TILLU Backend",
            "repo_id": "tillu-AI/tillu-backend",
            "local_path": base_path / "deployments" / "huggingface" / "tillu-backend",
            "files": ["app.py", "requirements.txt", "README.md", "Dockerfile"]
        }
    ]
    
    print("\n" + "=" * 60)
    print("TILLU HuggingFace Spaces Deployment")
    print("=" * 60 + "\n")
    
    for space in spaces:
        print(f"\n📦 Deploying: {space['name']}")
        print(f"   Repo: {space['repo_id']}")
        print(f"   Path: {space['local_path']}")
        
        # Check if space exists
        try:
            api.repo_info(repo_id=space['repo_id'], repo_type='space')
            print(f"   ✅ Space exists")
        except Exception:
            print(f"   📝 Creating space...")
            try:
                api.create_repo(
                    repo_id=space['repo_id'],
                    repo_type='space',
                    space_sdk='docker',
                    private=False,
                    exist_ok=True
                )
                print(f"   ✅ Space created")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Failed to create space: {e}")
                continue
        
        # Upload files
        for file_name in space['files']:
            file_path = space['local_path'] / file_name
            if file_path.exists():
                try:
                    print(f"   📤 Uploading {file_name}...", end=" ")
                    api.upload_file(
                        path_or_fileobj=str(file_path),
                        path_in_repo=file_name,
                        repo_id=space['repo_id'],
                        repo_type='space',
                        commit_message=f"Update {file_name}"
                    )
                    print("✅")
                except Exception as e:
                    print(f"❌ {e}")
            else:
                print(f"   ⚠️  Missing: {file_name}")
        
        # Print space URL
        space_url = f"https://huggingface.co/spaces/{space['repo_id']}"
        print(f"   🌐 Space URL: {space_url}")
    
    print("\n" + "=" * 60)
    print("✅ Deployment Complete!")
    print("=" * 60)
    print("\nSpaces are building (2-5 minutes)...")
    print("\nGateway: https://huggingface.co/spaces/tillu-AI/tillu-gateway")
    print("Backend: https://huggingface.co/spaces/tillu-AI/tillu-backend")
    print("\nNext steps:")
    print("1. Wait for spaces to build")
    print("2. Test gateway at: https://tillu-ai-tillu-gateway.hf.space")
    print("3. Test backend at: https://tillu-ai-tillu-backend.hf.space/docs")
    print("4. Configure gateway to use backend URL in settings")
    print()

if __name__ == "__main__":
    main()
