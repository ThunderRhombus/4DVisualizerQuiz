#!/bin/bash
# Quick build script for pygbag web deployment

echo "🚀 Building 4D Visualizer for Web with Pygbag..."
echo ""
echo "Checking for pygbag..."

if ! command -v pygbag &> /dev/null; then
    echo "❌ Pygbag not found. Installing..."
    pip install pygbag
else
    echo "✅ Pygbag found"
fi

echo ""
echo "Checking dependencies..."
pip install -r requirements.txt

echo ""
echo "🔨 Building web version..."
pygbag main.py

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output directory: web_build/"
echo "🌐 Access at: http://localhost:8000"
echo ""
echo "💡 To deploy, upload the contents of 'web_build/' to your web host"
