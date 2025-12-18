.PHONY: help build run stop clean test

# Default target
help:
	@echo "KOL Video Translation - Available Commands:"
	@echo ""
	@echo "  make build      - Build all Docker containers"
	@echo "  make run        - Start all services with Docker Compose"
	@echo "  make stop       - Stop all running services"
	@echo "  make clean      - Remove all containers, volumes, and temporary files"
	@echo "  make logs       - Show logs from all services"
	@echo "  make dev-backend   - Run backend in development mode"
	@echo "  make dev-python    - Run Python service in development mode"
	@echo "  make dev-frontend  - Run frontend in development mode"
	@echo ""

# Docker commands
build:
	docker-compose build

run:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8080"
	@echo "Python Service: http://localhost:5000"

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf output/* temp/*
	@echo "Cleaned up containers, volumes, and temporary files"

logs:
	docker-compose logs -f

# Development commands
dev-backend:
	cd backend && go run main.go

dev-python:
	cd python_service && python app.py

dev-frontend:
	cd frontend && npm run dev

# Setup commands
setup-backend:
	cd backend && go mod download

setup-python:
	cd python_service && pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install

setup-all: setup-backend setup-python setup-frontend
	@echo "All dependencies installed!"
