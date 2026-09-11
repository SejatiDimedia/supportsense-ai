#!/bin/bash
# SupportSense AI: Interactive React Frontend Launcher

set -e

echo "========================================================"
echo "          Starting SupportSense AI React Console        "
echo "========================================================"

# 1. Activate Python virtual environment if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 2. Check and start FastAPI backend if not already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "[1/2] FastAPI backend is already running on http://localhost:8000"
else
    echo "[1/2] Starting FastAPI backend on http://localhost:8000..."
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    sleep 2
    echo "FastAPI backend started (PID: $BACKEND_PID)"
fi

# 3. Start React Frontend via Vite
echo "[2/2] Launching React Vite Development Server on http://localhost:5173..."
cd frontend
npm run dev
