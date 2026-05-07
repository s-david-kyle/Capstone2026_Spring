"""Deterministic complaint scheduler for the clinical intake application."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.engine.utils import (
    evaluate_condition,
    is_negative_answer,
    is_positive_answer,
    is_episodic_pattern,
    parse_duration_str,
    dedup_family_covered,
    code_already_captured,
    mark_question_metadata,
    get_question_dedup_families,
)

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
    """
    Load a complaint file by id.

    Supports both final filenames:
      complaints/<complaint_id>.json
    and older legacy filenames:
      complaints/<complaint_id>_v2.json
    """
    complaints_dir = os.path.join(project_root(), "complaints_modules", "complaints")
    candidate_paths = [
        os.path.join(complaints_dir, f"{complaint_id}.json"),
        os.path.join(complaints_dir, f"{complaint_id}_v2.json"),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return load_json(path)
    raise FileNotFoundError(f"No complaint file found for {complaint_id}")


class IntakeEngine:
    def __init__(
        self,
        complaint_data: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None,
        shared_data: Optional[Dict[str, Any]] = None,
    ):
        self.complaint = complaint_data
        self.patient = patient_context or {}
        self.patient.setdefault("primary_complaint", complaint_data.get("complaint_id", ""))
        self.shared = shared_data or load_shared()
        self.concept_map = self.shared.get("concept_alias_map", {})
        self.ask_if_registry = self.shared.get("ask_if_registry", {})
        self.skip_if_registry = self.shared.get("skip_if_registry", {})
        self.escalation_rules = self._build_escalation_rule_map()
        self.sensitive_concept_list = self.shared.get("sensitive_concept_list", [])

        self.state: Dict[str, Any] = {}
        self.state["primary_complaint"] = self.complaint.get("complaint_id", "")
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

        self._check_eligibility()
        self._load_questions_and_schedule()
        self._build_detail_map()
        budget = self.complaint.get("question_budget", {}).get("primary_mode", {})
        hard_cap = self.shared.get("session_guardrails", {}).get("session_hard_cap_questions", 55)
        self._max_questions = min(int(budget.get("max_questions", 50)), int(hard_cap))

        self._apply_opening_state_note()

    def _check_eligibility(self) -> None:
        """Enforce complaint eligibility rules inside the engine as an extra safeguard."""
        eligibility = self.complaint.get("eligibility", {}) or {}
        if not eligibility:
            return

        allowed_sexes = [str(x).lower() for x in eligibility.get("allowed_patient_sex", [])]
        if not allowed_sexes:
            sex_required = str(eligibility.get("sex_required", "") or "").strip().lower()
            if sex_required:
                allowed_sexes = [sex_required]

        patient_sex = str(self.patient.get("sex", "") or "").strip().lower()
        if allowed_sexes and patient_sex not in allowed_sexes:
            raise ValueError(
                eligibility.get(
                    "message",
                    f"Complaint {self.complaint.get('complaint_id')} not eligible for this patient sex.",
                )
            )

    def _build_escalation_rule_map(self) -> Dict[str, Dict[str, Any]]:
        rules = self.shared.get("escalation_rules", [])
        if isinstance(rules, dict):
            return rules
        if isinstance(rules, list):
            return {
                str(rule.get("name", f"rule_{idx}")): rule
                for idx, rule in enumerate(rules)
                if isinstance(rule, dict) and rule.get("name")
            }
        return {}

    def _apply_opening_state_note(self) -> None:
        """
        Prefer complaint-provided opening_state_note over hardcoded complaint maps.

        Expected note pattern:
          Selecting this complaint should set state['headache'] = 'yes' before questioning begins.
        """
        note = str(self.complaint.get("opening_state_note", "") or "").strip()
        if not note:
            return

        match = re.search(r"state\[['\"]([^'\"]+)['\"]\]\s*=\s*['\"]([^'\"]+)['\"]", note)
        if not match:
            return

        field_name, field_value = match.group(1), match.group(2)
        if self.state.get(field_name) in (None, "", "not_assessed"):
            self.state[field_name] = field_value

    def _load_questions_and_schedule(self) -> None:
        """
        Support both:
        1) legacy complaint schedule with profile objects
        2) rebuilt complaint contract with:
             - question_schedule: [phase1, phase2, ...]
             - question_phase_map: {phase1: [...], ...}
        """
        self.questions = self.complaint.get("questions_by_id", {})

        if isinstance(self.complaint.get("question_phase_map"), dict) and isinstance(
            self.complaint.get("question_schedule"), list
        ):
            self.phases = self.complaint.get("question_schedule", [])
            self.profiles = {"default_profile": self.complaint.get("question_phase_map", {})}
            self.current_profile = "default_profile"
            self.current_profile_data = self.complaint.get("question_phase_map", {})
            return

        schedule = self.complaint.get("question_schedule", {})
        self.phases = schedule.get("enforced_phase_order", PHASE_ORDER)
        self.profiles = {k: v for k, v in schedule.items() if k.endswith("_profile")}
        self.current_profile_data = self.profiles.get(
            "default_profile", schedule.get("default_profile", {})
        )

    def _build_detail_map(self) -> None:
        for qid, q in self.questions.items():
            detail_field = q.get("detail_field")
            if detail_field:
                self._detail_to_parent[detail_field] = q.get("field", qid)
            parent_field = q.get("parent_field")
            if parent_field:
                self._detail_to_parent[q.get("field", qid)] = parent_field

    def _update_profile(self) -> None:
        if isinstance(self.complaint.get("question_schedule"), list):
            return

        rules = self.complaint.get("question_schedule", {}).get("profile_switch_rules", [])
        for rule in rules:
            trigger = rule.get("trigger")
            if evaluate_condition(trigger, self.state, self.patient):
                action = str(rule.get("action", "")).replace("use ", "").strip()
                if action in self.profiles and action != self.current_profile:
                    self.current_profile = action
                    self.current_profile_data = self.profiles[action]
                return

    def _concept_already_covered(self, canonical_concept: str) -> bool:
        if not canonical_concept:
            return False
        return canonical_concept in self._answered_concepts

    def _mark_concept_answered(self, q: Dict[str, Any]) -> None:
        mark_question_metadata(self.state, q, self.shared)
        cc = q.get("canonical_concept")
        if cc:
            self._answered_concepts.add(cc)
        field = q.get("field")
        if field:
            self._answered_concepts.add(field)
        for family in get_question_dedup_families(q, self.shared):
            self._answered_concepts.add(family)

    def _parent_from_ask_if(self, ask_if):
        if not isinstance(ask_if, dict):
            return None
        if ask_if.get("op") != "field_equals":
            return None
        if str(ask_if.get("value", "")).lower() != "yes":
            return None
        ref = ask_if.get("field_ref", "")
        if isinstance(ref, str) and ref.startswith("$state."):
            return ref[len("$state.") :]
        return None

    def _resolve_skip_rule(self, skip_rule: Any, q: Dict[str, Any]) -> bool:
        if isinstance(skip_rule, str):
            if skip_rule == "FIELD_ALREADY_CAPTURED":
                return self.state.get(q["field"]) not in (None, "")
            if skip_rule == "DETAIL_ALREADY_CAPTURED" and q.get("detail_field"):
                return self.state.get(q["detail_field"]) not in (None, "")
            if skip_rule == "PARENT_NEGATIVE":
                pf = q.get("parent_field") or self._detail_to_parent.get(
                    q["field"], q["field"].replace("_details", "")
                )
                parent_answer = self.state.get(pf)
                if parent_answer is None:
                    return True
                # Special handling for pattern field: treat "constant" as negative
                if pf == "pattern" and isinstance(parent_answer, str):
                    low = parent_answer.lower()
                    if low in ("constant", "always", "continuous", "all the time"):
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
            if skip_rule == "PATTERN_NOT_EPISODIC":
                return not is_episodic_pattern(self.state.get(q.get("parent_field") or "pattern"))

            rule_def = self.skip_if_registry.get(skip_rule)
            if rule_def:
                return evaluate_condition(
                    rule_def.get("logic", rule_def.get("condition")),
                    self.state,
                    {**self.patient, "escalation_level": self.escalation_level},
                    q,
                )
            return False

        if isinstance(skip_rule, dict):
            return evaluate_condition(
                skip_rule,
                self.state,
                {**self.patient, "escalation_level": self.escalation_level},
                q,
            )
        return False

    def _should_skip(self, q: Dict[str, Any]) -> bool:
        if self.state.get(q["field"]) not in (None, ""):
            return True

        if code_already_captured(q, self.state):
            return True

        if dedup_family_covered(q, self.state, self.shared):
            return True

        if not q.get("parent_field") and self._concept_already_covered(q.get("canonical_concept", "")):
            return True

        for rule in (q.get("skip_if") or []) + (q.get("skip_conditions") or []):
            if self._resolve_skip_rule(rule, q):
                return True

        ask_if = q.get("ask_if")
        if ask_if:
            if isinstance(ask_if, str):
                cond = self.ask_if_registry.get(ask_if, {}).get("logic")
                if cond and not evaluate_condition(cond, self.state, self.patient, q):
                    return True
            elif isinstance(ask_if, dict) and not evaluate_condition(
                ask_if, self.state, self.patient, q
            ):
                return True

        return False

    def _mkq(self, qid: str, q: Dict[str, Any], phase: Optional[str] = None) -> Dict[str, Any]:
        # Central sensitive topic enforcement
        sensitive = q.get("sensitive_topic", False)
        if not sensitive:
            field = q.get("field", "")
            if field in self.sensitive_concept_list:
                sensitive = True

        return {
            "id": qid,
            "field": q["field"],
            "code": q.get("code", ""),
            "text": q.get("text", ""),
            "ui_label": q.get("ui_label", qid),
            "phase": phase if phase is not None else q.get("phase", ""),
            "response_type": q.get("response_type", "SHORT_TEXT"),
            "sensitive_topic": sensitive,
            "compound_question": q.get("compound_question", False),
            "canonical_concept": q.get("canonical_concept", ""),
            "dedup_family": q.get("dedup_family"),
            "dedup_families": q.get("dedup_families", []),
            "question_role": q.get("question_role", "qualifier"),
        }

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        if self.completed:
            return None

        while self._detail_queue:
            qid = self._detail_queue.pop(0)
            q = self.questions.get(qid)
            current_phase = self.phases[self._phase_idx] if self._phase_idx < len(self.phases) else ""
            if q and not self._should_skip(q) and self.questions_asked < self._max_questions:
                self._visited_qids.add(qid)
                return self._mkq(qid, q, current_phase)

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
                return self._mkq(qid, q, phase)
            self._phase_idx += 1
            self._q_idx = 0

        self.completed = True
        return None

    def peek_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Return the question that would be asked next WITHOUT advancing any state.
        """
        if self.completed:
            return None

        if self._detail_queue:
            qid = self._detail_queue[0]
            q = self.questions.get(qid)
            current_phase = self.phases[self._phase_idx] if self._phase_idx < len(self.phases) else ""
            if q and not self._should_skip(q) and self.questions_asked < self._max_questions:
                return self._mkq(qid, q, current_phase)

        phase_idx = self._phase_idx
        q_idx = self._q_idx

        while phase_idx < len(self.phases):
            phase = self.phases[phase_idx]
            qids = self.current_profile_data.get(phase, [])
            while q_idx < len(qids):
                qid = qids[q_idx]
                q = self.questions.get(qid)
                if q and not self._should_skip(q):
                    if self.questions_asked < self._max_questions:
                        return self._mkq(qid, q, phase)
                    return None
                q_idx += 1
            phase_idx += 1
            q_idx = 0

        return None

    def _raise_escalation(self, target: str) -> None:
        if ESCALATION_ORDER.get(target, 99) < ESCALATION_ORDER.get(self.escalation_level, 99):
            self.escalation_level = target
            self.state["_escalation_level"] = target

    def _record_red_flag(
        self,
        pattern_name: str,
        field: str,
        answer: Any,
        escalation_level: str,
        fields: Optional[List[str]] = None,
        message: Optional[str] = None,
        label: Optional[str] = None,
    ) -> None:
        entry = {
            "pattern": pattern_name,
            "trigger_field": field,
            "value": answer,
            "escalation_level": escalation_level,
        }
        if fields:
            entry["fields"] = fields
        if label:
            entry["label"] = label
        if message:
            entry["message"] = message
        # De-duplicate by rule/pattern, not by the last trigger field, because shared
        # pattern rules are evaluated repeatedly after every answer.
        if not any(existing.get("pattern") == pattern_name for existing in self.red_flags):
            self.red_flags.append(entry)
        self._raise_escalation(escalation_level)

    def evaluate_shared_escalation_rules(self, trigger_field: str = "", trigger_answer: Any = None) -> None:
        """Evaluate all shared pattern escalation rules against accumulated state.

        Rules live in shared_v2.json as a dictionary keyed by rule id. Each rule may
        define applies_to_complaints and a structured condition. This method is
        intentionally called after complaint, ROS, and module answers so escalation
        is based on the full session state rather than a single question.
        """
        complaint_id = self.complaint.get("complaint_id", "")
        for rule_name, rule in self.escalation_rules.items():
            if not isinstance(rule, dict):
                continue
            applies = rule.get("applies_to_complaints") or rule.get("complaints") or []
            if applies and complaint_id not in applies:
                continue
            condition = rule.get("condition")
            if not condition:
                continue
            if evaluate_condition(
                condition,
                self.state,
                {**self.patient, "escalation_level": self.escalation_level},
                None,
            ):
                self._record_red_flag(
                    pattern_name=rule_name,
                    field=trigger_field or "shared_escalation_rule",
                    answer=trigger_answer if trigger_answer is not None else "matched",
                    escalation_level=rule.get("escalation_level", "priority_clinician_review"),
                    message=rule.get("message"),
                    label=rule.get("label"),
                )

    def _apply_linked_escalation_rules(self, q: Dict[str, Any], answer: Any) -> None:
        """
        Evaluate shared escalation rules referenced by a question.

        New complaint files use:
          linked_escalation_rules: [rule_name_1, rule_name_2]
        where each named rule exists in shared["escalation_rules"] and
        contains a structured `condition` plus `escalation_level`.
        """
        if not is_positive_answer(answer):
            return

        for rule_name in q.get("linked_escalation_rules", []) or []:
            rule = self.escalation_rules.get(rule_name)
            if not rule:
                continue
            condition = rule.get("condition")
            if condition and evaluate_condition(
                condition,
                self.state,
                {**self.patient, "escalation_level": self.escalation_level},
                q,
            ):
                self._record_red_flag(
                    pattern_name=rule_name,
                    field=q.get("field", ""),
                    answer=answer,
                    escalation_level=rule.get("escalation_level", "priority_clinician_review"),
                    message=rule.get("message"),
                    label=rule.get("label"),
                )

    def _check_red_flags(self, field: str, answer: Any) -> None:
        patterns = self.complaint.get("derived_red_flag_patterns", {})

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
                if field not in fields:
                    continue
                if not is_positive_answer(answer):
                    continue
                all_positive = all(
                    is_positive_answer(str(self.state.get(f, ""))) for f in fields if f != field
                )
                if all_positive:
                    self._record_red_flag(
                        pattern_name=pattern_name,
                        field=field,
                        answer=answer,
                        escalation_level=escalation,
                        fields=fields,
                    )
            return

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
                    matched = is_positive_answer(answer) if expected else is_negative_answer(answer)
                elif expected is None:
                    matched = is_positive_answer(answer)
                else:
                    matched = str(answer).strip().lower() == str(expected).strip().lower()
                if matched:
                    self._record_red_flag(
                        pattern_name=pattern.get("pattern", field),
                        field=field,
                        answer=answer,
                        escalation_level=pattern.get("escalation_level", "priority_clinician_review"),
                    )

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

        if is_positive_answer(answer):
            parent_field = self._parent_from_ask_if(q_def.get("ask_if"))
            if parent_field and self.state.get(parent_field) in (None, "", "not_assessed"):
                self.state[parent_field] = "yes"
                turn.setdefault("extracted_bonus_fields", {})[parent_field] = "yes"

        if is_positive_answer(answer):
            self._check_red_flags(field, answer)
            self._apply_linked_escalation_rules(q_def, answer)

        # Evaluate shared pattern rules after every answer, even if the current
        # answer is not positive, because this answer may complete or contextualize
        # a multi-field pattern.
        self.evaluate_shared_escalation_rules(field, answer)

        if q_def.get("capture_detail_if_positive") and q_def.get("detail_field") and is_positive_answer(answer):
            detail = str(answer).strip()
            low = detail.lower()
            for pfx in ("yes -", "yes,", "yes.", "yeah -", "yeah,", "yep -", "yep,"):
                if low.startswith(pfx):
                    detail = detail[len(pfx) :].strip()
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
            "phase": self.phases[min(self._phase_idx, len(self.phases) - 1)] if self.phases else "",
            "completed": self.completed,
            "escalation_level": self.escalation_level,
            "red_flags": self.red_flags,
        }