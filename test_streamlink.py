#!/usr/bin/env python3

import subprocess
import sys
import os

# Test streamlink command directly
def test_streamlink_command():
    # Command that should be executed
    cmd = [
        "streamlink",
        "--twitch-proxy-playlist=https://eu.luminous.dev",
        "https://www.twitch.tv/xqc",
        "best"
    ]
    
    print("Testing streamlink command:")
    print(" ".join(cmd))
    print("-" * 50)
    
    try:
        # Run the command with output capture
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Command timed out after 10 seconds")
    except FileNotFoundError:
        print("streamlink command not found")
    except Exception as e:
        print(f"Error running command: {e}")

if __name__ == "__main__":
    test_streamlink_command()
