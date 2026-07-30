#!/bin/bash

cd /Users/shouryamarwaha/Documents/Projects/resume-builder

# Start backend in background
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ..
uv run streamlit run frontend/app.py &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:8501"
echo "Press CTRL+C to stop both"

# Wait and kill both on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait