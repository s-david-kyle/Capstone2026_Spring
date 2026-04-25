"""Template and AI-backed summary generation aligned to rebuilt complaint files."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from api_keys import ANTHROPIC_API_KEY as _ANTHROPIC_API_KEY
except ImportError:
    _ANTHROPIC_API_KEY = ""

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

ROS_DISPLAY = [
    "Constitutional", "Cardiovascular", "Respiratory", "Gastrointestinal",
    "Genitourinary", "Neurological", "Musculoskeletal", "Skin",
    "Endocrine", "Hematologic or Lymphatic", "Psychiatric",
]

NEGATIVE_WORDS = {"no", "denied", "none", "negative", "false", "nil", "nothing", "never", "not at all"}

# This list is kept for backward compatibility but no longer used for ROS filtering.
# The ROS block now uses the ROS bank index exclusively.
NON_ROS_FIELDS = {
    "presenting_complaint_narrative","OtherSymptomDetails","secondary_complaints",
    "onset","pattern","duration","severity","location","site","character",
    "pain_site","pain_specific_location","pain_distribution","dominant_pain_site_if_multiple",
    "pain_severity","radiation","aggravating_factors","relieving_factors","functional_impact",
    "associated_symptoms","course","timing","time_of_injury","location_of_injury","event_timing",
    "past_medical_history","past_surgical_history","current_medications","allergies","family_history",
    "occupation","living_situation","recent_travel","occupational_exposures","smoking_current",
    "smoking_past","alcohol_current","recreational_drug_use","sexual_history","new_partner",
    "partner_symptoms","known_sti_exposure","recent_unprotected_sex","pregnancy_context","lmp",
    "last_menstrual_period","timing_with_cycle","contraceptive_use","menopausal_status","douching",
    "local_hygiene_products","gynecologic_history_other","immunization_record_available",
    "childhood_immunizations_current","influenza_immunization_recent","covid_immunization_recent",
    "pneumococcal_immunization_history","bcg_immunization_history",
    "meningococcal_or_hib_immunization_history","other_relevant_immunization_history","recent_antibiotics",
    "recent_catheter","prior_uti","prior_stones","prior_abdominal_surgery","anticoagulant_use",
    "immunocompromised_state","diabetes_history","family_history_bladder_or_kidney_cancer",
    "family_history_early_heart_disease","prior_clot_history","clot_risk_history","prior_cardiac_history",
    "known_asthma_or_copd","known_heart_failure","known_kidney_disease","known_liver_disease","known_epilepsy",
    "prior_seizure_history","prior_brain_pathology","family_history_epilepsy","family_history_sudden_death",
    "family_history_cancer","family_history_arthritis","psoriasis_history","uric_acid_risk",
    "osteoporosis_or_steroid_use","prior_anaemia","history_of_cancer","atrial_fibrillation_or_vascular_history",
    "_escalation_level",
}

def _is_meaningful(value: Any) -> bool:
    return value not in (None, "", "not_assessed", "unknown")

def _clean_answer(answer: Any) -> str:
    return "" if answer is None else str(answer).strip()

def _project_root() -> str:
    return os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def _build_ros_bank_index(project_root: str) -> Dict[str, Dict[str, Any]]:
    """Build an index of ROS questions by field name, using ros_question_bank.json."""
    path = os.path.join(project_root, "complaints_modules", "ros_question_bank.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        bank = json.load(f)
    out: Dict[str, Dict[str, Any]] = {}
    for qid, q in bank.get("questions", {}).items():
        field = q.get("field") or qid
        out[field] = {
            "display_system": q.get("display_system"),
            "system": q.get("system"),
            "canonical_concept": q.get("canonical_concept"),
            "ui_label": q.get("ui_label", field.replace("_", " ")),
            "detail_field": q.get("detail_field"),
            "parent_field": q.get("parent_field"),
        }
    return out

def _build_hpi(state: Dict[str, Any], complaint_name: str) -> str:
    """Build the HPI (History of Present Illness) paragraph from captured state."""
    parts: List[str] = []
    narrative = state.get("presenting_complaint_narrative")
    parts.append(f"Patient presents with {complaint_name.lower()}.")
    if _is_meaningful(narrative) and len(str(narrative).strip()) > 5:
        parts.append(f'Patient states: "{narrative}"')
    onset = state.get("onset") or state.get("event_timing") or state.get("time_of_injury")
    duration = state.get("duration")
    if _is_meaningful(onset):
        parts.append(f"Onset: {onset}.")
    if _is_meaningful(duration) and duration != onset:
        parts.append(f"Duration: {duration}.")
    loc = state.get("location") or state.get("pain_site") or state.get("site") or state.get("location_of_injury")
    char = state.get("character")
    loc_ok = _is_meaningful(loc) and str(loc).strip().lower() not in NEGATIVE_WORDS
    char_ok = _is_meaningful(char) and str(char).strip().lower() not in NEGATIVE_WORDS
    if loc_ok and char_ok:
        parts.append(f"Located in the {loc}, described as {char}.")
    elif loc_ok:
        parts.append(f"Location: {loc}.")
    elif char_ok:
        parts.append(f"Character: {char}.")
    sev = state.get("severity") or state.get("pain_severity")
    if _is_meaningful(sev) and str(sev).strip().lower() not in NEGATIVE_WORDS:
        parts.append(f"Severity: {sev}.")
    for key, label in [("course","Course"),("radiation","Radiation"),("aggravating_factors","Aggravating factors"),("relieving_factors","Relieving factors"),("functional_impact","Functional impact"),("associated_symptoms","Associated symptoms")]:
        val = state.get(key)
        if _is_meaningful(val) and str(val).lower() not in NEGATIVE_WORDS:
            parts.append(f"{label}: {val}.")
    return " ".join(parts)

def _build_ros_block(state: Dict[str, Any], ros_bank: Dict[str, Dict[str, Any]], complaint_questions: Dict[str, Any]) -> Dict[str, List[Tuple[str, str, bool]]]:
    """
    Build ROS block using only fields that exist in the ROS bank index.
    This ensures that non‑ROS qualifiers (like persistent_vomiting) never appear.
    """
    by_system: Dict[str, List[Tuple[str, str, bool]]] = {s: [] for s in ROS_DISPLAY}
    # First pass: collect detail answers for parents
    seen_parents: Dict[str, str] = {}
    for field, value in state.items():
        if not _is_meaningful(value):
            continue
        meta = ros_bank.get(field)
        if meta and meta.get("parent_field"):
            seen_parents[meta.get("parent_field")] = _clean_answer(value)
    # Second pass: only fields present in ros_bank
    for field, value in state.items():
        if not _is_meaningful(value):
            continue
        meta = ros_bank.get(field)
        if not meta or meta.get("parent_field"):
            continue
        ds = meta.get("display_system")
        if not ds or ds not in by_system:
            continue
        label = meta.get("ui_label", field.replace("_", " "))
        txt = _clean_answer(value)
        is_pos = txt.lower() not in NEGATIVE_WORDS
        detail_text = seen_parents.get(field)
        if detail_text and detail_text.lower() not in {"yes","true","y"} | NEGATIVE_WORDS:
            display = f"{label}: {detail_text}"
        else:
            display = f"{label}: {txt}" if is_pos else f"{label}: denied"
        by_system[ds].append((label, display, is_pos))
    return by_system

def _get_required_fields_from_complaint(engine) -> List[str]:
    """Extract required fields from the complaint's phase map."""
    required_fields: List[str] = []
    question_phase_map = engine.complaint.get("question_phase_map", {})
    if isinstance(question_phase_map, dict):
        for phase, qids in question_phase_map.items():
            if phase == "final_closeout":
                continue
            for qid in qids:
                q = engine.questions.get(qid, {})
                field = q.get("field", qid)
                if field and field != "final_closeout_question":
                    required_fields.append(field)
        return required_fields
    current_profile_data = getattr(engine, "current_profile_data", {}) or {}
    if isinstance(current_profile_data, dict):
        for qids in current_profile_data.values():
            for qid in qids:
                q = engine.questions.get(qid, {})
                field = q.get("field", qid)
                if field and field != "final_closeout_question":
                    required_fields.append(field)
    return required_fields

def _build_missing_clarifications(engine) -> List[str]:
    """Identify required fields that remain empty in the state."""
    seen = set()
    missing: List[str] = []
    for field in _get_required_fields_from_complaint(engine):
        if field in seen:
            continue
        seen.add(field)
        if engine.state.get(field) in (None, "", "not_assessed"):
            missing.append(field.replace("_", " "))
    return missing

def generate_template_summary(engine, ros_answers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate the structured template summary from engine state."""
    state = engine.state
    complaint_name = engine.complaint.get("display_name", "Unknown")
    positives, negatives = [], []
    skip_fields = set(NON_ROS_FIELDS) | {"_escalation_level"}
    for field, value in state.items():
        if str(field).startswith("_") or field in skip_fields or not _is_meaningful(value):
            continue
        low = str(value).strip().lower()
        if low in NEGATIVE_WORDS:
            negatives.append(field.replace("_", " "))
        else:
            positives.append(f"{field.replace('_', ' ')}: {value}")
    flags = [f"{f['pattern'].replace('_', ' ')} (triggered by {f['trigger_field'].replace('_', ' ')}: {f['value']})" for f in engine.red_flags] or ["None"]
    ros_bank = _build_ros_bank_index(_project_root())
    ros_details = _build_ros_block(state, ros_bank, engine.complaint.get("questions_by_id", {}))
    ros_summary: Dict[str, str] = {}
    for sys_name in ROS_DISPLAY:
        items = ros_details.get(sys_name, [])
        if not items:
            ros_summary[sys_name] = "Not assessed"
            continue
        pos = [d for (_l, d, p) in items if p]
        neg = [d for (_l, d, p) in items if not p]
        parts = []
        if pos:
            parts.append("; ".join(pos))
        if neg:
            parts.append("denies " + ", ".join(d.split(":", 1)[0].strip() for d in neg))
        ros_summary[sys_name] = " | ".join(parts) if parts else "Not assessed"
    social_parts = []
    for field in ["occupation","living_situation","recent_travel","occupational_exposures"]:
        val = state.get(field)
        if _is_meaningful(val):
            social_parts.append(str(val))
    social_factors = ", ".join(social_parts) if social_parts else "Not obtained"
    smoking_parts = []
    for field in ["smoking_current","smoking_past"]:
        val = state.get(field)
        if _is_meaningful(val):
            smoking_parts.append(str(val))
    smoking = ", ".join(smoking_parts) if smoking_parts else "Not obtained"
    alcohol = state.get("alcohol_current")
    alcohol = alcohol if _is_meaningful(alcohol) else "Not obtained"
    gynecologic = state.get("gynecologic_history_other")
    gynecologic = gynecologic if _is_meaningful(gynecologic) else "Not obtained"
    immunization_parts = []
    for field in ["immunization_record_available","childhood_immunizations_current","influenza_immunization_recent","covid_immunization_recent","pneumococcal_immunization_history","bcg_immunization_history","meningococcal_or_hib_immunization_history","other_relevant_immunization_history"]:
        val = state.get(field)
        if _is_meaningful(val):
            immunization_parts.append(str(val))
    immunization = ", ".join(immunization_parts) if immunization_parts else "Not obtained"
    return {
        "chief_complaint": complaint_name,
        "other_concerns": state.get("secondary_complaints", "None reported"),
        "hpi": _build_hpi(state, complaint_name),
        "ros": ros_summary,
        "ros_details": {k: [{"label": l, "text": t, "is_positive": p} for (l, t, p) in v] for k, v in ros_details.items()},
        "pertinent_positives": positives,
        "pertinent_negatives": negatives,
        "pmh_psh": state.get("past_medical_history", "Not obtained"),
        "past_surgical": state.get("past_surgical_history", "Not obtained"),
        "medications": state.get("current_medications", "Not obtained"),
        "allergies": state.get("allergies", "Not obtained"),
        "social_factors": social_factors,
        "family_history": state.get("family_history", "Not obtained"),
        "smoking": smoking,
        "alcohol": alcohol,
        "gynecologic_history": gynecologic,
        "immunization_history": immunization,
        "missing_clarifications": _build_missing_clarifications(engine),
        "flags": flags,
        "escalation_level": engine.escalation_level,
        "questions_asked": engine.questions_asked,
        "generated_at": datetime.utcnow().isoformat(),
    }

def ai_summarize(extracted_state: Dict[str, Any], template_summary: Dict[str, Any], model: str = "claude-sonnet-4-20250514") -> str:
    """
    Generate AI summary with fallback order:
    1) Anthropic, if API key is available
    2) local Ollama
    3) template HPI
    """
    ros_lines = []
    for sys_name, detail in template_summary.get("ros", {}).items():
        if detail and detail != "Not assessed":
            ros_lines.append(f"  {sys_name}: {detail}")

    compact_state = {k: v for k, v in extracted_state.items() if not str(k).startswith("_") and _is_meaningful(v)}
    prompt = (
        "You are a clinical documentation assistant. Write a thorough, factual HPI "
        "paragraph (5-10 sentences) that incorporates every relevant captured finding below. "
        "Do not invent information. Do not omit captured positives. Name the key negatives "
        "at the end in one sentence. If a finding was explicitly denied, report it as denied. "
        "Keep sentences clinical and concise.\n\n"
        f"Chief complaint: {template_summary.get('chief_complaint', 'Unknown')}\n"
        f"Other concerns: {template_summary.get('other_concerns', 'None reported')}\n\n"
        f"Captured state:\n{json.dumps(compact_state, indent=2)}\n\n"
        f"Pertinent positives: {'; '.join(template_summary.get('pertinent_positives', []))}\n"
        f"Pertinent negatives: {', '.join(template_summary.get('pertinent_negatives', []))}\n"
        f"Red flags: {'; '.join(template_summary.get('flags', ['None']))}\n"
        f"Escalation level: {template_summary.get('escalation_level', 'none')}\n\n"
        + ("Review of systems:\n" + "\n".join(ros_lines) + "\n\n" if ros_lines else "")
        + "Write only the HPI paragraph."
    )

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "") or _ANTHROPIC_API_KEY

    if anthropic_key:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            resp.raise_for_status()
            content = resp.json().get("content", [])
            text = next((block["text"] for block in content if block.get("type") == "text"), "")
            if text and text.strip():
                return text.strip()
        except Exception:
            pass

    try:
        ollama_payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 700,
                "temperature": 0.2,
            },
        }
        resp = requests.post(OLLAMA_URL, json=ollama_payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = (data.get("response") or "").strip()
        if text:
            return text
    except Exception:
        pass

    return template_summary.get("hpi", "AI summarizer unavailable.")

def format_summary_text(summary: Dict[str, Any]) -> str:
    """Format the template summary into readable text."""
    lines = [
        f"Patient: {summary.get('patient_age', 'Unknown')} years, {summary.get('patient_sex', 'Unknown')}",
        "",
        f"Chief Complaint (Primary): {summary['chief_complaint']}",
        f"Other Concerns: {summary['other_concerns']}",
        "",
        "HPI:",
        summary["hpi"],
        "",
        "Review of Systems (ROS):",
    ]
    for sys, val in summary["ros"].items():
        lines.append(f"  {sys}: {val}")
    lines += [
        "",
        "Pertinent Positives: " + ("; ".join(summary["pertinent_positives"]) or "None"),
        "Pertinent Negatives: " + (", ".join(summary["pertinent_negatives"]) or "None"),
        "",
        f"PMH / PSH: {summary['pmh_psh']}",
        f"Past Surgical History: {summary['past_surgical']}",
        f"Medications: {summary['medications']}",
        f"Allergies: {summary['allergies']}",
        f"Social Factors: {summary['social_factors']}",
        f"Family History: {summary.get('family_history', 'Not obtained')}",
        "",
        f"Smoking: {summary.get('smoking', 'Not obtained')}",
        f"Alcohol: {summary.get('alcohol', 'Not obtained')}",
        f"Gynecologic History: {summary.get('gynecologic_history', 'Not obtained')}",
        f"Immunization History: {summary.get('immunization_history', 'Not obtained')}",
        "",
        "Missing Clarifications: " + (", ".join(summary["missing_clarifications"]) or "None"),
        "Flags: " + "; ".join(summary["flags"]),
        f"Escalation Level: {summary['escalation_level']}",
    ]
    return "\n".join(lines)

def format_transcript(turns: List[Dict[str, Any]], complaint_name: str = "", age: int = 0, sex: str = "") -> str:
    """Format the session transcript for export."""
    header = [
        "=" * 60,
        "CLINICAL INTAKE TRANSCRIPT",
        "=" * 60,
        f"Complaint: {complaint_name}",
        f"Patient: Age {age}, Sex {sex}",
        f"Date: {datetime.utcnow().isoformat()}",
        "=" * 60,
        "",
    ]
    body = []
    for turn in turns:
        body.append(f"[{turn.get('phase', '')}] Q: {turn.get('question_text', '')}")
        body.append(f"  A: {'[SKIPPED]' if turn.get('skipped') else turn.get('answer', '')}")
        body.append("")
    return "\n".join(header + body)