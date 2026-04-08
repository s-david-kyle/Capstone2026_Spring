"""
Summary generation v2.3
- deterministic template summary
- simple ROS rendering from structured state
- transcript formatter
"""
from __future__ import annotations

from datetime import datetime

ROS_SECTIONS = {
    "Constitutional": ["fever", "rigors_or_chills", "night_sweats", "fatigue", "weakness", "weight_loss", "weight_gain", "loss_of_appetite"],
    "Cardiovascular": ["chest_pain", "palpitations", "irregular_heartbeat", "syncope", "near_syncope", "orthopnea_or_pnd", "exertional_dyspnea", "leg_swelling"],
    "Respiratory": ["shortness_of_breath", "cough", "sputum", "hemoptysis", "wheeze", "pleuritic_pain"],
    "Gastrointestinal": ["abdominal_pain", "nausea", "vomiting", "diarrhea", "constipation", "blood_in_stool", "heartburn", "bloating", "loss_of_appetite"],
    "Genitourinary": ["dysuria", "urinary_frequency_or_urgency", "hematuria", "flank_pain", "incontinence", "vaginal_bleeding", "vaginal_discharge", "pregnancy_context"],
    "Neurological": ["headache", "dizziness", "lightheadedness", "syncope", "weakness", "numbness_or_tingling", "seizure", "confusion_or_ams", "speech_change", "visual_loss"],
    "Musculoskeletal": ["joint_pain", "muscle_pain", "back_pain", "neck_pain", "joint_swelling", "stiffness", "limited_range_of_motion"],
    "Skin": ["rash", "itching", "lesions", "bruising"],
    "Endocrine": ["heat_intolerance", "cold_intolerance", "polyuria_polydipsia", "excessive_hunger"],
    "Hematologic or Lymphatic": ["easy_bruising", "easy_bleeding", "lymph_node_swelling", "anaemia_symptoms"],
    "Psychiatric": ["anxiety", "depression", "mood_changes", "sleep_disturbances"],
}


def _negish(v: str) -> bool:
    return str(v).strip().lower() in {"no", "denied", "none", "negative", "false", "nil", "nothing", "never", "not at all"}


def _field_label(name: str) -> str:
    return name.replace("_", " ")


def _render_ros(engine_state: dict) -> dict[str, str]:
    rendered = {}
    for section, fields in ROS_SECTIONS.items():
        vals = []
        for field in fields:
            if field not in engine_state:
                continue
            value = engine_state.get(field)
            if not value or value in ("not_assessed", "unknown"):
                continue
            if _negish(value):
                vals.append(f"denies {_field_label(field)}")
            else:
                vals.append(f"{_field_label(field)} present")
        rendered[section] = ", ".join(vals) if vals else "not assessed"
    return rendered


def _build_hpi(state: dict, complaint_name: str) -> str:
    parts = [f"Patient presents with {complaint_name.lower()}."]
    narrative = state.get("presenting_complaint_narrative")
    if narrative and narrative not in ("not_assessed", "unknown"):
        parts.append(f'Patient states: "{narrative}".')
    onset = state.get("onset") or state.get("event_timing")
    if onset and onset != "not_assessed":
        parts.append(f"Onset {onset}.")
    duration = state.get("duration")
    if duration and duration != "not_assessed":
        parts.append(f"Duration {duration}.")
    location = state.get("location") or state.get("site") or state.get("pain_site")
    character = state.get("character")
    if location:
        parts.append(f"Location: {location}.")
    if character:
        parts.append(f"Character: {character}.")
    severity = state.get("severity") or state.get("pain_severity")
    if severity and severity != "not_assessed":
        parts.append(f"Severity: {severity}.")
    course = state.get("course")
    if course and course != "not_assessed":
        parts.append(f"Course: {course}.")
    functional = state.get("functional_impact") or state.get("functional_loss")
    if functional and functional != "not_assessed":
        parts.append(f"Functional impact: {functional}.")
    positives = []
    for field, val in state.items():
        if field in {"presenting_complaint_narrative", "onset", "duration", "location", "character", "severity", "pain_severity", "course", "functional_impact", "functional_loss"}:
            continue
        if not val or val in ("not_assessed", "unknown") or _negish(val):
            continue
        if field.endswith("_details"):
            continue
        detail = state.get(f"{field}_details")
        positives.append(f"{_field_label(field)} ({detail})" if detail else _field_label(field))
    if positives:
        parts.append("Associated with: " + ", ".join(positives[:10]) + ".")
    return " ".join(parts)


def generate_template_summary(engine):
    state = engine.state
    complaint_name = engine.complaint.get("display_name", "Unknown")
    pos, neg = [], []
    for field, value in state.items():
        if not value or value in ("not_assessed", "unknown"):
            continue
        if field.endswith("_details"):
            continue
        if _negish(value):
            neg.append(_field_label(field))
        else:
            pos.append(f"{_field_label(field)}: {value}")
    core = engine.schedule.get("core_characterize", []) + engine.schedule.get("early_danger_screen", []) + engine.schedule.get("critical_followup", [])
    missing = [_field_label(qid) for qid in core if engine.state.get(engine.questions.get(qid, {}).get("field", qid)) is None]
    flags = [
        f"{rf['pattern'].replace('_', ' ')} (triggered by {rf['trigger_field'].replace('_', ' ')}: {rf['value']})"
        for rf in engine.red_flags
    ] or ["None"]
    return {
        "chief_complaint": complaint_name,
        "other_concerns": state.get("secondary_complaints", "None reported"),
        "hpi": _build_hpi(state, complaint_name),
        "ros": _render_ros(state),
        "pertinent_positives": pos,
        "pertinent_negatives": neg,
        "pmh_psh": state.get("PastMedicalHistory", "Not obtained"),
        "past_surgical": state.get("PastSurgicalHistory", "Not obtained"),
        "medications": state.get("MedicationsTreatments", "Not obtained"),
        "allergies": state.get("Allergies", "Not obtained"),
        "social_factors": state.get("SocialHistory", "Not obtained"),
        "family_history": state.get("FamilyHistory", "Not obtained"),
        "missing_clarifications": missing,
        "flags": flags,
        "escalation_level": engine.escalation_level,
        "questions_asked": engine.questions_asked,
    }


def format_summary_text(summary: dict) -> str:
    lines = [
        f"Chief Complaint (Primary): {summary['chief_complaint']}",
        f"Other Concerns: {summary['other_concerns']}",
        "",
        "HPI:",
        summary["hpi"],
        "",
        "Review of Systems (ROS):",
    ]
    for section, value in summary["ros"].items():
        lines.append(f"  {section}: {value}")
    lines += [
        "",
        "Pertinent Positives: " + ("; ".join(summary["pertinent_positives"]) or "None identified"),
        "Pertinent Negatives: " + ("; ".join(summary["pertinent_negatives"]) or "None identified"),
        "",
        f"PMH / PSH: {summary['pmh_psh']}",
        f"Past Surgical History: {summary['past_surgical']}",
        f"Medications: {summary['medications']}",
        f"Allergies: {summary['allergies']}",
        f"Social Factors: {summary['social_factors']}",
        f"Family History: {summary['family_history']}",
        "",
        "Missing Clarifications: " + (", ".join(summary["missing_clarifications"]) or "None"),
        "Flags: " + "; ".join(summary["flags"]),
        f"Escalation Level: {summary['escalation_level']}",
    ]
    return "\n".join(lines)


def format_transcript(turns: list[dict], complaint_name: str = "", age: int = 0, sex: str = "") -> str:
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
    for turn in turns:
        header.append(f"[{turn.get('phase', '')}] Q: {turn.get('question_text', '')}")
        header.append(f"  A: {'[SKIPPED]' if turn.get('skipped') else turn.get('answer', '')}")
        header.append("")
    return "\n".join(header)
