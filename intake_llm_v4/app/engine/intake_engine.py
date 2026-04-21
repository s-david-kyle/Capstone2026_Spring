"""Deterministic complaint scheduler for the clinical intake application."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.engine.utils import evaluate_condition, is_negative_answer, is_positive_answer, parse_duration_str

PHASE_ORDER = [
    "opening",
    "core_characterize",
    "early_danger_screen",
    "extended_characterize",
    "critical_followup",
    "high_priority_followup",
    "context_and_history",
]

ESCALATION_ORDER = {
    "immediate_alert": 0,
    "urgent_escalation": 1,
    "priority_clinician_review": 2,
    "same_day_clinician_review": 3,
    "none": 4,
}


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_shared() -> Dict[str, Any]:
    """Load the shared contract file."""
    path = os.path.join(project_root(), "complaints_modules", "shared_v2.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"shared_v2.json not found at {path}")
    return load_json(path)


def load_complaint(complaint_id: str) -> Dict[str, Any]:
    """Load a complaint file by id."""
    path = os.path.join(project_root(), "complaints_modules", "complaints", f"{complaint_id}_v2.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No complaint file found for {complaint_id}")
    return load_json(path)


class IntakeEngine:

    # ---- v1.0.0 implicit-parent seeding ---------------------------------
    # When a complaint file contains linker atomics gated on the complaint's
    # root symptom (e.g. cough complaint asks pleuritic_quality gated on
    # $state.cough == yes), we pre-set that parent to "yes" so the linker
    # actually fires. Only applies when the parent field name matches the
    # complaint identity or a declared implicit positive.
    _COMPLAINT_IMPLICIT_PARENTS = {
        "cough":                "cough",
        "headache":             "headache",
        "palpitations":         "palpitations",
        "trauma":               "trauma_present",
        "abdominal_pain":       "abdominal_pain",
        "chest_pain":           "chest_pain",
        "shortness_of_breath":  "shortness_of_breath",
        "back_pain":            "back_pain",
        "joint_pain":           "joint_pain",
        "rash":                 "rash",
        "sore_throat":          "sore_throat",
        "fever":                "fever",
        "vomiting":             "vomiting",
        "loose_stool":          "diarrhea",
        "constipation":         "constipation",
        "dysuria":              "dysuria",
        "hematuria":            "hematuria",
        "weight_loss":          "weight_loss",
        "vaginal_discharge":    "vaginal_discharge",
        "dizziness":            "dizziness",
        "oedema":               "oedema",
        "swelling_or_lump":     "swelling_or_lump",
        "seizure":              "seizure",
        "loss_of_consciousness":"loss_of_consciousness",
        "fatigue":              "fatigue",
    }

    def _seed_complaint_implicits(self) -> None:
        """Pre-set state[parent] = 'yes' for the complaint's implicit parent
        field, so linker atomics with ask_if gates on that field actually fire.
        Idempotent; only sets if state is currently empty for that field."""
        complaint_id = getattr(self, "complaint_id", None) or self.complaint.get("complaint_id","")
        parent = self._COMPLAINT_IMPLICIT_PARENTS.get(complaint_id)
        if parent and self.state.get(parent) in (None, "", "not_assessed"):
            self.state[parent] = "yes"
    # ---------------------------------------------------------------------

    def __init__(self, complaint_data: Dict[str, Any], patient_context: Optional[Dict[str, Any]] = None, shared_data: Optional[Dict[str, Any]] = None):
        self.complaint = complaint_data
        self.patient = patient_context or {}
        self.shared = shared_data or load_shared()
        self.concept_map = self.shared.get("concept_alias_map", {})
        self.ask_if_registry = self.shared.get("ask_if_registry", {})
        self.skip_if_registry = self.shared.get("skip_if_registry", {})

        self.state: Dict[str, Any] = {}
        self.turns: List[Dict[str, Any]] = []
        self.questions_asked = 0
        self.red_flags: List[Dict[str, Any]] = []
        self.completed = False
        self.started_at = datetime.utcnow().isoformat()
        self.escalation_level = "none"

        self.current_profile = "default_profile"
        self._phase_idx = 0
        self._q_idx = 0
        self._detail_queue: List[str] = []
        self._detail_to_parent: Dict[str, str] = {}
        self._answered_concepts = set()
        self._visited_qids = set()

        self._load_questions_and_schedule()
        self._build_detail_map()
        budget = self.complaint.get("question_budget", {}).get("primary_mode", {})
        hard_cap = self.shared.get("session_guardrails", {}).get("session_hard_cap_questions", 55)
        self._max_questions = min(int(budget.get("max_questions", 50)), int(hard_cap))

        # Seed implicit parent so linker atomics fire
        self._seed_complaint_implicits()

    def _load_questions_and_schedule(self) -> None:
        self.questions = self.complaint.get("questions_by_id", {})
        schedule = self.complaint.get("question_schedule", {})
        self.phases = schedule.get("enforced_phase_order", PHASE_ORDER)
        self.profiles = {k: v for k, v in schedule.items() if k.endswith("_profile")}
        self.current_profile_data = self.profiles.get("default_profile", schedule.get("default_profile", {}))

    def _build_detail_map(self) -> None:
        for qid, q in self.questions.items():
            detail_field = q.get("detail_field")
            if detail_field:
                self._detail_to_parent[detail_field] = q.get("field", qid)
            parent_field = q.get("parent_field")
            if parent_field:
                self._detail_to_parent[q.get("field", qid)] = parent_field

    def _update_profile(self) -> None:
        rules = self.complaint.get("question_schedule", {}).get("profile_switch_rules", [])
        for rule in rules:
            trigger = rule.get("trigger")
            if evaluate_condition(trigger, self.state, self.patient):
                action = str(rule.get("action", "")).replace("use ", "").strip()
                if action in self.profiles and action != self.current_profile:
                    self.current_profile = action
                    self.current_profile_data = self.profiles[action]
                return

    # Removed _concept_already_covered method – dedup is now strictly field-based.
    # The skip pipeline uses FIELD_ALREADY_CAPTURED exclusively.

    def _mark_concept_answered(self, q: Dict[str, Any]) -> None:
        cc = q.get("canonical_concept")
        if cc:
            self._answered_concepts.add(cc)
        field = q.get("field")
        if field:
            self._answered_concepts.add(field)

    def _parent_from_ask_if(self, ask_if):
        """Return the parent field name if ask_if is a simple
        {op: field_equals, field_ref: $state.<field>, value: yes} gate that
        declares a linker relationship. Otherwise return None."""
        if not isinstance(ask_if, dict):
            return None
        if ask_if.get("op") != "field_equals":
            return None
        if str(ask_if.get("value","")).lower() != "yes":
            return None
        ref = ask_if.get("field_ref","")
        if isinstance(ref, str) and ref.startswith("$state."):
            return ref[len("$state."):]
        return None

    def _resolve_skip_rule(self, skip_rule: Any, q: Dict[str, Any]) -> bool:
        if isinstance(skip_rule, str):
            if skip_rule == "FIELD_ALREADY_CAPTURED":
                return self.state.get(q["field"]) not in (None, "")
            if skip_rule == "DETAIL_ALREADY_CAPTURED" and q.get("detail_field"):
                return self.state.get(q["detail_field"]) not in (None, "")
            if skip_rule == "PARENT_NEGATIVE":
                pf = q.get("parent_field") or self._detail_to_parent.get(q["field"], q["field"].replace("_details", ""))
                parent_answer = self.state.get(pf)
                if parent_answer is None:
                    return True
                return is_negative_answer(str(parent_answer))
            if skip_rule == "SEVERITY_BELOW_8":
                try:
                    return float(str(self.state.get("severity", "")).split("/", 1)[0]) < 8
                except Exception:
                    return False
            if skip_rule == "SEVERITY_BELOW_7":
                try:
                    return float(str(self.state.get("severity", "")).split("/", 1)[0]) < 7
                except Exception:
                    return False
            if skip_rule == "DURATION_BELOW_4_WEEKS":
                return parse_duration_str(self.state.get("duration", "")) < 4
            if skip_rule == "DURATION_BELOW_2_WEEKS":
                return parse_duration_str(self.state.get("duration", "")) < 2

            rule_def = self.skip_if_registry.get(skip_rule)
            if rule_def:
                return evaluate_condition(rule_def.get("logic"), self.state, {**self.patient, "escalation_level": self.escalation_level}, q)
            return False

        if isinstance(skip_rule, dict):
            return evaluate_condition(skip_rule, self.state, {**self.patient, "escalation_level": self.escalation_level}, q)
        return False

    def _should_skip(self, q: Dict[str, Any]) -> bool:
        # v1.0.0 dedup: skip if field already captured
        if self.state.get(q["field"]) not in (None, ""):
            return True

        for skip_rule in q.get("skip_if", []):
            if self._resolve_skip_rule(skip_rule, q):
                return True

        ask_if = q.get("ask_if")
        if ask_if:
            if isinstance(ask_if, str):
                cond = self.ask_if_registry.get(ask_if, {}).get("logic")
                if cond and not evaluate_condition(cond, self.state, self.patient, q):
                    return True
            elif isinstance(ask_if, dict) and not evaluate_condition(ask_if, self.state, self.patient, q):
                return True

        return False

    def _mkq(self, qid: str, q: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": qid,
            "field": q["field"],
            "text": q.get("text", ""),
            "ui_label": q.get("ui_label", qid),
            "phase": q.get("phase", ""),
            "response_type": q.get("response_type", "SHORT_TEXT"),
            "sensitive_topic": q.get("sensitive_topic", False),
            "compound_question": q.get("compound_question", False),
            "canonical_concept": q.get("canonical_concept", ""),
        }

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        if self.completed:
            return None

        while self._detail_queue:
            qid = self._detail_queue.pop(0)
            q = self.questions.get(qid)
            if q and not self._should_skip(q) and self.questions_asked < self._max_questions:
                self._visited_qids.add(qid)
                return self._mkq(qid, q)

        while self._phase_idx < len(self.phases):
            phase = self.phases[self._phase_idx]
            qids = self.current_profile_data.get(phase, [])
            while self._q_idx < len(qids):
                qid = qids[self._q_idx]
                self._q_idx += 1
                q = self.questions.get(qid)
                if not q or self._should_skip(q):
                    continue
                if self.questions_asked >= self._max_questions:
                    self.completed = True
                    return None
                self._visited_qids.add(qid)
                return self._mkq(qid, q)
            self._phase_idx += 1
            self._q_idx = 0

        self.completed = True
        return None

    def _raise_escalation(self, target: str) -> None:
        if ESCALATION_ORDER.get(target, 99) < ESCALATION_ORDER.get(self.escalation_level, 99):
            self.escalation_level = target
            self.state["_escalation_level"] = target

    def _check_red_flags(self, field: str, answer: Any) -> None:
        patterns = self.complaint.get("derived_red_flag_patterns", {})

        # v2 format: dict of pattern_name -> list of field names (AND-pattern)
        # A pattern fires when the newly answered field is in its list AND
        # all other fields in the list are already positive in state.
        if isinstance(patterns, dict):
            acuity = self.complaint.get("acuity_tier", "medium")
            escalation = {
                "high": "urgent_escalation",
                "medium": "priority_clinician_review",
                "low": "same_day_clinician_review",
            }.get(acuity, "priority_clinician_review")

            for pattern_name, fields in patterns.items():
                if not isinstance(fields, list):
                    continue
                # Only evaluate patterns that include the field just answered
                if field not in fields:
                    continue
                # Current answer must be positive
                if not is_positive_answer(answer):
                    continue
                # All other fields in the pattern must already be positive in state
                all_positive = all(
                    is_positive_answer(str(self.state.get(f, "")))
                    for f in fields if f != field
                )
                if all_positive:
                    entry = {
                        "pattern": pattern_name,
                        "trigger_field": field,
                        "fields": fields,
                        "value": answer,
                        "escalation_level": escalation,
                    }
                    if entry not in self.red_flags:
                        self.red_flags.append(entry)
                    self._raise_escalation(escalation)
            return

        # Legacy format: list of dicts with trigger_field/value/escalation_level
        if isinstance(patterns, list):
            for pattern in patterns:
                if not isinstance(pattern, dict):
                    continue
                trig = pattern.get("trigger_field")
                if trig and trig != field:
                    continue
                expected = pattern.get("value")
                matched = False
                if isinstance(expected, bool):
                    matched = (is_positive_answer(answer) if expected else is_negative_answer(answer))
                elif expected is None:
                    matched = is_positive_answer(answer)
                else:
                    matched = str(answer).strip().lower() == str(expected).strip().lower()
                if matched:
                    entry = {
                        "pattern": pattern.get("pattern", field),
                        "trigger_field": field,
                        "value": answer,
                        "escalation_level": pattern.get("escalation_level", "priority_clinician_review"),
                    }
                    if entry not in self.red_flags:
                        self.red_flags.append(entry)
                    self._raise_escalation(entry["escalation_level"])

    def record_answer(self, qid: str, field: str, answer: Any, phase: str) -> Dict[str, Any]:
        self.state[field] = answer
        self.questions_asked += 1

        turn = {
            "turn_number": len(self.turns) + 1,
            "question_id": qid,
            "field": field,
            "phase": phase,
            "question_text": self.questions.get(qid, {}).get("text", qid),
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat(),
            "skipped": False,
            "extracted_bonus_fields": {},
        }
        self.turns.append(turn)

        q_def = self.questions.get(qid, {})
        self._mark_concept_answered(q_def)

        # --- Parent auto-set (v1.0.0 linker behaviour) ---
        # When a qualifier atomic is answered positive, its parent atomic is
        # implicitly positive too. Parent relationship is declared via
        # ask_if: {op: field_equals, field_ref: $state.<parent>, value: yes}.
        # This guarantees dedup correctness: answering `pleuritic_chest_pain=yes`
        # also sets `chest_pain=yes`, so a later generic ROS "any chest pain?"
        # is suppressed by the "if state[field] set, skip" rule.
        if is_positive_answer(answer):
            parent_field = self._parent_from_ask_if(q_def.get("ask_if"))
            if parent_field and self.state.get(parent_field) in (None, ""):
                self.state[parent_field] = "yes"
                turn.setdefault("extracted_bonus_fields", {})[parent_field] = "yes"

        if is_positive_answer(answer):
            self._check_red_flags(field, answer)

        if q_def.get("capture_detail_if_positive") and q_def.get("detail_field") and is_positive_answer(answer):
            detail = str(answer).strip()
            low = detail.lower()
            for pfx in ("yes -", "yes,", "yes.", "yeah -", "yeah,", "yep -", "yep,"):
                if low.startswith(pfx):
                    detail = detail[len(pfx):].strip()
                    break
            if detail.lower() not in ("yes", "yeah", "yep", "y", ""):
                self.state[q_def["detail_field"]] = detail
                turn["extracted_bonus_fields"][q_def["detail_field"]] = detail

        if is_positive_answer(answer):
            for fup_id in q_def.get("if_positive_ask", []):
                if fup_id in self.questions and fup_id not in self._detail_queue:
                    fup_field = self.questions[fup_id].get("field", fup_id)
                    if self.state.get(fup_field) is None:
                        self._detail_queue.append(fup_id)

        self._update_profile()
        return turn

    def skip_question(self, qid: str, field: str, phase: str) -> Dict[str, Any]:
        self.state[field] = "not_assessed"
        self.questions_asked += 1
        turn = {
            "turn_number": len(self.turns) + 1,
            "question_id": qid,
            "field": field,
            "phase": phase,
            "question_text": self.questions.get(qid, {}).get("text", qid),
            "answer": "not_assessed",
            "timestamp": datetime.utcnow().isoformat(),
            "skipped": True,
        }
        self.turns.append(turn)
        return turn

    def get_progress(self) -> Dict[str, Any]:
        total = max(sum(len(v) for v in self.current_profile_data.values()), 1)
        completion = min(round((self.questions_asked / total) * 100, 1), 100.0)
        return {
            "questions_asked": self.questions_asked,
            "estimated_total": total,
            "completion_percent": completion,
            "current_profile": self.current_profile,
            "phase": self.phases[min(self._phase_idx, len(self.phases)-1)] if self.phases else "",
            "completed": self.completed,
            "escalation_level": self.escalation_level,
        }