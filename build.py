#!/usr/bin/env python3
"""
Build script for StreaMaski executable
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_files():
    """Clean up build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['StreaMaski.exe']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Cleaned {file_name}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("========================================")
    print("    Building StreaMaski Executable")
    print("========================================")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    clean_build_files()
    
    # Build with PyInstaller
    print("\nBuilding with PyInstaller...")
    
    # Use the virtual environment's PyInstaller
    pyinstaller_path = Path(".venv/Scripts/pyinstaller.exe")
    if not pyinstaller_path.exists():
        print("Error: PyInstaller not found in virtual environment!")
        return False
    
    try:
        result = subprocess.run([
            str(pyinstaller_path),
            "--clean",
            "--noconfirm", 
            "StreaMaski.spec"
        ], check=True, capture_output=True, text=True)
        
        print("PyInstaller output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print("Error output:")
        print(e.stderr)
        return False
    
    # Move executable to main directory
    exe_path = Path("dist/StreaMaski.exe")
    if exe_path.exists():
        shutil.move(str(exe_path), "StreaMaski.exe")
        print("\n========================================")
        print("    BUILD SUCCESSFUL!")
        print("========================================")
        
        # Show file size
        size = os.path.getsize("StreaMaski.exe")
        print(f"\nThe executable 'StreaMaski.exe' has been created.")
        print(f"Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        print("\nYou can now run the application by double-clicking StreaMaski.exe")
        
        # Clean up build files (but keep the exe)
        print("\nCleaning up build files...")
        dirs_to_clean = ['build', 'dist']
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name}/")
        
        return True
    else:
        print("\n========================================")
        print("    BUILD FAILED!")
        print("========================================")
        print("\nExecutable not found in dist/ directory.")
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
