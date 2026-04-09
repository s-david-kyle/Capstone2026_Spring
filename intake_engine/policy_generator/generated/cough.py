# Policy: Cough
# Add COUGH_POLICY to COMPLAINT_POLICIES in complaint_policies.py

COUGH_POLICY = {
    "policy_name": "cough",
    "display_name": "Cough",
    "aliases": [
        "cough",
        "coughing",
        "coughing up blood",
        "persistent cough",
        "dry cough",
        "wet cough",
        "i have a cough",
        "i keep coughing",
        "can't stop coughing",
    ],
    "critical_followups": [
        "shortness_of_breath",
        "chest_pain",
        "rapid_worsening",
        "hemoptysis",
        "fever_or_neck_stiffness",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "timing",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "wheezing",
        "sick_contacts",
    ],
    "red_flags": [
        "hemoptysis",
        "cough_with_respiratory_distress",
        "cough_with_chest_pain",
        "rapidly_worsening_cough_with_fever",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "character",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 5,
    },
}
