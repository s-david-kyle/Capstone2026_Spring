"""DDx — Probabilistic Differential Diagnosis viewer for clinicians."""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

# ── path setup so imports work whether run directly or via multipage ──────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from api_keys import ANTHROPIC_API_KEY
except ImportError:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

DB_PATH = os.environ.get(
    "DB_PATH", os.path.join(_PROJECT_ROOT, "data", "clinical_intake.db")
)

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DDx — Clinical Decision Support",
    page_icon="🩺",
    layout="wide",
)

# ── shared CSS (mirrors streamlit_app.py palette exactly) ─────────────────────
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
  color: white; border-radius: 26px; padding: 22px 28px; margin-bottom: 20px;
  box-shadow: 0 22px 45px rgba(29,78,216,.20);
}
.hero h1 {font-size:26px; font-weight:900; margin:0 0 4px 0; letter-spacing:-.02em;}
.hero p  {font-size:13px; opacity:.75; margin:0;}
.card {
  background: rgba(255,255,255,.95); border:1px solid rgba(148,163,184,.18);
  border-radius: 22px; padding: 20px 22px; margin-bottom: 16px;
  box-shadow: 0 10px 32px rgba(15,23,42,.08);
}
/* ── DDx rank card ── */
.ddx-card {
  background: rgba(255,255,255,.97);
  border: 1px solid rgba(148,163,184,.2);
  border-radius: 20px;
  padding: 18px 22px;
  margin-bottom: 14px;
  box-shadow: 0 8px 24px rgba(15,23,42,.07);
  position: relative;
  overflow: hidden;
}
.ddx-card::before {
  content: '';
  position: absolute; top:0; left:0; width:5px; height:100%;
  border-radius: 20px 0 0 20px;
}
.ddx-rank-1::before { background: linear-gradient(180deg,#7c3aed,#2563eb); }
.ddx-rank-2::before { background: linear-gradient(180deg,#0284c7,#0891b2); }
.ddx-rank-3::before { background: linear-gradient(180deg,#0d9488,#059669); }
.ddx-rank-4::before { background: linear-gradient(180deg,#ca8a04,#d97706); }
.ddx-rank-5::before { background: linear-gradient(180deg,#9ca3af,#6b7280); }
.ddx-header {display:flex; align-items:baseline; gap:12px; margin-bottom:10px; flex-wrap:wrap;}
.ddx-rank  {font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.1em; color:#64748b;}
.ddx-name  {font-size:20px; font-weight:900; color:#0f172a; flex:1;}
.ddx-pct   {font-size:28px; font-weight:900; color:#1d4ed8;}
.bar-wrap  {background:#e2e8f0; border-radius:99px; height:8px; margin-bottom:14px;}
.bar-fill  {height:8px; border-radius:99px; transition:width .6s ease;}
.ddx-grid  {display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:2px;}
.ddx-col-head {
  font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.1em;
  margin-bottom:6px; padding-bottom:4px; border-bottom:2px solid;
}
.col-for   {color:#059669; border-color:#059669;}
.col-against {color:#dc2626; border-color:#dc2626;}
.evidence-item {
  display:flex; align-items:flex-start; gap:8px;
  font-size:13px; color:#1e293b; margin-bottom:5px; line-height:1.4;
}
.ev-dot {width:7px; height:7px; border-radius:50%; flex-shrink:0; margin-top:5px;}
.ev-dot-for     {background:#059669;}
.ev-dot-against {background:#dc2626;}
.icd-chip {
  display:inline-block; background:#ede9fe; color:#6d28d9;
  font-size:11px; font-weight:700; border-radius:8px;
  padding:2px 8px; margin-top:8px; font-family: monospace;
}
.urgency-immediate {
  display:inline-block; background:#fee2e2; color:#991b1b;
  font-size:11px; font-weight:800; border-radius:8px; padding:3px 10px; margin-left:8px;
}
.urgency-urgent {
  display:inline-block; background:#fff7ed; color:#9a3412;
  font-size:11px; font-weight:800; border-radius:8px; padding:3px 10px; margin-left:8px;
}
.urgency-routine {
  display:inline-block; background:#f0fdf4; color:#166534;
  font-size:11px; font-weight:800; border-radius:8px; padding:3px 10px; margin-left:8px;
}
.caveats-box {
  background:linear-gradient(135deg,#fffbeb,#fef3c7);
  border:1px solid #fde68a; border-radius:14px;
  padding:14px 18px; margin-top:20px; font-size:13px; color:#78350f;
}
/* sidebar */
section[data-testid="stSidebar"] {background:#0f172a !important;}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
  color:#f1f5f9 !important;
}
section[data-testid="stSidebar"] label {font-weight:700 !important;}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {color:#cbd5e1 !important;}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background:#ffffff !important; color:#0f172a !important; border:1px solid #334155 !important;
}
section[data-testid="stSidebar"] .stSelectbox label {color:#f1f5f9 !important;}
.stButton>button {
  border-radius:14px; border:none; padding:.65rem 1rem;
  font-weight:700; box-shadow:0 10px 20px rgba(79,70,229,.12);
}
.stButton>button[kind="primary"] {
  background:linear-gradient(135deg,#7c3aed,#2563eb); color:white;
}
.meta-row {display:flex; gap:12px; flex-wrap:wrap; margin-bottom:14px;}
.meta-chip {
  background:#f1f5f9; border:1px solid #e2e8f0; border-radius:10px;
  padding:4px 12px; font-size:12px; font-weight:700; color:#334155;
}
.escalation-immediate {background:#fee2e2 !important; color:#991b1b !important; border-color:#fca5a5 !important;}
.escalation-urgent    {background:#fff7ed !important; color:#9a3412 !important; border-color:#fdba74 !important;}
</style>
""",
    unsafe_allow_html=True,
)

# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_completed_encounters() -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.session_name, e.primary_complaint, e.patient_age,
                   e.patient_sex, e.escalation_level, e.created_at,
                   e.pertinent_positive, e.pertinent_negative, e.extracted_state,
                   e.secondary_complaint,
                   s.ai_summary, s.pre_summary
            FROM encounters e
            LEFT JOIN summaries s ON e.id = s.session_id
            WHERE e.status = 'force_completed'
            ORDER BY e.created_at DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


# ── Anthropic call ────────────────────────────────────────────────────────────

DDX_SYSTEM = """You are a senior clinical decision-support system assisting emergency and general medicine physicians.
You receive structured intake data from a patient encounter and return a probabilistic differential diagnosis.

Return ONLY a JSON object — no markdown fences, no preamble — with this exact schema:

{
  "diagnoses": [
    {
      "rank": 1,
      "name": "Bacterial Meningitis",
      "icd10": "G00.9",
      "probability_pct": 52,
      "urgency": "immediate",
      "for": [
        "Nuchal rigidity with Kernig/Brudzinski signs",
        "Fever 38.9 °C with photophobia",
        "Worst headache of life — thunderclap-type onset"
      ],
      "against": [
        "No focal neurological deficit",
        "Onset subacute over 2 weeks rather than fulminant"
      ],
      "next_steps": "LP after NCCT head; empiric ceftriaxone + dexamethasone before imaging if haemodynamically unstable"
    }
  ],
  "clinical_caveat": "One-sentence note about uncertainty or data gaps that limits confidence."
}

Rules:
- Return 3–5 ranked diagnoses. Probabilities must sum to ≤ 100.
- urgency values: "immediate" | "urgent" | "routine"
- "for" and "against" use clinical shorthand appropriate for attending-level physicians (eponyms, abbreviations, Latin OK).
- "next_steps" is one concise action sentence.
- Keep ICD-10 codes accurate.
- Do NOT add any text outside the JSON object.
"""


def build_ddx_prompt(enc: Dict[str, Any]) -> str:
    complaint = enc.get("primary_complaint", "unknown").replace("_", " ")
    age = enc.get("patient_age", "unknown")
    sex = enc.get("patient_sex", "unknown")
    escalation = enc.get("escalation_level", "none")

    try:
        pp = json.loads(enc.get("pertinent_positive") or "[]")
    except Exception:
        pp = []
    try:
        pn = json.loads(enc.get("pertinent_negative") or "[]")
    except Exception:
        pn = []
    try:
        state = json.loads(enc.get("extracted_state") or "{}")
    except Exception:
        state = {}
    try:
        secondary = json.loads(enc.get("secondary_complaint") or "[]")
    except Exception:
        secondary = []

    # Build a compact state excluding internal bookkeeping keys
    skip = {"_captured_fields", "_captured_question_codes"}
    compact = {k: v for k, v in state.items() if k not in skip and v not in (None, "", "not_assessed")}

    lines = [
        f"Patient: {age} year-old {sex}",
        f"Primary complaint: {complaint}",
    ]
    if secondary:
        lines.append(f"Secondary complaints: {', '.join(str(s) for s in secondary)}")
    if escalation and escalation != "none":
        lines.append(f"Triage escalation flag: {escalation.replace('_', ' ').upper()}")
    lines.append("")
    if pp:
        lines.append("Pertinent positives:")
        for item in pp:
            lines.append(f"  + {item}")
    if pn:
        lines.append("Pertinent negatives:")
        for item in pn:
            lines.append(f"  − {item}")
    if compact:
        lines.append("\nCaptured clinical state (key fields):")
        for k, v in compact.items():
            lines.append(f"  {k.replace('_', ' ')}: {v}")

    ai_sum = enc.get("ai_summary") or enc.get("pre_summary")
    if ai_sum:
        lines.append(f"\nNarrative summary:\n{ai_sum[:800]}")

    lines.append("\nGenerate a ranked probabilistic differential diagnosis as specified.")
    return "\n".join(lines)


def get_ddx(enc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    prompt = build_ddx_prompt(enc)
    key = ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("No Anthropic API key found. Check api_keys.py or ANTHROPIC_API_KEY env var.")
        return None
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-opus-4-5",
                "max_tokens": 2048,
                "system": DDX_SYSTEM,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        raw = next((b["text"] for b in content if b.get("type") == "text"), "").strip()
        # Strip markdown fences if the model wrapped the JSON
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.error(f"Could not parse DDx JSON response: {e}")
    except Exception as e:
        st.error(f"API error: {e}")
    return None


# ── rendering helpers ─────────────────────────────────────────────────────────

RANK_COLORS = ["#6d28d9", "#0284c7", "#0d9488", "#ca8a04", "#6b7280"]


def render_ddx_card(dx: Dict[str, Any], idx: int) -> None:
    rank = dx.get("rank", idx + 1)
    css_rank = min(rank, 5)
    name = dx.get("name", "Unknown")
    pct = dx.get("probability_pct", 0)
    icd = dx.get("icd10", "")
    urgency = dx.get("urgency", "routine")
    for_items: List[str] = dx.get("for", [])
    against_items: List[str] = dx.get("against", [])
    next_steps = dx.get("next_steps", "")
    color = RANK_COLORS[min(rank - 1, 4)]

    urgency_html = ""
    if urgency == "immediate":
        urgency_html = '<span class="urgency-immediate">⚡ IMMEDIATE</span>'
    elif urgency == "urgent":
        urgency_html = '<span class="urgency-urgent">⚠ URGENT</span>'
    else:
        urgency_html = '<span class="urgency-routine">✓ ROUTINE</span>'

    bar_html = (
        f'<div class="bar-wrap">'
        f'<div class="bar-fill" style="width:{pct}%;background:linear-gradient(90deg,{color},{color}99)"></div>'
        f"</div>"
    )

    for_html = "".join(
        f'<div class="evidence-item"><div class="ev-dot ev-dot-for"></div><span>{item}</span></div>'
        for item in for_items
    )
    against_html = "".join(
        f'<div class="evidence-item"><div class="ev-dot ev-dot-against"></div><span>{item}</span></div>'
        for item in against_items
    )

    icd_html = f'<span class="icd-chip">ICD-10 {icd}</span>' if icd else ""

    for_fallback = '<div class="evidence-item" style="color:#94a3b8">None captured</div>'
    against_fallback = '<div class="evidence-item" style="color:#94a3b8">None captured</div>'
    grid_html = (
        '<div class="ddx-grid">'
        '<div>'
        '<div class="ddx-col-head col-for">Supporting evidence</div>'
        + (for_html or for_fallback) +
        '</div>'
        '<div>'
        '<div class="ddx-col-head col-against">Evidence against</div>'
        + (against_html or against_fallback) +
        '</div>'
        '</div>'
    )

    # Each st.markdown call is isolated — mixing HTML chunks in one block causes Streamlit to escape inner tags
    st.markdown(
        f"""
        <div class="ddx-card ddx-rank-{css_rank}">
          <div class="ddx-header">
            <span class="ddx-rank">#{rank}</span>
            <span class="ddx-name">{name}</span>
            <span class="ddx-pct">{pct}%</span>
            {urgency_html}
          </div>
          {bar_html}
          {grid_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if next_steps:
        st.markdown(
            f'<div style="margin:-8px 0 6px 0;padding:10px 16px;background:#f8fafc;'
            f'border-radius:12px;border-left:4px solid {color};font-size:13px;color:#0f172a;">'
            f'<span style="font-weight:800;color:{color};font-size:11px;text-transform:uppercase;'
            f'letter-spacing:.08em;">Next step &nbsp;·&nbsp; </span>{next_steps}</div>',
            unsafe_allow_html=True,
        )

    if icd_html:
        st.markdown(
            f'<div style="margin:-2px 0 18px 0;">{icd_html}</div>',
            unsafe_allow_html=True,
        )


def escalation_class(level: str) -> str:
    if "immediate" in level:
        return "escalation-immediate"
    if "urgent" in level:
        return "escalation-urgent"
    return ""


# ── main layout ───────────────────────────────────────────────────────────────

encounters = load_completed_encounters()

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🩺 DDx Console")
    st.caption("Probabilistic differential diagnosis from structured intake data.")
    st.divider()

    if not encounters:
        st.warning("No completed encounters found in the database.")
        st.stop()

    labels = []
    for i, e in enumerate(encounters):
        complaint = e["primary_complaint"].replace("_", " ").title()
        ts_raw = (e.get("created_at") or "")
        # Parse "2026-04-27 22:57:09" → "Apr 27, 2026  22:57"
        try:
            from datetime import datetime as _dt
            ts = _dt.strptime(ts_raw[:19], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y  %H:%M")
        except Exception:
            ts = ts_raw[:16]
        enc_num = len(encounters) - i  # most recent = highest number
        labels.append(f"Enc #{enc_num:03d}  ·  {ts}  ·  {complaint}")

    selected_idx = st.selectbox(
        "Encounter",
        options=range(len(encounters)),
        format_func=lambda i: labels[i],
        index=0,
        key="encounter_select",
    )

    enc = encounters[selected_idx]

    st.divider()
    st.markdown("**Patient summary**")
    complaint_display = enc["primary_complaint"].replace("_", " ").title()
    st.caption(f"**Complaint:** {complaint_display}")
    st.caption(f"**Age / Sex:** {enc.get('patient_age', '?')} y / {(enc.get('patient_sex') or '?').capitalize()}")
    esc = enc.get("escalation_level", "none")
    esc_label = esc.replace("_", " ").upper() if esc and esc != "none" else "None"
    st.caption(f"**Triage flag:** {esc_label}")
    st.caption(f"**Session:** `{enc.get('session_name', '')}`")

    st.divider()

    run_ddx = st.button("🔬 Get DDx", type="primary", use_container_width=True)

# ── main body ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <h1>Differential Diagnosis</h1>
      <p>AI-assisted probabilistic DDx · For clinical decision support only · Not a substitute for clinical judgment</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Encounter metadata strip
esc_chip_class = escalation_class(enc.get("escalation_level", ""))
esc_display = (enc.get("escalation_level") or "none").replace("_", " ").upper()
try:
    pp_list = json.loads(enc.get("pertinent_positive") or "[]")
    pn_list = json.loads(enc.get("pertinent_negative") or "[]")
except Exception:
    pp_list, pn_list = [], []

st.markdown(
    f"""
    <div class="card">
      <div class="meta-row">
        <span class="meta-chip">📋 {complaint_display}</span>
        <span class="meta-chip">🧑 {enc.get('patient_age','?')} y {(enc.get('patient_sex') or '?').capitalize()}</span>
        <span class="meta-chip {esc_chip_class}">⚑ {esc_display}</span>
        <span class="meta-chip">✚ {len(pp_list)} positives</span>
        <span class="meta-chip">✗ {len(pn_list)} negatives</span>
      </div>
      <div style="font-size:13px;color:#475569;line-height:1.5;">
        {(enc.get("ai_summary") or enc.get("pre_summary") or "<em>No narrative summary available.</em>")}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# State for DDx result
if "ddx_result" not in st.session_state:
    st.session_state.ddx_result = None
if "ddx_encounter_id" not in st.session_state:
    st.session_state.ddx_encounter_id = None

# Clear cached DDx if a different encounter is selected
if st.session_state.ddx_encounter_id != enc.get("id"):
    st.session_state.ddx_result = None
    st.session_state.ddx_encounter_id = enc.get("id")

if run_ddx:
    with st.spinner("Generating differential diagnosis…"):
        result = get_ddx(enc)
    if result:
        st.session_state.ddx_result = result

# Render results
if st.session_state.ddx_result:
    result = st.session_state.ddx_result
    diagnoses: List[Dict] = result.get("diagnoses", [])
    caveat: str = result.get("clinical_caveat", "")

    if diagnoses:
        st.markdown(
            f"<div style='font-size:13px;color:#64748b;margin-bottom:16px;'>"
            f"Showing <strong>{len(diagnoses)}</strong> ranked diagnoses · "
            f"Probabilities reflect prior likelihood given collected history only — "
            f"examine, investigate, and revise accordingly.</div>",
            unsafe_allow_html=True,
        )
        for i, dx in enumerate(diagnoses):
            render_ddx_card(dx, i)
    else:
        st.warning("No diagnoses returned. Try re-running.")

    if caveat:
        st.markdown(
            f'<div class="caveats-box">⚠️ <strong>Clinical caveat:</strong> {caveat}</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="card" style="text-align:center;padding:48px 24px;color:#94a3b8;">
          <div style="font-size:40px;margin-bottom:12px;">🔬</div>
          <div style="font-size:18px;font-weight:700;color:#64748b;margin-bottom:6px;">
            Ready to generate DDx
          </div>
          <div style="font-size:14px;">
            Select an encounter in the left panel, then press <strong>Get DDx</strong>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
