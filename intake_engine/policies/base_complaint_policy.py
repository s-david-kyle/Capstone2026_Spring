from intake_engine.policies.target_specs import TARGET_SPECS


class BaseComplaintPolicy:
    """
    Generic runtime wrapper around a plain complaint policy dictionary.

    This replaces complaint-specific subclasses. Complaint-specific differences
    now live in the data passed into this class.
    """

    def __init__(self, policy_definition):
        self.policy_definition = policy_definition

        self.policy_name = policy_definition.get("policy_name")
        self.display_name = policy_definition.get("display_name", self.policy_name)
        self.aliases = policy_definition.get("aliases", [])

        self.critical_followups = policy_definition.get("critical_followups", [])
        self.must_characterize = policy_definition.get("must_characterize", [])
        self.high_priority_followups = policy_definition.get("high_priority_followups", [])
        self.red_flags = policy_definition.get("red_flags", [])
        self.wrap_up_rule = policy_definition.get("wrap_up_rule", {})

    def target_to_state_path(self, target):
        spec = TARGET_SPECS.get(target, {})
        return spec.get("state_path")

    def get_target_spec(self, target):
        return TARGET_SPECS.get(target, {})

    def target_to_intent(self, target):
        """
        Backward-compatible method expected by IntakeState.

        Prefer an explicit question_intent from TARGET_SPECS.
        Fall back to ask_<target>.
        """
        if target is None:
            return None

        spec = self.get_target_spec(target)
        return spec.get("question_intent", f"ask_{target}")

    def is_missing(self, value):
        if value is None:
            return True

        if isinstance(value, str) and value.strip() == "":
            return True

        if isinstance(value, (list, dict, set, tuple)) and len(value) == 0:
            return True

        return False

    def get_field_value(self, intake, state_path, default = None):
        """
        Supports dotted paths like 'hpi.onset'.
        Accepts either dict-like intake or object-like intake.
        """
        if not state_path:
            return default

        current = intake

        for part in state_path.split("."):
            if current is None:
                return default

            if isinstance(current, dict):
                current = current.get(part, default)
            else:
                current = getattr(current, part, default)

        return current

    def _list_contains_target_value(self, value, target):
        """
        Handles targets whose state_path points to a list-like bucket such as
        pertinent_positives, pertinent_negatives, or flags.
        """
        if value is None:
            return False

        if isinstance(value, str):
            return target in value

        if isinstance(value, (list, set, tuple)):
            return target in value

        return False

    def _is_target_resolved(self, intake, target):
        """
        Generic target resolution check.

        If the target maps to a simple scalar field such as hpi.onset, we check
        whether that field is missing.

        If the target maps to a list-like bucket such as pertinent_positives,
        pertinent_negatives, or flags, presence of the target name in that bucket
        counts as resolved.

        If the spec provides an explicit resolve_mode, we honor it.
        """
        spec = self.get_target_spec(target)
        state_path = spec.get("state_path")

        if not state_path:
            return False

        value = self.get_field_value(intake, state_path)
        resolve_mode = spec.get("resolve_mode")

        if resolve_mode == "presence_in_collection":
            return self._list_contains_target_value(value, target)

        if resolve_mode == "non_missing_field":
            return not self.is_missing(value)

        if isinstance(value, (list, set, tuple)):
            return self._list_contains_target_value(value, target)

        return not self.is_missing(value)

    def choose_next_target(self, intake):
        """
        Prioritize unresolved targets in this order:
        critical_followups -> must_characterize -> high_priority_followups
        """
        ordered_groups = [
            self.critical_followups,
            self.must_characterize,
            self.high_priority_followups,
        ]

        for group in ordered_groups:
            for target in group:
                if not self._is_target_resolved(intake, target):
                    return target

        return None

    def choose_next_question_intent(self, intake):
        """
        Returns the question intent for the next unresolved target.
        """
        target = self.choose_next_target(intake)
        return self.target_to_intent(target)

    def _evaluate_all_required_rule(self, intake, rule):
        required_targets = rule.get("required_targets", [])

        if rule.get("require_all_critical", False):
            critical_resolved = all(
                self._is_target_resolved(intake, target)
                for target in self.critical_followups
            )

            if not critical_resolved:
                return False

        return all(
            self._is_target_resolved(intake, target)
            for target in required_targets
        )

    def _evaluate_characterization_threshold_rule(self, intake, rule):
        if rule.get("require_all_critical", False):
            critical_resolved = all(
                self._is_target_resolved(intake, target)
                for target in self.critical_followups
            )

            if not critical_resolved:
                return False

        required_characterization_targets = rule.get(
            "required_characterization_targets",
            [],
        )
        min_required_characterization_count = rule.get(
            "min_required_characterization_count",
            len(required_characterization_targets),
        )

        characterization_resolved_count = sum(
            1
            for target in required_characterization_targets
            if self._is_target_resolved(intake, target)
        )

        return characterization_resolved_count >= min_required_characterization_count

    def is_ready_to_wrap_up(self, intake):
        """
        Generic wrap-up evaluator driven entirely by policy data.
        """
        rule = self.wrap_up_rule or {}

        rule_type = rule.get("type", "all_required")

        if rule_type == "all_required":
            return self._evaluate_all_required_rule(intake, rule)

        if rule_type == "characterization_threshold":
            return self._evaluate_characterization_threshold_rule(intake, rule)

        raise ValueError(
            f"Unsupported wrap_up_rule type '{rule_type}' for policy '{self.policy_name}'"
        )