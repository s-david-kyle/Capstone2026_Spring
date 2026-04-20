"""Shared utility helpers for the deterministic clinical intake runtime."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

_POS = frozenset(["yes", "yeah", "yep", "yea", "y", "positive", "present", "true", "correct", "sure", "definitely"])
_NEG = frozenset(["no", "nope", "nah", "n", "none", "nil", "nothing", "negative", "denied", "never", "not at all", "false", "neither", "not really", "n/a"])


def normalize_boolean(raw: Any) -> Optional[bool]:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    low = str(raw).strip().lower()
    if low in _POS:
        return True
    if low in _NEG:
        return False
    for pw in ("yes ", "yeah ", "yep "):
        if low.startswith(pw):
            return True
    for nw in ("no ", "no,", "no.", "nope ", "none ", "not "):
        if low.startswith(nw):
            return False
    return None


def is_positive_answer(raw: Any) -> bool:
    b = normalize_boolean(raw)
    if b is False:
        return False
    if b is True:
        return True
    low = str(raw).strip().lower()
    return low not in ("", "unknown", "not_assessed", "not assessed", "n/a", "none")


def is_negative_answer(raw: Any) -> bool:
    return normalize_boolean(raw) is False


def parse_duration_str(dur_str: Any) -> float:
    """Return an approximate duration in weeks."""
    if not dur_str:
        return 0.0
    low = str(dur_str).lower().strip()
    if re.search(r"year", low):
        m = re.search(r"(\d+(?:\.\d+)?)", low)
        return float(m.group(1)) * 52 if m else 52
    if re.search(r"month", low):
        m = re.search(r"(\d+(?:\.\d+)?)", low)
        return float(m.group(1)) * 4 if m else 4
    m = re.search(r"(\d+(?:\.\d+)?)\s*(week|day|hour|minute)", low)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        if unit == "week":
            return num
        if unit == "day":
            return num / 7
        if unit == "hour":
            return num / 168
        if unit == "minute":
            return num / 10080
    return 0.0


def _resolve_ref(ref: Any, state: Dict[str, Any], patient: Dict[str, Any], question: Optional[Dict[str, Any]] = None) -> Any:
    if not isinstance(ref, str):
        return ref
    if ref.startswith("$question.") and question:
        key = ref.split(".", 1)[1]
        return question.get(key)
    if ref.startswith("$patient."):
        key = ref.split(".", 1)[1]
        return patient.get(key)
    if ref in state:
        return state.get(ref)
    return ref


def _to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if "/" in text:
        text = text.split("/", 1)[0]
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None


def evaluate_condition(cond: Any, state: Dict[str, Any], patient: Dict[str, Any], question: Optional[Dict[str, Any]] = None) -> bool:
    if cond is None:
        return True
    if isinstance(cond, str):
        low = cond.strip().lower()
        if low in ("true", "always_true", "always true"):
            return True
        if low in ("false",):
            return False
        return True

    op = cond.get("op")
    if op == "always_true":
        return True

    if op == "field_equals":
        return _resolve_ref(cond.get("field_ref"), state, patient, question) == cond.get("value")
    if op == "field_not_equals":
        return _resolve_ref(cond.get("field_ref"), state, patient, question) != cond.get("value")

    if op in ("field_gte", "field_above", "field_below", "field_exists_and_below"):
        value = _to_number(state.get(_resolve_ref(cond.get("field_ref"), state, patient, question)))
        threshold = _to_number(cond.get("value", cond.get("threshold")))
        if value is None or threshold is None:
            return False
        if op == "field_gte":
            return value >= threshold
        if op == "field_above":
            return value > threshold
        return value < threshold

    if op == "field_exists_and_not_null":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        if key in state:
            val = state.get(key)
            return val is not None and str(val).strip() != ""
        return False

    if op == "field_contains":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return str(cond.get("value", "")).lower() in str(state.get(key, "")).lower()

    if op == "field_text_contains_any":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        val = str(state.get(key, "")).lower()
        return any(str(v).lower() in val for v in cond.get("value", []))

    if op == "duration_gte":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return parse_duration_str(state.get(key, "")) >= float(cond.get("value", 0))

    if op == "duration_below_threshold":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        threshold = cond.get("threshold_value", cond.get("value", 0))
        return parse_duration_str(state.get(key, "")) < float(threshold)

    if op == "field_in_known_diagnoses":
        hay = str(state.get("PastMedicalHistory", "")).lower()
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return str(key).lower() in hay

    if op == "clinician_exclusion_flag_set":
        return False

    if op == "field_in_shared_session_state":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return key in state

    if op == "escalation_level_gte":
        order = {
            "immediate_alert": 0,
            "urgent_escalation": 1,
            "priority_clinician_review": 2,
            "same_day_clinician_review": 3,
            "none": 4,
        }
        current = state.get("_escalation_level", patient.get("escalation_level", "none"))
        return order.get(str(current), 4) <= order.get(cond.get("level", "none"), 4)

    if op == "system_screen_negative":
        return False

    if op == "entity_extracted_positive":
        key = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return is_positive_answer(state.get(key))

    if op == "parent_field_equals":
        parent_key = None
        if question:
            parent_key = question.get("parent_field") or question.get("field", "").replace("_details", "")
        parent_val = state.get(parent_key)
        expected = cond.get("value")
        nb = normalize_boolean(parent_val)
        if isinstance(expected, bool):
            return nb is expected
        return parent_val == expected

    if op == "any":
        return any(evaluate_condition(c, state, patient, question) for c in cond.get("conditions", []))
    if op == "all":
        return all(evaluate_condition(c, state, patient, question) for c in cond.get("conditions", []))

    # backward compatible custom shorthand sometimes found in shared files
    # e.g. { "field": "PatientSex", "operator": "eq", "value": "female" }
    if "operator" in cond and "field" in cond:
        field = cond["field"]
        operator = cond["operator"]
        value = cond.get("value")

        # Patient-context keys (sex, age) are stored in the `patient` dict, not
        # in `state`. The engine passes patient = {"age": 35, "sex": "female"},
        # but shared gates reference "PatientSex" / "PatientAge". Normalize both
        # directions and look in patient first, then state.
        patient_key_aliases = {
            "PatientSex": "sex",
            "patient_sex": "sex",
            "Sex": "sex",
            "PatientAge": "age",
            "patient_age": "age",
            "Age": "age",
        }
        lookup_key = patient_key_aliases.get(field, field)
        if lookup_key in patient:
            cur = patient.get(lookup_key)
        elif field in patient:
            cur = patient.get(field)
        else:
            cur = state.get(field)

        if operator in ("eq", "equals"):
            if isinstance(cur, str) and isinstance(value, str):
                return cur.strip().lower() == value.strip().lower()
            return cur == value
        if operator in ("neq", "not_equals"):
            if isinstance(cur, str) and isinstance(value, str):
                return cur.strip().lower() != value.strip().lower()
            return cur != value
        if operator == "in":
            if isinstance(cur, str):
                values = [str(v).strip().lower() for v in (value or [])]
                return cur.strip().lower() in values
            return cur in (value or [])
        if operator == "not_in":
            if isinstance(cur, str):
                values = [str(v).strip().lower() for v in (value or [])]
                return cur.strip().lower() not in values
            return cur not in (value or [])
        if operator == "not_empty":
            return cur not in (None, "", [])
        if operator == "gte":
            try:
                return float(cur) >= float(value)
            except (TypeError, ValueError):
                return False
        if operator == "lte":
            try:
                return float(cur) <= float(value)
            except (TypeError, ValueError):
                return False
    return True
