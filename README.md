# KOL Video Translation

🎥 An AI-powered web application that automatically translates YouTube videos to any language while cloning the presenter's voice. The app also generates captions and thumbnails automatically.

## Features

- ✅ **YouTube Video Download**: Download videos directly from YouTube URLs
- 🎤 **Speech-to-Text**: Transcribe video audio using OpenAI Whisper
- 🌍 **Translation**: Translate transcripts to 12+ languages using Google Translate
- 🗣️ **Voice Cloning**: Generate translated audio with AI voice cloning (Coqui TTS)
- 📝 **Caption Generation**: Automatically create SRT subtitle files
- 🖼️ **Thumbnail Generation**: Extract and generate video thumbnails
- 🎬 **Video Merging**: Combine translated audio with original video

## Tech Stack

### Backend (Golang)
- **Gin Framework**: RESTful API server
- **Go-Redis**: Redis client for job management
- **Job Management**: Asynchronous processing with Redis queue
- **CORS Support**: Cross-origin resource sharing

### Python Service
- **Flask**: Python web framework
- **yt-dlp**: YouTube video downloading
- **OpenAI Whisper**: Speech-to-text transcription
- **Deep Translator**: Multi-language translation
- **Coqui TTS**: Text-to-speech with voice cloning
- **MoviePy**: Video processing and merging
- **Pillow**: Thumbnail generation

### Frontend (React)
- **React 18**: Modern UI framework
- **Vite**: Fast build tool
- **Axios**: HTTP client
- **Responsive Design**: Mobile-friendly interface

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌─────────────────┐
│   React     │─────▶│   Golang     │─────▶│    Redis     │─────▶│  Python Service │
│  Frontend   │      │   Backend    │      │ (Queue/DB)   │      │    (Worker)     │
└─────────────┘      └──────────────┘      └──────────────┘      └─────────────────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐      ┌──────────────┐
                     │ File Storage │      │ File Storage │
                     │ (Output/Temp)│      │ (Output/Temp)│
                     └──────────────┘      └──────────────┘
```

## Prerequisites

### For Local Development
- Go 1.21+
- Python 3.10+
- Node.js 18+
- FFmpeg (for video processing)

### For Docker Deployment
- Docker
- Docker Compose

### Infrastructure
- Redis 7+ (Required for job queue and persistence)

## Installation & Setup

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/chunjenpeng/kol_video_translation.git
cd kol_video_translation
```

2. Build and start all services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- Python Service: http://localhost:5000

### Option 2: Local Development

#### Backend Setup

```bash
cd backend
go mod download
cp .env.example .env
go run main.go
```

#### Python Service Setup

```bash
cd python_service
pip install -r requirements.txt
cp .env.example .env
python app.py
```

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Configuration

### Backend Environment Variables
```env
PORT=8080
PYTHON_SERVICE_URL=http://localhost:5000
```

### Python Service Environment Variables
```env
PORT=5000
BACKEND_API_URL=http://localhost:8080
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for advanced features
```

### Frontend Environment Variables
```env
VITE_API_URL=http://localhost:8080/api/v1
```

## API Documentation

### Endpoints

#### GET `/api/v1/health`
Health check endpoint
- **Response**: `{ "status": "healthy", "time": "..." }`

#### GET `/api/v1/languages`
Get supported languages
- **Response**: `{ "languages": [{ "code": "en", "name": "English" }, ...] }`

#### POST `/api/v1/translate`
Start a video translation job
- **Request Body**:
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "source_language": "en",
  "target_language": "es"
}
```
- **Response**: `{ "job_id": "...", "status": "pending" }`

#### GET `/api/v1/job/:id`
Get job status
- **Response**:
```json
{
  "id": "...",
  "status": "completed",
  "progress": 100,
  "output_video_path": "...",
  "captions_path": "...",
  "thumbnail_path": "..."
}
```

#### GET `/api/v1/download/:id`
Download the translated video
- **Response**: Video file download

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese Simplified (zh)
- Arabic (ar)
- Hindi (hi)

## Usage

1. **Open the web application** in your browser
2. **Paste a YouTube URL** in the input field
3. **Select source language** (the language of the video)
4. **Select target language** (the language you want to translate to)
5. **Click "Translate Video"** and wait for processing
6. **Download the result** when completed

The processing includes:
- Downloading the video from YouTube
- Transcribing audio to text
- Translating the transcript
- Generating new audio with voice cloning
- Creating subtitle files
- Generating thumbnails
- Merging everything into a final video

## Project Structure

```
kol_video_translation/
├── backend/                 # Golang API server
│   ├── handlers/           # HTTP request handlers
│   ├── middleware/         # CORS and other middleware
│   ├── models/             # Data models
│   ├── main.go             # Application entry point
│   └── Dockerfile          # Docker configuration
├── python_service/         # Python processing service
│   ├── services/           # Processing modules
│   │   ├── youtube_downloader.py
│   │   ├── transcription_service.py
│   │   ├── translation_service.py
│   │   ├── voice_cloning_service.py
│   │   ├── caption_generator.py
│   │   ├── thumbnail_generator.py
│   │   └── video_processor.py
│   ├── app.py              # Flask application
│   └── Dockerfile          # Docker configuration
├── frontend/               # React web application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.jsx        # Main application
│   │   └── main.jsx       # Entry point
│   ├── Dockerfile         # Docker configuration
│   └── nginx.conf         # Nginx configuration
├── tests/                 # End-to-End tests
│   └── e2e/
│       └── smoke_test.py
└── docker-compose.yml     # Docker Compose configuration
```

## Testing

### Backend (Unit Tests)
```bash
cd backend
go test -v ./...
```

### Frontend (Component Tests)
```bash
cd frontend
npm test
```

### Python Service (Functional Tests)
```bash
cd python_service
pytest test_pipeline_functional.py
```

### End-to-End (Smoke Test)
```bash
# Requires running stack
python tests/e2e/smoke_test.py
```

## Performance Considerations

- **Video Length**: Processing time depends on video length (typically 5-15 minutes for a 3-minute video)
- **Voice Cloning**: The XTTS model provides the best quality but requires more processing time
- **Concurrent Jobs**: The system can handle multiple jobs simultaneously
- **Storage**: Ensure adequate disk space for temporary and output files

## Troubleshooting

### Issue: FFmpeg not found
**Solution**: Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Issue: Python dependencies failing to install
**Solution**: Try installing system dependencies first
```bash
sudo apt-get install python3-dev build-essential
```

### Issue: Out of memory during processing
**Solution**: Increase Docker memory limits or use a smaller Whisper model (tiny/base instead of large)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Setup Guide](SETUP.md)** - Detailed installation instructions
- **[API Documentation](API.md)** - Complete API reference
- **[Architecture](ARCHITECTURE.md)** - System design and architecture
- **[Security](SECURITY.md)** - Security considerations and best practices
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[Examples](examples/)** - Code examples in Python and JavaScript

## Acknowledgments

- OpenAI Whisper for speech-to-text
- Coqui TTS for voice cloning
- yt-dlp for YouTube downloading
- Deep Translator for translation services

## Security Notes

⚠️ **Important**: 
- Never commit API keys or sensitive credentials
- Use environment variables for all configuration
- Implement rate limiting for production use
- Add authentication for production deployment
- Sanitize user inputs to prevent injection attacks

See [SECURITY.md](SECURITY.md) for detailed security considerations.
