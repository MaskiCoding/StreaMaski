#!/usr/bin/env python3
"""
Build script for Streamlink Maski - Monolithic version
"""

import subprocess
import sys
import os

def build_executable():
    """Build the executable from main.py"""
    print("Building Streamlink Maski...")
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "Streamlink Maski",
        "main.py",
        "--clean"
    ]
    
    print("Running:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable location: {os.path.abspath('dist/Streamlink Maski.exe')}")
        
        # Show file size
        exe_path = "dist/Streamlink Maski.exe"
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            print(f"File size: {size / 1024 / 1024:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    
    return True

if __name__ == "__main__":
    build_executable()
