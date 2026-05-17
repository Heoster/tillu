#!/usr/bin/env python3
"""
TILLU Complete Deployment Script
Deploys both spaces and sets all environment variables
Usage: python scripts/deploy_tillu_complete.py --token hf_your_token_here
"""

import os
import sys
import argparse
import pathlib
import time
from huggingface_hub import HfApi

def parse_env_file(env_path):
    """Parse .env file and return dict of variables"""
    env_vars = {}
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip placeholder values
                if value.startswith('YOUR_') or value == '':
                    continue
                
                env_vars[key] = value
    
    return env_vars

def upload_file(api, repo_id, file_path, file_name):
    """Upload a file to HuggingFace Space"""
    try:
        print(f"  📤 Uploading {file_name}...", end=" ")
        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=file_name,
            repo_id=repo_id,
            repo_type='space',
            commit_message=f"Update {file_name}"
        )
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {str(e)[:50]}")
        return False

def set_space_secrets(api, space_id, secrets):
    """Set secrets for a HuggingFace Space"""
    print(f"\n🔐 Setting secrets for {space_id}...")
    
    success_count = 0
    error_count = 0
    
    for key, value in secrets.items():
        try:
            api.add_space_secret(
                repo_id=space_id,
                key=key,
                value=value
            )
            print(f"  ✅ {key}")
            success_count += 1
        except Exception as e:
            # Ignore "secret already exists" errors
            if "already exists" not in str(e).lower():
                print(f"  ⚠️  {key}: {str(e)[:30]}")
            success_count += 1  # Count as success if already exists
    
    print(f"\n📊 Secrets: {success_count} set")
    return success_count

def deploy_space(api, space_name, space_config, hf_token):
    """Deploy a single HuggingFace Space"""
    print(f"\n{'='*60}")
    print(f"📦 Deploying: {space_name}")
    print(f"{'='*60}")
    
    repo_id = space_config['repo_id']
    local_path = space_config['local_path']
    files = space_config['files']
    
    print(f"   Repo: {repo_id}")
    print(f"   Path: {local_path}")
    
    # Check if space exists
    try:
        api.repo_info(repo_id=repo_id, repo_type='space')
        print(f"   ✅ Space exists")
    except Exception:
        print(f"   📝 Creating space...")
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type='space',
                space_sdk=space_config.get('sdk', 'docker'),
                private=False,
                exist_ok=True
            )
            print(f"   ✅ Space created")
            time.sleep(2)
        except Exception as e:
            print(f"   ❌ Failed to create space: {e}")
            return False
    
    # Upload files
    print(f"\n📤 Uploading files...")
    upload_success = 0
    for file_name in files:
        file_path = local_path / file_name
        if file_path.exists():
            if upload_file(api, repo_id, file_path, file_name):
                upload_success += 1
        else:
            print(f"   ⚠️  Missing: {file_name}")
    
    print(f"\n📊 Files: {upload_success}/{len(files)} uploaded")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Complete TILLU deployment to HuggingFace Spaces")
    parser.add_argument("--token", required=True, help="HuggingFace API token")
    parser.add_argument("--skip-secrets", action="store_true", help="Skip setting secrets")
    parser.add_argument("--skip-upload", action="store_true", help="Skip file upload (only set secrets)")
    args = parser.parse_args()
    
    # Initialize API
    try:
        api = HfApi(token=args.token)
        user = api.whoami()
        print(f"\n✅ Logged in as: {user['name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    base_path = pathlib.Path(__file__).parent.parent
    
    # Define spaces to deploy
    spaces = {
        'TILLU Gateway': {
            'repo_id': 'tillu-AI/tillu-gateway',
            'local_path': base_path / 'deployments' / 'huggingface' / 'tillu-gateway',
            'files': ['streamlit_app.py', 'requirements.txt', 'README.md', 'Dockerfile'],
            'sdk': 'docker'
        },
        'TILLU Backend': {
            'repo_id': 'tillu-AI/tillu-backend',
            'local_path': base_path / 'deployments' / 'huggingface' / 'tillu-backend',
            'files': ['app.py', 'requirements.txt', 'README.md', 'Dockerfile'],
            'sdk': 'docker'
        }
    }
    
    # Environment file
    env_path = base_path / '.env.hf-spaces'
    
    print("\n" + "="*60)
    print("TILLU COMPLETE DEPLOYMENT")
    print("="*60)
    
    # Phase 1: Deploy spaces
    if not args.skip_upload:
        print("\n📍 PHASE 1: Deploying Spaces")
        print("="*60)
        
        for space_name, space_config in spaces.items():
            deploy_space(api, space_name, space_config, args.token)
    
    # Phase 2: Set secrets for backend
    if not args.skip_secrets:
        print("\n" + "="*60)
        print("🔐 PHASE 2: Setting Environment Variables")
        print("="*60)
        
        if env_path.exists():
            print(f"\n📄 Reading from: {env_path}")
            secrets = parse_env_file(env_path)
            print(f"📋 Found {len(secrets)} secrets")
            
            # Set secrets for backend (main backend needs all secrets)
            backend_repo = spaces['TILLU Backend']['repo_id']
            set_space_secrets(api, backend_repo, secrets)
            
            # Set minimal secrets for gateway
            print(f"\n🔐 Setting secrets for TILLU Gateway...")
            gateway_secrets = {
                'TILLU_API_URL': 'https://tillu-ai-tillu-backend.hf.space'
            }
            set_space_secrets(api, spaces['TILLU Gateway']['repo_id'], gateway_secrets)
        else:
            print(f"❌ Environment file not found: {env_path}")
            print("   Run: python scripts/set_hf_secrets.py separately")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print("\n🌐 Space URLs:")
    for space_name, space_config in spaces.items():
        space_url = f"https://huggingface.co/spaces/{space_config['repo_id']}"
        print(f"   • {space_name}: {space_url}")
    
    print("\n🚀 Next Steps:")
    print("   1. Wait 2-5 minutes for spaces to build")
    print("   2. Test backend: curl https://tillu-ai-tillu-backend.hf.space/health")
    print("   3. Open gateway: https://tillu-ai-tillu-gateway.hf.space")
    print("   4. Test connection in gateway UI")
    
    print("\n📊 Management:")
    print("   • Backend logs: https://huggingface.co/spaces/tillu-AI/tillu-backend/logs")
    print("   • Gateway logs: https://huggingface.co/spaces/tillu-AI/tillu-gateway/logs")
    print("   • Backend secrets: https://huggingface.co/spaces/tillu-AI/tillu-backend/settings")
    print("   • Gateway secrets: https://huggingface.co/spaces/tillu-AI/tillu-gateway/settings")
    
    print("\n⏱️  Build Status:")
    print("   Spaces are building now (2-5 minutes)")
    print("   Check status at the URLs above")
    
    print()

if __name__ == "__main__":
    main()
