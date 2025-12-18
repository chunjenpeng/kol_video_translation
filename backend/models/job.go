package models

import (
	"time"
)

// JobStatus represents the status of a translation job
type JobStatus string

const (
	StatusPending             JobStatus = "pending"
	StatusDownloading         JobStatus = "downloading"
	StatusTranscribing        JobStatus = "transcribing"
	StatusTranslating         JobStatus = "translating"
	StatusGeneratingVoice     JobStatus = "generating_voice"
	StatusGeneratingCaptions  JobStatus = "generating_captions"
	StatusGeneratingThumbnail JobStatus = "generating_thumbnail"
	StatusCompleted           JobStatus = "completed"
	StatusFailed              JobStatus = "failed"
)

// TranslationJob represents a video translation job
type TranslationJob struct {
	ID              string    `json:"id"`
	YouTubeURL      string    `json:"youtube_url"`
	SourceLanguage  string    `json:"source_language"`
	TargetLanguage  string    `json:"target_language"`
	Status          JobStatus `json:"status"`
	Progress        int       `json:"progress"` // 0-100
	ErrorMessage    string    `json:"error_message,omitempty"`
	OutputVideoPath string    `json:"output_video_path,omitempty"`
	CaptionsPath    string    `json:"captions_path,omitempty"`
	ThumbnailPath   string    `json:"thumbnail_path,omitempty"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
}

// TranslationRequest represents the request to translate a video
type TranslationRequest struct {
	YouTubeURL     string `json:"youtube_url" binding:"required"`
	SourceLanguage string `json:"source_language" binding:"required"`
	TargetLanguage string `json:"target_language" binding:"required"`
}

// Language represents a supported language
type Language struct {
	Code string `json:"code"`
	Name string `json:"name"`
}
