# Policy: Urinary Symptoms
# Add URINARY_SYMPTOMS_POLICY to COMPLAINT_POLICIES in complaint_policies.py

URINARY_SYMPTOMS_POLICY = {
    "policy_name": "urinary_symptoms",
    "display_name": "Urinary Symptoms",
    "aliases": [
        "urinary symptoms",
        "burning urination",
        "painful urination",
        "frequent urination",
        "blood in urine",
        "can't urinate",
        "trouble urinating",
        "dysuria",
        "uti",
        "urinary tract infection",
        "i can't pee",
        "it burns when i pee",
    ],
    "critical_followups": [
        "fever_or_neck_stiffness",
        "flank_pain",
        "hematuria",
        "urinary_retention",
        "rapid_worsening",
        "neurologic_symptoms",
    ],
    "must_characterize": [
        "onset",
        "duration",
        "severity",
        "aggravating_factors",
        "relieving_factors",
        "associated_symptoms",
    ],
    "high_priority_followups": [
        "medications",
        "allergies",
        "suprapubic_pain",
        "nausea_or_vomiting",
        "pregnancy_or_postpartum_context",
    ],
    "red_flags": [
        "fever_with_urinary_symptoms_suggesting_pyelonephritis",
        "flank_pain_with_urinary_symptoms",
        "hematuria_with_urinary_symptoms",
        "complete_urinary_retention",
        "neurologic_deficit_with_urinary_changes",
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
