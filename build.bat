@echo off
REM Quick build script for pygbag web deployment (Windows)

echo.
echo 🚀 Building 4D Visualizer for Web with Pygbag...
echo.
echo Checking for pygbag...

where pygbag >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Pygbag not found. Installing...
    pip install pygbag
) else (
    echo ✅ Pygbag found
)

echo.
echo Checking dependencies...
pip install -r requirements.txt

echo.
echo 🔨 Building web version...
pygbag main.py

echo.
echo ✅ Build complete!
echo.
echo 📁 Output directory: web_build\
echo 🌐 Access at: http://localhost:8000
echo.
echo 💡 To deploy, upload the contents of 'web_build\' to your web host
echo.
pause
