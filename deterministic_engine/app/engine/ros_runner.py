"""Deterministic ROS runner — v1.1.0 with batch mode support.

Batch mode: collects all unanswered questions of a single system and returns them
as a batch. The UI presents them as a checklist, saving time and reducing turns.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from app.engine.utils import evaluate_condition, is_negative_answer, dedup_family_covered, code_already_captured, mark_question_metadata


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


class ROSRunner:
    def __init__(
        self,
        state: Dict[str, Any],
        patient: Dict[str, Any],
        complaint: Dict[str, Any],
        shared_data: Dict[str, Any],
    ):
        """
        Initialise the ROS runner.

        Args:
            state: Shared session state (filled by complaint engine, modules, etc.)
            patient: Patient demographics (age, sex)
            complaint: Complaint data (used for ROS planning and budget)
            shared_data: Shared_v2.json content (ask_if, skip_if, sensitive concepts)
        """
        self.state = state
        self.patient = patient
        self.patient.setdefault("primary_complaint", complaint.get("complaint_id", ""))
        self.state.setdefault("primary_complaint", complaint.get("complaint_id", ""))
        self.complaint = complaint
        self.shared = shared_data
        self.sensitive_concept_list = shared_data.get("sensitive_concept_list", [])

        bank_path = os.path.join(project_root(), "complaints_modules", "ros_question_bank.json")
        with open(bank_path, "r", encoding="utf-8") as f:
            self.bank = json.load(f)

        self.questions: Dict[str, Dict[str, Any]] = self.bank.get("questions", {})
        self.ask_if_registry = shared_data.get("ask_if_registry", {})
        self.skip_if_registry = shared_data.get("skip_if_registry", {})

        # Build the ordered list of question IDs (priority topics first, then cross-system)
        self._ordered_qids: List[str] = self._build_ordered_queue()
        self._idx = 0               # Current position in the ordered queue
        self._asked_count = 0       # Number of ROS questions already asked (budget consumption)
        self.completed = False

    @staticmethod
    def _system_match(q_system: str, tokens: List[str]) -> bool:
        """
        Check if a question's system matches a list of tokens.
        Supports wildcard suffix '*', e.g., 'respiratory*' matches 'respiratory' or 'respiratory_infectious'.
        """
        if not q_system:
            return False
        for token in tokens:
            if not token:
                continue
            if token.endswith("*"):
                root = token[:-1].rstrip("_")
                if q_system == root or q_system.startswith(root + "_"):
                    return True
            elif q_system == token:
                return True
        return False

    def _plan_tokens(self) -> Dict[str, List[str]]:
        """
        Determine which systems to ask based on the complaint's ROS plan.
        Returns two lists: priority systems (must be asked) and cross systems (optional).
        """
        plan = self.complaint.get("targeted_ros_plan") or {}
        rel = self.complaint.get("related_systems") or {}

        high_yield = list(plan.get("high_yield_systems") or rel.get("high_yield") or [])
        cross = list(plan.get("cross_system_systems") or [])
        if not cross:
            cross = list(rel.get("selective_cross_system") or []) + list(rel.get("contextual") or [])

        primary = (
            plan.get("primary_system")
            or self.complaint.get("question_budget", {}).get("ros_mode", {}).get("pathological_system")
            or self.complaint.get("primary_system", "")
        )

        priority_tokens: List[str] = []
        for token in [primary, *high_yield]:
            if token and token not in priority_tokens:
                priority_tokens.append(token)

        cross_tokens: List[str] = []
        for token in cross:
            if token and token not in priority_tokens and token not in cross_tokens:
                cross_tokens.append(token)

        return {"priority": priority_tokens, "cross": cross_tokens}

    def _build_ordered_queue(self) -> List[str]:
        """
        Build the global ordered list of ROS question IDs.
        Priority pool first (sorted by display system order, then clinical priority, then ID),
        then cross-system pool (filtered to high/medium priority, same sort).
        """
        tokens = self._plan_tokens()
        display_order = self.bank.get("rendering_rules", {}).get("system_display_order", [])

        priority_pool: List[str] = []
        cross_pool: List[str] = []
        for qid, q in self.questions.items():
            if q.get("parent_field"):
                continue  # Skip child questions (they are asked only if parent is yes)
            sys = q.get("system", "")
            if self._system_match(sys, tokens["priority"]):
                priority_pool.append(qid)
            elif self._system_match(sys, tokens["cross"]):
                cross_pool.append(qid)

        def sort_key(qid: str):
            q = self.questions[qid]
            prio = _PRIORITY_RANK.get(q.get("clinical_priority", "medium"), 1)
            label = q.get("display_system") or q.get("system", "")
            sys_idx = display_order.index(label) if label in display_order else 999
            return (sys_idx, prio, qid)

        priority_pool.sort(key=sort_key)
        cross_pool = [
            qid for qid in cross_pool
            if self.questions[qid].get("clinical_priority", "medium") in ("high", "medium")
        ]
        cross_pool.sort(key=sort_key)
        return priority_pool + cross_pool

    @property
    def _max_ros(self) -> int:
        """Maximum number of ROS questions allowed for this complaint."""
        return int(
            self.complaint.get("question_budget", {})
            .get("ros_mode", {})
            .get("max_ros_questions", 4)
        )

    def _field_already_captured(self, field: str) -> bool:
        """Check if a field already has a meaningful value in the session state."""
        v = self.state.get(field)
        return v is not None and v != "" and v != "not_assessed"

    def _should_skip(self, q: Dict[str, Any]) -> bool:
        """
        Decide whether a ROS question should be skipped.

        Reasons to skip:
        - The field already has a value (asked in complaint/module/previous ROS).
        - Any skip_if or skip_conditions evaluate to true.
        - ask_if condition fails.
        """
        field = q.get("field", "")
        if self._field_already_captured(field):
            return True
        if code_already_captured(q, self.state):
            return True
        if dedup_family_covered(q, self.state, self.shared):
            return True

        for rule in (q.get("skip_if") or []) + (q.get("skip_conditions") or []):
            if isinstance(rule, str):
                if rule == "FIELD_ALREADY_CAPTURED":
                    if self._field_already_captured(field):
                        return True
                    continue
                if rule == "PARENT_NEGATIVE":
                    pf = q.get("parent_field", field.replace("_details", ""))
                    parent_answer = self.state.get(pf)
                    if parent_answer is None or is_negative_answer(str(parent_answer)):
                        return True
                    continue
            reg = self.skip_if_registry.get(rule)
            if reg and evaluate_condition(reg.get("logic", reg.get("condition")), self.state, self.patient, q):
                return True

        ask_if = q.get("ask_if")
        if isinstance(ask_if, str):
            reg = self.ask_if_registry.get(ask_if)
            if reg and not evaluate_condition(reg.get("logic", reg.get("condition")), self.state, self.patient, q):
                return True
        elif isinstance(ask_if, dict):
            if not evaluate_condition(ask_if, self.state, self.patient, q):
                return True
        return False

    # -------------------- Batch mode (primary) --------------------
    def get_next_batch(self) -> Optional[Dict[str, Any]]:
        """
        Return a batch of unanswered ROS questions belonging to the next system.

        Each batch includes all remaining questions of that system (up to a safe limit),
        respecting the global ROS budget. The UI can present them as a checklist.

        Returns:
            Dictionary with keys:
                - type: "ros_batch"
                - system: Display name of the system (e.g., "Constitutional")
                - questions: List of question dictionaries (each with id, field, text, etc.)
                - budget_remaining: Number of ROS questions still allowed
            or None if ROS is complete or budget exhausted.
        """
        if self._asked_count >= self._max_ros:
            self.completed = True
            return None

        current_system = None
        batch_questions: List[Dict[str, Any]] = []
        idx = self._idx

        # Collect questions until we hit a different system or exceed budget.
        while idx < len(self._ordered_qids) and len(batch_questions) < 20:
            qid = self._ordered_qids[idx]
            q = self.questions[qid]
            if not self._should_skip(q):
                sys = q.get("display_system") or q.get("system")
                if current_system is None:
                    current_system = sys
                if sys == current_system:
                    # Check budget: if adding this question would exceed max_ros, stop.
                    if self._asked_count + len(batch_questions) + 1 > self._max_ros:
                        break
                    field = q.get("field", qid)
                    sensitive = q.get("sensitive_topic", False)
                    if not sensitive and field in self.sensitive_concept_list:
                        sensitive = True
                    batch_questions.append({
                        "id": qid,
                        "field": field,
                        "code": q.get("code", ""),
                        "text": q.get("text", ""),
                        "ui_label": q.get("ui_label", qid),
                        "response_type": q.get("response_type", "BOOLEAN_WITH_OPTIONAL_DETAILS"),
                        "canonical_concept": q.get("canonical_concept", field),
                        "dedup_family": q.get("dedup_family"),
                        "dedup_families": q.get("dedup_families", []),
                        "question_role": q.get("question_role", "ros_question"),
                        "sensitive_topic": sensitive,
                        "detail_field": q.get("detail_field"),
                    })
                    idx += 1
                else:
                    break
            else:
                idx += 1

        if not batch_questions:
            self.completed = True
            return None

        # Remember where we stopped, so record_batch_answers can advance the pointer.
        self._batch_pending_idx = idx
        return {
            "type": "ros_batch",
            "system": current_system,
            "questions": batch_questions,
            "budget_remaining": self._max_ros - self._asked_count
        }

    def record_batch_answers(self, answers: Dict[str, str], details: Optional[Dict[str, str]] = None) -> None:
        """
        Record answers for the last batch returned by get_next_batch().

        Args:
            answers: Dictionary mapping field names to answer strings (e.g., {"fever": "yes"})
            details: Optional dictionary mapping field names to detail text (e.g., {"fever": "38.5°C"})
        """
        for field, answer in answers.items():
            # Find the question definition by field name
            q = next((q for q in self.questions.values() if q.get("field") == field), None)
            if not q:
                continue
            self.state[field] = answer
            mark_question_metadata(self.state, q, self.shared)
            self._asked_count += 1
            if q.get("detail_field") and details and field in details:
                detail_val = details[field]
                if detail_val and detail_val.strip():
                    self.state[q["detail_field"]] = detail_val.strip()
        if hasattr(self, "_batch_pending_idx"):
            self._idx = self._batch_pending_idx
            delattr(self, "_batch_pending_idx")

    def peek_current_batch(self) -> Optional[Dict[str, Any]]:
        """
        Return the next batch without advancing state (for preview).

        Used by the UI to display the batch before the user submits answers.
        """
        if self._asked_count >= self._max_ros:
            return None
        current_system = None
        batch_questions = []
        idx = self._idx
        while idx < len(self._ordered_qids) and len(batch_questions) < 20:
            qid = self._ordered_qids[idx]
            q = self.questions[qid]
            if not self._should_skip(q):
                sys = q.get("display_system") or q.get("system")
                if current_system is None:
                    current_system = sys
                if sys == current_system:
                    if self._asked_count + len(batch_questions) + 1 > self._max_ros:
                        break
                    field = q.get("field", qid)
                    sensitive = q.get("sensitive_topic", False)
                    if not sensitive and field in self.sensitive_concept_list:
                        sensitive = True
                    batch_questions.append({
                        "id": qid,
                        "field": field,
                        "code": q.get("code", ""),
                        "text": q.get("text", ""),
                        "ui_label": q.get("ui_label", qid),
                        "response_type": q.get("response_type", "BOOLEAN_WITH_OPTIONAL_DETAILS"),
                        "canonical_concept": q.get("canonical_concept", field),
                        "dedup_family": q.get("dedup_family"),
                        "dedup_families": q.get("dedup_families", []),
                        "question_role": q.get("question_role", "ros_question"),
                        "sensitive_topic": sensitive,
                        "detail_field": q.get("detail_field"),
                    })
                    idx += 1
                else:
                    break
            else:
                idx += 1
        if not batch_questions:
            return None
        return {
            "type": "ros_batch",
            "system": current_system,
            "questions": batch_questions,
            "budget_remaining": self._max_ros - self._asked_count
        }

    # -------------------- Legacy single‑question mode (kept for compatibility) --------------------
    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """
        Legacy single‑question mode. Returns one question at a time.
        Not recommended for production; use batch mode instead.
        """
        if self._asked_count >= self._max_ros:
            self.completed = True
            return None
        while self._idx < len(self._ordered_qids):
            qid = self._ordered_qids[self._idx]
            self._idx += 1
            q = self.questions[qid]
            if self._should_skip(q):
                continue
            self._asked_count += 1
            field = q.get("field", qid)
            sensitive = q.get("sensitive_topic", False)
            if not sensitive and field in self.sensitive_concept_list:
                sensitive = True
            return {
                "id": qid,
                "field": field,
                "code": q.get("code", ""),
                "text": q.get("text", ""),
                "ui_label": q.get("ui_label", qid),
                "phase": "ros",
                "response_type": q.get("response_type", "BOOLEAN_WITH_OPTIONAL_DETAILS"),
                "canonical_concept": q.get("canonical_concept", field),
                "sensitive_topic": sensitive,
                "detail_field": q.get("detail_field"),
            }
        self.completed = True
        return None

    def record_answer(self, question: Dict[str, Any], answer: Any) -> None:
        """Legacy single‑answer recording (kept for compatibility)."""
        self.state[question["field"]] = answer
        mark_question_metadata(self.state, question, self.shared)
        self._asked_count += 1
        if (
            question.get("response_type") == "BOOLEAN_WITH_OPTIONAL_DETAILS"
            and question.get("detail_field")
            and answer
            and str(answer).strip().lower() not in ("no", "none", "false")
            and str(answer).strip().lower() not in ("yes", "true")
        ):
            self.state[question["detail_field"]] = answer

    def peek_current_question(self) -> Optional[Dict[str, Any]]:
        """Legacy peek – not used in batch mode."""
        return None