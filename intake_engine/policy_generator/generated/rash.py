# Policy: Rash
# Add RASH_POLICY to COMPLAINT_POLICIES in complaint_policies.py

RASH_POLICY = {
    "policy_name": "rash",
    "display_name": "Rash",
    "aliases": [
        "rash",
        "skin rash",
        "hives",
        "breakout",
        "skin irritation",
        "itchy skin",
        "spots on skin",
        "i have a rash",
        "my skin broke out",
        "welts",
    ],
    "critical_followups": [
        "fever_or_neck_stiffness",
        "syncope_or_presyncope",
        "shortness_of_breath",
        "trouble_swallowing",
        "drooling",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "location",
        "character",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "sick_contacts",
    ],
    "red_flags": [
        "petechial_rash_with_fever_suggesting_meningococcemia",
        "anaphylaxis_with_rash",
        "airway_compromise_with_rash",
        "rash_with_syncope",
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
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
        ],
        "min_required_characterization_count": 6,
    },
}
