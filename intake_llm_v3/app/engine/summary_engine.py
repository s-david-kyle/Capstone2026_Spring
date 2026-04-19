"""Template and Anthropic Claude-backed summary generation."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import anthropic

ROS_DISPLAY = [
    "Constitutional", "Cardiovascular", "Respiratory", "Gastrointestinal",
    "Genitourinary", "Neurological", "Musculoskeletal", "Skin",
    "Endocrine", "Hematologic or Lymphatic", "Psychiatric"
]

NEGATIVE_WORDS = {"no", "denied", "none", "negative", "false", "nil", "nothing", "never", "not at all"}


def _build_hpi(state: Dict[str, Any], complaint_name: str) -> str:
    parts: List[str] = []
    narrative = state.get("presenting_complaint_narrative")
    parts.append(f"Patient presents with {complaint_name.lower()}.")
    if narrative and narrative != "not_assessed" and len(str(narrative).strip()) > 5:
        parts.append(f'Patient states: "{narrative}"')
    onset = state.get("onset") or state.get("event_timing") or state.get("time_of_injury")
    duration = state.get("duration")
    if onset and onset != "not_assessed":
        parts.append(f"Onset: {onset}.")
    if duration and duration != "not_assessed" and duration != onset:
        parts.append(f"Duration: {duration}.")
    loc = state.get("location") or state.get("pain_site") or state.get("site") or state.get("location_of_injury")
    char = state.get("character")
    loc_ok = loc and str(loc).strip().lower() not in NEGATIVE_WORDS and loc != "not_assessed"
    char_ok = char and str(char).strip().lower() not in NEGATIVE_WORDS and char != "not_assessed"
    if loc_ok and char_ok:
        parts.append(f"Located in the {loc}, described as {char}.")
    elif loc_ok:
        parts.append(f"Location: {loc}.")
    elif char_ok:
        parts.append(f"Character: {char}.")
    sev = state.get("severity") or state.get("pain_severity")
    if sev and sev != "not_assessed" and str(sev).strip().lower() not in NEGATIVE_WORDS:
        parts.append(f"Severity: {sev}.")
    for key, label in [
        ("course", "Course"),
        ("radiation", "Radiation"),
        ("aggravating_factors", "Aggravating factors"),
        ("relieving_factors", "Relieving factors"),
        ("functional_impact", "Functional impact"),
        ("associated_symptoms", "Associated symptoms"),
    ]:
        val = state.get(key)
        if val and str(val).lower() not in NEGATIVE_WORDS and val != "not_assessed":
            parts.append(f"{label}: {val}.")
    return " ".join(parts)


def generate_template_summary(engine, ros_answers=None) -> Dict[str, Any]:
    s = engine.state
    cn = engine.complaint.get("display_name", "Unknown")
    contract = engine.complaint.get("summary_contract", {})
    missing_sources = contract.get("missing_clarifications", {}).get("source", [])
    schedule = engine.current_profile_data
    required_fields = set()
    for src in missing_sources:
        if src in schedule:
            for qid in schedule[src]:
                field = engine.questions.get(qid, {}).get("field", qid)
                required_fields.add(field)
    missing = sorted(f.replace("_", " ") for f in required_fields if s.get(f) is None)
    positives, negatives = [], []
    skip_fields = {"presenting_complaint_narrative", "OtherSymptomDetails", "_escalation_level"}
    for f, v in s.items():
        if f in skip_fields or v in (None, "", "not_assessed", "unknown"):
            continue
        low = str(v).lower().strip()
        if low in NEGATIVE_WORDS:
            negatives.append(f.replace("_", " "))
        else:
            positives.append(f"{f.replace('_', ' ')}: {v}")
    flags = [
        f"{f['pattern'].replace('_', ' ')} (triggered by {f['trigger_field'].replace('_', ' ')}: {f['value']})"
        for f in engine.red_flags
    ] or ["None"]

    ros_summary = {sys: "Not assessed" for sys in ROS_DISPLAY}
    for key, value in (ros_answers or {}).items():
        display = key.replace("_", " ").title()
        ros_summary[display] = value

    return {
        "chief_complaint": cn,
        "other_concerns": s.get("secondary_complaints", "None reported"),
        "hpi": _build_hpi(s, cn),
        "ros": ros_summary,
        "pertinent_positives": positives,
        "pertinent_negatives": negatives,
        "pmh_psh": s.get("PastMedicalHistory", "Not obtained"),
        "past_surgical": s.get("PastSurgicalHistory", "Not obtained"),
        "medications": s.get("MedicationsTreatments", "Not obtained"),
        "allergies": s.get("Allergies", "Not obtained"),
        "social_factors": s.get("SocialHistory", "Not obtained"),
        "family_history": s.get("FamilyHistory", "Not obtained"),
        "smoking": s.get("smoking_history", "Not obtained"),
        "alcohol": s.get("alcohol_history", "Not obtained"),
        "missing_clarifications": missing,
        "flags": flags,
        "escalation_level": engine.escalation_level,
        "questions_asked": engine.questions_asked,
        "generated_at": datetime.utcnow().isoformat(),
    }


def ai_summarize(extracted_state: Dict[str, Any], template_summary: Dict[str, Any]) -> str:
    """Generate a fluent HPI paragraph using Claude Sonnet via the Anthropic API."""
    from api_keys import ANTHROPIC_API_KEY

    prompt = (
        "You are a clinical documentation assistant. Write a concise, factual HPI paragraph "
        "suitable for a clinician to review and sign. Do not invent findings. "
        "If information is missing, do not fill it in.\n\n"
        f"Chief Complaint: {template_summary.get('chief_complaint', 'Unknown')}\n\n"
        f"Extracted data: {json.dumps({k: v for k, v in extracted_state.items() if v and v != 'not_assessed'}, indent=2)}\n\n"
        f"Pertinent Positives: {'; '.join(template_summary.get('pertinent_positives', []))}\n"
        f"Pertinent Negatives: {', '.join(template_summary.get('pertinent_negatives', []))}\n"
        f"Red Flags: {'; '.join(template_summary.get('flags', ['None']))}\n\n"
        "Write only the HPI paragraph. Be concise and use clinical language."
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip() or template_summary.get("hpi", "")
    except Exception as e:
        print(f"AI summarizer error: {e}")
        return template_summary.get("hpi", "AI summarizer unavailable.")


def format_summary_text(summary: Dict[str, Any]) -> str:
    lines = [
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
        "Missing Clarifications: " + (", ".join(summary["missing_clarifications"]) or "None"),
        "Flags: " + "; ".join(summary["flags"]),
        f"Escalation Level: {summary['escalation_level']}",
    ]
    return "\n".join(lines)


def format_transcript(turns: List[Dict[str, Any]], complaint_name: str = "", age: int = 0, sex: str = "") -> str:
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
