# Quick Start Guide

Get up and running with KOL Video Translation in 5 minutes!

## Prerequisites

Choose one option:

**Option A: Docker (Recommended)**
- Docker Desktop or Docker Engine
- Docker Compose

**Option B: Local Development**
- Go 1.21+
- Python 3.10+
- Node.js 18+
- FFmpeg

## Quick Start with Docker (Easiest)

1. **Clone the repository:**
```bash
git clone https://github.com/chunjenpeng/kol_video_translation.git
cd kol_video_translation
```

2. **Start all services:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Open http://localhost:3000 in your browser
- The backend API is at http://localhost:8080
- The Python service is at http://localhost:5000

4. **Try it out:**
- Paste a YouTube URL (try: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
- Select source language (e.g., English)
- Select target language (e.g., Spanish)
- Click "Translate Video"
- Wait for processing (may take several minutes)
- Download your translated video!

## Quick Start with Makefile

If you have make installed:

```bash
# Build everything
make build

# Start all services
make run

# View logs
make logs

# Stop services
make stop

# Clean up
make clean
```

## Quick Start - Local Development

### Terminal 1 - Backend
```bash
cd backend
go mod download
cp .env.example .env
go run main.go
# Server starts on http://localhost:8080
```

### Terminal 2 - Python Service
```bash
cd python_service
pip install -r requirements.txt
cp .env.example .env
python app.py
# Server starts on http://localhost:5000
```

### Terminal 3 - Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# Server starts on http://localhost:3000
```

## Verify Installation

### Check Backend
```bash
curl http://localhost:8080/api/v1/health
# Expected: {"status":"healthy","time":"..."}
```

### Check Python Service
```bash
curl http://localhost:5000/api/health
# Expected: {"status":"healthy","service":"python-video-processor"}
```

### Check Frontend
Open http://localhost:3000 in your browser - you should see the app interface.

## Test with a Sample Video

1. Go to http://localhost:3000
2. Enter this sample URL: `https://www.youtube.com/watch?v=jNQXAC9IVRw`
3. Source: English
4. Target: Spanish
5. Click "Translate Video"
6. Wait for completion (this may take 5-15 minutes)
7. Download the result

## Common Issues

### Issue: Port already in use
```bash
# Find and kill process using port 8080
lsof -i :8080
kill -9 <PID>
```

### Issue: Docker containers won't start
```bash
# Remove old containers and volumes
docker-compose down -v
docker-compose up --build
```

### Issue: Python dependencies fail
```bash
# Install system dependencies first (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev build-essential ffmpeg
pip install -r requirements.txt
```

### Issue: FFmpeg not found
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

## Next Steps

- Read the [README.md](README.md) for detailed information
- Check [SETUP.md](SETUP.md) for advanced setup options
- Review [API.md](API.md) for API documentation
- See [examples/](examples/) for code examples
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design

## Need Help?

- Check [SETUP.md](SETUP.md) for troubleshooting
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open an issue on GitHub

## Quick Reference

### Supported Languages
English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi

### Processing Time
- Short video (3 min): ~5-15 minutes
- Medium video (10 min): ~15-45 minutes
- Long video (30 min): ~45-120 minutes

### Output Files
- Translated video (MP4)
- Captions (SRT)
- Thumbnail (JPG)

## Quick Tips

1. **Start with short videos** (1-3 minutes) for testing
2. **Use Wi-Fi** - downloads can be large
3. **Be patient** - AI processing takes time
4. **Check logs** if something fails:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Local
   # Check each terminal window
   ```
5. **Clear temp files** regularly:
   ```bash
   rm -rf output/* temp/*
   ```

## That's it! 🎉

You're now ready to translate videos with AI-powered voice cloning!
