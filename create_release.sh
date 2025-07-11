#!/bin/bash
# GitHub Release Script for Streamlink Maski
# This script helps create a GitHub release with the executable

echo "🎭 Streamlink Maski - GitHub Release Helper"
echo "==========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Please install it from: https://cli.github.com/"
    echo ""
    echo "Alternative: Create release manually at:"
    echo "https://github.com/MaskiCoding/streamlink-maski/releases/new"
    echo ""
    exit 1
fi

echo "✅ GitHub CLI found!"
echo ""

# Create the release
echo "📦 Creating GitHub release v2.0.0..."

gh release create v2.0.0 \
    --title "Streamlink Maski v2.0.0 - Performance Optimized" \
    --notes-file RELEASE_NOTES.md \
    ./dist/Streamlink-Maski.exe

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Release created successfully!"
    echo "🔗 View release: https://github.com/MaskiCoding/streamlink-maski/releases/tag/v2.0.0"
    echo ""
    echo "Users can now download the executable directly from GitHub!"
else
    echo ""
    echo "❌ Failed to create release. Please create it manually at:"
    echo "https://github.com/MaskiCoding/streamlink-maski/releases/new"
    echo ""
    echo "Upload file: ./dist/Streamlink-Maski.exe"
fi
