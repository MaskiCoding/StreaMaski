@echo off
REM Build script for Streamlink Maski v3.0.0
REM Run this to create the executable

echo.
echo ================================
echo  Streamlink Maski v3.0.0 Build
echo ================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python and try again.
    pause
    exit /b 1
)

echo Checking PyInstaller installation...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Starting build process...
python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo ================================
    echo  Build completed successfully!
    echo ================================
    echo.
    echo Executable created: dist\StreamlinkMaski.exe
    echo Release package: StreamlinkMaski_v3.0.0_Windows.zip
    echo.
) else (
    echo.
    echo ================================
    echo  Build failed!
    echo ================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
