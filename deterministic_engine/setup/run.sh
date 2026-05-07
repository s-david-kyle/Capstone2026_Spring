#!/usr/bin/env bash
set -e

MODE="${1:-all}"

case "$MODE" in
  api)
    uvicorn app.api.main:app --reload --port 8000
    ;;
  ui)
    streamlit run app/ui/streamlit_app.py
    ;;
  all)
    echo "Run one of these from the project root:"
    echo "  bash setup/run.sh api"
    echo "  bash setup/run.sh ui"
    ;;
  *)
    echo "Usage: bash setup/run.sh [api|ui|all]"
    exit 1
    ;;
esac
