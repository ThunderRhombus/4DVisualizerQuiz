# Pygbag Setup Guide - 4D Visualizer Quiz

This guide explains how to convert the 4D Visualizer Quiz to a website using **pygbag** (no Java required).

## What is Pygbag?

**Pygbag** is a build tool that converts Python pygame applications into WebAssembly-based web applications. It compiles your Python code to run directly in a web browser without needing a server or any backend Java infrastructure.

**Key Benefits:**
- ✅ No Java needed
- ✅ Runs entirely in the browser
- ✅ Uses WebAssembly for performance
- ✅ Compatible with most pygame code
- ✅ Cross-platform (works on Windows, Mac, Linux)

## Prerequisites

### 1. Install Python (3.8+)
Ensure you have Python 3.8 or higher installed on your system.

```bash
python --version
```

### 2. Install Pygbag

Install pygbag using pip:

```bash
pip install pygbag
```

Or install it with development tools:

```bash
pip install "pygbag[dev]"
```

### 3. Install Project Dependencies

From the project root directory, install the required Python packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` has been updated to use `pygame-ce` (Community Edition), which is optimized for web deployment.

## Project Structure

Your project now has the following key files for pygbag:

```
/workspaces/4DVisualizerQuiz/
├── main.py                 # 🚀 Web entry point (replaces MAINInterface.py)
├── build.toml              # ⚙️ Pygbag build configuration
├── requirements.txt        # 📦 Python dependencies (updated with pygame-ce)
├── index.html              # 🌐 Web page template (optional)
├── [All other Python modules remain unchanged]
└── web_build/              # 📁 Output directory (created during build)
```

## Building for Web

### Option 1: Build with Pygbag (Recommended)

From the project root directory:

```bash
pygbag main.py
```

This command will:
1. ✅ Compile your Python code to WebAssembly
2. ✅ Generate HTML/CSS/JS files
3. ✅ Create a `web_build` directory with all web assets
4. ✅ Start a local development server automatically

### Option 2: Build with Custom Output Directory

```bash
pygbag --build --dir web_build main.py
```

### Option 3: Build for Release

```bash
pygbag --build --release main.py
```

This creates an optimized, production-ready build.

## Running the Web Version

### Local Testing

After building, pygbag automatically starts a local server. You can access it at:

```
http://localhost:8000
```

Or in your terminal, pygbag will provide the exact URL.

### Testing on Mobile/Other Devices

If running on a dev machine, access from other devices:

```
http://<your-machine-ip>:8000
```

Find your machine IP:
- **Linux/Mac:** `ifconfig | grep inet`
- **Windows:** `ipconfig` (look for IPv4 Address)

## Project Files Created/Modified

### 1. **main.py** (NEW)
- Web-compatible entry point
- Replaces multiprocessing with single-threaded origin viewer
- Fully compatible with pygbag

### 2. **build.toml** (NEW)
- Pygbag build configuration
- Specifies dependencies, build options, canvas size
- Can be customized for your needs

### 3. **requirements.txt** (MODIFIED)
- Changed `pygame` → `pygame-ce` (Community Edition)
- `pygame-ce` is optimized for WebAssembly

## Configuration Options

Edit `build.toml` to customize:

```toml
[build]
title = "4D Visualizer Quiz"              # Browser tab title
author = "Your Name"                       # Author name
version = "1.0.0"                          # App version

[build.web]
fullscreen = false                         # Allow fullscreen toggle
width = 1200                               # Canvas width
height = 800                               # Canvas height
debug = true                               # Show debug messages

[build.dependencies]
pygame-ce = "*"                            # Pygame Community Edition
numpy = "*"                                # NumPy for mathematics
```

## Deployment

### Option 1: Static Hosting (Easiest)

Simply upload the contents of `web_build/` to any static web host:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Any traditional web server

Example with GitHub Pages:
```bash
# After building with pygbag
cp -r web_build/* /path/to/github-pages-repo/
git add .
git commit -m "Deploy 4D Visualizer"
git push
```

### Option 2: Docker Container

Create a `Dockerfile`:

```dockerfile
FROM nginx:latest
COPY web_build/ /usr/share/nginx/html/
```

Build and run:
```bash
docker build -t 4d-visualizer .
docker run -p 80:80 4d-visualizer
```

## Troubleshooting

### Issue: "pygbag not found"
**Solution:** Ensure pygbag is installed:
```bash
pip install pygbag
```

### Issue: "pygame not found"
**Solution:** Install pygame-ce:
```bash
pip install pygame-ce numpy
```

### Issue: Build takes too long
**Solution:** This is normal the first time. Subsequent builds are faster. The initial build compiles Python to WebAssembly, which can take 2-5 minutes.

### Issue: App crashes on startup
**Solution:** Check the browser console (F12 → Console tab) for error messages. Common issues:
- Missing imports (check import statements in main.py)
- NumPy version incompatibility
- Large file sizes

### Issue: Performance is slow
**Solution:**
- Reduce canvas resolution in `build.toml`
- Optimize 3D mesh complexity
- Use the `--release` flag for optimized build

## Performance Tips

1. **Optimize Mesh Complexity:** Reduce polygon count in Tesseract/shapes
2. **Use Release Builds:** `pygbag --build --release main.py`
3. **Lazy Load:** Load non-essential modules on-demand
4. **Cache Assets:** Browser caches will speed up subsequent loads
5. **Monitor Size:** Keep WebAssembly bundle under 20MB for mobile

## Browser Compatibility

Pygbag works on:
- ✅ Chrome/Chromium (80+)
- ✅ Firefox (79+)
- ✅ Safari (14+)
- ✅ Edge (80+)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Differences from Desktop Version

The web version (`main.py`) differs from desktop versions (`MAINWireframe.py`, etc.):

1. **No Multiprocessing:** Origin viewer integrated into main window
2. **Single-threaded:** No separate origin process (web limitation)
3. **Async-safe:** Uses asyncio for non-blocking updates
4. **Web-compatible:** All pygame calls work in WebAssembly context

Original desktop files remain unchanged for local development.

## Further Resources

- **Pygbag Documentation:** https://github.com/pygame-web/pygbag
- **Pygame Community Edition:** https://github.com/pygame-web/pygame-ce
- **WebAssembly Guide:** https://webassembly.org/

## Quick Start Cheat Sheet

```bash
# Install pygbag
pip install pygbag

# Install dependencies
pip install -r requirements.txt

# Build web version
pygbag main.py

# Access at http://localhost:8000
```

That's it! Your 4D Visualizer is now a web app! 🚀
