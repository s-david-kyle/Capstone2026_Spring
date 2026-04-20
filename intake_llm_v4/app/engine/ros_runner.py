"""Deterministic ROS runner — v1.0.0 atomic model.

Under v1.0.0, every symptom has exactly ONE canonical field name used
everywhere. The dedup rule collapses to a single check:

    if state[question.field] is already set, skip.

No alias_map traversal, no cluster_map, no compound coverage tracking —
because no field is ever used in two places with two different names.

Selection pipeline:
  1. Resolve the complaint ROS plan. Use complaint.targeted_ros_plan when
     present; otherwise derive it from complaint.primary_system,
     complaint.question_budget.ros_mode.pathological_system, and
     complaint.related_systems.
  2. Partition the ROS bank by system. Exact matching; a trailing '*' on a
     token acts as a subtree wildcard (e.g. 'respiratory*' matches
     'respiratory_infectious').
  3. Sort priority pool by display_system order, then clinical_priority,
     then qid.
  4. Cross-system pool is filtered to clinical_priority in {high, medium}
     only, then sorted the same way.
  5. Iterator walks priority first, then cross. max_ros_questions caps the
     number ASKED (not candidates). Questions whose field is already in
     state are silently skipped without consuming budget.
"""


from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from app.engine.utils import evaluate_condition, is_negative_answer


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
        self.state = state
        self.patient = patient
        self.complaint = complaint
        self.shared = shared_data

        bank_path = os.path.join(project_root(), "complaints_modules", "ros_question_bank.json")
        with open(bank_path, "r", encoding="utf-8") as f:
            self.bank = json.load(f)

        self.questions: Dict[str, Dict[str, Any]] = self.bank.get("questions", {})
        self.ask_if_registry = shared_data.get("ask_if_registry", {})
        self.skip_if_registry = shared_data.get("skip_if_registry", {})

        self._ordered_qids: List[str] = self._build_ordered_queue()
        self._idx = 0
        self._asked_count = 0
        self.completed = False

    @staticmethod
    def _system_match(q_system: str, tokens: List[str]) -> bool:
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
        tokens = self._plan_tokens()
        display_order = self.bank.get("rendering_rules", {}).get("system_display_order", [])

        priority_pool: List[str] = []
        cross_pool: List[str] = []
        for qid, q in self.questions.items():
            if q.get("parent_field"):
                continue
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
        return int(
            self.complaint.get("question_budget", {})
            .get("ros_mode", {})
            .get("max_ros_questions", 4)
        )

    def _field_already_captured(self, field: str) -> bool:
        v = self.state.get(field)
        return v is not None and v != "" and v != "not_assessed"

    def _should_skip(self, q: Dict[str, Any]) -> bool:
        field = q.get("field", "")
        if self._field_already_captured(field):
            return True

        # Check both skip_if and skip_conditions
        for rule in (q.get("skip_if") or []) + (q.get("skip_conditions") or []):
            if isinstance(rule, str):
                if rule == "FIELD_ALREADY_CAPTURED" and self._field_already_captured(field):
                    return True
                if rule == "PARENT_NEGATIVE":
                    pf = q.get("parent_field", field.replace("_details", ""))
                    parent_answer = self.state.get(pf)
                    if parent_answer is None or is_negative_answer(str(parent_answer)):
                        return True
            reg = self.skip_if_registry.get(rule)
            if reg and evaluate_condition(reg.get("logic"), self.state, self.patient, q):
                return True

        ask_if = q.get("ask_if")
        if isinstance(ask_if, str):
            reg = self.ask_if_registry.get(ask_if)
            if reg and not evaluate_condition(reg.get("logic"), self.state, self.patient, q):
                return True
        elif isinstance(ask_if, dict):
            if not evaluate_condition(ask_if, self.state, self.patient, q):
                return True
        return False

    def get_next_question(self) -> Optional[Dict[str, Any]]:
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
            return {
                "id": qid,
                "field": q["field"],
                "text": q.get("text", ""),
                "ui_label": q.get("ui_label", qid),
                "phase": "ros",
                "response_type": q.get("response_type", "SHORT_TEXT"),
                "canonical_concept": q.get("canonical_concept", q["field"]),
                "sensitive_topic": q.get("sensitive_topic", False),
                "detail_field": q.get("detail_field"),
            }
        self.completed = True
        return None

    def record_answer(self, question: Dict[str, Any], answer: Any) -> None:
        self.state[question["field"]] = answer
        if (
            question.get("response_type") == "BOOLEAN_WITH_OPTIONAL_DETAILS"
            and question.get("detail_field")
            and answer
            and str(answer).strip().lower() not in ("no", "none", "false")
            and str(answer).strip().lower() not in ("yes", "true")
        ):
            self.state[question["detail_field"]] = answer