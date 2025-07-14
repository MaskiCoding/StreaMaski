@echo off
REM Quick build script for Streamlink Maski
REM Run this from the root directory

echo.
echo ================================
echo  Streamlink Maski v3.0.0 Build
echo ================================
echo.

if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

echo Building executable...
cd build
call build.bat

echo.
echo Build completed! Check the dist/ folder for the executable.
pause
