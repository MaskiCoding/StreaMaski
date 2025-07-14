# 🎭 Streamlink Maski

A lightweight desktop GUI for watching **ad-free Twitch streams** using Streamlink with a beautiful Rose Pine theme and advanced stream management features.

## ✨ What it does

**Streamlink Maski** transforms your Twitch viewing experience by:
- 🚫 **Blocking all ads** - No pre-roll, mid-roll, or banner ads
- 🎥 **Direct media player streaming** - Opens streams in VLC, MPV, or your default video player
- 🔄 **Instant stream switching** - Switch between streamers without delay
- 💾 **Quick Swap slots** - Save up to 4 favorite streams for one-click access
- 🔍 **Stream status checking** - Real-time online/offline indicators for saved streams
- 🎯 **Quality control** - Choose from 360p to 1080p60 based on your connection
- 🎭 **Beautiful interface** - Custom Rose Pine dark theme with smooth animations

## 🎮 Key Features

### 🎬 Core Streaming Features
- **Ad-free streaming** - Watch Twitch without any interruptions
- **Quick stream switching** - Seamlessly switch between different streamers
- **Multiple quality options** - 360p, 480p, 720p, 1080p, 1080p60, and more
- **Smart error handling** - User-friendly error messages and automatic recovery

### 🚀 Advanced Stream Management
- **Quick Swap slots** - Save and organize your favorite streams (up to 4)
- **Stream status indicators** - Real-time colored dots showing online/offline status
  - 🟢 Green: Stream is online
  - 🔴 Red: Stream is offline
  - 🟡 Yellow: Status unknown
  - 🟠 Gold: Currently checking status
- **One-click status checking** - Check all saved streams simultaneously
- **Automatic stream validation** - URL validation and normalization

### 🎨 User Interface
- **Rose Pine theme** - Elegant dark interface with custom colors
- **Optimized performance** - Fast startup, low memory usage, responsive UI
- **Windows integration** - High-resolution icons and taskbar optimization
- **Consistent spacing** - Professional layout with standardized button sizes
- **Hover effects** - Smooth transitions and visual feedback

## 🆕 Version 3.0.0 Features

### � Performance Optimizations
- **Enhanced caching system** - Smart cache management with size limits
- **Improved thread management** - Better concurrent stream checking
- **Memory optimization** - Reduced memory footprint and better cleanup
- **Faster startup** - Optimized initialization and loading times

### 🔧 Code Quality Improvements
- **Better error handling** - More specific exception handling with logging
- **Resource management** - Proper cleanup and memory management
- **Type safety** - Comprehensive type hints throughout codebase
- **Maintainable architecture** - Better separation of concerns and modularity

### 🔍 Enhanced Stream Status System
- **Consistent button sizing** - All management buttons are 180px wide
- **Improved spacing** - 15px gaps between all UI sections
- **Better alignment** - Status indicators positioned perfectly in button corners
- **Hover synchronization** - Status indicators match button hover states
- **Professional layout** - Clean, modern design with attention to detail

### 🔧 Technical Improvements
- **Optimized code structure** - Clean, maintainable codebase with DRY principles
- **Better error handling** - Comprehensive error messages and recovery
- **Performance enhancements** - Faster startup and smoother operation
- **Memory optimization** - Efficient resource usage and cleanup

## 📦 Installation & Usage

### 🎯 Quick Start (Recommended)
1. **Download** the latest [Streamlink-Maski.exe](https://github.com/MaskiCoding/streamlink-maski/releases/latest) from releases
2. **Install [Streamlink](https://streamlink.github.io/)** (required dependency)
3. **Run** the executable - no installation needed!

### 🔧 From Source
```bash
# Clone the repository
git clone https://github.com/MaskiCoding/streamlink-maski.git
cd streamlink-maski

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 🚀 Getting Started

### 📥 Option 1: Download Release (Recommended)
1. Go to [Releases](https://github.com/MaskiCoding/streamlink-maski/releases)
2. Download `StreamlinkMaski_v3.0.0_Windows.zip`
3. Extract and run `StreamlinkMaski.exe`
4. Install [Streamlink](https://streamlink.github.io/install.html) when prompted

### 🔧 Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/MaskiCoding/streamlink-maski.git
cd streamlink-maski

# Setup dependencies
python setup.py

# Run the application
python main.py
```

## 🎮 How to Use

### 🎬 Basic Streaming
1. **Enter Twitch URL** - Paste any Twitch stream URL (e.g., `https://www.twitch.tv/streamer_name`)
2. **Select Quality** - Choose from 360p to 1080p60 based on your internet speed
3. **Click "Watch Stream"** - Stream opens in your default video player
4. **Enjoy ad-free streaming!** 🎉

### 💾 Quick Swap Management
1. **Add streams** - Click "Add to Quick Swap" to save current stream
2. **Check status** - Click "Check Status" to see which streams are online
3. **Visual indicators** - Colored dots show stream status:
   - 🟢 **Green**: Stream is online
   - 🔴 **Red**: Stream is offline  
   - 🟡 **Yellow**: Status unknown
   - 🟠 **Gold**: Currently checking
4. **One-click access** - Click any Quick Swap button to instantly switch streams
5. **Remove streams** - Click the ✕ button to remove streams from Quick Swap

### 💡 Pro Tips
- **Status checking**: Use "Check Status" to see which of your saved streamers are live
- **Quality selection**: Start with "best" and adjust if buffering occurs
- **Stream switching**: Use the switch button to change streams without stopping
- **Quick Swap**: Save frequently watched streamers for instant access
- **Keyboard shortcuts**: Close the video player to return to the main interface

## 🔧 Build Your Own Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable with icon
pyinstaller --onefile --windowed --icon=Icon.ico --name="Streamlink-Maski" main.py
```

## 🎯 How It Works

**Streamlink Maski** acts as a bridge between Twitch and your video player:

1. **Input**: You provide a Twitch stream URL
2. **Processing**: Streamlink extracts the direct video stream (bypassing ads)
3. **Proxy**: Uses eu.luminous.dev proxy for enhanced ad-blocking
4. **Output**: Opens the clean stream in your preferred video player

This method ensures **100% ad-free viewing** since the ads are never downloaded or displayed.

## 🎨 Screenshots

The application features a beautiful **Rose Pine** dark theme with:
- Custom color palette for easy viewing
- Smooth animations and transitions  
- High-resolution icons and graphics
- Responsive layout that works on all screen sizes

## 🔧 Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: CustomTkinter
- **HTTP Requests**: Requests library for stream status checking
- **Streaming Engine**: Streamlink
- **Theme**: Rose Pine color scheme
- **Architecture**: Event-driven with async stream management and threading
- **Platform**: Windows 10/11 (primary), macOS, Linux (community tested)

### 🏗️ Architecture Highlights
- **Modular Design**: Separate classes for different functionality
- **Event-Driven**: Callback-based system for stream events
- **Threaded Operations**: Non-blocking UI with background stream checking
- **Caching System**: 60-second cache for stream status to reduce API calls
- **Error Recovery**: Graceful handling of network and stream errors

## 📋 System Requirements

- **Operating System**: Windows 10/11 (recommended), macOS, Linux
- **Python**: 3.8+ (if running from source)
- **Memory**: 50MB RAM during operation
- **Storage**: 25MB free space (executable + settings)
- **Dependencies**: 
  - [Streamlink](https://streamlink.github.io/) (required for streaming)
  - Video player (VLC, MPV, or system default)
  - Internet connection for stream status checking
- **Network**: Stable internet connection for streaming

## 🆘 Troubleshooting

### 🚨 Common Issues

**Stream won't start?**
- Ensure Streamlink is installed and accessible from command line
- Check if the Twitch URL is valid and the stream is live
- Try a different quality setting (start with "best")
- Verify your internet connection is stable

**Status indicators not working?**
- Check your internet connection
- Some streams may have restricted API access
- Status checking has a 60-second cache - wait and try again
- Ensure the Twitch URLs are valid and properly formatted

**Poor performance?**
- Lower the stream quality (720p instead of 1080p)
- Close other applications using bandwidth
- Check your internet connection speed
- Ensure video player is properly configured

**Application crashes?**
- Check if you have Python 3.8+ installed (source version)
- Ensure all dependencies are properly installed
- Check the console for error messages
- Try running as administrator (Windows)

### 🔧 Advanced Troubleshooting

**Stream status shows as offline but stream is live?**
- The stream might have just started (check again in a minute)
- API might be temporarily unavailable
- Try removing and re-adding the stream to Quick Swap

**Video player doesn't open?**
- Ensure you have a compatible video player installed (VLC recommended)
- Check if Streamlink can access your video player
- Try running `streamlink --version` in command prompt

## 🔨 Building from Source

Want to build the executable yourself? It's easy!

### Quick Build (Windows)
```bash
# Clone the repository
git clone https://github.com/MaskiCoding/streamlink-maski.git
cd streamlink-maski

# Run the build script
cd build
build.bat
```

### Manual Build
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
cd build
python build_exe.py
```

The executable will be created in the `dist/` folder, and a complete release package will be generated as `StreamlinkMaski_v3.0.0_Windows.zip`.

For detailed build instructions, see [`build/BUILD.md`](build/BUILD.md).

## 📁 Repository Structure

```
streamlink-maski/
├── main.py              # Main application
├── Icon.ico             # Application icon
├── requirements.txt     # Dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
├── docs/               # Documentation
│   ├── CHANGELOG.md    # Version history
│   └── RELEASE_NOTES.md # Release information
├── build/              # Build system
│   ├── build_exe.py    # Build script
│   ├── build.bat       # Windows build script
│   ├── StreamlinkMaski.spec # PyInstaller config
│   ├── version_info.py # Windows version info
│   └── BUILD.md        # Build documentation
└── .github/            # GitHub Actions
    └── workflows/
        └── build.yml   # Automated builds
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**🎭 Enjoy ad-free Twitch streaming with Streamlink Maski!**

*Built with ❤️ by [MaskiCoding](https://github.com/MaskiCoding)*
