# API Documentation

## Base URL

- **Development**: `http://localhost:8080/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication

Currently, the API does not require authentication. For production use, implement authentication middleware.

## Endpoints

### Health Check

Check if the API is running.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "time": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Service is healthy

---

### Get Supported Languages

Retrieve a list of all supported languages for translation.

**Endpoint**: `GET /languages`

**Response**:
```json
{
  "languages": [
    {
      "code": "en",
      "name": "English"
    },
    {
      "code": "es",
      "name": "Spanish"
    },
    ...
  ]
}
```

**Status Codes**:
- `200 OK`: Successfully retrieved languages

---

### Create Translation Job

Submit a new video translation job.

**Endpoint**: `POST /translate`

**Request Body**:
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "source_language": "en",
  "target_language": "es"
}
```

**Request Parameters**:
- `youtube_url` (string, required): Valid YouTube video URL
- `source_language` (string, required): Source language code
- `target_language` (string, required): Target language code

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

**Status Codes**:
- `202 Accepted`: Job created successfully
- `400 Bad Request`: Invalid request parameters

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "source_language": "en",
    "target_language": "es"
  }'
```

---

### Get Job Status

Retrieve the current status and progress of a translation job.

**Endpoint**: `GET /job/:id`

**Path Parameters**:
- `id` (string): Job ID returned from the translate endpoint

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "source_language": "en",
  "target_language": "es",
  "status": "generating_voice",
  "progress": 55,
  "error_message": "",
  "output_video_path": "",
  "captions_path": "",
  "thumbnail_path": "",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

**Job Status Values**:
- `pending`: Job is queued
- `downloading`: Downloading video from YouTube
- `transcribing`: Transcribing audio to text
- `translating`: Translating text
- `generating_voice`: Generating translated audio with voice cloning
- `generating_captions`: Creating caption files
- `generating_thumbnail`: Generating thumbnail
- `completed`: Job finished successfully
- `failed`: Job failed (check error_message)

**Progress**: Integer from 0 to 100 indicating completion percentage

**Status Codes**:
- `200 OK`: Successfully retrieved job status
- `404 Not Found`: Job ID not found

**Example**:
```bash
curl http://localhost:8080/api/v1/job/550e8400-e29b-41d4-a716-446655440000
```

---

### Download Translated Video

Download the completed translated video file.

**Endpoint**: `GET /download/:id`

**Path Parameters**:
- `id` (string): Job ID

**Response**: Binary video file (MP4 format)

**Status Codes**:
- `200 OK`: File download started
- `400 Bad Request`: Job not completed yet
- `404 Not Found`: Job or file not found

**Example**:
```bash
curl -O http://localhost:8080/api/v1/download/550e8400-e29b-41d4-a716-446655440000
```

Or download via browser:
```
http://localhost:8080/api/v1/download/550e8400-e29b-41d4-a716-446655440000
```

---

### Update Job Status (Internal)

This endpoint is used internally by the Python service to update job status. Not intended for public use.

**Endpoint**: `PUT /job/:id`

**Path Parameters**:
- `id` (string): Job ID

**Request Body**:
```json
{
  "status": "completed",
  "progress": 100,
  "error_message": "",
  "output_video_path": "/app/output/job_id_final.mp4",
  "captions_path": "/app/output/job_id_captions.srt",
  "thumbnail_path": "/app/output/job_id_thumbnail.jpg"
}
```

**Status Codes**:
- `200 OK`: Job updated successfully
- `400 Bad Request`: Invalid request
- `404 Not Found`: Job not found

---

## Python Service API

The Python service has its own API for internal communication.

### Health Check

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "python-video-processor"
}
```

### Process Video (Internal)

**Endpoint**: `POST /api/process`

**Request Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "source_language": "en",
  "target_language": "es"
}
```

**Response**:
```json
{
  "status": "processing",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Common Status Codes**:
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error occurred

---

## Rate Limiting

Currently not implemented. For production use, implement rate limiting to prevent abuse.

**Recommended limits**:
- 10 requests per minute per IP
- 100 requests per hour per IP

---

## CORS

The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:
- Allowed Origins: All (`*`)
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed Headers: Content-Type, Authorization, etc.

For production, restrict origins to specific domains.

---

## Webhooks (Future Feature)

In a future version, you could implement webhooks to notify external systems when jobs complete:

```json
{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "output_video_url": "https://your-domain.com/api/v1/download/550e8400..."
}
```

---

## Client Libraries

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8080/api/v1';

// Get languages
const languages = await axios.get(`${API_BASE}/languages`);

// Start translation
const response = await axios.post(`${API_BASE}/translate`, {
  youtube_url: 'https://www.youtube.com/watch?v=...',
  source_language: 'en',
  target_language: 'es'
});

const jobId = response.data.job_id;

// Poll for status
const checkStatus = async () => {
  const status = await axios.get(`${API_BASE}/job/${jobId}`);
  return status.data;
};

// Download result
window.open(`${API_BASE}/download/${jobId}`, '_blank');
```

### Python

```python
import requests
import time

API_BASE = 'http://localhost:8080/api/v1'

# Get languages
languages = requests.get(f'{API_BASE}/languages').json()

# Start translation
response = requests.post(f'{API_BASE}/translate', json={
    'youtube_url': 'https://www.youtube.com/watch?v=...',
    'source_language': 'en',
    'target_language': 'es'
})

job_id = response.json()['job_id']

# Poll for completion
while True:
    status = requests.get(f'{API_BASE}/job/{job_id}').json()
    print(f"Status: {status['status']}, Progress: {status['progress']}%")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(3)

# Download result
if status['status'] == 'completed':
    video = requests.get(f'{API_BASE}/download/{job_id}')
    with open('translated_video.mp4', 'wb') as f:
        f.write(video.content)
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

const APIBase = "http://localhost:8080/api/v1"

type TranslateRequest struct {
    YouTubeURL     string `json:"youtube_url"`
    SourceLanguage string `json:"source_language"`
    TargetLanguage string `json:"target_language"`
}

type JobStatus struct {
    ID       string `json:"id"`
    Status   string `json:"status"`
    Progress int    `json:"progress"`
}

func main() {
    // Start translation
    req := TranslateRequest{
        YouTubeURL:     "https://www.youtube.com/watch?v=...",
        SourceLanguage: "en",
        TargetLanguage: "es",
    }
    
    body, _ := json.Marshal(req)
    resp, _ := http.Post(APIBase+"/translate", "application/json", bytes.NewBuffer(body))
    
    var result map[string]string
    json.NewDecoder(resp.Body).Decode(&result)
    jobID := result["job_id"]
    
    // Poll for completion
    for {
        resp, _ := http.Get(fmt.Sprintf("%s/job/%s", APIBase, jobID))
        var status JobStatus
        json.NewDecoder(resp.Body).Decode(&status)
        
        fmt.Printf("Status: %s, Progress: %d%%\n", status.Status, status.Progress)
        
        if status.Status == "completed" || status.Status == "failed" {
            break
        }
        
        time.Sleep(3 * time.Second)
    }
}
```

---

## Best Practices

1. **Poll Responsibly**: Don't poll job status more frequently than every 2-3 seconds
2. **Handle Errors**: Always check status codes and handle errors gracefully
3. **Validate Input**: Validate YouTube URLs before sending to API
4. **Store Job IDs**: Save job IDs for later retrieval of results
5. **Implement Timeouts**: Set appropriate timeouts for HTTP requests
6. **Check File Size**: Be aware of large file downloads

---

## Performance Notes

- Video processing time varies based on video length (typically 2-5x the video duration)
- Longer videos require more processing time
- Voice cloning is the most time-intensive step
- Concurrent job processing is supported

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/chunjenpeng/kol_video_translation/issues
- Documentation: See README.md and SETUP.md
