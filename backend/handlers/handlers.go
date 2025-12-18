package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/chunjenpeng/kol_video_translation/backend/models"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
)

var (
	rdb *redis.Client
	ctx = context.Background()
	// GenerateID is used to generate unique IDs (can be mocked for testing)
	GenerateID = func() string {
		return uuid.New().String()
	}
	// Now is used for time generation (can be mocked)
	Now = time.Now
)

// InitRedis initializes the Redis client
func InitRedis() {
	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		redisHost = "localhost"
	}
	redisPort := os.Getenv("REDIS_PORT")
	if redisPort == "" {
		redisPort = "6379"
	}

	rdb = redis.NewClient(&redis.Options{
		Addr: fmt.Sprintf("%s:%s", redisHost, redisPort),
	})

	// Test connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
	log.Println("Connected to Redis successfully")
}

// SetRedisClient sets the Redis client (used for testing)
func SetRedisClient(client *redis.Client) {
	rdb = client
}

// HealthCheck returns the health status of the API
func HealthCheck(c *gin.Context) {
	redisStatus := "up"
	if _, err := rdb.Ping(ctx).Result(); err != nil {
		redisStatus = "down"
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"redis":  redisStatus,
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
		{Code: "zh-CN", Name: "Chinese (Simplified)"},
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
		ID:             GenerateID(),
		YouTubeURL:     req.YouTubeURL,
		SourceLanguage: req.SourceLanguage,
		TargetLanguage: req.TargetLanguage,
		Status:         models.StatusPending,
		Progress:       0,
		CreatedAt:      Now(),
		UpdatedAt:      Now(),
	}

	// Serialize job to JSON
	jobJSON, err := json.Marshal(job)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to serialize job"})
		return
	}

	// Save to Redis (Key: job:{id})
	err = rdb.Set(ctx, fmt.Sprintf("job:%s", job.ID), jobJSON, 24*time.Hour).Err() // Expire in 24 hours
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save job to Redis"})
		return
	}

	// Push job ID to Queue (List: jobs_queue)
	err = rdb.RPush(ctx, "jobs_queue", job.ID).Err()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add job to queue"})
		return
	}

	log.Printf("Job %s submitted and queued", job.ID)

	c.JSON(http.StatusAccepted, gin.H{
		"job_id": job.ID,
		"status": job.Status,
	})
}

// GetJobStatus returns the status of a translation job
func GetJobStatus(c *gin.Context) {
	jobID := c.Param("id")

	// Get job from Redis
	val, err := rdb.Get(ctx, fmt.Sprintf("job:%s", jobID)).Result()
	if err == redis.Nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	var job models.TranslationJob
	if err := json.Unmarshal([]byte(val), &job); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse job data"})
		return
	}

	c.JSON(http.StatusOK, job)
}

// DownloadVideo returns the translated video file
func DownloadVideo(c *gin.Context) {
	jobID := c.Param("id")

	// Get job from Redis
	val, err := rdb.Get(ctx, fmt.Sprintf("job:%s", jobID)).Result()
	if err == redis.Nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	var job models.TranslationJob
	if err := json.Unmarshal([]byte(val), &job); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse job data"})
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

	// Handle both relative and absolute paths
	// If path starts with "output/", convert to absolute path in shared volume
	videoPath := job.OutputVideoPath
	if len(videoPath) >= 7 && videoPath[:7] == "output/" {
		videoPath = "/app/" + videoPath
	}

	// Check if file exists
	if _, err := os.Stat(videoPath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Video file not found on disk"})
		return
	}

	c.File(videoPath)
}
