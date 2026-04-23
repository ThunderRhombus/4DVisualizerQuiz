# 4D Visualizer Quiz - Web Version

Welcome! This is the web-based version of the 4D Visualizer Quiz, built using **pygbag** and running in your browser via WebAssembly.

## 🚀 Quick Start

The web build has been created and is ready to serve!

### Running Locally

**Option 1: Python HTTP Server** (Simple)
```bash
cd web_build
python -m http.server 8000
```

Then open: http://localhost:8000

**Option 2: Using pygbag's built-in server**
```bash
pygbag main.py
```

**Option 3: NPX http-server** (Requires Node.js)
```bash
cd web_build
npx http-server -p 8000 -c-1
```

### On Mobile or Different Machine

Replace `localhost` with your machine's IP address:
```
http://192.168.1.100:8000
```

## 🎮 How to Use

**Rotation Controls:**
- **Drag mouse** - Rotate the tesseract in 3D space
- **Scroll wheel** - Adjust W-axis (4D dimension)
- **Space** - Pause/Resume animation
- **R** - Reset rotation to default

**Visualization Modes:**
- **Wireframe** - Edge-based visualization
- **W-Shells** - 4D slices through the W-axis
- **CellHl** - 8 cells of tesseract highlighted

The **small origin window** (top-right) shows the dimensional axes synchronized with main view.

## 📁 What's Included

- `index.html` - Main web page
- `index.js` - JavaScript loader for WebAssembly
- `pygame.wasm` - WebAssembly runtime
- Supporting files for pygame-ce

## 🌐 Browser Support

Works on:
- ✅ Chrome/Chromium 80+
- ✅ Firefox 79+
- ✅ Safari 14+
- ✅ Edge 80+
- ✅ Mobile browsers (iOS 14+, Android 11+)

## 🚀 Deploy to the Web

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for deployment options:
- **GitHub Pages** - Free, easiest
- **Netlify** - Free, auto-deploy
- **AWS S3** - Scalable
- And many more options...

## 🔧 How This Was Built

1. **pygbag** compiled Python code to WebAssembly
2. **pygame-ce** (Community Edition) provides the graphics runtime
3. **NumPy** powers the 4D mathematics
4. The entire app runs in the browser - no server needed!

## ⚡ Performance Notes

- First load may take 10-30 seconds (downloading WebAssembly)
- Subsequent loads are faster (browser caching)
- Performance depends on GPU and system memory
- Works best on modern hardware

## 🐛 Troubleshooting

**App doesn't load?**
- Check browser console (F12 → Console)
- Ensure `.wasm` file exists in directory
- Try a different browser
- Check your internet connection

**Slow performance?**
- Close other browser tabs
- Disable browser extensions
- Try fullscreen mode (if available)
- Use Chrome/Firefox for best performance

**Controls not responsive?**
- Click on the canvas to ensure focus
- Try different browser
- Check if JavaScript is enabled

## 📚 More Information

- [Pygbag Setup Guide](../PYGBAG_SETUP.md) - How to rebuild
- [Deployment Guide](../DEPLOYMENT_GUIDE.md) - Deploy to hosting
- [Pygame-CE Docs](https://github.com/pygame-web/pygame-ce)
- [Pygbag GitHub](https://github.com/pygame-web/pygbag)

## 💡 Tips & Tricks

- **Smooth rotation:** Drag slowly for precise control
- **Fast rotation:** Drag quickly for momentum
- **W-axis exploration:** Use mouse wheel to slice through 4D
- **Screenshot:** Most browsers allow right-click → Screenshot

## 🎓 About This Project

This is an interactive quiz and visualization tool for understanding 4D geometry, specifically the tesseract (4D cube). The physics-accurate rotation system allows you to see how 4D objects project into 3D space.

---

**Enjoy exploring the 4th dimension!** 🌌✨
