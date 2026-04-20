"""Reusable history-module runner."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from app.engine.utils import evaluate_condition, is_negative_answer


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ModuleRunner:
    def __init__(
        self,
        modules_dir: str,
        state: Dict[str, Any],
        patient: Dict[str, Any],
        complaint_id: str,
        conditional_modules: List[str],
        shared_data: Dict[str, Any],
    ):
        self.modules_dir = modules_dir
        self.state = state
        self.patient = patient
        self.complaint_id = complaint_id
        self.conditional_modules = conditional_modules
        self.shared = shared_data
        self.concept_map = shared_data.get("concept_alias_map", {})
        self.ask_if_registry = shared_data.get("ask_if_registry", {})
        self.skip_if_registry = shared_data.get("skip_if_registry", {})
        self._current_module_idx = 0
        self._current_q_idx = 0
        self._loaded_modules: List[Dict[str, Any]] = []
        self._module_budget_remaining: Dict[str, int] = {}
        self.completed = False
        self._answered_concepts = set(state.keys())
        self._load_modules()
        self._init_budgets()

    def _ordered_module_names(self) -> List[str]:
        names = self.shared.get("authoritative_module_order", [])
        return [x for x in names if x.endswith("_module.json")]

    def _evaluate_activation_rules(self, mod: Dict[str, Any]) -> bool:
        """Return True if the module's activation_rules all evaluate to true."""
        rules = mod.get("activation_rules", [])
        if not rules:
            # No activation rules → always load (subject to conditional_modules list)
            return True
        # Rules are a list of strings that correspond to entries in ask_if_registry
        for rule_name in rules:
            reg = self.ask_if_registry.get(rule_name)
            if reg is None:
                # Unknown rule → skip module
                return False
            if not evaluate_condition(reg.get("logic"), self.state, self.patient):
                return False
        return True

    def _load_modules(self) -> None:
        for mod_file in self._ordered_module_names():
            mod_name = mod_file.replace(".json", "")
            path = os.path.join(self.modules_dir, mod_file)
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                mod = json.load(f)

            # Conditional modules (gynecologic, immunization) are only loaded if:
            # - They appear in the index's conditional_modules list for this complaint, AND
            # - Their own activation_rules evaluate to true.
            if mod_name in ("gynecologic_history_module", "immunization_history_module"):
                if mod_name not in self.conditional_modules:
                    continue
                if not self._evaluate_activation_rules(mod):
                    continue

            self._loaded_modules.append(mod)

    def _init_budgets(self) -> None:
        for mod in self._loaded_modules:
            self._module_budget_remaining[mod.get("module_name", "")] = int(
                mod.get("session_cap_questions", 10)
            )

    def _should_skip(self, q: Dict[str, Any], mod_name: str) -> bool:
        if self._module_budget_remaining.get(mod_name, 10) <= 0:
            return True

        field = q.get("field")
        # v1.0.0 dedup: skip if field already captured
        if self.state.get(field) not in (None, ""):
            return True

        for rule in q.get("skip_if", []):
            if rule == "FIELD_ALREADY_CAPTURED" and self.state.get(field) not in (
                None,
                "",
            ):
                return True
            if rule == "PARENT_NEGATIVE":
                pf = q.get("parent_field", field.replace("_details", ""))
                pa = self.state.get(pf)
                if pa is None or is_negative_answer(str(pa)):
                    return True
            reg = self.skip_if_registry.get(rule)
            if reg and evaluate_condition(
                reg.get("logic"), self.state, self.patient, q
            ):
                return True

        ask_if = q.get("ask_if")
        if isinstance(ask_if, str):
            cond = self.ask_if_registry.get(ask_if, {}).get("logic")
            if cond and not evaluate_condition(cond, self.state, self.patient, q):
                return True
        elif isinstance(ask_if, dict):
            if not evaluate_condition(ask_if, self.state, self.patient, q):
                return True
        return False

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        while self._current_module_idx < len(self._loaded_modules):
            mod = self._loaded_modules[self._current_module_idx]
            mod_name = mod.get("module_name", "")
            questions = mod.get("questions", [])
            field_order = mod.get("field_order", [q["field"] for q in questions])

            while self._current_q_idx < len(field_order):
                field = field_order[self._current_q_idx]
                self._current_q_idx += 1
                q = next((x for x in questions if x.get("field") == field), None)
                if not q or self._should_skip(q, mod_name):
                    continue
                return {
                    "id": q.get("field"),
                    "field": q.get("field"),
                    "text": q.get("text", ""),
                    "ui_label": q.get("ui_label", q.get("field")),
                    "phase": q.get("phase", "context_and_history"),
                    "response_type": q.get("response_type", "SHORT_TEXT"),
                    "canonical_concept": q.get("canonical_concept", q.get("field", "")),
                    "sensitive_topic": q.get("sensitive_topic", False),
                    "compound_question": q.get("compound_question", False),
                    "detail_field": q.get("detail_field"),
                }

            self._current_module_idx += 1
            self._current_q_idx = 0

        self.completed = True
        return None

    def record_answer(self, question: Dict[str, Any], answer: Any) -> None:
        self.state[question["field"]] = answer
        self._answered_concepts.add(
            question.get("canonical_concept") or question["field"]
        )
        self._answered_concepts.add(question["field"])
        if (
            question.get("detail_field")
            and str(answer).strip().lower() not in ("", "no", "none", "false")
        ):
            if str(answer).strip().lower() not in ("yes", "true"):
                self.state[question["detail_field"]] = answer
        mod_name = ""
        if self._current_module_idx < len(self._loaded_modules):
            mod_name = self._loaded_modules[self._current_module_idx].get(
                "module_name", ""
            )
        if mod_name:
            self._module_budget_remaining[mod_name] = max(
                0, self._module_budget_remaining.get(mod_name, 1) - 1
            )

    # ------------------------------------------------------------------
    # Public helper methods for main.py
    # ------------------------------------------------------------------
    def get_question_text(self, field: str) -> Optional[str]:
        """Return the question text for a given field, or None if not found."""
        for mod in self._loaded_modules:
            for q in mod.get("questions", []):
                if q.get("field") == field:
                    return q.get("text")
        return None

    def get_question_definition(self, field: str) -> Optional[Dict[str, Any]]:
        """Return the full question definition for a given field, or None if not found."""
        for mod in self._loaded_modules:
            for q in mod.get("questions", []):
                if q.get("field") == field:
                    return {
                        "id": field,
                        "field": field,
                        "phase": q.get("phase", "context_and_history"),
                        "response_type": q.get("response_type"),
                        "canonical_concept": q.get("canonical_concept"),
                        "detail_field": q.get("detail_field"),
                    }
        return None