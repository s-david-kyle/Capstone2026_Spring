# Setup v1.1

This guide sets up the Clinical Intake Runtime v1.1.0 for local VS Code testing.

## 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Optional: configure Anthropic for AI summaries

The app always generates a deterministic template summary. To use Anthropic for the AI-drafted HPI, set `ANTHROPIC_API_KEY` before starting the API.

macOS / Linux:

```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

Do not commit real keys to GitHub or store them in tracked project files.

## 4. Optional: configure local Ollama fallback

If Anthropic is not configured or fails, the summary engine tries local Ollama before falling back to the template HPI.

```bash
ollama serve
ollama pull llama3.1
export OLLAMA_URL="http://localhost:11434/api/generate"
export OLLAMA_MODEL="llama3.1"
```

## 5. Initialize the SQLite database

```bash
python setup/init_db.py
```

## 6. Start the FastAPI backend

```bash
bash setup/run.sh api
```

Or directly:

```bash
uvicorn app.api.main:app --reload --port 8000
```

## 7. Start the Streamlit UI

Open a second terminal with the virtual environment active:

```bash
bash setup/run.sh ui
```

Or directly:

```bash
streamlit run app/ui/streamlit_app.py
```

## 8. Run smoke tests

```bash
bash setup/run_tests.sh
```

## 9. Summary behavior

The summary path in v1.1.0 is:

1. Deterministic template summary from captured state.
2. Anthropic if `ANTHROPIC_API_KEY` is set.
3. Ollama if Anthropic is unavailable.
4. Template HPI fallback if no AI provider responds.

## 10. Troubleshooting

If the UI cannot connect to the API, confirm FastAPI is running on port 8000.

```bash
export UI_API_BASE_URL="http://localhost:8000"
```

If Anthropic does not run, confirm the key is present in the same terminal session that launched the API.


## v1.1 Question Cap Note

The shared session guardrail is now:

```json
"session_hard_cap_questions": 60
```

Complaint-level max-question caps were increased in v1.1.0 so the app has room to complete complaint questioning while still allowing ROS and module questions. Skip logic and dedup rules still prevent unnecessary repeated questions.


## Windows summary display note

Generated Template Summary and AI HPI outputs are rendered in read-only HTML panels instead of disabled Streamlit text areas. This avoids a Windows/browser issue where `disabled=True` text areas can appear blank even when summary text exists. The doctor-reviewed summary remains editable.
