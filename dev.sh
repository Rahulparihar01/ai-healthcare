#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting HealthID AI Development Environment...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Database might fail to connect!${NC}"
fi

# Pre-flight check: Free ports 8000 and 5173 if lingering
echo -e "${BLUE}Checking ports 8000 and 5173...${NC}"
DOCKER_CONFLICT=$(docker ps --filter "publish=8000" --format "{{.Names}}" 2>/dev/null)
if [ -n "$DOCKER_CONFLICT" ]; then
    echo -e "${YELLOW}Stopping conflicting Docker container on port 8000: $DOCKER_CONFLICT...${NC}"
    docker stop "$DOCKER_CONFLICT" >/dev/null 2>&1 || true
fi

fuser -k 8000/tcp >/dev/null 2>&1 || true
fuser -k 5173/tcp >/dev/null 2>&1 || true

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill -TERM $BACKEND_PID $FRONTEND_PID $CELERY_PID 2>/dev/null || true
    pkill -P $BACKEND_PID 2>/dev/null || true
    pkill -P $CELERY_PID 2>/dev/null || true
    pkill -P $FRONTEND_PID 2>/dev/null || true
    fuser -k 8000/tcp >/dev/null 2>&1 || true
    fuser -k 5173/tcp >/dev/null 2>&1 || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "${GREEN}Starting FastAPI Backend on port 8000...${NC}"
cd app
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}Starting Celery Worker...${NC}"
celery -A celery_app worker --loglevel=info &
CELERY_PID=$!

cd ..

# Health check loop for backend
echo -e "${YELLOW}Waiting for backend to become healthy...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while ! curl -sf http://localhost:8000/api/v1/healthz > /dev/null 2>&1; do
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}Backend failed to start after $MAX_RETRIES seconds! Check the logs above.${NC}"
        cleanup
    fi
done
echo -e "${GREEN}Backend is healthy!${NC}"

# Start Frontend
echo -e "${GREEN}Starting React/Vite Frontend on port 5173...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}All services started successfully! Press Ctrl+C to stop everything.${NC}"
echo -e "Backend running at: http://localhost:8000"
echo -e "Frontend running at: http://localhost:5173"

wait
