from intake_engine.policies.target_specs import TARGET_SPECS


class BaseComplaintPolicy:
    policy_name = "base"
    critical_followups = []
    must_characterize = []
    high_priority_followups = []
    red_flags = []

    def is_missing(self, value):
        if value is None:
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False

    def get_field_value(self, intake, field):
        """
        Supports dotted paths like 'hpi.onset' or 'policy_answers.visual_changes'.
        """
        value = intake
        for part in field.split("."):
            value = value.get(part)
            if value is None:
                return None
        return value

    def target_to_state_path(self, target):
        spec = TARGET_SPECS.get(target)
        if spec is not None:
            return spec["state_path"]

        if target == "recommend_immediate_attention":
            return target

        return target

    def missing_fields(self, intake, fields):
        for field in fields:
            state_path = self.target_to_state_path(field)
            value = self.get_field_value(intake, state_path)
            if self.is_missing(value):
                yield field

    def has_urgent_flag(self, intake):
        flags = set(intake.get("flags", []))
        acuity = set(intake.get("conversation_meta", {}).get("acuity_signal", []))

        return (
            "active_breathing_difficulty" in acuity
            or "syncope_or_presyncope" in acuity
            or "recommend_immediate_attention" in flags
        )

    def _get_question_status_map(self, intake):
        return intake.get("conversation_meta", {}).get("question_status", {})

    def _is_target_resolved(self, intake, target):
        question_status = self._get_question_status_map(intake)
        return question_status.get(target) in {
            "asked_answered",
            "asked_unknown",
            "asked_declined",
        }

    def _count_resolved_targets(self, intake, targets):
        return sum(
            1 for target in targets
            if self._is_target_resolved(intake, target)
        )

    def is_ready_to_wrap_up(self, intake):
        return False

    def choose_next_target(self, intake):
        if self.has_urgent_flag(intake):
            return "recommend_immediate_attention"

        if self.is_ready_to_wrap_up(intake):
            return None

        for field in self.critical_followups:
            if not self._is_target_resolved(intake, field):
                state_path = self.target_to_state_path(field)
                value = self.get_field_value(intake, state_path)
                if self.is_missing(value):
                    return field

        for field in self.must_characterize:
            state_path = self.target_to_state_path(field)
            value = self.get_field_value(intake, state_path)
            if self.is_missing(value):
                return field

        for field in self.high_priority_followups:
            if not self._is_target_resolved(intake, field):
                state_path = self.target_to_state_path(field)
                value = self.get_field_value(intake, state_path)
                if self.is_missing(value):
                    return field

        return None

    def target_to_intent(self, target):
        spec = TARGET_SPECS.get(target)
        if spec is not None:
            return spec["intent"]

        if target == "recommend_immediate_attention":
            return "recommend_immediate_attention"

        return None