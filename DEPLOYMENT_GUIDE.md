# 4D Visualizer Quiz - Web Deployment Guide

This guide covers how to deploy your pygbag-built 4D Visualizer to various platforms.

## 📋 Prerequisites

Before deploying, ensure you've built the web version:

```bash
# Build the web version
pygbag main.py

# This creates the 'web_build/' directory with all necessary files
```

The `web_build/` directory contains:
- `index.html` - Main HTML file
- `index.js` - JavaScript loader
- `pygame.wasm` - WebAssembly module
- Other supporting files

## 🌐 Deployment Options

### Option 1: GitHub Pages (Easiest - Free)

Perfect for free, simple hosting with automatic HTTPS.

#### Steps:

1. **Create a GitHub repository** (if you don't have one):
   ```bash
   git remote add origin https://github.com/yourusername/4d-visualizer.git
   git branch -M main
   git push -u origin main
   ```

2. **Create a `docs/` folder and copy build output:**
   ```bash
   mkdir -p docs
   cp -r web_build/* docs/
   git add docs/
   git commit -m "Deploy web version to GitHub Pages"
   git push
   ```

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Select "Deploy from a branch"
   - Choose branch: `main`, folder: `/docs`
   - Save

4. **Access your site:**
   ```
   https://yourusername.github.io/4d-visualizer
   ```

#### Why GitHub Pages?
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Built-in CDN
- ✅ Easy updates (just push)

---

### Option 2: Netlify (Very Easy - Free)

Excellent for continuous deployment from GitHub.

#### Steps:

1. **Push your repo to GitHub** (including `web_build/` or create build script)

2. **Sign up at netlify.com** (free tier available)

3. **Connect GitHub repository:**
   - Click "New site from Git"
   - Select GitHub
   - Choose your repository
   - Set build command: `pygbag main.py`
   - Set publish directory: `web_build`

4. **Deploy:**
   - Netlify automatically builds and deploys on push
   - Get automatic HTTPS and custom domain

#### Why Netlify?
- ✅ Continuous deployment from GitHub
- ✅ Free tier (very generous)
- ✅ Automatic builds
- ✅ Easy environment variables
- ✅ Built-in analytics

---

### Option 3: Vercel (Very Easy - Free)

Similar to Netlify with Vercel's edge network.

#### Steps:

1. **Create `vercel.json`:**
   ```json
   {
     "buildCommand": "pygbag main.py",
     "outputDirectory": "web_build",
     "python": {
       "version": "3.11"
     }
   }
   ```

2. **Push to GitHub**

3. **Sign up at vercel.com** and import your GitHub repository

4. **Vercel automatically deploys** on push

#### Why Vercel?
- ✅ Extremely fast
- ✅ Edge functions support
- ✅ Free tier
- ✅ Automatic HTTPS
- ✅ Analytics included

---

### Option 4: AWS S3 + CloudFront (Scalable)

Good for high-traffic applications.

#### Steps:

1. **Create S3 bucket:**
   ```bash
   aws s3 mb s3://4d-visualizer-web
   ```

2. **Upload web_build contents:**
   ```bash
   aws s3 sync web_build/ s3://4d-visualizer-web/
   ```

3. **Configure bucket for static hosting:**
   - AWS S3 → Bucket Properties → Static website hosting
   - Index document: `index.html`

4. **Set bucket policy to public:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::4d-visualizer-web/*"
     }]
   }
   ```

5. **Create CloudFront distribution** (optional, for CDN)

6. **Access your site:**
   ```
   http://4d-visualizer-web.s3.amazonaws.com
   ```

#### Why AWS S3?
- ✅ Extremely reliable
- ✅ Scales to any traffic
- ✅ Cost-effective for static content
- ✅ CloudFront CDN available
- ✅ Global distribution

---

### Option 5: Traditional Web Hosting (Shared/VPS)

For existing hosting accounts.

#### Steps:

1. **Connect via FTP/SFTP:**
   ```bash
   # Using sftp command
   sftp user@yourhost.com
   cd /public_html
   put -r web_build/* .
   ```

2. **Using rsync (recommended):**
   ```bash
   rsync -avz web_build/ user@yourhost.com:/public_html/
   ```

3. **Set correct permissions:**
   ```bash
   chmod -R 755 /public_html/web_build
   ```

4. **Access your site:**
   ```
   https://yourhost.com/
   ```

#### Why Traditional Hosting?
- ✅ Existing account reuse
- ✅ Control over full server
- ✅ Multiple projects possible
- ✅ Familiar setup

---

### Option 6: Docker Container (Advanced)

For containerized deployment.

#### Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt
RUN pip install pygbag

# Build for web
RUN pygbag main.py

# Serve with simple HTTP server
EXPOSE 8000
CMD ["python", "-m", "http.server", "--directory", "web_build", "8000"]
```

#### Build and run:

```bash
# Build image
docker build -t 4d-visualizer .

# Run container
docker run -p 8000:8000 4d-visualizer

# Access at http://localhost:8000
```

#### Deploy to cloud:
- **Docker Hub** → Create repo → Push image → Deploy to any cloud
- **AWS ECS/EKS** → Container registry → Scale globally
- **Google Cloud Run** → Auto-scaling containers (pay per request)
- **Azure Container Instances** → Managed containers

---

### Option 7: Google Cloud Storage (Fast + Cheap)

Simple static hosting with Google's global CDN.

#### Steps:

1. **Create bucket:**
   ```bash
   gsutil mb gs://4d-visualizer-web
   ```

2. **Upload files:**
   ```bash
   gsutil -m cp -r web_build/* gs://4d-visualizer-web/
   ```

3. **Set as public:**
   ```bash
   gsutil iam ch allUsers:objectViewer gs://4d-visualizer-web
   ```

4. **Configure CORS (if needed):**
   ```bash
   gsutil cors set cors.json gs://4d-visualizer-web
   ```

5. **Set up Load Balancer** for HTTPS and custom domain

#### Why Google Cloud Storage?
- ✅ Google's global infrastructure
- ✅ Pay only for what you use
- ✅ Built-in CDN (100+ locations)
- ✅ Excellent for WebAssembly apps

---

## 📊 Hosting Comparison

| Platform | Cost | Ease | Speed | HTTPS | Scalability |
|----------|------|------|-------|-------|-------------|
| GitHub Pages | Free | ⭐⭐⭐ | Fast | Auto | Good |
| Netlify | Free | ⭐⭐⭐⭐ | Very Fast | Auto | Excellent |
| Vercel | Free | ⭐⭐⭐⭐ | Blazing | Auto | Excellent |
| AWS S3 | $0.023/GB | ⭐⭐ | Fast | Separate | Unlimited |
| Traditional | $5-50/mo | ⭐⭐⭐ | Variable | Optional | Limited |
| Docker Cloud | $5+/mo | ⭐⭐ | Fast | Setup | Scalable |
| Google Cloud | $0.020/GB | ⭐⭐ | Very Fast | Setup | Unlimited |

**Recommendation for beginners:** Start with **Netlify** or **GitHub Pages**. Upgrade to AWS/Google Cloud if you need global distribution or high traffic.

---

## 🔄 Continuous Deployment (Auto-deploy on Push)

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pygbag
      
      - name: Build web version
        run: pygbag main.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web_build
```

Now, every push to `main` automatically builds and deploys! 🚀

---

## 🛡️ Security Considerations

1. **HTTPS:** Always use HTTPS in production
   - GitHub Pages: Automatic
   - Netlify/Vercel: Automatic
   - AWS: Use CloudFront
   - Traditional: Get SSL certificate (Let's Encrypt is free)

2. **CORS:** If accessing external APIs:
   ```toml
   # In build.toml
   [build.web]
   cors_headers = true
   ```

3. **Content Security Policy:** Add to HTML header
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; script-src 'self' 'wasm-unsafe-eval'">
   ```

---

## 📈 Monitoring & Analytics

### GitHub Pages + Google Analytics

Add to `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Netlify Analytics (Built-in)
- Enable in Netlify dashboard
- See traffic, performance, user agent data

### Vercel Analytics (Built-in)
- Automatic Web Vitals tracking
- Performance monitoring
- User analytics

---

## 🚀 Quick Deploy Cheat Sheet

```bash
# Build
pygbag main.py

# GitHub Pages
cp -r web_build/* docs/
git add docs/ && git commit -m "Deploy" && git push

# AWS S3
aws s3 sync web_build/ s3://your-bucket/

# Traditional Hosting
rsync -avz web_build/ user@host:/public_html/

# Docker
docker build -t 4d-vis .
docker run -p 8000:8000 4d-vis
```

---

## 🆘 Troubleshooting

**Site works locally but not online?**
- Check file permissions (should be 644 for files, 755 for directories)
- Verify CORS headers if loading assets
- Check browser console (F12) for errors

**WebAssembly module not loading?**
- Ensure `.wasm` file is uploaded
- Check MIME type (should be `application/wasm`)
- Verify Content-Encoding headers

**Performance issues?**
- Enable gzip compression on server
- Use a CDN (CloudFront, CloudFlare)
- Optimize assets in `web_build/`

---

Choose your platform and happy deploying! 🎉
