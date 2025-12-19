package middleware

import (
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// RateLimiter implements a simple token bucket rate limiter
type RateLimiter struct {
	mu              sync.Mutex
	clients         map[string]*clientBucket
	rate            int           // requests per window
	window          time.Duration // time window
	cleanupInterval time.Duration
}

type clientBucket struct {
	tokens    int
	lastReset time.Time
}

// NewRateLimiter creates a new rate limiter
// rate: number of requests allowed per window
// window: time window duration
func NewRateLimiter(rate int, window time.Duration) *RateLimiter {
	rl := &RateLimiter{
		clients:         make(map[string]*clientBucket),
		rate:            rate,
		window:          window,
		cleanupInterval: 10 * time.Minute,
	}

	// Start cleanup goroutine
	go rl.cleanup()

	return rl
}

// cleanup removes stale client buckets
func (rl *RateLimiter) cleanup() {
	ticker := time.NewTicker(rl.cleanupInterval)
	defer ticker.Stop()

	for range ticker.C {
		rl.mu.Lock()
		now := time.Now()
		for ip, bucket := range rl.clients {
			if now.Sub(bucket.lastReset) > rl.window*2 {
				delete(rl.clients, ip)
			}
		}
		rl.mu.Unlock()
	}
}

// Middleware returns a Gin middleware function
func (rl *RateLimiter) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		ip := c.ClientIP()

		if !rl.allow(ip) {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error":   "rate limit exceeded",
				"details": "too many requests, please try again later",
			})
			c.Abort()
			return
		}

		c.Next()
	}
}

// allow checks if a request from the given IP should be allowed
func (rl *RateLimiter) allow(ip string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	bucket, exists := rl.clients[ip]

	if !exists || now.Sub(bucket.lastReset) > rl.window {
		// Create new bucket or reset existing one
		rl.clients[ip] = &clientBucket{
			tokens:    rl.rate - 1,
			lastReset: now,
		}
		return true
	}

	if bucket.tokens > 0 {
		bucket.tokens--
		return true
	}

	return false
}
