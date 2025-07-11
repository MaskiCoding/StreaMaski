#!/usr/bin/env python3
"""
Comprehensive test script for Streamlink Maski
Tests all major functionality before building the executable
"""

import sys
import os
import subprocess
import time
from main import URLValidator, StreamlinkService, SettingsManager, QuickSwapManager

def test_url_validation():
    """Test URL validation including 3-character usernames"""
    print("=" * 50)
    print("Testing URL Validation")
    print("=" * 50)
    
    test_cases = [
        ("https://www.twitch.tv/xqc", True, "3-character username"),
        ("https://www.twitch.tv/abc", True, "3-character username"),
        ("https://www.twitch.tv/ab", False, "2-character username (should fail)"),
        ("https://www.twitch.tv/a", False, "1-character username (should fail)"),
        ("https://www.twitch.tv/summit1g", True, "Normal username"),
        ("https://twitch.tv/pokimane", True, "Without www"),
        ("http://www.twitch.tv/shroud", True, "HTTP instead of HTTPS"),
        ("not-a-url", False, "Invalid URL"),
        ("https://youtube.com/watch", False, "Wrong platform"),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected_valid, description in test_cases:
        is_valid, error_msg = URLValidator.validate(url)
        
        if is_valid == expected_valid:
            print(f"✓ PASS: {description}")
            passed += 1
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Expected: {expected_valid}, Got: {is_valid}")
            if error_msg:
                print(f"  Error: {error_msg}")
            failed += 1
    
    print(f"\nURL Validation Results: {passed} passed, {failed} failed")
    return failed == 0

def test_streamlink_service():
    """Test Streamlink service availability"""
    print("\n" + "=" * 50)
    print("Testing Streamlink Service")
    print("=" * 50)
    
    service = StreamlinkService()
    
    print(f"Streamlink path: {service.path}")
    print(f"Streamlink available: {service.is_available()}")
    
    if service.is_available():
        # Test command creation
        cmd = service.create_command("https://www.twitch.tv/xqc", "best")
        print(f"Sample command: {' '.join(cmd)}")
        print("✓ Streamlink service is working")
        return True
    else:
        print("✗ Streamlink service is not available")
        return False

def test_settings_manager():
    """Test settings management"""
    print("\n" + "=" * 50)
    print("Testing Settings Manager")
    print("=" * 50)
    
    # Use a test settings file
    test_settings_file = "test_settings.json"
    
    try:
        settings = SettingsManager(test_settings_file)
        
        # Test setting and getting values
        settings.set("test_key", "test_value")
        value = settings.get("test_key")
        
        if value == "test_value":
            print("✓ Settings save/load working")
            
            # Test URL validation in settings
            settings.set("last_url", "https://www.twitch.tv/xqc")
            url = settings.get("last_url")
            is_valid, _ = URLValidator.validate(url)
            
            if is_valid:
                print("✓ URL validation in settings working")
                return True
            else:
                print("✗ URL validation in settings failed")
                return False
        else:
            print("✗ Settings save/load failed")
            return False
            
    except Exception as e:
        print(f"✗ Settings manager error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_settings_file):
            os.remove(test_settings_file)

def test_quick_swap_manager():
    """Test quick swap functionality"""
    print("\n" + "=" * 50)
    print("Testing Quick Swap Manager")
    print("=" * 50)
    
    # Use a test settings file
    test_settings_file = "test_quickswap_settings.json"
    
    try:
        settings = SettingsManager(test_settings_file)
        quick_swap = QuickSwapManager(settings)
        
        # Test adding streams
        test_urls = [
            "https://www.twitch.tv/xqc",
            "https://www.twitch.tv/summit1g",
            "https://www.twitch.tv/pokimane"
        ]
        
        for url in test_urls:
            result = quick_swap.add_stream(url)
            if result:
                print(f"✓ Added stream: {URLValidator.extract_streamer_name(url)}")
            else:
                print(f"✗ Failed to add stream: {url}")
                return False
        
        # Test getting streams
        streams = quick_swap.get_streams()
        if len(streams) == 3:
            print("✓ Quick swap retrieval working")
            
            # Test removing a stream
            if quick_swap.remove_by_index(0):
                print("✓ Stream removal working")
                return True
            else:
                print("✗ Stream removal failed")
                return False
        else:
            print(f"✗ Expected 3 streams, got {len(streams)}")
            return False
            
    except Exception as e:
        print(f"✗ Quick swap manager error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_settings_file):
            os.remove(test_settings_file)

def main():
    """Run all tests"""
    print("🎭 Streamlink Maski - Comprehensive Testing")
    print("=" * 60)
    
    tests = [
        ("URL Validation", test_url_validation),
        ("Streamlink Service", test_streamlink_service),
        ("Settings Manager", test_settings_manager),
        ("Quick Swap Manager", test_quick_swap_manager),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"\n✓ {test_name}: PASSED")
            else:
                print(f"\n✗ {test_name}: FAILED")
        except Exception as e:
            print(f"\n✗ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Ready to build executable.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before building.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
