"""Vibrant Streamlit UI for deterministic clerking with batch ROS."""
from __future__ import annotations

import json
import os
from html import escape
from typing import Any, Dict, List

import requests
import streamlit as st

API_BASE = os.environ.get("UI_API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Clinical Intake", page_icon="⚕️", layout="wide")
st.markdown(
    """
<style>
:root {
  --bg1:#0f172a; --bg2:#1d4ed8; --card:#ffffff; --muted:#64748b; --accent:#7c3aed;
  --good:#059669; --warn:#ea580c; --danger:#dc2626; --soft:#eef2ff;
}
.stApp {
  background:
    radial-gradient(circle at top left, rgba(124,58,237,.22), transparent 28%),
    radial-gradient(circle at top right, rgba(37,99,235,.18), transparent 25%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}
.block-container {padding-top: 1.2rem;}
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #7c3aed 100%);
  color: white; border-radius: 26px; padding: 22px 24px; margin-bottom: 16px;
  box-shadow: 0 22px 45px rgba(29,78,216,.20);
}
.card {
  background: rgba(255,255,255,.95); border:1px solid rgba(148,163,184,.18);
  border-radius: 22px; padding: 18px 18px; box-shadow: 0 10px 32px rgba(15,23,42,.08);
}
.metric-card {
  background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(238,242,255,.98));
  border:1px solid rgba(99,102,241,.18); border-radius: 20px; padding: 14px 16px;
  box-shadow: 0 8px 24px rgba(79,70,229,.08);
}
.metric-k {font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.08em}
.metric-v {font-size:28px;font-weight:800;color:#0f172a;line-height:1.1}
.metric-s {font-size:12px;color:#6366f1;font-weight:600}
.sys-msg{background:linear-gradient(180deg,#ffffff,#eef4ff);color:#0f172a;border:1px solid #dbeafe;border-radius:18px 18px 18px 6px;padding:14px 18px;margin:6px 0;max-width:88%;box-shadow:0 8px 18px rgba(37,99,235,.08)}
.pat-msg{background:linear-gradient(135deg,#7c3aed,#2563eb);color:white;border-radius:18px 18px 6px 18px;padding:12px 16px;margin:6px 0;margin-left:auto;width:fit-content;max-width:88%;box-shadow:0 10px 20px rgba(37,99,235,.18)}
.phase-tag{font-size:11px;color:#334155;text-transform:uppercase;letter-spacing:.12em;font-weight:700;margin-bottom:4px}
.red-flag{background:linear-gradient(180deg,#fff1f2,#ffe4e6);border-left:4px solid #dc2626;border-radius:14px;padding:10px 16px;color:#991b1b;margin:8px 0}
.escalation-chip{display:inline-block;padding:7px 12px;border-radius:999px;font-size:12px;font-weight:700;background:#ede9fe;color:#6d28d9}
.question-shell{background:linear-gradient(180deg,#ffffff,#f8fafc);border:1px solid #dbeafe;border-radius:24px;padding:20px;box-shadow:0 12px 28px rgba(15,23,42,.07)}
.helper{font-size:12px;color:#64748b}
.section-title{font-weight:800;font-size:20px;color:#0f172a;margin-bottom:8px}
.stButton>button, .stDownloadButton>button {
  border-radius: 14px; border: none; padding: .65rem 1rem; font-weight: 700;
  box-shadow: 0 10px 20px rgba(79,70,229,.12);
}
.stButton>button[kind="primary"] {background: linear-gradient(135deg,#7c3aed,#2563eb); color: white;}
.question-prompt{background:linear-gradient(135deg,#eff6ff,#eef2ff 55%,#f5f3ff);border:1px solid #c7d2fe;color:#0f172a;border-radius:18px;padding:14px 16px;font-size:20px;font-weight:800;line-height:1.35;margin:10px 0 14px 0;box-shadow:0 8px 18px rgba(79,70,229,.08)}

/* Remove focus outlines from all inputs */
input:focus, textarea:focus, select:focus,
[data-baseweb="select"]:focus-within,
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus,
.stTextInput > div:focus-within, .stTextArea > div:focus-within {
  outline: none !important;
  box-shadow: none !important;
  border-color: #cbd5e1 !important;
}
*:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Ensure all headings in cards are dark */
.card h1, .card h2, .card h3, .card h4,
.question-shell h1, .question-shell h2, .question-shell h3, .question-shell h4,
.stTextArea label, .stTextInput label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  color: #0f172a !important;
  font-weight: 700 !important;
}

/* Override Streamlit's default JSON viewer background */
.stJson {
  background: #f8fafc !important;
  border-radius: 12px !important;
  padding: 10px !important;
  color: #0f172a !important;
}

/* force readable widget labels and input text */
[data-testid="stMarkdownContainer"], .stMarkdown, .stCaption, label, p, span, div {color: inherit;}
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label, .stMultiSelect label, .stRadio label {color:#0f172a !important; font-weight:700 !important;}
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div, .stNumberInput input, .stMultiSelect [data-baseweb="select"] > div {background:#ffffff !important; color:#0f172a !important; border:1px solid #cbd5e1 !important; border-radius:14px !important;}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {color:#64748b !important; opacity:1 !important;}
.stRadio div[role="radiogroup"] label p, .stRadio div[role="radiogroup"] label span {color:#0f172a !important;}
.question-shell h1, .question-shell h2, .question-shell h3, .question-shell p, .question-shell label, .question-shell .stMarkdown {color:#0f172a !important;}
.sidebar-question-note{font-size:12px;color:#475569;margin-top:8px}

/* --- sidebar contrast (dark panel) --- */
section[data-testid="stSidebar"] {background:#0f172a !important;}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
  color:#f1f5f9 !important;
}
section[data-testid="stSidebar"] label {font-weight:700 !important;}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {color:#cbd5e1 !important;}
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background:#ffffff !important; color:#0f172a !important; border:1px solid #334155 !important;
}
/* Ensure disabled inputs in sidebar keep readable text */
section[data-testid="stSidebar"] input:disabled,
section[data-testid="stSidebar"] textarea:disabled,
section[data-testid="stSidebar"] [data-baseweb="select"] > div[disabled] {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  opacity: 0.8 !important;
  background: #f1f5f9 !important;
}

/* Sidebar multiselect tags and input text */
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
  background-color: #e2e8f0 !important;
  color: #0f172a !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {
  color: #0f172a !important;
}
section[data-testid="stSidebar"] .stMultiSelect input,
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] input,
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextInput input::placeholder {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
}
section[data-testid="stSidebar"] .stMultiSelect input::placeholder,
section[data-testid="stSidebar"] .stTextInput input::placeholder {
  color: #64748b !important;
  -webkit-text-fill-color: #64748b !important;
  opacity: 1 !important;
}
/* Multiselect dropdown options */
section[data-testid="stSidebar"] .stMultiSelect [role="listbox"] li {
  color: #0f172a !important;
  background: #ffffff !important;
}
section[data-testid="stSidebar"] .stMultiSelect [role="listbox"] li:hover {
  background: #eef2ff !important;
}

/* --- tab bar contrast --- */
[data-testid="stTabs"] button[role="tab"] {
  color:#475569 !important; font-weight:700 !important; opacity:1 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color:#1e3a8a !important;
}
[data-testid="stTabs"] button[role="tab"] p {color: inherit !important;}

/* --- stronger heading contrast everywhere --- */
h1, h2, h3, h4, h5, h6, .section-title, .stSubheader, .stHeading {
  color:#0f172a !important;
}

/* --- summary and state panel labels should never fade into light background --- */
.card strong, .card b, .card label, .card p, .card span,
.question-shell strong, .question-shell b, .question-shell label, .question-shell p,
[data-testid="stJson"] *, .stJson * {
  color:#0f172a !important;
}

/* --- remove stray small rectangles in BaseWeb text/select inputs --- */
.stTextInput [data-baseweb="base-input"],
.stTextArea [data-baseweb="base-input"],
.stNumberInput [data-baseweb="base-input"],
.stMultiSelect [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div {
  box-shadow:none !important;
}

.stMultiSelect [data-baseweb="tag"],
.stSelectbox [data-baseweb="tag"] {
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
}

.stMultiSelect [data-baseweb="select"] input,
.stSelectbox [data-baseweb="select"] input {
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
}

/* soften the question answer box border */
.stTextArea textarea, .stTextInput input, .stNumberInput input {
  border:1px solid #cbd5e1 !important;
}

/* --- Sidebar buttons: black text, purple refresh hover, red stop hover --- */
section[data-testid="stSidebar"] .stButton > button {
    color: #000000 !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #f1f5f9 !important;
    border-color: #94a3b8 !important;
    color: #000000 !important;
}
/* New session (primary) keeps its purple gradient */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9, #1e40af) !important;
    color: white !important;
}
/* Stop session (secondary) – red on hover */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #fee2e2 !important;
    border-color: #f87171 !important;
    color: #000000 !important;
}
/* Override for Refresh button specifically: purple on hover */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"][aria-label="Refresh current"]:hover {
    background-color: #ede9fe !important;
    border-color: #a78bfa !important;
    color: #000000 !important;
}

/* cleaner yes/no presentation and stronger contrast */
.stRadio [role="radiogroup"] {
    gap: .75rem !important;
}
.stRadio [role="radiogroup"] label {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 999px !important;
    padding: .35rem .85rem !important;
}
.stRadio [role="radiogroup"] label:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
}
.stRadio [role="radiogroup"] label p,
.stRadio [role="radiogroup"] label span,
.stRadio [role="radiogroup"] div {
    color: #0f172a !important;
    opacity: 1 !important;
}
.hero h1, .hero h2, .hero h3, .hero p, .hero span, .hero strong,
.metric-card h1, .metric-card h2, .metric-card h3, .metric-card p, .metric-card span,
.stAlert p, .stAlert span, .stAlert div {
    color: inherit !important;
    opacity: 1 !important;
}
.status-shell {
    background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(238,242,255,.98));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 20px;
    padding: 14px 16px;
    box-shadow: 0 8px 24px rgba(79,70,229,.08);
}
.status-title {
    color: #0f172a !important;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 6px;
}
.status-caption {
    color: #334155 !important;
    font-size: 13px;
    font-weight: 600;
}
.ros-batch-checkbox {
    margin-bottom: 6px;
}
.ros-question-row {
    background: #ffffff !important;
    border: 1px solid #dbeafe !important;
    border-radius: 16px !important;
    padding: 12px 14px !important;
    margin: 10px 0 !important;
}
.ros-question-text {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    line-height: 1.35 !important;
}
.ros-detail-label {
    color: #000000 !important;
    font-weight: 700 !important;
}

/* --- readable summary textareas, including disabled summary boxes --- */
.stTextArea textarea,
.stTextArea textarea:disabled,
[data-testid="stTextArea"] textarea,
[data-testid="stTextArea"] textarea:disabled {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
  opacity: 1 !important;
  background-color: #ffffff !important;
}
.stTextArea textarea::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
  color: #475569 !important;
  -webkit-text-fill-color: #475569 !important;
  opacity: 1 !important;
}
.stTextArea label,
[data-testid="stTextArea"] label,
[data-testid="stTextArea"] p,
[data-testid="stTextArea"] span {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
  opacity: 1 !important;
}

/* --- stop and refresh controls should keep black font, including hover --- */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover *,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"][aria-label="Refresh current"]:hover,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"][aria-label="Refresh current"]:hover * {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


SUPPORTED_GYNE_SYMPTOMS = ["vaginal discharge", "vaginal bleeding"]
SECONDARY_OPTIONS = [
    "Vaginal discharge",
    "Vaginal bleeding",
    "Pelvic pain",
    "Urinary frequency",
    "Dysuria",
    "Cough",
    "Fever",
    "Headache",
    "Weight loss",
]


def api_get(path: str):
    resp = requests.get(f"{API_BASE}{path}", timeout=45)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, payload: dict):
    resp = requests.post(f"{API_BASE}{path}", json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()


def api_put(path: str, payload: dict):
    resp = requests.put(f"{API_BASE}{path}", json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()


def init_state():
    defaults = {
        "session_id": None,
        "current_question": None,
        "current_batch": None,
        "phase": None,
        "progress": {},
        "complaint_name": "",
        "patient_age": None,
        "patient_sex": "",
        "summary_payload": None,
        "doctor_summary": "",
        "chat_history": [],
        "live_metrics": {},
        "secondary_selected": [],
        "session_closed": False,
        "confirm_finish": False,
        "extracted_state_cache": {},
        "engine_status": "idle",
        "last_error": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def reset_session_state():
    for k in [
        "session_id", "current_question", "current_batch", "phase", "progress", "complaint_name", "patient_age",
        "patient_sex", "summary_payload", "doctor_summary", "chat_history", "live_metrics",
        "secondary_selected", "session_closed", "confirm_finish", "extracted_state_cache",
        "engine_status", "last_error"
    ]:
        if k in st.session_state:
            del st.session_state[k]
    init_state()


def safe_text(value: Any) -> str:
    return escape(str(value or ""))


def render_readonly_text(label: str, value: Any, height: int = 280) -> None:
    """Render generated text reliably without disabled=True text areas.

    Disabled Streamlit text areas can appear blank on some Windows/browser/theme
    combinations. Generated summaries are shown in a read-only HTML panel instead.
    """
    safe_label = escape(str(label or ""))
    safe_value = escape(str(value or ""))
    st.markdown(
        f"""
        <div style="margin-top:0.25rem;margin-bottom:0.35rem;font-weight:700;color:#0f172a;">{safe_label}</div>
        <div style="
            background-color:#ffffff;
            color:#000000;
            border:1px solid #cbd5e1;
            border-radius:14px;
            padding:14px 16px;
            min-height:{int(height)}px;
            max-height:{int(height)}px;
            overflow-y:auto;
            white-space:pre-wrap;
            font-family:Arial, Helvetica, sans-serif;
            font-size:14px;
            line-height:1.45;
            box-shadow:inset 0 0 0 1px rgba(15,23,42,.03);
        ">{safe_value}</div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubble(role: str, message: str, phase: str | None = None):
    klass = "sys-msg" if role == "system" else "pat-msg"
    phase_html = f'<div class="phase-tag">{safe_text(phase)}</div>' if role == "system" and phase else ""
    st.markdown(f'<div class="{klass}">{phase_html}{safe_text(message)}</div>', unsafe_allow_html=True)


def set_engine_status(state: str, error_message: str = "") -> None:
    """Store the current UI status without using image assets."""
    if state not in {"idle", "thinking", "complete", "error"}:
        state = "idle"
    st.session_state.engine_status = state
    if error_message:
        st.session_state.last_error = error_message
    elif state != "error":
        st.session_state.last_error = ""


def get_engine_status() -> str:
    """Resolve the current UI status from the Streamlit session."""
    if st.session_state.get("engine_status") == "error":
        return "error"
    if st.session_state.session_closed or st.session_state.summary_payload:
        return "complete"
    if st.session_state.get("current_question") or st.session_state.get("current_batch"):
        return "idle"
    return "idle"

def get_engine_status_caption() -> str:
    state = get_engine_status()
    if state == "error":
        return st.session_state.get("last_error") or "Something needs attention before we continue."
    if state == "complete":
        return "Summary ready for clinician review."
    if state == "thinking":
        return "Working through the next best clinical question."
    return "Ready to start a new intake session."


def render_status_panel():
    """Render a lightweight text status panel. GIF assets are intentionally not used."""
    state = get_engine_status()
    label = {"idle": "Ready", "thinking": "In progress", "complete": "Complete", "error": "Needs attention"}.get(state, "Ready")
    st.markdown('<div class="status-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="status-title">Clinical intake status: {safe_text(label)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-caption">{safe_text(get_engine_status_caption())}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def sync_session_snapshot():
    if st.session_state.session_id is None:
        return
    try:
        snapshot = api_get(f"/sessions/{st.session_state.session_id}")
    except Exception:
        return
    st.session_state.extracted_state_cache = snapshot.get("state", {}) or {}
    if snapshot.get("progress"):
        st.session_state.progress = snapshot.get("progress", {})
    if snapshot.get("phase"):
        st.session_state.phase = snapshot.get("phase")


def merge_extracted_state(field: str, answer: str, extracted_bonus: Dict[str, Any] | None = None):
    merged = dict(st.session_state.extracted_state_cache or {})
    if field:
        merged[field] = answer
    for k, v in (extracted_bonus or {}).items():
        merged[k] = v
    st.session_state.extracted_state_cache = merged


def render_widget(q: dict):
    rt = q.get("response_type", "SHORT_TEXT")
    key = f"answer_{q['id']}"
    label = q.get("text") or q.get("ui_label") or q["field"]

    if rt == "BOOLEAN_WITH_OPTIONAL_DETAILS":
        try:
            yn = st.radio(label, ["Yes", "No"], horizontal=True, key=f"{key}_bool", index=None)
        except TypeError:
            yn = st.radio(label, ["Yes", "No"], horizontal=True, key=f"{key}_bool")
        details = st.text_input("Add detail if relevant", key=f"{key}_details", placeholder="Only if Yes")
        if yn == "Yes" and details.strip():
            return details.strip()
        if yn == "Yes":
            return "yes"
        if yn == "No":
            return "no"
        return ""
    if rt == "SCALE_0_10":
        return str(st.slider(label, min_value=0, max_value=10, value=5, key=key))
    if rt in ("TEMPORAL_WITH_UNIT_OR_SHORT_TEXT", "TEMPORAL_OR_SHORT_TEXT"):
        col1, col2 = st.columns([1, 1])
        with col1:
            num = st.text_input("Value", key=f"{key}_num")
        with col2:
            unit = st.selectbox("Unit", ["", "minutes", "hours", "days", "weeks", "months", "years"], key=f"{key}_unit")
        free = st.text_input("Or enter free text", key=f"{key}_free")
        if free.strip():
            return free.strip()
        if num.strip() and unit:
            return f"{num.strip()} {unit}"
        return ""
    if rt == "NUMERIC_OR_SHORT_TEXT":
        return st.text_input(label, key=key, placeholder="Numeric value or brief text")
    if rt == "COUNT_OR_SHORT_TEXT":
        return st.text_input(label, key=key, placeholder="Count or brief text")
    if rt == "NARRATIVE_FREE_TEXT":
        return st.text_area(label, key=key, height=120)
    return st.text_input(label, key=key)


def update_live_metrics():
    transcript = st.session_state.chat_history
    patient_turns = sum(1 for item in transcript if item.get("role") == "patient")
    system_turns = sum(1 for item in transcript if item.get("role") == "system")
    red_flags = len(st.session_state.progress.get("red_flags", []) or [])
    st.session_state.live_metrics = {
        "patient_turns": patient_turns,
        "system_turns": system_turns,
        "completion": float(st.session_state.progress.get("completion_percent", 0.0) or 0.0),
        "red_flags": red_flags,
        "phase": st.session_state.phase or "not started",
        "escalation": st.session_state.progress.get("escalation_level", "none"),
    }


def append_system_question(q: Dict[str, Any] | None):
    if not q:
        return
    message = q.get("text") or q.get("ui_label") or q.get("field") or q.get("id")
    last = st.session_state.chat_history[-1] if st.session_state.chat_history else None
    if last and last.get("role") == "system" and last.get("message") == message and last.get("phase") == q.get("phase"):
        return
    st.session_state.chat_history.append({"role": "system", "message": message, "phase": q.get("phase")})


def append_batch_messages(batch: dict):
    """Add each question in the batch as a separate system message for the transcript."""
    for q in batch["questions"]:
        st.session_state.chat_history.append({"role": "system", "message": q["text"], "phase": "ros"})


def load_metrics_from_api():
    if st.session_state.session_id is None:
        return None
    try:
        return api_get(f"/sessions/{st.session_state.session_id}/metrics")
    except Exception:
        return None


def start_session(complaint_id: str, complaint_name: str, age: int, sex: str, secondary_text: str):
    data = api_post("/sessions", {"complaint_id": complaint_id, "patient_age": age, "patient_sex": sex, "secondary_complaint": secondary_text})
    st.session_state.session_id = data["session_id"]
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    st.session_state.complaint_name = complaint_name
    st.session_state.patient_age = age
    st.session_state.patient_sex = sex
    st.session_state.chat_history = []
    st.session_state.session_closed = False
    st.session_state.confirm_finish = False
    set_engine_status("thinking")

    # The API may return a batch (if ROS starts immediately) or a single question.
    # Reset chat history before appending so the first system item is not lost.
    if "next_batch" in data:
        st.session_state.current_batch = data["next_batch"]
        st.session_state.current_question = None
        append_batch_messages(data["next_batch"])
    else:
        st.session_state.current_question = data.get("next_question")
        st.session_state.current_batch = None
        append_system_question(st.session_state.current_question)

    sync_session_snapshot()
    update_live_metrics()


def submit_answer(answer: str):
    set_engine_status("thinking")
    q = st.session_state.current_question
    st.session_state.chat_history.append({"role": "patient", "message": answer, "phase": q.get("phase")})
    data = api_post(
        f"/sessions/{st.session_state.session_id}/answer",
        {"question_id": q["id"], "field": q["field"], "answer": answer, "phase": q["phase"]},
    )
    if "next_batch" in data:
        st.session_state.current_batch = data["next_batch"]
        st.session_state.current_question = None
        append_batch_messages(data["next_batch"])
    else:
        st.session_state.current_question = data.get("next_question")
        st.session_state.current_batch = None
        append_system_question(st.session_state.current_question)
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    if data.get("extracted_state") is not None:
        st.session_state.extracted_state_cache = data.get("extracted_state", {}) or {}
    else:
        merge_extracted_state(q.get("field"), answer, data.get("extracted_bonus", {}))
    update_live_metrics()


def submit_ros_batch(batch: dict, answers: dict, details: dict):
    """Submit a ROS batch to the API."""
    set_engine_status("thinking")
    # Record the batch questions and answers in the chat history for display
    for q in batch["questions"]:
        field = q["field"]
        answer = answers.get(field, "no")
        st.session_state.chat_history.append({"role": "patient", "message": f"{q['text']} → {answer}", "phase": "ros"})
        if details.get(field):
            st.session_state.chat_history.append({"role": "patient", "message": f"Detail: {details[field]}", "phase": "ros"})
    data = api_post(
        f"/sessions/{st.session_state.session_id}/ros_batch",
        {"answers": answers, "details": details}
    )
    if "next_batch" in data:
        st.session_state.current_batch = data["next_batch"]
        st.session_state.current_question = None
        append_batch_messages(data["next_batch"])
    elif "next_question" in data:
        st.session_state.current_question = data["next_question"]
        st.session_state.current_batch = None
        append_system_question(st.session_state.current_question)
    else:
        st.session_state.current_question = None
        st.session_state.current_batch = None
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    if data.get("extracted_state") is not None:
        st.session_state.extracted_state_cache = data.get("extracted_state", {}) or {}
    else:
        for field, answer in answers.items():
            merge_extracted_state(field, answer, {})
        for field, detail in details.items():
            if detail:
                merge_extracted_state(f"{field}_detail", detail, {})
    update_live_metrics()


def skip_current_question():
    set_engine_status("thinking")
    q = st.session_state.current_question
    st.session_state.chat_history.append({"role": "patient", "message": "Skipped / not assessed", "phase": q.get("phase")})
    data = api_post(
        f"/sessions/{st.session_state.session_id}/skip",
        {"question_id": q["id"], "field": q["field"], "answer": "not_assessed", "phase": q["phase"]},
    )
    if "next_batch" in data:
        st.session_state.current_batch = data["next_batch"]
        st.session_state.current_question = None
        append_batch_messages(data["next_batch"])
    else:
        st.session_state.current_question = data.get("next_question")
        st.session_state.current_batch = None
        append_system_question(st.session_state.current_question)
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    merge_extracted_state(q.get("field"), "not_assessed", data.get("extracted_bonus", {}))
    if data.get("extracted_state") is not None:
        st.session_state.extracted_state_cache = data.get("extracted_state", {})
    update_live_metrics()

    return data


def complete_session():
    """Exhaust remaining questions then generate summary."""
    data = api_post(f"/sessions/{st.session_state.session_id}/complete", {})
    if data.get("phase") == "completed":
        st.session_state.summary_payload = data
        st.session_state.current_question = None
        st.session_state.current_batch = None
        st.session_state.session_closed = True
        set_engine_status("complete")
        st.session_state.extracted_state_cache = data.get("extracted_state", {}) or st.session_state.extracted_state_cache
    else:
        if "next_batch" in data:
            st.session_state.current_batch = data["next_batch"]
            st.session_state.current_question = None
            append_batch_messages(data["next_batch"])
        else:
            st.session_state.current_question = data.get("next_question")
            st.session_state.current_batch = None
            append_system_question(st.session_state.current_question)
        st.session_state.phase = data.get("phase")
        st.session_state.progress = data.get("progress", {})
    update_live_metrics()


def force_complete_session():
    """Immediately stop and generate summary without asking remaining questions."""
    data = api_post(f"/sessions/{st.session_state.session_id}/force_complete", {})
    st.session_state.summary_payload = data
    st.session_state.current_question = None
    st.session_state.current_batch = None
    st.session_state.phase = "completed"
    st.session_state.session_closed = True
    sync_session_snapshot()
    update_live_metrics()


def abandon_session():
    """Stop the session without generating summary."""
    if st.session_state.session_id is None:
        return
    try:
        api_post(f"/sessions/{st.session_state.session_id}/abandon", {})
    except Exception:
        pass
    reset_session_state()
    set_engine_status("idle")
    st.rerun()


def save_doctor_summary():
    api_put(f"/sessions/{st.session_state.session_id}/doctor-summary", {"post_summary": st.session_state.doctor_summary})
    st.success("Doctor-edited summary saved.")


def download_transcript() -> bytes:
    lines = []
    for turn in st.session_state.chat_history:
        lines.append(f"[{turn.get('phase','')}] {turn.get('role','').upper()}: {turn.get('message','')}")
    return "\n".join(lines).encode("utf-8")


def compatibility_message(sex: str, primary_display_name: str, secondary_selected: List[str], secondary_text: str) -> str | None:
    combined = ", ".join(([primary_display_name] if primary_display_name else []) + secondary_selected + ([secondary_text] if secondary_text else []))
    lower = combined.lower()
    if sex == "male" and any(term in lower for term in SUPPORTED_GYNE_SYMPTOMS):
        return "Male selected together with a gynecologic symptom (for example vaginal discharge / vaginal bleeding). Please review the sex or symptom selection before starting."
    return None


def render_metrics_row(saved_metrics: Dict[str, Any] | None = None):
    live = st.session_state.live_metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        saved_rate = saved_metrics.get("completion_rate") if saved_metrics else None
        if saved_rate is not None:
            pct_val = f'{(100*float(saved_rate)):.0f}%'
            subtitle = "Saved to database"
        else:
            pct_val = f'{live.get("completion",0):.0f}%'
            subtitle = "Current flow progress"
        st.markdown(f'<div class="metric-card"><div class="metric-k">Completion</div><div class="metric-v">{pct_val}</div><div class="metric-s">{subtitle}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-k">Turns</div><div class="metric-v">{live.get("patient_turns",0)}/{live.get("system_turns",0)}</div><div class="metric-s">Patient / system</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-k">Red flags</div><div class="metric-v">{live.get("red_flags",0)}</div><div class="metric-s">Detected so far</div></div>', unsafe_allow_html=True)
    with col4:
        escalation = live.get("escalation") or "none"
        st.markdown(f'<div class="metric-card"><div class="metric-k">Escalation</div><div class="metric-v">{safe_text(escalation)}</div><div class="metric-s">Live clinical acuity</div></div>', unsafe_allow_html=True)


def render_ros_batch(batch: dict):
    """Render a batch of ROS questions with explicit Yes/No options for each item."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Review of Systems – {batch["system"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="helper">This block asks ROS questions for one body system. Select Yes or No for each question. After you submit this block, the app will automatically show the next relevant system block if more ROS questions remain.</div>', unsafe_allow_html=True)
    
    answers = {}
    details = {}
    
    for q in batch["questions"]:
        q_key = f"ros_{st.session_state.session_id}_{q.get('id', q['field'])}_{q['field']}"
        st.markdown('<div class="ros-question-row">', unsafe_allow_html=True)
        st.markdown(f'<div class="ros-question-text">{escape(str(q["text"]))}</div>', unsafe_allow_html=True)
        yn = st.radio(
            "Answer",
            ["Yes", "No"],
            horizontal=True,
            key=f"{q_key}_yn",
            index=1,
            label_visibility="collapsed",
        )
        checked = yn == "Yes"
        answers[q["field"]] = "yes" if checked else "no"

        if checked and q.get("detail_field"):
            detail = st.text_input(
                "Details",
                key=f"{q_key}_detail",
                placeholder="Add details if known, e.g., 38.5°C, dry cough, started yesterday",
            )
            if detail:
                details[q["field"]] = detail
        if q.get("sensitive_topic"):
            st.caption("🔒 Sensitive topic – your answers are confidential.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="helper">Budget remaining: {batch["budget_remaining"]} questions</div>', unsafe_allow_html=True)
    
    if st.button("Submit this system block", type="primary", use_container_width=True):
        submit_ros_batch(batch, answers, details)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    init_state()
    st.markdown(
        '<div class="hero"><div style="font-size:30px;font-weight:900">⚕️ Clinical Intake</div><div style="opacity:.92;margin-top:6px">Deterministic complaint-led clerking with batch ROS, modules, Ollama summary, doctor review, and database metrics.</div></div>',
        unsafe_allow_html=True,
    )

    try:
        if "complaints_cache" not in st.session_state:
            st.session_state.complaints_cache = api_get("/complaints")
        complaints = st.session_state.complaints_cache
    except Exception:
        st.error(f"API not reachable at {API_BASE}. Start the backend first.")
        st.stop()

    saved_metrics = load_metrics_from_api() if st.session_state.session_id else None
    update_live_metrics()
    render_metrics_row(saved_metrics)
    st.write("")

    tab_intake, tab_transcript, tab_summary, tab_metrics = st.tabs(["Intake", "Transcript", "Summary", "Metrics"])

    with st.sidebar:
        # --- DYNAMIC AVATAR LOGIC ---
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            st.session_state.image_folder = os.path.join(current_dir, "images")
            
            # 1. Create a placeholder that we can inject images into instantly
            avatar_placeholder = st.empty()
            st.session_state.avatar_placeholder = avatar_placeholder
            
            # 2. Get current state and display default image
            current_state = get_engine_status()
            avatar_files = {
                "idle": "idle.gif",
                "thinking": "thinking.gif",
                "complete": "complete.gif",
                "error": "error.gif"
            }
            current_avatar = avatar_files.get(current_state, "idle.gif")
            image_path = os.path.join(st.session_state.image_folder, current_avatar)
            
            # 3. Draw it inside the placeholder
            avatar_placeholder.image(image_path, use_container_width=True)
        except Exception:
            st.warning("Could not load avatar file")
        st.write("") 
        # -----------------------------

        st.markdown('<div class="section-title">Session controls</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New session", use_container_width=True, type="primary"):
                reset_session_state()
                st.rerun()
        with col2:
            if st.session_state.session_id is not None and st.button("⏹️ Stop session", use_container_width=True):
                abandon_session()
                st.rerun()

        if st.session_state.session_id is not None and not st.session_state.session_closed and st.button("🔄 Refresh current", use_container_width=True):
            data = api_get(f"/sessions/{st.session_state.session_id}/current")
            current = data.get("current")
            if current:
                if isinstance(current, dict) and current.get("type") == "ros_batch":
                    st.session_state.current_batch = current
                    st.session_state.current_question = None
                else:
                    st.session_state.current_question = current
                    st.session_state.current_batch = None
                st.session_state.progress = data.get("progress", {})
                st.session_state.phase = data.get("phase")
                sync_session_snapshot()
                update_live_metrics()
            else:
                st.warning("No current question or batch available.")
            st.rerun()

        render_status_panel()

        st.markdown('<div class="card" style="margin-top:10px">', unsafe_allow_html=True)
        st.markdown("**New session setup**")
        complaint_map = {c["display_name"]: c["complaint_id"] for c in complaints}
        display_names = list(complaint_map.keys())
        display_name = st.selectbox("Primary complaint", display_names, index=display_names.index(st.session_state.complaint_name) if st.session_state.complaint_name in display_names else 0, disabled=st.session_state.session_id is not None)
        age = st.number_input("Patient age", min_value=0, max_value=120, value=int(st.session_state.patient_age or 35), disabled=st.session_state.session_id is not None)
        sex = st.selectbox("Patient sex", ["female", "male", "other"], index=["female", "male", "other"].index(st.session_state.patient_sex) if st.session_state.patient_sex in ["female","male","other"] else 0, disabled=st.session_state.session_id is not None)
        secondary_selected = st.multiselect("Quick secondary concerns", SECONDARY_OPTIONS, default=st.session_state.secondary_selected, disabled=st.session_state.session_id is not None)
        st.session_state.secondary_selected = secondary_selected
        secondary_free = st.text_input("Other concerns / secondary complaint", disabled=st.session_state.session_id is not None)
        guard = compatibility_message(sex, display_name, secondary_selected, secondary_free)
        if guard:
            st.error(guard)
        if sex == "female":
            st.caption("Female selection allows gynecologic review items such as vaginal discharge or vaginal bleeding when relevant.")
        elif sex == "male":
            st.caption("If a gynecologic symptom was intended, review the sex selection before starting.")

        secondary_text = ", ".join([x for x in secondary_selected if x] + ([secondary_free.strip()] if secondary_free.strip() else []))
        if st.session_state.session_id is None and st.button("▶ Start intake", use_container_width=True, type="primary", disabled=bool(guard)):
            try:
                start_session(complaint_map[display_name], display_name, int(age), sex, secondary_text)
                st.rerun()
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                set_engine_status("error", f"Could not start session: {detail}")
                st.error(f"Could not start session: {detail}")
            except Exception as exc:
                set_engine_status("error", f"Could not start session: {exc}")
                st.error(f"Could not start session: {exc}")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.session_id is not None:
            st.markdown('<div class="card" style="margin-top:12px">', unsafe_allow_html=True)
            st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
            st.markdown(f"**Complaint:** {safe_text(st.session_state.complaint_name)}")
            st.markdown(f"**Phase:** {safe_text(st.session_state.phase)}")
            if st.session_state.session_closed:
                st.success("Session ended. Summary is ready for review.")
            esc = st.session_state.progress.get("escalation_level", "none")
            if esc != "none":
                st.markdown(f'<span class="escalation-chip">Escalation: {safe_text(esc)}</span>', unsafe_allow_html=True)
            prog = st.session_state.progress.get("completion_percent", 0.0)
            st.progress(min(max(prog / 100.0, 0.0), 1.0), text=f"{prog:.1f}% through complaint flow")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_intake:
        if st.session_state.session_id is None:
            st.info("Configure the patient and start a session from the sidebar.")
        else:
            left, right = st.columns([1.25, 0.9])
            with left:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Conversation</div>', unsafe_allow_html=True)
                
                # 1. Added a fixed-height container to create a scrollable box
                # 2. Removed the [-15:] limit so the entire chat history is preserved
                with st.container(height=600, border=False):
                    if not st.session_state.chat_history:
                        st.caption("The live conversation will appear here.")
                    else:
                        for item in st.session_state.chat_history:
                            render_chat_bubble(item["role"], item["message"], item.get("phase"))
                            
                st.markdown('</div>', unsafe_allow_html=True)
            with right:
                if st.session_state.progress.get("red_flags"):
                    for flag in st.session_state.progress.get("red_flags", []):
                        st.markdown(f'<div class="red-flag">{safe_text(flag.get("pattern", "red flag")).replace("_", " ")}</div>', unsafe_allow_html=True)
                
                # Handle current state based on phase and presence of batch
                if st.session_state.phase == "ros" and st.session_state.current_batch:
                    render_ros_batch(st.session_state.current_batch)
                elif st.session_state.phase == "complaint" and st.session_state.current_question:
                    q = st.session_state.current_question
                    
                    # Wrap the question and Submit button in an st.form so Enter works
                    with st.form(key=f"form_complaint_{q.get('id', 'default')}", clear_on_submit=False, border=False):
                        st.markdown('<div class="question-shell">', unsafe_allow_html=True)
                        st.markdown(f'<div class="phase-tag">{safe_text(q.get("phase"))}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="question-prompt">{safe_text(q.get("text") or q.get("ui_label") or q.get("field"))}</div>', unsafe_allow_html=True)
                        st.markdown(f'**Field:** {safe_text(q.get("ui_label") or q.get("field"))}')
                        if q.get("sensitive_topic"):
                            st.caption("🔒 Sensitive topic")
                        
                        answer = render_widget(q)
                        
                        st.markdown('<div class="sidebar-question-note">Question text is shown above in high contrast for readability.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        submitted = st.form_submit_button("Submit answer", use_container_width=True, type="primary")
                        if submitted:
                            if not str(answer).strip():
                                st.warning("Enter an answer before continuing.")
                            else:
                                # 1. Instantly inject the thinking GIF into the sidebar placeholder!
                                thinking_path = os.path.join(st.session_state.image_folder, "thinking.gif")
                                st.session_state.avatar_placeholder.image(thinking_path, use_container_width=True)
                                
                                # 2. Safely talk to the database
                                submit_answer(str(answer).strip())
                                
                                # 3. Redraw the screen (which naturally reverts to idle)
                                st.rerun()

                    # Keep Skip and Finish OUTSIDE the form
                    if st.session_state.confirm_finish:
                        st.warning("Are you sure you want to end the session now and generate a summary with the information provided so far?")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("✅ Yes, finish now", use_container_width=True, type="primary"):
                                force_complete_session()
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", use_container_width=True):
                                st.session_state.confirm_finish = False
                                st.rerun()
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Skip question", use_container_width=True):
                                skip_current_question()
                                st.rerun()
                        with c2:
                            if st.button("Finish & summarize", use_container_width=True):
                                st.session_state.confirm_finish = True
                                st.rerun()
                elif st.session_state.phase == "modules" and st.session_state.current_question:
                    st.info("General history modules are now running: PMH/PSH, medications/allergies, social/family history, and conditional history where relevant.")
                    q = st.session_state.current_question
                    
                    # Wrap in form
                    with st.form(key=f"form_modules_{q.get('id', 'default')}", clear_on_submit=False, border=False):
                        st.markdown('<div class="question-shell">', unsafe_allow_html=True)
                        st.markdown(f'<div class="phase-tag">{safe_text(q.get("phase"))}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="question-prompt">{safe_text(q.get("text") or q.get("ui_label") or q.get("field"))}</div>', unsafe_allow_html=True)
                        st.markdown(f'**Field:** {safe_text(q.get("ui_label") or q.get("field"))}')
                        if q.get("sensitive_topic"):
                            st.caption("🔒 Sensitive topic")
                        
                        answer = render_widget(q)
                        st.markdown('</div>', unsafe_allow_html=True)

                        submitted = st.form_submit_button("Submit answer", use_container_width=True, type="primary")
                        if submitted:
                            if not str(answer).strip():
                                st.warning("Enter an answer before continuing.")
                            else:
                                # 1. Instantly inject the thinking GIF into the sidebar placeholder!
                                thinking_path = os.path.join(st.session_state.image_folder, "thinking.gif")
                                st.session_state.avatar_placeholder.image(thinking_path, use_container_width=True)
                                
                                # 2. Safely talk to the database
                                submit_answer(str(answer).strip())
                                
                                # 3. Redraw the screen (which naturally reverts to idle)
                                st.rerun()

                    # Keep Skip and Finish OUTSIDE the form
                    if st.session_state.confirm_finish:
                        st.warning("Are you sure you want to end the session now and generate a summary?")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("✅ Yes, finish now", use_container_width=True, type="primary"):
                                force_complete_session()
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", use_container_width=True):
                                st.session_state.confirm_finish = False
                                st.rerun()
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Skip question", use_container_width=True):
                                skip_current_question()
                                st.rerun()
                        with c2:
                            if st.button("Finish & summarize", use_container_width=True):
                                st.session_state.confirm_finish = True
                                st.rerun()
                elif st.session_state.summary_payload or st.session_state.session_closed:
                    st.markdown('<div class="question-shell"><div class="section-title">Session completed</div><div class="helper">The chat has ended and the summaries are ready in the Summary tab.</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="question-shell"><div class="section-title">Ready to summarize</div><div class="helper">The complaint flow, ROS, and modules are exhausted. Generate the summaries and review the calculated metrics.</div></div>', unsafe_allow_html=True)
                    if st.button("🧠 Generate summaries", use_container_width=True, type="primary"):
                        complete_session()
                        st.rerun()

                st.write("")
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Current extracted state</div>', unsafe_allow_html=True)
                if st.session_state.summary_payload and st.session_state.summary_payload.get("extracted_state") is not None:
                    extracted_state = st.session_state.summary_payload.get("extracted_state", {})
                else:
                    extracted_state = st.session_state.get("extracted_state_cache", {})
                safe_state = escape(json.dumps(extracted_state or {}, indent=2, ensure_ascii=False))
                st.markdown(
                    f"""
                    <div style="
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #cbd5e1;
                        border-radius: 14px;
                        padding: 14px 16px;
                        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                        font-size: 14px;
                        line-height: 1.45;
                        white-space: pre-wrap;
                        overflow-x: auto;
                        box-shadow: inset 0 0 0 1px rgba(15,23,42,.03);
                    ">{safe_state}</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_transcript:
        if st.session_state.session_id is None:
            st.info("No transcript yet.")
        else:
            st.markdown('<div class="card"><div class="section-title">Transcript</div></div>', unsafe_allow_html=True)
            for item in st.session_state.chat_history:
                render_chat_bubble(item["role"], item["message"], item.get("phase"))
            st.download_button("Download transcript", data=download_transcript(), file_name=f"transcript_{st.session_state.session_id}.txt", use_container_width=False)

    with tab_summary:
        if not st.session_state.summary_payload:
            st.info("Complete the session to generate the template summary and Ollama summary.")
        else:
            payload = st.session_state.summary_payload
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Template summary</div>', unsafe_allow_html=True)
                render_readonly_text("Structured summary", payload.get("pre_summary", ""), height=480)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Ollama summary</div>', unsafe_allow_html=True)
                render_readonly_text("AI HPI", payload.get("ai_summary", ""), height=180)
                st.markdown('<div class="section-title" style="margin-top:10px;">Doctor edit</div>', unsafe_allow_html=True)
                default_summary = payload.get("ai_summary") or payload.get("pre_summary", "")
                if not st.session_state.doctor_summary:
                    st.session_state.doctor_summary = default_summary
                st.text_area("Final doctor-reviewed summary", key="doctor_summary", height=240)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save doctor summary", use_container_width=True, type="primary"):
                        save_doctor_summary()
                with c2:
                    st.download_button("Download transcript", data=download_transcript(), file_name=f"transcript_{st.session_state.session_id}.txt", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_metrics:
        if st.session_state.session_id is None:
            st.info("Start a session to see metrics.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Metric calculators</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="helper" style="color:#0f172a !important; margin-bottom:12px;">'
                'Live metrics are calculated from the active conversation state. Saved metrics are written to SQLite when the session is completed.'
                '</div>',
                unsafe_allow_html=True,
            )
            metrics_payload = {"live_metrics": st.session_state.live_metrics, "saved_metrics": saved_metrics or {}}
            safe_metrics = escape(json.dumps(metrics_payload, indent=2, ensure_ascii=False))
            st.markdown(
                f"""
                <div style="
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cbd5e1;
                    border-radius: 14px;
                    padding: 14px 16px;
                    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                    font-size: 14px;
                    line-height: 1.45;
                    white-space: pre-wrap;
                    overflow-x: auto;
                    box-shadow: inset 0 0 0 1px rgba(15,23,42,.03);
                ">{safe_metrics}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
