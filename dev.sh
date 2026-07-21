#!/bin/bash

# Define colors for output
GREEN='\039[0;32m'
BLUE='\039[0;34m'
YELLOW='\039[1;33m'
RED='\039[0;31m'
NC='\039[0m' # No Color

echo -e "${BLUE}Starting HealthID AI Development Environment...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Database might fail to connect!${NC}"
fi

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Start Backend
echo -e "${GREEN}Installing Backend Dependencies...${NC}"
cd backend
pip install -r requirements.txt

echo -e "${GREEN}Starting FastAPI Backend on port 8000...${NC}"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Health check loop for backend
echo -e "${YELLOW}Waiting for backend to become healthy...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while ! curl -s http://localhost:8000/ > /dev/null; do
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo -e "${RED}Backend failed to start after $MAX_RETRIES seconds! Check the logs above.${NC}"
        cleanup
    fi
done
echo -e "${GREEN}Backend is healthy!${NC}"

# Start Frontend
echo -e "${GREEN}Installing Frontend Dependencies...${NC}"
cd frontend
npm install

echo -e "${GREEN}Starting React/Vite Frontend on port 5173...${NC}"
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}All services started successfully! Press Ctrl+C to stop everything.${NC}"
echo -e "Backend running at: http://localhost:8000"
echo -e "Frontend running at: http://localhost:5173"

wait
