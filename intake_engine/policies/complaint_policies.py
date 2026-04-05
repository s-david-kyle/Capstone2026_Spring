from intake_engine.policies.base_complaint_policy import BaseComplaintPolicy


class HeadachePolicy(BaseComplaintPolicy):
    policy_name = "headache"

    critical_followups = [
        "sudden_severe_onset",
        "neurologic_symptoms",
        "visual_changes",
        "confusion_or_ams",
        "fever_or_neck_stiffness",
        "head_trauma",
        "pregnancy_or_postpartum_context",
    ]

    must_characterize = [
        "onset",
        "duration",
        "severity",
        "timing",
        "course",
        "location",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ]

    high_priority_followups = [
        "medications",
        "allergies",
        "photophobia",
        "phonophobia",
        "nausea_or_vomiting",
        "aura_features",
        "exertional_trigger",
        "positional_component",
        "new_or_progressive_pattern",
        "medication_overuse_context",
    ]

    red_flags = [
        "thunderclap_headache",
        "focal_neurologic_deficit",
        "altered_mental_status",
        "fever_with_neck_stiffness",
        "post_traumatic_headache",
        "progressive_or_new_severe_pattern",
    ]

    def is_ready_to_wrap_up(self, intake):
        critical_resolved = all(
            self._is_target_resolved(intake, target)
            for target in self.critical_followups
        )

        required_characterization_targets = [
            "onset",
            "duration",
            "severity",
            "location",
            "character",
            "associated_symptoms",
        ]

        characterization_resolved_count = 0

        for target in required_characterization_targets:
            state_path = self.target_to_state_path(target)
            value = self.get_field_value(intake, state_path)

            if not self.is_missing(value):
                characterization_resolved_count += 1

        return critical_resolved and characterization_resolved_count >= 4


class ChestPainPolicy(BaseComplaintPolicy):
    policy_name = "chest_pain"

    critical_followups = [
        "shortness_of_breath",
        "syncope_or_presyncope",
        "rapid_worsening",
    ]

    must_characterize = [
        "onset",
        "location",
        "duration",
        "severity",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ]

    high_priority_followups = [
        "medications",
        "allergies",
        "radiation",
        "nausea",
        "diaphoresis",
        "exertional_component",
    ]

    red_flags = [
        "active_breathing_difficulty",
        "syncope_or_presyncope",
        "severe_symptom_intensity",
    ]

    def is_ready_to_wrap_up(self, intake):
        critical_resolved = all(
            self._is_target_resolved(intake, target)
            for target in self.critical_followups
        )

        required_characterization_targets = [
            "onset",
            "duration",
            "severity",
            "location",
            "associated_symptoms",
        ]

        characterization_complete = all(
            not self.is_missing(
                self.get_field_value(intake, self.target_to_state_path(target))
            )
            for target in required_characterization_targets
        )

        return critical_resolved and characterization_complete