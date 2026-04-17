# Clinical Intake System

A deterministic, complaint-driven clerking app that uses complaint JSON contracts, shared skip/ask rules, SQLite persistence, a Streamlit UI, and Ollama for HPI refinement.

## What was corrected

- Normalized all uploaded filenames into a runnable package layout.
- Restored a real Streamlit UI (the uploaded `streamlit_app.py` contained summary-engine code instead of UI code).
- Fixed package imports by placing API, DB, engine, and UI files under `app/...`.
- Added deterministic phase orchestration: complaint flow -> ROS -> history modules -> summary.
- Added SQLite initialization and encounter/turn/summary persistence.
- Added Ollama summary call with safe fallback to the template HPI.
- Added doctor-edit workflow and transcript download.
- Preserved the uploaded complaint JSON contracts and module content.

## Project layout

- `app/api/main.py` - FastAPI backend
- `app/ui/streamlit_app.py` - Streamlit frontend
- `app/engine/intake_engine.py` - complaint scheduler
- `app/engine/ros_runner.py` - ROS scheduler
- `app/engine/module_runner.py` - reusable history modules
- `app/engine/summary_engine.py` - template and Ollama summary generation
- `app/db/db_manager.py` - SQLite persistence
- `complaints_modules/complaints/*.json` - complaint contracts
- `complaints_modules/modules/*.json` - shared history modules
- `complaints_modules/shared_v2.json` - shared runtime rules
- `complaints_modules/ros_question_bank.json` - ROS bank
- `complaints_modules/index_v2.json` - complaint registry

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
ollama serve
ollama pull llama3.1
uvicorn app.api.main:app --reload --port 8000
```

In another terminal:

```bash
source venv/bin/activate
streamlit run app/ui/streamlit_app.py --server.port 8501
```

Or run both with:

```bash
./run.sh
```

## Notes

- The runtime honors the complaint-owned schedules and budgets from the uploaded contracts.
- ROS is intentionally lightweight and deduplicated against already captured concepts.
- The API stores encounter state, turns, summaries, and metrics in SQLite.
- The doctor can edit the final summary and save it back to the database.
