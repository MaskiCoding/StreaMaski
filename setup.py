#!/usr/bin/env python3
"""
Setup script for Streamlink Maski
Installs dependencies and prepares the environment
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_streamlink():
    """Check if Streamlink is available"""
    print("🔍 Checking Streamlink installation...")
    try:
        result = subprocess.run(["streamlink", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Streamlink found: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Streamlink not found in PATH")
            return False
    except FileNotFoundError:
        print("⚠️  Streamlink not found")
        return False

def main():
    """Main setup process"""
    print("🚀 Setting up Streamlink Maski...")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please run this script from the project root directory.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check Streamlink
    streamlink_ok = check_streamlink()
    
    print("\n" + "=" * 40)
    if streamlink_ok:
        print("🎉 Setup completed successfully!")
        print("You can now run: python main.py")
    else:
        print("⚠️  Setup completed with warnings!")
        print("Please install Streamlink from: https://streamlink.github.io/install.html")
        print("Then you can run: python main.py")
    
    print("\n📖 For building an executable, see: build/BUILD.md")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
