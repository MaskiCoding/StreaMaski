# StreaMaski - Ultra-Lightweight Twitch Stream Viewer

![StreaMaski Logo](StreaMaski_icon.ico)

**Version 3.3.0** - A minimal desktop GUI for watching ad-free Twitch streams using Streamlink

## Features

- **🎬 Ultra-Lightweight**: Optimized for minimal memory usage and fast startup
- **🚀 Ad-Free Streaming**: Uses Streamlink with proxy support for ad-free viewing
- **⚡ Quick Swap**: Store up to 4 favorite streams for instant switching
- **🎯 Status Indicators**: Visual dots showing live/offline status of saved streams
- **🔄 Smart Switching**: Seamlessly switch between streams without interruption
- **🎨 Modern UI**: Clean, dark theme with Rose Pine color scheme
- **💾 Settings Persistence**: Remembers your preferences and stream history

## Requirements

- Windows 10/11 (64-bit)
- [Streamlink](https://streamlink.github.io/) installed
- Internet connection

## Installation

1. Download the latest `StreaMaski.exe` from the [Releases](https://github.com/MaskiCoding/StreaMaski/releases) page
2. Install [Streamlink](https://streamlink.github.io/install.html) if not already installed
3. Run `StreaMaski.exe` - no additional installation required!

## Usage

1. **Enter Stream URL**: Paste any Twitch stream URL (e.g., `https://www.twitch.tv/streamer_name`)
2. **Select Quality**: Choose your preferred stream quality (best, 1080p, 720p, etc.)
3. **Watch Stream**: Click "Watch Stream" to start streaming
4. **Add to Quick Swap**: Save frequently watched streams for quick access
5. **Check Status**: Use "Check Status" to see which saved streams are currently live

## Quick Swap Features

- **Status Dots**: 
  - 🟢 Green = Stream is live
  - 🔴 Red = Stream is offline
  - 🟡 Yellow = Checking status
  - ⚫ Black = Unknown status
- **Hover Effects**: Status dots seamlessly match button colors when hovering
- **One-Click Access**: Click any saved stream to instantly switch to it

## Technical Details

- **Memory Optimized**: Uses aggressive optimization techniques for minimal resource usage
- **Lazy Loading**: Modules are loaded only when needed to reduce startup time
- **Singleton Patterns**: Shared resources to minimize memory footprint
- **Thread-Safe**: Proper handling of concurrent operations
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Build from Source

```bash
# Clone the repository
git clone https://github.com/MaskiCoding/StreaMaski.git
cd StreaMaski

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Build executable
pyinstaller StreaMaski.spec
```

## Version History

### v3.3.0 (Current)
- Enhanced status dot system with hover effects
- Improved memory optimization and performance
- Better error handling and user feedback
- Code cleanup and refactoring

### v3.2.0
- Added visual status indicators (dots) for stream status
- Improved UI responsiveness and theme consistency
- Enhanced error handling for network issues

### v3.1.0
- Introduced Quick Swap functionality
- Added stream status checking
- Improved memory management

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or feature requests, please visit the [GitHub Issues](https://github.com/MaskiCoding/StreaMaski/issues) page.

## Credits

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern GUI
- Uses [Streamlink](https://streamlink.github.io/) for stream processing
- Rose Pine color theme for beautiful aesthetics

---

**Made with ❤️ by MaskiCoding**
