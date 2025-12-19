package constants

// Redis keys
const (
	RedisJobPrefix = "job:"
	RedisJobsQueue = "jobs_queue"
	RedisJobExpiry = 24 // hours
)

// Job status values
const (
	StatusPending    = "pending"
	StatusProcessing = "processing"
	StatusCompleted  = "completed"
	StatusFailed     = "failed"
)

// Validation
const (
	YouTubeURLPattern = `^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11}$`
)
