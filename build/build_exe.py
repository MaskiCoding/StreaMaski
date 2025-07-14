#!/usr/bin/env python3
"""
Build script for creating Streamlink Maski executable
Version: 3.0.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Build configuration
APP_NAME = "Streamlink Maski"
APP_VERSION = "3.0.0"
MAIN_SCRIPT = "../main.py"
ICON_FILE = "../Icon.ico"
BUILD_DIR = "../build"
DIST_DIR = "../dist"
SPEC_FILE = "StreamlinkMaski.spec"

# PyInstaller options
USE_SPEC_FILE = True
SPEC_FILE = "streamlink_maski.spec"

PYINSTALLER_OPTIONS = [
    "--onefile",                    # Create a single executable file
    "--windowed",                   # Don't show console window
    "--name=StreamlinkMaski",       # Executable name
    f"--icon={ICON_FILE}",          # Application icon
    "--add-data=Icon.ico;.",        # Include icon in executable
    "--hidden-import=customtkinter", # Ensure CTk is included
    "--hidden-import=tkinter",      # Ensure tkinter is included
    "--hidden-import=requests",     # Ensure requests is included
    "--hidden-import=subprocess",   # Ensure subprocess is included
    "--hidden-import=threading",    # Ensure threading is included
    "--hidden-import=json",         # Ensure json is included
    "--hidden-import=os",           # Ensure os is included
    "--hidden-import=sys",          # Ensure sys is included
    "--hidden-import=re",           # Ensure re is included
    "--hidden-import=contextlib",   # Ensure contextlib is included
    "--hidden-import=weakref",      # Ensure weakref is included
    "--hidden-import=enum",         # Ensure enum is included
    "--hidden-import=typing",       # Ensure typing is included
    "--clean",                      # Clean build cache
    "--noconfirm",                  # Overwrite without confirmation
    MAIN_SCRIPT
]

def clean_build_directories():
    """Clean build and dist directories"""
    print("🧹 Cleaning build directories...")
    
    for directory in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"   Removed {directory}/")
    
    # Remove spec file if it exists
    if os.path.exists(SPEC_FILE):
        os.remove(SPEC_FILE)
        print(f"   Removed {SPEC_FILE}")

def check_requirements():
    """Check if all required files exist"""
    print("🔍 Checking requirements...")
    
    required_files = [MAIN_SCRIPT, ICON_FILE]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"   ✓ {file} found")
    
    if missing_files:
        print(f"   ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def run_pyinstaller():
    """Run PyInstaller to create executable"""
    print("🔨 Building executable with PyInstaller...")
    
    try:
        # Choose build method
        if USE_SPEC_FILE and os.path.exists(SPEC_FILE):
            print(f"   Using spec file: {SPEC_FILE}")
            cmd = ["pyinstaller", SPEC_FILE]
        else:
            print("   Using command line options")
            cmd = ["pyinstaller"] + PYINSTALLER_OPTIONS
        
        # Run PyInstaller
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("   ✓ PyInstaller completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ PyInstaller failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("   ❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def create_release_package():
    """Create release package with executable and documentation"""
    print("📦 Creating release package...")
    
    exe_path = Path(DIST_DIR) / "StreamlinkMaski.exe"
    if not exe_path.exists():
        print("   ❌ Executable not found in dist directory")
        return False
    
    # Create release directory
    release_dir = Path(f"StreamlinkMaski_v{APP_VERSION}")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # Copy executable
    shutil.copy2(exe_path, release_dir / "StreamlinkMaski.exe")
    print(f"   ✓ Copied executable to {release_dir}")
    
    # Copy documentation files
    docs_to_copy = ["../README.md", "../docs/CHANGELOG.md", "../docs/RELEASE_NOTES.md"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir / os.path.basename(doc))
            print(f"   ✓ Copied {os.path.basename(doc)}")
    
    # Create installation instructions
    install_instructions = f"""# Streamlink Maski v{APP_VERSION} - Installation Instructions

## Quick Start
1. Extract this folder to your desired location
2. Run `StreamlinkMaski.exe`
3. Enter a Twitch stream URL and enjoy!

## Requirements
- Windows 10 or later
- Internet connection
- Streamlink (will be prompted to install if not found)

## Features
- 🎭 Ad-free Twitch streaming
- 🚀 Quick swap between streams
- 🎨 Beautiful Rose Pine theme
- 📊 Stream status checking
- 💾 Settings persistence

## Support
- GitHub: https://github.com/MaskiCoding/streamlink-maski
- Issues: https://github.com/MaskiCoding/streamlink-maski/issues

## Version Information
Version: {APP_VERSION}
Build Date: {Path().cwd().stat().st_mtime}
"""
    
    with open(release_dir / "INSTALL.txt", "w", encoding="utf-8") as f:
        f.write(install_instructions)
    
    print(f"   ✓ Created installation instructions")
    
    # Create ZIP archive
    zip_name = f"StreamlinkMaski_v{APP_VERSION}_Windows"
    shutil.make_archive(zip_name, 'zip', release_dir)
    print(f"   ✓ Created {zip_name}.zip")
    
    return True

def get_executable_info():
    """Get information about the created executable"""
    exe_path = Path(DIST_DIR) / "StreamlinkMaski.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📊 Executable Information:")
        print(f"   📁 Location: {exe_path.absolute()}")
        print(f"   📏 Size: {size_mb:.2f} MB")
        print(f"   🏷️  Version: {APP_VERSION}")
        return True
    return False

def main():
    """Main build process"""
    print(f"🚀 Building {APP_NAME} v{APP_VERSION} executable...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ {MAIN_SCRIPT} not found. Please run this script from the build directory.")
        return False
    
    # Step 1: Clean previous builds
    clean_build_directories()
    
    # Step 2: Check requirements
    if not check_requirements():
        return False
    
    # Step 3: Build executable
    if not run_pyinstaller():
        return False
    
    # Step 4: Get executable info
    if not get_executable_info():
        return False
    
    # Step 5: Create release package
    if not create_release_package():
        return False
    
    print("=" * 50)
    print("🎉 Build completed successfully!")
    print(f"📦 Release package: StreamlinkMaski_v{APP_VERSION}_Windows.zip")
    print(f"🎯 Executable: dist/StreamlinkMaski.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
