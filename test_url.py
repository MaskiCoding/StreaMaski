#!/usr/bin/env python3

from main import URLValidator

# Test URLs
test_urls = [
    "https://www.twitch.tv/xqc",
    "https://twitch.tv/xqc", 
    "http://www.twitch.tv/xqc",
    "https://www.twitch.tv/xqcow",
    "https://www.twitch.tv/a",     # 1 char (should fail)
    "https://www.twitch.tv/ab",    # 2 chars (should fail)
    "https://www.twitch.tv/abc",   # 3 chars (should pass)
    "https://www.twitch.tv/abcd",  # 4 chars (should pass)
]

print("Testing URL validation:")
print("=" * 50)

for url in test_urls:
    is_valid, error = URLValidator.validate(url)
    streamer_name = URLValidator.extract_streamer_name(url) if is_valid else ""
    status = "✓ PASS" if is_valid else "✗ FAIL"
    
    print(f"{status} | {url}")
    if not is_valid:
        print(f"     Error: {error}")
    else:
        print(f"     Streamer: {streamer_name}")
    print()
