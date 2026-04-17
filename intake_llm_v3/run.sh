#!/usr/bin/env bash
set -e
python init_db.py
uvicorn app.api.main:app --reload --port 8000 &
API_PID=$!
streamlit run app/ui/streamlit_app.py --server.port 8501
kill $API_PID || true
