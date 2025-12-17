package main

import (
	"log"
	"os"

	"github.com/chunjenpeng/kol_video_translation/backend/handlers"
	"github.com/chunjenpeng/kol_video_translation/backend/middleware"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// Initialize Gin router
	router := gin.Default()

	// Apply middleware
	router.Use(middleware.CORSMiddleware())

	// API routes
	api := router.Group("/api/v1")
	{
		api.GET("/health", handlers.HealthCheck)
		api.POST("/translate", handlers.TranslateVideo)
		api.GET("/job/:id", handlers.GetJobStatus)
		api.PUT("/job/:id", handlers.UpdateJobFromPython)
		api.GET("/download/:id", handlers.DownloadVideo)
		api.GET("/languages", handlers.GetSupportedLanguages)
	}

	// Serve static files for frontend
	router.Static("/static", "./static")
	router.StaticFile("/", "./static/index.html")

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
