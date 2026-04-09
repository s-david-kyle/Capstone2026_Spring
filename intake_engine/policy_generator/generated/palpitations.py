# Policy: Palpitations
# Add PALPITATIONS_POLICY to COMPLAINT_POLICIES in complaint_policies.py

PALPITATIONS_POLICY = {
    "policy_name": "palpitations",
    "display_name": "Palpitations",
    "aliases": [
        "palpitations",
        "heart racing",
        "heart pounding",
        "heart fluttering",
        "skipping beats",
        "irregular heartbeat",
        "my heart is racing",
        "i can feel my heart beating",
        "heart is pounding",
        "heart is fluttering",
    ],
    "critical_followups": [
        "chest_pain",
        "shortness_of_breath",
        "syncope_or_presyncope",
        "rapid_worsening",
        "diaphoresis",
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
        "exertional_component",
        "positional_component",
    ],
    "red_flags": [
        "palpitations_with_chest_pain",
        "palpitations_with_syncope",
        "palpitations_with_dyspnea",
        "rapidly_worsening_palpitations",
        "palpitations_with_diaphoresis",
    ],
    "wrap_up_rule": {
        "type": "characterization_threshold",
        "require_all_critical": True,
        "required_characterization_targets": [
            "onset",
            "duration",
            "severity",
            "timing",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 5,
    },
}
