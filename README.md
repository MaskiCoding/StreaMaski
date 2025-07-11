# 🎭 Streamlink Maski

A lightweight desktop GUI for watching **ad-free Twitch streams** using Streamlink with a beautiful Rose Pine theme.

## ✨ What it does

**Streamlink Maski** transforms your Twitch viewing experience by:
- 🚫 **Blocking all ads** - No pre-roll, mid-roll, or banner ads
- 🎥 **Direct media player streaming** - Opens streams in VLC, MPV, or your default video player
- 🔄 **Instant stream switching** - Switch between streamers without delay
- 💾 **Quick Swap slots** - Save up to 4 favorite streams for one-click access
- � **Quality control** - Choose from 360p to 1080p60 based on your connection
- 🎭 **Beautiful interface** - Custom Rose Pine dark theme with smooth animations

## 🎮 Key Features

- **🎬 Ad-free streaming** - Watch Twitch without any interruptions
- **🚀 Quick stream switching** - Seamlessly switch between different streamers
- **� Quick Swap management** - Save and organize your favorite streams
- **🎯 Multiple quality options** - 360p, 480p, 720p, 1080p, 1080p60, and more
- **🎭 Rose Pine theme** - Elegant dark interface with custom colors
- **⚡ Optimized performance** - Fast startup, low memory usage, responsive UI
- **� Smart error handling** - User-friendly error messages and automatic recovery
- **💻 Windows integration** - High-resolution icons and taskbar optimization

## 🆕 Version 2.3.0 Improvements

- **🖼️ High-resolution icons** - Crystal clear icons on Windows taskbar and alt-tab
- **🎨 Enhanced Rose Pine theme** - More consistent and beautiful color scheme
- **🔧 Better error handling** - Improved user feedback and error recovery
- **⚡ Performance optimizations** - Faster startup and smoother operation
- **🧹 Code improvements** - Cleaner, more maintainable codebase

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

## 🎮 How to Use

1. **Enter Twitch URL** - Paste any Twitch stream URL (e.g., `https://www.twitch.tv/streamer_name`)
2. **Select Quality** - Choose from 360p to 1080p60 based on your internet speed
3. **Click "Watch Stream"** - Stream opens in your default video player
4. **Use Quick Swap** - Add streams to quick access slots for instant switching
5. **Enjoy ad-free streaming!** 🎉

### 💡 Pro Tips
- **Quick Swap**: Save frequently watched streamers for one-click access
- **Quality Selection**: Start with "best" and adjust if buffering occurs
- **Stream Switching**: Use the switch button to change streams without stopping
- **Keyboard Shortcuts**: Close the video player to return to the main interface

## 🔧 Build Your Own Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable with icon
pyinstaller --onefile --windowed --icon=ghost_play_icon.ico --name="Streamlink-Maski" main.py
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
- **Streaming Engine**: Streamlink
- **Theme**: Rose Pine color scheme
- **Architecture**: Event-driven with async stream management
- **Platform**: Windows 10/11 (primary), macOS, Linux (community tested)

## 📋 System Requirements

- **Operating System**: Windows 10/11 (recommended), macOS, Linux
- **Memory**: 50MB RAM during operation
- **Storage**: 25MB free space (executable + settings)
- **Dependencies**: 
  - [Streamlink](https://streamlink.github.io/) (required for streaming)
  - Video player (VLC, MPV, or system default)
- **Internet**: Stable connection for streaming

## 🆘 Troubleshooting

**Stream won't start?**
- Ensure Streamlink is installed and accessible
- Check if the Twitch URL is valid and the stream is live
- Try a different quality setting

**Poor performance?**
- Lower the stream quality (720p instead of 1080p)
- Close other applications using bandwidth
- Check your internet connection speed

**Application crashes?**
- Check if you have Python 3.8+ installed
- Ensure all dependencies are properly installed
- Check the console for error messages

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
