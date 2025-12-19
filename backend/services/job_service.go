package services

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/chunjenpeng/kol_video_translation/backend/constants"
	"github.com/chunjenpeng/kol_video_translation/backend/models"
	"github.com/redis/go-redis/v9"
)

// JobService handles job-related operations
type JobService struct {
	redis *redis.Client
}

// NewJobService creates a new JobService
func NewJobService(redisClient *redis.Client) *JobService {
	return &JobService{redis: redisClient}
}

// CreateJob creates a new translation job
func (s *JobService) CreateJob(jobID string, req models.TranslationRequest, createdAt time.Time) error {
	job := &models.TranslationJob{
		ID:             jobID,
		YouTubeURL:     req.YouTubeURL,
		SourceLanguage: req.SourceLanguage,
		TargetLanguage: req.TargetLanguage,
		Status:         constants.StatusPending,
		Progress:       0,
		CreatedAt:      createdAt,
		UpdatedAt:      createdAt,
	}

	jobJSON, err := json.Marshal(job)
	if err != nil {
		return fmt.Errorf("failed to marshal job: %w", err)
	}

	ctx := context.Background()

	// Save job to Redis
	key := constants.RedisJobPrefix + jobID
	if err := s.redis.Set(ctx, key, jobJSON, constants.RedisJobExpiry*time.Hour).Err(); err != nil {
		return fmt.Errorf("failed to save job to Redis: %w", err)
	}

	// Queue job for processing
	if err := s.redis.RPush(ctx, constants.RedisJobsQueue, jobID).Err(); err != nil {
		return fmt.Errorf("failed to queue job: %w", err)
	}

	return nil
}

// GetJob retrieves a job by ID
func (s *JobService) GetJob(jobID string) (*models.TranslationJob, error) {
	ctx := context.Background()
	key := constants.RedisJobPrefix + jobID

	jobJSON, err := s.redis.Get(ctx, key).Result()
	if err == redis.Nil {
		return nil, fmt.Errorf("job not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get job from Redis: %w", err)
	}

	var job models.TranslationJob
	if err := json.Unmarshal([]byte(jobJSON), &job); err != nil {
		return nil, fmt.Errorf("failed to unmarshal job: %w", err)
	}

	return &job, nil
}
