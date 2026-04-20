"""Vibrant Streamlit UI for deterministic clerking."""
from __future__ import annotations

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
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def reset_session_state():
    for k in [
        "session_id", "current_question", "phase", "progress", "complaint_name", "patient_age",
        "patient_sex", "summary_payload", "doctor_summary", "chat_history", "live_metrics",
        "secondary_selected", "session_closed", "confirm_finish"
    ]:
        if k in st.session_state:
            del st.session_state[k]
    init_state()


def safe_text(value: Any) -> str:
    return escape(str(value or ""))


def render_chat_bubble(role: str, message: str, phase: str | None = None):
    klass = "sys-msg" if role == "system" else "pat-msg"
    phase_html = f'<div class="phase-tag">{safe_text(phase)}</div>' if role == "system" and phase else ""
    st.markdown(f'<div class="{klass}">{phase_html}{safe_text(message)}</div>', unsafe_allow_html=True)


def render_widget(q: dict):
    rt = q.get("response_type", "SHORT_TEXT")
    key = f"answer_{q['id']}"
    label = q.get("text") or q.get("ui_label") or q["field"]

    if rt == "BOOLEAN_WITH_OPTIONAL_DETAILS":
        yn = st.radio(label, ["", "Yes", "No"], horizontal=True, key=f"{key}_bool")
        details = st.text_input("Add detail if relevant", key=f"{key}_details")
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
    st.session_state.current_question = data.get("next_question")
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    st.session_state.complaint_name = complaint_name
    st.session_state.patient_age = age
    st.session_state.patient_sex = sex
    st.session_state.chat_history = []
    st.session_state.session_closed = False
    st.session_state.confirm_finish = False
    append_system_question(st.session_state.current_question)
    update_live_metrics()


def submit_answer(answer: str):
    q = st.session_state.current_question
    st.session_state.chat_history.append({"role": "patient", "message": answer, "phase": q.get("phase")})
    data = api_post(
        f"/sessions/{st.session_state.session_id}/answer",
        {"question_id": q["id"], "field": q["field"], "answer": answer, "phase": q["phase"]},
    )
    st.session_state.current_question = data.get("next_question")
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    append_system_question(st.session_state.current_question)
    update_live_metrics()


def skip_current_question():
    q = st.session_state.current_question
    st.session_state.chat_history.append({"role": "patient", "message": "Skipped / not assessed", "phase": q.get("phase")})
    data = api_post(
        f"/sessions/{st.session_state.session_id}/skip",
        {"question_id": q["id"], "field": q["field"], "answer": "not_assessed", "phase": q["phase"]},
    )
    st.session_state.current_question = data.get("next_question")
    st.session_state.progress = data.get("progress", {})
    st.session_state.phase = data.get("phase")
    append_system_question(st.session_state.current_question)
    update_live_metrics()


def complete_session():
    """Exhaust remaining questions then generate summary."""
    data = api_post(f"/sessions/{st.session_state.session_id}/complete", {})
    if data.get("phase") == "completed":
        st.session_state.summary_payload = data
        st.session_state.current_question = None
        st.session_state.session_closed = True
    else:
        st.session_state.current_question = data.get("next_question")
        st.session_state.phase = data.get("phase")
        st.session_state.progress = data.get("progress", {})
        append_system_question(st.session_state.current_question)
    update_live_metrics()


def force_complete_session():
    """Immediately stop and generate summary without asking remaining questions."""
    data = api_post(f"/sessions/{st.session_state.session_id}/force_complete", {})
    st.session_state.summary_payload = data
    st.session_state.current_question = None
    st.session_state.phase = "completed"
    st.session_state.session_closed = True
    st.session_state.confirm_finish = False
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


def main():
    init_state()
    st.markdown(
        '<div class="hero"><div style="font-size:30px;font-weight:900">⚕️ Clinical Intake</div><div style="opacity:.92;margin-top:6px">Deterministic complaint-led clerking with ROS, modules, Ollama summary, doctor review, and database metrics.</div></div>',
        unsafe_allow_html=True,
    )

    try:
        complaints = api_get("/complaints")
    except Exception:
        st.error(f"API not reachable at {API_BASE}. Start the backend first.")
        st.stop()

    saved_metrics = load_metrics_from_api() if st.session_state.session_id else None
    update_live_metrics()
    render_metrics_row(saved_metrics)
    st.write("")

    tab_intake, tab_transcript, tab_summary, tab_metrics = st.tabs(["Intake", "Transcript", "Summary", "Metrics"])

    with st.sidebar:
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

        if st.session_state.session_id is not None and not st.session_state.session_closed and st.button("🔄 Refresh current question", use_container_width=True):
            data = api_get(f"/sessions/{st.session_state.session_id}/next")
            st.session_state.current_question = data.get("next_question")
            st.session_state.progress = data.get("progress", {})
            st.session_state.phase = data.get("phase")
            append_system_question(st.session_state.current_question)
            update_live_metrics()
            st.rerun()

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
                st.error(f"Could not start session: {detail}")
            except Exception as exc:
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
                if not st.session_state.chat_history:
                    st.caption("The live conversation will appear here.")
                else:
                    for item in st.session_state.chat_history[-10:]:
                        render_chat_bubble(item["role"], item["message"], item.get("phase"))
                st.markdown('</div>', unsafe_allow_html=True)
            with right:
                if st.session_state.progress.get("red_flags"):
                    for flag in st.session_state.progress.get("red_flags", []):
                        st.markdown(f'<div class="red-flag">{safe_text(flag.get("pattern", "red flag")).replace("_", " ")}</div>', unsafe_allow_html=True)
                q = st.session_state.current_question
                if q is None:
                    if st.session_state.summary_payload or st.session_state.session_closed:
                        st.markdown('<div class="question-shell"><div class="section-title">Session completed</div><div class="helper">The chat has ended and the summaries are ready in the Summary tab.</div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="question-shell"><div class="section-title">Ready to summarize</div><div class="helper">The complaint flow, ROS, and modules are exhausted. Generate the summaries and review the calculated metrics.</div></div>', unsafe_allow_html=True)
                        if st.button("🧠 Generate summaries", use_container_width=True, type="primary"):
                            complete_session()
                            st.rerun()
                else:
                    st.markdown('<div class="question-shell">', unsafe_allow_html=True)
                    st.markdown(f'<div class="phase-tag">{safe_text(q.get("phase"))}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="question-prompt">{safe_text(q.get("text") or q.get("ui_label") or q.get("field"))}</div>', unsafe_allow_html=True)
                    st.markdown(f'**Field:** {safe_text(q.get("ui_label") or q.get("field"))}')
                    if q.get("sensitive_topic"):
                        st.caption("Sensitive topic")
                    answer = render_widget(q)
                    st.markdown('<div class="sidebar-question-note">Question text is shown above in high contrast for readability.</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Confirmation logic for "Finish & summarize"
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
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("Submit answer", use_container_width=True, type="primary"):
                                if not str(answer).strip():
                                    st.warning("Enter an answer before continuing.")
                                else:
                                    submit_answer(str(answer).strip())
                                    st.rerun()
                        with c2:
                            if st.button("Skip question", use_container_width=True):
                                skip_current_question()
                                st.rerun()
                        with c3:
                            if st.button("Finish & summarize", use_container_width=True):
                                st.session_state.confirm_finish = True
                                st.rerun()

                st.write("")
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Current extracted state</div>', unsafe_allow_html=True)
                extracted_state = {}
                if st.session_state.summary_payload and st.session_state.summary_payload.get("extracted_state") is not None:
                    extracted_state = st.session_state.summary_payload.get("extracted_state", {})
                elif not st.session_state.session_closed:
                    session = api_get(f"/sessions/{st.session_state.session_id}")
                    extracted_state = session.get("state", {})
                st.json(extracted_state, expanded=False)
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
                st.text_area("Structured summary", payload.get("pre_summary", ""), height=480, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Ollama summary</div>', unsafe_allow_html=True)
                st.text_area("AI HPI", payload.get("ai_summary", ""), height=180, disabled=True)
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
            st.write("Live metrics are calculated from the active conversation state. Saved metrics are written to SQLite when the session is completed.")
            st.json({"live_metrics": st.session_state.live_metrics, "saved_metrics": saved_metrics or {}}, expanded=True)
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()