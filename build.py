#!/usr/bin/env python3
"""
Build script for StreaMaski
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    print("🎭 Building StreaMaski v3.0.0...")
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous build
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=StreaMaski",
        "--icon=Icon.ico",
        "--add-data=Icon.ico;.",
        "main.py"
    ]
    
    print("🔨 Building executable...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print(f"📁 Executable created: dist/StreaMaski.exe")
        
        # Clean up build artifacts
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("StreaMaski.spec"):
            os.remove("StreaMaski.spec")
            
        # Get file size
        exe_path = Path("dist/StreaMaski.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
    else:
        print("❌ Build failed!")
        print(result.stderr)
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
