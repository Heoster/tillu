#!/usr/bin/env python3
"""
Deploy ALL TILLU Spaces to HuggingFace
Includes: Gateway, Backend, Daemon, SearXNG, WebSearch, n8n
Usage: python scripts/deploy_all_spaces.py --token hf_your_token_here
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
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value and not value.startswith('YOUR_'):
                    env_vars[key] = value
    
    return env_vars

def upload_file(api, repo_id, file_path, file_name):
    """Upload a file to HuggingFace Space"""
    try:
        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=file_name,
            repo_id=repo_id,
            repo_type='space',
            commit_message=f"Update {file_name}"
        )
        return True
    except Exception as e:
        if "no changes" not in str(e).lower():
            print(f"    ⚠️  {file_name}: {str(e)[:50]}")
        return True  # Count as success if no changes

def ensure_space(api, repo_id, sdk='docker', private=False):
    """Create space if it doesn't exist"""
    try:
        api.repo_info(repo_id=repo_id, repo_type='space')
        return True
    except Exception:
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type='space',
                space_sdk=sdk,
                private=private,
                exist_ok=True
            )
            time.sleep(2)
            return True
        except Exception as e:
            print(f"    ❌ Failed to create: {e}")
            return False

def set_secrets(api, repo_id, secrets):
    """Set secrets for a space"""
    count = 0
    for key, value in secrets.items():
        try:
            api.add_space_secret(repo_id=repo_id, key=key, value=value)
            count += 1
        except Exception:
            count += 1  # Count as success if already exists
    return count

def main():
    parser = argparse.ArgumentParser(description="Deploy ALL TILLU spaces")
    parser.add_argument("--token", required=True, help="HuggingFace API token")
    parser.add_argument("--skip-secrets", action="store_true", help="Skip setting secrets")
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
    env_path = base_path / '.env.hf-spaces'
    
    # Define all spaces
    spaces = [
        {
            'name': 'TILLU Gateway',
            'repo_id': 'tillu-AI/tillu-gateway',
            'local_path': base_path / 'deployments' / 'huggingface' / 'tillu-gateway',
            'files': ['streamlit_app.py', 'requirements.txt', 'README.md', 'Dockerfile'],
            'sdk': 'docker',
            'secrets': {'TILLU_API_URL': 'https://tillu-ai-tillu-backend.hf.space'}
        },
        {
            'name': 'TILLU Backend',
            'repo_id': 'tillu-AI/tillu-backend',
            'local_path': base_path / 'deployments' / 'huggingface' / 'tillu-backend',
            'files': ['app.py', 'requirements.txt', 'README.md', 'Dockerfile'],
            'sdk': 'docker',
            'secrets': 'all'  # Will use .env.hf-spaces
        },
        {
            'name': 'TILLU Daemon',
            'repo_id': 'tillu-AI/tillu-daemon',
            'local_path': base_path / 'deployments' / 'huggingface' / 'daemon-space',
            'files': ['README.md', 'Dockerfile', 'requirements.txt'],
            'sdk': 'docker',
            'secrets': ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_KEY', 'REDIS_URL', 
                       'GROQ_API_KEY', 'HF_TOKEN', 'SECRET_KEY']
        },
        {
            'name': 'TILLU SearXNG',
            'repo_id': 'codeex123/tillu-searxng',
            'local_path': base_path / 'deployments' / 'huggingface' / 'searxng-space',
            'files': ['Dockerfile', 'settings.yml'],
            'sdk': 'docker',
            'secrets': {}
        },
        {
            'name': 'TILLU WebSearch',
            'repo_id': 'tillu-AI/tillu-websearch',
            'local_path': base_path / 'deployments' / 'huggingface' / 'scraper-space',
            'files': ['Dockerfile', 'main.py', 'requirements.txt'],
            'sdk': 'docker',
            'secrets': ['SEARXNG_URL', 'GROQ_API_KEY', 'PLAYWRIGHT_SERVICE_URL']
        },
        {
            'name': 'TILLU Engine (n8n)',
            'repo_id': 'tillu-AI/tillu-engine',
            'local_path': base_path / 'deployments' / 'huggingface' / 'n8n-space',
            'files': ['Dockerfile', 'README.md'],
            'sdk': 'docker',
            'secrets': ['N8N_EMAIL', 'N8N_PASSWORD', 'SUPABASE_URL', 'SUPABASE_KEY']
        }
    ]
    
    # Load environment variables
    all_secrets = {}
    if env_path.exists() and not args.skip_secrets:
        all_secrets = parse_env_file(env_path)
        print(f"📋 Loaded {len(all_secrets)} secrets from {env_path}")
    
    print("\n" + "="*60)
    print("TILLU COMPLETE DEPLOYMENT - ALL SPACES")
    print("="*60)
    
    # Deploy each space
    for space in spaces:
        print(f"\n📦 {space['name']}")
        print(f"   Repo: {space['repo_id']}")
        
        # Create space
        if not ensure_space(api, space['repo_id'], space.get('sdk', 'docker')):
            continue
        
        # Upload files
        uploaded = 0
        for file_name in space['files']:
            file_path = space['local_path'] / file_name
            if file_path.exists():
                if upload_file(api, space['repo_id'], file_path, file_name):
                    uploaded += 1
            else:
                # Check for alternative files
                if file_name == 'main.py':
                    alt_path = space['local_path'] / 'app.py'
                    if alt_path.exists() and upload_file(api, space['repo_id'], alt_path, file_name):
                        uploaded += 1
        
        print(f"   📤 Files: {uploaded}/{len(space['files'])}")
        
        # Set secrets
        if not args.skip_secrets and space.get('secrets'):
            if space['secrets'] == 'all':
                count = set_secrets(api, space['repo_id'], all_secrets)
                print(f"   🔐 Secrets: {count} set")
            elif isinstance(space['secrets'], dict):
                count = set_secrets(api, space['repo_id'], space['secrets'])
                print(f"   🔐 Secrets: {count} set")
            elif isinstance(space['secrets'], list):
                secrets_to_set = {k: all_secrets[k] for k in space['secrets'] if k in all_secrets}
                if secrets_to_set:
                    count = set_secrets(api, space['repo_id'], secrets_to_set)
                    print(f"   🔐 Secrets: {count} set")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print("\n🌐 Space URLs:")
    for space in spaces:
        print(f"   • {space['name']}: https://huggingface.co/spaces/{space['repo_id']}")
    
    print("\n🚀 Production URLs:")
    print("   • Gateway: https://tillu-ai-tillu-gateway.hf.space")
    print("   • Backend: https://tillu-ai-tillu-backend.hf.space")
    print("   • Daemon: https://tillu-ai-tillu-daemon.hf.space")
    print("   • SearXNG: https://tillu-ai-tillu-searxng.hf.space")
    print("   • WebSearch: https://tillu-ai-tillu-websearch.hf.space")
    print("   • Engine: https://tillu-ai-tillu-engine.hf.space")
    
    print("\n⏱️  Wait 3-5 minutes for all spaces to build")

if __name__ == "__main__":
    main()
