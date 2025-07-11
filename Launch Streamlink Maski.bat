@echo off
echo 🎭 Starting Streamlink Maski...
echo.
cd /d "%~dp0"
if exist "dist\Streamlink Maski.exe" (
    echo ✅ Launching application...
    start "" "dist\Streamlink Maski.exe"
) else (
    echo ❌ Executable not found in dist folder
    echo Please make sure "Streamlink Maski.exe" is in the dist folder
    pause
)
