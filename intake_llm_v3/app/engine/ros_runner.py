"""Deterministic ROS runner using the uploaded ROS bank."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from app.engine.utils import evaluate_condition, is_negative_answer

def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ROSRunner:
    def __init__(self, state: Dict[str, Any], patient: Dict[str, Any], complaint: Dict[str, Any], shared_data: Dict[str, Any]):
        self.state = state
        self.patient = patient
        self.complaint = complaint
        self.shared = shared_data
        path = os.path.join(project_root(), "complaints_modules", "ros_question_bank.json")
        with open(path, "r", encoding="utf-8") as f:
            self.bank = json.load(f)

        self.questions = self.bank.get("questions", {})
        self.ask_if_registry = shared_data.get("ask_if_registry", {})
        self.skip_if_registry = shared_data.get("skip_if_registry", {})
        self.concept_map = shared_data.get("concept_dedup_map", {})
        self._answered_concepts = set(state.keys())
        self._ordered_qids = self._build_ordered_queue()
        self._idx = 0
        self.completed = False

    def _related_system_tokens(self) -> List[str]:
        related = [self.complaint.get("primary_system", "")]
        rel_obj = self.complaint.get("related_systems", {})
        for v in rel_obj.values():
            if isinstance(v, list):
                related.extend(v)
        ros_mode = self.complaint.get("question_budget", {}).get("ros_mode", {})
        if ros_mode.get("pathological_system"):
            related.insert(0, ros_mode["pathological_system"])
        return [x for x in related if x]

    def _system_match(self, q_system: str, tokens: List[str]) -> bool:
        for token in tokens:
            if q_system == token:
                return True
            if q_system.startswith(token + "_") or token.startswith(q_system + "_"):
                return True
        return False

    def _build_ordered_queue(self) -> List[str]:
        tokens = self._related_system_tokens()
        systems = self.bank.get("rendering_rules", {}).get("system_display_order", [])
        priority, secondary = [], []
        for qid, q in self.questions.items():
            if self._system_match(q.get("system", ""), tokens):
                priority.append(qid)
            else:
                secondary.append(qid)

        def sort_key(qid: str):
            q = self.questions[qid]
            prio = {"high": 0, "medium": 1, "low": 2}.get(q.get("clinical_priority", "medium"), 1)
            label = q.get("display_system") or q.get("system", "")
            system_idx = systems.index(label) if label in systems else 999
            return (system_idx, prio, qid)

        ordered = sorted(priority, key=sort_key)
        max_ros = self.complaint.get("question_budget", {}).get("ros_mode", {}).get("max_ros_questions", 4)
        extras = sorted(secondary, key=sort_key)[:max(0, max_ros)]
        return ordered[:max_ros] + extras

    def _concept_already_covered(self, concept: str) -> bool:
        if not concept:
            return False
        if concept in self._answered_concepts:
            return True
        for _, aliases in self.concept_map.items():
            if concept in aliases and any(alias in self._answered_concepts for alias in aliases):
                return True
        return False

    def _should_skip(self, q: Dict[str, Any]) -> bool:
        if self._concept_already_covered(q.get("canonical_concept", "")):
            return True
        for rule in q.get("skip_if", []):
            if rule == "FIELD_ALREADY_CAPTURED" and self.state.get(q["field"]) not in (None, ""):
                return True
            if rule == "ROS_CONCEPT_ALREADY_COVERED" and self._concept_already_covered(q.get("canonical_concept", "")):
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
        while self._idx < len(self._ordered_qids):
            qid = self._ordered_qids[self._idx]
            self._idx += 1
            q = self.questions[qid]
            if self._should_skip(q):
                continue
            return {
                "id": qid,
                "field": q["field"],
                "text": q.get("text", ""),
                "ui_label": q.get("ui_label", qid),
                "phase": "ros",
                "response_type": q.get("response_type", "SHORT_TEXT"),
                "canonical_concept": q.get("canonical_concept", ""),
                "sensitive_topic": q.get("sensitive_topic", False),
                "compound_question": q.get("compound_question", False),
            }
        self.completed = True
        return None

    def record_answer(self, question: Dict[str, Any], answer: Any) -> None:
        self.state[question["field"]] = answer
        concept = question.get("canonical_concept")
        if concept:
            self._answered_concepts.add(concept)
        self._answered_concepts.add(question["field"])
        if question.get("response_type") == "BOOLEAN_WITH_OPTIONAL_DETAILS" and question.get("detail_field") and answer and str(answer).strip().lower() not in ("no", "none", "false"):
            if str(answer).strip().lower() not in ("yes", "true"):
                self.state[question["detail_field"]] = answer
