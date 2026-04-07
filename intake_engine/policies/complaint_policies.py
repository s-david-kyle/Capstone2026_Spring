from copy import deepcopy


HEADACHE_POLICY = {
    "policy_name": "headache",
    "display_name": "Headache",
    "aliases": [
        "headache",
        "migraine",
        "head pain",
    ],
    "critical_followups": [
        "sudden_severe_onset",
        "neurologic_symptoms",
        "visual_changes",
        "confusion_or_ams",
        "fever_or_neck_stiffness",
        "head_trauma",
        "pregnancy_or_postpartum_context",
    ],
    "must_characterize": [
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
    ],
    "high_priority_followups": [
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
    ],
    "red_flags": [
        "thunderclap_headache",
        "focal_neurologic_deficit",
        "altered_mental_status",
        "fever_with_neck_stiffness",
        "post_traumatic_headache",
        "progressive_or_new_severe_pattern",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "location",
            "character",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}


CHEST_PAIN_POLICY = {
    "policy_name": "chest_pain",
    "display_name": "Chest Pain",
    "aliases": [
        "chest pain",
        "chest pressure",
        "chest tightness",
    ],
    "critical_followups": [
        "shortness_of_breath",
        "syncope_or_presyncope",
        "rapid_worsening",
    ],
    "must_characterize": [
        "onset",
        "location",
        "duration",
        "severity",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "radiation",
        "nausea",
        "diaphoresis",
        "exertional_component",
    ],
    "red_flags": [
        "active_breathing_difficulty",
        "syncope_or_presyncope",
        "severe_symptom_intensity",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "location",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 5,
    },
}


COMPLAINT_POLICIES = {
    "headache": HEADACHE_POLICY,
    "chest_pain": CHEST_PAIN_POLICY,
}


def get_policy_dict(policy_name):
    """
    Return a deep copy of the policy definition so callers do not mutate
    the module-level source of truth.
    """
    policy = COMPLAINT_POLICIES.get(policy_name)

    if policy is None:
        return None

    return deepcopy(policy)


def get_all_policy_dicts():
    """
    Return a deep copy of all policies keyed by policy_name.
    """
    return deepcopy(COMPLAINT_POLICIES)