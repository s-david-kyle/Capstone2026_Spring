# Policy: Nausea / Vomiting
# Add NAUSEA_VOMITING_POLICY to COMPLAINT_POLICIES in complaint_policies.py

NAUSEA_VOMITING_POLICY = {
    "policy_name": "nausea_vomiting",
    "display_name": "Nausea / Vomiting",
    "aliases": [
        "nausea",
        "vomiting",
        "nausea and vomiting",
        "throwing up",
        "feeling sick",
        "queasy",
        "i feel nauseous",
        "i keep throwing up",
        "can't keep anything down",
    ],
    "critical_followups": [
        "bloody_stool_or_melena",
        "chest_pain",
        "neurologic_symptoms",
        "fever",
        "rapid_worsening",
        "syncope_or_presyncope",
        "pregnancy_or_postpartum_context",
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
        "last_oral_intake",
        "sick_contacts",
    ],
    "red_flags": [
        "gi_bleeding_with_nausea",
        "chest_pain_with_nausea",
        "neurologic_symptoms_with_vomiting",
        "fever_with_vomiting",
        "syncope_with_nausea",
        "pregnancy_related_vomiting",
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
