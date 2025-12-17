# Setup Guide

This guide will help you set up the KOL Video Translation application on your local machine.

## Quick Start (Docker)

The easiest way to get started is using Docker:

```bash
# 1. Clone the repository
git clone https://github.com/chunjenpeng/kol_video_translation.git
cd kol_video_translation

# 2. Build and run with Docker Compose
make build
make run

# 3. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8080
# Python Service: http://localhost:5000
```

## Local Development Setup

### Prerequisites

Before starting, ensure you have the following installed:

1. **Go 1.21 or higher**
   ```bash
   go version
   ```

2. **Python 3.10 or higher**
   ```bash
   python --version
   ```

3. **Node.js 18 or higher**
   ```bash
   node --version
   npm --version
   ```

4. **FFmpeg**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Go dependencies:
   ```bash
   go mod download
   ```

3. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` if needed (defaults should work):
   ```env
   PORT=8080
   PYTHON_SERVICE_URL=http://localhost:5000
   ```

5. Run the backend:
   ```bash
   go run main.go
   ```

The backend API will be available at http://localhost:8080

### Python Service Setup

1. Navigate to the Python service directory:
   ```bash
   cd python_service
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   
   # Activate on Linux/macOS
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: This may take several minutes as it downloads ML models.

4. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` if needed:
   ```env
   PORT=5000
   BACKEND_API_URL=http://localhost:8080
   ```

6. Run the Python service:
   ```bash
   python app.py
   ```

The Python service will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` if needed:
   ```env
   VITE_API_URL=http://localhost:8080/api/v1
   ```

5. Run the frontend development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:3000

## Verifying the Setup

Once all three services are running, verify the setup:

1. **Check Backend Health**:
   ```bash
   curl http://localhost:8080/api/v1/health
   ```
   Expected response: `{"status":"healthy","time":"..."}`

2. **Check Python Service Health**:
   ```bash
   curl http://localhost:5000/api/health
   ```
   Expected response: `{"status":"healthy","service":"python-video-processor"}`

3. **Check Frontend**:
   Open http://localhost:3000 in your browser. You should see the application interface.

## Testing the Application

1. Open the frontend at http://localhost:3000
2. Paste a YouTube URL (try a short video first): `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. Select source language (e.g., English)
4. Select target language (e.g., Spanish)
5. Click "Translate Video"
6. Wait for processing (this may take several minutes)
7. Download the result when completed

## Common Issues and Solutions

### Issue: Port already in use

**Error**: `address already in use`

**Solution**: Change the port in the `.env` file or kill the process using the port:
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Issue: Python dependencies fail to install

**Error**: `Failed building wheel for...`

**Solution**: Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# macOS
xcode-select --install
```

### Issue: FFmpeg not found

**Error**: `ffmpeg: command not found`

**Solution**: Install FFmpeg (see Prerequisites section)

### Issue: Out of memory during video processing

**Solution**: 
- Use shorter videos for testing
- Increase available RAM
- Use a smaller Whisper model (edit `transcription_service.py` to use "tiny" or "base" instead of "large")

### Issue: Go module errors

**Error**: `go.mod file not found`

**Solution**: Make sure you're in the correct directory:
```bash
cd backend
go mod download
```

### Issue: React build fails

**Error**: `Module not found`

**Solution**: Clear npm cache and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Production Deployment

For production deployment, consider:

1. **Use Docker** for consistency and isolation
2. **Set up reverse proxy** (nginx/Apache) for SSL/TLS
3. **Add authentication** to protect the API
4. **Implement rate limiting** to prevent abuse
5. **Set up monitoring** (logs, metrics, alerts)
6. **Configure file cleanup** to manage disk space
7. **Add database** for persistent job storage (replace in-memory map)
8. **Use cloud storage** (S3, GCS) for video files

## Development Workflow

Using the Makefile commands:

```bash
# Install all dependencies
make setup-all

# Run individual services
make dev-backend    # Terminal 1
make dev-python     # Terminal 2
make dev-frontend   # Terminal 3

# Or use Docker for everything
make build
make run
make logs          # View logs

# Clean up when done
make stop
make clean
```

## Environment Variables Reference

### Backend (.env)
- `PORT`: API server port (default: 8080)
- `PYTHON_SERVICE_URL`: Python service endpoint

### Python Service (.env)
- `PORT`: Service port (default: 5000)
- `BACKEND_API_URL`: Backend API endpoint
- `OPENAI_API_KEY`: (Optional) For advanced features

### Frontend (.env)
- `VITE_API_URL`: Backend API URL

## Next Steps

- Read the [API Documentation](README.md#api-documentation)
- Explore the code structure
- Try translating different videos
- Experiment with different language pairs
- Contribute improvements!

## Getting Help

If you encounter issues:
1. Check the logs for error messages
2. Review this setup guide
3. Search existing GitHub issues
4. Create a new issue with detailed information

Happy translating! 🎥🌍
