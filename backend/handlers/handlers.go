package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/chunjenpeng/kol_video_translation/backend/models"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// In-memory job storage
// WARNING: This is a simple in-memory storage for demonstration purposes.
// For production use, implement persistent storage using:
// - Redis for distributed caching
// - PostgreSQL/MySQL for relational data
// - MongoDB for document storage
// This will ensure data persistence across restarts and horizontal scaling.
var (
	jobs   = make(map[string]*models.TranslationJob)
	jobsMu sync.RWMutex
)

// HealthCheck returns the health status of the API
func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"time":   time.Now().Format(time.RFC3339),
	})
}

// GetSupportedLanguages returns the list of supported languages
func GetSupportedLanguages(c *gin.Context) {
	languages := []models.Language{
		{Code: "en", Name: "English"},
		{Code: "es", Name: "Spanish"},
		{Code: "fr", Name: "French"},
		{Code: "de", Name: "German"},
		{Code: "it", Name: "Italian"},
		{Code: "pt", Name: "Portuguese"},
		{Code: "ru", Name: "Russian"},
		{Code: "ja", Name: "Japanese"},
		{Code: "ko", Name: "Korean"},
		{Code: "zh", Name: "Chinese (Simplified)"},
		{Code: "ar", Name: "Arabic"},
		{Code: "hi", Name: "Hindi"},
	}

	c.JSON(http.StatusOK, gin.H{
		"languages": languages,
	})
}

// TranslateVideo initiates a video translation job
func TranslateVideo(c *gin.Context) {
	var req models.TranslationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Create a new job
	job := &models.TranslationJob{
		ID:             uuid.New().String(),
		YouTubeURL:     req.YouTubeURL,
		SourceLanguage: req.SourceLanguage,
		TargetLanguage: req.TargetLanguage,
		Status:         models.StatusPending,
		Progress:       0,
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	// Store the job
	jobsMu.Lock()
	jobs[job.ID] = job
	jobsMu.Unlock()

	// Process the job asynchronously
	go processJob(job.ID)

	c.JSON(http.StatusAccepted, gin.H{
		"job_id": job.ID,
		"status": job.Status,
	})
}

// GetJobStatus returns the status of a translation job
func GetJobStatus(c *gin.Context) {
	jobID := c.Param("id")

	jobsMu.RLock()
	job, exists := jobs[jobID]
	jobsMu.RUnlock()

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	c.JSON(http.StatusOK, job)
}

// DownloadVideo returns the translated video file
func DownloadVideo(c *gin.Context) {
	jobID := c.Param("id")

	jobsMu.RLock()
	job, exists := jobs[jobID]
	jobsMu.RUnlock()

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	if job.Status != models.StatusCompleted {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Job not completed yet"})
		return
	}

	if job.OutputVideoPath == "" {
		c.JSON(http.StatusNotFound, gin.H{"error": "Video file not found"})
		return
	}

	c.File(job.OutputVideoPath)
}

// processJob processes a translation job by calling the Python service
func processJob(jobID string) {
	jobsMu.RLock()
	job := jobs[jobID]
	jobsMu.RUnlock()

	if job == nil {
		return
	}

	// Update job status to processing
	updateJobStatus(jobID, models.StatusDownloading, 10, "")

	// Get Python service URL from environment
	pythonServiceURL := os.Getenv("PYTHON_SERVICE_URL")
	if pythonServiceURL == "" {
		pythonServiceURL = "http://localhost:5000"
	}

	// Prepare request to Python service
	requestData := map[string]string{
		"job_id":          job.ID,
		"youtube_url":     job.YouTubeURL,
		"source_language": job.SourceLanguage,
		"target_language": job.TargetLanguage,
	}

	jsonData, err := json.Marshal(requestData)
	if err != nil {
		updateJobStatus(jobID, models.StatusFailed, 0, fmt.Sprintf("Failed to marshal request: %v", err))
		return
	}

	// Call Python service
	resp, err := http.Post(
		pythonServiceURL+"/api/process",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		updateJobStatus(jobID, models.StatusFailed, 0, fmt.Sprintf("Failed to call Python service: %v", err))
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusAccepted {
		updateJobStatus(jobID, models.StatusFailed, 0, fmt.Sprintf("Python service returned status %d", resp.StatusCode))
		return
	}

	log.Printf("Job %s submitted to Python service", jobID)
}

// updateJobStatus updates the status of a job
func updateJobStatus(jobID string, status models.JobStatus, progress int, errorMsg string) {
	jobsMu.Lock()
	defer jobsMu.Unlock()

	if job, exists := jobs[jobID]; exists {
		job.Status = status
		job.Progress = progress
		job.ErrorMessage = errorMsg
		job.UpdatedAt = time.Now()
	}
}

// UpdateJobFromPython is called by the Python service to update job status
func UpdateJobFromPython(c *gin.Context) {
	jobID := c.Param("id")

	jobsMu.RLock()
	job, exists := jobs[jobID]
	jobsMu.RUnlock()

	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	var update struct {
		Status          string `json:"status"`
		Progress        int    `json:"progress"`
		ErrorMessage    string `json:"error_message"`
		OutputVideoPath string `json:"output_video_path"`
		CaptionsPath    string `json:"captions_path"`
		ThumbnailPath   string `json:"thumbnail_path"`
	}

	if err := c.ShouldBindJSON(&update); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	jobsMu.Lock()
	job.Status = models.JobStatus(update.Status)
	job.Progress = update.Progress
	job.ErrorMessage = update.ErrorMessage
	if update.OutputVideoPath != "" {
		job.OutputVideoPath = update.OutputVideoPath
	}
	if update.CaptionsPath != "" {
		job.CaptionsPath = update.CaptionsPath
	}
	if update.ThumbnailPath != "" {
		job.ThumbnailPath = update.ThumbnailPath
	}
	job.UpdatedAt = time.Now()
	jobsMu.Unlock()

	c.JSON(http.StatusOK, gin.H{"status": "updated"})
}
