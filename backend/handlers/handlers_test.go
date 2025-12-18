package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/chunjenpeng/kol_video_translation/backend/models"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redismock/v9"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
)

func SetupRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	r.POST("/api/v1/translate", TranslateVideo)
	r.GET("/api/v1/job/:id", GetJobStatus)
	return r
}

func TestTranslateVideo(t *testing.T) {
	db, mock := redismock.NewClientMock()
	SetRedisClient(db)

	// Mock ID generation
	GenerateID = func() string {
		return "test-uuid"
	}
	// Define fixed time for deterministic testing
	fixedTime := time.Date(2023, 1, 1, 12, 0, 0, 0, time.UTC)
	Now = func() time.Time {
		return fixedTime
	}

	router := SetupRouter()

	t.Run("Success", func(t *testing.T) {
		reqBody := models.TranslationRequest{
			YouTubeURL:     "https://youtube.com/watch?v=123",
			SourceLanguage: "en",
			TargetLanguage: "es",
		}
		jsonValue, _ := json.Marshal(reqBody)

		// Create expected job for validation
		expectedJob := &models.TranslationJob{
			ID:             "test-uuid",
			YouTubeURL:     reqBody.YouTubeURL,
			SourceLanguage: reqBody.SourceLanguage,
			TargetLanguage: reqBody.TargetLanguage,
			Status:         models.StatusPending,
			Progress:       0,
			CreatedAt:      fixedTime,
			UpdatedAt:      fixedTime,
		}
		expectedJSON, _ := json.Marshal(expectedJob)

		mock.ExpectSet("job:test-uuid", expectedJSON, 24*time.Hour).SetVal("OK")
		mock.ExpectRPush("jobs_queue", "test-uuid").SetVal(1)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/v1/translate", bytes.NewBuffer(jsonValue))
		router.ServeHTTP(w, req)

		assert.Equal(t, 202, w.Code)

		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)

		assert.Equal(t, "pending", response["status"])
		assert.Equal(t, "test-uuid", response["job_id"])
	})

	t.Run("Invalid Input", func(t *testing.T) {
		reqBody := models.TranslationRequest{
			YouTubeURL: "https://youtube.com/watch?v=123",
		}
		jsonValue, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/v1/translate", bytes.NewBuffer(jsonValue))
		router.ServeHTTP(w, req)

		assert.Equal(t, 400, w.Code)
	})
}

func TestGetJobStatus(t *testing.T) {
	db, mock := redismock.NewClientMock()
	SetRedisClient(db)

	router := SetupRouter()

	t.Run("Job Found", func(t *testing.T) {
		jobID := "test-job-id"
		job := models.TranslationJob{
			ID:     jobID,
			Status: models.StatusCompleted,
		}
		jobJSON, _ := json.Marshal(job)

		mock.ExpectGet("job:" + jobID).SetVal(string(jobJSON))

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/job/"+jobID, nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, 200, w.Code)

		var response models.TranslationJob
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, models.StatusCompleted, response.Status)
	})

	t.Run("Job Not Found", func(t *testing.T) {
		jobID := "missing-job"
		// FIX: Use redis.Nil explicitly
		mock.ExpectGet("job:" + jobID).SetErr(redis.Nil)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/job/"+jobID, nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, 404, w.Code)
	})
}
