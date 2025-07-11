"""
Test script to verify all dependencies are working correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        import tkinter as tk
        print("✅ tkinter imported successfully")
        
        import customtkinter as ctk
        print("✅ customtkinter imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        from PIL import Image
        print("✅ Pillow imported successfully")
        
        import subprocess
        print("✅ subprocess imported successfully")
        
        import threading
        print("✅ threading imported successfully")
        
        import json
        print("✅ json imported successfully")
        
        print("\n🎉 All dependencies are working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_streamlink():
    """Test if Streamlink is installed and accessible"""
    try:
        import subprocess
        result = subprocess.run(
            ["streamlink", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Streamlink found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Streamlink not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Streamlink not found in PATH")
        print("💡 Install with: pip install streamlink")
        return False

def test_gui():
    """Test if GUI can be created"""
    try:
        import customtkinter as ctk
        
        # Test creating a simple window
        root = ctk.CTk()
        root.title("Test Window")
        root.geometry("300x200")
        
        label = ctk.CTkLabel(root, text="GUI Test Successful!")
        label.pack(pady=20)
        
        # Don't show the window, just test creation
        root.after(100, root.destroy)  # Close after 100ms
        
        print("✅ GUI creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Streamlink Maski Dependencies\n")
    
    imports_ok = test_imports()
    streamlink_ok = test_streamlink()
    gui_ok = test_gui()
    
    print(f"\n📊 Test Results:")
    print(f"   Dependencies: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Streamlink:   {'✅ PASS' if streamlink_ok else '❌ FAIL'}")
    print(f"   GUI:          {'✅ PASS' if gui_ok else '❌ FAIL'}")
    
    if imports_ok and gui_ok:
        print(f"\n🎯 Ready to run: python main.py")
        if not streamlink_ok:
            print("⚠️  Note: Install Streamlink to stream videos")
    else:
        print(f"\n❌ Please fix the failing tests before running the app")
