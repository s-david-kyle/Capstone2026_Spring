#!/usr/bin/env bash
set -e

# Kill any existing uvicorn process on port 8000
echo "Checking for existing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "Starting FastAPI backend on port 8000..."
uvicorn app.api.main:app --reload --port 8000 &
API_PID=$!

echo "Starting Streamlit frontend on port 8501..."
streamlit run app/ui/streamlit_app.py --server.port 8501

echo "Shutting down backend..."
kill $API_PID || true