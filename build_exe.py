#!/usr/bin/env python3
"""
Build script for creating Streamlink Maski executable
Run this script to create a standalone executable file
"""

import subprocess
import sys
import os

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        subprocess.run([sys.executable, "-m", "pyinstaller", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True)
        print("PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller")
        return False

def build_executable():
    """Build the executable"""
    print("Building Streamlink Maski executable...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--windowed", 
        "--clean",
        "--name", "Streamlink-Maski",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Executable built successfully!")
        print("📁 Check the 'dist' folder for Streamlink-Maski.exe")
        
        # Check if executable was created
        exe_path = os.path.join("dist", "Streamlink-Maski.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 Executable size: {size_mb:.1f} MB")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to build executable")
        return False

def main():
    """Main build process"""
    print("🎭 Streamlink Maski - Executable Builder")
    print("=" * 40)
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller not found.")
        if not install_pyinstaller():
            print("❌ Cannot proceed without PyInstaller")
            sys.exit(1)
    
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("You can now distribute the executable file.")
    else:
        print("\n💥 Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
