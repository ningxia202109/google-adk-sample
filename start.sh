#!/bin/bash

. .venv/bin/activate

# Function to handle Ctrl+C
cleanup() {
    echo ""
    echo "Terminating adk web and cleaning up port 8000..."
    
    # Kill the adk web process
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null || true
    fi
    
    # Kill any process using port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    cd ..
    echo "Cleanup complete"
    exit 0

}

# Set trap to catch Ctrl+C (SIGINT)
trap cleanup SIGINT
cd src
# Start adk web on port 8000
echo "Starting adk web on port 8000..."
adk web --port 8000 &
PID=$!

# Wait for the process
wait $PID
