@echo off
echo ========================================
echo    Building StreaMaski Executable
echo ========================================
echo.

echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "StreaMaski.exe" del "StreaMaski.exe"

echo.
echo Building with PyInstaller...
".venv\Scripts\pyinstaller.exe" --clean --noconfirm StreaMaski.spec

echo.
if exist "dist\StreaMaski.exe" (
    echo Moving executable to main directory...
    move "dist\StreaMaski.exe" "StreaMaski.exe"
    echo.
    echo ========================================
    echo    BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo The executable "StreaMaski.exe" has been created.
    echo Size: 
    dir "StreaMaski.exe" | find "StreaMaski.exe"
    echo.
    echo You can now run the application by double-clicking StreaMaski.exe
    echo.
) else (
    echo.
    echo ========================================
    echo    BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the output above for errors.
    echo.
)

echo Cleaning up build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Press any key to exit...
pause >nul
