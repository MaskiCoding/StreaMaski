# 🎭 Streamlink Maski - Executable Version

## 📦 **What's Included**

The `Streamlink Maski.exe` file is a standalone executable that includes:
- ✅ All Python dependencies built-in
- ✅ Modern dark GUI with Rose Pine theme
- ✅ Quick swap functionality for 4 favorite streams
- ✅ Completely invisible terminal windows
- ✅ Auto-saving settings
- ✅ Streamlined UI without popup interruptions

## 🚀 **How to Use**

1. **Double-click** `Streamlink Maski.exe` to launch the application
2. **Enter a Twitch URL** (e.g., `https://www.twitch.tv/streamer_name`)
3. **Select video quality** from the dropdown
4. **Click "Watch Stream"** to start streaming
5. **Add streams to Quick Swap** - just click "Add to Quick Swap" (no popups!)
6. **Remove streams** - click the ✕ button (instant removal, no confirmation)

## 📋 **Requirements**

- **Streamlink**: Must be installed separately
  ```bash
  pip install streamlink
  ```
- **Media Player**: VLC, MPV, or similar (for video playback)
- **Windows 10/11**: 64-bit version

## 🎯 **Features**

- **🎬 Stream Watching**: Direct streaming from Twitch
- **🔄 Quick Swap**: Save up to 4 favorite streams
- **⚡ Fast Switching**: Instant switching between streams
- **🎨 Modern UI**: Dark theme with intuitive controls
- **💾 Auto-Save**: Settings persist between sessions
- **🔕 Silent Operation**: No visible terminal windows
- **🚫 No Popups**: Streamlined experience without interrupting dialogs

## 📁 **File Structure**

```
Streamlink Maski/
├── Streamlink Maski.exe    # Main executable (~21MB)
├── settings.json          # Auto-generated settings
└── README_EXECUTABLE.md   # This file
```

## 🔧 **Troubleshooting**

### Application Won't Start
- Ensure you're running on Windows 10/11 64-bit
- Check if Windows Defender or antivirus is blocking the file
- Try running as administrator

### Stream Won't Play
- Verify Streamlink is installed: `streamlink --version`
- Check if you have a media player installed (VLC recommended)
- Ensure the Twitch URL is valid and the stream is live

### Performance Issues
- The executable is ~21MB and may take a moment to start
- Settings are saved automatically in `settings.json`
- Quick swap operations are instant without confirmation dialogs

## 🌟 **Version Information**

- **Version**: 2.0.0
- **Build Date**: July 11, 2025
- **PyInstaller Version**: 6.14.2
- **Python Version**: 3.13.5

## 🎉 **What's New in This Version**

- ✅ **Fixed** all button functionality issues
- ✅ **Removed** "Quick Swap Streams (0/4)" counter text
- ✅ **Eliminated** popup messages for adding/removing streams
- ✅ **Streamlined** quick swap experience
- ✅ **Enhanced** error handling and validation
- ✅ **Improved** code organization and performance

## 🎉 **Ready to Stream!**

Your Streamlink Maski executable is ready to use. Simply double-click and start watching your favorite Twitch streams with a clean, modern interface!
