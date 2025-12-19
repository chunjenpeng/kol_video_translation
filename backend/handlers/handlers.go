package handlers

import (
	"context"
	"log"
	"net/http"
	"os"
	"regexp"
	"time"

	"github.com/chunjenpeng/kol_video_translation/backend/constants"
	"github.com/chunjenpeng/kol_video_translation/backend/models"
	"github.com/chunjenpeng/kol_video_translation/backend/services"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
)

var (
	rdb             *redis.Client
	jobService      *services.JobService
	youtubeURLRegex *regexp.Regexp
	// GenerateID is used to generate unique IDs (can be mocked for testing)
	GenerateID = func() string {
		return uuid.New().String()
	}
	// Now is used for time generation (can be mocked)
	Now = time.Now
)

// InitRedis initializes the Redis client and job service
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
		Addr: redisHost + ":" + redisPort,
	})

	// Test connection
	ctx := rdb.Context()
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	// Initialize job service
	jobService = services.NewJobService(rdb)

	// Compile YouTube URL regex
	youtubeURLRegex = regexp.MustCompile(constants.YouTubeURLPattern)

	log.Println("Connected to Redis successfully")
}

// SetRedisClient sets the Redis client (used for testing)
func SetRedisClient(client *redis.Client) {
	rdb = client
	jobService = services.NewJobService(client)
}

// HealthCheck returns the health status of the API
func HealthCheck(c *gin.Context) {
	redisStatus := "up"
	ctx := context.Background()
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
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid request body",
			"details": err.Error(),
		})
		return
	}

	// Validate required fields
	if req.YouTubeURL == "" || req.SourceLanguage == "" || req.TargetLanguage == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "missing required fields",
			"details": gin.H{
				"youtube_url":     req.YouTubeURL == "",
				"source_language": req.SourceLanguage == "",
				"target_language": req.TargetLanguage == "",
			},
		})
		return
	}

	// Validate YouTube URL format
	if !youtubeURLRegex.MatchString(req.YouTubeURL) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid YouTube URL format",
			"details": "URL must be in format: https://www.youtube.com/watch?v=... or https://youtu.be/...",
		})
		return
	}

	// Generate job ID
	jobID := GenerateID()

	// Create job using service layer
	createdAt := Now()
	if err := jobService.CreateJob(jobID, req, createdAt); err != nil {
		log.Printf("Error creating job: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to create job",
			"details": err.Error(),
		})
		return
	}

	log.Printf("Job %s submitted and queued", jobID)

	c.JSON(http.StatusAccepted, gin.H{
		"job_id": jobID,
		"status": constants.StatusPending,
	})
}

// GetJobStatus returns the status of a translation job
func GetJobStatus(c *gin.Context) {
	jobID := c.Param("id")

	// Get job using service layer
	job, err := jobService.GetJob(jobID)
	if err != nil {
		if err.Error() == "job not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": "job not found"})
		} else {
			log.Printf("Error getting job: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error":   "failed to retrieve job",
				"details": err.Error(),
			})
		}
		return
	}

	c.JSON(http.StatusOK, job)
}

// DownloadVideo returns the translated video file
func DownloadVideo(c *gin.Context) {
	jobID := c.Param("id")

	// Get job using service layer
	job, err := jobService.GetJob(jobID)
	if err != nil {
		if err.Error() == "job not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": "job not found"})
		} else {
			log.Printf("Error getting job: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error":   "failed to retrieve job",
				"details": err.Error(),
			})
		}
		return
	}

	if job.Status != constants.StatusCompleted {
		c.JSON(http.StatusBadRequest, gin.H{"error": "job not completed yet"})
		return
	}

	if job.OutputVideoPath == "" {
		c.JSON(http.StatusNotFound, gin.H{"error": "video file not found"})
		return
	}

	// Handle both relative and absolute paths
	videoPath := job.OutputVideoPath
	if len(videoPath) >= 7 && videoPath[:7] == "output/" {
		videoPath = "/app/" + videoPath
	}

	// Check if file exists
	if _, err := os.Stat(videoPath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "video file not found on disk"})
		return
	}

	c.File(videoPath)
}
