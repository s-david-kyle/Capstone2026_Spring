# Clinical Intake Runtime — v1.1.0

This package contains the deterministic clinical intake runtime, FastAPI backend, Streamlit UI, SQLite persistence layer, ROS batch runner, shared escalation-rule engine, and template/AI summary pipeline.

## Key features

- JSON-driven complaint workflows.
- Shared canonical question/code registry.
- ROS-owned dedup families to prevent repeated symptom review.
- Secondary-complaint dedup using field/code first and parent-family suppression.
- Shared condition-based escalation rules evaluated from accumulated session state.
- Batch ROS review by body system.
- Deterministic template summary plus optional Anthropic or Ollama AI summary.
- SQLite database with encounters, turns, summaries, metrics, and schema versioning.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup/init_db.py
bash setup/run.sh api
bash setup/run.sh ui
```

See `SETUP.md` for Anthropic and Ollama configuration.

## Documentation

- `SETUP.md` — local setup, Anthropic key, Ollama fallback, and run commands.
- `ARCHITECTURE.md` — system design and runtime flow.
- `TESTING.md` — manual and smoke-test workflow.
- `docs/DOCS_INDEX.md` — documentation index.
- `docs/DB_Codebook_Summarizer_template_v1.1.0.docx` — database codebook and summary template.
- `docs/questions_by_symptom_current.md` / `.csv` — current question inventory by symptom.
- `docs/questions_summary_current.csv` — symptom question counts.

## Version

Current package version: **v1.1.0**.