#!/usr/bin/env python3

import subprocess
import sys
import os

# Test multiple streamers
def test_multiple_streamers():
    streamers = [
        "xqc",
        "summit1g",
        "pokimane",
        "shroud",
        "lirik"
    ]
    
    for streamer in streamers:
        print(f"\n{'='*50}")
        print(f"Testing: {streamer}")
        print('='*50)
        
        cmd = [
            "streamlink",
            "--twitch-proxy-playlist=https://eu.luminous.dev",
            f"https://www.twitch.tv/{streamer}",
            "best"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=8
            )
            
            print(f"Return code: {result.returncode}")
            if result.returncode == 0:
                print("✓ SUCCESS - Stream found and working!")
            else:
                # Parse the error
                stdout_lines = result.stdout.split('\n')
                error_lines = [line for line in stdout_lines if '[error]' in line or 'error:' in line.lower()]
                
                if error_lines:
                    print(f"✗ ERROR: {error_lines[-1]}")
                else:
                    print(f"✗ FAILED with return code {result.returncode}")
                    
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT after 8 seconds")
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")

if __name__ == "__main__":
    test_multiple_streamers()
