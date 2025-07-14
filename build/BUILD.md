# Building Streamlink Maski v3.0.0 Executable

This document explains how to build the Streamlink Maski executable from source.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Windows OS (for Windows executable)

## Quick Build

### Option 1: Using the Batch File (Recommended)
1. Double-click `build.bat`
2. The script will automatically:
   - Check Python installation
   - Install PyInstaller if needed
   - Build the executable
   - Create release package

### Option 2: Using Python Script
```bash
python build_exe.py
```

### Option 3: Manual PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file (recommended)
pyinstaller streamlink_maski.spec

# Or build using command line
pyinstaller --onefile --windowed --name=StreamlinkMaski --icon=Icon.ico main.py
```

## Build Output

After successful build, you'll find:

- `dist/StreamlinkMaski.exe` - The main executable
- `StreamlinkMaski_v3.0.0_Windows.zip` - Release package containing:
  - StreamlinkMaski.exe
  - README.md
  - CHANGELOG.md
  - RELEASE_NOTES.md
  - INSTALL.txt

## Build Configuration

### PyInstaller Options
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window
- `--icon=Icon.ico`: Sets the application icon
- `--add-data=Icon.ico;.`: Includes icon in the executable

### Hidden Imports
The build includes these modules that PyInstaller might miss:
- customtkinter and related modules
- tkinter components
- requests and urllib modules
- All standard library modules used

### Excluded Modules
To reduce size, these modules are excluded:
- matplotlib, numpy, pandas, scipy
- GUI frameworks (PyQt, wxPython)
- Web frameworks (Flask, Django)
- Development tools (pytest, setuptools)

## Advanced Build Options

### Using the Spec File
The `streamlink_maski.spec` file provides advanced configuration:
- Version information embedding
- Advanced import handling
- Size optimization
- Windows-specific settings

### Customizing the Build
To modify the build:
1. Edit `streamlink_maski.spec` for advanced options
2. Edit `build_exe.py` for build process changes
3. Edit `version_info.py` for executable metadata

## Troubleshooting

### Common Issues

**PyInstaller not found:**
```bash
pip install pyinstaller
```

**Icon not found:**
- Ensure `Icon.ico` is in the project directory
- Check the file path in the build script

**Missing modules:**
- Add missing imports to `hiddenimports` in the spec file
- Use `--hidden-import=module_name` in command line

**Large file size:**
- Review `excludes` list in spec file
- Consider using `--exclude-module=module_name`

### Build Errors
If the build fails:
1. Check Python version compatibility
2. Ensure all dependencies are installed
3. Try building with verbose output:
   ```bash
   pyinstaller --log-level=DEBUG streamlink_maski.spec
   ```

## GitHub Actions

Automated builds are configured via `.github/workflows/build.yml`:
- Triggered on version tags (v3.0.0, etc.)
- Builds on Windows
- Uploads artifacts
- Creates GitHub releases

## File Structure

```
Streamlink Maski/
├── main.py                 # Main application
├── Icon.ico               # Application icon
├── build_exe.py           # Build script
├── build.bat              # Windows batch file
├── streamlink_maski.spec  # PyInstaller spec file
├── version_info.py        # Windows version info
├── requirements.txt       # Dependencies
└── .github/workflows/
    └── build.yml          # GitHub Actions
```

## Version Information

The executable includes embedded version information:
- Version: 3.0.0
- Company: MaskiCoding
- Description: Lightweight Twitch Stream Viewer
- Copyright: © 2025 MaskiCoding

## Performance Notes

- Build time: ~30-60 seconds
- Executable size: ~15-25 MB
- Memory usage: ~50-80 MB
- Startup time: ~2-3 seconds

## Distribution

The release package is ready for distribution and includes:
- Portable executable (no installation required)
- Documentation files
- Installation instructions
- Version and changelog information
