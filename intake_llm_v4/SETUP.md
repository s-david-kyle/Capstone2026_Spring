# Setup

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Start Ollama and pull `llama3.1`.
4. Run `python init_db.py`.
5. Start the FastAPI backend on port 8000.
6. Start the Streamlit UI on port 8501.

Environment variable for the UI:
- `UI_API_BASE_URL` defaults to `http://localhost:8000`
