# Streamlink Maski - Installation Guide

## Prerequisites

Before running the application, you need to install:

1. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
2. **Streamlink** - Install with: `pip install streamlink`

## Quick Start

### Option 1: Run from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2: Build Executable
```bash
# Run the build script (Windows)
build.bat

# Or manually build
pip install pyinstaller
pyinstaller --onefile --windowed --name="StreamlinkMaski" main.py
```

## Features Implemented

✅ **Core Features:**
- Beautiful Rose Pine-themed dark UI
- Twitch URL input with validation
- Quality selection dropdown
- Background streaming (no terminal window)
- Stream switching with clean process termination
- Settings persistence
- Error handling and user feedback

✅ **Technical Features:**
- Minimal dependencies (only customtkinter, requests, Pillow)
- Low memory footprint
- Clean process management
- Windows-optimized build scripts
- Proper threading for non-blocking UI

🔄 **Coming Soon:**
- Twitch OAuth integration
- Followed channels display
- Stream history
- Custom quality presets

## Usage

1. **Launch the application**
2. **Enter a Twitch URL** (e.g., `https://www.twitch.tv/streamer_name`)
3. **Select quality** from the dropdown
4. **Click "Watch Stream"** to start
5. **Use "Switch Stream"** to change streams

## Building for Distribution

The application is designed to be easily compiled into a standalone executable:

```bash
# Build single executable
pyinstaller --onefile --windowed --name="StreamlinkMaski" main.py

# The executable will be in: dist/StreamlinkMaski.exe
```

## Dependencies

- **customtkinter**: Modern UI framework (5.2.2)
- **requests**: HTTP library for API calls (2.31.0)
- **Pillow**: Image processing (10.0.1)

All dependencies are lightweight and the final executable is typically under 50MB.

## Troubleshooting

### "Streamlink not found" error
- Install Streamlink: `pip install streamlink`
- Ensure it's in your PATH: `streamlink --version`

### Build issues
- Update pip: `pip install --upgrade pip`
- Clear build cache: Delete `build/` and `dist/` folders
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Architecture

The application uses:
- **tkinter/customtkinter**: Native GUI framework
- **subprocess**: For running Streamlink commands
- **threading**: For non-blocking stream operations
- **requests**: For future Twitch API integration

This ensures minimal dependencies while maintaining a professional look and feel.
