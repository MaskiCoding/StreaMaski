# Streamlink Maski

A lightweight desktop GUI application for Windows that allows you to watch ad-free Twitch streams using Streamlink with a beautiful Rose Pine-inspired dark theme.

## Description

This application provides a clean, minimal interface to watch Twitch streams without ads using Streamlink. Features include:

- 🎯 **Lightweight & Fast**: Minimal dependencies, low memory footprint
- 🖼️ **Rose Pine UI**: Beautiful dark theme with smooth animations
- 📺 **Quality Selection**: Choose from various stream qualities (best, 1080p60, 720p, etc.)
- 🔄 **Stream Switching**: Easily switch between streams with clean process handling
- 🔐 **Twitch Integration**: Optional OAuth login to view followed channels
- ⚡ **Background Processing**: Streams run without terminal windows
- 🛡️ **Error Handling**: Input validation and user-friendly error messages

## Installation

### Prerequisites
- Python 3.8 or higher
- Streamlink installed and accessible from command line

### Setup
```bash
# Clone the repository
git clone https://github.com/MaskiCoding/streamlink-maski.git
cd streamlink-maski

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## Usage

1. **Launch the application**
2. **Enter Twitch stream URL** (e.g., https://www.twitch.tv/agurin)
3. **Select stream quality** from the dropdown
4. **Click "Watch"** to start streaming
5. **Use "Switch Stream"** to change to a different stream
6. **Optional**: Login with Twitch to see followed channels

## Contributing

Feel free to submit issues and enhancement requests.

## License

Add your license information here.
