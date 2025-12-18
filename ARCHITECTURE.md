# Architecture Documentation

## Overview

The KOL Video Translation application follows a microservices architecture with three main components:

1. **Backend API (Golang)** - Request handling and job orchestration
2. **Python Service** - Video processing and AI operations
3. **Frontend (React)** - User interface

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                      (React Frontend)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Go Backend API (Port 8080)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Handlers: Health, Translate, Status, Download          │ │
│  │ Middleware: CORS, Logging                              │ │
│  │ Models: Job, Language                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│                 In-Memory Job Storage                        │
│                 (Map + Mutex for thread-safety)             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Python Processing Service (Port 5000)           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Video Processor (Main Pipeline)                         │ │
│  │  ├─ YouTube Downloader (yt-dlp)                        │ │
│  │  ├─ Transcription Service (Whisper)                    │ │
│  │  ├─ Translation Service (Google Translate)             │ │
│  │  ├─ Voice Cloning Service (Coqui TTS)                  │ │
│  │  ├─ Caption Generator (SRT format)                     │ │
│  │  ├─ Thumbnail Generator (PIL/MoviePy)                  │ │
│  │  └─ Video Merger (MoviePy)                             │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
                ┌────────────────┐
                │  File Storage  │
                │  (temp, output)│
                └────────────────┘
```

## Component Details

### 1. Frontend (React + Vite)

**Purpose:** User interface for video translation

**Key Features:**
- Video URL input
- Language selection
- Real-time progress tracking
- Result download

**Technology Stack:**
- React 18
- Vite (build tool)
- Axios (HTTP client)
- CSS (responsive styling)

**Architecture Pattern:** Component-based

**Components:**
- `App.jsx` - Main application container
- `VideoForm.jsx` - Input form for translation jobs
- `JobStatus.jsx` - Progress display and results

**State Management:**
- React hooks (useState, useEffect)
- Polling mechanism for job updates

**Communication:**
- REST API calls to backend
- Polling interval: 3 seconds

### 2. Backend API (Golang + Gin)

**Purpose:** API server for request handling and orchestration

**Key Responsibilities:**
- Accept translation requests
- Manage job lifecycle
- Store job metadata
- Serve static files
- Forward processing to Python service

**Technology Stack:**
- Go 1.21
- Gin web framework
- UUID for job IDs
- sync.RWMutex for concurrency

**Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/languages | Get supported languages |
| POST | /api/v1/translate | Start translation job |
| GET | /api/v1/job/:id | Get job status |
| PUT | /api/v1/job/:id | Update job (internal) |
| GET | /api/v1/download/:id | Download result |

**Job States:**
```
pending → downloading → transcribing → translating → 
generating_voice → generating_captions → generating_thumbnail → 
completed/failed
```

**Concurrency Model:**
- Goroutines for async job processing
- RWMutex for thread-safe job storage
- Non-blocking API responses

### 3. Python Processing Service (Flask)

**Purpose:** Heavy video processing and AI operations

**Key Responsibilities:**
- Download YouTube videos
- Transcribe audio to text
- Translate text
- Generate cloned voice
- Create captions
- Generate thumbnails
- Merge final video

**Technology Stack:**
- Python 3.10
- Flask (web framework)
- yt-dlp (YouTube downloader)
- OpenAI Whisper (speech-to-text)
- Deep Translator (translation)
- Coqui TTS (text-to-speech)
- MoviePy (video processing)
- Pillow (image processing)

**Processing Pipeline:**

```
1. Download Video (yt-dlp)
   ├─ Video file (.mp4)
   └─ Audio file (.wav)

2. Transcribe Audio (Whisper)
   └─ Segments with timestamps

3. Translate Text (Google Translate)
   └─ Translated segments

4. Generate Voice (Coqui TTS)
   ├─ Voice cloning from original
   └─ Translated audio (.wav)

5. Generate Captions (SRT)
   └─ Caption file (.srt)

6. Generate Thumbnail (PIL/MoviePy)
   └─ Thumbnail image (.jpg)

7. Merge Video + Audio
   └─ Final video (.mp4)
```

**Threading Model:**
- Background threads for processing
- Non-blocking request handling
- Updates backend via HTTP callbacks

## Data Flow

### Translation Request Flow

```
1. User submits URL via Frontend
   ↓
2. Frontend POST /api/v1/translate
   ↓
3. Backend creates job with unique ID
   ↓
4. Backend returns job ID (202 Accepted)
   ↓
5. Backend async calls Python service
   ↓
6. Python service starts processing
   ↓
7. Frontend polls GET /api/v1/job/:id
   ↓
8. Backend returns job status
   ↓
9. Python service updates progress via PUT
   ↓
10. Job completes (success/failure)
   ↓
11. Frontend downloads result
```

### Status Update Flow

```
Python Service           Backend API           Frontend
     │                       │                     │
     │ PUT /api/v1/job/:id  │                     │
     │ (status, progress)   │                     │
     │─────────────────────>│                     │
     │                       │                     │
     │                       │ GET /api/v1/job/:id │
     │                       │<────────────────────│
     │                       │                     │
     │                       │ {status, progress}  │
     │                       │────────────────────>│
```

## Storage Architecture

### Current Implementation

**Job Storage:**
- In-memory map (Go)
- Thread-safe with sync.RWMutex
- Lost on restart

**File Storage:**
- Local filesystem
- Temporary files: `temp/`
- Output files: `output/`

### Recommended Production Architecture

```
┌──────────────┐
│   Backend    │──────> Redis (Job metadata + cache)
└──────────────┘
       │
       └─────────> PostgreSQL (Persistent jobs + history)
       
┌──────────────┐
│   Python     │──────> S3/GCS (Video files)
└──────────────┘
       │
       └─────────> CDN (Serve completed videos)
```

## Scalability Considerations

### Current Limitations

1. **Single Instance:** No horizontal scaling
2. **In-Memory Storage:** Not distributed
3. **File Storage:** Local disk only
4. **No Queue:** Direct processing, no buffering

### Scaling Strategy

#### Horizontal Scaling

**Backend:**
- Deploy multiple instances behind load balancer
- Use Redis for shared job storage
- Use database for persistence

**Python Service:**
- Deploy multiple workers
- Use message queue (RabbitMQ, Redis Queue)
- Distribute processing load

**Architecture:**
```
Load Balancer
    ↓
Backend (N instances) → Redis → PostgreSQL
    ↓
Message Queue (RabbitMQ)
    ↓
Python Workers (M instances) → S3/GCS
```

#### Vertical Scaling

- Increase CPU for faster processing
- Increase RAM for larger videos
- Add GPU for faster AI operations

## Performance Optimization

### Current Performance

- Small video (3 min): ~5-15 minutes
- Medium video (10 min): ~15-45 minutes
- Large video (30 min): ~45-120 minutes

### Optimization Strategies

1. **Model Selection:**
   - Use smaller Whisper model (base vs large)
   - Cache model weights in memory
   - Use quantized models

2. **Parallel Processing:**
   - Process segments in parallel
   - Use multiprocessing for CPU-bound tasks
   - Use async/await for I/O operations

3. **Caching:**
   - Cache transcriptions
   - Cache translations
   - Reuse voice models

4. **Hardware:**
   - GPU acceleration for AI models
   - SSD for faster I/O
   - More RAM for larger files

## Security Architecture

See [SECURITY.md](SECURITY.md) for detailed security considerations.

**Key Points:**
- No authentication (add in production)
- CORS enabled (restrict in production)
- No rate limiting (add in production)
- Debug mode disabled by default
- Input validation on all endpoints

## Deployment Options

### Option 1: Docker Compose (Development/Small Scale)

```bash
docker-compose up
```

**Pros:** Simple, all-in-one
**Cons:** Single host, not scalable

### Option 2: Kubernetes (Production/Large Scale)

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  ...
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-service
spec:
  replicas: 5
  ...
```

**Pros:** Scalable, resilient, auto-healing
**Cons:** Complex setup

### Option 3: Cloud Services

**AWS:**
- ECS/Fargate for containers
- S3 for file storage
- RDS for database
- ElastiCache for Redis

**GCP:**
- Cloud Run for containers
- Cloud Storage for files
- Cloud SQL for database
- Memorystore for Redis

## Monitoring & Observability

### Recommended Tools

- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics:** Prometheus + Grafana
- **Tracing:** Jaeger or Zipkin
- **Alerting:** PagerDuty or OpsGenie

### Key Metrics to Monitor

- Request rate
- Error rate
- Response time
- Job completion time
- Queue length
- Resource usage (CPU, RAM, Disk)
- Failed jobs

## Future Enhancements

1. **Authentication & Authorization**
2. **Queue System** (RabbitMQ/Redis Queue)
3. **Database Integration** (PostgreSQL)
4. **Cloud Storage** (S3/GCS)
5. **CDN Integration** (CloudFront/Cloud CDN)
6. **WebSocket Support** (real-time updates)
7. **Batch Processing**
8. **Multiple Quality Options**
9. **Advanced Voice Cloning**
10. **Custom Model Training**

## Conclusion

This architecture provides a solid foundation for video translation with voice cloning. For production deployment, additional components (authentication, queuing, persistent storage) should be implemented based on specific requirements and scale.
