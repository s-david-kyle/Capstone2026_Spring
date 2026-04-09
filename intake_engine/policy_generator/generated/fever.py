# Policy: Fever
# Add FEVER_POLICY to COMPLAINT_POLICIES in complaint_policies.py

FEVER_POLICY = {
    "policy_name": "fever",
    "display_name": "Fever",
    "aliases": [
        "fever",
        "high temperature",
        "high temp",
        "running a fever",
        "i have a fever",
        "feel hot",
        "chills",
        "i have chills",
    ],
    "critical_followups": [
        "fever_or_neck_stiffness",
        "neurologic_symptoms",
        "shortness_of_breath",
        "chest_pain",
        "confusion_or_ams",
        "rapid_worsening",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "timing",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "nausea_or_vomiting",
        "cough",
        "urinary_symptoms",
        "rash_or_petechiae",
        "sick_contacts",
    ],
    "red_flags": [
        "fever_with_neck_stiffness",
        "fever_with_neurologic_symptoms",
        "fever_with_respiratory_distress",
        "fever_with_altered_mental_status",
        "rapidly_worsening_fever_with_systemic_signs",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 4,
    },
}
