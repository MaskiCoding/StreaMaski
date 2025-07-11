# GitHub Release Script for Streamlink Maski (PowerShell)
# This script helps create a GitHub release with the executable

Write-Host "🎭 Streamlink Maski - GitHub Release Helper" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check if gh CLI is installed
try {
    $ghVersion = gh --version
    Write-Host "✅ GitHub CLI found!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ GitHub CLI not found. Please install it from: https://cli.github.com/" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Create release manually at:" -ForegroundColor Yellow
    Write-Host "https://github.com/MaskiCoding/streamlink-maski/releases/new" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Upload file: .\dist\Streamlink-Maski.exe" -ForegroundColor Yellow
    exit 1
}

# Check if executable exists
if (-not (Test-Path ".\dist\Streamlink-Maski.exe")) {
    Write-Host "❌ Executable not found at .\dist\Streamlink-Maski.exe" -ForegroundColor Red
    Write-Host "Please run the build script first: python build_exe.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Creating GitHub release v2.0.0..." -ForegroundColor Blue
Write-Host ""

# Create the release
try {
    gh release create v2.0.0 --title "Streamlink Maski v2.0.0 - Performance Optimized" --notes-file RELEASE_NOTES.md ".\dist\Streamlink-Maski.exe"
    
    Write-Host ""
    Write-Host "🎉 Release created successfully!" -ForegroundColor Green
    Write-Host "🔗 View release: https://github.com/MaskiCoding/streamlink-maski/releases/tag/v2.0.0" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Users can now download the executable directly from GitHub!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Failed to create release. Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create it manually at:" -ForegroundColor Yellow
    Write-Host "https://github.com/MaskiCoding/streamlink-maski/releases/new" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Upload file: .\dist\Streamlink-Maski.exe" -ForegroundColor Yellow
}
