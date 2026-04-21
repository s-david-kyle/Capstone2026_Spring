"""Template and Ollama-backed summary generation.

FIX NOTES vs previous version:
  1. ROS block is now populated by walking the intake state and resolving each
     field's display_system via the ROS bank (and the shared field_registry if
     present). Previously the function required a separate `ros_answers` dict
     that was never passed in, so every system stayed "Not assessed".
  2. Every "not_assessed" system is shown as "Not assessed"; every system with
     at least one answer gets a structured line listing positives and negatives.
  3. AI prompt broadened to include ROS, modules data, red flags, escalation,
     and explicit instructions to include ALL captured positives + key negatives.
     Also raises num_predict so the output isn't truncated.
  4. Negatives now filter out clearly-irrelevant "not_assessed" / empty values.
  5. HPI keeps its prior behaviour but no longer double-reports duration==onset.
  6. Added patient line, smoking, alcohol, gynecologic, immunization to summary.
"""
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

ROS_DISPLAY = [
    "Constitutional", "Cardiovascular", "Respiratory", "Gastrointestinal",
    "Genitourinary", "Neurological", "Musculoskeletal", "Skin",
    "Endocrine", "Hematologic or Lymphatic", "Psychiatric"
]

NEGATIVE_WORDS = {"no", "denied", "none", "negative", "false", "nil", "nothing", "never", "not at all"}

# ------------------------------------------------------------------------------
# Fields that are collected by the core complaint flow or history modules, not
# by ROS. They should not appear in the Review of Systems block even when set.
# Keep this list in sync with the canonical fields in shared_v2.json and the
# history module fields.
# ------------------------------------------------------------------------------
NON_ROS_FIELDS = {
    # Core complaint fields
    "presenting_complaint_narrative", "OtherSymptomDetails", "secondary_complaints",
    "onset", "duration", "severity", "location", "site", "character",
    "pain_site", "pain_specific_location", "pain_distribution",
    "dominant_pain_site_if_multiple", "pain_severity",
    "radiation", "aggravating_factors", "relieving_factors", "functional_impact",
    "associated_symptoms", "course", "timing", "time_of_injury",
    "location_of_injury", "event_timing",
    # Past medical / surgical / medications / allergies
    "past_medical_history", "past_surgical_history", "current_medications",
    "allergies", "family_history",
    # Social history
    "occupation", "living_situation", "recent_travel", "occupational_exposures",
    "smoking_current", "smoking_past", "alcohol_current", "recreational_drug_use",
    # Sexual / STI
    "sexual_history", "new_partner", "partner_symptoms",
    "known_sti_exposure", "recent_unprotected_sex",
    # Gynecologic
    "pregnancy_context", "lmp", "timing_with_cycle",
    "contraceptive_use", "menopausal_status",
    "douching", "local_hygiene_products", "gynecologic_history_other",
    # Immunization
    "immunization_record_available", "childhood_immunizations_current",
    "influenza_immunization_recent", "covid_immunization_recent",
    "pneumococcal_immunization_history", "bcg_immunization_history",
    "meningococcal_or_hib_immunization_history",
    "other_relevant_immunization_history",
    # Medications / antibiotics
    "recent_antibiotics",
    # Additional v1.0.0 fields that belong to history/context
    "recent_catheter", "prior_uti", "prior_stones", "prior_abdominal_surgery",
    "anticoagulant_use", "immunocompromised_state", "diabetes_history",
    "family_history_bladder_or_kidney_cancer", "family_history_early_heart_disease",
    "prior_clot_history", "clot_risk_history", "prior_cardiac_history",
    "known_asthma_or_copd", "known_heart_failure", "known_kidney_disease",
    "known_liver_disease", "known_epilepsy", "prior_seizure_history",
    "prior_brain_pathology", "family_history_epilepsy", "family_history_sudden_death",
    "family_history_cancer", "family_history_arthritis", "psoriasis_history",
    "uric_acid_risk", "osteoporosis_or_steroid_use", "prior_anaemia",
    "history_of_cancer", "atrial_fibrillation_or_vascular_history",
    # Internal fields
    "_escalation_level",
}


def _strip_details_suffix(field: str) -> str:
    return field[:-len("_details")] if field.endswith("_details") else field


def _is_meaningful(value: Any) -> bool:
    if value in (None, "", "not_assessed", "unknown"):
        return False
    return True


def _clean_answer(answer: Any) -> str:
    if answer is None:
        return ""
    return str(answer).strip()


def _build_ros_bank_index(project_root: str) -> Dict[str, Dict[str, Any]]:
    """Return {field: {display_system, canonical_concept, ui_label, detail_field,
    parent_field}} for every entry in the ROS bank."""
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


def _project_root_from_engine(engine) -> str:
    # engine already knows where its complaint file lives; fall back to env var
    return os.environ.get("PROJECT_ROOT", os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


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


def _build_ros_block(
    state: Dict[str, Any],
    ros_bank: Dict[str, Dict[str, Any]],
    complaint_questions: Dict[str, Any],
) -> Dict[str, List[Tuple[str, str, bool]]]:
    """
    For each ROS display system, collect the (ui_label, answer_text, is_positive)
    tuples for fields answered anywhere in the session that belong to that system.
    Detail fields are attached to their parent in the output text.
    """
    # Build a lookup from field -> (display_system, ui_label, is_detail_of)
    # using the ROS bank AND any ROS-style entry in the complaint file.
    field_meta: Dict[str, Dict[str, Any]] = {}
    for field, meta in ros_bank.items():
        field_meta[field] = meta
    # Also inherit display_system from complaint questions that explicitly declare one
    for qid, q in (complaint_questions or {}).items():
        f = q.get("field") or qid
        ds = q.get("display_system")
        if ds and f not in field_meta:
            field_meta[f] = {
                "display_system": ds,
                "system": q.get("system"),
                "canonical_concept": q.get("canonical_concept"),
                "ui_label": q.get("ui_label", f.replace("_", " ")),
                "detail_field": q.get("detail_field"),
                "parent_field": q.get("parent_field"),
            }

    by_system: Dict[str, List[Tuple[str, str, bool]]] = {s: [] for s in ROS_DISPLAY}
    seen_parents: Dict[str, str] = {}  # parent_field -> its detail text (if any)

    # First pass: collect detail texts so we can attach them to their parent
    for field, value in state.items():
        if field in NON_ROS_FIELDS or field.startswith("_"):
            continue
        if not _is_meaningful(value):
            continue
        meta = field_meta.get(field)
        if not meta:
            continue
        pf = meta.get("parent_field")
        if pf:
            seen_parents[pf] = _clean_answer(value)

    # Second pass: emit one line per parent field that was answered
    for field, value in state.items():
        if field in NON_ROS_FIELDS or field.startswith("_"):
            continue
        if not _is_meaningful(value):
            continue
        meta = field_meta.get(field)
        if not meta:
            continue
        # Skip detail rows — they're attached via seen_parents below
        if meta.get("parent_field"):
            continue
        ds = meta.get("display_system")
        if not ds or ds not in by_system:
            continue

        label = meta.get("ui_label", field.replace("_", " "))
        txt = _clean_answer(value)
        is_pos = txt.lower() not in NEGATIVE_WORDS

        # Attach detail text if present and meaningful
        detail_text = seen_parents.get(field)
        if detail_text and detail_text.lower() not in {"yes", "true", "y"} | NEGATIVE_WORDS:
            display = f"{label}: {detail_text}"
        else:
            display = f"{label}: {txt}" if is_pos else f"{label}: denied"

        by_system[ds].append((label, display, is_pos))

    return by_system


def generate_template_summary(engine, ros_answers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    skip_fields = set(NON_ROS_FIELDS) | {"_escalation_level"}
    for f, v in s.items():
        if f in skip_fields or not _is_meaningful(v):
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

    # ---- Real ROS block ----
    ros_bank = _build_ros_bank_index(_project_root_from_engine(engine))
    ros_details = _build_ros_block(s, ros_bank, engine.complaint.get("questions_by_id", {}))
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

    # ---- Fixed social/smoking/alcohol concatenation ----
    social_parts = []
    for field in ["occupation", "living_situation", "recent_travel", "occupational_exposures"]:
        val = s.get(field)
        if val and str(val).strip() not in ("", "not_assessed", "unknown"):
            social_parts.append(val)
    social_factors = ", ".join(social_parts) if social_parts else "Not obtained"

    smoking_parts = []
    for field in ["smoking_current", "smoking_past"]:
        val = s.get(field)
        if val and str(val).strip() not in ("", "not_assessed", "unknown"):
            smoking_parts.append(val)
    smoking = ", ".join(smoking_parts) if smoking_parts else "Not obtained"

    alcohol = s.get("alcohol_current")
    if alcohol in (None, "", "not_assessed", "unknown"):
        alcohol = "Not obtained"

    # ---- Gynecologic and immunization history aggregation ----
    gynecologic = s.get("gynecologic_history_other")
    if gynecologic in (None, "", "not_assessed", "unknown"):
        gynecologic = "Not obtained"

    immunization_parts = []
    for field in ["immunization_record_available", "childhood_immunizations_current",
                  "influenza_immunization_recent", "covid_immunization_recent",
                  "pneumococcal_immunization_history", "bcg_immunization_history",
                  "meningococcal_or_hib_immunization_history", "other_relevant_immunization_history"]:
        val = s.get(field)
        if val and str(val).strip() not in ("", "not_assessed", "unknown"):
            immunization_parts.append(val)
    immunization = ", ".join(immunization_parts) if immunization_parts else "Not obtained"

    return {
        "chief_complaint": cn,
        "other_concerns": s.get("secondary_complaints", "None reported"),
        "hpi": _build_hpi(s, cn),
        "ros": ros_summary,
        "ros_details": {k: [{"label": l, "text": t, "is_positive": p} for (l, t, p) in v]
                        for k, v in ros_details.items()},
        "pertinent_positives": positives,
        "pertinent_negatives": negatives,
        "pmh_psh": s.get("past_medical_history", "Not obtained"),
        "past_surgical": s.get("past_surgical_history", "Not obtained"),
        "medications": s.get("current_medications", "Not obtained"),
        "allergies": s.get("allergies", "Not obtained"),
        "social_factors": social_factors,
        "family_history": s.get("family_history", "Not obtained"),
        "smoking": smoking,
        "alcohol": alcohol,
        "gynecologic_history": gynecologic,
        "immunization_history": immunization,
        "missing_clarifications": missing,
        "flags": flags,
        "escalation_level": engine.escalation_level,
        "questions_asked": engine.questions_asked,
        "generated_at": datetime.utcnow().isoformat(),
    }


def ai_summarize(extracted_state: Dict[str, Any], template_summary: Dict[str, Any], model: str = "claude-sonnet-4-20250514") -> str:
    # Build a compact, structured view of everything that was captured, including ROS
    ros_lines = []
    for sys_name, detail in template_summary.get("ros", {}).items():
        if detail and detail != "Not assessed":
            ros_lines.append(f"  {sys_name}: {detail}")

    compact_state = {k: v for k, v in extracted_state.items() if _is_meaningful(v)}
    prompt = (
        "You are a clinical documentation assistant. Write a thorough, factual HPI "
        "paragraph (5-10 sentences) that incorporates EVERY relevant captured finding below. "
        "Do not invent information. Do not omit captured positives. Name the key negatives "
        "(pertinent negatives) at the end in one sentence. If a finding was explicitly denied, "
        "report it as denied. Keep sentences clinical and concise.\n\n"
        f"Chief complaint: {template_summary.get('chief_complaint', 'Unknown')}\n"
        f"Other concerns: {template_summary.get('other_concerns', 'None reported')}\n\n"
        f"Captured state (all fields, structured):\n{json.dumps(compact_state, indent=2)}\n\n"
        f"Pertinent positives: {'; '.join(template_summary.get('pertinent_positives', []))}\n"
        f"Pertinent negatives: {', '.join(template_summary.get('pertinent_negatives', []))}\n"
        f"Red flags: {'; '.join(template_summary.get('flags', ['None']))}\n"
        f"Escalation level: {template_summary.get('escalation_level', 'none')}\n\n"
        + ("Review of systems positives/denials:\n" + "\n".join(ros_lines) + "\n\n" if ros_lines else "")
        + "Write only the HPI paragraph."
    )
    api_key = os.environ.get("ANTHROPIC_API_KEY", "") or _ANTHROPIC_API_KEY
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
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
        return text.strip() or template_summary.get("hpi", "")
    except Exception:
        return template_summary.get("hpi", "AI summarizer unavailable.")


def format_summary_text(summary: Dict[str, Any]) -> str:
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