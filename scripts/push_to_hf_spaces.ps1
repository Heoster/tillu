# Push TILLU Gateway to HuggingFace Spaces
# Usage: .\push_to_hf_spaces.ps1 -HFToken "your_token" -HFUsername "tillu-AI"

param(
    [string]$HFToken = $env:HF_TOKEN,
    [string]$HFUsername = "tillu-AI",
    [string]$SpaceName = "tillu-gateway"
)

if (-not $HFToken) {
    Write-Host "❌ Error: HF_TOKEN not provided" -ForegroundColor Red
    exit 1
}

$SpaceId = "$HFUsername/$SpaceName"
$SpaceUrl = "https://huggingface.co/spaces/$SpaceId"
$GitUrl = "https://huggingface.co/spaces/$SpaceId"
$TempDir = "$env:TEMP\tillu-hf-space"
$GatewayDir = "deployments\huggingface\tillu-gateway"

Write-Host "🚀 TILLU Gateway - HuggingFace Spaces Deployment" -ForegroundColor Cyan
Write-Host "=" * 60

# Create temp directory
Write-Host "`n📁 Setting up temporary directory..."
if (Test-Path $TempDir) {
    Remove-Item -Recurse -Force $TempDir
}
New-Item -ItemType Directory -Path $TempDir | Out-Null
Write-Host "✅ Created: $TempDir"

# Clone Space repo
Write-Host "`n📥 Cloning Space repository..."
$env:GIT_ASKPASS = "echo"
$env:GIT_ASKPASS_RESULT = $HFToken

try {
    Push-Location $TempDir
    
    # Use git clone with token
    $CloneUrl = "https://user:$HFToken@huggingface.co/spaces/$SpaceId"
    git clone $CloneUrl . 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Space doesn't exist yet, creating..." -ForegroundColor Yellow
        # Create empty repo
        git init
        git config user.email "tillu@ai.com"
        git config user.name "TILLU AI"
    }
    
    Write-Host "✅ Repository ready"
} catch {
    Write-Host "❌ Failed to clone: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Copy files
Write-Host "`n📤 Copying gateway files..."
$SourceDir = Resolve-Path "..\..\$GatewayDir"

foreach ($file in @("app.py", "requirements.txt", "README.md", "Dockerfile")) {
    $source = Join-Path $SourceDir $file
    $dest = Join-Path $TempDir $file
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Force
        Write-Host "✅ Copied: $file"
    } else {
        Write-Host "⚠️  Skipped: $file (not found)" -ForegroundColor Yellow
    }
}

# Create .gitattributes for line endings
Write-Host "`n🔧 Configuring git..."
$gitattributes = @"
* text=auto
*.py text eol=lf
*.sh text eol=lf
Dockerfile text eol=lf
*.md text eol=lf
*.txt text eol=lf
"@
$gitattributes | Out-File -FilePath (Join-Path $TempDir ".gitattributes") -Encoding UTF8

# Commit and push
Write-Host "`n📝 Committing changes..."
git add -A
git commit -m "TILLU Gateway - Streamlit interface for personal AI backend" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes committed"
} else {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
}

Write-Host "`n🚀 Pushing to HuggingFace Spaces..."
git push -u origin main 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pushed successfully"
} else {
    Write-Host "❌ Push failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Print summary
Write-Host "`n" + "=" * 60
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n🌐 Space URL: $SpaceUrl"
Write-Host "`n📝 Next steps:"
Write-Host "   1. Wait 2-3 minutes for Space to build"
Write-Host "   2. Open the Space URL above"
Write-Host "   3. Add secret in Space settings:"
Write-Host "      - Name: TILLU_API_URL"
Write-Host "      - Value: https://tillu-backend.onrender.com"
Write-Host "   4. Test connection in sidebar"
Write-Host "   5. Should see '✅ Connected to TILLU backend'"
Write-Host "`n💡 If connection fails:"
Write-Host "   - Check backend: https://tillu-backend.onrender.com/health"
Write-Host "   - Verify TILLU_API_URL secret is set"
Write-Host "   - Check Space logs for errors"
Write-Host "`n"

# Cleanup
Write-Host "🧹 Cleaning up temporary files..."
Remove-Item -Recurse -Force $TempDir
Write-Host "✅ Done"
