#!/usr/bin/env python3
"""
Set HuggingFace Space Secrets from .env.hf-spaces file
Usage: python scripts/set_hf_secrets.py --token hf_your_token_here --space tillu-AI/tillu-backend
"""

import os
import sys
import argparse
from pathlib import Path
from huggingface_hub import HfApi

# HuggingFace reserved environment variables - DO NOT SET
HF_RESERVED_VARS = {
    'SPACE_ID',           # Automatically set by HF
    'SPACE_AUTHOR_NAME',  # Automatically set by HF
    'SPACE_REPO_NAME',    # Automatically set by HF
    'SPACE_URL',          # May conflict
    'HF_TOKEN',           # Set via HF UI, not secrets
}

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
                
                # Skip reserved HuggingFace variables
                if key in HF_RESERVED_VARS:
                    print(f"  ⚠️  Skipping reserved variable: {key}")
                    continue
                
                env_vars[key] = value
    
    return env_vars

def set_space_secrets(api, space_id, secrets):
    """Set secrets for a HuggingFace Space"""
    print(f"\n📝 Setting secrets for {space_id}...")
    
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
            print(f"  ❌ {key}: {str(e)[:50]}")
            error_count += 1
    
    print(f"\n📊 Results: {success_count} success, {error_count} errors")
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description="Set HuggingFace Space secrets from .env file")
    parser.add_argument("--token", required=True, help="HuggingFace API token")
    parser.add_argument("--space", required=True, help="Space ID (e.g., tillu-AI/tillu-backend)")
    parser.add_argument("--env-file", default=".env.hf-spaces", help="Path to .env file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be set without setting")
    args = parser.parse_args()
    
    # Initialize API
    try:
        api = HfApi(token=args.token)
        user = api.whoami()
        print(f"✅ Logged in as: {user['name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    # Find env file
    base_path = Path(__file__).parent.parent
    env_path = base_path / args.env_file
    
    if not env_path.exists():
        print(f"❌ Environment file not found: {env_path}")
        sys.exit(1)
    
    print(f"📄 Reading from: {env_path}")
    
    # Parse env file
    secrets = parse_env_file(env_path)
    print(f"📋 Found {len(secrets)} secrets to set")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Would set these secrets:")
        for key in sorted(secrets.keys()):
            value = secrets[key]
            # Mask sensitive values
            if 'KEY' in key or 'SECRET' in key or 'TOKEN' in key or 'PASSWORD' in key:
                print(f"  {key} = {'*' * 8}")
            else:
                print(f"  {key} = {value[:30]}{'...' if len(value) > 30 else ''}")
        return
    
    # Set secrets
    success, errors = set_space_secrets(api, args.space, secrets)
    
    if errors > 0:
        sys.exit(1)
    
    print(f"\n✅ Successfully set {success} secrets for {args.space}")
    print(f"\n🌐 Space URL: https://huggingface.co/spaces/{args.space}")
    print(f"⚙️  Manage secrets: https://huggingface.co/spaces/{args.space}/settings")

if __name__ == "__main__":
    main()
