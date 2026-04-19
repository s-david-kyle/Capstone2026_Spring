# Running the Clinical Intake System (intake_llm_v3)

## Prerequisites

- Python 3.10+
- An `api_keys.py` file in the `intake_llm_v3/` root (ask a teammate — do not commit this file)

## First-time setup

Open a terminal and navigate to the `intake_llm_v3` folder:

```bash
cd intake_llm_v3
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize the database (only needed once):

```bash
python init_db.py
```

---

## Running the app

You need **two terminals** running at the same time.

### Terminal 1 — FastAPI backend

```bash
cd intake_llm_v3
uvicorn app.api.main:app --reload --port 8000
```

You should see:
```
Application startup complete.
```

Leave this running.

### Terminal 2 — Streamlit frontend

```bash
cd intake_llm_v3
streamlit run app/ui/streamlit_app.py --server.port 8502
```

Then open your browser to:

```
http://localhost:8502
```

---

## Stopping the app

- In Terminal 1: `Ctrl+C`
- In Terminal 2: `Ctrl+C`

---

## Troubleshooting

**"No module named 'fastapi'"** — run `pip install -r requirements.txt`

**"Cannot reach API at localhost:8000"** — the backend isn't running. Start Terminal 1 first.

**"Port 8502 is not available"** — try `--server.port 8503` or any other free port.

**"cannot import name from secrets"** — you have a leftover `secrets.py` file. Delete it and make sure `api_keys.py` is in the `intake_llm_v3/` root.
