#!/bin/bash

. .venv/bin/activate

# Function to kill processes on port 8000
kill_port_8000() {
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
}

# Function to kill processes on port 6060
kill_port_6060() {
    lsof -ti:6060 | xargs kill -9 2>/dev/null || true
}

# Function to handle Ctrl+C
cleanup() {
    echo ""
    echo "Terminating services and cleaning up ports..."
    
    # Kill the adk web process
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null || true
    fi

    # Kill the dummy fastapi service process
    if [ ! -z "$DUMMY_PID" ]; then
        kill $DUMMY_PID 2>/dev/null || true
    fi
    
    # Kill any process using ports
    kill_port_8000
    kill_port_6060

    # Stop docker containers
    echo "Stopping docker containers..."
    docker compose -f ../docker-compose/docker-compose.yml down
    
    cd ..
    echo "Cleanup complete"
    exit 0

}

# Set trap to catch Ctrl+C (SIGINT)
trap cleanup SIGINT

# Start docker containers
echo "Starting docker containers..."
docker compose -f docker-compose/docker-compose.yml up -d

cd src
# Start adk web on port 8000
echo "Starting adk web on port 8000..."

# Kill any existing processes before starting
echo "Checking for existing processes on ports 8000 and 6060..."
kill_port_8000
kill_port_6060
sleep 1

# Start dummy fastapi service on port 6060 with auto-reload
echo "Starting dummy fastapi service on port 6060..."
PYTHONPATH=$PYTHONPATH:$(pwd)/.. uv run uvicorn dummy_fastapi_service.main:app --host 0.0.0.0 --port 6060 --reload &
DUMMY_PID=$!

adk web --port 8000 --reload --reload_agents &
PID=$!

# Wait for the processes
wait $DUMMY_PID $PID
