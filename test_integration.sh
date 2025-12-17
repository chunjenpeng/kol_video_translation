#!/bin/bash

# Integration Test Script
# This script tests the basic functionality of the KOL Video Translation system

set -e

echo "========================================="
echo "KOL Video Translation Integration Test"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
check_service() {
    local service_name=$1
    local url=$2
    echo -n "Checking $service_name... "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not responding${NC}"
        return 1
    fi
}

# Test backend health
test_backend_health() {
    echo -n "Testing Backend Health... "
    response=$(curl -s http://localhost:8080/api/v1/health)
    if echo "$response" | grep -q "healthy"; then
        echo -e "${GREEN}✓ Passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test get languages
test_get_languages() {
    echo -n "Testing Get Languages... "
    response=$(curl -s http://localhost:8080/api/v1/languages)
    if echo "$response" | grep -q "English"; then
        echo -e "${GREEN}✓ Passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test Python service health
test_python_health() {
    echo -n "Testing Python Service Health... "
    response=$(curl -s http://localhost:5000/api/health)
    if echo "$response" | grep -q "python-video-processor"; then
        echo -e "${GREEN}✓ Passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test translation job creation (without actual processing)
test_create_job() {
    echo -n "Testing Job Creation... "
    response=$(curl -s -X POST http://localhost:8080/api/v1/translate \
        -H "Content-Type: application/json" \
        -d '{
            "youtube_url": "https://www.youtube.com/watch?v=test",
            "source_language": "en",
            "target_language": "es"
        }')
    
    if echo "$response" | grep -q "job_id"; then
        echo -e "${GREEN}✓ Passed${NC}"
        job_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
        echo "  Job ID: $job_id"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

echo "Running Basic Tests"
echo "-------------------"

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed${NC}"
    exit 1
fi

echo ""
echo "Note: This test expects services to be running on:"
echo "  - Backend: http://localhost:8080"
echo "  - Python Service: http://localhost:5000"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "If services are not running, start them with:"
echo "  docker-compose up    (for Docker)"
echo "  or run each service manually (see SETUP.md)"
echo ""

# Run tests
PASSED=0
FAILED=0

if test_backend_health; then
    ((PASSED++))
else
    ((FAILED++))
fi

if test_get_languages; then
    ((PASSED++))
else
    ((FAILED++))
fi

if test_python_health; then
    ((PASSED++))
else
    ((FAILED++))
fi

if test_create_job; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""
echo "========================================="
echo "Test Results"
echo "========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi
