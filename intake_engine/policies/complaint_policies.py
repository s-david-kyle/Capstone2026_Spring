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


ABDOMINAL_PAIN_POLICY = {
    "policy_name": "abdominal_pain",
    "display_name": "Abdominal Pain",
    "aliases": [
        "abdominal pain",
        "stomach pain",
        "belly pain",
        "stomach ache",
    ],
    "critical_followups": [
        "vomiting",
        "fever",
        "bloody_stool_or_melena",
        "pregnancy_or_postpartum_context",
        "syncope_or_presyncope",
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
        "nausea",
        "diarrhea",
        "constipation",
        "urinary_symptoms",
        "last_oral_intake",
    ],
    "red_flags": [
        "persistent_vomiting",
        "blood_in_stool",
        "pregnancy_related_abdominal_pain",
        "severe_abdominal_pain_with_syncope",
        "fever_with_abdominal_pain",
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
        "min_required_characterization_count": 4,
    },
}


SHORTNESS_OF_BREATH_POLICY = {
    "policy_name": "shortness_of_breath",
    "display_name": "Shortness of Breath",
    "aliases": [
        "shortness of breath",
        "sob",
        "trouble breathing",
        "breathing difficulty",
    ],
    "critical_followups": [
        "chest_pain",
        "rapid_worsening",
        "syncope_or_presyncope",
        "fever",
        "wheezing",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "timing",
        "course",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "cough",
        "orthopnea",
        "leg_swelling",
        "exertional_component",
    ],
    "red_flags": [
        "active_breathing_difficulty",
        "shortness_of_breath_with_chest_pain",
        "shortness_of_breath_with_syncope",
        "rapidly_worsening_breathing",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}


DIZZINESS_POLICY = {
    "policy_name": "dizziness",
    "display_name": "Dizziness",
    "aliases": [
        "dizziness",
        "lightheadedness",
        "feeling faint",
        "vertigo",
    ],
    "critical_followups": [
        "syncope_or_presyncope",
        "neurologic_symptoms",
        "chest_pain",
        "shortness_of_breath",
        "head_trauma",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "timing",
        "course",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "visual_changes",
        "palpitations",
        "positional_component",
        "nausea",
    ],
    "red_flags": [
        "dizziness_with_syncope",
        "dizziness_with_neurologic_deficit",
        "dizziness_with_chest_pain",
        "post_traumatic_dizziness",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}


SORE_THROAT_POLICY = {
    "policy_name": "sore_throat",
    "display_name": "Sore Throat",
    "aliases": [
        "sore throat",
        "throat pain",
        "scratchy throat",
    ],
    "critical_followups": [
        "shortness_of_breath",
        "trouble_swallowing",
        "drooling",
        "fever",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "timing",
        "course",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "cough",
        "voice_change",
        "sick_contacts",
    ],
    "red_flags": [
        "airway_compromise_symptoms",
        "severe_trouble_swallowing",
        "drooling_with_sore_throat",
        "fever_with_worsening_throat_pain",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}


BACK_PAIN_POLICY = {
    "policy_name": "back_pain",
    "display_name": "Back Pain",
    "aliases": [
        "back pain",
        "low back pain",
        "upper back pain",
    ],
    "critical_followups": [
        "neurologic_symptoms",
        "bowel_or_bladder_changes",
        "fever",
        "head_trauma",
        "rapid_worsening",
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
        "radiation",
        "recent_heavy_lifting",
        "numbness_or_tingling",
    ],
    "red_flags": [
        "back_pain_with_neurologic_deficit",
        "back_pain_with_bowel_or_bladder_changes",
        "fever_with_back_pain",
        "post_traumatic_back_pain",
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
        "min_required_characterization_count": 4,
    },
}


COMPLAINT_POLICIES = {
    "headache": HEADACHE_POLICY,
    "chest_pain": CHEST_PAIN_POLICY,
    "abdominal_pain": ABDOMINAL_PAIN_POLICY,
    "shortness_of_breath": SHORTNESS_OF_BREATH_POLICY,
    "dizziness": DIZZINESS_POLICY,
    "sore_throat": SORE_THROAT_POLICY,
    "back_pain": BACK_PAIN_POLICY,
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