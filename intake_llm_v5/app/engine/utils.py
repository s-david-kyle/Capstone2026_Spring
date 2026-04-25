"""Shared utility helpers for the deterministic clinical intake runtime."""
from __future__ import annotations

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



def is_episodic_pattern(raw: Any) -> bool:
    """Return True when a free-text pattern answer means symptoms come and go.

    Used to decide whether episode_duration should be asked. Answers such as
    "constant", "continuous", "all through", or "always there" should not trigger
    episode-duration questions.
    """
    if raw is None:
        return False
    low = str(raw).strip().lower()
    if not low or low in ("unknown", "not_assessed", "not assessed", "n/a"):
        return False

    constant_markers = (
        "constant", "constantly", "continuous", "continuously", "always",
        "all the time", "all through", "there all through", "always there",
        "does not stop", "doesn't stop", "never stops", "persistent",
        "ongoing", "steady", "unchanged", "throughout", "no break",
        "no breaks", "not episodic", "not intermittent"
    )
    episodic_markers = (
        "comes and goes", "come and go", "coming and going", "on and off",
        "off and on", "intermittent", "episodic", "episodes", "episode",
        "attacks", "attack", "bouts", "bout", "waves", "wave",
        "comes", "goes", "sometimes", "periodic", "periodically", "recurs",
        "recurrent", "flare", "flares"
    )

    if any(marker in low for marker in episodic_markers):
        return True
    if any(marker in low for marker in constant_markers):
        return False
    return False


def is_constant_pattern(raw: Any) -> bool:
    """Return True when a pattern answer clearly means constant/non-episodic."""
    if raw is None:
        return False
    low = str(raw).strip().lower()
    return bool(low) and not is_episodic_pattern(low) and any(
        marker in low for marker in (
            "constant", "constantly", "continuous", "continuously", "always",
            "all the time", "all through", "there all through", "always there",
            "does not stop", "doesn't stop", "never stops", "persistent",
            "ongoing", "steady", "throughout", "no break", "no breaks"
        )
    )


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
    if ref.startswith("$state."):
        key = ref[len("$state."):]
        return state.get(key)
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


def _matches_expected(actual: Any, expected: Any) -> bool:
    """
    Compare values with boolean-aware semantics so detail-text positives like
    'bright red blood' still satisfy conditions that expect 'yes'.
    """
    actual_bool = normalize_boolean(actual)
    expected_bool = normalize_boolean(expected)

    if expected_bool is not None:
        return actual_bool is expected_bool

    if isinstance(actual, str) and isinstance(expected, str):
        return actual.strip().lower() == expected.strip().lower()
    return actual == expected



def _evaluate_condition_string(cond: str, state: Dict[str, Any], patient: Dict[str, Any], question: Optional[Dict[str, Any]] = None) -> bool:
    """Evaluate simple shared registry condition strings safely.

    Supports the limited expression language used by shared_v2.json: ==, !=,
    >=, <=, >, <, IN [...], CONTAINS, AND, OR, parentheses, true/false, and
    field names from patient/state/question.
    """
    import re
    raw = (cond or "").strip()
    low = raw.lower()
    if low in ("", "true", "always_true", "always true"):
        return True
    if low in ("false", "never"):
        return False

    ctx: Dict[str, Any] = {}
    ctx.update(state or {})
    ctx.update(patient or {})
    if question:
        ctx.update({f"question_{k}": v for k, v in question.items() if isinstance(k, str)})
    if "duration_weeks" not in ctx:
        ctx["duration_weeks"] = parse_duration_str((state or {}).get("duration") or (state or {}).get("timeframe") or "")
    if "last_menstrual_period_exists" not in ctx:
        ctx["last_menstrual_period_exists"] = bool((state or {}).get("lmp") or (state or {}).get("last_menstrual_period"))

    expr = raw
    expr = re.sub(r"\bAND\b", "and", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bOR\b", "or", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\btrue\b", "True", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bfalse\b", "False", expr, flags=re.IGNORECASE)
    expr = re.sub(r"(\b[A-Za-z_][A-Za-z0-9_]*\b)\s+IN\s+(\[[^\]]*\])", r"\1 in \2", expr, flags=re.IGNORECASE)
    expr = re.sub(r"(\b[A-Za-z_][A-Za-z0-9_]*\b)\s+CONTAINS\s+('[^']*'|\"[^\"]*\")", r"contains(\1, \2)", expr, flags=re.IGNORECASE)

    identifiers = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expr))
    reserved = {"and", "or", "not", "in", "True", "False", "contains"}
    safe_locals: Dict[str, Any] = {name: ctx.get(name) for name in identifiers if name not in reserved}
    safe_locals["contains"] = lambda hay, needle: str(needle).lower() in str(hay or "").lower()
    try:
        return bool(eval(expr, {"__builtins__": {}}, safe_locals))
    except Exception:
        return False

def evaluate_condition(cond: Any, state: Dict[str, Any], patient: Dict[str, Any], question: Optional[Dict[str, Any]] = None) -> bool:
    if cond is None:
        return True
    if isinstance(cond, str):
        return _evaluate_condition_string(cond, state, patient, question)

    op = cond.get("op")
    if op == "always_true":
        return True

    if op == "field_equals":
        actual = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return _matches_expected(actual, cond.get("value"))
    if op == "field_not_equals":
        actual = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return not _matches_expected(actual, cond.get("value"))
    if op == "field_equals_any":
        actual = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return any(_matches_expected(actual, v) for v in cond.get("value", []))
    if op == "field_not_equals_any":
        actual = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return all(not _matches_expected(actual, v) for v in cond.get("value", []))

    if op in ("field_gte", "field_above", "field_below", "field_exists_and_below"):
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        value = _to_number(val)
        threshold = _to_number(cond.get("value", cond.get("threshold")))
        if value is None or threshold is None:
            return False
        if op == "field_gte":
            return value >= threshold
        if op == "field_above":
            return value > threshold
        return value < threshold

    if op == "field_exists_and_not_null":
        ref = cond.get("field_ref")
        key = ref[len("$state."):] if isinstance(ref, str) and ref.startswith("$state.") else ref
        if key in state:
            val = state.get(key)
            return val is not None and str(val).strip() != ""
        return False

    if op == "field_not_exists_or_null":
        ref = cond.get("field_ref")
        key = ref[len("$state."):] if isinstance(ref, str) and ref.startswith("$state.") else ref
        if key not in state:
            return True
        val = state.get(key)
        return val is None or str(val).strip() == ""

    if op in ("field_contains", "field_text_contains"):
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return str(cond.get("value", "")).lower() in str(val).lower()

    if op == "field_text_contains_any":
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        val_str = str(val).lower()
        return any(str(v).lower() in val_str for v in cond.get("value", []))

    if op == "duration_gte":
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return parse_duration_str(val) >= float(cond.get("value", 0))

    if op == "duration_below_threshold":
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        threshold = cond.get("threshold_value", cond.get("value", 0))
        return parse_duration_str(val) < float(threshold)

    if op == "field_in_known_diagnoses":
        hay = str(state.get("past_medical_history", "")).lower()
        term = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return str(term).lower() in hay

    if op == "clinician_exclusion_flag_set":
        return False

    if op == "field_in_shared_session_state":
        ref = cond.get("field_ref")
        key = ref[len("$state."):] if isinstance(ref, str) and ref.startswith("$state.") else ref
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
        val = _resolve_ref(cond.get("field_ref"), state, patient, question)
        return is_positive_answer(val)

    if op == "parent_field_equals":
        parent_key = None
        if question:
            parent_key = question.get("parent_field") or question.get("field", "").replace("_details", "")
        parent_val = state.get(parent_key)
        expected = cond.get("value")
        nb = normalize_boolean(parent_val)
        if isinstance(expected, bool):
            return nb is expected
        return _matches_expected(parent_val, expected)

    if op == "any":
        return any(evaluate_condition(c, state, patient, question) for c in cond.get("conditions", []))
    if op == "all":
        return all(evaluate_condition(c, state, patient, question) for c in cond.get("conditions", []))

    if "operator" in cond and "field" in cond:
        field = cond["field"]
        operator = cond["operator"]
        value = cond.get("value")

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
            return _matches_expected(cur, value)
        if operator in ("neq", "not_equals"):
            return not _matches_expected(cur, value)
        if operator == "in":
            return any(_matches_expected(cur, v) for v in (value or []))
        if operator == "not_in":
            return all(not _matches_expected(cur, v) for v in (value or []))
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

    return False


def is_meaningful_capture(value: Any) -> bool:
    """True when a state value means the concept has already been asked/captured.

    Both positive and negative answers count as covered for deduplication, because
    the goal is to avoid re-asking the same symptom family. Values such as
    not_assessed/unknown do not count as covered.
    """
    return value not in (None, "", "not_assessed", "not assessed", "unknown")


def get_question_dedup_families(question: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> set:
    """Return ROS-owned dedup families declared on a question.

    The ROS bank owns the family names (for example ros:vomiting). Complaint and
    module questions reference those families so that primary, secondary, module,
    and ROS phases can all suppress repeated parent symptom questions.
    """
    out = set()
    families = question.get("dedup_families")
    if isinstance(families, list):
        out.update(str(x) for x in families if x)
    family = question.get("dedup_family")
    if family:
        out.add(str(family))
    field = question.get("field")
    canonical = question.get("canonical_concept")
    if shared:
        fmap = shared.get("dedup_family_by_field", {})
        if field in fmap:
            out.add(str(fmap[field]))
        if canonical in fmap:
            out.add(str(fmap[canonical]))
    return out


def get_state_dedup_families(state: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> set:
    """Compute covered ROS-owned dedup families from the current session state."""
    covered = set()
    if not shared:
        return covered
    fmap = shared.get("dedup_family_by_field", {})
    for field, value in state.items():
        if not is_meaningful_capture(value):
            continue
        family = fmap.get(field)
        if family:
            covered.add(str(family))
    return covered




def _reserved_state_list(state: Dict[str, Any], key: str) -> list:
    """Return a mutable reserved metadata list on session state."""
    current = state.get(key)
    if isinstance(current, list):
        return current
    if isinstance(current, set):
        current = list(current)
    elif current in (None, "", "not_assessed", "unknown"):
        current = []
    else:
        current = [current]
    state[key] = current
    return current


def get_question_code(question: Dict[str, Any]) -> str:
    """Return the stable question code if present."""
    return str(question.get("code") or "").strip()


def code_already_captured(question: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """True when this exact stable question code was already captured.

    This is especially important for primary -> secondary complaint dedup. The
    secondary complaint should not repeat an exact question/code, but it may still
    ask unasked qualifiers or red-flag subquestions in the same ROS family.
    """
    code = get_question_code(question)
    if not code:
        return False
    captured_codes = set(str(x) for x in state.get("_captured_question_codes", []) if x)
    return code in captured_codes


def mark_question_metadata(state: Dict[str, Any], question: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> None:
    """Record hidden field/code/family metadata for future dedup checks.

    The hidden keys are prefixed with '_' so summary rendering can ignore them.
    """
    field = question.get("field")
    if field:
        fields = _reserved_state_list(state, "_captured_fields")
        if field not in fields:
            fields.append(field)

    code = get_question_code(question)
    if code:
        codes = _reserved_state_list(state, "_captured_question_codes")
        if code not in codes:
            codes.append(code)

    families = sorted(get_question_dedup_families(question, shared))
    if families:
        all_families = _reserved_state_list(state, "_covered_dedup_families")
        for family in families:
            if family not in all_families:
                all_families.append(family)

        if question.get("question_role") == "parent_symptom":
            parent_families = _reserved_state_list(state, "_covered_parent_symptom_families")
            for family in families:
                if family not in parent_families:
                    parent_families.append(family)


def secondary_parent_family_covered(question: Dict[str, Any], state: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> bool:
    """True only when a parent symptom question repeats an already-covered family.

    Use this for complaint and secondary-complaint scheduling. It prevents asking
    generic parent questions twice but still allows useful unasked qualifiers and
    red flags in a secondary complaint.
    """
    if question.get("question_role") != "parent_symptom":
        return False
    q_families = get_question_dedup_families(question, shared)
    if not q_families:
        return False
    covered = set(str(x) for x in state.get("_covered_dedup_families", []) if x)
    covered.update(get_state_dedup_families(state, shared))
    return bool(q_families & covered)


def ros_family_covered(question: Dict[str, Any], state: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> bool:
    """True when a ROS question's family was already covered anywhere earlier."""
    q_families = get_question_dedup_families(question, shared)
    if not q_families:
        return False
    covered = set(str(x) for x in state.get("_covered_dedup_families", []) if x)
    covered.update(get_state_dedup_families(state, shared))
    return bool(q_families & covered)

def dedup_family_covered(question: Dict[str, Any], state: Dict[str, Any], shared: Optional[Dict[str, Any]] = None) -> bool:
    """Backward-compatible dedup check.

    Complaint/secondary flows only use the family to suppress repeated parent
    symptoms. ROS questions use stricter family dedup because ROS runs after HPI
    and modules and should not re-ask any already-covered ROS family.
    """
    role = question.get("question_role", "")
    if role == "ros_question":
        return ros_family_covered(question, state, shared)
    return secondary_parent_family_covered(question, state, shared)
