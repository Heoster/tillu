#!/usr/bin/env python3
"""Upload startup.sh to n8n HuggingFace Space"""

from huggingface_hub import HfApi

api = HfApi(token='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')

# Upload startup.sh
api.upload_file(
    path_or_fileobj='deployments/huggingface/n8n-space/startup.sh',
    path_in_repo='startup.sh',
    repo_id='tillu-AI/tillu-engine',
    repo_type='space',
    commit_message='Add startup.sh'
)
print('startup.sh uploaded successfully')
